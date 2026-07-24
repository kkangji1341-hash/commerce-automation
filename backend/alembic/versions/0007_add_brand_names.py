"""add brand_names table for dynamic brand filtering

Revision ID: 0007
Revises: 0006
Create Date: 2026-07-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "brand_names",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False, server_default="collected"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_brand_names_name", "brand_names", ["name"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_brand_names_name", table_name="brand_names")
    op.drop_table("brand_names")
