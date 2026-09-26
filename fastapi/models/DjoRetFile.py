import datetime
from sqlmodel import Relationship

from core.BaseModel import BaseModel



# from models.RetFileCabecalho import RetFileCabecalho


class DjoRetFile(BaseModel, table=True): # table=True indica que este modelo corresponde a uma tabela    
    nome: str
    tamanho: float
    tipo_arquivo: str
    data: datetime.datetime | None = None
    # cabecalho_id: int = Field(default=None, foreign_key="retfilecabecalho.id") 
    cabecalhos: list["DjoRetFileCabecalho"] = Relationship(back_populates="retfile")
    retfiletipoa: list["DjoRetFileTipoA"] = Relationship(back_populates="retfile")  # Referência por string
    retfiletipoc: "DjoRetFileTipoC" = Relationship(back_populates="retfile")  # Referência por string
    