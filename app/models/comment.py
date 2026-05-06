"""Modeles pour les commentaires sur les AO."""

from datetime import datetime
from typing import Optional
import uuid
from enum import Enum as PyEnum

from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean, Index, func, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CommentStatus(str, PyEnum):
    OPEN = "open"
    RESOLVED = "resolved"


class Comment(Base):
    """Commentaire sur un AO (thread de discussion)."""

    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    ao_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("aos.id"), nullable=False, index=True)
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("comments.id"), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(SQLEnum(CommentStatus, name="comment_status"), default=CommentStatus.OPEN, nullable=False)

    is_edited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    edited_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_comments_ao", "ao_id", "created_at"),
        Index("idx_comments_author", "author_id", "created_at"),
        Index("idx_comments_parent", "parent_id"),
    )


class CommentMention(Base):
    """Mention @utilisateur dans un commentaire."""

    __tablename__ = "comment_mentions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("comments.id"), nullable=False, index=True)
    mentioned_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    mentioned_by_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    is_notified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_mention_user", "mentioned_user_id", "is_notified"),
    )
