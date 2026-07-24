"""마진 계산기 서비스 — 실제 엑셀(방구석 비즈니스 마진계산기 v5) 수식을 그대로 재현.

매출/ROI/예상 판매량처럼 불확실한 추정치는 다루지 않는다. 사용자가 입력한
원가·배송비·마진율·광고비를 바탕으로 스마트스토어 수수료 구조를 반영해
판매가와 최종 마진만 정확히 계산한다.

엑셀 원본 셀 E4/E5/J5=147840/3000/0.15, E6(판매가)=207120 등 실제 저장된
수식·캐시값과 소수점까지 일치하도록 아래 상수·공식을 역산해 맞췄다.
구입처 배송비(E5)와 판매 배송비 연동 수수료(E20)는 엑셀 자체에서도 원가/마진
계산식에 쓰이지 않는 입력 전용 칸이라, 여기서도 참고용으로만 저장하고
최종 마진 계산에는 포함하지 않는다.
"""

import math

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calculation import ProductCalculation
from app.schemas.calculation import ProductCalculationCreate, ProductCalculationUpdate

STORE_FEE_RATE = 0.0563      # G19: 스마트스토어 결제 수수료
RETURN_FEE_RATE = 0.0363     # G21: 반품/교환 배송비 수수료 (왕복이라 2배 적용)
SHIPPING_FEE_RATE = 0.0363   # G20: 배송비 연동 수수료 (엑셀 E20 — 표시만 되고 마진 계산엔 미반영)
AD_RATE_IN_PRICE = 0.05      # G23: 판매가 산정에 포함되는 광고비 비율 (E23의 광고비 정액과는 별개)
VAT_RATE = 0.10              # G22


def _round_up_to_10(value: float) -> int:
    # 엑셀 ROUNDUP(value, -1) — 반올림이 아니라 항상 10원 단위로 올림.
    value = round(value, 6)
    return int(math.ceil(value / 10)) * 10


def _compute_financials(
    cost: int,
    cost_shipping: int,
    selling_shipping: int,
    margin_rate: float,
    ad_cost: int,
    benefits_cost: int,
) -> dict:
    # base = (원가 + 원가×마진율) × 1.1  — 엑셀 J8/J9/J10에서 공유되는 기준값
    base = cost * (1 + margin_rate) * (1 + VAT_RATE)

    store_fee = base * STORE_FEE_RATE
    return_fee = selling_shipping * RETURN_FEE_RATE * 2
    ad_in_price = base * AD_RATE_IN_PRICE

    # J10: base에 스토어수수료·반품배송비수수료·광고비(5%)까지 얹어 10원 단위로 올림
    selling_price = _round_up_to_10(base + store_fee + return_fee + ad_in_price)

    shipping_fee = selling_shipping * SHIPPING_FEE_RATE  # 참고용 표시 항목 (E20)
    vat = selling_price * VAT_RATE  # E22: 최종 판매가 기준

    # E8: (혜택,수수료,세금 뺀) 마진 — cost_shipping은 실제 엑셀에서도 여기 쓰이지 않는다
    margin_before_ad = selling_price - cost - store_fee - return_fee - vat - benefits_cost
    # E9: 광고비(정액)까지 뺀 최종 마진
    final_margin = round(margin_before_ad - ad_cost)
    # E10: 최종 마진율 = 최종 마진 / 판매가
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
