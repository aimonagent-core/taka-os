"""Agent Deposant — orchestre le depot des reponses sur les plateformes."""
import logging
from datetime import datetime, timezone

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.response import GeneratedResponse
from app.models.submission import Submission, SubmissionPlatform
from app.models.audit import PlatformCredential
from app.agents.deposant.connectors import get_connector
from app.agents.deposant.connectors.base import PlatformCredentials
from app.agents.auditor import AuditEngine

logger = logging.getLogger(__name__)


class DeposantSubmitter:
    """Soumissionnaire automatique pour les reponses validees."""

    async def _get_connector_for_platform(
        self,
        db: AsyncSession,
        tenant_id,
        platform_type: str,
    ):
        """Selectionne real vs mock avec fallback audite."""
        from app.core.encryption import decrypt_value

        # 1. Cherche credential valide
        stmt_cred = select(PlatformCredential).where(
            and_(
                PlatformCredential.tenant_id == tenant_id,
                PlatformCredential.platform_type == platform_type,
                PlatformCredential.is_active == True,
            )
        )
        result = await db.execute(stmt_cred)
        cred = result.scalar_one_or_none()

        # 2. Si credential valide, tente le connecteur real
        if cred and cred.is_validated:
            try:
                connector_creds = PlatformCredentials(
                    username=decrypt_value(cred.username),
                    password=decrypt_value(cred.password),
                    api_key=decrypt_value(cred.api_key),
                    certificate_pem=decrypt_value(cred.certificate_pem),
                    base_url=cred.base_url,
                    additional_data=cred.additional_data,
                )
                connector_class = get_connector(platform_type, use_real=True)
                logger.info("[Deposant] Utilisation connecteur REAL pour %s", platform_type)
                return connector_class(connector_creds), True, cred
            except ValueError:
                # Pas de connecteur real disponible pour cette plateforme
                pass
            except Exception as e:
                logger.warning("[Deposant] Echec init connecteur real %s: %s", platform_type, e)

        # 3. Fallback sur mock
        try:
            connector_class = get_connector(platform_type, use_real=False)
            logger.info("[Deposant] Fallback MOCK pour %s", platform_type)
            return connector_class(PlatformCredentials()), False, None
        except ValueError:
            logger.error("[Deposant] Aucun connecteur (real ou mock) pour %s", platform_type)
            raise ValueError(f"Plateforme '{platform_type}' non supportee")

    async def submit(
        self,
        generated_response_id: str,
        platform_id: str,
        user_id: str,
        db: AsyncSession,
        tenant_id=None,
    ) -> Submission:
        """Soumet une reponse generee sur une plateforme."""
        stmt = select(GeneratedResponse).where(GeneratedResponse.id == generated_response_id)
        row = await db.execute(stmt)
        response = row.scalar_one_or_none()
        if not response:
            raise ValueError(f"Reponse {generated_response_id} introuvable")

        if response.status not in ("approved",):
            raise ValueError(f"Reponse status={response.status} — doit etre 'approved' avant depot")

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

        audit = AuditEngine(db)

        try:
            connector, is_real, cred = await self._get_connector_for_platform(
                db, tenant_id or getattr(response, "tenant_id", None), platform.platform_type
            )

            docs = []  # TODO: rattacher documents reels depuis response.documents
            result = await connector.submit(
                ao_reference=str(response.ao_id),
                response_text=response.content[:5000],
                documents=docs,
            )

            if result.status.value in ("success", "pending"):
                submission.status = "submitted" if result.status.value == "success" else "pending"
                submission.platform_reference = result.platform_reference
                submission.submitted_at = datetime.now(timezone.utc)
                submission.platform_response = {
                    "real": is_real,
                    "status": result.status.value,
                    "message": result.message,
                    "next_steps": result.next_steps,
                }
                logger.info(
                    "[Deposant] Soumission %s OK (%s) — ref=%s",
                    submission.id,
                    "real" if is_real else "mock",
                    result.platform_reference,
                )

                # Audit log
                await audit.log_user_action(
                    tenant_id=tenant_id or getattr(response, "tenant_id", None),
                    user_id=user_id,
                    user_email="system",
                    action="submission_created",
                    target_type="submission",
                    target_id=submission.id,
                    target_display=f"Depot {platform.platform_type}",
                    change_summary=f"Soumission {'reelle' if is_real else 'mock'} sur {platform.platform_type}",
                    after_state=submission.platform_response,
                )
            else:
                submission.status = "rejected"
                submission.error_message = result.message
                submission.retry_count += 1
                logger.warning(
                    "[Deposant] Soumission %s echouee (%s): %s",
                    submission.id,
                    result.status.value,
                    result.message,
                )

                await audit.log_system_action(
                    tenant_id=tenant_id or getattr(response, "tenant_id", None),
                    action="submission_failed",
                    target_type="submission",
                    target_id=submission.id,
                    change_summary=f"Echec depot {platform.platform_type}: {result.message}",
                    severity="warning",
                    after_state={"error": result.message, "status": result.status.value},
                )

        except Exception as e:
            submission.status = "rejected"
            submission.error_message = str(e)
            submission.retry_count += 1
            logger.error("[Deposant] Exception soumission %s: %s", submission.id, e)

            await audit.log_system_action(
                tenant_id=tenant_id or getattr(response, "tenant_id", None),
                action="submission_exception",
                target_type="submission",
                target_id=submission.id,
                change_summary=f"Exception depot: {str(e)[:200]}",
                severity="error",
                after_state={"error": str(e)},
            )

        await db.commit()
        return submission

    async def retry(self, submission_id: str, user_id: str, db: AsyncSession, tenant_id=None) -> Submission:
        """Relance une soumission en echec."""
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
            tenant_id=tenant_id,
        )
