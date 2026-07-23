"""마진 계산기 요청/응답 스키마"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductCalculationCreate(BaseModel):
    keyword_analysis_id: int | None = None
    product_name: str = Field(..., min_length=1)
    cost: int = Field(..., gt=0)
    shipping_cost: int = 0
    margin_rate: float = Field(..., ge=0, description="1.0 = 100%")
    monthly_searches: int = Field(..., ge=0, description="판매량 추정에 쓸 월간 검색량")


class ProductCalculationUpdate(BaseModel):
    product_name: str = Field(..., min_length=1)
    cost: int = Field(..., gt=0)
    shipping_cost: int = 0
    margin_rate: float = Field(..., ge=0)
    monthly_searches: int = Field(..., ge=0)


class ProductCalculationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    keyword_analysis_id: int | None = None
    product_name: str
    cost: int
    shipping_cost: int
    margin_rate: float
    monthly_searches: int
    selling_price: int
    monthly_sales_estimate: int
    monthly_revenue: int
    monthly_profit: int
    roi_percent: float
    created_at: datetime | None = None


class MyCalculationsResponse(BaseModel):
    items: list[ProductCalculationResponse]
    total: int
