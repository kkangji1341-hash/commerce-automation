"""북마크렛용 이미지 ZIP 릴레이 엔드포인트.

로그인 없이 호출된다 — 북마크렛은 대상 사이트(알리바바 등)의 origin에서
실행되므로 우리 앱의 로그인 토큰을 들고 있지 않다. 대신 개수/용량 제한과
SSRF 방지(app/services/scrape_service.py 참고)로 오남용을 제한한다.
"""

from urllib.parse import quote

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.core.rate_limit import RateLimiter
from app.schemas.scrape import ZipFromUrlsRequest
from app.services.scrape_service import build_zip_from_urls

router = APIRouter()

# 사람이 북마크렛을 클릭하는 빈도를 넘지 않는 선 — 분당 10회, IP당.
_rate_limit = RateLimiter(max_requests=10, window_seconds=60)


@router.post("/zip-from-urls", dependencies=[Depends(_rate_limit)])
async def zip_from_urls(request: ZipFromUrlsRequest):
    zip_bytes, filename = await build_zip_from_urls(request.image_urls, request.filename)
    encoded_filename = quote(filename)
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": (
                f"attachment; filename=\"images.zip\"; filename*=UTF-8''{encoded_filename}"
            )
        },
    )
