"""온채널 상세페이지 이미지 수집 요청/응답 스키마"""

from typing import List, Optional

from pydantic import BaseModel, Field


class OnchCollectRequest(BaseModel):
    url: str = Field(..., min_length=1)


class OnchCollectResponse(BaseModel):
    product_name: str
    product_code: Optional[str]
    source_url: str
    images: List[str]
    total_images: int


class OnchZipRequest(BaseModel):
    image_urls: List[str] = Field(..., min_length=1, max_length=50)
    product_name: str = Field(default="상품이미지")
