"""브랜드명 DB 엔드포인트 — 동적 브랜드 수집/신고"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.brand import BrandCollectResponse, BrandReportRequest, BrandReportResponse
from app.services.brand_service import collect_and_store_brands, report_brand_name

router = APIRouter()


@router.post("/collect", response_model=BrandCollectResponse)
async def collect_brands(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """대표 카테고리 키워드로 네이버 쇼핑을 조회해 브랜드 DB를 갱신한다.

    키워드 89개 × API 호출 1번이라 몇 초~십수 초 내에 끝난다. 자동 주기
    실행 대신 필요할 때 수동으로 호출하는 방식으로 구현했다.
    """
    result = await collect_and_store_brands(db)
    return result


@router.post("/report", response_model=BrandReportResponse)
async def report_brand(
    request: BrandReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    added = await report_brand_name(db, request.name)
    message = "브랜드명을 추가했습니다" if added else "이미 등록되어 있거나 유효하지 않습니다"
    return BrandReportResponse(added=added, message=message)
