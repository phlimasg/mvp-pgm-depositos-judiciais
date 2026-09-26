from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = "c8d9e0f1a2b3"
down_revision: Union[str, None] = "b7c8d9e0f1a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "assistente_ia_config",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column(
            "openwebui_url",
            sqlmodel.sql.sqltypes.AutoString(length=500),
            nullable=False,
        ),
        sa.Column("api_key_encrypted", sa.Text(), nullable=True),
        sa.Column(
            "modelo_padrao",
            sqlmodel.sql.sqltypes.AutoString(length=200),
            nullable=True,
        ),
        sa.Column("limite_tokens", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    bind = op.get_bind()
    existe = bind.execute(
        sa.text("SELECT 1 FROM pg_type WHERE typname = 'logapplicationenum'")
    ).scalar()
    if existe:
        op.execute(
            "ALTER TYPE logapplicationenum ADD VALUE IF NOT EXISTS 'ASSISTENTE_IA_CONFIG'"
        )


def downgrade() -> None:
    op.drop_table("assistente_ia_config")
