"""키워드 분석 요청/응답 스키마"""

import re
from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator

# 공백만 있거나 특수문자만 있는 키워드를 막기 위해, 문자/숫자(한글 포함)가
# 최소 하나는 있어야 한다.
_HAS_ALNUM_RE = re.compile(r"[0-9A-Za-z가-힣]")


def _validate_keyword(v: str) -> str:
    v = v.strip()
    if not v:
        raise ValueError("키워드를 입력해주세요")
    if not _HAS_ALNUM_RE.search(v):
        raise ValueError("키워드에 문자 또는 숫자를 포함해주세요")
    return v


class KeywordAnalysisRequest(BaseModel):
    keyword: str = Field(..., min_length=1)
    monthly_searches: int
    cpc_cost: int = 0
    num_top_sellers: int
    avg_listing_price: int
    search_trend: List[int] = Field(..., description="지난 12개월 트렌드 (0-100)")
    review_count_top_10: List[int]
    platform: str = "naver"

    @field_validator("keyword")
    @classmethod
    def keyword_must_be_meaningful(cls, v: str) -> str:
        return _validate_keyword(v)


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
    keyword: str = Field(..., min_length=1)

    @field_validator("keyword")
    @classmethod
    def keyword_must_be_meaningful(cls, v: str) -> str:
        return _validate_keyword(v)


class KeywordFetchAutoResponse(BaseModel):
    keyword: str
    search_trend: List[int]
    trend_source: str
    monthly_searches: int | None
    monthly_searches_source: str | None
    avg_price: int | None = None
    avg_price_source: str | None = None
    seller_count: int | None = None
    seller_count_source: str | None = None
    status: str  # success | partial_success | failed
    message: str


class AnalyzeAndGenerateRequest(BaseModel):
    keyword: str = Field(..., min_length=1)

    @field_validator("keyword")
    @classmethod
    def keyword_must_be_meaningful(cls, v: str) -> str:
        return _validate_keyword(v)


class KeywordVariantResponse(BaseModel):
    keyword: str
    monthly_searches: int
    click_rate: float
    competition: str
    score: float


class AnalyzeAndGenerateResponse(BaseModel):
    main_keyword: str
    top_variants: List[KeywordVariantResponse]
    generated_product_names: List[str]
