"""Service de gestion des commentaires sur les AO.

CRUD commentaires, extraction des mentions @utilisateur, notifications.
"""

import re
import logging
from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.comment import Comment, CommentMention, CommentStatus
from app.models.ao import User
from app.services.notifications.in_app import NotificationService

logger = logging.getLogger(__name__)

MENTION_PATTERN = re.compile(r"@([a-zA-Z0-9._-]+)")


class CommentService:
    """Service de gestion des commentaires."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.notif_service = NotificationService(db)

    async def create_comment(
        self,
        tenant_id: uuid.UUID,
        ao_id: uuid.UUID,
        author_id: uuid.UUID,
        content: str,
        parent_id: Optional[uuid.UUID] = None,
    ) -> Comment:
        """Cree un commentaire et extrait les mentions."""
        comment = Comment(
            tenant_id=tenant_id,
            ao_id=ao_id,
            author_id=author_id,
            parent_id=parent_id,
            content=content,
        )
        self.db.add(comment)
        await self.db.flush()

        mentions = MENTION_PATTERN.findall(content)
        for username in mentions:
            await self._process_mention(
                comment_id=comment.id,
                username=username,
                tenant_id=tenant_id,
                author_id=author_id,
                ao_id=ao_id,
            )

        await self._notify_thread_participants(comment, author_id)
        await self.db.flush()
        return comment

    async def _process_mention(
        self,
        comment_id: uuid.UUID,
        username: str,
        tenant_id: uuid.UUID,
        author_id: uuid.UUID,
        ao_id: uuid.UUID,
    ) -> None:
        """Trouve l'utilisateur mentionne et cree la notification."""
        stmt = select(User).where(
            and_(
                User.tenant_id == tenant_id,
                User.email.ilike(f"{username}@%"),
            )
        )
        result = await self.db.execute(stmt)
        mentioned_user = result.scalar_one_or_none()

        if not mentioned_user:
            stmt = select(User).where(
                and_(
                    User.tenant_id == tenant_id,
                    User.full_name.ilike(f"%{username}%"),
                )
            )
            result = await self.db.execute(stmt)
            mentioned_user = result.scalar_one_or_none()

        if mentioned_user:
            mention = CommentMention(
                comment_id=comment_id,
                mentioned_user_id=mentioned_user.id,
                mentioned_by_user_id=author_id,
            )
            self.db.add(mention)

            await self.notif_service.notify_mention(
                tenant_id=tenant_id,
                recipient_id=mentioned_user.id,
                comment_id=comment_id,
                ao_id=ao_id,
                mentioned_by=author_id,
            )

    async def _notify_thread_participants(
        self,
        comment: Comment,
        author_id: uuid.UUID,
    ) -> None:
        """Notifie les participants du thread qu'une reponse a ete ajoutee."""
        if not comment.parent_id:
            return

        stmt = select(Comment).where(Comment.id == comment.parent_id)
        result = await self.db.execute(stmt)
        parent = result.scalar_one_or_none()

        if parent and parent.author_id != author_id:
            await self.notif_service.notify_reply(
                tenant_id=comment.tenant_id,
                recipient_id=parent.author_id,
                comment_id=comment.id,
                ao_id=comment.ao_id,
                reply_author_id=author_id,
            )

    async def get_comments_for_ao(
        self,
        ao_id: uuid.UUID,
        include_resolved: bool = False,
    ) -> list[dict]:
        """Liste les commentaires d'un AO (threaded)."""
        conditions = [Comment.ao_id == ao_id]
        if not include_resolved:
            conditions.append(Comment.status == CommentStatus.OPEN)

        stmt = select(Comment).where(
            and_(*conditions, Comment.parent_id.is_(None))
        ).order_by(Comment.created_at.desc())

        result = await self.db.execute(stmt)
        root_comments = result.scalars().all()

        comments_tree = []
        for root in root_comments:
            comments_tree.append(await self._build_comment_tree(root, conditions))

        return comments_tree

    async def _build_comment_tree(
        self,
        comment: Comment,
        conditions: list,
    ) -> dict:
        """Construit l'arbre des reponses."""
        stmt = select(Comment).where(
            and_(*conditions, Comment.parent_id == comment.id)
        ).order_by(Comment.created_at)

        result = await self.db.execute(stmt)
        replies = result.scalars().all()

        reply_dicts = []
        for reply in replies:
            reply_dicts.append(await self._build_comment_tree(reply, conditions))

        return {
            "id": str(comment.id),
            "content": comment.content,
            "author_id": str(comment.author_id),
            "status": comment.status.value,
            "is_edited": comment.is_edited,
            "created_at": comment.created_at.isoformat() if comment.created_at else None,
            "replies": reply_dicts,
        }

    async def update_comment(
        self,
        comment_id: uuid.UUID,
        author_id: uuid.UUID,
        new_content: str,
    ) -> Optional[Comment]:
        """Met a jour un commentaire (seulement l'auteur)."""
        stmt = select(Comment).where(
            and_(Comment.id == comment_id, Comment.author_id == author_id)
        )
        result = await self.db.execute(stmt)
        comment = result.scalar_one_or_none()

        if not comment:
            return None

        comment.content = new_content
        comment.is_edited = True
        comment.edited_at = datetime.now(timezone.utc)
        await self.db.flush()

        return comment

    async def resolve_comment(
        self,
        comment_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Marque un commentaire comme resolu."""
        stmt = select(Comment).where(Comment.id == comment_id)
        result = await self.db.execute(stmt)
        comment = result.scalar_one_or_none()

        if not comment:
            return False

        comment.status = CommentStatus.RESOLVED
        await self.db.flush()
        return True
