"""fix lista_espera_limite

Revision ID: bde571a493f4
Revises: b0238b79d48f
Create Date: 2025-12-18 11:12:40.113406

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'bde571a493f4'
down_revision: Union[str, None] = 'b0238b79d48f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Converter coluna lista_espera_limite de TIMESTAMP para INTEGER (minutos)
    # 1. Adicionar coluna temporária para armazenar valores em minutos
    op.add_column('cursos_ofertas', sa.Column('lista_espera_limite_temp', sa.Integer(), nullable=True))
    
    # 2. Calcular minutos a partir do TIMESTAMP existente
    # Se o timestamp for NULL, usar 48 * 60 = 2880 minutos (padrão 48h)
    # Se o timestamp for no passado, usar 0
    # Se o timestamp for no futuro, calcular diferença em minutos
    op.execute("""
        UPDATE cursos_ofertas
        SET lista_espera_limite_temp = CASE
            WHEN lista_espera_limite IS NULL THEN 2880
            WHEN lista_espera_limite > NOW() THEN 
                EXTRACT(EPOCH FROM (lista_espera_limite - NOW())) / 60.0
            ELSE 0
        END
    """)
    
    # 3. Remover coluna antiga
    op.drop_column('cursos_ofertas', 'lista_espera_limite')
    
    # 4. Renomear coluna temporária para o nome original
    op.alter_column('cursos_ofertas', 'lista_espera_limite_temp', new_column_name='lista_espera_limite')


def downgrade() -> None:
    # Reverter: converter INTEGER (minutos) de volta para TIMESTAMP
    # 1. Adicionar coluna temporária
    op.add_column('cursos_ofertas', sa.Column('lista_espera_limite_temp', postgresql.TIMESTAMP(), nullable=True))
    
    # 2. Converter minutos de volta para TIMESTAMP (adicionando aos minutos atuais)
    op.execute("""
        UPDATE cursos_ofertas
        SET lista_espera_limite_temp = CASE
            WHEN lista_espera_limite IS NULL THEN NULL
            ELSE NOW() + (lista_espera_limite * INTERVAL '1 minute')
        END
    """)
    
    # 3. Remover coluna antiga
    op.drop_column('cursos_ofertas', 'lista_espera_limite')
    
    # 4. Renomear coluna temporária
    op.alter_column('cursos_ofertas', 'lista_espera_limite_temp', new_column_name='lista_espera_limite')
