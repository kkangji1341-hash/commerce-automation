"""add grade, risk breakdown, payback period to product_recommendations

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "product_recommendations",
        sa.Column("seller_competition_level", sa.String(length=20), server_default="MEDIUM", nullable=False),
    )
    op.add_column(
        "product_recommendations",
        sa.Column("market_saturation_level", sa.String(length=20), server_default="MEDIUM", nullable=False),
    )
    op.add_column(
        "product_recommendations",
        sa.Column("grade", sa.String(length=10), server_default="BRONZE", nullable=False),
    )
    op.add_column(
        "product_recommendations",
        sa.Column("grade_reason", sa.String(length=255), server_default="", nullable=False),
    )
    op.add_column(
        "product_recommendations",
        sa.Column("payback_period_months", sa.Float(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("product_recommendations", "payback_period_months")
    op.drop_column("product_recommendations", "grade_reason")
    op.drop_column("product_recommendations", "grade")
    op.drop_column("product_recommendations", "market_saturation_level")
    op.drop_column("product_recommendations", "seller_competition_level")
