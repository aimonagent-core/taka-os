# File: app/api/v1/router.py
# Purpose: Main API v1 router aggregator

from fastapi import APIRouter

from app.api.v1 import auth, auth_mfa, autonomy, billing, onboarding, webhooks_stripe
from app.api.v1.endpoints import documents, health, hil, memory, tenants, users
from app.api.v1 import veille, scoring, business_lines, dashboard, redacteur, deposant, audit, compliance_reports, platform_credentials, analytics, scrapers

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(auth_mfa.router, prefix="/auth", tags=["MFA"])
api_router.include_router(autonomy.router, tags=["Autonomy"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["Tenants"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(memory.router, prefix="/memory", tags=["Memory"])
api_router.include_router(hil.router, prefix="/hil", tags=["Human-in-the-Loop"])
api_router.include_router(veille.router, tags=["Veille"])
api_router.include_router(scoring.router, tags=["Scoring"])
api_router.include_router(business_lines.router, tags=["Business Lines"])
api_router.include_router(dashboard.router, tags=["Dashboard"])
api_router.include_router(redacteur.router, tags=["Redacteur"])
api_router.include_router(deposant.router, tags=["Deposant"])
api_router.include_router(billing.router, tags=["Billing"])
api_router.include_router(onboarding.router, tags=["Onboarding"])
api_router.include_router(webhooks_stripe.router, tags=["Webhooks"])
api_router.include_router(audit.router, tags=["Audit"])
api_router.include_router(compliance_reports.router, tags=["Compliance"])
api_router.include_router(platform_credentials.router, tags=["Platform Credentials"])
api_router.include_router(analytics.router, tags=["Analytics"])
api_router.include_router(scrapers.router, tags=["Scrapers"])
