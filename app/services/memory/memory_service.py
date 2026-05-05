# File: app/services/memory/memory_service.py
# Purpose: Memory service adapted to existing MemoryEntry model
# Dependencies: datetime, structlog, app.models.ao

import hashlib
from datetime import datetime, timedelta
from typing import Any, Sequence

import logging
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ao import MemoryEntry, MemoryType

logger = logging.getLogger(__name__)


class MemoryService:
    STM_TTL_SECONDS: int = 72 * 3600
    IM_TTL_SECONDS: int = 30 * 24 * 3600
    LTM_TTL_SECONDS: int = 7 * 365 * 24 * 3600
    CONSOLIDATION_BATCH: int = 20
    DECAY_HALF_LIFE_DAYS: float = 7.0

    def __init__(self, db: AsyncSession, embedding_client: "MistralAIClient") -> None:
        self._db = db
        self._embedding_client = embedding_client

    async def ingest(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.SEMANTIC,
        user_id: Any = None,
        source_type: str = "document",
        source_id: Any = None,
        metadata: dict[str, Any] | None = None,
        priority: int = 3,
    ) -> MemoryEntry:
        try:
            embeddings = await self._embedding_client.embed_texts([content])
            embedding = embeddings[0] if embeddings else []
        except Exception as exc:
            logger.error("embedding_failed", error=str(exc))
            embedding = []

        content_dict = {"text": content, **(metadata or {})}
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        entry = MemoryEntry(
            user_id=user_id,
            memory_type=memory_type,
            content=content_dict,
            content_hash=content_hash,
            embedding=embedding,
            priority=priority,
            source_type=source_type,
            source_id=source_id,
            ttl_seconds=self.STM_TTL_SECONDS,
            decay_factor=1.0,
        )
        self._db.add(entry)
        await self._db.commit()
        await self._db.refresh(entry)
        logger.info("memory_ingest", entry_id=str(entry.id), memory_type=memory_type.value)
        await self._maybe_consolidate()
        return entry

    async def search(
        self,
        query: str,
        user_id: Any = None,
        limit: int = 10,
    ) -> Sequence[MemoryEntry]:
        try:
            embeddings = await self._embedding_client.embed_texts([query])
            query_embedding = embeddings[0] if embeddings else []
        except Exception as exc:
            logger.error("embedding_failed_search", error=str(exc))
            query_embedding = []

        if not query_embedding:
            stmt = (
                select(MemoryEntry)
                .where(MemoryEntry.user_id == user_id)
                .order_by(desc(MemoryEntry.created_at))
                .limit(limit)
            )
            result = await self._db.execute(stmt)
            return result.scalars().all()

        stmt = (
            select(MemoryEntry)
            .where(MemoryEntry.user_id == user_id)
            .order_by(
                MemoryEntry.embedding.cosine_distance(query_embedding)
            )
            .limit(limit)
        )
        result = await self._db.execute(stmt)
        return result.scalars().all()

    async def _maybe_consolidate(self) -> None:
        from sqlalchemy import func

        count_stm = await self._db.scalar(
            select(func.count(MemoryEntry.id)).where(
                MemoryEntry.ttl_seconds == self.STM_TTL_SECONDS,
                MemoryEntry.consolidated_at.is_(None),
            )
        )
        if (count_stm or 0) < self.CONSOLIDATION_BATCH:
            return

        stmt = (
            select(MemoryEntry)
            .where(
                MemoryEntry.ttl_seconds == self.STM_TTL_SECONDS,
                MemoryEntry.consolidated_at.is_(None),
            )
            .order_by(MemoryEntry.created_at)
            .limit(self.CONSOLIDATION_BATCH)
        )
        result = await self._db.execute(stmt)
        batch = result.scalars().all()

        summary_content = " ".join(
            str(b.content.get("text", "")) for b in batch if isinstance(b.content, dict)
        )
        try:
            embeddings = await self._embedding_client.embed_texts([summary_content])
            summary_embedding = embeddings[0] if embeddings else []
        except Exception:
            summary_embedding = []

        summary_hash = hashlib.sha256(summary_content.encode()).hexdigest()
        summary = MemoryEntry(
            user_id=batch[0].user_id,
            memory_type=MemoryType.SEMANTIC,
            content={"text": f"Consolidated summary of {len(batch)} entries"},
            content_hash=summary_hash,
            embedding=summary_embedding,
            priority=4,
            source_type="consolidation",
            ttl_seconds=self.IM_TTL_SECONDS,
            decay_factor=1.0,
        )
        self._db.add(summary)
        await self._db.flush()

        for entry in batch:
            entry.consolidated_at = datetime.utcnow()
            entry.ttl_seconds = self.IM_TTL_SECONDS

        await self._db.commit()
        logger.info(
            "memory_consolidated",
            batch_size=len(batch),
            summary_id=str(summary.id),
        )

    async def apply_decay(self) -> int:
        now = datetime.utcnow()
        half_life = timedelta(days=self.DECAY_HALF_LIFE_DAYS)
        stmt = select(MemoryEntry).where(
            MemoryEntry.ttl_seconds.isnot(None),
            MemoryEntry.last_accessed_at.isnot(None),
        )
        result = await self._db.execute(stmt)
        entries = result.scalars().all()
        decayed = 0
        for entry in entries:
            if entry.last_accessed_at:
                age = now - entry.last_accessed_at
                factor = 0.5 ** (age.total_seconds() / half_life.total_seconds())
                entry.decay_factor *= factor
                if entry.decay_factor < 0.1:
                    entry.ttl_seconds = self.LTM_TTL_SECONDS
                    decayed += 1
        await self._db.commit()
        logger.info("memory_decay_applied", decayed_count=decayed)
        return decayed

    async def promote_to_ltm(self, entry_id: Any) -> bool:
        entry = await self._db.get(MemoryEntry, entry_id)
        if not entry:
            return False
        entry.ttl_seconds = self.LTM_TTL_SECONDS
        entry.priority = 5
        await self._db.commit()
        logger.info("memory_promoted_to_ltm", entry_id=str(entry.id))
        return True

    async def delete_expired(self) -> int:
        now = datetime.utcnow()
        from sqlalchemy import delete

        stmt = delete(MemoryEntry).where(
            MemoryEntry.expires_at.isnot(None),
            MemoryEntry.expires_at < now,
        )
        result = await self._db.execute(stmt)
        await self._db.commit()
        count = result.rowcount or 0
        logger.info("memory_expired_deleted", count=count)
        return count
