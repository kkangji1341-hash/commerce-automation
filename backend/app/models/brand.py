"""동적으로 수집/신고된 브랜드명 — 상품명 자동 생성 시 필터링에 쓰인다."""

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class BrandName(Base):
    __tablename__ = "brand_names"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    source: Mapped[str] = mapped_column(String(50), default="collected")  # collected | reported
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
