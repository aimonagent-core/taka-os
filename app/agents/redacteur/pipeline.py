"""Pipeline de rédaction automatique — déclenché après scoring GO/MAYBE."""
import logging

from app.database import AsyncSessionLocal
from app.models.ao_s2 import AO
from app.services.plan_feature_flags import FeatureFlagService
from app.agents.redacteur.generator import RedacteurGenerator

logger = logging.getLogger(__name__)


class RedactionPipeline:
    """Pipeline automatique : AO qualifié → rédaction → HIL pending."""

    def __init__(self):
        self.generator = RedacteurGenerator()

    async def on_ao_scored(self, ao_id: str, scoring_run_id: str) -> dict:
        """Callback appelé quand un AO est scoré.
        Si verdict = GO ou MAYBE et FF 'generation_ia' activé → génère lettre.
        """
        async with AsyncSessionLocal() as db:
            try:
                enabled = await FeatureFlagService.is_enabled(
                    db, "generation_ia", tenant_tier="pro"
                )
                if not enabled:
                    logger.info("[Pipeline Redaction] generation_ia désactivé — skip AO %s", ao_id)
                    return {"generated": False, "response_id": None, "error": "Feature flag désactivé"}
            except Exception:
                logger.info("[Pipeline Redaction] generation_ia désactivé — skip AO %s", ao_id)
                return {"generated": False, "response_id": None, "error": "Feature flag désactivé"}

            from sqlalchemy import select
            stmt = select(AO).where(AO.id == ao_id)
            row = await db.execute(stmt)
            ao = row.scalar_one_or_none()
            if not ao:
                return {"generated": False, "response_id": None, "error": "AO introuvable"}

            verdict = ao.scoring_result.get("verdict") if ao.scoring_result else None
            if verdict not in ("GO", "MAYBE"):
                return {"generated": False, "response_id": None, "error": f"Verdict {verdict} — pas de rédaction auto"}

            try:
                SYSTEM_USER_ID = "00000000-0000-0000-0000-000000000001"
                response = await self.generator.generate(
                    ao_id=ao_id,
                    category="letter",
                    user_id=SYSTEM_USER_ID,
                    db=db,
                    tenant_id=str(ao.source_id),  # Simplification
                )
                return {"generated": True, "response_id": str(response.id), "error": None}
            except Exception as e:
                logger.error("[Pipeline Redaction] Erreur génération AO %s: %s", ao_id, e)
                return {"generated": False, "response_id": None, "error": str(e)}
