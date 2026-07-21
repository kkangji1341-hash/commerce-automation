"""
키워드 분석 엔진
상품 선정의 핵심: 트렌드 + 경쟁도 + 수익성 분석
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import math
from enum import Enum


class CompetitionLevel(str, Enum):
    """경쟁도 수준"""
    LOW = "LOW"          # 0-30: 경쟁 적음 (침투 용이)
    MEDIUM = "MEDIUM"    # 30-70: 중간 경쟁
    HIGH = "HIGH"        # 70-100: 높은 경쟁 (차별화 필요)


@dataclass
class KeywordData:
    """키워드 원본 데이터"""
    keyword: str
    monthly_searches: int           # 월간 검색량
    cpc_cost: int                   # Cost Per Click (원)
    num_top_sellers: int            # 상위 판매자 수 (0-100+)
    avg_listing_price: int          # 평균 판매가
    search_trend: List[int]         # 지난 12개월 트렌드 (0-100)
    review_count_top_10: List[int]  # 상위 10개 상품의 리뷰 수
    platform: str = "naver"


@dataclass
class KeywordAnalysis:
    """키워드 분석 결과"""
    keyword: str
    monthly_searches: int
    
    # 핵심 지표
    trend_score: float              # 0-100: 높을수록 뜨는 상품
    competition_score: float        # 0-100: 높을수록 경쟁 심함
    competition_level: CompetitionLevel
    opportunity_score: float        # 0-100: 종합 기회도
    
    # 수익성 분석
    avg_selling_price: int
    estimated_monthly_sales: int    # 예상 월판매량
    estimated_monthly_revenue: int  # 예상 월매출
    
    # 상세 분석
    seasonality: str                # 계절성: YEAR_ROUND, SEASONAL, PEAK
    risk_level: str                 # 위험도: LOW, MEDIUM, HIGH
    recommendation: str             # 추천 여부: HIGHLY_RECOMMENDED, RECOMMENDED, CAUTION, NOT_RECOMMENDED
    
    # 상세 이유
    reasons: List[str]              # 분석 결과 설명


class KeywordAnalysisEngine:
    """키워드 분석 엔진 (핵심 로직)"""
    
    def __init__(self):
        self.min_opportunity_for_recommendation = 50  # 기회점수 50점 이상만 추천
    
    def analyze(self, data: KeywordData) -> KeywordAnalysis:
        """
        키워드를 종합적으로 분석하고 점수 계산
        
        핵심 알고리즘:
        1. 트렌드 분석 (지난 12개월 데이터)
        2. 경쟁도 분석 (판매자 수 + 리뷰 수)
        3. 수익성 분석 (가격 + 검색량)
        4. 종합 기회점수 계산
        """
        
        # Step 1: 트렌드 분석
        trend_score = self._calculate_trend_score(data.search_trend)
        
        # Step 2: 경쟁도 분석
        competition_score = self._calculate_competition_score(
            data.num_top_sellers,
            data.review_count_top_10
        )
        competition_level = self._get_competition_level(competition_score)
        
        # Step 3: 시즈널리티
        seasonality = self._analyze_seasonality(data.search_trend)
        
        # Step 4: 수익성 분석
        estimated_monthly_sales = self._estimate_monthly_sales(
            data.monthly_searches,
            data.num_top_sellers,
            competition_level
        )
        estimated_monthly_revenue = estimated_monthly_sales * data.avg_listing_price
        
        # Step 5: 위험도 평가
        risk_level = self._assess_risk(
            competition_level,
            trend_score,
            seasonality
        )
        
        # Step 6: 종합 기회점수 (가장 중요!)
        opportunity_score = self._calculate_opportunity_score(
            trend_score=trend_score,
            competition_score=competition_score,
            monthly_searches=data.monthly_searches,
            estimated_revenue=estimated_monthly_revenue
        )
        
        # Step 7: 추천도 및 이유
        recommendation, reasons = self._make_recommendation(
            opportunity_score=opportunity_score,
            trend_score=trend_score,
            competition_level=competition_level,
            risk_level=risk_level,
            seasonality=seasonality,
            estimated_revenue=estimated_monthly_revenue
        )
        
        return KeywordAnalysis(
            keyword=data.keyword,
            monthly_searches=data.monthly_searches,
            trend_score=trend_score,
            competition_score=competition_score,
            competition_level=competition_level,
            opportunity_score=opportunity_score,
            avg_selling_price=data.avg_listing_price,
            estimated_monthly_sales=estimated_monthly_sales,
            estimated_monthly_revenue=estimated_monthly_revenue,
            seasonality=seasonality,
            risk_level=risk_level,
            recommendation=recommendation,
            reasons=reasons
        )
    
    # ==================== 세부 계산 함수 ====================
    
    def _calculate_trend_score(self, trend_data: List[int]) -> float:
        """
        지난 12개월 트렌드로 상승추세 계산
        
        로직:
        - 최근 3개월 평균 vs 이전 3개월 평균 비교
        - 상승 중: 높은 점수
        - 하강 중: 낮은 점수
        """
        if len(trend_data) < 6:
            return 50.0  # 데이터 부족시 중간값
        
        # 최근 3개월 vs 이전 3개월
        recent_3_months = trend_data[-3:]  # 마지막 3개
        previous_3_months = trend_data[-6:-3]  # 그 전 3개
        
        recent_avg = sum(recent_3_months) / len(recent_3_months)
        previous_avg = sum(previous_3_months) / len(previous_3_months)
        
        # 상승률 계산
        if previous_avg == 0:
            trend_growth = 0
        else:
            trend_growth = ((recent_avg - previous_avg) / previous_avg) * 100
        
        # 트렌드 점수 계산
        # -100% ~ +100% 범위를 0-100 점수로 변환
        trend_score = min(100, max(0, 50 + (trend_growth / 2)))
        
        return round(trend_score, 1)
    
    def _calculate_competition_score(
        self,
        num_top_sellers: int,
        review_count_top_10: List[int]
    ) -> float:
        """
        경쟁도 계산
        
        요소:
        1. 상위 판매자 수 (많을수록 경쟁 심함)
        2. 평균 리뷰 수 (많을수록 이미 잘 팔림 = 경쟁 심함)
        """
        
        # 요소 1: 판매자 수 기반 경쟁도 (0-50점)
        # 0-10명: 경쟁 적음, 50명 이상: 경쟁 많음
        sellers_score = min(50, (num_top_sellers / 50) * 50)
        
        # 요소 2: 리뷰 수 기반 경쟁도 (0-50점)
        # 리뷰가 많다 = 이미 잘 팔림 = 경쟁 심함
        avg_reviews = sum(review_count_top_10) / len(review_count_top_10) if review_count_top_10 else 0
        
        # 리뷰 1000개마다 10점 증가 (최대 50점)
        reviews_score = min(50, (avg_reviews / 1000) * 50)
        
        # 종합 경쟁도
        competition_score = sellers_score * 0.6 + reviews_score * 0.4
        
        return round(competition_score, 1)
    
    def _get_competition_level(self, competition_score: float) -> CompetitionLevel:
        """경쟁도 점수를 수준으로 변환"""
        if competition_score < 30:
            return CompetitionLevel.LOW
        elif competition_score < 70:
            return CompetitionLevel.MEDIUM
        else:
            return CompetitionLevel.HIGH
    
    def _estimate_monthly_sales(
        self,
        monthly_searches: int,
        num_top_sellers: int,
        competition_level: CompetitionLevel
    ) -> int:
        """
        예상 월판매량 추정
        
        로직:
        1. 기본값: 월간 검색량 * 전환율 (일반적으로 1-3%)
        2. 판매자 수로 조정 (많을수록 시장이 크지만 경쟁 심함)
        3. 경쟁도로 최종 조정
        """
        
        # 기본 전환율 (검색량 * 전환율)
        if competition_level == CompetitionLevel.LOW:
            conversion_rate = 0.03  # 낮은 경쟁 = 높은 전환율
        elif competition_level == CompetitionLevel.MEDIUM:
            conversion_rate = 0.02
        else:
            conversion_rate = 0.01  # 높은 경쟁 = 낮은 전환율
        
        # 기본 판매량
        base_sales = int(monthly_searches * conversion_rate)
        
        # 판매자 수로 조정 (포화도 고려)
        if num_top_sellers > 0:
            market_saturation = min(1.0, num_top_sellers / 50)  # 50명 기준
            adjusted_sales = int(base_sales * (1 - market_saturation * 0.5))
        else:
            adjusted_sales = base_sales
        
        return max(10, adjusted_sales)  # 최소 10개
    
    def _analyze_seasonality(self, trend_data: List[int]) -> str:
        """
        계절성 분석
        
        YEAR_ROUND: 연중 안정적
        SEASONAL: 특정 시즌에만 팔림
        PEAK: 특정 시즌에 폭증
        """
        
        if len(trend_data) < 12:
            return "YEAR_ROUND"
        
        # 표준편차 계산 (변동성)
        avg = sum(trend_data) / len(trend_data)
        variance = sum((x - avg) ** 2 for x in trend_data) / len(trend_data)
        std_dev = math.sqrt(variance)
        coefficient_of_variation = std_dev / avg if avg > 0 else 0
        
        if coefficient_of_variation < 0.2:
            return "YEAR_ROUND"  # 변동성 낮음 = 연중 판매
        elif coefficient_of_variation < 0.5:
            return "SEASONAL"     # 중간 변동성 = 계절상품
        else:
            return "PEAK"         # 높은 변동성 = 피크 시즌만 판매
    
    def _assess_risk(
        self,
        competition_level: CompetitionLevel,
        trend_score: float,
        seasonality: str
    ) -> str:
        """
        위험도 평가
        
        위험 요소:
        - 높은 경쟁 (판매 어려움)
        - 낮은 트렌드 (내리막)
        - 계절성 상품 (불안정)
        """
        
        risk_score = 0
        
        # 경쟁도에 따른 위험
        if competition_level == CompetitionLevel.HIGH:
            risk_score += 40
        elif competition_level == CompetitionLevel.MEDIUM:
            risk_score += 20
        
        # 트렌드에 따른 위험
        if trend_score < 30:
            risk_score += 40  # 내리막
        elif trend_score < 50:
            risk_score += 20  # 정체
        
        # 계절성에 따른 위험
        if seasonality == "PEAK":
            risk_score += 30  # 계절상품은 불안정
        elif seasonality == "SEASONAL":
            risk_score += 15
        
        if risk_score >= 70:
            return "HIGH"
        elif risk_score >= 40:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _calculate_opportunity_score(
        self,
        trend_score: float,
        competition_score: float,
        monthly_searches: int,
        estimated_revenue: int
    ) -> float:
        """
        종합 기회점수 (가장 중요!)
        
        공식:
        기회점수 = (트렌드 * 0.3 + 경쟁도_역 * 0.2 + 검색량_정규화 * 0.3 + 수익성_정규화 * 0.2)
        
        높을수록: 잘 팔릴 가능성 높음
        """
        
        # 요소 1: 트렌드 (30%)
        trend_component = trend_score * 0.3
        
        # 요소 2: 낮은 경쟁 (20%)
        # 경쟁도가 낮을수록 좋음 (역함수)
        low_competition_score = (100 - competition_score) * 0.2
        
        # 요소 3: 높은 검색량 (30%)
        # 검색량 기준: 5000 = 0점, 100000 = 100점
        search_normalized = min(100, (monthly_searches / 100000) * 100)
        search_component = search_normalized * 0.3
        
        # 요소 4: 높은 수익성 (20%)
        # 수익성 기준: 0 = 0점, ₩10M = 100점
        revenue_normalized = min(100, (estimated_revenue / 10000000) * 100)
        revenue_component = revenue_normalized * 0.2
        
        # 종합
        opportunity_score = (
            trend_component +
            low_competition_score +
            search_component +
            revenue_component
        )
        
        return round(opportunity_score, 1)
    
    def _make_recommendation(
        self,
        opportunity_score: float,
        trend_score: float,
        competition_level: CompetitionLevel,
        risk_level: str,
        seasonality: str,
        estimated_revenue: int
    ) -> tuple:
        """
        추천도 결정 및 이유 생성
        
        추천도 분류:
        HIGHLY_RECOMMENDED: 기회점수 75점 이상 (강력 추천)
        RECOMMENDED: 기회점수 50-75점 (추천)
        CAUTION: 기회점수 30-50점 (신중)
        NOT_RECOMMENDED: 기회점수 30점 이하 (미추천)
        """
        
        reasons = []
        
        # 추천도 결정
        if opportunity_score >= 75:
            recommendation = "HIGHLY_RECOMMENDED"
            reasons.append(f"✨ 우수한 기회점수: {opportunity_score}점")
        elif opportunity_score >= 50:
            recommendation = "RECOMMENDED"
            reasons.append(f"⭐ 좋은 기회점수: {opportunity_score}점")
        elif opportunity_score >= 30:
            recommendation = "CAUTION"
            reasons.append(f"🔔 보통 기회점수: {opportunity_score}점")
        else:
            recommendation = "NOT_RECOMMENDED"
            reasons.append(f"⚠️ 낮은 기회점수: {opportunity_score}점")
        
        # 긍정적 이유
        if trend_score >= 60:
            reasons.append(f"📈 상승 추세: 트렌드 {trend_score:.0f}점")
        
        if competition_level == CompetitionLevel.LOW:
            reasons.append("🟢 낮은 경쟁: 침투 기회 있음")
        elif competition_level == CompetitionLevel.MEDIUM and opportunity_score >= 60:
            reasons.append("🟡 중간 경쟁: 차별화로 성공 가능")
        
        if estimated_revenue >= 10000000:
            reasons.append(f"💰 높은 수익성: 월 ₩{estimated_revenue:,.0f} 예상")
        
        if seasonality == "YEAR_ROUND":
            reasons.append("📅 연중 판매: 안정적 수익")
        
        # 부정적 이유
        if trend_score < 40:
            reasons.append(f"📉 하강 추세: 트렌드 {trend_score:.0f}점 (주의)")
        
        if competition_level == CompetitionLevel.HIGH:
            reasons.append("🔴 높은 경쟁: 차별화 전략 필수")
        
        if risk_level == "HIGH":
            reasons.append("⚠️ 높은 위험도: 충분한 준비 필요")
        
        if seasonality == "PEAK":
            reasons.append("❄️ 계절성: 특정 시즌만 판매 가능")
        
        if estimated_revenue < 5000000:
            reasons.append(f"💸 낮은 수익성: 월 ₩{estimated_revenue:,.0f} 예상")
        
        return recommendation, reasons


# ==================== 테스트 예시 ====================

def test_keyword_analysis():
    """키워드 분석 엔진 테스트"""
    
    engine = KeywordAnalysisEngine()
    
    # 예시 1: 뜨는 상품 (높은 트렌드, 낮은 경쟁)
    hot_product = KeywordData(
        keyword="무선 이어폰",
        monthly_searches=18500,
        cpc_cost=1200,
        num_top_sellers=25,  # 중간 정도
        avg_listing_price=59900,
        search_trend=[40, 45, 50, 55, 65, 70, 75, 80, 85, 88, 90, 92],
        review_count_top_10=[500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400],
    )
    
    # 예시 2: 경쟁이 심한 상품 (많은 판매자)
    competitive_product = KeywordData(
        keyword="스마트폰 케이스",
        monthly_searches=45000,
        cpc_cost=2500,
        num_top_sellers=200,  # 경쟁 매우 심함
        avg_listing_price=9900,
        search_trend=[80, 82, 84, 85, 86, 87, 88, 88, 89, 89, 90, 90],
        review_count_top_10=[5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000, 13000, 14000],
    )
    
    # 예시 3: 내리막 상품 (낮아지는 트렌드)
    declining_product = KeywordData(
        keyword="DVD 플레이어",
        monthly_searches=2100,
        cpc_cost=300,
        num_top_sellers=15,
        avg_listing_price=35000,
        search_trend=[95, 90, 85, 80, 70, 60, 50, 45, 40, 35, 30, 25],
        review_count_top_10=[100, 150, 200, 250, 300, 350, 400, 450, 500, 550],
    )
    
    print("=" * 80)
    print("🔍 키워드 분석 엔진 테스트")
    print("=" * 80)
    
    for product in [hot_product, competitive_product, declining_product]:
        result = engine.analyze(product)
        print_analysis(result)
        print()


def print_analysis(analysis: KeywordAnalysis):
    """분석 결과 출력"""
    print(f"\n📊 키워드: {analysis.keyword}")
    print(f"   월간 검색량: {analysis.monthly_searches:,}명")
    print(f"\n✨ 분석 결과:")
    print(f"   트렌드 점수:     {analysis.trend_score:>6.1f}/100  {'📈' if analysis.trend_score >= 60 else '📉'}")
    print(f"   경쟁도 점수:     {analysis.competition_score:>6.1f}/100  [{analysis.competition_level.value}]")
    print(f"   기회점수:       {analysis.opportunity_score:>6.1f}/100  ⭐⭐⭐")
    print(f"   위험도:         {analysis.risk_level}")
    print(f"   계절성:         {analysis.seasonality}")
    print(f"\n💰 수익성 분석:")
    print(f"   평균 판매가:     ₩{analysis.avg_selling_price:,}")
    print(f"   예상 월판매:     {analysis.estimated_monthly_sales}개")
    print(f"   예상 월매출:     ₩{analysis.estimated_monthly_revenue:,}")
    print(f"   ROI (원가 50% 기준): {(analysis.estimated_monthly_revenue / (analysis.avg_selling_price * analysis.estimated_monthly_sales * 0.5) * 100 - 100) if analysis.estimated_monthly_sales > 0 else 0:.0f}%")
    print(f"\n🎯 추천도: {analysis.recommendation}")
    print(f"   분석 이유:")
    for reason in analysis.reasons:
        print(f"   - {reason}")


if __name__ == "__main__":
    test_keyword_analysis()
