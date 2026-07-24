"""동적 브랜드명 DB — 네이버 쇼핑 실제 상품의 brand/maker 필드에서 수집하고,
DB(brand_names 테이블)에 영구 저장한다.

JSON 파일이 아니라 DB에 저장하는 이유: Railway 같은 컨테이너 배포 환경은
파일시스템이 배포/재시작마다 초기화되는 경우가 많아, 로컬 JSON 파일에 쓴
내용은 다음 배포에서 사라진다. 이미 쓰고 있는 Postgres(로컬은 SQLite)는
재시작해도 유지되므로 여기 저장한다.

"주 1회 자동 수집" 스케줄러(APScheduler 등)는 구현하지 않았다 — 이 앱은
트래픽이 크지 않은 1인 운영 도구라, 백그라운드 스케줄러가 주는 운영
복잡도(다중 워커에서 중복 실행 방지, 실패 처리, 프로세스 재시작 시 상태 등)
대비 얻는 이득이 작다고 판단했다. 대신 관리자가 필요할 때 수동으로 호출하는
API 엔드포인트(POST /api/v1/brands/collect)로 구현했다 — Railway cron이나
외부 스케줄러를 붙이고 싶으면 이 엔드포인트를 그대로 호출하면 된다.
"""

import asyncio
import time
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crawlers.keyword_crawler import fetch_naver_shopping_brands
from app.models.brand import BrandName

# 대표 카테고리 키워드 — 네이버 쇼핑에서 상위 100개 상품의 브랜드를 긁어온다.
# 카테고리당 API 호출 1번(display=100)이라 89개 키워드도 금방 끝난다.
COLLECTION_KEYWORDS: List[str] = [
    # 전자제품
    "무선이어폰", "마우스", "키보드", "모니터", "노트북",
    "웹캠", "마이크", "스피커", "헤드폰", "이어버드",
    "휴대폰거치대", "충전기", "케이블", "외장하드", "태블릿",
    # 가전
    "탁상용선풍기", "냉장고", "세탁기", "에어컨", "청소기",
    "밥솥", "전자레인지", "커피머신", "가습기", "제습기",
    # 생활용품
    "우산", "수건", "침구류", "화장품", "칫솔", "비누", "로션", "샤워기",
    # 의류/패션
    "셔츠", "바지", "신발", "가방", "모자",
    "양말", "내복", "레깅스", "니트", "자켓",
    # 유아용품
    "유모차", "기저귀", "분유", "장난감", "아기옷", "아기침대", "젖병",
    # 반려동물
    "개사료", "고양이사료", "반려동물옷", "강아지장난감", "고양이장난감", "반려동물침대",
    # 주방용품
    "냄비", "칼", "도마", "포크", "스푼", "젓가락", "접시",
    # 스포츠
    "요가매트", "덤벨", "운동화", "요가복", "런닝화", "트레이닝복", "줄넘기",
    # 뷰티
    "스킨케어", "파운데이션", "쿠션", "립스틱", "샴푸", "헤어팩", "에센스", "토너",
    # 식품
    "비타민", "프로틴", "영양제", "초콜릿", "우유", "요거트", "견과류", "에너지바",
]

_CACHE_TTL_SECONDS = 600  # 10분 — 요청마다 DB를 조회하지 않도록 짧게 캐시
_cache: dict = {"names": None, "loaded_at": 0.0}


async def collect_and_store_brands(db: AsyncSession, keywords: List[str] | None = None) -> dict:
    """대표 키워드들로 네이버 쇼핑을 조회해 새 브랜드명을 DB에 추가한다."""
    keywords = keywords or COLLECTION_KEYWORDS

    collected: set[str] = set()
    for keyword in keywords:
        brands = await asyncio.to_thread(fetch_naver_shopping_brands, keyword)
        collected.update(brands)

    result = await db.execute(select(BrandName.name))
    existing = {row[0] for row in result.all()}

    new_names = sorted(collected - existing)
    for name in new_names:
        db.add(BrandName(name=name, source="collected"))
    await db.commit()

    _cache["names"] = None  # 다음 조회 때 다시 로드하도록 캐시 무효화

    return {
        "keywords_scanned": len(keywords),
        "total_collected": len(collected),
        "new_brands_added": len(new_names),
        "total_brands_in_db": len(existing) + len(new_names),
    }


async def report_brand_name(db: AsyncSession, name: str) -> bool:
    """사용자가 신고한 브랜드명 1개를 즉시 DB에 추가한다.

    별도 검수 단계 없이 바로 반영한다 — 이 앱은 소수 인원이 쓰는 내부 도구라
    악용 위험이 낮고, 검수 워크플로를 새로 만드는 비용이 더 크다고 판단했다.
    """
    name = name.strip()
    if len(name) < 2:
        return False

    result = await db.execute(select(BrandName).where(BrandName.name == name))
    if result.scalar_one_or_none():
        return False

    db.add(BrandName(name=name, source="reported"))
    await db.commit()
    _cache["names"] = None
    return True


async def get_dynamic_brand_names(db: AsyncSession) -> set[str]:
    """DB에 저장된 브랜드명 전체를 소문자 집합으로 반환한다 (짧게 캐시)."""
    now = time.monotonic()
    if _cache["names"] is not None and (now - _cache["loaded_at"]) < _CACHE_TTL_SECONDS:
        return _cache["names"]

    result = await db.execute(select(BrandName.name))
    names = {row[0].lower() for row in result.all()}
    _cache["names"] = names
    _cache["loaded_at"] = now
    return names
