# File: app/core/rate_limit.py
# Purpose: Rate limiting configuration using SlowAPI with Redis fallback
# Dependencies: app.config.settings, slowapi, redis (fakeredis fallback)

from fastapi import Request, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings


# NOTE: FakeRedis import is deferred to avoid hard dependency issues.
# In production, real Redis should always be available.
def _get_limiter_backend() -> object:
    """Return Redis client or FakeRedis if Redis is unavailable."""
    try:
        import redis.asyncio as redis

        return redis.from_url(settings.redis_url, decode_responses=True)
    except Exception:
        import fakeredis.aioredis

        return fakeredis.aioredis.FakeRedis()


limiter = Limiter(
    key_func=lambda req: _derive_key(req),
    storage_uri=settings.redis_url,
    strategy="fixed-window",
)


def _derive_key(request: Request) -> str:
    """Derive rate limit key from user_id if authenticated, else IP."""
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return f"user:{user_id}"
    return f"ip:{get_remote_address(request)}"


def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """Global handler for rate limit exceeded."""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "status": "error",
            "data": None,
            "message": f"Rate limit exceeded: {exc.detail}",
            "meta": None,
        },
    )


def get_default_limit() -> str:
    return settings.rate_limit_default


def get_auth_limit() -> str:
    return settings.rate_limit_auth


def get_health_limit() -> str:
    return settings.rate_limit_health
