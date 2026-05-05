"""Sécurité — JWT + bcrypt + MFA TOTP (sans passlib, bug bcrypt 72 bytes)."""

from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
import pyotp
from jose import jwt, JWTError
from app.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe contre son hash bcrypt."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def get_password_hash(password: str) -> str:
    """Génère un hash bcrypt (limité à 72 bytes, standard bcrypt)."""
    password_bytes = password.encode("utf-8")[:72]
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12))
    return hashed.decode("utf-8")


def create_access_token(
    data: dict = None,
    subject: str = None,
    expires_delta: Optional[timedelta] = None,
    extra_claims: dict = None,
) -> str:
    """Crée un token JWT d'accès. Accepte data dict, subject string, ou les deux."""
    if data is None:
        data = {}
    to_encode = data.copy()
    if subject is not None:
        to_encode.update({"sub": subject})
    if extra_claims:
        to_encode.update(extra_claims)
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    to_encode.setdefault("type", "access")
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def create_refresh_token(data: dict = None, subject: str = None) -> str:
    """Crée un token JWT de rafraîchissement."""
    if data is None:
        data = {}
    to_encode = data.copy()
    if subject is not None:
        to_encode.update({"sub": subject})
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Décode un token JWT (access ou refresh). Retourne None si invalide."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_totp(secret: str, code: str) -> bool:
    """Vérifie un code TOTP (6 chiffres) contre un secret."""
    try:
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)
    except Exception:
        return False


def generate_mfa_secret() -> str:
    """Génère un secret TOTP aléatoire (base32)."""
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str, issuer: str = "TAKA OS") -> str:
    """Génère l'URI otpauth pour le QR code."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=issuer)


def encrypt_mfa_secret(secret: str) -> str:
    """Chiffre le secret MFA. En v0.1 : stockage plain (pas de chiffrement)."""
    # TODO(v0.3) : Implémenter le chiffrement avec Vault
    return secret


def decrypt_mfa_secret(encrypted_secret: str) -> str:
    """Déchiffre le secret MFA. En v0.1 : stockage plain (pas de chiffrement)."""
    return encrypted_secret


def generate_backup_code() -> str:
    """Génère un code de secours MFA (8 caractères hex)."""
    import secrets
    return secrets.token_hex(4).upper()


def hash_backup_code(code: str) -> str:
    """Hash un code de secours avec SHA-256."""
    import hashlib
    return hashlib.sha256(code.encode()).hexdigest()


def verify_backup_code(stored_codes: list[str] | None, code: str) -> tuple[bool, list[str] | None]:
    """Verifie un backup code contre une liste de codes hashes.
    Retourne (ok, remaining_codes) ou (False, stored_codes).
    """
    if not stored_codes:
        return False, stored_codes
    code_hash = hash_backup_code(code)
    if code_hash in stored_codes:
        remaining = [c for c in stored_codes if c != code_hash]
        return True, remaining if remaining else None
    return False, stored_codes
