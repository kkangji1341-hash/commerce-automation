"""마진 계산기 저장 결과 모델 — 원가 → 판매가(수수료/부가세 반영) 계산 결과"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ProductCalculation(Base):
    __tablename__ = "product_calculations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    keyword_analysis_id: Mapped[int | None] = mapped_column(
        ForeignKey("keyword_analyses.id"), nullable=True
    )

    product_name: Mapped[str] = mapped_column(String(255))

    # 입력값
    cost: Mapped[int] = mapped_column(Integer)  # 원가
    cost_shipping: Mapped[int] = mapped_column(Integer, default=3000)  # 구입처 배송비
    selling_shipping: Mapped[int] = mapped_column(Integer, default=3000)  # 판매 배송비
    margin_rate: Mapped[float] = mapped_column(Float)  # 0.15 = 15%
    ad_cost: Mapped[int] = mapped_column(Integer, default=50)  # 광고비
    benefits_cost: Mapped[int] = mapped_column(Integer, default=0)  # 스토어 혜택 비용

    # 계산 결과
    selling_price: Mapped[int] = mapped_column(Integer)  # 최종 판매가
    store_fee: Mapped[float] = mapped_column(Float)  # 스토어 수수료 (5.63%)
    shipping_fee: Mapped[float] = mapped_column(Float)  # 배송비 연동 수수료 (3.63%)
    return_fee: Mapped[float] = mapped_column(Float)  # 반품 배송비 수수료 (3.63% x 2)
    vat: Mapped[float] = mapped_column(Float)  # 부가세 (10%)
    final_margin: Mapped[int] = mapped_column(Integer)  # 최종 마진
    final_margin_rate: Mapped[float] = mapped_column(Float)  # 최종 마진율

    is_display: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    keyword_analysis = relationship("KeywordAnalysis")
