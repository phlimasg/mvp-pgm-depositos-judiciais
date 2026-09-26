"""add usuario_id FK to assistente_ia_logs

Revision ID: e4f5a6b7c8d9
Revises: d3e4f5a6b7c8
Create Date: 2026-08-12 17:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e4f5a6b7c8d9"
down_revision: Union[str, None] = "d3e4f5a6b7c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "assistente_ia_logs",
        sa.Column("usuario_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        op.f("ix_assistente_ia_logs_usuario_id"),
        "assistente_ia_logs",
        ["usuario_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_assistente_ia_logs_usuario_id_funcionarios",
        "assistente_ia_logs",
        "funcionarios",
        ["usuario_id"],
        ["id"],
    )
    # Backfill: vincula logs existentes à matrícula do funcionário
    op.execute(
        """
        UPDATE assistente_ia_logs AS l
        SET usuario_id = f.id
        FROM funcionarios AS f
        WHERE l.usuario_id IS NULL
          AND f.matricula = l.usuario_matricula
          AND f.deleted_at IS NULL
        """
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_assistente_ia_logs_usuario_id_funcionarios",
        "assistente_ia_logs",
        type_="foreignkey",
    )
    op.drop_index(
        op.f("ix_assistente_ia_logs_usuario_id"),
        table_name="assistente_ia_logs",
    )
    op.drop_column("assistente_ia_logs", "usuario_id")
