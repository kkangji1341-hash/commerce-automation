"""redesign product_calculations to excel-style cost->price model

Revision ID: 0006
Revises: 0005
Create Date: 2026-07-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 매출/ROI 중심 컬럼 제거 (완전 재설계 — 원가->판매가 계산기로 전환)
    op.drop_column("product_calculations", "shipping_cost")
    op.drop_column("product_calculations", "monthly_searches")
    op.drop_column("product_calculations", "monthly_sales_estimate")
    op.drop_column("product_calculations", "monthly_revenue")
    op.drop_column("product_calculations", "monthly_profit")
    op.drop_column("product_calculations", "roi_percent")

    # 새 입력 컬럼
    op.add_column(
        "product_calculations",
        sa.Column("cost_shipping", sa.Integer(), server_default="3000", nullable=False),
    )
    op.add_column(
        "product_calculations",
        sa.Column("selling_shipping", sa.Integer(), server_default="3000", nullable=False),
    )
    op.add_column(
        "product_calculations",
        sa.Column("ad_cost", sa.Integer(), server_default="50", nullable=False),
    )
    op.add_column(
        "product_calculations",
        sa.Column("benefits_cost", sa.Integer(), server_default="0", nullable=False),
    )

    # 새 계산 결과 컬럼
    op.add_column(
        "product_calculations",
        sa.Column("store_fee", sa.Float(), server_default="0", nullable=False),
    )
    op.add_column(
        "product_calculations",
        sa.Column("shipping_fee", sa.Float(), server_default="0", nullable=False),
    )
    op.add_column(
        "product_calculations",
        sa.Column("return_fee", sa.Float(), server_default="0", nullable=False),
    )
    op.add_column(
        "product_calculations",
        sa.Column("vat", sa.Float(), server_default="0", nullable=False),
    )
    op.add_column(
        "product_calculations",
        sa.Column("final_margin", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "product_calculations",
        sa.Column("final_margin_rate", sa.Float(), server_default="0", nullable=False),
    )
    op.add_column(
        "product_calculations",
        sa.Column("is_display", sa.Boolean(), server_default=sa.true(), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("product_calculations", "is_display")
    op.drop_column("product_calculations", "final_margin_rate")
    op.drop_column("product_calculations", "final_margin")
    op.drop_column("product_calculations", "vat")
    op.drop_column("product_calculations", "return_fee")
    op.drop_column("product_calculations", "shipping_fee")
    op.drop_column("product_calculations", "store_fee")
    op.drop_column("product_calculations", "benefits_cost")
    op.drop_column("product_calculations", "ad_cost")
    op.drop_column("product_calculations", "selling_shipping")
    op.drop_column("product_calculations", "cost_shipping")

    op.add_column(
        "product_calculations", sa.Column("roi_percent", sa.Float(), server_default="0", nullable=False)
    )
    op.add_column(
        "product_calculations", sa.Column("monthly_profit", sa.Integer(), server_default="0", nullable=False)
    )
    op.add_column(
        "product_calculations", sa.Column("monthly_revenue", sa.Integer(), server_default="0", nullable=False)
    )
    op.add_column(
        "product_calculations",
        sa.Column("monthly_sales_estimate", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "product_calculations", sa.Column("monthly_searches", sa.Integer(), server_default="0", nullable=False)
    )
    op.add_column(
        "product_calculations", sa.Column("shipping_cost", sa.Integer(), server_default="0", nullable=False)
    )
