"""Routes pour les notifications in-app.

Routes :
  GET  /notifications              → Liste des notifications
  GET  /notifications/unread-count → Nombre de non-lues
  POST /notifications/{id}/read    → Marquer comme lue
  POST /notifications/read-all     → Tout marquer comme lu
"""

import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.ao import User
from app.services.notifications.in_app import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
async def list_notifications(
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Liste les notifications de l'utilisateur."""
    service = NotificationService(db)
    notifs, total = await service.get_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )

    return {
        "items": [
            {
                "id": str(n.id),
                "type": n.notification_type,
                "title": n.title,
                "message": n.message,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat() if n.created_at else None,
                "link_url": n.link_url,
            }
            for n in notifs
        ],
        "total": total,
        "unread_count": await service.get_unread_count(current_user.id),
    }


@router.get("/unread-count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Nombre de notifications non lues."""
    service = NotificationService(db)
    count = await service.get_unread_count(current_user.id)
    return {"unread_count": count}


@router.post("/{notif_id}/read")
async def mark_read(
    notif_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Marque une notification comme lue."""
    service = NotificationService(db)
    ok = await service.mark_as_read(notif_id, current_user.id)
    return {"read": ok}


@router.post("/read-all")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Marque toutes les notifications comme lues."""
    service = NotificationService(db)
    count = await service.mark_all_as_read(current_user.id)
    return {"marked_read": count}
