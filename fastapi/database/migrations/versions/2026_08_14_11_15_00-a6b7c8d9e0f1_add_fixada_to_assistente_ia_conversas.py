"""Adiciona fixação às conversas do Assistente IA

Revision ID: a6b7c8d9e0f1
Revises: f5a6b7c8d9e0
Create Date: 2026-08-14 11:15:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a6b7c8d9e0f1"
down_revision: Union[str, None] = "f5a6b7c8d9e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "assistente_ia_conversas",
        sa.Column(
            "fixada",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column("assistente_ia_conversas", "fixada")
