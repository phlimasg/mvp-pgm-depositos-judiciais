"""Criando ChaveAPIAplicacao por uma relacao de m2m com ChaveAPI.slugs e Aplicacao

Revision ID: abc982830207
Revises: 63fa288d3e96
Create Date: 2026-06-09 18:19:13.736728

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = 'abc982830207'
down_revision: Union[str, None] = '63fa288d3e96'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not inspector.has_table('chaves_api_aplicacoes'):
        op.create_table('chaves_api_aplicacoes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('chave_api_id', sa.Integer(), nullable=False),
        sa.Column('aplicacao_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['aplicacao_id'], ['aplicacao.id'], ),
        sa.ForeignKeyConstraint(['chave_api_id'], ['chaves_api.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_chaves_api_aplicacoes_aplicacao_id'), 'chaves_api_aplicacoes', ['aplicacao_id'], unique=False)
        op.create_index(op.f('ix_chaves_api_aplicacoes_chave_api_id'), 'chaves_api_aplicacoes', ['chave_api_id'], unique=False)
    else:
        existing_indexes = {index['name'] for index in inspector.get_indexes('chaves_api_aplicacoes')}
        if op.f('ix_chaves_api_aplicacoes_aplicacao_id') not in existing_indexes:
            op.create_index(op.f('ix_chaves_api_aplicacoes_aplicacao_id'), 'chaves_api_aplicacoes', ['aplicacao_id'], unique=False)
        if op.f('ix_chaves_api_aplicacoes_chave_api_id') not in existing_indexes:
            op.create_index(op.f('ix_chaves_api_aplicacoes_chave_api_id'), 'chaves_api_aplicacoes', ['chave_api_id'], unique=False)

    chaves_api_columns = {column['name'] for column in inspector.get_columns('chaves_api')}
    if 'tag' in chaves_api_columns:
        op.drop_column('chaves_api', 'tag')


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    chaves_api_columns = {column['name'] for column in inspector.get_columns('chaves_api')}
    if 'tag' not in chaves_api_columns:
        op.add_column('chaves_api', sa.Column('tag', sa.VARCHAR(), autoincrement=False, nullable=False))

    if inspector.has_table('chaves_api_aplicacoes'):
        existing_indexes = {index['name'] for index in inspector.get_indexes('chaves_api_aplicacoes')}
        if op.f('ix_chaves_api_aplicacoes_chave_api_id') in existing_indexes:
            op.drop_index(op.f('ix_chaves_api_aplicacoes_chave_api_id'), table_name='chaves_api_aplicacoes')
        if op.f('ix_chaves_api_aplicacoes_aplicacao_id') in existing_indexes:
            op.drop_index(op.f('ix_chaves_api_aplicacoes_aplicacao_id'), table_name='chaves_api_aplicacoes')
        op.drop_table('chaves_api_aplicacoes')
