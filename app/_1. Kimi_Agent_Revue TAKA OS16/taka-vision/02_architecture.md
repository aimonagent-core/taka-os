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
