"""Service de notifications in-app.

Cree, liste, et marque comme lues les notifications pour les utilisateurs.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.notification import InAppNotification, NotificationType

logger = logging.getLogger(__name__)


class NotificationService:
    """Service de notifications in-app."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_notification(
        self,
        tenant_id: uuid.UUID,
        recipient_id: uuid.UUID,
        notification_type: NotificationType | str,
        title: str,
        message: str,
        target_type: Optional[str] = None,
        target_id: Optional[uuid.UUID] = None,
        link_url: Optional[str] = None,
    ) -> InAppNotification:
        """Cree une notification in-app."""
        if isinstance(notification_type, NotificationType):
            notification_type = notification_type.value

        notif = InAppNotification(
            tenant_id=tenant_id,
            recipient_id=recipient_id,
            notification_type=notification_type,
            title=title,
            message=message,
            target_type=target_type,
            target_id=target_id,
            link_url=link_url,
        )
        self.db.add(notif)
        await self.db.flush()
        return notif

    async def notify_mention(
        self,
        tenant_id: uuid.UUID,
        recipient_id: uuid.UUID,
        comment_id: uuid.UUID,
        ao_id: uuid.UUID,
        mentioned_by: uuid.UUID,
    ) -> InAppNotification:
        """Notifie un utilisateur qu'il a ete mentionne."""
        return await self.create_notification(
            tenant_id=tenant_id,
            recipient_id=recipient_id,
            notification_type=NotificationType.MENTION,
            title="Nouvelle mention",
            message="Vous avez ete mentionne dans un commentaire.",
            target_type="comment",
            target_id=comment_id,
            link_url=f"/ao/{ao_id}?comment={comment_id}",
        )

    async def notify_reply(
        self,
        tenant_id: uuid.UUID,
        recipient_id: uuid.UUID,
        comment_id: uuid.UUID,
        ao_id: uuid.UUID,
        reply_author_id: uuid.UUID,
    ) -> InAppNotification:
        """Notifie qu'une reponse a ete ajoutee a un commentaire."""
        return await self.create_notification(
            tenant_id=tenant_id,
            recipient_id=recipient_id,
            notification_type=NotificationType.MENTION,
            title="Nouvelle reponse",
            message="Quelqu'un a repondu a votre commentaire.",
            target_type="comment",
            target_id=comment_id,
            link_url=f"/ao/{ao_id}?comment={comment_id}",
        )

    async def notify_approval_required(
        self,
        tenant_id: uuid.UUID,
        recipient_id: uuid.UUID,
        request_id: uuid.UUID,
        step_name: str,
    ) -> InAppNotification:
        """Notifie qu'une approbation est requise."""
        return await self.create_notification(
            tenant_id=tenant_id,
            recipient_id=recipient_id,
            notification_type=NotificationType.APPROVAL_REQUIRED,
            title="Approbation requise",
            message=f"Une demande necessite votre approbation : {step_name}",
            target_type="approval_request",
            target_id=request_id,
            link_url=f"/workflows/requests/{request_id}",
        )

    async def notify_approval_decided(
        self,
        tenant_id: uuid.UUID,
        recipient_id: uuid.UUID,
        request_id: uuid.UUID,
        decision: str,
    ) -> InAppNotification:
        """Notifie le demandeur de la decision."""
        title = "Demande approuvee" if decision == "approved" else "Demande rejetee"
        return await self.create_notification(
            tenant_id=tenant_id,
            recipient_id=recipient_id,
            notification_type=NotificationType.APPROVAL_DECIDED,
            title=title,
            message=f"Votre demande d'approbation a ete {decision}.",
            target_type="approval_request",
            target_id=request_id,
            link_url=f"/workflows/requests/{request_id}",
        )

    async def get_notifications(
        self,
        user_id: uuid.UUID,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[InAppNotification], int]:
        """Liste les notifications d'un utilisateur."""
        conditions = [InAppNotification.recipient_id == user_id]
        if unread_only:
            conditions.append(InAppNotification.is_read == False)

        count_stmt = select(func.count(InAppNotification.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()

        stmt = (
            select(InAppNotification)
            .where(and_(*conditions))
            .order_by(InAppNotification.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        notifications = result.scalars().all()

        return notifications, total

    async def mark_as_read(
        self,
        notification_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Marque une notification comme lue."""
        stmt = select(InAppNotification).where(
            and_(
                InAppNotification.id == notification_id,
                InAppNotification.recipient_id == user_id,
            )
        )
        result = await self.db.execute(stmt)
        notif = result.scalar_one_or_none()

        if not notif:
            return False

        notif.is_read = True
        notif.read_at = datetime.now(timezone.utc)
        await self.db.flush()
        return True

    async def mark_all_as_read(self, user_id: uuid.UUID) -> int:
        """Marque toutes les notifications comme lues."""
        stmt = select(InAppNotification).where(
            and_(
                InAppNotification.recipient_id == user_id,
                InAppNotification.is_read == False,
            )
        )
        result = await self.db.execute(stmt)
        notifs = result.scalars().all()

        now = datetime.now(timezone.utc)
        for notif in notifs:
            notif.is_read = True
            notif.read_at = now

        await self.db.flush()
        return len(notifs)

    async def get_unread_count(self, user_id: uuid.UUID) -> int:
        """Retourne le nombre de notifications non lues."""
        stmt = select(func.count(InAppNotification.id)).where(
            and_(
                InAppNotification.recipient_id == user_id,
                InAppNotification.is_read == False,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0
