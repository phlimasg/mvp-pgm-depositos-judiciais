from sqlmodel import Field, Relationship

from core.BaseModel import BaseModel
from models.DjoRetFile import DjoRetFile



class DjoRetFileCabecalho(BaseModel, table=True): 
    tipo_registro: str = Field(nullable=True)
    tipo_arquivo: str  = Field(nullable=True)
    remessa: str  = Field(nullable=True)
    idremessa: str  = Field(nullable=True)
    digito: str = Field(nullable=True)    
    
    retfile_id: int | None = Field(default=None,foreign_key="djoretfile.id")
    retfile: DjoRetFile| None  = Relationship(back_populates="cabecalhos")
