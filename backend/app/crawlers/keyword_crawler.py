"""
키워드 자동 수집 크롤러 (Phase 2a, 3a, 5)

구현된 것:
- 검색 트렌드(12개월, 0-100 상대 지수): 네이버 데이터랩 검색어트렌드 API 우선,
  실패/미연동 시 Google Trends(비공식, pytrends)로 폴백
- 평균 판매가 / 판매자 수(proxy): 네이버 검색 API(쇼핑) 기반
  (NAVER_SEARCH_CLIENT_ID/SECRET 환경변수 필요 — 위 데이터랩과는 별개 앱/자격증명)
- 절대 월간 검색량: 네이버 검색광고 API (NAVER_AD_* 환경변수 필요)

여전히 불가능한 것 (네이버 공식 API가 아예 제공하지 않음 — 지어내지 않음):
- 상위 10개 상품 리뷰 수: 어떤 공식 네이버 API에도 리뷰 수 필드가 없다.
  실제 값을 얻으려면 네이버 쇼핑 페이지를 직접 크롤링해야 하는데, 이는 네이버
  이용약관 위반 소지가 있어 Phase 2에서 보류한 부분이다. 여기서는 계속 None.
"""

import base64
import hashlib
import hmac
import logging
import os
import re
import time
from dataclasses import dataclass
from typing import List, Optional

import requests
from dotenv import load_dotenv
from pytrends.request import TrendReq

load_dotenv()

logger = logging.getLogger(__name__)

NAVER_AD_BASE_URL = "https://api.searchad.naver.com"
NAVER_AD_KEYWORDSTOOL_URI = "/keywordstool"
NAVER_OPENAPI_BASE_URL = "https://openapi.naver.com"


@dataclass
class KeywordCrawlResult:
    keyword: str

    search_trend: List[int]  # 지난 12개월, 0-100 상대 지수
    trend_source: str  # "naver_datalab" | "google_trends"

    monthly_searches: Optional[int]  # 절대 검색량 - 네이버 검색광고 API 미연동/실패 시 None
    monthly_searches_source: Optional[str]

    avg_price: Optional[int]  # 평균 판매가 (네이버 쇼핑 검색 상위 N개 평균)
    avg_price_source: Optional[str]

    seller_count: Optional[int]  # 상위 판매자 수 proxy (검색 결과 내 고유 쇼핑몰 수)
    seller_count_source: Optional[str]

    review_count_top_10: Optional[List[int]]  # 리뷰 수 — 공식 API 없음, 항상 None


# ==================== 1. 검색 트렌드 (네이버 데이터랩 우선, Google Trends 폴백) ====================

def fetch_naver_search_trend(keyword: str, months: int = 12) -> List[int]:
    """
    네이버 데이터랩 검색어트렌드 API. 절대 검색량이 아니라 조회 기간 내 최댓값을
    100으로 정규화한 상대 지수(0-100)를 준다.
    NAVER_CLIENT_ID/NAVER_CLIENT_SECRET 환경변수가 필요하다.
    """
    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET")
    if not (client_id and client_secret):
        raise RuntimeError("NAVER_CLIENT_ID/NAVER_CLIENT_SECRET이 설정되지 않았습니다")

    from datetime import date
    from dateutil.relativedelta import relativedelta

    end = date.today()
    start = end - relativedelta(months=months)

    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
        "Content-Type": "application/json",
    }
    body = {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "timeUnit": "month",
        "keywordGroups": [{"groupName": keyword, "keywords": [keyword.replace(" ", "")]}],
    }
    response = requests.post(
        f"{NAVER_OPENAPI_BASE_URL}/v1/datalab/search", headers=headers, json=body, timeout=10
    )
    response.raise_for_status()
    data_points = response.json()["results"][0]["data"]

    values = [round(p["ratio"]) for p in data_points][-months:]
    if len(values) < months:
        pad = [values[0]] * (months - len(values)) if values else [0] * months
        values = pad + values
    return values


def fetch_google_trends_monthly(keyword: str, months: int = 12) -> List[int]:
    """Google Trends에서 최근 `months`개월치 월별 평균 관심도(0-100)를 가져온다."""
    pytrends = TrendReq(hl="ko-KR", tz=540)
    pytrends.build_payload([keyword], timeframe="today 12-m", geo="KR")
    df = pytrends.interest_over_time()

    if df.empty:
        raise ValueError(f"'{keyword}'에 대한 Google Trends 데이터가 없습니다")

    df = df.drop(columns=["isPartial"], errors="ignore")
    monthly = df.resample("MS").mean().round().astype(int)

    values = monthly[keyword].tolist()
    values = values[-months:]
    if len(values) < months:
        pad = [values[0]] * (months - len(values)) if values else [0] * months
        values = pad + values

    return values


def fetch_search_trend(keyword: str, months: int = 12) -> tuple:
    """네이버 데이터랩을 먼저 시도하고, 실패하면 Google Trends로 폴백한다."""
    try:
        return fetch_naver_search_trend(keyword, months), "naver_datalab"
    except Exception as exc:
        logger.warning("네이버 데이터랩 검색어트렌드 실패, Google Trends로 폴백: %s", exc)
        return fetch_google_trends_monthly(keyword, months), "google_trends"


# ==================== 2. 네이버 쇼핑 검색 (평균가 / 판매자 수 proxy) ====================

def fetch_naver_shopping_snapshot(keyword: str, top_n: int = 10) -> dict:
    """
    네이버 검색 API(쇼핑)로 상위 `top_n`개 상품을 조회해 평균가/고유 판매자 수를 계산한다.
    NAVER_SEARCH_CLIENT_ID/NAVER_SEARCH_CLIENT_SECRET 환경변수가 필요하다
    (데이터랩과는 별개의 앱/자격증명일 수 있다).

    주의: 이 API는 리뷰 수를 제공하지 않는다 — review_count는 항상 None.
    """
    client_id = os.getenv("NAVER_SEARCH_CLIENT_ID")
    client_secret = os.getenv("NAVER_SEARCH_CLIENT_SECRET")
    if not (client_id and client_secret):
        raise RuntimeError("NAVER_SEARCH_CLIENT_ID/NAVER_SEARCH_CLIENT_SECRET이 설정되지 않았습니다")

    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
    response = requests.get(
        f"{NAVER_OPENAPI_BASE_URL}/v1/search/shop.json",
        headers=headers,
        params={"query": keyword, "display": top_n, "sort": "sim"},
        timeout=10,
    )
    response.raise_for_status()
    items = response.json().get("items", [])

    prices = [int(i["lprice"]) for i in items if i.get("lprice")]
    avg_price = round(sum(prices) / len(prices)) if prices else None
    seller_count = len({i.get("mallName") for i in items if i.get("mallName")}) or None

    return {"avg_price": avg_price, "seller_count": seller_count, "sample_size": len(items)}


_TAG_RE = re.compile(r"<[^>]+>")
_MIN_REASONABLE_PRICE = 100
_MAX_REASONABLE_PRICE = 10_000_000


def fetch_naver_shopping_products(keyword: str, limit: int = 10) -> List[dict]:
    """
    네이버 검색 API(쇼핑)로 키워드에 실제로 잡히는 판매 중 상품 목록을 가져온다
    (상품 추천 엔진이 카탈로그에 없는 카테고리의 후보를 동적으로 채울 때 사용).

    주의: 이 API는 "이미 팔리고 있는 소매가"만 준다 — 원가/배송비/MOQ/리드타임/
    리뷰수 같은 소싱 정보는 전혀 없다. 그 필드들은 호출부(product_recommendation_system)에서
    추정치로 채우고 반드시 "추정" 표시를 해야 한다. 실패 시 예외를 던지지 않고
    빈 리스트를 반환한다 — 이 데이터가 없어도 정적 카탈로그 기반 추천은 계속 동작해야 하므로.
    """
    client_id = os.getenv("NAVER_SEARCH_CLIENT_ID")
    client_secret = os.getenv("NAVER_SEARCH_CLIENT_SECRET")
    if not (client_id and client_secret):
        logger.warning("NAVER_SEARCH_CLIENT_ID/SECRET 미설정 — 동적 상품 조회 건너뜀")
        return []

    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
    try:
        response = requests.get(
            f"{NAVER_OPENAPI_BASE_URL}/v1/search/shop.json",
            headers=headers,
            params={"query": keyword, "display": min(limit * 2, 30), "sort": "sim"},
            timeout=5,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.exceptions.Timeout:
        logger.warning("네이버 쇼핑 검색 타임아웃(5s): keyword=%r", keyword)
        return []
    except requests.exceptions.RequestException as exc:
        logger.warning("네이버 쇼핑 검색 실패(HTTP/네트워크): keyword=%r, %s", keyword, exc)
        return []
    except ValueError as exc:  # JSON 파싱 실패
        logger.warning("네이버 쇼핑 검색 응답 파싱 실패: keyword=%r, %s", keyword, exc)
        return []

    raw_items = payload.get("items", [])
    products: List[dict] = []
    seen_ids: set = set()

    for item in raw_items:
        normalized = _validate_and_normalize_naver_product(item)
        if normalized is None:
            continue
        if normalized["product_id"] in seen_ids:
            continue
        seen_ids.add(normalized["product_id"])
        products.append(normalized)
        if len(products) >= limit:
            break

    return products


def _validate_and_normalize_naver_product(item: dict) -> Optional[dict]:
    """네이버 쇼핑 검색 결과 1건을 검증하고 정규화한다. 유효하지 않으면 None."""
    try:
        title = _TAG_RE.sub("", item.get("title", "")).strip()
        mall_name = (item.get("mallName") or "").strip()
        product_id = str(item.get("productId") or "").strip()
        price_raw = item.get("lprice")

        if not title or not mall_name or not product_id or not price_raw:
            return None

        price = int(price_raw)
        if not (_MIN_REASONABLE_PRICE <= price <= _MAX_REASONABLE_PRICE):
            return None

        category = item.get("category4") or item.get("category3") or item.get("category1") or ""

        return {
            "product_id": product_id,
            "title": title,
            "price": price,
            "seller": mall_name,
            "category": category,
        }
    except (TypeError, ValueError) as exc:
        logger.warning("네이버 쇼핑 상품 데이터 형식 오류, 건너뜀: %s", exc)
        return None


def fetch_naver_shopping_brands(keyword: str, display: int = 100) -> List[str]:
    """네이버 쇼핑 검색 결과 상위 상품들의 실제 브랜드명을 가져온다.

    브랜드명 자동 수집(동적 브랜드 DB 구축)에 쓰인다. mallName은 "네이버",
    "쿠팡" 같은 판매 채널/오픈마켓 스토어명이라 브랜드가 아니다 — 반드시
    item의 brand/maker 필드를 써야 한다(실측 확인: 무선이어폰 검색 시
    mallName="네이버", brand="베이스어스"). brand가 비어있으면 maker로
    대체하고, 둘 다 없으면 건너뛴다. 실패 시 예외 없이 빈 리스트.
    """
    client_id = os.getenv("NAVER_SEARCH_CLIENT_ID")
    client_secret = os.getenv("NAVER_SEARCH_CLIENT_SECRET")
    if not (client_id and client_secret):
        logger.warning("NAVER_SEARCH_CLIENT_ID/SECRET 미설정 — 브랜드 수집 건너뜀")
        return []

    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
    try:
        response = requests.get(
            f"{NAVER_OPENAPI_BASE_URL}/v1/search/shop.json",
            headers=headers,
            params={"query": keyword, "display": min(display, 100), "sort": "sim"},
            timeout=10,
        )
        response.raise_for_status()
        items = response.json().get("items", [])
    except requests.exceptions.RequestException as exc:
        logger.warning("네이버 쇼핑 브랜드 수집 실패: keyword=%r, %s", keyword, exc)
        return []
    except ValueError as exc:
        logger.warning("네이버 쇼핑 브랜드 응답 파싱 실패: keyword=%r, %s", keyword, exc)
        return []

    brands: set = set()
    for item in items:
        brand = (item.get("brand") or item.get("maker") or "").strip()
        if len(brand) > 1:
            brands.add(brand)
    return sorted(brands)


# ==================== 3. 절대 월간 검색량 (네이버 검색광고 API) ====================

def _naver_ad_signature(timestamp: str, method: str, uri: str, secret_key: str) -> str:
    message = f"{timestamp}.{method}.{uri}"
    digest = hmac.new(secret_key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")


def _naver_ad_headers(method: str, uri: str, api_key: str, secret_key: str, customer_id: str) -> dict:
    timestamp = str(int(time.time() * 1000))
    return {
        "Content-Type": "application/json; charset=UTF-8",
        "X-Timestamp": timestamp,
        "X-API-KEY": api_key,
        "X-Customer": customer_id,
        "X-Signature": _naver_ad_signature(timestamp, method, uri, secret_key),
    }


def _parse_naver_count(value) -> int:
    """"< 10" 같은 문자열도 처리 (네이버는 낮은 검색량을 이렇게 뭉뚱그려 준다)."""
    if isinstance(value, str):
        digits = "".join(c for c in value if c.isdigit())
        return int(digits) if digits else 0
    return int(value)


def fetch_naver_monthly_searches(keyword: str) -> Optional[int]:
    """
    네이버 검색광고 API(키워드 도구)로 절대 월간 검색량(PC+모바일)을 가져온다.
    자격증명이 없거나 API 호출이 실패하면 (가짜 숫자를 만들지 않고) None을 반환한다.
    """
    api_key = os.getenv("NAVER_AD_API_KEY")
    secret_key = os.getenv("NAVER_AD_SECRET_KEY")
    customer_id = os.getenv("NAVER_AD_CUSTOMER_ID")

    if not (api_key and secret_key and customer_id):
        return None

    hint_keyword = keyword.replace(" ", "")

    headers = _naver_ad_headers("GET", NAVER_AD_KEYWORDSTOOL_URI, api_key, secret_key, customer_id)
    response = requests.get(
        NAVER_AD_BASE_URL + NAVER_AD_KEYWORDSTOOL_URI,
        headers=headers,
        params={"hintKeywords": hint_keyword, "showDetail": "1"},
        timeout=10,
    )
    response.raise_for_status()
    keyword_list = response.json().get("keywordList", [])

    if not keyword_list:
        return None

    match = next(
        (k for k in keyword_list if k.get("relKeyword") == hint_keyword),
        keyword_list[0],
    )

    pc = _parse_naver_count(match.get("monthlyPcQcCnt", 0))
    mobile = _parse_naver_count(match.get("monthlyMobileQcCnt", 0))
    return pc + mobile


# 네이버 광고 API의 compIdx는 이미 "낮음/중간/높음" 문자열로 온다 — 지어낼 필요 없음.
_COMPETITION_MAP = {"낮음": "LOW", "중간": "MEDIUM", "높음": "HIGH"}


def fetch_related_keywords(keyword: str, limit: int = 30) -> List[dict]:
    """
    네이버 검색광고 API(키워드 도구)로 시드 키워드의 실제 세부/연관 키워드를 가져온다.

    keywordstool은 hintKeywords로 준 키워드와 "관련성 있다고 판단되는" 키워드를
    수백 개까지 함께 반환하는데, 그중 상당수는 실제로는 다른 카테고리 상품이다
    (예: "우산" 검색 시 "지갑", "가디건"도 섞여 나옴 — 광고 타겟팅용 유사군집이지
    진짜 세부 키워드가 아니기 때문). 그래서 relKeyword에 시드 키워드 문자열이
    실제로 포함된 것만 "세부 키워드"로 취급해 필터링한다.

    검색량/클릭률/경쟁도 전부 실측값이며 절대 지어내지 않는다. 실패 시 빈 리스트.
    """
    api_key = os.getenv("NAVER_AD_API_KEY")
    secret_key = os.getenv("NAVER_AD_SECRET_KEY")
    customer_id = os.getenv("NAVER_AD_CUSTOMER_ID")
    if not (api_key and secret_key and customer_id):
        logger.warning("NAVER_AD_* 미설정 — 세부 키워드 조회 건너뜀")
        return []

    hint_keyword = keyword.replace(" ", "")
    headers = _naver_ad_headers("GET", NAVER_AD_KEYWORDSTOOL_URI, api_key, secret_key, customer_id)

    try:
        response = requests.get(
            NAVER_AD_BASE_URL + NAVER_AD_KEYWORDSTOOL_URI,
            headers=headers,
            params={"hintKeywords": hint_keyword, "showDetail": "1"},
            timeout=10,
        )
        response.raise_for_status()
        items = response.json().get("keywordList", [])
    except requests.exceptions.RequestException as exc:
        logger.warning("네이버 세부 키워드 조회 실패: keyword=%r, %s", keyword, exc)
        return []
    except ValueError as exc:
        logger.warning("네이버 세부 키워드 응답 파싱 실패: keyword=%r, %s", keyword, exc)
        return []

    results: List[dict] = []
    for item in items:
        rel_keyword = item.get("relKeyword", "")
        if hint_keyword not in rel_keyword or rel_keyword == hint_keyword:
            continue

        pc_qc = _parse_naver_count(item.get("monthlyPcQcCnt", 0))
        mobile_qc = _parse_naver_count(item.get("monthlyMobileQcCnt", 0))
        total_qc = pc_qc + mobile_qc

        try:
            pc_ctr = float(item.get("monthlyAvePcCtr", 0) or 0)
            mobile_ctr = float(item.get("monthlyAveMobileCtr", 0) or 0)
        except (TypeError, ValueError):
            pc_ctr = mobile_ctr = 0.0

        # PC/모바일 검색량 비중으로 가중평균 (한쪽 채널 검색량이 0이면 단순평균으로 대체)
        if total_qc > 0:
            click_rate = (pc_ctr * pc_qc + mobile_ctr * mobile_qc) / total_qc
        else:
            click_rate = (pc_ctr + mobile_ctr) / 2

        competition = _COMPETITION_MAP.get(item.get("compIdx", ""), "MEDIUM")

        results.append(
            {
                "keyword": rel_keyword,
                "monthly_searches": total_qc,
                "click_rate": round(click_rate, 2),
                "competition": competition,
            }
        )

    results.sort(key=lambda x: x["monthly_searches"], reverse=True)
    return results[:limit]


# ==================== 통합 ====================

def fetch_keyword_data(keyword: str) -> KeywordCrawlResult:
    search_trend, trend_source = fetch_search_trend(keyword)

    try:
        monthly_searches = fetch_naver_monthly_searches(keyword)
    except Exception:
        logger.exception("네이버 검색광고 API 호출 실패: keyword=%r", keyword)
        monthly_searches = None

    avg_price = seller_count = None
    try:
        snapshot = fetch_naver_shopping_snapshot(keyword)
        avg_price = snapshot["avg_price"]
        seller_count = snapshot["seller_count"]
    except Exception:
        logger.exception("네이버 쇼핑 검색 API 호출 실패: keyword=%r", keyword)

    return KeywordCrawlResult(
        keyword=keyword,
        search_trend=search_trend,
        trend_source=trend_source,
        monthly_searches=monthly_searches,
        monthly_searches_source="naver_search_ad_api" if monthly_searches is not None else None,
        avg_price=avg_price,
        avg_price_source="naver_shopping_search" if avg_price is not None else None,
        seller_count=seller_count,
        seller_count_source="naver_shopping_search" if seller_count is not None else None,
        review_count_top_10=None,
    )


if __name__ == "__main__":
    result = fetch_keyword_data("무선 이어폰")
    print(f"키워드: {result.keyword}")
    print(f"검색 트렌드 (12개월, {result.trend_source}): {result.search_trend}")
    print(
        f"월간 검색량: "
        f"{result.monthly_searches if result.monthly_searches is not None else '(수집 안 됨)'}"
        f" ({result.monthly_searches_source})"
    )
    print(f"평균 판매가: {result.avg_price} ({result.avg_price_source})")
    print(f"판매자 수(proxy): {result.seller_count} ({result.seller_count_source})")
    print(f"리뷰 수: {result.review_count_top_10} (공식 API 없음 - 항상 None)")
