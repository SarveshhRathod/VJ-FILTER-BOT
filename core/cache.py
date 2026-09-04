# Don't Remove Credit @VJ_Bots
# (c) Tech VJ / VJ-Filter-Bot V2 Core

import time
import asyncio
from collections import OrderedDict
from typing import Any, Optional, Tuple, Callable

class TTLCache:
    """Bounded in-memory LRU + TTL Cache with auto-eviction."""
    def __init__(self, maxsize: int = 5000, default_ttl: int = 300):
        self.maxsize = maxsize
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            if key not in self._cache:
                return None
            val, exp = self._cache[key]
            if time.time() > exp:
                del self._cache[key]
                return None
            self._cache.move_to_end(key)
            return val

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        async with self._lock:
            ttl = ttl if ttl is not None else self.default_ttl
            exp = time.time() + ttl
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = (value, exp)
            if len(self._cache) > self.maxsize:
                self._cache.popitem(last=False)

    async def delete(self, key: str) -> bool:
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    async def clear(self) -> None:
        async with self._lock:
            self._cache.clear()

    async def cleanup_expired(self) -> int:
        async with self._lock:
            now = time.time()
            expired_keys = [k for k, (_, exp) in self._cache.items() if now > exp]
            for k in expired_keys:
                del self._cache[k]
            return len(expired_keys)

    def size(self) -> int:
        return len(self._cache)


class SingleFlight:
    """Request coalescing to prevent DB hammering on concurrent identical queries."""
    def __init__(self):
        self._in_flight: dict[str, asyncio.Future] = {}
        self._lock = asyncio.Lock()

    async def execute(self, key: str, coro_func: Callable, *args, **kwargs) -> Any:
        async with self._lock:
            if key in self._in_flight:
                future = self._in_flight[key]
            else:
                loop = asyncio.get_running_loop()
                future = loop.create_future()
                self._in_flight[key] = future
                asyncio.create_task(self._run(key, future, coro_func, *args, **kwargs))
        return await asyncio.shield(future)

    async def _run(self, key: str, future: asyncio.Future, coro_func: Callable, *args, **kwargs):
        try:
            res = await coro_func(*args, **kwargs)
            if not future.done():
                future.set_result(res)
        except Exception as exc:
            if not future.done():
                future.set_exception(exc)
        finally:
            async with self._lock:
                self._in_flight.pop(key, None)


search_cache = TTLCache(maxsize=8000, default_ttl=300)
settings_cache = TTLCache(maxsize=3000, default_ttl=600)
user_cache = TTLCache(maxsize=5000, default_ttl=600)
single_flight = SingleFlight()
