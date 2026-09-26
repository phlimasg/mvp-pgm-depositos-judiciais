"""corrigindo tipo_afastamento

Revision ID: f5d20493ce48
Revises: 0ddd26cdf888
Create Date: 2025-11-17 11:47:09.609554
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel

revision: str = 'f5d20493ce48'
down_revision: Union[str, None] = '0ddd26cdf888'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'honorarios_tipos_afastamento',
        sa.Column('mnemônico', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True)
    )
    op.add_column(
        'honorarios_tipos_afastamento',
        sa.Column('via_frequencia', sa.Boolean(), nullable=True)
    )
    op.add_column(
        'honorarios_tipos_afastamento',
        sa.Column('onus', sa.Boolean(), nullable=True)
    )
    op.add_column(
        'honorarios_tipos_afastamento',
        sa.Column('afast', sa.Boolean(), nullable=True)
    )
    op.add_column(
        'honorarios_tipos_afastamento',
        sa.Column('exige_regras', sa.Boolean(), nullable=True)
    )
    op.add_column(
        'honorarios_tipos_afastamento',
        sa.Column('valido_para_o_sexo', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True)
    )
    op.add_column(
        'honorarios_tipos_afastamento',
        sa.Column('esocial', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True)
    )
    op.add_column(
        'honorarios_tipos_afastamento',
        sa.Column('preenchimento_quantidade', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True)
    )
    op.add_column(
        'honorarios_tipos_afastamento',
        sa.Column('formato_quantidade', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True)
    )
    op.add_column(
        'honorarios_tipos_afastamento',
        sa.Column('mostrar_horarios', sa.Boolean(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('honorarios_tipos_afastamento', 'mostrar_horarios')
    op.drop_column('honorarios_tipos_afastamento', 'formato_quantidade')
    op.drop_column('honorarios_tipos_afastamento', 'preenchimento_quantidade')
    op.drop_column('honorarios_tipos_afastamento', 'esocial')
    op.drop_column('honorarios_tipos_afastamento', 'valido_para_o_sexo')
    op.drop_column('honorarios_tipos_afastamento', 'exige_regras')
    op.drop_column('honorarios_tipos_afastamento', 'afast')
    op.drop_column('honorarios_tipos_afastamento', 'onus')
    op.drop_column('honorarios_tipos_afastamento', 'via_frequencia')
    op.drop_column('honorarios_tipos_afastamento', 'mnemônico')
