"""add product_calculations table (margin calculator)

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "product_calculations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "keyword_analysis_id",
            sa.Integer(),
            sa.ForeignKey("keyword_analyses.id"),
            nullable=True,
        ),
        sa.Column("product_name", sa.String(length=255), nullable=False),
        sa.Column("cost", sa.Integer(), nullable=False),
        sa.Column("shipping_cost", sa.Integer(), server_default="0", nullable=False),
        sa.Column("margin_rate", sa.Float(), nullable=False),
        sa.Column("monthly_searches", sa.Integer(), server_default="0", nullable=False),
        sa.Column("selling_price", sa.Integer(), nullable=False),
        sa.Column("monthly_sales_estimate", sa.Integer(), nullable=False),
        sa.Column("monthly_revenue", sa.Integer(), nullable=False),
        sa.Column("monthly_profit", sa.Integer(), nullable=False),
        sa.Column("roi_percent", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(
        "ix_product_calculations_user_id", "product_calculations", ["user_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_product_calculations_user_id", table_name="product_calculations")
    op.drop_table("product_calculations")
