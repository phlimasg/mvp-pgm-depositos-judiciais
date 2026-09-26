"""criando status com enum

Revision ID: e307805ee818
Revises: ea5e3be0c53b
Create Date: 2025-11-07 09:33:27.041379

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'e307805ee818'
down_revision: Union[str, None] = 'ea5e3be0c53b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Defina o Enum aqui para poder criar no banco
func_status_enum = sa.Enum(
    "ATIVO",
    "APOSENTADO",
    "OBITO",
    "INATIVO",
    "AFASTADO",
    "CEDIDO",
    name="funcionariostatus"
)

def upgrade():
    bind = op.get_bind()

    # 1. Criar o ENUM no banco (se ainda não existir)
    func_status_enum.create(bind, checkfirst=True)

    # 2. Normalizar valores inválidos ANTES do cast
    op.execute("""
        UPDATE funcionarios
        SET status = 'ATIVO'
        WHERE status IS NULL
           OR TRIM(status) = ''
           OR status NOT IN ('ATIVO', 'APOSENTADO', 'OBITO', 'INATIVO', 'AFASTADO', 'CEDIDO');
    """)

    # 3. Alterar tipo da coluna usando o ENUM
    op.execute("""
        ALTER TABLE funcionarios
        ALTER COLUMN status
        TYPE funcionariostatus
        USING status::funcionariostatus;
    """)

    # 4. Definir DEFAULT 'ATIVO'
    op.execute("""
        ALTER TABLE funcionarios
        ALTER COLUMN status
        SET DEFAULT 'ATIVO';
    """)


def downgrade():
    bind = op.get_bind()

    # Reverter NOT NULL
    op.alter_column("funcionarios", "status", nullable=True)

    # Remover default
    op.execute("""
        ALTER TABLE funcionarios
        ALTER COLUMN status DROP DEFAULT;
    """)

    # Voltar para VARCHAR
    op.execute("""
        ALTER TABLE funcionarios
        ALTER COLUMN status
        TYPE VARCHAR(100);
    """)

    # Remover ENUM
    func_status_enum.drop(bind, checkfirst=True)
