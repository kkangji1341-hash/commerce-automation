"""상품 추천 결과 모델 — product_recommendation_system.RecommendedProduct dataclass와 1:1 매핑"""

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class RecommendedProduct(Base):
    __tablename__ = "product_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    keyword_analysis_id: Mapped[int] = mapped_column(ForeignKey("keyword_analyses.id"))
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    # RecommendedProduct dataclass 필드
    product_name: Mapped[str] = mapped_column(String(255))
    keyword: Mapped[str] = mapped_column(String(255), index=True)

    product_score: Mapped[float] = mapped_column(Float)
    match_score: Mapped[float] = mapped_column(Float)

    recommended_selling_price: Mapped[int] = mapped_column(Integer)
    cost_of_goods: Mapped[int] = mapped_column(Integer)
    profit_per_unit: Mapped[int] = mapped_column(Integer)
    profit_margin_percent: Mapped[float] = mapped_column(Float)

    estimated_monthly_sales: Mapped[int] = mapped_column(Integer)
    estimated_monthly_revenue: Mapped[int] = mapped_column(Integer)
    estimated_monthly_profit: Mapped[int] = mapped_column(Integer)

    risk_factors: Mapped[list] = mapped_column(JSON, default=list)
    risk_level: Mapped[str] = mapped_column(String(20), default="MEDIUM")
    recommendation_reasons: Mapped[list] = mapped_column(JSON, default=list)

    # Phase 4: 시장 리스크 세분화 + 등급 시스템
    seller_competition_level: Mapped[str] = mapped_column(String(20), default="MEDIUM")
    market_saturation_level: Mapped[str] = mapped_column(String(20), default="MEDIUM")
    grade: Mapped[str] = mapped_column(String(10), default="BRONZE")
    grade_reason: Mapped[str] = mapped_column(String(255), default="")
    payback_period_months: Mapped[float | None] = mapped_column(Float, nullable=True)

    # SourceProduct 요약 (source_product 필드를 평탄화해서 저장)
    source_id: Mapped[str] = mapped_column(String(100))
    source_platform: Mapped[str] = mapped_column(String(50))
    cost_price: Mapped[int] = mapped_column(Integer)
    shipping_cost: Mapped[int] = mapped_column(Integer)
    min_order_quantity: Mapped[int] = mapped_column(Integer)
    lead_time_days: Mapped[int] = mapped_column(Integer)
    # True면 cost_price 등 소싱 필드가 네이버 판매가 기반 추정치임 (실제 소싱처 데이터 아님)
    is_estimated: Mapped[bool] = mapped_column(Boolean, default=False)

    # roi_percent()는 dataclass에서 메서드로 계산되는 값이라 저장 시점 스냅샷으로 보관
    roi_percent: Mapped[float] = mapped_column(Float, default=0.0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    keyword_analysis = relationship("KeywordAnalysis", back_populates="product_recommendations")
