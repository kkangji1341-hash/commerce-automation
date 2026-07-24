"""
메인 키워드 → 세부 키워드 추출 → 경쟁력 점수 → 상위 6개 선택
→ 20개 상품명 후보 생성 → 상위 6개 후보 선택 → 1개의 완성된 제목으로 병합

세부 키워드의 검색량/클릭률/경쟁도는 keyword_crawler.fetch_related_keywords()가
네이버 검색광고 API에서 실측한 값을 그대로 쓴다 — 지어내지 않는다.

"상품명 자동 생성"은 카테고리별로 손으로 만든 형용사 사전을 쓰지 않는다.
(예: "우산"엔 이런 형용사, "마우스"엔 저런 형용사 — 이런 사전은 목록에 없는
임의의 키워드에는 전부 "프리미엄/고급"류로 뭉뚱그려지므로 사실상 3~5개
키워드에만 통하는 하드코딩이다.) 대신 카테고리에 무관하게 쓸 수 있는 범용
품질 수식어 풀을 순서대로 붙인다 — 어떤 메인 키워드를 넣어도 동일하게 동작한다.

최종 제목 병합 단계도 같은 이유로 "여자/남자/20대는 하나만" 같은 카테고리별
동의어 그룹을 하드코딩하지 않는다. 대신 세부 키워드에서 메인 키워드를 뺀
"특징 단어"와 수식어를 모아 완전히 같은 토큰만 한 번씩 남기는 방식으로
중복을 제거한다 — 의미상 겹치는 단어(예: 여자/남자)까지는 걸러내지 못하지만,
어떤 카테고리에도 동일하게 적용되는 유일한 일반화 가능한 규칙이다.
"""

import asyncio
from typing import List, TypedDict

from app.crawlers.keyword_crawler import fetch_related_keywords

COMPETITION_PENALTY = {"LOW": 10, "MEDIUM": 20, "HIGH": 30}

# 카테고리에 무관하게 쓸 수 있는 범용 품질/판매 수식어. 특정 키워드 전용 사전이
# 아니라는 점이 중요 — 이래야 "우산"이 아닌 임의의 키워드에도 동일하게 동작한다.
GENERIC_MODIFIERS = ["프리미엄", "베스트", "인기", "가성비", "신상", "실속형"]

CANDIDATES_PER_VARIANT = 4  # 세부 키워드 1개당 생성할 후보 수 (6개 × 4 = 최대 24개)


class KeywordVariant(TypedDict):
    keyword: str
    monthly_searches: int
    click_rate: float
    competition: str


class ScoredVariant(KeywordVariant):
    score: float


class NameCandidate(TypedDict):
    name: str
    variant: str
    modifier: str
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


def generate_candidates(
    top_variants: List[ScoredVariant], per_variant: int = CANDIDATES_PER_VARIANT
) -> List[NameCandidate]:
    """세부 키워드마다 범용 수식어를 붙여 여러 개의 상품명 후보를 만든다.

    후보 점수는 세부 키워드 자체의 경쟁력 점수를 그대로 물려받되, 수식어
    풀에서 앞쪽에 있는(더 일반적으로 선호되는) 수식어일수록 아주 작은 값을
    더해 동점을 깨뜨린다 — 이래야 같은 키워드의 후보들 중 "최고 후보"가
    실행할 때마다 흔들리지 않고 항상 동일하게 뽑힌다.
    """
    candidates: List[NameCandidate] = []
    for variant in top_variants:
        for i in range(per_variant):
            modifier = GENERIC_MODIFIERS[i % len(GENERIC_MODIFIERS)]
            tie_break = (per_variant - i) * 0.001
            candidates.append(
                {
                    "name": f"{modifier} {variant['keyword']}",
                    "variant": variant["keyword"],
                    "modifier": modifier,
                    "score": round(variant["score"] + tie_break, 4),
                }
            )
    return candidates


def select_top_candidates(candidates: List[NameCandidate], top_n: int = 6) -> List[NameCandidate]:
    """세부 키워드 1개당 최고 점수 후보 1개만 남긴 뒤, 점수순 상위 N개를 고른다.

    이렇게 해야 최종적으로 서로 다른 세부 키워드가 골고루 섞여서 뽑히고,
    같은 키워드의 후보 4개가 전부 선택되는 일이 없다.
    """
    best_per_variant: dict[str, NameCandidate] = {}
    for c in candidates:
        current = best_per_variant.get(c["variant"])
        if current is None or c["score"] > current["score"]:
            best_per_variant[c["variant"]] = c
    ranked = sorted(best_per_variant.values(), key=lambda x: x["score"], reverse=True)
    return ranked[:top_n]


def generate_final_title(main_keyword: str, top_candidates: List[NameCandidate]) -> str:
    """선택된 후보들을 하나의 제목으로 병합한다.

    각 후보에서 메인 키워드를 뺀 "특징 단어"와 수식어를 모아, 완전히 같은
    토큰이 반복되면 처음 한 번만 남긴다. 첫 번째 특징 단어에 메인 키워드를
    바로 붙이고, 나머지는 공백으로 이어 붙인다.
    """
    tokens: List[str] = []
    seen: set[str] = set()

    for c in top_candidates:
        feature = c["variant"].replace(main_keyword, "").strip()
        if feature and feature not in seen:
            tokens.append(feature)
            seen.add(feature)

    for c in top_candidates:
        modifier = c["modifier"]
        if modifier not in seen:
            tokens.append(modifier)
            seen.add(modifier)

    if not tokens:
        return main_keyword
    if len(tokens) == 1:
        return f"{tokens[0]}{main_keyword}"
    return f"{tokens[0]}{main_keyword} " + " ".join(tokens[1:])


async def analyze_and_generate(keyword: str, top_n: int = 6) -> dict:
    variants = await asyncio.to_thread(fetch_related_keywords, keyword)
    top_variants = select_top_variants(variants, top_n=top_n)

    candidates = generate_candidates(top_variants)
    top_candidates = select_top_candidates(candidates, top_n=top_n)
    final_title = generate_final_title(keyword, top_candidates)

    return {
        "main_keyword": keyword,
        "top_variants": top_variants,
        "total_candidates_generated": len(candidates),
        "top_candidates": top_candidates,
        "final_title": final_title,
    }
