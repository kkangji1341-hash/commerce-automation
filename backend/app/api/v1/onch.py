"""온채널 상세페이지 이미지 수집 엔드포인트"""

from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response

from app.api.deps import get_current_user
from app.crawlers.onch_crawler import InvalidOnchUrlError
from app.models.user import User
from app.schemas.onch import OnchCollectRequest, OnchCollectResponse, OnchZipRequest
from app.services.onch_service import build_images_zip, collect_product_details

router = APIRouter()


@router.post("/collect", response_model=OnchCollectResponse)
async def collect(
    request: OnchCollectRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = await collect_product_details(request.url)
    except InvalidOnchUrlError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="상세페이지를 불러오지 못했습니다")
    return result


@router.post("/download-zip")
async def download_zip(
    request: OnchZipRequest,
    current_user: User = Depends(get_current_user),
):
    zip_bytes, filename = await build_images_zip(request.image_urls, request.product_name)
    # Content-Disposition 헤더는 latin-1만 허용해서 한글 파일명은 RFC 5987
    # filename*= 형식으로 percent-encode하고, 구형 클라이언트를 위한 ASCII
    # filename= 폴백도 함께 준다.
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
