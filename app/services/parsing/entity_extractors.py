# File: app/services/parsing/entity_extractors.py
# Purpose: Entity extractors: CPV, amounts, deadlines
# Dependencies: re, dateparser, structlog

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Pattern

import dateparser
import logging

logger = logging.getLogger(__name__)

CPV_RE: Pattern = re.compile(r"\b(\d{2,8})(?:\s*[-–—]\s*(\d))?\b")
AMOUNT_RE: Pattern = re.compile(
    r"([0-9]{1,3}(?:\s?[0-9]{3})*(?:[,.][0-9]{1,2})?)\s*\€?\s*(EUR|€|HT|TTC)?",
    re.IGNORECASE,
)
EUROS_KEYWORDS: list[str] = ["montant", "budget", "prix", "caution", "garantie"]


@dataclass
class CPVMatch:
    code: str
    confidence: float
    context: str = ""


@dataclass
class AmountMatch:
    value: Decimal
    currency: str
    type_label: str
    confidence: float
    context: str = ""


@dataclass
class DeadlineMatch:
    date: date
    type_label: str
    confidence: float
    context: str = ""


class CPVExtractor:
    def extract(self, text: str) -> list[CPVMatch]:
        lines = text.split("\n")
        results: list[CPVMatch] = []
        for line in lines:
            for match in CPV_RE.finditer(line):
                code = match.group(1)
                section = match.group(2) or ""
                if not section:
                    code = code[:8].ljust(8, "0")
                else:
                    code = f"{code}{section}"
                conf = 1.0 if 33000000 <= int(code) <= 99999999 else 0.7
                results.append(CPVMatch(code=code, confidence=conf, context=line[:120]))
        return results


class AmountExtractor:
    def extract(self, text: str) -> list[AmountMatch]:
        lines = text.split("\n")
        results: list[AmountMatch] = []
        for line in lines:
            for match in AMOUNT_RE.finditer(line):
                raw_value = match.group(1).replace(" ", "").replace(",", ".")
                try:
                    value = Decimal(raw_value)
                except InvalidOperation:
                    continue
                if value < 500:
                    continue
                if value > 10_000_000_000:
                    continue
                currency = "EUR"
                currency_raw = (match.group(2) or "").upper()
                if "TTC" in currency_raw:
                    pass
                label = self._detect_type(line.lower())
                conf = self._confidence(line.lower(), label)
                results.append(
                    AmountMatch(
                        value=value,
                        currency=currency,
                        type_label=label,
                        confidence=conf,
                        context=line[:120],
                    )
                )
        return results

    def _detect_type(self, lower_line: str) -> str:
        if "caution" in lower_line or "garantie" in lower_line:
            return "caution"
        if "honoraires" in lower_line or "prestations" in lower_line:
            return "honoraires"
        if "budget" in lower_line or "plafond" in lower_line:
            return "budget"
        return "total_estime"

    def _confidence(self, lower_line: str, label: str) -> float:
        base = 0.6
        if any(kw in lower_line for kw in EUROS_KEYWORDS):
            base += 0.3
        if label != "total_estime":
            base += 0.1
        return min(base, 1.0)


class DeadlineExtractor:
    KEYWORDS: list[str] = [
        "date limite",
        "date de remise",
        "date de depot",
        "date de soumission",
        "avant le",
        "au plus tard le",
        "retour des offres",
        "remise des plis",
        "fin de candidature",
        "deadline",
        "closing date",
        "submission date",
    ]

    def extract(self, text: str, base_date: date | None = None) -> list[DeadlineMatch]:
        lines = text.split("\n")
        results: list[DeadlineMatch] = []
        for line in lines:
            for kw in self.KEYWORDS:
                if kw in line.lower():
                    parsed = dateparser.parse(
                        line,
                        languages=["fr", "en"],
                        settings={
                            "RELATIVE_BASE": datetime.combine(
                                base_date or date.today(), datetime.min.time()
                            )
                        },
                    )
                    if parsed:
                        d = parsed.date()
                        conf = 0.9 if re.search(r"\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}", line) else 0.6
                        results.append(
                            DeadlineMatch(
                                date=d,
                                type_label="date_limite",
                                confidence=conf,
                                context=line[:120],
                            )
                        )
                    break
        return results
