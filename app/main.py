# File: app/main.py
# Purpose: FastAPI application entry point with Sentry, rate limiting, timeout middleware
# Dependencies: app.config, app.core.sentry, app.core.rate_limit, app.api.v1.router, app.database

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.api.v1.router import api_router
from app.config import settings
from app.core.feature_flags_middleware import FeatureFlagsMiddleware
from app.core.rate_limit import limiter, rate_limit_exceeded_handler
from app.core.sentry import init_sentry
from app.database import init_db

init_sentry()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: init DB on startup."""
    logger.info("Starting up TAKA API v%s", settings.app_version)
    await init_db()

    from app.agents.veilleur.scheduler import VeilleurScheduler

    scheduler = VeilleurScheduler()
    await scheduler.start()
    app.state.veille_scheduler = scheduler
    logger.info("Scheduler started")

    yield

    if hasattr(app.state, "veille_scheduler"):
        app.state.veille_scheduler.stop()
    logger.info("Shutting down TAKA API")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="TAKA - Plateforme d'appels d'offres automatises",
    lifespan=lifespan,
)

# === MIDDLEWARES ===


@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    """Global 30s timeout on all requests. Override via X-Request-Timeout header (max 120s)."""
    timeout_seconds = 30
    timeout_header = request.headers.get("x-request-timeout")
    if timeout_header and timeout_header.isdigit():
        timeout_seconds = min(int(timeout_header), 120)
    try:
        return await asyncio.wait_for(call_next(request), timeout=timeout_seconds)
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={
                "status": "error",
                "data": None,
                "message": f"Request timeout after {timeout_seconds}s",
                "meta": None,
            },
        )


@app.middleware("http")
async def rate_limit_state_middleware(request: Request, call_next):
    """Attach rate limiter to request.state for SlowAPI key derivation."""
    request.state.limiter = limiter
    response = await call_next(request)
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    max_age=3600,
)
app.add_middleware(FeatureFlagsMiddleware)

# === EXCEPTION HANDLERS ===


@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return rate_limit_exceeded_handler(request, exc)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "data": None,
            "message": "Internal server error",
            "meta": None,
        },
    )


# === ROUTES ===

app.state.limiter = limiter
app.include_router(api_router)


@app.get("/health", tags=["Health"])
async def root_health():
    return {"status": "success", "data": {"alive": True}, "message": "OK", "meta": None}
