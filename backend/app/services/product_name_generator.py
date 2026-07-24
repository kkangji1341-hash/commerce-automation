"""
메인 키워드 → 세부 키워드 추출 → 경쟁력 점수 → 상위 N개 선택 → 상품명 자동 생성

세부 키워드의 검색량/클릭률/경쟁도는 keyword_crawler.fetch_related_keywords()가
네이버 검색광고 API에서 실측한 값을 그대로 쓴다 — 지어내지 않는다.

"상품명 자동 생성"은 카테고리별로 손으로 만든 형용사 사전을 쓰지 않는다.
(예: "우산"엔 이런 형용사, "마우스"엔 저런 형용사 — 이런 사전은 목록에 없는
임의의 키워드에는 전부 "프리미엄/고급"류로 뭉뚱그려지므로 사실상 3~5개
키워드에만 통하는 하드코딩이다.) 대신 카테고리에 무관하게 쓸 수 있는 범용
품질 수식어 풀을 순서대로 붙인다 — 어떤 메인 키워드를 넣어도 동일하게 동작한다.
"""

import asyncio
from typing import List, TypedDict

from app.crawlers.keyword_crawler import fetch_related_keywords

COMPETITION_PENALTY = {"LOW": 10, "MEDIUM": 20, "HIGH": 30}

# 카테고리에 무관하게 쓸 수 있는 범용 품질/판매 수식어. 특정 키워드 전용 사전이
# 아니라는 점이 중요 — 이래야 "우산"이 아닌 임의의 키워드에도 동일하게 동작한다.
GENERIC_MODIFIERS = ["프리미엄", "베스트", "인기", "가성비", "신상", "실속형"]


class KeywordVariant(TypedDict):
    keyword: str
    monthly_searches: int
    click_rate: float
    competition: str


class ScoredVariant(KeywordVariant):
    score: float


def calculate_competitiveness_score(
    monthly_searches: int, click_rate: float, competition: str
) -> float:
    """
    점수 = (검색량/1000 × 0.6) + (클릭률 × 0.4) - 경쟁도 페널티
    검색량이 커질수록, 클릭률이 높을수록, 경쟁이 낮을수록 점수가 높다.
    """
    search_score = (monthly_searches / 1000) * 0.6
    click_score = click_rate * 0.4
    penalty = COMPETITION_PENALTY.get(competition, 20)
    return round(search_score + click_score - penalty, 1)


def select_top_variants(variants: List[KeywordVariant], top_n: int = 6) -> List[ScoredVariant]:
    scored = [
        {**v, "score": calculate_competitiveness_score(
            v["monthly_searches"], v["click_rate"], v["competition"]
        )}
        for v in variants
    ]
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_n]


def generate_product_names(top_variants: List[ScoredVariant], limit: int = 6) -> List[str]:
    names = []
    for i, variant in enumerate(top_variants[:limit]):
        modifier = GENERIC_MODIFIERS[i % len(GENERIC_MODIFIERS)]
        names.append(f"{modifier} {variant['keyword']}")
    return names


async def analyze_and_generate(keyword: str, top_n: int = 6) -> dict:
    variants = await asyncio.to_thread(fetch_related_keywords, keyword)
    top_variants = select_top_variants(variants, top_n=top_n)
    product_names = generate_product_names(top_variants, limit=top_n)
    return {
        "main_keyword": keyword,
        "top_variants": top_variants,
        "generated_product_names": product_names,
    }
