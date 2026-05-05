# File: tests/test_tenants.py
# Purpose: Tenant CRUD tests with role-based permissions
# Dependencies: tests.conftest fixtures

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ao import Tenant, User, UserRole


@pytest.mark.asyncio
async def test_list_tenants_as_admin(client: AsyncClient, admin_headers: dict, test_tenant: Tenant):
    resp = await client.get("/api/v1/tenants/", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert len(data["data"]["items"]) >= 1


@pytest.mark.asyncio
async def test_list_tenants_as_viewer(client: AsyncClient, auth_headers: dict, test_tenant: Tenant):
    resp = await client.get("/api/v1/tenants/", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    # Viewer should only see their own tenant
    assert all(item["id"] == str(test_tenant.id) for item in data["data"]["items"])


@pytest.mark.asyncio
async def test_create_tenant_as_super_admin(client: AsyncClient, db_session: AsyncSession):
    # Create a super admin
    from app.core.security import get_password_hash
    super_admin = User(
        tenant_id=None,  # type: ignore[arg-type]
        email="super@example.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.SUPER_ADMIN,
    )
    db_session.add(super_admin)
    await db_session.commit()

    from app.core.security import create_access_token
    headers = {"Authorization": f"Bearer {create_access_token(str(super_admin.id))}"}

    resp = await client.post("/api/v1/tenants/", headers=headers, json={
        "name": "New Super Tenant",
        "type": "acheteur",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["data"]["name"] == "New Super Tenant"


@pytest.mark.asyncio
async def test_create_tenant_as_viewer(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/tenants/", headers=auth_headers, json={
        "name": "Forbidden Tenant",
    })
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_update_tenant(client: AsyncClient, admin_headers: dict, test_tenant: Tenant):
    resp = await client.patch(
        f"/api/v1/tenants/{test_tenant.id}",
        headers=admin_headers,
        json={"name": "Updated Tenant Name"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["data"]["name"] == "Updated Tenant Name"


@pytest.mark.asyncio
async def test_soft_delete_tenant(
    client: AsyncClient, db_session: AsyncSession, test_tenant: Tenant
):
    from app.core.security import get_password_hash, create_access_token
    super_admin = User(
        tenant_id=test_tenant.id,
        email="super2@example.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.SUPER_ADMIN,
    )
    db_session.add(super_admin)
    await db_session.commit()
    headers = {"Authorization": f"Bearer {create_access_token(str(super_admin.id))}"}

    resp = await client.delete(f"/api/v1/tenants/{test_tenant.id}", headers=headers)
    assert resp.status_code == 200

    result = await db_session.execute(select(Tenant).where(Tenant.id == test_tenant.id))
    tenant = result.scalar_one()
    assert tenant.deleted_at is not None
