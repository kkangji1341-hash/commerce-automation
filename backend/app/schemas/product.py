"""상품 추천 요청/응답 스키마"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict

from app.schemas.keyword import KeywordAnalysisRequest


class ProductRecommendRequest(KeywordAnalysisRequest):
    budget: int = 5_000_000
    limit: int = 5


class RecommendedProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    product_name: str
    keyword: str
    product_score: float
    match_score: float
    recommended_selling_price: int
    cost_of_goods: int
    profit_per_unit: int
    profit_margin_percent: float
    estimated_monthly_sales: int
    estimated_monthly_revenue: int
    estimated_monthly_profit: int
    roi_percent: float
    risk_level: str
    risk_factors: List[str]
    recommendation_reasons: List[str]
    source_id: str
    source_platform: str
    cost_price: int
    shipping_cost: int
    min_order_quantity: int
    lead_time_days: int
    created_at: datetime | None = None


class ProductRecommendResponse(BaseModel):
    products: List[RecommendedProductResponse]


class MyProductsResponse(BaseModel):
    items: List[RecommendedProductResponse]
    total: int
