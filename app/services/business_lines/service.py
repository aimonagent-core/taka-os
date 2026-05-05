"""Service Business Lines — CRUD, matching CPV, gestion des membres."""
import logging
from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ao_s2 import AO
from app.models.business_line import BLCPVKeyword, BLMember, BusinessLine

logger = logging.getLogger(__name__)


class BusinessLineService:
    """Service de gestion des lignes metiers."""

    @staticmethod
    async def create_bl(
        db: AsyncSession,
        tenant_id: str,
        name: str,
        description: Optional[str] = None,
        color: str = "#3B82F6",
        default_profile: str = "prudent",
        cpv_keywords: list[str] = None,
        free_text_keywords: list[str] = None,
    ) -> BusinessLine:
        bl = BusinessLine(
            tenant_id=tenant_id,
            name=name,
            description=description,
            color=color,
            default_profile=default_profile,
            cpv_keywords=cpv_keywords or [],
            free_text_keywords=free_text_keywords or [],
        )
        db.add(bl)
        await db.commit()
        await db.refresh(bl)
        logger.info("[BL] Cree: %s (tenant=%s)", name, tenant_id)
        return bl

    @staticmethod
    async def get_bl_for_tenant(db: AsyncSession, tenant_id: str) -> list[BusinessLine]:
        stmt = select(BusinessLine).where(
            and_(BusinessLine.tenant_id == tenant_id, BusinessLine.is_active.is_(True))
        )
        rows = await db.execute(stmt)
        return list(rows.scalars().all())

    @staticmethod
    async def assign_user_to_bl(
        db: AsyncSession,
        business_line_id: str,
        user_id: str,
        role: str = "member",
        is_primary: bool = False,
    ) -> BLMember:
        if is_primary:
            stmt = select(BLMember).where(
                and_(BLMember.user_id == user_id, BLMember.is_primary.is_(True))
            )
            rows = await db.execute(stmt)
            old_primary = rows.scalar_one_or_none()
            if old_primary:
                old_primary.is_primary = False

        member = BLMember(
            business_line_id=business_line_id,
            user_id=user_id,
            role=role,
            is_primary=is_primary,
        )
        db.add(member)
        await db.commit()
        await db.refresh(member)
        return member

    @staticmethod
    async def match_ao_to_bl(
        db: AsyncSession, ao: AO, tenant_id: str
    ) -> Optional[BusinessLine]:
        bls = await BusinessLineService.get_bl_for_tenant(db, tenant_id)
        if not bls:
            return None

        best_bl = None
        best_score = 0.0

        ao_cpv = set(ao.cpv_codes or [])
        title_lower = (ao.title or "").lower()
        desc_lower = (ao.description or "").lower()

        for bl in bls:
            score = 0.0
            bl_cpv = set(bl.cpv_keywords or [])

            if bl_cpv and ao_cpv:
                intersection = bl_cpv & ao_cpv
                if intersection:
                    score += len(intersection) * 2.0

            for kw in bl.free_text_keywords or []:
                kw_lower = kw.lower()
                if kw_lower in title_lower:
                    score += 1.5
                if kw_lower in desc_lower:
                    score += 0.5

            if score > best_score:
                best_score = score
                best_bl = bl

        if best_bl and best_score >= 1.0:
            logger.info("[BL] AO %s → BL %s (score=%.1f)", ao.id, best_bl.name, best_score)
            return best_bl
        return None

    @staticmethod
    async def get_user_bl_scope(db: AsyncSession, user_id: str) -> dict:
        stmt = select(BLMember).where(BLMember.user_id == user_id)
        rows = await db.execute(stmt)
        members = rows.scalars().all()

        scope = {
            "primary_bl_id": None,
            "bl_ids": [],
            "roles": {},
        }
        for m in members:
            scope["bl_ids"].append(str(m.business_line_id))
            scope["roles"][str(m.business_line_id)] = m.role
            if m.is_primary:
                scope["primary_bl_id"] = str(m.business_line_id)

        return scope
