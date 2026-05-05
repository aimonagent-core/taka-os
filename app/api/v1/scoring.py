"""Routes API pour le Scoring Engine V2."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.scoring import ScoringFeedback, ScoringRun
from app.models.ao import User
from app.services.plan_feature_flags import FeatureFlagService
from app.services.scoring.engine import ScoringEngine

router = APIRouter(prefix="/scoring", tags=["scoring"])


def _get_tenant_tier(user: User) -> str:
    return user.tenant.billing_plan or "free" if user.tenant else "free"


@router.post("/run/{ao_id}")
async def run_scoring(
    ao_id: str,
    profile: str = "prudent",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Execute le scoring sur un AO avec un profil donne."""
    await FeatureFlagService.check_feature(db, "scoring_v2", _get_tenant_tier(current_user))

    if profile not in ("prudent", "opportuniste", "specialise"):
        raise HTTPException(status_code=400, detail="Profil invalide")

    engine = ScoringEngine()
    scoring_run = await engine.score_and_save(
        ao_id=ao_id,
        profile=profile,
        db=db,
        triggered_by=str(current_user.id),
    )

    return {
        "id": str(scoring_run.id),
        "ao_id": str(scoring_run.ao_id),
        "profile": scoring_run.profile,
        "score_global": float(scoring_run.score_global),
        "verdict": scoring_run.verdict,
        "confidence": float(scoring_run.confidence),
        "details": scoring_run.details,
        "recommendations": scoring_run.recommendations,
        "execution_time_ms": scoring_run.execution_time_ms,
    }


@router.get("/runs/{ao_id}")
async def get_scoring_runs(
    ao_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retourne l'historique des scoring pour un AO."""
    await FeatureFlagService.check_feature(db, "scoring_v2", _get_tenant_tier(current_user))

    stmt = select(ScoringRun).where(ScoringRun.ao_id == ao_id).order_by(
        desc(ScoringRun.created_at)
    )
    rows = await db.execute(stmt)
    runs = rows.scalars().all()

    return {
        "runs": [
            {
                "id": str(r.id),
                "profile": r.profile,
                "score_global": float(r.score_global),
                "scores": {
                    "coherence": float(r.score_coherence),
                    "financiere": float(r.score_financiere),
                    "geographique": float(r.score_geographique),
                    "temporelle": float(r.score_temporelle),
                    "concurrentielle": float(r.score_concurrentielle),
                },
                "verdict": r.verdict,
                "confidence": float(r.confidence),
                "recommendations": r.recommendations,
                "created_at": r.created_at.isoformat(),
            }
            for r in runs
        ]
    }


@router.post("/feedback/{scoring_run_id}")
async def post_scoring_feedback(
    scoring_run_id: str,
    feedback_type: str,
    comment: Optional[str] = None,
    override_verdict: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soumet un feedback utilisateur sur un scoring pour calibration."""
    await FeatureFlagService.check_feature(
        db, "scoring_feedback", _get_tenant_tier(current_user)
    )

    if feedback_type not in ("too_strict", "too_lenient", "correct", "irrelevant"):
        raise HTTPException(status_code=400, detail="Type de feedback invalide")

    fb = ScoringFeedback(
        scoring_run_id=scoring_run_id,
        user_id=current_user.id,
        feedback_type=feedback_type,
        user_comment=comment,
        user_override_verdict=override_verdict,
    )
    db.add(fb)
    await db.commit()

    return {"id": str(fb.id), "message": "Feedback enregistre"}


@router.get("/dimensions")
async def get_dimensions_config(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retourne la configuration des 5 dimensions de scoring."""
    await FeatureFlagService.check_feature(db, "scoring_v2", _get_tenant_tier(current_user))

    engine = ScoringEngine()
    return {
        "dimensions": engine.config["dimensions"],
        "profile_weights": engine.config["profile_weights"],
        "verdict_thresholds": engine.config["verdict_thresholds"],
    }
