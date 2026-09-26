"""Indice composto para consultas do assistente IA

Revision ID: b2e4d8f39c52
Revises: a1f3c9e27b41
Create Date: 2026-08-05 15:20:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b2e4d8f39c52'
down_revision: Union[str, None] = 'a1f3c9e27b41'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        'ix_assistente_ia_logs_user_chat_created',
        'assistente_ia_logs',
        ['usuario_matricula', 'openwebui_chat_id', 'created_at'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index('ix_assistente_ia_logs_user_chat_created', table_name='assistente_ia_logs')
