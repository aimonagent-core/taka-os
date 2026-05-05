"""Agent Déposant — orchestre le dépôt des réponses sur les plateformes."""
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.response import GeneratedResponse
from app.models.submission import Submission, SubmissionPlatform
from app.agents.deposant.mock_platforms import PLATFORM_REGISTRY

logger = logging.getLogger(__name__)


class DeposantSubmitter:
    """Soumissionnaire automatique pour les réponses validées."""

    async def submit(
        self,
        generated_response_id: str,
        platform_id: str,
        user_id: str,
        db: AsyncSession,
    ) -> Submission:
        """Soumet une réponse générée sur une plateforme."""
        stmt = select(GeneratedResponse).where(GeneratedResponse.id == generated_response_id)
        row = await db.execute(stmt)
        response = row.scalar_one_or_none()
        if not response:
            raise ValueError(f"Réponse {generated_response_id} introuvable")

        if response.status not in ("approved",):
            raise ValueError(f"Réponse status={response.status} — doit être 'approved' avant dépôt")

        if response.hil_status != "validated":
            raise ValueError(f"HIL status={response.hil_status} — validation humaine requise")

        stmt_plat = select(SubmissionPlatform).where(SubmissionPlatform.id == platform_id)
        row_plat = await db.execute(stmt_plat)
        platform = row_plat.scalar_one_or_none()
        if not platform:
            raise ValueError(f"Plateforme {platform_id} introuvable")

        submission = Submission(
            generated_response_id=generated_response_id,
            platform_id=platform_id,
            user_id=user_id,
            status="submitting",
        )
        db.add(submission)
        await db.commit()
        await db.refresh(submission)

        try:
            mock_platform_class = PLATFORM_REGISTRY.get(platform.platform_type)
            if not mock_platform_class:
                raise ValueError(f"Type de plateforme inconnu : {platform.platform_type}")

            mock_platform = mock_platform_class()
            dossier = {
                "ao_reference": str(response.ao_id),
                "response_id": str(response.id),
                "content": response.content[:1000],
                "category": response.category,
            }

            result = await mock_platform.submit(dossier)

            if result.success:
                submission.status = "submitted"
                submission.platform_reference = result.reference
                submission.submitted_at = datetime.now(timezone.utc)
                submission.platform_response = {
                    "mock": True,
                    "latency_ms": result.latency_ms,
                    "timestamp": result.timestamp.isoformat(),
                }
                logger.info("[Déposant] Soumission %s OK — ref=%s", submission.id, result.reference)
            else:
                submission.status = "rejected"
                submission.error_message = result.error
                submission.retry_count += 1
                logger.warning("[Déposant] Soumission %s échouée : %s", submission.id, result.error)

        except Exception as e:
            submission.status = "rejected"
            submission.error_message = str(e)
            submission.retry_count += 1
            logger.error("[Déposant] Exception soumission %s: %s", submission.id, e)

        await db.commit()
        return submission

    async def retry(self, submission_id: str, user_id: str, db: AsyncSession) -> Submission:
        """Relance une soumission en échec."""
        stmt = select(Submission).where(Submission.id == submission_id)
        row = await db.execute(stmt)
        sub = row.scalar_one_or_none()
        if not sub:
            raise ValueError(f"Soumission {submission_id} introuvable")

        if sub.status not in ("rejected", "pending"):
            raise ValueError(f"Statut {sub.status} — retry impossible")

        if sub.retry_count >= 3:
            raise ValueError("Nombre max de retries atteint (3)")

        sub.status = "submitting"
        await db.commit()

        return await self.submit(
            generated_response_id=str(sub.generated_response_id),
            platform_id=str(sub.platform_id),
            user_id=user_id,
            db=db,
        )
