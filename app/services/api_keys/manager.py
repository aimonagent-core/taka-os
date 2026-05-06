"""Gestion des cles API publiques (externes).

Generation, revocation, verification des cles API pour les integrations
Enterprise. Les cles sont prefixees (tak_live_xxx) et stockees en hash.
"""

import hashlib
import secrets
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.api_publique import ExternalApiKey

logger = logging.getLogger(__name__)

LIVE_PREFIX = "tak_live_"
TEST_PREFIX = "tak_test_"
KEY_LENGTH = 48


class ExternalApiKeyManager:
    """Manager pour les cles API publiques."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_key(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        name: str,
        permissions: list[str],
        is_test: bool = False,
        rate_limit: int = 100,
        expires_days: Optional[int] = None,
    ) -> tuple[str, ExternalApiKey]:
        """Genere une nouvelle cle API.

        Returns:
            (cle_en_clair, objet_db)
        """
        prefix = TEST_PREFIX if is_test else LIVE_PREFIX
        secret = secrets.token_urlsafe(KEY_LENGTH)
        full_key = f"{prefix}{secret}"

        key_hash = hashlib.sha256(full_key.encode()).hexdigest()
        key_prefix = prefix[:-1]  # 'tak_live' ou 'tak_test'

        expires_at = None
        if expires_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days)

        api_key = ExternalApiKey(
            tenant_id=tenant_id,
            created_by_user_id=user_id,
            key_prefix=key_prefix,
            key_hash=key_hash,
            key_name=name,
            permissions=permissions,
            rate_limit_per_minute=rate_limit,
            expires_at=expires_at,
        )
        self.db.add(api_key)
        await self.db.flush()

        logger.info(f"API key creee pour tenant {tenant_id} : {name}")
        return full_key, api_key

    async def verify_key(self, api_key: str) -> Optional[ExternalApiKey]:
        """Verifie une cle API et retourne l'objet si valide."""
        if not api_key or len(api_key) < 20:
            return None

        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        stmt = select(ExternalApiKey).where(
            and_(
                ExternalApiKey.key_hash == key_hash,
                ExternalApiKey.is_active == True,
            )
        )
        result = await self.db.execute(stmt)
        key_obj = result.scalar_one_or_none()

        if not key_obj:
            return None

        if key_obj.expires_at and datetime.now(timezone.utc) > key_obj.expires_at:
            return None

        key_obj.last_used_at = datetime.now(timezone.utc)
        key_obj.total_requests += 1
        await self.db.flush()

        return key_obj

    async def list_keys(
        self,
        tenant_id: uuid.UUID,
    ) -> list[ExternalApiKey]:
        """Liste les cles API d'un tenant (sans les secrets)."""
        stmt = select(ExternalApiKey).where(
            ExternalApiKey.tenant_id == tenant_id
        ).order_by(ExternalApiKey.created_at.desc())

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def revoke_key(
        self,
        key_id: uuid.UUID,
        tenant_id: uuid.UUID,
    ) -> bool:
        """Revoke une cle API."""
        stmt = select(ExternalApiKey).where(
            and_(
                ExternalApiKey.id == key_id,
                ExternalApiKey.tenant_id == tenant_id,
            )
        )
        result = await self.db.execute(stmt)
        key_obj = result.scalar_one_or_none()

        if not key_obj:
            return False

        key_obj.is_active = False
        await self.db.flush()
        logger.info(f"API key revoquee : {key_id}")
        return True

    async def rotate_key(
        self,
        key_id: uuid.UUID,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[str]:
        """Rotoie une cle API (genere une nouvelle, revoque l'ancienne)."""
        stmt = select(ExternalApiKey).where(
            and_(
                ExternalApiKey.id == key_id,
                ExternalApiKey.tenant_id == tenant_id,
            )
        )
        result = await self.db.execute(stmt)
        old_key = result.scalar_one_or_none()

        if not old_key:
            return None

        old_key.is_active = False

        is_test = old_key.key_prefix == "tak_test"
        new_key, _ = await self.create_key(
            tenant_id=tenant_id,
            user_id=user_id,
            name=f"{old_key.key_name} (rotated)",
            permissions=old_key.permissions,
            is_test=is_test,
            rate_limit=old_key.rate_limit_per_minute,
        )

        await self.db.flush()
        return new_key
