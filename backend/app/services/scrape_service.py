"""북마크렛이 브라우저에서 수집한 이미지 URL들을 서버가 대신 내려받아 ZIP으로
묶어주는 서비스.

북마크렛은 대상 사이트(알리바바 등) 안에서 실행되기 때문에, 이미지를 직접
fetch()로 받으려 하면 대부분 이미지 CDN이 CORS 헤더를 안 줘서 브라우저가
차단한다(실측 확인 — onch3.co.kr 이미지로 테스트해도 전부 실패). <img> 태그로
"보여주는" 것과 fetch()로 "바이트를 읽는" 것은 브라우저 보안 모델이 다르다.
그래서 북마크렛은 이미지 URL 목록만 모아서(이건 CORS 제약이 없다) 우리
서버로 보내고, 서버가 대신 내려받아 ZIP으로 묶어 돌려준다.

이 엔드포인트는 로그인 없이 호출 가능하다(북마크렛이 대상 사이트의 origin에서
실행되므로 우리 앱의 로그인 토큰을 들고 있지 않다). 그래서 임의의 URL을 서버가
대신 요청하는 것 자체가 SSRF(서버가 내부망/사설 IP를 대신 찔러보게 만드는 공격)
통로가 될 수 있어, URL의 호스트를 DNS로 직접 해석해 사설/루프백/링크로컬 IP인
경우 거부한다. 개수 제한(60개)과 이미지당 용량 제한(15MB)도 함께 건다.
"""

import asyncio
import io
import ipaddress
import logging
import re
import socket
import zipfile
from typing import List
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)

MAX_IMAGES = 60
MAX_IMAGE_BYTES = 15 * 1024 * 1024  # 이미지 1개당 15MB 상한
_SAFE_NAME_RE = re.compile(r"[^\w\-가-힣]+")


def _is_safe_url(url: str) -> bool:
    """SSRF 방지: http(s)만 허용하고, 호스트가 사설/루프백/링크로컬 IP로
    풀리면 거부한다."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    host = parsed.hostname
    if not host:
        return False
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False
    for info in infos:
        try:
            ip = ipaddress.ip_address(info[4][0])
        except ValueError:
            return False
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            return False
    return True


def _guess_ext(url: str) -> str:
    path = urlparse(url).path.lower()
    for ext in ("jpg", "jpeg", "png", "gif", "webp"):
        if path.endswith("." + ext):
            return ext
    return "jpg"


def _download_capped(url: str) -> bytes | None:
    with requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"}, stream=True) as resp:
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "")
        if content_type and not content_type.startswith("image/"):
            return None
        chunks = []
        total = 0
        for chunk in resp.iter_content(chunk_size=65536):
            total += len(chunk)
            if total > MAX_IMAGE_BYTES:
                return None
            chunks.append(chunk)
        return b"".join(chunks)


def _build_zip(image_urls: List[str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, url in enumerate(image_urls[:MAX_IMAGES]):
            if not _is_safe_url(url):
                logger.warning("안전하지 않은 URL, 건너뜀: %r", url)
                continue
            try:
                data = _download_capped(url)
            except requests.exceptions.RequestException as exc:
                logger.warning("이미지 다운로드 실패, 건너뜀: url=%r, %s", url, exc)
                continue
            if not data:
                continue
            zf.writestr(f"image_{i + 1:03d}.{_guess_ext(url)}", data)
    buffer.seek(0)
    return buffer.getvalue()


async def build_zip_from_urls(image_urls: List[str], filename: str) -> tuple[bytes, str]:
    zip_bytes = await asyncio.to_thread(_build_zip, image_urls)
    safe_name = _SAFE_NAME_RE.sub("_", filename).strip("_") or "images"
    return zip_bytes, f"{safe_name}.zip"
