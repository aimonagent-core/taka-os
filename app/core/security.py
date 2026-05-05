# File: app/core/security.py
# Purpose: Password hashing, JWT tokens, and MFA/TOTP handling
# Dependencies: app.config.settings, passlib, python-jose, pyotp

import base64
from datetime import datetime, timedelta, timezone
from typing import Any

import pyotp
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = settings.algorithm


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    subject: str | Any,
    expires_delta: timedelta | None = None,
    extra_claims: dict | None = None,
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    if extra_claims:
        to_encode.update(extra_claims)
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: str | Any) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# === MFA / TOTP ===


def generate_mfa_secret() -> str:
    """Generate a new TOTP secret (base32)."""
    return pyotp.random_base32()


def get_totp_uri(secret: str, user_email: str) -> str:
    """Generate the otpauth:// URI for QR code generation."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=user_email, issuer_name=settings.mfa_issuer_name)


def verify_totp(secret: str, token: str) -> bool:
    """Verify a TOTP code against a secret. Window=1 (30s before/after)."""
    if not secret or not token:
        return False
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)


def encrypt_mfa_secret(secret: str, encryption_key: str | None = None) -> str:
    """
    Encrypt the MFA secret before storage.
    Fallback: XOR with a derived key from SECRET_KEY if no encryption_key provided.
    TODO: Replace with proper Fernet encryption in production.
    """
    key = (encryption_key or settings.secret_key)[:32].encode("utf-8")
    secret_bytes = secret.encode("utf-8")
    encrypted = bytes(s ^ key[i % len(key)] for i, s in enumerate(secret_bytes))
    return base64.b64encode(encrypted).decode("ascii")


def decrypt_mfa_secret(encrypted_secret: str, encryption_key: str | None = None) -> str:
    """Decrypt the MFA secret."""
    key = (encryption_key or settings.secret_key)[:32].encode("utf-8")
    encrypted_bytes = base64.b64decode(encrypted_secret.encode("ascii"))
    decrypted = bytes(e ^ key[i % len(key)] for i, e in enumerate(encrypted_bytes))
    return decrypted.decode("utf-8")
