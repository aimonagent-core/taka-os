# Section 3 — Agents TAKA & Système de Mémoire

> **Document** : Blueprint TAKA OS — Section 3
> **Version** : 1.0
> **Date** : 2025-01
> **Statut** : Spécification Technique Détaillée
> **Stack** : PostgreSQL 15 + pgvector | httpx + Jinja2 | Mistral AI API | pypdf / pdfplumber / Tesseract

---

## Table des Matières

1. [Architecture des 3 Agents](#31-architecture-des-3-agents)
   - 1.1 [Agent Sourcer (`ao_sourcer`)](#311-agent-sourcer-ao_sourcer)
   - 1.2 [Agent Qualifieur (`ao_qualifier`)](#312-agent-qualifieur-ao_qualifier)
   - 1.3 [Agent Tracker (`ao_tracker`)](#313-agent-tracker-ao_tracker)
2. [Système de Mémoire (pgvector)](#32-système-de-mémoire-pgvector)
   - 2.1 [Génération d'embeddings](#321-génération-dembeddings)
   - 2.2 [Stockage pgvector](#322-stockage-pgvector)
   - 2.3 [Recherche de similarité](#323-recherche-de-similarité)
   - 2.4 [Capitalisation échecs/succès](#324-capitalisation-des-échecssuccès)
3. [Pipeline de Parsing PDF](#33-pipeline-de-parsing-pdf)
   - 3.1 [Architecture stratifiée](#331-architecture-stratifiée)
   - 3.2 [Champs à extraire](#332-champs-à-extraire)
   - 3.3 [Gestion des échecs](#333-gestion-des-échecs)
   - 3.4 [Traitement asynchrone](#334-traitement-asynchrone)
4. [Intégration Mistral AI](#34-intégration-mistral-ai)
   - 4.1 [Configuration](#341-configuration)
   - 4.2 [Client HTTP (httpx)](#342-client-http-httpx)
   - 4.3 [Prompts Templates (Jinja2)](#343-prompts-templates-jinja2)

---

## 3.1 Architecture des 3 Agents

### 3.1.1 Agent Sourcer (`ao_sourcer`)

#### Responsabilité

L'Agent Sourcer est le point d'entrée du système pour tous les Appels d'Offres. Il reçoit les documents (PDF DCE, ZIP, XML UBL, emails), les persiste, déclenche le pipeline de parsing, et notifie les autres agents via le bus d'événements interne.

| Attribut | Valeur |
|----------|--------|
| **Module** | `takaos.agents.sourcer` |
| **Classe principale** | `SourcerAgent` |
| **Dépendances** | `DocumentStore`, `ParsingPipeline`, `EventBus`, `TenderRepository` |
| **Concurrence** | Thread-safe, stateless |

#### Types d'entrée supportés

```python
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, BinaryIO
from datetime import datetime

class InputSourceType(Enum):
    """Source de réception du DCE."""
    PDF_DCE = auto()       # Document de Consultation des Entreprises (PDF)
    ZIP_ARCHIVE = auto()   # Archive ZIP contenant multiple PDF/XML
    XML_UBL = auto()       # Format UBL 2.1 / UN/CEFACT
    EMAIL_EML = auto()     # Email au format .eml ou .msg
    MANUAL_FORM = auto()   # Saisie manuelle via l'interface web
    API_PULL = auto()      # Pull depuis API externe (BOAMP, TED, etc.)

class DocumentFormat(Enum):
    """Format physique du document reçu."""
    PDF_TEXT = auto()      # PDF natif texte (texte extractible)
    PDF_SCANNED = auto()   # PDF image (nécessite OCR)
    XML = auto()           # XML structuré (UBL, etc.)
    EMAIL = auto()         # Email brut
    UNKNOWN = auto()       # Format non détecté

@dataclass(frozen=True)
class SourcerInput:
    """DTO d'entrée pour l'Agent Sourcer."""
    tenant_id: str                          # UUID du tenant (isolation multi-entreprise)
    source_type: InputSourceType            # Type de source
    filename: str                           # Nom du fichier original
    content: bytes                          # Contenu brut du fichier
    content_type: str                       # MIME type (application/pdf, etc.)
    uploaded_by: Optional[str] = None       # UUID de l'utilisateur (si upload manuel)
    external_id: Optional[str] = None       # ID externe (ex: référence BOAMP)
    metadata: dict = field(default_factory=dict)  # Métadonnées libres
    received_at: datetime = field(default_factory=datetime.utcnow)
```

#### Flux complet — Upload à Tender créé

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FLUX AGENT SOURCER (ao_sourcer)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [1. RECEPTEUR]        [2. PERSISTANCE]      [3. DETECTION FORMAT]        │
│  ┌─────────────┐      ┌──────────────┐      ┌──────────────────┐          │
│  │ Upload PDF  │─────▶│ Save to disk │─────▶│ Detect format    │          │
│  │ ZIP / XML   │      │ + S3 backup  │      │ (text/scanned/   │          │
│  │ Email / API │      │ (async)      │      │  xml/email)      │          │
│  └─────────────┘      └──────────────┘      └──────────────────┘          │
│                                                      │                      │
│                                                      ▼                      │
│  [4. CREATION TENDER]     [5. EVENT PARSING]      [6. NOTIFICATION]       │
│  ┌──────────────────┐    ┌─────────────────┐    ┌─────────────────┐       │
│  │ INSERT tenders   │    │ Emit            │    │ WebSocket       │       │
│  │   status='detected'    │ 'tender.received'    │   to client     │       │
│  │   link document  │    │   + document_id     │   (async)       │       │
│  └──────────────────┘    └─────────────────┘    └─────────────────┘       │
│         │                       │                                           │
│         ▼                       ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │                    [7. PARSING PIPELINE]                         │       │
│  │              (déclenché async par event handler)                 │       │
│  │  ┌──────────┐ ──▶ ┌──────────┐ ──▶ ┌──────────┐ ──▶ ┌────────┐ │       │
│  │  │ pypdf    │     │pdfplumber│     │ Tesseract│     │ Mistral│ │       │
│  │  │ Niveau 1 │     │ Niveau 2 │     │ Niveau 3 │     │Niveau 4│ │       │
│  │  └──────────┘     └──────────┘     └──────────┘     └────────┘ │       │
│  └─────────────────────────────────────────────────────────────────┘       │
│                                    │                                        │
│                                    ▼                                        │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │ [8. MISE A JOUR TENDER]                                            │    │
│  │   - Statut → 'parsed' | 'parsed_partial' | 'failed'               │    │
│  │   - Champs extraits : cpv, amount, deadline, lots, criteria       │    │
│  │   - Mise à jour mémoire épisodique (pgvector)                     │    │
│  │   - Emit 'tender.parsed' → déclenche Qualifieur                   │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Pseudo-code complet — Agent Sourcer

```python
# ============================================================
# takaos/agents/sourcer.py — Agent Sourcer (ao_sourcer)
# ============================================================

import asyncio
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Optional, BinaryIO, Dict, Any
import aiofiles

import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from takaos.core.events import EventBus, TenderReceivedEvent, TenderParsedEvent
from takaos.core.exceptions import (
    StorageError, FormatDetectionError, UnsupportedFormatError
)
from takaos.db.repositories import TenderRepository, DocumentRepository
from takaos.parsing.pipeline import ParsingPipeline, ParsingResult
from takaos.storage.document_store import DocumentStore
from takaos.models.domain import Tender, Document, TenderStatus

logger = structlog.get_logger("takaos.agents.sourcer")


class SourcerAgent:
    """
    Agent Sourcer — Point d'entrée pour la réception de DCE.
    
    Responsabilités :
    1. Recevoir et valider les fichiers entrants (PDF, ZIP, XML, email)
    2. Persister les documents sur stockage objet (S3/local)
    3. Détecter le format et créer l'enregistrement Tender en base
    4. Émettre l'événement 'tender.received' pour déclencher le parsing
    5. Retourner immédiatement un handle de tracking au client
    
    Conception : Stateless, thread-safe. Chaque appel est indépendant.
    """

    # ------------------------------------------------------------------
    # Constructeur et injection de dépendances
    # ------------------------------------------------------------------

    def __init__(
        self,
        document_store: DocumentStore,
        tender_repository: TenderRepository,
        document_repository: DocumentRepository,
        parsing_pipeline: ParsingPipeline,
        event_bus: EventBus,
        config: Dict[str, Any],
    ) -> None:
        self._store = document_store
        self._tender_repo = tender_repository
        self._doc_repo = document_repository
        self._pipeline = parsing_pipeline
        self._event_bus = event_bus
        self._config = config
        self._upload_base_path = Path(config.get("storage.upload_path", "/data/uploads"))

    # ------------------------------------------------------------------
    # API Publique — Point d'entrée principal
    # ------------------------------------------------------------------

    async def process_input(self, inp: SourcerInput) -> Dict[str, Any]:
        """
        Point d'entrée unique pour traiter un nouveau DCE.
        
        Returns :
            {
                "tender_id": "uuid",
                "document_id": "uuid",
                "status": "detected",
                "estimated_parse_time": 15,  # secondes estimées
                "tracking_url": "/api/v1/tenders/uuid/status"
            }
        
        Raises :
            StorageError : Échec de persistance
            UnsupportedFormatError : Format non supporté
        """
        # --- ÉTAPE 1 : Validation et fingerprinting ---
        file_hash = self._compute_hash(inp.content)
        
        # Déduplication : ce fichier a-t-il déjà été traité ?
        existing = await self._doc_repo.find_by_hash(file_hash, inp.tenant_id)
        if existing:
            logger.info("sourcer.deduplication_hit", 
                       tenant_id=inp.tenant_id, 
                       file_hash=file_hash[:16])
            return {
                "tender_id": existing.tender_id,
                "document_id": existing.id,
                "status": "duplicate",
                "message": "Document déjà traité"
            }

        # --- ÉTAPE 2 : Détection du format physique ---
        doc_format = self._detect_format(inp.content, inp.content_type)
        logger.info("sourcer.format_detected",
                   tenant_id=inp.tenant_id,
                   format=doc_format.name,
                   filename=inp.filename)

        # --- ÉTAPE 3 : Persistance asynchrone du fichier ---
        storage_path = await self._persist_file(inp, file_hash)

        # --- ÉTAPE 4 : Création du Document en base ---
        document = Document(
            id=generate_uuid(),
            tenant_id=inp.tenant_id,
            filename=inp.filename,
            content_type=inp.content_type,
            file_size=len(inp.content),
            file_hash=file_hash,
            storage_path=str(storage_path),
            format=doc_format.name,
            source_type=inp.source_type.name,
            external_id=inp.external_id,
            uploaded_by=inp.uploaded_by,
            metadata=inp.metadata,
            created_at=datetime.utcnow(),
        )
        await self._doc_repo.insert(document)

        # --- ÉTAPE 5 : Création du Tender ---
        tender = Tender(
            id=generate_uuid(),
            tenant_id=inp.tenant_id,
            status=TenderStatus.DETECTED,
            source_type=inp.source_type.name,
            source_reference=inp.external_id,
            document_id=document.id,
            received_at=inp.received_at,
            created_at=datetime.utcnow(),
        )
        await self._tender_repo.insert(tender)

        # Liaison bidirectionnelle tender <-> document
        document.tender_id = tender.id
        await self._doc_repo.update(document)

        logger.info("sourcer.tender_created",
                   tenant_id=inp.tenant_id,
                   tender_id=tender.id,
                   document_id=document.id)

        # --- ÉTAPE 6 : Émission événement + lancement parsing async ---
        event = TenderReceivedEvent(
            tender_id=tender.id,
            tenant_id=inp.tenant_id,
            document_id=document.id,
            source_type=inp.source_type.name,
            doc_format=doc_format.name,
        )
        
        # Fire-and-forget : le parsing se fait en tâche de fond
        asyncio.create_task(
            self._handle_tender_received(event),
            name=f"parse-{tender.id[:8]}"
        )

        # --- ÉTAPE 7 : Réponse immédiate au client ---
        return {
            "tender_id": tender.id,
            "document_id": document.id,
            "status": TenderStatus.DETECTED.value,
            "estimated_parse_time": self._estimate_parse_time(
                len(inp.content), doc_format
            ),
            "tracking_url": f"/api/v1/tenders/{tender.id}/status",
        }

    # ------------------------------------------------------------------
    # Méthodes internes
    # ------------------------------------------------------------------

    def _compute_hash(self, content: bytes) -> str:
        """SHA-256 du contenu pour déduplication."""
        return hashlib.sha256(content).hexdigest()

    def _detect_format(self, content: bytes, content_type: str) -> DocumentFormat:
        """
        Détection du format physique du document.
        Heuristiques multi-critères (magic bytes + content-type + structure).
        """
        # Magic bytes
        if content[:4] == b"%PDF":
            # PDF texte vs PDF scanné : vérifier la présence de texte extractible
            text_ratio = self._estimate_text_ratio(content)
            if text_ratio > 0.05:  # >5% de texte extractible
                return DocumentFormat.PDF_TEXT
            return DocumentFormat.PDF_SCANNED
        
        if content[:5] == b"<?xml" or b"<Ubl" in content[:100]:
            return DocumentFormat.XML
        
        if content_type in ("message/rfc822", "application/vnd.ms-outlook"):
            return DocumentFormat.EMAIL
        
        # Fallback sur content-type MIME
        mime_mapping = {
            "application/pdf": DocumentFormat.PDF_TEXT,
            "application/xml": DocumentFormat.XML,
            "text/xml": DocumentFormat.XML,
        }
        if content_type in mime_mapping:
            return mime_mapping[content_type]
        
        raise UnsupportedFormatError(
            f"Format non supporté : content_type={content_type}, "
            f"magic={content[:8].hex()}"
        )

    def _estimate_text_ratio(self, content: bytes) -> float:
        """
        Estimation rapide du ratio texte/contenu dans un PDF.
        Retourne un float entre 0.0 (image pur) et 1.0 (texte pur).
        """
        # Heuristique rapide : compter les caractères imprimables ASCII
        printable = sum(1 for b in content[:8192] if 32 <= b <= 126)
        return printable / max(len(content[:8192]), 1)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _persist_file(self, inp: SourcerInput, file_hash: str) -> Path:
        """
        Persistance du fichier sur stockage local + backup S3 (async).
        Structure : /data/uploads/{tenant_id}/{year}/{month}/{hash[:2]}/{hash}.pdf
        """
        now = datetime.utcnow()
        relative_path = Path(
            inp.tenant_id,
            str(now.year),
            f"{now.month:02d}",
            file_hash[:2],
            f"{file_hash}.{self._get_extension(inp.filename)}"
        )
        full_path = self._upload_base_path / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Écriture asynchrone
        async with aiofiles.open(full_path, "wb") as f:
            await f.write(inp.content)

        # Backup S3 (fire-and-forget)
        asyncio.create_task(
            self._store.upload_backup(str(relative_path), inp.content)
        )

        return full_path

    def _get_extension(self, filename: str) -> str:
        """Extraction sécurisée de l'extension."""
        ext = Path(filename).suffix.lower()
        return ext.lstrip(".") if ext else "bin"

    def _estimate_parse_time(self, file_size: int, fmt: DocumentFormat) -> int:
        """Estimation du temps de parsing pour le client (secondes)."""
        base_times = {
            DocumentFormat.PDF_TEXT: 5,
            DocumentFormat.PDF_SCANNED: 30,
            DocumentFormat.XML: 3,
            DocumentFormat.EMAIL: 10,
        }
        base = base_times.get(fmt, 15)
        # +1s par Mo
        size_overhead = max(0, file_size // (1024 * 1024))
        return base + size_overhead

    # ------------------------------------------------------------------
    # Event Handler — Parsing asynchrone
    # ------------------------------------------------------------------

    async def _handle_tender_received(self, event: TenderReceivedEvent) -> None:
        """
        Handler déclenché par l'événement 'tender.received'.
        Exécute le pipeline de parsing complet en tâche de fond.
        """
        logger.info("sourcer.parsing_started",
                   tender_id=event.tender_id,
                   document_id=event.document_id)

        try:
            # --- Récupération du document ---
            document = await self._doc_repo.get(event.document_id)
            tender = await self._tender_repo.get(event.tender_id)

            # --- Exécution du pipeline de parsing ---
            parse_result: ParsingResult = await self._pipeline.execute(
                document=document,
                tenant_id=event.tenant_id,
            )

            # --- Mise à jour du Tender avec les données extraites ---
            tender.status = (
                TenderStatus.PARSED if parse_result.success
                else TenderStatus.PARSED_PARTIAL if parse_result.partial
                else TenderStatus.PARSING_FAILED
            )
            
            # Injection des champs extraits
            if parse_result.extracted_fields:
                tender.cpv_code = parse_result.extracted_fields.get("cpv_code")
                tender.cpv_description = parse_result.extracted_fields.get("cpv_description")
                tender.estimated_amount = parse_result.extracted_fields.get("estimated_amount")
                tender.currency = parse_result.extracted_fields.get("currency", "EUR")
                tender.deadline_submission = parse_result.extracted_fields.get("deadline_submission")
                tender.deadline_questions = parse_result.extracted_fields.get("deadline_questions")
                tender.title = parse_result.extracted_fields.get("title")
                tender.description = parse_result.extracted_fields.get("description")
                tender.buyer_name = parse_result.extracted_fields.get("buyer_name")
                tender.lots = parse_result.extracted_fields.get("lots", [])
                tender.award_criteria = parse_result.extracted_fields.get("award_criteria", [])
                tender.keywords = parse_result.extracted_fields.get("keywords", [])

            tender.parsing_metadata = {
                "levels_tried": parse_result.levels_tried,
                "level_succeeded": parse_result.level_succeeded,
                "processing_time_ms": parse_result.processing_time_ms,
                "confidence_scores": parse_result.confidence_scores,
                "parse_log": parse_result.log_entries,
            }
            tender.updated_at = datetime.utcnow()

            await self._tender_repo.update(tender)

            # --- Émission événement 'tender.parsed' ---
            parsed_event = TenderParsedEvent(
                tender_id=tender.id,
                tenant_id=event.tenant_id,
                status=tender.status.value,
                extracted_fields=list(parse_result.extracted_fields.keys()),
                confidence_global=parse_result.global_confidence,
            )
            await self._event_bus.publish(parsed_event)

            logger.info("sourcer.parsing_completed",
                       tender_id=tender.id,
                       status=tender.status.value,
                       fields_found=len(parse_result.extracted_fields),
                       confidence=parse_result.global_confidence)

        except Exception as exc:
            logger.error("sourcer.parsing_failed",
                        tender_id=event.tender_id,
                        error=str(exc),
                        exc_info=True)
            
            # Mise à jour du statut en erreur
            await self._tender_repo.update_status(
                event.tender_id, TenderStatus.PARSING_FAILED,
                error_message=str(exc)
            )

            # Émission événement d'erreur
            await self._event_bus.publish(TenderParsedEvent(
                tender_id=event.tender_id,
                tenant_id=event.tenant_id,
                status="failed",
                extracted_fields=[],
                confidence_global=0.0,
                error=str(exc),
            ))
```

#### Schéma de la table `documents` (liée au Sourcer)

```sql
-- ============================================================
-- Table documents — Stockage des métadonnées de fichiers DCE
-- ============================================================

CREATE TABLE documents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    tender_id       UUID REFERENCES tenders(id) ON DELETE SET NULL,
    
    -- Identité du fichier
    filename        VARCHAR(512) NOT NULL,
    content_type    VARCHAR(128) NOT NULL,        -- MIME type
    file_size       BIGINT NOT NULL,              -- Taille en octets
    file_hash       VARCHAR(64) NOT NULL,         -- SHA-256 (déduplication)
    
    -- Stockage
    storage_path    VARCHAR(1024) NOT NULL,       -- Chemin relatif sur stockage
    storage_backend VARCHAR(32) DEFAULT 'local',  -- 'local' | 's3' | 'gcs'
    
    -- Caractérisation du document
    format          VARCHAR(32) NOT NULL,         -- 'PDF_TEXT' | 'PDF_SCANNED' | 'XML' | 'EMAIL'
    source_type     VARCHAR(32) NOT NULL,         -- 'PDF_DCE' | 'ZIP_ARCHIVE' | 'XML_UBL' | ...
    external_id     VARCHAR(256),                 -- Référence externe (BOAMP, TED...)
    
    -- Traçabilité
    uploaded_by     UUID REFERENCES users(id),
    metadata        JSONB DEFAULT '{}',           -- Métadonnées libres
    
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    
    -- Contraintes
    CONSTRAINT uq_doc_hash_per_tenant UNIQUE (tenant_id, file_hash)
);

-- Index pour la déduplication rapide
CREATE INDEX idx_documents_hash ON documents(tenant_id, file_hash);

-- Index pour lister les documents d'un tender
CREATE INDEX idx_documents_tender ON documents(tender_id);
```

---

### 3.1.2 Agent Qualifieur (`ao_qualifier`)

#### Responsabilité

L'Agent Qualifieur évalue chaque tender fraîchement parsé et produit une décision **GO / NO-GO / MAYBE** en combinant un scoring à base de règles métier (80% du poids) et un scoring par LLM (20% du poids, uniquement en zone ambiguë).

| Attribut | Valeur |
|----------|--------|
| **Module** | `takaos.agents.qualifier` |
| **Classe principale** | `QualifierAgent` |
| **Dépendances** | `TenderRepository`, `TenantConfigRepository`, `MemorySystem`, `MistralClient` |
| **Trigger** | Événement `tender.parsed` (event-driven) |

#### Modèle de données — Règles de qualification

```python
# ============================================================
# takaos/models/qualification.py — Modèles du Qualifieur
# ============================================================

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional, Any

class QualificationDecision(Enum):
    """Décision finale de qualification."""
    GO = "go"           # Poursuivre → créer dossier de réponse
    NO_GO = "no_go"     # Rejeter → archiver
    MAYBE = "maybe"     # Révision manuelle requise

class AmountRange:
    """Fourchette de montant acceptable pour un tenant."""
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    currency: str = "EUR"

@dataclass
class QualificationRules:
    """
    Règles de qualification configurables par tenant.
    Chaque critère a un poids (0.0 - 1.0) et un seuil de rejet.
    """
    tenant_id: str
    
    # --- Critère CPV ---
    cpv_weights: Dict[str, float] = field(default_factory=dict)
    # Ex: {"03311000": 1.0, "03111000": 0.8, "DEFAULT": 0.0}
    # Les CPV autorisés avec leur poids de correspondance
    
    # --- Critère Montant ---
    amount_range: Optional[AmountRange] = None
    amount_weight: float = 0.20           # Poids dans le score global
    
    # --- Critère Deadline ---
    min_preparation_days: int = 14        # Jours minimum pour préparer
    deadline_weight: float = 0.20         # Poids dans le score global
    
    # --- Critère Mémoire Épisodique ---
    memory_weight: float = 0.25           # Poids de l'historique
    memory_similarity_threshold: float = 0.75  # Seuil de similarité cosine
    
    # --- Pondération globale ---
    rules_weight: float = 0.80            # 80% règles métier
    llm_weight: float = 0.20              # 20% LLM fallback
    
    # --- Seuils de décision ---
    threshold_go: float = 0.70
    threshold_no_go: float = 0.30
    
    # --- Zones d'ambiguité déclenchant le LLM ---
    llm_trigger_min: float = 0.30
    llm_trigger_max: float = 0.70

@dataclass
class CriterionScore:
    """Score individuel d'un critère de qualification."""
    name: str                             # Nom du critère
    score: float                          # Score brut (0.0 - 1.0)
    weight: float                         # Poids appliqué
    weighted_score: float                 # Score * poids
    passed: bool                          # Le critère est-il satisfait ?
    details: Dict[str, Any] = field(default_factory=dict)
    # Ex: {"cpv_matched": "03311000", "similarity": 0.95}

@dataclass
class QualificationResult:
    """Résultat complet de la qualification d'un tender."""
    tender_id: str
    tenant_id: str
    
    # Scores
    rules_score: float                    # Score règles (0.0 - 1.0)
    llm_score: Optional[float] = None     # Score LLM (0.0 - 1.0), si déclenché
    global_score: float = 0.0             # Score global pondéré
    
    # Détail par critère
    criterion_scores: List[CriterionScore] = field(default_factory=list)
    
    # Décision
    decision: QualificationDecision = QualificationDecision.MAYBE
    
    # Justification
    justification: str = ""               # Texte explicatif de la décision
    llm_reasoning: Optional[str] = None   # Raisonnement du LLM (si déclenché)
    
    # Méta
    rules_processing_ms: int = 0
    llm_processing_ms: int = 0
    total_processing_ms: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
```

#### Algorithme complet de scoring

```
╔══════════════════════════════════════════════════════════════════════════════╗
║           ALGORITHME DE QUALIFICATION — Agent Qualifieur                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ENTRÉE  : tender (parsé), rules (config tenant), memory (pgvector)          ║
║  SORTIE  : QualificationResult (GO / NO-GO / MAYBE + scores + justif.)       ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────┐    ║
║  │ ÉTAPE 1 : SCORING RÈGLES MÉTIER (poids : 80%)                      │    ║
║  │ ─────────────────────────────────────────────                       │    ║
║  │                                                                     │    ║
║  │  Critère 1 : CPV Match                    [weight configurable]     │    ║
║  │  ─────────────────────                                              │    ║
║  │  IF tender.cpv_code IN rules.cpv_weights:                           │    ║
║  │      cpv_score = rules.cpv_weights[tender.cpv_code]                 │    ║
║  │  ELSE IF cpv parent match:                                          │    ║
║  │      cpv_score = 0.5  # Correspondance partielle niveau parent      │    ║
║  │  ELSE:                                                              │    ║
║  │      cpv_score = 0.0  # CPV non dans le périmètre                   │    ║
║  │                                                                     │    ║
║  │  Critère 2 : Montant dans fourchette           [weight: 0.20]       │    ║
║  │  ───────────────────────────────────                                │    ║
║  │  IF rules.amount_range is None:                                     │    ║
║  │      amount_score = 1.0  # Pas de contrainte                        │    ║
║  │  ELSE IF tender.amount IS NULL:                                     │    ║
║  │      amount_score = 0.5  # Information manquante                    │    ║
║  │  ELSE IF range_min <= amount <= range_max:                          │    ║
║  │      amount_score = 1.0                                             │    ║
║  │  ELSE IF amount < range_min:                                        │    ║
║  │      amount_score = max(0, 1 - (range_min - amount)/range_min)      │    ║
║  │  ELSE:  # amount > range_max                                        │    ║
║  │      amount_score = max(0, 1 - (amount - range_max)/range_max)      │    ║
║  │                                                                     │    ║
║  │  Critère 3 : Deadline suffisante               [weight: 0.20]       │    ║
║  │  ───────────────────────────────                                    │    ║
║  │  IF tender.deadline_submission IS NULL:                             │    ║
║  │      deadline_score = 0.5  # Information manquante                  │    ║
║  │  ELSE:                                                              │    ║
║  │      days_remaining = (deadline - today).days                       │    ║
║  │      IF days_remaining >= min_preparation_days * 2:                 │    ║
║  │          deadline_score = 1.0  # Confortable                        │    ║
║  │      ELSE IF days_remaining >= min_preparation_days:                │    ║
║  │          deadline_score = 0.7  # Juste assez                        │    ║
║  │      ELSE IF days_remaining > 0:                                    │    ║
║  │          deadline_score = max(0, days_remaining / min_preparation_days)║ ║
║  │      ELSE:                                                          │    ║
║  │          deadline_score = 0.0  # Deadline dépassée                  │    ║
║  │                                                                     │    ║
║  │  Critère 4 : Mémoire Épisodique                [weight: 0.25]       │    ║
║  │  ──────────────────────────────                                     │    ║
║  │  similar_cases = memory.search_similar(                             │    ║
║  │      text=tender.title + " " + tender.description,                  │    ║
║  │      tenant_id=tenant_id,                                           │    ║
║  │      top_k=5,                                                       │    ║
║  │      filters={"tags": ["success"] or ["failure"]}                   │    ║
║  │  )                                                                  │    ║
║  │  IF similar_cases:                                                  │    ║
║  │      win_rate = count_success / len(similar_cases)                  │    ║
║  │      avg_similarity = mean(c.similarity for c in similar_cases)     │    ║
║  │      memory_score = win_rate * avg_similarity                       │    ║
║  │  ELSE:                                                              │    ║
║  │      memory_score = 0.5  # Pas d'historique = neutre                │    ║
║  │                                                                     │    ║
║  │  ─────────────────────────────────────────────────────────────      │    ║
║  │  SCORE RÈGLES = Σ (score_criterion * weight_criterion)              │    ║
║  │  score_rules = cpv_score*w_cpv + amount_score*w_amount + ...        │    ║
║  │                                                                     │    ║
║  └─────────────────────────────────────────────────────────────────────┘    ║
║                              │                                               ║
║                              ▼                                               ║
║  ┌─────────────────────────────────────────────────────────────────────┐    ║
║  │ ÉTAPE 2 : DÉCISION PRÉLIMINAIRE + DÉCLENCHEMENT LLM                │    ║
║  │ ───────────────────────────────────────────────────                  │    ║
║  │                                                                     │    ║
║  │  IF score_rules >= 0.70:  ──▶  DECISION = GO (pas de LLM)           │    ║
║  │  IF score_rules <= 0.30:  ──▶  DECISION = NO-GO (pas de LLM)        │    ║
║  │  IF 0.30 < score_rules < 0.70:                                      │    ║
║  │      ──▶  DÉCLENCHE LLM FALLBACK (zone ambiguë)                     │    ║
║  │                                                                     │    ║
║  └─────────────────────────────────────────────────────────────────────┘    ║
║                              │                                               ║
║                              ▼ (si zone ambiguë)                             ║
║  ┌─────────────────────────────────────────────────────────────────────┐    ║
║  │ ÉTAPE 3 : LLM FALLBACK (poids : 20%, uniquement si ambigu)          │    ║
║  │ ────────────────────────────────────────────────                     │    ║
║  │                                                                     │    ║
║  │  Construction du contexte :                                         │    ║
║  │    • Résumé du DCE (titre, description, montant, deadline)          │    ║
║  │    • Règles du tenant (CPV cibles, fourchettes, historique)         │    ║
║  │    • Cas similaires en mémoire (succès/échecs)                      │    ║
║  │    • Scores des règles individuelles (pour transparence)            │    ║
║  │                                                                     │    ║
║  │  Template Jinja2 → Prompt structuré → API Mistral                   │    ║
║  │                                                                     │    ║
║  │  Réponse attendue : JSON structuré                                  │    ║
║  │  {                                                                  │    ║
║  │    "score": 0.65,         # Score LLM 0.0-1.0                       │    ║
║  │    "justification": "...",# Raisonnement explicatif                 │    ║
║  │    "key_factors": [...],  # Facteurs déterminants                   │    ║
║  │    "confidence": 0.85      # Confiance du LLM dans sa réponse       │    ║
║  │  }                                                                  │    ║
║  │                                                                     │    ║
║  │  score_llm = response.score * response.confidence  # Pénalisation   │    ║
║  └─────────────────────────────────────────────────────────────────────┘    ║
║                              │                                               ║
║                              ▼                                               ║
║  ┌─────────────────────────────────────────────────────────────────────┐    ║
║  │ ÉTAPE 4 : FUSION ET DÉCISION FINALE                                │    ║
║  │ ────────────────────────────────────                                 │    ║
║  │                                                                     │    ║
║  │  IF LLM déclenché :                                                 │    ║
║  │      score_global = score_rules * 0.80 + score_llm * 0.20           │    ║
║  │  ELSE:                                                              │    ║
║  │      score_global = score_rules  # Règles seules = 100%             │    ║
║  │                                                                     │    ║
║  │  ──▶ DÉCISION FINALE :                                              │    ║
║  │      score_global >= 0.70  →  GO                                    │    ║
║  │      score_global <= 0.30  →  NO-GO                                 │    ║
║  │      0.30 < score < 0.70   →  MAYBE                                 │    ║
║  │                                                                     │    ║
║  └─────────────────────────────────────────────────────────────────────┘    ║
║                              │                                               ║
║                              ▼                                               ║
║  ┌─────────────────────────────────────────────────────────────────────┐    ║
║  │ ÉTAPE 5 : PERSISTANCE ET NOTIFICATION                              │    ║
║  │ ─────────────────────────────────────                                │    ║
║  │                                                                     │    ║
║  │  • INSERT qualification_results (score détaillé)                    │    ║
║  │  • UPDATE tenders SET status = 'qualified', decision = GO/NOGO     │    ║
║  │  • Emit 'tender.qualified' → déclenche Tracker + workflows          │    ║
║  │  • Notification WebSocket au client (temps réel)                    │    ║
║  │                                                                     │    ║
║  └─────────────────────────────────────────────────────────────────────┘    ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

#### Pseudo-code Python — Agent Qualifieur

```python
# ============================================================
# takaos/agents/qualifier.py — Agent Qualifieur (ao_qualifier)
# ============================================================

import time
from dataclasses import asdict
from datetime import datetime, date
from typing import List, Dict, Optional, Any

import structlog
import httpx

from takaos.core.events import EventBus, TenderParsedEvent, TenderQualifiedEvent
from takaos.db.repositories import TenderRepository, TenantConfigRepository
from takaos.llm.mistral_client import MistralClient, CircuitOpenError
from takaos.memory.vector_store import MemorySystem
from takaos.models.domain import Tender, TenderStatus
from takaos.models.qualification import (
    QualificationRules, CriterionScore, QualificationResult,
    QualificationDecision, AmountRange,
)
from takaos.templates.qualifier import QUALIFIER_PROMPT_TEMPLATE

logger = structlog.get_logger("takaos.agents.qualifier")


class QualifierAgent:
    """
    Agent Qualifieur — Décide GO / NO-GO / MAYBE pour chaque tender.
    
    Architecture :
    - 80% règles métier (CPV, montant, deadline, mémoire)
    - 20% LLM fallback uniquement en zone ambiguë (0.3 - 0.7)
    - Circuit breaker sur l'API Mistral pour dégradation gracieuse
    """

    def __init__(
        self,
        tender_repository: TenderRepository,
        tenant_config_repository: TenantConfigRepository,
        memory_system: MemorySystem,
        mistral_client: MistralClient,
        event_bus: EventBus,
    ) -> None:
        self._tender_repo = tender_repository
        self._config_repo = tenant_config_repository
        self._memory = memory_system
        self._llm = mistral_client
        self._event_bus = event_bus

    # ------------------------------------------------------------------
    # API Publique
    # ------------------------------------------------------------------

    async def qualify(self, tender_id: str, tenant_id: str) -> QualificationResult:
        """
        Qualifie un tender et retourne le résultat complet.
        Appelé par l'event handler 'tender.parsed'.
        """
        start_time = time.monotonic()
        
        # --- Récupération des données ---
        tender = await self._tender_repo.get(tender_id)
        rules = await self._config_repo.get_qualification_rules(tenant_id)
        
        logger.info("qualifier.start",
                   tender_id=tender_id,
                   tenant_id=tenant_id,
                   tender_title=tender.title)

        # --- ÉTAPE 1 : Scoring règles ---
        rules_start = time.monotonic()
        criterion_scores = await self._score_rules(tender, rules, tenant_id)
        
        # Calcul du score règles pondéré
        score_rules = sum(cs.weighted_score for cs in criterion_scores)
        score_rules = max(0.0, min(1.0, score_rules))  # Clamp [0, 1]
        rules_ms = int((time.monotonic() - rules_start) * 1000)
        
        logger.info("qualifier.rules_scored",
                   tender_id=tender_id,
                   score_rules=round(score_rules, 3),
                   criteria=[{c.name: round(c.score, 2)} for c in criterion_scores])

        # --- ÉTAPE 2 & 3 : Décision préliminaire + LLM fallback ---
        llm_score: Optional[float] = None
        llm_reasoning: Optional[str] = None
        llm_ms = 0
        
        if rules.llm_trigger_min < score_rules < rules.llm_trigger_max:
            # Zone ambiguë → déclencher le LLM
            logger.info("qualifier.llm_triggered",
                       tender_id=tender_id,
                       score_rules=round(score_rules, 3))
            
            llm_start = time.monotonic()
            llm_result = await self._llm_fallback(tender, rules, criterion_scores, tenant_id)
            llm_ms = int((time.monotonic() - llm_start) * 1000)
            
            if llm_result is not None:
                llm_score = llm_result["score"] * llm_result.get("confidence", 1.0)
                llm_score = max(0.0, min(1.0, llm_score))
                llm_reasoning = llm_result.get("justification", "")
                
                logger.info("qualifier.llm_scored",
                           tender_id=tender_id,
                           llm_score=round(llm_score, 3),
                           confidence=llm_result.get("confidence"))

        # --- ÉTAPE 4 : Fusion et décision finale ---
        if llm_score is not None:
            score_global = score_rules * rules.rules_weight + llm_score * rules.llm_weight
        else:
            score_global = score_rules
        
        score_global = max(0.0, min(1.0, score_global))
        
        # Décision
        if score_global >= rules.threshold_go:
            decision = QualificationDecision.GO
        elif score_global <= rules.threshold_no_go:
            decision = QualificationDecision.NO_GO
        else:
            decision = QualificationDecision.MAYBE
        
        total_ms = int((time.monotonic() - start_time) * 1000)
        
        # Construction du résultat
        justification = self._build_justification(
            criterion_scores, decision, score_global, llm_reasoning
        )
        
        result = QualificationResult(
            tender_id=tender_id,
            tenant_id=tenant_id,
            rules_score=score_rules,
            llm_score=llm_score,
            global_score=round(score_global, 4),
            criterion_scores=criterion_scores,
            decision=decision,
            justification=justification,
            llm_reasoning=llm_reasoning,
            rules_processing_ms=rules_ms,
            llm_processing_ms=llm_ms,
            total_processing_ms=total_ms,
        )

        # --- ÉTAPE 5 : Persistance ---
        await self._persist_result(result)
        
        logger.info("qualifier.completed",
                   tender_id=tender_id,
                   decision=decision.value,
                   global_score=round(score_global, 3),
                   total_ms=total_ms)

        return result

    # ------------------------------------------------------------------
    # Scoring Règles — Détails par critère
    # ------------------------------------------------------------------

    async def _score_rules(
        self,
        tender: Tender,
        rules: QualificationRules,
        tenant_id: str,
    ) -> List[CriterionScore]:
        """Calcule les scores pour chaque critère métier."""
        scores: List[CriterionScore] = []
        
        # --- Critère 1 : CPV Match ---
        scores.append(self._score_cpv(tender, rules))
        
        # --- Critère 2 : Montant ---
        scores.append(self._score_amount(tender, rules))
        
        # --- Critère 3 : Deadline ---
        scores.append(self._score_deadline(tender, rules))
        
        # --- Critère 4 : Mémoire Épisodique ---
        scores.append(await self._score_memory(tender, rules, tenant_id))
        
        return scores

    def _score_cpv(self, tender: Tender, rules: QualificationRules) -> CriterionScore:
        """
        Score de correspondance CPV.
        Correspondance exacte = 1.0, parent = 0.5, absent = 0.0.
        """
        if not tender.cpv_code:
            return CriterionScore(
                name="cpv_match",
                score=0.5,
                weight=rules.cpv_weights.get("_weight", 0.35),
                weighted_score=0.5 * rules.cpv_weights.get("_weight", 0.35),
                passed=False,
                details={"reason": "CPV non extrait du DCE"}
            )
        
        # Correspondance exacte
        if tender.cpv_code in rules.cpv_weights:
            weight = rules.cpv_weights[tender.cpv_code]
            return CriterionScore(
                name="cpv_match",
                score=1.0,
                weight=weight,
                weighted_score=1.0 * weight,
                passed=True,
                details={"cpv_matched": tender.cpv_code, "match_type": "exact"}
            )
        
        # Correspondance parent (8 premiers caractères = niveau famille)
        cpv_parent = tender.cpv_code[:8] if len(tender.cpv_code) >= 8 else None
        if cpv_parent and any(k.startswith(cpv_parent) for k in rules.cpv_weights.keys()):
            parent_weight = max(
                v for k, v in rules.cpv_weights.items() if k.startswith(cpv_parent)
            )
            return CriterionScore(
                name="cpv_match",
                score=0.5,
                weight=parent_weight,
                weighted_score=0.5 * parent_weight,
                passed=True,
                details={"cpv_matched": tender.cpv_code, "match_type": "parent",
                        "parent_cpv": cpv_parent}
            )
        
        # Aucune correspondance
        return CriterionScore(
            name="cpv_match",
            score=0.0,
            weight=rules.cpv_weights.get("_default_weight", 0.35),
            weighted_score=0.0,
            passed=False,
            details={"cpv_tender": tender.cpv_code, "match_type": "none"}
        )

    def _score_amount(self, tender: Tender, rules: QualificationRules) -> CriterionScore:
        """
        Score de correspondance du montant estimé.
        Dans la fourchette = 1.0, hors fourchette = décroissance linéaire.
        """
        if rules.amount_range is None:
            return CriterionScore(
                name="amount_fit",
                score=1.0, weight=rules.amount_weight,
                weighted_score=rules.amount_weight,
                passed=True,
                details={"reason": "Pas de contrainte de montant configurée"}
            )
        
        if tender.estimated_amount is None:
            return CriterionScore(
                name="amount_fit",
                score=0.5, weight=rules.amount_weight,
                weighted_score=0.5 * rules.amount_weight,
                passed=False,
                details={"reason": "Montant non extrait du DCE"}
            )
        
        rmin = rules.amount_range.min_amount
        rmax = rules.amount_range.max_amount
        amount = tender.estimated_amount
        
        if rmin is not None and rmax is not None and rmin <= amount <= rmax:
            score = 1.0
        elif rmin is not None and amount < rmin:
            # Décroissance linéaire jusqu'à 0
            score = max(0.0, 1.0 - (rmin - amount) / rmin) if rmin > 0 else 0.0
        elif rmax is not None and amount > rmax:
            score = max(0.0, 1.0 - (amount - rmax) / rmax) if rmax > 0 else 0.0
        else:
            score = 1.0
        
        return CriterionScore(
            name="amount_fit",
            score=score,
            weight=rules.amount_weight,
            weighted_score=score * rules.amount_weight,
            passed=score >= 0.5,
            details={
                "amount": amount,
                "range_min": rmin,
                "range_max": rmax,
                "currency": rules.amount_range.currency,
            }
        )

    def _score_deadline(self, tender: Tender, rules: QualificationRules) -> CriterionScore:
        """
        Score basé sur le nombre de jours restants avant deadline.
        >= 2x min_preparation_days = 1.0, décroissance linéaire.
        """
        if tender.deadline_submission is None:
            return CriterionScore(
                name="deadline_sufficient",
                score=0.5, weight=rules.deadline_weight,
                weighted_score=0.5 * rules.deadline_weight,
                passed=False,
                details={"reason": "Deadline non extraite du DCE"}
            )
        
        today = date.today()
        if isinstance(tender.deadline_submission, datetime):
            deadline = tender.deadline_submission.date()
        else:
            deadline = tender.deadline_submission
        
        days_remaining = (deadline - today).days
        min_days = rules.min_preparation_days
        
        if days_remaining >= min_days * 2:
            score = 1.0
        elif days_remaining >= min_days:
            score = 0.7
        elif days_remaining > 0:
            score = max(0.0, days_remaining / min_days)
        else:
            score = 0.0
        
        return CriterionScore(
            name="deadline_sufficient",
            score=score,
            weight=rules.deadline_weight,
            weighted_score=score * rules.deadline_weight,
            passed=days_remaining >= min_days,
            details={
                "days_remaining": days_remaining,
                "min_required": min_days,
                "deadline": deadline.isoformat(),
            }
        )

    async def _score_memory(
        self, tender: Tender, rules: QualificationRules, tenant_id: str
    ) -> CriterionScore:
        """
        Score basé sur la mémoire épisodique — AO similaires passés.
        Recherche par similarité sémantique via pgvector.
        """
        search_text = f"{tender.title or ''} {tender.description or ''}"
        if not search_text.strip():
            return CriterionScore(
                name="episodic_memory",
                score=0.5, weight=rules.memory_weight,
                weighted_score=0.5 * rules.memory_weight,
                passed=False,
                details={"reason": "Pas de texte pour la recherche mémoire"}
            )
        
        # Recherche en mémoire : cas similaires (succès et échecs)
        similar = await self._memory.search_similar(
            query_text=search_text,
            tenant_id=tenant_id,
            top_k=5,
            filters={"entity_type": "tender_outcome"},
            min_similarity=rules.memory_similarity_threshold,
        )
        
        if not similar:
            return CriterionScore(
                name="episodic_memory",
                score=0.5, weight=rules.memory_weight,
                weighted_score=0.5 * rules.memory_weight,
                passed=True,
                details={"reason": "Aucun cas similaire en mémoire", "results_count": 0}
            )
        
        # Calcul du win rate pondéré par similarité
        total_sim = sum(r.similarity for r in similar)
        weighted_wins = sum(
            r.similarity for r in similar if "success" in (r.tags or [])
        )
        win_rate = weighted_wins / total_sim if total_sim > 0 else 0.5
        
        # Score final : win_rate * moyenne des similarités
        avg_similarity = total_sim / len(similar)
        score = win_rate * avg_similarity
        
        return CriterionScore(
            name="episodic_memory",
            score=round(score, 4),
            weight=rules.memory_weight,
            weighted_score=score * rules.memory_weight,
            passed=score >= 0.5,
            details={
                "results_count": len(similar),
                "win_rate": round(win_rate, 3),
                "avg_similarity": round(avg_similarity, 3),
                "similar_cases": [
                    {"id": r.id, "sim": round(r.similarity, 3), "tags": r.tags}
                    for r in similar[:3]
                ],
            }
        )

    # ------------------------------------------------------------------
    # LLM Fallback — Zone ambiguë
    # ------------------------------------------------------------------

    async def _llm_fallback(
        self,
        tender: Tender,
        rules: QualificationRules,
        criterion_scores: List[CriterionScore],
        tenant_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Appelle l'API Mistral pour scorer un tender en zone ambiguë.
        Retourne None si le circuit breaker est ouvert.
        """
        try:
            # Préparation du contexte
            context = {
                "tender": {
                    "title": tender.title,
                    "description": tender.description,
                    "cpv_code": tender.cpv_code,
                    "cpv_description": tender.cpv_description,
                    "estimated_amount": tender.estimated_amount,
                    "currency": tender.currency,
                    "deadline_submission": tender.deadline_submission.isoformat() if tender.deadline_submission else None,
                    "deadline_questions": tender.deadline_questions.isoformat() if tender.deadline_questions else None,
                    "buyer_name": tender.buyer_name,
                    "lots_count": len(tender.lots) if tender.lots else 0,
                    "award_criteria": tender.award_criteria,
                },
                "rules_summary": {
                    "cpv_target": list(rules.cpv_weights.keys()),
                    "amount_range": {
                        "min": rules.amount_range.min_amount if rules.amount_range else None,
                        "max": rules.amount_range.max_amount if rules.amount_range else None,
                    },
                    "min_preparation_days": rules.min_preparation_days,
                },
                "criterion_scores": [
                    {
                        "name": cs.name,
                        "score": round(cs.score, 3),
                        "passed": cs.passed,
                        "details": cs.details,
                    }
                    for cs in criterion_scores
                ],
                "threshold_go": rules.threshold_go,
                "threshold_no_go": rules.threshold_no_go,
            }
            
            # Rendu du template Jinja2
            prompt = QUALIFIER_PROMPT_TEMPLATE.render(context=context)
            
            # Appel API Mistral (avec circuit breaker intégré)
            response = await self._llm.complete(
                prompt=prompt,
                temperature=0.1,  # Faible température = précision
                max_tokens=1024,
                response_format={"type": "json_object"},
            )
            
            # Parsing de la réponse JSON
            result = self._llm.parse_json_response(response)
            
            # Validation du schéma
            if "score" not in result or not isinstance(result["score"], (int, float)):
                logger.warning("qualifier.llm_invalid_response",
                             tender_id=tender.id,
                             response_keys=list(result.keys()))
                return None
            
            return result
            
        except CircuitOpenError:
            logger.warning("qualifier.llm_circuit_open", tender_id=tender.id)
            return None
        except Exception as exc:
            logger.error("qualifier.llm_error", tender_id=tender.id, error=str(exc))
            return None

    # ------------------------------------------------------------------
    # Utilitaires
    # ------------------------------------------------------------------

    def _build_justification(
        self,
        scores: List[CriterionScore],
        decision: QualificationDecision,
        global_score: float,
        llm_reasoning: Optional[str],
    ) -> str:
        """Construit un texte de justification lisible."""
        parts = [f"Décision : {decision.value.upper()} (score : {global_score:.2f})"]
        parts.append("\nScores par critère :")
        for cs in scores:
            status = "✓" if cs.passed else "✗"
            parts.append(f"  {status} {cs.name}: {cs.score:.2f} (poids: {cs.weight})")
        if llm_reasoning:
            parts.append(f"\nAnalyse LLM : {llm_reasoning[:500]}")
        return "\n".join(parts)

    async def _persist_result(self, result: QualificationResult) -> None:
        """Persistance du résultat et mise à jour du tender."""
        # INSERT dans qualification_results
        await self._tender_repo.insert_qualification_result(result)
        
        # UPDATE tender
        decision_map = {
            QualificationDecision.GO: TenderStatus.QUALIFIED_GO,
            QualificationDecision.NO_GO: TenderStatus.QUALIFIED_NOGO,
            QualificationDecision.MAYBE: TenderStatus.QUALIFIED_MAYBE,
        }
        await self._tender_repo.update_status(
            result.tender_id,
            decision_map[result.decision],
            qualification_score=result.global_score,
        )
        
        # Émission événement
        await self._event_bus.publish(TenderQualifiedEvent(
            tender_id=result.tender_id,
            tenant_id=result.tenant_id,
            decision=result.decision.value,
            score=result.global_score,
        ))
```

#### Template Jinja2 — Prompt de qualification LLM

```jinja2n{### Template Jinja2 : Prompt de Qualification (LLM Fallback) ###}

{# Fichier : takaos/templates/prompts/qualifier.jinja2 #}

Tu es un expert en marchés publics français. Tu aides une entreprise à décider
si elle doit répondre (GO), ne pas répondre (NO-GO), ou étudier plus en détail
(MAYBE) à un Appel d'Offres.

Voici les informations du DCE (Document de Consultation des Entreprises) :

--- DCE ---
Titre : {{ context.tender.title or "Non spécifié" }}
Description : {{ context.tender.description or "Non spécifiée" }}
Code CPV : {{ context.tender.cpv_code or "Non extrait" }} — {{ context.tender.cpv_description or "" }}
Montant estimé : {% if context.tender.estimated_amount %}{{ "{:,.0f}".format(context.tender.estimated_amount) }} {{ context.tender.currency or "EUR" }}{% else %}Non extrait{% endif %}
Deadline soumission : {{ context.tender.deadline_submission or "Non extraite" }}
Deadline questions : {{ context.tender.deadline_questions or "Non extraite" }}
Acheteur : {{ context.tender.buyer_name or "Non identifié" }}
Nombre de lots : {{ context.tender.lots_count }}
Critères d'attribution : {{ context.tender.award_criteria | join(", ") or "Non extraits" }}
---

Voici les règles métier de l'entreprise (scores déjà calculés) :
{% for cs in context.criterion_scores %}
- {{ cs.name }} : {{ "%.2f"|format(cs.score) }} ({{ "PASS" if cs.passed else "FAIL" }})
  Détails : {{ cs.details | tojson }}
{% endfor %}

Règles de l'entreprise :
- CPV cibles : {{ context.rules_summary.cpv_target | join(", ") }}
- Fourchette de montant : [{{ context.rules_summary.amount_range.min or "N/A" }}, {{ context.rules_summary.amount_range.max or "N/A" }}]
- Jours minimum de préparation : {{ context.rules_summary.min_preparation_days }}

Instructions :
1. Analyse le DCE au regard des règles de l'entreprise
2. Identifie les facteurs clés qui pourraient influencer la décision
3. Attribue un score global entre 0.0 (fortement déconseillé) et 1.0 (fortement recommandé)
4. Explique ton raisonnement

Réponds UNIQUEMENT en JSON valide avec ce format exact :

{
  "score": 0.72,
  "justification": "Le CPV correspond parfaitement au cœur de métier. Le montant est dans la fourchette. La deadline laisse 21 jours de préparation, ce qui est suffisant. Historique favorable sur des AO similaires.",
  "key_factors": [
    "CPV match exact (03311000)",
    "Montant dans la fourchette cible",
    "Deadline confortable (21 jours)",
    "Critères d'attribution favorables (prix 60%, technique 40%)"
  ],
  "confidence": 0.88,
  "risks": ["Concurrent majeur attendu", "Délai court pour questions"]
}
```

#### Exemple de réponse JSON attendue de Mistral

```json
{
  "score": 0.72,
  "justification": "Le CPV 33111000 correspond exactement au cœur de métier de l'entreprise (matériel médical). Le montant estimé de 450 000 EUR se situe dans la fourchette cible [200K, 800K]. La deadline de soumission dans 21 jours offre une marge de préparation confortable au-delà des 14 jours minimum requis. L'historique montre un taux de succès de 75% sur des AO similaires. Les critères d'attribution (60% prix, 40% technique) sont favorables étant donné la compétitivité historique de l'entreprise.",
  "key_factors": [
    "CPV 33111000 — correspondance exacte avec le périmètre médical",
    "Montant 450K EUR dans la fourchette [200K, 800K]",
    "21 jours de préparation (seuil: 14 jours)",
    "Historique favorable : 75% de succès sur AO similaires",
    "Critères d'attribution équilibrés (prix 60%, technique 40%)"
  ],
  "confidence": 0.88,
  "risks": [
    "Concurrence attendue de grands groupes (Siemens Healthineers, GE)",
    "Deadline questions dans 5 jours — besoin de réactivité",
    "Condition de performance exigeante (disponibilité 99.9%)"
  ]
}
```

#### Schéma SQL — Table qualification_results

```sql
-- ============================================================
-- Table qualification_results — Historique des qualifications
-- ============================================================

CREATE TABLE qualification_results (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tender_id           UUID NOT NULL REFERENCES tenders(id) ON DELETE CASCADE,
    tenant_id           UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Scores
    rules_score         DECIMAL(5,4) NOT NULL,       -- Score règles (0.0000 - 1.0000)
    llm_score           DECIMAL(5,4),                -- Score LLM (NULL si pas déclenché)
    global_score        DECIMAL(5,4) NOT NULL,       -- Score global fusionné
    
    -- Décision
    decision            VARCHAR(8) NOT NULL,         -- 'go' | 'no_go' | 'maybe'
    
    -- Détail
    criterion_scores    JSONB NOT NULL DEFAULT '[]', -- Liste des CriterionScore sérialisés
    justification       TEXT,                        -- Texte explicatif
    llm_reasoning       TEXT,                        -- Raisonnement brut du LLM
    
    -- Performance
    rules_processing_ms INTEGER DEFAULT 0,
    llm_processing_ms   INTEGER DEFAULT 0,
    total_processing_ms INTEGER DEFAULT 0,
    
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    
    -- Index
    CONSTRAINT uq_qual_result_tender UNIQUE (tender_id)
);

-- Index pour les dashboards et filtres
CREATE INDEX idx_qual_results_tenant ON qualification_results(tenant_id);
CREATE INDEX idx_qual_results_decision ON qualification_results(decision);
CREATE INDEX idx_qual_results_score ON qualification_results(global_score);
```

---

### 3.1.3 Agent Tracker (`ao_tracker`)

#### Responsabilité

L'Agent Tracker surveille en continu les deadlines de tous les tenders actifs et émet des alertes programmées. Il fonctionne comme un **cron job** interne (via APScheduler) avec un endpoint de déclenchement manuel.

| Attribut | Valeur |
|----------|--------|
| **Module** | `takaos.agents.tracker` |
| **Classe principale** | `TrackerAgent` |
| **Dépendances** | `TenderRepository`, `NotificationService`, `EventBus` |
| **Trigger** | Cron toutes les heures + endpoint manuel `POST /api/v1/tracker/run` |

#### Matrice d'alertes — Deadlines

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MATRICE DES ALERTES — Agent Tracker                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  DEADLINE SOUMISSION (date limite de dépôt du dossier)                      │
│  ─────────────────────────────────────────────────────                      │
│  Jours avant deadline    │ Niveau d'alerte    │ Canaux                       │
│  ────────────────────────┼────────────────────┼──────────────────────────────│
│  30 jours                │ INFO (bleu)        │ In-app                       │
│  14 jours                │ WARNING (jaune)    │ In-app + Email               │
│  7 jours                 │ URGENT (orange)    │ In-app + Email               │
│  3 jours                 │ CRITICAL (rouge)   │ In-app + Email + Push        │
│  1 jour                  │ FINAL (rouge+)     │ In-app + Email + Push + SMS  │
│                                                                             │
│  DEADLINE QUESTIONS (date limite pour poser des questions)                  │
│  ─────────────────────────────────────────────────────────                  │
│  Jours avant deadline    │ Niveau d'alerte    │ Canaux                       │
│  ────────────────────────┼────────────────────┼──────────────────────────────│
│  7 jours                 │ INFO (bleu)        │ In-app                       │
│  3 jours                 │ WARNING (jaune)    │ In-app + Email               │
│  1 jour                  │ URGENT (orange)    │ In-app + Email               │
│                                                                             │
│  STATUT SPÉCIAUX                                                            │
│  ─────────────                                                              │
│  • Deadline questions dépassée → Alerte si questions encore en rédaction    │
│  • Deadline soumission dans <24h + statut != 'submitted' → Alerte CRITICAL  │
│  • Tender GO mais sans responsable assigné → Alerte WARNING après 48h       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Pseudo-code complet — Agent Tracker

```python
# ============================================================
# takaos/agents/tracker.py — Agent Tracker (ao_tracker)
# ============================================================

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from enum import Enum
from typing import List, Dict, Optional, Any

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from takaos.core.events import EventBus, DeadlineAlertEvent
from takaos.db.repositories import TenderRepository
from takaos.models.domain import Tender, TenderStatus
from takaos.notifications.service import NotificationService

logger = structlog.get_logger("takaos.agents.tracker")


class AlertLevel(Enum):
    """Niveaux d'alerte pour les deadlines."""
    INFO = "info"           # Bleu — In-app uniquement
    WARNING = "warning"     # Jaune — In-app + Email
    URGENT = "urgent"       # Orange — In-app + Email
    CRITICAL = "critical"   # Rouge — In-app + Email + Push
    FINAL = "final"         # Rouge+ — In-app + Email + Push + SMS


class DeadlineType(Enum):
    """Type de deadline surveillée."""
    SUBMISSION = "submission"   # Date limite de dépôt
    QUESTIONS = "questions"     # Date limite de questions


@dataclass
class AlertRule:
    """Règle d'alerte : déclenchement à N jours avant deadline."""
    deadline_type: DeadlineType
    days_before: int                # Jours avant la deadline
    level: AlertLevel               # Niveau d'alerte
    channels: List[str]             # ['in_app', 'email', 'push', 'sms']
    template_key: str               # Clé du template de notification


@dataclass
class Alert:
    """Alerte générée par le Tracker."""
    tender_id: str
    tenant_id: str
    deadline_type: DeadlineType
    deadline_date: datetime
    days_remaining: int
    level: AlertLevel
    channels: List[str]
    message: str
    actions: List[Dict[str, str]] = field(default_factory=list)
    # Ex: [{"label": "Voir le dossier", "url": "/tenders/abc"}]


# ============================================================
# RÈGLES D'ALERTE PRÉDÉFINIES (configurables par tenant)
# ============================================================

DEFAULT_ALERT_RULES: List[AlertRule] = [
    # ── Deadline Soumission ──
    AlertRule(DeadlineType.SUBMISSION, 30, AlertLevel.INFO,     ["in_app"],          "submission_30d"),
    AlertRule(DeadlineType.SUBMISSION, 14, AlertLevel.WARNING,  ["in_app", "email"], "submission_14d"),
    AlertRule(DeadlineType.SUBMISSION,  7, AlertLevel.URGENT,   ["in_app", "email"], "submission_7d"),
    AlertRule(DeadlineType.SUBMISSION,  3, AlertLevel.CRITICAL, ["in_app", "email", "push"], "submission_3d"),
    AlertRule(DeadlineType.SUBMISSION,  1, AlertLevel.FINAL,    ["in_app", "email", "push", "sms"], "submission_1d"),
    
    # ── Deadline Questions ──
    AlertRule(DeadlineType.QUESTIONS,   7, AlertLevel.INFO,     ["in_app"],          "questions_7d"),
    AlertRule(DeadlineType.QUESTIONS,   3, AlertLevel.WARNING,  ["in_app", "email"], "questions_3d"),
    AlertRule(DeadlineType.QUESTIONS,   1, AlertLevel.URGENT,   ["in_app", "email"], "questions_1d"),
]


class TrackerAgent:
    """
    Agent Tracker — Surveillance des deadlines et émission d'alertes.
    
    Architecture :
    - Cron job toutes les heures (via APScheduler)
    - Endpoint manuel pour déclenchement immédiat
    - Règles d'alerte configurables par tenant
    - Multi-canaux : in-app, email (SMTP), push, SMS
    - Dédoublonnage : une alerte par (tender, deadline, rule) par période
    """

    def __init__(
        self,
        tender_repository: TenderRepository,
        notification_service: NotificationService,
        event_bus: EventBus,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._tender_repo = tender_repository
        self._notif = notification_service
        self._event_bus = event_bus
        self._config = config or {}
        self._rules: List[AlertRule] = DEFAULT_ALERT_RULES
        self._scheduler: Optional[AsyncIOScheduler] = None

    # ------------------------------------------------------------------
    # Gestion du cycle de vie (démarrage / arrêt)
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Démarre le scheduler cron."""
        self._scheduler = AsyncIOScheduler()
        
        # Exécution toutes les heures, à la minute 0
        self._scheduler.add_job(
            self.run_check,
            trigger=CronTrigger(minute=0),  # Toutes les heures
            id="tracker_hourly",
            replace_existing=True,
            max_instances=1,  # Pas de chevauchement
        )
        
        self._scheduler.start()
        logger.info("tracker.scheduler_started", interval="hourly")

    async def stop(self) -> None:
        """Arrête proprement le scheduler."""
        if self._scheduler:
            self._scheduler.shutdown(wait=True)
            logger.info("tracker.scheduler_stopped")

    # ------------------------------------------------------------------
    # API Publique — Déclenchement manuel + Cron
    # ------------------------------------------------------------------

    async def run_check(self) -> Dict[str, Any]:
        """
        Exécute un tour complet de vérification des deadlines.
        Appelé par le cron toutes les heures OU manuellement via API.
        
        Returns :
            {"alerts_generated": N, "tenders_checked": M, "processing_ms": X}
        """
        start_time = datetime.utcnow()
        logger.info("tracker.check_started", timestamp=start_time.isoformat())

        # Récupération des tenders actifs (non soumis, non archivés)
        active_statuses = [
            TenderStatus.PARSED,
            TenderStatus.QUALIFIED_GO,
            TenderStatus.QUALIFIED_MAYBE,
            TenderStatus.IN_PREPARATION,
            TenderStatus.REVIEW_PENDING,
        ]
        
        tenders = await self._tender_repo.find_by_statuses(active_statuses)
        
        alerts_generated: List[Alert] = []
        
        for tender in tenders:
            try:
                tender_alerts = self._evaluate_tender(tender)
                
                for alert in tender_alerts:
                    # Vérification de dédoublonnage
                    if await self._should_emit_alert(alert):
                        await self._emit_alert(alert)
                        alerts_generated.append(alert)
                        
            except Exception as exc:
                logger.error("tracker.tender_evaluation_failed",
                           tender_id=tender.id, error=str(exc))
                continue

        processing_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        logger.info("tracker.check_completed",
                   tenders_checked=len(tenders),
                   alerts_generated=len(alerts_generated),
                   processing_ms=processing_ms)

        return {
            "alerts_generated": len(alerts_generated),
            "tenders_checked": len(tenders),
            "processing_ms": processing_ms,
        }

    # ------------------------------------------------------------------
    # Évaluation d'un tender
    # ------------------------------------------------------------------

    def _evaluate_tender(self, tender: Tender) -> List[Alert]:
        """
        Évalue un tender contre toutes les règles d'alerte.
        Retourne la liste des alertes à émettre.
        """
        alerts: List[Alert] = []
        today = date.today()
        
        for rule in self._rules:
            # Récupération de la date de deadline selon le type
            deadline = (
                tender.deadline_submission if rule.deadline_type == DeadlineType.SUBMISSION
                else tender.deadline_questions if rule.deadline_type == DeadlineType.QUESTIONS
                else None
            )
            
            if deadline is None:
                continue
            
            # Conversion en date si datetime
            deadline_date = deadline.date() if isinstance(deadline, datetime) else deadline
            
            # Calcul des jours restants
            days_remaining = (deadline_date - today).days
            
            # La règle s'applique-t-elle ? (on alerte dans une fenêtre de ±12h)
            if days_remaining == rule.days_before:
                # Construction du message
                message = self._build_alert_message(tender, rule, days_remaining)
                
                alert = Alert(
                    tender_id=tender.id,
                    tenant_id=tender.tenant_id,
                    deadline_type=rule.deadline_type,
                    deadline_date=deadline,
                    days_remaining=days_remaining,
                    level=rule.level,
                    channels=rule.channels,
                    message=message,
                    actions=[
                        {"label": "Voir le dossier", "url": f"/tenders/{tender.id}"},
                        {"label": "Calendrier", "url": f"/tenders/{tender.id}/timeline"},
                    ],
                )
                alerts.append(alert)
        
        # ── Alertes spéciales (hors règles standard) ──
        
        # Alert spéciale : deadline dans <24h et pas encore soumis
        if tender.deadline_submission:
            sub_deadline = (
                tender.deadline_submission.date()
                if isinstance(tender.deadline_submission, datetime)
                else tender.deadline_submission
            )
            if (sub_deadline - today).days < 1 and tender.status != TenderStatus.SUBMITTED:
                alerts.append(Alert(
                    tender_id=tender.id,
                    tenant_id=tender.tenant_id,
                    deadline_type=DeadlineType.SUBMISSION,
                    deadline_date=tender.deadline_submission,
                    days_remaining=(sub_deadline - today).days,
                    level=AlertLevel.FINAL,
                    channels=["in_app", "email", "push", "sms"],
                    message=f"⚠️ DERNIER JOUR — Le dossier '{tender.title or tender.id}' doit être soumis aujourd'hui ! Statut actuel : {tender.status.value}",
                    actions=[
                        {"label": "Finaliser la soumission", "url": f"/tenders/{tender.id}/submit"},
                    ],
                ))
        
        # Alert spéciale : tender GO mais sans responsable assigné après 48h
        if (tender.status == TenderStatus.QUALIFIED_GO 
            and tender.assigned_to is None
            and tender.qualified_at is not None):
            hours_since_qual = (datetime.utcnow() - tender.qualified_at).total_seconds() / 3600
            if hours_since_qual >= 48:
                alerts.append(Alert(
                    tender_id=tender.id,
                    tenant_id=tender.tenant_id,
                    deadline_type=DeadlineType.SUBMISSION,
                    deadline_date=tender.deadline_submission,
                    days_remaining=0,
                    level=AlertLevel.WARNING,
                    channels=["in_app", "email"],
                    message=f"⚠️ Le tender '{tender.title or tender.id}' (GO) n'a pas encore de responsable assigné après 48h.",
                    actions=[
                        {"label": "Assigner", "url": f"/tenders/{tender.id}/assign"},
                    ],
                ))
        
        return alerts

    # ------------------------------------------------------------------
    # Émission et dédoublonnage
    # ------------------------------------------------------------------

    async def _should_emit_alert(self, alert: Alert) -> bool:
        """
        Vérifie si l'alerte n'a pas déjà été émise récemment.
        Dédoublonnage par (tender_id, deadline_type, days_before, date).
        """
        # Clé de dédoublonnage : tender + type + jours restants + date
        dedup_key = (
            f"alert:{alert.tender_id}:"
            f"{alert.deadline_type.value}:"
            f"{alert.days_remaining}:"
            f"{date.today().isoformat()}"
        )
        
        # Vérification via Redis/cache (SETNX = set if not exists)
        was_new = await self._notif.check_and_set_dedup(dedup_key, ttl=86400)
        return was_new

    async def _emit_alert(self, alert: Alert) -> None:
        """Émet l'alerte sur tous les canaux configurés."""
        logger.info("tracker.alert_emitting",
                   tender_id=alert.tender_id,
                   level=alert.level.value,
                   channels=alert.channels,
                   days_remaining=alert.days_remaining)
        
        # 1. Notification in-app (event bus → WebSocket)
        if "in_app" in alert.channels:
            await self._event_bus.publish(DeadlineAlertEvent(
                tender_id=alert.tender_id,
                tenant_id=alert.tenant_id,
                level=alert.level.value,
                message=alert.message,
                deadline_type=alert.deadline_type.value,
                days_remaining=alert.days_remaining,
                actions=alert.actions,
            ))
        
        # 2. Email (SMTP async)
        if "email" in alert.channels:
            await self._notif.send_email(
                tenant_id=alert.tenant_id,
                template_key=f"tracker_{alert.level.value}",
                context={
                    "tender_title": alert.message,
                    "days_remaining": alert.days_remaining,
                    "deadline_date": alert.deadline_date.isoformat() if alert.deadline_date else None,
                    "actions": alert.actions,
                },
            )
        
        # 3. Push notification
        if "push" in alert.channels:
            await self._notif.send_push(
                tenant_id=alert.tenant_id,
                title=f"Deadline — {alert.level.value.upper()}",
                body=alert.message,
                data={"tender_id": alert.tender_id, "screen": "/tenders/alert.tender_id"},
            )
        
        # 4. SMS (canal réservé aux alertes FINAL)
        if "sms" in alert.channels:
            await self._notif.send_sms(
                tenant_id=alert.tenant_id,
                message=f"[TAKA] {alert.message[:140]}",  # Troncature SMS
            )

    # ------------------------------------------------------------------
    # Utilitaires
    # ------------------------------------------------------------------

    def _build_alert_message(
        self, tender: Tender, rule: AlertRule, days_remaining: int
    ) -> str:
        """Construit le message d'alerte localisé."""
        deadline_labels = {
            DeadlineType.SUBMISSION: "soumission",
            DeadlineType.QUESTIONS: "questions",
        }
        
        if days_remaining == 0:
            return (f"🔴 DERNIER JOUR pour la deadline de {deadline_labels[rule.deadline_type]} "
                   f"du dossier '{tender.title or tender.id}'")
        elif days_remaining == 1:
            return (f"🟠 {days_remaining} jour restant avant la deadline de {deadline_labels[rule.deadline_type]} "
                   f"du dossier '{tender.title or tender.id}'")
        else:
            return (f"{days_remaining} jours restants avant la deadline de {deadline_labels[rule.deadline_type]} "
                   f"du dossier '{tender.title or tender.id}'")
```

#### Configuration APScheduler

```python
# ============================================================
# takaos/agents/tracker_scheduler.py — Configuration Scheduler
# ============================================================

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

# Job store PostgreSQL pour persistance des jobs (clustering, reprise)
jobstores = {
    "default": SQLAlchemyJobStore(
        url="postgresql://user:pass@localhost/takaos",
        tablename="apscheduler_jobs",
    )
}

# Executor async pour les tâches I/O (DB, API, SMTP)
executors = {
    "default": AsyncIOExecutor(max_workers=10),
}

# Politique de coalescence : si le scheduler était arrêté,
# ne pas exécuter les jobs manqués en rafale
job_defaults = {
    "coalesce": True,           # Fusionner les exécutions manquées
    "max_instances": 1,         # Pas de chevauchement
    "misfire_grace_time": 3600, # Tolérance 1h de décalage
}

scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone="Europe/Paris",  # Fuseau horaire France/Belgique
)
```

---

## 3.2 Système de Mémoire (pgvector)

### 3.2.1 Génération d'embeddings

#### Architecture du pipeline d'embedding

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              PIPELINE DE GÉNÉRATION D'EMBEDDINGS                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   TEXT BRUT          NORMALISATION           EMBEDDING           STOCKAGE   │
│  ┌─────────┐       ┌──────────────┐       ┌────────────┐      ┌──────────┐ │
│  │ Titre   │       │ Minuscules   │       │ Mistral    │      │ pgvector │ │
│  │ Desc.   │  ──▶  │ Sans accents │  ──▶  │ API        │ ──▶  │ HNSW     │ │
│  │ Critères│       │ Sans stopwords│      │ 768 dims   │      │ index    │ │
│  │ Lots    │       │ Troncature   │       │            │      │          │ │
│  └─────────┘       │ 8000 tokens  │       │ OU local   │      └──────────┘ │
│                    └──────────────┘       │ all-MiniLM │                   │
│                                           └────────────┘                   │
│                                                                             │
│  SEUIL DE PASSAGE AU MODÈLE LOCAL :                                         │
│  • > 10 000 embeddings/jour  ET  latence API > 200ms p95                   │
│  • OU coût API > 500€/mois                                                  │
│  • ALORS : déploiement all-MiniLM-L6-v2 sur GPU local (T4 / A10G)           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Pipeline de normalisation

```python
# ============================================================
# takaos/memory/embeddings.py — Pipeline d'embeddings
# ============================================================

import re
import unicodedata
from typing import List, Optional

import httpx
import structlog
import torch
from transformers import AutoTokenizer, AutoModel

logger = structlog.get_logger("takaos.memory.embeddings")


class EmbeddingPipeline:
    """
    Pipeline de génération d'embeddings pour le système de mémoire.
    
    Deux modes de fonctionnement :
    1. API Mistral (mode cloud, par défaut) — 768 dimensions
    2. Modèle local all-MiniLM-L6-v2 (mode on-prem, fallback) — 384 dimensions
    
    Le passage au modèle local est conditionnel (volume + coût + latence).
    """

    # Configuration
    MISTRAL_EMBED_DIM = 768
    LOCAL_EMBED_DIM = 384
    MAX_TOKENS = 8000          # Limite de tokens pour Mistral
    LOCAL_MAX_TOKENS = 512     # Limite pour all-MiniLM-L6-v2
    
    # Stopwords français pour nettoyage léger
    STOPWORDS = {
        "le", "la", "les", "un", "une", "des", "du", "de", "et", "en",
        "à", "au", "aux", "par", "pour", "dans", "sur", "ce", "cet",
        "ces", "son", "sa", "ses", "qui", "que", "quoi", "dont", "où",
        "est", "sont", "être", "avoir", "faire", "plus", "moins", "très",
        "tout", "tous", "toute", "toutes", "avec", "sans", "mais", "ou",
        "si", "car", "donc", "ni", "ne", "pas", "aussi",
    }

    def __init__(
        self,
        mistral_api_key: str,
        mistral_endpoint: str = "https://api.mistral.ai/v1/embeddings",
        use_local: bool = False,
        local_model_path: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> None:
        self._api_key = mistral_api_key
        self._endpoint = mistral_endpoint
        self._use_local = use_local
        
        # Chargement conditionnel du modèle local
        self._local_tokenizer: Optional[Any] = None
        self._local_model: Optional[Any] = None
        
        if use_local:
            logger.info("embeddings.loading_local_model", model=local_model_path)
            self._local_tokenizer = AutoTokenizer.from_pretrained(local_model_path)
            self._local_model = AutoModel.from_pretrained(local_model_path)
            self._local_model.eval()
            logger.info("embeddings.local_model_loaded")

    # ------------------------------------------------------------------
    # API Publique
    # ------------------------------------------------------------------

    async def embed(self, text: str) -> List[float]:
        """
        Génère un vecteur d'embedding pour un texte.
        Route vers API ou modèle local selon la configuration.
        """
        normalized = self._normalize(text)
        
        if self._use_local:
            return await self._embed_local(normalized)
        return await self._embed_api(normalized)

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Génère des embeddings en batch (optimisé).
        """
        normalized = [self._normalize(t) for t in texts]
        
        if self._use_local:
            return await self._embed_batch_local(normalized)
        return await self._embed_batch_api(normalized)

    # ------------------------------------------------------------------
    # Normalisation
    # ------------------------------------------------------------------

    def _normalize(self, text: str) -> str:
        """
        Normalisation du texte avant embedding.
        Chaîne : unicode → minuscules → accents → stopwords → espace.
        """
        if not text:
            return ""
        
        # 1. Normalisation Unicode (NFKC)
        text = unicodedata.normalize("NFKC", text)
        
        # 2. Minuscules
        text = text.lower()
        
        # 3. Suppression des accents (optionnel — conservé car utile pour le français)
        # text = "".join(c for c in unicodedata.normalize("NFD", text)
        #                if unicodedata.category(c) != "Mn")
        
        # 4. Suppression des URLs
        text = re.sub(r"https?://\S+", "", text)
        
        # 5. Suppression des caractères spéciaux (conservation alpha-num + ponctuation)
        text = re.sub(r"[^\w\s.,;:!?-]", " ", text)
        
        # 6. Suppression légère des stopwords (pour réduire le bruit)
        words = text.split()
        words = [w for w in words if w not in self.STOPWORDS and len(w) > 1]
        text = " ".join(words)
        
        # 7. Compression des espaces multiples
        text = re.sub(r"\s+", " ", text).strip()
        
        return text

    # ------------------------------------------------------------------
    # Embedding via API Mistral
    # ------------------------------------------------------------------

    async def _embed_api(self, text: str) -> List[float]:
        """Appel API Mistral pour un embedding."""
        # Troncature au niveau token (estimation ~4 chars/token)
        max_chars = self.MAX_TOKENS * 4
        if len(text) > max_chars:
            text = text[:max_chars]
            logger.debug("embeddings.text_truncated", original_len=len(text) + max_chars)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self._endpoint,
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "model": "mistral-embed",
                    "input": text,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]

    async def _embed_batch_api(self, texts: List[str]) -> List[List[float]]:
        """Appel API Mistral en batch (jusqu'à 96 texts par appel)."""
        BATCH_SIZE = 96  # Limite Mistral
        all_embeddings: List[List[float]] = []
        
        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i:i + BATCH_SIZE]
            # Troncature
            batch = [t[:self.MAX_TOKENS * 4] for t in batch]
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self._endpoint,
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json={
                        "model": "mistral-embed",
                        "input": batch,
                    },
                )
                response.raise_for_status()
                data = response.json()
                all_embeddings.extend([d["embedding"] for d in data["data"]])
        
        return all_embeddings

    # ------------------------------------------------------------------
    # Embedding via modèle local (all-MiniLM-L6-v2)
    # ------------------------------------------------------------------

    async def _embed_local(self, text: str) -> List[float]:
        """Embedding via modèle local (CPU/GPU)."""
        import asyncio
        # Exécution CPU-intensive dans un thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._embed_local_sync, text)

    def _embed_local_sync(self, text: str) -> List[float]:
        """Version synchrone pour thread pool."""
        # Tokenization
        inputs = self._local_tokenizer(
            text[:self.LOCAL_MAX_TOKENS * 4],
            return_tensors="pt",
            truncation=True,
            max_length=self.LOCAL_MAX_TOKENS,
            padding=True,
        )
        
        # Inference
        with torch.no_grad():
            outputs = self._local_model(**inputs)
        
        # Mean pooling
        embeddings = self._mean_pooling(outputs, inputs["attention_mask"])
        
        # Normalisation L2
        embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
        
        return embeddings[0].tolist()

    def _mean_pooling(self, model_output, attention_mask):
        """Mean pooling des token embeddings pondéré par attention mask."""
        token_embeddings = model_output.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
            input_mask_expanded.sum(1), min=1e-9
        )
```

### 3.2.2 Stockage pgvector

#### Table `memory_vectors`

```sql
-- ============================================================
-- Table memory_vectors — Stockage vectoriel avec pgvector
-- ============================================================

CREATE TABLE memory_vectors (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Référence à l'entité source
    entity_type     VARCHAR(32) NOT NULL,  -- 'tender_outcome' | 'procedural' | 'episodic'
    entity_id       UUID,                  -- ID de l'entité source (tender, etc.)
    
    -- Contenu sémantique
    content         TEXT NOT NULL,          -- Texte original (pour affichage + recherche full-text)
    embedding       vector(768) NOT NULL,   -- Vecteur d'embedding (768 dims = Mistral)
    
    -- Métadonnées structurées
    tags            TEXT[] DEFAULT '{}',    -- Tags pour filtrage : ['success', 'cpv_33111000', 'amount_high']
    metadata        JSONB DEFAULT '{}',     -- Métadonnées libres
    
    -- Traçabilité
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    created_by      UUID REFERENCES users(id),
    
    -- Poids pour le scoring (optionnel, default 1.0)
    weight          FLOAT DEFAULT 1.0
);

-- Commentaires
COMMENT ON TABLE memory_vectors IS 'Stockage vectoriel de la mémoire TAKA (épisodique + procédurale)';
COMMENT ON COLUMN memory_vectors.entity_type IS 'tender_outcome: résultat AO, procedural: règle/process, episodic: événement';

-- ============================================================
-- Index HNSW — Recherche par similarité approximée
-- ============================================================

-- Index HNSW pour cosine similarity (recommandé pour pgvector)
-- m=16 : nombre de connexions par élément (équilibre précision/vitesse)
-- ef_construction=64 : facteur de recherche lors de la construction
CREATE INDEX idx_memory_vectors_hnsw
    ON memory_vectors
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Index pour filtrage par tenant (pré-filtre avant recherche vectorielle)
CREATE INDEX idx_memory_vectors_tenant ON memory_vectors(tenant_id);

-- Index pour filtrage par tags (GIN pour array)
CREATE INDEX idx_memory_vectors_tags ON memory_vectors USING GIN (tags);

-- Index pour filtrage par entity_type
CREATE INDEX idx_memory_vectors_entity ON memory_vectors(entity_type, entity_id);

-- Index full-text pour recherche hybride (vectoriel + texte)
CREATE INDEX idx_memory_vectors_fts ON memory_vectors
    USING GIN (to_tsvector('french', content));

-- ============================================================
-- Paramètres de performance HNSW
-- ============================================================

-- ef_search : contrôle la précision vs vitesse lors de la recherche
-- Valeur par défaut : 40. Augmenter pour plus de précision.
SET hnsw.ef_search = 64;  -- ~10% meilleure recall, ~20% plus lent
```

#### Paramètres d'indexation HNSW optimisés

| Paramètre | Valeur | Justification |
|-----------|--------|---------------|
| `m` | 16 | Bon équilibre pour 10K-1M vecteurs. Augmenter à 32 au-delà de 1M. |
| `ef_construction` | 64 | Qualité de construction acceptable. 128 pour meilleure recall. |
| `ef_search` | 64 (session) | Compromis précision/vitesse. 128 si recall insuffisant. |
| `vector dimension` | 768 | Embedding Mistral (mode cloud). 384 si modèle local. |
| `lists` (IVFFlat alt.) | 100 | Alternative à HNSW si build time critique. |

> **Performance attendue** : < 20ms pour requête top_k=5 sur 10K vecteurs avec pré-filtre tenant_id sur PostgreSQL 15 + pgvector 0.5+ sur instance db.r6g.xlarge équivalent.

### 3.2.3 Recherche de similarité

#### Pseudo-code complet — Recherche de similarité

```python
# ============================================================
# takaos/memory/vector_store.py — Système de Mémoire Vectorielle
# ============================================================

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any

import asyncpg
import structlog

from takaos.memory.embeddings import EmbeddingPipeline

logger = structlog.get_logger("takaos.memory.vector_store")


@dataclass
class MemorySearchResult:
    """Résultat d'une recherche en mémoire."""
    id: str
    content: str
    similarity: float                    # Cosine similarity (0.0 - 1.0)
    entity_type: str
    entity_id: Optional[str]
    tags: List[str]
    metadata: Dict[str, Any]
    created_at: datetime


class MemorySystem:
    """
    Système de Mémoire Vectorielle — Cœur du RAG de TAKA OS.
    
    Responsabilités :
    1. Stockage d'embeddings en mémoire (pgvector)
    2. Recherche par similarité sémantique avec filtrage
    3. Capitalisation des succès/échecs (mémoire épisodique)
    4. Recherche hybride : vectoriel + full-text
    
    Architecture :
    - Isolation stricte par tenant_id sur toutes les opérations
    - Index HNSW pour recherche rapide (<20ms @ 10K vecteurs)
    - Requêtes paramétrées (prévention injection SQL)
    """

    def __init__(
        self,
        pool: asyncpg.Pool,
        embedding_pipeline: EmbeddingPipeline,
    ) -> None:
        self._pool = pool
        self._embedder = embedding_pipeline

    # ------------------------------------------------------------------
    # Stockage
    # ------------------------------------------------------------------

    async def store(
        self,
        content: str,
        tenant_id: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        weight: float = 1.0,
    ) -> str:
        """
        Stocke un nouveau vecteur en mémoire.
        
        Returns :
            UUID du vecteur stocké.
        """
        # Génération de l'embedding
        embedding = await self._embedder.embed(content)
        
        # Sérialisation en format pgvector : [x,y,z,...]
        embedding_str = f"[{','.join(str(v) for v in embedding)}]"
        
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO memory_vectors
                    (tenant_id, entity_type, entity_id, content, embedding,
                     tags, metadata, weight)
                VALUES ($1, $2, $3, $4, $5::vector, $6, $7, $8)
                RETURNING id
                """,
                tenant_id,
                entity_type,
                entity_id,
                content,
                embedding_str,
                tags or [],
                metadata or {},
                weight,
            )
            
            logger.debug("memory.stored",
                        vector_id=str(row["id"]),
                        tenant_id=tenant_id,
                        entity_type=entity_type)
            
            return str(row["id"])

    async def store_batch(
        self,
        items: List[Dict[str, Any]],
        tenant_id: str,
    ) -> List[str]:
        """
        Stockage batch optimisé (pour import initial ou capitalisation).
        
        items : [{"content": str, "entity_type": str, "entity_id": str, ...}]
        """
        # Génération batch des embeddings
        texts = [item["content"] for item in items]
        embeddings = await self._embedder.embed_batch(texts)
        
        inserted_ids: List[str] = []
        
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                for item, embedding in zip(items, embeddings):
                    embedding_str = f"[{','.join(str(v) for v in embedding)}]"
                    
                    row = await conn.fetchrow(
                        """
                        INSERT INTO memory_vectors
                            (tenant_id, entity_type, entity_id, content, embedding,
                             tags, metadata, weight)
                        VALUES ($1, $2, $3, $4, $5::vector, $6, $7, $8)
                        RETURNING id
                        """,
                        tenant_id,
                        item["entity_type"],
                        item.get("entity_id"),
                        item["content"],
                        embedding_str,
                        item.get("tags", []),
                        item.get("metadata", {}),
                        item.get("weight", 1.0),
                    )
                    inserted_ids.append(str(row["id"]))
        
        logger.info("memory.batch_stored",
                   count=len(inserted_ids), tenant_id=tenant_id)
        return inserted_ids

    # ------------------------------------------------------------------
    # Recherche par similarité
    # ------------------------------------------------------------------

    async def search_similar(
        self,
        query_text: str,
        tenant_id: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        min_similarity: float = 0.0,
        entity_types: Optional[List[str]] = None,
    ) -> List[MemorySearchResult]:
        """
        Recherche sémantique par similarité cosine.
        
        Args :
            query_text : Texte de recherche (sera embeddé)
            tenant_id : Isolation obligatoire
            top_k : Nombre de résultats
            filters : Filtres optionnels {"tags": [...], "metadata": {...}}
            min_similarity : Seuil minimum de similarité
            entity_types : Filtrer par types d'entité
        
        Returns :
            Liste des résultats triés par similarité décroissante.
            
        Performance : < 20ms pour top_k=5 sur 10K vecteurs.
        """
        # Génération de l'embedding de requête
        query_embedding = await self._embedder.embed(query_text)
        query_embedding_str = f"[{','.join(str(v) for v in query_embedding)}]"
        
        # Construction dynamique des filtres SQL
        where_clauses = ["tenant_id = $2"]
        params: List[Any] = [query_embedding_str, tenant_id]
        param_idx = 3
        
        # Filtre par entity_type
        if entity_types:
            where_clauses.append(f"entity_type = ANY(${param_idx})")
            params.append(entity_types)
            param_idx += 1
        
        # Filtre par tags (INTERSECT)
        if filters and filters.get("tags"):
            where_clauses.append(f"tags && ${param_idx}")  # Intersection d'arrays
            params.append(filters["tags"])
            param_idx += 1
        
        # Filtre par metadata (JSONB containment)
        if filters and filters.get("metadata"):
            where_clauses.append(f"metadata @> ${param_idx}::jsonb")
            params.append(filters["metadata"])
            param_idx += 1
        
        where_sql = " AND ".join(where_clauses)
        
        # Requête principale avec HNSW + filtre
        sql = f"""
            SELECT
                id,
                content,
                1 - (embedding <=> ${1}::vector) AS similarity,
                entity_type,
                entity_id,
                tags,
                metadata,
                created_at
            FROM memory_vectors
            WHERE {where_sql}
              AND 1 - (embedding <=> ${1}::vector) >= ${param_idx}
            ORDER BY embedding <=> ${1}::vector
            LIMIT ${param_idx + 1}
        """
        params.append(min_similarity)
        params.append(top_k)
        
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
        
        results = [
            MemorySearchResult(
                id=str(row["id"]),
                content=row["content"],
                similarity=round(row["similarity"], 6),
                entity_type=row["entity_type"],
                entity_id=str(row["entity_id"]) if row["entity_id"] else None,
                tags=row["tags"] or [],
                metadata=row["metadata"] or {},
                created_at=row["created_at"],
            )
            for row in rows
        ]
        
        logger.debug("memory.search_completed",
                    query_len=len(query_text),
                    results_found=len(results),
                    top_similarity=round(results[0].similarity, 3) if results else None)
        
        return results

    # ------------------------------------------------------------------
    # Recherche hybride (vectoriel + full-text)
    # ------------------------------------------------------------------

    async def search_hybrid(
        self,
        query_text: str,
        tenant_id: str,
        top_k: int = 5,
        vector_weight: float = 0.7,
        text_weight: float = 0.3,
    ) -> List[MemorySearchResult]:
        """
        Recherche hybride : combine similarité vectorielle et score full-text.
        
        Formule : score_final = vector_weight * sim_cosine + text_weight * ts_rank
        
        Usage : quand la recherche sémantique pure manque des mots-clés exacts.
        """
        query_embedding = await self._embedder.embed(query_text)
        query_embedding_str = f"[{','.join(str(v) for v in query_embedding)}]"
        
        # Requête CTE hybride avec reranking
        sql = """
            WITH vector_scores AS (
                SELECT
                    id,
                    1 - (embedding <=> $1::vector) AS vscore
                FROM memory_vectors
                WHERE tenant_id = $2
                ORDER BY embedding <=> $1::vector
                LIMIT $3 * 3  -- Candidat pool plus large
            ),
            text_scores AS (
                SELECT
                    id,
                    ts_rank_cd(
                        to_tsvector('french', content),
                        plainto_tsquery('french', $4)
                    ) AS tscore
                FROM memory_vectors
                WHERE tenant_id = $2
                  AND to_tsvector('french', content) @@ plainto_tsquery('french', $4)
            ),
            combined AS (
                SELECT
                    COALESCE(v.id, t.id) AS id,
                    COALESCE(v.vscore, 0) * $5 AS vector_score,
                    COALESCE(t.tscore, 0) * $6 AS text_score
                FROM vector_scores v
                FULL OUTER JOIN text_scores t ON v.id = t.id
            )
            SELECT
                mv.id,
                mv.content,
                (c.vector_score + c.text_score) AS similarity,
                mv.entity_type,
                mv.entity_id,
                mv.tags,
                mv.metadata,
                mv.created_at
            FROM combined c
            JOIN memory_vectors mv ON c.id = mv.id
            ORDER BY (c.vector_score + c.text_score) DESC
            LIMIT $3
        """
        
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                sql,
                query_embedding_str,
                tenant_id,
                top_k,
                query_text,
                vector_weight,
                text_weight,
            )
        
        return [
            MemorySearchResult(
                id=str(row["id"]),
                content=row["content"],
                similarity=round(row["similarity"], 6),
                entity_type=row["entity_type"],
                entity_id=str(row["entity_id"]) if row["entity_id"] else None,
                tags=row["tags"] or [],
                metadata=row["metadata"] or {},
                created_at=row["created_at"],
            )
            for row in rows
        ]

    # ------------------------------------------------------------------
    # Suppression et maintenance
    # ------------------------------------------------------------------

    async def delete_by_entity(
        self, entity_type: str, entity_id: str, tenant_id: str
    ) -> int:
        """Supprime tous les vecteurs liés à une entité."""
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                """
                DELETE FROM memory_vectors
                WHERE entity_type = $1 AND entity_id = $2 AND tenant_id = $3
                """,
                entity_type, entity_id, tenant_id,
            )
            deleted = int(result.split()[-1]) if result else 0
            logger.info("memory.deleted_by_entity",
                       entity_type=entity_type, entity_id=entity_id,
                       deleted=deleted)
            return deleted

    async def vacuum(self, tenant_id: str, max_age_days: int = 365) -> int:
        """Nettoyage des vecteurs obsolètes (> max_age_days)."""
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                """
                DELETE FROM memory_vectors
                WHERE tenant_id = $1
                  AND created_at < NOW() - INTERVAL '$2 days'
                """,
                tenant_id, max_age_days,
            )
            deleted = int(result.split()[-1]) if result else 0
            logger.info("memory.vacuumed", tenant_id=tenant_id,
                       max_age_days=max_age_days, deleted=deleted)
            return deleted
```

### 3.2.4 Capitalisation des échecs/succès

#### Flux de capitalisation épisodique

```python
# ============================================================
# takaos/memory/episodic.py — Capitalisation épisodique
# ============================================================

from datetime import datetime
from typing import Dict, Any, Optional

import structlog

from takaos.memory.vector_store import MemorySystem
from takaos.models.domain import Tender, TenderStatus

logger = structlog.get_logger("takaos.memory.episodic")


class EpisodicMemoryCapitalizer:
    """
    Capitalise les résultats des tenders (succès/échecs) en mémoire épisodique.
    
    Déclenchement : transition de statut d'un tender vers 'won' ou 'lost'.
    
    Pour chaque tender finalisé :
    1. Construit un résumé structuré (texte riche sémantiquement)
    2. Tagge avec le résultat, CPV, montant, raison
    3. Stocke dans memory_vectors via le MemorySystem
    4. Ce vecteur sera retrouvé lors des futures qualifications
    """

    def __init__(self, memory_system: MemorySystem) -> None:
        self._memory = memory_system

    async def capitalize_tender_outcome(
        self,
        tender: Tender,
        outcome: str,           # 'won' | 'lost'
        reason: Optional[str] = None,
        score_attributed: Optional[float] = None,
        winning_bidder: Optional[str] = None,
    ) -> str:
        """
        Capitalise le résultat d'un tender en mémoire épisodique.
        
        Returns :
            UUID du vecteur stocké.
        """
        # --- Construction du contenu sémantique ---
        content = self._build_memory_content(
            tender=tender,
            outcome=outcome,
            reason=reason,
            score_attributed=score_attributed,
            winning_bidder=winning_bidder,
        )
        
        # --- Construction des tags ---
        tags = self._build_tags(tender, outcome, reason)
        
        # --- Métadonnées structurées ---
        metadata = {
            "tender_id": tender.id,
            "tender_reference": tender.source_reference,
            "outcome": outcome,
            "cpv_code": tender.cpv_code,
            "cpv_description": tender.cpv_description,
            "estimated_amount": tender.estimated_amount,
            "currency": tender.currency,
            "buyer_name": tender.buyer_name,
            "deadline_submission": tender.deadline_submission.isoformat() if tender.deadline_submission else None,
            "score_attributed": score_attributed,
            "winning_bidder": winning_bidder,
            "capitalized_at": datetime.utcnow().isoformat(),
        }
        
        # --- Stockage en mémoire ---
        vector_id = await self._memory.store(
            content=content,
            tenant_id=tender.tenant_id,
            entity_type="tender_outcome",
            entity_id=tender.id,
            tags=tags,
            metadata=metadata,
            weight=1.5 if outcome == "won" else 1.0,  # Les succès ont plus de poids
        )
        
        logger.info("episodic.capitalized",
                   tender_id=tender.id,
                   outcome=outcome,
                   vector_id=vector_id,
                   tags=tags)
        
        return vector_id

    def _build_memory_content(
        self,
        tender: Tender,
        outcome: str,
        reason: Optional[str],
        score_attributed: Optional[float],
        winning_bidder: Optional[str],
    ) -> str:
        """
        Construit un texte riche sémantiquement pour l'embedding.
        Le texte doit contenir les concepts clés pour la recherche future.
        """
        parts = [
            f"Appel d'offres : {tender.title or 'Sans titre'}",
            f"Description : {tender.description or 'Non disponible'}",
            f"Résultat : {'CONTRAT REMPORTÉ' if outcome == 'won' else 'CONTRAT NON OBTENU'}",
        ]
        
        if tender.cpv_code:
            parts.append(f"Code CPV : {tender.cpv_code} — {tender.cpv_description or ''}")
        
        if tender.buyer_name:
            parts.append(f"Acheteur public : {tender.buyer_name}")
        
        if tender.estimated_amount:
            parts.append(f"Montant : {tender.estimated_amount:,.0f} {tender.currency or 'EUR'}")
        
        if score_attributed:
            parts.append(f"Score attribué : {score_attributed}/100")
        
        if winning_bidder:
            parts.append(f"Attributaire : {winning_bidder}")
        
        if reason:
            parts.append(f"Raison : {reason}")
        
        # Ajout de contexte sémantique pour enrichir la recherche
        if outcome == "won":
            parts.append("Facteurs de succès : offre compétitive, expérience reconnue, réponse technique de qualité.")
        else:
            parts.append("Facteurs d'échec : concurrence forte, prix non compétitif, critères techniques non atteints.")
        
        return "\n".join(parts)

    def _build_tags(
        self, tender: Tender, outcome: str, reason: Optional[str]
    ) -> list:
        """Construit les tags pour filtrage et recherche."""
        tags = [outcome]  # 'success' ou 'failure'
        
        if tender.cpv_code:
            # Tag CPV niveau 2 (famille) : les 2 premiers chiffres
            cpv_family = tender.cpv_code[:2] if len(tender.cpv_code) >= 2 else tender.cpv_code
            tags.append(f"cpv_{tender.cpv_code}")
            tags.append(f"cpv_family_{cpv_family}")
        
        if tender.estimated_amount:
            # Tag de fourchette de montant
            if tender.estimated_amount < 100000:
                tags.append("amount_small")
            elif tender.estimated_amount < 500000:
                tags.append("amount_medium")
            elif tender.estimated_amount < 1000000:
                tags.append("amount_large")
            else:
                tags.append("amount_xlarge")
        
        if reason:
            # Tag de raison d'échec/succès
            tags.append(f"reason_{reason.lower().replace(' ', '_')[:50]}")
        
        return tags
```

#### Déclenchement via event handler

```python
# ============================================================
# Event handler : capitalisation automatique sur changement de statut
# ============================================================

async def on_tender_status_changed(event: TenderStatusChangedEvent) -> None:
    """
    Handler déclenché à chaque changement de statut d'un tender.
    Capitalise automatiquement en mémoire épisodique si le tender
    passe à 'won' ou 'lost'.
    """
    if event.new_status not in (TenderStatus.WON.value, TenderStatus.LOST.value):
        return
    
    # Récupération du tender complet
    tender = await tender_repository.get(event.tender_id)
    
    # Capitalisation
    capitalizer = EpisodicMemoryCapitalizer(memory_system)
    
    outcome = "won" if event.new_status == TenderStatus.WON.value else "lost"
    
    await capitalizer.capitalize_tender_outcome(
        tender=tender,
        outcome=outcome,
        reason=event.reason,  # Raison fournie lors du changement de statut
        score_attributed=event.score_attributed,
        winning_bidder=event.winning_bidder,
    )
```

---

## 3.3 Pipeline de Parsing PDF

### 3.3.1 Architecture stratifiée

```
┌─────────────────────────────────────────────────────────────────────────────┐
│           PIPELINE DE PARSING PDF — Architecture en 4 Niveaux              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Niveau 1 : pypdf — Extraction texte rapide (60% des cas)                 │
│   ═══════════════════════════════════════════════════════                   │
│   • Extraction naïve du texte brut des PDF natifs                          │
│   • Avantage : rapide (<2s), pas de dépendances lourdes                    │
│   • Limite : pas de structure, pas de tableaux, échoue sur PDF scannés     │
│   • Critère de succès : >30% du texte extrait ET champs prioritaires trouvés│
│                                                                             │
│       ┌─────────┐     ┌──────────────┐     ┌─────────────────────┐        │
│       │ pypdf   │───▶│ Texte brut   │───▶│ Regex extraction    │        │
│       │ Reader  │     │ (str)        │     │ CPV / Montant / Date │        │
│       └─────────┘     └──────────────┘     └─────────────────────┘        │
│                                                                             │
│   Niveau 2 : pdfplumber — Extraction structurée (25% des cas)              │
│   ════════════════════════════════════════════════════════════              │
│   • Extraction de tableaux et texte positionnel                            │
│   • Avantage : tableaux (lots, critères), mise en page préservée           │
│   • Limite : échoue sur PDF complexes ou scannés                           │
│   • Critère de succès : champs manquants au N1 complétés                   │
│                                                                             │
│       ┌─────────────┐ ┌──────────────┐ ┌─────────────────────────────┐    │
│       │ pdfplumber  │▶│ Pages +      │▶│ Table extraction            │    │
│       │ .open()     │ │ BoundingBox  │ │ + Structured text           │    │
│       └─────────────┘ └──────────────┘ └─────────────────────────────┘    │
│                                                                             │
│   Niveau 3 : OCR Tesseract — PDF scannés (10% des cas)                     │
│   ═════════════════════════════════════════════════════                     │
│   • Conversion image → texte via OCR                                       │
│   • Pré-processing : deskew, binarisation, découpage en blocs              │
│   • Langue : fra+eng (français + anglais)                                  │
│   • Critère de succès : taux de confiance OCR moyen > 60%                  │
│                                                                             │
│       ┌─────────────┐ ┌──────────────┐ ┌─────────────────────────────┐    │
│       │ pdf2image   │▶│ PIL Image    │▶│ pytesseract.image_to_string │    │
│       │ .convert()  │ │ preprocessing│ │ + confidence scoring        │    │
│       └─────────────┘ └──────────────┘ └─────────────────────────────┘    │
│                                                                             │
│   Niveau 4 : LLM Mistral — Extraction champs manquants (5% des cas)        │
│   ═════════════════════════════════════════════════════════════════         │
│   • Fallback final : le LLM lit le texte brut et extrait les champs        │
│   • Avantage : robustesse, compréhension contextuelle                      │
│   • Limite : coût API, latence (~5-10s), dépend du circuit breaker         │
│   • Usage : champs manquants après les 3 niveaux précédents                │
│                                                                             │
│       ┌─────────────┐ ┌──────────────────┐ ┌─────────────────────────┐    │
│       │ Texte brut  │▶│ Prompt Jinja2    │▶│ Mistral API             │    │
│       │ (accumulé)  │ │ + Instructions   │ │ JSON structuré          │    │
│       └─────────────┘ └──────────────────┘ └─────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3.2 Champs à extraire (par priorité)

```python
# ============================================================
# takaos/parsing/extraction_targets.py — Cibles d'extraction
# ============================================================

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from enum import Enum


class Priority(Enum):
    """Priorité d'extraction d'un champ."""
    P1 = "P1"  # Critique — bloquant pour la qualification
    P2 = "P2"  # Important — enrichit la qualification
    P3 = "P3"  # Optionnel — valeur ajoutée


class ExtractionMethod(Enum):
    """Méthode d'extraction qui a produit le résultat."""
    REGEX = "regex"           # Extraction par expression régulière
    RULE_BASED = "rule_based" # Règles métier (heuristiques)
    TABLE = "table"           # Extraction de tableau
    OCR = "ocr"               # Reconnaissance optique
    LLM = "llm"               # Modèle de langage
    MANUAL = "manual"         # Saisie manuelle


@dataclass
class ExtractedField:
    """Champ extrait du DCE avec traçabilité complète."""
    name: str                           # Nom technique du champ
    value: Any                          # Valeur extraite
    raw_value: Optional[str] = None     # Valeur brute avant parsing
    confidence: float = 0.0             # Confiance (0.0 - 1.0)
    method: ExtractionMethod = ExtractionMethod.REGEX
    source_page: Optional[int] = None   # Page source dans le PDF
    source_text: Optional[str] = None   # Texte source (contexte)
    extraction_level: int = 0           # Niveau du pipeline (1-4)
    validator: Optional[str] = None     # Nom du validateur utilisé


# ============================================================
# DÉFINITION DES CHAMPS À EXTRAIRE
# ============================================================

EXTRACTION_TARGETS = {
    # ── PRIORITÉ 1 : Critique pour la qualification ──
    
    "cpv_code": {
        "priority": Priority.P1,
        "expected_success_rate": 0.85,      # 85-90%
        "types": [str],
        "validators": ["cpv_format", "cpv_known"],
        "extraction_patterns": [
            r"CPV\s*:?\s*(\d{8}-?\d?)",           # "CPV : 33111000"
            r"code\s+CPV\s*:?\s*(\d{8}-?\d?)",      # "code CPV : 33111000"
            r"(\d{8}-?\d?)\s*[-–]\s*[^\n]{10,50}", # "33111000 - Matériel médical"
            r"CPV\s+principal\s*:?\s*(\d{8})",      # "CPV principal : 33111000"
        ],
        "normalization": lambda v: v.replace("-", "").replace(" ", "").strip()[:8],
    },
    
    "cpv_description": {
        "priority": Priority.P1,
        "expected_success_rate": 0.85,
        "types": [str],
        "extraction_patterns": [
            r"\d{8}\s*[-–]\s*([^\n]{5,100})",       # "33111000 - Matériel médical"
            r"description\s+CPV\s*:?\s*([^\n]{5,100})",
        ],
    },
    
    "estimated_amount": {
        "priority": Priority.P1,
        "expected_success_rate": 0.75,       # 70-80%
        "types": [float, int],
        "validators": ["amount_positive", "amount_reasonable"],
        "extraction_patterns": [
            r"montant\s+(?:total|estimé|maximum)\s*:?\s*(?:HT)?\s*:?\s*([\d\s.,]+)",
            r"valeur\s+(?:totale|estimée)\s*:?\s*([\d\s.,]+)",
            r"budget\s*:?\s*([\d\s.,]+)",
            r"([\d\s.,]+)\s*€\s*(?:HT|TTC)?",
            r"(?:EUR|€)\s*([\d\s.,]+)",
        ],
        "normalization": "parse_amount",  # Fonction spéciale pour parser les montants
    },
    
    "currency": {
        "priority": Priority.P1,
        "expected_success_rate": 0.90,
        "types": [str],
        "default": "EUR",
        "extraction_patterns": [
            r"\b(EUR|€|USD|\$|GBP|£)\b",
        ],
    },
    
    "deadline_submission": {
        "priority": Priority.P1,
        "expected_success_rate": 0.80,       # 75-85%
        "types": ["datetime"],
        "validators": ["date_future", "date_reasonable"],
        "extraction_patterns": [
            r"date\s+limite\s+de\s+r(?:é|e)ception\s*:?\s*([\d]{1,2}[/-][\d]{1,2}[/-][\d]{2,4})",
            r"date\s+limite\s+de\s+d(?:é|e)p(?:ô|o)t\s*:?\s*([\d]{1,2}[/-][\d]{1,2}[/-][\d]{2,4})",
            r"deadline\s*:?\s*([\d]{1,2}[/-][\d]{1,2}[/-][\d]{2,4})",
            r"(?:remettre|dépôt|soumission)\s+avant\s+(?:le\s+)?([\d]{1,2}[/-][\d]{1,2}[/-][\d]{2,4})",
            # Format français textuel : "15 janvier 2025"
            r"(\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4})",
        ],
        "normalization": "parse_french_date",
    },
    
    # ── PRIORITÉ 2 : Enrichissement ──
    
    "award_criteria": {
        "priority": Priority.P2,
        "expected_success_rate": 0.55,       # 50-60%
        "types": [list],
        "extraction_patterns": [
            r"critères?\s+d['\s]attribution\s*:?\s*([^\n]+(?:\n[^\n]+){0,10})",
        ],
        "llm_extraction": True,  # Nécessite souvent le LLM pour structurer
    },
    
    "lots": {
        "priority": Priority.P2,
        "expected_success_rate": 0.65,       # 60-70%
        "types": [list],
        "extraction_patterns": [
            r"lot\s+n?°?\s*\d+\s*:?\s*([^\n]+)",  # "Lot 1 : Fourniture de..."
        ],
        "table_extraction": True,  # Souvent dans des tableaux
    },
    
    "title": {
        "priority": Priority.P2,
        "expected_success_rate": 0.70,
        "types": [str],
        "extraction_patterns": [
            r"objet\s+(?:du\s+)?march(?:é|e)\s*:?\s*([^\n]{10,200})",
            r"titre\s*:?\s*([^\n]{10,200})",
        ],
    },
    
    "description": {
        "priority": Priority.P2,
        "expected_success_rate": 0.65,
        "types": [str],
        "extraction_patterns": [
            r"description\s*:?\s*([^\n]+(?:\n[^\n]+){0,20})",
        ],
    },
    
    "buyer_name": {
        "priority": Priority.P2,
        "expected_success_rate": 0.75,
        "types": [str],
        "extraction_patterns": [
            r"organisme\s+(?:acheteur|public)\s*:?\s*([^\n]{5,100})",
            r"acheteur\s+public\s*:?\s*([^\n]{5,100})",
            r"maître\s+d['\s]ouvrage\s*:?\s*([^\n]{5,100})",
        ],
    },
    
    # ── PRIORITÉ 3 : Optionnel ──
    
    "deadline_questions": {
        "priority": Priority.P3,
        "expected_success_rate": 0.75,       # 70-80%
        "types": ["datetime"],
        "extraction_patterns": [
            r"date\s+limite\s+de\s+questions?\s*:?\s*([\d]{1,2}[/-][\d]{1,2}[/-][\d]{2,4})",
            r"questions?\s+avant\s+(?:le\s+)?([\d]{1,2}[/-][\d]{1,2}[/-][\d]{2,4})",
        ],
        "normalization": "parse_french_date",
    },
    
    "keywords": {
        "priority": Priority.P3,
        "expected_success_rate": 0.60,
        "types": [list],
        "llm_extraction": True,  # Extraction par LLM uniquement
    },
    
    "contract_type": {
        "priority": Priority.P3,
        "expected_success_rate": 0.70,
        "types": [str],
        "extraction_patterns": [
            r"type\s+de\s+march(?:é|e)\s*:?\s*([^\n]{3,50})",
        ],
    },
    
    "procedure_type": {
        "priority": Priority.P3,
        "expected_success_rate": 0.65,
        "types": [str],
        "extraction_patterns": [
            r"proc(?:é|e)dure\s*:?\s*([^\n]{3,50})",
            r"proc(?:é|e)dure\s+(?:adaptée|restreinte|négociée|ouverte)",
        ],
    },
}
```

### 3.3.3 Gestion des échecs

```python
# ============================================================
# takaos/parsing/pipeline.py — Pipeline de Parsing Complet
# ============================================================

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple

import structlog

from takaos.models.domain import Document, Tender
from takaos.parsing.levels import (
    PypdfExtractor, PdfplumberExtractor, OcrExtractor, LlmFallbackExtractor,
)
from takaos.parsing.extraction_targets import EXTRACTION_TARGETS, ExtractedField

logger = structlog.get_logger("takaos.parsing.pipeline")


class ParsingStatus(Enum):
    """Statut du parsing pour un tender."""
    SUCCESS = "success"           # Tous les champs P1 extraits
    PARTIAL = "partial"           # Certains champs P1 manquants
    FAILED = "failed"             # Échec complet — saisie manuelle requise


@dataclass
class ParsingResult:
    """Résultat complet du pipeline de parsing."""
    success: bool                       # Parsing réussi (tous P1)
    partial: bool                       # Parsing partiel (certains P1)
    extracted_fields: Dict[str, Any]    # Champs extraits {nom: valeur}
    field_details: Dict[str, ExtractedField]  # Métadonnées par champ
    levels_tried: List[int]             # Niveaux essayés [1, 2, 3, 4]
    level_succeeded: Optional[int]      # Niveau qui a réussi (1-4)
    processing_time_ms: int
    confidence_scores: Dict[str, float] # Confiance par champ
    global_confidence: float
    log_entries: List[str]              # Log détaillé
    raw_text: Optional[str] = None      # Texte brut accumulé
    error: Optional[str] = None         # Message d'erreur


class ParsingPipeline:
    """
    Pipeline de parsing stratifié en 4 niveaux.
    
    Principe : essayer les niveaux du plus rapide au plus lent,
    s'arrêter dès que les champs P1 sont extraits.
    
    Niveau 1 : pypdf (rapide, 60% des cas)
    Niveau 2 : pdfplumber (structuré, 25% des cas)
    Niveau 3 : OCR Tesseract (scannés, 10% des cas)
    Niveau 4 : LLM Mistral (fallback, 5% des cas)
    """

    # Seuils de succès
    P1_FIELDS_REQUIRED = ["cpv_code", "estimated_amount", "deadline_submission"]
    CONFIDENCE_THRESHOLD = 0.5          # Confiance minimale pour considérer un champ valide
    OCR_MIN_CONFIDENCE = 0.6            # Confiance minimale OCR

    def __init__(
        self,
        pypdf_extractor: PypdfExtractor,
        pdfplumber_extractor: PdfplumberExtractor,
        ocr_extractor: OcrExtractor,
        llm_extractor: LlmFallbackExtractor,
    ) -> None:
        self._extractors = {
            1: pypdf_extractor,
            2: pdfplumber_extractor,
            3: ocr_extractor,
            4: llm_extractor,
        }

    async def execute(
        self, document: Document, tenant_id: str
    ) -> ParsingResult:
        """
        Exécute le pipeline de parsing complet.
        
        Strategy : essayer les niveaux séquentiellement, accumuler
        les champs extraits, s'arrêter quand tous les P1 sont trouvés.
        """
        start_time = time.monotonic()
        log_entries: List[str] = []
        levels_tried: List[int] = []
        
        # Accumulateur de champs extraits
        all_fields: Dict[str, ExtractedField] = {}
        raw_text_accumulated: List[str] = []
        
        # --- Essai des niveaux 1 à 3 (rapides, pas de LLM) ---
        for level in [1, 2, 3]:
            levels_tried.append(level)
            extractor = self._extractors[level]
            
            try:
                level_start = time.monotonic()
                level_result = await extractor.extract(document)
                level_ms = int((time.monotonic() - level_start) * 1000)
                
                log_entries.append(
                    f"Niveau {level} ({extractor.name}): "
                    f"{len(level_result.fields)} champs en {level_ms}ms, "
                    f"confiance={level_result.avg_confidence:.2f}"
                )
                
                # Accumulation du texte brut
                if level_result.raw_text:
                    raw_text_accumulated.append(level_result.raw_text)
                
                # Fusion des champs (garder le meilleur score par champ)
                for name, field in level_result.fields.items():
                    if name not in all_fields or field.confidence > all_fields[name].confidence:
                        all_fields[name] = field
                
                # Vérification : tous les champs P1 sont-ils trouvés avec bonne confiance ?
                if self._has_all_p1_fields(all_fields):
                    log_entries.append(
                        f"Arrêt au niveau {level} — tous les champs P1 trouvés"
                    )
                    break
                    
            except Exception as exc:
                log_entries.append(f"Niveau {level} ÉCHEC: {str(exc)}")
                logger.warning("parsing.level_failed",
                             level=level, document_id=document.id, error=str(exc))
                continue
        
        # --- Niveau 4 : LLM Fallback si champs P1 manquants ---
        if not self._has_all_p1_fields(all_fields):
            levels_tried.append(4)
            
            try:
                llm_start = time.monotonic()
                
                # Préparation du texte brut accumulé
                combined_text = "\n\n".join(raw_text_accumulated)
                
                # Champs déjà trouvés (pour ne pas les re-demander)
                already_found = {name: f.value for name, f in all_fields.items()}
                
                llm_result = await self._extractors[4].extract(
                    document=document,
                    raw_text=combined_text,
                    missing_fields=self._get_missing_p1_fields(all_fields),
                    already_found=already_found,
                )
                
                llm_ms = int((time.monotonic() - llm_start) * 1000)
                log_entries.append(
                    f"Niveau 4 (LLM): {len(llm_result.fields)} champs en {llm_ms}ms, "
                    f"confiance={llm_result.avg_confidence:.2f}"
                )
                
                # Fusion (LLM peut aussi améliorer des champs existants)
                for name, field in llm_result.fields.items():
                    if name not in all_fields or field.confidence > all_fields[name].confidence:
                        all_fields[name] = field
                        
            except Exception as exc:
                log_entries.append(f"Niveau 4 ÉCHEC: {str(exc)}")
                logger.error("parsing.llm_fallback_failed",
                           document_id=document.id, error=str(exc))
        
        # --- Construction du résultat ---
        processing_ms = int((time.monotonic() - start_time) * 1000)
        
        # Évaluation du résultat global
        has_all_p1 = self._has_all_p1_fields(all_fields)
        has_some_p1 = self._has_some_p1_fields(all_fields)
        
        status = (
            ParsingStatus.SUCCESS if has_all_p1
            else ParsingStatus.PARTIAL if has_some_p1
            else ParsingStatus.FAILED
        )
        
        # Calcul de la confiance globale
        p1_confidences = [
            all_fields[f].confidence for f in self.P1_FIELDS_REQUIRED if f in all_fields
        ]
        global_confidence = sum(p1_confidences) / len(p1_confidences) if p1_confidences else 0.0
        
        # Confiance par champ
        confidence_scores = {name: f.confidence for name, f in all_fields.items()}
        
        # Valeurs finales (pour injection dans le Tender)
        extracted_values = {name: f.value for name, f in all_fields.items()}
        
        result = ParsingResult(
            success=status == ParsingStatus.SUCCESS,
            partial=status == ParsingStatus.PARTIAL,
            extracted_fields=extracted_values,
            field_details=all_fields,
            levels_tried=levels_tried,
            level_succeeded=levels_tried[-1] if has_some_p1 else None,
            processing_time_ms=processing_ms,
            confidence_scores=confidence_scores,
            global_confidence=round(global_confidence, 4),
            log_entries=log_entries,
            raw_text="\n\n".join(raw_text_accumulated) if raw_text_accumulated else None,
        )
        
        logger.info("parsing.completed",
                   document_id=document.id,
                   status=status.value,
                   fields_found=len(all_fields),
                   global_confidence=round(global_confidence, 3),
                   processing_ms=processing_ms)
        
        return result

    # ------------------------------------------------------------------
    # Utilitaires
    # ------------------------------------------------------------------

    def _has_all_p1_fields(self, fields: Dict[str, ExtractedField]) -> bool:
        """Vérifie que tous les champs P1 sont présents avec confiance suffisante."""
        for required in self.P1_FIELDS_REQUIRED:
            if required not in fields:
                return False
            if fields[required].confidence < self.CONFIDENCE_THRESHOLD:
                return False
        return True

    def _has_some_p1_fields(self, fields: Dict[str, ExtractedField]) -> bool:
        """Vérifie qu'au moins un champ P1 est présent."""
        return any(f in fields for f in self.P1_FIELDS_REQUIRED)

    def _get_missing_p1_fields(self, fields: Dict[str, ExtractedField]) -> List[str]:
        """Retourne la liste des champs P1 manquants."""
        missing = []
        for required in self.P1_FIELDS_REQUIRED:
            if required not in fields:
                missing.append(required)
            elif fields[required].confidence < self.CONFIDENCE_THRESHOLD:
                missing.append(required)
        return missing
```

### 3.3.4 Traitement asynchrone

```python
# ============================================================
# takaos/parsing/async_processor.py — Traitement Asynchrone
# ============================================================

import asyncio
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, Callable
from uuid import UUID

import structlog

from takaos.parsing.pipeline import ParsingPipeline, ParsingResult
from takaos.models.domain import Document, Tender

logger = structlog.get_logger("takaos.parsing.async_processor")


class ProcessingState(Enum):
    """État d'une tâche de parsing."""
    QUEUED = "queued"           # En file d'attente
    RUNNING = "running"         # En cours d'exécution
    COMPLETED = "completed"     # Terminé avec succès
    PARTIAL = "partial"         # Terminé partiellement
    FAILED = "failed"           # Échec complet
    CANCELLED = "cancelled"     # Annulé


@dataclass
class ProcessingJob:
    """Tâche de parsing traçable."""
    job_id: str
    tender_id: str
    document_id: str
    tenant_id: str
    state: ProcessingState
    progress_percent: int = 0
    result: Optional[ParsingResult] = None
    error: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class AsyncParsingProcessor:
    """
    Processeur asynchrone de parsing avec file d'attente et notifications.
    
    Architecture :
    - Upload = immédiat (sauvegarde fichier)
    - Parsing = tâche de fond (asyncio.create_task)
    - Notification au client via WebSocket
    - File d'attente avec limite de concurrence
    """

    def __init__(
        self,
        parsing_pipeline: ParsingPipeline,
        max_concurrent: int = 5,
        websocket_manager: Optional[Any] = None,
    ) -> None:
        self._pipeline = parsing_pipeline
        self._max_concurrent = max_concurrent
        self._ws = websocket_manager
        
        # Sémaphore pour limiter la concurrence
        self._semaphore = asyncio.Semaphore(max_concurrent)
        
        # Registre des jobs actifs
        self._jobs: Dict[str, ProcessingJob] = {}

    async def submit(
        self,
        document: Document,
        tender_id: str,
        tenant_id: str,
    ) -> str:
        """
        Soumet un document au pipeline de parsing asynchrone.
        
        Returns immédiatement un job_id pour le tracking.
        """
        job_id = f"parse-{tender_id[:8]}-{datetime.utcnow().strftime('%H%M%S')}"
        
        job = ProcessingJob(
            job_id=job_id,
            tender_id=tender_id,
            document_id=document.id,
            tenant_id=tenant_id,
            state=ProcessingState.QUEUED,
        )
        self._jobs[job_id] = job
        
        # Lancement en tâche de fond (fire-and-forget)
        asyncio.create_task(
            self._process_job(job, document),
            name=job_id,
        )
        
        logger.info("async_processor.submitted",
                   job_id=job_id, tender_id=tender_id,
                   document_id=document.id)
        
        return job_id

    async def _process_job(self, job: ProcessingJob, document: Document) -> None:
        """
        Exécute le parsing avec sémaphore de concurrence et notifications.
        """
        async with self._semaphore:
            job.state = ProcessingState.RUNNING
            job.started_at = datetime.utcnow()
            
            # Notification : démarrage
            await self._notify_progress(job)
            
            try:
                # Progression simulée pour le client
                await self._update_progress(job, 10)
                await asyncio.sleep(0.5)  # Latence réseau simulée
                
                await self._update_progress(job, 30)
                
                # === EXÉCUTION DU PIPELINE ===
                result: ParsingResult = await self._pipeline.execute(
                    document=document,
                    tenant_id=job.tenant_id,
                )
                
                await self._update_progress(job, 90)
                
                # Finalisation
                job.result = result
                job.completed_at = datetime.utcnow()
                
                if result.success:
                    job.state = ProcessingState.COMPLETED
                elif result.partial:
                    job.state = ProcessingState.PARTIAL
                else:
                    job.state = ProcessingState.FAILED
                
                await self._update_progress(job, 100)
                
                logger.info("async_processor.completed",
                           job_id=job.job_id,
                           state=job.state.value,
                           processing_ms=result.processing_time_ms)
                
            except Exception as exc:
                job.state = ProcessingState.FAILED
                job.error = str(exc)
                job.completed_at = datetime.utcnow()
                
                logger.error("async_processor.failed",
                            job_id=job.job_id, error=str(exc))
                
                await self._notify_progress(job)

    async def _update_progress(self, job: ProcessingJob, percent: int) -> None:
        """Met à jour la progression et notifie le client."""
        job.progress_percent = percent
        await self._notify_progress(job)

    async def _notify_progress(self, job: ProcessingJob) -> None:
        """
        Notifie le client via WebSocket de l'état du parsing.
        Fallback sur polling si WebSocket non disponible.
        """
        payload = {
            "type": "parsing_progress",
            "job_id": job.job_id,
            "tender_id": job.tender_id,
            "state": job.state.value,
            "progress_percent": job.progress_percent,
            "processing_ms": (
                int((job.completed_at - job.started_at).total_seconds() * 1000)
                if job.completed_at and job.started_at else None
            ),
        }
        
        # Ajout des résultats si terminé
        if job.result:
            payload["result"] = {
                "success": job.result.success,
                "partial": job.result.partial,
                "fields_found": list(job.result.extracted_fields.keys()),
                "global_confidence": job.result.global_confidence,
                "levels_tried": job.result.levels_tried,
            }
        
        if job.error:
            payload["error"] = job.error
        
        # Envoi WebSocket (room = tenant_id)
        if self._ws:
            try:
                await self._ws.broadcast_to_room(
                    room=f"tenant:{job.tenant_id}",
                    message=payload,
                )
            except Exception:
                # Fallback silencieux — le client peut poller
                pass

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Endpoint de polling pour le client."""
        job = self._jobs.get(job_id)
        if not job:
            return None
        
        return {
            "job_id": job.job_id,
            "tender_id": job.tender_id,
            "state": job.state.value,
            "progress_percent": job.progress_percent,
            "fields_found": (
                list(job.result.extracted_fields.keys()) if job.result else []
            ),
            "error": job.error,
        }
```

---

## 3.4 Intégration Mistral AI

### 3.4.1 Configuration

```python
# ============================================================
# takaos/llm/config.py — Configuration Mistral AI
# ============================================================

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class MistralConfig:
    """
    Configuration de l'API Mistral AI.
    
    Modèles disponibles :
    - mistral-large-latest : Tâches complexes (qualification, analyse)
    - mistral-medium : Tâches intermédiaires
    - mistral-small : Tâches simples (résumé, extraction basique)
    - mistral-embed : Embeddings (768 dimensions)
    """
    
    # Endpoint et authentification
    api_endpoint: str = "https://api.mistral.ai/v1/chat/completions"
    embeddings_endpoint: str = "https://api.mistral.ai/v1/embeddings"
    api_key: str = ""                       # À charger depuis env var
    
    # Modèles par usage
    model_complex: str = "mistral-large-latest"   # Qualification, analyse stratégique
    model_standard: str = "mistral-small-latest"  # Parsing, résumé
    model_embeddings: str = "mistral-embed"       # Vecteurs
    
    # Paramètres de génération
    temperature_precision: float = 0.1     # Qualification, scoring (précis)
    temperature_creative: float = 0.3      # Parsing, résumé (légère créativité)
    max_tokens_qualification: int = 1024
    max_tokens_parsing: int = 2048
    max_tokens_summary: int = 1500
    
    # Timeout et retry
    timeout_seconds: float = 30.0
    retry_max_attempts: int = 3
    retry_base_delay: float = 2.0
    retry_max_delay: float = 10.0
    retry_exponential_base: float = 2.0
    
    # Circuit Breaker
    circuit_failure_threshold: int = 5     # Échecs avant ouverture
    circuit_recovery_timeout: float = 60.0 # Secondes avant HALF-OPEN
    circuit_half_open_max_calls: int = 2   # Appels test en HALF-OPEN
    
    # Rate limiting (côté client)
    rate_limit_requests_per_minute: int = 60
    rate_limit_tokens_per_minute: int = 200000
    
    # Fallback
    fallback_to_rules_only: bool = True    # Si circuit ouvert, scoring règles uniquement


# Instance par défaut (surchargeable par tenant)
DEFAULT_MISTRAL_CONFIG = MistralConfig()
```

### 3.4.2 Client HTTP (httpx)

```python
# ============================================================
# takaos/llm/mistral_client.py — Client HTTP Mistral
# ============================================================

import asyncio
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import httpx
import structlog
from tenacity import (
    retry, stop_after_attempt, wait_exponential,
    retry_if_exception_type, before_sleep_log,
)

from takaos.llm.config import MistralConfig

logger = structlog.get_logger("takaos.llm.mistral_client")


class CircuitState(Enum):
    """État du circuit breaker."""
    CLOSED = "closed"           # Fonctionnement normal
    OPEN = "open"               # Circuit ouvert — rejette les appels
    HALF_OPEN = "half_open"     # Test de récupération


class CircuitOpenError(Exception):
    """Levé quand le circuit breaker est ouvert."""
    pass


@dataclass
class LLMResponse:
    """Réponse structurée de l'API Mistral."""
    content: str                        # Contenu textuel
    model: str                          # Modèle utilisé
    usage: Dict[str, int] = field(default_factory=dict)
    finish_reason: str = "stop"
    latency_ms: int = 0
    raw_response: Optional[Dict] = None


class CircuitBreaker:
    """
    Circuit Breaker pour l'API Mistral.
    
    États :
    - CLOSED : Les appels passent normalement
    - OPEN : Les appels sont rejetés immédiatement (après N échecs)
    - HALF_OPEN : Quelques appels test autorisés après timeout de récupération
    
    Transitions :
    CLOSED ──(N échecs)──▶ OPEN ──(timeout)──▶ HALF_OPEN
     ▲                                               │
     └────────(succès)───────────────────────────────┘
     ▲                                               │
     └────────(échec)────────────────────────────────┘ (retour OPEN)
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 2,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._half_open_max_calls = half_open_max_calls
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._half_open_calls = 0
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CircuitState:
        return self._state

    async def call(self, coro_factory):
        """
        Exécute une coroutine via le circuit breaker.
        
        Args :
            coro_factory : Fonction sans argument retournant une coroutine.
                          (évite l'évaluation prématurée de la coroutine)
        """
        async with self._lock:
            # Vérification de l'état
            if self._state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._state = CircuitState.HALF_OPEN
                    self._half_open_calls = 0
                    logger.info("circuit_breaker.half_open")
                else:
                    raise CircuitOpenError(
                        f"Circuit breaker OPEN — réessayez dans "
                        f"{self._remaining_timeout():.0f}s"
                    )
            
            if self._state == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self._half_open_max_calls:
                    raise CircuitOpenError(
                        "Circuit breaker HALF_OPEN — limite d'appels test atteinte"
                    )
                self._half_open_calls += 1

        # Exécution (hors du lock)
        try:
            result = await coro_factory()
            await self._on_success()
            return result
        except Exception as exc:
            await self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """Vérifie si le timeout de récupération est écoulé."""
        if self._last_failure_time is None:
            return True
        return (time.monotonic() - self._last_failure_time) >= self._recovery_timeout

    def _remaining_timeout(self) -> float:
        """Temps restant avant tentative de HALF_OPEN."""
        if self._last_failure_time is None:
            return 0.0
        elapsed = time.monotonic() - self._last_failure_time
        return max(0.0, self._recovery_timeout - elapsed)

    async def _on_success(self):
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self._half_open_max_calls:
                    # Récupération complète
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    self._success_count = 0
                    logger.info("circuit_breaker.closed")
            else:
                self._failure_count = max(0, self._failure_count - 1)

    async def _on_failure(self):
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()
            
            if self._state == CircuitState.HALF_OPEN:
                # Échec en HALF_OPEN → retour OPEN
                self._state = CircuitState.OPEN
                logger.warning("circuit_breaker.open_from_half")
            elif self._failure_count >= self._failure_threshold:
                self._state = CircuitState.OPEN
                logger.warning("circuit_breaker.open",
                             failure_count=self._failure_count)


class MistralClient:
    """
    Client HTTP pour l'API Mistral AI.
    
    Fonctionnalités :
    - Appels API via httpx (async)
    - Retry exponentiel 3x (tenacity)
    - Circuit breaker intégré
    - Parsing JSON structuré des réponses
    - Fallback gracieux en cas d'indisponibilité
    """

    def __init__(self, config: MistralConfig) -> None:
        self._config = config
        self._circuit = CircuitBreaker(
            failure_threshold=config.circuit_failure_threshold,
            recovery_timeout=config.circuit_recovery_timeout,
            half_open_max_calls=config.circuit_half_open_max_calls,
        )
        
        # Client HTTP persistent (connection pooling)
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(config.timeout_seconds),
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            headers={"Authorization": f"Bearer {config.api_key}"},
        )

    async def close(self):
        """Fermeture propre du client HTTP."""
        await self._client.aclose()

    # ------------------------------------------------------------------
    # API Publique
    # ------------------------------------------------------------------

    async def complete(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
        response_format: Optional[Dict[str, str]] = None,
    ) -> LLMResponse:
        """
        Appel completion à l'API Mistral.
        
        Args :
            prompt : Prompt complet (système + user combinés)
            temperature : 0.1=précis, 0.3=créatif
            max_tokens : Limite de tokens générés
            model : Override du modèle
            response_format : {"type": "json_object"} pour JSON forcé
        """
        model = model or self._config.model_standard
        temperature = temperature or self._config.temperature_precision
        max_tokens = max_tokens or self._config.max_tokens_qualification
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": self._system_prompt()},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if response_format:
            payload["response_format"] = response_format
        
        # Exécution via circuit breaker
        start_time = time.monotonic()
        
        raw_response = await self._circuit.call(
            lambda: self._request_with_retry(payload)
        )
        
        latency_ms = int((time.monotonic() - start_time) * 1000)
        
        # Parsing de la réponse
        content = raw_response["choices"][0]["message"]["content"]
        
        return LLMResponse(
            content=content,
            model=raw_response.get("model", model),
            usage=raw_response.get("usage", {}),
            finish_reason=raw_response["choices"][0].get("finish_reason", "stop"),
            latency_ms=latency_ms,
            raw_response=raw_response,
        )

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Génère des embeddings via l'API Mistral.
        
        Batch size max : 96 textes par appel.
        """
        all_embeddings: List[List[float]] = []
        batch_size = 96
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            payload = {
                "model": self._config.model_embeddings,
                "input": batch,
            }
            
            response = await self._circuit.call(
                lambda: self._request_with_retry(payload, endpoint="embeddings")
            )
            
            all_embeddings.extend([
                d["embedding"] for d in response["data"]
            ])
        
        return all_embeddings

    # ------------------------------------------------------------------
    # Retry avec tenacity
    # ------------------------------------------------------------------

    @retry(
        retry=retry_if_exception_type((
            httpx.TimeoutException,
            httpx.ConnectError,
            httpx.HTTPStatusError,
        )),
        stop=stop_after_attempt(3),  # Configurable
        wait=wait_exponential(
            multiplier=2,
            min=2,
            max=10,
        ),
        reraise=True,
    )
    async def _request_with_retry(
        self,
        payload: Dict[str, Any],
        endpoint: str = "chat",
    ) -> Dict[str, Any]:
        """
        Requête HTTP avec retry exponentiel.
        N'est appelée que si le circuit breaker est CLOSED ou HALF_OPEN.
        """
        url = (
            self._config.embeddings_endpoint if endpoint == "embeddings"
            else self._config.api_endpoint
        )
        
        response = await self._client.post(url, json=payload)
        
        # Gestion des erreurs HTTP
        if response.status_code == 429:
            # Rate limit — retry après le header Retry-After
            retry_after = int(response.headers.get("retry-after", 5))
            logger.warning("mistral.rate_limited", retry_after=retry_after)
            await asyncio.sleep(retry_after)
            response.raise_for_status()
        
        if response.status_code >= 500:
            logger.error("mistral.server_error",
                        status=response.status_code,
                        body=response.text[:500])
            response.raise_for_status()
        
        response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------
    # Parsing JSON
    # ------------------------------------------------------------------

    def parse_json_response(self, response: LLMResponse) -> Dict[str, Any]:
        """
        Parse la réponse JSON du LLM avec gestion des erreurs.
        """
        content = response.content.strip()
        
        # Nettoyage : suppression des ```json ... ```
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            logger.error("mistral.json_parse_error",
                        content_preview=content[:200],
                        error=str(exc))
            # Fallback : extraction du premier objet JSON trouvé
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            raise ValueError(f"Réponse LLM non parsable en JSON : {content[:200]}")

    # ------------------------------------------------------------------
    # Utilitaires
    # ------------------------------------------------------------------

    def _system_prompt(self) -> str:
        """Prompt système par défaut pour tous les appels."""
        return (
            "Tu es un assistant expert en marchés publics français et belges. "
            "Tu analyses des Documents de Consultation des Entreprises (DCE). "
            "Tu réponds de manière concise, précise et structurée. "
            "Quand on te demande du JSON, tu réponds UNIQUEMENT avec du JSON valide, "
            "sans texte additionnel, sans markdown."
        )

    @property
    def circuit_state(self) -> str:
        """État du circuit breaker (pour monitoring)."""
        return self._circuit.state.value
```

### 3.4.3 Prompts Templates (Jinja2)

#### a) Template Qualification

```jinja2
{# ============================================================ #}
{# Template : Qualification (LLM Fallback)                     #}
{# Usage : Zone ambiguë (score règles 0.3-0.7)                 #}
{# Temperature : 0.1 — Précision maximale                       #}
{# ============================================================ #}

Tu es un expert en stratégie de réponse aux marchés publics. Tu aides une
entreprise à décider si elle doit investir des ressources pour répondre à
un Appel d'Offres (AO).

=== CONTEXTE DU DCE ===
Titre : {{ tender.title | default("Non spécifié") }}
Description : {{ tender.description | default("Non spécifiée") }}
Code CPV : {{ tender.cpv_code | default("Non extrait") }} — {{ tender.cpv_description | default("") }}
Montant estimé : {% if tender.estimated_amount %}{{ "{:,.0f}".format(tender.estimated_amount) }} {{ tender.currency | default("EUR") }}{% else %}Non extrait{% endif %}
Deadline soumission : {{ tender.deadline_submission | default("Non extraite") }}
Deadline questions : {{ tender.deadline_questions | default("Non extraite") }}
Acheteur public : {{ tender.buyer_name | default("Non identifié") }}
Nombre de lots : {{ tender.lots | length if tender.lots else 0 }}
Critères d'attribution : {{ tender.award_criteria | join(", ") | default("Non extraits") }}

=== PROFIL DE L'ENTREPRISE ===
CPV cibles : {{ rules.cpv_target | join(", ") | default("Non configuré") }}
Fourchette montant : [{{ rules.amount_range.min | default("N/A") }}, {{ rules.amount_range.max | default("N/A") }}] EUR
Jours min de préparation : {{ rules.min_preparation_days | default(14) }}

=== SCORES RÈGLES DÉJÀ CALCULÉS ===
{% for cs in criterion_scores %}
- {{ cs.name }} : {{ "%.2f" | format(cs.score) }} ({{ "PASS" if cs.passed else "FAIL" }}) — {{ cs.details | tojson }}
{% endfor %}
Score règles global : {{ "%.2f" | format(rules_score) }}

=== INSTRUCTIONS ===
1. Analyse le DCE au regard du profil de l'entreprise
2. Identifie les facteurs clés favorables et défavorables
3. Attribue un score global 0.0-1.0 (0=déconseillé fortement, 1=recommandé fortement)
4. Fournis un raisonnement structuré

=== FORMAT DE RÉPONSE (JSON OBLIGATOIRE) ===
{
  "score": 0.72,
  "justification": "Le CPV correspond au cœur de métier...",
  "key_factors": ["facteur 1", "facteur 2"],
  "confidence": 0.85,
  "risks": ["risque 1", "risque 2"]
}
```

#### b) Template Parsing

```jinja2
{# ============================================================ #}
{# Template : Parsing (Extraction de champs)                   #}
{# Usage : Niveau 4 — Fallback LLM pour champs manquants       #}
{# Temperature : 0.3 — Créativité légère pour interprétation   #}
{# ============================================================ #}

Tu es un système d'extraction d'informations pour les marchés publics.
Tu dois extraire des champs spécifiques du texte brut d'un DCE ci-dessous.

=== TEXTE DU DCE ===
{{ raw_text[:12000] }}
{% if raw_text | length > 12000 %}
[... texte tronqué ...]
{% endif %}
=== FIN DU TEXTE ===

=== CHAMPS À EXTRAIRE ===
{% for field in missing_fields %}
- {{ field }} : {{ field_descriptions[field] | default("") }}
{% endfor %}

{% if already_found %}
=== CHAMPS DÉJÀ TROUVÉS (ne pas modifier) ===
{{ already_found | tojson(indent=2) }}
{% endif %}

=== RÈGLES D'EXTRACTION ===
- CPV : Code à 8 chiffres (ex: 33111000). Le libellé CPV est aussi utile.
- Montant : Valeur numérique en EUR. Ignorer les montants par lot, prendre le total.
- Deadline : Format ISO 8601 (YYYY-MM-DD). Parser les dates françaises.
- Si un champ n'est pas trouvé dans le texte, retourner null (pas de valeur inventée).

=== FORMAT DE RÉPONSE (JSON OBLIGATOIRE) ===
{
  "cpv_code": "33111000",
  "cpv_description": "Matériel médical",
  "estimated_amount": 450000,
  "currency": "EUR",
  "deadline_submission": "2025-03-15",
  "deadline_questions": "2025-02-28",
  "confidence": 0.85,
  "found_fields": ["cpv_code", "estimated_amount", "deadline_submission"],
  "notes": "Dates extraites du tableau récapitulatif page 3."
}
```

#### c) Template Résumé

```jinja2
{# ============================================================ #}
{# Template : Résumé de DCE                                     #}
{# Usage : Génération résumé 500 mots pour qualification       #}
{# Temperature : 0.3                                            #}
{# ============================================================ #}

Résume le Document de Consultation des Entreprises suivant en maximum 500 mots.
Le résumé doit être structuré et couvrir :

1. **Objet du marché** : de quoi parle cet AO ?
2. **Acheteur public** : qui lance l'AO ?
3. **Montant et durée** : budget estimé et durée du contrat
4. **Deadlines** : dates limites clés
5. **Critères d'attribution** : sur quels critères sera évaluée l'offre ?
6. **Lots** : le marché est-il découpé en lots ?
7. **Conditions particulières** : exigences techniques, garanties, etc.
8. **Opportunités et risques** : points forts et points d'attention

=== TEXTE DU DCE ===
{{ raw_text[:15000] }}
=== FIN ===

Rédige en français professionnel. Sois factuel et précis.
```

#### d) Registre des templates

```python
# ============================================================
# takaos/templates/__init__.py — Registre des templates Jinja2
# ============================================================

from jinja2 import Environment, PackageLoader, select_autoescape

# Configuration de l'environnement Jinja2
jinja_env = Environment(
    loader=PackageLoader("takaos", "templates/prompts"),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)

# Chargement des templates
QUALIFIER_PROMPT_TEMPLATE = jinja_env.get_template("qualifier.jinja2")
PARSING_PROMPT_TEMPLATE = jinja_env.get_template("parsing.jinja2")
SUMMARY_PROMPT_TEMPLATE = jinja_env.get_template("summary.jinja2")

# Mapping usage → template
TEMPLATE_REGISTRY = {
    "qualification": QUALIFIER_PROMPT_TEMPLATE,
    "parsing": PARSING_PROMPT_TEMPLATE,
    "summary": SUMMARY_PROMPT_TEMPLATE,
}
```

---

## 3.5 Schéma SQL Complet des Tables Agent

```sql
-- ============================================================
-- Schéma complet — Section 3 : Agents & Mémoire
-- ============================================================

-- Table des statuts de tender (enum en pratique)
-- DETECTED → PARSING → PARSED / PARSED_PARTIAL / PARSING_FAILED
-- → QUALIFIED_GO / QUALIFIED_NOGO / QUALIFIED_MAYBE
-- → IN_PREPARATION → SUBMITTED → WON / LOST

-- tender_parsing_logs — Log détaillé du pipeline de parsing
CREATE TABLE tender_parsing_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tender_id       UUID NOT NULL REFERENCES tenders(id) ON DELETE CASCADE,
    document_id     UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    level           INTEGER NOT NULL,               -- Niveau du pipeline (1-4)
    extractor_name  VARCHAR(32) NOT NULL,           -- 'pypdf', 'pdfplumber', 'ocr', 'llm'
    success         BOOLEAN NOT NULL,
    fields_found    JSONB DEFAULT '{}',             -- {field_name: value}
    confidence      DECIMAL(4,3),                   -- Confiance globale
    processing_ms   INTEGER,
    error_message   TEXT,
    raw_text_sample TEXT,                           -- Échantillon du texte extrait
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    
    INDEX idx_parsing_logs_tender (tender_id)
);

-- alert_history — Historique des alertes émises (dédoublonnage)
CREATE TABLE alert_history (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tender_id       UUID NOT NULL REFERENCES tenders(id) ON DELETE CASCADE,
    tenant_id       UUID NOT NULL,
    alert_type      VARCHAR(32) NOT NULL,           -- 'submission_30d', 'questions_7d', etc.
    deadline_type   VARCHAR(16) NOT NULL,           -- 'submission' | 'questions'
    days_before     INTEGER NOT NULL,
    level           VARCHAR(16) NOT NULL,           -- 'info' | 'warning' | 'urgent' | 'critical' | 'final'
    channels        TEXT[] DEFAULT '{}',
    message         TEXT NOT NULL,
    emitted_at      TIMESTAMPTZ DEFAULT NOW(),
    
    -- Contrainte de dédoublonnage
    CONSTRAINT uq_alert_per_day UNIQUE (tender_id, alert_type, DATE(emitted_at))
);

-- llm_call_logs — Audit des appels LLM (coût, performance, qualité)
CREATE TABLE llm_call_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    call_type       VARCHAR(32) NOT NULL,           -- 'qualification' | 'parsing' | 'summary' | 'embedding'
    model           VARCHAR(64) NOT NULL,
    prompt_tokens   INTEGER,
    completion_tokens INTEGER,
    total_tokens    INTEGER,
    latency_ms      INTEGER NOT NULL,
    cost_eur        DECIMAL(8,6),                   -- Estimation du coût
    success         BOOLEAN NOT NULL,
    error_type      VARCHAR(64),                    -- 'timeout' | 'rate_limit' | 'parse_error' | ...
    circuit_state   VARCHAR(16),                    -- 'closed' | 'open' | 'half_open'
    response_preview TEXT,                          -- 500 premiers caractères
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    
    INDEX idx_llm_logs_tenant (tenant_id, created_at),
    INDEX idx_llm_logs_type (call_type, created_at)
);
```

---

## 3.6 Résumé des Flux de Données

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FLUX DE DONNÉES INTER-AGENTS                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [UPLOAD]          [PARSE]           [QUALIFY]         [TRACK]             │
│     │                 │                  │                │                │
│     ▼                 ▼                  ▼                ▼                │
│  ┌─────────┐     ┌──────────┐      ┌──────────┐     ┌──────────┐          │
│  │ SOURCER │────▶│ Pipeline │─────▶│ QUALIF.  │────▶│ TRACKER  │          │
│  │         │     │ PDF 4L   │      │ 80/20    │     │ Cron     │          │
│  └─────────┘     └──────────┘      └──────────┘     └──────────┘          │
│       │                │                 │               │                 │
│       │                │                 │               │                 │
│       ▼                ▼                 ▼               ▼                 │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │                    MÉMOIRE (pgvector)                             │      │
│  │  • Parsing → memory_vectors (texte brut DCE)                     │      │
│  │  • Qualif. → memory_vectors (résultats épisodiques)              │      │
│  │  • Qualif. ← memory_vectors (recherche cas similaires)           │      │
│  │  • Won/Lost → memory_vectors (capitalisation succès/échecs)      │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │                    MISTRAL AI API                                 │      │
│  │  • Qualif. ← LLM fallback (zone ambiguë 0.3-0.7)                │      │
│  │  • Parsing ← LLM Niveau 4 (champs manquants)                     │      │
│  │  • Mémoire ← Embeddings 768d                                     │      │
│  │  • Circuit breaker + retry 3x pour résilience                    │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │                    NOTIFICATIONS                                  │      │
│  │  • Sourcer → WebSocket (parsing en temps réel)                   │      │
│  │  • Qualif. → WebSocket (résultat GO/NOGO/MAYBE)                 │      │
│  │  • Tracker → Email SMTP + Push + SMS (deadlines)                 │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3.7 Checklist d'Implémentation

| # | Tâche | Priorité | Fichier(s) | Dépendances |
|---|-------|----------|------------|-------------|
| 1 | Modèle `SourcerInput` + détection format | P0 | `models/sourcer.py` | — |
| 2 | Agent Sourcer + event handler | P0 | `agents/sourcer.py` | (1) |
| 3 | Table `documents` + repository | P0 | `db/repositories/document_repo.py` | Migrations |
| 4 | Extracteur pypdf (Niveau 1) | P0 | `parsing/levels/pypdf_extractor.py` | pypdf |
| 5 | Extracteur pdfplumber (Niveau 2) | P0 | `parsing/levels/pdfplumber_extractor.py` | pdfplumber |
| 6 | Extracteur OCR Tesseract (Niveau 3) | P1 | `parsing/levels/ocr_extractor.py` | pytesseract, pdf2image |
| 7 | Extracteur LLM Mistral (Niveau 4) | P1 | `parsing/levels/llm_extractor.py` | MistralClient |
| 8 | Pipeline de parsing orchestrateur | P0 | `parsing/pipeline.py` | (4,5,6,7) |
| 9 | Client HTTP Mistral + Circuit Breaker | P0 | `llm/mistral_client.py` | httpx, tenacity |
| 10 | Templates Jinja2 (qualif/parsing/résumé) | P0 | `templates/prompts/*.jinja2` | jinja2 |
| 11 | EmbeddingPipeline (API + local) | P0 | `memory/embeddings.py` | httpx / transformers |
| 12 | MemorySystem (pgvector) | P0 | `memory/vector_store.py` | asyncpg, pgvector |
| 13 | EpisodicMemoryCapitalizer | P1 | `memory/episodic.py` | (12) |
| 14 | Agent Qualifieur (scoring 80/20) | P0 | `agents/qualifier.py` | (8,9,12) |
| 15 | Agent Tracker + APScheduler | P1 | `agents/tracker.py` | apscheduler |
| 16 | Service de notifications | P1 | `notifications/service.py` | aiosmtplib |
| 17 | AsyncParsingProcessor + WS | P1 | `parsing/async_processor.py` | websockets |
| 18 | Tests d'intégration agents | P1 | `tests/agents/` | (2,14,15) |

---

> **Document généré pour TAKA OS — Section 3 : Agents & Système de Mémoire**
> Stack : PostgreSQL 15 + pgvector | httpx + Jinja2 | Mistral AI API | pypdf / pdfplumber / Tesseract
> Licence : MIT
