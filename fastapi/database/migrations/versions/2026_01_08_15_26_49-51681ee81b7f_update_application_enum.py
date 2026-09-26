"""update_application_enum

Revision ID: 51681ee81b7f
Revises: c107819222a6
Create Date: 2026-01-08 15:26:49.562769

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "51681ee81b7f"
down_revision: Union[str, None] = "c107819222a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Adiciona o valor 'PUBLIC_UPLOAD' ao ENUM logapplicationenum
    op.execute("ALTER TYPE logapplicationenum ADD VALUE IF NOT EXISTS 'PUBLIC_UPLOAD';")


def downgrade() -> None:
    # Nota: PostgreSQL não permite remover valores de enums diretamente.
    # Para remover 'PUBLIC_UPLOAD', seria necessário recriar o enum completo,
    # o que é complexo e pode causar problemas com dados existentes.
    # Portanto, o downgrade não remove o valor do enum.
    pass
