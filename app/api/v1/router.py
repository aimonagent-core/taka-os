# File: app/api/v1/router.py
# Purpose: Main API v1 router aggregator
# Dependencies: all v1 endpoint modules

from fastapi import APIRouter

from app.api.v1 import auth, auth_mfa
from app.api.v1.endpoints import health, tenants, users

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(auth_mfa.router, prefix="/auth", tags=["MFA"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["Tenants"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
