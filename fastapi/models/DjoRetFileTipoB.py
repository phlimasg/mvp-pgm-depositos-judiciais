
import datetime
import decimal
from sqlmodel import Field, Relationship

from core.BaseModel import BaseModel

class DjoRetFileTipoB(BaseModel, table=True): 
    tipo_arquivo: str = ""
    cod_banco: str = ""
    cod_agencia: str = ""
    guia: str = ""
    data_deposito: datetime.datetime = datetime.datetime.now()
    valor_principal: decimal.Decimal = 0
    juros: decimal.Decimal = 0
    correcao: decimal.Decimal = 0
    valor_atualizado: decimal.Decimal = 0
    valor_resgatado: decimal.Decimal = 0
    data_movimentacao: datetime.datetime | None = None
    cod_controle: str = "" 
    tipo_evento: str = "" 
    parcela: str = ""

    retfiletipoa_id: int = Field(foreign_key="djoretfiletipoa.id")
    retfiletipoa: "DjoRetFileTipoA" = Relationship(back_populates="retfiletipob")
