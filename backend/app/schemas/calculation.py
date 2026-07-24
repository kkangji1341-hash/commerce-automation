"""마진 계산기 요청/응답 스키마 — 엑셀식 원가 → 판매가 계산"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductCalculationCreate(BaseModel):
    keyword_analysis_id: int | None = None
    product_name: str = Field(..., min_length=1)
    cost: int = Field(..., gt=0)
    cost_shipping: int = 3000
    selling_shipping: int = 3000
    margin_rate: float = Field(..., ge=0, description="0.15 = 15%")
    ad_cost: int = 50
    benefits_cost: int = 0


class ProductCalculationUpdate(BaseModel):
    product_name: str = Field(..., min_length=1)
    cost: int = Field(..., gt=0)
    cost_shipping: int = 3000
    selling_shipping: int = 3000
    margin_rate: float = Field(..., ge=0)
    ad_cost: int = 50
    benefits_cost: int = 0


class ProductCalculationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    keyword_analysis_id: int | None = None
    product_name: str
    cost: int
    cost_shipping: int
    selling_shipping: int
    margin_rate: float
    ad_cost: int
    benefits_cost: int
    selling_price: int
    store_fee: float
    shipping_fee: float
    return_fee: float
    vat: float
    final_margin: int
    final_margin_rate: float
    is_display: bool
    created_at: datetime | None = None


class MyCalculationsResponse(BaseModel):
    items: list[ProductCalculationResponse]
    total: int
