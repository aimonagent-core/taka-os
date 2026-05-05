# File: app/core/sentry.py
# Purpose: Sentry SDK initialization and utility helpers
# Dependencies: app.config.settings

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from app.config import settings


def init_sentry() -> None:
    """Initialize Sentry SDK if DSN is configured."""
    if not settings.sentry_enabled:
        return
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment,
        release=settings.app_version,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        profiles_sample_rate=0.1 if settings.is_production else 0.0,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
        ],
        attach_stacktrace=True,
        include_source_context=True,
        before_send=strip_sensitive_data,
    )


def strip_sensitive_data(event: dict, hint: dict) -> dict | None:
    """Remove sensitive fields from Sentry events before sending."""
    if "request" in event and "data" in event["request"]:
        for key in ["password", "token", "secret", "credit_card", "mfa_code"]:
            if key in event["request"]["data"]:
                event["request"]["data"][key] = "[FILTERED]"
    return event


def set_sentry_user(user_id: str, tenant_id: str | None, role: str) -> None:
    """Enrich Sentry scope with user context."""
    if not settings.sentry_enabled:
        return
    sentry_sdk.set_user(
        {
            "id": user_id,
            "tenant_id": tenant_id,
            "role": role,
        }
    )


def clear_sentry_user() -> None:
    """Clear user context from Sentry scope (logout)."""
    if not settings.sentry_enabled:
        return
    sentry_sdk.set_user(None)
