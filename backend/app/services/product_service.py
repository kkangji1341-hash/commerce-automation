"""product_recommendation_system.py와 연동하는 서비스"""

import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crawlers.keyword_crawler import fetch_naver_shopping_products
from app.models.product import RecommendedProduct as RecommendedProductModel
from app.schemas.keyword import KeywordAnalysisRequest
from app.schemas.product import ProductRecommendRequest
from app.services.keyword_analysis_engine import KeywordData
from app.services.keyword_service import analyze_and_save
from app.services.keyword_service import engine as keyword_engine
from app.services.product_recommendation_system import (
    ProductRecommendationEngine,
    naver_product_to_source_product,
)

product_engine = ProductRecommendationEngine()
logger = logging.getLogger(__name__)


async def _fetch_dynamic_source_products(keyword: str):
    """
    정적 카탈로그(무선이어폰 4개)에 없는 카테고리를 위해, 네이버 판매가 기반
    추정 후보를 가져온다. 네이버 호출이 실패해도(크레덴셜 없음/타임아웃/장애)
    빈 리스트를 반환해 정적 카탈로그 기반 추천은 그대로 동작하게 한다.
    """
    try:
        # requests는 동기(blocking) 호출이라 이벤트 루프를 막지 않도록 스레드에서 실행
        raw_items = await asyncio.to_thread(fetch_naver_shopping_products, keyword, 10)
    except Exception:
        logger.exception("네이버 판매가 기반 동적 상품 조회 실패: keyword=%r", keyword)
        return []
    return [naver_product_to_source_product(item, keyword) for item in raw_items]


async def recommend_and_save(
    db: AsyncSession,
    request: ProductRecommendRequest,
    user_id: int | None = None,
) -> list[RecommendedProductModel]:
    keyword_fields = request.model_dump(exclude={"budget", "limit"})
    keyword_record = await analyze_and_save(
        db, request=KeywordAnalysisRequest(**keyword_fields), user_id=user_id
    )

    keyword_data = KeywordData(**keyword_fields)
    analysis = keyword_engine.analyze(keyword_data)

    dynamic_products = await _fetch_dynamic_source_products(request.keyword)

    recommendations = product_engine.recommend_products(
        keyword_analysis=analysis,
        keyword_data=keyword_data,
        budget=request.budget,
        limit=request.limit,
        dynamic_products=dynamic_products,
    )

    saved: list[RecommendedProductModel] = []
    for rec in recommendations:
        record = RecommendedProductModel(
            keyword_analysis_id=keyword_record.id,
            user_id=user_id,
            product_name=rec.product_name,
            keyword=rec.keyword,
            product_score=rec.product_score,
            match_score=rec.match_score,
            recommended_selling_price=rec.recommended_selling_price,
            cost_of_goods=rec.cost_of_goods,
            profit_per_unit=rec.profit_per_unit,
            profit_margin_percent=rec.profit_margin_percent,
            estimated_monthly_sales=rec.estimated_monthly_sales,
            estimated_monthly_revenue=rec.estimated_monthly_revenue,
            estimated_monthly_profit=rec.estimated_monthly_profit,
            payback_period_months=rec.payback_period_months,
            risk_factors=rec.risk_factors,
            risk_level=rec.risk_level,
            seller_competition_level=rec.seller_competition_level,
            market_saturation_level=rec.market_saturation_level,
            grade=rec.grade,
            grade_reason=rec.grade_reason,
            recommendation_reasons=rec.recommendation_reasons,
            source_id=rec.source_product.source_id,
            source_platform=rec.source_product.source_platform.value,
            cost_price=rec.source_product.cost_price,
            shipping_cost=rec.source_product.shipping_cost,
            min_order_quantity=rec.source_product.min_order_quantity,
            lead_time_days=rec.source_product.lead_time_days,
            roi_percent=rec.roi_percent(),
            is_estimated=rec.source_product.is_estimated,
        )
        db.add(record)
        saved.append(record)

    await db.commit()
    for record in saved:
        await db.refresh(record)
    return saved


async def get_my_products(
    db: AsyncSession, user_id: int, limit: int = 20
) -> list[RecommendedProductModel]:
    stmt = (
        select(RecommendedProductModel)
        .where(RecommendedProductModel.user_id == user_id)
        .order_by(RecommendedProductModel.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
