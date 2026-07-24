"""마진 계산기 서비스 — 엑셀식 "원가 입력 → 판매가 출력" 계산.

매출/ROI/예상 판매량처럼 불확실한 추정치는 다루지 않는다. 사용자가 입력한
원가·배송비·마진율·광고비를 바탕으로 스마트스토어 수수료 구조를 반영해
판매가와 최종 마진만 정확히 계산한다.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calculation import ProductCalculation
from app.schemas.calculation import ProductCalculationCreate, ProductCalculationUpdate

STORE_FEE_RATE = 0.0563   # 스마트스토어 결제 수수료
SHIPPING_FEE_RATE = 0.0363  # 배송비 연동 수수료
VAT_RATE = 0.10


def _round_to_10(value: float) -> int:
    return int(round(value / 10)) * 10


def _compute_financials(
    cost: int,
    cost_shipping: int,
    selling_shipping: int,
    margin_rate: float,
    ad_cost: int,
    benefits_cost: int,
) -> dict:
    # 판매가는 원가(원가 자체)에만 마진율과 부가세를 얹어 계산한다 — 구입처 배송비는
    # 판매가 산정에는 관여하지 않고, 최종 마진을 깎는 비용으로만 별도 반영한다.
    selling_price = _round_to_10(cost * (1 + margin_rate) * (1 + VAT_RATE))

    store_fee = selling_price * STORE_FEE_RATE
    shipping_fee = selling_shipping * SHIPPING_FEE_RATE
    return_fee = selling_shipping * SHIPPING_FEE_RATE * 2
    vat = selling_price * VAT_RATE

    final_margin = round(
        selling_price
        - cost
        - cost_shipping
        - store_fee
        - shipping_fee
        - return_fee
        - vat
        - ad_cost
        - benefits_cost
    )
    final_margin_rate = (final_margin / selling_price) if selling_price > 0 else 0.0

    return {
        "selling_price": selling_price,
        "store_fee": store_fee,
        "shipping_fee": shipping_fee,
        "return_fee": return_fee,
        "vat": vat,
        "final_margin": final_margin,
        "final_margin_rate": final_margin_rate,
    }


async def create_calculation(
    db: AsyncSession, request: ProductCalculationCreate, user_id: int
) -> ProductCalculation:
    financials = _compute_financials(
        cost=request.cost,
        cost_shipping=request.cost_shipping,
        selling_shipping=request.selling_shipping,
        margin_rate=request.margin_rate,
        ad_cost=request.ad_cost,
        benefits_cost=request.benefits_cost,
    )
    record = ProductCalculation(
        user_id=user_id,
        keyword_analysis_id=request.keyword_analysis_id,
        product_name=request.product_name,
        cost=request.cost,
        cost_shipping=request.cost_shipping,
        selling_shipping=request.selling_shipping,
        margin_rate=request.margin_rate,
        ad_cost=request.ad_cost,
        benefits_cost=request.benefits_cost,
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
        .where(ProductCalculation.user_id == user_id, ProductCalculation.is_display.is_(True))
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
        cost_shipping=request.cost_shipping,
        selling_shipping=request.selling_shipping,
        margin_rate=request.margin_rate,
        ad_cost=request.ad_cost,
        benefits_cost=request.benefits_cost,
    )
    record.product_name = request.product_name
    record.cost = request.cost
    record.cost_shipping = request.cost_shipping
    record.selling_shipping = request.selling_shipping
    record.margin_rate = request.margin_rate
    record.ad_cost = request.ad_cost
    record.benefits_cost = request.benefits_cost
    for key, value in financials.items():
        setattr(record, key, value)

    await db.commit()
    await db.refresh(record)
    return record


async def set_display(db: AsyncSession, record: ProductCalculation, is_display: bool) -> ProductCalculation:
    record.is_display = is_display
    await db.commit()
    await db.refresh(record)
    return record


async def delete_calculation(db: AsyncSession, record: ProductCalculation) -> None:
    await db.delete(record)
    await db.commit()
