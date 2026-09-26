import decimal
from sqlmodel import Field, Relationship


from core.BaseModel import BaseModel
from models import DjoRetFile



class DjoRetFileTipoC(BaseModel, table=True): 
    valor_total: decimal.Decimal = 0 
    valor_total_juros: decimal.Decimal = 0 
    valor_total_correcao: decimal.Decimal = 0 
    valor_total_atualizado: decimal.Decimal = 0    
    retfile_id: int | None = Field(default=None,foreign_key="djoretfile.id")
    retfile: DjoRetFile | None  = Relationship(back_populates="retfiletipoc")