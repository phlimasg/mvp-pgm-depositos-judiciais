"""Merge dos heads 8abeab441d2a e 98f6319924ec

Revision ID: 97294309583b
Revises: 8abeab441d2a, 98f6319924ec
Create Date: 2025-11-26 17:05:34.791831

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '97294309583b'
down_revision: Union[str, None] = ('8abeab441d2a', '98f6319924ec')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
