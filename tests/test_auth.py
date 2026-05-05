# File: tests/test_auth.py
# Purpose: Authentication flow tests including MFA and invitations
# Dependencies: tests.conftest fixtures

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token, generate_mfa_secret, get_password_hash, encrypt_mfa_secret
from app.models.ao import InvitationStatus, Tenant, User, UserInvitation, UserRole


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient, db_session: AsyncSession):
    resp = await client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "password": "password123",
        "full_name": "New User",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "user_id" in data["data"]
    assert "tenant_id" in data["data"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user: User):
    resp = await client.post("/api/v1/auth/register", json={
        "email": test_user.email,
        "password": "password123",
    })
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: User):
    resp = await client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "password123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]


@pytest.mark.asyncio
async def test_login_mfa_required(client: AsyncClient, db_session: AsyncSession, test_tenant: Tenant):
    secret = generate_mfa_secret()
    user = User(
        tenant_id=test_tenant.id,
        email="mfauser@example.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.VIEWER,
        mfa_enabled=True,
        mfa_secret=encrypt_mfa_secret(secret),
    )
    db_session.add(user)
    await db_session.commit()

    resp = await client.post("/api/v1/auth/login", json={
        "email": user.email,
        "password": "password123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["data"]["mfa_required"] is True
    assert "mfa_token" in data["data"]


@pytest.mark.asyncio
async def test_mfa_verify_success(client: AsyncClient, db_session: AsyncSession, test_tenant: Tenant):
    import pyotp
    secret = generate_mfa_secret()
    user = User(
        tenant_id=test_tenant.id,
        email="mfaverify@example.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.VIEWER,
        mfa_enabled=True,
        mfa_secret=encrypt_mfa_secret(secret),
    )
    db_session.add(user)
    await db_session.commit()

    mfa_token = pyotp.TOTP(secret).now()
    # First get mfa_token from login
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": user.email,
        "password": "password123",
    })
    mfa_challenge_token = login_resp.json()["data"]["mfa_token"]

    resp = await client.post("/api/v1/auth/mfa/verify", params={
        "mfa_token": mfa_challenge_token,
        "code": mfa_token,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data["data"]


@pytest.mark.asyncio
async def test_mfa_verify_invalid_code(client: AsyncClient, db_session: AsyncSession, test_tenant: Tenant):
    secret = generate_mfa_secret()
    user = User(
        tenant_id=test_tenant.id,
        email="mfabad@example.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.VIEWER,
        mfa_enabled=True,
        mfa_secret=encrypt_mfa_secret(secret),
    )
    db_session.add(user)
    await db_session.commit()

    login_resp = await client.post("/api/v1/auth/login", json={
        "email": user.email,
        "password": "password123",
    })
    mfa_challenge_token = login_resp.json()["data"]["mfa_token"]

    resp = await client.post("/api/v1/auth/mfa/verify", params={
        "mfa_token": mfa_challenge_token,
        "code": "000000",
    })
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, test_user: User):
    from app.core.security import create_refresh_token
    token = create_refresh_token(str(test_user.id))
    resp = await client.post("/api/v1/auth/refresh", params={"refresh_token": token})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data["data"]


@pytest.mark.asyncio
async def test_refresh_invalid(client: AsyncClient):
    resp = await client.post("/api/v1/auth/refresh", params={"refresh_token": "invalid"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_invitation_accept(client: AsyncClient, db_session: AsyncSession, test_admin: User, test_tenant: Tenant):
    from datetime import datetime, timedelta, timezone
    invitation = UserInvitation(
        tenant_id=test_tenant.id,
        email="invited@example.com",
        token="invitetoken123",
        role=UserRole.VIEWER,
        invited_by_id=test_admin.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db_session.add(invitation)
    await db_session.commit()

    resp = await client.post("/api/v1/auth/invitation/accept", json={
        "token": "invitetoken123",
        "password": "password123",
        "full_name": "Invited User",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "user_id" in data["data"]

    # Check invitation status
    result = await db_session.execute(
        select(UserInvitation).where(UserInvitation.token == "invitetoken123")
    )
    inv = result.scalar_one()
    assert inv.status == InvitationStatus.ACCEPTED


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, auth_headers: dict, test_user: User):
    resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["data"]["email"] == test_user.email
