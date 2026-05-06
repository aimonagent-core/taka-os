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
from app.models.tenant_profile import TenantCPVPreference
from app.schemas.onboarding import OnboardingSetupRequest, OnboardingSetupResponse
from app.schemas.onboarding_enterprise import (
    OnboardingEnterpriseRequest,
    OnboardingEnterpriseResponse,
    OnboardingStatusResponse,
)
from app.services.onboarding import create_tenant_and_admin
from app.services.onboarding_enterprise import create_tenant_enterprise

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
# Sprint 11 — Onboarding entreprise complet (5 etapes)
# =============================================================================

@router.post(
    "/enterprise-setup",
    response_model=OnboardingEnterpriseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Configuration initiale entreprise — cree tenant + admin + profil",
)
async def onboarding_enterprise_setup(
    request_data: OnboardingEnterpriseRequest,
    db: AsyncSession = Depends(get_db),
) -> OnboardingEnterpriseResponse:
    """Cree un nouveau tenant entreprise avec son administrateur et son profil complet."""
    tenant, user, token = await create_tenant_enterprise(
        db=db,
        tenant_name=request_data.tenant_name,
        siret=request_data.siret,
        admin_email=request_data.admin_email,
        admin_password=request_data.admin_password,
        admin_full_name=request_data.admin_full_name,
        domaine_activite=request_data.domaine_activite,
        cpv_preferences=[cpv.model_dump() for cpv in request_data.cpv_preferences],
        effectif=request_data.effectif,
        ca_annuel=request_data.ca_annuel,
        zones_geo=request_data.zones_geo,
        types_marche_acceptes=request_data.types_marche_acceptes,
        plan=request_data.plan,
    )

    return OnboardingEnterpriseResponse(
        tenant_id=str(tenant.id),
        tenant_uuid=str(tenant.id),
        admin_user_id=str(user.id),
        admin_email=user.email,
        access_token=token,
        token_type="bearer",
        onboarding_completed=tenant.onboarding_completed,
        message="Tenant entreprise et administrateur crees avec succes.",
    )


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


@router.get("/status/{tenant_id}", response_model=OnboardingStatusResponse)
async def onboarding_status_by_id(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Verifie le statut d'onboarding d'un tenant par son ID."""
    stmt = select(Tenant).where(Tenant.id == tenant_id)
    row = await db.execute(stmt)
    tenant = row.scalar_one_or_none()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant non trouve")

    # Verifier que l'utilisateur appartient bien a ce tenant (ou est super admin)
    if str(current_user.tenant_id) != tenant_id and current_user.role.value != "super_admin":
        raise HTTPException(status_code=403, detail="Acces refuse")

    stmt_cpv = select(TenantCPVPreference).where(
        TenantCPVPreference.tenant_id == tenant.id
    )
    row_cpv = await db.execute(stmt_cpv)
    has_cpv = row_cpv.scalar_one_or_none() is not None

    stmt_bl = select(BusinessLine).where(
        BusinessLine.tenant_id == tenant.id,
        BusinessLine.is_active.is_(True),
    )
    row_bl = await db.execute(stmt_bl)
    has_bl = row_bl.scalar_one_or_none() is not None

    return OnboardingStatusResponse(
        tenant_id=str(tenant.id),
        onboarding_completed=tenant.onboarding_completed,
        onboarding_completed_at=tenant.onboarding_completed_at.isoformat() if tenant.onboarding_completed_at else None,
        has_cpv_preferences=has_cpv,
        has_business_line=has_bl,
        fields_filled={
            "siret": tenant.siret is not None,
            "domaine_activite": len(tenant.domaine_activite or []) > 0,
            "effectif": tenant.effectif is not None,
            "ca_annuel": tenant.ca_annuel is not None,
            "zones_geo": len(tenant.zones_geo or []) > 0,
            "types_marche_acceptes": len(tenant.types_marche_acceptes or []) > 0,
        },
    )
