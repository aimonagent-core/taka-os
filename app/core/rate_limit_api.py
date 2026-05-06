"""Rate limiting par cle API avec Redis (sliding window).

Verifie le nombre de requetes par minute pour chaque cle API.
Utilise Redis pour le comptage (TTL = 60s par window).

Sans Redis : fallback en memoire (per process, pas partage entre workers).
"""

import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

_memory_windows: dict[str, list[float]] = {}


class ApiKeyRateLimiter:
    """Rate limiter par cle API."""

    WINDOW_SIZE = 60  # secondes

    async def check_rate_limit(
        self,
        key_hash: str,
        limit_per_minute: int,
    ) -> tuple[bool, int, int]:
        """Verifie si la requete est autorisee.

        Returns:
            (allowed, remaining_requests, reset_timestamp)
        """
        try:
            return await self._check_with_redis(key_hash, limit_per_minute)
        except Exception:
            return self._check_with_memory(key_hash, limit_per_minute)

    async def _check_with_redis(
        self,
        key_hash: str,
        limit: int,
    ) -> tuple[bool, int, int]:
        """Rate limiting avec Redis."""
        import redis.asyncio as redis
        from app.config import settings

        r = redis.from_url(settings.redis_url or "redis://redis:6379")

        now = int(time.time())
        window_key = f"ratelimit:{key_hash}:{now // self.WINDOW_SIZE}"

        pipe = r.pipeline()
        pipe.incr(window_key)
        pipe.expire(window_key, self.WINDOW_SIZE)
        results = await pipe.execute()

        current_count = results[0]
        allowed = current_count <= limit
        remaining = max(0, limit - current_count)
        reset_at = (now // self.WINDOW_SIZE + 1) * self.WINDOW_SIZE

        await r.aclose()

        return allowed, remaining, reset_at

    def _check_with_memory(
        self,
        key_hash: str,
        limit: int,
    ) -> tuple[bool, int, int]:
        """Rate limiting en memoire (fallback)."""
        global _memory_windows

        now = time.time()
        window_start = now - self.WINDOW_SIZE

        if key_hash not in _memory_windows:
            _memory_windows[key_hash] = []

        _memory_windows[key_hash] = [
            ts for ts in _memory_windows[key_hash] if ts > window_start
        ]

        current_count = len(_memory_windows[key_hash])
        allowed = current_count < limit

        if allowed:
            _memory_windows[key_hash].append(now)

        remaining = max(0, limit - current_count - 1)
        reset_at = int(now + self.WINDOW_SIZE)

        return allowed, remaining, reset_at
