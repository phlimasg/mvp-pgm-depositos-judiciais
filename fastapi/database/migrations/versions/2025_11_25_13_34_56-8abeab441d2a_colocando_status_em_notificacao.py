"""colocando status em notificacao

Revision ID: 8abeab441d2a
Revises: d2076dbb98ee
Create Date: 2025-11-25 13:34:56.622622
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '8abeab441d2a'
down_revision: Union[str, None] = 'd2076dbb98ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # 1️⃣ Criar coluna como NULLABLE
    op.add_column(
        'notificacoes',
        sa.Column(
            'status',
            sa.Enum(
                'NAO_VISTA',
                'VISTA',
                'LIDA',
                'NAO_LIDA',
                name='notificacao_status_enum',
                native_enum=False
            ),
            nullable=True   # ← IMPORTANTE
        )
    )

    # 2️⃣ Preencher registros antigos com valor default
    op.execute("UPDATE notificacoes SET status = 'NAO_VISTA' WHERE status IS NULL")

    # 3️⃣ Agora tornar NOT NULL
    op.alter_column(
        'notificacoes',
        'status',
        nullable=False
    )

    # 4️⃣ Remover coluna antiga "lida"
    op.drop_column('notificacoes', 'lida')


def downgrade() -> None:
    op.add_column('notificacoes', sa.Column('lida', sa.Boolean(), nullable=False))
    op.drop_column('notificacoes', 'status')
