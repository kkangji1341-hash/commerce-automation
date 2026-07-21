"""
키워드 자동 수집 크롤러 (Phase 2a)

현재 구현된 것:
- Google Trends(비공식, pytrends) 기반 12개월 검색 트렌드(0-100 상대 지수)

아직 구현 안 된 것 (자격증명 필요 — 계정 생성은 사용자가 직접 해야 함):
- 절대 월간 검색량: 네이버 검색광고 API(https://searchad.naver.com) 라이선스 키 필요.
  NAVER_AD_API_KEY / NAVER_AD_SECRET_KEY / NAVER_AD_CUSTOMER_ID 환경변수가 설정되면
  fetch_naver_monthly_searches()가 실제 값을 반환하고, 없으면 None을 반환한다
  (추정치를 지어내지 않는다).
"""

import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

import pandas as pd
from pytrends.request import TrendReq


@dataclass
class KeywordCrawlResult:
    keyword: str
    search_trend: List[int]  # 지난 12개월, 0-100 상대 지수 (Google Trends)
    monthly_searches: Optional[int]  # 절대 검색량 - 네이버 API 미연동 시 None
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


def fetch_naver_monthly_searches(keyword: str) -> Optional[int]:
    """
    네이버 검색광고 API로 절대 월간 검색량을 가져온다.
    NAVER_AD_API_KEY/NAVER_AD_SECRET_KEY/NAVER_AD_CUSTOMER_ID가 없으면
    (가짜 숫자를 만들지 않고) None을 반환한다.
    """
    api_key = os.getenv("NAVER_AD_API_KEY")
    secret_key = os.getenv("NAVER_AD_SECRET_KEY")
    customer_id = os.getenv("NAVER_AD_CUSTOMER_ID")

    if not (api_key and secret_key and customer_id):
        return None

    # TODO: 네이버 검색광고 API(RelKwdStat) 연동.
    # https://naver.github.io/searchad-apidoc/#/tags/RelKwdStat
    # HMAC-SHA256 서명 방식 인증이 필요하며, 자격증명이 준비된 후 구현 예정.
    raise NotImplementedError("네이버 검색광고 API 연동은 아직 구현되지 않았습니다")


def fetch_keyword_data(keyword: str) -> KeywordCrawlResult:
    search_trend = fetch_google_trends_monthly(keyword)
    monthly_searches = fetch_naver_monthly_searches(keyword)

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
        f"{result.monthly_searches if result.monthly_searches is not None else '(네이버 API 미연동 - 수집 안 됨)'}"
    )
