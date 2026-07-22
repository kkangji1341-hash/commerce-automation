"""
키워드 자동 수집 크롤러 (Phase 2a, Phase 3a)

구현된 것:
- Google Trends(비공식, pytrends) 기반 12개월 검색 트렌드(0-100 상대 지수)
- 네이버 검색광고 API(https://searchad.naver.com) 기반 절대 월간 검색량
  (PC + 모바일 합산). NAVER_AD_API_KEY / NAVER_AD_SECRET_KEY / NAVER_AD_CUSTOMER_ID
  환경변수가 없으면 (추정치를 지어내지 않고) None을 반환한다.
"""

import base64
import hashlib
import hmac
import logging
import os
import time
from dataclasses import dataclass
from typing import List, Optional

import pandas as pd
import requests
from pytrends.request import TrendReq

logger = logging.getLogger(__name__)

NAVER_AD_BASE_URL = "https://api.searchad.naver.com"
NAVER_AD_KEYWORDSTOOL_URI = "/keywordstool"


@dataclass
class KeywordCrawlResult:
    keyword: str
    search_trend: List[int]  # 지난 12개월, 0-100 상대 지수 (Google Trends)
    monthly_searches: Optional[int]  # 절대 검색량 - 네이버 API 미연동/실패 시 None
    trend_source: str
    monthly_searches_source: Optional[str]


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

    # 최근 `months`개월만 사용, 부족하면 앞쪽을 마지막 값으로 채움 (신규 키워드 등)
    values = values[-months:]
    if len(values) < months:
        pad = [values[0]] * (months - len(values)) if values else [0] * months
        values = pad + values

    return values


def _naver_signature(timestamp: str, method: str, uri: str, secret_key: str) -> str:
    message = f"{timestamp}.{method}.{uri}"
    digest = hmac.new(secret_key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")


def _naver_headers(method: str, uri: str, api_key: str, secret_key: str, customer_id: str) -> dict:
    timestamp = str(int(time.time() * 1000))
    return {
        "Content-Type": "application/json; charset=UTF-8",
        "X-Timestamp": timestamp,
        "X-API-KEY": api_key,
        "X-Customer": customer_id,
        "X-Signature": _naver_signature(timestamp, method, uri, secret_key),
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

    # 네이버 검색광고 API는 hintKeywords에 공백이 있으면 안 됨 (예: "무선 이어폰" -> "무선이어폰")
    hint_keyword = keyword.replace(" ", "")

    headers = _naver_headers("GET", NAVER_AD_KEYWORDSTOOL_URI, api_key, secret_key, customer_id)
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


def fetch_keyword_data(keyword: str) -> KeywordCrawlResult:
    search_trend = fetch_google_trends_monthly(keyword)

    try:
        monthly_searches = fetch_naver_monthly_searches(keyword)
    except Exception:
        # 네이버 API가 실패해도(자격증명 오류, 레이트리밋 등) Google Trends 결과는 살린다.
        logger.exception("네이버 검색광고 API 호출 실패: keyword=%r", keyword)
        monthly_searches = None

    return KeywordCrawlResult(
        keyword=keyword,
        search_trend=search_trend,
        monthly_searches=monthly_searches,
        trend_source="google_trends",
        monthly_searches_source="naver_search_ad_api" if monthly_searches is not None else None,
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
