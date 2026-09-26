"""create_bucket

Revision ID: 64c4c8f988d6
Revises: ec63ee30e8fe
Create Date: 2025-12-18 17:06:37.074110

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "64c4c8f988d6"
down_revision: Union[str, None] = "ec63ee30e8fe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bucket_files",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("file_extension", sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
        sa.Column("file_id", sqlmodel.sql.sqltypes.AutoString(length=36), nullable=False),
        sa.Column("file_name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("bucket_files")
