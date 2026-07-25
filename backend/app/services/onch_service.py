"""온채널 상세페이지 이미지 수집/ZIP 패키징 서비스"""

import asyncio
import io
import logging
import re
import zipfile
from typing import List
from urllib.parse import urlparse

import requests

from app.crawlers.onch_crawler import fetch_onch_product_details

logger = logging.getLogger(__name__)

_SAFE_NAME_RE = re.compile(r"[^\w\-가-힣]+")


async def collect_product_details(url: str) -> dict:
    result = await asyncio.to_thread(fetch_onch_product_details, url)
    result["total_images"] = len(result["images"])
    return result


def _filename_from_url(url: str, index: int) -> str:
    path = urlparse(url).path
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else "jpg"
    if ext not in ("jpg", "jpeg", "png", "gif", "webp"):
        ext = "jpg"
    return f"image_{index + 1:03d}.{ext}"


def _build_zip(image_urls: List[str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, url in enumerate(image_urls):
            try:
                resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                resp.raise_for_status()
            except requests.exceptions.RequestException as exc:
                logger.warning("이미지 다운로드 실패, 건너뜀: url=%r, %s", url, exc)
                continue
            zf.writestr(_filename_from_url(url, i), resp.content)
    buffer.seek(0)
    return buffer.getvalue()


async def build_images_zip(image_urls: List[str], product_name: str) -> tuple[bytes, str]:
    zip_bytes = await asyncio.to_thread(_build_zip, image_urls)
    safe_name = _SAFE_NAME_RE.sub("_", product_name).strip("_") or "상품이미지"
    filename = f"{safe_name}.zip"
    return zip_bytes, filename
