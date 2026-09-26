"""Atualizar caminho dos arquivos para midia-indoor-slides

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-11 15:50:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE midia_indoor_slides
        SET arquivo_path = REPLACE(arquivo_path, 'midia-indoor/', 'midia-indoor-slides/')
        WHERE arquivo_path LIKE 'midia-indoor/%'
        """
    )
    op.execute(
        """
        UPDATE midia_indoor_slides
        SET arquivo_path = 'midia-indoor-slides/' || arquivo_path
        WHERE arquivo_path NOT LIKE '%/%'
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE midia_indoor_slides
        SET arquivo_path = REPLACE(arquivo_path, 'midia-indoor-slides/', '')
        WHERE arquivo_path LIKE 'midia-indoor-slides/%'
        """
    )
