# =============================================================================
# C6b — app/agents/scorer/agent.py
# Wrapper AgentScorer — delegue a ScoringEngine
# =============================================================================

"""
Agent Scorer — Wrapper vers ScoringEngine.

Ce module expose un 'agent' scorer qui delegue toute la logique metier
au ScoringEngine existant dans app/services/scoring.py.

Cette architecture permet :
1. De presenter le scorer comme un agent (coherence avec les autres agents)
2. De garder la logique metier dans services/ (separation des concerns)
3. De migrer la logique ici plus tard si le scorer devient plus complexe
"""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scoring import ScoringFeedback, ScoringRun
from app.services.scoring.engine import ScoringEngine

logger = logging.getLogger(__name__)


class AgentScorer:
    """Agent de scoring — wrapper vers ScoringEngine.

    Cet agent encapsule la logique de scoring des appels d'offres.
    Il delegue au ScoringEngine pour l'execution reelle.
    """

    name: str = "scorer"
    description: str = "Evalue la compatibilite d'un AO avec le profil de l'entreprise"

    def __init__(self) -> None:
        """Initialise l'agent scorer avec le moteur de scoring."""
        self._engine = ScoringEngine()
        logger.debug("AgentScorer initialise")

    async def score_ao(
        self,
        db: AsyncSession,
        ao_id: UUID,
        profile: str = "prudent",
        triggered_by: str = "auto",
    ) -> Dict[str, Any]:
        """Execute un scoring complet sur un AO et persiste le resultat.

        Args:
            db: Session async SQLAlchemy
            ao_id: ID de l'appel d'offres a scorer
            profile: Profil de scoring (prudent, equilibre, audacieux)
            triggered_by: Declencheur du scoring

        Returns:
            Dict contenant le scoring_id, score_global, et les dimensions
        """
        logger.info("AgentScorer — scoring AO %s (profile=%s)", ao_id, profile)
        scoring_run = await self._engine.score_and_save(
            ao_id=ao_id,
            profile=profile,
            db=db,
            triggered_by=triggered_by,
        )
        logger.info(
            "AgentScorer — scoring termine : score=%s verdict=%s",
            scoring_run.score_global,
            scoring_run.verdict,
        )
        return {
            "scoring_id": str(scoring_run.id),
            "ao_id": str(scoring_run.ao_id),
            "score_global": float(scoring_run.score_global),
            "verdict": scoring_run.verdict,
            "confidence": float(scoring_run.confidence),
            "profile": scoring_run.profile,
            "details": scoring_run.details,
            "recommendations": scoring_run.recommendations,
        }

    async def get_score_dimensions(
        self,
        db: AsyncSession,
        scoring_run_id: UUID,
    ) -> List[Dict[str, Any]]:
        """Recupere les dimensions d'un scoring existant.

        Args:
            db: Session async SQLAlchemy
            scoring_run_id: ID du run de scoring

        Returns:
            Liste des dimensions avec leurs scores
        """
        stmt = select(ScoringRun).where(ScoringRun.id == scoring_run_id)
        result = await db.execute(stmt)
        run = result.scalar_one_or_none()
        if not run:
            return []

        return [
            {"dimension_key": "coherence", "dimension_label": "Coherence metier", "score": float(run.score_coherence)},
            {"dimension_key": "financiere", "dimension_label": "Rentabilite financiere", "score": float(run.score_financiere)},
            {"dimension_key": "geographique", "dimension_label": "Proximite geographique", "score": float(run.score_geographique)},
            {"dimension_key": "temporelle", "dimension_label": "Disponibilite temporelle", "score": float(run.score_temporelle)},
            {"dimension_key": "concurrentielle", "dimension_label": "Position concurrentielle", "score": float(run.score_concurrentielle)},
        ]

    async def submit_feedback(
        self,
        db: AsyncSession,
        scoring_run_id: UUID,
        user_id: UUID,
        feedback_type: str = "general",
        rating: Optional[int] = None,
        comment: Optional[str] = None,
        verdict_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Soumet un feedback utilisateur sur un scoring.

        Args:
            db: Session async SQLAlchemy
            scoring_run_id: ID du run de scoring
            user_id: ID de l'utilisateur qui feedback
            feedback_type: Type de feedback
            rating: Note de 1 a 5 (optionnel)
            comment: Commentaire optionnel
            verdict_override: Surcharge de verdict (optionnel)

        Returns:
            Dict avec le feedback_id et statut
        """
        feedback = ScoringFeedback(
            scoring_run_id=scoring_run_id,
            user_id=user_id,
            feedback_type=feedback_type,
            user_comment=comment,
            user_override_verdict=verdict_override,
        )
        db.add(feedback)
        await db.commit()
        await db.refresh(feedback)
        logger.info(
            "AgentScorer — feedback soumis : run=%s user=%s",
            scoring_run_id,
            user_id,
        )
        return {
            "feedback_id": str(feedback.id),
            "status": "submitted",
        }
