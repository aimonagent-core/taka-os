"""Pipeline de rédaction — connecte le scoring à la génération automatique."""
import logging

from app.database import AsyncSessionLocal
from app.models.ao_s2 import AO
from app.agents.redacteur.pipeline import RedactionPipeline
from app.agents.deposant.tracker import SubmissionTracker

logger = logging.getLogger(__name__)


class RedactionOrchestrator:
    """Orchestreur : Scoring → Rédaction (auto) → HIL pending → Dépôt (manuel)."""

    def __init__(self):
        self.redaction_pipeline = RedactionPipeline()
        self.tracker = SubmissionTracker()

    async def on_scoring_complete(self, ao_id: str, scoring_run_id: str):
        """Callback appelé après qu'un AO a été scoré."""
        logger.info("[Orchestrator] Scoring complete pour AO %s", ao_id)
        result = await self.redaction_pipeline.on_ao_scored(ao_id, scoring_run_id)
        if result["generated"]:
            logger.info("[Orchestrator] Réponse auto-générée : %s", result["response_id"])
        else:
            logger.info("[Orchestrator] Pas de rédaction auto : %s", result["error"])

    async def run_periodic_checks(self):
        """Vérifie périodiquement les statuts de soumission."""
        async with AsyncSessionLocal() as db:
            updates = await self.tracker.check_all_pending(db)
            if updates:
                logger.info("[Orchestrator] %s soumissions mises à jour", len(updates))
