"""initial schema: users, keyword_analyses, product_recommendations

Revision ID: 0001
Revises:
Create Date: 2026-07-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "keyword_analyses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("monthly_searches", sa.Integer(), nullable=False),
        sa.Column("trend_score", sa.Float(), nullable=False),
        sa.Column("competition_score", sa.Float(), nullable=False),
        sa.Column("competition_level", sa.String(length=20), nullable=False),
        sa.Column("opportunity_score", sa.Float(), nullable=False),
        sa.Column("avg_selling_price", sa.Integer(), nullable=False),
        sa.Column("estimated_monthly_sales", sa.Integer(), nullable=False),
        sa.Column("estimated_monthly_revenue", sa.Integer(), nullable=False),
        sa.Column("seasonality", sa.String(length=20), nullable=False),
        sa.Column("risk_level", sa.String(length=20), nullable=False),
        sa.Column("recommendation", sa.String(length=30), nullable=False),
        sa.Column("reasons", sa.JSON(), nullable=False),
        sa.Column("platform", sa.String(length=50), server_default="naver", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_keyword_analyses_keyword", "keyword_analyses", ["keyword"])

    op.create_table(
        "product_recommendations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "keyword_analysis_id",
            sa.Integer(),
            sa.ForeignKey("keyword_analyses.id"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("product_name", sa.String(length=255), nullable=False),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("product_score", sa.Float(), nullable=False),
        sa.Column("match_score", sa.Float(), nullable=False),
        sa.Column("recommended_selling_price", sa.Integer(), nullable=False),
        sa.Column("cost_of_goods", sa.Integer(), nullable=False),
        sa.Column("profit_per_unit", sa.Integer(), nullable=False),
        sa.Column("profit_margin_percent", sa.Float(), nullable=False),
        sa.Column("estimated_monthly_sales", sa.Integer(), nullable=False),
        sa.Column("estimated_monthly_revenue", sa.Integer(), nullable=False),
        sa.Column("estimated_monthly_profit", sa.Integer(), nullable=False),
        sa.Column("risk_factors", sa.JSON(), nullable=False),
        sa.Column("risk_level", sa.String(length=20), server_default="MEDIUM", nullable=False),
        sa.Column("recommendation_reasons", sa.JSON(), nullable=False),
        sa.Column("source_id", sa.String(length=100), nullable=False),
        sa.Column("source_platform", sa.String(length=50), nullable=False),
        sa.Column("cost_price", sa.Integer(), nullable=False),
        sa.Column("shipping_cost", sa.Integer(), nullable=False),
        sa.Column("min_order_quantity", sa.Integer(), nullable=False),
        sa.Column("lead_time_days", sa.Integer(), nullable=False),
        sa.Column("roi_percent", sa.Float(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_product_recommendations_keyword", "product_recommendations", ["keyword"])


def downgrade() -> None:
    op.drop_index("ix_product_recommendations_keyword", table_name="product_recommendations")
    op.drop_table("product_recommendations")
    op.drop_index("ix_keyword_analyses_keyword", table_name="keyword_analyses")
    op.drop_table("keyword_analyses")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
