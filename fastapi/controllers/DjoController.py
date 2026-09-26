import datetime
import decimal
import time
from typing import Any, List
from fastapi import APIRouter, Depends, UploadFile, status

from enums.RoutesTagsEnum import RoutesTagsEnum
from repositories.DJORepository import DjoRepository

# Inicializa um APIRouter. Todas as rotas definidas com este router
# podem ter um prefixo e tags comuns.
djo_router = APIRouter(
    prefix="/djos",
    tags=[RoutesTagsEnum.BB],  # Agrupa estas rotas na documentação Swagger UI
)


@djo_router.post("", response_model=object, status_code=status.HTTP_201_CREATED)
async def upload_files(
    files: List[UploadFile] = [],
    repository: DjoRepository = Depends(),
):
    """
    Faz o upload de múltiplos arquivos .ret e os armazena no banco de dados.
    """
    inicio = time.perf_counter()
    result = []
    for file in files:
        result.append(await processarLinhas(file, repository))
    tempo_total = time.perf_counter() - inicio
    print(f"[DJO] Tempo total de execução: {tempo_total:.4f} segundos")
    return result


async def processarLinhas(file: UploadFile, repository: DjoRepository):
    """
    Processa as linhas do arquivo e salva no banco de dados usando bulk insert otimizado.
    """
    # 1. Checagem rápida de duplicidade
    if repository.find_by_nome(file.filename or ""):
        return {
            "message": f"Arquivo '{file.filename}' já foi processado anteriormente.",
            "error": "Arquivo duplicado.",
        }

    conteudo = await file.read()
    texto = conteudo.decode("latin-1")  # Use 'utf-8' se o arquivo for UTF-8
    linhas = texto.splitlines()

    arquivo_info: dict[str, Any] = {
        "nome": file.filename,
        "tamanho": file.size,
        "tipo_arquivo": file.content_type,
        "data": None,
    }

    cabecalhos: List[dict[str, Any]] = []
    tipos_a: List[dict[str, Any]] = []
    tipos_b: List[dict[str, Any]] = []
    tipo_c: dict[str, Any] | None = None

    for linha in linhas:
        if not linha:
            continue

        tipo = linha[0]
        match tipo:
            case "0":
                cabecalhos.append(
                    {
                        "tipo_registro": linha[0:2],
                        "tipo_arquivo": linha[2:8],
                        "remessa": linha[8:20],
                        "idremessa": linha[20:35].strip(),
                        "digito": linha[36:].strip(),
                    }
                )
            case "1":
                cabecalhos.append(
                    {
                        "tipo_registro": linha[0:1],
                        "tipo_arquivo": linha[1:].strip(),
                    }
                )
            case "2":
                cabecalhos.append(
                    {
                        "tipo_registro": linha[0:1],
                        "tipo_arquivo": linha[26:].strip(),
                        "idremessa": linha[12:26].strip(),
                    }
                )
            case "3":
                cabecalhos.append(
                    {
                        "tipo_registro": linha[0:1],
                        "tipo_arquivo": linha[15:].strip().replace(".", "/"),
                    }
                )
            case "4":
                cabecalhos.append(
                    {
                        "tipo_registro": linha[0:1],
                        "tipo_arquivo": linha[1:].strip().replace(",", ""),
                    }
                )
                tempDate = linha[121:].strip()
                try:
                    arquivo_info["data"] = datetime.datetime.strptime(tempDate, "%d.%m.%Y %H.%M.%S")
                except ValueError:
                    pass
            case "5":
                tipo_arq_cab = linha[1:].strip()
                arquivo_info["tipo_arquivo"] = tipo_arq_cab
                if tipo_arq_cab == "RESUMO DO MOVIMENTO DIARIO":
                    return {
                        "message": f"Arquivo '{tipo_arq_cab}' não importado.",
                        "error": "Arquivo não compatível.",
                    }
                cabecalhos.append(
                    {
                        "tipo_registro": linha[0:1],
                        "tipo_arquivo": tipo_arq_cab,
                    }
                )
            case "A":
                tipos_a.append(
                    {
                        "tipo_arquivo": linha[0:1],
                        "num_processo": linha[1:26].strip(),
                        "tribunal": linha[26:51].strip(),
                        "municipio": linha[51:76].strip(),
                        "unidade_judiciaria": linha[76:101].strip(),
                        "cod_agencia": linha[101:105].strip(),
                        "nome_autor": linha[105:135].strip(),
                        "cpf_cnpj_autor": linha[135:149].strip(),
                        "nome_reu": linha[149:179].strip(),
                        "cpf_cnpj_reu": linha[179:].strip(),
                    }
                )
            case "B":
                data_deposito_str = linha[33:43].strip()
                try:
                    data_deposito = datetime.datetime.strptime(data_deposito_str, "%d.%m.%Y")
                except ValueError:
                    data_deposito = datetime.datetime.now()

                data2 = linha[128:138].strip()
                data_movimentacao = None
                if data2:
                    try:
                        data_movimentacao = datetime.datetime.strptime(data2, "%d.%m.%Y")
                    except ValueError:
                        data_movimentacao = None

                valor_resgatado_str = linha[111:128].strip()
                valor_resgatado = (
                    decimal.Decimal(valor_resgatado_str) / 100 if valor_resgatado_str else decimal.Decimal(0)
                )

                tipos_b.append(
                    {
                        "_tipo_a_index": len(tipos_a) - 1,
                        "tipo_arquivo": linha[0:1],
                        "cod_banco": linha[1:5].strip(),
                        "cod_agencia": linha[5:14].strip(),
                        "parcela": linha[14:18].strip(),
                        "guia": linha[18:33].strip(),
                        "data_deposito": data_deposito,
                        "valor_principal": decimal.Decimal(linha[43:60].strip() or 0) / 100,
                        "correcao": decimal.Decimal(linha[60:77].strip() or 0) / 100,
                        "juros": decimal.Decimal(linha[77:94].strip() or 0) / 100,
                        "valor_atualizado": decimal.Decimal(linha[94:111].strip() or 0) / 100,
                        "valor_resgatado": valor_resgatado,
                        "data_movimentacao": data_movimentacao,
                        "cod_controle": linha[138:].strip(),
                        "tipo_evento":"",
                    }
                )
            case "C":
                tipo_c = {
                    "valor_total": decimal.Decimal(linha[1:19].strip() or 0) / 100,
                    "valor_total_juros": decimal.Decimal(linha[20:37].strip() or 0) / 100,
                    "valor_total_correcao": decimal.Decimal(linha[38:55].strip() or 0) / 100,
                    "valor_total_atualizado": decimal.Decimal(linha[56:].strip() or 0) / 100,
                }
            case _:
                continue

    # Persiste em lote através do repositório
    repository.salvar_arquivo_completo(
        arquivo_info=arquivo_info,
        cabecalhos=cabecalhos,
        tipos_a=tipos_a,
        tipos_b=tipos_b,
        tipo_c=tipo_c,
    )

    return {"message": f"Arquivo '{file.filename}' processado com sucesso."}
