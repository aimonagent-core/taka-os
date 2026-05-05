"""Suivi des soumissions — vérifie les statuts et notifie."""
import logging
from datetime import datetime, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.submission import Submission, SubmissionPlatform
from app.agents.deposant.mock_platforms import PLATFORM_REGISTRY

logger = logging.getLogger(__name__)


class SubmissionTracker:
    """Tracker de statuts de soumission."""

    async def check_all_pending(self, db: AsyncSession) -> list[dict]:
        """Vérifie le statut de toutes les soumissions 'submitted' non confirmées."""
        stmt = select(Submission).where(
            and_(
                Submission.status == "submitted",
                Submission.confirmed_at.is_(None),
            )
        )
        rows = await db.execute(stmt)
        subs = rows.scalars().all()

        updates = []
        for sub in subs:
            try:
                stmt_plat = select(SubmissionPlatform).where(SubmissionPlatform.id == sub.platform_id)
                row_plat = await db.execute(stmt_plat)
                platform = row_plat.scalar_one_or_none()
                if not platform:
                    continue

                mock_class = PLATFORM_REGISTRY.get(platform.platform_type)
                if not mock_class:
                    continue

                mock = mock_class()
                status = await mock.check_status(sub.platform_reference or "")

                if status["status"] in ("accepted", "published", "attribué"):
                    sub.status = "confirmed"
                    sub.confirmed_at = datetime.now(timezone.utc)
                    sub.platform_response = {**(sub.platform_response or {}), "final_status": status}
                    updates.append({"id": str(sub.id), "status": "confirmed"})
                elif status["status"] in ("rejected",):
                    sub.status = "rejected"
                    sub.error_message = "Rejeté par la plateforme"
                    updates.append({"id": str(sub.id), "status": "rejected"})

            except Exception as e:
                logger.warning("[Tracker] Erreur check %s: %s", sub.id, e)

        if updates:
            await db.commit()

        return updates
