"""브랜드명 DB 요청/응답 스키마"""

from pydantic import BaseModel, Field


class BrandCollectResponse(BaseModel):
    keywords_scanned: int
    total_collected: int
    new_brands_added: int
    total_brands_in_db: int


class BrandReportRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)


class BrandReportResponse(BaseModel):
    added: bool
    message: str
