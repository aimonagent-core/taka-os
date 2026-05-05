# File: app/api/v1/auth_mfa.py
# Purpose: MFA setup and management endpoints
# Dependencies: app.dependencies, app.core.security, app.models.ao, qrcode, io, base64

import base64
from io import BytesIO

import qrcode
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    decrypt_mfa_secret,
    encrypt_mfa_secret,
    generate_mfa_secret,
    get_totp_uri,
    verify_totp,
)
from app.database import get_db
from app.dependencies import get_current_user
from app.models.ao import User

router = APIRouter(prefix="/mfa", tags=["MFA"])


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


@router.post("/enable")
async def enable_mfa(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Generate MFA secret and return QR code as base64 PNG."""
    if user.mfa_enabled:
        raise HTTPException(status_code=400, detail="MFA already enabled")
    secret = generate_mfa_secret()
    uri = get_totp_uri(secret, user.email)
    qr = qrcode.make(uri)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_b64 = base64.b64encode(buffer.getvalue()).decode("ascii")
    user.mfa_secret = encrypt_mfa_secret(secret)
    await db.commit()
    return _standard_response(
        "success",
        {
            "qr_code_base64": f"data:image/png;base64,{qr_b64}",
            "secret": secret,
        },
        "Scan the QR code with your authenticator app, then verify to enable",
    )


@router.post("/verify-and-enable")
async def verify_and_enable_mfa(
    code: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Verify TOTP code and permanently enable MFA."""
    if not user.mfa_secret:
        raise HTTPException(
            status_code=400, detail="MFA not set up. Call /enable first."
        )
    secret = decrypt_mfa_secret(user.mfa_secret)
    if not verify_totp(secret, code):
        raise HTTPException(status_code=400, detail="Invalid TOTP code")
    user.mfa_enabled = True
    await db.commit()
    return _standard_response(
        "success",
        {"mfa_enabled": True},
        "MFA enabled successfully",
    )


@router.post("/disable")
async def disable_mfa(
    code: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Disable MFA after verifying a TOTP code."""
    if not user.mfa_enabled or not user.mfa_secret:
        raise HTTPException(status_code=400, detail="MFA is not enabled")
    secret = decrypt_mfa_secret(user.mfa_secret)
    if not verify_totp(secret, code):
        raise HTTPException(status_code=400, detail="Invalid TOTP code")
    user.mfa_enabled = False
    user.mfa_secret = None
    await db.commit()
    return _standard_response(
        "success",
        {"mfa_enabled": False},
        "MFA disabled successfully",
    )
