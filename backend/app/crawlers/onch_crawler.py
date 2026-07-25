"""온채널(onch3.co.kr) 상품 상세페이지 이미지 수집.

승인받아 판매 중인 자신의 상품 상세페이지에서 이미지를 한 번에 모아 받기
위한 기능이다. 온채널 상품 상세페이지는 로그인 없이도 이미지 자체는
공개돼 있지만("판매 승인 없이 이미지를 무단 전시/판매하면 저작권 저촉"이
온채널 자체 공지사항), 판매 승인을 받은 사용자가 자신이 이미 파는 상품의
이미지를 재사용하는 것은 문제가 없다 — 그래서 이 크롤러는 onch3.co.kr
도메인으로만 동작을 제한한다(다른 사이트 URL은 거부).

정적 HTML 하나만 요청해서 파싱한다 — 실측 확인 결과 이 사이트는 상품
이미지가 전부 최초 HTML 응답에 그대로 들어있어(자바스크립트 렌더링이나
로그인 없이도) 헤드리스 브라우저가 필요 없었다. 캡차/봇차단 우회 같은
건 하지 않는다.
"""

import logging
import re
from typing import List
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

ALLOWED_HOST_SUFFIX = "onch3.co.kr"

# 온채널 자체 UI 아이콘/버튼/로고는 전부 "/images/" 경로 밑에 있다(대문자
# "Image"를 쓰는 공급사 CDN 경로와는 다르다 — 실측으로 구분 확인).
_UI_CHROME_MARKER = "/images/"
_IMG_EXT_RE = re.compile(r"\.(jpe?g|png|gif|webp)(\?|$)", re.IGNORECASE)


class InvalidOnchUrlError(ValueError):
    pass


def _validate_onch_url(url: str) -> None:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if not (host == ALLOWED_HOST_SUFFIX or host.endswith("." + ALLOWED_HOST_SUFFIX)):
        raise InvalidOnchUrlError("온채널(onch3.co.kr) 상품 URL만 지원합니다")


def _is_real_product_image(src: str) -> bool:
    if not src or src.startswith("data:"):
        return False
    if _UI_CHROME_MARKER in src:
        return False
    return bool(_IMG_EXT_RE.search(src))


def fetch_onch_product_details(url: str) -> dict:
    """온채널 상품 상세페이지 URL에서 상품명/상품코드/이미지 목록을 가져온다."""
    _validate_onch_url(url)

    response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    title_tag = soup.find("title")
    product_name = title_tag.get_text(strip=True).split(" - 온채널")[0] if title_tag else "상품명 미확인"

    code_match = re.search(r"\bCH\d{5,}\b", response.text)
    product_code = code_match.group(0) if code_match else None

    images: List[str] = []
    seen: set[str] = set()
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if _is_real_product_image(src) and src not in seen:
            images.append(src)
            seen.add(src)

    return {
        "product_name": product_name,
        "product_code": product_code,
        "source_url": url,
        "images": images,
    }
