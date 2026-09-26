from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = "b7c8d9e0f1a2"
down_revision: Union[str, None] = "a6b7c8d9e0f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "assistente_ia_contexto_documentos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("chat_id", sqlmodel.sql.sqltypes.AutoString(length=36), nullable=False),
        sa.Column("usuario_matricula", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column("documento_id", sqlmodel.sql.sqltypes.AutoString(length=120), nullable=False),
        sa.Column("tipo", sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
        sa.Column("numero_judicial", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column("nome", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("id_arquivo", sqlmodel.sql.sqltypes.AutoString(length=64), nullable=True),
        sa.Column("nome_arquivo", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "chat_id",
            "documento_id",
            "tipo",
            name="uq_assistente_ia_contexto_documento",
        ),
    )
    op.create_index(
        op.f("ix_assistente_ia_contexto_documentos_chat_id"),
        "assistente_ia_contexto_documentos",
        ["chat_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_assistente_ia_contexto_documentos_usuario_matricula"),
        "assistente_ia_contexto_documentos",
        ["usuario_matricula"],
        unique=False,
    )
    op.create_index(
        op.f("ix_assistente_ia_contexto_documentos_documento_id"),
        "assistente_ia_contexto_documentos",
        ["documento_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_assistente_ia_contexto_documentos_documento_id"),
        table_name="assistente_ia_contexto_documentos",
    )
    op.drop_index(
        op.f("ix_assistente_ia_contexto_documentos_usuario_matricula"),
        table_name="assistente_ia_contexto_documentos",
    )
    op.drop_index(
        op.f("ix_assistente_ia_contexto_documentos_chat_id"),
        table_name="assistente_ia_contexto_documentos",
    )
    op.drop_table("assistente_ia_contexto_documentos")
