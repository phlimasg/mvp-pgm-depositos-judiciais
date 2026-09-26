"""fix invalid status in cursos_ofertas

Revision ID: fix_invalid_status_ofertas
Revises: dc97f47d9500
Create Date: 2025-12-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_invalid_status_ofertas'
down_revision = 'dc97f47d9500'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Corrigir valores inválidos no campo status para ABERTA (padrão)
    op.execute(
        """
        UPDATE cursos_ofertas 
        SET status = 'ABERTA' 
        WHERE status NOT IN ('ABERTA', 'FECHADA', 'CANCELADA')
        """
    )


def downgrade() -> None:
    pass
