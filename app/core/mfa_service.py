# File: app/core/mfa_service.py
# Purpose: MFA/TOTP service with Fernet encryption and backup codes
# Dependencies: pyotp, cryptography.fernet, passlib.hash.bcrypt, secrets, base64

import base64
import secrets
from typing import Tuple

import pyotp
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from passlib.hash import bcrypt

from app.config import settings


class MFAService:
    BACKUP_CODE_COUNT: int = 10
    BACKUP_CODE_LENGTH: int = 8
    TOTP_DIGITS: int = 6
    TOTP_INTERVAL: int = 30
    TOTP_WINDOW: int = 1

    def __init__(self, master_secret: str | None = None) -> None:
        self._fernet = self._derive_fernet(master_secret or settings.secret_key)

    def _derive_fernet(self, master_secret: str) -> Fernet:
        salt = b"app_mfa_salt_v1_2024"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_secret.encode()))
        return Fernet(key)

    def generate_secret(
        self, user_email: str, issuer: str = "TAKA OS"
    ) -> Tuple[str, str, list[str]]:
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret, digits=self.TOTP_DIGITS, interval=self.TOTP_INTERVAL)
        provisioning_uri = totp.provisioning_uri(name=user_email, issuer_name=issuer)
        backup_codes = self.generate_backup_codes()
        return secret, provisioning_uri, backup_codes

    def encrypt_secret(self, plain_secret: str) -> str:
        return self._fernet.encrypt(plain_secret.encode()).decode()

    def decrypt_secret(self, encrypted_secret: str) -> str:
        return self._fernet.decrypt(encrypted_secret.encode()).decode()

    def verify_totp(self, encrypted_secret: str, otp_code: str) -> bool:
        try:
            secret = self.decrypt_secret(encrypted_secret)
        except Exception:
            return False
        totp = pyotp.TOTP(secret, digits=self.TOTP_DIGITS, interval=self.TOTP_INTERVAL)
        return totp.verify(otp_code, valid_window=self.TOTP_WINDOW)

    def verify_backup_code(
        self, hashed_codes: list[str], code_input: str
    ) -> Tuple[bool, list[str] | None]:
        for idx, hashed in enumerate(hashed_codes):
            if bcrypt.verify(code_input, hashed):
                remaining = hashed_codes[:idx] + hashed_codes[idx + 1:]
                return True, remaining
        return False, None

    def hash_backup_codes(self, codes: list[str]) -> list[str]:
        return [bcrypt.hash(code) for code in codes]

    def generate_backup_codes(self, count: int = BACKUP_CODE_COUNT) -> list[str]:
        return [secrets.token_urlsafe(self.BACKUP_CODE_LENGTH) for _ in range(count)]
