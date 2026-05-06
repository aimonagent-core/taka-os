"""Detection d'anomalies par l'Agent Auditor."""

import logging
import statistics
from datetime import datetime, timezone, timedelta
from typing import Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.audit import AnomalyDetection, AnomalySeverity, AnomalyStatus, AuditTrail

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Detecteur d'anomalies pour TAKA OS."""

    SCORE_Z_THRESHOLD = 2.5
    SUBMISSION_FAILURE_THRESHOLD = 0.3
    ACTIVITY_OUTLIER_THRESHOLD = 3.0
    CREDENTIAL_EXPIRY_DAYS = 30

    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_scoring_bias(
        self,
        tenant_id: uuid.UUID,
        ao_id: uuid.UUID,
        score_value: Optional[float] = None,
    ) -> list[AnomalyDetection]:
        """Detecte les biais dans les scores attribues a un AO."""
        anomalies = []
        from_date = datetime.now(timezone.utc) - timedelta(days=30)

        stmt = (
            select(AuditTrail)
            .where(
                and_(
                    AuditTrail.tenant_id == tenant_id,
                    AuditTrail.action_category == "scoring",
                    AuditTrail.action == "ao_scored",
                    AuditTrail.created_at >= from_date,
                )
            )
            .order_by(AuditTrail.created_at.desc())
        )
        result = await self.db.execute(stmt)
        scoring_logs = result.scalars().all()

        if len(scoring_logs) < 5:
            return anomalies

        scores = []
        for log in scoring_logs:
            if log.after_state and "score" in log.after_state:
                try:
                    scores.append(float(log.after_state["score"]))
                except (ValueError, TypeError):
                    continue

        if len(scores) < 5:
            return anomalies

        if score_value is not None:
            if score_value > 95:
                anomalies.append(
                    AnomalyDetection(
                        tenant_id=tenant_id,
                        detected_by="rule_engine",
                        anomaly_type="scoring_bias",
                        severity=AnomalySeverity.MEDIUM,
                        title="Score exceptionnellement eleve",
                        description=f"Score de {score_value}% attribue — bien au-dessus de la moyenne du tenant ({statistics.mean(scores):.1f}%)",
                        affected_resource_type="ao",
                        affected_resource_id=ao_id,
                        detection_data={
                            "score": score_value,
                            "tenant_avg": statistics.mean(scores),
                            "tenant_std": statistics.stdev(scores) if len(scores) > 1 else 0,
                            "historical_scores": scores[:50],
                        },
                    )
                )
            elif score_value < 15:
                anomalies.append(
                    AnomalyDetection(
                        tenant_id=tenant_id,
                        detected_by="rule_engine",
                        anomaly_type="scoring_bias",
                        severity=AnomalySeverity.LOW,
                        title="Score exceptionnellement bas",
                        description=f"Score de {score_value}% — bien en-dessous de la moyenne",
                        affected_resource_type="ao",
                        affected_resource_id=ao_id,
                        detection_data={"score": score_value, "tenant_avg": statistics.mean(scores)},
                    )
                )

        user_scores: dict[uuid.UUID, list[float]] = {}
        for log in scoring_logs:
            if log.actor_id and log.after_state and "score" in log.after_state:
                uid = log.actor_id
                if uid not in user_scores:
                    user_scores[uid] = []
                try:
                    user_scores[uid].append(float(log.after_state["score"]))
                except (ValueError, TypeError):
                    continue

        for user_id, user_score_list in user_scores.items():
            if len(user_score_list) >= 5:
                user_std = statistics.stdev(user_score_list)
                if user_std > 40:
                    anomalies.append(
                        AnomalyDetection(
                            tenant_id=tenant_id,
                            detected_by="rule_engine",
                            anomaly_type="scoring_bias",
                            severity=AnomalySeverity.HIGH,
                            title="Variance de scoring excessive",
                            description=f"Utilisateur {user_id} a un ecart-type de {user_std:.1f} sur {len(user_score_list)} scores — indique potentiellement un biais",
                            affected_resource_type="user",
                            affected_resource_id=user_id,
                            detection_data={
                                "user_std": user_std,
                                "score_count": len(user_score_list),
                                "score_range": [min(user_score_list), max(user_score_list)],
                            },
                        )
                    )

        return anomalies

    async def check_user_activity(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> list[AnomalyDetection]:
        """Detecte une activite inhabituelle pour un utilisateur."""
        anomalies = []
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)

        stmt = (
            select(func.count(AuditTrail.id))
            .where(
                and_(
                    AuditTrail.tenant_id == tenant_id,
                    AuditTrail.actor_id == user_id,
                    AuditTrail.actor_type == "user",
                    AuditTrail.created_at >= one_hour_ago,
                )
            )
        )
        result = await self.db.execute(stmt)
        recent_count = result.scalar()

        if recent_count > 100:
            anomalies.append(
                AnomalyDetection(
                    tenant_id=tenant_id,
                    detected_by="rule_engine",
                    anomaly_type="unusual_activity",
                    severity=AnomalySeverity.HIGH,
                    title="Activite inhabituellement intense",
                    description=f"{recent_count} actions en 1 heure — possible usage automatise",
                    affected_resource_type="user",
                    affected_resource_id=user_id,
                    detection_data={"actions_last_hour": recent_count, "threshold": 100},
                )
            )

        return anomalies

    async def check_submission_failures(
        self,
        tenant_id: uuid.UUID,
    ) -> list[AnomalyDetection]:
        """Detecte une augmentation soudaine des echecs de soumission."""
        anomalies = []
        from_date = datetime.now(timezone.utc) - timedelta(hours=24)

        total_stmt = (
            select(func.count(AuditTrail.id))
            .where(
                and_(
                    AuditTrail.tenant_id == tenant_id,
                    AuditTrail.action_category == "submission",
                    AuditTrail.created_at >= from_date,
                )
            )
        )
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar()

        if total < 3:
            return anomalies

        failed_stmt = (
            select(func.count(AuditTrail.id))
            .where(
                and_(
                    AuditTrail.tenant_id == tenant_id,
                    AuditTrail.action_category == "submission",
                    AuditTrail.action == "submission_failed",
                    AuditTrail.created_at >= from_date,
                )
            )
        )
        failed_result = await self.db.execute(failed_stmt)
        failed = failed_result.scalar()

        failure_rate = failed / total if total > 0 else 0

        if failure_rate > self.SUBMISSION_FAILURE_THRESHOLD:
            anomalies.append(
                AnomalyDetection(
                    tenant_id=tenant_id,
                    detected_by="rule_engine",
                    anomaly_type="submission_failure_spike",
                    severity=AnomalySeverity.HIGH if failure_rate > 0.5 else AnomalySeverity.MEDIUM,
                    title=f"Spike d'echecs de soumission ({failure_rate*100:.0f}%)",
                    description=f"{failed} echecs sur {total} soumissions en 24h — verifiez vos credentials plateforme",
                    detection_data={"failed": failed, "total": total, "rate": failure_rate},
                )
            )

        return anomalies

    async def check_credential_expiry(
        self,
        tenant_id: uuid.UUID,
    ) -> list[AnomalyDetection]:
        """Detecte les credentials plateforme proches de l'expiration."""
        anomalies = []

        from app.models.audit import PlatformCredential

        alert_date = datetime.now(timezone.utc) + timedelta(days=self.CREDENTIAL_EXPIRY_DAYS)

        stmt = (
            select(PlatformCredential)
            .where(
                and_(
                    PlatformCredential.tenant_id == tenant_id,
                    PlatformCredential.is_active == True,
                    PlatformCredential.expires_at <= alert_date,
                )
            )
        )
        result = await self.db.execute(stmt)
        expiring_creds = result.scalars().all()

        for cred in expiring_creds:
            days_remaining = (cred.expires_at - datetime.now(timezone.utc)).days if cred.expires_at else 0
            severity = (
                AnomalySeverity.CRITICAL if days_remaining <= 7
                else AnomalySeverity.HIGH if days_remaining <= 14
                else AnomalySeverity.MEDIUM
            )

            anomalies.append(
                AnomalyDetection(
                    tenant_id=tenant_id,
                    detected_by="rule_engine",
                    anomaly_type="credential_expiry",
                    severity=severity,
                    title=f"Credentials {cred.platform_type} expirent bientot",
                    description=f"Credentials pour {cred.platform_name or cred.platform_type} expirent dans {days_remaining} jours",
                    affected_resource_type="config",
                    detection_data={
                        "platform_type": cred.platform_type,
                        "platform_name": cred.platform_name,
                        "expires_at": cred.expires_at.isoformat() if cred.expires_at else None,
                        "days_remaining": days_remaining,
                    },
                )
            )

        return anomalies

    async def check_data_quality(
        self,
        tenant_id: uuid.UUID,
    ) -> list[AnomalyDetection]:
        """Detecte les problemes de qualite des donnees AO."""
        anomalies = []

        from app.models.ao import AO
        from sqlalchemy import or_

        stmt = (
            select(func.count(AO.id))
            .where(
                and_(
                    AO.tenant_id == tenant_id,
                    or_(AO.description == None, func.length(AO.description) < 50),
                )
            )
        )
        result = await self.db.execute(stmt)
        short_desc_count = result.scalar()

        if short_desc_count > 10:
            anomalies.append(
                AnomalyDetection(
                    tenant_id=tenant_id,
                    detected_by="rule_engine",
                    anomaly_type="data_quality",
                    severity=AnomalySeverity.LOW,
                    title=f"{short_desc_count} AO avec description insuffisante",
                    description="Des AO ont une description vide ou trop courte — le scoring et la generation de reponses seront degrades",
                    detection_data={"ao_with_short_description": short_desc_count, "threshold": 50},
                )
            )

        return anomalies

    async def analyze_with_ai(
        self,
        tenant_id: uuid.UUID,
        anomaly: AnomalyDetection,
    ) -> AnomalyDetection:
        """Enrichit une anomalie avec une analyse Mistral."""
        try:
            from app.services.llm.mistral_client import MistralAIClient

            client = MistralAIClient()

            prompt = f"""Tu es un expert en audit et conformite des marches publics.

Anomalie detectee :
- Type : {anomaly.anomaly_type}
- Titre : {anomaly.title}
- Description : {anomaly.description}
- Donnees : {anomaly.detection_data}

Analyse cette anomalie et fournis :
1. Une analyse de la cause probable (2-3 phrases)
2. Une recommandation d'action concrete
3. Un niveau de risque (LOW / MEDIUM / HIGH / CRITICAL)

Reponds en JSON :
{{"analysis": "...", "recommendation": "...", "risk_level": "..."}}"""

            response = await client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )

            import json
            content = response["choices"][0]["message"]["content"]
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            ai_result = json.loads(content.strip())

            anomaly.ai_analysis = ai_result.get("analysis", "")
            anomaly.ai_recommendation = ai_result.get("recommendation", "")

            ai_risk = ai_result.get("risk_level", "").upper()
            if ai_risk == "CRITICAL" and anomaly.severity != AnomalySeverity.CRITICAL:
                anomaly.severity = AnomalySeverity.CRITICAL

        except Exception as e:
            logger.warning(f"Anomaly AI analysis failed: {e}")
            anomaly.ai_analysis = None
            anomaly.ai_recommendation = None

        return anomaly

    async def run_all_checks(self, tenant_id: uuid.UUID) -> list[AnomalyDetection]:
        """Execute toutes les verifications de detection."""
        all_anomalies: list[AnomalyDetection] = []

        all_anomalies.extend(await self.check_submission_failures(tenant_id))
        all_anomalies.extend(await self.check_credential_expiry(tenant_id))
        all_anomalies.extend(await self.check_data_quality(tenant_id))

        for anomaly in all_anomalies:
            if anomaly.severity in (AnomalySeverity.HIGH, AnomalySeverity.CRITICAL):
                await self.analyze_with_ai(tenant_id, anomaly)

        for anomaly in all_anomalies:
            existing = await self._find_similar_open_anomaly(anomaly)
            if not existing:
                self.db.add(anomaly)
                logger.info(f"Anomaly detected: {anomaly.title} ({anomaly.severity.value})")

        await self.db.flush()
        return all_anomalies

    async def _find_similar_open_anomaly(
        self,
        anomaly: AnomalyDetection,
    ) -> Optional[AnomalyDetection]:
        """Verifie si une anomalie similaire existe deja en statut OPEN."""
        stmt = (
            select(AnomalyDetection)
            .where(
                and_(
                    AnomalyDetection.tenant_id == anomaly.tenant_id,
                    AnomalyDetection.anomaly_type == anomaly.anomaly_type,
                    AnomalyDetection.affected_resource_id == anomaly.affected_resource_id,
                    AnomalyDetection.status == AnomalyStatus.OPEN,
                )
            )
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
