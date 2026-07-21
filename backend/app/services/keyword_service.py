"""keyword_analysis_engine.py와 연동하는 서비스"""

import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crawlers.keyword_crawler import fetch_keyword_data
from app.models.keyword import KeywordAnalysis as KeywordAnalysisModel
from app.schemas.keyword import KeywordAnalysisRequest, KeywordFetchAutoResponse
from app.services.keyword_analysis_engine import KeywordAnalysisEngine, KeywordData

engine = KeywordAnalysisEngine()
logger = logging.getLogger(__name__)


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


async def fetch_auto(keyword: str) -> KeywordFetchAutoResponse:
    """
    크롤러(keyword_crawler)로 실제 수집 가능한 데이터만 가져온다.
    크롤링 자체가 실패해도(Google Trends 차단/레이트리밋 등) 500을 던지지 않고
    status="failed"로 부분 응답한다.
    """
    try:
        # pytrends는 동기(blocking) HTTP 호출이라 이벤트 루프를 막지 않도록 스레드에서 실행
        result = await asyncio.to_thread(fetch_keyword_data, keyword)
    except Exception as exc:
        logger.warning("keyword auto-fetch failed for %r: %s", keyword, exc)
        return KeywordFetchAutoResponse(
            keyword=keyword,
            search_trend=[],
            trend_source="google_trends",
            monthly_searches=None,
            monthly_searches_source=None,
            status="failed",
            message=f"자동 수집에 실패했습니다: {exc}",
        )

    if result.monthly_searches is not None:
        status = "success"
        message = "모든 데이터가 자동으로 수집되었습니다."
    else:
        status = "partial_success"
        message = "Google Trends 데이터만 수집됨. 월간 검색량은 네이버 API 연동 필요 (직접 입력해주세요)."

    return KeywordFetchAutoResponse(
        keyword=result.keyword,
        search_trend=result.search_trend,
        trend_source=result.trend_source,
        monthly_searches=result.monthly_searches,
        monthly_searches_source=result.monthly_searches_source,
        status=status,
        message=message,
    )
