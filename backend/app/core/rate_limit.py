"""아주 단순한 in-memory IP별 sliding-window rate limiter.

Redis 없이 dict + threading.Lock으로 구현한다 — app/core/simple_cache.py와
같은 전제: 이 앱은 Railway에서 uvicorn 워커 1개로만 뜨므로(Procfile에
--workers 옵션 없음) 프로세스 간 카운터 불일치 문제가 없다.

용도:
- POST /api/v1/scrape/zip-from-urls: 인증 없이 열려 있어(북마크렛이 대상
  사이트 origin에서 실행되므로 우리 앱 토큰을 못 가짐) 반복 호출로 서버
  대역폭/CPU를 소모시킬 수 있다.
- POST /api/v1/auth/login: 실패 횟수 제한이 전혀 없어 비밀번호 무차별
  대입 공격에 그대로 노출돼 있었다.
- POST /api/v1/auth/signup: 스팸 계정 생성 방지.
"""

import threading
import time
from typing import Dict, List

from fastapi import HTTPException, Request, status


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    def _client_ip(self, request: Request) -> str:
        # Railway/Vercel 등 리버스 프록시 뒤에 있으므로 X-Forwarded-For를 우선 본다
        # (가장 왼쪽 값이 실제 클라이언트 IP).
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def __call__(self, request: Request) -> None:
        ip = self._client_ip(request)
        now = time.monotonic()
        cutoff = now - self.window_seconds

        with self._lock:
            hits = self._hits.setdefault(ip, [])
            while hits and hits[0] < cutoff:
                hits.pop(0)

            if len(hits) >= self.max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="요청이 너무 많습니다. 잠시 후 다시 시도해주세요.",
                )

            hits.append(now)

            # 메모리 누수 방지: 추적 중인 IP가 너무 많아지면 빈 기록부터 정리
            if len(self._hits) > 5000:
                for k in [k for k, v in self._hits.items() if not v]:
                    del self._hits[k]
