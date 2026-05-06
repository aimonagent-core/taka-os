"""Service Sprint 11 — Algorithme de matching score entre un AO et le profil tenant."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ao_s2 import AO
from app.models.ao import Tenant
from app.models.tenant_profile import TenantCPVPreference

logger = logging.getLogger(__name__)

# Mapping domaine d'activite vers mots-cles de recherche dans le titre
DOMAINE_KEYWORDS: dict[str, list[str]] = {
    "btp": ["btp", "batiment", "construction", "travaux"],
    "travaux publics": ["travaux publics", "voirie", "reseaux", "assainissement"],
    "electricite": ["electricite", "electrique", "courant fort", "courant faible"],
    "plomberie": ["plomberie", "sanitaire", "chauffage", "climatisation"],
    "menuiserie": ["menuiserie", "bois", "pvc", "aluminium", "fenetre", "porte"],
    "maconnerie": ["maconnerie", "gros oeuvre", "beton", "mortier"],
    "peinture": ["peinture", "revetement", "enduit", "facade"],
    "etancheite": ["etancheite", "etanch", "impermeabilisation"],
}


def _normalize(text: str) -> str:
    return text.lower().strip()


def _days_until(date: Optional[datetime]) -> Optional[int]:
    if date is None:
        return None
    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)
    delta = date - datetime.now(timezone.utc)
    return max(0, int(delta.total_seconds() / 86400))


class MatchingService:
    """Calcule le score de correspondance entre un AO et le profil d'un tenant."""

    @staticmethod
    async def compute_score(
        db: AsyncSession,
        ao: AO,
        tenant: Tenant,
    ) -> dict:
        """Retourne un dict avec total_score (0-100) et le detail."""

        # Charger les preferences CPV du tenant
        stmt_cpv = select(TenantCPVPreference).where(
            TenantCPVPreference.tenant_id == tenant.id
        )
        rows = await db.execute(stmt_cpv)
        tenant_cpvs = [r.cpv_code for r in rows.scalars().all()]

        score_breakdown = {}
        total = 0.0

        # 1. CPV match — 30 pts max
        cpv_matched = []
        if ao.cpv_codes and tenant_cpvs:
            ao_cpv_set = {_normalize(c) for c in ao.cpv_codes}
            tenant_cpv_set = {_normalize(c) for c in tenant_cpvs}
            cpv_matched = list(ao_cpv_set & tenant_cpv_set)
        cpv_score = 30.0 if cpv_matched else 0.0
        score_breakdown["cpv"] = {"points": cpv_score, "matched": cpv_matched}
        total += cpv_score

        # 2. Departement match — 25 pts
        dept_matched = False
        if ao.department_code and tenant.zones_geo:
            tenant_zones = {_normalize(z) for z in tenant.zones_geo}
            if _normalize(ao.department_code) in tenant_zones:
                dept_matched = True
        dept_score = 25.0 if dept_matched else 0.0
        score_breakdown["department"] = {"points": dept_score, "matched": dept_matched}
        total += dept_score

        # 3. Type de marche match — 20 pts
        type_matched = False
        if ao.notice_type and tenant.types_marche_acceptes:
            ao_type_norm = _normalize(ao.notice_type)
            accepted = {_normalize(t) for t in tenant.types_marche_acceptes}
            if ao_type_norm in accepted:
                type_matched = True
        type_score = 20.0 if type_matched else 0.0
        score_breakdown["type_marche"] = {"points": type_score, "matched": type_matched}
        total += type_score

        # 4. Deadline proche — 15 pts si < 14 jours
        deadline_bonus = False
        days = _days_until(ao.deadline_date)
        if days is not None and days <= 14:
            deadline_bonus = True
        deadline_score = 15.0 if deadline_bonus else 0.0
        score_breakdown["deadline"] = {"points": deadline_score, "days_until": days, "matched": deadline_bonus}
        total += deadline_score

        # 5. Mots-cles domaine dans titre — 10 pts max
        keyword_matches = []
        if ao.title and tenant.domaine_activite:
            title_norm = _normalize(ao.title)
            for domaine in tenant.domaine_activite:
                keywords = DOMAINE_KEYWORDS.get(_normalize(domaine), [_normalize(domaine)])
                for kw in keywords:
                    if kw in title_norm:
                        keyword_matches.append(kw)
                        break
        keyword_score = 10.0 if keyword_matches else 0.0
        score_breakdown["keywords"] = {"points": keyword_score, "matched": list(set(keyword_matches))}
        total += keyword_score

        total = round(min(100.0, total), 1)

        return {
            "total_score": total,
            "breakdown": score_breakdown,
            "matched_cpv": cpv_matched,
            "matched_department": dept_matched,
            "matched_type_marche": type_matched,
            "deadline_bonus": deadline_bonus,
            "keyword_matches": list(set(keyword_matches)),
        }

    @staticmethod
    async def get_recent_ao_with_scores(
        db: AsyncSession,
        tenant: Tenant,
        limit: int = 5,
    ) -> list[dict]:
        """Retourne les N derniers AO avec leur score de matching."""
        stmt = (
            select(AO)
            .where(AO.status == "detected")
            .order_by(AO.created_at.desc())
            .limit(limit * 3)
        )
        rows = await db.execute(stmt)
        aos = rows.scalars().all()

        results = []
        for ao in aos:
            score_data = await MatchingService.compute_score(db, ao, tenant)
            results.append({
                "ao": ao,
                "score": score_data["total_score"],
                "details": score_data,
            })

        # Trier par score decroissant et limiter
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
