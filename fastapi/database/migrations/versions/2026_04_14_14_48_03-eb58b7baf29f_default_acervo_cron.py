"""default acervo cron

Revision ID: eb58b7baf29f
Revises: 95a7576b4cd6
Create Date: 2026-04-14 14:48:03.412257

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "eb58b7baf29f"
down_revision: Union[str, None] = "95a7576b4cd6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Adiciona entry default para o AppSettings (default_acervo_indexador_cron)
    op.execute(
        """
        INSERT INTO app_settings (key, value, created_at, updated_at)
        VALUES (
            'default_acervo_indexador_cron',
            '{"cron_atualizacao": "0 0 */7 * *", "cron_backup": "0 0 * */1 *"}',
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        )
        ON CONFLICT (key) DO UPDATE
        SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP
        """
    )


def downgrade() -> None:
    # Remove entry default para o AppSettings (default_acervo_indexador_cron)
    op.execute(
        """
        DELETE FROM app_settings
        WHERE key = 'default_acervo_indexador_cron'
        """
    )
