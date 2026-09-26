"""fix sg_unidade_honoraria_atual

Revision ID: e3abbb5bbae1
Revises: 7751670c1902
Create Date: 2025-10-14 12:36:38.511814

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'e3abbb5bbae1'
down_revision: Union[str, None] = '7751670c1902'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Conversão segura: trata strings vazias e NULL antes de mudar o tipo
    op.execute("""
        ALTER TABLE funcionarios
        ALTER COLUMN sg_unidade_honoraria_atual
        TYPE double precision
        USING NULLIF(sg_unidade_honoraria_atual, '')::double precision;
    """)

    # Opcional: garante que valores nulos fiquem com 0.0
    op.execute("""
        UPDATE funcionarios
        SET sg_unidade_honoraria_atual = 0.0
        WHERE sg_unidade_honoraria_atual IS NULL;
    """)


def downgrade() -> None:
    op.alter_column(
        "funcionarios",
        "sg_unidade_honoraria_atual",
        existing_type=sa.Float(),
        type_=sa.VARCHAR(length=45),
        nullable=True,
    )
