"""Scoring Engine V2 — moteur de scoring multi-dimensionnel pour AO."""
import logging
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ao_s2 import AO
from app.models.business_line import BusinessLine
from app.models.scoring import ScoringRun

logger = logging.getLogger(__name__)

YAML_PATH = os.path.join(os.path.dirname(__file__), "dimensions.yaml")


class ScoreCard:
    """Resultat complet du scoring d'un AO."""

    def __init__(self):
        self.score_global: float = 0.0
        self.score_coherence: float = 0.0
        self.score_financiere: float = 0.0
        self.score_geographique: float = 0.0
        self.score_temporelle: float = 0.0
        self.score_concurrentielle: float = 0.0
        self.profile: str = "prudent"
        self.verdict: str = "NO_GO"
        self.confidence: float = 0.0
        self.details: dict = {}
        self.recommendations: list[str] = []
        self.execution_time_ms: int = 0

    def to_dict(self) -> dict:
        return {
            "score_global": round(self.score_global, 2),
            "score_coherence": round(self.score_coherence, 2),
            "score_financiere": round(self.score_financiere, 2),
            "score_geographique": round(self.score_geographique, 2),
            "score_temporelle": round(self.score_temporelle, 2),
            "score_concurrentielle": round(self.score_concurrentielle, 2),
            "profile": self.profile,
            "verdict": self.verdict,
            "confidence": round(self.confidence, 2),
            "details": self.details,
            "recommendations": self.recommendations,
        }


class ScoringEngine:
    """Moteur de scoring V2 — 5 dimensions x 3 profils."""

    def __init__(self):
        self.config = self._load_config()

    def _load_config(self) -> dict:
        with open(YAML_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    async def score_ao(
        self,
        ao: AO,
        profile: str = "prudent",
        db: Optional[AsyncSession] = None,
        business_line: Optional[BusinessLine] = None,
    ) -> ScoreCard:
        start = datetime.now(timezone.utc)
        card = ScoreCard()
        card.profile = profile

        ctx = await self._build_context(ao, db, business_line)

        for dim_name in [
            "coherence",
            "financiere",
            "geographique",
            "temporelle",
            "concurrentielle",
        ]:
            score, explanation = self._eval_dimension(dim_name, profile, ctx)
            setattr(card, f"score_{dim_name}", score)
            card.details[dim_name] = {"score": score, "explanation": explanation}

        weights = self.config["profile_weights"].get(
            profile, self.config["profile_weights"]["prudent"]
        )
        card.score_global = (
            card.score_coherence * weights["coherence"]
            + card.score_financiere * weights["financiere"]
            + card.score_geographique * weights["geographique"]
            + card.score_temporelle * weights["temporelle"]
            + card.score_concurrentielle * weights["concurrentielle"]
        )

        thresholds = self.config["verdict_thresholds"]
        if card.score_global >= thresholds["GO"]:
            card.verdict = "GO"
        elif card.score_global >= thresholds["MAYBE"]:
            card.verdict = "MAYBE"
        else:
            card.verdict = "NO_GO"

        card.confidence = self._compute_confidence(card, ctx)
        card.recommendations = self._generate_recommendations(card, ctx)
        card.execution_time_ms = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
        return card

    async def _build_context(
        self, ao: AO, db: Optional[AsyncSession], bl: Optional[BusinessLine]
    ) -> dict:
        ctx = {
            "cpv_codes": ao.cpv_codes or [],
            "cpv_match": False,
            "keyword_match": False,
            "amount": float(ao.estimated_amount) if ao.estimated_amount else None,
            "dept_code": ao.department_code,
            "region": ao.region,
            "country": ao.country,
            "user_departments": [ao.department_code] if ao.department_code else [],
            "user_region": ao.region,
            "user_country": ao.country,
            "days_to_deadline": None,
            "notice_type": ao.notice_type or "appel_offre_ouvert",
        }

        if ao.deadline_date:
            delta = ao.deadline_date - datetime.now(timezone.utc)
            ctx["days_to_deadline"] = max(0, delta.days)

        if bl and ao.cpv_codes:
            bl_cpv_codes = set(bl.cpv_keywords or [])
            ao_cpv_codes = set(ao.cpv_codes or [])
            if bl_cpv_codes & ao_cpv_codes:
                ctx["cpv_match"] = True

            title_lower = (ao.title or "").lower()
            desc_lower = (ao.description or "").lower()
            for kw in bl.free_text_keywords or []:
                if kw.lower() in title_lower or kw.lower() in desc_lower:
                    ctx["keyword_match"] = True
                    break

        if ao.department_code and ao.country == "FR":
            ctx["adjacent_departments"] = self._get_adjacent_departments(ao.department_code)
        else:
            ctx["adjacent_departments"] = []

        return ctx

    def _eval_dimension(self, dim_name: str, profile: str, ctx: dict) -> tuple[float, str]:
        dim_config = self.config["dimensions"][dim_name]
        rules = dim_config["profiles"].get(profile, [])
        default_score = dim_config.get("default_score", 5.0)

        for rule in rules:
            try:
                if eval(rule["condition"], {"__builtins__": {}}, ctx):
                    return float(rule["score"]), rule["explanation"]
            except Exception as e:
                logger.warning("[Scoring] Erreur evaluation regle %s/%s: %s", dim_name, profile, e)
                continue

        return float(default_score), "Aucune regle specifique applicable — score par defaut"

    def _compute_confidence(self, card: ScoreCard, ctx: dict) -> float:
        conf = 1.0

        if ctx["amount"] is None:
            conf -= 0.2
        if ctx["days_to_deadline"] is None:
            conf -= 0.2
        if not ctx["cpv_codes"]:
            conf -= 0.15
        if ctx["dept_code"] is None:
            conf -= 0.1

        scores = [
            card.score_coherence,
            card.score_financiere,
            card.score_geographique,
            card.score_temporelle,
            card.score_concurrentielle,
        ]
        variance = sum((s - card.score_global) ** 2 for s in scores) / 5
        if variance > 9:
            conf -= 0.15

        return max(0.0, min(1.0, conf))

    def _generate_recommendations(self, card: ScoreCard, ctx: dict) -> list[str]:
        recs = []

        if card.score_financiere < 5:
            recs.append("Preparer caution bancaire ou garantie financiere")
        if card.score_temporelle < 5 and ctx.get("days_to_deadline", 999) < 14:
            recs.append(f"Deadline dans {ctx['days_to_deadline']} jours — agir immediatement")
        if card.score_geographique < 5:
            recs.append("Envisager un partenariat local ou co-traitance")
        if card.score_coherence < 5:
            recs.append("Verifier alignment metier — risque de non-qualification technique")
        if card.score_concurrentielle < 5:
            recs.append("AO ouvert avec forte concurrence — differencier sur la valeur technique")
        if card.verdict == "GO" and card.score_global >= 8:
            recs.append("AO hautement recommande — prioriser la preparation du dossier")

        return recs

    def _get_adjacent_departments(self, dept_code: str) -> list[str]:
        adjacency = {
            "01": ["69", "38", "73", "74"],
            "02": ["59", "62", "80", "60"],
            "03": ["63", "42", "43", "71", "58", "18"],
            "04": ["83", "06", "05", "38", "26"],
            "05": ["26", "04", "83"],
            "06": ["83", "04"],
            "07": ["43", "30", "26", "38"],
            "08": ["55", "51", "02"],
            "09": ["31", "11", "66"],
            "10": ["51", "77", "89", "21"],
            "11": ["66", "09", "31", "81"],
            "12": ["48", "34", "81", "15", "63"],
            "13": ["84", "30", "83"],
            "14": ["27", "76", "50", "61"],
            "15": ["12", "63", "43", "48", "19"],
            "16": ["17", "24", "87", "19", "86"],
            "17": ["85", "44", "49", "79", "16"],
            "18": ["45", "58", "71", "03", "23"],
            "19": ["87", "16", "24", "46", "15", "63"],
            "21": ["10", "89", "71", "58", "52", "70"],
            "22": ["56", "35", "29", "50"],
            "23": ["87", "36", "18", "03", "63"],
            "24": ["33", "47", "46", "19", "16"],
            "25": ["90", "70", "39", "71", "01"],
            "26": ["07", "38", "05", "04", "84", "30"],
            "27": ["76", "78", "28", "61", "45", "14"],
            "28": ["27", "78", "91", "45"],
            "29": ["56", "22", "50"],
            "30": ["34", "48", "13", "84", "26", "07"],
            "31": ["81", "82", "32", "09", "11", "65"],
            "32": ["65", "31", "82", "40", "47", "46"],
            "33": ["47", "24", "40", "17", "16"],
            "34": ["30", "11", "81", "12", "48"],
            "35": ["56", "22", "50", "53"],
            "36": ["87", "23", "18", "37", "41", "86"],
            "37": ["45", "41", "36", "86", "49"],
            "38": ["01", "73", "26", "07", "43", "42", "69"],
            "39": ["25", "70", "71"],
            "40": ["47", "33", "64"],
            "41": ["37", "45", "28", "72"],
            "42": ["69", "38", "43", "07"],
            "43": ["63", "15", "48", "07", "42", "38"],
            "44": ["49", "85", "17", "56", "35", "22"],
            "45": ["18", "58", "89", "77", "91", "28", "41", "37"],
            "46": ["47", "24", "19", "82", "15"],
            "47": ["32", "82", "46", "24", "33", "40"],
            "48": ["12", "15", "43", "07", "30", "34"],
            "49": ["53", "72", "37", "86", "79", "44", "85"],
            "50": ["14", "61", "29", "22", "35"],
            "51": ["08", "55", "77", "89", "10", "02"],
            "52": ["55", "21", "70", "88"],
            "53": ["35", "49", "72", "61"],
            "54": ["57", "55", "88", "67"],
            "55": ["08", "51", "77", "54", "57", "88", "52"],
            "56": ["35", "22", "29", "44"],
            "57": ["54", "55", "67"],
            "58": ["71", "03", "18", "45", "89"],
            "59": ["62", "80", "02"],
            "60": ["80", "02", "77", "95", "91", "27", "76"],
            "61": ["14", "27", "53", "72"],
            "62": ["59", "80", "02"],
            "63": ["03", "43", "15", "19", "23", "42"],
            "64": ["40", "33", "65", "32"],
            "65": ["64", "32", "31", "09"],
            "66": ["11", "09"],
            "67": ["57", "68", "88"],
            "68": ["67", "88"],
            "69": ["01", "38", "42", "71"],
            "70": ["25", "90", "39", "52", "88", "21"],
            "71": ["69", "01", "39", "58", "03", "42"],
            "72": ["61", "53", "49", "41", "28"],
            "73": ["74", "38", "01"],
            "74": ["73", "01"],
            "75": ["92", "93", "94", "95", "77", "78", "91"],
            "76": ["27", "14", "60"],
            "77": ["91", "45", "89", "51", "55", "93", "94", "60"],
            "78": ["27", "91", "95", "92"],
            "79": ["86", "49", "44", "17", "16"],
            "80": ["62", "59", "02", "60"],
            "81": ["34", "11", "31", "82", "12"],
            "82": ["81", "31", "32", "46", "47"],
            "83": ["13", "06", "04", "84"],
            "84": ["30", "26", "04", "83", "13"],
            "85": ["44", "49", "79", "17"],
            "86": ["36", "37", "49", "79", "16"],
            "87": ["23", "36", "19", "16"],
            "88": ["55", "54", "57", "67", "68", "70", "52"],
            "89": ["21", "58", "45", "77", "10"],
            "90": ["25", "70"],
            "91": ["28", "45", "77", "78", "92", "93", "94", "95"],
            "92": ["75", "78", "91", "93", "94", "95"],
            "93": ["75", "77", "91", "92", "94", "95"],
            "94": ["75", "77", "91", "92", "93"],
            "95": ["75", "77", "78", "91", "92", "93", "60"],
        }
        return adjacency.get(dept_code, [])

    async def score_and_save(
        self,
        ao_id: str,
        profile: str,
        db: AsyncSession,
        triggered_by: str = "auto",
    ) -> ScoringRun:
        stmt = select(AO).where(AO.id == ao_id)
        row = await db.execute(stmt)
        ao = row.scalar_one_or_none()
        if not ao:
            raise ValueError(f"AO {ao_id} introuvable")

        bl = None
        if ao.business_line_id:
            stmt_bl = select(BusinessLine).where(BusinessLine.id == ao.business_line_id)
            row_bl = await db.execute(stmt_bl)
            bl = row_bl.scalar_one_or_none()

        card = await self.score_ao(ao, profile=profile, db=db, business_line=bl)

        scoring_run = ScoringRun(
            ao_id=ao.id,
            profile=profile,
            score_global=Decimal(str(card.score_global)),
            score_coherence=Decimal(str(card.score_coherence)),
            score_financiere=Decimal(str(card.score_financiere)),
            score_geographique=Decimal(str(card.score_geographique)),
            score_temporelle=Decimal(str(card.score_temporelle)),
            score_concurrentielle=Decimal(str(card.score_concurrentielle)),
            verdict=card.verdict,
            confidence=Decimal(str(card.confidence)),
            details=card.details,
            recommendations=card.recommendations,
            triggered_by=triggered_by,
            execution_time_ms=card.execution_time_ms,
        )
        db.add(scoring_run)

        ao.scoring_result = card.to_dict()
        ao.status = "scored"
        await db.commit()
        await db.refresh(scoring_run)

        logger.info(
            "[Scoring] AO %s → %s (%.1f) en %sms",
            ao_id,
            card.verdict,
            card.score_global,
            card.execution_time_ms,
        )
        return scoring_run
