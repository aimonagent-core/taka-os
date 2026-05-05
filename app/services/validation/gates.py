# File: app/services/validation/gates.py
# Purpose: N-gates validation pipeline adapted to existing ValidationAudit model
# Dependencies: datetime, structlog, app.models.ao

import enum
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ao import ValidationAudit

logger = logging.getLogger(__name__)


class GateName(str, enum.Enum):
    COMPLETENESS = "completeness"
    FRESHNESS = "freshness"
    CONSISTENCY = "consistency"
    QUALITY = "quality"
    COMPLIANCE = "compliance"
    VALUE = "value"


@dataclass
class GateResult:
    gate: GateName
    passed: bool
    score: float
    threshold: float
    details: dict[str, Any] = field(default_factory=dict)
    retryable: bool = False


@dataclass
class ValidationResult:
    document_id: UUID
    overall_passed: bool = False
    overall_score: float = 0.0
    gate_results: list[GateResult] = field(default_factory=list)
    status: str = "pending"
    retryable: bool = False


class GateRegistry:
    _gates: dict[GateName, "Gate"] = {}

    @classmethod
    def register(cls, gate: "Gate") -> None:
        cls._gates[gate.name] = gate

    @classmethod
    def get(cls, name: GateName) -> "Gate":
        return cls._gates[name]

    @classmethod
    def all_gates(cls) -> list["Gate"]:
        return list(cls._gates.values())


class Gate:
    name: GateName
    threshold: float = 0.7
    weight: float = 1.0

    def __init_subclass__(cls) -> None:
        if hasattr(cls, "name"):
            GateRegistry.register(cls())

    async def evaluate(
        self, document_data: dict[str, Any], context: dict[str, Any]
    ) -> GateResult:
        raise NotImplementedError


class CompletenessGate(Gate):
    name = GateName.COMPLETENESS
    threshold = 0.6

    REQUIRED_FIELDS: list[str] = ["title", "description", "amount", "deadline"]

    async def evaluate(
        self, document_data: dict[str, Any], context: dict[str, Any]
    ) -> GateResult:
        present = sum(1 for f in self.REQUIRED_FIELDS if document_data.get(f))
        score = present / len(self.REQUIRED_FIELDS)
        missing = [f for f in self.REQUIRED_FIELDS if not document_data.get(f)]
        return GateResult(
            gate=self.name,
            passed=score >= self.threshold,
            score=score,
            threshold=self.threshold,
            details={"missing_fields": missing, "present_count": present},
            retryable=bool(missing),
        )


class FreshnessGate(Gate):
    name = GateName.FRESHNESS
    threshold = 0.8

    async def evaluate(
        self, document_data: dict[str, Any], context: dict[str, Any]
    ) -> GateResult:
        deadline = document_data.get("deadline")
        if not deadline:
            return GateResult(
                gate=self.name, passed=False, score=0.0, threshold=self.threshold,
                details={"error": "no_deadline"}, retryable=False,
            )
        now = datetime.utcnow().date()
        if isinstance(deadline, str):
            from datetime import date as dt_date
            try:
                deadline = dt_date.fromisoformat(deadline)
            except ValueError:
                return GateResult(
                    gate=self.name, passed=False, score=0.0, threshold=self.threshold,
                    details={"error": "invalid_deadline_format"}, retryable=False,
                )
        days_remaining = (deadline - now).days
        score = max(0.0, min(1.0, days_remaining / 30.0))
        return GateResult(
            gate=self.name,
            passed=score >= self.threshold,
            score=score,
            threshold=self.threshold,
            details={"days_remaining": days_remaining},
            retryable=False,
        )


class ConsistencyGate(Gate):
    name = GateName.CONSISTENCY
    threshold = 0.75

    async def evaluate(
        self, document_data: dict[str, Any], context: dict[str, Any]
    ) -> GateResult:
        amount = document_data.get("amount")
        text = document_data.get("raw_text", "")
        if not amount or not text:
            return GateResult(
                gate=self.name, passed=False, score=0.0, threshold=self.threshold,
                details={"error": "missing_data"}, retryable=True,
            )
        amount_str = str(int(amount))
        found_in_text = amount_str.replace(" ", "") in text.replace(" ", "")
        score = 1.0 if found_in_text else 0.5
        return GateResult(
            gate=self.name,
            passed=score >= self.threshold,
            score=score,
            threshold=self.threshold,
            details={"amount_found_in_text": found_in_text},
            retryable=not found_in_text,
        )


class QualityGate(Gate):
    name = GateName.QUALITY
    threshold = 0.65

    async def evaluate(
        self, document_data: dict[str, Any], context: dict[str, Any]
    ) -> GateResult:
        text = document_data.get("raw_text", "")
        word_count = len(text.split())
        if word_count < 50:
            score = 0.2
        elif word_count < 200:
            score = 0.5
        elif word_count < 500:
            score = 0.8
        else:
            score = 1.0
        return GateResult(
            gate=self.name,
            passed=score >= self.threshold,
            score=score,
            threshold=self.threshold,
            details={"word_count": word_count},
            retryable=score < 0.5,
        )


class ComplianceGate(Gate):
    name = GateName.COMPLIANCE
    threshold = 0.5

    KEYWORDS: list[str] = ["rgpd", "cnil", "loi", "reglement", "directive", "article"]

    async def evaluate(
        self, document_data: dict[str, Any], context: dict[str, Any]
    ) -> GateResult:
        text = document_data.get("raw_text", "").lower()
        matches = [kw for kw in self.KEYWORDS if kw in text]
        score = min(len(matches) / 2.0, 1.0)
        return GateResult(
            gate=self.name,
            passed=score >= self.threshold,
            score=score,
            threshold=self.threshold,
            details={"matched_keywords": matches},
            retryable=len(matches) == 0,
        )


class ValueGate(Gate):
    name = GateName.VALUE
    threshold = 0.6

    async def evaluate(
        self, document_data: dict[str, Any], context: dict[str, Any]
    ) -> GateResult:
        amount = document_data.get("amount")
        if amount is None:
            return GateResult(
                gate=self.name, passed=False, score=0.0, threshold=self.threshold,
                details={"error": "no_amount"}, retryable=True,
            )
        score = 0.3
        if amount > 50_000:
            score = 0.6
        if amount > 500_000:
            score = 0.9
        return GateResult(
            gate=self.name,
            passed=score >= self.threshold,
            score=score,
            threshold=self.threshold,
            details={"amount": amount},
            retryable=False,
        )


class ValidationPipeline:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._gates = GateRegistry.all_gates()

    async def validate(
        self, document_data: dict[str, Any], document_id: UUID
    ) -> ValidationResult:
        result = ValidationResult(document_id=document_id)
        total_weight = sum(g.weight for g in self._gates)
        weighted_score = 0.0
        any_retryable = False
        start_time = datetime.utcnow()

        for gate in self._gates:
            gate_start = datetime.utcnow()
            try:
                gate_result = await gate.evaluate(document_data, {})
            except Exception as exc:
                logger.error("gate_error: gate=%s error=%s", gate.name, exc)
                gate_result = GateResult(
                    gate=gate.name,
                    passed=False,
                    score=0.0,
                    threshold=gate.threshold,
                    details={"error": str(exc)},
                    retryable=True,
                )
            result.gate_results.append(gate_result)
            weighted_score += gate_result.score * gate.weight
            if gate_result.retryable:
                any_retryable = True

            gate_time_ms = int((datetime.utcnow() - gate_start).total_seconds() * 1000)
            input_data = json.dumps(document_data, sort_keys=True, default=str)
            output_data = json.dumps(gate_result.details, sort_keys=True, default=str)
            audit = ValidationAudit(
                id=uuid4(),
                request_id=document_id,
                gate_name=gate.name.value,
                input_hash=hashlib.sha256(input_data.encode()).hexdigest(),
                output_hash=hashlib.sha256(output_data.encode()).hexdigest(),
                status="passed" if gate_result.passed else "failed",
                detail={
                    "score": gate_result.score,
                    "threshold": gate_result.threshold,
                    "details": gate_result.details,
                },
                execution_time_ms=gate_time_ms,
            )
            self._db.add(audit)

        result.overall_score = weighted_score / total_weight if total_weight else 0.0
        result.overall_passed = result.overall_score >= 0.7 and all(
            g.passed for g in result.gate_results
        )
        result.retryable = any_retryable and not result.overall_passed
        result.status = "validated" if result.overall_passed else "rejected"

        await self._db.commit()
        logger.info(
            "validation_complete",
            document_id=str(document_id),
            overall_score=result.overall_score,
            passed=result.overall_passed,
        )
        return result
