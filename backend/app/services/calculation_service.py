"""마진 계산기 서비스 — 사용자가 직접 입력한 원가/마진율로 판매가·ROI를 계산해 저장한다.

상품 추천 엔진(product_recommendation_system)과 달리 원가를 추정하지 않는다 —
사용자가 실제 아는 원가를 입력하므로 계산 결과가 추정치가 아니라 정확하다
(단, monthly_sales_estimate는 검색량 기반 추정이라는 한계는 동일하게 있음).
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calculation import ProductCalculation
from app.schemas.calculation import ProductCalculationCreate, ProductCalculationUpdate

# 검색량 대비 월 판매량 전환율. keyword_analysis_engine의 기본 전환율(1~3%)과
# 별개로, 마진 계산기는 사용자가 이미 구체적인 상품/원가를 정한 상태라
# 좀 더 낙관적인 5%를 기본값으로 쓴다.
SALES_CONVERSION_RATE = 0.05


def _compute_financials(
    cost: int, shipping_cost: int, margin_rate: float, monthly_searches: int
) -> dict:
    selling_price = round(cost * (1 + margin_rate))
    monthly_sales_estimate = round(monthly_searches * SALES_CONVERSION_RATE)
    monthly_revenue = selling_price * monthly_sales_estimate
    unit_profit = selling_price - cost - shipping_cost
    monthly_profit = unit_profit * monthly_sales_estimate
    roi_percent = (unit_profit / cost) * 100 if cost > 0 else 0.0

    return {
        "selling_price": selling_price,
        "monthly_sales_estimate": monthly_sales_estimate,
        "monthly_revenue": monthly_revenue,
        "monthly_profit": monthly_profit,
        "roi_percent": roi_percent,
    }


async def create_calculation(
    db: AsyncSession, request: ProductCalculationCreate, user_id: int
) -> ProductCalculation:
    financials = _compute_financials(
        cost=request.cost,
        shipping_cost=request.shipping_cost,
        margin_rate=request.margin_rate,
        monthly_searches=request.monthly_searches,
    )
    record = ProductCalculation(
        user_id=user_id,
        keyword_analysis_id=request.keyword_analysis_id,
        product_name=request.product_name,
        cost=request.cost,
        shipping_cost=request.shipping_cost,
        margin_rate=request.margin_rate,
        monthly_searches=request.monthly_searches,
        **financials,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_my_calculations(
    db: AsyncSession, user_id: int, limit: int = 50
) -> list[ProductCalculation]:
    stmt = (
        select(ProductCalculation)
        .where(ProductCalculation.user_id == user_id)
        .order_by(ProductCalculation.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_calculation_for_user(
    db: AsyncSession, calculation_id: int, user_id: int
) -> ProductCalculation | None:
    stmt = select(ProductCalculation).where(
        ProductCalculation.id == calculation_id, ProductCalculation.user_id == user_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_calculation(
    db: AsyncSession, record: ProductCalculation, request: ProductCalculationUpdate
) -> ProductCalculation:
    financials = _compute_financials(
        cost=request.cost,
        shipping_cost=request.shipping_cost,
        margin_rate=request.margin_rate,
        monthly_searches=request.monthly_searches,
    )
    record.product_name = request.product_name
    record.cost = request.cost
    record.shipping_cost = request.shipping_cost
    record.margin_rate = request.margin_rate
    record.monthly_searches = request.monthly_searches
    for key, value in financials.items():
        setattr(record, key, value)

    await db.commit()
    await db.refresh(record)
    return record


async def delete_calculation(db: AsyncSession, record: ProductCalculation) -> None:
    await db.delete(record)
    await db.commit()
