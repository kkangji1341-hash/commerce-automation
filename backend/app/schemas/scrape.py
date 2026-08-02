"""북마크렛이 수집한 이미지 URL 목록을 서버가 대신 내려받아 ZIP으로 묶어주는 요청 스키마"""

from typing import List

from pydantic import BaseModel, Field


class ZipFromUrlsRequest(BaseModel):
    image_urls: List[str] = Field(..., min_length=1, max_length=60)
    filename: str = Field(default="images")
