"""Predictions de probabilite de gain par heuristique + Mistral AI."""
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.ao_s2 import AO
from app.models.scoring import ScoringRun

logger = logging.getLogger(__name__)


class GainPredictor:
    """Predicteur de probabilite de gain."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def predict_for_ao(self, tenant_id: uuid.UUID, ao_id: uuid.UUID) -> dict:
        """Predire la probabilite de gain pour un AO."""
        ao_stmt = select(AO).where(AO.id == ao_id)
        ao_result = await self.db.execute(ao_stmt)
        ao = ao_result.scalar_one_or_none()
        if not ao:
            raise ValueError(f"AO {ao_id} non trouve")

        factors = []

        score_stmt = (
            select(ScoringRun)
            .where(ScoringRun.ao_id == ao_id)
            .order_by(ScoringRun.created_at.desc())
            .limit(1)
        )
        score_result = await self.db.execute(score_stmt)
        latest_score = score_result.scalar_one_or_none()

        score_factor = 0.0
        if latest_score and latest_score.score_global is not None:
            score_normalized = float(latest_score.score_global) / 100.0
            score_factor = score_normalized * 0.30
            factors.append({
                "factor": "Score de correspondance",
                "impact": "positive" if score_normalized > 0.5 else "negative",
                "weight": round(score_factor, 3),
                "detail": f"Score: {latest_score.score_global}/100",
            })

        value_factor = 0.0
        if ao.estimated_amount:
            avg_value = await self._get_avg_ao_value()
            if avg_value and avg_value > 0:
                ratio = float(ao.estimated_amount) / avg_value
                if ratio > 3:
                    value_factor = -0.10
                else:
                    value_factor = 0.05
                factors.append({
                    "factor": "Valeur du marche",
                    "impact": "negative" if ratio > 3 else "positive",
                    "weight": round(value_factor, 3),
                    "detail": f"{float(ao.estimated_amount):,.0f} EUR",
                })

        time_factor = 0.0
        if ao.deadline_date:
            days_remaining = (ao.deadline_date - datetime.now(timezone.utc)).days
            if days_remaining < 3:
                time_factor = -0.20
            elif days_remaining > 30:
                time_factor = 0.10
            factors.append({
                "factor": "Delai restant",
                "impact": "negative" if days_remaining < 3 else "positive",
                "weight": round(time_factor, 3),
                "detail": f"{days_remaining} jours",
            })

        base_probability = 0.15
        total_adjustment = score_factor + value_factor + time_factor
        probability = max(0.0, min(1.0, base_probability + total_adjustment))

        confidence = "high" if len(factors) >= 3 else "medium" if len(factors) >= 2 else "low"
        explanation = await self._generate_explanation(ao, factors)

        return {
            "ao_id": str(ao_id),
            "probability": round(probability, 2),
            "confidence": confidence,
            "factors": factors,
            "explanation": explanation,
        }

    async def _get_avg_ao_value(self) -> Optional[float]:
        stmt = select(func.avg(AO.estimated_amount)).where(
            AO.estimated_amount.isnot(None)
        )
        result = await self.db.execute(stmt)
        val = result.scalar()
        return float(val) if val else None

    async def _generate_explanation(self, ao: AO, factors: list[dict]) -> Optional[str]:
        try:
            from app.services.llm.mistral_client import MistralAIClient
            if len(factors) < 2:
                return None

            client = MistralAIClient()
            factors_text = "\n".join([
                f"- {f['factor']}: {f['impact']}"
                for f in factors
            ])
            prompt = f"""Analyse cette prediction pour un AO :
Titre : {ao.title}
Valeur : {ao.estimated_amount or 'N/A'} EUR
CPV : {ao.cpv_codes or 'N/A'}
Facteurs :
{factors_text}
Resume en 2 phrases en francais."""

            response = await client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=150,
            )
            return response.get("content", "").strip()
        except Exception as e:
            logger.warning(f"Explication prediction failed: {e}")
            return None

    async def predict_batch(self, tenant_id: uuid.UUID, limit: int = 50) -> list[dict]:
        from_date = datetime.now(timezone.utc) - timedelta(days=30)
        stmt = (
            select(AO)
            .where(AO.created_at >= from_date)
            .order_by(AO.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        aos = result.scalars().all()

        predictions = []
        for ao in aos:
            pred = await self.predict_for_ao(tenant_id, ao.id)
            predictions.append(pred)
        return predictions
