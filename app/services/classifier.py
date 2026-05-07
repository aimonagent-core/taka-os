"""Service Sprint 12 — Classification des AO par type de marche.

Déduit le type de marché (Travaux, Services, Fournitures, Concession, Mixte)
à partir des CPV et des mots-clés présents dans le titre/description.
"""

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.procedure_type_mapping import ProcedureTypeMapping

logger = logging.getLogger(__name__)


class AOTypeClassifier:
    """Classifie un AO selon ses CPV et mots-cles pour determiner le type de marche."""

    def __init__(self, db: Optional[AsyncSession] = None) -> None:
        self.db = db
        self._rules: Optional[list[dict]] = None

    async def _load_rules(self) -> list[dict]:
        """Charge les regles de mapping depuis la base (ou cache memoire)."""
        if self._rules is not None:
            return self._rules

        if self.db is None:
            # Fallback : regles hardcodees si pas de session DB
            self._rules = _DEFAULT_RULES
            return self._rules

        stmt = select(ProcedureTypeMapping).order_by(ProcedureTypeMapping.priority.asc())
        rows = await self.db.execute(stmt)
        mappings = rows.scalars().all()

        self._rules = [
            {
                "keywords": [k.lower() for k in m.keywords],
                "cpv_prefixes": m.cpv_prefixes,
                "type_marche": m.type_marche,
                "priority": m.priority,
            }
            for m in mappings
        ]
        return self._rules

    def classify_sync(
        self,
        ao_record: dict[str, any],
    ) -> str:
        """Version synchrone de classify (utilise les regles par defaut)."""
        return self._classify_with_rules(ao_record, _DEFAULT_RULES)

    @staticmethod
    def _classify_with_rules(ao_record: dict[str, any], rules: list[dict]) -> str:
        """Logique de classification avec une liste de regles donnee."""
        cpv_codes = ao_record.get("cpv_codes") or []
        title = (ao_record.get("title") or "").lower()
        description = (ao_record.get("description") or "").lower()
        text = f"{title} {description}"

        matches: list[str] = []

        for rule in rules:
            matched = False

            # 1. Match par prefixe CPV
            if rule.get("cpv_prefixes") and cpv_codes:
                for cpv in cpv_codes:
                    cpv_clean = cpv.replace("-", "").replace(" ", "")
                    for prefix in rule["cpv_prefixes"]:
                        if cpv_clean.startswith(str(prefix)):
                            matches.append(rule["type_marche"])
                            matched = True
                            break
                    if matched:
                        break

            if matched:
                continue

            # 2. Match par mots-cles
            if rule.get("keywords"):
                for kw in rule["keywords"]:
                    if kw in text:
                        matches.append(rule["type_marche"])
                        matched = True
                        break

        if not matches:
            return "Mixte"

        if len(matches) == 1:
            return matches[0]

        if len(set(matches)) == 1:
            return matches[0]

        logger.debug("[Classifier] Ambiguite detectee — matches=%s", matches)
        return "Mixte"

    async def classify(
        self,
        ao_record: dict[str, any],
    ) -> str:
        """Classifie un AO et retourne le type de marche le plus probable.

        Args:
            ao_record: Dict avec au moins 'cpv_codes' (list[str]), 'title' (str),
                       et optionnellement 'description' (str).

        Returns:
            Type de marche : "Travaux", "Services", "Fournitures", "Concession", "Mixte"
        """
        rules = await self._load_rules()
        return self._classify_with_rules(ao_record, rules)


# Regles par defaut (fallback si DB indisponible)
_DEFAULT_RULES: list[dict] = [
    {"keywords": [], "cpv_prefixes": ["45", "71"], "type_marche": "Travaux", "priority": 10},
    {"keywords": [], "cpv_prefixes": ["50", "51"], "type_marche": "Services", "priority": 10},
    {"keywords": [], "cpv_prefixes": [f"{i:02d}" for i in range(30, 40)], "type_marche": "Fournitures", "priority": 10},
    {"keywords": ["concession", "delegation de service public", "dsp", "affermage"], "cpv_prefixes": [], "type_marche": "Concession", "priority": 20},
    {"keywords": ["travaux", "construction", "batiment", "maconnerie", "beton", "gros oeuvre"], "cpv_prefixes": [], "type_marche": "Travaux", "priority": 20},
    {"keywords": ["prestation de service", "etude", "conseil", "expertise", "audit", "formation"], "cpv_prefixes": [], "type_marche": "Services", "priority": 20},
    {"keywords": ["fourniture", "materiel", "equipement", "logiciel", "produit", "achat"], "cpv_prefixes": [], "type_marche": "Fournitures", "priority": 20},
    {"keywords": ["mixte", "travaux et fournitures", "fournitures et services"], "cpv_prefixes": [], "type_marche": "Mixte", "priority": 30},
]
