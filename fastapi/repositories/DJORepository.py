import datetime
import decimal
import logging
from typing import Any, List, cast
from fastapi import Depends
from sqlalchemy import Table
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Session, select

from core.BaseRepository import BaseRepository
from database.engine import get_session
from models.DjoRetFile import DjoRetFile
from models.DjoRetFileCabecalho import DjoRetFileCabecalho
from models.DjoRetFileTipoA import DjoRetFileTipoA
from models.DjoRetFileTipoB import DjoRetFileTipoB
from models.DjoRetFileTipoC import DjoRetFileTipoC

logger = logging.getLogger(__name__)


class DjoRepository(BaseRepository[DjoRetFile]):
    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(DjoRetFile, session)

    def find_by_nome(self, nome: str) -> DjoRetFile | None:
        """Busca um arquivo DJO pelo nome para validação de duplicidade."""
        statement = select(DjoRetFile).where(DjoRetFile.nome == nome)
        return self.session.exec(statement).first()

    def salvar_arquivo_completo(
        self,
        arquivo_info: dict[str, Any],
        cabecalhos: List[dict[str, Any]],
        tipos_a: List[dict[str, Any]],
        tipos_b: List[dict[str, Any]],
        tipo_c: dict[str, Any] | None = None,
        batch_size: int = 2000,
    ) -> DjoRetFile:
        """
        Salva o arquivo DJO e todas as suas entidades associadas usando bulk insert otimizado.
        Garante integridade transacional e alta performance mesmo com 80k+ linhas.
        """
        try:
            # 1. Cria e persiste o registro principal (DjoRetFile)
            ret_file = DjoRetFile(
                nome=arquivo_info.get("nome", ""),
                tamanho=arquivo_info.get("tamanho", 0.0),
                tipo_arquivo=arquivo_info.get("tipo_arquivo", ""),
                data=arquivo_info.get("data"),
            )
            self.session.add(ret_file)
            self.session.flush()  # Obtém ret_file.id sem commit final

            file_id = ret_file.id
            if not file_id:
                raise ValueError("Falha ao gerar ID para DjoRetFile.")

            # 2. Bulk insert dos cabeçalhos
            if cabecalhos:
                for c in cabecalhos:
                    c["retfile_id"] = file_id
                self._bulk_insert_chunks(DjoRetFileCabecalho, cabecalhos, batch_size=batch_size)

            # 3. Bulk insert de Tipo C (resumo final)
            if tipo_c:
                tipo_c["retfile_id"] = file_id
                now = datetime.datetime.now(datetime.timezone.utc)
                tipo_c.setdefault("created_at", now)
                tipo_c.setdefault("updated_at", now)
                table_c = cast(Table, getattr(DjoRetFileTipoC, "__table__"))
                stmt_c = insert(table_c).values(tipo_c)
                self.session.exec(stmt_c)

            # 4. Inserção do Tipo A e mapeamento para Tipo B
            # tipos_b possui o índice do Tipo A pai (_tipo_a_index) para amarrar os IDs
            if tipos_a:
                tipo_a_ids = self._insert_tipos_a_returning_ids(file_id, tipos_a, batch_size=batch_size)

                # Vincula retfiletipoa_id correto em cada Tipo B
                if tipos_b:
                    for b in tipos_b:
                        parent_idx = b.pop("_tipo_a_index", None)
                        if parent_idx is not None and parent_idx < len(tipo_a_ids):
                            b["retfiletipoa_id"] = tipo_a_ids[parent_idx]
                        else:
                            raise ValueError(f"Tipo B órfão ou índice pai inválido: {parent_idx}")

                    self._bulk_insert_chunks(DjoRetFileTipoB, tipos_b, batch_size=batch_size)

            # 5. Commit único de toda a transação
            self.session.commit()
            self.session.refresh(ret_file)
            return ret_file

        except Exception as e:
            self.session.rollback()
            logger.exception("Erro ao salvar dados do arquivo DJO em lote: %s", str(e))
            raise e

    def _normalize_records(self, table: Table, records: List[dict[str, Any]]) -> List[dict[str, Any]]:
        """
        Garante que todos os dicionários no lote contenham exatamente as mesmas chaves
        esperadas pela tabela do banco, preenchendo ausências com None ou valores padrão.
        Isso evita o erro de CompileError do SQLAlchemy em INSERT multi-row com chaves heterogêneas.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        column_names = [col.name for col in table.columns if col.name != "id"]

        normalized: List[dict[str, Any]] = []
        for r in records:
            item: dict[str, Any] = {}
            for col in column_names:
                if col in r:
                    item[col] = r[col]
                elif col in ("created_at", "updated_at"):
                    item[col] = now
                elif col == "deleted_at":
                    item[col] = None
                else:
                    item[col] = None
            normalized.append(item)
        return normalized

    def _insert_tipos_a_returning_ids(
        self, file_id: int, records: List[dict[str, Any]], batch_size: int = 1000
    ) -> List[int]:
        """
        Insere registros de Tipo A em lotes preservando a ordem e retornando os IDs gerados.
        """
        all_ids: List[int] = []
        table = cast(Table, getattr(DjoRetFileTipoA, "__table__"))

        for i in range(0, len(records), batch_size):
            chunk = records[i : i + batch_size]
            for item in chunk:
                item["retfile_id"] = file_id

            normalized_chunk = self._normalize_records(table, chunk)
            stmt = insert(table).values(normalized_chunk).returning(table.c.id)
            result = self.session.exec(stmt)
            inserted_rows = list(result.all())
            for row in inserted_rows:
                row_val = row[0] if hasattr(row, "__getitem__") else row
                all_ids.append(int(row_val))

        return all_ids

    def _bulk_insert_chunks(
        self, model_class: Any, records: List[dict[str, Any]], batch_size: int = 2000
    ) -> None:
        """
        Insere múltiplos dicionários via direct table insert em chunks/lotes para não exceder limites de bind params.
        Normaliza os dicionários para garantir que todos tenham as mesmas chaves em multi-row INSERTs.
        """
        table = cast(Table, getattr(model_class, "__table__"))
        for i in range(0, len(records), batch_size):
            chunk = records[i : i + batch_size]
            normalized_chunk = self._normalize_records(table, chunk)
            stmt = insert(table).values(normalized_chunk)
            self.session.exec(stmt)
