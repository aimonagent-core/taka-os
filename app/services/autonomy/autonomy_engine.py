# File: app/services/autonomy/autonomy_engine.py
# Purpose: Autonomy decision engine with HIL triggers
# Dependencies: datetime, structlog, app.models.ao

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ao import HILRequest

logger = logging.getLogger(__name__)


@dataclass
class Decision:
    action: str
    params: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    requires_hil: bool = False
    hil_reason: str = ""


class AutonomyEngine:
    HIGH_CONFIDENCE_THRESHOLD: float = 0.85
    MEDIUM_CONFIDENCE_THRESHOLD: float = 0.6

    def __init__(
        self,
        db: AsyncSession,
        autonomy_level: str = "advisor",
    ) -> None:
        self._db = db
        self._autonomy_level = autonomy_level

    async def decide_document_action(
        self,
        document_data: dict[str, Any],
        validation_score: float,
        user_id: UUID,
    ) -> Decision:
        amount = document_data.get("amount", 0) or 0
        hil_reasons: list[str] = []

        if validation_score < self.MEDIUM_CONFIDENCE_THRESHOLD:
            hil_reasons.append("low_validation_score")
        if amount > 1_000_000:
            hil_reasons.append("high_value_threshold")
        if document_data.get("requires_compliance_review"):
            hil_reasons.append("compliance_flag")

        if self._autonomy_level == "advisor":
            requires_hil = True
            hil_reasons.append("advisor_mode_always_hil")
        elif self._autonomy_level == "semi_autonomous":
            requires_hil = bool(hil_reasons)
        else:  # fully_autonomous
            requires_hil = validation_score < self.HIGH_CONFIDENCE_THRESHOLD and amount > 5_000_000

        if requires_hil:
            request_id = uuid4()
            hil = HILRequest(
                id=uuid4(),
                request_id=request_id,
                autonomy_level=2 if self._autonomy_level == "semi_autonomous" else 3,
                decision_type="document_validation",
                context={
                    "document_data": document_data,
                    "validation_score": validation_score,
                    "autonomy_level": self._autonomy_level,
                    "hil_reasons": hil_reasons,
                },
                status="pending",
                expires_at=datetime.utcnow() + timedelta(hours=48),
            )
            self._db.add(hil)
            await self._db.commit()
            await self._db.refresh(hil)
            logger.info("hil_request_created: hil_id=%s reasons=%s", hil.id, hil_reasons)
            return Decision(
                action="await_hil",
                params={"hil_id": str(hil.id), "reasons": hil_reasons},
                confidence=validation_score,
                requires_hil=True,
                hil_reason="; ".join(hil_reasons),
            )

        return Decision(
            action="auto_process",
            params={"document_data": document_data},
            confidence=validation_score,
            requires_hil=False,
        )

    async def decide_memory_action(
        self, memory_entry: dict[str, Any], user_id: UUID
    ) -> Decision:
        priority = memory_entry.get("priority", 3)
        if priority >= 5:
            return Decision(
                action="promote_ltm",
                params={"entry_id": memory_entry.get("id")},
                confidence=0.95,
                requires_hil=False,
            )
        if self._autonomy_level == "fully_autonomous":
            return Decision(
                action="auto_classify",
                params={"entry_id": memory_entry.get("id")},
                confidence=0.8,
                requires_hil=False,
            )
        return Decision(
            action="suggest_classify",
            params={"entry_id": memory_entry.get("id")},
            confidence=0.7,
            requires_hil=True,
            hil_reason="memory_classification",
        )
