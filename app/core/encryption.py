"""Service de chiffrement Fernet (AES-128) pour les donnees sensibles."""

import base64
import logging
import os

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)

_fernet_instance: Fernet | None = None


def _get_fernet_key_from_password(password: str, salt: bytes | None = None) -> tuple[bytes, bytes]:
    """Derive une cle Fernet 32-bytes a partir d'un mot de passe."""
    if salt is None:
        salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt


def init_encryption() -> Fernet:
    """Initialise l'instance Fernet singleton."""
    global _fernet_instance
    if _fernet_instance is not None:
        return _fernet_instance

    from app.config import settings

    raw_key = None

    if hasattr(settings, "fernet_key") and settings.fernet_key:
        raw_key = settings.fernet_key
        logger.info("Fernet: cle chargee depuis FERNET_KEY")

    key_file = "/app/data/.fernet_key"
    if raw_key is None and os.path.exists(key_file):
        with open(key_file, "rb") as f:
            raw_key = f.read().decode()
        logger.info("Fernet: cle chargee depuis fichier")

    if raw_key is None:
        raw_key = Fernet.generate_key().decode()
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        with open(key_file, "wb") as f:
            f.write(raw_key.encode())
        os.chmod(key_file, 0o600)
        logger.warning(
            "Fernet: nouvelle cle generee et sauvegardee dans %s — "
            "STOCKEZ CETTE CLE DANS UN VAULT SECURISE ET DEFINISSEZ FERNET_KEY dans .env",
            key_file,
        )

    _fernet_instance = Fernet(raw_key.encode())
    return _fernet_instance


def encrypt_value(plaintext: str | None) -> str | None:
    """Chiffre une valeur string avec Fernet."""
    if plaintext is None:
        return None
    f = init_encryption()
    return f.encrypt(plaintext.encode()).decode()


def decrypt_value(ciphertext: str | None) -> str | None:
    """Dechiffre une valeur Fernet."""
    if ciphertext is None:
        return None
    f = init_encryption()
    try:
        return f.decrypt(ciphertext.encode()).decode()
    except InvalidToken:
        logger.error("Fernet: tentative de dechiffrement avec cle invalide ou donnees corrompues")
        raise ValueError("Donnees chiffrees invalides — cle incorrecte ou donnees corrompues")


def encrypt_dict_values(data: dict, fields: list[str]) -> dict:
    """Chiffre selectivement certains champs d'un dict."""
    result = dict(data)
    for field in fields:
        if field in result and result[field] is not None:
            result[field] = encrypt_value(str(result[field]))
    return result


def decrypt_dict_values(data: dict, fields: list[str]) -> dict:
    """Dechiffre selectivement certains champs d'un dict."""
    result = dict(data)
    for field in fields:
        if field in result and result[field] is not None:
            result[field] = decrypt_value(result[field])
    return result
