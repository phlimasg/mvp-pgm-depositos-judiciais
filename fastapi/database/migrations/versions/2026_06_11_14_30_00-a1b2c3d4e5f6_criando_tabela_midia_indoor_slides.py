"""Criando tabela midia_indoor_slides

Revision ID: a1b2c3d4e5f6
Revises: abc982830207
Create Date: 2026-06-11 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "abc982830207"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "midia_indoor_slides",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("titulo", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("tipo", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column("arquivo_nome", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("arquivo_path", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("ordem", sa.Integer(), nullable=False),
        sa.Column("duracao_segundos", sa.Integer(), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("midia_indoor_slides")
