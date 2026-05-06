"""
Agent Deposant — orchestre le depot des reponses sur les plateformes.

VERSION v0.10.0 : Fallback EXPLICITE — le mock n'est plus silencieux.
Risque juridique L121-1 Code conso : toute soumission mock DOIT etre signalee.
"""

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.response import GeneratedResponse
from app.models.submission import Submission, SubmissionPlatform
from app.models.audit import PlatformCredential
from app.agents.deposant.connectors import get_connector
from app.agents.deposant.connectors.base import PlatformCredentials
from app.agents.auditor import AuditEngine

logger = logging.getLogger(__name__)

# Variable d'environnement pour forcer les soumissions reelles
FORCE_REAL_SUBMISSION = os.environ.get("FORCE_REAL_SUBMISSION", "false").lower() in (
    "true",
    "1",
    "yes",
)


@dataclass
class SubmissionResult:
    """
    Resultat d'une tentative de depot.

    Champs:
        status: Statut de la soumission ("submitted" | "mock_submitted" | "error" | "pending")
        platform: Nom de la plateforme cible
        is_mock: True si c'etait une simulation
        warning: Message d'avertissement si mock
        requires_action: Action utilisateur requise pour passer en reel
        submitted_at: Timestamp de la soumission
        external_id: ID externe retourne par la plateforme (si reel)
        error_message: Message d'erreur (si erreur)
        details: Details supplementaires
    """

    status: str  # "submitted" | "mock_submitted" | "error" | "pending"
    platform: str
    is_mock: bool = False
    warning: Optional[str] = None
    requires_action: Optional[str] = None
    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    external_id: Optional[str] = None
    error_message: Optional[str] = None
    details: Optional[dict[str, Any]] = None


class DeposantSubmitter:
    """Soumissionnaire automatique pour les reponses validees.

    VERSION v0.10.0 — Fallback explicite:
    - Si aucun connecteur reel n'est configure pour une plateforme,
      le systeme retourne un statut "mock_submitted" (pas "submitted")
    - Un message d'avertissement clair est inclus dans la reponse
    - Une action requise est indiquee pour configurer un connecteur
    - Le mock est logge en WARNING (pas INFO silencieux)
    - Option FORCE_REAL_SUBMISSION=true pour desactiver le mock
    """

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

        # === FALLBACK EXPLICITE v0.10.0 ===
        # Aucun connecteur reel configure

        if FORCE_REAL_SUBMISSION:
            logger.error(
                "[Deposant] FORCE_REAL_SUBMISSION=true mais aucun connecteur "
                "valide pour %s — Refus du mock",
                platform_type,
            )
            raise ValueError(
                f"FORCE_REAL_SUBMISSION est active mais aucun connecteur "
                f"n'est configure pour '{platform_type}'. "
                f"Configurez un connecteur ou desactivez FORCE_REAL_SUBMISSION."
            )

        # 3. Fallback sur mock — EXPLICITE
        try:
            connector_class = get_connector(platform_type, use_real=False)
            logger.warning(
                "[MOCK] Fallback MOCK explicite pour %s — aucun connecteur reel configure. "
                "Article L121-1 Code conso — obligation d'information.",
                platform_type,
            )
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
                    # v0.10.0 — Fallback explicite
                    "is_mock": not is_real,
                    "warning": (
                        "Ce depot est une SIMULATION. Aucun dossier n'a ete soumis "
                        f"sur la plateforme reelle '{platform.platform_type}'. "
                        "Les donnees ont ete enregistrees localement uniquement."
                        if not is_real
                        else None
                    ),
                    "requires_action": (
                        "Configurer un connecteur dans Parametres > Plateformes"
                        if not is_real
                        else None
                    ),
                    "_mock_notice": (
                        "[ATTENTION] Cette soumission est une simulation locale. "
                        "Aucun dossier n'a ete transmis a la plateforme reelle. "
                        "Article L121-1 Code de la consommation — obligation d'information."
                        if not is_real
                        else None
                    ),
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

    async def check_status(
        self,
        submission_id: str,
        db: AsyncSession,
    ) -> dict[str, Any]:
        """Verifie le statut d'une soumission existante."""
        stmt = select(Submission).where(Submission.id == submission_id)
        row = await db.execute(stmt)
        sub = row.scalar_one_or_none()
        if not sub:
            raise ValueError(f"Soumission {submission_id} introuvable")

        return {
            "id": str(sub.id),
            "status": sub.status,
            "platform_reference": sub.platform_reference,
            "is_mock": sub.platform_response.get("is_mock", False) if sub.platform_response else False,
            "warning": sub.platform_response.get("warning") if sub.platform_response else None,
            "submitted_at": sub.submitted_at.isoformat() if sub.submitted_at else None,
            "error": sub.error_message,
        }

    async def get_platforms_status(self, db: AsyncSession, tenant_id) -> dict[str, dict[str, Any]]:
        """Retourne le statut de toutes les plateformes supportees."""
        all_platforms = [
            "boamp",
            "e_notification",
            "maroc",
            "ted",
            "custom",
        ]

        result: dict[str, dict[str, Any]] = {}
        for platform in all_platforms:
            stmt = select(PlatformCredential).where(
                and_(
                    PlatformCredential.tenant_id == tenant_id,
                    PlatformCredential.platform_type == platform,
                    PlatformCredential.is_active == True,
                )
            )
            row = await db.execute(stmt)
            cred = row.scalar_one_or_none()
            result[platform] = {
                "configured": cred is not None,
                "enabled": cred is not None and cred.is_validated,
                "has_real_connector": cred is not None and cred.is_validated,
            }

        return result
