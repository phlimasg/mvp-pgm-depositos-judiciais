"""add_honorarios_agrupamento_funcionarios

Revision ID: 1c0c8ec2ff07
Revises: c44d9da4e86e
Create Date: 2026-02-25 09:50:43.680932

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '1c0c8ec2ff07'
down_revision: Union[str, None] = 'c44d9da4e86e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'honorarios_agrupamento_funcionarios',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('funcionario_id', sa.Integer, sa.ForeignKey('funcionarios.id'), nullable=False, index=True),
        sa.Column('funcionario_agrupado_id', sa.Integer, sa.ForeignKey('funcionarios.id'), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
        sa.Column('deleted_at', sa.DateTime, nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['funcionario_id'], ['funcionarios.id']),
        sa.ForeignKeyConstraint(['funcionario_agrupado_id'], ['funcionarios.id']),
        # sa.Index('ix_honorarios_agrupamento_funcionarios_funcionario_id', 'funcionario_id'),
        # sa.Index('ix_honorarios_agrupamento_funcionarios_funcionario_agrupado_id', 'funcionario_agrupado_id')
    )

def downgrade() -> None:
    op.drop_table('honorarios_agrupamento_funcionarios')
