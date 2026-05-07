"""Factory de connecteurs de depot generiques (Sprint 12 Module 3)."""

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.platform_connector import PlatformConnector
from app.services.deposant.connectors.base_connector import BasePlatformConnector
from app.services.deposant.connectors.mock_connector import MockConnector
from app.services.deposant.connectors.email_connector import EmailDirectConnector
from app.services.deposant.connectors.api_connector import GenericAPIConnector

logger = logging.getLogger(__name__)

# Mapping type -> classe connecteur
_CONNECTOR_MAP: dict[str, type[BasePlatformConnector]] = {
    "email_direct": EmailDirectConnector,
    "custom_api": GenericAPIConnector,
    "marches_publics": GenericAPIConnector,
    "mpst": GenericAPIConnector,
    "marcoweb": GenericAPIConnector,
    "actradis": GenericAPIConnector,
    "atexio": GenericAPIConnector,
}


async def get_connector(
    tenant_id: uuid.UUID,
    platform_type: str,
    session: AsyncSession,
) -> BasePlatformConnector:
    """Recupere un connecteur actif pour un tenant et un type de plateforme.

    Args:
        tenant_id: UUID du tenant.
        platform_type: Type de plateforme (email_direct, custom_api, mpst, etc.).
        session: Session SQLAlchemy async.

    Returns:
        Instance d'un BasePlatformConnector concret, ou MockConnector si aucun
        connecteur actif n'est configure.
    """
    stmt = select(PlatformConnector).where(
        PlatformConnector.tenant_id == tenant_id,
        PlatformConnector.platform_type == platform_type,
        PlatformConnector.is_active.is_(True),
    )
    result = await session.execute(stmt)
    pc = result.scalar_one_or_none()

    if not pc:
        logger.info(
            "[ConnectorFactory] Aucun connecteur %s actif pour tenant %s — fallback mock",
            platform_type,
            tenant_id,
        )
        return MockConnector(config={})

    connector_class = _CONNECTOR_MAP.get(platform_type, GenericAPIConnector)
    logger.info(
        "[ConnectorFactory] Connecteur %s (%s) pour tenant %s",
        platform_type,
        connector_class.__name__,
        tenant_id,
    )
    return connector_class(pc.config)


def list_supported_platforms() -> list[dict]:
    """Liste les types de plateformes supportes."""
    return [
        {"type": key, "name": key.replace("_", " ").title()}
        for key in _CONNECTOR_MAP.keys()
    ]
