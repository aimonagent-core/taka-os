"""Routes API pour l'onboarding self-serve."""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import create_access_token, get_password_hash
from app.database import get_db
from app.dependencies import get_current_user
from app.models.ao import Tenant, TenantType, User, UserRole
from app.models.billing import EmailPreference, TenantSubscription
from app.models.business_line import BusinessLine
from app.models.feature_flag import SubscriptionTier
from app.services.email.service import EmailService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


class OnboardingRegister:
    email: str
    password: str
    first_name: str
    last_name: str
    company_name: str


@router.post("/register")
async def onboarding_register(
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    company_name: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Inscription initiale : cree le tenant + l'utilisateur admin."""
    # Verifier si l'email existe deja
    stmt = select(User).where(User.email == email)
    row = await db.execute(stmt)
    if row.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cet email est deja utilise",
        )

    # Creer le tenant
    import uuid
    slug_base = company_name.lower().replace(" ", "-")[:50]
    slug = slug_base
    counter = 1
    while True:
        existing = await db.execute(select(Tenant).where(Tenant.slug == slug))
        if not existing.scalar_one_or_none():
            break
        slug = f"{slug_base}-{counter}"
        counter += 1

    tenant = Tenant(
        id=uuid.uuid4(),
        name=company_name,
        type=TenantType.SOUMISSIONNAIRE,
        slug=slug,
        billing_plan="free",
        is_active=True,
    )
    db.add(tenant)
    await db.flush()

    # Tier par defaut = free
    stmt_free = select(SubscriptionTier).where(SubscriptionTier.name == "free")
    row_free = await db.execute(stmt_free)
    free_tier = row_free.scalar_one()

    # Creer la souscription
    sub = TenantSubscription(
        tenant_id=tenant.id,
        tier_id=free_tier.id,
        status="active",
    )
    db.add(sub)

    # Creer l'utilisateur admin
    user = User(
        id=uuid.uuid4(),
        email=email,
        hashed_password=get_password_hash(password),
        full_name=full_name,
        tenant_id=tenant.id,
        role=UserRole.TENANT_ADMIN,
        is_active=True,
        email_verified=True,
    )
    db.add(user)
    await db.flush()

    # Preferences email par defaut
    prefs = EmailPreference(user_id=user.id)
    db.add(prefs)
    await db.commit()

    # Envoyer email de bienvenue
    await EmailService.send_welcome_email(
        db,
        recipient=email,
        user_name=full_name,
        tenant_id=str(tenant.id),
        user_id=str(user.id),
    )

    # Generer le token JWT
    token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "tenant_id": str(tenant.id),
        }
    )

    logger.info(f"[Onboarding] Nouveau tenant cree : {tenant.name} ({tenant.id})")
    return {
        "status": "success",
        "data": {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "tenant_id": str(tenant.id),
            },
        },
        "message": "Compte cree avec succes",
    }


@router.post("/setup")
async def onboarding_setup(
    business_line_name: str = Form(...),
    cpv_keywords: Optional[list[str]] = Form(None),
    plan_name: Optional[str] = Form(None),
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
            db.add(BLCPVKeyword(
                business_line_id=bl.id,
                cpv_code=kw,
                label=kw,
                weight=1.0,
            ))

    # Si un plan payant est selectionne, mettre a jour la souscription
    if plan_name and plan_name in ("pro", "enterprise"):
        stmt = select(SubscriptionTier).where(SubscriptionTier.name == plan_name)
        row = await db.execute(stmt)
        tier = row.scalar_one_or_none()

        if tier:
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
