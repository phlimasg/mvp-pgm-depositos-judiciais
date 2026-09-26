"""add pav_jsession to sessions

Revision ID: c1d2e3f4a5b6
Revises: 00bfeeea405d
Create Date: 2026-08-12 11:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c1d2e3f4a5b6"
down_revision: Union[str, None] = "00bfeeea405d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "sessions",
        sa.Column("pav_jsession", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("sessions", "pav_jsession")
