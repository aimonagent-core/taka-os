# Specifications Techniques — Scoring Engine V2

## TAKA OS — Moteur de Scoring Parametrique Plugin-Based

**Version:** 2.0.0  
**Date:** 2025-01-20  
**Statut:** Specification technique complete — prete pour implementation Kimi Code  
**Dependances:** Python 3.12+, Pydantic v2, PyYAML, Jinja2  
**Licence:** MIT

---

## Table des matieres

1. [Architecture du moteur](#section-1--architecture-du-moteur)
2. [Classes Python completes](#section-2--classes-python-completes)
3. [Templates YAML des 5 dimensions](#section-3--templates-yaml-des-5-dimensions)
4. [Schema JSON ScoreCard de sortie](#section-4--schema-json-scorecard-de-sortie)
5. [Integration avec l'existant](#section-5--integration-avec-lexistant)
6. [Phasing d'implementation](#section-6--phasing-dimplementation)

---

## SECTION 1 — Architecture du moteur

### 1.1 Vue d'ensemble

Le Scoring Engine V2 est un moteur de scoring parametric plugin-based qui evalue la pertinence d'un Appel d'Offres (AO) pour une entreprise donnee selon 5 dimensions configurables. Chaque dimension est implementee comme un plugin Python independant, configure par un fichier YAML declaratif.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SCORING ENGINE V2                                │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │   Registry   │  │   Balancer   │  │  Explainer   │  │  Feedback   │ │
│  │   (rules)    │  │  (weights)   │  │    (XAI)     │  │   (learn)   │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘ │
│         │                 │                 │                 │        │
│         └─────────────────┴─────────────────┴─────────────────┘        │
│                                   │                                    │
│                    ┌──────────────┴──────────────┐                     │
│                    │      ScoringEngine          │                     │
│                    │      (orchestrateur)        │                     │
│                    └──────────────┬──────────────┘                     │
│                                   │                                    │
│         ┌─────────────────────────┼─────────────────────────┐          │
│         │                         │                         │          │
│  ┌──────┴──────┐  ┌──────────────┴──────────────┐  ┌──────┴──────┐  │
│  │  Dimension  │  │        Dimension            │  │  Dimension  │  │
│  │  Plugin #1  │  │        Plugin #2            │  │  Plugin #N  │  │
│  │(coherence)  │  │   (viabilite_financiere)    │  │   (...)     │  │
│  │  + YAML     │  │        + YAML               │  │   + YAML    │  │
│  └─────────────┘  └─────────────────────────────┘  └─────────────┘  │
│                                                                       │
│  Input:  ao_data (dict) + enterprise_data (dict) + profile (enum)    │
│  Output: ScoreCard (Pydantic model) → JSON serializable              │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Composants principaux

#### 1.2.1 Plugin Architecture

Chaque dimension de scoring est un **plugin** constitue de :

| Composant | Role | Fichier |
|-----------|------|---------|
| Classe Python | Logique d'evaluation, application des regles | `engine.py` — sous-classe de `AbstractDimensionPlugin` |
| Fichier YAML | Regles SI/ALORS, poids par defaut, schema d'entree | `config/scoring_dimensions/{id}.yaml` |
| Sortie | `ScoreBreakdown` — score brut + pondere + explication | Objet Pydantic |

Le moteur charge dynamiquement les plugins depuis le `RuleRegistry` qui lit les fichiers YAML au demarrage.

#### 1.2.2 RuleRegistry

Le `RuleRegistry` est le registre central qui :
- Charge les configurations YAML de chaque dimension
- Indexe les plugins par leur `dimension_id`
- Fournit les `DimensionConfig` au `ScoringEngine`
- Valide la coherence des regles au chargement

#### 1.2.3 ScoreCard

La `ScoreCard` est la **sortie standardisee** du moteur. C'est un modele Pydantic serialisable en JSON qui contient :
- Le score total pondere (0-100)
- Le verdict (`GO`, `MAYBE`, `NO-GO`)
- Le detail par dimension (`ScoreBreakdown`)
- Une explication globale en langage naturel (XAI)
- Les metadonnees (version, timestamp)

#### 1.2.4 FeedbackLoop

La boucle de retroaction permet d'apprendre des corrections manuelles des utilisateurs :
- L'utilisateur peut surclasser (override) le verdict predit
- Le systeme enregistre l'ecart (predicted vs actual)
- Un algorithme d'ajustement corrige les poids et seuils
- Un rapport de precision (accuracy) par dimension est genere

#### 1.2.5 WeightBalancer

Le `WeightBalancer` ajuste dynamiquement les ponderations des dimensions en fonction de l'historique de feedback. Si une dimension accumule les desaccords utilisateur, son poids est reduit automatiquement.

#### 1.2.6 ThresholdManager

Le `ThresholdManager` gere les seuils de decision (`GO` / `MAYBE` / `NO-GO`) par profil de scoring. Trois profils predefinis existent :

| Profil | Seuil GO | Seuil MAYBE | Usage |
|--------|----------|-------------|-------|
| `prudent` | 0.70 | 0.45 | Enterprise risque-averse, forte selectivite |
| `opportuniste` | 0.55 | 0.30 | Enterprise en croissance, accepte plus de risque |
| `specialise` | 0.65 | 0.40 | Enterprise nichee, profil equilibre (defaut) |

### 1.3 Flux de donnees

```
1. Reception requete:  POST /api/v1/tenders/{id}/qualify
                        Body: { "profile": "prudent" }
                        
2. Chargement donnees: ao_data ← tender (DB)
                       enterprise_data ← enterprise (DB)
                       
3. Chargement config:  dimensions ← Registry.load_dimensions(yaml_dir)
                       thresholds ← ThresholdManager.get(profile)
                       weights ← Balancer.balance(profile, feedback)
                       
4. Evaluation:         pour chaque dimension:
                         breakdown = plugin.evaluate(ao_data, enterprise_data)
                         breakdowns.append(breakdown)
                         
5. Aggregation:        total_score = sum(b.weighted_score for b in breakdowns)
                       verdict = threshold.resolve(total_score)
                       
6. Explication:        global_explanation = Explainer.explain(scorecard)
                       
7. Sortie:             ScoreCard → JSON → client
```

### 1.4 Diagramme de classes

```
┌─────────────────────┐         ┌─────────────────────┐
│  <<Protocol>>       │         │  <<Abstract>>       │
│  DimensionPlugin    │◄────────│AbstractDimensionPlugin│
├─────────────────────┤         ├─────────────────────┤
│+ dimension_id: str  │         │+ config: DimensionConfig│
│+ dimension_name: str│         │+ rules: list[Rule]  │
│+ version: str       │         │+ __init__(config)   │
│+ evaluate(...)      │         │+ _load_rules()      │
│+ explain(...)       │         │+ _apply_rules(...)  │
└─────────────────────┘         │+ _eval_condition(...)│
                                │+ _apply_action(...) │
                                │+ evaluate(...) [abs]│
                                └─────────────────────┘
                                         ▲
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
           ┌────────┴────────┐  ┌────────┴────────┐  ┌────────┴────────┐
           │CoherenceMetier  │  │ViabiliteFinanciere│  │  ... (x3)       │
           │Plugin           │  │Plugin             │  │                 │
           └─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 1.5 Principes de conception

1. **Separation des concerns** : Logique d'evaluation (Python) separee de la configuration (YAML)
2. **Open/Closed** : Nouvelle dimension = nouveau YAML + nouvelle classe plugin, sans modifier le moteur
3. **Explicabilite (XAI)** : Chaque score est explique par les regles declenchees, en langage naturel
4. **Testabilite** : Chaque plugin est testable independamment avec des donnees mock
5. **Retrocompatibilite** : Le scoring V1 reste accessible via le parametre `?engine=legacy`

---

## SECTION 2 — Classes Python completes

### 2.1 Fichier: `app/core/types/scoring.py`

Fichier de types partages, enumerations et modeles de donnees fondamentaux.

```python
"""Types fondamentaux du Scoring Engine V2.

Ce module definit les enumerations, modeles Pydantic et protocols
utilises par l'ensemble du sous-systeme de scoring.
"""

from __future__ import annotations

import enum
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Literal, Protocol, Self

from pydantic import BaseModel, Field, field_validator, model_validator


# ──────────────────────────────────────────────────────────────
# Enumerations
# ──────────────────────────────────────────────────────────────

class ScoreVerdict(str, enum.Enum):
    """Verdict de scoring — decision finale sur un AO."""

    GO = "GO"
    MAYBE = "MAYBE"
    NO_GO = "NO-GO"


class ScoringProfile(str, enum.Enum):
    """Profil de scoring — determine les seuils et ponderations."""

    PRUDENT = "prudent"
    OPPORTUNISTE = "opportuniste"
    SPECIALISE = "specialise"


# ──────────────────────────────────────────────────────────────
# Modeles de configuration
# ──────────────────────────────────────────────────────────────

class DimensionWeight(BaseModel):
    """Ponderation d'une dimension pour un profil donne.

    Attributes:
        dimension_id: Identifiant unique de la dimension.
        weight: Poids entre 0.0 et 1.0. La somme des poids d'un
            profil doit idealement egaler 1.0.
    """

    dimension_id: str
    weight: float = Field(ge=0.0, le=1.0)

    @field_validator("weight")
    @classmethod
    def _validate_weight(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("weight doit etre compris entre 0.0 et 1.0")
        return v


class ThresholdConfig(BaseModel):
    """Seuils de decision pour un profil de scoring.

    Les seuils doivent respecter l'ordre strict : no_go < maybe < go.
    Les valeurs sont exprimees en pourcentage (0.0 a 1.0).

    Attributes:
        go: Seuil minimum pour un verdict GO (recommande).
        maybe: Seuil minimum pour un verdict MAYBE (a etudier).
        no_go: Seuil maximum pour un verdict NO_GO (defaut 0.0).
    """

    go: float = Field(ge=0.0, le=1.0)
    maybe: float = Field(ge=0.0, le=1.0)
    no_go: float = Field(default=0.0, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def _validate_order(self) -> Self:
        if self.maybe >= self.go:
            raise ValueError(
                f"threshold 'maybe' ({self.maybe}) doit etre strictement "
                f"inferieur a 'go' ({self.go})"
            )
        if self.no_go >= self.maybe:
            raise ValueError(
                f"threshold 'no_go' ({self.no_go}) doit etre strictement "
                f"inferieur a 'maybe' ({self.maybe})"
            )
        return self

    def resolve(self, score: float) -> ScoreVerdict:
        """Resout le verdict en fonction d'un score normalise (0.0-1.0).

        Args:
            score: Score entre 0.0 et 1.0.

        Returns:
            Le verdict correspondant au score.
        """
        if score >= self.go:
            return ScoreVerdict.GO
        if score >= self.maybe:
            return ScoreVerdict.MAYBE
        return ScoreVerdict.NO_GO


class ScoringRule(BaseModel):
    """Regle SI/ALORS pour une dimension de scoring.

    La condition est une expression Python evaluee dans un contexte
    securise. L'action modifie le score courant.

    Attributes:
        condition: Expression Python evaluee comme booleen.
            Exemple: "ao.estimated_amount > enterprise.ca * 0.5"
        action: Operation sur le score. Valeurs supportees:
            "score = X", "score += X", "score -= X", "score *= X"
        score_value: Valeur numerique appliquee par l'action.
        strict: Si True, un declenchement qui mene a score=0 arrete
            l'evaluation des regles suivantes.
        explanation_template: Template Jinja2 pour l'explication.
    """

    condition: str
    action: str
    score_value: float | None = None
    strict: bool = False
    explanation_template: str = "{dimension}: {condition} -> {action}"

    @field_validator("action")
    @classmethod
    def _validate_action(cls, v: str) -> str:
        allowed_prefixes = ("score =", "score +=", "score -=", "score *=")
        if not any(v.startswith(p) for p in allowed_prefixes):
            raise ValueError(
                f"action doit commencer par l'un de: {allowed_prefixes}"
            )
        return v


class DimensionConfig(BaseModel):
    """Configuration YAML d'une dimension de scoring.

    Cette classe est instanciee a partir du fichier YAML de configuration
    de chaque dimension. Elle definit le schema d'entree, les regles et
    les valeurs par defaut.

    Attributes:
        dimension_id: Identifiant unique (snake_case).
        name: Nom d'affichage de la dimension.
        version: Version de la configuration (incrementale).
        input_schema: Liste des chemins de donnees requises.
        rules: Liste des regles SI/ALORS.
        default_score: Score de depart avant application des regles.
        default_weight: Poids par defaut de la dimension.
    """

    dimension_id: str
    name: str
    version: int = 1
    input_schema: list[str]
    rules: list[dict[str, Any]]
    default_score: float = Field(default=50.0, ge=0.0, le=100.0)
    default_weight: float = Field(ge=0.0, le=1.0)

    @field_validator("dimension_id")
    @classmethod
    def _validate_id(cls, v: str) -> str:
        if not v or " " in v:
            raise ValueError("dimension_id ne doit pas contenir d'espaces")
        return v


# ──────────────────────────────────────────────────────────────
# Modeles de sortie (ScoreCard)
# ──────────────────────────────────────────────────────────────

class RuleApplied(BaseModel):
    """Trace d'une regle appliquee lors de l'evaluation.

    Attributes:
        condition: La condition evaluee.
        action: L'action executee.
        result_score: Le score apres application de l'action.
        strict: Indique si la regle etait en mode strict.
    """

    condition: str
    action: str
    result_score: float
    strict: bool


class ScoreBreakdown(BaseModel):
    """Detail du score pour une dimension.

    Attributes:
        dimension_id: Identifiant de la dimension.
        dimension_name: Nom d'affichage.
        raw_score: Score brut (0-100) avant ponderation.
        weighted_score: Score pondere (raw * weight).
        weight: Poids applique (0.0-1.0).
        rules_applied: Liste des regles declenchees.
        explanation: Explication textuelle (XAI).
    """

    dimension_id: str
    dimension_name: str
    raw_score: float = Field(ge=0.0, le=100.0)
    weighted_score: float
    weight: float = Field(ge=0.0, le=1.0)
    rules_applied: list[dict[str, Any]] = Field(default_factory=list)
    explanation: str = ""


class ScoreCard(BaseModel):
    """Resultat complet du scoring — sortie standardisee du moteur.

    C'est l'objet principal retourne par le ScoringEngine. Il est
    serialisable en JSON et contient toutes les informations necessaires
    a la comprehension de la decision (explicabilite).

    Attributes:
        tender_id: UUID de l'AO evalue.
        profile: Profil de scoring utilise.
        total_score: Score total pondere (0-100).
        verdict: Decision finale (GO/MAYBE/NO-GO).
        breakdowns: Detail par dimension.
        global_explanation: Explication synthetique en langage naturel.
        metadata: Metadonnees techniques (version, timestamp, etc.).
        scored_at: Timestamp ISO 8601 de l'evaluation.
        engine_version: Version du moteur de scoring.
    """

    tender_id: str
    profile: ScoringProfile
    total_score: float = Field(ge=0.0, le=100.0)
    verdict: ScoreVerdict
    breakdowns: list[ScoreBreakdown] = Field(default_factory=list)
    global_explanation: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    scored_at: str = ""
    engine_version: str = "2.0.0"

    @model_validator(mode="after")
    def _set_timestamp(self) -> Self:
        if not self.scored_at:
            self.scored_at = datetime.now(timezone.utc).isoformat()
        return self

    def to_json(self) -> str:
        """Serialise la ScoreCard en JSON.

        Returns:
            Chaine JSON formatee.
        """
        return self.model_dump_json(indent=2)

    def to_dict(self) -> dict[str, Any]:
        """Exporte la ScoreCard en dictionnaire.

        Returns:
            Dictionnaire serialisable.
        """
        return self.model_dump(mode="json")


# ──────────────────────────────────────────────────────────────
# Feedback types
# ──────────────────────────────────────────────────────────────

class FeedbackEntry(BaseModel):
    """Entree de feedback utilisateur pour la boucle d'apprentissage.

    Attributes:
        tender_id: UUID de l'AO concerne.
        user_id: UUID de l'utilisateur ayant fait l'override.
        predicted_verdict: Verdict predit par le moteur.
        actual_verdict: Verdict reel choisi par l'utilisateur.
        override_reason: Raison textuelle de l'override.
        dimension_scores: Scores par dimension au moment de la prediction.
        created_at: Timestamp de l'override.
    """

    tender_id: str
    user_id: str
    predicted_verdict: ScoreVerdict
    actual_verdict: ScoreVerdict
    override_reason: str = ""
    dimension_scores: dict[str, float] = Field(default_factory=dict)
    created_at: str = ""

    @model_validator(mode="after")
    def _set_timestamp(self) -> Self:
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        return self


class FeedbackReport(BaseModel):
    """Rapport d'accuracy du scoring par dimension.

    Attributes:
        total_evaluations: Nombre total d'evaluations.
        total_overrides: Nombre total d'overrides.
        override_rate: Taux d'override global.
        accuracy_by_dimension: Precision par dimension.
        suggested_adjustments: Ajustements recommandes.
        generated_at: Timestamp de generation.
    """

    total_evaluations: int
    total_overrides: int
    override_rate: float
    accuracy_by_dimension: dict[str, float]
    suggested_adjustments: dict[str, float]
    generated_at: str = ""

    @model_validator(mode="after")
    def _set_timestamp(self) -> Self:
        if not self.generated_at:
            self.generated_at = datetime.now(timezone.utc).isoformat()
        return self


# ──────────────────────────────────────────────────────────────
# Protocols plugin
# ──────────────────────────────────────────────────────────────

class DimensionPlugin(Protocol):
    """Protocol pour un plugin de dimension de scoring.

    Tout plugin de dimension doit implementer ce protocol pour etre
    compatible avec le ScoringEngine. L'evaluation est asynchrone
    pour permettre les appels externes (LLM, API tierces).
    """

    dimension_id: str
    dimension_name: str
    version: str

    async def evaluate(
        self,
        ao_data: dict[str, Any],
        enterprise_data: dict[str, Any],
    ) -> ScoreBreakdown:
        """Evalue la dimension et retourne un breakdown detaille.

        Args:
            ao_data: Donnees de l'appel d'offres.
            enterprise_data: Donnees de l'entreprise evaluatrice.

        Returns:
            ScoreBreakdown avec score brut, pondere et explication.
        """
        ...

    async def explain(self, breakdown: ScoreBreakdown) -> str:
        """Genere une explication textuelle du breakdown.

        Args:
            breakdown: Le breakdown a expliquer.

        Returns:
            Explication en langage naturel.
        """
        ...
```

---

### 2.2 Fichier: `app/services/scoring/engine.py`

Moteur principal et classe de base abstraite pour les plugins de dimension.

```python
"""Scoring Engine V2 — Moteur de scoring parametrique plugin-based.

Ce module contient le ScoringEngine (orchestrateur central) et la
classe AbstractDimensionPlugin (base de tous les plugins de dimension).

Usage:
    engine = ScoringEngine(registry, threshold_manager, balancer, explainer)
    scorecard = await engine.evaluate(tender_id, ao_data, enterprise_data, profile)
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from app.core.types.scoring import (
    DimensionConfig,
    DimensionPlugin,
    ScoreBreakdown,
    ScoreCard,
    ScoreVerdict,
    ScoringProfile,
    ScoringRule,
)

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# AbstractDimensionPlugin
# ──────────────────────────────────────────────────────────────

class AbstractDimensionPlugin(ABC):
    """Classe de base pour tous les plugins de dimension.

    Cette classe fournit le mecanisme generique d'application des regles
    SI/ALORS depuis la configuration YAML. Les sous-classes doivent
    implementer la methode `evaluate` pour construire le contexte
    specifique a leur dimension.

    Attributes:
        config: Configuration YAML de la dimension.
        rules: Liste des regles chargees depuis le YAML.
    """

    dimension_id: str = ""
    dimension_name: str = ""
    version: str = "1.0.0"

    def __init__(self, config: DimensionConfig) -> None:
        self.config = config
        self.rules: list[ScoringRule] = []
        self._load_rules()

    def _load_rules(self) -> None:
        """Charge et valide les regles depuis la configuration YAML."""
        for rule_data in self.config.rules:
            try:
                rule = ScoringRule(**rule_data)
                self.rules.append(rule)
            except Exception as exc:
                logger.warning(
                    "Regle invalide ignoree dans %s: %s — %s",
                    self.config.dimension_id,
                    rule_data,
                    exc,
                )
        logger.info(
            "%s: %d regles chargees",
            self.config.dimension_id,
            len(self.rules),
        )

    @abstractmethod
    async def evaluate(
        self,
        ao_data: dict[str, Any],
        enterprise_data: dict[str, Any],
    ) -> ScoreBreakdown:
        """Evalue la dimension pour un AO et une entreprise donnes.

        Cette methode doit construire le contexte d'evaluation specifique
        a la dimension, appeler `_apply_rules`, puis construire et
        retourner le ScoreBreakdown.

        Args:
            ao_data: Donnees de l'appel d'offres.
            enterprise_data: Donnees de l'entreprise.

        Returns:
            ScoreBreakdown complet avec score et explication.
        """
        ...

    async def explain(self, breakdown: ScoreBreakdown) -> str:
        """Genere une explication textuelle du breakdown.

        Par defaut, utilise les explanation_template des regles appliquees.
        Peut etre surchargee pour des explications plus sophistiquees.

        Args:
            breakdown: Le breakdown a expliquer.

        Returns:
            Explication en langage naturel.
        """
        explanations = [
            rule["condition"] + " -> " + rule["action"]
            for rule in breakdown.rules_applied
        ]
        if not explanations:
            return (
                f"Aucune regle specifique declenchee pour "
                f"{breakdown.dimension_name}. Score par defaut: "
                f"{breakdown.raw_score:.1f}"
            )
        return f"{breakdown.dimension_name}: " + "; ".join(explanations)

    def _apply_rules(
        self,
        context: dict[str, Any],
    ) -> tuple[float, list[dict[str, Any]]]:
        """Applique les regles SI/ALORS et retourne le score final.

        Le score de depart est `config.default_score`. Chaque regle dont
        la condition est vraie modifie le score selon son action. Si une
        regle `strict` mene a un score de 0, l'evaluation s'arrete.

        Args:
            context: Dictionnaire de variables disponibles pour eval().
                Doit contenir les cles references dans les conditions.

        Returns:
            Tuple (score_final, liste_des_regles_appliquees).
        """
        score = float(self.config.default_score)
        applied: list[dict[str, Any]] = []

        for rule in self.rules:
            try:
                condition_met = self._eval_condition(rule.condition, context)
            except Exception as exc:
                logger.debug(
                    "Condition en erreur (ignoree): %s — %s",
                    rule.condition,
                    exc,
                )
                continue

            if condition_met:
                new_score = self._apply_action(
                    rule.action, rule.score_value, score
                )
                applied.append({
                    "condition": rule.condition,
                    "action": rule.action,
                    "result_score": new_score,
                    "strict": rule.strict,
                })
                score = new_score

                if rule.strict and score <= 0:
                    logger.debug(
                        "Regle stricte a zero le score pour %s",
                        self.config.dimension_id,
                    )
                    break

        return max(0.0, min(100.0, score)), applied

    def _eval_condition(
        self,
        condition: str,
        context: dict[str, Any],
    ) -> bool:
        """Evalue une condition Python dans un contexte securise.

        Le contexte d'evaluation est isole: seules les variables
        explicitement fournies sont accessibles. Aucun builtin Python
        n'est disponible (sandbox).

        Args:
            condition: Expression Python booleenne.
            context: Variables disponibles dans l'expression.

        Returns:
            Resultat booleen de l'evaluation.

        Raises:
            SyntaxError: Si la condition n'est pas une expression valide.
        """
        try:
            result = eval(condition, {"__builtins__": {}}, context)
            return bool(result)
        except Exception:
            raise

    def _apply_action(
        self,
        action: str,
        value: float | None,
        current: float,
    ) -> float:
        """Applique une action sur le score courant.

        Actions supportees:
            - "score = X" : Affectation directe
            - "score += X" : Addition (plafonnee a 100)
            - "score -= X" : Soustraction (plancher a 0)
            - "score *= X" : Multiplication (plafonnee a 100)

        Args:
            action: Chaine d'action (ex: "score += 20").
            value: Valeur numerique a appliquer.
            current: Score courant avant l'action.

        Returns:
            Nouveau score apres l'action.
        """
        if value is None:
            return current

        if action.startswith("score ="):
            return value
        elif action.startswith("score +="):
            return min(100.0, current + value)
        elif action.startswith("score -="):
            return max(0.0, current - value)
        elif action.startswith("score *="):
            return min(100.0, current * value)

        logger.warning("Action non reconnue: %s", action)
        return current


# ──────────────────────────────────────────────────────────────
# ScoringEngine (Orchestrateur)
# ──────────────────────────────────────────────────────────────

class ScoringEngine:
    """Orchestrateur central du moteur de scoring.

    Le ScoringEngine coordonne l'evaluation de toutes les dimensions,
    l'agregation des scores, l'application des seuils et la generation
    des explications. Il est stateless et thread-safe.

    Attributes:
        registry: Registre des dimensions et plugins.
        threshold_manager: Gestionnaire des seuils par profil.
        balancer: Ajusteur dynamique des ponderations.
        explainer: Generateur d'explications XAI.
    """

    def __init__(
        self,
        registry: RuleRegistry,
        threshold_manager: ThresholdManager,
        balancer: WeightBalancer,
        explainer: Explainer,
    ) -> None:
        self.registry = registry
        self.threshold_manager = threshold_manager
        self.balancer = balancer
        self.explainer = explainer

    async def evaluate(
        self,
        tender_id: str,
        ao_data: dict[str, Any],
        enterprise_data: dict[str, Any],
        profile: ScoringProfile = ScoringProfile.SPECIALISE,
    ) -> ScoreCard:
        """Evalue un AO complet et retourne une ScoreCard.

        Cette methode orchestre le pipeline complet:
        1. Charge les dimensions depuis le registry
        2. Ajuste les ponderations via le balancer
        3. Evalue chaque dimension via son plugin
        4. Agrege les scores et applique les seuils
        5. Genere l'explication globale

        Args:
            tender_id: UUID de l'AO.
            ao_data: Donnees de l'appel d'offres.
            enterprise_data: Donnees de l'entreprise.
            profile: Profil de scoring a utiliser.

        Returns:
            ScoreCard complete avec verdict et explications.
        """
        logger.info(
            "Evaluation demarree: tender=%s profile=%s",
            tender_id,
            profile.value,
        )

        # 1. Charger les dimensions et plugins
        dimensions = self.registry.list_dimensions()
        plugins = [
            self.registry.get_plugin(dim_id) for dim_id in dimensions
        ]

        # 2. Recuperer les seuils
        thresholds = self.threshold_manager.get_thresholds(profile)

        # 3. Ajuster les ponderations dynamiquement
        feedback_history = []  # TODO: charger depuis DB
        weights = self.balancer.balance(profile, feedback_history)

        # 4. Evaluer chaque dimension
        breakdowns: list[ScoreBreakdown] = []
        for plugin in plugins:
            try:
                breakdown = await plugin.evaluate(ao_data, enterprise_data)
                # Appliquer le poids ajuste
                dim_weight = weights.get(
                    plugin.dimension_id,
                    plugin.config.default_weight,
                )
                breakdown.weight = dim_weight
                breakdown.weighted_score = (
                    breakdown.raw_score * dim_weight
                )
                breakdown.explanation = await plugin.explain(breakdown)
                breakdowns.append(breakdown)
            except Exception as exc:
                logger.error(
                    "Erreur evaluation %s: %s",
                    plugin.dimension_id,
                    exc,
                    exc_info=True,
                )
                # Dimension en erreur = score nul
                breakdowns.append(
                    ScoreBreakdown(
                        dimension_id=plugin.dimension_id,
                        dimension_name=plugin.dimension_name,
                        raw_score=0.0,
                        weighted_score=0.0,
                        weight=0.0,
                        explanation=f"Erreur: {exc}",
                    )
                )

        # 5. Agreger
        total_score = sum(b.weighted_score for b in breakdowns)
        normalised_score = total_score / 100.0  # 0.0 - 1.0
        verdict = thresholds.resolve(normalised_score)

        # 6. Construire la ScoreCard
        scorecard = ScoreCard(
            tender_id=tender_id,
            profile=profile,
            total_score=total_score,
            verdict=verdict,
            breakdowns=breakdowns,
            metadata={
                "engine_version": "2.0.0",
                "dimensions_count": len(breakdowns),
                "dimensions_evaluated": len([b for b in breakdowns if b.raw_score > 0]),
                "thresholds": {
                    "go": thresholds.go,
                    "maybe": thresholds.maybe,
                },
            },
        )

        # 7. Generer l'explication globale
        scorecard.global_explanation = await self.explainer.explain(
            scorecard, lang="fr"
        )

        logger.info(
            "Evaluation terminee: tender=%s score=%.1f verdict=%s",
            tender_id,
            total_score,
            verdict.value,
        )

        return scorecard

    async def evaluate_single_dimension(
        self,
        dimension_id: str,
        ao_data: dict[str, Any],
        enterprise_data: dict[str, Any],
    ) -> ScoreBreakdown:
        """Evalue une seule dimension (utile pour debug et tests).

        Args:
            dimension_id: Identifiant de la dimension a evaluer.
            ao_data: Donnees de l'AO.
            enterprise_data: Donnees de l'entreprise.

        Returns:
            ScoreBreakdown de la dimension.

        Raises:
            ValueError: Si la dimension n'existe pas.
        """
        plugin = self.registry.get_plugin(dimension_id)
        return await plugin.evaluate(ao_data, enterprise_data)
```


---

### 2.3 Fichier: `app/services/scoring/registry.py`

Registre central des dimensions et plugins de scoring.

```python
"""RuleRegistry — Registre central des dimensions et plugins de scoring.

Charge les configurations YAML depuis le repertoire de dimensions,
instancie les plugins Python associes, et les expose au ScoringEngine.

Usage:
    registry = RuleRegistry()
    registry.load_dimensions("/app/config/scoring_dimensions/")
    plugin = registry.get_plugin("coherence_metier")
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import yaml

from app.core.types.scoring import (
    AbstractDimensionPlugin,
    DimensionConfig,
    DimensionPlugin,
)
from app.services.scoring.plugins import (
    AccessibiliteGeographiquePlugin,
    CoherenceMetierPlugin,
    FaisabiliteTemporellePlugin,
    IntelligenceConcurrentiellePlugin,
    ViabiliteFinancierePlugin,
)

logger = logging.getLogger(__name__)


class RuleRegistry:
    """Registre central des regles et plugins de scoring.

    Le RuleRegistry est responsable de:
    - Charger les fichiers YAML de configuration des dimensions
    - Instancier les plugins Python associes a chaque dimension
    - Fournir un acces unifie aux dimensions et plugins
    - Valider la coherence globale de la configuration

    Attributes:
        _dimensions: Dictionnaire dimension_id -> DimensionConfig
        _plugins: Dictionnaire dimension_id -> DimensionPlugin
        _yaml_dir: Chemin vers le repertoire des fichiers YAML
    """

    # Mapping dimension_id -> classe de plugin
    PLUGIN_MAP: dict[str, type[AbstractDimensionPlugin]] = {
        "coherence_metier": CoherenceMetierPlugin,
        "viabilite_financiere": ViabiliteFinancierePlugin,
        "accessibilite_geographique": AccessibiliteGeographiquePlugin,
        "faisabilite_temporelle": FaisabiliteTemporellePlugin,
        "intelligence_concurrentielle": IntelligenceConcurrentiellePlugin,
    }

    def __init__(self) -> None:
        self._dimensions: dict[str, DimensionConfig] = {}
        self._plugins: dict[str, AbstractDimensionPlugin] = {}
        self._yaml_dir: str = ""

    def load_dimensions(self, yaml_dir: str) -> list[DimensionConfig]:
        """Charge toutes les configurations YAML depuis un repertoire.

        Parcourt le repertoire fourni, charge chaque fichier .yaml,
        cree la DimensionConfig associee et instancie le plugin.

        Args:
            yaml_dir: Chemin absolu vers le repertoire des YAML.

        Returns:
            Liste des configurations chargees.

        Raises:
            FileNotFoundError: Si le repertoire n'existe pas.
        """
        self._yaml_dir = yaml_dir
        path = Path(yaml_dir)

        if not path.exists():
            raise FileNotFoundError(
                f"Repertoire de configuration non trouve: {yaml_dir}"
            )

        configs: list[DimensionConfig] = []
        yaml_files = sorted(path.glob("*.yaml"))

        logger.info(
            "Chargement de %d fichiers YAML depuis %s",
            len(yaml_files),
            yaml_dir,
        )

        for yaml_file in yaml_files:
            try:
                config = self._load_yaml_file(str(yaml_file))
                configs.append(config)
                self._dimensions[config.dimension_id] = config

                # Instancier le plugin associe
                plugin = self._instantiate_plugin(config)
                if plugin:
                    self._plugins[config.dimension_id] = plugin

                logger.info(
                    "Dimension chargee: %s (%s) — %d regles",
                    config.dimension_id,
                    config.name,
                    len(config.rules),
                )
            except Exception as exc:
                logger.error(
                    "Echec chargement %s: %s", yaml_file.name, exc
                )

        self._validate_weights()
        return configs

    def _load_yaml_file(self, file_path: str) -> DimensionConfig:
        """Charge un fichier YAML individuel.

        Args:
            file_path: Chemin absolu vers le fichier YAML.

        Returns:
            DimensionConfig valide.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return DimensionConfig(**data)

    def _instantiate_plugin(
        self, config: DimensionConfig
    ) -> AbstractDimensionPlugin | None:
        """Instancie le plugin Python associe a une dimension.

        Args:
            config: Configuration de la dimension.

        Returns:
            Instance du plugin, ou None si aucun plugin n'est enregistre.
        """
        plugin_class = self.PLUGIN_MAP.get(config.dimension_id)
        if plugin_class is None:
            logger.warning(
                "Aucun plugin enregistre pour la dimension: %s",
                config.dimension_id,
            )
            return None
        return plugin_class(config)

    def _validate_weights(self) -> None:
        """Valide que la somme des poids par defaut est raisonnable.

        Emet un warning si la somme s'eloigne significativement de 1.0.
        """
        total_weight = sum(
            d.default_weight for d in self._dimensions.values()
        )
        if not 0.95 <= total_weight <= 1.05:
            logger.warning(
                "Somme des poids = %.2f (attendu ~1.0). "
                "Verifier la configuration des dimensions.",
                total_weight,
            )

    def get_dimension(self, dimension_id: str) -> DimensionConfig:
        """Retourne la configuration d'une dimension.

        Args:
            dimension_id: Identifiant de la dimension.

        Returns:
            DimensionConfig.

        Raises:
            KeyError: Si la dimension n'existe pas.
        """
        if dimension_id not in self._dimensions:
            raise KeyError(
                f"Dimension inconnue: {dimension_id}. "
                f"Disponibles: {list(self._dimensions.keys())}"
            )
        return self._dimensions[dimension_id]

    def get_plugin(self, dimension_id: str) -> AbstractDimensionPlugin:
        """Retourne l'instance du plugin d'une dimension.

        Args:
            dimension_id: Identifiant de la dimension.

        Returns:
            Instance du plugin pret a evaluer.

        Raises:
            KeyError: Si la dimension ou le plugin n'existe pas.
        """
        if dimension_id not in self._plugins:
            raise KeyError(
                f"Plugin non disponible pour: {dimension_id}"
            )
        return self._plugins[dimension_id]

    def list_dimensions(self) -> list[str]:
        """Liste les identifiants de toutes les dimensions chargees.

        Returns:
            Liste ordonnee des dimension_id.
        """
        return list(self._dimensions.keys())

    def list_plugins(self) -> list[str]:
        """Liste les identifiants des plugins disponibles.

        Returns:
            Liste des dimension_id ayant un plugin instancie.
        """
        return list(self._plugins.keys())

    def register_plugin(
        self,
        dimension_id: str,
        plugin_class: type[AbstractDimensionPlugin],
    ) -> None:
        """Enregistre manuellement une classe de plugin.

        Permet l'extension dynamique du moteur avec de nouvelles
        dimensions sans modifier le code du registry.

        Args:
            dimension_id: Identifiant de la nouvelle dimension.
            plugin_class: Classe heritant de AbstractDimensionPlugin.
        """
        self.PLUGIN_MAP[dimension_id] = plugin_class
        logger.info("Plugin enregistre: %s -> %s", dimension_id, plugin_class.__name__)

    def reload_dimension(self, dimension_id: str) -> DimensionConfig:
        """Recharge une dimension depuis son fichier YAML.

        Utile pour le hot-reload en developpement.

        Args:
            dimension_id: Identifiant de la dimension a recharger.

        Returns:
            Nouvelle configuration chargee.
        """
        yaml_file = Path(self._yaml_dir) / f"{dimension_id}.yaml"
        config = self._load_yaml_file(str(yaml_file))
        self._dimensions[dimension_id] = config
        plugin = self._instantiate_plugin(config)
        if plugin:
            self._plugins[dimension_id] = plugin
        return config

    def get_dimension_count(self) -> int:
        """Retourne le nombre de dimensions chargees.

        Returns:
            Nombre de dimensions.
        """
        return len(self._dimensions)

    def get_rules_summary(self) -> dict[str, int]:
        """Retourne un resume du nombre de regles par dimension.

        Returns:
            Dictionnaire dimension_id -> nombre de regles.
        """
        return {
            dim_id: len(config.rules)
            for dim_id, config in self._dimensions.items()
        }
```

---

### 2.4 Fichier: `app/services/scoring/balancer.py`

Ajusteur dynamique des ponderations base sur le feedback historique.

```python
"""WeightBalancer — Ajusteur dynamique des ponderations de scoring.

Ajuste les poids des dimensions en fonction de l'historique de feedback
utilisateur. Si une dimension accumule les desaccords, son poids est
reduit progressivement.

Usage:
    balancer = WeightBalancer(registry)
    weights = balancer.balance(ScoringProfile.PRUDENT, feedback_history)
"""

from __future__ import annotations

import logging
from typing import Any

from app.core.types.scoring import (
    DimensionConfig,
    FeedbackEntry,
    ScoringProfile,
)
from app.services.scoring.registry import RuleRegistry

logger = logging.getLogger(__name__)


class WeightBalancer:
    """Ajuste les ponderations des dimensions dynamiquement.

    Le balancer analyse l'historique de feedback et ajuste les poids:
    - Si une dimension a >80% de feedback negatif: reduction de 20%
    - Si une dimension a >60% de feedback negatif: reduction de 10%
    - Si une dimension a >80% de feedback positif: augmentation de 10%
    - Les poids sont renormalises pour sommer a 1.0

    Attributes:
        registry: Registre des dimensions (acces aux poids par defaut).
        adjustment_factor: Facteur maximum d'ajustement (defaut: 0.20).
    """

    def __init__(
        self,
        registry: RuleRegistry,
        adjustment_factor: float = 0.20,
    ) -> None:
        self.registry = registry
        self.adjustment_factor = adjustment_factor

    def balance(
        self,
        profile: ScoringProfile,
        feedback_history: list[FeedbackEntry],
    ) -> dict[str, float]:
        """Calcule les poids ajustes pour chaque dimension.

        Args:
            profile: Profil de scoring (influence la strategie d'ajustement).
            feedback_history: Liste des entrees de feedback utilisateur.

        Returns:
            Dictionnaire dimension_id -> poids ajuste (somme = 1.0).
        """
        # Poids par defaut depuis le registry
        base_weights = {
            dim_id: self.registry.get_dimension(dim_id).default_weight
            for dim_id in self.registry.list_dimensions()
        }

        if not feedback_history:
            logger.debug("Aucun feedback — poids par defaut utilises")
            return base_weights

        # Calculer les taux de desaccord par dimension
        disagreement_rates = self._compute_disagreement_rates(
            feedback_history
        )

        # Appliquer les ajustements
        adjusted_weights: dict[str, float] = {}
        for dim_id, base_weight in base_weights.items():
            rate = disagreement_rates.get(dim_id, 0.0)
            adjustment = self._compute_adjustment(rate, profile)
            adjusted_weights[dim_id] = base_weight * (1.0 + adjustment)

        # Renormaliser pour sommer a 1.0
        return self._normalize(adjusted_weights)

    def _compute_disagreement_rates(
        self,
        feedback_history: list[FeedbackEntry],
    ) -> dict[str, float]:
        """Calcule le taux de desaccord par dimension.

        Un desaccord est compte quand l'utilisateur a change le verdict
        predit. On attribue le desaccord a la dimension dont le score
        s'ecarte le plus de la moyenne.

        Args:
            feedback_history: Entrees de feedback.

        Returns:
            Dictionnaire dimension_id -> taux de desaccord (0.0-1.0).
        """
        from collections import defaultdict

        totals: dict[str, int] = defaultdict(int)
        disagreements: dict[str, int] = defaultdict(int)

        for entry in feedback_history:
            for dim_id, score in entry.dimension_scores.items():
                totals[dim_id] += 1
                if entry.predicted_verdict != entry.actual_verdict:
                    disagreements[dim_id] += 1

        return {
            dim_id: (
                disagreements[dim_id] / totals[dim_id]
                if totals[dim_id] > 0
                else 0.0
            )
            for dim_id in totals
        }

    def _compute_adjustment(
        self, disagreement_rate: float, profile: ScoringProfile
    ) -> float:
        """Calcule le facteur d'ajustement pour un taux de desaccord.

        Args:
            disagreement_rate: Taux de desaccord (0.0-1.0).
            profile: Profil de scoring.

        Returns:
            Facteur d'ajustement (positif = augmentation, negatif = reduction).
        """
        # Le profil prudent ajuste plus aggressivement
        multiplier = 1.5 if profile == ScoringProfile.PRUDENT else 1.0

        if disagreement_rate >= 0.80:
            return -self.adjustment_factor * multiplier  # Reduction forte
        elif disagreement_rate >= 0.60:
            return -self.adjustment_factor * 0.5 * multiplier  # Reduction legere
        elif disagreement_rate <= 0.20:
            return self.adjustment_factor * 0.5  # Augmentation legere

        return 0.0  # Pas d'ajustement

    def _normalize(self, weights: dict[str, float]) -> dict[str, float]:
        """Renormalise les poids pour que leur somme egale 1.0.

        Args:
            weights: Poids potentiellement non normalises.

        Returns:
            Poids normalises.
        """
        total = sum(weights.values())
        if total == 0:
            logger.warning("Somme des poids nulle — retour aux poids egaux")
            n = len(weights)
            return {k: 1.0 / n for k in weights}
        return {k: v / total for k, v in weights.items()}

    def get_adjustment_summary(
        self,
        profile: ScoringProfile,
        feedback_history: list[FeedbackEntry],
    ) -> dict[str, Any]:
        """Genere un resume des ajustements effectues.

        Args:
            profile: Profil de scoring.
            feedback_history: Entrees de feedback.

        Returns:
            Dictionnaire avec poids avant/apres et taux de desaccord.
        """
        base_weights = {
            dim_id: self.registry.get_dimension(dim_id).default_weight
            for dim_id in self.registry.list_dimensions()
        }
        adjusted = self.balance(profile, feedback_history)

        return {
            dim_id: {
                "base": base_weights.get(dim_id, 0.0),
                "adjusted": adjusted.get(dim_id, 0.0),
                "delta": adjusted.get(dim_id, 0.0) - base_weights.get(dim_id, 0.0),
            }
            for dim_id in base_weights
        }
```

---

### 2.5 Fichier: `app/services/scoring/explainer.py`

Generateur d'explications XAI (Explainable AI) pour les ScoreCards.

```python
"""Explainer — Generateur d'explications XAI pour le Scoring Engine.

Produit des explications en langage naturel comprehensibles par les
utilisateurs finaux. Chaque explication detaille les facteurs qui ont
conduit au verdict (GO/MAYBE/NO-GO).

Usage:
    explainer = Explainer()
    explanation = await explainer.explain(scorecard, lang="fr")
"""

from __future__ import annotations

import logging
from typing import Any

from jinja2 import BaseLoader, Environment

from app.core.types.scoring import ScoreBreakdown, ScoreCard, ScoreVerdict

logger = logging.getLogger(__name__)

# Templates Jinja2 par verdict
TEMPLATES = {
    "fr": {
        "GO": (
            "L'AO est {{strongly_recommended}} (GO, score {{total_score:.1f}}%) "
            "car : {{reasons}}. Les dimensions fortes sont : {{strengths}}."
        ),
        "MAYBE": (
            "L'AO merite d'etre etudie (MAYBE, score {{total_score:.1f}}%) "
            "car : {{reasons}}. Points d'attention : {{weaknesses}}."
        ),
        "NO-GO": (
            "L'AO n'est pas recommande (NO-GO, score {{total_score:.1f}}%) "
            "car : {{reasons}}. Dimensions bloquantes : {{blockers}}."
        ),
    },
    "en": {
        "GO": (
            "The tender is {{strongly_recommended}} (GO, score {{total_score:.1f}}%) "
            "because: {{reasons}}. Strong dimensions: {{strengths}}."
        ),
        "MAYBE": (
            "The tender should be reviewed (MAYBE, score {{total_score:.1f}}%) "
            "because: {{reasons}}. Watch points: {{weaknesses}}."
        ),
        "NO-GO": (
            "The tender is not recommended (NO-GO, score {{total_score:.1f}}%) "
            "because: {{reasons}}. Blocking dimensions: {{blockers}}."
        ),
    },
}

# Adverbes d'intensite selon le score
INTENSITY = {
    "fr": {
        (85, 100): "fortement recommande",
        (70, 85): "recommande",
        (55, 70): "modereement recommande",
    },
    "en": {
        (85, 100): "strongly recommended",
        (70, 85): "recommended",
        (55, 70): "moderately recommended",
    },
}


class Explainer:
    """Generateur d'explications pour les ScoreCards.

    L'explainer produit des textes comprehensibles qui justifient
    le verdict du moteur de scoring. Les explications sont basees sur
    les regles effectivement declenchees et les scores par dimension.

    Attributes:
        env: Environnement Jinja2 pour le rendu des templates.
    """

    def __init__(self) -> None:
        self.env = Environment(loader=BaseLoader())

    async def explain(
        self, scorecard: ScoreCard, lang: str = "fr"
    ) -> str:
        """Genere une explication textuelle complete d'une ScoreCard.

        Args:
            scorecard: La ScoreCard a expliquer.
            lang: Langue de l'explication ("fr" ou "en").

        Returns:
            Explication en langage naturel.
        """
        templates = TEMPLATES.get(lang, TEMPLATES["fr"])
        template_str = templates.get(
            scorecard.verdict.value, templates["MAYBE"]
        )

        # Construire le contexte de rendu
        context = self._build_context(scorecard, lang)

        try:
            template = self.env.from_string(template_str)
            return template.render(**context)
        except Exception as exc:
            logger.error("Erreur rendu template: %s", exc)
            return self._fallback_explanation(scorecard, lang)

    def _build_context(
        self, scorecard: ScoreCard, lang: str
    ) -> dict[str, Any]:
        """Construit le contexte pour le rendu du template.

        Args:
            scorecard: La ScoreCard source.
            lang: Langue.

        Returns:
            Dictionnaire de variables pour Jinja2.
        """
        breakdowns = sorted(
            scorecard.breakdowns,
            key=lambda b: b.weighted_score,
            reverse=True,
        )

        # Dimensions fortes (top 2)
        strengths = [
            f"{b.dimension_name} ({b.raw_score:.0f}%)"
            for b in breakdowns[:2]
            if b.raw_score >= 60
        ]

        # Dimensions faibles (bottom 2)
        weaknesses = [
            f"{b.dimension_name} ({b.raw_score:.0f}%)"
            for b in breakdowns[-2:]
            if b.raw_score < 60
        ]

        # Dimensions bloquantes (score < 20)
        blockers = [
            f"{b.dimension_name} ({b.raw_score:.0f}%)"
            for b in breakdowns
            if b.raw_score < 20
        ]

        # Raisons principales
        reasons = self._build_reasons(scorecard, lang)

        # Intensite
        strongly = self._intensity(scorecard.total_score, lang)

        return {
            "total_score": scorecard.total_score,
            "verdict": scorecard.verdict.value,
            "strongly_recommended": strongly,
            "reasons": reasons,
            "strengths": ", ".join(strengths) if strengths else "aucune",
            "weaknesses": ", ".join(weaknesses) if weaknesses else "aucune",
            "blockers": ", ".join(blockers) if blockers else "aucune",
        }

    def _build_reasons(
        self, scorecard: ScoreCard, lang: str
    ) -> str:
        """Construit la liste des raisons principales du verdict.

        Args:
            scorecard: La ScoreCard source.
            lang: Langue.

        Returns:
            Texte des raisons.
        """
        reasons: list[str] = []

        for b in scorecard.breakdowns:
            if b.rules_applied:
                # Prendre la premiere regle declenchee comme raison
                rule = b.rules_applied[0]
                if lang == "fr":
                    reasons.append(
                        f"{b.dimension_name}: {rule['condition']}"
                    )
                else:
                    reasons.append(
                        f"{b.dimension_name}: {rule['condition']}"
                    )

        if not reasons:
            return (
                "aucune regle specifique declenchee"
                if lang == "fr"
                else "no specific rule triggered"
            )

        return "; ".join(reasons[:3])  # Max 3 raisons

    def _intensity(self, score: float, lang: str) -> str:
        """Determine l'intensite de la recommandation.

        Args:
            score: Score total (0-100).
            lang: Langue.

        Returns:
            Adverbe d'intensite.
        """
        intensity_map = INTENSITY.get(lang, INTENSITY["fr"])
        for (low, high), label in intensity_map.items():
            if low <= score <= high:
                return label
        return (
            "faiblement recommande" if lang == "fr" else "weakly recommended"
        )

    def _fallback_explanation(
        self, scorecard: ScoreCard, lang: str
    ) -> str:
        """Explication de secours si le template echoue.

        Args:
            scorecard: La ScoreCard source.
            lang: Langue.

        Returns:
            Explication simple.
        """
        if lang == "fr":
            return (
                f"Score: {scorecard.total_score:.1f}/100 — "
                f"Verdict: {scorecard.verdict.value}. "
                f"{len(scorecard.breakdowns)} dimensions evaluees."
            )
        return (
            f"Score: {scorecard.total_score:.1f}/100 — "
            f"Verdict: {scorecard.verdict.value}. "
            f"{len(scorecard.breakdowns)} dimensions evaluated."
        )

    def explain_dimension(
        self, breakdown: ScoreBreakdown, lang: str = "fr"
    ) -> str:
        """Genere une explication pour une seule dimension.

        Args:
            breakdown: Le breakdown a expliquer.
            lang: Langue.

        Returns:
            Explication textuelle.
        """
        if lang == "fr":
            parts = [
                f"Dimension: {breakdown.dimension_name}",
                f"Score brut: {breakdown.raw_score:.1f}/100",
                f"Poids: {breakdown.weight:.0%}",
                f"Score pondere: {breakdown.weighted_score:.2f}",
            ]
            if breakdown.rules_applied:
                parts.append("Regles appliquees:")
                for rule in breakdown.rules_applied:
                    parts.append(f"  - {rule['condition']} -> {rule['action']}")
            else:
                parts.append("Aucune regle appliquee (score par defaut)")
            return "\n".join(parts)

        # English fallback
        parts = [
            f"Dimension: {breakdown.dimension_name}",
            f"Raw score: {breakdown.raw_score:.1f}/100",
            f"Weight: {breakdown.weight:.0%}",
            f"Weighted score: {breakdown.weighted_score:.2f}",
        ]
        if breakdown.rules_applied:
            parts.append("Applied rules:")
            for rule in breakdown.rules_applied:
                parts.append(f"  - {rule['condition']} -> {rule['action']}")
        else:
            parts.append("No rule applied (default score)")
        return "\n".join(parts)
```


---

### 2.6 Fichier: `app/services/scoring/feedback.py`

Boucle de retroaction et apprentissage des overrides utilisateur.

```python
"""FeedbackLoop — Apprentissage des overrides utilisateur.

Ce module gere la collecte du feedback utilisateur (overrides de verdict)
et produit des rapports d'accuracy ainsi que des suggestions d'ajustement.

Usage:
    loop = FeedbackLoop(repository)
    await loop.record_feedback(entry)
    adjustment = loop.get_bias_adjustment("coherence_metier")
    report = await loop.generate_report()
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Protocol

from app.core.types.scoring import (
    FeedbackEntry,
    FeedbackReport,
    ScoreVerdict,
)

logger = logging.getLogger(__name__)


class FeedbackRepository(Protocol):
    """Protocol pour le stockage des entrees de feedback.

    Permet de brancher differentes implementations de persistance
    (PostgreSQL, SQLite en test, etc.).
    """

    async def save(self, entry: FeedbackEntry) -> None:
        """Sauvegarde une entree de feedback."""
        ...

    async def get_by_dimension(
        self, dimension_id: str, limit: int = 100
    ) -> list[FeedbackEntry]:
        """Recupere les feedbacks pour une dimension."""
        ...

    async def get_all(self, limit: int = 1000) -> list[FeedbackEntry]:
        """Recupere tous les feedbacks."""
        ...

    async def get_stats(self) -> dict[str, Any]:
        """Recupere les statistiques globales."""
        ...


class FeedbackLoop:
    """Boucle de retroaction pour l'amelioration continue du scoring.

    Le FeedbackLoop collecte les overrides manuels des utilisateurs,
    analyse les ecarts prediction vs realite, et suggere des ajustements
    de poids et de seuils.

    Attributes:
        repository: Repository de persistance des feedbacks.
        _cache: Cache memoire des ajustements calcules.
    """

    def __init__(self, repository: FeedbackRepository) -> None:
        self.repository = repository
        self._cache: dict[str, float] = {}

    async def record_feedback(self, entry: FeedbackEntry) -> None:
        """Enregistre un feedback utilisateur.

        Args:
            entry: L'entree de feedback a persister.
        """
        await self.repository.save(entry)
        # Invalider le cache
        self._cache.clear()
        logger.info(
            "Feedback enregistre: tender=%s predicted=%s actual=%s",
            entry.tender_id,
            entry.predicted_verdict.value,
            entry.actual_verdict.value,
        )

    def get_bias_adjustment(self, dimension_id: str) -> float:
        """Retourne la correction de biais suggeree pour une dimension.

        La correction est basee sur l'analyse des ecarts entre prediction
        et realite pour cette dimension. Une correction positive signifie
        que le moteur sous-estime la dimension (il faut augmenter son poids).

        Args:
            dimension_id: Identifiant de la dimension.

        Returns:
            Correction a appliquer (entre -0.2 et +0.2).
        """
        if dimension_id in self._cache:
            return self._cache[dimension_id]

        # TODO: Implementer le calcul base sur les feedbacks stockes
        # Placeholder: retourner 0.0 (pas de correction connue)
        return 0.0

    async def generate_report(self) -> FeedbackReport:
        """Genere un rapport d'accuracy global.

        Analyse l'ensemble des feedbacks et produit des statistiques
        par dimension avec suggestions d'ajustement.

        Returns:
            FeedbackReport avec statistiques et recommandations.
        """
        all_feedback = await self.repository.get_all()

        if not all_feedback:
            return FeedbackReport(
                total_evaluations=0,
                total_overrides=0,
                override_rate=0.0,
                accuracy_by_dimension={},
                suggested_adjustments={},
            )

        total = len(all_feedback)
        overrides = [
            f for f in all_feedback
            if f.predicted_verdict != f.actual_verdict
        ]
        override_count = len(overrides)

        # Accuracy par dimension
        accuracy_by_dim: dict[str, dict[str, int]] = {}
        for feedback in all_feedback:
            for dim_id in feedback.dimension_scores:
                if dim_id not in accuracy_by_dim:
                    accuracy_by_dim[dim_id] = {
                        "total": 0, "correct": 0
                    }
                accuracy_by_dim[dim_id]["total"] += 1
                if feedback.predicted_verdict == feedback.actual_verdict:
                    accuracy_by_dim[dim_id]["correct"] += 1

        accuracy_rates = {
            dim_id: (
                stats["correct"] / stats["total"]
                if stats["total"] > 0
                else 0.0
            )
            for dim_id, stats in accuracy_by_dim.items()
        }

        # Suggestions d'ajustement
        suggestions = {
            dim_id: self._suggest_adjustment(rate)
            for dim_id, rate in accuracy_rates.items()
        }

        return FeedbackReport(
            total_evaluations=total,
            total_overrides=override_count,
            override_rate=override_count / total if total > 0 else 0.0,
            accuracy_by_dimension=accuracy_rates,
            suggested_adjustments=suggestions,
        )

    def _suggest_adjustment(self, accuracy_rate: float) -> float:
        """Suggere un ajustement de poids base sur le taux d'accuracy.

        Args:
            accuracy_rate: Taux d'accuracy (0.0-1.0).

        Returns:
            Ajustement suggere (-0.2 a +0.2).
        """
        if accuracy_rate >= 0.85:
            return 0.05  # Legerement augmenter
        elif accuracy_rate >= 0.70:
            return 0.0  # Pas de changement
        elif accuracy_rate >= 0.50:
            return -0.10  # Reduire legerement
        else:
            return -0.20  # Reduire fortement

    async def get_dimension_feedback_summary(
        self, dimension_id: str
    ) -> dict[str, Any]:
        """Recupere un resume des feedbacks pour une dimension.

        Args:
            dimension_id: Identifiant de la dimension.

        Returns:
            Dictionnaire avec statistiques et exemples.
        """
        feedbacks = await self.repository.get_by_dimension(dimension_id)

        if not feedbacks:
            return {
                "dimension_id": dimension_id,
                "total_feedback": 0,
                "override_count": 0,
                "override_rate": 0.0,
            }

        overrides = [
            f for f in feedbacks
            if f.predicted_verdict != f.actual_verdict
        ]

        # Distribution des overrides par type de transition
        transitions: dict[str, int] = {}
        for f in overrides:
            key = (
                f"{f.predicted_verdict.value}->{f.actual_verdict.value}"
            )
            transitions[key] = transitions.get(key, 0) + 1

        return {
            "dimension_id": dimension_id,
            "total_feedback": len(feedbacks),
            "override_count": len(overrides),
            "override_rate": len(overrides) / len(feedbacks),
            "transitions": transitions,
            "average_dimension_score": sum(
                f.dimension_scores.get(dimension_id, 0)
                for f in feedbacks
            ) / len(feedbacks) if feedbacks else 0.0,
        }
```

---

### 2.7 Fichier: `app/services/scoring/thresholds.py`

Gestionnaire des seuils de decision par profil.

```python
"""ThresholdManager — Gestion des seuils de decision par profil.

Fournit les seuils GO/MAYBE/NO-GO pour chaque profil de scoring
et permet leur ajustement base sur le feedback historique.

Usage:
    manager = ThresholdManager()
    thresholds = manager.get_thresholds(ScoringProfile.PRUDENT)
    adjusted = manager.adjust_thresholds(ScoringProfile.PRUDENT, feedback)
"""

from __future__ import annotations

import logging
from typing import Any

from app.core.types.scoring import (
    FeedbackEntry,
    ScoringProfile,
    ThresholdConfig,
)

logger = logging.getLogger(__name__)

# Seuils par defaut pour chaque profil
DEFAULT_THRESHOLDS: dict[ScoringProfile, ThresholdConfig] = {
    ScoringProfile.PRUDENT: ThresholdConfig(
        go=0.70,
        maybe=0.45,
        no_go=0.0,
    ),
    ScoringProfile.OPPORTUNISTE: ThresholdConfig(
        go=0.55,
        maybe=0.30,
        no_go=0.0,
    ),
    ScoringProfile.SPECIALISE: ThresholdConfig(
        go=0.65,
        maybe=0.40,
        no_go=0.0,
    ),
}


class ThresholdManager:
    """Gestionnaire des seuils de decision.

    Maintient les seuils pour chaque profil et permet leur ajustement
    dynamique base sur le feedback utilisateur.

    Attributes:
        _thresholds: Dictionnaire profil -> ThresholdConfig.
        _min_gap: Ecart minimum requis entre maybe et go.
    """

    def __init__(self, min_gap: float = 0.15) -> None:
        self._thresholds: dict[ScoringProfile, ThresholdConfig] = dict(
            DEFAULT_THRESHOLDS
        )
        self._min_gap = min_gap

    def get_thresholds(
        self, profile: ScoringProfile
    ) -> ThresholdConfig:
        """Retourne les seuils pour un profil donne.

        Args:
            profile: Profil de scoring.

        Returns:
            ThresholdConfig avec les seuils go/maybe/no_go.
        """
        return self._thresholds.get(
            profile, DEFAULT_THRESHOLDS[ScoringProfile.SPECIALISE]
        )

    def set_thresholds(
        self,
        profile: ScoringProfile,
        thresholds: ThresholdConfig,
    ) -> None:
        """Definit les seuils pour un profil.

        Args:
            profile: Profil a modifier.
            thresholds: Nouveaux seuils (valides).

        Raises:
            ValueError: Si les seuils sont invalides.
        """
        self._thresholds[profile] = thresholds
        logger.info(
            "Seuils mis a jour pour %s: go=%.2f maybe=%.2f",
            profile.value,
            thresholds.go,
            thresholds.maybe,
        )

    def adjust_thresholds(
        self,
        profile: ScoringProfile,
        feedback: list[FeedbackEntry],
    ) -> ThresholdConfig:
        """Ajuste les seuils base sur le feedback historique.

        Si les utilisateurs surclassent frequemment MAYBE en GO,
        le seuil maybe est legerement abaisse. Inversement, si les
        GO sont souvent surclasses en NO-GO, le seuil go est releve.

        Args:
            profile: Profil a ajuster.
            feedback: Historique des feedbacks.

        Returns:
            Nouveaux seuils ajustes.
        """
        base = self.get_thresholds(profile)

        if not feedback:
            return base

        # Analyser les transitions de verdict
        maybe_to_go = 0  # Trop conservateur
        go_to_nogo = 0  # Trop optimiste
        total = len(feedback)

        for entry in feedback:
            if (
                entry.predicted_verdict == ScoreVerdict.MAYBE
                and entry.actual_verdict == ScoreVerdict.GO
            ):
                maybe_to_go += 1
            elif (
                entry.predicted_verdict == ScoreVerdict.GO
                and entry.actual_verdict == ScoreVerdict.NO_GO
            ):
                go_to_nogo += 1

        maybe_to_go_rate = maybe_to_go / total
        go_to_nogo_rate = go_to_nogo / total

        new_go = base.go
        new_maybe = base.maybe

        # Ajuster
        if maybe_to_go_rate > 0.30:
            # Trop de MAYBE qui devraient etre GO: baisser les seuils
            new_maybe = max(0.20, base.maybe - 0.05)
            new_go = max(new_maybe + self._min_gap, base.go - 0.05)
        elif go_to_nogo_rate > 0.30:
            # Trop de GO qui devraient etre NO-GO: monter les seuils
            new_go = min(0.95, base.go + 0.05)
            new_maybe = min(new_go - self._min_gap, base.maybe + 0.03)

        try:
            adjusted = ThresholdConfig(
                go=new_go,
                maybe=new_maybe,
                no_go=base.no_go,
            )
            self._thresholds[profile] = adjusted
            logger.info(
                "Seuils ajustes pour %s: go=%.2f->%.2f maybe=%.2f->%.2f",
                profile.value,
                base.go,
                new_go,
                base.maybe,
                new_maybe,
            )
            return adjusted
        except ValueError as exc:
            logger.warning("Ajustement invalide ignore: %s", exc)
            return base

    def reset_to_defaults(self) -> None:
        """Reinitialise tous les seuils aux valeurs par defaut."""
        self._thresholds = dict(DEFAULT_THRESHOLDS)
        logger.info("Seuils reinitialises aux valeurs par defaut")

    def get_all_thresholds(self) -> dict[str, dict[str, float]]:
        """Retourne tous les seuils pour tous les profils.

        Returns:
            Dictionnaire profile_name -> {go, maybe, no_go}.
        """
        return {
            profile.value: {
                "go": t.go,
                "maybe": t.maybe,
                "no_go": t.no_go,
            }
            for profile, t in self._thresholds.items()
        }
```


---

### 2.8 Fichier: `app/services/scoring/plugins/__init__.py`

```python
"""Plugins de dimension pour le Scoring Engine V2.

Ce package contient les implementations concretes des 5 dimensions
de scoring. Chaque plugin herite de AbstractDimensionPlugin et
implemente la logique specifique a sa dimension.
"""

from app.services.scoring.plugins.coherence_metier import (
    CoherenceMetierPlugin,
)
from app.services.scoring.plugins.viabilite_financiere import (
    ViabiliteFinancierePlugin,
)
from app.services.scoring.plugins.accessibilite_geographique import (
    AccessibiliteGeographiquePlugin,
)
from app.services.scoring.plugins.faisabilite_temporelle import (
    FaisabiliteTemporellePlugin,
)
from app.services.scoring.plugins.intelligence_concurrentielle import (
    IntelligenceConcurrentiellePlugin,
)

__all__ = [
    "CoherenceMetierPlugin",
    "ViabiliteFinancierePlugin",
    "AccessibiliteGeographiquePlugin",
    "FaisabiliteTemporellePlugin",
    "IntelligenceConcurrentiellePlugin",
]
```

---

### 2.9 Fichier: `app/services/scoring/plugins/coherence_metier.py`

Plugin de scoring — Cohérence Métier (alignment CPV/compétences).

```python
"""CoherenceMetierPlugin — Dimension 1: Cohérence Métier.

Evalue l'adéquation entre le code CPV de l'AO et les compétences,
secteurs d'activité et historique de l'entreprise.

Input schema (YAML):
    - ao.cpv_code: str, code CPV à 8 chiffres
    - ao.cpv_description: str, libellé CPV
    - ao.keywords: list[str], mots-clés de l'AO
    - enterprise.competencies: list[str], compétences déclarées
    - enterprise.cpv_whitelist: list[str], CPV ciblés
    - enterprise.sectors: list[str], secteurs d'activité
    - enterprise.past_cpv_success: list[str], CPV historiquement gagnés
"""

from __future__ import annotations

import logging
from typing import Any

from app.core.types.scoring import (
    DimensionConfig,
    ScoreBreakdown,
)
from app.services.scoring.engine import AbstractDimensionPlugin

logger = logging.getLogger(__name__)


class CoherenceMetierPlugin(AbstractDimensionPlugin):
    """Plugin d'évaluation de la cohérence métier.

    Cette dimension mesure dans quelle mesure l'AO correspond aux
    compétences déclarées, aux secteurs d'activité et à l'historique
    de l'entreprise. Un CPV présent dans la whitelist ou déjà gagné
    confère un score maximal.
    """

    dimension_id = "coherence_metier"
    dimension_name = "Cohérence Métier"
    version = "1.0.0"

    def __init__(self, config: DimensionConfig) -> None:
        super().__init__(config)

    async def evaluate(
        self,
        ao_data: dict[str, Any],
        enterprise_data: dict[str, Any],
    ) -> ScoreBreakdown:
        """Évalue la cohérence métier entre l'AO et l'entreprise.

        Construit le contexte d'évaluation à partir des données de l'AO
        et de l'entreprise, applique les règles SI/ALORS, et retourne
        le breakdown détaillé.

        Args:
            ao_data: Données de l'appel d'offres.
            enterprise_data: Données de l'entreprise.

        Returns:
            ScoreBreakdown avec score et explication.
        """
        # Extraire les champs nécessaires avec valeurs par défaut
        ao = ao_data or {}
        ent = enterprise_data or {}

        cpv_code = ao.get("cpv_code", "")
        cpv_description = ao.get("cpv_description", "")
        keywords = set(ao.get("keywords", []))

        cpv_whitelist = ent.get("cpv_whitelist", [])
        competencies = set(ent.get("competencies", []))
        sectors = ent.get("sectors", [])
        past_cpv_success = ent.get("past_cpv_success", [])

        # Calculer les métriques dérivées
        common_keywords = keywords & competencies
        n_common = len(common_keywords)

        # Construire le contexte d'évaluation
        context: dict[str, Any] = {
            "ao": {
                "cpv_code": cpv_code,
                "cpv_description": cpv_description,
                "keywords": list(keywords),
            },
            "enterprise": {
                "cpv_whitelist": cpv_whitelist,
                "competencies": list(competencies),
                "sectors": sectors,
                "past_cpv_success": past_cpv_success,
            },
            "n": n_common,  # Pour le template Jinja2
        }

        # Ajouter des variables raccourcies pour les conditions
        context["cpv_code"] = cpv_code
        context["cpv_description"] = cpv_description
        context["keywords"] = list(keywords)
        context["cpv_whitelist"] = cpv_whitelist
        context["competencies"] = list(competencies)
        context["sectors"] = sectors
        context["past_cpv_success"] = past_cpv_success

        # Appliquer les règles
        raw_score, rules_applied = self._apply_rules(context)

        # Construire l'explication
        explanation = self._build_explanation(
            cpv_code, cpv_whitelist, n_common, rules_applied
        )

        return ScoreBreakdown(
            dimension_id=self.dimension_id,
            dimension_name=self.dimension_name,
            raw_score=raw_score,
            weighted_score=0.0,  # Sera calculé par le moteur
            weight=self.config.default_weight,
            rules_applied=rules_applied,
            explanation=explanation,
        )

    def _build_explanation(
        self,
        cpv_code: str,
        cpv_whitelist: list[str],
        n_common: int,
        rules_applied: list[dict[str, Any]],
    ) -> str:
        """Construit l'explication textuelle du scoring.

        Args:
            cpv_code: Code CPV de l'AO.
            cpv_whitelist: Liste des CPV ciblés.
            n_common: Nombre de mots-clés communs.
            rules_applied: Règles déclenchées.

        Returns:
            Explication en langage naturel.
        """
        parts: list[str] = []

        if cpv_code in cpv_whitelist:
            parts.append(
                f"CPV {cpv_code} dans la whitelist entreprise — "
                f"correspondance parfaite"
            )
        elif any(cpv_code[:2] == w[:2] for w in cpv_whitelist):
            parts.append(
                f"CPV {cpv_code} dans la même famille que les CPV ciblés"
            )
        else:
            parts.append(
                f"CPV {cpv_code} non ciblé explicitement"
            )

        if n_common > 0:
            parts.append(
                f"{n_common} mot(s)-clé(s) en commun avec les compétences"
            )

        if not rules_applied:
            parts.append(
                "Aucune correspondance forte détectée — score par défaut"
            )

        return "; ".join(parts)
```

---

### 2.10 Fichier: `app/services/scoring/plugins/viabilite_financiere.py`

Plugin de scoring — Viabilité Financière.

```python
"""ViabiliteFinancierePlugin — Dimension 2: Viabilité Financière.

Evalue la capacité financière de l'entreprise à réaliser le marché
en comparant le montant estimé de l'AO avec le CA, la trésorerie,
le capital social et le ratio d'endettement.

Input schema (YAML):
    - ao.estimated_amount: float, montant estimé du marché (EUR)
    - ao.cautionnement: float, montant du cautionnement requis
    - ao.cautionnement_percent: float, cautionnement / montant total
    - ao.payment_terms_days: int, délai de paiement
    - enterprise.ca: float, chiffre d'affaires annuel
    - enterprise.tresorerie: float, trésorerie disponible
    - enterprise.ratio_endettement: float, dettes / capitaux propres
    - enterprise.capital_social: float, capital social
    - enterprise.avg_project_size: float, taille moyenne des projets
"""

from __future__ import annotations

import logging
from typing import Any

from app.core.types.scoring import DimensionConfig, ScoreBreakdown
from app.services.scoring.engine import AbstractDimensionPlugin

logger = logging.getLogger(__name__)


class ViabiliteFinancierePlugin(AbstractDimensionPlugin):
    """Plugin d'évaluation de la viabilité financière.

    Cette dimension mesure si l'entreprise a les moyens financiers
    d'honorer le marché. Un AO représentant plus de 50% du CA ou
    nécessitant un cautionnement supérieur à la trésorerie est
    fortement pénalisé.
    """

    dimension_id = "viabilite_financiere"
    dimension_name = "Viabilité Financière"
    version = "1.0.0"

    def __init__(self, config: DimensionConfig) -> None:
        super().__init__(config)

    async def evaluate(
        self,
        ao_data: dict[str, Any],
        enterprise_data: dict[str, Any],
    ) -> ScoreBreakdown:
        """Évalue la viabilité financière de l'AO pour l'entreprise.

        Args:
            ao_data: Données de l'appel d'offres.
            enterprise_data: Données de l'entreprise.

        Returns:
            ScoreBreakdown avec score financier.
        """
        ao = ao_data or {}
        ent = enterprise_data or {}

        # Extraire les valeurs financières
        estimated_amount = float(ao.get("estimated_amount", 0))
        cautionnement = float(ao.get("cautionnement", 0))
        cautionnement_pct = float(ao.get("cautionnement_percent", 0))
        payment_terms = int(ao.get("payment_terms_days", 30))

        ca = float(ent.get("ca", 1))  # Éviter division par zéro
        tresorerie = float(ent.get("tresorerie", 0))
        ratio_endettement = float(ent.get("ratio_endettement", 0))
        capital_social = float(ent.get("capital_social", 0))
        avg_project_size = float(ent.get("avg_project_size", ca * 0.1))

        # Construire le contexte
        context: dict[str, Any] = {
            "ao": {
                "estimated_amount": estimated_amount,
                "cautionnement": cautionnement,
                "cautionnement_percent": cautionnement_pct,
                "payment_terms_days": payment_terms,
            },
            "enterprise": {
                "ca": ca,
                "tresorerie": tresorerie,
                "ratio_endettement": ratio_endettement,
                "capital_social": capital_social,
                "avg_project_size": avg_project_size,
            },
            # Variables raccourcies pour les conditions
            "estimated_amount": estimated_amount,
            "cautionnement": cautionnement,
            "cautionnement_percent": cautionnement_pct,
            "payment_terms_days": payment_terms,
            "ca": ca,
            "tresorerie": tresorerie,
            "ratio_endettement": ratio_endettement,
            "capital_social": capital_social,
            "avg_project_size": avg_project_size,
        }

        raw_score, rules_applied = self._apply_rules(context)

        explanation = self._build_explanation(
            estimated_amount, ca, cautionnement, tresorerie,
            ratio_endettement, rules_applied,
        )

        return ScoreBreakdown(
            dimension_id=self.dimension_id,
            dimension_name=self.dimension_name,
            raw_score=raw_score,
            weighted_score=0.0,
            weight=self.config.default_weight,
            rules_applied=rules_applied,
            explanation=explanation,
        )

    def _build_explanation(
        self,
        estimated_amount: float,
        ca: float,
        cautionnement: float,
        tresorerie: float,
        ratio_endettement: float,
        rules_applied: list[dict[str, Any]],
    ) -> str:
        """Construit l'explication financière."""
        parts: list[str] = []

        ao_ratio = (estimated_amount / ca * 100) if ca > 0 else 0
        parts.append(f"AO = {ao_ratio:.1f}% du CA")

        if tresorerie < cautionnement:
            parts.append(
                f"Trésorerie ({tresorerie:,.0f}€) < cautionnement "
                f"({cautionnement:,.0f}€)"
            )
        else:
            parts.append(
                f"Trésorerie suffisante: {tresorerie:,.0f}€ "
                f"vs cautionnement {cautionnement:,.0f}€"
            )

        if ratio_endettement > 0.5:
            parts.append(
                f"Ratio d'endettement élevé: {ratio_endettement:.0%}"
            )

        if not rules_applied:
            parts.append("Situation financière globalement saine")

        return "; ".join(parts)
```

---

### 2.11 Fichier: `app/services/scoring/plugins/accessibilite_geographique.py`

Plugin de scoring — Accessibilité Géographique.

```python
"""AccessibiliteGeographiquePlugin — Dimension 3: Accessibilité Géographique.

Evalue si l'entreprise peut techniquement intervenir sur le site de
l'AO en fonction de ses zones d'intervention, du siège social et
de la distance estimée.

Input schema (YAML):
    - ao.location: str, lieu d'exécution
    - ao.region: str, code région
    - ao.departement: str, code département
    - ao.is_remote_accepted: bool, télétravail accepté
    - enterprise.zones_intervention: list[str], régions couvertes
    - enterprise.departements_couverts: list[str], départements couverts
    - enterprise.siege_social: dict, coordonnées du siège
    - distance_km: float, distance estimée siège → site
"""

from __future__ import annotations

import logging
import math
from typing import Any

from app.core.types.scoring import DimensionConfig, ScoreBreakdown
from app.services.scoring.engine import AbstractDimensionPlugin

logger = logging.getLogger(__name__)


class AccessibiliteGeographiquePlugin(AbstractDimensionPlugin):
    """Plugin d'évaluation de l'accessibilité géographique.

    Cette dimension vérifie si le lieu d'exécution de l'AO est dans
    la zone d'intervention de l'entreprise et calcule l'impact de la
distance sur la faisabilité opérationnelle.
    """

    dimension_id = "accessibilite_geographique"
    dimension_name = "Accessibilité Géographique"
    version = "1.0.0"

    def __init__(self, config: DimensionConfig) -> None:
        super().__init__(config)

    async def evaluate(
        self,
        ao_data: dict[str, Any],
        enterprise_data: dict[str, Any],
    ) -> ScoreBreakdown:
        """Évalue l'accessibilité géographique.

        Args:
            ao_data: Données de l'AO avec localisation.
            enterprise_data: Données de l'entreprise avec zones.

        Returns:
            ScoreBreakdown géographique.
        """
        ao = ao_data or {}
        ent = enterprise_data or {}

        region = ao.get("region", "")
        departement = ao.get("departement", "")
        is_remote = ao.get("is_remote_accepted", False)
        ao_location = ao.get("location", {})

        zones = ent.get("zones_intervention", [])
        departements = ent.get("departements_couverts", [])
        siege = ent.get("siege_social", {})
        has_remote = ent.get("has_remote_capability", False)

        # Calculer la distance si les coordonnées sont disponibles
        distance_km = self._calculate_distance(
            siege, ao_location
        )

        # Construire le contexte
        context: dict[str, Any] = {
            "ao": {
                "location": ao_location,
                "region": region,
                "departement": departement,
                "is_remote_accepted": is_remote,
            },
            "enterprise": {
                "zones_intervention": zones,
                "departements_couverts": departements,
                "siege_social": siege,
                "has_remote_capability": has_remote,
            },
            "distance_km": distance_km,
            "region": region,
            "departement": departement,
            "is_remote_accepted": is_remote,
            "zones_intervention": zones,
            "departements_couverts": departements,
            "has_remote_capability": has_remote,
        }

        raw_score, rules_applied = self._apply_rules(context)

        explanation = self._build_explanation(
            region, zones, distance_km, is_remote, has_remote, rules_applied
        )

        return ScoreBreakdown(
            dimension_id=self.dimension_id,
            dimension_name=self.dimension_name,
            raw_score=raw_score,
            weighted_score=0.0,
            weight=self.config.default_weight,
            rules_applied=rules_applied,
            explanation=explanation,
        )

    def _calculate_distance(
        self,
        siege: dict[str, Any],
        ao_location: dict[str, Any],
    ) -> float:
        """Calcule la distance en km entre le siège et le site de l'AO.

        Utilise la formule de Haversine si les coordonnées GPS sont
        disponibles, sinon retourne une estimation conservative.

        Args:
            siege: Coordonnées du siège {lat, lon}.
            ao_location: Coordonnées du site {lat, lon}.

        Returns:
            Distance en kilomètres.
        """
        try:
            lat1 = float(siege.get("lat", 0))
            lon1 = float(siege.get("lon", 0))
            lat2 = float(ao_location.get("lat", 0))
            lon2 = float(ao_location.get("lon", 0))

            if not all([lat1, lon1, lat2, lon2]):
                return 999.0  # Distance inconnue = conservative

            # Formule de Haversine
            R = 6371  # Rayon de la Terre en km
            phi1, phi2 = math.radians(lat1), math.radians(lat2)
            dphi = math.radians(lat2 - lat1)
            dlambda = math.radians(lon2 - lon1)

            a = (
                math.sin(dphi / 2) ** 2
                + math.cos(phi1)
                * math.cos(phi2)
                * math.sin(dlambda / 2) ** 2
            )
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c
        except (TypeError, ValueError, AttributeError):
            return 999.0

    def _build_explanation(
        self,
        region: str,
        zones: list[str],
        distance_km: float,
        is_remote: bool,
        has_remote: bool,
        rules_applied: list[dict[str, Any]],
    ) -> str:
        """Construit l'explication géographique."""
        parts: list[str] = []

        if region in zones:
            parts.append(f"Région {region} couverte")
        else:
            parts.append(f"Région {region} NON couverte")

        if distance_km < 999:
            parts.append(f"Distance: {distance_km:.0f} km")

        if is_remote and has_remote:
            parts.append("Télétravail possible")

        if not rules_applied:
            parts.append("Accessibilité standard")

        return "; ".join(parts)
```

---

### 2.12 Fichier: `app/services/scoring/plugins/faisabilite_temporelle.py`

Plugin de scoring — Faisabilité Temporelle.

```python
"""FaisabiliteTemporellePlugin — Dimension 4: Faisabilité Temporelle.

Evalue si l'entreprise dispose de suffisamment de temps pour préparer
une réponse de qualité avant la date limite de l'AO.

Input schema (YAML):
    - ao.date_publication: str, date de publication (ISO 8601)
    - ao.date_limite: str, date limite de réponse (ISO 8601)
    - ao.date_debut_prestation: str, date de début (ISO 8601)
    - ao.duree_mois: int, durée de la prestation en mois
    - ao.complexite_estimee: str, 'faible' | 'moyenne' | 'elevee'
    - enterprise.delai_preparation_jours: int, jours nécessaires
    - enterprise.avg_response_time_days: int, historique de réponse
    - enterprise.current_workload: float, charge actuelle (0.0-1.0)
    - jours_restants: int, jours restants avant deadline
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from app.core.types.scoring import DimensionConfig, ScoreBreakdown
from app.services.scoring.engine import AbstractDimensionPlugin

logger = logging.getLogger(__name__)


class FaisabiliteTemporellePlugin(AbstractDimensionPlugin):
    """Plugin d'évaluation de la faisabilité temporelle.

    Cette dimension mesure si le délai restant avant la date limite
    est suffisant pour préparer une réponse de qualité, en tenant
    compte de la charge de travail actuelle et de la complexité de l'AO.
    """

    dimension_id = "faisabilite_temporelle"
    dimension_name = "Faisabilité Temporelle"
    version = "1.0.0"

    def __init__(self, config: DimensionConfig) -> None:
        super().__init__(config)

    async def evaluate(
        self,
        ao_data: dict[str, Any],
        enterprise_data: dict[str, Any],
    ) -> ScoreBreakdown:
        """Évalue la faisabilité temporelle.

        Args:
            ao_data: Données de l'AO avec dates.
            enterprise_data: Données de l'entreprise avec capacités.

        Returns:
            ScoreBreakdown temporel.
        """
        ao = ao_data or {}
        ent = enterprise_data or {}

        date_limite_str = ao.get("date_limite", "")
        complexite = ao.get("complexite_estimee", "moyenne")
        duree_mois = int(ao.get("duree_mois", 0))

        delai_prep = int(ent.get("delai_preparation_jours", 14))
        avg_response = int(ent.get("avg_response_time_days", delai_prep))
        workload = float(ent.get("current_workload", 0.5))
        pmi_flag = bool(ent.get("pmi_flag", False))

        # Calculer les jours restants
        jours_restants = self._compute_jours_restants(date_limite_str)

        # Construire le contexte
        context: dict[str, Any] = {
            "ao": {
                "date_limite": date_limite_str,
                "complexite_estimee": complexite,
                "duree_mois": duree_mois,
            },
            "enterprise": {
                "delai_preparation_jours": delai_prep,
                "avg_response_time_days": avg_response,
                "current_workload": workload,
                "pmi_flag": pmi_flag,
            },
            "jours_restants": jours_restants,
            "complexite_estimee": complexite,
            "duree_mois": duree_mois,
            "delai_preparation_jours": delai_prep,
            "avg_response_time_days": avg_response,
            "current_workload": workload,
            "pmi_flag": pmi_flag,
        }

        raw_score, rules_applied = self._apply_rules(context)

        explanation = self._build_explanation(
            jours_restants, delai_prep, workload, complexite, rules_applied
        )

        return ScoreBreakdown(
            dimension_id=self.dimension_id,
            dimension_name=self.dimension_name,
            raw_score=raw_score,
            weighted_score=0.0,
            weight=self.config.default_weight,
            rules_applied=rules_applied,
            explanation=explanation,
        )

    def _compute_jours_restants(self, date_limite_str: str) -> int:
        """Calcule le nombre de jours restants avant la deadline.

        Args:
            date_limite_str: Date limite au format ISO 8601.

        Returns:
            Nombre de jours restants (peut être négatif).
        """
        try:
            deadline = datetime.fromisoformat(
                date_limite_str.replace("Z", "+00:00")
            )
            now = datetime.now(timezone.utc)
            delta = deadline - now
            return max(0, int(delta.total_seconds() / 86400))
        except (ValueError, TypeError):
            logger.warning(
                "Date limite invalide: %s — retour à 0 jours",
                date_limite_str,
            )
            return 0

    def _build_explanation(
        self,
        jours_restants: int,
        delai_prep: int,
        workload: float,
        complexite: str,
        rules_applied: list[dict[str, Any]],
    ) -> str:
        """Construit l'explication temporelle."""
        parts: list[str] = []

        ratio = jours_restants / delai_prep if delai_prep > 0 else 0
        parts.append(
            f"{jours_restants} jours restants "
            f"(délai préparation: {delai_prep} jours, ratio: {ratio:.1f}x)"
        )

        if workload > 0.8:
            parts.append(f"Charge de travail élevée: {workload:.0%}")

        if complexite == "elevee":
            parts.append("AO à complexité élevée — préparation plus longue")

        if not rules_applied:
            parts.append("Délai standard — aucun facteur de risque")

        return "; ".join(parts)
```

---

### 2.13 Fichier: `app/services/scoring/plugins/intelligence_concurrentielle.py`

Plugin de scoring — Intelligence Concurrentielle.

```python
"""IntelligenceConcurrentiellePlugin — Dimension 5: Intelligence Concurrentielle.

Evalue les chances de succès de l'entreprise en analysant la
concurrence estimée, les barrières à l'entrée et l'avantage
compétitif de l'entreprise (certifications, références).

Input schema (YAML):
    - ao.nb_concurrents_estime: int, nombre de concurrents estimés
    - ao.barrieres_entree: str, 'faible' | 'moyenne' | 'elevee'
    - ao.type_marche: str, type de procédure
    - ao.avis_precedent_exists: bool, avis précédent disponible
    - enterprise.positionnement: str, 'premium' | 'standard' | 'low_cost'
    - enterprise.certifications: list[str], certifications
    - enterprise.references_significatives: int, nombre de références
    - enterprise.past_wins_same_type: list[str], types de marchés gagnés
"""

from __future__ import annotations

import logging
from typing import Any

from app.core.types.scoring import DimensionConfig, ScoreBreakdown
from app.services.scoring.engine import AbstractDimensionPlugin

logger = logging.getLogger(__name__)


class IntelligenceConcurrentiellePlugin(AbstractDimensionPlugin):
    """Plugin d'évaluation de l'intelligence concurrentielle.

    Cette dimension analyse l'environnement concurrentiel de l'AO :
    nombre de concurrents estimés, barrières à l'entrée, et avantages
    spécifiques de l'entreprise (certifications, références passées).
    """

    dimension_id = "intelligence_concurrentielle"
    dimension_name = "Intelligence Concurrentielle"
    version = "1.0.0"

    def __init__(self, config: DimensionConfig) -> None:
        super().__init__(config)

    async def evaluate(
        self,
        ao_data: dict[str, Any],
        enterprise_data: dict[str, Any],
    ) -> ScoreBreakdown:
        """Évalue l'intelligence concurrentielle.

        Args:
            ao_data: Données de l'AO avec estimations concurrentielles.
            enterprise_data: Données de l'entreprise avec avantages.

        Returns:
            ScoreBreakdown concurrentiel.
        """
        ao = ao_data or {}
        ent = enterprise_data or {}

        nb_concurrents = int(ao.get("nb_concurrents_estime", 5))
        barrieres = ao.get("barrieres_entree", "moyenne")
        type_marche = ao.get("type_marche", "")
        avis_precedent = bool(ao.get("avis_precedent_exists", False))
        estimated_amount = float(ao.get("estimated_amount", 0))
        past_award_price = float(ao.get("past_award_price", 0))

        positionnement = ent.get("positionnement", "standard")
        certifications = ent.get("certifications", [])
        references = int(ent.get("references_significatives", 0))
        past_wins = ent.get("past_wins_same_type", [])

        # Construire le contexte
        context: dict[str, Any] = {
            "ao": {
                "nb_concurrents_estime": nb_concurrents,
                "barrieres_entree": barrieres,
                "type_marche": type_marche,
                "avis_precedent_exists": avis_precedent,
                "estimated_amount": estimated_amount,
                "past_award_price": past_award_price,
            },
            "enterprise": {
                "positionnement": positionnement,
                "certifications": certifications,
                "references_significatives": references,
                "past_wins_same_type": past_wins,
            },
            "nb_concurrents_estime": nb_concurrents,
            "barrieres_entree": barrieres,
            "type_marche": type_marche,
            "avis_precedent_exists": avis_precedent,
            "positionnement": positionnement,
            "certifications": certifications,
            "references_significatives": references,
            "past_wins_same_type": past_wins,
            "estimated_amount": estimated_amount,
        }

        raw_score, rules_applied = self._apply_rules(context)

        explanation = self._build_explanation(
            nb_concurrents, barrieres, certifications,
            references, rules_applied,
        )

        return ScoreBreakdown(
            dimension_id=self.dimension_id,
            dimension_name=self.dimension_name,
            raw_score=raw_score,
            weighted_score=0.0,
            weight=self.config.default_weight,
            rules_applied=rules_applied,
            explanation=explanation,
        )

    def _build_explanation(
        self,
        nb_concurrents: int,
        barrieres: str,
        certifications: list[str],
        references: int,
        rules_applied: list[dict[str, Any]],
    ) -> str:
        """Construit l'explication concurrentielle."""
        parts: list[str] = []

        if nb_concurrents <= 5:
            parts.append(
                f"Concurrence limitée ({nb_concurrents} estimés)"
            )
        elif nb_concurrents <= 10:
            parts.append(
                f"Concurrence modérée ({nb_concurrents} estimés)"
            )
        else:
            parts.append(
                f"Forte concurrence ({nb_concurrents} estimés)"
            )

        if barrieres == "elevee" and len(certifications) >= 3:
            parts.append(
                f"Barrières élevées + {len(certifications)} certifications — "
                f"avantage compétitif"
            )

        if references >= 3:
            parts.append(f"{references} références significatives")

        if not rules_applied:
            parts.append("Situation concurrentielle standard")

        return "; ".join(parts)
```


---

## SECTION 3 — Templates YAML des 5 dimensions

Cette section documente les 5 fichiers YAML de configuration des dimensions. Chaque fichier definit le schema d'entree, les regles SI/ALORS, et les parametres par defaut. Les fichiers sont stockes dans `config/scoring_dimensions/`.

### 3.1 Dimension 1: Cohérence Métier

**Fichier:** `config/scoring_dimensions/coherence_metier.yaml`

```yaml
dimension_id: "coherence_metier"
name: "Cohérence Métier"
version: 1
input_schema:
  - ao.cpv_code
  - ao.cpv_description
  - ao.keywords
  - enterprise.competencies
  - enterprise.cpv_whitelist
  - enterprise.sectors
  - enterprise.past_cpv_success
rules:
  - condition: "ao.cpv_code in enterprise.cpv_whitelist"
    action: "score = 100"
    score_value: 100.0
    strict: false
    explanation_template: "CPV {ao.cpv_code} dans la whitelist = score maximal"

  - condition: "ao.cpv_code[:2] in [cpv[:2] for cpv in enterprise.cpv_whitelist]"
    action: "score = 70"
    score_value: 70.0
    strict: false
    explanation_template: "CPV {ao.cpv_code} dans la même famille (2 premiers digits) = score moyen-haut"

  - condition: "len(set(ao.keywords) & set(enterprise.competencies)) >= 3"
    action: "score += 20"
    score_value: 20.0
    strict: false
    explanation_template: "{n} mots-clés en commun avec les compétences de l'entreprise (+20)"

  - condition: "ao.cpv_code in enterprise.past_cpv_success"
    action: "score += 15"
    score_value: 15.0
    strict: false
    explanation_template: "CPV déjà gagné par le passé, expérience confirmée (+15)"

  - condition: "any(sector.lower() in ao.cpv_description.lower() for sector in enterprise.sectors)"
    action: "score += 10"
    score_value: 10.0
    strict: false
    explanation_template: "Secteur d'activité mentionné dans la description du CPV (+10)"

default_score: 30.0
default_weight: 0.25
```

**Logique métier:**

| Règle | Condition | Action | Impact |
|-------|-----------|--------|--------|
| 1 | CPV dans la whitelist entreprise | `score = 100` | Score maximal — correspondance parfaite |
| 2 | CPV dans la même famille (2 digits) | `score = 70` | Bon score — proximité sectorielle |
| 3 | 3+ mots-clés en commun avec compétences | `score += 20` | Bonus alignement sémantique |
| 4 | CPV déjà gagné par le passé | `score += 15` | Bonus expérience prouvée |
| 5 | Secteur mentionné dans description CPV | `score += 10` | Bonus sectoriel mineur |

---

### 3.2 Dimension 2: Viabilité Financière

**Fichier:** `config/scoring_dimensions/viabilite_financiere.yaml`

```yaml
dimension_id: "viabilite_financiere"
name: "Viabilité Financière"
version: 1
input_schema:
  - ao.estimated_amount
  - ao.cautionnement
  - ao.cautionnement_percent
  - ao.payment_terms_days
  - enterprise.ca
  - enterprise.tresorerie
  - enterprise.ratio_endettement
  - enterprise.capital_social
  - enterprise.avg_project_size
rules:
  - condition: "ao.estimated_amount > enterprise.ca * 0.5"
    action: "score = 10"
    score_value: 10.0
    strict: false
    explanation_template: "AO représente plus de 50% du CA — risque financier majeur (score bas)"

  - condition: "enterprise.tresorerie < ao.cautionnement"
    action: "score = 5"
    score_value: 5.0
    strict: false
    explanation_template: "Trésorerie insuffisante pour couvrir le cautionnement — risque très élevé"

  - condition: "ao.cautionnement_percent > 0.05"
    action: "score -= 25"
    score_value: 25.0
    strict: false
    explanation_template: "Cautionnement supérieur à 5% du montant estimé — pénalité (-25)"

  - condition: "enterprise.ratio_endettement > 0.50"
    action: "score -= 20"
    score_value: 20.0
    strict: false
    explanation_template: "Ratio d'endettement > 50% — fragilité financière (-20)"

  - condition: "ao.estimated_amount <= enterprise.avg_project_size * 1.2"
    action: "score += 25"
    score_value: 25.0
    strict: false
    explanation_template: "AO dans la fourchette habituelle des projets (+25)"

  - condition: "ao.payment_terms_days > 60"
    action: "score -= 15"
    score_value: 15.0
    strict: false
    explanation_template: "Délai de paiement > 60 jours — impact trésorerie négatif (-15)"

  - condition: "enterprise.capital_social < ao.estimated_amount * 0.10"
    action: "score -= 20"
    score_value: 20.0
    strict: false
    explanation_template: "Capital social < 10% du montant de l'AO — capacité financière insuffisante (-20)"

default_score: 50.0
default_weight: 0.25
```

**Logique métier:**

| Règle | Condition | Action | Impact |
|-------|-----------|--------|--------|
| 1 | AO > 50% du CA | `score = 10` | Risque majeur — taille critique |
| 2 | Trésorerie < cautionnement | `score = 5` | Incapacité à cautionner |
| 3 | Cautionnement > 5% | `score -= 25` | Pénalité engagement financier |
| 4 | Endettement > 50% | `score -= 20` | Fragilité structurelle |
| 5 | AO dans fourchette habituelle | `score += 25` | Confort taille projet |
| 6 | Délai paiement > 60j | `score -= 15` | Impact trésorerie |
| 7 | Capital social < 10% AO | `score -= 20` | Sous-capitalisation |

---

### 3.3 Dimension 3: Accessibilité Géographique

**Fichier:** `config/scoring_dimensions/accessibilite_geographique.yaml`

```yaml
dimension_id: "accessibilite_geographique"
name: "Accessibilité Géographique"
version: 1
input_schema:
  - ao.location
  - ao.region
  - ao.departement
  - ao.is_remote_accepted
  - enterprise.zones_intervention
  - enterprise.departements_couverts
  - enterprise.siege_social
  - distance_km
rules:
  - condition: "ao.region not in enterprise.zones_intervention"
    action: "score = 0"
    score_value: 0.0
    strict: true
    explanation_template: "Région {ao.region} hors zones d'intervention — élimination (score 0, strict)"

  - condition: "distance_km > 300"
    action: "score = 5"
    score_value: 5.0
    strict: false
    explanation_template: "Distance > 300km — accessibilité très difficile"

  - condition: "distance_km > 200"
    action: "score -= 30"
    score_value: 30.0
    strict: false
    explanation_template: "Distance > 200km — coût logistique élevé (-30)"

  - condition: "distance_km <= 50"
    action: "score += 30"
    score_value: 30.0
    strict: false
    explanation_template: "Proximité géographique < 50km — avantage concurrentiel (+30)"

  - condition: "ao.is_remote_accepted and enterprise.has_remote_capability"
    action: "score += 20"
    score_value: 20.0
    strict: false
    explanation_template: "Télétravail accepté et capacité confirmée — flexibilité géographique (+20)"

  - condition: "ao.departement in enterprise.departements_couverts"
    action: "score += 15"
    score_value: 15.0
    strict: false
    explanation_template: "Département {ao.departement} couvert par l'entreprise (+15)"

default_score: 60.0
default_weight: 0.15
```

**Logique métier:**

| Règle | Condition | Action | Impact |
|-------|-----------|--------|--------|
| 1 | Région hors zones | `score = 0` (strict) | Élimination immédiate |
| 2 | Distance > 300km | `score = 5` | Quasi-inaccessible |
| 3 | Distance > 200km | `score -= 30` | Pénalité logistique |
| 4 | Distance <= 50km | `score += 30` | Avantage proximité |
| 5 | Télétravail possible | `score += 20` | Flexibilité |
| 6 | Département couvert | `score += 15` | Couverture confirmée |

---

### 3.4 Dimension 4: Faisabilité Temporelle

**Fichier:** `config/scoring_dimensions/faisabilite_temporelle.yaml`

```yaml
dimension_id: "faisabilite_temporelle"
name: "Faisabilité Temporelle"
version: 1
input_schema:
  - ao.date_publication
  - ao.date_limite
  - ao.date_debut_prestation
  - ao.duree_mois
  - ao.complexite_estimee
  - enterprise.delai_preparation_jours
  - enterprise.avg_response_time_days
  - enterprise.current_workload
  - jours_restants
rules:
  - condition: "jours_restants < enterprise.delai_preparation_jours"
    action: "score = 5"
    score_value: 5.0
    strict: false
    explanation_template: "Délai insuffisant pour préparer une réponse de qualité — risque élevé"

  - condition: "jours_restants > enterprise.delai_preparation_jours * 2"
    action: "score = 100"
    score_value: 100.0
    strict: false
    explanation_template: "Délai confortable (>2x le délai de préparation) — score maximal"

  - condition: "jours_restants < 7"
    action: "score -= 40"
    score_value: 40.0
    strict: false
    explanation_template: "Moins de 7 jours restants — urgence extrême, qualité compromise (-40)"

  - condition: "enterprise.current_workload > 0.8"
    action: "score -= 25"
    score_value: 25.0
    strict: false
    explanation_template: "Charge de travail > 80% — capacité limitée pour répondre (-25)"

  - condition: "ao.complexite_estimee == 'elevee' and jours_restants < 14"
    action: "score -= 30"
    score_value: 30.0
    strict: false
    explanation_template: "AO complexe avec moins de 14 jours — préparation inadéquate (-30)"

  - condition: "enterprise.avg_response_time_days < jours_restants * 0.5"
    action: "score += 15"
    score_value: 15.0
    strict: false
    explanation_template: "Historique de réponse rapide par rapport au délai disponible (+15)"

  - condition: "ao.duree_mois > 24 and enterprise.pmi_flag"
    action: "score -= 15"
    score_value: 15.0
    strict: false
    explanation_template: "Prestation longue (>24 mois) pour une PMI — risque ressources (-15)"

default_score: 50.0
default_weight: 0.20
```

**Logique métier:**

| Règle | Condition | Action | Impact |
|-------|-----------|--------|--------|
| 1 | Délai < préparation requise | `score = 5` | Délai insuffisant |
| 2 | Délai > 2x préparation | `score = 100` | Délai confortable |
| 3 | < 7 jours restants | `score -= 40` | Urgence extrême |
| 4 | Charge > 80% | `score -= 25` | Saturé |
| 5 | Complexe + < 14j | `score -= 30` | Double pénalité |
| 6 | Historique rapide | `score += 15` | Capacité prouvée |
| 7 | Long contrat + PMI | `score -= 15` | Risque ressources |

---

### 3.5 Dimension 5: Intelligence Concurrentielle

**Fichier:** `config/scoring_dimensions/intelligence_concurrentielle.yaml`

```yaml
dimension_id: "intelligence_concurrentielle"
name: "Intelligence Concurrentielle"
version: 1
input_schema:
  - ao.nb_concurrents_estime
  - ao.barrieres_entree
  - ao.type_marche
  - ao.avis_precedent_exists
  - enterprise.positionnement
  - enterprise.certifications
  - enterprise.references_significatives
  - enterprise.past_wins_same_type
rules:
  - condition: "ao.nb_concurrents_estime > 15"
    action: "score = 10"
    score_value: 10.0
    strict: false
    explanation_template: "Plus de 15 concurrents estimés — concurrence intense, faible probabilité"

  - condition: "ao.nb_concurrents_estime > 10"
    action: "score -= 30"
    score_value: 30.0
    strict: false
    explanation_template: "10 à 15 concurrents — forte concurrence (-30)"

  - condition: "ao.nb_concurrents_estime <= 5"
    action: "score += 25"
    score_value: 25.0
    strict: false
    explanation_template: "Moins de 5 concurrents estimés — niche intéressante (+25)"

  - condition: "ao.barrieres_entree == 'elevee' and len(enterprise.certifications) >= 3"
    action: "score += 25"
    score_value: 25.0
    strict: false
    explanation_template: "Barrières à l'entrée élevées et certifications solides — avantage compétitif (+25)"

  - condition: "ao.barrieres_entree == 'faible' and enterprise.positionnement == 'premium'"
    action: "score -= 20"
    score_value: 20.0
    strict: false
    explanation_template: "Positionnement premium sur marché sans barrières — désavantage (-20)"

  - condition: "ao.type_marche in enterprise.past_wins_same_type"
    action: "score += 15"
    score_value: 15.0
    strict: false
    explanation_template: "Type de marché déjà remporté par le passé — expérience validée (+15)"

  - condition: "enterprise.references_significatives >= 3 and ao.estimated_amount > 100000"
    action: "score += 20"
    score_value: 20.0
    strict: false
    explanation_template: "Références significatives pour un gros montant — crédibilité (+20)"

  - condition: "ao.avis_precedent_exists and ao.past_award_price"
    action: "score += 10"
    score_value: 10.0
    strict: false
    explanation_template: "Avis précédent disponible avec prix d'attribution — intelligence concurrentielle (+10)"

default_score: 40.0
default_weight: 0.15
```

**Logique métier:**

| Règle | Condition | Action | Impact |
|-------|-----------|--------|--------|
| 1 | 15+ concurrents | `score = 10` | Concurrence intense |
| 2 | 10-15 concurrents | `score -= 30` | Forte concurrence |
| 3 | <= 5 concurrents | `score += 25` | Niche intéressante |
| 4 | Barrières élevées + certifications | `score += 25` | Avantage protégé |
| 5 | Premium + sans barrières | `score -= 20` | Désavantage positionnement |
| 6 | Type de marché déjà gagné | `score += 15` | Expérience prouvée |
| 7 | 3+ références + gros montant | `score += 20` | Crédibilité |
| 8 | Avis précédent disponible | `score += 10` | Info concurrentielle |

---

### 3.6 Résumé des configurations YAML

| Dimension | Règles | Poids | Score défaut | Strict |
|-----------|--------|-------|--------------|--------|
| Cohérence Métier | 5 | 0.25 | 30 | Non |
| Viabilité Financière | 7 | 0.25 | 50 | Non |
| Accessibilité Géographique | 6 | 0.15 | 60 | Oui (règle 1) |
| Faisabilité Temporelle | 7 | 0.20 | 50 | Non |
| Intelligence Concurrentielle | 8 | 0.15 | 40 | Non |
| **Total** | **33** | **1.00** | | |

---

## SECTION 4 — Schéma JSON ScoreCard de sortie

### 4.1 Spécification JSON Schema

Le schéma JSON suivant définit la structure de la `ScoreCard` retournée par le moteur. Ce schéma est utilisé pour la validation côté client et la documentation OpenAPI.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ScoreCard",
  "description": "Résultat complet du scoring — sortie standardisée du Scoring Engine V2",
  "type": "object",
  "required": [
    "tender_id", "profile", "total_score", "verdict",
    "breakdowns", "global_explanation", "scored_at", "engine_version"
  ],
  "properties": {
    "tender_id": {
      "type": "string",
      "format": "uuid",
      "description": "UUID de l'AO évalué"
    },
    "profile": {
      "type": "string",
      "enum": ["prudent", "opportuniste", "specialise"],
      "description": "Profil de scoring utilisé"
    },
    "total_score": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 100.0,
      "description": "Score total pondéré (0-100)"
    },
    "verdict": {
      "type": "string",
      "enum": ["GO", "MAYBE", "NO-GO"],
      "description": "Décision finale"
    },
    "breakdowns": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/ScoreBreakdown"
      },
      "description": "Détail du score par dimension"
    },
    "global_explanation": {
      "type": "string",
      "description": "Explication synthétique en langage naturel (XAI)"
    },
    "metadata": {
      "type": "object",
      "description": "Métadonnées techniques",
      "properties": {
        "engine_version": { "type": "string" },
        "dimensions_count": { "type": "integer" },
        "dimensions_evaluated": { "type": "integer" },
        "thresholds": {
          "type": "object",
          "properties": {
            "go": { "type": "number" },
            "maybe": { "type": "number" }
          }
        }
      }
    },
    "scored_at": {
      "type": "string",
      "format": "date-time",
      "description": "Timestamp ISO 8601 de l'évaluation"
    },
    "engine_version": {
      "type": "string",
      "description": "Version du moteur de scoring"
    }
  },
  "definitions": {
    "ScoreBreakdown": {
      "type": "object",
      "required": [
        "dimension_id", "dimension_name", "raw_score",
        "weighted_score", "weight", "explanation"
      ],
      "properties": {
        "dimension_id": {
          "type": "string",
          "description": "Identifiant de la dimension"
        },
        "dimension_name": {
          "type": "string",
          "description": "Nom d'affichage de la dimension"
        },
        "raw_score": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 100.0,
          "description": "Score brut (0-100)"
        },
        "weighted_score": {
          "type": "number",
          "description": "Score pondéré (raw * weight)"
        },
        "weight": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0,
          "description": "Poids appliqué"
        },
        "rules_applied": {
          "type": "array",
          "items": {
            "$ref": "#/definitions/RuleApplied"
          },
          "description": "Règles SI/ALORS déclenchées"
        },
        "explanation": {
          "type": "string",
          "description": "Explication de la dimension"
        }
      }
    },
    "RuleApplied": {
      "type": "object",
      "required": ["condition", "action", "result_score", "strict"],
      "properties": {
        "condition": {
          "type": "string",
          "description": "Condition Python évaluée"
        },
        "action": {
          "type": "string",
          "description": "Action exécutée sur le score"
        },
        "result_score": {
          "type": "number",
          "description": "Score après application"
        },
        "strict": {
          "type": "boolean",
          "description": "Règle en mode strict"
        }
      }
    }
  }
}
```

### 4.2 Exemple de ScoreCard (JSON)

```json
{
  "tender_id": "550e8400-e29b-41d4-a716-446655440000",
  "profile": "prudent",
  "total_score": 78.5,
  "verdict": "GO",
  "breakdowns": [
    {
      "dimension_id": "coherence_metier",
      "dimension_name": "Cohérence Métier",
      "raw_score": 95.0,
      "weighted_score": 23.75,
      "weight": 0.25,
      "rules_applied": [
        {
          "condition": "ao.cpv_code in enterprise.cpv_whitelist",
          "action": "score = 100",
          "result_score": 100,
          "strict": false
        },
        {
          "condition": "ao.cpv_code in enterprise.past_cpv_success",
          "action": "score += 15",
          "result_score": 100,
          "strict": false
        }
      ],
      "explanation": "CPV 45310000 dans la whitelist = score maximal; CPV déjà gagné par le passé, expérience confirmée (+15)"
    },
    {
      "dimension_id": "viabilite_financiere",
      "dimension_name": "Viabilité Financière",
      "raw_score": 75.0,
      "weighted_score": 18.75,
      "weight": 0.25,
      "rules_applied": [
        {
          "condition": "ao.estimated_amount <= enterprise.avg_project_size * 1.2",
          "action": "score += 25",
          "result_score": 75.0,
          "strict": false
        }
      ],
      "explanation": "AO dans la fourchette habituelle des projets (+25); Trésorerie suffisante"
    },
    {
      "dimension_id": "accessibilite_geographique",
      "dimension_name": "Accessibilité Géographique",
      "raw_score": 90.0,
      "weighted_score": 13.50,
      "weight": 0.15,
      "rules_applied": [
        {
          "condition": "distance_km <= 50",
          "action": "score += 30",
          "result_score": 90.0,
          "strict": false
        }
      ],
      "explanation": "Région IDF couverte; Distance: 35 km; Proximité géographique < 50km — avantage concurrentiel (+30)"
    },
    {
      "dimension_id": "faisabilite_temporelle",
      "dimension_name": "Faisabilité Temporelle",
      "raw_score": 100.0,
      "weighted_score": 20.00,
      "weight": 0.20,
      "rules_applied": [
        {
          "condition": "jours_restants > enterprise.delai_preparation_jours * 2",
          "action": "score = 100",
          "result_score": 100.0,
          "strict": false
        }
      ],
      "explanation": "42 jours restants (délai préparation: 14 jours, ratio: 3.0x); Délai confortable"
    },
    {
      "dimension_id": "intelligence_concurrentielle",
      "dimension_name": "Intelligence Concurrentielle",
      "raw_score": 65.0,
      "weighted_score": 9.75,
      "weight": 0.15,
      "rules_applied": [
        {
          "condition": "ao.nb_concurrents_estime <= 5",
          "action": "score += 25",
          "result_score": 65.0,
          "strict": false
        }
      ],
      "explanation": "Concurrence limitée (4 estimés); Niche intéressante (+25)"
    }
  ],
  "global_explanation": "L'AO est recommandé (GO, score 78.5%) car : la cohérence métier est excellente (95%) avec CPV dans la whitelist et déjà gagné par le passé; la viabilité financière est bonne (75%) avec un montant dans la fourchette habituelle; la faisabilité temporelle est optimale (100%) avec un délai confortable de 42 jours.",
  "metadata": {
    "engine_version": "2.0.0",
    "dimensions_count": 5,
    "dimensions_evaluated": 5,
    "thresholds": {
      "go": 0.70,
      "maybe": 0.45
    }
  },
  "scored_at": "2025-01-20T10:30:00+00:00",
  "engine_version": "2.0.0"
}
```

### 4.3 Sérialisation Pydantic

La `ScoreCard` est un modèle Pydantic v2 qui se sérialise naturellement :

```python
# Sérialisation JSON
json_output = scorecard.model_dump_json(indent=2)

# Sérialisation dict (pour JSONResponse FastAPI)
dict_output = scorecard.model_dump(mode="json")

# Stockage en base (JSONB PostgreSQL)
# await db.execute(
#     "UPDATE tenders SET score_card_json = $1 WHERE id = $2",
#     dict_output, tender_id
# )
```

---

## SECTION 5 — Intégration avec l'existant

### 5.1 Modèle de données — Migrations SQL

#### Migration: `alembic/versions/20250120_add_scoring_v2.sql`

```sql
-- ============================================================
-- Migration: Scoring Engine V2 — Tables et colonnes
-- ============================================================

-- 1. Nouvelle table: scoring_dimensions
-- Remplace et étend la table legacy qualification_rules
CREATE TABLE IF NOT EXISTS scoring_dimensions (
    id              SERIAL PRIMARY KEY,
    dimension_id    VARCHAR(50) NOT NULL UNIQUE,
    name            VARCHAR(100) NOT NULL,
    version         INT DEFAULT 1,
    config_yaml     TEXT NOT NULL,
    default_weight  DECIMAL(3,2) NOT NULL DEFAULT 0.20,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE scoring_dimensions IS
    'Configuration des dimensions de scoring V2 (YAML stocké en texte)';

-- 2. Nouvelle table: scoring_feedback
CREATE TABLE IF NOT EXISTS scoring_feedback (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tender_id           UUID NOT NULL REFERENCES tenders(id) ON DELETE CASCADE,
    user_id             UUID NOT NULL REFERENCES users(id),
    profile             VARCHAR(20) NOT NULL,
    predicted_verdict   VARCHAR(10) NOT NULL,
    actual_verdict      VARCHAR(10) NOT NULL,
    override_reason     TEXT,
    dimension_scores    JSONB DEFAULT '{}',
    score_card_snapshot JSONB,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_scoring_feedback_tender ON scoring_feedback(tender_id);
CREATE INDEX idx_scoring_feedback_user ON scoring_feedback(user_id);
CREATE INDEX idx_scoring_feedback_created ON scoring_feedback(created_at);

COMMENT ON TABLE scoring_feedback IS
    'Feedback utilisateur pour la boucle d apprentissage du scoring';

-- 3. Nouvelles colonnes sur tenders
ALTER TABLE tenders
    ADD COLUMN IF NOT EXISTS scoring_profile VARCHAR(20)
        DEFAULT 'specialise'
        CHECK (scoring_profile IN ('prudent', 'opportuniste', 'specialise')),
    ADD COLUMN IF NOT EXISTS score_card_json JSONB,
    ADD COLUMN IF NOT EXISTS scored_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS score_engine_version VARCHAR(10)
        DEFAULT '2.0.0';

CREATE INDEX idx_tenders_score_card ON tenders USING GIN(score_card_json);
CREATE INDEX idx_tenders_profile ON tenders(scoring_profile);

-- 4. Migration des données legacy
-- Copier les règles existantes vers la nouvelle structure
INSERT INTO scoring_dimensions (dimension_id, name, config_yaml, default_weight)
SELECT
    'legacy_' || id::text,
    COALESCE(name, 'Règle legacy ' || id::text),
    '{"migrated": true, "legacy_id": ' || id::text || '}',
    0.20
FROM qualification_rules
WHERE NOT EXISTS (
    SELECT 1 FROM scoring_dimensions WHERE dimension_id = 'legacy_' || qualification_rules.id::text
);

-- 5. Vue pour compatibilité
CREATE OR REPLACE VIEW scoring_summary AS
SELECT
    t.id AS tender_id,
    t.scoring_profile,
    t.score_card_json->>'total_score' AS total_score,
    t.score_card_json->>'verdict' AS verdict,
    t.scored_at,
    (t.score_card_json->>'breakdowns')::jsonb AS breakdowns
FROM tenders t
WHERE t.score_card_json IS NOT NULL;

-- 6. Trigger pour updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_scoring_dimensions_updated_at
    BEFORE UPDATE ON scoring_dimensions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 5.2 Endpoint API FastAPI

#### Fichier: `app/api/v1/endpoints/scoring.py`

```python
"""Endpoints API pour le Scoring Engine V2.

Fournit les routes REST pour qualifier un AO, consulter son score,
et soumettre du feedback utilisateur.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.types.scoring import (
    FeedbackEntry,
    ScoreCard,
    ScoringProfile,
)
from app.deps import get_scoring_engine, get_feedback_loop

router = APIRouter(prefix="/tenders", tags=["scoring"])


@router.post(
    "/{tender_id}/qualify",
    response_model=dict[str, Any],
    summary="Qualifier un AO avec le Scoring Engine V2",
    description="Évalue un appel d'offres selon les 5 dimensions de scoring.
        Retourne une ScoreCard complète avec verdict et explications.",
)
async def qualify_tender(
    tender_id: str,
    profile: Annotated[
        ScoringProfile,
        Query(description="Profil de scoring à utiliser"),
    ] = ScoringProfile.SPECIALISE,
    engine: ScoringEngine = Depends(get_scoring_engine),
) -> dict[str, Any]:
    """Qualifie un AO et retourne la ScoreCard.

    Args:
        tender_id: UUID de l'AO à qualifier.
        profile: Profil de scoring (prudent/opportuniste/specialise).
        engine: Instance du ScoringEngine (injection de dépendance).

    Returns:
        ScoreCard serialisée en JSON.

    Raises:
        HTTPException 404: Si l'AO n'existe pas.
        HTTPException 422: Si les données sont insuffisantes.
    """
    # Charger les données de l'AO et de l'entreprise
    # TODO: Remplacer par les vraies queries DB
    ao_data = await _load_ao_data(tender_id)
    if not ao_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AO non trouvé: {tender_id}",
        )

    enterprise_id = ao_data.get("enterprise_id")
    enterprise_data = await _load_enterprise_data(enterprise_id)

    # Évaluer
    scorecard = await engine.evaluate(
        tender_id=tender_id,
        ao_data=ao_data,
        enterprise_data=enterprise_data,
        profile=profile,
    )

    # Persister en base
    await _persist_scorecard(tender_id, scorecard)

    return scorecard.to_dict()


@router.post(
    "/{tender_id}/feedback",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soumettre un feedback utilisateur",
    description="Permet à l'utilisateur de corriger le verdict prédit
        pour améliorer le moteur de scoring.",
)
async def submit_feedback(
    tender_id: str,
    feedback: FeedbackEntry,
    loop: FeedbackLoop = Depends(get_feedback_loop),
) -> None:
    """Enregistre un feedback utilisateur.

    Args:
        tender_id: UUID de l'AO concerné.
        feedback: Entrée de feedback avec verdict réel et raison.
        loop: Instance du FeedbackLoop.

    Raises:
        HTTPException 400: Si le feedback est invalide.
    """
    if feedback.tender_id != tender_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le tender_id du feedback ne correspond pas à l'URL",
        )

    await loop.record_feedback(feedback)


@router.get(
    "/{tender_id}/score",
    response_model=dict[str, Any],
    summary="Consulter le score d'un AO",
)
async def get_score(
    tender_id: str,
) -> dict[str, Any]:
    """Retourne la ScoreCard stockée pour un AO.

    Args:
        tender_id: UUID de l'AO.

    Returns:
        ScoreCard depuis la base de données.

    Raises:
        HTTPException 404: Si l'AO n'a pas encore été scoré.
    """
    # TODO: Query DB
    score_card = await _load_scorecard(tender_id)
    if not score_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AO non scoré: {tender_id}",
        )
    return score_card


@router.get(
    "/{tender_id}/score/explain",
    response_model=str,
    summary="Explication textuelle du score",
)
async def explain_score(
    tender_id: str,
    lang: str = Query(default="fr", enum=["fr", "en"]),
    explainer: Explainer = Depends(get_explainer),
) -> str:
    """Retourne l'explication XAI du score en langage naturel.

    Args:
        tender_id: UUID de l'AO.
        lang: Langue de l'explication (fr/en).
        explainer: Instance de l'Explainer.

    Returns:
        Explication textuelle.
    """
    scorecard_dict = await _load_scorecard(tender_id)
    if not scorecard_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AO non scoré: {tender_id}",
        )

    scorecard = ScoreCard(**scorecard_dict)
    return await explainer.explain(scorecard, lang=lang)


# ──────────────────────────────────────────────────────────────
# Helpers (TODO: à remplacer par les vraies implémentations)
# ──────────────────────────────────────────────────────────────

async def _load_ao_data(tender_id: str) -> dict[str, Any] | None:
    """Charge les données d'un AO depuis la base."""
    # TODO: Implementer avec SQLAlchemy
    return {}


async def _load_enterprise_data(enterprise_id: str) -> dict[str, Any]:
    """Charge les données d'une entreprise depuis la base."""
    # TODO: Implementer avec SQLAlchemy
    return {}


async def _persist_scorecard(
    tender_id: str, scorecard: ScoreCard
) -> None:
    """Persiste la ScoreCard en base de données."""
    # TODO: Implementer avec SQLAlchemy
    pass


async def _load_scorecard(
    tender_id: str,
) -> dict[str, Any] | None:
    """Charge la ScoreCard stockée pour un AO."""
    # TODO: Implementer avec SQLAlchemy
    return None
```

### 5.3 Dépendances (deps.py)

```python
"""Dépendances FastAPI pour le Scoring Engine V2.

Fournit les factories d'injection de dépendances pour le ScoringEngine,
le FeedbackLoop, et les composants annexes.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

from app.services.scoring.balancer import WeightBalancer
from app.services.scoring.engine import ScoringEngine
from app.services.scoring.explainer import Explainer
from app.services.scoring.feedback import FeedbackLoop
from app.services.scoring.registry import RuleRegistry
from app.services.scoring.thresholds import ThresholdManager


@lru_cache
def get_registry() -> RuleRegistry:
    """Retourne le RuleRegistry (singleton).

    Le registre charge les dimensions depuis le répertoire YAML
    configuré. L'instance est mise en cache (singleton).
    """
    registry = RuleRegistry()
    yaml_dir = os.getenv(
        "SCORING_DIMENSIONS_DIR",
        "/app/config/scoring_dimensions",
    )
    registry.load_dimensions(yaml_dir)
    return registry


@lru_cache
def get_threshold_manager() -> ThresholdManager:
    """Retourne le ThresholdManager (singleton)."""
    return ThresholdManager()


@lru_cache
def get_balancer() -> WeightBalancer:
    """Retourne le WeightBalancer (singleton)."""
    registry = get_registry()
    return WeightBalancer(registry)


@lru_cache
def get_explainer() -> Explainer:
    """Retourne l'Explainer (singleton)."""
    return Explainer()


def get_scoring_engine() -> ScoringEngine:
    """Retourne le ScoringEngine (factory).

    Construit le moteur avec toutes ses dépendances injectées.
    """
    return ScoringEngine(
        registry=get_registry(),
        threshold_manager=get_threshold_manager(),
        balancer=get_balancer(),
        explainer=get_explainer(),
    )


def get_feedback_loop() -> FeedbackLoop:
    """Retourne le FeedbackLoop (factory).

    TODO: Brancher le vrai repository de persistance.
    """
    # Placeholder: repository en mémoire
    from unittest.mock import AsyncMock
    mock_repo = AsyncMock()
    return FeedbackLoop(repository=mock_repo)
```

### 5.4 Rétrocompatibilité

Le scoring V1 (legacy) reste accessible via le paramètre `?engine=legacy` :

```python
@router.post("/{tender_id}/qualify")
async def qualify_tender(
    tender_id: str,
    profile: ScoringProfile = ScoringProfile.SPECIALISE,
    engine: str = Query(default="v2", enum=["v2", "legacy"]),
    # ...
) -> dict[str, Any]:
    if engine == "legacy":
        # Déléguer à l'ancien moteur
        return await legacy_qualify(tender_id, profile)
    # Sinon: ScoringEngine V2
    scorecard = await scoring_engine.evaluate(...)
    return scorecard.to_dict()
```

### 5.5 Configuration environnement

```env
# Scoring Engine V2
SCORING_DIMENSIONS_DIR=/app/config/scoring_dimensions
SCORING_DEFAULT_PROFILE=specialise
SCORING_MIN_GAP_THRESHOLD=0.15
SCORING_FEEDBACK_ENABLED=true
SCORING_FEEDBACK_MIN_ENTRIES=10
```

---

## SECTION 6 — Phasing d'implementation

### 6.1 Roadmap

| Version | Feature | Fichiers | Priorité |
|---------|---------|----------|----------|
| **v0.1** | Scoring regles hardcodees (MVP legacy) | `rules_engine.py` | Done |
| **v0.4** | Scoring V2 — 5 dimensions hardcodees | `engine.py` + 5 plugins | High |
| **v0.5** | Scoring V2 — YAML configurable | `registry.py` + `config/dimensions/*.yaml` | High |
| **v1.0** | Scoring V2 — FeedbackLoop actif | `feedback.py` + ajustement auto | Medium |
| **v1.1** | Scoring V2 — Nouvelles dimensions | Nouveaux YAML plugins (RSE, Innovation) | Low |

### 6.2 Détail par phase

#### Phase 1: v0.4 — Plugins hardcodés (Sprint courant)

**Objectif:** Avoir un moteur fonctionnel avec les 5 dimensions en code Python, sans YAML.

**Livrables:**
- [x] `app/core/types/scoring.py` — Types et modèles Pydantic
- [x] `app/services/scoring/engine.py` — ScoringEngine + AbstractDimensionPlugin
- [x] 5 plugins concrets (`plugins/*.py`) avec règles en dur
- [x] Tests unitaires par plugin (mock data)

**Indicateur de succès:** Le moteur produit une ScoreCard valide avec les 5 dimensions.

#### Phase 2: v0.5 — YAML configurable (Sprint suivant)

**Objectif:** Externaliser les règles dans des fichiers YAML modifiables sans redéploiement.

**Livrables:**
- [x] `app/services/scoring/registry.py` — RuleRegistry
- [x] 5 fichiers YAML dans `config/scoring_dimensions/`
- [x] Hot-reload des dimensions en dev
- [x] Validation YAML au chargement

**Indicateur de succès:** Modifier un YAML et recharger suffit pour changer le comportement.

#### Phase 3: v1.0 — FeedbackLoop (Sprint +2)

**Objectif:** Apprendre des corrections utilisateur pour améliorer la précision.

**Livrables:**
- [x] `app/services/scoring/feedback.py` — FeedbackLoop
- [x] `app/services/scoring/balancer.py` — WeightBalancer
- [x] `app/services/scoring/thresholds.py` — ThresholdManager
- [x] Table `scoring_feedback` + migrations
- [x] Endpoint `POST /tenders/{id}/feedback`

**Indicateur de succès:** Taux d'override < 15% apres 100 feedbacks.

#### Phase 4: v1.1 — Extensions (Futur)

**Objectif:** Ajouter de nouvelles dimensions sans modifier le cœur.

**Dimensions candidates:**
- **RSE** (Responsabilité Sociale): clauses environnementales, achats responsables
- **Innovation**: R&D, brevets, partenariats recherche
- **Cybersecurite**: certifications, niveaux de securite requis
- **Soustraitance**: capacite a sous-traiter, reseau de partenaires

**Mécanisme:** Créer un fichier YAML + une classe plugin → enregistrer dans le registry.

### 6.3 Tests recommandés

```python
"""Tests du Scoring Engine V2.

Usage: pytest tests/services/scoring/ -v
"""

import pytest

from app.core.types.scoring import ScoreVerdict, ScoringProfile
from app.services.scoring.engine import ScoringEngine


@pytest.mark.asyncio
class TestScoringEngine:
    """Tests d'intégration du ScoringEngine."""

    async def test_full_evaluation_go(self, scoring_engine):
        """Un AO parfaitement aligné doit recevoir GO."""
        ao_data = {
            "cpv_code": "45310000",
            "cpv_description": "Travaux de construction",
            "keywords": ["construction", "batiment", "genie_civil"],
            "estimated_amount": 150000,
            "cautionnement": 7500,
            "cautionnement_percent": 0.05,
            "payment_terms_days": 30,
            "region": "IDF",
            "departement": "75",
            "is_remote_accepted": True,
            "date_limite": "2025-03-01T12:00:00Z",
            "duree_mois": 12,
            "complexite_estimee": "moyenne",
            "nb_concurrents_estime": 4,
            "barrieres_entree": "elevee",
            "type_marche": "mapa",
        }
        enterprise_data = {
            "cpv_whitelist": ["45310000", "45320000"],
            "competencies": ["construction", "batiment", "genie_civil", "electricite"],
            "sectors": ["BTP"],
            "past_cpv_success": ["45310000"],
            "ca": 2000000,
            "tresorerie": 500000,
            "ratio_endettement": 0.30,
            "capital_social": 100000,
            "avg_project_size": 180000,
            "zones_intervention": ["IDF", "HDF"],
            "departements_couverts": ["75", "92", "93", "94"],
            "siege_social": {"lat": 48.8566, "lon": 2.3522},
            "has_remote_capability": True,
            "delai_preparation_jours": 14,
            "avg_response_time_days": 10,
            "current_workload": 0.5,
            "positionnement": "premium",
            "certifications": ["ISO9001", "ISO14001", "MASE"],
            "references_significatives": 5,
            "past_wins_same_type": ["mapa", "appel_offres_ouvert"],
        }

        scorecard = await scoring_engine.evaluate(
            tender_id="test-uuid",
            ao_data=ao_data,
            enterprise_data=enterprise_data,
            profile=ScoringProfile.SPECIALISE,
        )

        assert scorecard.total_score > 65.0
        assert scorecard.verdict == ScoreVerdict.GO
        assert len(scorecard.breakdowns) == 5
        assert scorecard.tender_id == "test-uuid"

    async def test_no_go_region_hors_zone(self, scoring_engine):
        """Un AO hors zone doit recevoir NO-GO."""
        ao_data = {
            "cpv_code": "45310000",
            "region": "DOMTOM",
            "date_limite": "2025-03-01T12:00:00Z",
            "nb_concurrents_estime": 5,
            "barrieres_entree": "moyenne",
        }
        enterprise_data = {
            "cpv_whitelist": ["45310000"],
            "competencies": ["construction"],
            "zones_intervention": ["IDF"],
            "departements_couverts": ["75"],
            "ca": 2000000,
            "tresorerie": 500000,
            "delai_preparation_jours": 14,
            "current_workload": 0.5,
            "positionnement": "standard",
            "certifications": ["ISO9001"],
            "references_significatives": 2,
            "past_wins_same_type": [],
        }

        scorecard = await scoring_engine.evaluate(
            tender_id="test-uuid-2",
            ao_data=ao_data,
            enterprise_data=enterprise_data,
        )

        # La dimension géographique doit avoir un score de 0 (strict)
        geo = [b for b in scorecard.breakdowns
               if b.dimension_id == "accessibilite_geographique"][0]
        assert geo.raw_score == 0.0

    async def test_scorecard_serialization(self, scoring_engine):
        """La ScoreCard doit se sérialiser correctement en JSON."""
        scorecard = await scoring_engine.evaluate(
            tender_id="test-uuid-3",
            ao_data={"cpv_code": "45310000"},
            enterprise_data={"cpv_whitelist": ["45310000"]},
        )

        json_str = scorecard.to_json()
        assert "tender_id" in json_str
        assert "verdict" in json_str

        dict_data = scorecard.to_dict()
        assert dict_data["engine_version"] == "2.0.0"
        assert "scored_at" in dict_data


@pytest.mark.asyncio
class TestThresholdManager:
    """Tests du ThresholdManager."""

    def test_threshold_prudent(self):
        from app.services.scoring.thresholds import ThresholdManager
        mgr = ThresholdManager()
        t = mgr.get_thresholds(ScoringProfile.PRUDENT)

        assert t.go == 0.70
        assert t.maybe == 0.45
        assert t.resolve(0.75) == ScoreVerdict.GO
        assert t.resolve(0.50) == ScoreVerdict.MAYBE
        assert t.resolve(0.30) == ScoreVerdict.NO_GO

    def test_threshold_opportuniste(self):
        from app.services.scoring.thresholds import ThresholdManager
        mgr = ThresholdManager()
        t = mgr.get_thresholds(ScoringProfile.OPPORTUNISTE)

        assert t.go == 0.55
        assert t.maybe == 0.30

    def test_invalid_threshold_raises(self):
        from app.core.types.scoring import ThresholdConfig
        with pytest.raises(ValueError):
            ThresholdConfig(go=0.40, maybe=0.50)  # maybe >= go
```

### 6.4 Checklist de validation

Avant mise en production du Scoring V2 :

- [ ] Les 5 plugins produisent des scores cohérents (0-100)
- [ ] La somme des poids pondérés est proche de 1.0
- [ ] Les règles `strict` arrêtent correctement l'évaluation
- [ ] La sérialisation JSON de ScoreCard est valide
- [ ] Les explications XAI sont compréhensibles
- [ ] Le feedback est persisté en base
- [ ] La rétrocompatibilité `?engine=legacy` fonctionne
- [ ] Les migrations SQL s'appliquent sans erreur
- [ ] Les tests unitaires passent (>80% coverage)
- [ ] Les tests d'intégration passent

---

## Annexe A — Glossaire

| Terme | Definition |
|-------|------------|
| **AO** | Appel d'Offres — consultation publique pour attribuer un marché |
| **CPV** | Common Procurement Vocabulary — code européen normalisé |
| **ScoreCard** | Document de sortie standardisé avec score et explications |
| **XAI** | Explainable AI — IA explicable, capacite a expliquer les decisions |
| **Dimension** | Axe d'evaluation du scoring (ex: viabilite financiere) |
| **Breakdown** | Detail du score pour une dimension |
| **Verdict** | Decision finale: GO, MAYBE, NO-GO |
| **Override** | Correction manuelle du verdict par l'utilisateur |
| **FeedbackLoop** | Boucle d'apprentissage basee sur les corrections |
| **Registry** | Registre central des composants plugin |
| **YAML** | Format de configuration declaratif |

## Annexe B — Arborescence des fichiers

```
app/
├── core/
│   └── types/
│       └── scoring.py              # Types Pydantic fondamentaux
├── services/
│   └── scoring/
│       ├── __init__.py
│       ├── engine.py               # ScoringEngine + AbstractDimensionPlugin
│       ├── registry.py             # RuleRegistry
│       ├── balancer.py             # WeightBalancer
│       ├── explainer.py            # Explainer (XAI)
│       ├── feedback.py             # FeedbackLoop
│       ├── thresholds.py           # ThresholdManager
│       └── plugins/
│           ├── __init__.py
│           ├── coherence_metier.py
│           ├── viabilite_financiere.py
│           ├── accessibilite_geographique.py
│           ├── faisabilite_temporelle.py
│           └── intelligence_concurrentielle.py
├── api/
│   └── v1/
│       └── endpoints/
│           └── scoring.py          # Endpoints REST
├── config/
│   └── scoring_dimensions/
│       ├── coherence_metier.yaml
│       ├── viabilite_financiere.yaml
│       ├── accessibilite_geographique.yaml
│       ├── faisabilite_temporelle.yaml
│       └── intelligence_concurrentielle.yaml
└── deps.py                         # Injection de dependances
```

---

*Document produit par l'Architecte ML — TAKA OS.*  
*Mis a jour: 2025-01-20 — Version 2.0.0*
