"""Criando tabela assistente_ia_logs

Revision ID: a1f3c9e27b41
Revises: 7d99519d923a
Create Date: 2026-08-05 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'a1f3c9e27b41'
down_revision: Union[str, None] = '7d99519d923a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('assistente_ia_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.Column('usuario_matricula', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
    sa.Column('openwebui_chat_id', sqlmodel.sql.sqltypes.AutoString(length=36), nullable=False),
    sa.Column('titulo', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
    sa.Column('pergunta', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('resposta', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('model', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assistente_ia_logs_usuario_matricula'), 'assistente_ia_logs', ['usuario_matricula'], unique=False)
    op.create_index(op.f('ix_assistente_ia_logs_openwebui_chat_id'), 'assistente_ia_logs', ['openwebui_chat_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_assistente_ia_logs_openwebui_chat_id'), table_name='assistente_ia_logs')
    op.drop_index(op.f('ix_assistente_ia_logs_usuario_matricula'), table_name='assistente_ia_logs')
    op.drop_table('assistente_ia_logs')
