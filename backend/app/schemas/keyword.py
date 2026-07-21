"""키워드 분석 요청/응답 스키마"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class KeywordAnalysisRequest(BaseModel):
    keyword: str
    monthly_searches: int
    cpc_cost: int = 0
    num_top_sellers: int
    avg_listing_price: int
    search_trend: List[int] = Field(..., description="지난 12개월 트렌드 (0-100)")
    review_count_top_10: List[int]
    platform: str = "naver"


class KeywordAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    keyword: str
    monthly_searches: int
    trend_score: float
    competition_score: float
    competition_level: str
    opportunity_score: float
    avg_selling_price: int
    estimated_monthly_sales: int
    estimated_monthly_revenue: int
    seasonality: str
    risk_level: str
    recommendation: str
    reasons: List[str]
    created_at: datetime | None = None


class KeywordAnalysisHistoryResponse(BaseModel):
    items: List[KeywordAnalysisResponse]
    total: int


class KeywordFetchAutoRequest(BaseModel):
    keyword: str


class KeywordFetchAutoResponse(BaseModel):
    keyword: str
    search_trend: List[int]
    trend_source: str
    monthly_searches: int | None
    monthly_searches_source: str | None
    status: str  # success | partial_success | failed
    message: str
