"""마진 계산기 저장 결과 모델"""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
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
    cost: Mapped[int] = mapped_column(Integer)
    shipping_cost: Mapped[int] = mapped_column(Integer, default=0)
    margin_rate: Mapped[float] = mapped_column(Float)  # 1.0 = 100%
    monthly_searches: Mapped[int] = mapped_column(Integer, default=0)

    selling_price: Mapped[int] = mapped_column(Integer)
    monthly_sales_estimate: Mapped[int] = mapped_column(Integer)
    monthly_revenue: Mapped[int] = mapped_column(Integer)
    monthly_profit: Mapped[int] = mapped_column(Integer)
    roi_percent: Mapped[float] = mapped_column(Float)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    keyword_analysis = relationship("KeywordAnalysis")
