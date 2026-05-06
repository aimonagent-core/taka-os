"""Service Sprint 11 — Onboarding entreprise avec profil complet."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Tuple

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, create_access_token
from app.models.ao import Tenant, TenantType, User, UserRole
from app.models.billing import EmailPreference, TenantSubscription
from app.models.feature_flag import SubscriptionTier
from app.models.tenant_profile import TenantCPVPreference
from app.services.email.service import EmailService

logger = logging.getLogger(__name__)


async def create_tenant_enterprise(
    db: AsyncSession,
    tenant_name: str,
    siret: str,
    admin_email: str,
    admin_password: str,
    admin_full_name: str | None,
    domaine_activite: list[str],
    cpv_preferences: list[dict],
    effectif: str | None,
    ca_annuel: float | None,
    zones_geo: list[str],
    types_marche_acceptes: list[str],
    plan: str = "free",
) -> Tuple[Tenant, User, str]:
    """Cree un nouveau tenant entreprise avec son administrateur et son profil.

    Cette fonction cree en transaction atomique :
    1. Un tenant avec les parametres specifies
    2. Un utilisateur TENANT_ADMIN associe a ce tenant
    3. Une souscription au tier 'free' par defaut
    4. Les preferences email par defaut
    5. Les preferences CPV du tenant
    """
    # --- Verifier que l'email n'existe pas deja ---
    existing = await db.execute(select(User).where(User.email == admin_email))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cet email est deja utilise.",
        )

    # --- Generer le slug du tenant ---
    slug_base = tenant_name.lower().replace(" ", "-")[:50]
    slug = slug_base
    counter = 1
    while True:
        existing_slug = await db.execute(
            select(Tenant).where(Tenant.slug == slug)
        )
        if not existing_slug.scalar_one_or_none():
            break
        slug = f"{slug_base}-{counter}"
        counter += 1

    # --- Creer le tenant avec les champs onboarding ---
    tenant = Tenant(
        id=uuid.uuid4(),
        name=tenant_name,
        type=TenantType.SOUMISSIONNAIRE,
        slug=slug,
        billing_plan=plan,
        siret=siret,
        domaine_activite=domaine_activite or [],
        effectif=effectif,
        ca_annuel=ca_annuel,
        zones_geo=zones_geo or [],
        types_marche_acceptes=types_marche_acceptes or [],
        onboarding_completed=True,
        onboarding_completed_at=datetime.now(timezone.utc),
        is_active=True,
    )
    db.add(tenant)
    await db.flush()

    # --- Tier par defaut = free ---
    stmt_free = select(SubscriptionTier).where(SubscriptionTier.name == "free")
    row_free = await db.execute(stmt_free)
    free_tier = row_free.scalar_one_or_none()

    if free_tier:
        sub = TenantSubscription(
            tenant_id=tenant.id,
            tier_id=free_tier.id,
            status="active",
        )
        db.add(sub)
        await db.flush()

    # --- Creer l'admin ---
    hashed_pw = get_password_hash(admin_password)
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        email=admin_email,
        hashed_password=hashed_pw,
        full_name=admin_full_name,
        role=UserRole.TENANT_ADMIN,
        is_active=True,
        email_verified=True,
    )
    db.add(user)
    await db.flush()

    # --- Preferences email par defaut ---
    prefs = EmailPreference(user_id=user.id)
    db.add(prefs)

    # --- Preferences CPV ---
    for cpv in (cpv_preferences or []):
        db.add(
            TenantCPVPreference(
                tenant_id=tenant.id,
                cpv_code=cpv["cpv_code"],
                label=cpv["label"],
                weight=cpv.get("weight", 1.0),
            )
        )

    await db.commit()
    await db.refresh(tenant)
    await db.refresh(user)

    # --- Generer le token JWT ---
    token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "tenant_id": str(tenant.id),
        }
    )

    # --- Email de bienvenue (fire-and-forget) ---
    try:
        await EmailService.send_welcome_email(
            db,
            recipient=admin_email,
            user_name=admin_full_name or admin_email,
            tenant_id=str(tenant.id),
            user_id=str(user.id),
        )
    except Exception:
        logger.warning("[Onboarding] Echec envoi email de bienvenue", exc_info=True)

    logger.info(
        "Tenant entreprise '%s' (siret=%s, id=%s) et admin '%s' crees",
        tenant_name,
        siret,
        tenant.id,
        admin_email,
    )
    return tenant, user, token
