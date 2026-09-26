"""add processo to sessions and assistente_ia_logs

Revision ID: d3e4f5a6b7c8
Revises: c1d2e3f4a5b6
Create Date: 2026-08-12 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d3e4f5a6b7c8"
down_revision: Union[str, None] = "c1d2e3f4a5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "sessions",
        sa.Column("pav_processo", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "assistente_ia_logs",
        sa.Column("processo", sa.String(length=50), nullable=True),
    )
    op.create_index(
        op.f("ix_assistente_ia_logs_processo"),
        "assistente_ia_logs",
        ["processo"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_assistente_ia_logs_processo"), table_name="assistente_ia_logs")
    op.drop_column("assistente_ia_logs", "processo")
    op.drop_column("sessions", "pav_processo")
