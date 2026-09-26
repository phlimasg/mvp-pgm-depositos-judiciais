"""merge midia_indoor e assistente_ia heads

Revision ID: 00bfeeea405d
Revises: b2c3d4e5f6a7, b2e4d8f39c52
Create Date: 2026-08-11 18:04:20.384814

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '00bfeeea405d'
down_revision: Union[str, None] = ('b2c3d4e5f6a7', 'b2e4d8f39c52')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
