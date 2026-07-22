"""
상품 추천 시스템
키워드 분석 결과를 바탕으로 최적의 상품을 추천

Phase 4: 위험도 분석 강화 + 리뷰 기반 판매량 추정 + GOLD/SILVER/BRONZE 등급
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
from app.services.keyword_analysis_engine import KeywordAnalysis, KeywordData, CompetitionLevel


class SourcePlatform(str, Enum):
    """상품 소싱처"""
    ALIBABA = "alibaba"
    ALIEXPRESS = "aliexpress"
    DHGATE = "dhgate"
    DROPSHIPPING = "dropshipping"
    DOMESTIC = "domestic"


@dataclass
class SourceProduct:
    """소싱처 상품 정보"""
    source_id: str
    source_platform: SourcePlatform
    product_name: str
    cost_price: int              # 원가
    shipping_cost: int           # 배송비
    min_order_quantity: int      # 최소 주문 수량
    lead_time_days: int          # 배송 기간
    quality_score: float         # 품질 점수 (0-100)
    supplier_rating: float       # 공급처 평가 (0-5)
    stock_quantity: int          # 재고량


@dataclass
class RecommendedProduct:
    """추천 상품"""
    product_name: str
    source_product: SourceProduct
    keyword: str

    # 추천 점수 및 분석
    product_score: float         # 0-100: 이 상품 추천도
    match_score: float           # 0-100: 키워드와의 매칭도

    # 수익성 분석
    recommended_selling_price: int
    cost_of_goods: int          # (원가 + 배송비)
    profit_per_unit: int
    profit_margin_percent: float

    # 예상 성과
    estimated_monthly_sales: int
    estimated_monthly_revenue: int
    estimated_monthly_profit: int

    # 원금 회수 기간 (개월). 월이익이 0 이하면 회수 불가 -> None
    payback_period_months: Optional[float] = None

    # 위험도
    risk_factors: List[str] = field(default_factory=list)
    risk_level: str = "MEDIUM"

    # 시장 분석 (Phase 4: 판매자 수 / 리뷰 수 기반)
    seller_competition_level: str = "MEDIUM"   # 상위 판매자 수 기반 (1-5 LOW / 6-15 MEDIUM / 16+ HIGH)
    market_saturation_level: str = "MEDIUM"    # 리뷰 수 기반 시장 포화도

    # 상품 등급 (Phase 4)
    grade: str = "BRONZE"        # GOLD | SILVER | BRONZE
    grade_reason: str = ""

    # 추천 이유
    recommendation_reasons: List[str] = field(default_factory=list)

    def roi_percent(self) -> float:
        """투자 수익률"""
        return _calculate_roi(
            cost_of_goods=self.cost_of_goods,
            min_order_quantity=self.source_product.min_order_quantity,
            estimated_monthly_profit=self.estimated_monthly_profit,
        )


# ==================== 모듈 레벨 헬퍼 (등급 계산에도 재사용) ====================

def _calculate_roi(cost_of_goods: int, min_order_quantity: int, estimated_monthly_profit: int) -> float:
    initial_investment = cost_of_goods * min_order_quantity
    if initial_investment <= 0:
        return 0.0
    return (estimated_monthly_profit / initial_investment) * 100


def _calculate_payback_period(
    cost_of_goods: int, min_order_quantity: int, estimated_monthly_profit: int
) -> Optional[float]:
    """초기 투자금(원가 * 최소주문수량)을 월이익으로 회수하는 데 걸리는 개월 수"""
    initial_investment = cost_of_goods * min_order_quantity
    if initial_investment <= 0 or estimated_monthly_profit <= 0:
        return None
    return round(initial_investment / estimated_monthly_profit, 1)


def classify_seller_competition(num_top_sellers: int) -> str:
    """
    상위 판매자 수 기반 경쟁도
    1-5명: LOW (독점적) / 6-15명: MEDIUM / 16명 이상: HIGH
    """
    if num_top_sellers <= 5:
        return "LOW"
    elif num_top_sellers <= 15:
        return "MEDIUM"
    else:
        return "HIGH"


def classify_market_saturation(review_count_top_10: List[int]) -> tuple:
    """
    리뷰 수 기반 시장 포화도.
    평균 리뷰가 적으면 아직 기회가 있는 시장, 많으면 이미 경쟁이 심한(포화된) 시장으로 본다.
    기준값(500 / 2000)은 명시적으로 주어지지 않아 임의로 설정한 값이다.
    """
    avg_reviews = sum(review_count_top_10) / len(review_count_top_10) if review_count_top_10 else 0

    if avg_reviews < 500:
        return "LOW", f"평균 리뷰 {avg_reviews:.0f}개 — 아직 기회가 있는 시장"
    elif avg_reviews < 2000:
        return "MEDIUM", f"평균 리뷰 {avg_reviews:.0f}개 — 중간 수준의 경쟁"
    else:
        return "HIGH", f"평균 리뷰 {avg_reviews:.0f}개 — 이미 경쟁이 심한 포화 시장"


def assign_grade(roi_percent: float, risk_level: str) -> tuple:
    """
    상품 등급: GOLD(고ROI+저위험) > SILVER(준수한 ROI, 낮거나 중간 위험) > BRONZE(나머지)
    """
    if risk_level == "LOW" and roi_percent >= 200:
        return "GOLD", f"고ROI({roi_percent:.0f}%) + 저위험도 추천"
    if risk_level in ("LOW", "MEDIUM") and roi_percent >= 80:
        return "SILVER", f"준수한 ROI({roi_percent:.0f}%), {risk_level} 위험도"
    return "BRONZE", f"ROI {roi_percent:.0f}%, {risk_level} 위험도 — 신중 검토 권장"


class ProductRecommendationEngine:
    """상품 추천 엔진"""

    def __init__(self):
        # 테스트용 샘플 상품 데이터베이스
        self.source_products = self._load_sample_products()

    def recommend_products(
        self,
        keyword_analysis: KeywordAnalysis,
        keyword_data: Optional[KeywordData] = None,
        budget: int = 5000000,
        limit: int = 5
    ) -> List[RecommendedProduct]:
        """
        키워드 분석 결과를 바탕으로 상품 추천

        Args:
            keyword_analysis: 키워드 분석 결과
            keyword_data: 키워드 원본 입력값 (상위 판매자 수, 리뷰 수 등 — Phase 4 위험도/판매량 추정에 사용)
            budget: 초기 투자 예산
            limit: 추천 상품 개수

        Returns:
            추천 상품 리스트 (점수 순)
        """

        recommendations = []

        # 각 소싱처 상품에 대해 점수 계산
        for source_product in self.source_products:
            # 필터: 예산 내에서 구매 가능한가?
            if not self._is_affordable(source_product, budget):
                continue

            # 점수 계산
            recommended = self._score_product(
                source_product=source_product,
                keyword=keyword_analysis.keyword,
                keyword_analysis=keyword_analysis,
                keyword_data=keyword_data,
            )

            if recommended:
                recommendations.append(recommended)

        # 점수 순 정렬 (높은 순)
        recommendations.sort(key=lambda x: x.product_score, reverse=True)

        return recommendations[:limit]

    def _score_product(
        self,
        source_product: SourceProduct,
        keyword: str,
        keyword_analysis: KeywordAnalysis,
        keyword_data: Optional[KeywordData] = None,
    ) -> Optional[RecommendedProduct]:
        """
        상품에 점수를 매기고 추천 상품 객체 생성

        점수 구성:
        1. 키워드 매칭도 (30%)
        2. 수익성 (35%)
        3. 공급 안정성 (20%)
        4. 품질 (15%)
        """

        # Step 1: 키워드 매칭도 계산
        match_score = self._calculate_match_score(source_product, keyword)

        # Step 2: 최적 판매가 계산
        recommended_price = self._calculate_selling_price(
            source_product=source_product,
            target_margin=50,  # 50% 마진율 목표
            market_avg_price=keyword_analysis.avg_selling_price
        )

        # Step 3: 수익성 분석
        cost_of_goods = source_product.cost_price + source_product.shipping_cost
        profit_per_unit = recommended_price - cost_of_goods
        profit_margin = (profit_per_unit / recommended_price) * 100

        # 수익성이 마이너스면 제외
        if profit_per_unit <= 0:
            return None

        # Step 4: 예상 판매량 (키워드 분석 + 리뷰 수 기반)
        review_count_top_10 = keyword_data.review_count_top_10 if keyword_data else []
        estimated_monthly_sales = self._estimate_sales(
            source_product=source_product,
            keyword_analysis=keyword_analysis,
            review_count_top_10=review_count_top_10,
        )

        # Step 5: 재무 예상
        estimated_monthly_revenue = estimated_monthly_sales * recommended_price
        estimated_monthly_profit = estimated_monthly_sales * profit_per_unit
        payback_period_months = _calculate_payback_period(
            cost_of_goods, source_product.min_order_quantity, estimated_monthly_profit
        )

        # Step 6: 종합 점수 계산
        product_score = self._calculate_product_score(
            match_score=match_score,
            profit_margin=profit_margin,
            supplier_rating=source_product.supplier_rating,
            quality_score=source_product.quality_score,
            lead_time=source_product.lead_time_days,
            estimated_profit=estimated_monthly_profit
        )

        # Step 7: 위험도 및 이유 분석 (판매자 수/리뷰 수 기반 시장 리스크 포함)
        num_top_sellers = keyword_data.num_top_sellers if keyword_data else 0
        seller_competition_level = classify_seller_competition(num_top_sellers)
        market_saturation_level, saturation_desc = classify_market_saturation(review_count_top_10)

        risk_factors, risk_level = self._assess_risk(
            source_product=source_product,
            profit_margin=profit_margin,
            estimated_sales=estimated_monthly_sales,
            lead_time=source_product.lead_time_days,
            seller_competition_level=seller_competition_level,
            market_saturation_level=market_saturation_level,
            saturation_desc=saturation_desc,
        )

        # Step 8: ROI + 등급 산정
        roi_percent_value = _calculate_roi(
            cost_of_goods, source_product.min_order_quantity, estimated_monthly_profit
        )
        grade, grade_reason = assign_grade(roi_percent_value, risk_level)

        recommendation_reasons = self._generate_reasons(
            source_product=source_product,
            keyword_analysis=keyword_analysis,
            match_score=match_score,
            profit_margin=profit_margin,
            estimated_profit=estimated_monthly_profit,
            risk_level=risk_level
        )

        return RecommendedProduct(
            product_name=source_product.product_name,
            source_product=source_product,
            keyword=keyword,
            product_score=product_score,
            match_score=match_score,
            recommended_selling_price=recommended_price,
            cost_of_goods=cost_of_goods,
            profit_per_unit=profit_per_unit,
            profit_margin_percent=profit_margin,
            estimated_monthly_sales=estimated_monthly_sales,
            estimated_monthly_revenue=estimated_monthly_revenue,
            estimated_monthly_profit=estimated_monthly_profit,
            payback_period_months=payback_period_months,
            risk_factors=risk_factors,
            risk_level=risk_level,
            seller_competition_level=seller_competition_level,
            market_saturation_level=market_saturation_level,
            grade=grade,
            grade_reason=grade_reason,
            recommendation_reasons=recommendation_reasons
        )

    # ==================== 세부 계산 함수 ====================

    def _is_affordable(self, product: SourceProduct, budget: int) -> bool:
        """초기 투자가 예산 내인가?"""
        initial_investment = (product.cost_price + product.shipping_cost) * product.min_order_quantity
        return initial_investment <= budget

    def _calculate_match_score(self, product: SourceProduct, keyword: str) -> float:
        """
        상품이 키워드와 얼마나 잘 맞는가?

        간단한 텍스트 매칭 (실제로는 더 복잡한 ML 사용)
        """

        product_name_lower = product.product_name.lower()
        keyword_lower = keyword.lower()

        # 정확 일치: 100점
        if keyword_lower in product_name_lower or product_name_lower in keyword_lower:
            return 100.0

        # 부분 일치: 70점
        # 예: "wireless" vs "무선"은 번역 문제 (실제로는 ML 사용)
        keywords = keyword_lower.split()
        matches = sum(1 for kw in keywords if kw in product_name_lower)

        if matches > 0:
            return 50 + (matches / len(keywords)) * 50

        # 유사 카테고리 (30점)
        return 30.0

    def _calculate_selling_price(
        self,
        source_product: SourceProduct,
        target_margin: float,  # 목표 마진율 (%)
        market_avg_price: int
    ) -> int:
        """
        최적 판매가 계산

        고려 사항:
        1. 원가 기반 계산 (원가 * (1 + 마진율))
        2. 시장 가격 확인 (경쟁력)
        3. 심리적 가격 설정 (9900, 19900 등)
        """

        cost_of_goods = source_product.cost_price + source_product.shipping_cost

        # 원가 기반 가격
        cost_based_price = int(cost_of_goods * (1 + target_margin / 100))

        # 시장 가격 확인
        # 시장 평균가보다 5-10% 낮게 설정하는 것이 경쟁력 있음
        market_competitive_price = int(market_avg_price * 0.95)

        # 최종 가격 (둘 중 높은 값, 하지만 시장 가격은 존중)
        final_price = max(cost_based_price, market_competitive_price)

        # 심리적 가격 설정 (9900, 19900, 29900 등)
        # 99로 끝나는 가격이 더 많이 팔림
        if final_price % 1000 >= 500:
            final_price = (final_price // 1000 + 1) * 1000 - 100
        else:
            final_price = (final_price // 1000) * 1000 - 100

        return max(cost_of_goods + 1000, final_price)  # 최소한 1000원 이상 마진

    def _estimate_sales(
        self,
        source_product: SourceProduct,
        keyword_analysis: KeywordAnalysis,
        review_count_top_10: List[int],
    ) -> int:
        """
        예상 월판매량 추정 (Phase 4: 리뷰 수 기반 수요 신호 반영)

        요소:
        1. 키워드 기본 판매량 (키워드 분석 엔진 산출값)
        2. 리뷰 수 기반 수요 신호 (상위 상품 리뷰가 많을수록 검증된 시장 수요가 크다고 가정)
        3. 공급처 평판 (높을수록 판매량 ↑)
        4. 배송 기간 (길수록 판매량 ↓, 신뢰도 ↓)
        5. 품질 점수
        """

        base_sales = keyword_analysis.estimated_monthly_sales

        # 리뷰 수 기반 수요 배수: 평균 리뷰가 많을수록(검증된 수요) 배수를 키우되 0.5~2.0배로 캡
        avg_reviews = sum(review_count_top_10) / len(review_count_top_10) if review_count_top_10 else 0
        review_demand_factor = min(2.0, 0.5 + avg_reviews / 2000)
        base_sales = int(base_sales * review_demand_factor)

        # 공급처 평판에 따른 조정
        # 별 4.5개 이상: 100% / 4.0개: 90% / 3.5개: 80%
        rating_factor = max(0.5, source_product.supplier_rating / 5.0)

        # 배송 기간에 따른 조정
        # 7일 이하: 100% / 15일: 85% / 30일: 70%
        if source_product.lead_time_days <= 7:
            time_factor = 1.0
        elif source_product.lead_time_days <= 15:
            time_factor = 0.85
        else:
            time_factor = max(0.6, 1.0 - (source_product.lead_time_days - 15) / 50)

        # 품질 점수에 따른 조정
        quality_factor = source_product.quality_score / 100

        estimated_sales = int(base_sales * rating_factor * time_factor * quality_factor)

        return max(10, estimated_sales)  # 최소 10개

    def _calculate_product_score(
        self,
        match_score: float,
        profit_margin: float,
        supplier_rating: float,
        quality_score: float,
        lead_time: int,
        estimated_profit: int
    ) -> float:
        """
        최종 상품 점수 (0-100)

        가중치:
        - 수익성 (35%): 마진율과 예상 이익
        - 매칭도 (30%): 키워드와의 관련성
        - 공급 안정성 (20%): 공급처 평가 + 배송 기간
        - 품질 (15%): 제품 품질
        """

        # 요소 1: 수익성 (35%)
        # 마진율 30% = 50점, 60% = 100점
        margin_component = min(100, (profit_margin / 30) * 50) * 0.35

        # 요소 2: 매칭도 (30%)
        match_component = match_score * 0.30

        # 요소 3: 공급 안정성 (20%)
        # 공급처 평가 (0-5별) + 배송 기간 고려
        supplier_component = (supplier_rating / 5.0) * 100

        if lead_time <= 7:
            delivery_component = 100
        elif lead_time <= 15:
            delivery_component = 85
        else:
            delivery_component = max(50, 100 - (lead_time - 15) / 2)

        stability_component = (supplier_component * 0.6 + delivery_component * 0.4) * 0.20

        # 요소 4: 품질 (15%)
        quality_component = quality_score * 0.15

        # 종합 점수
        total_score = margin_component + match_component + stability_component + quality_component

        return round(total_score, 1)

    def _assess_risk(
        self,
        source_product: SourceProduct,
        profit_margin: float,
        estimated_sales: int,
        lead_time: int,
        seller_competition_level: str,
        market_saturation_level: str,
        saturation_desc: str,
    ) -> tuple:
        """
        위험도 평가 및 위험 요소 파악 (Phase 4: 판매자 수 / 리뷰 수 기반 시장 리스크 포함)
        """

        risk_factors = []
        risk_score = 0

        # 1. 마진율 위험
        if profit_margin < 20:
            risk_factors.append(f"낮은 마진율 ({profit_margin:.0f}%): 수익성 약함")
            risk_score += 30
        elif profit_margin < 40:
            risk_factors.append(f"중간 마진율 ({profit_margin:.0f}%): 수익 개선 필요")
            risk_score += 10

        # 2. 판매량 위험
        if estimated_sales < 20:
            risk_factors.append("낮은 예상 판매량: 실제 판매 보장 없음")
            risk_score += 20

        # 3. 배송 위험
        if lead_time > 30:
            risk_factors.append(f"긴 배송 기간 ({lead_time}일): 고객 만족도 저하 우려")
            risk_score += 25

        # 4. 공급처 평가
        if source_product.supplier_rating < 4.0:
            risk_factors.append(f"공급처 평가 낮음 ({source_product.supplier_rating}/5.0): 품질 우려")
            risk_score += 20

        # 5. 품질 점수
        if source_product.quality_score < 70:
            risk_factors.append(f"품질 점수 낮음 ({source_product.quality_score}/100): 반품률 우려")
            risk_score += 15

        # 6. 판매자 수 기반 경쟁도 (Phase 4)
        if seller_competition_level == "HIGH":
            risk_factors.append("높은 판매자 경쟁 (상위 판매자 16명 이상): 가격 경쟁 심화 우려")
            risk_score += 25
        elif seller_competition_level == "MEDIUM":
            risk_factors.append("중간 판매자 경쟁 (상위 판매자 6-15명)")
            risk_score += 10

        # 7. 리뷰 수 기반 시장 포화도 (Phase 4)
        if market_saturation_level == "HIGH":
            risk_factors.append(f"시장 포화도 높음: {saturation_desc}")
            risk_score += 20
        elif market_saturation_level == "MEDIUM":
            risk_factors.append(f"시장 포화도 중간: {saturation_desc}")
            risk_score += 8

        # 위험도 분류
        if risk_score >= 60:
            risk_level = "HIGH"
        elif risk_score >= 30:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return risk_factors, risk_level

    def _generate_reasons(
        self,
        source_product: SourceProduct,
        keyword_analysis: KeywordAnalysis,
        match_score: float,
        profit_margin: float,
        estimated_profit: int,
        risk_level: str
    ) -> List[str]:
        """추천 이유 생성"""

        reasons = []

        # 긍정적 이유
        if match_score >= 70:
            reasons.append(f"✓ 키워드와의 높은 매칭도 ({match_score:.0f}%)")

        if profit_margin >= 50:
            reasons.append(f"✓ 우수한 마진율 ({profit_margin:.0f}%)")

        if estimated_profit >= 5000000:
            reasons.append(f"✓ 높은 예상 이익: 월 ₩{estimated_profit:,}")

        if source_product.supplier_rating >= 4.5:
            reasons.append(f"✓ 우수한 공급처 평가 ({source_product.supplier_rating}/5.0)")

        if source_product.quality_score >= 85:
            reasons.append(f"✓ 높은 제품 품질 ({source_product.quality_score}/100)")

        if source_product.lead_time_days <= 7:
            reasons.append(f"✓ 빠른 배송 ({source_product.lead_time_days}일)")

        # 부정적 이유
        if risk_level == "HIGH":
            reasons.append("⚠ 높은 위험도: 사전 테스트 권장")

        if source_product.min_order_quantity > 100:
            reasons.append(f"⚠ 높은 최소 주문 수량 ({source_product.min_order_quantity}개)")

        return reasons

    # ==================== 샘플 데이터 ====================

    def _load_sample_products(self) -> List[SourceProduct]:
        """테스트용 샘플 상품 데이터"""

        return [
            SourceProduct(
                source_id="alibaba_001",
                source_platform=SourcePlatform.ALIBABA,
                product_name="Premium Wireless Bluetooth Earbuds V2",
                cost_price=2500,
                shipping_cost=1000,
                min_order_quantity=50,
                lead_time_days=15,
                quality_score=88,
                supplier_rating=4.7,
                stock_quantity=10000
            ),
            SourceProduct(
                source_id="aliexpress_001",
                source_platform=SourcePlatform.ALIEXPRESS,
                product_name="Wireless Earbuds with Noise Cancellation",
                cost_price=1800,
                shipping_cost=500,
                min_order_quantity=100,
                lead_time_days=20,
                quality_score=75,
                supplier_rating=4.3,
                stock_quantity=5000
            ),
            SourceProduct(
                source_id="dhgate_001",
                source_platform=SourcePlatform.DHGATE,
                product_name="Budget Wireless Earbuds",
                cost_price=1200,
                shipping_cost=300,
                min_order_quantity=200,
                lead_time_days=25,
                quality_score=65,
                supplier_rating=4.0,
                stock_quantity=20000
            ),
            SourceProduct(
                source_id="domestic_001",
                source_platform=SourcePlatform.DOMESTIC,
                product_name="OEM 무선 이어폰 (국내 제조)",
                cost_price=8000,
                shipping_cost=2000,
                min_order_quantity=20,
                lead_time_days=5,
                quality_score=92,
                supplier_rating=4.9,
                stock_quantity=500
            ),
        ]


# ==================== 테스트 ====================

def test_product_recommendation():
    """상품 추천 시스템 테스트"""

    from app.services.keyword_analysis_engine import KeywordAnalysisEngine, KeywordData

    # 키워드 분석 먼저
    engine = KeywordAnalysisEngine()
    keyword_data = KeywordData(
        keyword="무선 이어폰",
        monthly_searches=18500,
        cpc_cost=1200,
        num_top_sellers=25,
        avg_listing_price=59900,
        search_trend=[40, 45, 50, 55, 65, 70, 75, 80, 85, 88, 90, 92],
        review_count_top_10=[500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400],
    )

    keyword_analysis = engine.analyze(keyword_data)

    print("=" * 80)
    print("🎯 상품 추천 시스템 테스트 (Phase 4: 등급/위험도 강화)")
    print("=" * 80)
    print(f"\n📊 키워드: {keyword_analysis.keyword}")
    print(f"   기회점수: {keyword_analysis.opportunity_score}점")
    print(f"   예상 월판매: {keyword_analysis.estimated_monthly_sales}개")

    # 상품 추천
    recommender = ProductRecommendationEngine()
    recommendations = recommender.recommend_products(
        keyword_analysis=keyword_analysis,
        keyword_data=keyword_data,
        budget=5000000,
        limit=5
    )

    print(f"\n💡 추천 상품 ({len(recommendations)}개):")
    print("-" * 80)

    grade_emoji = {"GOLD": "🥇", "SILVER": "🥈", "BRONZE": "🥉"}

    for i, rec in enumerate(recommendations, 1):
        print(f"\n#{i} {grade_emoji.get(rec.grade, '')} [{rec.grade}] {rec.product_name}")
        print(f"    등급 이유:         {rec.grade_reason}")
        print(f"    점수:              {rec.product_score:.1f}/100")
        print(f"    매칭도:            {rec.match_score:.0f}%")
        print(f"    원가:              ₩{rec.cost_of_goods:,}")
        print(f"    추천 판매가:       ₩{rec.recommended_selling_price:,}")
        print(f"    단가 이익:         ₩{rec.profit_per_unit:,} ({rec.profit_margin_percent:.0f}%)")
        print(f"    예상 월판매:       {rec.estimated_monthly_sales}개")
        print(f"    예상 월매출:       ₩{rec.estimated_monthly_revenue:,}")
        print(f"    예상 월이익:       ₩{rec.estimated_monthly_profit:,}")
        print(f"    ROI:               {rec.roi_percent():.0f}%")
        payback_str = f"{rec.payback_period_months}개월" if rec.payback_period_months is not None else "-"
        print(f"    원금 회수 기간:    {payback_str}")
        print(f"    위험도:            {rec.risk_level}")
        print(f"    판매자 경쟁도:     {rec.seller_competition_level}")
        print(f"    시장 포화도:       {rec.market_saturation_level}")

        if rec.recommendation_reasons:
            print(f"    이유:")
            for reason in rec.recommendation_reasons:
                print(f"      {reason}")

        if rec.risk_factors:
            print(f"    주의사항:")
            for factor in rec.risk_factors:
                print(f"      ⚠ {factor}")


if __name__ == "__main__":
    test_product_recommendation()
