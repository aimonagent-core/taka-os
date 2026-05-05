# Benchmark Complet TAKA Vision
## Modèles VLA/VLM pour Computer Use — TAKA OS v1.2

> Document de référence technique pour la sélection de provider VLA.  
> Version : 1.0 — Juin 2026.  
> Statut : Validé sur benchmarks publics (ScreenSpot, WebClick, WebVoyager, OSWorld).

---

## 1. Synthèse exécutive

TAKA Vision doit couvrir 6 cas d'usage distincts : navigation web sur portails d'appels d'offres, localisation précise d'éléments UI (boutons, champs, menus déroulants), OCR multilingue sur documents administratifs, veille concurrentielle visuelle, remplissage de formulaires legacy, et dépôt automatisé sur plateformes propriétaires. Aucun modèle VLA unique ne domine tous ces axes. Le cho optimal est **multi-provider avec fallback automatique**.

---

## 2. Inventaire des modèles évalués

| Modèle | Taille | Architecture | Licence | Statut |
|--------|--------|-------------|---------|--------|
| **Holo1.5-3B** | 3B | Dense | Qwen Research (NC) | Self-host |
| **Holo1.5-7B** | 7B | Dense | Apache 2.0 | Self-host |
| **Holo1.5-72B** | 72B | Dense | Research only | API payante |
| **Holo3-35B-A3B** | 35B MoE (3B actives) | MoE | Apache 2.0 | Cloud API |
| **Qwen3 VL 235B** | 235B MoE (22B actives) | MoE | Apache 2.0 | API / Cloud GPU |
| **Kimi K2.5** | 1T MoE (32B actives) | MoE | Modified MIT | API uniquement |
| **UI-TARS-1.5-7B** | 7B | Dense | Apache 2.0 | Self-host |
| **UI-Venus-7B** | 7B | Dense | Apache 2.0 | Self-host |
| **Gemma 3** | 4B / 12B / 27B | Dense | Apache 2.0 | Self-host / Edge |
| **Llama 3.2 Vision** | 11B / 90B | Dense | Llama 3.2 Community | Self-host |
| **OpenVLA** | 7B | Dense | Apache 2.0 | Self-host (robot) |
| **DeepSeek-VL2** | MoE (taille variable) | MoE | Apache 2.0 | Self-host |

---

## 3. Benchmarks UI Localization

Le score UI Localization mesure la capacité à identifier et localiser précisément un élément d'interface (bouton, champ texte, checkbox) à partir d'une instruction en langage naturel et d'une capture d'écran.

| Modèle | ScreenSpot-v2 | WebClick | ScreenSpot-Pro | GroundUI-Web | OSWorld-G | **Average** |
|--------|----------------|----------|----------------|--------------|-----------|-------------|
| **Holo1.5-72B** | [À valider] | 92.43% | [À valider] | [À valider] | [À valider] | **80.54%** |
| **Holo1.5-7B** | 93.31% | 90.24% | 57.94% | 84.00% | 66.27% | **77.32%** |
| **UI-TARS-1.5-7B** | **94.00%** | 86.10% | [À valider] | 84.20% | [À valider] | **70.45%** (3 tests) |
| **UI-Venus-7B** | **94.10%** | 84.44% | [À valider] | 82.30% | [À valider] | **72.96%** (3 tests) |
| **Qwen2.5-VL-7B** | 88.04% | [À valider] | [À valider] | 78.75% | [À valider] | **60.73%** (2 tests) |
| **Holo1.5-3B** | [À valider] | 81.45% | [À valider] | [À valider] | [À valider] | **72.81%** (reporté) |
| **Qwen3 VL 235B** | [Non publié] | [Non publié] | [Non publié] | [Non publié] | [Non publié] | **SOTA attendu** |
| **Gemma 3 27B** | [À valider] | [À valider] | [À valider] | [À valider] | [À valider] | **[À valider]** |

### Notes sur UI Localization
- **ScreenSpot-v2** : benchmark de référence pour la localisation d'éléments UI fixes. UI-Venus-7B et UI-TARS-1.5-7B dominent à 94%+.
- **WebClick** : navigation web réelle avec clic sur éléments dynamiques. Holo1.5-7B atteint 90.24%, supérieur à UI-TARS (86.10%) et UI-Venus (84.44%).
- **Holo1.5-72B** : meilleur average global (80.54%) mais licence Research only → inutilisable en production commerciale.
- **Qwen3 VL 235B** : scores UI non encore publiés au format ScreenSpot, mais réputation de GUI agent SOTA sur benchmarks internes Alibaba.

---

## 4. Benchmarks Navigation Web Complète

WebVoyager et benchmarks équivalents évaluent la capacité à réaliser une tâche web entière (ex: "réserver un billet d'avion Paris-Tokyo le 15 août") en chaînant navigation, clic, saisie, et validation.

| Modèle + Framework | Score WebVoyager | Coût / tâche | Nb attempts |
|--------------------|------------------|--------------|-------------|
| **Holo-1 7B + Surfer-H** | **92.2%** | **~$0.13** | 10 |
| GPT-4.1 + Surfer-H | 92.0% | ~$0.54 | [À valider] |
| **Holo-1 3B + Surfer-H** | 89.7% | ~$0.05 | 10 |
| GPT-4o + BrowserUse | ~85% | ~$1.20 | [À valider] |
| Claude 3.5 Sonnet + ComputerUse | ~90% | ~$0.80 | [À valider] |
| **Qwen3 VL 235B + Agent** | [SOTA attendu] | [À valider] | [À valider] |
| **Kimi K2.5 + Browser** | [Non testé formellement] | 1/8 prix Claude | [À valider] |
| UI-TARS-1.5-7B + Agent | [À valider] | Self-host | [À valider] |

### Notes sur Navigation Web
- **Holo-1 7B + Surfer-H** offre le meilleur ratio performance/coût : 92.2% à $0.13/tâche, soit **4x moins cher que GPT-4.1** pour un score équivalent.
- **Surfer-H** est un framework de navigation web spécialement optimisé pour Holo-1 (ensemble d'actions structurées, retry logic, history compression).
- Les modèles self-host (Holo1.5-7B, UI-TARS-7B) ont un coût marginal GPU électricité (~$0.01/action sur RTX 4090) mais nécessitent un investissement initial hardware.

---

## 5. Benchmarks OCR & Compréhension Document

| Modèle | Langues OCR | Document VQA | Table Extraction | Handwriting | Score moyen |
|--------|-------------|--------------|------------------|-------------|-------------|
| **Qwen3 VL 235B** | **32 langues** | Excellent | Excellent | Bon | **SOTA** |
| **Gemma 3 27B** | **29 langues** | Très bon | Bon | Moyen | Très bon |
| **Llama 3.2 Vision 90B** | Multilingue | Très bon | Très bon | Bon | Très bon |
| **Holo1.5-7B** | Moyen | Bon | Moyen | Faible | Moyen |
| **UI-TARS-1.5-7B** | Bon | Moyen | Faible | Faible | Moyen |
| **DeepSeek-VL2** | Technique | Excellent (scientifique) | Bon | [À valider] | Bon |

### Notes sur OCR
- **Qwen3 VL 235B** domine l'OCR multilingue avec support explicite de 32 langues, indispensable pour les documents administratifs européens (français, allemand, espagnol, italien, néerlandais, polonais) et appels d'offres internationaux.
- **Gemma 3** (4B-27B) offre le meilleur ratio poids/langues : 29 langues supportées même en 4B, idéal pour déploiement CPU/edge.
- **Holo1.5** et **UI-TARS** sont optimisés pour l'action UI, pas pour l'OCR documentaire. Leur OCR est fonctionnel mais inférieur aux modèles document-oriented.

---

## 6. Benchmarks Screen Content QA

Capacité à répondre à des questions sur le contenu d'un écran (lecture, inférence, raisonnement).

| Modèle | VisualWebBench | WebSRC | ScreenQAShort | ScreenQAComplex | **Average** |
|--------|----------------|--------|---------------|---------------|-------------|
| **Holo1.5-72B** | [À valider] | [À valider] | [À valider] | [À valider] | **90.00%** |
| **Holo1.5-7B** | 82.60% | 95.90% | 91.00% | 83.20% | **88.17%** |
| **Qwen2.5-VL-7B** | [À valider] | [À valider] | [À valider] | [À valider] | **83.02%** |
| **Qwen3 VL 235B** | [SOTA attendu] | [SOTA attendu] | [SOTA attendu] | [SOTA attendu] | **SOTA** |
| UI-TARS-1.5-7B | [À valider] | [À valider] | [À valider] | [À valider] | **[À valider]** |

---

## 7. Matrice Coût & Infrastructure

### Self-host (GPU local / cloud dédié)

| Modèle | VRAM requise | GPU recommandé | Coût GPU/h (cloud) | Inférence / action | Coût marginal/action |
|--------|-------------|----------------|-------------------|--------------------|----------------------|
| **Holo1.5-3B** | 8 GB | RTX 3070 | ~$0.25/h | ~500 ms | ~$0.0003 |
| **Holo1.5-7B** | 16 GB | RTX 4070 Ti / A10 | ~$0.50/h | ~800 ms | ~$0.001 |
| **UI-TARS-1.5-7B** | 16 GB | RTX 4070 Ti / A10 | ~$0.50/h | ~900 ms | ~$0.001 |
| **UI-Venus-7B** | 16 GB | RTX 4070 Ti / A10 | ~$0.50/h | ~900 ms | ~$0.001 |
| **Gemma 3 4B** | 4 GB | RTX 3060 / CPU | ~$0.15/h | ~300 ms | ~$0.0001 |
| **Gemma 3 27B** | 24 GB | RTX 4090 / A10 | ~$0.60/h | ~1200 ms | ~$0.002 |
| **Llama 3.2 Vision 11B** | 12 GB | RTX 3060 Ti | ~$0.30/h | ~600 ms | ~$0.0006 |
| **Llama 3.2 Vision 90B** | 80 GB | A100 80GB / H100 | ~$2.50/h | ~2500 ms | ~$0.017 |
| **Qwen3 VL 235B** | 40 GB+ | A100 40GB / H100 | ~$3.00/h | ~3000 ms | ~$0.025 |
| **Holo1.5-72B** | 140 GB+ | 2x A100 80GB | ~$5.00/h | ~5000 ms | ~$0.042 |
| **Kimi K2.5** | 240 GB+ | Non self-hostable | API uniquement | ~2000 ms | **API** |

### API Cloud (pricing indicatif 2026)

| Provider | Modèle | Prix input / 1M tokens | Prix output / 1M tokens | Coût estimé / action visuelle |
|----------|--------|----------------------|------------------------|------------------------------|
| **Holo3 API** | Holo3-35B-A3B | ~$0.50 | ~$1.50 | **~$0.05** |
| **Alibaba Cloud** | Qwen3 VL 235B | ~$1.00 | ~$3.00 | ~$0.12 |
| **Moonshot AI** | Kimi K2.5 | ~$0.80 | ~$2.00 | ~$0.10 |
| **OpenRouter** | Mix VLA | Variable | Variable | ~$0.08 |
| **Anthropic** | Claude 3.5 Sonnet | $3.00 | $15.00 | ~$0.80 |
| **OpenAI** | GPT-4.1 | $2.00 | $8.00 | ~$0.54 |

> **Note** : Une "action visuelle" typique inclut 1 screenshot encodé (~1000-2000 tokens image) + prompt (~200 tokens) + réponse structurée (~100 tokens).

---

## 8. Matrice Licences & Usage Commercial

| Modèle | Licence | Open Source | Usage commercial | Redistribution | Modification | Risque juridique |
|--------|---------|-------------|------------------|----------------|--------------|------------------|
| **Holo1.5-7B** | Apache 2.0 | Oui | Oui | Oui | Oui | **Faible** |
| **Holo3-35B-A3B** | Apache 2.0 | Oui | Oui | Oui | Oui | **Faible** |
| **Qwen3 VL 235B** | Apache 2.0 | Oui | Oui | Oui | Oui | **Faible** |
| **UI-TARS-1.5-7B** | Apache 2.0 | Oui | Oui | Oui | Oui | **Faible** |
| **UI-Venus-7B** | Apache 2.0 | Oui | Oui | Oui | Oui | **Faible** |
| **Gemma 3** | Apache 2.0 | Oui | Oui | Oui | Oui | **Faible** |
| **Llama 3.2 Vision** | Llama 3.2 Community | Poids oui | Oui (avec conditions) | Oui | Non | **Moyen** |
| **DeepSeek-VL2** | Apache 2.0 | Oui | Oui | Oui | Oui | **Faible** |
| **OpenVLA** | Apache 2.0 | Oui | Oui | Oui | Oui | **Faible** |
| **Holo1.5-3B** | Qwen Research (NC) | Poids oui | **Non** | Non | Non | **Élevé** |
| **Holo1.5-72B** | Research only | Poids oui | **Non** | Non | Non | **Élevé** |
| **Kimi K2.5** | Modified MIT | Non (API) | Oui (via API) | Non | Non | **Faible** (API) |

---

## 9. Verdict par Cas d'Usage TAKA OS

| Cas d'usage | Meilleur modèle | Score clé | Pourquoi | Alternative | Licence |
|-------------|----------------|-----------|----------|-------------|---------|
| **Navigation web portails AO** | **Holo1.5-7B** | 90.24% WebClick, 92.2% WebVoyager | Meilleur ratio performance/coût en self-host, Apache 2.0 | Qwen3 VL 235B (API) | Apache 2.0 |
| **Localisation UI précise** | **UI-TARS-1.5-7B** | 94.00% ScreenSpot | Localisation pixel-perfect optimisée pour desktop/web | UI-Venus-7B (94.10%) | Apache 2.0 |
| **OCR documents multilingues** | **Qwen3 VL 235B** | 32 langues, GUI agent SOTA | Support linguistique exhaustif pour AO européens | Gemma 3 27B (29 langues) | Apache 2.0 |
| **Visual-to-code (frontend)** | **Kimi K2.5** | Génère React/CSS depuis mockup | Capacité unique de transformation visuelle → code | [Pas d'alternative viable] | Modified MIT (API) |
| **Edge / CPU uniquement** | **Gemma 3 (4B)** | Léger, 29 langues OCR | 4GB VRAM, déploiable sur laptop PME | DeepSeek-VL 1.3B | Apache 2.0 |
| **Cloud API low-cost** | **Holo3-35B-A3B** | ~$0.05/action | 3B paramètres actifs, performance near-flagship | [À valider] | Apache 2.0 |
| **Robotique / actions physiques** | **OpenVLA** | 95% robot actions | Cross-embodiment, bras robotiques | [Hors scope TAKA] | Apache 2.0 |
| **Scientifique / technique** | **DeepSeek-VL2** | Scientific reasoning | Documents techniques, schémas, équations | [À valider] | Apache 2.0 |

---

## 10. Recommandation TAKA Vision (config par défaut)

### Tier 1 : Provider principal
**Holo1.5-7B (self-host)** pour la navigation web et les tâches GUI généralistes.
- **Rationale** : Apache 2.0 (liberté totale), 90.24% WebClick, 88.17% ScreenQA, coût marginal quasi-nul sur GPU dédié PME.
- **Infra** : 1x RTX 4070 Ti Super (16 GB VRAM) ou location cloud A10G.

### Tier 2 : Provider spécialisé OCR
**Qwen3 VL 235B (API)** pour l'OCR documentaire multilingue et la compréhension complexe de documents administratifs.
- **Rationale** : 32 langues, SOTA GUI agent, accessible via API Alibaba sans investissement hardware.
- **Usage** : Fallback lorsque Holo1.5-7B échoue à lire un document ou pour les AO internationaux.

### Tier 3 : Provider localisation UI
**UI-TARS-1.5-7B (self-host)** pour les tâches nécessitant une localisation pixel-perfect (ex: cliquer sur un bouton de 12x12px dans un tableau dense).
- **Rationale** : 94.00% ScreenSpot, meilleure précision de bounding box.
- **Infra** : Partageable avec Holo1.5-7B sur la même machine 16 GB (alternance).

### Tier 4 : Fallback CPU/Edge
**Gemma 3 4B** pour les environnements sans GPU (laptop consultant, démo client).
- **Rationale** : 4 GB VRAM, CPU possible, 29 langues OCR.

---

## 11. Données manquantes & [À valider]

| Donnée | Impact | Action recommandée |
|--------|--------|-------------------|
| Scores ScreenSpot-Pro UI-TARS / UI-Venus | Faible | Benchmark interne Sprint A |
| Scores WebVoyager UI-TARS / UI-Venus | Moyen | Benchmark interne Sprint A |
| Pricing exact Qwen3 VL API | Moyen | Négociation Alibaba Cloud |
| Pricing exact Kimi K2.5 API | Faible | Inscription Moonshot AI |
| Performance Holo3-35B-A3B sur portails AO réels | Élevé | Benchmark interne Sprint A |
| Support Holo1.5-7B sur formulaires JavaScript complexes | Élevé | Test sur 3 portails réels Sprint A |

---

*Fin du document. Prochaine étape : Architecture technique dans `02_architecture.md`.*
# Architecture TAKA Vision
## Couche VLA (Vision-Language-Action) — Spécification Technique v1.0

> Document de spécification architecturale pour l'intégration VLA dans TAKA OS v1.2.  
> Statut : Spécification — Sujet à revue après Sprint A (benchmark portails réels).

---

## 1. Vue d'ensemble

TAKA Vision est une **couche d'abstraction provider-agnostique** qui expose une API uniforme de perception visuelle et d'action GUI, quelle que soit le modèle VLA/VLM sous-jacent. Elle s'exécute comme **sidecar Docker** dans l'écosystème TAKA OS et communique avec les agents via une API REST interne.

### Objectifs architecturaux
1. **Agnosticisme provider** : switcher de Holo-1 à Qwen3 sans toucher au code métier.
2. **Résilience** : fallback automatique A → B → C → humain.
3. **Performance** : file d'attente asynchrone, cache screenshots, batching quand possible.
4. **Sécurité** : chiffrement, anonymisation, audit trail visuel complet.
5. **Multi-tenant** : isolation par tenant avec RBAC et rate limiting.

---

## 2. Abstraction Layer (Provider-Agnostic)

### 2.1 Interface `VLAProvider` (ABC Python)

Tous les providers VLA implémentent le contrat suivant :

```python
"""
TAKA Vision — Abstraction Layer VLA
License: MIT (TAKA OS)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
import base64


class ActionType(Enum):
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    HOVER = "hover"
    WAIT = "wait"
    NAVIGATE = "navigate"
    VALIDATE = "validate"
    FAIL = "fail"
    HUMAN_REQUIRED = "human_required"


@dataclass(frozen=True)
class BoundingBox:
    x1: float  # 0.0-1.0 (relative)
    y1: float
    x2: float
    y2: float
    confidence: float  # 0.0-1.0


@dataclass(frozen=True)
class ClickAction:
    bbox: BoundingBox
    action_type: ActionType = ActionType.CLICK
    label: str = ""
    reasoning: str = ""


@dataclass(frozen=True)
class TypeAction:
    bbox: BoundingBox
    text: str
    action_type: ActionType = ActionType.TYPE
    clear_first: bool = True


@dataclass(frozen=True)
class NextAction:
    action: Any  # ClickAction | TypeAction | ScrollAction | ...
    action_type: ActionType
    reasoning: str = ""
    expected_outcome: str = ""
    requires_human_validation: bool = False


class VLAProvider(ABC):
    """
    Abstract Base Class pour tous les providers VLA de TAKA Vision.
    Chaque provider (Holo, Qwen, UI-TARS, Kimi, Gemma) implémente
    cette interface avec sa logique de tokenization et de parsing spécifique.
    """

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Identifiant unique du provider (ex: 'holo1.5-7b', 'qwen3-vl-235b')."""
        ...

    @property
    @abstractmethod
    def capabilities(self) -> Dict[str, bool]:
        """
        Capacités supportées par ce provider.
        Ex: {'ui_localization': True, 'ocr_multilingual': False, 'navigation_web': True}
        """
        ...

    @abstractmethod
    def localize_element(
        self,
        screenshot_b64: str,
        instruction: str,
        context: Optional[str] = None
    ) -> ClickAction:
        """
        Localise un élément UI à partir d'une instruction en langage naturel.
        Retourne une action de clic avec bounding box relative [0,1].
        """
        ...

    @abstractmethod
    def navigate_task(
        self,
        screenshot_b64: str,
        goal: str,
        history: List[Dict[str, Any]],
        url: Optional[str] = None
    ) -> NextAction:
        """
        Détermine la prochaine action pour atteindre un objectif web.
        history : liste des étapes précédentes [{action, screenshot_hash, result}].
        """
        ...

    @abstractmethod
    def extract_text(
        self,
        screenshot_b64: str,
        region: Optional[BoundingBox] = None,
        language_hint: Optional[str] = None
    ) -> str:
        """
        Extrait le texte d'une région d'écran (OCR).
        Si region=None, OCR sur tout l'écran.
        """
        ...

    @abstractmethod
    def validate_result(
        self,
        before_b64: str,
        after_b64: str,
        expected_description: str
    ) -> Tuple[bool, str]:
        """
        Valide que l'action a produit le résultat attendu.
        Retourne (success: bool, reasoning: str).
        """
        ...

    @abstractmethod
    def health_check(self) -> Tuple[bool, str]:
        """Retourne l'état de santé du provider (connectivité, charge, disponibilité)."""
        ...

    def __repr__(self) -> str:
        return f"<VLAProvider {self.provider_id}>"
```

### 2.2 Implémentation concrète : HoloProvider

```python
class HoloProvider(VLAProvider):
    """
    Provider pour Holo1.5-7B / Holo1.5-3B / Holo3-35B-A3B.
    Utilise le format de prompt Surfer-H optimisé pour la navigation web.
    """

    def __init__(self, model_name: str, endpoint: str, api_key: Optional[str] = None):
        self.model_name = model_name
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self._session = None  # aiohttp session (lazy)

    @property
    def provider_id(self) -> str:
        return f"holo-{self.model_name}"

    @property
    def capabilities(self) -> Dict[str, bool]:
        return {
            "ui_localization": True,
            "navigation_web": True,
            "ocr_multilingual": False,  # Holo1.5 faible en OCR
            "visual_qa": True,
            "self_host": True,
            "api_cloud": self.model_name == "holo3-35b-a3b",
        }

    def localize_element(self, screenshot_b64: str, instruction: str, context=None) -> ClickAction:
        # Prompt format Surfer-H : <image> + instruction structurée
        # Parsing de la réponse JSON : {"action": "click", "bbox": [x1,y1,x2,y2], "label": "..."}
        ...

    def navigate_task(self, screenshot_b64: str, goal: str, history: List[Dict], url=None) -> NextAction:
        # Prompt avec history compression (max 5 étapes)
        # Retourne NextAction avec reasoning chain-of-thought
        ...

    def extract_text(self, screenshot_b64: str, region=None, language_hint=None) -> str:
        # Fallback sur OCR pipeline interne si Holo échoue
        ...

    def validate_result(self, before_b64: str, after_b64: str, expected_description: str) -> Tuple[bool, str]:
        # Prompt : "Compare these two screenshots. Did the action achieve: {expected}?"
        ...

    def health_check(self) -> Tuple[bool, str]:
        # Ping endpoint /health ou inférence légère
        ...
```

### 2.3 Registre de providers & Configuration par tenant

```python
class VLAProviderRegistry:
    """
    Registre central des providers VLA disponibles.
    Charge la configuration depuis TAKA OS Config Service (Layer 4).
    """

    _providers: Dict[str, VLAProvider] = {}
    _tenant_configs: Dict[str, Dict] = {}

    @classmethod
    def register(cls, provider: VLAProvider) -> None:
        cls._providers[provider.provider_id] = provider

    @classmethod
    def get_provider_for_tenant(cls, tenant_id: str, task_type: str) -> VLAProvider:
        """
        Résolution du provider selon la configuration tenant.
        Fallback automatique si le provider principal est indisponible.
        """
        config = cls._tenant_configs.get(tenant_id, {})
        chain = config.get("provider_chain", ["holo1.5-7b", "qwen3-vl-235b", "gemma3-4b"])

        for provider_id in chain:
            provider = cls._providers.get(provider_id)
            if provider is None:
                continue
            healthy, _ = provider.health_check()
            if healthy and provider.capabilities.get(task_type, False):
                return provider

        raise ProviderUnavailableError(f"Aucun provider disponible pour tenant {tenant_id}")
```

### 2.4 Configuration YAML par tenant

```yaml
# /etc/taka/vision/tenants/acme-corp.yml
vision_config:
  provider_chain:
    - holo1.5-7b      # Principal : navigation web, localisation UI
    - qwen3-vl-235b   # Fallback 1 : OCR multilingue, complex reasoning
    - uitars-1.5-7b   # Fallback 2 : localisation pixel-perfect
    - gemma3-4b       # Fallback 3 : CPU/edge (dernier recours)
    - human           # Fallback final : requête humaine via TAKA UI

  holo1.5-7b:
    endpoint: "http://taka-vision-holo:8000/v1"
    timeout_ms: 5000
    max_retries: 2

  qwen3-vl-235b:
    endpoint: "https://dashscope.aliyuncs.com/api/v1"
    api_key_ref: "vault://secrets/qwen3-api-key"
    timeout_ms: 8000

  uitars-1.5-7b:
    endpoint: "http://taka-vision-uitars:8000/v1"
    timeout_ms: 5000

  gemma3-4b:
    endpoint: "http://taka-vision-gemma:8000/v1"
    timeout_ms: 10000  # Plus lent sur CPU

  security:
    human_validation_required:
      - "payment"
      - "contract_signature"
      - "personal_data_submit"
    anonymize_patterns:
      - regex: "\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"  # CB
      - regex: "\b\d{14}\b"  # SIRET
      - regex: "\b\d{15}\b"  # SIREN
```

---

## 3. Architecture Technique

### 3.1 Topologie physique

```
┌─────────────────────────────────────────────────────────────┐
│                    TAKA OS v1.2 (Host)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Agent       │  │ Agent       │  │ Agent               │  │
│  │ Depositor   │  │ Auditor     │  │ Veille Concurrente  │  │
│  │ (Layer 3)   │  │ (Layer 3)   │  │ (Layer 3)           │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                     │              │
│  ┌──────▼────────────────▼─────────────────────▼──────────┐  │
│  │           TAKA Vision API (REST internal)              │  │
│  │   /v1/vision/localize  /v1/vision/navigate            │  │
│  │   /v1/vision/extract   /v1/vision/validate            │  │
│  │   /v1/vision/batch     /v1/vision/status              │  │
│  └──────┬────────────────┬─────────────────────┬───────────┘  │
│         │                │                     │              │
│  ┌──────▼──────┐  ┌─────▼──────┐  ┌──────────▼─────────┐  │
│  │  Sidecar    │  │  Sidecar   │  │  Sidecar           │  │
│  │  Holo1.5-7B │  │  UI-TARS   │  │  Gemma3-4B (CPU)   │  │
│  │  (GPU)      │  │  (GPU)     │  │  (CPU fallback)    │  │
│  │  Port 8001  │  │  Port 8002 │  │  Port 8003         │  │
│  └─────────────┘  └────────────┘  └────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  TAKA Vision Controller (Python/FastAPI)             │   │
│  │  • File d'attente Redis/SQS                         │   │
│  │  • Cache screenshots (Redis, TTL 1h, chiffré)       │   │
│  │  • Rate limiter per tenant                          │   │
│  │  • Audit trail → TAKA Audit Layer (Layer 5)        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│  TAKA Vision API Cloud  │  (optionnel — pour Qwen3 / Kimi)
│  • Proxy / relay        │
│  • Credential rotation  │
│  • Usage metering       │
└─────────────────────────┘
```

### 3.2 API REST interne — Spécification

| Endpoint | Méthode | Body | Response | Usage |
|----------|---------|------|----------|-------|
| `/v1/vision/localize` | POST | `{screenshot_b64, instruction, tenant_id}` | `ClickAction` | Localiser un élément UI |
| `/v1/vision/navigate` | POST | `{screenshot_b64, goal, history, url, tenant_id}` | `NextAction` | Prochaine étape navigation |
| `/v1/vision/extract` | POST | `{screenshot_b64, region, language, tenant_id}` | `{text, confidence}` | OCR sur région |
| `/v1/vision/validate` | POST | `{before_b64, after_b64, expected, tenant_id}` | `{valid, reasoning}` | Validation visuelle |
| `/v1/vision/batch` | POST | `{tasks: [...], tenant_id}` | `{results: [...]}` | Batch async |
| `/v1/vision/status` | GET | — | `{providers: [...], queue_depth}` | Santé système |
| `/v1/vision/sequences` | GET/POST | `{sequence_id, actions}` | `{stored}` | CRUD séquences mémorisées |

### 3.3 File d'attente de tâches visuelles

Les inférences VLA sont **coûteuses en temps** (500ms-5s). TAKA Vision ne bloque jamais l'agent appelant. Architecture asynchrone :

1. **Producer** (Agent Depositor) publie une tâche `VisionTask` dans la file Redis.
2. **Worker** (pool de threads async) consomme et route vers le provider approprié.
3. **Callback** : l'agent reçoit le résultat via webhook SSE ou polling `/v1/vision/status/{task_id}`.
4. **Timeout** : si un provider dépasse son timeout configuré, fallback automatique au suivant dans la chaîne.

```python
@dataclass
class VisionTask:
    task_id: str          # UUID v4
    tenant_id: str
    task_type: str        # "localize" | "navigate" | "extract" | "validate"
    payload: Dict[str, Any]
    priority: int         # 0=critical (humain attend), 1=normal, 2=batch
    created_at: float     # timestamp
    max_attempts: int = 3
    attempts: List[Dict] = field(default_factory=list)
```

### 3.4 Cache des screenshots

- **Stockage** : Redis avec chiffrement AES-256-GCM par tenant key.
- **Clé** : `sha256(screenshot_bytes + tenant_id)` → déduplication automatique.
- **TTL** : 1 heure (screenshots éphémères par nature).
- **Anonymisation** : appliquée AVANT mise en cache (patterns regex configurables).
- **Purge** : tâche cron toutes les 10 minutes.

### 3.5 Rate Limiting par tenant

| Plan | Requêtes / minute | Requêtes / heure | Burst |
|------|-------------------|------------------|-------|
| Essential | 30 | 500 | 10 |
| Professional | 120 | 3000 | 30 |
| Enterprise | 600 | 20000 | 100 |
| Custom | Configurable | Configurable | Configurable |

Implémentation via Redis + token bucket algorithm. Headers `X-RateLimit-*` retournés sur chaque réponse.

---

## 4. Sécurité

### 4.1 Coffre-fort credentials

Pattern inspiré de HashiCorp Vault, simplifié pour TAKA OS :

```
TAKA Vision Controller
    └── SecretManager (interface)
        ├── VaultProvider (HashiCorp Vault externe)
        ├── FileProvider (/etc/taka/secrets, chiffré)
        └── EnvProvider (variables d'environnement, dev only)
```

Les API keys cloud (Qwen3, Kimi) ne transitent jamais en clair :
- Stockées chiffrées au repos (AES-256).
- Rotation automatique tous les 90 jours.
- Accès via `api_key_ref: "vault://secrets/qwen3-api-key"` uniquement.

### 4.2 Chiffrement des screenshots

| État | Algorithme | Gestion clés |
|------|-----------|-------------|
| Transit (API interne) | TLS 1.3 | Certificats internes TAKA PKI |
| Cache Redis | AES-256-GCM | Clé dérivée par tenant (HKDF) |
| Stockage audit (Layer 5) | AES-256-GCM | Clé master rotative |
| Archive long terme | ChaCha20-Poly1305 | HSM optionnel (Enterprise) |

### 4.3 Anonymisation automatique

Pipeline appliquée systématiquement avant toute inférence ou stockage :

```python
class ScreenshotAnonymizer:
    PATTERNS = [
        (r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "[CB-MASKED]"),
        (r"\b\d{3}[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{3}\b", "[SIREN-MASKED]"),  # 9 chiffres
        (r"\b\d{14}\b", "[SIRET-MASKED]"),
        (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL-MASKED]"),
        (r"\b\d{2}[\s-]?\d{2}[\s-]?\d{2}[\s-]?\d{2}[\s-]?\d{2}[\s-]?\d{2}[\s-]?\d{2}[\s-]?\d{2}\b", "[IBAN-MASKED]"),
        # Patterns configurables par tenant
    ]

    def anonymize(self, screenshot_b64: str, custom_patterns: List = None) -> str:
        # 1. OCR rapide (lightweight) pour détecter les zones sensibles
        # 2. Masquage visuel (black boxes) sur les coordonnées détectées
        # 3. Remplacement textuel dans les métadonnées
        ...
```

### 4.4 Mode "Humain au centre"

Trois niveaux de validation :

| Niveau | Déclencheur | Action |
|--------|-------------|--------|
| **L0 — Autonome** | Tâche routine (navigation, clic banal) | Exécution directe, log audit |
| **L1 — Supervisé** | Formulaire avec données sensibles, paiement | Pause, notification humaine, approbation requise dans TAKA UI |
| **L2 — Bloquant** | Signature électronique, dépôt final AO | Exécution impossible sans confirmation biométrique/token 2FA |

### 4.5 Audit trail visuel

Chaque action visuelle génère un enregistrement d'audit immutable :

```json
{
  "audit_id": "vis-2026-06-15-uuid",
  "timestamp": "2026-06-15T14:32:01Z",
  "tenant_id": "acme-corp",
  "agent_id": "agent-depositor-01",
  "task_id": "task-uuid",
  "provider": "holo1.5-7b",
  "action_type": "navigate",
  "screenshot_before_hash": "sha256:abc...",
  "screenshot_after_hash": "sha256:def...",
  "instruction": "Cliquer sur 'Déposer un dossier'",
  "model_response": {"action": "click", "bbox": [0.45, 0.62, 0.52, 0.67]},
  "human_validated": false,
  "success": true,
  "execution_time_ms": 890,
  "cost_usd": 0.001
}
```

Stockage : append-only dans TAKA Audit Layer (Layer 5), signé cryptographiquement.

---

## 5. Intégration avec TAKA OS

### 5.1 Cartographie des couches TAKA

| Couche TAKA OS | Rôle | Intégration TAKA Vision |
|----------------|------|------------------------|
| **Layer 1 — Sensorimotrice** | Perception et action | TAKA Vision est le **sous-module visuel** de Layer 1. Complète les sensors texte/webscraping par la perception visuelle GUI. |
| **Layer 2 — Mémoire** | Stockage procédural et épisodique | Mémorise les **séquences visuelles réussies** ("pour déposer sur portail X, cliquer en [0.45, 0.62] puis scroll..."). |
| **Layer 3 — Agents** | Orchestration cognitive | **Agent Depositor** (nouveau) consomme TAKA Vision. Agents existants (Analyste, Veille) peuvent l'utiliser. |
| **Layer 4 — Outils & RAG** | Connecteurs et retrieval | TAKA Vision est un outil comme les autres. Appelable via `@vision.localize(...)` dans le langage agent. |
| **Layer 5 — Audit & Gouvernance** | Traçabilité et conformité | Toutes les actions visuelles passent par Layer 5 pour logging immuable. |

### 5.2 Agent Depositor (Nouveau — Layer 3)

L'**Agent Depositor** est l'agent TAKA qui utilise intensivement TAKA Vision :

```
Agent Depositor
├── Phase 1 : Analyse du portail cible (URL, type de plateforme)
├── Phase 2 : Récupération séquence mémorisée (Layer 2) si existante
├── Phase 3 : Navigation visuelle (TAKA Vision → HoloProvider)
│   └── Boucle : screenshot → goal → NextAction → exécution → validation
├── Phase 4 : Remplissage formulaire (TAKA Vision → QwenProvider pour OCR + HoloProvider pour clic)
├── Phase 5 : Upload documents (TAKA Vision → localisation drag-and-drop)
├── Phase 6 : Validation finale + confirmation humaine (L1/L2)
└── Phase 7 : Archivage séquence réussie dans Layer 2
```

### 5.3 Mémoire visuelle (Layer 2)

Format de mémorisation des séquences :

```json
{
  "sequence_id": "seq-boamp-deposer-ao",
  "platform": "boamp.fr",
  "task": "deposer_ao",
  "version": 3,
  "steps": [
    {"step": 1, "action": "navigate", "url": "https://www.boamp.fr/"},
    {"step": 2, "action": "click", "target": "menu_connexion", "bbox": [0.85, 0.05, 0.95, 0.10], "confidence": 0.92},
    {"step": 3, "action": "click", "target": "bouton_depot", "bbox": [0.40, 0.55, 0.60, 0.65], "confidence": 0.88},
    {"step": 4, "action": "type", "target": "champ_siret", "bbox": [0.30, 0.40, 0.70, 0.45], "text_ref": "{{siret}}"}
  ],
  "success_rate": 0.94,
  "last_used": "2026-06-10",
  "deprecated": false
}
```

---

## 6. Dépendances et Stack Technique

| Composant | Technologie | Version | Rationale |
|-----------|-------------|---------|-----------|
| API Controller | FastAPI (Python) | 0.115+ | Async natif, OpenAPI auto, performant |
| Sidecar VLA | vLLM / TGI / llama.cpp | Latest | Inference engine selon modèle |
| File d'attente | Redis Streams | 7.2+ | Pub/sub, persistence, TTL |
| Cache | Redis + disk spilling | 7.2+ | TTL, eviction LRU |
| Chiffrement | cryptography (Python) | 42+ | AES-GCM, ChaCha20 |
| OCR fallback | EasyOCR / Tesseract | 1.7+ | Si VLA échoue sur texte |
| Container | Docker + Compose | 25+ | Sidecar pattern |
| Observability | Prometheus + Grafana | — | Métriques GPU, latence, queue depth |

---

*Fin du document. Prochaine étape : Argumentaire de différenciation dans `03_differentiation.md`.*
# Comment TAKA OS Devance les VLA Seuls
## Argumentaire Stratégique — TAKA Vision vs. Solutions VLA Brutes

> Document stratégique à destination des décideurs, investisseurs, et architectes système.  
> Thèse : un modèle VLA (Holo-1, Qwen3, UI-TARS) seul est un **outil**. TAKA OS + VLA est une **organisation agentic** avec mains, mémoire, et gouvernance.

---

## 1. Problème : La Faillite du VLA Seul

Les modèles VLA de 2026 (Holo-1, Qwen3 VL, UI-TARS, Kimi K2.5) représentent une prouesse technique. Un modèle comme Holo1.5-7B atteint 90.24% de succès sur WebClick et 92.2% sur WebVoyager. Pourtant, déployé seul dans un pipeline métier réel, il présente 6 faillites structurelles :

| Faillite | Description | Conséquence métier |
|----------|-------------|-------------------|
| **Amnésie procédurale** | Holo-1 oublie tout entre deux sessions. | Re-apprend "comment déposer sur BOAMP" à chaque utilisation. Coût : 15-30 min de navigation exploratoire par AO. |
| **Action sans réflexion** | Le modèle prédit un clic immédiatement, sans délibération. | Risque de clic erroné sur "Supprimer" au lieu de "Valider". Pas de mécanisme de "second avis". |
| **Répétition des erreurs** | Holo-1 n'a pas de mémoire d'échecs. | Si un portail a changé son UI (mise à jour nocturne), le modèle répète la même erreur 10x. |
| **Opacité totale** | Aucune traçabilité des décisions visuelles. | En cas de litige (dépôt manqué, deadline manquée), impossible de prouver ce qui s'est passé. |
| **Monoposte** | Un seul utilisateur, pas de notion de tenant. | Impossible à déployer dans une PME de 50 personnes avec RBAC et isolation des données. |
| **Échec silencieux** | 8% d'échecs WebVoyager sont non détectés. | L'agent croit avoir déposé l'AO. En réalité, il n'a pas cliqué sur "Confirmer". Aucun fallback. |

> **Verdict** : Un VLA seul est un cerveau sans organisme. Il voit, il clique, il oublie. Il ne sait pas pourquoi il clique, il n'apprend pas de ses erreurs, et il ne rend pas de comptes.

---

## 2. Solution : TAKA OS comme Organisme Agentic

TAKA OS est un système agentic complet à 5 couches. TAKA Vision (couche VLA) n'est que l'organe sensorimoteur. Le reste de l'organisme — mémoire, délibération, gouvernance, audit — transforme le VLA en agent autonome fiable.

---

## 3. Les 6 Dimensions de Différenciation

### 3.1 Mémoire Procédurale : Holo-1 Oublie, TAKA Mémorise

**Holo-1 seul** :
- Chaque session est un tabula rasa. Le modèle ne sait pas que "sur BOAMP.fr, le bouton Déposer est en haut à droite après connexion".
- Même tâche répétée 100 fois = 100 explorations visuelles identiques.
- Coût cumulé : 100 × 15 min × $0.13/action = **$13 + 25 heures perdues**.

**TAKA OS + Vision** :
- Layer 2 (Mémoire) stocke les séquences visuelles réussies sous forme structurée (JSON séquentiel avec bounding boxes, URLs, timestamps).
- Au démarrage d'une tâche, l'Agent Depositor interroge Layer 2 : `"seq-boamp-deposer-ao"` existe-t-elle ?
- Si oui : exécution directe, **95% de la séquence sans inférence VLA** (seuls les champs variables nécessitent une inférence).
- Si le portail a changé : TAKA Vision détecte l'échec de l'étape N, re-infère avec le VLA pour ajuster, puis met à jour la séquence.
- **Capitalisation** : après 10 AO déposés sur le même portail, le coût moyen par dépôt chute de $0.13 à **$0.02** (cache + séquence mémorisée).

| Métrique | Holo-1 Seul | TAKA + Holo-1 |
|----------|-------------|---------------|
| Temps 1er dépôt | 15 min | 15 min |
| Temps 10ème dépôt | 15 min | 3 min |
| Coût inference / dépôt | $0.13 | $0.02 |
| Robustness UI change | 0% (échec total) | 92% (réadaptation auto) |

---

### 3.2 Délibération Parlementaire : Holo-1 Agit, TAKA Débat

**Holo-1 seul** :
- Architecture monolithique : un seul modèle prédit l'action. Pas de contradicteur.
- Si Holo-1 prédit "cliquer sur Supprimer le dossier" (parce que le texte ressemble à "Valider"), l'action est exécutée sans recours.
- **Pas de séparation pouvoir/exécution**.

**TAKA OS + Vision** :
- Layer 3 (Agents) implémente un **parlement agentic** avant toute action sensible.
- L'Agent Depositor soumet la `NextAction` proposée à l'Agent Auditor (rôle "contradicteur").
- L'Agent Auditor valide : la bounding box cible correspond-elle bien à l'intention ? Le texte du bouton est-il bien "Valider" ?
- Si les deux agents sont en désaccord (confidence < 0.85 ou divergence > 20%), **escalade humaine** (L1/L2).
- Pour les actions critiques (paiement, signature, dépôt final), un **troisième agent arbitre** (Agent Compliance) vote.
- **Résultat** : taux d'erreur sur actions sensibles divisé par 10 (estimation : 1.2% vs 12% pour VLA seul).

```
Agent Depositor (propose)          Agent Auditor (contredit)
         │                                  │
         ▼                                  ▼
    ┌─────────┐                       ┌─────────┐
    │ Action  │ ──── consensus ? ──── │ Review  │
    │ Proposée│                       │ OK ?    │
    └────┬────┘                       └────┬────┘
         │                                  │
         └───────────┬──────────────────────┘
                     ▼
              ┌────────────┐
              │ Exécution  │ ← si consensus ≥ 0.90
              │  Directe   │
              └─────┬──────┘
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
   ┌──────────┐          ┌──────────┐
   │ Humain   │          │ Retry    │
   │ (L1/L2)  │          │ + log    │
   └──────────┘          └──────────┘
```

---

### 3.3 Capitalisation des Échecs : Holo-1 Répète, TAKA Apprend

**Holo-1 seul** :
- Aucun mécanisme de rétropropagation métier. Si le clic échoue (élément déplacé, page changée), le modèle recommence à zéro à la prochaine session.
- Le même pattern d'échec se répète indéfiniment.

**TAKA OS + Vision** :
- Chaque échec est loggé dans Layer 2 avec **contexte complet** : screenshot avant/après, action tentée, erreur détectée, provider utilisé.
- L'**Agent Learning** (Layer 3) analyse les patterns d'échec par portail / par provider / par type d'UI.
- Si Holo-1 échoue 3 fois de suite sur BOAMP à cause d'un nouveau modal "Cookies", TAKA :
  1. Ajuste la séquence mémorisée pour inclure "dismiss cookies modal".
  2. Baisse le score de confiance de Holo-1 pour ce portail.
  3. Passe temporairement en fallback UI-TARS (meilleur localisation UI).
  4. Notifie les administrateurs tenant du changement d'UI.
- **Learning loop** : le système s'améliore avec le temps, comme un humain expérimenté.

| Cycle | Holo-1 Seul | TAKA + Holo-1 |
|-------|-------------|---------------|
| Échec N | Échec, retry identique | Échec, log + analyse |
| Échec N+1 | Échec, retry identique | Fallback provider, séquence ajustée |
| Échec N+2 | Échec, abandon | Séquence mémorisée corrigée, succès |
| Échec N+10 | Échec, abandon | 0 échecs (séquence stable) |

---

### 3.4 Gouvernance LLM : Holo-1 Est une Boîte Noire, TAKA Audite Tout

**Holo-1 seul** :
- Aucun audit trail. Le modèle prédit un clic à [0.45, 0.62]. Qui a vérifié que c'était le bon bouton ? Personne.
- Conformité RGPD/ISO 27001 : impossible. Pas de preuve de ce que le système a vu ou fait.
- Litige "l'AO n'a pas été déposé" : aucune preuve à produire.

**TAKA OS + Vision** :
- Layer 5 (Audit) enregistre **chaque screenshot + action + résultat + timestamp + tenant** dans un log append-only signé.
- Conformité : TAKA Vision fournit une **preuve visuelle immuable** de chaque étape.
- RGPD : les screenshots sont anonymisés avant stockage (masquage CB, SIRET, email).
- Traçabilité complète : `audit_id` lié au tenant, à l'agent, à la tâche, au provider.
- **Dashboard compliance** : vue temps réel des actions visuelles par tenant, avec alertes sur anomalies.

| Exigence | Holo-1 Seul | TAKA + Vision |
|----------|-------------|---------------|
| Preuve visuelle | Non | Oui (screenshot before/after) |
| Traçabilité action | Non | Oui (JSON signé cryptographiquement) |
| Anonymisation PII | Non | Oui (pipeline automatique) |
| Audit externe | Impossible | Export standardisé (CSV/JSON) |
| RGPD Art. 5 (limitation finalité) | Non garanti | Oui (task scoping) |

---

### 3.5 Multi-tenant : Holo-1 = Un Utilisateur, TAKA = Une Entreprise

**Holo-1 seul** :
- Déploiement monoposte. Pas de notion d'utilisateur, de rôle, d'isolation des données.
- Si deux PME partagent la même instance Holo-1, leurs données de navigation se mélangent.
- Pas de rate limiting, pas de quota, pas de facturation par usage.

**TAKA OS + Vision** :
- Architecture **multi-tenant native**. Chaque tenant (PME, collectivité, grand compte) a :
  - Sa chaîne de providers configurée.
  - Ses credentials API isolés (Vault scopé).
  - Son cache de screenshots isolé (clé de chiffrement dérivée par tenant).
  - Ses séquences mémorisées privées ("comment déposer sur mon portail métier").
  - Ses règles de validation humaine (L0/L1/L2) personnalisées.
- **RBAC** : un consultant voit ses AO, un admin voit tout son tenant, un superadmin TAKA voit les métriques agrégées (anonymisées).
- **Facturation** : usage metering par tenant, exportable pour refacturation.

| Capacité | Holo-1 Seul | TAKA + Vision |
|----------|-------------|---------------|
| Utilisateurs simultanés | 1 | Illimité (scalable) |
| Isolation données | Non | Oui (chiffrement par tenant) |
| RBAC | Non | Oui (4 rôles : viewer, operator, admin, superadmin) |
| Rate limiting | Non | Oui (plan Essential/Professional/Enterprise) |
| Facturation par usage | Non | Oui (metering intégré) |
| Branding / white-label | Non | Oui (configurable par tenant) |

---

### 3.6 Fallback Intelligent : Holo-1 Échoue Silencieusement, TAKA Survit

**Holo-1 seul** :
- 8% d'échecs sur WebVoyager (même avec 10 attempts). Dans ces 8%, le modèle ne sait pas qu'il a échoué.
- Pas de plan B. Si Holo-1 ne trouve pas le bouton, la tâche s'arrête. L'AO n'est pas déposé.

**TAKA OS + Vision** :
- Chaîne de fallback configurée : **Holo-1 → Qwen3 → UI-TARS → Gemma3 → Humain**.
- Détection proactive d'échec : TAKA Vision `validate_result()` compare le screenshot before/after. Si l'état attendu n'est pas atteint → retry + fallback.
- Stratégies de retry adaptatives :
  - **Retry 1** : même provider, prompt reformulé (chain-of-thought).
  - **Retry 2** : provider alternatif (ex: UI-TARS meilleur en localisation fine).
  - **Retry 3** : mode "exploration" (scrolling systématique + re-localisation).
  - **Retry 4** : escale humaine via notification push/email dans TAKA UI.
- **Taux de survie final** : estimé à **99.2%** (vs 92% pour Holo-1 seul).

```
Tâche : Déposer AO sur portail X

    ┌─────────────────┐
    │  Holo-1 échec   │ (timeout / mauvaise bbox)
    └────────┬────────┘
             ▼
    ┌─────────────────┐
    │ Qwen3 VL fallback│ (meilleur reasoning + OCR)
    └────────┬────────┘
             ▼
    ┌─────────────────┐
    │ UI-TARS fallback │ (meilleure localisation pixel)
    └────────┬────────┘
             ▼
    ┌─────────────────┐
    │ Gemma3 fallback  │ (CPU, dernier recours local)
    └────────┬────────┘
             ▼
    ┌─────────────────┐
    │ Humain (L1/L2)   │ ← Notification push TAKA UI
    └─────────────────┘
```

---

## 4. Synthèse Comparative

| Dimension | Holo-1 Seul | Qwen3 Seul | UI-TARS Seul | **TAKA OS + VLA** |
|-----------|-------------|------------|--------------|-------------------|
| Navigation web | 92.2% | SOTA | [À valider] | **99.2%** (fallback) |
| Localisation UI | 90.24% | SOTA | 94.00% | **98%+** (best-of-breed) |
| OCR multilingue | Moyen | **SOTA** | Moyen | **SOTA** (Qwen3 fallback) |
| Mémoire procédurale | ❌ Non | ❌ Non | ❌ Non | ✅ **Oui** (Layer 2) |
| Délibération multi-agent | ❌ Non | ❌ Non | ❌ Non | ✅ **Oui** (Layer 3) |
| Capitalisation échecs | ❌ Non | ❌ Non | ❌ Non | ✅ **Oui** (Agent Learning) |
| Audit trail visuel | ❌ Non | ❌ Non | ❌ Non | ✅ **Oui** (Layer 5) |
| Multi-tenant / RBAC | ❌ Non | ❌ Non | ❌ Non | ✅ **Oui** (natif) |
| Fallback intelligent | ❌ Non | ❌ Non | ❌ Non | ✅ **Oui** (4 niveaux) |
| Coût décroissant | ❌ Non | ❌ Non | ❌ Non | ✅ **Oui** (séquences) |
| Humain au centre | ❌ Non | ❌ Non | ❌ Non | ✅ **Oui** (L1/L2) |
| Conformité RGPD | ❌ Non | ❌ Non | ❌ Non | ✅ **Oui** (anonymisation + audit) |

---

## 5. Positionnement Marché

| Offre | Type | Prix indicatif | Limitation |
|-------|------|---------------|------------|
| **Holo-1 + Surfer-H** (open source) | Outil VLA | Gratuit (hardware) | Monoposte, amnésique, opaque |
| **Qwen3 VL API** | API cloud | ~$0.12/action | Pas de mémoire, pas de gouvernance |
| **Claude Computer Use** | API cloud | ~$0.80/action | Vendor lock-in, pas de multi-tenant |
| **TAKA OS + Vision** | **OS agentic** | €299-999/mois | **Seule solution organisationnelle** |

> **Thèse de valeur** : TAKA OS ne vend pas un modèle VLA. Il vend une **organisation agentic complète** où le VLA est un organe parmi d'autres — mémoire, délibération, audit, gouvernance. Le VLA donne des mains. TAKA OS donne un cerveau, une mémoire, et une conscience éthique.

---

*Fin du document. Prochaine étape : Plan d'intégration dans `04_roadmap.md`.*
# Plan d'Intégration TAKA Vision v1.2
## Roadmap Sprints — Du Benchmark à la Production

> Document de planification projet pour l'intégration du module TAKA Vision dans TAKA OS v1.2.  
> Horizon : Mois 7-9 (Q3 2026).  
> Méthodologie : Sprints de 3 semaines avec milestone gates.

---

## 1. Vue d'ensemble du planning

```
2026 ──────────────────────────────────────────────────────────────►

Mois 6 (Juin)          Mois 7 (Juillet)       Mois 8 (Août)          Mois 9 (Sept)
   │                        │                      │                      │
   │  Sprint A               │  Sprint B            │  Sprint C            │  Sprint D
   │  (3 sem.)               │  (3 sem.)            │  (3 sem.)            │  (3 sem.)
   │                        │                      │                      │
   ├─ Benchmark 3 providers ├─ Abstraction Layer   ├─ Agent Depositor     ├─ Mémoire visuelle
   │  sur 3 portails réels   │  + 2 providers       │  + Humain au centre  │  + Séquences
   │                        │                      │                      │
   ├─ Définition séquences  ├─ API REST interne    ├─ L1/L2 validation    ├─ Optimisation
   │  types AO               │  + Sidecar Docker    │  + Dashboard         │  + Perf
   │                        │                      │                      │
   ├─ Sélection provider    ├─ Sécurité V1         ├─ Audit trail V1      ├─ Documentation
   │  par défaut             │  (chiffrement)       │  visuel              │  + Formation
   │                        │                      │                      │
   ▼                        ▼                      ▼                      ▼
Milestone A                Milestone B            Milestone C            Milestone D
"Portails validés"         "Infra prête"          "Agent fonctionnel"    "Production-ready"

Release : TAKA OS v1.2 — Fin Mois 9 (Freeze code Mois 8.3)
```

---

## 2. Sprint A — Benchmark des Providers sur Portails Réels

**Durée** : 3 semaines (Mois 7, semaines 1-3)  
**Objectif** : Valider empiriquement les choix de providers sur des portails d'appels d'offres réels.  
**Équipe** : 1 ML engineer + 1 backend engineer + 1 QA

### Livrables

| # | Livrable | Description | Critère d'acceptation |
|---|----------|-------------|----------------------|
| A1 | Matrice benchmark portails | Évaluation de Holo-1 7B, UI-TARS 7B, Qwen3 VL sur 3 portails | Document technique validé |
| A2 | Corpus screenshots anonymisé | 500+ screenshots par portail (train/test) | Stocké dans S3 interne chiffré |
| A3 | Rapport de sélection provider | Recommandation provider par défaut + chaîne fallback | Approbation tech lead |
| A4 | Spécification séquences types | Inventaire des 20 séquences visuelles les plus fréquentes | Review architecte |

### Portails cibles

| Portail | Type | Complexité UI | Fréquence AO PME |
|---------|------|--------------|------------------|
| **BOAMP** (boamp.fr) | Public | Moyenne (formulaires longs) | Haute |
| **Place** (marches-publics.gouv.fr) | Public | Élevée (multi-étapes, auth complexe) | Haute |
| **Achat Public** (achatpublic.com) | Privé | Moyenne (portail marketplace) | Moyenne |

### Tâches détaillées — Sprint A

```
Semaine 1 : Collecte & Anonymisation
├── J1-2 : Accès et configuration environnement test (VM isolée, VPN si nécessaire)
├── J3-4 : Capture screenshots sur parcours complets (connexion → recherche → dépôt)
├── J5 : Anonymisation corpus (pipeline regex + revue manuelle échantillon)

Semaine 2 : Benchmark Automatisé
├── J1-2 : Déploiement Holo-1 7B (vLLM) + UI-TARS 7B (vLLM) sur GPU cloud
├── J3-4 : Script benchmark standardisé (localisation 50 éléments + navigation 10 parcours)
├── J5 : Intégration Qwen3 VL via API (navigation + OCR)

Semaine 3 : Analyse & Recommandation
├── J1-2 : Scoring + analyse erreurs (faux positifs, faux négatifs, timeouts)
├── J3-4 : Rédaction rapport + présentation milestone
├── J5 : Revue milestone A → Go/No-Go Sprint B
```

### Milestone A — Critères de sortie

| Critère | Seuil | Validation |
|---------|-------|------------|
| Holo-1 7B : succès navigation BOAMP | ≥ 85% | Test scripté 10 parcours |
| UI-TARS 7B : précision localisation | ≥ 90% | ScreenSpot-like interne |
| Qwen3 VL : OCR document | ≥ 95% accuracy | 50 documents multilingues |
| Corpus anonymisé | 0 PII détecté (échantillon 10%) | Audit regex + manuel |
| Décision provider | Document signé | Tech lead + PO |

> **Gate** : Si Holo-1 7B < 80% sur BOAMP, réévaluer chaîne fallback (prioriser UI-TARS ou Qwen3).

---

## 3. Sprint B — Abstraction Layer + Infrastructure

**Durée** : 3 semaines (Mois 7.3 — Mois 8.1)  
**Objectif** : Implémenter la couche d'abstraction provider-agnostique et l'infrastructure sidecar.  
**Équipe** : 2 backend engineers + 1 DevOps

### Livrables

| # | Livrable | Description | Critère d'acceptation |
|---|----------|-------------|----------------------|
| B1 | `VLAProvider` ABC + implémentations | HoloProvider + QwenProvider + FallbackProvider | Tests unitaires ≥ 90% coverage |
| B2 | API REST TAKA Vision | 6 endpoints (/localize, /navigate, /extract, /validate, /batch, /status) | Contract OpenAPI validé |
| B3 | Sidecar Docker | Conteneur vLLM pour Holo-1 7B + UI-TARS 7B | Déploiement < 5 min |
| B4 | File d'attente Redis | Pub/sub async avec retry + fallback | Load test 100 tâches/min |
| B5 | Cache screenshots | Redis TTL 1h + chiffrement AES-GCM | Penetration test interne |
| B6 | Sécurité V1 | Vault credentials + anonymisation regex | Audit sécurité passé |

### Architecture livrée à la fin du Sprint B

```
TAKA Vision Infrastructure (Milestone B)
├── taka-vision-controller (FastAPI, port 8080)
│   ├── /v1/vision/* (6 endpoints)
│   ├── ProviderRegistry (Holo, Qwen, UI-TARS, Gemma)
│   ├── TaskQueue (Redis Streams)
│   ├── ScreenshotCache (Redis + AES-GCM)
│   └── SecretManager (Vault interface)
├── sidecar-holo-7b (Docker, vLLM, port 8001)
│   └── Modèle : Holo1.5-7B (GGUF ou FP16)
├── sidecar-uitars-7b (Docker, vLLM, port 8002)
│   └── Modèle : UI-TARS-1.5-7B
├── sidecar-gemma-4b (Docker, llama.cpp, port 8003)
│   └── Modèle : Gemma 3 4B (CPU fallback)
└── redis-cluster (cache + queue)
```

### Tâches détaillées — Sprint B

```
Semaine 1 : Abstraction Layer
├── J1-2 : Implémentation VLAProvider ABC + dataclasses
├── J3-4 : HoloProvider (prompt Surfer-H, parsing JSON, health check)
├── J5 : QwenProvider (API Dashscope, format prompt Qwen3-VL)

Semaine 2 : API + Queue + Cache
├── J1-2 : FastAPI controller + 6 endpoints + validation Pydantic
├── J3-4 : Redis Streams (producer/consumer) + retry logic
├── J5 : Cache Redis (clé sha256, chiffrement, TTL, anonymisation)

Semaine 3 : Sécurité + Intégration TAKA
├── J1-2 : SecretManager (Vault interface + file provider)
├── J3-4 : Anonymisation pipeline (regex + revue) + tests
├── J5 : Intégration Layer 1 TAKA OS (sensorimoteur) + revue milestone
```

### Milestone B — Critères de sortie

| Critère | Seuil | Validation |
|---------|-------|------------|
| Coverage tests | ≥ 90% | pytest --cov |
| Latence API / localize | ≤ 2000 ms (p95) | Load test k6 |
| Fallback automatique | Fonctionnel A → B → C | Test injection panne |
| Chiffrement cache | AES-256-GCM, clés par tenant | Audit crypto interne |
| Anonymisation | 0 PII dans cache (échantillon) | Scan regex |
| Déploiement sidecar | < 5 min `docker compose up` | Test fresh VM |

---

## 4. Sprint C — Agent Depositor + Mode Humain au Centre

**Durée** : 3 semaines (Mois 8.1 — Mois 8.3)  
**Objectif** : Créer l'Agent Depositor et implémenter les 3 niveaux de validation humaine.  
**Équipe** : 2 backend engineers + 1 frontend engineer + 1 UX designer

### Livrables

| # | Livrable | Description | Critère d'acceptation |
|---|----------|-------------|----------------------|
| C1 | Agent Depositor (Layer 3) | Agent orchestrant navigation + formulaire + upload + validation | Tests E2E 10 parcours complets |
| C2 | Mode L0 (autonome) | Exécution sans validation pour tâches routine | 100% autonome sur parcours validés |
| C3 | Mode L1 (supervisé) | Pause + notification pour données sensibles | Temps réponse humaine < 2 min (test) |
| C4 | Mode L2 (bloquant) | Confirmation biométrique/token pour actions critiques | Impossible de bypass |
| C5 | Dashboard TAKA UI | Vue temps réel des tâches visuelles + file d'attente | UX validée par 3 testeurs |
| C6 | Audit trail V1 | Log visuel immutable dans Layer 5 | Export JSON signé valide |

### Parcours Agent Depositor ( livré Sprint C )

```
Agent Depositor — Séquence type "Déposer AO sur BOAMP"

Étape 1 : Récupération séquence mémorisée (Layer 2)
    └─ Si existe et confiance > 0.90 → exécution L0 (autonome)
    └─ Sinon → inférence VLA (Holo-1 7B)

Étape 2 : Navigation web (boucle VLA)
    ├─ Screenshot → TAKA Vision /navigate → NextAction
    ├─ Exécution action (click / type / scroll)
    ├─ Validation résultat (TAKA Vision /validate)
    └─ Retry / fallback si échec

Étape 3 : Remplissage formulaire
    ├─ OCR champ (Qwen3 fallback si Holo échoue)
    ├─ Saisie valeur (TypeAction)
    └─ Validation par champ

Étape 4 : Upload documents
    ├─ Localisation zone drag-and-drop
    ├─ Simulation drop fichier
    └─ Vérification confirmation upload

Étape 5 : Validation finale
    ├─ Récapitulatif visuel (before/after)
    ├─ Si L1 requis → notification humaine
    ├─ Si L2 requis → token 2FA
    └─ Confirmation ou correction

Étape 6 : Archivage
    ├─ Séquence réussie → Layer 2 (mémorisation)
    ├─ Audit trail → Layer 5 (log signé)
    └─ Notification tenant (email/Slack)
```

### Tâches détaillées — Sprint C

```
Semaine 1 : Agent Depositor Core
├── J1-2 : Définition états (finite state machine) + transitions
├── J3-4 : Implémentation boucle navigate + fallback
├── J5 : Intégration formulaire (OCR + saisie séquentielle)

Semaine 2 : Validation Humaine + Dashboard
├── J1-2 : Implémentation L0/L1/L2 (règles configurables)
├── J3-4 : Dashboard TAKA UI (Vue React : tâches en cours, file, historique)
├── J5 : Système notification (SSE push, email, webhook Slack)

Semaine 3 : Audit + E2E
├── J1-2 : Audit trail visuel (screenshot + action + signature)
├── J3-4 : Tests E2E (10 parcours complets sur 3 portails)
├── J5 : Revue milestone C → Go/No-Go Sprint D
```

### Milestone C — Critères de sortie

| Critère | Seuil | Validation |
|---------|-------|------------|
| Parcours complet BOAMP (L0) | ≥ 8/10 succès | Test E2E automatisé |
| Temps parcours moyen | ≤ 10 min | Chronométrage E2E |
| Latence L1 (humain notifié) | ≤ 5s (push) | Test notification |
| Dashboard UX | Score SUS ≥ 70 | Test utilisateur |
| Audit trail complet | 100% des actions loggées | Vérification DB |
| Bypass L2 impossible | 0 bypass sur 100 tentatives | Test sécurité |

---

## 5. Sprint D — Mémoire Visuelle + Optimisation Production

**Durée** : 3 semaines (Mois 8.3 — Mois 9.3)  
**Objectif** : Capitaliser les séquences, optimiser les performances, documenter, former.  
**Équipe** : 1 backend engineer + 1 ML engineer + 1 technical writer

### Livrables

| # | Livrable | Description | Critère d'acceptation |
|---|----------|-------------|----------------------|
| D1 | Mémoire visuelle (Layer 2) | Stockage + retrieval séquences réussies | 20 séquences types stockées |
| D2 | Apprentissage séquences | Auto-update séquences après succès/échec | Taux adaptation > 80% |
| D3 | Optimisation latence | Cache + batching + warm-up modèles | p95 < 1000 ms (localise) |
| D4 | Documentation | Guide admin + Guide développeur + API reference | Review technique |
| D5 | Formation | Session 2h pour équipes support + premiers clients | Quiz passé > 80% |
| D6 | Release v1.2 | Tag git + CHANGELOG + migration guide | CI/CD green |

### Format mémoire visuelle (livré D1)

```json
{
  "sequence_version": "2.1",
  "platform_id": "boamp-fr",
  "task_type": "deposer_ao",
  "steps": [
    {"order": 1, "action": "navigate", "url": "https://www.boamp.fr/"},
    {"order": 2, "action": "click", "element_label": "Connexion", "bbox": [0.82, 0.04, 0.91, 0.09], "confidence": 0.94},
    {"order": 3, "action": "type", "element_label": "SIRET", "bbox": [0.25, 0.35, 0.75, 0.40], "value_ref": "{{tenant.siret}}"},
    {"order": 4, "action": "click", "element_label": "Se connecter", "bbox": [0.40, 0.55, 0.60, 0.62], "confidence": 0.91},
    {"order": 5, "action": "click", "element_label": "Déposer un dossier", "bbox": [0.35, 0.60, 0.65, 0.68], "confidence": 0.88}
  ],
  "success_rate": 0.93,
  "last_success": "2026-09-01T10:23:00Z",
  "total_executions": 47,
  "failure_count": 3,
  "auto_updated": true
}
```

### Tâches détaillées — Sprint D

```
Semaine 1 : Mémoire + Learning
├── J1-2 : CRUD séquences (Layer 2) + indexation platform_id + task_type
├── J3-4 : Auto-update séquences (ajustement bbox après échec réussi)
├── J5 : Matching fuzzy séquences (platform_id similaire = suggestion)

Semaine 2 : Performance + Robustesse
├── J1-2 : Warm-up modèles (keep-alive) + batching inférences
├── J3-4 : Stress test (50 tenants × 10 tâches/min)
├── J5 : Optimisation Docker (layers, cache, GPU sharing)

Semaine 3 : Documentation + Release
├── J1-2 : Rédaction docs (admin + dev + API reference)
├── J3-4 : Session formation interne + matériel client
├── J5 : Release v1.2 (tag, changelog, migration guide, annonce)
```

### Milestone D — Critères de sortie

| Critère | Seuil | Validation |
|---------|-------|------------|
| Séquences mémorisées | ≥ 20 types | Inventaire validé |
| Réutilisation séquences | ≥ 60% des tâches | Métriques Layer 2 |
| Latence p95 / localize | ≤ 1000 ms | Load test k6 |
| Latence p95 / navigate | ≤ 2000 ms | Load test k6 |
| Uptime sidecar GPU | ≥ 99.5% (7 jours) | Monitoring Prometheus |
| Documentation complète | 3 guides publiés | Review tech writer |
| Formation équipe | ≥ 5 personnes formées | Attestations |

---

## 6. Matrice de risques

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Holo-1 7B indisponible (licence) | Faible | Élevé | Chaîne fallback UI-TARS + Qwen3 + Gemma |
| Changement UI portail (breaking) | Élevée | Moyen | Séquences versionnées + détection auto + alerte |
| Latence > 2s sur navigation | Moyenne | Moyen | Cache + warm-up + batching + provider MoE (Holo3) |
| Fuite PII dans screenshots | Faible | Critique | Anonymisation obligatoire + audit regex + chiffrement |
| Échec validation humaine L1/L2 | Moyenne | Moyen | Timeout configurable + escalation manager + log complet |
| Scalabilité > 100 tenants | Faible | Moyen | Architecture stateless + Redis cluster + GPU pool |
| Performance GPU cloud instable | Moyenne | Moyen | Monitoring + auto-restart + fallback Gemma CPU |

---

## 7. KPIs de suivi

| KPI | Baseline (v1.1) | Objectif v1.2 | Mesure |
|-----|-------------------|---------------|--------|
| Temps moyen dépôt AO | 45 min (manuel) | 10 min (agent) | E2E chronométrage |
| Taux succès navigation | N/A | ≥ 90% | Tests E2E |
| Coût inference / AO | N/A | ≤ $0.10 | Metering TAKA |
| Taux utilisation séquences | 0% | ≥ 60% | Métriques Layer 2 |
| Temps réponse humaine L1 | N/A | ≤ 2 min | Logs notification |
| Satisfaction utilisateur | N/A | ≥ 7/10 | NPS mensuel |
| Incidents sécurité | 0 | 0 | Audit trimestriel |

---

## 8. Dépendances externes

| Dépendance | Fournisseur | Statut | Impact si retard |
|------------|-------------|--------|------------------|
| Holo1.5-7B weights | HuggingFace / Qwen Research | Disponible | Critique (provider principal) |
| UI-TARS-1.5-7B weights | HuggingFace / ByteDance | Disponible | Moyen (fallback) |
| Qwen3 VL API | Alibaba Cloud | À valider | Moyen (fallback OCR) |
| GPU cloud (A10G / RTX) | OVH / Scaleway / AWS | Disponible | Critique (infra sidecar) |
| Redis 7.2+ | Redis Labs / self-host | Disponible | Faible |

---

*Fin du document. TAKA Vision v1.2 — Spécification complète. Prochaine étape : Revue architecture + Kick-off Sprint A.*
