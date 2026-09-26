"""mudando model de folhahonorarios

Revision ID: a5a21889ba51
Revises: ff3a60146918
Create Date: 2025-11-13 15:14:39.819814

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a5a21889ba51"
down_revision: Union[str, None] = "ff3a60146918"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ENUM object (precisa estar fora do upgrade)
status_enum = sa.Enum(
    "DRAFT",
    "RH_CALCULATING",
    "RH_READY",
    "CONT_EDITING",
    "CONT_READY",
    "RH_APPROVED",
    "CLOSED",
    name="folha_status_enum",
    native_enum=False,
)


def upgrade() -> None:
    # 1) criar ENUM (se não existir)
    status_enum.create(op.get_bind(), checkfirst=True)

    # 2) adicionar coluna status com default temporário
    op.add_column(
        "folhas_honorarios",
        sa.Column(
            "status",
            status_enum,
            nullable=True,
            server_default="DRAFT",
        ),
    )

    # 3) atualizar registros existentes
    op.execute("UPDATE folhas_honorarios SET status = 'DRAFT' WHERE status IS NULL")

    # 4) remover default
    op.alter_column(
        "folhas_honorarios",
        "status",
        server_default=None,
    )

    # 5) transformar em NOT NULL
    op.alter_column(
        "folhas_honorarios",
        "status",
        nullable=False,
    )

    # adiciona os outros campos
    op.add_column(
        "folhas_honorarios",
        sa.Column("rh_calculated_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "folhas_honorarios",
        sa.Column("cont_started_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "folhas_honorarios",
        sa.Column("cont_finished_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "folhas_honorarios",
        sa.Column("rh_approved_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "folhas_honorarios",
        sa.Column("closed_at", sa.DateTime(), nullable=True),
    )

    # remover a coluna antiga
    op.drop_column("folhas_honorarios", "liberar_rh")


def downgrade() -> None:
    op.add_column(
        "folhas_honorarios",
        sa.Column("liberar_rh", sa.Boolean(), nullable=False),
    )
    op.drop_column("folhas_honorarios", "closed_at")
    op.drop_column("folhas_honorarios", "rh_approved_at")
    op.drop_column("folhas_honorarios", "cont_finished_at")
    op.drop_column("folhas_honorarios", "cont_started_at")
    op.drop_column("folhas_honorarios", "rh_calculated_at")
    op.drop_column("folhas_honorarios", "status")

    # remove ENUM
    status_enum.drop(op.get_bind(), checkfirst=True)
