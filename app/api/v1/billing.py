"""Routes API pour la facturation Stripe."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.ao import User
from app.services.billing.stripe_service import BillingService

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.post("/checkout-session")
async def create_checkout_session(
    tier_name: str,
    yearly: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cree une session Stripe Checkout pour souscription."""
    if not settings.stripe_secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe non configure",
        )

    try:
        result = await BillingService.create_checkout_session(
            db,
            tenant_id=str(current_user.tenant_id),
            tier_name=tier_name,
            yearly=yearly,
            success_url=f"{settings.frontend_url}/subscription/success",
            cancel_url=f"{settings.frontend_url}/subscription/cancel",
        )
        return {"status": "success", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/portal-session")
async def create_portal_session(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cree un lien vers le portal client Stripe."""
    if not settings.stripe_secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe non configure",
        )

    try:
        url = await BillingService.create_portal_session(
            db,
            tenant_id=str(current_user.tenant_id),
            return_url=f"{settings.frontend_url}/subscription",
        )
        return {"status": "success", "data": {"url": url}}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/subscription")
async def get_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retourne la souscription active du tenant."""
    from sqlalchemy import select
    from app.models.billing import TenantSubscription

    stmt = (
        select(TenantSubscription)
        .where(TenantSubscription.tenant_id == current_user.tenant_id)
    )
    row = await db.execute(stmt)
    sub = row.scalar_one_or_none()

    if not sub:
        return {
            "status": "success",
            "data": {
                "tier_name": "free",
                "status": "active",
                "stripe_subscription_id": None,
            },
        }

    from app.models.feature_flag import SubscriptionTier
    stmt_tier = select(SubscriptionTier).where(SubscriptionTier.id == sub.tier_id)
    row_tier = await db.execute(stmt_tier)
    tier = row_tier.scalar_one_or_none()

    return {
        "status": "success",
        "data": {
            "tier_name": tier.name if tier else "free",
            "status": sub.status,
            "stripe_subscription_id": sub.stripe_subscription_id,
            "trial_ends_at": sub.trial_ends_at.isoformat() if sub.trial_ends_at else None,
            "current_period_start": sub.current_period_start.isoformat() if sub.current_period_start else None,
            "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
        },
    }
