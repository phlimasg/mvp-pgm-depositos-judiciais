"""atualizando os atributos de report

Revision ID: ca7134aad55d
Revises: 799b93345254
Create Date: 2025-12-02 11:35:27.286043

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'ca7134aad55d'
down_revision: Union[str, None] = '799b93345254'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
   
    # Novo campo tipo
    op.add_column(
        'reports',
        sa.Column('tipo', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True)
    )

    # Criação do Enum
    reportstatus = sa.Enum(
        'em aberto', 'andamento', 'concluído', 'improcedente',
        name='reportstatus'
    )
    reportstatus.create(op.get_bind(), checkfirst=True)

    # Alterar tipo da coluna COM conversão explícita
    op.alter_column(
        'reports',
        'status',
        existing_type=sa.BOOLEAN(),
        type_=reportstatus,
        existing_nullable=True,
        postgresql_using=(
            "CASE "
            "WHEN status = true THEN 'concluído'::reportstatus "
            "WHEN status = false THEN 'andamento'::reportstatus "
            "ELSE 'em aberto'::reportstatus "
            "END"
        )
    )


def downgrade() -> None:

    # Converter ENUM → BOOLEAN
    op.alter_column(
        'reports',
        'status',
        existing_type=sa.Enum(
            'em aberto', 'andamento', 'concluído', 'improcedente',
            name='reportstatus'
        ),
        type_=sa.BOOLEAN(),
        existing_nullable=True,
        postgresql_using=(
            "CASE "
            "WHEN status = 'concluído' THEN true "
            "ELSE false "
            "END"
        )
    )

    # Remover ENUM
    reportstatus = sa.Enum(
        'em aberto', 'andamento', 'concluído', 'improcedente',
        name='reportstatus'
    )
    reportstatus.drop(op.get_bind(), checkfirst=True)

    # Remover coluna
    op.drop_column('reports', 'tipo')

    # Restaurar tabela removida
    op.create_table(
        'usuario',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('username', sa.VARCHAR(length=100), nullable=False),
        sa.Column('senha', sa.VARCHAR(length=100), nullable=False),
        sa.Column('cargo', sa.VARCHAR(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )
