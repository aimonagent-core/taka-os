"""Service Sprint 12 Module 2 — Matching tenant-AO pour notifications auto."""

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ao import Tenant
from app.models.ao_s2 import AO
from app.services.matching import MatchingService

logger = logging.getLogger(__name__)

# Seuil minimum de pertinence pour notifier un tenant
MATCHING_THRESHOLD = 30.0


async def find_matching_tenants(
    ao_id: uuid.UUID,
    session: AsyncSession,
) -> list[tuple[uuid.UUID, float]]:
    """Trouve tous les tenants dont le profil correspond a un AO.

    Args:
        ao_id: ID de l'AO a matcher.
        session: Session SQLAlchemy async.

    Returns:
        Liste de tuples (tenant_id, score) pour les scores >= seuil.
    """
    # 1. Charger l'AO
    stmt_ao = select(AO).where(AO.id == ao_id)
    row = await session.execute(stmt_ao)
    ao = row.scalar_one_or_none()
    if not ao:
        logger.warning("[TenantMatcher] AO %s introuvable", ao_id)
        return []

    # 2. Charger tous les tenants actifs ayant complete l'onboarding
    stmt_tenants = select(Tenant).where(
        Tenant.onboarding_completed.is_(True),
        Tenant.is_active.is_(True),
    )
    rows = await session.execute(stmt_tenants)
    tenants = rows.scalars().all()

    if not tenants:
        logger.debug("[TenantMatcher] Aucun tenant eligible")
        return []

    # 3. Calculer le score pour chaque tenant
    matches: list[tuple[uuid.UUID, float]] = []
    for tenant in tenants:
        try:
            score_data = await MatchingService.compute_score(session, ao, tenant)
            score = score_data["total_score"]
            if score >= MATCHING_THRESHOLD:
                matches.append((tenant.id, score))
                logger.debug(
                    "[TenantMatcher] Match trouve — tenant=%s ao=%s score=%s",
                    tenant.id,
                    ao_id,
                    score,
                )
        except Exception:
            logger.exception("[TenantMatcher] Erreur scoring tenant=%s", tenant.id)
            continue

    logger.info(
        "[TenantMatcher] AO %s — %s match(s) sur %s tenant(s)",
        ao_id,
        len(matches),
        len(tenants),
    )
    return matches
