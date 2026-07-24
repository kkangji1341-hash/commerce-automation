"""마진 계산기 엔드포인트"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.calculation import (
    MyCalculationsResponse,
    ProductCalculationCreate,
    ProductCalculationResponse,
    ProductCalculationUpdate,
)
from app.services.calculation_service import (
    create_calculation,
    delete_calculation,
    get_calculation_for_user,
    get_my_calculations,
    set_display,
    update_calculation,
)

router = APIRouter()


@router.post("/create", response_model=ProductCalculationResponse, status_code=status.HTTP_201_CREATED)
async def create(
    request: ProductCalculationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await create_calculation(db, request, user_id=current_user.id)


@router.get("/my-calculations", response_model=MyCalculationsResponse)
async def my_calculations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = await get_my_calculations(db, user_id=current_user.id)
    return MyCalculationsResponse(items=items, total=len(items))


@router.put("/{calculation_id}", response_model=ProductCalculationResponse)
async def update(
    calculation_id: int,
    request: ProductCalculationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = await get_calculation_for_user(db, calculation_id, user_id=current_user.id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="계산 결과를 찾을 수 없습니다")
    return await update_calculation(db, record, request)


@router.delete("/{calculation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    calculation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = await get_calculation_for_user(db, calculation_id, user_id=current_user.id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="계산 결과를 찾을 수 없습니다")
    await delete_calculation(db, record)


@router.patch("/{calculation_id}/hide", response_model=ProductCalculationResponse)
async def hide(
    calculation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = await get_calculation_for_user(db, calculation_id, user_id=current_user.id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="계산 결과를 찾을 수 없습니다")
    return await set_display(db, record, is_display=False)
