"""v1 API 라우터 통합"""

from fastapi import APIRouter

from app.api.v1 import auth, keywords, products

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(keywords.router, prefix="/keywords", tags=["keywords"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
