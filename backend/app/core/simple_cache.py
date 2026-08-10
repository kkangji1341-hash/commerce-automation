"""아주 단순한 프로세스-내 TTL 캐시.

네이버 API 크리덴셜은 모든 사용자가 공유하는 앱 전역 키다. 사용자마다 같은
인기 키워드("무선이어폰" 등)를 반복 조회하면 매번 네이버에 실시간으로 재요청이
나가는데, 사용자가 늘면 네이버 쪽 초당 호출 제한에 동시에 걸려 전체 서비스가
막힐 수 있다. 그래서 짧은 시간 안의 동일 키워드 조회는 캐시로 흡수한다.

Redis 없이 dict + threading.Lock으로 구현한다 — 이 앱은 Railway에서
uvicorn 워커 1개로만 떠 있어서(Procfile에 --workers 옵션 없음) 프로세스 간
캐시 공유 문제가 없고, 조회 함수들은 requests 기반 동기 함수라
asyncio.to_thread로 스레드풀에서 돌기 때문에 dict 동시 접근에는 락이 필요하다.

실패 응답(빈 리스트/None)은 기본적으로 캐시하지 않는다 — 일시적 API 장애를
캐시 TTL만큼(몇 시간) 그대로 숨기면 안 되기 때문이다.
"""

import threading
import time
from functools import wraps
from typing import Callable


def ttl_cache(ttl_seconds: int, maxsize: int = 256, cache_if: Callable = bool):
    """동기 함수용 TTL 캐시 데코레이터.

    cache_if(result) -> bool: 이 결과를 캐시할지 결정한다. 기본값은 "참 같은
    값만 캐시"(빈 리스트/빈 문자열/None/False는 캐시 안 함) — 실패를 오래
    숨기지 않기 위해서다. 0을 유효한 값으로 다뤄야 하는 함수(예: 검색량 0)는
    호출부에서 `cache_if=lambda r: r is not None` 처럼 넘긴다.
    """

    def decorator(fn):
        cache: dict = {}
        lock = threading.Lock()

        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = time.monotonic()

            with lock:
                entry = cache.get(key)
                if entry is not None and now - entry[1] < ttl_seconds:
                    return entry[0]

            result = fn(*args, **kwargs)

            if cache_if(result):
                with lock:
                    if len(cache) >= maxsize:
                        cache.pop(next(iter(cache)), None)
                    cache[key] = (result, now)

            return result

        wrapper.cache_clear = lambda: cache.clear()
        return wrapper

    return decorator
