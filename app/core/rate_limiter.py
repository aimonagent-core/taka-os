# File: app/core/rate_limiter.py
# Purpose: Rate limiting utility using Redis
# Dependencies: redis.asyncio

import redis.asyncio as redis

from app.config import settings


class RateLimiter:
    def __init__(self, redis_client: redis.Redis | None = None) -> None:
        self._redis = redis_client

    async def is_allowed(self, key: str, max_attempts: int, window_seconds: int) -> tuple[bool, int]:
        if not self._redis:
            return True, max_attempts
        current = await self._redis.incr(key)
        if current == 1:
            await self._redis.expire(key, window_seconds)
        remaining = max_attempts - current
        return current <= max_attempts, max(remaining, 0)

    async def acquire_lockout(self, key: str, duration_seconds: int) -> None:
        if self._redis:
            await self._redis.setex(key, duration_seconds, "1")

    async def is_locked_out(self, key: str) -> bool:
        if not self._redis:
            return False
        return await self._redis.exists(key) > 0

    async def reset(self, key: str) -> None:
        if self._redis:
            await self._redis.delete(key)
