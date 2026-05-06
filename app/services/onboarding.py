# =============================================================================
# C16 — Service de onboarding : creation tenant + admin
# =============================================================================

import logging
import uuid
from typing import Tuple

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.ao import Tenant, TenantType, User, UserRole
from app.models.billing import EmailPreference, TenantSubscription
from app.models.feature_flag import SubscriptionTier
from app.services.email.service import EmailService

logger = logging.getLogger(__name__)


async def create_tenant_and_admin(
    db: AsyncSession,
    tenant_name: str,
    admin_email: str,
    admin_password: str,
    admin_full_name: str | None,
    plan: str = "free",
) -> Tuple[Tenant, User]:
    """Cree un nouveau tenant avec son administrateur.

    Cette fonction cree en transaction atomique :
    1. Un tenant avec les parametres specifies
    2. Un utilisateur TENANT_ADMIN associe a ce tenant
    3. Une souscription au tier 'free' par defaut
    4. Les preferences email par defaut

    Args:
        db: Session async SQLAlchemy
        tenant_name: Nom du nouveau tenant
        admin_email: Email de l'administrateur
        admin_password: Mot de passe en clair (sera hashe)
        admin_full_name: Nom complet (optionnel)
        plan: Plan de souscription (default: free)

    Returns:
        Tuple (Tenant, User) crees

    Raises:
        HTTPException 409 si l'email existe deja
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

    # --- Creer le tenant ---
    tenant = Tenant(
        id=uuid.uuid4(),
        name=tenant_name,
        type=TenantType.SOUMISSIONNAIRE,
        slug=slug,
        billing_plan=plan,
        is_active=True,
    )
    db.add(tenant)
    await db.flush()  # Pour obtenir l'ID du tenant

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

    await db.commit()
    await db.refresh(tenant)
    await db.refresh(user)

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
        "Tenant '%s' (id=%s) et admin '%s' crees",
        tenant_name,
        tenant.id,
        admin_email,
    )
    return tenant, user
