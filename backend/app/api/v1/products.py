"""상품 추천 엔드포인트"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_user_optional
from app.db.session import get_db
from app.models.user import User
from app.schemas.product import (
    MyProductsResponse,
    ProductRecommendRequest,
    ProductRecommendResponse,
)
from app.services.product_service import get_my_products, recommend_and_save

router = APIRouter()


@router.post("/recommend", response_model=ProductRecommendResponse)
async def recommend_products(
    request: ProductRecommendRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    user_id = current_user.id if current_user else None
    products = await recommend_and_save(db, request, user_id=user_id)
    return ProductRecommendResponse(products=products)


@router.get("/my-products", response_model=MyProductsResponse)
async def my_products(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = await get_my_products(db, user_id=current_user.id)
    return MyProductsResponse(items=items, total=len(items))
