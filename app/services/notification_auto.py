"""Service Sprint 12 Module 2 — Notifications automatiques (scraper → tenant)."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ao import Tenant, User, UserRole
from app.models.ao_s2 import AO
from app.models.notification import InAppNotification, NotificationType
from app.services.tenant_matcher import find_matching_tenants

logger = logging.getLogger(__name__)


class NotificationAutoService:
    """Cree des notifications automatiques pour les tenants quand un nouvel AO match."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def notify_tenants_for_new_ao(self, ao_id: uuid.UUID) -> int:
        """Notifie tous les tenants dont le profil correspond au nouvel AO.

        Args:
            ao_id: ID de l'AO nouvellement insere.

        Returns:
            Nombre de notifications creees.
        """
        matches = await find_matching_tenants(ao_id, self.db)
        if not matches:
            return 0

        # Charger l'AO pour le titre
        stmt_ao = select(AO).where(AO.id == ao_id)
        row = await self.db.execute(stmt_ao)
        ao = row.scalar_one_or_none()
        if not ao:
            return 0

        created_count = 0
        for tenant_id, score in matches:
            try:
                # Recuperer les users actifs du tenant
                stmt_users = select(User).where(
                    User.tenant_id == tenant_id,
                    User.is_active.is_(True),
                    User.deleted_at.is_(None),
                )
                rows_users = await self.db.execute(stmt_users)
                users = rows_users.scalars().all()

                if not users:
                    continue

                title = f"Nouvel AO correspondant : {ao.title[:50]}{'...' if len(ao.title) > 50 else ''}"
                message = f"Score de correspondance : {score:.0f}% — {ao.buyer_name or 'Acheteur non specifie'}"
                link = f"/ao/{ao.id}"

                for user in users:
                    notif = InAppNotification(
                        tenant_id=tenant_id,
                        recipient_id=user.id,
                        notification_type=NotificationType.NEW_AO.value,
                        title=title,
                        message=message,
                        target_type="ao",
                        target_id=ao.id,
                        link_url=link,
                    )
                    self.db.add(notif)
                    created_count += 1

            except Exception:
                logger.exception(
                    "[NotificationAuto] Erreur creation notif tenant=%s ao=%s",
                    tenant_id,
                    ao_id,
                )
                continue

        if created_count:
            await self.db.flush()
            logger.info(
                "[NotificationAuto] %s notification(s) creee(s) pour AO %s",
                created_count,
                ao_id,
            )

        return created_count

    async def notify_deadline_warnings(self) -> int:
        """Notifie les tenants des AO avec deadline dans les 7 jours.

        Returns:
            Nombre de notifications creees.
        """
        now = datetime.now(timezone.utc)
        imminent = now + timedelta(days=7)

        # AO avec deadline proche et pas encore notifiees
        stmt = select(AO).where(
            AO.deadline_date.isnot(None),
            AO.deadline_date <= imminent,
            AO.deadline_date >= now,
            AO.deadline_notified.is_(False),
            AO.status == "detected",
        )
        rows = await self.db.execute(stmt)
        aos = rows.scalars().all()

        if not aos:
            logger.debug("[NotificationAuto] Aucune deadline imminente")
            return 0

        created_count = 0
        for ao in aos:
            try:
                matches = await find_matching_tenants(ao.id, self.db)
                if not matches:
                    continue

                days_left = max(0, int((ao.deadline_date - now).total_seconds() / 86400))
                title = f"Deadline imminente : {ao.title[:50]}{'...' if len(ao.title) > 50 else ''}"
                message = f"Il reste {days_left} jour(s) pour repondre — {ao.buyer_name or 'Acheteur non specifie'}"
                link = f"/ao/{ao.id}"

                for tenant_id, score in matches:
                    stmt_users = select(User).where(
                        User.tenant_id == tenant_id,
                        User.is_active.is_(True),
                        User.deleted_at.is_(None),
                    )
                    rows_users = await self.db.execute(stmt_users)
                    users = rows_users.scalars().all()

                    for user in users:
                        notif = InAppNotification(
                            tenant_id=tenant_id,
                            recipient_id=user.id,
                            notification_type=NotificationType.DEADLINE_WARNING.value,
                            title=title,
                            message=message,
                            target_type="ao",
                            target_id=ao.id,
                            link_url=link,
                        )
                        self.db.add(notif)
                        created_count += 1

                # Marquer l'AO comme notifiee pour eviter les doublons
                ao.deadline_notified = True

            except Exception:
                logger.exception(
                    "[NotificationAuto] Erreur deadline notif ao=%s",
                    ao.id,
                )
                continue

        if created_count:
            await self.db.flush()
            logger.info(
                "[NotificationAuto] %s deadline notification(s) creee(s)",
                created_count,
            )

        return created_count
