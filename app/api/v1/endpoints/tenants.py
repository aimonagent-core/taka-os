# File: app/api/v1/endpoints/tenants.py
# Purpose: Tenant CRUD with role-based access control
# Dependencies: app.dependencies, app.models.ao, app.database, app.services.audit_service

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import (
    get_current_user,
    require_admin,
    require_any_authenticated,
)
from app.models.ao import AuditAction, Tenant, UserRole
from app.schemas.tenant import TenantCreate, TenantResponse, TenantUpdate
from app.services.audit_service import AuditService

router = APIRouter()


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
async def list_tenants(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    include_deleted: bool = Query(False),
    user: dict = Depends(require_any_authenticated),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List tenants with pagination and visibility rules."""
    offset = (page - 1) * per_page
    query = select(Tenant)

    if user.role != UserRole.SUPER_ADMIN:
        query = query.where(Tenant.id == user.tenant_id)
        if not include_deleted:
            query = query.where(Tenant.deleted_at.is_(None))
    else:
        if not include_deleted:
            query = query.where(Tenant.deleted_at.is_(None))

    total_result = await db.execute(query)
    total = len(total_result.scalars().all())

    query = query.offset(offset).limit(per_page)
    result = await db.execute(query)
    tenants = result.scalars().all()

    data = [TenantResponse.model_validate(t).model_dump() for t in tenants]

    await AuditService.log(
        db=db,
        action=AuditAction.READ,
        entity_type="tenant",
        user_id=str(user.id),
        tenant_id=str(user.tenant_id),
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()

    return _standard_response(
        "success",
        {"items": data},
        "Tenants retrieved",
        {"page": page, "per_page": per_page, "total": total},
    )


@router.get("/{tenant_id}")
async def get_tenant(
    request: Request,
    tenant_id: str,
    user: dict = Depends(require_any_authenticated),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get a single tenant by ID."""
    result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if user.role != UserRole.SUPER_ADMIN and tenant.id != user.tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    await AuditService.log(
        db=db,
        action=AuditAction.READ,
        entity_type="tenant",
        entity_id=tenant_id,
        user_id=str(user.id),
        tenant_id=str(tenant.id),
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()

    return _standard_response(
        "success",
        TenantResponse.model_validate(tenant).model_dump(),
        "Tenant retrieved",
    )


@router.post("/")
async def create_tenant(
    request: Request,
    req: TenantCreate,
    user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Create a new tenant."""
    slug = req.slug or req.name.lower().replace(" ", "-")[:50]
    existing = await db.execute(select(Tenant).where(Tenant.slug == slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Slug already exists")

    tenant = Tenant(
        name=req.name,
        type=req.type,
        slug=slug,
    )
    db.add(tenant)
    await db.flush()

    await AuditService.log(
        db=db,
        action=AuditAction.CREATE,
        entity_type="tenant",
        entity_id=str(tenant.id),
        user_id=str(user.id),
        tenant_id=str(tenant.id),
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()

    return _standard_response(
        "success",
        TenantResponse.model_validate(tenant).model_dump(),
        "Tenant created",
    )


@router.patch("/{tenant_id}")
async def update_tenant(
    request: Request,
    tenant_id: str,
    req: TenantUpdate,
    user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Partially update a tenant."""
    result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    if tenant.deleted_at is not None:
        raise HTTPException(status_code=400, detail="Cannot update deleted tenant")

    if user.role != UserRole.SUPER_ADMIN and tenant.id != user.tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    payload_before = {
        k: getattr(tenant, k)
        for k in ("name", "type", "settings", "billing_plan", "max_users", "is_active")
    }

    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tenant, key, value)

    await AuditService.log(
        db=db,
        action=AuditAction.UPDATE,
        entity_type="tenant",
        entity_id=tenant_id,
        payload_before=payload_before,
        payload_after=update_data,
        user_id=str(user.id),
        tenant_id=str(tenant.id),
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()

    return _standard_response(
        "success",
        TenantResponse.model_validate(tenant).model_dump(),
        "Tenant updated",
    )


@router.delete("/{tenant_id}")
async def delete_tenant(
    request: Request,
    tenant_id: str,
    user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Soft delete a tenant and cascade to users."""
    if user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=403, detail="Only super admin can delete tenants"
        )

    from datetime import datetime, timezone

    result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    tenant.deleted_at = datetime.now(timezone.utc)

    # Cascade soft delete to users
    from app.models.ao import User

    user_result = await db.execute(
        select(User).where(User.tenant_id == tenant_id)
    )
    for u in user_result.scalars().all():
        u.deleted_at = tenant.deleted_at

    await AuditService.log(
        db=db,
        action=AuditAction.DELETE,
        entity_type="tenant",
        entity_id=tenant_id,
        user_id=str(user.id),
        tenant_id=tenant_id,
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()

    return _standard_response("success", None, "Tenant soft deleted")
