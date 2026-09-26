
from typing import List
from sqlmodel import Field, Relationship


from core.BaseModel import BaseModel
from models import DjoRetFile



class DjoRetFileTipoA(BaseModel, table=True): 
    tipo_arquivo: str
    num_processo: str
    tribunal: str
    municipio: str
    unidade_judiciaria: str
    cod_agencia: str
    nome_autor: str #nome_remetente
    cpf_cnpj_autor: str #cpf_cnpj_remetente
    nome_reu: str #nome_destinatario
    cpf_cnpj_reu: str #cpf_cnpj_destinatario
    especializada: str = Field(nullable=True)

    retfiletipob: List["DjoRetFileTipoB"] = Relationship(back_populates="retfiletipoa")
    retfile_id: int | None = Field(default=None,foreign_key="djoretfile.id")
    retfile: DjoRetFile | None  = Relationship(back_populates="retfiletipoa")