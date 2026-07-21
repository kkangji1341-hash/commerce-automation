"""keyword_analysis_engine.py와 연동하는 서비스"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.keyword import KeywordAnalysis as KeywordAnalysisModel
from app.schemas.keyword import KeywordAnalysisRequest
from app.services.keyword_analysis_engine import KeywordAnalysisEngine, KeywordData

engine = KeywordAnalysisEngine()


async def analyze_and_save(
    db: AsyncSession,
    request: KeywordAnalysisRequest,
    user_id: int | None = None,
) -> KeywordAnalysisModel:
    data = KeywordData(**request.model_dump())
    result = engine.analyze(data)

    record = KeywordAnalysisModel(
        user_id=user_id,
        keyword=result.keyword,
        monthly_searches=result.monthly_searches,
        trend_score=result.trend_score,
        competition_score=result.competition_score,
        competition_level=result.competition_level.value,
        opportunity_score=result.opportunity_score,
        avg_selling_price=result.avg_selling_price,
        estimated_monthly_sales=result.estimated_monthly_sales,
        estimated_monthly_revenue=result.estimated_monthly_revenue,
        seasonality=result.seasonality,
        risk_level=result.risk_level,
        recommendation=result.recommendation,
        reasons=result.reasons,
        platform=request.platform,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_history(
    db: AsyncSession, user_id: int | None = None, limit: int = 20
) -> list[KeywordAnalysisModel]:
    stmt = select(KeywordAnalysisModel).order_by(KeywordAnalysisModel.created_at.desc()).limit(limit)
    if user_id is not None:
        stmt = stmt.where(KeywordAnalysisModel.user_id == user_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())
