"""키워드 분석 엔드포인트"""

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_user_optional
from app.db.session import get_db
from app.models.user import User
from app.schemas.keyword import (
    AnalyzeAndGenerateRequest,
    AnalyzeAndGenerateResponse,
    KeywordAnalysisHistoryResponse,
    KeywordAnalysisRequest,
    KeywordAnalysisResponse,
    KeywordFetchAutoRequest,
    KeywordFetchAutoResponse,
)
from app.services.keyword_service import analyze_and_save, fetch_auto, get_history
from app.services.product_name_generator import analyze_and_generate

router = APIRouter()


@router.post("/analyze", response_model=KeywordAnalysisResponse)
async def analyze_keyword(
    request: KeywordAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    user_id = current_user.id if current_user else None
    record = await analyze_and_save(db, request, user_id=user_id)
    return record


@router.post("/fetch-auto", response_model=KeywordFetchAutoResponse)
async def fetch_keyword_auto(request: KeywordFetchAutoRequest):
    return await fetch_auto(request.keyword)


@router.get("/history", response_model=KeywordAnalysisHistoryResponse)
async def keyword_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = await get_history(db, user_id=current_user.id)
    return KeywordAnalysisHistoryResponse(items=items, total=len(items))


@router.post("/analyze-and-generate", response_model=AnalyzeAndGenerateResponse)
async def analyze_and_generate_products(request: AnalyzeAndGenerateRequest):
    return await analyze_and_generate(request.keyword)
