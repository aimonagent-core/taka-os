"""Middleware FastAPI pour injection automatique des Feature Flags dans les reponses.
Ajoute un header X-Feature-Flags avec les flags actifs pour le tenant.
"""
import json
import logging

from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class FeatureFlagsMiddleware(BaseHTTPMiddleware):
    """Injecte les Feature Flags dans le contexte de chaque requete."""

    async def dispatch(self, request, call_next):
        response = await call_next(request)

        tenant_tier = getattr(request.state, "tenant_tier", "free")
        try:
            from app.database import AsyncSessionLocal
            from app.services.plan_feature_flags import FeatureFlagService

            async with AsyncSessionLocal() as db:
                flags = await FeatureFlagService.get_all_for_tier(db, tenant_tier)
                response.headers["X-Feature-Flags"] = json.dumps(flags)
        except Exception:
            pass

        return response
