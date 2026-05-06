"""Moteur d'audit trail — ecriture et lecture des AuditTrail."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.audit import AuditTrail, AuditAction

logger = logging.getLogger(__name__)


class AuditEngine:
    """Moteur d'audit trail pour TAKA OS."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_action(
        self,
        tenant_id: uuid.UUID,
        actor_type: str,
        actor_id: Optional[uuid.UUID],
        actor_email: Optional[str],
        action: str | AuditAction,
        action_category: str,
        target_type: str,
        target_id: Optional[uuid.UUID],
        target_display: Optional[str] = None,
        before_state: Optional[dict] = None,
        after_state: Optional[dict] = None,
        change_summary: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        severity: str = "info",
        event_metadata: Optional[dict] = None,
    ) -> Optional[AuditTrail]:
        """Cree une entree d'audit trail."""
        try:
            if isinstance(action, AuditAction):
                action = action.value

            log = AuditTrail(
                tenant_id=tenant_id,
                actor_type=actor_type,
                actor_id=actor_id,
                actor_email=actor_email,
                action=action,
                action_category=action_category,
                target_type=target_type,
                target_id=target_id,
                target_display=target_display,
                before_state=before_state,
                after_state=after_state,
                change_summary=change_summary,
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id,
                severity=severity,
                event_metadata=event_metadata,
            )
            self.db.add(log)
            await self.db.flush()

            logger.debug(f"Audit: {action} sur {target_type}:{target_id} par {actor_type}:{actor_id}")
            return log

        except Exception as e:
            logger.error(f"Audit: ERREUR CRITIQUE log_action — {e} | action={action} target={target_type}:{target_id}")
            return None

    async def log_user_action(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        user_email: str,
        action: str | AuditAction,
        action_category: str,
        target_type: str,
        target_id: Optional[uuid.UUID] = None,
        target_display: Optional[str] = None,
        after_state: Optional[dict] = None,
        change_summary: Optional[str] = None,
        ip_address: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Optional[AuditTrail]:
        """Shortcut pour logger une action utilisateur."""
        return await self.log_action(
            tenant_id=tenant_id,
            actor_type="user",
            actor_id=user_id,
            actor_email=user_email,
            action=action,
            action_category=action_category,
            target_type=target_type,
            target_id=target_id,
            target_display=target_display,
            after_state=after_state,
            change_summary=change_summary,
            ip_address=ip_address,
            request_id=request_id,
        )

    async def log_system_action(
        self,
        tenant_id: uuid.UUID,
        action: str | AuditAction,
        action_category: str,
        target_type: str,
        target_id: Optional[uuid.UUID] = None,
        target_display: Optional[str] = None,
        after_state: Optional[dict] = None,
        change_summary: Optional[str] = None,
        severity: str = "info",
    ) -> Optional[AuditTrail]:
        """Shortcut pour logger une action systeme."""
        return await self.log_action(
            tenant_id=tenant_id,
            actor_type="system",
            actor_id=None,
            actor_email=None,
            action=action,
            action_category=action_category,
            target_type=target_type,
            target_id=target_id,
            target_display=target_display,
            after_state=after_state,
            change_summary=change_summary,
            severity=severity,
        )

    async def get_logs_for_target(
        self,
        tenant_id: uuid.UUID,
        target_type: str,
        target_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditTrail]:
        """Recupere l'historique d'audit pour une cible specifique."""
        stmt = (
            select(AuditTrail)
            .where(
                and_(
                    AuditTrail.tenant_id == tenant_id,
                    AuditTrail.target_type == target_type,
                    AuditTrail.target_id == target_id,
                )
            )
            .order_by(AuditTrail.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_logs_for_user(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditTrail]:
        """Recupere l'historique des actions d'un utilisateur."""
        stmt = (
            select(AuditTrail)
            .where(
                and_(
                    AuditTrail.tenant_id == tenant_id,
                    AuditTrail.actor_type == "user",
                    AuditTrail.actor_id == user_id,
                )
            )
            .order_by(AuditTrail.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def search_logs(
        self,
        tenant_id: uuid.UUID,
        action_category: Optional[str] = None,
        action: Optional[str] = None,
        actor_type: Optional[str] = None,
        severity: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[AuditTrail], int]:
        """Recherche avancee dans les logs d'audit."""
        conditions = [AuditTrail.tenant_id == tenant_id]

        if action_category:
            conditions.append(AuditTrail.action_category == action_category)
        if action:
            conditions.append(AuditTrail.action == action)
        if actor_type:
            conditions.append(AuditTrail.actor_type == actor_type)
        if severity:
            conditions.append(AuditTrail.severity == severity)
        if date_from:
            conditions.append(AuditTrail.created_at >= date_from)
        if date_to:
            conditions.append(AuditTrail.created_at <= date_to)

        count_stmt = select(func.count(AuditTrail.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()

        stmt = (
            select(AuditTrail)
            .where(and_(*conditions))
            .order_by(AuditTrail.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        logs = result.scalars().all()

        return logs, total

    async def get_activity_stats(
        self,
        tenant_id: uuid.UUID,
        days: int = 30,
    ) -> dict:
        """Statistiques d'activite pour le dashboard."""
        from_date = datetime.now(timezone.utc) - timedelta(days=days)

        total_stmt = select(func.count(AuditTrail.id)).where(
            and_(AuditTrail.tenant_id == tenant_id, AuditTrail.created_at >= from_date)
        )
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar()

        cat_stmt = (
            select(AuditTrail.action_category, func.count(AuditTrail.id))
            .where(and_(AuditTrail.tenant_id == tenant_id, AuditTrail.created_at >= from_date))
            .group_by(AuditTrail.action_category)
        )
        cat_result = await self.db.execute(cat_stmt)
        by_category = {row[0]: row[1] for row in cat_result.all()}

        sev_stmt = (
            select(AuditTrail.severity, func.count(AuditTrail.id))
            .where(and_(AuditTrail.tenant_id == tenant_id, AuditTrail.created_at >= from_date))
            .group_by(AuditTrail.severity)
        )
        sev_result = await self.db.execute(sev_stmt)
        by_severity = {row[0]: row[1] for row in sev_result.all()}

        users_stmt = select(func.count(func.distinct(AuditTrail.actor_id))).where(
            and_(
                AuditTrail.tenant_id == tenant_id,
                AuditTrail.created_at >= from_date,
                AuditTrail.actor_type == "user",
            )
        )
        users_result = await self.db.execute(users_stmt)
        unique_users = users_result.scalar()

        trend_stmt = (
            select(
                func.date_trunc("day", AuditTrail.created_at).label("day"),
                func.count(AuditTrail.id),
            )
            .where(and_(AuditTrail.tenant_id == tenant_id, AuditTrail.created_at >= from_date))
            .group_by(func.date_trunc("day", AuditTrail.created_at))
            .order_by(func.date_trunc("day", AuditTrail.created_at))
        )
        trend_result = await self.db.execute(trend_stmt)
        trend = [
            {"date": row[0].strftime("%Y-%m-%d"), "count": row[1]}
            for row in trend_result.all() if row[0]
        ]

        return {
            "total_actions": total,
            "by_category": by_category,
            "by_severity": by_severity,
            "unique_users": unique_users,
            "trend": trend,
        }
