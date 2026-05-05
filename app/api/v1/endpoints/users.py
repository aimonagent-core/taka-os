# File: app/api/v1/endpoints/users.py
# Purpose: User CRUD with invitations, role changes, and soft delete
# Dependencies: app.dependencies, app.models.ao, app.database, app.services.audit_service

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import (
    get_current_user,
    require_admin,
    require_collaborator,
    require_manager,
)
from app.models.ao import (
    AuditAction,
    InvitationStatus,
    User,
    UserInvitation,
    UserRole,
)
from app.schemas.auth import InvitationCreate
from app.services.audit_service import AuditService

router = APIRouter()

ROLE_HIERARCHY = {
    UserRole.SUPER_ADMIN: 5,
    UserRole.TENANT_ADMIN: 4,
    UserRole.TENANT_MANAGER: 3,
    UserRole.TENANT_COLLABORATOR: 2,
    UserRole.VIEWER: 1,
}


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


@router.get("/")
async def list_users(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    role: str | None = None,
    user: User = Depends(require_collaborator),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List users in the current tenant."""
    offset = (page - 1) * per_page
    query = select(User).where(
        User.deleted_at.is_(None),
        User.is_active == True,  # noqa: E712
    )

    if user.role != UserRole.SUPER_ADMIN:
        query = query.where(User.tenant_id == user.tenant_id)

    if role:
        query = query.where(User.role == role)

    total_result = await db.execute(query)
    total = len(total_result.scalars().all())

    query = query.offset(offset).limit(per_page)
    result = await db.execute(query)
    users = result.scalars().all()

    data = [
        {
            "id": str(u.id),
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role.value,
            "is_active": u.is_active,
            "tenant_id": str(u.tenant_id),
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]

    return _standard_response(
        "success",
        {"items": data},
        "Users retrieved",
        {"page": page, "per_page": per_page, "total": total},
    )


@router.get("/{user_id}")
async def get_user(
    request: Request,
    user_id: str,
    current_user: User = Depends(require_collaborator),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get a single user."""
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target or target.deleted_at is not None:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.role != UserRole.SUPER_ADMIN and target.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return _standard_response(
        "success",
        {
            "id": str(target.id),
            "email": target.email,
            "full_name": target.full_name,
            "role": target.role.value,
            "is_active": target.is_active,
            "tenant_id": str(target.tenant_id),
            "mfa_enabled": target.mfa_enabled,
            "created_at": target.created_at.isoformat() if target.created_at else None,
        },
        "User retrieved",
    )


@router.post("/invite")
async def invite_user(
    request: Request,
    req: InvitationCreate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Invite a user by email."""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    invitation = UserInvitation(
        tenant_id=current_user.tenant_id,
        email=req.email,
        token=token,
        role=UserRole(req.role),
        invited_by_id=current_user.id,
        expires_at=expires_at,
    )
    db.add(invitation)
    await db.flush()

    await AuditService.log(
        db=db,
        action=AuditAction.INVITATION_SENT,
        entity_type="user_invitation",
        entity_id=str(invitation.id),
        user_id=str(current_user.id),
        tenant_id=str(current_user.tenant_id),
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()

    return _standard_response(
        "success",
        {
            "id": str(invitation.id),
            "email": invitation.email,
            "token": invitation.token,
            "expires_at": invitation.expires_at.isoformat(),
        },
        "Invitation sent",
    )


@router.patch("/{user_id}/role")
async def change_role(
    request: Request,
    user_id: str,
    new_role: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Change a user's role with hierarchy validation."""
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target or target.deleted_at is not None:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.role != UserRole.SUPER_ADMIN and target.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        target_role_enum = UserRole(new_role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role")

    # Hierarchy check
    current_level = ROLE_HIERARCHY.get(current_user.role, 0)
    target_level = ROLE_HIERARCHY.get(target_role_enum, 0)
    if target_level > current_level:
        raise HTTPException(
            status_code=403,
            detail="Cannot assign a role higher than your own",
        )

    # Cannot demote self via this endpoint (special case)
    if str(target.id) == str(current_user.id) and target_level < current_level:
        raise HTTPException(status_code=403, detail="Cannot retrograde yourself")

    old_role = target.role
    target.role = target_role_enum

    await AuditService.log(
        db=db,
        action=AuditAction.UPDATE,
        entity_type="user",
        entity_id=user_id,
        payload_before={"role": old_role.value},
        payload_after={"role": target_role_enum.value},
        user_id=str(current_user.id),
        tenant_id=str(target.tenant_id),
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()

    return _standard_response(
        "success",
        {"id": str(target.id), "role": target.role.value},
        "Role updated",
    )


@router.delete("/{user_id}")
async def delete_user(
    request: Request,
    user_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Soft delete a user. Cannot self-delete."""
    if str(current_user.id) == user_id:
        raise HTTPException(status_code=403, detail="Cannot delete yourself")

    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target or target.deleted_at is not None:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.role != UserRole.SUPER_ADMIN and target.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    target.deleted_at = datetime.now(timezone.utc)
    target.is_active = False

    await AuditService.log(
        db=db,
        action=AuditAction.DELETE,
        entity_type="user",
        entity_id=user_id,
        user_id=str(current_user.id),
        tenant_id=str(target.tenant_id),
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()

    return _standard_response("success", None, "User soft deleted")
