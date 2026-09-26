"""ajustando afastamentos

Revision ID: 22882ab055b5
Revises: 927a7558b22b
Create Date: 2025-10-13 17:42:18.634878
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '22882ab055b5'
down_revision: Union[str, None] = '927a7558b22b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ajusta colunas LE para tipo DATE com cast explícito
    op.alter_column(
        'honorarios_afastamentos', 'lei_ini',
        existing_type=sa.VARCHAR(length=30),
        type_=sa.Date(),
        existing_nullable=True,
        postgresql_using="lei_ini::date"
    )
    op.alter_column(
        'honorarios_afastamentos', 'lei_fim',
        existing_type=sa.VARCHAR(length=30),
        type_=sa.Date(),
        existing_nullable=True,
        postgresql_using="lei_fim::date"
    )

    # Atualiza constraint única e remove colunas antigas
    op.drop_constraint(op.f('uq_afast_funcionario_inicio_fim_tipo'), 'honorarios_afastamentos', type_='unique')
    op.create_unique_constraint(
        'uq_afast_funcionario_tipo_periodo',
        'honorarios_afastamentos',
        ['funcionario_id', 'tipo_id', 'lei_ini', 'lei_fim', 'freq_ini', 'freq_fim']
    )

    op.drop_column('honorarios_afastamentos', 'dt_fim')
    op.drop_column('honorarios_afastamentos', 'dt_prevista')
    op.drop_column('honorarios_afastamentos', 'dt_inicio')


def downgrade() -> None:
    # Reverte alterações
    op.add_column('honorarios_afastamentos', sa.Column('dt_inicio', sa.DATE(), autoincrement=False, nullable=True))
    op.add_column('honorarios_afastamentos', sa.Column('dt_prevista', sa.DATE(), autoincrement=False, nullable=True))
    op.add_column('honorarios_afastamentos', sa.Column('dt_fim', sa.DATE(), autoincrement=False, nullable=True))

    op.drop_constraint('uq_afast_funcionario_tipo_periodo', 'honorarios_afastamentos', type_='unique')
    op.create_unique_constraint(
        op.f('uq_afast_funcionario_inicio_fim_tipo'),
        'honorarios_afastamentos',
        ['funcionario_id', 'dt_inicio', 'dt_fim'],
        postgresql_nulls_not_distinct=False
    )

    op.alter_column(
        'honorarios_afastamentos', 'lei_fim',
        existing_type=sa.Date(),
        type_=sa.VARCHAR(length=30),
        existing_nullable=True,
        postgresql_using="lei_fim::text"
    )
    op.alter_column(
        'honorarios_afastamentos', 'lei_ini',
        existing_type=sa.Date(),
        type_=sa.VARCHAR(length=30),
        existing_nullable=True,
        postgresql_using="lei_ini::text"
    )
