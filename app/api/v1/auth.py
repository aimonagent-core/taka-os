# File: app/api/v1/auth.py
# Purpose: Authentication endpoints with JWT, MFA challenge, and invitations
# Dependencies: app.dependencies, app.core.security, app.models.ao, app.database, app.services.audit_service

import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import now_utc
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    decrypt_mfa_secret,
    get_password_hash,
    verify_backup_code,
    verify_password,
    verify_totp,
)
from app.core.sentry import clear_sentry_user
from app.database import get_db
from app.dependencies import get_current_user, set_request_state_user
from app.models.ao import (
    AuditAction,
    InvitationStatus,
    Tenant,
    TenantType,
    User,
    UserInvitation,
    UserRole,
)
from app.schemas.auth import (
    InvitationAccept,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.services.audit_service import AuditService

router = APIRouter(tags=["Authentication"])


def _standard_response(
    status_str: str,
    data: dict | None,
    message: str | None = None,
    meta: dict | None = None,
) -> dict:
    return {
        "status": status_str,
        "data": data,
        "message": message,
        "meta": meta,
    }


@router.post("/register")
async def register(
    req: UserRegister,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Register a new user with a default tenant."""
    existing = await db.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    tenant_name = req.tenant_name or f"Tenant of {req.email}"
    slug_base = tenant_name.lower().replace(" ", "-")[:50]
    slug = slug_base
    counter = 1
    while True:
        existing_tenant = await db.execute(
            select(Tenant).where(Tenant.slug == slug)
        )
        if not existing_tenant.scalar_one_or_none():
            break
        slug = f"{slug_base}-{counter}"
        counter += 1

    tenant = Tenant(
        name=tenant_name,
        type=TenantType.SOUMISSIONNAIRE,
        slug=slug,
    )
    db.add(tenant)
    await db.flush()

    user = User(
        tenant_id=tenant.id,
        email=req.email,
        hashed_password=get_password_hash(req.password),
        full_name=req.full_name,
        role=UserRole.VIEWER,
    )
    db.add(user)
    await db.commit()

    return _standard_response(
        "success",
        {"user_id": str(user.id), "tenant_id": str(tenant.id)},
        "User registered successfully",
    )


@router.post("/login")
async def login(
    req: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Authenticate user. Returns tokens or MFA challenge."""
    result = await db.execute(
        select(User).where(
            User.email == req.email,
            User.is_active == True,  # noqa: E712
            User.deleted_at.is_(None),
        )
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if user.mfa_enabled:
        if not req.mfa_code:
            mfa_token = create_access_token(
                subject=str(user.id),
                expires_delta=timedelta(minutes=5),
                extra_claims={"type": "mfa_challenge"},
            )
            return _standard_response(
                "success",
                {"mfa_required": True, "mfa_token": mfa_token},
                "MFA code required",
            )
        secret = decrypt_mfa_secret(user.mfa_secret)
        if not verify_totp(secret, req.mfa_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA code",
            )

    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))
    user.last_login_at = now_utc()

    await AuditService.log(
        db=db,
        action=AuditAction.LOGIN,
        entity_type="user",
        entity_id=str(user.id),
        user_id=str(user.id),
        tenant_id=str(user.tenant_id),
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()

    return _standard_response(
        "success",
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        },
        "Login successful",
    )


async def _mfa_attempt_key(user_id: str) -> str:
    """Cle Redis pour le compteur de tentatives MFA."""
    return f"mfa_attempts:{user_id}"


async def _mfa_rate_limit_check(user_id: str) -> tuple[bool, int]:
    """Verifie si l'utilisateur a depasse la limite de tentatives MFA.
    Retourne (allowed, remaining_attempts).
    """
    import redis.asyncio as redis
    from app.config import settings
    try:
        r = redis.from_url(settings.redis_url, decode_responses=True)
    except Exception:
        import fakeredis.aioredis
        r = fakeredis.aioredis.FakeRedis()
    key = await _mfa_attempt_key(user_id)
    current = await r.get(key)
    if current and int(current) >= 5:
        ttl = await r.ttl(key)
        return False, 0
    return True, 5 - (int(current) if current else 0)


async def _mfa_attempt_increment(user_id: str):
    """Incrémente le compteur de tentatives MFA echouees."""
    import redis.asyncio as redis
    from app.config import settings
    try:
        r = redis.from_url(settings.redis_url, decode_responses=True)
    except Exception:
        import fakeredis.aioredis
        r = fakeredis.aioredis.FakeRedis()
    key = await _mfa_attempt_key(user_id)
    pipe = r.pipeline()
    pipe.incr(key)
    pipe.expire(key, 300)
    await pipe.execute()


async def _mfa_attempt_reset(user_id: str):
    """Reset le compteur de tentatives MFA."""
    import redis.asyncio as redis
    from app.config import settings
    try:
        r = redis.from_url(settings.redis_url, decode_responses=True)
    except Exception:
        import fakeredis.aioredis
        r = fakeredis.aioredis.FakeRedis()
    key = await _mfa_attempt_key(user_id)
    await r.delete(key)


@router.post("/mfa/verify")
async def mfa_verify(
    mfa_token: str,
    code: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Verify MFA code (TOTP or backup code) and issue tokens."""
    payload = decode_token(mfa_token)
    if not payload or payload.get("type") != "mfa_challenge":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA token",
        )

    user_id = payload.get("sub")

    # --- Rate limiting ---
    allowed, remaining = await _mfa_rate_limit_check(user_id)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de tentatives echouees. Reessayez dans 5 minutes.",
        )

    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.is_active == True,  # noqa: E712
            User.deleted_at.is_(None),
        )
    )
    user = result.scalar_one_or_none()
    if not user or not user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not configured",
        )

    # --- Verification TOTP ---
    secret = decrypt_mfa_secret(user.mfa_secret)
    ok = verify_totp(secret, code)

    # --- Verification backup code (fallback) ---
    if not ok and user.mfa_backup_codes_hash:
        ok, remaining_codes = verify_backup_code(user.mfa_backup_codes_hash, code)
        if ok:
            user.mfa_backup_codes_hash = remaining_codes

    if not ok:
        await _mfa_attempt_increment(user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Code invalide. Tentatives restantes: {remaining - 1}",
        )

    # Reset compteur en cas de succes
    await _mfa_attempt_reset(user_id)

    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))
    user.last_login_at = now_utc()

    await AuditService.log(
        db=db,
        action=AuditAction.LOGIN,
        entity_type="user",
        entity_id=str(user.id),
        user_id=str(user.id),
        tenant_id=str(user.tenant_id),
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()

    return _standard_response(
        "success",
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        },
        "MFA verification successful",
    )


@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Exchange a valid refresh token for a new access token."""
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.is_active == True,  # noqa: E712
            User.deleted_at.is_(None),
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    new_access_token = create_access_token(subject=str(user.id))
    return _standard_response(
        "success",
        {"access_token": new_access_token, "token_type": "bearer"},
        "Token refreshed",
    )


@router.post("/logout")
async def logout(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Client-side logout. Clears Sentry context."""
    clear_sentry_user()
    await AuditService.log(
        db=db,
        action=AuditAction.LOGOUT,
        entity_type="user",
        entity_id=str(user.id),
        user_id=str(user.id),
        tenant_id=str(user.tenant_id),
    )
    await db.commit()
    return _standard_response("success", None, "Logout successful")


@router.post("/invitation/accept")
async def accept_invitation(
    req: InvitationAccept,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Accept an invitation using a secure token."""
    result = await db.execute(
        select(UserInvitation).where(
            UserInvitation.token == req.token,
            UserInvitation.status == InvitationStatus.PENDING,
        )
    )
    invitation = result.scalar_one_or_none()
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired invitation token",
        )

    if invitation.expires_at < now_utc():
        invitation.status = InvitationStatus.EXPIRED
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired",
        )

    existing_user = await db.execute(
        select(User).where(User.email == invitation.email)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    user = User(
        tenant_id=invitation.tenant_id,
        email=invitation.email,
        hashed_password=get_password_hash(req.password),
        full_name=req.full_name,
        role=invitation.role,
        email_verified=True,
    )
    db.add(user)

    invitation.status = InvitationStatus.ACCEPTED
    invitation.accepted_at = now_utc()

    await AuditService.log(
        db=db,
        action=AuditAction.INVITATION_ACCEPTED,
        entity_type="user_invitation",
        entity_id=str(invitation.id),
        user_id=str(user.id),
        tenant_id=str(invitation.tenant_id),
    )
    await db.commit()

    return _standard_response(
        "success",
        {"user_id": str(user.id)},
        "Invitation accepted successfully",
    )


@router.get("/me")
async def get_me(
    user: User = Depends(get_current_user),
) -> dict:
    """Return current authenticated user info."""
    return _standard_response(
        "success",
        {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "is_active": user.is_active,
            "tenant_id": str(user.tenant_id),
            "mfa_enabled": user.mfa_enabled,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        },
        "User info retrieved",
    )
