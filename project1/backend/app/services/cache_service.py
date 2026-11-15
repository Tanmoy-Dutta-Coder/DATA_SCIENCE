import time
from typing import Any, Optional, Dict
from cachetools import TTLCache

class CacheService:
    def __init__(self, maxsize: int = 1000, default_ttl: int = 1800):
        # Default TTL: 30 minutes
        self.cache: TTLCache = TTLCache(maxsize=maxsize, ttl=default_ttl)

    def _make_key(self, prefix: str, **kwargs: Any) -> str:
        sorted_items = sorted(kwargs.items())
        parts = [prefix] + [f"{k}={v}" for k, v in sorted_items]
        return ":".join(parts)

    def get(self, key: str) -> Optional[Any]:
        return self.cache.get(key)

    def set(self, key: str, value: Any) -> None:
        self.cache[key] = value

    def clear(self) -> None:
        self.cache.clear()

cache_service = CacheService()

