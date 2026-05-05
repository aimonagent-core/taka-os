# File: app/services/hil/hil_service.py
# Purpose: Human-in-the-loop request service
# Dependencies: datetime, structlog, app.models.ao

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ao import HILRequest

logger = logging.getLogger(__name__)


class HILService:
    DEFAULT_EXPIRY_HOURS: int = 48

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_request(
        self,
        user_id: UUID,
        request_id: UUID,
        autonomy_level: int,
        decision_type: str,
        context: dict[str, Any],
        expires_hours: int = DEFAULT_EXPIRY_HOURS,
    ) -> HILRequest:
        hil = HILRequest(
            request_id=request_id,
            autonomy_level=autonomy_level,
            decision_type=decision_type,
            context=context,
            status="pending",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=expires_hours),
        )
        self._db.add(hil)
        await self._db.commit()
        await self._db.refresh(hil)
        logger.info("hil_request_created: hil_id=%s decision_type=%s", hil.id, decision_type)
        return hil

    async def get_pending(self, user_id: UUID | None = None) -> list[HILRequest]:
        stmt = select(HILRequest).where(
            HILRequest.status == "pending",
            HILRequest.expires_at > datetime.now(timezone.utc),
        )
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def resolve(
        self,
        hil_id: UUID,
        decision: str,
        resolver_id: UUID,
        notes: str = "",
    ) -> HILRequest:
        hil = await self._db.get(HILRequest, hil_id)
        if not hil:
            raise ValueError(f"HIL request {hil_id} not found")
        if hil.status != "pending":
            raise ValueError(f"HIL request {hil_id} is not pending")
        if datetime.now(timezone.utc) > hil.expires_at:
            hil.status = "expired"
            await self._db.commit()
            raise ValueError(f"HIL request {hil_id} has expired")

        hil.status = "resolved"
        hil.decided_by = resolver_id
        hil.decided_at = datetime.now(timezone.utc)
        hil.decision_value = {"decision": decision, "notes": notes}
        await self._db.commit()
        await self._db.refresh(hil)
        logger.info(
            "hil_resolved",
            hil_id=str(hil_id),
            decision=decision,
            resolver_id=str(resolver_id),
        )
        return hil

    async def reject(self, hil_id: UUID, resolver_id: UUID, reason: str = "") -> HILRequest:
        hil = await self._db.get(HILRequest, hil_id)
        if not hil:
            raise ValueError(f"HIL request {hil_id} not found")
        hil.status = "rejected"
        hil.decided_by = resolver_id
        hil.decided_at = datetime.now(timezone.utc)
        hil.decision_value = {"decision": "rejected", "notes": reason}
        await self._db.commit()
        await self._db.refresh(hil)
        logger.info("hil_rejected: hil_id=%s resolver_id=%s", hil_id, resolver_id)
        return hil

    async def escalate(self, hil_id: UUID, to_user_id: UUID, reason: str = "") -> HILRequest:
        original = await self._db.get(HILRequest, hil_id)
        if not original:
            raise ValueError(f"HIL request {hil_id} not found")
        original.status = "escalated"

        escalated = HILRequest(
            request_id=original.request_id,
            autonomy_level=original.autonomy_level,
            decision_type=original.decision_type,
            context={
                **original.context,
                "escalated_from": str(hil_id),
                "escalation_reason": reason,
            },
            status="pending",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=self.DEFAULT_EXPIRY_HOURS),
        )
        self._db.add(escalated)
        await self._db.commit()
        await self._db.refresh(escalated)
        logger.info("hil_escalated: from_hil_id=%s to_hil_id=%s", hil_id, escalated.id)
        return escalated

    async def expire_stale(self) -> int:
        now = datetime.now(timezone.utc)
        stmt = select(HILRequest).where(
            HILRequest.status == "pending",
            HILRequest.expires_at <= now,
        )
        result = await self._db.execute(stmt)
        stale = result.scalars().all()
        count = 0
        for req in stale:
            req.status = "expired"
            count += 1
        await self._db.commit()
        logger.info("hil_expired_stale: count=%s", count)
        return count
