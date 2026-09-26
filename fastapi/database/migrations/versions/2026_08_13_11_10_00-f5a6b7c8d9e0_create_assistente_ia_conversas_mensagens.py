"""RF17: tabelas de conversa e mensagens individuais do Assistente IA

Revision ID: f5a6b7c8d9e0
Revises: e4f5a6b7c8d9
Create Date: 2026-08-13 11:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = "f5a6b7c8d9e0"
down_revision: Union[str, None] = "e4f5a6b7c8d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "assistente_ia_conversas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("chat_id", sqlmodel.sql.sqltypes.AutoString(length=36), nullable=False),
        sa.Column("usuario_matricula", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("processo", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column("titulo", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["funcionarios.id"],
            name="fk_assistente_ia_conversas_usuario_id_funcionarios",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("chat_id", name="uq_assistente_ia_conversas_chat_id"),
    )
    op.create_index(
        op.f("ix_assistente_ia_conversas_chat_id"),
        "assistente_ia_conversas",
        ["chat_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_assistente_ia_conversas_usuario_matricula"),
        "assistente_ia_conversas",
        ["usuario_matricula"],
        unique=False,
    )
    op.create_index(
        op.f("ix_assistente_ia_conversas_usuario_id"),
        "assistente_ia_conversas",
        ["usuario_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_assistente_ia_conversas_processo"),
        "assistente_ia_conversas",
        ["processo"],
        unique=False,
    )

    op.create_table(
        "assistente_ia_mensagens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("conversa_id", sa.Integer(), nullable=False),
        sa.Column("role", sqlmodel.sql.sqltypes.AutoString(length=16), nullable=False),
        sa.Column("conteudo", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["conversa_id"],
            ["assistente_ia_conversas.id"],
            name="fk_assistente_ia_mensagens_conversa_id",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_assistente_ia_mensagens_conversa_id"),
        "assistente_ia_mensagens",
        ["conversa_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_assistente_ia_mensagens_role"),
        "assistente_ia_mensagens",
        ["role"],
        unique=False,
    )

    op.execute(
        """
        INSERT INTO assistente_ia_conversas (
            chat_id, usuario_id, usuario_matricula, processo, titulo,
            created_at, updated_at
        )
        SELECT
            openwebui_chat_id,
            (ARRAY_AGG(usuario_id ORDER BY created_at DESC)
                FILTER (WHERE usuario_id IS NOT NULL))[1],
            (ARRAY_AGG(usuario_matricula ORDER BY created_at DESC))[1],
            (ARRAY_AGG(processo ORDER BY created_at ASC)
                FILTER (WHERE processo IS NOT NULL AND processo <> ''))[1],
            (ARRAY_AGG(titulo ORDER BY created_at ASC)
                FILTER (WHERE titulo IS NOT NULL AND titulo <> ''))[1],
            MIN(created_at),
            MAX(COALESCE(updated_at, created_at))
        FROM assistente_ia_logs
        WHERE deleted_at IS NULL
        GROUP BY openwebui_chat_id
        """
    )

    op.execute(
        """
        INSERT INTO assistente_ia_mensagens (
            conversa_id, role, conteudo, created_at, updated_at
        )
        SELECT c.id, 'user', l.pergunta, l.created_at, l.created_at
        FROM assistente_ia_logs l
        JOIN assistente_ia_conversas c ON c.chat_id = l.openwebui_chat_id
        WHERE l.deleted_at IS NULL
          AND l.pergunta IS NOT NULL
          AND l.pergunta <> ''
        ORDER BY l.created_at, l.id
        """
    )

    op.execute(
        """
        INSERT INTO assistente_ia_mensagens (
            conversa_id, role, conteudo, created_at, updated_at
        )
        SELECT
            c.id,
            'assistant',
            l.resposta,
            l.created_at + INTERVAL '1 millisecond',
            l.created_at + INTERVAL '1 millisecond'
        FROM assistente_ia_logs l
        JOIN assistente_ia_conversas c ON c.chat_id = l.openwebui_chat_id
        WHERE l.deleted_at IS NULL
          AND l.resposta IS NOT NULL
          AND l.resposta <> ''
        ORDER BY l.created_at, l.id
        """
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_assistente_ia_mensagens_role"), table_name="assistente_ia_mensagens")
    op.drop_index(
        op.f("ix_assistente_ia_mensagens_conversa_id"),
        table_name="assistente_ia_mensagens",
    )
    op.drop_table("assistente_ia_mensagens")
    op.drop_index(op.f("ix_assistente_ia_conversas_processo"), table_name="assistente_ia_conversas")
    op.drop_index(
        op.f("ix_assistente_ia_conversas_usuario_id"),
        table_name="assistente_ia_conversas",
    )
    op.drop_index(
        op.f("ix_assistente_ia_conversas_usuario_matricula"),
        table_name="assistente_ia_conversas",
    )
    op.drop_index(op.f("ix_assistente_ia_conversas_chat_id"), table_name="assistente_ia_conversas")
    op.drop_table("assistente_ia_conversas")
