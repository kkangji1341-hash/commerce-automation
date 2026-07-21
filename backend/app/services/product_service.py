"""product_recommendation_system.py와 연동하는 서비스"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import RecommendedProduct as RecommendedProductModel
from app.schemas.keyword import KeywordAnalysisRequest
from app.schemas.product import ProductRecommendRequest
from app.services.keyword_analysis_engine import KeywordData
from app.services.keyword_service import analyze_and_save
from app.services.keyword_service import engine as keyword_engine
from app.services.product_recommendation_system import ProductRecommendationEngine

product_engine = ProductRecommendationEngine()


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

    recommendations = product_engine.recommend_products(
        keyword_analysis=analysis,
        budget=request.budget,
        limit=request.limit,
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
            risk_factors=rec.risk_factors,
            risk_level=rec.risk_level,
            recommendation_reasons=rec.recommendation_reasons,
            source_id=rec.source_product.source_id,
            source_platform=rec.source_product.source_platform.value,
            cost_price=rec.source_product.cost_price,
            shipping_cost=rec.source_product.shipping_cost,
            min_order_quantity=rec.source_product.min_order_quantity,
            lead_time_days=rec.source_product.lead_time_days,
            roi_percent=rec.roi_percent(),
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
