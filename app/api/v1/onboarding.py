"""Routes API pour l'onboarding self-serve."""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import create_access_token
from app.database import get_db
from app.dependencies import get_current_user
from app.models.ao import Tenant, User
from app.models.business_line import BusinessLine
from app.models.feature_flag import SubscriptionTier
from app.schemas.onboarding import OnboardingSetupRequest, OnboardingSetupResponse
from app.services.onboarding import create_tenant_and_admin

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


# =============================================================================
# C4/C5/C10 — Endpoint onboarding renomme et converti en Pydantic
# =============================================================================

@router.post(
    "/setup",
    response_model=OnboardingSetupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Configuration initiale — cree un tenant et un admin",
    description="""
    Endpoint de setup initial pour un nouveau client.
    Cree un tenant + un utilisateur TENANT_ADMIN.
    DIFFERENT de POST /auth/register qui cree un utilisateur VIEWER existant.
    """,
)
async def onboarding_setup(
    request_data: OnboardingSetupRequest,
    db: AsyncSession = Depends(get_db),
) -> OnboardingSetupResponse:
    """Cree un nouveau tenant avec son administrateur.

    Cet endpoint est le point d'entree pour un nouveau client.
    Il cree simultanement :
    - Un tenant avec le plan et la configuration specifies
    - Un utilisateur TENANT_ADMIN associe a ce tenant

    Le endpoint /auth/register reste le chemin canonique pour l'inscription
    d'utilisateurs supplementaires sur un tenant existant.
    """
    tenant, user = await create_tenant_and_admin(
        db=db,
        tenant_name=request_data.tenant_name,
        admin_email=request_data.admin_email,
        admin_password=request_data.admin_password,
        admin_full_name=request_data.admin_full_name,
        plan=request_data.plan,
    )

    # Generer le token JWT
    token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "tenant_id": str(tenant.id),
        }
    )

    return OnboardingSetupResponse(
        tenant_id=str(tenant.id),
        tenant_uuid=str(tenant.id),
        admin_user_id=str(user.id),
        admin_email=user.email,
        access_token=token,
        token_type="bearer",
        message="Tenant et administrateur crees avec succes.",
    )


# =============================================================================
# Configuration post-inscription : ligne metier + plan
# =============================================================================

@router.post("/configure")
async def onboarding_configure(
    business_line_name: str,
    cpv_keywords: Optional[list[str]] = None,
    plan_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Configuration post-inscription : ligne metier + plan."""
    import uuid

    # Creer la premiere ligne metier
    bl = BusinessLine(
        id=uuid.uuid4(),
        tenant_id=current_user.tenant_id,
        name=business_line_name,
        color="#2563eb",
        is_active=True,
    )
    db.add(bl)
    await db.flush()

    # Ajouter les mots-cles CPV si fournis
    if cpv_keywords:
        from app.models.business_line import BLCPVKeyword
        for kw in cpv_keywords:
            db.add(
                BLCPVKeyword(
                    business_line_id=bl.id,
                    cpv_code=kw,
                    label=kw,
                    weight=1.0,
                )
            )

    # Si un plan payant est selectionne, mettre a jour la souscription
    if plan_name and plan_name in ("pro", "enterprise"):
        stmt = select(SubscriptionTier).where(SubscriptionTier.name == plan_name)
        row = await db.execute(stmt)
        tier = row.scalar_one_or_none()

        if tier:
            from app.models.billing import TenantSubscription
            stmt_sub = select(TenantSubscription).where(
                TenantSubscription.tenant_id == current_user.tenant_id
            )
            row_sub = await db.execute(stmt_sub)
            sub = row_sub.scalar_one_or_none()

            if sub:
                sub.tier_id = tier.id
                sub.status = "active"

    await db.commit()

    return {
        "status": "success",
        "data": {
            "business_line_id": str(bl.id),
            "business_line_name": bl.name,
        },
        "message": "Configuration terminee",
    }


# =============================================================================
# Statut onboarding
# =============================================================================

@router.get("/status")
async def onboarding_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Verifie si l'onboarding est complet."""
    stmt = select(BusinessLine).where(
        BusinessLine.tenant_id == current_user.tenant_id,
        BusinessLine.is_active.is_(True),
    )
    row = await db.execute(stmt)
    has_bl = row.scalar_one_or_none() is not None

    from app.models.billing import TenantSubscription
    stmt_sub = select(TenantSubscription).where(
        TenantSubscription.tenant_id == current_user.tenant_id
    )
    row_sub = await db.execute(stmt_sub)
    sub = row_sub.scalar_one_or_none()

    return {
        "status": "success",
        "data": {
            "onboarding_complete": has_bl,
            "has_business_line": has_bl,
            "subscription_tier": sub.status if sub else "free",
        },
    }
