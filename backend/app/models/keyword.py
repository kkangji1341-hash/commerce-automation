"""키워드 분석 결과 모델 — keyword_analysis_engine.KeywordAnalysis dataclass와 1:1 매핑"""

from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class KeywordAnalysis(Base):
    __tablename__ = "keyword_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    # KeywordAnalysis dataclass 필드
    keyword: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    monthly_searches: Mapped[int] = mapped_column(Integer)
    trend_score: Mapped[float] = mapped_column(Float)
    competition_score: Mapped[float] = mapped_column(Float)
    competition_level: Mapped[str] = mapped_column(String(20))
    opportunity_score: Mapped[float] = mapped_column(Float)
    avg_selling_price: Mapped[int] = mapped_column(Integer)
    estimated_monthly_sales: Mapped[int] = mapped_column(Integer)
    estimated_monthly_revenue: Mapped[int] = mapped_column(Integer)
    seasonality: Mapped[str] = mapped_column(String(20))
    risk_level: Mapped[str] = mapped_column(String(20))
    recommendation: Mapped[str] = mapped_column(String(30))
    reasons: Mapped[list] = mapped_column(JSON, default=list)

    # 저장용 부가 필드 (dataclass엔 없음)
    platform: Mapped[str] = mapped_column(String(50), default="naver")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="keyword_analyses")
    product_recommendations = relationship(
        "RecommendedProduct", back_populates="keyword_analysis"
    )
