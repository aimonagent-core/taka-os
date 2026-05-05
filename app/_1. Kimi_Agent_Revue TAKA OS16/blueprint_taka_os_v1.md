# TAKA OS v1.0 — Blueprint de Conception Technique Complete

**Systeme d'Exploitation Agentic Open Source — Vertical Appels d'Offres**

| | |
|---|---|
| **Version** | 1.0 |
| **Date** | Mai 2026 |
| **Classification** | Document de conception — pre-developpement |
| **Statut** | GO — 5 validations CEO |
| **Licence** | MIT |

---

## Table des Matieres

- **Section 1 — Architecture & Modeles de Donnees**
  - Vue d'ensemble architecturale (3 couches MVP)
  - Schema de base de donnees SQLAlchemy 2.0 (8 tables completes)
  - Modeles Pydantic v2 (Base/Create/Update/Response/Filter)
  - Migrations Alembic
  - Configuration Pydantic-Settings

- **Section 2 — API REST & Securite**
  - Specification complete (28 endpoints)
  - Architecture JWT (auth dev + production)
  - RBAC (3 roles : viewer/manager/admin)
  - Multi-tenancy isolation
  - Audit trail append-only avec hash chain
  - Rate limiting & protection attaques

- **Section 3 — Agents TAKA & Systeme de Memoire**
  - Agent Sourcer (upload + parsing trigger)
  - Agent Qualifieur (scoring 80% regles / 20% LLM)
  - Agent Tracker (alertes deadlines)
  - Memoire pgvector (embeddings, HNSW, recherche similarite)
  - Capitalisation echecs/succes
  - Pipeline parsing PDF stratifie (4 niveaux)
  - Integration Mistral AI (circuit breaker, retry, templates Jinja2)

- **Section 4 — Frontend & DevOps**
  - Architecture React + Vite + Tailwind + Zustand
  - 9 pages avec composants detailles
  - State management (4 stores Zustand)
  - Docker Compose production (Nginx + SSL)
  - CI/CD GitHub Actions
  - Monitoring, backup, zero-downtime deploy

---

## Resume Executif

TAKA OS est un systeme d'exploitation agentic open source verticalise sur les Appels d'Offres publics et prives. Il aide les PME et ETI soumissionnaires a detecter, qualifier, suivre et capitaliser leurs candidatures aux marches publics.

### Architecture MVP (3 couches)

```
+--------------------------------------------------+
|  COUCHE 3 — AGENTS                               |
|  Sourcer | Qualifieur | Tracker                   |
+--------------------------------------------------+
|  COUCHE 2 — MEMOIRE                                |
|  PostgreSQL + pgvector (transactionnel + vectoriel) |
+--------------------------------------------------+
|  COUCHE 1 — SENSORIMOTRICE                        |
|  Upload PDF | Parsing PDF | Notifications          |
+--------------------------------------------------+
|  KERNEL                                            |
|  EventBus async | Config | Auth JWT | RBAC | Audit |
+--------------------------------------------------+
```

### Decisions architecturales cles

| Decision | Choix | Rejet |
|----------|-------|-------|
| Base de donnees | PostgreSQL + pgvector | Qdrant, Redis, Neo4j |
| Framework web | FastAPI + SQLAlchemy 2.0 async | Django, Flask |
| LLM | Mistral AI API (France) | Kimi API (Chine) |
| Client LLM | httpx + Jinja2 | LangChain, CrewAI |
| Auth | JWT maison (python-jose) | Auth0 |
| EventBus | asyncio in-memory | Redis, RabbitMQ |
| Frontend | React + Vite + Tailwind | Next.js |
| Parsing PDF | pypdf -> pdfplumber -> OCR | PyMuPDF (AGPL) |
| Python | 3.12+ (bloque <3.14) | 3.14 (NEXA-MIND) |
| Deploiement | Docker Compose 1 VPS | Kubernetes |

### 3 risques critiques adresses

1. **Parsing PDF** — Pipeline stratifie 4 niveaux, traitement asynchrone, saisie manuelle fallback
2. **Sessions async SQLAlchemy** — `expire_on_commit=False` obligatoire, pool_size=5
3. **Appels LLM** — Circuit breaker + retry exponentiel + fallback scoring regles

### Stack technique verrouillee

| Couche | Technologie |
|--------|-------------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 async |
| Base de donnees | PostgreSQL 15 + pgvector (HNSW) |
| LLM | Mistral AI API (httpx + Jinja2) |
| Auth | python-jose + passlib (JWT maison) |
| Parsing PDF | pypdf + pdfplumber + Tesseract OCR |
| Frontend | React 18 + TypeScript + Vite + Tailwind |
| State | Zustand + TanStack Query |
| UI | shadcn/ui + React Hook Form + Zod |
| DevOps | Docker Compose, Nginx, GitHub Actions |
| Infra | VPS Hetzner 6-8 EUR/mois |

### Roadmap developpement (4 semaines)

| Semaine | Focus | Livrable |
|---------|-------|----------|
| S1 | Fondation (Kernel + DB + Auth + API) | API fonctionnelle sur :8000 |
| S2 | Sensorimotrice + Memoire (Upload + Parsing + pgvector) | POST /parse-pdf retourne JSON |
| S3 | Agents Qualifieur + Pipeline Kanban | Scoring GO/NO-GO + Kanban UI |
| S4 | Tracker + SaaS Packaging (Auth prod + Docker + Tests) | v0.1 deployable en 5 min |

---

*Ce document est le resultat de 3 audits paralleles (concurrence, reglementaire, technique) croises avec l'historique complet du projet (NEXA-MIND, TAKA Advisory, iterations successives). Il constitue la reference unique pour la redaction des prompts de developpement Kimi Code.*

*Document produit par l'equipe CTO TAKA OS | Mai 2026*

---

# TAKA OS — Blueprint Technique

## Section 1 : Architecture & Modèles de Données

**Version** : 1.0.0-MVP  
**Date** : 2025-01-14  
**Statut** : SPECIFICATION  
**Stack** : Python 3.12+, FastAPI, SQLAlchemy 2.0 async, PostgreSQL 15+pgvector, Pydantic v2

---

## Table des matières

1. [Vue d'ensemble architecturale](#1-vue-densemble-architecturale)
2. [Schéma de base de données complet](#2-schéma-de-base-de-données-complet)
3. [Modèles Pydantic v2](#3-modèles-pydantic-v2)
4. [Migrations Alembic](#4-migrations-alembic)
5. [Configuration Pydantic-Settings](#5-configuration-pydantic-settings)

---

## 1. Vue d'ensemble architecturale

### 1.1 Principes directeurs

L'architecture de TAKA OS repose sur trois principes hérités directement des échecs de NEXA-MIND :

1. **Une seule source de vérité** : un seul fichier de modèles `app/models/ao.py`, une seule base PostgreSQL. Zero duplication de tables.
2. **Async partout** : SQLAlchemy 2.0 async avec `expire_on_commit=False` pour éliminer les lazy loading errors.
3. **Minimalisme opérationnel** : un seul conteneur de données (PostgreSQL + pgvector) pour rester déployable sur un VPS standard (2 vCPU / 4 Go RAM).

### 1.2 Les 3 couches MVP

TAKA OS adopte une architecture en trois couches inspirée des systèmes agentiques mais implémentée de manière pragmatique pour un MVP :

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           COUCHE 1 : SENSORIMOTRICE                              │
│  (Interface avec le monde extérieur — entrées/sorties)                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │  API Routes  │    │  Document    │    │  Webhooks    │    │  Fichiers    │   │
│  │  FastAPI     │    │  Parser      │    │  (futur)     │    │  Upload/DL   │   │
│  │              │    │  (PDF/DOCX)  │    │              │    │              │   │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘   │
│         │                   │                   │                   │            │
│         └───────────────────┴───────────────────┴───────────────────┘            │
│                                     │                                            │
│                              ┌──────┴──────┐                                    │
│                              │   Pydantic  │                                    │
│                              │  Validation │                                    │
│                              └──────┬──────┘                                    │
└─────────────────────────────────────┼───────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         COUCHE 2 : MÉMOIRE (PostgreSQL+pgvector)                │
│  (Persistance, structuration, recherche sémantique)                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                         DONNÉES STRUCTURÉES                               │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────────┐ │   │
│  │  │ tenants  │ │  users   │ │ tenders  │ │pipeline_ │ │qualification_   │ │   │
│  │  │          │ │          │ │          │ │ stages   │ │    rules        │ │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └─────────────────┘ │   │
│  │  ┌──────────┐ ┌──────────┐ ┌─────────────────────────────────────────────┐│   │
│  │  │tender_   │ │ audit_   │ │              memory_vectors                 ││   │
│  │  │documents │ │  logs    │ │          (pgvector 768 dims)                ││   │
│  │  └──────────┘ └──────────┘ └─────────────────────────────────────────────┘│   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                         MOTEUR SÉMANTIQUE                                 │   │
│  │  Recherche par similarité cosinus via pgvector                           │   │
│  │  Récupération épisodique : "AO similaires passés" → GO/NO-GO historique  │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         COUCHE 3 : AGENTS (Python pur)                          │
│  (Logique métier, scoring, qualification, pipeline)                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐              │
│  │ Agent Qualifier  │  │ Agent Scorer     │  │ Agent Memory     │              │
│  │                  │  │                  │  │                  │              │
│  │ • Parse DCE PDF  │  │ • Score critères │  │ • Index échecs   │              │
│  │ • Extraction     │  │   d'attribution  │  │ • Recherche      │              │
│  │   automatique    │  │ • Pondération    │  │   sémantique     │              │
│  │ • Règles GO/NO-GO│  │   configurable   │  │ • Récupération   │              │
│  │                  │  │ • Seuils         │  │   épisodique     │              │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘              │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                         ORCHESTRATEUR (synchrone)                         │   │
│  │  FastAPI background tasks / asyncio.gather pour enchaîner les agents     │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Description détaillée des couches

#### Couche 1 — Sensorimotrice

**Responsabilité** : Capturer les inputs du monde extérieur et valider leur forme avant transmission à la mémoire.

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| API HTTP | FastAPI + Uvicorn | Endpoints RESTful, auto-doc OpenAPI, validation Pydantic v2 |
| Parsing documents | `pymupdf` (PDF), `python-docx` (DOCX) | Extraction textuelle des DCE, détection de structure |
| Upload fichiers | FastAPI `UploadFile`, stockage disque | Réception des DCE, sauvegarde avec UUIDv4 |
| Validation | Pydantic v2 | Conformité des payloads, sanitization, typage strict |

**Contraintes MVP** :
- Pas de webhook externe (v2)
- Pas de scraping en temps réel (v2 — import manuel ou API Places/AchatPublic v2)
- Upload limité à 50 Mo par fichier, 5 fichiers par AO

#### Couche 2 — Mémoire

**Responsabilité** : Persister l'état du système avec cohérence transactionnelle et capacité de recherche sémantique.

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| Base relationnelle | PostgreSQL 15 | Données structurées avec intégrité référentielle |
| Vecteurs | pgvector extension | Stockage et recherche cosinus sur embeddings 768 dims |
| ORM | SQLAlchemy 2.0 async | Mapping objet-relationnel, requêtes type-safe |

**Architecture de ségrégation** : Multi-tenant par `tenant_id` sur chaque table. Pas de schéma PostgreSQL séparé par tenant (simplification MVP — les requêtes filtrent systématiquement sur `tenant_id`).

#### Couche 3 — Agents

**Responsabilité** : Implémenter la logique métier de qualification, scoring et capitalisation de la connaissance.

| Agent | Rôle | Déclencheur |
|-------|------|-------------|
| Agent Qualifier | Analyse un DCE et produit un verdict GO/NO-GO/MAYBE | Upload d'un document + clic "Qualifier" |
| Agent Scorer | Attribue un score numérique basé sur les critères d'attribution | Phase de qualification |
| Agent Memory | Indexe les résultats (succès/échec) pour récupération future | Changement de statut vers won/lost |

**Important** : Les agents sont des fonctions Python pures, pas des frameworks agentic. Aucun LangChain, aucun CrewAI. L'orchestration se fait via des appels de fonctions Python standard dans des background tasks FastAPI.

### 1.4 Flux de données complet — DCE uploadé à mémoire épisodique

```
Étape 1 : UPLOAD
────────────────
Utilisateur → POST /api/v1/tenders/{tender_id}/documents
                ↓
            FastAPI reçoit UploadFile
                ↓
            Validation : taille ≤ 50Mo, extension ∈ {pdf,docx,zip}
                ↓
            Sauvegarde disque : /data/uploads/{tenant_id}/{tender_id}/{uuid}.{ext}
                ↓
            Création ligne tender_documents (parsing_status = 'pending')
                ↓
            Réponse HTTP 201 au client (upload accepté)


Étape 2 : PARSING (async background task)
────────────────
BackgroundTask lancé par l'endpoint
                ↓
            tender_documents.parsing_status → 'processing'
                ↓
            ┌─────────────────────────────────────┐
            │  Si PDF  → pymupdf.extract_text()   │
            │  Si DOCX → python-docx paragraphs   │
            │  Si ZIP  → extraction récursive     │
            └─────────────────────────────────────┘
                ↓
            tender_documents.parsed_content = texte brut extrait
            tender_documents.metadata = {                 ← JSONB
                "pages": 47,
                "word_count": 15234,
                "detected_sections": ["CCAG-TCE", "CCTP", "DPGF", "RCR"],
                "lots_count": 3,
                "deadline_detected": "2025-03-15T12:00:00Z"
            }
                ↓
            tender_documents.parsing_status → 'completed' (ou 'failed')


Étape 3 : QUALIFICATION (déclenché manuellement par l'utilisateur)
────────────────
Utilisateur → POST /api/v1/tenders/{tender_id}/qualify
                ↓
            Lecture tender + parsed_content + qualification_rules
                ↓
            Agent Qualifier exécute les règles du tenant :
                • CPV dans whitelist ?
                • Montant dans [min_amount, max_amount] ?
                • Délai de préparation suffisant ?
                • Certifications requises disponibles ?
                ↓
            Calcul du score pondéré :
                tenders.qualification_score = Decimal('0.00') → '0.78'
                tenders.qualification_result = 'GO' | 'NO-GO' | 'MAYBE'
                ↓
            Si qualification_result = 'GO' :
                tenders.pipeline_stage_id → stage 'in_preparation'
            Si 'NO-GO' :
                tenders.pipeline_stage_id → stage 'abandoned'
            Si 'MAYBE' :
                reste sur stage actuel (souvent 'qualified')


Étape 4 : PIPELINE KANBAN (mouvements manuels ou automatiques)
────────────────
Utilisateur déplace la carte dans l'interface Kanban
                ↓
            PATCH /api/v1/tenders/{tender_id}
            body: { "pipeline_stage_id": "<new_stage_uuid>" }
                ↓
            Vérification : le stage existe et appartient au même tenant
                ↓
            Si new_stage.is_final = True (won/lost/abandoned) :
                → Déclenche Étape 5 : MÉMOIRE
            Sinon :
                → Simple mise à jour du stage


Étape 5 : MÉMOIRE ÉPISODIQUE (automatique sur état final)
────────────────
tenders.status → 'archived' + stage.is_final = True
                ↓
            Agent Memory indexe le résultat :
                ↓
            INSERT INTO memory_vectors (
                tenant_id,
                tender_id,
                content,                    ← résumé structuré de l'AO
                embedding,                  ← vector(768) via modèle d'embedding
                memory_type = 'episodic',
                tags = ARRAY['won|lost', cpv_code, buyer_name]
            )
                ↓
            Ce vecteur servira lors des futures qualifications :
                "Cet AO ressemble à un AO précédent qui a échoué sur le critère X"
```

### 1.5 Architecture des répertoires

```
taka-os/
├── alembic/
│   ├── env.py                          # Configuration async Alembic
│   ├── script.py.mako                  # Template de migration
│   └── versions/
│       └── 001_create_all_tables.py    # Migration initiale + seed data
├── app/
│   ├── __init__.py
│   ├── main.py                         # Point d'entrée FastAPI
│   ├── config.py                       # Pydantic-Settings (Section 5)
│   ├── database.py                     # Engine async, sessionmaker, get_db()
│   ├── models/
│   │   ├── __init__.py                 # Exporte tous les modèles
│   │   └── ao.py                       # SEUL fichier modèles (leçon NEXA-MIND)
│   ├── schemas/                        # Pydantic models (Section 3)
│   │   ├── __init__.py
│   │   ├── tenant.py
│   │   ├── user.py
│   │   ├── tender.py
│   │   ├── tender_document.py
│   │   ├── pipeline_stage.py
│   │   ├── qualification_rule.py
│   │   ├── memory_vector.py
│   │   └── audit_log.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── tenants.py
│   │   ├── users.py
│   │   ├── tenders.py
│   │   ├── documents.py
│   │   ├── pipeline.py
│   │   ├── qualification.py
│   │   └── memory.py
│   ├── services/                       # Logique métier (Agents)
│   │   ├── __init__.py
│   │   ├── qualifier.py                # Agent Qualifier
│   │   ├── scorer.py                   # Agent Scorer
│   │   ├── memory_indexer.py           # Agent Memory
│   │   └── document_parser.py          # Parsing PDF/DOCX
│   └── dependencies.py                 # Auth, permissions, get_current_user
├── data/
│   └── uploads/                        # Stockage fichiers DCE
├── tests/
├── pyproject.toml                      # Poetry, Python <3.14
├── docker-compose.yml                  # UN SEUL service : PostgreSQL 15
└── Dockerfile
```

---

## 2. Schéma de base de données complet

### 2.1 Fichier `app/database.py` — Configuration SQLAlchemy 2.0 async

```python
"""
Configuration de la base de données SQLAlchemy 2.0 async.

Leçons appliquées (NEXA-MIND) :
- expire_on_commit=False obligatoire pour éviter les lazy loading errors
- Une seule base PostgreSQL (pas de Redis, pas de Qdrant)
- Python <3.14 (3.14 incompatible avec SQLAlchemy 2.0.36)
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# ---------------------------------------------------------------------------
# Engine async PostgreSQL
# ---------------------------------------------------------------------------
# pool_pre_ping=True : vérifie la connexion avant utilisation (évite les
#                      connexions mortes après un idle timeout côté PG)
# pool_recycle=300   : recycle les connexions après 5 minutes d'inactivité
# echo=False         : logging SQL désactivé en production
# ---------------------------------------------------------------------------
async_engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.debug,
)

# ---------------------------------------------------------------------------
# Session factory async
# ---------------------------------------------------------------------------
# expire_on_commit=False : les objets restent attachés après commit.
#   Sans cela, tout accès à un attribut après commit déclenche un lazy load
#   qui échoue en async (DetachedInstanceError). C'est LA cause des erreurs
#   en cascade de NEXA-MIND.
# autocommit=False, autoflush=False : comportement transactionnel explicite
# ---------------------------------------------------------------------------
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# ---------------------------------------------------------------------------
# Base déclarative commune
# ---------------------------------------------------------------------------
# Tous les modèles héritent de cette base.
# Le paramètre future=True n'est plus nécessaire en SQLAlchemy 2.0.
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    """Base déclarative pour tous les modèles SQLAlchemy."""


# ---------------------------------------------------------------------------
# Dependency pour FastAPI
# ---------------------------------------------------------------------------
# Utilisé via Depends(get_db) dans les routers.
# Le générateur async garantit la fermeture de la session même en cas d'erreur.
# ---------------------------------------------------------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Fournit une session de base de données async par requête HTTP."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 2.2 Fichier `app/models/ao.py` — Tous les modèles SQLAlchemy 2.0

Ce fichier est le **seul et unique** fichier de modèles SQLAlchemy de TAKA OS. Cette unification est une décision architecturale critique issue de l'échec de NEXA-MIND où deux modules concurrents (legacy et nouveau) possédaient chacun leurs propres tables `tenders`, causant des conflits de synchronisation et des pertes de données.

#### 2.2.1 Imports et types communs

```python
"""
Modèles SQLAlchemy 2.0 — Fichier unique TAKA OS.

Tables définies :
    - tenants              : Organisation (multi-tenant)
    - users                : Utilisateurs authentifiés
    - pipeline_stages      : Étapes du pipeline Kanban
    - tenders              : Appels d'offres
    - tender_documents     : Documents joints aux AO
    - memory_vectors       : Mémoire épisodique et procédurale (pgvector)
    - audit_logs           : Traçabilité des actions
    - qualification_rules  : Règles de qualification GO/NO-GO

Style SQLAlchemy 2.0 : Mapped[Type] pour toutes les colonnes.
Leçon NEXA-MIND : un seul fichier de modèles, jamais de duplication.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pgvector.sqlalchemy import Vector  # pgvector extension
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
    inspect,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def utc_now() -> datetime:
    """Retourne le datetime UTC actuel. Utilisé comme default des colonnes."""
    return datetime.now(timezone.utc)


def generate_uuid() -> uuid.UUID:
    """Génère un UUIDv4."""
    return uuid.uuid4()


# ---------------------------------------------------------------------------
# Énumérations métier
# ---------------------------------------------------------------------------


class UserRole(str, Enum):
    """Rôles utilisateur dans un tenant."""

    ADMIN = "admin"       # Gestion complète : utilisateurs, règles, configuration
    MANAGER = "manager"   # Gestion des AO, qualification, pipeline
    VIEWER = "viewer"     # Lecture seule


class TenderStatus(str, Enum):
    """Statut de vie d'un appel d'offres."""

    DRAFT = "draft"         # Créé manuellement, pas encore actif
    ACTIVE = "active"       # En cours de traitement dans le pipeline
    ARCHIVED = "archived"   # Terminé (won/lost/abandoned/on_hold)


class QualificationResult(str, Enum):
    """Verdict de qualification d'un AO."""

    GO = "GO"           # L'entreprise peut/doit répondre
    NO_GO = "NO-GO"     # L'entreprise ne répond pas
    MAYBE = "MAYBE"     # Décision différée, analyse complémentaire nécessaire


class DocumentParsingStatus(str, Enum):
    """État du parsing d'un document uploadé."""

    PENDING = "pending"       # En attente de traitement
    PROCESSING = "processing" # Traitement en cours
    COMPLETED = "completed"   # Parsing terminé avec succès
    FAILED = "failed"         # Erreur lors du parsing


class MemoryType(str, Enum):
    """Type de mémoire stockée dans memory_vectors."""

    EPISODIC = "episodic"     # Souvenir d'un événement spécifique (AO won/lost)
    PROCEDURAL = "procedural" # Connaissance procédurale (patterns, règles apprises)


# ---------------------------------------------------------------------------
# 1. TENANTS — Organisation multi-tenant
# ---------------------------------------------------------------------------
# Justification : Chaque client (PME/ETI) a son propre tenant.
# Toutes les données sont isolées par tenant_id.
# Pas de schéma PostgreSQL séparé par tenant (simplification MVP).
# ---------------------------------------------------------------------------


class Tenant(Base):
    """Organisation cliente de TAKA OS. Unité d'isolation multi-tenant.

    Un tenant représente une entreprise soumissionnaire (PME/ETI) qui
    utilise TAKA OS pour gérer ses appels d'offres. Toutes les données
    (AO, documents, règles, mémoire) sont scopées par tenant_id.
    """

    __tablename__ = "tenants"
    __table_args__ = (
        # Index sur le slug pour les recherches rapides par identifiant textuel
        {"comment": "Organisation cliente — unité d'isolation multi-tenant"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=generate_uuid,
        comment="Identifiant unique du tenant (UUIDv4)",
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Nom de l'organisation (ex: 'BTP Dupont SAS')",
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Identifiant URL-safe (ex: 'btp-dupont-sas')",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Description optionnelle du tenant",
    )
    settings: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment=(
            "Configuration du tenant au format JSON. "
            "Ex: {'default_currency': 'EUR', 'notification_email': 'ao@btpdupont.fr', "
            "'theme_color': '#1a73e8'}"
        ),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        comment="Date de création du tenant",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
        comment="Date de dernière modification",
    )

    # Relationships
    users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="tenant",
        cascade="all, delete-orphan",
        lazy="selectin",
        comment="Utilisateurs appartenant à ce tenant",
    )
    pipeline_stages: Mapped[List["PipelineStage"]] = relationship(
        "PipelineStage",
        back_populates="tenant",
        cascade="all, delete-orphan",
        lazy="selectin",
        comment="Étapes de pipeline personnalisées du tenant",
    )
    tenders: Mapped[List["Tender"]] = relationship(
        "Tender",
        back_populates="tenant",
        cascade="all, delete-orphan",
        lazy="selectin",
        comment="Appels d'offres du tenant",
    )
    qualification_rules: Mapped[List["QualificationRule"]] = relationship(
        "QualificationRule",
        back_populates="tenant",
        cascade="all, delete-orphan",
        lazy="selectin",
        comment="Règles de qualification du tenant",
    )
    memory_vectors: Mapped[List["MemoryVector"]] = relationship(
        "MemoryVector",
        back_populates="tenant",
        cascade="all, delete-orphan",
        lazy="selectin",
        comment="Vecteurs de mémoire du tenant",
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="tenant",
        cascade="all, delete-orphan",
        lazy="selectin",
        comment="Logs d'audit du tenant",
    )


# ---------------------------------------------------------------------------
# 2. USERS — Utilisateurs authentifiés
# ---------------------------------------------------------------------------
# Justification : Authentification et autorisation par tenant.
# Un user appartient à un seul tenant (MVP). Pas de "cross-tenant" users.
# Le mot de passe est stocké hashé (bcrypt) — jamais en clair.
# ---------------------------------------------------------------------------


class User(Base):
    """Utilisateur authentifié de TAKA OS.

    Chaque utilisateur appartient à exactement un tenant. L'email est unique
    au sein d'un tenant (deux tenants différents peuvent avoir un user avec
    le même email). Le rôle détermine les permissions.
    """

    __tablename__ = "users"
    __table_args__ = (
        # Contrainte d'unicité : email unique PAR tenant
        UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
        {
            "comment": (
                "Utilisateurs authentifiés — appartiennent à un tenant, "
                "authentification par email/password"
            )
        },
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=generate_uuid,
        comment="Identifiant unique de l'utilisateur (UUIDv4)",
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "tenants.id",
            ondelete="CASCADE",
            name="fk_users_tenant_id",
        ),
        nullable=False,
        index=True,
        comment="Tenant auquel l'utilisateur appartient",
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Adresse email de l'utilisateur (identifiant de connexion)",
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Mot de passe hashé avec bcrypt (jamais en clair)",
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Nom complet de l'utilisateur (ex: 'Jean Dupont')",
    )
    role: Mapped[UserRole] = mapped_column(
        String(20),
        nullable=False,
        default=UserRole.VIEWER,
        comment="Rôle : admin (gestion complète), manager (AO), viewer (lecture)",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="False si le compte est désactivé (soft delete)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        comment="Date de création du compte",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
        comment="Date de dernière modification du profil",
    )

    # Relationships
    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
        back_populates="users",
        lazy="joined",
        comment="Tenant parent",
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="user",
        lazy="selectin",
        comment="Actions auditées de cet utilisateur",
    )


# ---------------------------------------------------------------------------
# 3. PIPELINE_STAGES — Étapes du pipeline Kanban
# ---------------------------------------------------------------------------
# Justification : Chaque tenant configure son propre pipeline Kanban.
# 8 stages par défaut sont créés lors de la création du tenant (seed).
# L'ordre d'affichage est contrôlé par display_order.
# is_final indique les étapes terminales (won, lost, abandoned, on_hold).
# ---------------------------------------------------------------------------


class PipelineStage(Base):
    """Étape du pipeline Kanban de suivi des appels d'offres.

    Chaque tenant a ses propres stages. Par défaut, 8 stages sont créés
    lors de l'initialisation du tenant. Les stages avec is_final=True
    représentent des états terminaux qui déclenchent l'archivage de l'AO
    et potentiellement l'indexation en mémoire épisodique.
    """

    __tablename__ = "pipeline_stages"
    __table_args__ = (
        # Slug unique PAR tenant (un tenant ne peut pas avoir deux stages "won")
        UniqueConstraint("tenant_id", "slug", name="uq_pipeline_stages_tenant_slug"),
        # Index composite pour l'affichage ordonné du Kanban
        {"comment": "Étapes du pipeline Kanban — personnalisables par tenant"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=generate_uuid,
        comment="Identifiant unique du stage (UUIDv4)",
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "tenants.id",
            ondelete="CASCADE",
            name="fk_pipeline_stages_tenant_id",
        ),
        nullable=False,
        index=True,
        comment="Tenant propriétaire du stage",
    )
    slug: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment=(
            "Identifiant machine-readable du stage : "
            "'detected', 'qualified', 'in_preparation', 'submitted', "
            "'won', 'lost', 'abandoned', 'on_hold'"
        ),
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Nom affiché (ex: 'En préparation', 'Soumis', 'Gagné')",
    )
    color: Mapped[str] = mapped_column(
        String(7),
        nullable=False,
        default="#6B7280",
        comment="Couleur hexadécimale pour l'affichage Kanban (ex: '#10B981' pour vert)",
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Ordre d'affichage de gauche à droite dans le Kanban (0, 1, 2, ...)",
    )
    is_final: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment=(
            "True si c'est un état terminal (won, lost, abandoned, on_hold). "
            "Un AO dans un stage final sera archivé."
        ),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        comment="Date de création du stage",
    )

    # Relationships
    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
        back_populates="pipeline_stages",
        lazy="joined",
        comment="Tenant parent",
    )
    tenders: Mapped[List["Tender"]] = relationship(
        "Tender",
        back_populates="pipeline_stage",
        lazy="selectin",
        comment="Appels d'offres actuellement dans ce stage",
    )


# ---------------------------------------------------------------------------
# 4. TENDERS — Appels d'offres
# ---------------------------------------------------------------------------
# Justification : Table centrale du système. Un AO est créé soit manuellement,
# soit par import (v2). Il traverse le pipeline Kanban jusqu'à un état final.
# Le champ metadata (JSONB) stocke les données hétérogènes : critères
# d'attribution pondérés, lots, contacts acheteur, etc.
# ---------------------------------------------------------------------------


class Tender(Base):
    """Appel d'offres (AO) — entité centrale de TAKA OS.

    Un Tender représente un appel d'offres détecté par l'utilisateur,
    importé via API ou créé manuellement. Il traverse les étapes du
    pipeline Kanban et subit une qualification GO/NO-GO/MAYBE.

    Le champ metadata (JSONB) stocke les données structurellement variables :
    critères d'attribution avec pondération, liste des lots, contacts, etc.
    """

    __tablename__ = "tenders"
    __table_args__ = (
        # Référence unique PAR tenant (une entreprise ne peut pas avoir deux AO
        # avec la même référence acheteur)
        UniqueConstraint("tenant_id", "reference", name="uq_tenders_tenant_reference"),
        # Index composite pour les requêtes de liste filtrées
        {
            "comment": (
                "Appels d'offres — entité centrale, multi-tenant, "
                "liée à un stage de pipeline"
            )
        },
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=generate_uuid,
        comment="Identifiant unique de l'AO (UUIDv4)",
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "tenants.id",
            ondelete="CASCADE",
            name="fk_tenders_tenant_id",
        ),
        nullable=False,
        index=True,
        comment="Tenant propriétaire de l'AO",
    )
    reference: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment=(
            "Référence de l'acheteur (ex: '2025-03542', 'MAPAMarch-2025-001'). "
            "Unique par tenant."
        ),
    )
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Intitulé de l'appel d'offres",
    )
    buyer_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Nom de l'acheteur public/privé (ex: 'Conseil Départemental du Rhône')",
    )
    cpv_code: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        index=True,
        comment="Code CPV (Common Procurement Vocabulary) — classification européenne",
    )
    cpv_description: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Libellé du code CPV",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Description textuelle complète de l'AO",
    )
    amount_estimated: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2),
        nullable=True,
        comment="Montant estimé de l'AO en EUR (TTC ou HT selon convention du tenant)",
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="EUR",
        comment="Devise ISO 4217 (EUR par défaut)",
    )
    deadline_submission: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        index=True,
        comment="Date limite de dépôt des candidatures/offres",
    )
    deadline_questions: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Date limite de pose des questions (clarifications)",
    )
    status: Mapped[TenderStatus] = mapped_column(
        String(20),
        nullable=False,
        default=TenderStatus.ACTIVE,
        index=True,
        comment="Statut de vie : draft, active, archived",
    )
    pipeline_stage_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey(
            "pipeline_stages.id",
            ondelete="SET NULL",
            name="fk_tenders_pipeline_stage_id",
        ),
        nullable=True,
        index=True,
        comment="Stage actuel dans le pipeline Kanban. NULL si non assigné.",
    )
    qualification_result: Mapped[Optional[QualificationResult]] = mapped_column(
        String(10),
        nullable=True,
        index=True,
        comment="Verdict de qualification : GO, NO-GO, MAYBE, ou NULL (non qualifié)",
    )
    qualification_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment=(
            "Score de qualification entre 0.00 et 1.00. "
            "Ex: 0.85 = 85% des critères favorables"
        ),
    )
    metadata: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment=(
            "Données structurées variables de l'AO. Ex: "
            "{'criteria': [{'name': 'Prix', 'weight': 0.4}, ...], "
            "'lots': [{'num': 1, 'desc': 'Gros oeuvre', 'amount': 500000}], "
            "'contacts': [{'name': 'M. Martin', 'email': 'ao@acheteur.fr'}], "
            "'procedure_type': 'Appel d offres ouvert', "
            "'simplified_procedure': false}"
        ),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        comment="Date de création de l'AO dans TAKA OS",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
        comment="Date de dernière modification",
    )

    # Relationships
    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
        back_populates="tenders",
        lazy="joined",
        comment="Tenant parent",
    )
    pipeline_stage: Mapped[Optional["PipelineStage"]] = relationship(
        "PipelineStage",
        back_populates="tenders",
        lazy="joined",
        comment="Stage actuel dans le pipeline",
    )
    documents: Mapped[List["TenderDocument"]] = relationship(
        "TenderDocument",
        back_populates="tender",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="TenderDocument.created_at",
        comment="Documents attachés à l'AO (DCE, CCTP, etc.)",
    )
    memory_vectors: Mapped[List["MemoryVector"]] = relationship(
        "MemoryVector",
        back_populates="tender",
        cascade="all, delete-orphan",
        lazy="selectin",
        comment="Vecteurs de mémoire liés à cet AO",
    )


# ---------------------------------------------------------------------------
# 5. TENDER_DOCUMENTS — Documents joints aux AO
# ---------------------------------------------------------------------------
# Justification : Un AO peut avoir plusieurs documents (DCE, CCTP, DPGF,
# RCR, etc.). Le contenu parsé est stocké en texte brut pour recherche
# full-text (v2) et analyse par les agents.
# ---------------------------------------------------------------------------


class TenderDocument(Base):
    """Document joint à un appel d'offres.

    Représente un fichier uploadé par l'utilisateur (PDF, DOCX, ZIP).
    Le fichier est stocké sur disque ; la BDD conserve les métadonnées
    et le contenu textuel extrait (parsed_content).
    """

    __tablename__ = "tender_documents"
    __table_args__ = (
        {
            "comment": (
                "Documents des AO — stockage métadonnées + contenu parsé, "
                "fichiers sur disque"
            )
        },
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=generate_uuid,
        comment="Identifiant unique du document (UUIDv4)",
    )
    tender_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "tenders.id",
            ondelete="CASCADE",
            name="fk_tender_documents_tender_id",
        ),
        nullable=False,
        index=True,
        comment="AO auquel ce document est rattaché",
    )
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Nom original du fichier (ex: 'DCE-Lot1-2025.pdf')",
    )
    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment=(
            "Chemin relatif de stockage sur disque : "
            "'{tenant_id}/{tender_id}/{uuid}.pdf'"
        ),
    )
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Taille du fichier en octets",
    )
    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Type MIME (ex: 'application/pdf', 'application/vnd.openxmlformats...')",
    )
    parsed_content: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Contenu textuel brut extrait du document (NULL si parsing en cours/échoué)",
    )
    parsing_status: Mapped[DocumentParsingStatus] = mapped_column(
        String(20),
        nullable=False,
        default=DocumentParsingStatus.PENDING,
        index=True,
        comment="État du parsing : pending, processing, completed, failed",
    )
    parsing_error: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Message d'erreur si parsing_status = 'failed'",
    )
    metadata: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment=(
            "Métadonnées extraites du document. Ex: "
            "{'pages': 47, 'word_count': 15234, "
            "'detected_sections': ['CCAG-TCE', 'CCTP', 'DPGF'], "
            "'lots_count': 3, 'deadline_detected': '2025-03-15T12:00:00Z', "
            "'ocr_used': false}"
        ),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        comment="Date d'upload du document",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
        comment="Date de dernière modification (mise à jour du parsing)",
    )

    # Relationships
    tender: Mapped["Tender"] = relationship(
        "Tender",
        back_populates="documents",
        lazy="joined",
        comment="AO parent",
    )


# ---------------------------------------------------------------------------
# 6. MEMORY_VECTORS — Mémoire épisodique et procédurale (pgvector)
# ---------------------------------------------------------------------------
# Justification : C'est la couche "mémoire" de l'OS agentic.
# Chaque vecteur représente un souvenir (épisodique : résultat d'un AO)
# ou une connaissance (procédurale : patterns appris).
# tender_id peut être NULL pour les mémoires procédurales générales.
# Dimension 768 : correspond au modèle d'embedding par défaut (sentence-transformers
# 'all-mpnet-base-v2' produit des vecteurs 768-dims).
# ---------------------------------------------------------------------------


class MemoryVector(Base):
        r"""Vecteur de mémoire sémantique — mémoire épisodique et procédurale.

        Cette table utilise l'extension pgvector pour stocker des embeddings
        de haute dimension et effectuer des recherches par similarité cosinus.

        Mémoire épisodique : un AO terminé (gagné ou perdu) est résumé et indexé.
        Lors d'une future qualification, on recherche : "Quels AO similaires avons-nous
        traités ? Quel en a été le résultat ?"

        Mémoire procédurale : connaissances générales sur les types d'AO,
        les critères de succès, les patterns. tender_id est NULL.
        """

        __tablename__ = "memory_vectors"
        __table_args__ = (
            # Index HNSW pour recherche par similarité rapide (pgvector)
            # La création de l'index se fait dans la migration Alembic via op.execute()
            {
                "comment": (
                    "Mémoire sémantique — embeddings pgvector 768 dims, "
                    "recherche par similarité cosinus"
                )
            },
        )

        id: Mapped[uuid.UUID] = mapped_column(
            primary_key=True,
            default=generate_uuid,
            comment="Identifiant unique du vecteur mémoire (UUIDv4)",
        )
        tenant_id: Mapped[uuid.UUID] = mapped_column(
            ForeignKey(
                "tenants.id",
                ondelete="CASCADE",
                name="fk_memory_vectors_tenant_id",
            ),
            nullable=False,
            index=True,
            comment="Tenant scopant ce vecteur mémoire",
        )
        tender_id: Mapped[Optional[uuid.UUID]] = mapped_column(
            ForeignKey(
                "tenders.id",
                ondelete="CASCADE",
                name="fk_memory_vectors_tender_id",
            ),
            nullable=True,
            index=True,
            comment=(
                "AO lié (pour mémoire épisodique). NULL pour mémoire procédurale "
                "ou connaissances générales."
            ),
        )
        content: Mapped[str] = mapped_column(
            Text,
            nullable=False,
            comment=(
                "Contenu textuel du souvenir (résumé structuré). "
                "Ex: 'AO gagné pour construction crèche à Lyon, "
                "montant 1.2M EUR, CPV 45210000. Facteurs clés : "
                "expérience similaire sur 3 projets, prix 5% sous moyenne.'"
            ),
        )
        embedding: Mapped[Vector] = mapped_column(
            Vector(768),
            nullable=False,
            comment="Vecteur d'embedding 768 dimensions (pgvector) — similarité cosinus",
        )
        memory_type: Mapped[MemoryType] = mapped_column(
            String(20),
            nullable=False,
            index=True,
            comment="Type : episodic (souvenir d'AO) ou procedural (connaissance)",
        )
        tags: Mapped[List[str]] = mapped_column(
            ARRAY(String),
            nullable=False,
            default=list,
            comment=(
                "Tags pour filtrage préalable. Ex: ARRAY['won', '45210000', "
                "'construction', 'lyon', 'public']"
            ),
        )
        created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            nullable=False,
            default=utc_now,
            comment="Date d'indexation du souvenir",
        )

        # Relationships
        tenant: Mapped["Tenant"] = relationship(
            "Tenant",
            back_populates="memory_vectors",
            lazy="joined",
            comment="Tenant parent",
        )
        tender: Mapped[Optional["Tender"]] = relationship(
            "Tender",
            back_populates="memory_vectors",
            lazy="joined",
            comment="AO lié (NULL pour mémoire procédurale)",
        )


# ---------------------------------------------------------------------------
# 7. AUDIT_LOGS — Traçabilité des actions
# ---------------------------------------------------------------------------
# Justification : Traçabilité complète des actions sur les données.
# Nécessaire pour la conformité et le debugging.
# user_id peut être NULL pour les actions système (automatisées).
# resource_id est en String et non UUID pour permettre l'audit de ressources
# qui pourraient avoir des identifiants non-UUID.
# ---------------------------------------------------------------------------


class AuditLog(Base):
    """Log d'audit — traçabilité de toutes les actions sur les données.

    Chaque action significative (création, modification, suppression,
    qualification, changement de stage) est enregistrée avec l'utilisateur,
    l'action, la ressource concernée et le payload complet avant/après.
    """

    __tablename__ = "audit_logs"
    __table_args__ = (
        # Index composite pour les requêtes de filtrage par type de ressource
        # et par date (tableau de bord d'audit)
        {"comment": "Logs d'audit — traçabilité complète des actions utilisateurs et système"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=generate_uuid,
        comment="Identifiant unique du log (UUIDv4)",
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "tenants.id",
            ondelete="CASCADE",
            name="fk_audit_logs_tenant_id",
        ),
        nullable=False,
        index=True,
        comment="Tenant concerné par l'action",
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
            name="fk_audit_logs_user_id",
        ),
        nullable=True,
        index=True,
        comment="Utilisateur ayant effectué l'action. NULL pour actions système.",
    )
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment=(
            "Type d'action : 'create', 'update', 'delete', 'qualify', "
            "'stage_change', 'document_upload', 'document_parse', "
            "'memory_index', 'login', 'login_failed'"
        ),
    )
    resource_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Type de ressource : 'tender', 'user', 'document', 'pipeline_stage', ...",
    )
    resource_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
        comment="Identifiant de la ressource (UUID sous forme de string)",
    )
    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment=(
            "Données complètes de l'action. Ex pour update : "
            "{'before': {'stage_id': 'abc', 'score': 0.5}, "
            "'after': {'stage_id': 'def', 'score': 0.8}}"
        ),
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="Adresse IP de l'utilisateur (IPv4 ou IPv6)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        index=True,
        comment="Date et heure de l'action",
    )

    # Relationships
    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
        back_populates="audit_logs",
        lazy="joined",
        comment="Tenant concerné",
    )
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="audit_logs",
        lazy="joined",
        comment="Utilisateur ayant effectué l'action",
    )


# ---------------------------------------------------------------------------
# 8. QUALIFICATION_RULES — Règles de qualification GO/NO-GO
# ---------------------------------------------------------------------------
# Justification : Chaque tenant configure ses propres règles de qualification.
# Ces règles sont appliquées par l'Agent Qualifier lors de l'analyse d'un AO.
# Le champ scoring_weights permet de pondérer différemment les critères
# selon la stratégie de l'entreprise.
# ---------------------------------------------------------------------------


class QualificationRule(Base):
    """Règle de qualification GO/NO-GO configurable par tenant.

    Une règle définit un ensemble de conditions qu'un AO doit satisfaire
    pour recevoir un verdict GO. L'Agent Qualifier évalue chaque règle
    et combine les résultats via les poids définis dans scoring_weights.

    Un tenant peut avoir plusieurs règles (par exemple : une pour les
        marchés publics de travaux, une pour les marchés de services).
    """

    __tablename__ = "qualification_rules"
    __table_args__ = (
        {
            "comment": (
                "Règles de qualification GO/NO-GO — configurables par tenant, "
                "appliquées par l'Agent Qualifier"
            )
        },
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=generate_uuid,
        comment="Identifiant unique de la règle (UUIDv4)",
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "tenants.id",
            ondelete="CASCADE",
            name="fk_qualification_rules_tenant_id",
        ),
        nullable=False,
        index=True,
        comment="Tenant propriétaire de la règle",
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Nom descriptif de la règle (ex: 'Travaux de construction > 500k EUR')",
    )
    cpv_whitelist: Mapped[List[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
        comment=(
            "Liste des codes CPV acceptés (préfixes supportés). "
            "Ex: ARRAY['45', '71'] accepte tous les CPV commençant par 45 ou 71. "
            "Tableau vide = tous les CPV acceptés."
        ),
    )
    min_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2),
        nullable=True,
        comment="Montant minimum de l'AO pour que la règle s'applique (NULL = pas de minimum)",
    )
    max_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2),
        nullable=True,
        comment="Montant maximum de l'AO pour que la règle s'applique (NULL = pas de maximum)",
    )
    min_preparation_days: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment=(
            "Nombre minimum de jours entre aujourd'hui et la deadline de soumission "
            "pour que la règle s'applique. NULL = pas de contrainte."
        ),
    )
    required_certifications: Mapped[List[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
        comment=(
            "Certifications requises pour répondre. "
            "Ex: ARRAY['ISO 9001', 'Qualibat RGE']. "
            "Tableau vide = pas de certification requise."
        ),
    )
    scoring_weights: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment=(
            "Pondération des critères de scoring. Ex: "
            "{'cpv_match': 0.20, 'amount_range': 0.25, 'preparation_time': 0.20, "
            "'certifications': 0.15, 'buyer_history': 0.10, 'deadline_feasible': 0.10}"
        ),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        comment="Date de création de la règle",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
        comment="Date de dernière modification",
    )

    # Relationships
    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
        back_populates="qualification_rules",
        lazy="joined",
        comment="Tenant parent",
    )
```

### 2.3 Récapitulatif des index et contraintes

| Table | Index | Colonnes | Type | Justification |
|-------|-------|----------|------|---------------|
| `tenants` | `ix_tenants_slug` | `slug` | B-tree | Recherche par identifiant URL |
| `users` | `ix_users_tenant_id` | `tenant_id` | B-tree | Filtrage multi-tenant |
| `users` | `uq_users_tenant_email` | `tenant_id, email` | Unique | Unicité email par tenant |
| `pipeline_stages` | `ix_pipeline_stages_tenant_id` | `tenant_id` | B-tree | Filtrage multi-tenant |
| `pipeline_stages` | `uq_pipeline_stages_tenant_slug` | `tenant_id, slug` | Unique | Unicité du slug par tenant |
| `tenders` | `ix_tenders_tenant_id` | `tenant_id` | B-tree | Filtrage multi-tenant |
| `tenders` | `ix_tenders_reference` | `reference` | B-tree | Recherche par référence |
| `tenders` | `uq_tenders_tenant_reference` | `tenant_id, reference` | Unique | Unicité référence par tenant |
| `tenders` | `ix_tenders_cpv_code` | `cpv_code` | B-tree | Filtrage par code CPV |
| `tenders` | `ix_tenders_status` | `status` | B-tree | Filtrage par statut |
| `tenders` | `ix_tenders_pipeline_stage_id` | `pipeline_stage_id` | B-tree | Jointure avec pipeline |
| `tenders` | `ix_tenders_qualification_result` | `qualification_result` | B-tree | Filtrage GO/NO-GO/MAYBE |
| `tenders` | `ix_tenders_deadline_submission` | `deadline_submission` | B-tree | Tri par date limite |
| `tender_documents` | `ix_tender_documents_tender_id` | `tender_id` | B-tree | Jointure avec tender |
| `tender_documents` | `ix_tender_documents_parsing_status` | `parsing_status` | B-tree | Filtrage par état de parsing |
| `memory_vectors` | `ix_memory_vectors_tenant_id` | `tenant_id` | B-tree | Filtrage multi-tenant |
| `memory_vectors` | `ix_memory_vectors_tender_id` | `tender_id` | B-tree | Jointure avec tender |
| `memory_vectors` | `ix_memory_vectors_memory_type` | `memory_type` | B-tree | Filtrage épisodique/procédural |
| `memory_vectors` | `hnsw_memory_vectors_embedding` | `embedding` | HNSW (pgvector) | Recherche par similarité cosinus |
| `audit_logs` | `ix_audit_logs_tenant_id` | `tenant_id` | B-tree | Filtrage multi-tenant |
| `audit_logs` | `ix_audit_logs_user_id` | `user_id` | B-tree | Filtrage par utilisateur |
| `audit_logs` | `ix_audit_logs_action` | `action` | B-tree | Filtrage par type d'action |
| `audit_logs` | `ix_audit_logs_resource_type` | `resource_type` | B-tree | Filtrage par type de ressource |
| `audit_logs` | `ix_audit_logs_resource_id` | `resource_id` | B-tree | Recherche par ressource |
| `audit_logs` | `ix_audit_logs_created_at` | `created_at` | B-tree | Tri chronologique |
| `qualification_rules` | `ix_qualification_rules_tenant_id` | `tenant_id` | B-tree | Filtrage multi-tenant |

### 2.4 Récapitulatif des clés étrangères et ondelete

| Colonne | Table cible | `ondelete` | Justification |
|---------|-------------|------------|---------------|
| `users.tenant_id` | `tenants.id` | `CASCADE` | Suppression du tenant = suppression de tous ses users |
| `pipeline_stages.tenant_id` | `tenants.id` | `CASCADE` | Suppression du tenant = suppression des stages |
| `tenders.tenant_id` | `tenants.id` | `CASCADE` | Suppression du tenant = suppression de tous ses AO |
| `tenders.pipeline_stage_id` | `pipeline_stages.id` | `SET NULL` | Suppression d'un stage : les AO perdent leur stage mais ne sont pas supprimés |
| `tender_documents.tender_id` | `tenders.id` | `CASCADE` | Suppression de l'AO = suppression de ses documents |
| `memory_vectors.tenant_id` | `tenants.id` | `CASCADE` | Suppression du tenant = suppression de sa mémoire |
| `memory_vectors.tender_id` | `tenders.id` | `CASCADE` | Suppression de l'AO = suppression de ses vecteurs mémoire |
| `audit_logs.tenant_id` | `tenants.id` | `CASCADE` | Suppression du tenant = suppression de ses logs |
| `audit_logs.user_id` | `users.id` | `SET NULL` | Suppression d'un user : ses logs sont conservés (anonymisés) |
| `qualification_rules.tenant_id` | `tenants.id` | `CASCADE` | Suppression du tenant = suppression de ses règles |

### 2.5 Extension pgvector — Configuration

```python
# Fichier : app/database.py (complément pour pgvector)

"""
Configuration de l'extension pgvector.

Doit être exécuté une seule fois lors de l'initialisation de la base :
    CREATE EXTENSION IF NOT EXISTS vector;

Dimension 768 : correspond au modèle d'embedding par défaut.
Le modèle peut être configuré via settings.embedding_model.
Si le modèle change, la dimension doit être ajustée ici et dans
la migration Alembic.
"""

# Dimension de l'embedding — cohérente avec le modèle sentence-transformers
EMBEDDING_DIMENSION = 768

# Seuil de similarité cosinus pour la recherche de mémoire épisodique
# Un seuil de 0.75 signifie que seuls les résultats à 75%+ de similarité
# sont considérés comme pertinents.
MEMORY_SIMILARITY_THRESHOLD = 0.75

# Nombre maximum de souvenirs récupérés lors d'une recherche épisodique
MEMORY_TOP_K = 5
```

---

## 3. Modèles Pydantic v2

### 3.1 Architecture des schémas

Pour chaque entité, cinq modèles Pydantic sont définis :

| Modèle | Suffixe | Rôle | Champs `id` | Champs `created_at` |
|--------|---------|------|-------------|---------------------|
| Base | `*Base` | Champs communs validables | Non | Non |
| Create | `*Create` | Création via API | Exclu | Exclu |
| Update | `*Update` | Mise à jour partielle (PATCH) | Exclu | Exclu, tous les champs `Optional` |
| Response | `*Response` | Réponse API complète | Inclus | Inclus |
| Filter | `*Filter` | Requêtes de liste avec critères (query params) | — | — |

### 3.2 Base commune

```python
"""
Schémas Pydantic v2 — Base commune.

Tous les modèles Response incluent ConfigDict(from_attributes=True)
pour permettre la conversion automatique depuis les objets SQLAlchemy.

Le champ tenant_id est injecté par les dépendances d'authentification
(get_current_user) et n'est jamais présent dans les payloads client.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TimestampMixin(BaseModel):
    """Mixin pour les champs de timestamp présents dans tous les Response models."""

    created_at: datetime = Field(
        ...,  # requis
        description="Date de création de l'enregistrement",
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Date de dernière modification (NULL si jamais modifié)",
    )


class UUIDMixin(BaseModel):
    """Mixin pour l'identifiant UUID présent dans tous les Response models."""

    id: UUID = Field(
        ...,
        description="Identifiant unique (UUIDv4)",
    )


class TenantScopedModel(BaseModel):
    """Base pour les modèles liés à un tenant. Le tenant_id est injecté côté serveur."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )
```

### 3.3 Schémas Tenant

```python
"""Schémas Pydantic pour l'entité Tenant."""


class TenantBase(BaseModel):
    """Champs communs à tous les modèles Tenant."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Nom de l'organisation",
        examples=["BTP Dupont SAS"],
    )
    slug: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="Identifiant URL-safe (minuscules, chiffres, tirets)",
        examples=["btp-dupont-sas"],
    )
    description: Optional[str] = Field(
        None,
        max_length=5000,
        description="Description optionnelle du tenant",
    )
    settings: dict = Field(
        default_factory=dict,
        description="Configuration JSON du tenant",
    )


class TenantCreate(TenantBase):
    """Payload pour la création d'un tenant. Identique à TenantBase."""

    pass


class TenantUpdate(BaseModel):
    """Payload pour la mise à jour partielle d'un tenant (PATCH).

    Tous les champs sont optionnels pour permettre les mises à jour partielles.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Nom de l'organisation",
    )
    slug: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="Identifiant URL-safe",
    )
    description: Optional[str] = Field(
        None,
        max_length=5000,
    )
    settings: Optional[dict] = Field(
        None,
        description="Configuration JSON (fusion profonde recommandée côté serveur)",
    )


class TenantResponse(UUIDMixin, TenantBase):
    """Réponse API complète pour un tenant."""

    model_config = ConfigDict(from_attributes=True)

    created_at: datetime = Field(..., description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de modification")


class TenantFilter(BaseModel):
    """Filtres pour la liste des tenants (réservé super-admin)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    search: Optional[str] = Field(
        None,
        description="Recherche textuelle sur name et slug",
    )
    is_active: Optional[bool] = Field(
        None,
        description="Filtrer par statut actif",
    )
    order_by: str = Field(
        "created_at",
        description="Champ de tri",
        pattern=r"^(created_at|updated_at|name|slug)$",
    )
    order: str = Field(
        "desc",
        description="Direction du tri",
        pattern=r"^(asc|desc)$",
    )
    page: int = Field(1, ge=1, description="Numéro de page")
    page_size: int = Field(20, ge=1, le=100, description="Taille de page")
```

### 3.4 Schémas User

```python
"""Schémas Pydantic pour l'entité User."""


class UserBase(BaseModel):
    """Champs communs à tous les modèles User."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: str = Field(
        ...,
        min_length=5,
        max_length=255,
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        description="Adresse email de l'utilisateur",
        examples=["jean.dupont@btpdupont.fr"],
    )
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Nom complet",
        examples=["Jean Dupont"],
    )
    role: str = Field(
        ...,
        pattern=r"^(admin|manager|viewer)$",
        description="Rôle : admin, manager, ou viewer",
    )
    is_active: bool = Field(
        True,
        description="Compte actif (False = désactivé)",
    )


class UserCreate(UserBase):
    """Payload pour la création d'un utilisateur.

    Le mot de passe est requis à la création. Il sera hashé côté serveur
    avant stockage.
    """

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Mot de passe en clair (sera hashé côté serveur)",
    )


class UserUpdate(BaseModel):
    """Payload pour la mise à jour partielle d'un utilisateur (PATCH)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: Optional[str] = Field(
        None,
        min_length=5,
        max_length=255,
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    )
    full_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
    )
    role: Optional[str] = Field(
        None,
        pattern=r"^(admin|manager|viewer)$",
    )
    is_active: Optional[bool] = Field(None)
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=128,
        description="Nouveau mot de passe (sera hashé côté serveur)",
    )


class UserResponse(UUIDMixin, UserBase):
    """Réponse API complète pour un utilisateur.

    Le hashed_password est EXCLU de la réponse pour des raisons de sécurité.
    """

    model_config = ConfigDict(from_attributes=True)

    tenant_id: UUID = Field(..., description="ID du tenant parent")
    created_at: datetime = Field(..., description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de modification")


class UserMeResponse(UserResponse):
    """Réponse pour l'endpoint /users/me (profil de l'utilisateur connecté)."""

    tenant_name: str = Field(..., description="Nom du tenant")
    tenant_slug: str = Field(..., description="Slug du tenant")


class UserFilter(BaseModel):
    """Filtres pour la liste des utilisateurs d'un tenant."""

    model_config = ConfigDict(str_strip_whitespace=True)

    search: Optional[str] = Field(
        None,
        description="Recherche textuelle sur email et full_name",
    )
    role: Optional[str] = Field(
        None,
        pattern=r"^(admin|manager|viewer)$",
    )
    is_active: Optional[bool] = Field(None)
    order_by: str = Field(
        "created_at",
        pattern=r"^(created_at|updated_at|full_name|email|role)$",
    )
    order: str = Field("desc", pattern=r"^(asc|desc)$")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class UserLoginRequest(BaseModel):
    """Payload pour l'authentification."""

    email: str = Field(..., description="Email de l'utilisateur")
    password: str = Field(..., description="Mot de passe")


class TokenResponse(BaseModel):
    """Réponse avec le token JWT après authentification."""

    access_token: str = Field(..., description="Token JWT d'accès")
    token_type: str = Field("bearer", description="Type de token")
    expires_in: int = Field(..., description="Durée de validité en secondes")
    user: UserResponse = Field(..., description="Profil de l'utilisateur")
```

### 3.5 Schémas PipelineStage

```python
"""Schémas Pydantic pour l'entité PipelineStage."""


class PipelineStageBase(BaseModel):
    """Champs communs à tous les modèles PipelineStage."""

    model_config = ConfigDict(str_strip_whitespace=True)

    slug: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern=r"^[a-z0-9_]+$",
        description="Identifiant machine-readable (ex: 'in_preparation')",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nom affiché (ex: 'En préparation')",
    )
    color: str = Field(
        ...,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Couleur hexadécimale (ex: '#10B981')",
    )
    display_order: int = Field(
        ...,
        ge=0,
        description="Ordre d'affichage (0 = première colonne)",
    )
    is_final: bool = Field(
        False,
        description="État terminal (won, lost, abandoned, on_hold)",
    )


class PipelineStageCreate(PipelineStageBase):
    """Payload pour la création d'un stage de pipeline."""

    pass


class PipelineStageUpdate(BaseModel):
    """Payload pour la mise à jour partielle d'un stage (PATCH)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    display_order: Optional[int] = Field(None, ge=0)
    is_final: Optional[bool] = Field(None)
    # Le slug n'est pas modifiable (identifiant stable pour les règles métier)


class PipelineStageResponse(UUIDMixin, PipelineStageBase):
    """Réponse API complète pour un stage de pipeline."""

    model_config = ConfigDict(from_attributes=True)

    tenant_id: UUID = Field(..., description="ID du tenant parent")
    created_at: datetime = Field(..., description="Date de création")
    tender_count: int = Field(
        0,
        description="Nombre d'AO dans ce stage (calculé côté serveur)",
    )


class PipelineStageReorderRequest(BaseModel):
    """Payload pour réordonner les stages du pipeline."""

    stage_ids: List[UUID] = Field(
        ...,
        min_length=2,
        description="Liste ordonnée des IDs de stages",
    )


class PipelineStageFilter(BaseModel):
    """Filtres pour la liste des stages (utilisé principalement pour l'ordre)."""

    include_tender_count: bool = Field(
        False,
        description="Inclure le compte d'AO par stage",
    )
```

### 3.6 Schémas Tender

```python
"""Schémas Pydantic pour l'entité Tender (Appel d'Offres)."""


class TenderBase(BaseModel):
    """Champs communs à tous les modèles Tender."""

    model_config = ConfigDict(str_strip_whitespace=True)

    reference: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Référence de l'acheteur",
        examples=["2025-03542"],
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Intitulé de l'appel d'offres",
    )
    buyer_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Nom de l'acheteur",
    )
    cpv_code: Optional[str] = Field(
        None,
        max_length=20,
        description="Code CPV",
    )
    cpv_description: Optional[str] = Field(
        None,
        max_length=500,
        description="Libellé CPV",
    )
    description: Optional[str] = Field(
        None,
        description="Description complète de l'AO",
    )
    amount_estimated: Optional[Decimal] = Field(
        None,
        ge=Decimal("0"),
        max_digits=15,
        decimal_places=2,
        description="Montant estimé",
    )
    currency: str = Field(
        "EUR",
        max_length=3,
        description="Devise ISO 4217",
    )
    deadline_submission: Optional[date] = Field(
        None,
        description="Date limite de dépôt",
    )
    deadline_questions: Optional[date] = Field(
        None,
        description="Date limite de questions",
    )
    status: str = Field(
        "active",
        pattern=r"^(draft|active|archived)$",
        description="Statut de vie",
    )
    pipeline_stage_id: Optional[UUID] = Field(
        None,
        description="ID du stage actuel dans le pipeline",
    )
    qualification_result: Optional[str] = Field(
        None,
        pattern=r"^(GO|NO-GO|MAYBE)$",
        description="Verdict de qualification",
    )
    qualification_score: Optional[Decimal] = Field(
        None,
        ge=Decimal("0.00"),
        le=Decimal("1.00"),
        max_digits=5,
        decimal_places=2,
        description="Score de qualification (0.00 à 1.00)",
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Données structurées variables (critères, lots, contacts)",
    )

    @field_validator("deadline_questions")
    @classmethod
    def deadline_questions_before_submission(
        cls, v: Optional[date], info
    ) -> Optional[date]:
        """La deadline de questions doit être antérieure à celle de soumission."""
        if v is None:
            return v
        # Accès aux valeurs déjà validées
        data = info.data
        submission = data.get("deadline_submission")
        if submission and v > submission:
            raise ValueError(
                "deadline_questions doit être antérieure à deadline_submission"
            )
        return v


class TenderCreate(TenderBase):
    """Payload pour la création d'un AO."""

    # Lors de la création, on peut optionnellement fournir un stage initial
    # Par défaut, l'AO est créé sans stage (détecté mais non qualifié)
    pass


class TenderUpdate(BaseModel):
    """Payload pour la mise à jour partielle d'un AO (PATCH)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    reference: Optional[str] = Field(None, min_length=1, max_length=255)
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    buyer_name: Optional[str] = Field(None, min_length=1, max_length=255)
    cpv_code: Optional[str] = Field(None, max_length=20)
    cpv_description: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None)
    amount_estimated: Optional[Decimal] = Field(
        None, ge=Decimal("0"), max_digits=15, decimal_places=2
    )
    currency: Optional[str] = Field(None, max_length=3)
    deadline_submission: Optional[date] = Field(None)
    deadline_questions: Optional[date] = Field(None)
    status: Optional[str] = Field(None, pattern=r"^(draft|active|archived)$")
    pipeline_stage_id: Optional[UUID] = Field(None)
    qualification_result: Optional[str] = Field(
        None, pattern=r"^(GO|NO-GO|MAYBE)$"
    )
    qualification_score: Optional[Decimal] = Field(
        None, ge=Decimal("0.00"), le=Decimal("1.00"), max_digits=5, decimal_places=2
    )
    metadata: Optional[dict] = Field(None)

    @field_validator("deadline_questions")
    @classmethod
    def validate_deadline_questions(cls, v: Optional[date], info) -> Optional[date]:
        """Validation cohérence des dates."""
        if v is None:
            return v
        data = info.data
        submission = data.get("deadline_submission")
        if submission and v > submission:
            raise ValueError("deadline_questions doit etre anterieure a deadline_submission")
        return v


class TenderResponse(UUIDMixin, TenderBase):
    """Réponse API complète pour un appel d'offres."""

    model_config = ConfigDict(from_attributes=True)

    tenant_id: UUID = Field(..., description="ID du tenant")
    pipeline_stage: Optional[PipelineStageResponse] = Field(
        None,
        description="Stage actuel (expandable)",
    )
    document_count: int = Field(
        0,
        description="Nombre de documents attachés",
    )
    parsed_document_count: int = Field(
        0,
        description="Nombre de documents parsés avec succès",
    )
    created_at: datetime = Field(..., description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de modification")


class TenderMoveRequest(BaseModel):
    """Payload pour déplacer un AO vers un autre stage du pipeline."""

    pipeline_stage_id: UUID = Field(..., description="ID du stage destination")
    note: Optional[str] = Field(
        None,
        max_length=1000,
        description="Note optionnelle justifiant le mouvement",
    )


class TenderQualifyRequest(BaseModel):
    """Payload pour déclencher la qualification d'un AO."""

    rule_id: Optional[UUID] = Field(
        None,
        description="ID de la règle de qualification à appliquer (NULL = toutes les règles actives)",
    )
    force_requalify: bool = Field(
        False,
        description="Forcer la re-qualification même si déjà qualifié",
    )


class TenderQualifyResponse(BaseModel):
    """Réponse après qualification d'un AO."""

    tender_id: UUID = Field(..., description="ID de l'AO qualifié")
    qualification_result: str = Field(..., description="Verdict : GO, NO-GO, MAYBE")
    qualification_score: Decimal = Field(..., description="Score numérique")
    stage_changed: bool = Field(..., description="Le stage a-t-il été mis à jour ?")
    new_stage_id: Optional[UUID] = Field(None, description="Nouveau stage si changé")
    applied_rules: List[dict] = Field(
        default_factory=list,
        description="Règles appliquées avec leur score détaillé",
    )
    memory_matches: List[dict] = Field(
        default_factory=list,
        description="Souvenirs épisodiques similaires trouvés",
    )


class TenderFilter(BaseModel):
    """Filtres pour la liste des appels d'offres (query params)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    # Filtres textuels
    search: Optional[str] = Field(
        None,
        description="Recherche textuelle sur title, buyer_name, reference",
    )

    # Filtres par statut et qualification
    status: Optional[str] = Field(
        None,
        pattern=r"^(draft|active|archived)$",
    )
    qualification_result: Optional[str] = Field(
        None,
        pattern=r"^(GO|NO-GO|MAYBE)$",
    )

    # Filtres par pipeline
    pipeline_stage_id: Optional[UUID] = Field(None)
    exclude_final_stages: bool = Field(
        False,
        description="Exclure les AO dans des stages terminaux",
    )

    # Filtres par CPV
    cpv_code: Optional[str] = Field(None, max_length=20)
    cpv_prefix: Optional[str] = Field(
        None,
        max_length=10,
        description="Préfixe CPV pour filtrage par catégorie (ex: '45' pour travaux)",
    )

    # Filtres par montant
    min_amount: Optional[Decimal] = Field(None, ge=Decimal("0"))
    max_amount: Optional[Decimal] = Field(None, ge=Decimal("0"))

    # Filtres par date
    deadline_from: Optional[date] = Field(
        None,
        description="Date limite de soumission >= cette date",
    )
    deadline_to: Optional[date] = Field(
        None,
        description="Date limite de soumission <= cette date",
    )

    # Tri
    order_by: str = Field(
        "created_at",
        pattern=r"^(created_at|updated_at|deadline_submission|amount_estimated|qualification_score|title|buyer_name)$",
    )
    order: str = Field("desc", pattern=r"^(asc|desc)$")

    # Pagination
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

    @field_validator("deadline_to")
    @classmethod
    def deadline_to_after_from(cls, v: Optional[date], info) -> Optional[date]:
        """deadline_to doit être >= deadline_from."""
        if v is None:
            return v
        data = info.data
        deadline_from = data.get("deadline_from")
        if deadline_from and v < deadline_from:
            raise ValueError("deadline_to doit etre posterieure ou egale a deadline_from")
        return v
```

### 3.7 Schémas TenderDocument

```python
"""Schémas Pydantic pour l'entité TenderDocument."""


class TenderDocumentBase(BaseModel):
    """Champs communs à tous les modèles TenderDocument."""

    filename: str = Field(
        ...,
        max_length=255,
        description="Nom original du fichier",
    )
    file_size: int = Field(
        ...,
        ge=0,
        description="Taille en octets",
    )
    mime_type: str = Field(
        ...,
        max_length=100,
        description="Type MIME",
    )
    parsing_status: str = Field(
        "pending",
        pattern=r"^(pending|processing|completed|failed)$",
    )
    metadata: dict = Field(default_factory=dict)


class TenderDocumentCreate(TenderDocumentBase):
    """Payload pour la création d'un document (côté serveur après upload).

    Les champs file_path, parsed_content, parsing_error sont gérés côté serveur.
    """

    tender_id: UUID = Field(..., description="ID de l'AO parent")
    file_path: str = Field(..., description="Chemin de stockage sur disque")


class TenderDocumentUpdate(BaseModel):
    """Payload pour la mise à jour d'un document (principalement le statut de parsing)."""

    parsing_status: Optional[str] = Field(
        None,
        pattern=r"^(pending|processing|completed|failed)$",
    )
    parsed_content: Optional[str] = Field(None)
    parsing_error: Optional[str] = Field(None)
    metadata: Optional[dict] = Field(None)


class TenderDocumentResponse(UUIDMixin, TenderDocumentBase):
    """Réponse API complète pour un document."""

    model_config = ConfigDict(from_attributes=True)

    tender_id: UUID = Field(..., description="ID de l'AO parent")
    file_path: str = Field(..., description="Chemin de stockage")
    parsed_content: Optional[str] = Field(
        None,
        description="Contenu textuel extrait (NULL si non parsé)",
    )
    parsing_error: Optional[str] = Field(
        None,
        description="Message d'erreur si parsing échoué",
    )
    created_at: datetime = Field(...)
    updated_at: Optional[datetime] = Field(None)


class TenderDocumentFilter(BaseModel):
    """Filtres pour la liste des documents d'un AO."""

    tender_id: Optional[UUID] = Field(None)
    parsing_status: Optional[str] = Field(
        None,
        pattern=r"^(pending|processing|completed|failed)$",
    )
    order_by: str = Field("created_at", pattern=r"^(created_at|filename|file_size)$")
    order: str = Field("desc", pattern=r"^(asc|desc)$")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class DocumentUploadResponse(BaseModel):
    """Réponse après upload d'un ou plusieurs documents."""

    uploaded: List[TenderDocumentResponse] = Field(default_factory=list)
    errors: List[dict] = Field(
        default_factory=list,
        description="Erreurs par fichier : [{filename, reason}]",
    )
```

### 3.8 Schémas MemoryVector

```python
"""Schémas Pydantic pour l'entité MemoryVector."""

from typing import Any


class MemoryVectorBase(BaseModel):
    """Champs communs à tous les modèles MemoryVector."""

    content: str = Field(
        ...,
        min_length=10,
        description="Contenu textuel du souvenir",
    )
    memory_type: str = Field(
        ...,
        pattern=r"^(episodic|procedural)$",
        description="Type de mémoire",
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Tags pour filtrage",
    )


class MemoryVectorCreate(MemoryVectorBase):
    """Payload pour la création d'un vecteur mémoire.

    L'embedding est calculé côté serveur par l'Agent Memory, pas fourni
    par le client.
    """

    tender_id: Optional[UUID] = Field(None, description="AO lié (NULL = procédural)")


class MemoryVectorUpdate(BaseModel):
    """Payload pour la mise à jour d'un vecteur mémoire."""

    content: Optional[str] = Field(None, min_length=10)
    tags: Optional[List[str]] = Field(None)
    # L'embedding et le memory_type ne sont pas modifiables


class MemoryVectorResponse(UUIDMixin, MemoryVectorBase):
    """Réponse API complète pour un vecteur mémoire."""

    model_config = ConfigDict(from_attributes=True)

    tenant_id: UUID = Field(...)
    tender_id: Optional[UUID] = Field(None)
    created_at: datetime = Field(...)
    # L'embedding n'est pas inclus dans la réponse par défaut (trop volumineux)
    # Il peut être récupéré via un endpoint dédié si nécessaire


class MemoryVectorWithEmbedding(MemoryVectorResponse):
    """Réponse incluant le vecteur d'embedding (pour débogage/debug)."""

    embedding: List[float] = Field(
        ...,
        description="Vecteur 768 dimensions",
    )


class MemorySearchRequest(BaseModel):
    """Payload pour la recherche sémantique dans la mémoire."""

    query: str = Field(
        ...,
        min_length=5,
        description="Texte de recherche (sera embedding côté serveur)",
    )
    memory_type: Optional[str] = Field(
        None,
        pattern=r"^(episodic|procedural)$",
        description="Filtrer par type de mémoire",
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Tags requis (AND logique)",
    )
    top_k: int = Field(
        5,
        ge=1,
        le=20,
        description="Nombre maximum de résultats",
    )
    min_similarity: float = Field(
        0.70,
        ge=0.0,
        le=1.0,
        description="Seuil minimum de similarité cosinus",
    )


class MemorySearchResult(BaseModel):
    """Résultat individuel d'une recherche sémantique."""

    id: UUID = Field(..., description="ID du vecteur mémoire")
    content: str = Field(..., description="Contenu textuel")
    memory_type: str = Field(...)
    tags: List[str] = Field(default_factory=list)
    similarity: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Score de similarité cosinus (1.0 = identique)",
    )
    tender_id: Optional[UUID] = Field(None)
    created_at: datetime = Field(...)


class MemorySearchResponse(BaseModel):
    """Réponse de la recherche sémantique."""

    query: str = Field(..., description="Requête originale")
    results: List[MemorySearchResult] = Field(default_factory=list)
    total_found: int = Field(..., description="Nombre total de résultats")


class MemoryVectorFilter(BaseModel):
    """Filtres pour la liste des vecteurs mémoire."""

    memory_type: Optional[str] = Field(None, pattern=r"^(episodic|procedural)$")
    tender_id: Optional[UUID] = Field(None)
    tags: List[str] = Field(default_factory=list)
    order_by: str = Field("created_at", pattern=r"^(created_at|memory_type)$")
    order: str = Field("desc", pattern=r"^(asc|desc)$")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
```

### 3.9 Schémas AuditLog

```python
"""Schémas Pydantic pour l'entité AuditLog."""


class AuditLogBase(BaseModel):
    """Champs communs à tous les modèles AuditLog."""

    action: str = Field(
        ...,
        max_length=50,
        description="Type d'action effectuée",
    )
    resource_type: str = Field(
        ...,
        max_length=50,
        description="Type de ressource concernée",
    )
    resource_id: str = Field(
        ...,
        max_length=36,
        description="ID de la ressource",
    )
    payload: dict = Field(
        default_factory=dict,
        description="Données contextuelles de l'action",
    )
    ip_address: Optional[str] = Field(
        None,
        max_length=45,
        description="Adresse IP source",
    )


class AuditLogCreate(AuditLogBase):
    """Payload pour la création d'un log d'audit (côté serveur uniquement).

    Les champs tenant_id et user_id sont injectés par les dépendances.
    """

    tenant_id: UUID = Field(...)
    user_id: Optional[UUID] = Field(None)


class AuditLogResponse(UUIDMixin, AuditLogBase):
    """Réponse API complète pour un log d'audit."""

    model_config = ConfigDict(from_attributes=True)

    tenant_id: UUID = Field(...)
    user_id: Optional[UUID] = Field(None)
    user_email: Optional[str] = Field(
        None,
        description="Email de l'utilisateur (dénormalisé pour affichage)",
    )
    created_at: datetime = Field(...)


class AuditLogFilter(BaseModel):
    """Filtres pour la consultation des logs d'audit."""

    action: Optional[str] = Field(None, max_length=50)
    resource_type: Optional[str] = Field(None, max_length=50)
    resource_id: Optional[str] = Field(None, max_length=36)
    user_id: Optional[UUID] = Field(None)
    date_from: Optional[datetime] = Field(None)
    date_to: Optional[datetime] = Field(None)
    order_by: str = Field("created_at", pattern=r"^(created_at)$")
    order: str = Field("desc", pattern=r"^(asc|desc)$")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
```

### 3.10 Schémas QualificationRule

```python
"""Schémas Pydantic pour l'entité QualificationRule."""


class QualificationRuleBase(BaseModel):
    """Champs communs à tous les modèles QualificationRule."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Nom descriptif de la règle",
    )
    cpv_whitelist: List[str] = Field(
        default_factory=list,
        description="Codes CPV acceptés (préfixes autorisés)",
    )
    min_amount: Optional[Decimal] = Field(
        None,
        ge=Decimal("0"),
        max_digits=15,
        decimal_places=2,
        description="Montant minimum (NULL = pas de minimum)",
    )
    max_amount: Optional[Decimal] = Field(
        None,
        ge=Decimal("0"),
        max_digits=15,
        decimal_places=2,
        description="Montant maximum (NULL = pas de maximum)",
    )
    min_preparation_days: Optional[int] = Field(
        None,
        ge=0,
        description="Jours minimum de préparation requis",
    )
    required_certifications: List[str] = Field(
        default_factory=list,
        description="Certifications requises",
    )
    scoring_weights: dict = Field(
        default_factory=lambda: {
            "cpv_match": 0.20,
            "amount_range": 0.25,
            "preparation_time": 0.20,
            "certifications": 0.15,
            "buyer_history": 0.10,
            "deadline_feasible": 0.10,
        },
        description="Pondération des critères de scoring",
    )


class QualificationRuleCreate(QualificationRuleBase):
    """Payload pour la création d'une règle de qualification."""

    pass


class QualificationRuleUpdate(BaseModel):
    """Payload pour la mise à jour partielle d'une règle (PATCH)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    cpv_whitelist: Optional[List[str]] = Field(None)
    min_amount: Optional[Decimal] = Field(
        None, ge=Decimal("0"), max_digits=15, decimal_places=2
    )
    max_amount: Optional[Decimal] = Field(
        None, ge=Decimal("0"), max_digits=15, decimal_places=2
    )
    min_preparation_days: Optional[int] = Field(None, ge=0)
    required_certifications: Optional[List[str]] = Field(None)
    scoring_weights: Optional[dict] = Field(None)


class QualificationRuleResponse(UUIDMixin, QualificationRuleBase):
    """Réponse API complète pour une règle de qualification."""

    model_config = ConfigDict(from_attributes=True)

    tenant_id: UUID = Field(...)
    created_at: datetime = Field(...)
    updated_at: Optional[datetime] = Field(None)


class QualificationRuleFilter(BaseModel):
    """Filtres pour la liste des règles de qualification."""

    search: Optional[str] = Field(None, description="Recherche sur le nom")
    order_by: str = Field("created_at", pattern=r"^(created_at|updated_at|name)$")
    order: str = Field("desc", pattern=r"^(asc|desc)$")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class QualificationPreviewRequest(BaseModel):
    """Payload pour prévisualiser la qualification d'un AO sans l'enregistrer."""

    tender_id: UUID = Field(..., description="ID de l'AO à pré-qualifier")
    rule_id: Optional[UUID] = Field(None, description="Règle spécifique à appliquer")


class QualificationPreviewResponse(BaseModel):
    """Réponse de prévisualisation de qualification (dry-run)."""

    tender_id: UUID = Field(...)
    qualification_result: str = Field(...)
    qualification_score: Decimal = Field(...)
    score_breakdown: dict = Field(
        default_factory=dict,
        description="Détail du score par critère",
    )
    applied_rules: List[dict] = Field(default_factory=list)
    memory_matches: List[dict] = Field(default_factory=list)
    would_change_stage: bool = Field(...)
    target_stage_id: Optional[UUID] = Field(None)
```

### 3.11 Récapitulatif des schémas Pydantic

| Entité | Base | Create | Update | Response | Filter | Spécial |
|--------|------|--------|--------|----------|--------|---------|
| Tenant | `TenantBase` | `TenantCreate` | `TenantUpdate` | `TenantResponse` | `TenantFilter` | — |
| User | `UserBase` | `UserCreate` | `UserUpdate` | `UserResponse` | `UserFilter` | `UserLoginRequest`, `TokenResponse`, `UserMeResponse` |
| PipelineStage | `PipelineStageBase` | `PipelineStageCreate` | `PipelineStageUpdate` | `PipelineStageResponse` | `PipelineStageFilter` | `PipelineStageReorderRequest` |
| Tender | `TenderBase` | `TenderCreate` | `TenderUpdate` | `TenderResponse` | `TenderFilter` | `TenderMoveRequest`, `TenderQualifyRequest`, `TenderQualifyResponse` |
| TenderDocument | `TenderDocumentBase` | `TenderDocumentCreate` | `TenderDocumentUpdate` | `TenderDocumentResponse` | `TenderDocumentFilter` | `DocumentUploadResponse` |
| MemoryVector | `MemoryVectorBase` | `MemoryVectorCreate` | `MemoryVectorUpdate` | `MemoryVectorResponse` | `MemoryVectorFilter` | `MemorySearchRequest`, `MemorySearchResponse`, `MemoryVectorWithEmbedding` |
| AuditLog | `AuditLogBase` | `AuditLogCreate` | — | `AuditLogResponse` | `AuditLogFilter` | — |
| QualificationRule | `QualificationRuleBase` | `QualificationRuleCreate` | `QualificationRuleUpdate` | `QualificationRuleResponse` | `QualificationRuleFilter` | `QualificationPreviewRequest`, `QualificationPreviewResponse` |


---

## 4. Migrations Alembic

### 4.1 Configuration `alembic.ini`

```ini
# alembic.ini — Configuration Alembic pour TAKA OS

[alembic]
# Chemin vers le dossier des migrations
script_location = alembic

# Template de nom de fichier de migration
file_template = %%(year)d%%(month).2d%%(day).2d_%%(rev)s_%%(slug)s

# Nombre de révisions à conserver dans le fichier de tête trunc
truncate_slug_length = 40

# Système de versioning
version_path_separator = os

# Format de sortie des logs
# L'URL de la base est injectée dynamiquement via env.py (pas ici)

[post_write_hooks]
# Pas de hooks post-écriture (MVP)

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

### 4.2 Configuration `alembic/env.py` — Version async SQLAlchemy 2.0

```python
"""
Configuration Alembic pour SQLAlchemy 2.0 async.

Leçons appliquées (NEXA-MIND) :
- Utiliser run_async pour les migrations async (crucial pour éviter les
  warnings et erreurs de synchronisation)
- expire_on_commit=False dans la config pour cohérence avec l'app
- target_metadata = Base.metadata pour autogénération
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# ---------------------------------------------------------------------------
# Import des métadonnées SQLAlchemy
# ---------------------------------------------------------------------------
# Import conditionnel pour éviter les erreurs si l'app n'est pas installée
import sys
from pathlib import Path

# Ajoute le répertoire parent au PYTHONPATH pour les imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import Base  # noqa: E402
from app.config import settings  # noqa: E402

# ---------------------------------------------------------------------------
# Configuration Alembic
# ---------------------------------------------------------------------------
config = context.config

# Interprète le fichier de config Python (alembic.ini) pour le logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Métadonnées cible pour l'autogénération
# Tous les modèles héritent de Base → Base.metadata contient toutes les tables
target_metadata = Base.metadata

# URL de la base de données — injectée depuis les settings Pydantic
config.set_main_option("sqlalchemy.url", settings.database_url)


def run_migrations_offline() -> None:
    """Exécute les migrations en mode offline.

    Ce mode génère du SQL sans se connecter à la base. Utile pour :
    - Générer des scripts SQL à appliquer manuellement
    - CI/CD où la base n'est pas accessible
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Compare les types pour détecter les changements de type de colonnes
        compare_type=True,
        # Compare les server defaults
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Configure et exécute les migrations sur une connexion donnée."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # Activation de l'autogénération
        compare_type=True,
        compare_server_default=True,
        # Inclure les schémas (pour pgvector et autres extensions)
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Exécute les migrations en mode async.

    Crée un engine async temporaire, établit une connexion,
    et exécute les migrations de manière synchrone à l'intérieur
    du contexte async.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # run_sync exécute la fonction de manière synchrone dans le contexte async
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Exécute les migrations en mode online (connexion à la base)."""
    asyncio.run(run_async_migrations())


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 4.3 Template de migration `alembic/script.py.mako`

```mako
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downwards if downgrades else "pass"}
```

### 4.4 Migration initiale : `alembic/versions/001_create_all_tables.py`

```python
"""
001 — Création de toutes les tables et seed data.

Cette migration crée l'intégralité du schéma TAKA OS en une seule
révision. C'est une décision architecturale intentionnelle : le MVP
a un schéma connu et stable. Pas de migrations incrémentales
fragmentées.

Tables créées :
    - tenants
    - users
    - pipeline_stages
    - tenders
    - tender_documents
    - memory_vectors (avec pgvector)
    - audit_logs
    - qualification_rules

Seed data :
    - 8 pipeline stages par défaut

Revision ID: 001
Revises:
Create Date: 2025-01-14 00:00:00.000000

"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

UUID_TYPE = postgresql.UUID(as_uuid=True)


def create_tenants_table() -> None:
    """Crée la table tenants — unité d'isolation multi-tenant."""
    op.create_table(
        "tenants",
        sa.Column("id", UUID_TYPE, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id", name="pk_tenants"),
        sa.UniqueConstraint("slug", name="uq_tenants_slug"),
        comment="Organisation cliente — unité d'isolation multi-tenant",
    )
    op.create_index("ix_tenants_slug", "tenants", ["slug"], unique=False)


def create_users_table() -> None:
    """Crée la table users — authentification et autorisation."""
    op.create_table(
        "users",
        sa.Column("id", UUID_TYPE, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID_TYPE, nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="viewer"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_users_tenant_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
        comment="Utilisateurs authentifiés — appartiennent à un tenant",
    )
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"], unique=False)


def create_pipeline_stages_table() -> None:
    """Crée la table pipeline_stages — étapes du pipeline Kanban."""
    op.create_table(
        "pipeline_stages",
        sa.Column("id", UUID_TYPE, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID_TYPE, nullable=False),
        sa.Column("slug", sa.String(50), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("color", sa.String(7), nullable=False, server_default="#6B7280"),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_final", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_pipeline_stages_tenant_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_pipeline_stages"),
        sa.UniqueConstraint("tenant_id", "slug", name="uq_pipeline_stages_tenant_slug"),
        comment="Étapes du pipeline Kanban — personnalisables par tenant",
    )
    op.create_index("ix_pipeline_stages_tenant_id", "pipeline_stages", ["tenant_id"], unique=False)


def create_tenders_table() -> None:
    """Crée la table tenders — appels d'offres (entité centrale)."""
    op.create_table(
        "tenders",
        sa.Column("id", UUID_TYPE, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID_TYPE, nullable=False),
        sa.Column("reference", sa.String(255), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("buyer_name", sa.String(255), nullable=False),
        sa.Column("cpv_code", sa.String(20), nullable=True),
        sa.Column("cpv_description", sa.String(500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("amount_estimated", sa.Numeric(15, 2), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default="EUR"),
        sa.Column("deadline_submission", sa.Date(), nullable=True),
        sa.Column("deadline_questions", sa.Date(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("pipeline_stage_id", UUID_TYPE, nullable=True),
        sa.Column("qualification_result", sa.String(10), nullable=True),
        sa.Column("qualification_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_tenders_tenant_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["pipeline_stage_id"],
            ["pipeline_stages.id"],
            name="fk_tenders_pipeline_stage_id",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_tenders"),
        sa.UniqueConstraint("tenant_id", "reference", name="uq_tenders_tenant_reference"),
        comment="Appels d'offres — entité centrale, multi-tenant",
    )
    op.create_index("ix_tenders_tenant_id", "tenders", ["tenant_id"], unique=False)
    op.create_index("ix_tenders_cpv_code", "tenders", ["cpv_code"], unique=False)
    op.create_index("ix_tenders_status", "tenders", ["status"], unique=False)
    op.create_index("ix_tenders_pipeline_stage_id", "tenders", ["pipeline_stage_id"], unique=False)
    op.create_index("ix_tenders_qualification_result", "tenders", ["qualification_result"], unique=False)
    op.create_index("ix_tenders_deadline_submission", "tenders", ["deadline_submission"], unique=False)


def create_tender_documents_table() -> None:
    """Crée la table tender_documents — documents joints aux AO."""
    op.create_table(
        "tender_documents",
        sa.Column("id", UUID_TYPE, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tender_id", UUID_TYPE, nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("parsed_content", sa.Text(), nullable=True),
        sa.Column("parsing_status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("parsing_error", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(
            ["tender_id"],
            ["tenders.id"],
            name="fk_tender_documents_tender_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_tender_documents"),
        comment="Documents des AO — métadonnées + contenu parsé",
    )
    op.create_index("ix_tender_documents_tender_id", "tender_documents", ["tender_id"], unique=False)
    op.create_index("ix_tender_documents_parsing_status", "tender_documents", ["parsing_status"], unique=False)


def create_memory_vectors_table() -> None:
    """Crée la table memory_vectors — mémoire sémantique avec pgvector."""
    op.create_table(
        "memory_vectors",
        sa.Column("id", UUID_TYPE, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID_TYPE, nullable=False),
        sa.Column("tender_id", UUID_TYPE, nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", sa.NullType(), nullable=False),  # Type 'vector' géré par pgvector
        sa.Column("memory_type", sa.String(20), nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_memory_vectors_tenant_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tender_id"],
            ["tenders.id"],
            name="fk_memory_vectors_tender_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_memory_vectors"),
        comment="Mémoire sémantique — embeddings pgvector 768 dims",
    )
    op.create_index("ix_memory_vectors_tenant_id", "memory_vectors", ["tenant_id"], unique=False)
    op.create_index("ix_memory_vectors_tender_id", "memory_vectors", ["tender_id"], unique=False)
    op.create_index("ix_memory_vectors_memory_type", "memory_vectors", ["memory_type"], unique=False)


def create_audit_logs_table() -> None:
    """Crée la table audit_logs — traçabilité des actions."""
    op.create_table(
        "audit_logs",
        sa.Column("id", UUID_TYPE, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID_TYPE, nullable=False),
        sa.Column("user_id", UUID_TYPE, nullable=True),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("resource_id", sa.String(36), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_audit_logs_tenant_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_audit_logs_user_id",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_audit_logs"),
        comment="Logs d'audit — traçabilité complète des actions",
    )
    op.create_index("ix_audit_logs_tenant_id", "audit_logs", ["tenant_id"], unique=False)
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"], unique=False)
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"], unique=False)
    op.create_index("ix_audit_logs_resource_type", "audit_logs", ["resource_type"], unique=False)
    op.create_index("ix_audit_logs_resource_id", "audit_logs", ["resource_id"], unique=False)
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"], unique=False)


def create_qualification_rules_table() -> None:
    """Crée la table qualification_rules — règles GO/NO-GO."""
    op.create_table(
        "qualification_rules",
        sa.Column("id", UUID_TYPE, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID_TYPE, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("cpv_whitelist", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("min_amount", sa.Numeric(15, 2), nullable=True),
        sa.Column("max_amount", sa.Numeric(15, 2), nullable=True),
        sa.Column("min_preparation_days", sa.Integer(), nullable=True),
        sa.Column("required_certifications", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("scoring_weights", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_qualification_rules_tenant_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_qualification_rules"),
        comment="Règles de qualification GO/NO-GO — configurables par tenant",
    )
    op.create_index("ix_qualification_rules_tenant_id", "qualification_rules", ["tenant_id"], unique=False)


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

DEFAULT_PIPELINE_STAGES = [
    # slug, name, color, display_order, is_final
    ("detected", "Détecté", "#6B7280", 0, False),       # Gris — AO détecté, pas encore qualifié
    ("qualified", "Qualifié", "#3B82F6", 1, False),     # Bleu — Qualification GO, en attente
    ("in_preparation", "En préparation", "#F59E0B", 2, False),  # Orange — Rédaction en cours
    ("submitted", "Soumis", "#8B5CF6", 3, False),       # Violet — Candidature déposée
    ("won", "Gagné", "#10B981", 4, True),               # Vert — AO remporté (final)
    ("lost", "Perdu", "#EF4444", 5, True),              # Rouge — AO perdu (final)
    ("abandoned", "Abandonné", "#9CA3AF", 6, True),     # Gris clair — Désistement (final)
    ("on_hold", "En attente", "#EC4899", 7, True),      # Rose — Mise en attente (final)
]


def seed_pipeline_stages() -> None:
    """Insère les 8 pipeline stages par défaut pour chaque tenant existant.

    À l'initialisation d'un nouveau tenant, ces stages sont créés
    automatiquement. Cette fonction seed est exécutée lors de la migration
    initiale pour le premier tenant (créé lors du setup).
    """
    # Les stages sont insérés tenant par tenant via un trigger ou
    # lors de la création du tenant dans l'application.
    # Cette migration crée seulement la structure ; le seed est appliqué
    # par la fonction SQL ci-dessous.
    op.execute("""
        CREATE OR REPLACE FUNCTION create_default_pipeline_stages()
        RETURNS TRIGGER AS $$
        BEGIN
            INSERT INTO pipeline_stages (tenant_id, slug, name, color, display_order, is_final)
            VALUES
                (NEW.id, 'detected', 'Détecté', '#6B7280', 0, false),
                (NEW.id, 'qualified', 'Qualifié', '#3B82F6', 1, false),
                (NEW.id, 'in_preparation', 'En préparation', '#F59E0B', 2, false),
                (NEW.id, 'submitted', 'Soumis', '#8B5CF6', 3, false),
                (NEW.id, 'won', 'Gagné', '#10B981', 4, true),
                (NEW.id, 'lost', 'Perdu', '#EF4444', 5, true),
                (NEW.id, 'abandoned', 'Abandonné', '#9CA3AF', 6, true),
                (NEW.id, 'on_hold', 'En attente', '#EC4899', 7, true);
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trigger_create_default_pipeline_stages
        AFTER INSERT ON tenants
        FOR EACH ROW
        EXECUTE FUNCTION create_default_pipeline_stages();
    """)


# ---------------------------------------------------------------------------
# Upgrade / Downgrade
# ---------------------------------------------------------------------------

def upgrade() -> None:
    """Upgrade : crée toutes les tables, index, contraintes, triggers et seed data."""
    # 1. Active l'extension pgvector (nécessaire pour memory_vectors)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. Crée les tables dans l'ordre de dépendance (parents avant enfants)
    create_tenants_table()
    create_users_table()
    create_pipeline_stages_table()
    create_tenders_table()
    create_tender_documents_table()
    create_memory_vectors_table()
    create_audit_logs_table()
    create_qualification_rules_table()

    # 3. Crée l'index HNSW pour la recherche par similarité cosinus
    # HNSW (Hierarchical Navigable Small World) est l'algorithme le plus
    # performant pour la recherche ANN (Approximate Nearest Neighbors)
    # avec pgvector. L'index est créé après la table pour éviter les erreurs.
    op.execute("""
        CREATE INDEX hnsw_memory_vectors_embedding_idx
        ON memory_vectors
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
    """)

    # 4. Seed data : trigger pour créer les stages par défaut lors de la
    # création d'un tenant
    seed_pipeline_stages()


def downgrade() -> None:
    """Downgrade : supprime tout dans l'ordre inverse.

    Attention : le CASCADE sur les FK supprime automatiquement les données
    liées. Cette opération est DESTRUCTIVE.
    """
    # Supprime le trigger d'abord
    op.execute("DROP TRIGGER IF EXISTS trigger_create_default_pipeline_stages ON tenants;")
    op.execute("DROP FUNCTION IF EXISTS create_default_pipeline_stages;")

    # Supprime les tables dans l'ordre inverse (enfants avant parents)
    op.drop_table("qualification_rules")
    op.drop_table("audit_logs")
    op.drop_table("memory_vectors")
    op.drop_table("tender_documents")
    op.drop_table("tenders")
    op.drop_table("pipeline_stages")
    op.drop_table("users")
    op.drop_table("tenants")

    # Supprime l'extension pgvector
    op.execute("DROP EXTENSION IF EXISTS vector;")
```

### 4.5 Commandes d'exécution

```bash
# Initialiser Alembic (déjà fait dans la structure du projet)
# alembic init alembic

# Générer une migration (autogénération)
poetry run alembic revision --autogenerate -m "description"

# Exécuter les migrations (upgrader jusqu'à la dernière)
poetry run alembic upgrade head

# Voir la version actuelle
poetry run alembic current

# Downgrader d'une révision
poetry run alembic downgrade -1

# Downgrader tout (DESTRUCTIF — supprime toutes les données)
poetry run alembic downgrade base

# Vérifier que la base est à jour (utilisé au démarrage de l'app)
poetry run alembic check
```

### 4.6 Vérification au démarrage de l'application

```python
# Fichier : app/main.py (extrait — vérification au démarrage)

from alembic import command
from alembic.config import Config as AlembicConfig

async def verify_database_migration() -> None:
    """Vérifie que la base de données est à jour au démarrage.

    Si la base n'est pas à jour, lève une exception bloquante
    pour forcer l'exécution des migrations avant le démarrage.
    """
    from sqlalchemy import text

    async with async_engine.connect() as conn:
        # Vérifie que la table alembic_version existe
        result = await conn.execute(
            text("SELECT version_num FROM alembic_version")
        )
        current = result.scalar()

        # Récupère la dernière révision attendue
        alembic_cfg = AlembicConfig("alembic.ini")
        # Comparaison... (logique simplifiée)

        if current != EXPECTED_REVISION:
            raise RuntimeError(
                f"Database migration mismatch: current={current}, "
                f"expected={EXPECTED_REVISION}. Run: alembic upgrade head"
            )
```

---

## 5. Configuration Pydantic-Settings

### 5.1 Fichier `app/config.py` — Classe Settings

```python
"""
Configuration Pydantic-Settings pour TAKA OS.

Toutes les variables d'environnement sont préfixées par TAKA_OS_
pour éviter les conflits avec d'autres applications sur le même système.

Exemples :
    TAKA_OS_DATABASE_URL=postgresql+asyncpg://user:pass@localhost/takaos
    TAKA_OS_SECRET_KEY=super-secret-key
    TAKA_OS_DEBUG=true

Le fichier .env à la racine du projet est chargé automatiquement.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration centralisée de TAKA OS.

    Toutes les variables sont chargées depuis l'environnement ou le fichier .env.
    Le préfixe TAKA_OS_ est appliqué automatiquement à toutes les variables.
    """

    model_config = SettingsConfigDict(
        # Fichier .env chargé automatiquement
        env_file=".env",
        env_file_encoding="utf-8",
        # Préfixe obligatoire pour toutes les variables d'environnement
        env_prefix="TAKA_OS_",
        # Permet les champs optionnels sans valeur par défaut explicite
        populate_by_name=True,
        # Ignore les variables d'env supplémentaires non définies ici
        extra="ignore",
    )

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 1 — Base de données PostgreSQL
    # ──────────────────────────────────────────────────────────────────────

    database_url: str = Field(
        ...,
        description=(
            "URL de connexion PostgreSQL avec driver asyncpg. "
            "Format : postgresql+asyncpg://user:password@host:port/database"
        ),
        examples=["postgresql+asyncpg://takaos:takaos@localhost:5432/takaos"],
    )
    database_pool_size: int = Field(
        10,
        ge=1,
        le=100,
        description="Nombre de connexions permanentes dans le pool",
    )
    database_max_overflow: int = Field(
        20,
        ge=0,
        description="Nombre de connexions overflow temporaires autorisées",
    )
    database_pool_timeout: int = Field(
        30,
        ge=1,
        description="Timeout d'attente d'une connexion du pool (secondes)",
    )

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 2 — Sécurité & Authentification
    # ──────────────────────────────────────────────────────────────────────

    secret_key: str = Field(
        ...,
        min_length=32,
        description=(
            "Clé secrète pour la signature JWT et le chiffrement. "
            "DOIT être de 32+ caractères et unique par déploiement. "
            "Générer avec : openssl rand -hex 32"
        ),
    )
    jwt_algorithm: str = Field(
        "HS256",
        pattern=r"^(HS256|HS384|HS512)$",
        description="Algorithme de signature JWT",
    )
    jwt_access_token_expire_minutes: int = Field(
        60 * 24,  # 24 heures par défaut
        ge=5,
        description="Durée de validité du token JWT en minutes",
    )
    jwt_refresh_token_expire_days: int = Field(
        7,
        ge=1,
        description="Durée de validité du refresh token en jours",
    )
    password_hash_rounds: int = Field(
        12,
        ge=4,
        le=30,
        description="Nombre de rounds bcrypt pour le hash des mots de passe",
    )

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 3 — Serveur HTTP
    # ──────────────────────────────────────────────────────────────────────

    host: str = Field(
        "0.0.0.0",
        description="Interface d'écoute du serveur",
    )
    port: int = Field(
        8000,
        ge=1,
        le=65535,
        description="Port d'écoute HTTP",
    )
    workers: int = Field(
        1,
        ge=1,
        le=16,
        description="Nombre de workers Uvicorn (1 pour le MVP, >1 en production)",
    )
    reload: bool = Field(
        False,
        description="Rechargement automatique en mode développement",
    )

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 4 — Upload & Stockage de fichiers
    # ──────────────────────────────────────────────────────────────────────

    upload_max_file_size_mb: int = Field(
        50,
        ge=1,
        le=500,
        description="Taille maximum d'un fichier uploadé en Mo",
    )
    upload_max_files_per_tender: int = Field(
        5,
        ge=1,
        le=50,
        description="Nombre maximum de documents par AO",
    )
    upload_allowed_extensions: list[str] = Field(
        default=["pdf", "docx", "doc", "zip"],
        description="Extensions de fichier autorisées",
    )
    upload_storage_path: str = Field(
        "./data/uploads",
        description="Chemin de stockage des fichiers uploadés",
    )

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 5 — Embedding & Mémoire sémantique (pgvector)
    # ──────────────────────────────────────────────────────────────────────

    embedding_model: str = Field(
        "sentence-transformers/all-mpnet-base-v2",
        description="Modèle d'embedding sentence-transformers",
    )
    embedding_dimension: int = Field(
        768,
        ge=64,
        le=4096,
        description="Dimension des vecteurs d'embedding (doit matcher le modèle)",
    )
    embedding_device: str = Field(
        "cpu",
        pattern=r"^(cpu|cuda|mps)$",
        description="Device pour le calcul d'embedding (cpu/cuda/mps)",
    )
    memory_similarity_threshold: float = Field(
        0.70,
        ge=0.0,
        le=1.0,
        description="Seuil minimum de similarité cosinus pour la mémoire épisodique",
    )
    memory_top_k: int = Field(
        5,
        ge=1,
        le=50,
        description="Nombre maximum de souvenirs récupérés",
    )

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 6 — Qualification & Scoring
    # ──────────────────────────────────────────────────────────────────────

    qualification_go_threshold: float = Field(
        0.65,
        ge=0.0,
        le=1.0,
        description="Score minimum pour un verdict GO",
    )
    qualification_maybe_threshold: float = Field(
        0.40,
        ge=0.0,
        le=1.0,
        description="Score minimum pour un verdict MAYBE (en dessous = NO-GO)",
    )
    qualification_default_weights: dict = Field(
        default={
            "cpv_match": 0.20,
            "amount_range": 0.25,
            "preparation_time": 0.20,
            "certifications": 0.15,
            "buyer_history": 0.10,
            "deadline_feasible": 0.10,
        },
        description="Poids par défaut des critères de scoring",
    )

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 7 — Logging & Observabilité
    # ──────────────────────────────────────────────────────────────────────

    log_level: str = Field(
        "INFO",
        pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Niveau de logging global",
    )
    log_format: str = Field(
        "json",
        pattern=r"^(json|text)$",
        description="Format des logs (json pour production, text pour développement)",
    )
    sentry_dsn: Optional[str] = Field(
        None,
        description="DSN Sentry pour le suivi des erreurs (optionnel)",
    )

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 8 — Mode & Environnement
    # ──────────────────────────────────────────────────────────────────────

    environment: str = Field(
        "development",
        pattern=r"^(development|staging|production|test)$",
        description="Environnement d'exécution",
    )
    debug: bool = Field(
        False,
        description="Mode debug (active les logs SQL, les tracebacks détaillés)",
    )
    app_name: str = Field(
        "TAKA OS",
        description="Nom de l'application (utilisé dans les headers et logs)",
    )
    app_version: str = Field(
        "1.0.0",
        pattern=r"^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$",
        description="Version sémantique de l'application",
    )

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 9 — CORS & Sécurité HTTP
    # ──────────────────────────────────────────────────────────────────────

    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Origines autorisées pour CORS",
    )
    cors_allow_credentials: bool = Field(
        True,
        description="Autoriser les credentials CORS (cookies, auth headers)",
    )
    trusted_hosts: list[str] = Field(
        default=["*"],
        description="Hôtes de confiance (['*'] pour désactiver la vérification)",
    )

    # ──────────────────────────────────────────────────────────────────────
    # Validators
    # ──────────────────────────────────────────────────────────────────────

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Vérifie que l'URL utilise le driver asyncpg."""
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "database_url doit utiliser le driver asyncpg "
                "(ex: postgresql+asyncpg://user:pass@host/db). "
                f"Reçu: {v[:30]}..."
            )
        return v

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Vérifie que la secret_key n'est pas la valeur par défaut en production."""
        if len(v) < 32:
            raise ValueError("secret_key doit faire au minimum 32 caractères")
        # Liste de clés connues à rejeter
        weak_keys = [
            "changeme",
            "secret",
            "password",
            "123456",
            "default",
            "your-secret-key",
        ]
        if v.lower() in weak_keys:
            raise ValueError(f"secret_key trop faible / commune : '{v}'")
        return v

    @field_validator("upload_storage_path")
    @classmethod
    def validate_upload_path(cls, v: str) -> str:
        """S'assure que le chemin ne se termine pas par un slash."""
        return v.rstrip("/")

    @property
    def is_production(self) -> bool:
        """True si l'environnement est production."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """True si l'environnement est development."""
        return self.environment == "development"

    @property
    def database_url_sync(self) -> str:
        """Version synchrone de l'URL pour Alembic et outils CLI.

        Remplace asyncpg par psycopg2 pour les commandes synchrones.
        """
        return self.database_url.replace(
            "postgresql+asyncpg://", "postgresql+psycopg2://"
        )

    @property
    def upload_max_file_size_bytes(self) -> int:
        """Taille maximum en octets."""
        return self.upload_max_file_size_mb * 1024 * 1024


# ──────────────────────────────────────────────────────────────────────────
# Singleton settings (cacheé pour éviter les rechargements)
# ──────────────────────────────────────────────────────────────────────────


@lru_cache
def get_settings() -> Settings:
    """Retourne une instance unique des settings (singleton).

    Le lru_cache garantit que les settings ne sont chargés qu'une seule
    fois par processus, évitant les lectures répétées du fichier .env.
    """
    return Settings()


# Instance globale pour les imports directs
settings = get_settings()
```

### 5.2 Fichier `.env.example` — Variables d'environnement

```bash
# ═══════════════════════════════════════════════════════════════════════════
# TAKA OS — Configuration d'environnement (.env)
# ═══════════════════════════════════════════════════════════════════════════
# Copier ce fichier vers .env et remplir les valeurs.
# Toutes les variables sont préfixées par TAKA_OS_
# ═══════════════════════════════════════════════════════════════════════════

# ──────────────────────────────────────────────────────────────────────────
# SECTION 1 — Base de données PostgreSQL (OBLIGATOIRE)
# ──────────────────────────────────────────────────────────────────────────
TAKA_OS_DATABASE_URL=postgresql+asyncpg://takaos:takaos@localhost:5432/takaos
TAKA_OS_DATABASE_POOL_SIZE=10
TAKA_OS_DATABASE_MAX_OVERFLOW=20

# ──────────────────────────────────────────────────────────────────────────
# SECTION 2 — Sécurité & Authentification (OBLIGATOIRE)
# ──────────────────────────────────────────────────────────────────────────
# Générer avec : openssl rand -hex 32
TAKA_OS_SECRET_KEY=change-me-in-production-use-openssl-rand-hex-32
TAKA_OS_JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440
TAKA_OS_PASSWORD_HASH_ROUNDS=12

# ──────────────────────────────────────────────────────────────────────────
# SECTION 3 — Serveur HTTP
# ──────────────────────────────────────────────────────────────────────────
TAKA_OS_HOST=0.0.0.0
TAKA_OS_PORT=8000
TAKA_OS_WORKERS=1

# ──────────────────────────────────────────────────────────────────────────
# SECTION 4 — Upload & Stockage
# ──────────────────────────────────────────────────────────────────────────
TAKA_OS_UPLOAD_MAX_FILE_SIZE_MB=50
TAKA_OS_UPLOAD_MAX_FILES_PER_TENDER=5
TAKA_OS_UPLOAD_STORAGE_PATH=./data/uploads

# ──────────────────────────────────────────────────────────────────────────
# SECTION 5 — Embedding & Mémoire sémantique
# ──────────────────────────────────────────────────────────────────────────
TAKA_OS_EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
TAKA_OS_EMBEDDING_DIMENSION=768
TAKA_OS_EMBEDDING_DEVICE=cpu
TAKA_OS_MEMORY_SIMILARITY_THRESHOLD=0.70

# ──────────────────────────────────────────────────────────────────────────
# SECTION 6 — Qualification
# ──────────────────────────────────────────────────────────────────────────
TAKA_OS_QUALIFICATION_GO_THRESHOLD=0.65
TAKA_OS_QUALIFICATION_MAYBE_THRESHOLD=0.40

# ──────────────────────────────────────────────────────────────────────────
# SECTION 7 — Logging
# ──────────────────────────────────────────────────────────────────────────
TAKA_OS_LOG_LEVEL=INFO
TAKA_OS_LOG_FORMAT=text

# ──────────────────────────────────────────────────────────────────────────
# SECTION 8 — Environnement
# ──────────────────────────────────────────────────────────────────────────
TAKA_OS_ENVIRONMENT=development
TAKA_OS_DEBUG=false

# ──────────────────────────────────────────────────────────────────────────
# SECTION 9 — CORS
# ──────────────────────────────────────────────────────────────────────────
TAKA_OS_CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### 5.3 Fichier `pyproject.toml` — Configuration Poetry

```toml
[tool.poetry]
name = "taka-os"
version = "1.0.0"
description = "OS agentic open source pour la gestion des Appels d'Offres"
authors = ["TAKA OS Team <team@takaos.dev>"]
license = "MIT"
readme = "README.md"
homepage = "https://takaos.dev"
repository = "https://github.com/takaos/taka-os"
packages = [{ include = "app" }]

[tool.poetry.dependencies]
# ──────────────────────────────────────────────────────────────────
# Python — BLOQUÉ à <3.14 (SQLAlchemy 2.0.36 incompatible avec 3.14)
# ──────────────────────────────────────────────────────────────────
python = ">=3.12,<3.14"

# ──────────────────────────────────────────────────────────────────
# Framework web
# ──────────────────────────────────────────────────────────────────
fastapi = "^0.115.0"
uvicorn = { extras = ["standard" ], version = "^0.32.0" }
python-multipart = "^0.0.17"    # Pour UploadFile

# ──────────────────────────────────────────────────────────────────
# Base de données — SQLAlchemy 2.0 async
# ──────────────────────────────────────────────────────────────────
sqlalchemy = { extras = ["asyncio"], version = "^2.0.36" }
asyncpg = "^0.30.0"              # Driver PostgreSQL async
alembic = "^1.14.0"              # Migrations
pgvector = "^0.3.6"              # Extension pgvector pour SQLAlchemy

# ──────────────────────────────────────────────────────────────────
# Validation & Configuration
# ──────────────────────────────────────────────────────────────────
pydantic = "^2.9.0"
pydantic-settings = "^2.6.0"

# ──────────────────────────────────────────────────────────────────
# Sécurité & Auth
# ──────────────────────────────────────────────────────────────────
python-jose = { extras = ["cryptography"], version = "^3.3.0" }
passlib = { extras = ["bcrypt"], version = "^1.7.4" }
python-jose = "^3.3.0"           # JWT encoding/decoding

# ──────────────────────────────────────────────────────────────────
# Parsing documents
# ──────────────────────────────────────────────────────────────────
pymupdf = "^1.24.0"              # PDF parsing (remplace PyPDF2, plus rapide)
python-docx = "^1.1.0"           # DOCX parsing

# ──────────────────────────────────────────────────────────────────
# Embedding (mémoire sémantique)
# ──────────────────────────────────────────────────────────────────
sentence-transformers = "^3.2.0" # Modèles d'embedding

# ──────────────────────────────────────────────────────────────────
# Utilitaires
# ──────────────────────────────────────────────────────────────────
email-validator = "^2.2.0"       # Validation d'emails Pydantic
python-dotenv = "^1.0.0"         # Chargement .env
httpx = "^0.27.0"                # Client HTTP async (API externes v2)
structlog = "^24.4.0"            # Logging structuré (JSON en production)

[tool.poetry.group.dev.dependencies]
# ──────────────────────────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────────────────────────
pytest = "^8.3.0"
pytest-asyncio = "^0.24.0"       # Tests async
pytest-cov = "^6.0.0"            # Couverture de code
httpx = "^0.27.0"                # TestClient pour FastAPI
factory-boy = "^3.3.0"           # Génération de fixtures de test
faker = "^30.0"                  # Données de test réalistes

# ──────────────────────────────────────────────────────────────────
# Qualité de code
# ──────────────────────────────────────────────────────────────────
ruff = "^0.8.0"                  # Linter + formatter (remplace flake8, black, isort)
mypy = "^1.13.0"                 # Typage statique

# ──────────────────────────────────────────────────────────────────
# Debugging
# ──────────────────────────────────────────────────────────────────
debugpy = "^1.8.0"               # Debug remote

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

# ──────────────────────────────────────────────────────────────────
# Configuration Ruff
# ──────────────────────────────────────────────────────────────────
[tool.ruff]
target-version = "py312"         # Python 3.12+ uniquement
line-length = 100

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # Pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "W",   # pycodestyle warnings
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "SIM", # flake8-simplify
]
ignore = ["E501"]  # Line too long — géré par le formatter

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

# ──────────────────────────────────────────────────────────────────
# Configuration MyPy
# ──────────────────────────────────────────────────────────────────
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
ignore_missing_imports = true  # Pour les libs sans stubs

# ──────────────────────────────────────────────────────────────────
# Configuration Pytest
# ──────────────────────────────────────────────────────────────────
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "--cov=app --cov-report=term-missing --cov-report=html"
```

---

## 6. Docker — Infrastructure minimale (1 seul service)

### 6.1 `docker-compose.yml`

```yaml
# ═══════════════════════════════════════════════════════════════════
# TAKA OS — Docker Compose (MVP)
# ═══════════════════════════════════════════════════════════════════
# UNE SEULE BASE DE DONNÉES (leçon NEXA-MIND : 4 services = trop lourd)
# PostgreSQL 15 avec pgvector pré-installé.
# L'application FastAPI s'exécute directement sur le host ou via
# un process manager (systemd, supervisor) pour économiser les ressources.
# ═══════════════════════════════════════════════════════════════════

version: "3.8"

services:
  postgres:
    image: ankane/pgvector:v0.8.0
    container_name: takaos-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${TAKA_OS_DATABASE_USER:-takaos}
      POSTGRES_PASSWORD: ${TAKA_OS_DATABASE_PASSWORD:-takaos}
      POSTGRES_DB: ${TAKA_OS_DATABASE_NAME:-takaos}
    ports:
      - "${TAKA_OS_DATABASE_PORT:-5432}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 5
      start_period: 10s
    networks:
      - takaos-network

volumes:
  postgres_data:
    driver: local

networks:
  takaos-network:
    driver: bridge
```

### 6.2 `Dockerfile` (application)

```dockerfile
# ═══════════════════════════════════════════════════════════════════
# TAKA OS — Dockerfile
# ═══════════════════════════════════════════════════════════════════
# Build multi-stage pour minimiser la taille de l'image finale.
# Python 3.12 strictement (jamais 3.14 — leçon NEXA-MIND).
# ═══════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────
# Stage 1 — Builder (dépendances Python)
# ─────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Installation de Poetry
RUN pip install --no-cache-dir poetry==1.8.4

# Configuration Poetry — pas de virtualenv dans le conteneur
RUN poetry config virtualenvs.create false

# Copie des fichiers de dépendances
COPY pyproject.toml poetry.lock ./

# Installation des dépendances (sans le groupe dev)
RUN poetry install --no-dev --no-interaction --no-ansi

# ─────────────────────────────────────────────────────────────────
# Stage 2 — Runtime
# ─────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Création de l'utilisateur non-root
RUN groupadd --gid 1000 takaos && \
    useradd --uid 1000 --gid takaos --shell /bin/bash takaos

# Copie des dépendances installées depuis le builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copie du code source
COPY --chown=takaos:takaos app ./app
COPY --chown=takaos:takaos alembic ./alembic
COPY --chown=takaos:takaos alembic.ini .

# Création du répertoire de stockage des uploads
RUN mkdir -p /app/data/uploads && chown -R takaos:takaos /app/data

# Bascule vers l'utilisateur non-root
USER takaos

# Port exposé
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Commande de démarrage : migrations puis application
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

---

## 7. Glossaire & Conventions de nommage

### 7.1 Conventions de nommage SQL

| Élément | Convention | Exemple |
|---------|-----------|---------|
| Tables | Pluriel, snake_case | `tenders`, `memory_vectors` |
| Colonnes | Singulier, snake_case | `deadline_submission`, `qualification_score` |
| Clés primaires | `pk_{table}` | `pk_tenders` |
| Clés étrangères | `fk_{table}_{colonne}` | `fk_tenders_tenant_id` |
| Contraintes uniques | `uq_{table}_{colonnes}` | `uq_tenders_tenant_reference` |
| Index | `ix_{table}_{colonne}` | `ix_tenders_deadline_submission` |
| Triggers | `trigger_{action}` | `trigger_create_default_pipeline_stages` |
| Fonctions | `snake_case` | `create_default_pipeline_stages` |

### 7.2 Conventions de nommage Python

| Élément | Convention | Exemple |
|---------|-----------|---------|
| Classes de modèles SQLAlchemy | PascalCase, singulier | `Tender`, `MemoryVector` |
| Classes de schémas Pydantic | PascalCase + suffixe | `TenderCreate`, `TenderResponse` |
| Colonnes Mapped | snake_case | `pipeline_stage_id` |
| Enumérations | PascalCase + suffixe Enum | `TenderStatus`, `MemoryType` |
| Constants | UPPER_SNAKE_CASE | `EMBEDDING_DIMENSION = 768` |
| Fonctions | snake_case | `get_settings()`, `utc_now()` |
| Variables | snake_case | `qualification_score` |

### 7.3 Glossaire métier

| Terme | Définition |
|-------|-----------|
| **AO** | Appel d'Offres — consultation publique ou privée pour l'attribution d'un contrat |
| **CPV** | Common Procurement Vocabulary — classification européenne des marchés publics |
| **DCE** | Dossier de Consultation des Entreprises — ensemble des documents de l'AO |
| **CCTP** | Cahier des Clauses Techniques Particulières |
| **DPGF** | Décomposition du Prix Global Forfaitaire |
| **RCR** | Règlement de la Consultation Restreinte |
| **CCAG** | Cahier des Clauses Administratives Générales |
| **GO/NO-GO** | Décision binaire (ou ternaire avec MAYBE) de réponse à un AO |
| **Pipeline** | Processus de suivi des AO en colonnes (Kanban) |
| **Mémoire épisodique** | Souvenirs d'événements spécifiques (résultats d'AO passés) |
| **Mémoire procédurale** | Connaissances générales et patterns extraits de l'expérience |
| **Embedding** | Représentation vectorielle d'un texte pour calcul de similarité |
| **HNSW** | Hierarchical Navigable Small World — algorithme de recherche approximative |

---

## 8. Récapitulatif des décisions architecturales critiques (ADRs)

| # | Décision | Justification | Héritage NEXA-MIND |
|---|----------|-------------|-------------------|
| 1 | **Un seul fichier modèles** (`app/models/ao.py`) | Évite la duplication de tables et les conflits de synchronisation | 2 modules avec tables `tenders` dupliquées = données incohérentes |
| 2 | **Python `<3.14`** | SQLAlchemy 2.0.36 incompatible avec Python 3.14 (changements internals) | Build échoué silencieusement en CI avec 3.14-dev |
| 3 | **Un seul PostgreSQL** | Déployable sur VPS 2 vCPU / 4 Go RAM | 4 services Docker = OOM kills constants sur VPS |
| 4 | **`expire_on_commit=False`** | Les objets restent attachés après commit, pas de lazy loading | DetachedInstanceError en cascade sur toutes les requêtes |
| 5 | **Pas de framework agentic** | Fonctions Python pures + background tasks FastAPI | LangChain complexifiait sans valeur ajoutée, lock-in technique |
| 6 | **pgvector intégré à PostgreSQL** | Une seule base de données, pas de Qdrant/Weaviate | 2 bases de données = backup, monitoring, failover doublés |
| 7 | **Multi-tenant par `tenant_id`** | Pas de schéma PostgreSQL séparé (simplification MVP) | Schémas séparés = complexité de migration et de requêtes |
| 8 | **Seed data via trigger SQL** | 8 pipeline stages créés automatiquement à la création du tenant | Oubli du seed = tenant sans pipeline, erreurs 500 |
| 9 | **Modèle d'embedding 768 dims** | Correspond à `all-mpnet-base-v2`, bon ratio qualité/performance | Dimension incompatible entre modèle et DB = erreurs d'insertion |
| 10 | **Pydantic v2 partout** | Coherence de la validation, performance supérieure à v1 | Mix v1/v1 = confusion et bugs de sérialisation |

---

*Document produit conformément aux spécifications TAKA OS — Section 1.*  
*Tous les modèles sont COMPLETS. Aucun "...", aucun "etc.", aucune supposition.*

# TAKA OS — Blueprint Technique

## Section 2 : API REST & Sécurité

---

## 1. Spécification API REST Complète

### Conventions Globales

| Aspect | Spécification |
|--------|---------------|
| **Format** | JSON strict (`Content-Type: application/json`) |
| **Encodage** | UTF-8 |
| **Dates** | ISO 8601 (ex: `2025-01-15T14:30:00Z`) |
| **Pagination** | `limit` (max 100, défaut 20) + `offset` |
| **Tri** | `sort_by` (champ) + `sort_order` (`asc` ou `desc`) |
| **Authentification** | Header `Authorization: Bearer <access_token>` |
| **Refresh Token** | Cookie `refresh_token` (httpOnly, Secure, SameSite=Strict) |
| **Idempotence** | Header `Idempotency-Key` pour POST sensibles |

### Structure de Réponse Uniforme

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "timestamp": "2025-01-15T14:30:00Z",
    "request_id": "req_abc123",
    "pagination": {
      "limit": 20,
      "offset": 0,
      "total": 150
    }
  }
}
```

### Structure d'Erreur Uniforme

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Champ 'email' invalide",
    "details": [
      { "field": "email", "issue": "Format d'email invalide" }
    ],
    "request_id": "req_abc123",
    "timestamp": "2025-01-15T14:30:00Z"
  }
}
```

### Codes d'Erreur Internes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `AUTHENTICATION_REQUIRED` | Token manquant ou invalide | 401 |
| `TOKEN_EXPIRED` | Access token expiré | 401 |
| `TOKEN_REVOKED` | Token révoqué (logout) | 401 |
| `INSUFFICIENT_PERMISSIONS` | Rôle insuffisant | 403 |
| `CROSS_TENANT_ACCESS` | Tentative d'accès à un autre tenant | 403 |
| `RESOURCE_NOT_FOUND` | Ressource inexistante | 404 |
| `VALIDATION_ERROR` | Données d'entrée invalides | 422 |
| `RATE_LIMIT_EXCEEDED` | Trop de requêtes | 429 |
| `INTERNAL_ERROR` | Erreur serveur | 500 |
| `SERVICE_UNAVAILABLE` | Service temporairement indisponible | 503 |

---

## 1.1 Endpoints — Authentification (`/auth`)

### POST `/auth/dev-login` — Login Développement (sans mot de passe)

> ⚠️ **DANGER** — Endpoint activé uniquement si `ENV=development`. Retourne 404 en production.

| Attribut | Valeur |
|----------|--------|
| **Méthode** | POST |
| **Description** | Authentification de développement sans mot de passe. Permet aux développeurs de tester l'API sans configurer de credentials. |
| **Rôle requis** | Aucun (public, dev uniquement) |

**Paramètres (Body) :**

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `email` | string | Oui | Email de l'utilisateur dev |
| `tenant_id` | string (UUID) | Non | Tenant à utiliser (défaut: tenant dev) |

**Exemple Requête :**
```json
POST /auth/dev-login
Content-Type: application/json

{
  "email": "dev@taka.local",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900,
    "user": {
      "id": "usr_001",
      "email": "dev@taka.local",
      "full_name": "Dev User",
      "role": "admin",
      "tenant_id": "550e8400-e29b-41d4-a716-446655440000"
    }
  },
  "meta": { "timestamp": "2025-01-15T14:30:00Z", "request_id": "req_001" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Succès — JWT retourné |
| 400 | `ENV != development` — endpoint désactivé |
| 404 | Utilisateur non trouvé |
| 422 | Email invalide |

---

### POST `/auth/login` — Authentification

| Attribut | Valeur |
|----------|--------|
| **Méthode** | POST |
| **Description** | Authentification avec email et mot de passe (bcrypt). Retourne un access token (JWT) et un refresh token (cookie httpOnly). |
| **Rôle requis** | Aucun (public) |

**Paramètres (Body) :**

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `email` | string | Oui | Email de l'utilisateur |
| `password` | string | Oui | Mot de passe (8-128 caractères) |

**Exemple Requête :**
```json
POST /auth/login
Content-Type: application/json

{
  "email": "manager@client.fr",
  "password": "SuperSecret123!"
}
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c3JfMDAxIiwidGVuYW50X2lkIjoiNTUwZTg0MDAtZTI5Yi00MWQ0LWE3MTYtNDQ2NjU1NDQwMDAwIiwicm9sZSI6Im1hbmFnZXIiLCJleHAiOjE3MDUzMjYwMDAsImlhdCI6MTcwNTMyNTEwMH0...",
    "token_type": "bearer",
    "expires_in": 900,
    "user": {
      "id": "usr_001",
      "email": "manager@client.fr",
      "full_name": "Jean Dupont",
      "role": "manager",
      "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
      "tenant_name": "Acme Corp"
    }
  },
  "meta": { "timestamp": "2025-01-15T14:30:00Z", "request_id": "req_002" }
}
```

**Headers de Réponse :**
```
Set-Cookie: refresh_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...; HttpOnly; Secure; SameSite=Strict; Path=/auth/refresh; Max-Age=604800
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Authentification réussie |
| 400 | Compte désactivé ou verrouillé |
| 401 | Email ou mot de passe incorrect |
| 422 | Validation échouée (email malformé, password trop court) |
| 429 | Trop de tentatives (rate limiting) |
| 500 | Erreur serveur |

**Sécurité :**
- Comparaison bcrypt en **constant-time** pour prévenir les timing attacks
- Incrémentation du compteur d'échecs après chaque tentative → lockout après 5 échecs
- Audit log de chaque tentative (succès + échec)
- Rate limit : 5 req/min par IP

---

### POST `/auth/refresh` — Rafraîchissement du JWT

| Attribut | Valeur |
|----------|--------|
| **Méthode** | POST |
| **Description** | Échange un refresh token valide (cookie) contre un nouveau access token + nouveau refresh token (rotation). |
| **Rôle requis** | Aucun (refresh token requis) |

**Paramètres :** Aucun (le refresh token est lu depuis le cookie `refresh_token`)

**Exemple Requête :**
```
POST /auth/refresh
Cookie: refresh_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.NOUVEAU...",
    "token_type": "bearer",
    "expires_in": 900
  },
  "meta": { "timestamp": "2025-01-15T14:35:00Z", "request_id": "req_003" }
}
```

**Headers de Réponse :**
```
Set-Cookie: refresh_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.NOUVEAU...; HttpOnly; Secure; SameSite=Strict; Path=/auth/refresh; Max-Age=604800
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Refresh réussi — nouveau access token |
| 401 | Refresh token manquant, invalide ou expiré |
| 401 | Refresh token révoqué (logout effectué) |
| 401 | Refresh token déjà utilisé (détection de vol) |

**Sécurité — Rotation des Refresh Tokens :**
- Chaque refresh invalide l'ancien token et en génère un nouveau
- Si un refresh token déjà utilisé est représenté → révocation immédiate de toute la famille de tokens + alerte sécurité
- `token_family` UUID lié ensemble tous les refresh tokens d'une session

---

### GET `/auth/me` — Profil Utilisateur Connecté

| Attribut | Valeur |
|----------|--------|
| **Méthode** | GET |
| **Description** | Retourne le profil complet de l'utilisateur authentifié. |
| **Rôle requis** | `viewer`, `manager`, `admin` (tout rôle authentifié) |

**Paramètres :** Aucun (auth via Bearer token)

**Exemple Requête :**
```
GET /auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "id": "usr_001",
    "email": "manager@client.fr",
    "full_name": "Jean Dupont",
    "role": "manager",
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
    "tenant_name": "Acme Corp",
    "is_active": true,
    "created_at": "2024-12-01T10:00:00Z",
    "last_login_at": "2025-01-15T14:30:00Z",
    "permissions": ["tenders:read", "tenders:create", "tenders:update", "documents:read", "documents:create", "pipeline:read", "memory:read", "memory:create"]
  },
  "meta": { "timestamp": "2025-01-15T14:30:00Z", "request_id": "req_004" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Profil retourné |
| 401 | Token manquant ou invalide |
| 401 | Token expiré |
| 403 | Compte désactivé |

---

### POST `/auth/logout` — Déconnexion

| Attribut | Valeur |
|----------|--------|
| **Méthode** | POST |
| **Description** | Révoque le refresh token (cookie) et invalide l'access token (blacklist). |
| **Rôle requis** | `viewer`, `manager`, `admin` (tout rôle authentifié) |

**Paramètres :** Aucun

**Exemple Requête :**
```
POST /auth/logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Cookie: refresh_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": { "message": "Déconnexion réussie" },
  "meta": { "timestamp": "2025-01-15T14:40:00Z", "request_id": "req_005" }
}
```

**Headers de Réponse :**
```
Set-Cookie: refresh_token=; HttpOnly; Secure; SameSite=Strict; Path=/auth/refresh; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Déconnexion réussie — tokens révoqués |
| 401 | Token manquant |
| 500 | Erreur lors de la révocation |

---

## 1.2 Endpoints — Appels d'Offres (`/tenders`)

### GET `/tenders` — Liste des Appels d'Offres

| Attribut | Valeur |
|----------|--------|
| **Méthode** | GET |
| **Description** | Liste paginée des appels d'offres du tenant courant avec filtres avancés. |
| **Rôle requis** | `viewer`, `manager`, `admin` |

**Paramètres (Query) :**

| Paramètre | Type | Requis | Description | Défaut |
|-----------|------|--------|-------------|--------|
| `limit` | integer | Non | Nombre de résultats (max 100) | 20 |
| `offset` | integer | Non | Offset pour pagination | 0 |
| `search` | string | Non | Recherche textuelle (titre, description, client) | — |
| `pipeline_stage` | string | Non | Filtrer par stage (e.g. `new`, `qualified`, `submitted`) | — |
| `qualification_result` | string | Non | `eligible`, `ineligible`, `pending` | — |
| `deadline_from` | ISO date | Non | Date limite de réponse (début) | — |
| `deadline_to` | ISO date | Non | Date limite de réponse (fin) | — |
| `cpv_code` | string | Non | Code CPV (Common Procurement Vocabulary) | — |
| `sort_by` | string | Non | Champ de tri (`created_at`, `deadline`, `title`, `estimated_value`) | `created_at` |
| `sort_order` | string | Non | `asc` ou `desc` | `desc` |
| `is_archived` | boolean | Non | Inclure les soft-deleted | `false` |

**Exemple Requête :**
```
GET /tenders?limit=10&offset=0&search=informatique&pipeline_stage=new&deadline_from=2025-02-01&sort_by=deadline&sort_order=asc
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "tdr_001",
        "title": "Fourniture de matériel informatique — Lot 1",
        "reference_number": "2025-INFORMATIQUE-042",
        "issuing_organization": "Ministère de la Transition Écologique",
        "description": "Fourniture et installation de postes de travail...",
        "pipeline_stage": "new",
        "qualification_result": "pending",
        "estimated_value": 150000.00,
        "currency": "EUR",
        "deadline": "2025-02-15T17:00:00Z",
        "cpv_code": "30210000",
        "cpv_description": "Matériel informatique",
        "notice_url": "https://www.boamp.fr/avis/20250115042",
        "document_count": 3,
        "created_at": "2025-01-10T09:00:00Z",
        "updated_at": "2025-01-12T14:30:00Z"
      },
      {
        "id": "tdr_002",
        "title": "Développement d'une application métier",
        "reference_number": "2025-DEV-018",
        "issuing_organization": "Région Occitanie",
        "description": "Conception et développement d'une application web...",
        "pipeline_stage": "qualified",
        "qualification_result": "eligible",
        "estimated_value": 250000.00,
        "currency": "EUR",
        "deadline": "2025-03-01T12:00:00Z",
        "cpv_code": "72267000",
        "cpv_description": "Services de développement de logiciels",
        "notice_url": "https://www.marches-publics.gov.fr/2025018018",
        "document_count": 5,
        "created_at": "2025-01-08T11:00:00Z",
        "updated_at": "2025-01-14T16:45:00Z"
      }
    ]
  },
  "meta": {
    "timestamp": "2025-01-15T14:30:00Z",
    "request_id": "req_010",
    "pagination": { "limit": 10, "offset": 0, "total": 47 }
  }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Liste retournée (peut être vide) |
| 401 | Non authentifié |
| 403 | Cross-tenant détecté |
| 422 | Paramètre de filtre invalide |

---

### POST `/tenders` — Création d'un Appel d'Offres

| Attribut | Valeur |
|----------|--------|
| **Méthode** | POST |
| **Description** | Création manuelle d'un appel d'offres. Le `tenant_id` est injecté automatiquement depuis le JWT. |
| **Rôle requis** | `manager`, `admin` |

**Paramètres (Body) :**

| Champ | Type | Requis | Description | Validation |
|-------|------|--------|-------------|------------|
| `title` | string | Oui | Titre de l'AO | 5-500 caractères |
| `reference_number` | string | Non | Numéro de référence | 1-100 caractères, unique par tenant |
| `issuing_organization` | string | Non | Organisme émetteur | 1-300 caractères |
| `description` | string | Non | Description | Max 50000 caractères |
| `deadline` | ISO date | Non | Date limite de réponse | Doit être dans le futur |
| `estimated_value` | decimal | Non | Valeur estimée | ≥ 0 |
| `currency` | string | Non | Devise (ISO 4217) | `EUR` par défaut |
| `cpv_code` | string | Non | Code CPV | 8 caractères max |
| `notice_url` | string | Non | URL de l'avis | URL valide |
| `pipeline_stage` | string | Non | Stage initial | Défaut: `new` |

**Exemple Requête :**
```json
POST /tenders
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "title": "Maintenance des équipements réseau 2025",
  "reference_number": "2025-RESEAU-003",
  "issuing_organization": "Département de la Gironde",
  "description": "Prestation de maintenance préventive et corrective...",
  "deadline": "2025-04-30T17:00:00Z",
  "estimated_value": 80000.00,
  "currency": "EUR",
  "cpv_code": "32561000",
  "notice_url": "https://www.boamp.fr/avis/20250003"
}
```

**Exemple Réponse (201) :**
```json
{
  "success": true,
  "data": {
    "id": "tdr_003",
    "title": "Maintenance des équipements réseau 2025",
    "reference_number": "2025-RESEAU-003",
    "issuing_organization": "Département de la Gironde",
    "description": "Prestation de maintenance préventive et corrective...",
    "pipeline_stage": "new",
    "qualification_result": "pending",
    "estimated_value": 80000.00,
    "currency": "EUR",
    "deadline": "2025-04-30T17:00:00Z",
    "cpv_code": "32561000",
    "notice_url": "https://www.boamp.fr/avis/20250003",
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
    "document_count": 0,
    "created_at": "2025-01-15T14:45:00Z",
    "updated_at": "2025-01-15T14:45:00Z"
  },
  "meta": { "timestamp": "2025-01-15T14:45:00Z", "request_id": "req_011" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 201 | Création réussie |
| 400 | `reference_number` déjà existant pour ce tenant |
| 401 | Non authentifié |
| 403 | Rôle `viewer` — insuffisant |
| 422 | Validation échouée |
| 500 | Erreur base de données |

---

### GET `/tenders/{id}` — Détail d'un Appel d'Offres

| Attribut | Valeur |
|----------|--------|
| **Méthode** | GET |
| **Description** | Détail complet d'un AO avec documents associés et historique des changements. |
| **Rôle requis** | `viewer`, `manager`, `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID de l'appel d'offres |

**Paramètres (Query) :**

| Paramètre | Type | Requis | Description | Défaut |
|-----------|------|--------|-------------|--------|
| `include_documents` | boolean | Non | Inclure les documents | `true` |
| `include_history` | boolean | Non | Inclure l'historique | `true` |

**Exemple Requête :**
```
GET /tenders/tdr_001?include_documents=true&include_history=true
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "id": "tdr_001",
    "title": "Fourniture de matériel informatique — Lot 1",
    "reference_number": "2025-INFORMATIQUE-042",
    "issuing_organization": "Ministère de la Transition Écologique",
    "description": "Fourniture et installation de postes de travail...",
    "pipeline_stage": "qualified",
    "qualification_result": "eligible",
    "qualification_summary": "L'AO correspond aux critères de l'entreprise. Métier aligné (IT), valeur dans la fourchette cible, délai compatible.",
    "estimated_value": 150000.00,
    "currency": "EUR",
    "deadline": "2025-02-15T17:00:00Z",
    "cpv_code": "30210000",
    "cpv_description": "Matériel informatique",
    "notice_url": "https://www.boamp.fr/avis/20250115042",
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
    "is_archived": false,
    "created_at": "2025-01-10T09:00:00Z",
    "updated_at": "2025-01-14T16:30:00Z",
    "documents": [
      {
        "id": "doc_001",
        "filename": "avis-reglemente.pdf",
        "mime_type": "application/pdf",
        "file_size": 2457600,
        "uploaded_at": "2025-01-10T09:15:00Z",
        "uploaded_by": "Jean Dupont",
        "parsed": true,
        "parse_status": "completed"
      },
      {
        "id": "doc_002",
        "filename": "dce-complete.zip",
        "mime_type": "application/zip",
        "file_size": 15728640,
        "uploaded_at": "2025-01-11T10:30:00Z",
        "uploaded_by": "Marie Martin",
        "parsed": false,
        "parse_status": "pending"
      }
    ],
    "history": [
      {
        "action": "created",
        "actor": "system@taka.io",
        "timestamp": "2025-01-10T09:00:00Z",
        "details": "AO importé automatiquement depuis BOAMP"
      },
      {
        "action": "stage_changed",
        "actor": "manager@client.fr",
        "timestamp": "2025-01-12T14:30:00Z",
        "details": { "from": "new", "to": "analyzing" }
      },
      {
        "action": "qualified",
        "actor": "agent-qualifier@taka.io",
        "timestamp": "2025-01-14T16:30:00Z",
        "details": { "result": "eligible", "confidence": 0.92 }
      }
    ]
  },
  "meta": { "timestamp": "2025-01-15T14:30:00Z", "request_id": "req_012" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Détail retourné |
| 401 | Non authentifié |
| 403 | Cross-tenant (l'AO n'appartient pas au tenant du JWT) |
| 404 | AO non trouvé ou soft-deleted |

---

### PUT `/tenders/{id}` — Mise à Jour d'un Appel d'Offres

| Attribut | Valeur |
|----------|--------|
| **Méthode** | PUT |
| **Description** | Mise à jour complète (full replace) d'un AO. Champs non fournis = écrasés à NULL. Utiliser PATCH pour mise à jour partielle. |
| **Rôle requis** | `manager`, `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID de l'AO |

**Paramètres (Body) :** Mêmes champs que POST `/tenders`, tous optionnels (partial update via PUT — on garde les champs non fournis).

> **Note** : L'implémentation utilise un merge (PATCH sémantique) — seuls les champs fournis sont mis à jour.

**Exemple Requête :**
```json
PUT /tenders/tdr_001
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "pipeline_stage": "submitted",
  "qualification_summary": "Dossier soumis le 15/01. Attente de réponse."
}
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "id": "tdr_001",
    "title": "Fourniture de matériel informatique — Lot 1",
    "pipeline_stage": "submitted",
    "qualification_result": "eligible",
    "qualification_summary": "Dossier soumis le 15/01. Attente de réponse.",
    "updated_at": "2025-01-15T15:00:00Z"
  },
  "meta": { "timestamp": "2025-01-15T15:00:00Z", "request_id": "req_013" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Mise à jour réussie |
| 400 | `reference_number` déjà utilisé |
| 401 | Non authentifié |
| 403 | Rôle insuffisant OU cross-tenant |
| 404 | AO non trouvé |
| 422 | Validation échouée |
| 500 | Erreur base de données |

---

### DELETE `/tenders/{id}` — Suppression (Soft Delete)

| Attribut | Valeur |
|----------|--------|
| **Méthode** | DELETE |
| **Description** | Soft delete d'un AO (marqué `is_archived=true`). Les données restent en base pour l'audit. Un hard delete nécessite le rôle admin + confirmation explicite. |
| **Rôle requis** | `manager`, `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID de l'AO |

**Paramètres (Query) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `hard` | boolean | Non | Force la suppression définitive (admin uniquement) |

**Exemple Requête :**
```
DELETE /tenders/tdr_001
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "id": "tdr_001",
    "is_archived": true,
    "archived_at": "2025-01-15T15:30:00Z",
    "archived_by": "manager@client.fr",
    "message": "Appel d'offres archivé avec succès"
  },
  "meta": { "timestamp": "2025-01-15T15:30:00Z", "request_id": "req_014" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Soft delete réussi |
| 204 | Hard delete réussi (aucun body) |
| 401 | Non authentifié |
| 403 | Rôle insuffisant OU cross-tenant |
| 404 | AO non trouvé |
| 403 | Hard delete demandé sans rôle admin |

---

### PUT `/tenders/{id}/stage` — Changement de Pipeline Stage

| Attribut | Valeur |
|----------|--------|
| **Méthode** | PUT |
| **Description** | Transition d'un AO vers un nouveau stage du pipeline. Vérifie que le stage cible existe pour le tenant courant. |
| **Rôle requis** | `manager`, `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID de l'AO |

**Paramètres (Body) :**

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `stage` | string | Oui | Nouveau stage (doit exister dans `pipeline_stages`) |
| `reason` | string | Non | Motif du changement (max 1000 caractères) |

**Exemple Requête :**
```json
PUT /tenders/tdr_001/stage
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "stage": "qualified",
  "reason": "Qualification positive — tous les critères sont remplis"
}
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "id": "tdr_001",
    "pipeline_stage": "qualified",
    "previous_stage": "new",
    "stage_changed_at": "2025-01-15T16:00:00Z",
    "stage_changed_by": "manager@client.fr",
    "reason": "Qualification positive — tous les critères sont remplis"
  },
  "meta": { "timestamp": "2025-01-15T16:00:00Z", "request_id": "req_015" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Transition réussie |
| 400 | Stage cible inexistant pour ce tenant |
| 400 | Transition non autorisée (workflow invalide) |
| 401 | Non authentifié |
| 403 | Rôle insuffisant OU cross-tenant |
| 404 | AO non trouvé |
| 422 | Validation échouée |

---

### POST `/tenders/{id}/qualify` — Lancer la Qualification (Agent Qualifieur)

| Attribut | Valeur |
|----------|--------|
| **Méthode** | POST |
| **Description** | Déclenche l'agent qualifieur en arrière-plan. Analyse l'AO et les documents associés pour déterminer l'éligibilité. Retourne immédiatement un job ID pour suivi. |
| **Rôle requis** | `manager`, `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID de l'AO |

**Exemple Requête :**
```
POST /tenders/tdr_001/qualify
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (202) :**
```json
{
  "success": true,
  "data": {
    "job_id": "job_001",
    "status": "queued",
    "message": "Qualification démarrée. Utilisez GET /tenders/tdr_001/qualification pour suivre la progression.",
    "estimated_duration_seconds": 30
  },
  "meta": { "timestamp": "2025-01-15T16:05:00Z", "request_id": "req_016" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 202 | Qualification acceptée (en file d'attente) |
| 400 | Qualification déjà en cours pour cet AO |
| 401 | Non authentifié |
| 403 | Rôle insuffisant OU cross-tenant |
| 404 | AO non trouvé |
| 409 | Aucun document à analyser |
| 500 | Erreur lors du déclenchement de l'agent |

---

### GET `/tenders/{id}/qualification` — Résultat de Qualification

| Attribut | Valeur |
|----------|--------|
| **Méthode** | GET |
| **Description** | Retourne le résultat complet de la dernière qualification d'un AO. |
| **Rôle requis** | `viewer`, `manager`, `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID de l'AO |

**Exemple Requête :**
```
GET /tenders/tdr_001/qualification
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (200) — Qualification terminée :**
```json
{
  "success": true,
  "data": {
    "qualification_id": "qual_001",
    "tender_id": "tdr_001",
    "status": "completed",
    "result": "eligible",
    "confidence": 0.92,
    "started_at": "2025-01-15T16:05:00Z",
    "completed_at": "2025-01-15T16:05:28Z",
    "criteria_analysis": [
      {
        "criterion": "métier_aligné",
        "passed": true,
        "confidence": 0.98,
        "explanation": "Le code CPV 30210000 (Matériel informatique) correspond au cœur de métier."
      },
      {
        "criterion": "seuils_financiers",
        "passed": true,
        "confidence": 0.95,
        "explanation": "Valeur estimée (150k€) dans la fourchette acceptable (50k€ - 500k€)."
      },
      {
        "criterion": "délais_réalisables",
        "passed": true,
        "confidence": 0.88,
        "explanation": "Délai de 35 jours suffisant pour préparer la réponse."
      },
      {
        "criterion": "critères_techniques",
        "passed": true,
        "confidence": 0.85,
        "explanation": "Tous les critères techniques sont satisfaits."
      }
    ],
    "overall_summary": "Cet AO est fortement recommandé. Score de confiance élevé (92%).",
    "raw_agent_output": "[sortie brute du LLM — tronquée si > 10000 caractères]"
  },
  "meta": { "timestamp": "2025-01-15T16:10:00Z", "request_id": "req_017" }
}
```

**Exemple Réponse (200) — Qualification en cours :**
```json
{
  "success": true,
  "data": {
    "qualification_id": "qual_001",
    "tender_id": "tdr_001",
    "status": "running",
    "result": null,
    "started_at": "2025-01-15T16:05:00Z",
    "completed_at": null,
    "progress_percent": 45,
    "current_step": "Analyse des critères techniques..."
  },
  "meta": { "timestamp": "2025-01-15T16:06:00Z", "request_id": "req_018" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Résultat retourné (status: completed / running / failed) |
| 401 | Non authentifié |
| 403 | Cross-tenant |
| 404 | AO non trouvé OU aucune qualification lancée |

---

## 1.3 Endpoints — Documents (`/documents`)

### POST `/tenders/{id}/documents` — Upload de Document

| Attribut | Valeur |
|----------|--------|
| **Méthode** | POST |
| **Content-Type** | `multipart/form-data` |
| **Description** | Upload d'un document associé à un AO. Validation stricte du type MIME et des magic bytes. |
| **Rôle requis** | `manager`, `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID de l'AO parent |

**Paramètres (Body — multipart) :**

| Champ | Type | Requis | Description | Validation |
|-------|------|--------|-------------|------------|
| `file` | File | Oui | Fichier à uploader | Max 50MB, types autorisés vérifiés |
| `description` | string | Non | Description du document | Max 500 caractères |
| `document_type` | string | Non | `notice`, `dce`, `cctp`, `rc`, `other` | Énuméré |

**Types MIME Autorisés :**

| Extension | MIME Type | Magic Bytes |
|-----------|-----------|-------------|
| `.pdf` | `application/pdf` | `%PDF-` |
| `.docx` | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | `PK\x03\x04` |
| `.doc` | `application/msword` | `\xD0\xCF\x11\xE0` |
| `.xlsx` | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | `PK\x03\x04` |
| `.xls` | `application/vnd.ms-excel` | `\xD0\xCF\x11\xE0` |
| `.zip` | `application/zip` | `PK\x03\x04` |
| `.txt` | `text/plain` | — |
| `.csv` | `text/csv` | — |

**Exemple Requête :**
```
POST /tenders/tdr_001/documents
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="dce-complete.pdf"
Content-Type: application/pdf

[binary data]
------WebKitFormBoundary
Content-Disposition: form-data; name="description"

Dossier de consultation des entreprises complet
------WebKitFormBoundary
Content-Disposition: form-data; name="document_type"

dce
------WebKitFormBoundary--
```

**Exemple Réponse (201) :**
```json
{
  "success": true,
  "data": {
    "id": "doc_003",
    "tender_id": "tdr_001",
    "filename": "dce-complete.pdf",
    "original_filename": "dce-complete.pdf",
    "mime_type": "application/pdf",
    "file_size": 5242880,
    "file_size_human": "5.0 MB",
    "description": "Dossier de consultation des entreprises complet",
    "document_type": "dce",
    "storage_path": "tenants/550e8400-e29b-41d4-a716-446655440000/tenders/tdr_001/doc_003_dce-complete.pdf",
    "checksum_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "parsed": false,
    "parse_status": "pending",
    "uploaded_by": "manager@client.fr",
    "uploaded_at": "2025-01-15T16:30:00Z"
  },
  "meta": { "timestamp": "2025-01-15T16:30:00Z", "request_id": "req_020" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 201 | Upload réussi |
| 400 | Type de fichier non autorisé |
| 400 | Fichier trop volumineux (> 50MB) |
| 400 | Magic bytes ne correspondent pas à l'extension |
| 401 | Non authentifié |
| 403 | Rôle insuffisant OU cross-tenant |
| 404 | AO parent non trouvé |
| 413 | Payload trop grand |
| 422 | Paramètre `document_type` invalide |

---

### GET `/documents/{id}` — Détail d'un Document

| Attribut | Valeur |
|----------|--------|
| **Méthode** | GET |
| **Description** | Métadonnées d'un document (sans le contenu binaire). |
| **Rôle requis** | `viewer`, `manager`, `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID du document |

**Exemple Requête :**
```
GET /documents/doc_003
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "id": "doc_003",
    "tender_id": "tdr_001",
    "filename": "dce-complete.pdf",
    "original_filename": "dce-complete.pdf",
    "mime_type": "application/pdf",
    "file_size": 5242880,
    "file_size_human": "5.0 MB",
    "description": "Dossier de consultation des entreprises complet",
    "document_type": "dce",
    "checksum_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "parsed": true,
    "parse_status": "completed",
    "parse_result": {
      "text_extracted": true,
      "pages_count": 45,
      "word_count": 15230,
      "extracted_sections": ["objet", "prix", "délai", "critères_attribution"]
    },
    "uploaded_by": "manager@client.fr",
    "uploaded_at": "2025-01-15T16:30:00Z"
  },
  "meta": { "timestamp": "2025-01-15T16:35:00Z", "request_id": "req_021" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Détail retourné |
| 401 | Non authentifié |
| 403 | Cross-tenant |
| 404 | Document non trouvé |

---

### GET `/documents/{id}/download` — Téléchargement du Fichier

| Attribut | Valeur |
|----------|--------|
| **Méthode** | GET |
| **Description** | Téléchargement du fichier binaire. Retourne le fichier avec le bon Content-Type. |
| **Rôle requis** | `viewer`, `manager`, `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID du document |

**Paramètres (Query) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `disposition` | string | Non | `attachment` (force download) ou `inline` | `attachment` |

**Exemple Requête :**
```
GET /documents/doc_003/download?disposition=attachment
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Réponse (200) :**
```
HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="dce-complete.pdf"
Content-Length: 5242880
X-Checksum-Sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

[binary data]
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Fichier retourné |
| 401 | Non authentifié |
| 403 | Cross-tenant |
| 404 | Document ou fichier non trouvé |
| 410 | Fichier supprimé du stockage |

---

### DELETE `/documents/{id}` — Suppression d'un Document

| Attribut | Valeur |
|----------|--------|
| **Méthode** | DELETE |
| **Description** | Suppression d'un document (fichier + métadonnées). Suppression physique du fichier de stockage. |
| **Rôle requis** | `manager`, `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID du document |

**Exemple Requête :**
```
DELETE /documents/doc_003
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "id": "doc_003",
    "deleted": true,
    "file_removed": true,
    "deleted_by": "manager@client.fr",
    "deleted_at": "2025-01-15T17:00:00Z"
  },
  "meta": { "timestamp": "2025-01-15T17:00:00Z", "request_id": "req_022" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Suppression réussie |
| 401 | Non authentifié |
| 403 | Rôle insuffisant OU cross-tenant |
| 404 | Document non trouvé |

---

### POST `/documents/{id}/parse` — Lancer le Parsing Asynchrone

| Attribut | Valeur |
|----------|--------|
| **Méthode** | POST |
| **Description** | Déclenche le parsing asynchrone d'un document (extraction de texte, structuration). Retourne un job ID. |
| **Rôle requis** | `manager`, `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID du document |

**Exemple Requête :**
```
POST /documents/doc_003/parse
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (202) :**
```json
{
  "success": true,
  "data": {
    "job_id": "job_002",
    "document_id": "doc_003",
    "status": "queued",
    "message": "Parsing démarré. Le document sera analysé en arrière-plan.",
    "estimated_duration_seconds": 15
  },
  "meta": { "timestamp": "2025-01-15T17:05:00Z", "request_id": "req_023" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 202 | Parsing accepté (en file d'attente) |
| 400 | Parsing déjà en cours ou déjà complété |
| 401 | Non authentifié |
| 403 | Rôle insuffisant OU cross-tenant |
| 404 | Document non trouvé |
| 409 | Type de fichier non pris en charge pour le parsing |

---

## 1.4 Endpoints — Pipeline (`/pipeline-stages`)

### GET `/pipeline-stages` — Liste des Stages du Tenant

| Attribut | Valeur |
|----------|--------|
| **Méthode** | GET |
| **Description** | Retourne les stages du pipeline configurés pour le tenant courant, dans l'ordre. |
| **Rôle requis** | `viewer`, `manager`, `admin` |

**Exemple Requête :**
```
GET /pipeline-stages
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "stages": [
      { "id": "stage_001", "name": "new", "label": "Nouveau", "color": "#3498db", "order": 1, "is_default": true },
      { "id": "stage_002", "name": "analyzing", "label": "En analyse", "color": "#f39c12", "order": 2, "is_default": false },
      { "id": "stage_003", "name": "qualified", "label": "Qualifié", "color": "#2ecc71", "order": 3, "is_default": false },
      { "id": "stage_004", "name": "submitted", "label": "Soumis", "color": "#9b59b6", "order": 4, "is_default": false },
      { "id": "stage_005", "name": "won", "label": "Remporté", "color": "#27ae60", "order": 5, "is_default": false },
      { "id": "stage_006", "name": "lost", "label": "Perdu", "color": "#e74c3c", "order": 6, "is_default": false },
      { "id": "stage_007", "name": "abandoned", "label": "Abandonné", "color": "#95a5a6", "order": 7, "is_default": false }
    ]
  },
  "meta": { "timestamp": "2025-01-15T17:10:00Z", "request_id": "req_030" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Liste retournée |
| 401 | Non authentifié |

---

### PUT `/pipeline-stages/reorder` — Réordonner les Stages

| Attribut | Valeur |
|----------|--------|
| **Méthode** | PUT |
| **Description** | Réordonne les stages du pipeline. L'ordre détermine le flux de travail. |
| **Rôle requis** | `admin` uniquement |

**Paramètres (Body) :**

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `stage_orders` | array | Oui | Liste d'objets `{id, order}` |

**Exemple Requête :**
```json
PUT /pipeline-stages/reorder
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "stage_orders": [
    { "id": "stage_001", "order": 1 },
    { "id": "stage_002", "order": 2 },
    { "id": "stage_003", "order": 3 },
    { "id": "stage_004", "order": 4 },
    { "id": "stage_006", "order": 5 },
    { "id": "stage_005", "order": 6 },
    { "id": "stage_007", "order": 7 }
  ]
}
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "stages": [
      { "id": "stage_001", "name": "new", "label": "Nouveau", "order": 1 },
      { "id": "stage_002", "name": "analyzing", "label": "En analyse", "order": 2 },
      { "id": "stage_003", "name": "qualified", "label": "Qualifié", "order": 3 },
      { "id": "stage_004", "name": "submitted", "label": "Soumis", "order": 4 },
      { "id": "stage_006", "name": "lost", "label": "Perdu", "order": 5 },
      { "id": "stage_005", "name": "won", "label": "Remporté", "order": 6 },
      { "id": "stage_007", "name": "abandoned", "label": "Abandonné", "order": 7 }
    ]
  },
  "meta": { "timestamp": "2025-01-15T17:15:00Z", "request_id": "req_031" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Réordonnancement réussi |
| 400 | Un stage ID n'existe pas pour ce tenant |
| 400 | Ordres en doublon |
| 401 | Non authentifié |
| 403 | Rôle non-admin |
| 422 | Structure invalide |

---

## 1.5 Endpoints — Mémoire Vectorielle (`/memory`)

### POST `/memory/search` — Recherche par Similarité

| Attribut | Valeur |
|----------|--------|
| **Méthode** | POST |
| **Description** | Recherche sémantique dans la mémoire vectorielle : la requête textuelle est convertie en embedding puis recherchée via pgvector (similarity search cosine). |
| **Rôle requis** | `viewer`, `manager`, `admin` |

**Paramètres (Body) :**

| Champ | Type | Requis | Description | Validation |
|-------|------|--------|-------------|------------|
| `query` | string | Oui | Requête textuelle | 1-1000 caractères |
| `limit` | integer | Non | Nombre de résultats (max 50) | 1-50, défaut: 10 |
| `threshold` | float | Non | Score minimum de similarité | 0.0-1.0, défaut: 0.7 |
| `filter_type` | string | Non | Filtrer par type d'entrée | `tender`, `document`, `qualification`, `company_knowledge` |
| `filter_tender_id` | string | Non | Restreindre à un AO spécifique | UUID valide |

**Exemple Requête :**
```json
POST /memory/search
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "query": "matériel informatique et prestations de maintenance réseau",
  "limit": 10,
  "threshold": 0.75,
  "filter_type": "tender"
}
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "query_embedding_duration_ms": 245,
    "results": [
      {
        "id": "mem_001",
        "content": "Fourniture de matériel informatique — Lot 1. Postes de travail, écrans, claviers...",
        "source_type": "tender",
        "source_id": "tdr_001",
        "source_title": "Fourniture de matériel informatique — Lot 1",
        "similarity_score": 0.92,
        "metadata": {
          "tender_reference": "2025-INFORMATIQUE-042",
          "issuing_organization": "Ministère de la Transition Écologique",
          "deadline": "2025-02-15T17:00:00Z"
        },
        "created_at": "2025-01-10T09:05:00Z"
      },
      {
        "id": "mem_002",
        "content": "Maintenance préventive et corrective des équipements réseau et informatiques...",
        "source_type": "tender",
        "source_id": "tdr_003",
        "source_title": "Maintenance des équipements réseau 2025",
        "similarity_score": 0.84,
        "metadata": {
          "tender_reference": "2025-RESEAU-003",
          "issuing_organization": "Département de la Gironde",
          "deadline": "2025-04-30T17:00:00Z"
        },
        "created_at": "2025-01-15T14:50:00Z"
      }
    ]
  },
  "meta": {
    "timestamp": "2025-01-15T17:20:00Z",
    "request_id": "req_040",
    "pagination": { "limit": 10, "offset": 0, "total": 2 }
  }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Résultats retournés (liste peut être vide) |
| 401 | Non authentifié |
| 422 | `query` vide ou trop long |
| 500 | Erreur du service d'embedding |

---

### GET `/memory/{id}` — Détail d'une Entrée Mémoire

| Attribut | Valeur |
|----------|--------|
| **Méthode** | GET |
| **Description** | Retourne le détail d'une entrée mémoire vectorielle. |
| **Rôle requis** | `viewer`, `manager`, `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID de l'entrée mémoire |

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "id": "mem_001",
    "content": "Fourniture de matériel informatique — Lot 1. Postes de travail, écrans, claviers...",
    "embedding_model": "text-embedding-3-small",
    "embedding_dimensions": 1536,
    "source_type": "tender",
    "source_id": "tdr_001",
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
    "metadata": {
      "tender_reference": "2025-INFORMATIQUE-042",
      "issuing_organization": "Ministère de la Transition Écologique"
    },
    "created_at": "2025-01-10T09:05:00Z",
    "chunk_index": 0,
    "total_chunks": 3
  },
  "meta": { "timestamp": "2025-01-15T17:25:00Z", "request_id": "req_041" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Détail retourné |
| 401 | Non authentifié |
| 403 | Cross-tenant |
| 404 | Entrée non trouvée |

---

### DELETE `/memory/{id}` — Suppression (RGPD)

| Attribut | Valeur |
|----------|--------|
| **Méthode** | DELETE |
| **Description** | Suppression d'une entrée mémoire (droit à l'oubli RGPD). L'entrée est définitivement supprimée de pgvector. Nécessite le rôle admin ou une justification RGPD. |
| **Rôle requis** | `admin` |

**Paramètres (Path) :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `id` | string | Oui | UUID de l'entrée mémoire |

**Paramètres (Body) :**

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `deletion_reason` | string | Oui | Motif de suppression (`rgpd_request`, `data_error`, `other`) |
| `justification` | string | Non | Détails (requis si `other`) |

**Exemple Requête :**
```json
DELETE /memory/mem_001
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "deletion_reason": "rgpd_request",
  "justification": "Demande d'exercice du droit à l'oubli — email du demandeur"
}
```

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "id": "mem_001",
    "deleted": true,
    "deletion_reason": "rgpd_request",
    "deleted_by": "admin@client.fr",
    "deleted_at": "2025-01-15T17:30:00Z",
    "rgpd_compliant": true
  },
  "meta": { "timestamp": "2025-01-15T17:30:00Z", "request_id": "req_042" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Suppression réussie |
| 401 | Non authentifié |
| 403 | Rôle non-admin |
| 404 | Entrée non trouvée |
| 422 | `deletion_reason` manquant |

---

## 1.6 Endpoints — Administration (`/admin`)

> Tous les endpoints `/admin/*` nécessitent le rôle `admin`. Un `viewer` ou `manager` reçoit systématiquement un **403**.

### GET `/admin/tenants` — Liste des Tenants

| Attribut | Valeur |
|----------|--------|
| **Méthode** | GET |
| **Description** | Liste tous les tenants (pour super-admin) ou le tenant courant (pour admin de tenant). |
| **Rôle requis** | `admin` |

**Paramètres (Query) :**

| Paramètre | Type | Requis | Description | Défaut |
|-----------|------|--------|-------------|--------|
| `limit` | integer | Non | Pagination | 20 |
| `offset` | integer | Non | Offset | 0 |
| `is_active` | boolean | Non | Filtrer par statut | — |

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Acme Corp",
        "slug": "acme-corp",
        "contact_email": "contact@acme.fr",
        "is_active": true,
        "user_count": 5,
        "tender_count": 47,
        "storage_used_mb": 256.5,
        "created_at": "2024-11-01T08:00:00Z",
        "updated_at": "2025-01-10T12:00:00Z"
      }
    ]
  },
  "meta": {
    "timestamp": "2025-01-15T17:35:00Z",
    "request_id": "req_050",
    "pagination": { "limit": 20, "offset": 0, "total": 1 }
  }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Liste retournée |
| 401 | Non authentifié |
| 403 | Rôle non-admin |

---

### POST `/admin/tenants` — Création d'un Tenant

| Attribut | Valeur |
|----------|--------|
| **Méthode** | POST |
| **Description** | Crée un nouveau tenant avec ses stages de pipeline par défaut. |
| **Rôle requis** | `admin` (super-admin uniquement) |

**Paramètres (Body) :**

| Champ | Type | Requis | Description | Validation |
|-------|------|--------|-------------|------------|
| `name` | string | Oui | Nom du tenant | 2-200 caractères |
| `slug` | string | Oui | Identifiant URL-friendly | `^[a-z0-9-]+$`, unique |
| `contact_email` | string | Oui | Email de contact | Email valide |
| `plan` | string | Non | `free`, `starter`, `pro`, `enterprise` | Défaut: `free` |

**Exemple Requête :**
```json
POST /admin/tenants
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "name": "Construction Dupont SARL",
  "slug": "construction-dupont",
  "contact_email": "admin@dupont-construction.fr",
  "plan": "starter"
}
```

**Exemple Réponse (201) :**
```json
{
  "success": true,
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "Construction Dupont SARL",
    "slug": "construction-dupont",
    "contact_email": "admin@dupont-construction.fr",
    "plan": "starter",
    "is_active": true,
    "pipeline_stages": [
      { "name": "new", "label": "Nouveau", "order": 1, "is_default": true },
      { "name": "analyzing", "label": "En analyse", "order": 2 },
      { "name": "qualified", "label": "Qualifié", "order": 3 },
      { "name": "submitted", "label": "Soumis", "order": 4 },
      { "name": "won", "label": "Remporté", "order": 5 },
      { "name": "lost", "label": "Perdu", "order": 6 },
      { "name": "abandoned", "label": "Abandonné", "order": 7 }
    ],
    "created_at": "2025-01-15T17:40:00Z"
  },
  "meta": { "timestamp": "2025-01-15T17:40:00Z", "request_id": "req_051" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 201 | Tenant créé |
| 400 | `slug` déjà utilisé |
| 401 | Non authentifié |
| 403 | Rôle non-admin ou non super-admin |
| 422 | Validation échouée |

---

### GET `/admin/users` — Liste des Utilisateurs

| Attribut | Valeur |
|----------|--------|
| **Méthode** | GET |
| **Description** | Liste les utilisateurs du tenant courant (admin de tenant) ou de tous les tenants (super-admin). |
| **Rôle requis** | `admin` |

**Paramètres (Query) :**

| Paramètre | Type | Requis | Description | Défaut |
|-----------|------|--------|-------------|--------|
| `limit` | integer | Non | Pagination | 20 |
| `offset` | integer | Non | Offset | 0 |
| `tenant_id` | UUID | Non | Filtrer par tenant (super-admin) | — |
| `role` | string | Non | Filtrer par rôle | — |
| `is_active` | boolean | Non | Filtrer par statut | — |

**Exemple Réponse (200) :**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "usr_001",
        "email": "manager@client.fr",
        "full_name": "Jean Dupont",
        "role": "manager",
        "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
        "tenant_name": "Acme Corp",
        "is_active": true,
        "last_login_at": "2025-01-15T14:30:00Z",
        "created_at": "2024-12-01T10:00:00Z"
      },
      {
        "id": "usr_002",
        "email": "viewer@client.fr",
        "full_name": "Marie Martin",
        "role": "viewer",
        "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
        "tenant_name": "Acme Corp",
        "is_active": true,
        "last_login_at": "2025-01-14T09:00:00Z",
        "created_at": "2024-12-15T11:00:00Z"
      }
    ]
  },
  "meta": {
    "timestamp": "2025-01-15T17:45:00Z",
    "request_id": "req_052",
    "pagination": { "limit": 20, "offset": 0, "total": 5 }
  }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Liste retournée |
| 401 | Non authentifié |
| 403 | Rôle non-admin |
| 403 | Admin de tenant tentant de voir les users d'un autre tenant |

---

### POST `/admin/users` — Création d'un Utilisateur

| Attribut | Valeur |
|----------|--------|
| **Méthode** | POST |
| **Description** | Crée un nouvel utilisateur dans un tenant. Le mot de passe est généré automatiquement et envoyé par email (ou retourné en dev). |
| **Rôle requis** | `admin` |

**Paramètres (Body) :**

| Champ | Type | Requis | Description | Validation |
|-------|------|--------|-------------|------------|
| `email` | string | Oui | Email | Unique, email valide |
| `full_name` | string | Oui | Nom complet | 2-200 caractères |
| `role` | string | Oui | `viewer`, `manager`, `admin` | Énuméré |
| `tenant_id` | UUID | Non | Tenant (défaut: tenant de l'admin) | — |
| `password` | string | Non | Mot de passe temporaire | 8-128 caractères, auto-généré si absent |
| `is_active` | boolean | Non | Compte actif | `true` |

**Exemple Requête :**
```json
POST /admin/users
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "email": "nouveau@client.fr",
  "full_name": "Pierre Lefebvre",
  "role": "viewer",
  "password": "TempPass2025!"
}
```

**Exemple Réponse (201) :**
```json
{
  "success": true,
  "data": {
    "id": "usr_006",
    "email": "nouveau@client.fr",
    "full_name": "Pierre Lefebvre",
    "role": "viewer",
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
    "is_active": true,
    "created_at": "2025-01-15T17:50:00Z",
    "message": "Utilisateur créé. Mot de passe temporaire envoyé par email."
  },
  "meta": { "timestamp": "2025-01-15T17:50:00Z", "request_id": "req_053" }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 201 | Utilisateur créé |
| 400 | Email déjà utilisé |
| 401 | Non authentifié |
| 403 | Rôle non-admin OU tentative de créer un user dans un autre tenant (non super-admin) |
| 422 | Validation échouée |

---

### GET `/admin/audit-logs` — Audit Trail Complet

| Attribut | Valeur |
|----------|--------|
| **Méthode** | GET |
| **Description** | Accès complet au journal d'audit. Filtres par date, utilisateur, action, ressource. Supporte l'export CSV/PDF. |
| **Rôle requis** | `admin` |

**Paramètres (Query) :**

| Paramètre | Type | Requis | Description | Défaut |
|-----------|------|--------|-------------|--------|
| `limit` | integer | Non | Pagination (max 1000) | 50 |
| `offset` | integer | Non | Offset | 0 |
| `from_date` | ISO date | Non | Date de début | — |
| `to_date` | ISO date | Non | Date de fin | — |
| `user_id` | UUID | Non | Filtrer par utilisateur | — |
| `action` | string | Non | `create`, `update`, `delete`, `login`, `logout`, `qualify`, `stage_change`, `cross_tenant_attempt` | — |
| `resource_type` | string | Non | `tender`, `document`, `user`, `tenant`, `memory` | — |
| `resource_id` | string | Non | ID de la ressource | — |
| `format` | string | Non | `json`, `csv`, `pdf` | `json` |

**Exemple Requête :**
```
GET /admin/audit-logs?from_date=2025-01-01&action=login&limit=5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple Réponse (200) — Format JSON :**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "audit_001",
        "timestamp": "2025-01-15T14:30:00Z",
        "user_id": "usr_001",
        "user_email": "manager@client.fr",
        "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
        "action": "login",
        "resource_type": "session",
        "resource_id": "sess_001",
        "details": {
          "ip_address": "192.168.1.100",
          "user_agent": "Mozilla/5.0 (X11; Linux x86_64)...",
          "method": "password",
          "success": true
        },
        "hash_chain": "sha256:abc123...def456",
        "previous_hash": "sha256:xyz789...uvw012"
      },
      {
        "id": "audit_002",
        "timestamp": "2025-01-15T14:45:00Z",
        "user_id": "usr_001",
        "user_email": "manager@client.fr",
        "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
        "action": "create",
        "resource_type": "tender",
        "resource_id": "tdr_003",
        "details": {
          "title": "Maintenance des équipements réseau 2025",
          "reference_number": "2025-RESEAU-003"
        },
        "hash_chain": "sha256:def456...ghi789",
        "previous_hash": "sha256:abc123...def456"
      },
      {
        "id": "audit_003",
        "timestamp": "2025-01-15T15:02:00Z",
        "user_id": "usr_002",
        "user_email": "viewer@client.fr",
        "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
        "action": "cross_tenant_attempt",
        "resource_type": "tender",
        "resource_id": "tdr_099",
        "details": {
          "target_tenant_id": "770e8400-e29b-41d4-a716-446655440099",
          "ip_address": "192.168.1.105",
          "blocked": true
        },
        "hash_chain": "sha256:ghi789...jkl012",
        "previous_hash": "sha256:def456...ghi789"
      }
    ]
  },
  "meta": {
    "timestamp": "2025-01-15T17:55:00Z",
    "request_id": "req_054",
    "pagination": { "limit": 5, "offset": 0, "total": 1234 }
  }
}
```

**Codes de Réponse :**

| Code | Condition |
|------|-----------|
| 200 | Logs retournés (JSON) |
| 200 | Fichier CSV/PDF retourné (Content-Disposition: attachment) |
| 401 | Non authentifié |
| 403 | Rôle non-admin |
| 413 | Demande d'export trop volumineuse (> 50000 lignes) |

---


---

## 2. Architecture de Sécurité

---

### 2.1 JWT Authentication

#### 2.1.1 Structure du Token JWT

TAKA OS utilise **python-jose** avec l'algorithme **HS256** (HMAC-SHA256) en phase initiale. Migration vers RS256 recommandée en production multi-instance.

**Payload du Access Token :**

```json
{
  "sub": "usr_001",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "manager",
  "jti": "jwt_abc123unique",
  "iat": 1705325100,
  "exp": 1705326000,
  "type": "access"
}
```

| Claim | Description | Source |
|-------|-------------|--------|
| `sub` (subject) | ID utilisateur | Base de données |
| `tenant_id` | UUID du tenant | Base de données (table users) |
| `role` | Rôle de l'utilisateur | Base de données (`viewer` / `manager` / `admin`) |
| `jti` (JWT ID) | Identifiant unique du token | UUID v4 généré à la création |
| `iat` (issued at) | Timestamp de création | `datetime.utcnow()` |
| `exp` (expiration) | Timestamp d'expiration | `iat + 15 minutes` |
| `type` | Type de token | `"access"` ou `"refresh"` |

**Payload du Refresh Token :**

```json
{
  "sub": "usr_001",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "jti": "jwt_refresh_xyz789",
  "iat": 1705325100,
  "exp": 1705930800,
  "type": "refresh",
  "token_family": "fam_550e8400-e29b-41d4"
}
```

#### 2.1.2 Durée de Vie

| Token | Durée | Usage |
|-------|-------|-------|
| **Access Token** | 15 minutes (900s) | Chaque requête API — header `Authorization` |
| **Refresh Token** | 7 jours (604800s) | Renouvellement du access token — cookie httpOnly |

#### 2.1.3 Rotation des Refresh Tokens

```
┌─────────────┐     ┌─────────────────────┐     ┌──────────────────────┐
│  Client     │────▶│  POST /auth/refresh │────▶│  Refresh Token RT#1  │
│  (cookie    │     │  Cookie: RT#1       │     │  présenté            │
│   RT#1)     │◄────│                     │◄────│                      │
└─────────────┘     └─────────────────────┘     └──────────────────────┘
       │                                           │
       │◄── Nouveau Access Token + RT#2 (cookie)   │
       │                                           │
       │     RT#1 est INVALIDÉ (blacklist)         │ RT#2 est stocké
       │     RT#2 est stocké (nouveau cookie)      │
```

**Règles de rotation :**
- Chaque utilisation d'un refresh token valide génère un **nouveau couple** (access token, refresh token)
- L'ancien refresh token est **immédiatement révoqué** (blacklist)
- Tous les refresh tokens d'une même session partagent un `token_family` UUID
- **Détection de vol** : si un refresh token déjà utilisé est représenté → révocation de toute la famille + alerte

#### 2.1.4 Stockage Côté Client

| Token | Mécanisme | Attributs de Sécurité |
|-------|-----------|----------------------|
| **Access Token** | Header `Authorization: Bearer <token>` | Mémoire volatile (jamais localStorage) |
| **Refresh Token** | Cookie `refresh_token` | `HttpOnly; Secure; SameSite=Strict; Path=/auth/refresh` |

**Pourquoi pas localStorage pour l'access token ?**
- localStorage est vulnérable au XSS (script malveillant peut exfiltrer les tokens)
- L'access token en mémoire volatile (React state / variable JS) réduit la fenêtre d'exposition au strict minimum
- En cas de XSS, l'attaquant ne peut pas accéder au refresh token (httpOnly cookie)

#### 2.1.5 Middleware d'Authentification (FastAPI)

```python
# app/core/security.py
from jose import jwt, JWTError
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dépendance FastAPI : extrait et valide le JWT du header Authorization.
    Retourne l'objet User ou lève une exception 401/403.
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="AUTHENTICATION_REQUIRED")

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            key=settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="TOKEN_EXPIRED")
    except JWTError:
        raise HTTPException(status_code=401, detail="TOKEN_INVALID")

    # Vérification du type de token
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="TOKEN_TYPE_INVALID")

    # Vérification blacklist (token révoqué suite à logout)
    jti = payload.get("jti")
    if await is_token_revoked(jti):
        raise HTTPException(status_code=401, detail="TOKEN_REVOKED")

    # Récupération de l'utilisateur
    user = await get_user_by_id(payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="USER_INACTIVE")

    # Injection du tenant_id dans le contexte de requête
    request.state.tenant_id = payload["tenant_id"]
    request.state.user_role = payload["role"]

    return user
```

#### 2.1.6 Gestion du Logout (Révocation)

```python
# app/core/security.py

# Blacklist en Redis (TTL = durée de vie restante du token)
async def revoke_token(jti: str, expires_at: datetime) -> None:
    """Ajoute un JTI à la blacklist avec le TTL approprié."""
    ttl_seconds = int((expires_at - datetime.utcnow()).total_seconds())
    if ttl_seconds > 0:
        await redis.setex(f"token_blacklist:{jti}", ttl_seconds, "revoked")

async def is_token_revoked(jti: str) -> bool:
    """Vérifie si un JTI est dans la blacklist."""
    return await redis.exists(f"token_blacklist:{jti}") > 0
```

---

### 2.2 RBAC (Role-Based Access Control)

#### 2.2.1 Les 3 Rôles

| Rôle | Description | Capacités |
|------|-------------|-----------|
| **viewer** | Lecture seule | Consulter les AO, documents, pipeline, résultats de qualification, recherche mémoire |
| **manager** | CRUD + qualification | Tout ce que viewer fait + créer/modifier/supprimer des AO, uploader des documents, lancer des qualifications, changer les stages |
| **admin** | Tout + administration | Tout ce que manager fait + gérer les utilisateurs, configurer le pipeline, accéder aux audit logs, supprimer des entrées mémoire (RGPD) |

#### 2.2.2 Héritage des Permissions

```
                    ┌─────────────┐
                    │    admin    │  ← admin hérite de manager
                    │  (tout)     │
                    └──────┬──────┘
                           │ hérite
                    ┌──────▼──────┐
                    │   manager   │  ← manager hérite de viewer
                    │  (CRUD +    │
                    │   qualif)   │
                    └──────┬──────┘
                           │ hérite
                    ┌──────▼──────┐
                    │   viewer    │  ← base : lecture seule
                    │  (read)     │
                    └─────────────┘
```

#### 2.2.3 Matrice des Permissions (Endpoint × Rôle)

| Endpoint | viewer | manager | admin |
|----------|:------:|:-------:|:-----:|
| **Auth** ||||
| `POST /auth/dev-login` | ✅ | ✅ | ✅ |
| `POST /auth/login` | ✅ | ✅ | ✅ |
| `POST /auth/refresh` | ✅ | ✅ | ✅ |
| `GET /auth/me` | ✅ | ✅ | ✅ |
| `POST /auth/logout` | ✅ | ✅ | ✅ |
| **Tenders** ||||
| `GET /tenders` | ✅ | ✅ | ✅ |
| `POST /tenders` | ❌ | ✅ | ✅ |
| `GET /tenders/{id}` | ✅ | ✅ | ✅ |
| `PUT /tenders/{id}` | ❌ | ✅ | ✅ |
| `DELETE /tenders/{id}` | ❌ | ✅ | ✅ |
| `PUT /tenders/{id}/stage` | ❌ | ✅ | ✅ |
| `POST /tenders/{id}/qualify` | ❌ | ✅ | ✅ |
| `GET /tenders/{id}/qualification` | ✅ | ✅ | ✅ |
| **Documents** ||||
| `POST /tenders/{id}/documents` | ❌ | ✅ | ✅ |
| `GET /documents/{id}` | ✅ | ✅ | ✅ |
| `GET /documents/{id}/download` | ✅ | ✅ | ✅ |
| `DELETE /documents/{id}` | ❌ | ✅ | ✅ |
| `POST /documents/{id}/parse` | ❌ | ✅ | ✅ |
| **Pipeline** ||||
| `GET /pipeline-stages` | ✅ | ✅ | ✅ |
| `PUT /pipeline-stages/reorder` | ❌ | ❌ | ✅ |
| **Memory** ||||
| `POST /memory/search` | ✅ | ✅ | ✅ |
| `GET /memory/{id}` | ✅ | ✅ | ✅ |
| `DELETE /memory/{id}` | ❌ | ❌ | ✅ |
| **Admin** ||||
| `GET /admin/tenants` | ❌ | ❌ | ✅ |
| `POST /admin/tenants` | ❌ | ❌ | ✅ |
| `GET /admin/users` | ❌ | ❌ | ✅ |
| `POST /admin/users` | ❌ | ❌ | ✅ |
| `GET /admin/audit-logs` | ❌ | ❌ | ✅ |

> **Légende** : ✅ = accès autorisé | ❌ = accès refusé (403)

#### 2.2.4 Middleware RBAC (FastAPI)

```python
# app/core/rbac.py
from fastapi import Depends, HTTPException
from functools import wraps
from enum import Enum

class Role(str, Enum):
    VIEWER = "viewer"
    MANAGER = "manager"
    ADMIN = "admin"

# Héritage : chaque rôle a un niveau numérique
ROLE_LEVELS = {
    Role.VIEWER: 1,
    Role.MANAGER: 2,
    Role.ADMIN: 3,
}

def require_role(min_role: Role):
    """
    Dépendance FastAPI qui vérifie que l'utilisateur a au moins le rôle requis.
    Gère l'héritage automatiquement (admin >= manager >= viewer).
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_level = ROLE_LEVELS.get(Role(current_user.role), 0)
        required_level = ROLE_LEVELS[min_role]

        if user_level < required_level:
            # Log de la tentative d'accès non autorisé
            await audit_log(
                action="unauthorized_access_attempt",
                user_id=current_user.id,
                tenant_id=current_user.tenant_id,
                details={
                    "required_role": min_role.value,
                    "actual_role": current_user.role,
                    "endpoint": request.url.path
                }
            )
            raise HTTPException(
                status_code=403,
                detail="INSUFFICIENT_PERMISSIONS"
            )
        return current_user
    return role_checker

# Aliases pour plus de lisibilité
require_viewer = require_role(Role.VIEWER)      # Tout utilisateur authentifié
require_manager = require_role(Role.MANAGER)    # manager + admin
require_admin = require_role(Role.ADMIN)        # admin uniquement
```

#### 2.2.5 Utilisation dans les Routes

```python
# app/routers/tenders.py
from fastapi import APIRouter, Depends
from app.core.rbac import require_manager, require_viewer

router = APIRouter(prefix="/tenders", tags=["tenders"])

@router.get("/", dependencies=[Depends(require_viewer)])
async def list_tenders(...):
    ...

@router.post("/", dependencies=[Depends(require_manager)])
async def create_tender(...):
    ...

@router.put("/{id}/stage", dependencies=[Depends(require_manager)])
async def change_stage(...):
    ...

# app/routers/admin.py
from app.core.rbac import require_admin

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])

@router.get("/audit-logs")
async def get_audit_logs(...):
    ...
```

---

### 2.3 Multi-Tenancy

#### 2.3.1 Principe d'Isolation

TAKA OS utilise le **multi-tenancy par row-level filtering** (shared database, isolated schema logique). Chaque table contient une colonne `tenant_id`. Aucune requête ne peut contourner ce filtre.

```
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL 15                             │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Schema public                          │   │
│  │                                                     │   │
│  │   tenders              documents        users       │   │
│  │   ├─ id                ├─ id            ├─ id      │   │
│  │   ├─ tenant_id  ◄──────┼─ tenant_id    ├─ tenant_id│  │
│  │   ├─ title             ├─ tender_id     ├─ email    │   │
│  │   ├─ ...               ├─ ...           ├─ role     │   │
│  │                                                      │   │
│  │   pipeline_stages      audit_logs       memory_vectors│  │
│  │   ├─ id                ├─ id            ├─ id       │   │
│  │   ├─ tenant_id  ◄──────┼─ tenant_id    ├─ tenant_id │  │
│  │   └─ ...               └─ ...           └─ embedding │  │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

#### 2.3.2 Détermination du Tenant

Le `tenant_id` est extrait du JWT (claim `tenant_id`) à chaque requête. Il est injecté dans le `request.state` par le middleware d'authentification.

```python
# app/core/tenant.py
from fastapi import Request, HTTPException

class TenantContext:
    """Contexte de tenant injecté automatiquement dans chaque requête."""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id

    @classmethod
    async def from_request(cls, request: Request) -> "TenantContext":
        tenant_id = getattr(request.state, "tenant_id", None)
        if not tenant_id:
            raise HTTPException(status_code=401, detail="TENANT_NOT_DETERMINED")
        return cls(tenant_id)

# Dépendance FastAPI
async def get_tenant_context(request: Request) -> TenantContext:
    return await TenantContext.from_request(request)
```

#### 2.3.3 Row-Level Filtering (SQLAlchemy 2.0 Async)

```python
# app/db/base.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Select
from fastapi import Request

class TenantScopedQuery:
    """
    Mixin qui ajoute automatiquement le filtre tenant_id
    sur toutes les requêtes SELECT, INSERT, UPDATE, DELETE.
    """

    @classmethod
    def with_tenant(cls, stmt: Select, tenant_id: str) -> Select:
        """Ajoute le filtre tenant_id à une requête SELECT."""
        return stmt.where(cls.tenant_id == tenant_id)

    @classmethod
    async def get_by_id_for_tenant(
        cls,
        session: AsyncSession,
        obj_id: str,
        tenant_id: str
    ):
        """Récupère un objet par ID en vérifiant le tenant."""
        result = await session.execute(
            select(cls).where(cls.id == obj_id, cls.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()
```

```python
# app/models/tender.py
from sqlalchemy import String, Text, Numeric, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TenantScopedQuery

class Tender(Base, TenantScopedQuery):
    __tablename__ = "tenders"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)  # ULID
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    reference_number: Mapped[str] = mapped_column(String(100), nullable=True)
    issuing_organization: Mapped[str] = mapped_column(String(300), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    pipeline_stage: Mapped[str] = mapped_column(String(50), nullable=False, default="new")
    qualification_result: Mapped[str] = mapped_column(String(20), nullable=True)
    estimated_value: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    cpv_code: Mapped[str] = mapped_column(String(8), nullable=True)
    notice_url: Mapped[str] = mapped_column(String(1000), nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
```

#### 2.3.4 Détection Cross-Tenant (Zero Trust)

```python
# app/core/tenant.py

async def enforce_tenant_isolation(
    resource_tenant_id: str,
    request_tenant_id: str,
    resource_type: str,
    resource_id: str,
    user_id: str
) -> None:
    """
    Vérifie que l'utilisateur accède uniquement aux ressources de son tenant.
    En cas de tentative cross-tenant : 403 + log audit immédiat.
    """
    if resource_tenant_id != request_tenant_id:
        # Log sécurité critique
        await audit_log(
            action="cross_tenant_attempt",
            user_id=user_id,
            tenant_id=request_tenant_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details={
                "attempted_tenant_id": resource_tenant_id,
                "user_tenant_id": request_tenant_id,
                "severity": "high",
                "blocked": True
            }
        )
        raise HTTPException(
            status_code=403,
            detail="CROSS_TENANT_ACCESS"
        )
```

#### 2.3.5 Diagramme de Flux — Requête Multi-Tenant

```
┌─────────┐   ┌──────────────────────────────────────────────────────────┐
│ Client  │   │                         Serveur TAKA OS                │
└────┬────┘   └────┬──────────────┬──────────────┬──────────────┬──────┘
     │             │              │              │              │
     │  Bearer     │              │              │              │
     │  Token +    │              │              │              │
     │  Cookie     │              │              │              │
     │             │              │              │              │
     │────────────▶│  1. Auth     │              │              │
     │             │     Middleware              │              │
     │             │     (valide JWT,            │              │
     │             │      extrait tenant_id)     │              │
     │             │              │              │              │
     │             │─────────────▶│  2. RBAC     │              │
     │             │              │     Middleware              │
     │             │              │     (vérifie rôle)          │
     │             │              │              │              │
     │             │              │─────────────▶│  3. Tenant   │
     │             │              │              │     Filter   │
     │             │              │              │     (ajoute  │
     │             │              │              │      WHERE   │
     │             │              │              │      tenant) │
     │             │              │              │              │
     │             │              │              │─────────────▶│  4. DB
     │             │              │              │              │     Query
     │             │              │              │              │     (filtrée)
     │             │              │              │◄─────────────│
     │             │              │              │              │
     │             │              │◄─────────────│              │
     │             │◄─────────────│              │              │
     │◄────────────│  5. Response │              │              │
     │             │   (JSON)     │              │              │
     │             │              │              │              │
```

---

### 2.4 Audit Trail

#### 2.4.1 Philosophie : Append-Only, Immuable

L'audit trail est **sacré**. Jamais de `UPDATE` ou `DELETE` sur la table `audit_logs`. Chaque ligne est définitivement gravée.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Table audit_logs                             │
├──────────┬─────────────┬────────┬────────────┬─────────┬──────────┤
│ id (PK)  │ timestamp   │ user_id│ action     │ tenant  │ hash     │
├──────────┼─────────────┼────────┼────────────┼─────────┼──────────┤
│ audit_001│ 2025-01-15  │ usr_001│ login      │ tenant_1│ sha256:  │
│          │ 14:30:00Z   │        │            │         │  abc...  │
├──────────┼─────────────┼────────┼────────────┼─────────┼──────────┤
│ audit_002│ 2025-01-15  │ usr_001│ create     │ tenant_1│ sha256:  │
│          │ 14:45:00Z   │        │            │         │  def...  │
│          │             │        │            │         │  (hash   │
│          │             │        │            │         │  de 001) │
├──────────┼─────────────┼────────┼────────────┼─────────┼──────────┤
│ audit_003│ 2025-01-15  │ usr_002│cross_tenant│ tenant_1│ sha256:  │
│          │ 15:02:00Z   │        │_attempt    │         │  ghi...  │
│          │             │        │            │         │  (hash   │
│          │             │        │            │         │  de 002) │
└──────────┴─────────────┴────────┴────────────┴─────────┴──────────┘
```

#### 2.4.2 Schéma de la Table

```python
# app/models/audit.py
from sqlalchemy import String, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)  # ULID
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        index=True
    )
    user_id: Mapped[str] = mapped_column(String(26), nullable=True, index=True)
    user_email: Mapped[str] = mapped_column(String(255), nullable=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[str] = mapped_column(String(26), nullable=True)
    details: Mapped[dict] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str] = mapped_column(Text, nullable=True)

    # Hash chain pour l'immuabilité
    previous_hash: Mapped[str] = mapped_column(String(64), nullable=True)
    current_hash: Mapped[str] = mapped_column(String(64), nullable=False)
```

#### 2.4.3 Hash Chain (Chaîne d'Intégrité)

Chaque log contient un hash SHA-256 du log précédent, formant une chaîne cryptographique. Toute altération d'un log historique casse la chaîne.

```python
# app/core/audit.py
import hashlib
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def compute_hash_chain(
    session: AsyncSession,
    log_data: dict
) -> str:
    """
    Calcule le hash d'un log d'audit en incluant le hash du log précédent.
    Forme une chaîne immuable : alterer un log casse tous les suivants.
    """
    # Récupérer le dernier log pour ce tenant
    result = await session.execute(
        select(AuditLog)
        .where(AuditLog.tenant_id == log_data["tenant_id"])
        .order_by(AuditLog.timestamp.desc())
        .limit(1)
    )
    last_log = result.scalar_one_or_none()

    previous_hash = last_log.current_hash if last_log else "0" * 64

    # Construire le payload hashé
    hash_payload = {
        "timestamp": log_data["timestamp"].isoformat(),
        "user_id": log_data.get("user_id"),
        "action": log_data["action"],
        "resource_type": log_data.get("resource_type"),
        "resource_id": log_data.get("resource_id"),
        "details": log_data.get("details"),
        "previous_hash": previous_hash
    }

    # Hash SHA-256 canonique
    canonical = json.dumps(hash_payload, sort_keys=True, ensure_ascii=False)
    current_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    return current_hash, previous_hash
```

#### 2.4.4 Middleware d'Audit Automatique

```python
# app/core/audit.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware qui log automatiquement toutes les actions
    de création, modification et suppression.
    """

    AUDIT_ACTIONS = {
        "POST": "create",
        "PUT": "update",
        "PATCH": "update",
        "DELETE": "delete",
    }

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        method = request.method
        if method in self.AUDIT_ACTIONS and hasattr(request.state, "user"):
            action = self.AUDIT_ACTIONS[method]
            user = request.state.user

            # Extraire le resource_type et resource_id du path
            path_parts = request.url.path.strip("/").split("/")
            resource_type = path_parts[0] if path_parts else "unknown"
            resource_id = path_parts[1] if len(path_parts) > 1 else None

            await audit_log(
                action=action,
                user_id=user.id,
                user_email=user.email,
                tenant_id=user.tenant_id,
                resource_type=resource_type,
                resource_id=resource_id,
                details={
                    "method": method,
                    "path": str(request.url.path),
                    "status_code": response.status_code,
                },
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent")
            )

        return response
```

#### 2.4.5 Actions Auditées

| Action | Quand | Détails loggués |
|--------|-------|-----------------|
| `login` | Connexion réussie | IP, user-agent, méthode (password/dev) |
| `login_failed` | Tentative échouée | IP, email tenté, raison de l'échec |
| `logout` | Déconnexion | Session ID révoqué |
| `create` | POST réussi | Ressource créée, champs clés |
| `update` | PUT/PATCH réussi | Champs modifiés (diff) |
| `delete` | DELETE réussi | Ressource supprimée |
| `stage_change` | Changement de pipeline | `from` → `to`, motif |
| `qualify` | Lancement qualification | Job ID, AO concerné |
| `cross_tenant_attempt` | Tentative cross-tenant | Tenant cible, IP, bloqué |
| `unauthorized_access_attempt` | 403 RBAC | Rôle requis, rôle actuel |
| `token_revoked` | Refresh token révoqué | Raison (logout / vol détecté) |
| `user_created` | Création user | Email, rôle, tenant |
| `password_changed` | Changement password | — (jamais le password en clair) |

#### 2.4.6 Export Audit (Conformité Fiscale)

```
GET /admin/audit-logs?from_date=2025-01-01&to_date=2025-01-31&format=csv

→ Retourne un fichier CSV :
timestamp, user_email, action, resource_type, resource_id, details, ip_address, hash_chain
2025-01-15T14:30:00Z,manager@client.fr,login,session,sess_001,"{...}",192.168.1.100,sha256:abc...
2025-01-15T14:45:00Z,manager@client.fr,create,tender,tdr_003,"{...}",192.168.1.100,sha256:def...

GET /admin/audit-logs?from_date=2025-01-01&to_date=2025-01-31&format=pdf

→ Retourne un PDF tamponné, signé, horodaté pour l'inspecteur fiscal.
```

---

### 2.5 Rate Limiting

#### 2.5.1 Limites par Endpoint

| Groupe | Endpoints | Limite | Fenêtre |
|--------|-----------|--------|---------|
| **Auth** | `/auth/login`, `/auth/dev-login` | 5 requêtes | 1 minute |
| **Refresh** | `/auth/refresh` | 10 requêtes | 1 minute |
| **API générale** | Tous les endpoints API | 100 requêtes | 1 minute |
| **Upload** | `/tenders/{id}/documents` | 10 requêtes | 1 minute |
| **Qualification** | `/tenders/{id}/qualify` | 5 requêtes | 1 minute |
| **Memory search** | `/memory/search` | 30 requêtes | 1 minute |
| **Admin audit** | `/admin/audit-logs` | 20 requêtes | 1 minute |

#### 2.5.2 Implémentation : Sliding Window (In-Memory)

Pour un déploiement VPS 6-8€ (mono-instance), le sliding window en mémoire est suffisant. Pour du multi-instance, migrer vers Redis.

```python
# app/core/rate_limit.py
import time
from collections import deque
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class SlidingWindowRateLimiter:
    """
    Rate limiter in-memory avec sliding window.
    Clé de rate limit : "<client_id>:<endpoint_group>"
    """

    def __init__(self):
        # { "key": deque([timestamp1, timestamp2, ...]) }
        self.windows: dict[str, deque] = {}
        self.limits = {
            "auth": (5, 60),        # 5 req / 60s
            "refresh": (10, 60),    # 10 req / 60s
            "api": (100, 60),       # 100 req / 60s
            "upload": (10, 60),     # 10 req / 60s
            "qualify": (5, 60),     # 5 req / 60s
            "memory": (30, 60),     # 30 req / 60s
            "admin": (20, 60),      # 20 req / 60s
        }

    def _get_client_id(self, request: Request) -> str:
        """Identifie le client par IP ou par user_id si authentifié."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _get_endpoint_group(self, path: str, method: str) -> str:
        """Détermine le groupe de rate limit pour un endpoint."""
        if path.startswith("/auth/login") or path.startswith("/auth/dev-login"):
            return "auth"
        if path.startswith("/auth/refresh"):
            return "refresh"
        if path.startswith("/tenders/") and path.endswith("/documents") and method == "POST":
            return "upload"
        if path.startswith("/tenders/") and path.endswith("/qualify"):
            return "qualify"
        if path.startswith("/memory/search"):
            return "memory"
        if path.startswith("/admin/audit-logs"):
            return "admin"
        return "api"

    def is_allowed(self, key: str, group: str) -> tuple[bool, int]:
        """
        Vérifie si la requête est autorisée.
        Retourne (autorisé, retry_after_seconds).
        """
        max_requests, window_seconds = self.limits.get(group, (100, 60))
        now = time.time()

        window = self.windows.setdefault(key, deque())

        # Retirer les timestamps expirés (hors fenêtre)
        while window and window[0] < now - window_seconds:
            window.popleft()

        if len(window) >= max_requests:
            retry_after = int(window[0] + window_seconds - now) + 1
            return False, max(retry_after, 1)

        window.append(now)
        return True, 0

# Instance globale
rate_limiter = SlidingWindowRateLimiter()

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware de rate limiting appliqué à toutes les requêtes."""

    async def dispatch(self, request: Request, call_next):
        client_id = rate_limiter._get_client_id(request)
        group = rate_limiter._get_endpoint_group(
            request.url.path,
            request.method
        )
        key = f"{client_id}:{group}"

        allowed, retry_after = rate_limiter.is_allowed(key, group)

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="RATE_LIMIT_EXCEEDED",
                headers={"Retry-After": str(retry_after)}
            )

        response = await call_next(request)

        # Headers informatifs
        remaining = rate_limiter.limits[group][0] - len(rate_limiter.windows.get(key, []))
        response.headers["X-RateLimit-Limit"] = str(rate_limiter.limits[group][0])
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))

        return response
```

#### 2.5.3 Réponse 429 (Rate Limit Exceeded)

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Limite de requêtes atteinte. Réessayez dans 45 secondes.",
    "retry_after": 45,
    "request_id": "req_999",
    "timestamp": "2025-01-15T18:00:00Z"
  }
}
```

---

### 2.6 Protection contre les Attaques

#### 2.6.1 SQL Injection — IMMUNISÉ par SQLAlchemy 2.0

```python
# ✅ SÉCURISÉ — SQLAlchemy 2.0 parameterized queries (obligatoire)
result = await session.execute(
    select(Tender).where(
        Tender.tenant_id == tenant_id,        # Parameterized
        Tender.title.ilike(f"%{search}%")     # Parameterized
    )
)

# ❌ INTERDIT — Jamais de f-string ou concatenation SQL
# NEVER: f"SELECT * FROM tenders WHERE title = '{user_input}'"
# NEVER: text(f"SELECT * FROM tenders WHERE id = '{tender_id}'")
```

**Règle d'or** : Toute requête SQL passe par l'ORM SQLAlchemy. `text()` n'est utilisé que pour des requêtes statiques sans paramètres dynamiques.

#### 2.6.2 XSS (Cross-Site Scripting)

```python
# ✅ SÉCURISÉ — Content-Type JSON strict, pas de HTML dans les réponses
# Toutes les réponses API retournent Content-Type: application/json
# Le frontend échappe tout rendu HTML (React fait ça par défaut)

# ❌ INTERDIT — Ne jamais retourner du HTML dans une réponse API
# NEVER: return HTMLResponse(f"<div>{user_input}</div>")

# Validation Pydantic sur tous les inputs
class TenderCreate(BaseModel):
    title: constr(min_length=5, max_length=500)  # Pas d'injection possible
    description: constr(max_length=50000)
```

#### 2.6.3 CSRF (Cross-Site Request Forgery)

```python
# ✅ SÉCURISÉ — Cookies SameSite=Strict + Header Origin validation

# Configuration des cookies refresh_token
response.set_cookie(
    key="refresh_token",
    value=refresh_token,
    httponly=True,          # Non accessible par JavaScript
    secure=True,            # Uniquement HTTPS (en production)
    samesite="Strict",      # Jamais envoyé en cross-site
    path="/auth/refresh",   # Scope minimal
    max_age=604800          # 7 jours
)

# Validation de l'header Origin pour les requêtes sensibles
allowed_origins = ["https://app.taka.io", "https://admin.taka.io"]
origin = request.headers.get("origin")
if origin and origin not in allowed_origins:
    raise HTTPException(status_code=403, detail="ORIGIN_NOT_ALLOWED")
```

#### 2.6.4 File Upload — Validation Multi-Couches

```python
# app/core/upload_security.py
import magic
from fastapi import UploadFile, HTTPException

# Types MIME autorisés
ALLOWED_MIME_TYPES = {
    "application/pdf": [b"%PDF-"],
    "application/zip": [b"PK\x03\x04"],
    "text/plain": [],
    "text/csv": [],
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

async def validate_upload(file: UploadFile) -> None:
    """
    Validation de sécurité d'un fichier uploadé.
    Vérifie : extension, type MIME déclaré, magic bytes, taille.
    """
    # 1. Vérifier l'extension
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    allowed_extensions = ["pdf", "docx", "doc", "xlsx", "xls", "zip", "txt", "csv"]
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="FILE_EXTENSION_NOT_ALLOWED")

    # 2. Vérifier le type MIME déclaré
    declared_mime = file.content_type
    if declared_mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="MIME_TYPE_NOT_ALLOWED")

    # 3. Lire les premiers bytes et vérifier les magic bytes
    header = await file.read(8192)
    await file.seek(0)  # Remettre le curseur au début

    detected_mime = magic.from_buffer(header, mime=True)
    if detected_mime != declared_mime:
        raise HTTPException(
            status_code=400,
            detail=f"MIME_TYPE_MISMATCH: déclaré={declared_mime}, détecté={detected_mime}"
        )

    # Vérifier les magic bytes connus
    expected_magics = ALLOWED_MIME_TYPES.get(declared_mime, [])
    if expected_magics and not any(header.startswith(m) for m in expected_magics):
        raise HTTPException(status_code=400, detail="MAGIC_BYTES_INVALID")

    # 4. Vérifier la taille (lecture complète)
    content = await file.read()
    await file.seek(0)

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="FILE_TOO_LARGE")

    # 5. Stocker le checksum SHA-256 pour détecter les doublons
    import hashlib
    checksum = hashlib.sha256(content).hexdigest()

    return {
        "filename": file.filename,
        "mime_type": detected_mime,
        "file_size": len(content),
        "checksum_sha256": checksum,
        "content": content
    }
```

#### 2.6.5 Timing Attacks — Comparaison Constant-Time

```python
# ✅ SÉCURISÉ — passlib bcrypt avec comparaison constant-time intégrée
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérification bcrypt — comparaison en temps constant.
    Empêche les attaques par timing qui devinent le password caractère par caractère.
    """
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Hashage bcrypt avec salt automatique."""
    return pwd_context.hash(password)

# La méthode pwd_context.verify() utilise une comparaison constant-time
# qui prend le même temps quel que soit le nombre de caractères corrects.
```

#### 2.6.6 Récapitulatif des Protections

| Attaque | Mécanisme de protection | Niveau de confiance |
|---------|------------------------|---------------------|
| **SQL Injection** | SQLAlchemy 2.0 ORM uniquement, pas de raw SQL dynamique | Élevé |
| **XSS** | Content-Type JSON strict, pas de HTML, React échappe le DOM | Élevé |
| **CSRF** | SameSite=Strict cookies, Origin validation | Élevé |
| **File Upload** | Magic bytes + MIME + extension + taille max 50MB | Élevé |
| **Timing Attack** | bcrypt constant-time via passlib | Élevé |
| **JWT Theft** | Access token court (15min), refresh rotation, httpOnly cookie | Élevé |
| **Brute Force** | Rate limiting 5 req/min sur auth, lockout après 5 échecs | Élevé |
| **Cross-Tenant** | Row-level filtering sur chaque requête, vérification JWT tenant_id | Élevé |
| **Audit Tampering** | Hash chain SHA-256, append-only, pas d'UPDATE/DELETE | Élevé |

---

## 3. Implémentation FastAPI — Ordre des Middlewares

```python
# app/main.py
from fastapi import FastAPI
from app.core.rate_limit import RateLimitMiddleware
from app.core.audit import AuditMiddleware
from app.core.security import AuthMiddleware
from app.core.tenant import TenantMiddleware

app = FastAPI(title="TAKA OS API", version="2.0.0")

# Ordre CRUCIAL des middlewares (exécution de haut en bas pour les requêtes)
app.add_middleware(RateLimitMiddleware)    # 1. Rate limit (bloque les abus)
app.add_middleware(AuditMiddleware)         # 2. Audit (logge tout)
app.add_middleware(AuthMiddleware)          # 3. Auth (vérifie JWT)
app.add_middleware(TenantMiddleware)        # 4. Tenant (isole les données)

# Routers
app.include_router(auth.router, prefix="/auth")
app.include_router(tenders.router, prefix="/tenders")
app.include_router(documents.router, prefix="/documents")
app.include_router(pipeline.router, prefix="/pipeline-stages")
app.include_router(memory.router, prefix="/memory")
app.include_router(admin.router, prefix="/admin")
```

---

## 4. Variables d'Environnement Critiques

| Variable | Description | Exemple |
|----------|-------------|---------|
| `JWT_SECRET_KEY` | Clé secrète pour signer les JWT (min 256 bits) | `openssl rand -hex 32` |
| `JWT_ALGORITHM` | Algorithme de signature | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Durée de vie access token | `15` |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Durée de vie refresh token | `7` |
| `ENV` | Environnement (`development`, `staging`, `production`) | `production` |
| `ALLOWED_ORIGINS` | Origines CORS autorisées | `https://app.taka.io,https://admin.taka.io` |
| `MAX_UPLOAD_SIZE_MB` | Taille max upload | `50` |
| `RATE_LIMIT_AUTH_PER_MINUTE` | Rate limit auth | `5` |
| `RATE_LIMIT_API_PER_MINUTE` | Rate limit API | `100` |
| `BCRYPT_ROUNDS` | Rounds bcrypt (cost factor) | `12` |
| `DATABASE_URL` | URL PostgreSQL | `postgresql+asyncpg://...` |
| `REDIS_URL` | URL Redis (optionnel, pour blacklist) | `redis://localhost:6379/0` |

---

## 5. Diagramme de Séquence — Authentification Complète

```
┌────────┐     ┌──────────┐     ┌─────────────────┐     ┌──────────┐     ┌──────────┐
│ Client │     │  FastAPI │     │ Auth Middleware │     │  DB      │     │  Redis   │
└───┬────┘     └────┬─────┘     └────────┬────────┘     └────┬─────┘     └────┬─────┘
    │               │                    │                   │                │
    │  POST /login  │                    │                   │                │
    │  {email, pwd} │                    │                   │                │
    │──────────────▶│                    │                   │                │
    │               │  1. Rate limit OK? │                   │                │
    │               │  (vérifier abuse)  │                   │                │
    │               │                    │                   │                │
    │               │  2. Récupérer user │                   │                │
    │               │     par email      │                   │                │
    │               │────────────────────│──────────────────▶│                │
    │               │                    │                   │                │
    │               │  3. User + hash    │                   │                │
    │               │     bcrypt         │                   │                │
    │               │◀───────────────────│───────────────────│                │
    │               │                    │                   │                │
    │               │  4. verify_password│                   │                │
    │               │     (constant-time)│                   │                │
    │               │                    │                   │                │
    │               │  5. Générer        │                   │                │
    │               │     access_token   │                   │                │
    │               │     refresh_token  │                   │                │
    │               │     (JWT signé)    │                   │                │
    │               │                    │                   │                │
    │               │  6. Stocker RT     │                   │                │
    │               │     dans Redis     │───────────────────│───────────────▶│
    │               │                    │                   │                │
    │               │  7. Audit log      │                   │                │
    │               │     "login"        │                   │                │
    │               │────────────────────│──────────────────▶│                │
    │               │                    │                   │                │
    │◀──────────────│  8. 200 OK +      │                   │                │
    │  access_token │     Set-Cookie:    │                   │                │
    │  (body)       │     refresh_token  │                   │                │
    │               │     (httpOnly)     │                   │                │
    │               │                    │                   │                │
    │               │                    │                   │                │
    │  GET /tenders │                    │                   │                │
    │  Authorization:                   │                   │                │
    │  Bearer <AT>  │                    │                   │                │
    │──────────────▶│                    │                   │                │
    │               │  9. Vérifier AT    │                   │                │
    │               │     (signature,    │                   │                │
    │               │      expiry, type) │                   │                │
    │               │                    │                   │                │
    │               │  10. Vérifier JTI  │                   │                │
    │               │      non révoqué   │───────────────────│───────────────▶│
    │               │                    │                   │                │
    │               │  11. Extraire      │                   │                │
    │               │      tenant_id     │                   │                │
    │               │      depuis JWT    │                   │                │
    │               │                    │                   │                │
    │               │  12. Query DB avec │                   │                │
    │               │      WHERE         │                   │                │
    │               │      tenant_id = ? │                   │                │
    │               │────────────────────│──────────────────▶│                │
    │               │                    │                   │                │
    │               │  13. Résultats     │                   │                │
    │               │      filtrés       │◀──────────────────│                │
    │               │                    │                   │                │
    │◀──────────────│  14. 200 OK       │                   │                │
    │  {tenders}    │     (JSON)         │                   │                │
    │               │                    │                   │                │
    │               │                    │                   │                │
    │  POST /auth/refresh                │                   │                │
    │  Cookie: RT#1 │                    │                   │                │
    │──────────────▶│                    │                   │                │
    │               │  15. Vérifier RT#1 │                   │                │
    │               │     (signature,    │                   │                │
    │               │      expiry,       │                   │                │
    │               │      family)       │                   │                │
    │               │                    │                   │                │
    │               │  16. RT#1 déjà     │                   │                │
    │               │      utilisé ?     │───────────────────│───────────────▶│
    │               │                    │                   │                │
    │               │  17. Si oui →      │                   │                │
    │               │      révoquer      │                   │                │
    │               │      toute la      │                   │                │
    │               │      famille !     │                   │                │
    │               │                    │                   │                │
    │               │  18. Sinon →       │                   │                │
    │               │      générer AT+   │                   │                │
    │               │      RT#2,         │                   │                │
    │               │      invalider RT#1│                   │                │
    │               │                    │                   │                │
    │◀──────────────│  19. 200 OK +     │                   │                │
    │  Nouveau AT   │     Set-Cookie:    │                   │                │
    │               │     RT#2           │                   │                │
    │               │     (RT#1 blacklist│                   │                │
    │               │      dans Redis)   │───────────────────│───────────────▶│
    │               │                    │                   │                │
    │               │                    │                   │                │
    │  POST /logout │                    │                   │                │
    │  Bearer AT    │                    │                   │                │
    │  Cookie RT#2  │                    │                   │                │
    │──────────────▶│                    │                   │                │
    │               │  20. Blacklist AT  │                   │                │
    │               │      (JTI dans     │                   │                │
    │               │       Redis)       │───────────────────│───────────────▶│
    │               │                    │                   │                │
    │               │  21. Supprimer RT#2│                   │                │
    │               │      de Redis      │───────────────────│───────────────▶│
    │               │                    │                   │                │
    │               │  22. Audit log     │                   │                │
    │               │      "logout"      │                   │                │
    │               │                    │                   │                │
    │◀──────────────│  23. 200 OK +     │                   │                │
    │               │     Cookie vidé   │                   │                │
    │               │     (Max-Age=0)   │                   │                │
    │               │                    │                   │                │
```

---

## 6. Table Récapitulative — Tous les Endpoints

| # | Méthode | Endpoint | Auth | Rôle Min | Description |
|---|---------|----------|------|----------|-------------|
| 1 | POST | `/auth/dev-login` | Non | — | Login dev (env=development uniquement) |
| 2 | POST | `/auth/login` | Non | — | Login email+password |
| 3 | POST | `/auth/refresh` | Cookie | — | Refresh JWT |
| 4 | GET | `/auth/me` | Bearer | viewer | Profil connecté |
| 5 | POST | `/auth/logout` | Bearer+Cookie | viewer | Déconnexion |
| 6 | GET | `/tenders` | Bearer | viewer | Liste AO avec filtres |
| 7 | POST | `/tenders` | Bearer | manager | Création AO |
| 8 | GET | `/tenders/{id}` | Bearer | viewer | Détail AO |
| 9 | PUT | `/tenders/{id}` | Bearer | manager | Mise à jour AO |
| 10 | DELETE | `/tenders/{id}` | Bearer | manager | Suppression AO |
| 11 | PUT | `/tenders/{id}/stage` | Bearer | manager | Changer stage |
| 12 | POST | `/tenders/{id}/qualify` | Bearer | manager | Lancer qualification |
| 13 | GET | `/tenders/{id}/qualification` | Bearer | viewer | Résultat qualification |
| 14 | POST | `/tenders/{id}/documents` | Bearer | manager | Upload document |
| 15 | GET | `/documents/{id}` | Bearer | viewer | Détail document |
| 16 | GET | `/documents/{id}/download` | Bearer | viewer | Téléchargement |
| 17 | DELETE | `/documents/{id}` | Bearer | manager | Suppression document |
| 18 | POST | `/documents/{id}/parse` | Bearer | manager | Parsing asynchrone |
| 19 | GET | `/pipeline-stages` | Bearer | viewer | Liste stages |
| 20 | PUT | `/pipeline-stages/reorder` | Bearer | admin | Réordonner stages |
| 21 | POST | `/memory/search` | Bearer | viewer | Recherche vectorielle |
| 22 | GET | `/memory/{id}` | Bearer | viewer | Détail mémoire |
| 23 | DELETE | `/memory/{id}` | Bearer | admin | Suppression RGPD |
| 24 | GET | `/admin/tenants` | Bearer | admin | Liste tenants |
| 25 | POST | `/admin/tenants` | Bearer | admin | Création tenant |
| 26 | GET | `/admin/users` | Bearer | admin | Liste users |
| 27 | POST | `/admin/users` | Bearer | admin | Création user |
| 28 | GET | `/admin/audit-logs` | Bearer | admin | Audit trail (JSON/CSV/PDF) |

---

*Fin de la Section 2 — API REST & Sécurité*
*Document version : 2.0.0*
*Date de rédaction : 2025-01-15*
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
# Section 4 — Frontend & DevOps

## Blueprint TAKA OS : OS Agentic Open Source pour Appels d'Offres

---

## 1. Architecture Frontend

### 1.a. Stack Technique Detaillee

| Couche | Technologie | Version | Justification |
|--------|-------------|---------|---------------|
| Framework | React | 18+ | Concurrent features, Suspense, performance |
| Langage | TypeScript | 5.3+ | Typage strict, DX, maintainabilite |
| Bundler | Vite | 5+ | HMR ultra-rapide, build optimisee, ESM natif |
| Styling | Tailwind CSS | 3.4+ | Utility-first, consistency design system, zero CSS mort |
| Composants | shadcn/ui | latest | Base Radix UI + theming Tailwind, accessible, copiables |
| State Global | Zustand | 4.5+ | Minimal, pas de boilerplate, TypeScript-first |
| Data Fetching | TanStack Query (React Query) | 5+ | Cache intelligent, invalidation, dedup, background refetch |
| Routing | React Router | v6 | Declaratif, lazy loading, protected routes |
| Formulaires | React Hook Form + Zod | 7+ / 3+ | Validation performante, typesafe, schema-driven |
| HTTP Client | Axios | 1.6+ | Intercepteurs JWT, retry logic, cancel tokens |
| Dates | date-fns | 3+ | Tree-shakeable, immutabilite, i18n ready |
| DnD | @dnd-kit/core | 6+ | Accessible, moderne, flexible (pipeline Kanban) |

**Contraintes de la stack :**
- Pas de Redux : Zustand suffit pour la complexite du state TAKA OS
- Pas de CSS Modules : Tailwind uniquement, pas de conflit de specificity
- Pas de MUI/Chakra : shadcn/ui pour le controle total du design system
- Pas de Next.js : SPA Vite suffisant, pas besoin de SSR pour un SaaS interne

### 1.b. Structure du Projet

```
frontend/
├── src/
│   ├── main.tsx                    # Point d'entree, providers
│   ├── App.tsx                     # Router, layouts, guards
│   ├── index.css                   # Tailwind directives + variables CSS
│   │
│   ├── components/                 # COMPOSANTS REUTILISABLES
│   │   ├── ui/                     # shadcn/ui (Button, Card, Dialog, etc.)
│   │   ├── layout/
│   │   │   ├── Layout.tsx          # Sidebar + Header + Content
│   │   │   ├── Sidebar.tsx         # Navigation verticale
│   │   │   ├── Header.tsx          # Top bar (titre, actions, profil)
│   │   │   └── MobileNav.tsx       # Navigation mobile (bottom bar)
│   │   ├── tenders/
│   │   │   ├── TenderCard.tsx      # Carte Kanban + liste
│   │   │   ├── TenderForm.tsx      # Formulaire creation/edition
│   │   │   ├── TenderTable.tsx     # Tableau AO (sortable, paginable)
│   │   │   └── TenderFilters.tsx   # Barre de filtres avances
│   │   ├── pipeline/
│   │   │   ├── PipelineBoard.tsx   # Plateau Kanban complet
│   │   │   ├── PipelineColumn.tsx  # Colonne (stage)
│   │   │   └── SortableTenderCard.tsx # Carte draggable
│   │   ├── qualification/
│   │   │   ├── QualificationBadge.tsx   # GO/NO-GO/MAYBE
│   │   │   ├── QualificationResult.tsx  # Barres de score detaille
│   │   │   └── QualificationTrigger.tsx # Bouton lancer agent
│   │   ├── shared/
│   │   │   ├── KPICard.tsx         # Carte KPI (dashboard)
│   │   │   ├── DeadlineBadge.tsx   # Badge deadline colore
│   │   │   ├── FileUploadZone.tsx  # Zone drag & drop
│   │   │   ├── SearchBar.tsx       # Recherche + filtres
│   │   │   ├── DataTable.tsx       # Table generique (tanstack-table)
│   │   │   ├── StatusBadge.tsx     # Badge generique (stage, statut)
│   │   │   ├── ConfirmDialog.tsx   # Dialog de confirmation
│   │   │   ├── EmptyState.tsx      # Etat vide illustre
│   │   │   └── LoadingSkeleton.tsx # Skeleton screens
│   │   └── memory/
│   │       ├── MemorySearch.tsx    # Input recherche semantique
│   │       └── MemoryResultCard.tsx # Card resultat memoire
│   │
│   ├── pages/                      # PAGES (1 page = 1 route)
│   │   ├── LoginPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── TendersPage.tsx
│   │   ├── TenderDetailPage.tsx
│   │   ├── PipelinePage.tsx
│   │   ├── UploadPage.tsx
│   │   ├── MemoryPage.tsx
│   │   ├── SettingsPage.tsx
│   │   └── AuditLogsPage.tsx
│   │
│   ├── hooks/                      # CUSTOM HOOKS
│   │   ├── useAuth.ts              # Auth + guards
│   │   ├── useTenders.ts           # CRUD tenders + cache
│   │   ├── useTender.ts            # Single tender + mutations
│   │   ├── usePipeline.ts          # Kanban DnD + reorder
│   │   ├── useQualification.ts     # Lancer + suivre qualification
│   │   ├── useUpload.ts            # Upload DCE + progression
│   │   ├── useMemory.ts            # Recherche vectorielle
│   │   ├── useAuditLogs.ts         # Logs admin
│   │   ├── useStages.ts            # Stages pipeline (settings)
│   │   ├── useDebounce.ts          # Debounce generique
│   │   └── useMediaQuery.ts        # Breakpoints responsive
│   │
│   ├── stores/                     # ZUSTAND STORES
│   │   ├── authStore.ts
│   │   ├── tenderStore.ts
│   │   ├── pipelineStore.ts
│   │   └── uiStore.ts
│   │
│   ├── services/                   # API CALLS
│   │   ├── api.ts                  # Instance Axios configuree
│   │   ├── auth.service.ts         # Login, refresh, logout
│   │   ├── tender.service.ts       # CRUD tenders
│   │   ├── pipeline.service.ts     # Stages + mouvements
│   │   ├── upload.service.ts       # Upload + parsing DCE
│   │   ├── memory.service.ts       # Recherche memoire
│   │   ├── settings.service.ts     # Parametres tenant
│   │   └── audit.service.ts        # Logs audit
│   │
│   ├── types/                      # TYPES TYPESCRIPT
│   │   ├── auth.ts                 # User, Role, TokenPayload
│   │   ├── tender.ts               # Tender, Stage, Qualification
│   │   ├── pipeline.ts             # PipelineColumn, TenderCard
│   │   ├── upload.ts               # UploadProgress, ParsedDCE
│   │   ├── memory.ts               # MemoryChunk, SearchResult
│   │   ├── settings.ts             # TenantSettings, QualRule
│   │   └── api.ts                  # ApiResponse, PaginatedResult
│   │
│   └── lib/                        # UTILITAIRES
│       ├── utils.ts                # cn() (clsx + tailwind-merge)
│       ├── constants.ts            # Routes, stages par defaut, limits
│       ├── date-utils.ts           # Formatage dates, comparaisons
│       ├── formatters.ts           # Montants, pourcentages, texte
│       └── validators.ts           # Schemas Zod partages
│
├── public/                         # Assets statiques
│   ├── logo.svg
│   └── favicon.ico
│
├── index.html
├── package.json
├── tailwind.config.js              # Theme TAKA OS (colors, fonts)
├── tsconfig.json                   # Strict mode, path aliases
├── vite.config.ts                  # Proxy dev, path aliases
├── components.json                 # Config shadcn/ui
└── .env.example                    # Variables d'environnement
```

### 1.c. Configuration Tailwind (Theme TAKA OS)

```javascript
// tailwind.config.js
import { fontFamily } from "tailwindcss/defaultTheme";

/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: { "2xl": "1400px" },
    },
    extend: {
      colors: {
        // Palette TAKA OS
        taka: {
          50: "#f0f9ff",
          100: "#e0f2fe",
          200: "#bae6fd",
          300: "#7dd3fc",
          400: "#38bdf8",
          500: "#0ea5e9",
          600: "#0284c7",
          700: "#0369a1",
          800: "#075985",
          900: "#0c4a6e",
          950: "#082f49",
        },
        // Semantic colors (qualification)
        qual: {
          go: "#22c55e",      // Vert
          "go-light": "#dcfce7",
          maybe: "#f59e0b",   // Orange
          "maybe-light": "#fef3c7",
          nogo: "#ef4444",    // Rouge
          "nogo-light": "#fee2e2",
        },
        // Deadline colors
        deadline: {
          safe: "#22c55e",     // >14j
          warning: "#f59e0b",  // 7-14j
          danger: "#ef4444",   // <7j
          expired: "#6b7280",  // Passée
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        sans: ["Inter", ...fontFamily.sans],
        mono: ["JetBrains Mono", ...fontFamily.mono],
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        "slide-in": {
          from: { transform: "translateX(-100%)", opacity: "0" },
          to: { transform: "translateX(0)", opacity: "1" },
        },
        "fade-in": {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "slide-in": "slide-in 0.3s ease-out",
        "fade-in": "fade-in 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
```

### 1.d. Configuration Vite

```typescript
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "@components": path.resolve(__dirname, "./src/components"),
      "@pages": path.resolve(__dirname, "./src/pages"),
      "@hooks": path.resolve(__dirname, "./src/hooks"),
      "@stores": path.resolve(__dirname, "./src/stores"),
      "@services": path.resolve(__dirname, "./src/services"),
      "@types": path.resolve(__dirname, "./src/types"),
      "@lib": path.resolve(__dirname, "./src/lib"),
    },
  },
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["react", "react-dom"],
          router: ["react-router-dom"],
          query: ["@tanstack/react-query"],
          forms: ["react-hook-form", "@hookform/resolvers", "zod"],
          dnd: ["@dnd-kit/core", "@dnd-kit/sortable", "@dnd-kit/utilities"],
          charts: ["recharts"],
        },
      },
    },
  },
});
```

### 1.e. Point d'Entree (main.tsx)

```tsx
// src/main.tsx
import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { RouterProvider } from "react-router-dom";
import { router } from "./App";
import "./index.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,     // 5 min
      gcTime: 1000 * 60 * 30,       // 30 min (cacheTime renomme)
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
      {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  </React.StrictMode>
);
```

---

## 2. Pages et Composants Detailles

### 2.a. Login (/login)

**Route :** `/login` — Publique, redirect si deja authentifie

**Layout :** Centré, fond gradient subtil, sans sidebar

**Composants :**
- `LoginForm` (formulaire email + password)
- `DevLoginButton` (visible uniquement en `import.meta.env.DEV`)

**États :**
- Zustand : `authStore.login(credentials)`, `authStore.isLoading`
- React Query : `useLoginMutation`

**Actions utilisateur :**
1. Saisir email + password
2. Soumettre → appel `/api/auth/login`
3. Stockage token (httpOnly cookie + memoire Zustand)
4. Redirection vers `/dashboard`
5. Mode dev : bouton "Dev Login" → login automatique avec creds de test

```tsx
// src/pages/LoginPage.tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@stores/authStore";
import { Button } from "@components/ui/button";
import { Input } from "@components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@components/ui/form";

const loginSchema = z.object({
  email: z.string().email("Email invalide"),
  password: z.string().min(1, "Mot de passe requis"),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const navigate = useNavigate();
  const { login, isLoading } = useAuthStore();

  const form = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });

  const onSubmit = async (data: LoginFormData) => {
    await login(data);
    navigate("/dashboard");
  };

  const handleDevLogin = async () => {
    await login({ email: "dev@taka.os", password: "dev" });
    navigate("/dashboard");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-taka-50 to-taka-100">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader className="text-center">
          <img src="/logo.svg" alt="TAKA OS" className="h-12 mx-auto mb-4" />
          <CardTitle className="text-2xl">Connexion</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input type="email" placeholder="vous@entreprise.fr" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Mot de passe</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="••••••••" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "Connexion..." : "Se connecter"}
              </Button>
            </form>
          </Form>

          {import.meta.env.DEV && (
            <Button variant="outline" className="w-full" onClick={handleDevLogin}>
              Dev Login (rapide)
            </Button>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
```

**Design Responsive :**
- Desktop : Card centree, largeur max 448px
- Mobile : Card pleine largeur avec padding 16px

---

### 2.b. Dashboard (/dashboard)

**Route :** `/dashboard` — Protégée (tous les rôles)

**Layout :** Standard (sidebar + header + content)

**Composants :**
- `KPICard` x4 (AO actifs, deadlines 7j, taux GO, total en cours)
- `PipelineChart` (Recharts — bar chart des tenders par stage)
- `RecentTendersTable` (5 derniers AO avec statut)

**États :**
- React Query : `useDashboardStats`, `useRecentTenders`
- Zustand : `uiStore.sidebarOpen`

**Actions utilisateur :**
1. Visualiser KPIs (auto-refresh toutes les 5 min)
2. Cliquer sur un KPI → redirection vers `/tenders` avec filtre pre-rempli
3. Cliquer sur un AO recent → fiche detail
4. Hover sur graphique → tooltip detaille

```tsx
// src/pages/DashboardPage.tsx — extrait structure
import { KPICard } from "@components/shared/KPICard";
import { PipelineChart } from "@components/dashboard/PipelineChart";
import { RecentTendersTable } from "@components/dashboard/RecentTendersTable";

export default function DashboardPage() {
  const { data: stats } = useDashboardStats();
  const { data: recentTenders } = useRecentTenders(5);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Tableau de bord</h1>
        <p className="text-muted-foreground">Vue d'ensemble de vos appels d'offres</p>
      </div>

      {/* KPI Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <KPICard
          title="AO Actifs"
          value={stats?.activeTenders ?? 0}
          icon="FileText"
          trend={+12}
          href="/tenders?filter=active"
        />
        <KPICard
          title="Deadlines < 7j"
          value={stats?.urgentDeadlines ?? 0}
          icon="AlertTriangle"
          variant="warning"
          href="/tenders?filter=urgent"
        />
        <KPICard
          title="Taux Qualification GO"
          value={`${stats?.goRate ?? 0}%`}
          icon="CheckCircle"
          variant="success"
        />
        <KPICard
          title="Montant Total"
          value={formatCurrency(stats?.totalValue ?? 0)}
          icon="Euro"
        />
      </div>

      {/* Chart + Table */}
      <div className="grid gap-6 lg:grid-cols-7">
        <Card className="lg:col-span-4">
          <CardHeader>
            <CardTitle>Pipeline</CardTitle>
          </CardHeader>
          <CardContent>
            <PipelineChart data={stats?.pipelineDistribution} />
          </CardContent>
        </Card>

        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>AO Recents</CardTitle>
          </CardHeader>
          <CardContent>
            <RecentTendersTable data={recentTenders} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

**Design Responsive :**
- Desktop : Grid 2x2 KPIs, chart 7 cols + table 3 cols
- Tablette : KPIs 2x2, chart + table empilés
- Mobile : KPIs empilés, graphique avec hauteur 250px, table scrollable horizontalement

---

### 2.c. Liste des AO (/tenders)

**Route :** `/tenders` — Protégée (viewer+, manager+ pour création)

**Layout :** Standard

**Composants :**
- `SearchBar` (recherche texte libre)
- `TenderFilters` (stage, qualification, deadline range)
- `DataTable` (tableau paginé, triable)
- `NewTenderDialog` (modal création manuelle)
- `UploadDCEDialog` (modal upload PDF)

**Colonnes DataTable :**
| Colonne | Triable | Filtrable | Note |
|---------|---------|-----------|------|
| Reference | Oui | Non | Lien vers fiche |
| Titre | Oui | Search | Tronqué a 60 chars |
| Acheteur | Oui | Select | |
| Deadline | Oui | Date range | DeadlineBadge |
| Stage | Oui | Select | StatusBadge |
| Qualification | Oui | Select | QualificationBadge |
| Actions | Non | Non | Voir / Editer / Supprimer |

**États :**
- Zustand : `tenderStore.filters`, `tenderStore.pagination`
- React Query : `useTenders({ filters, pagination })`, `useDeleteTenderMutation`

```tsx
// src/pages/TendersPage.tsx — extrait
export default function TendersPage() {
  const { filters, setFilters, pagination, setPagination } = useTenderStore();
  const { data, isLoading } = useTenders({ filters, pagination });
  const deleteMutation = useDeleteTenderMutation();

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold">Appels d'Offres</h1>
          <p className="text-muted-foreground">{data?.total} AO trouves</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setUploadOpen(true)}>
            <Upload className="mr-2 h-4 w-4" /> Upload DCE
          </Button>
          <Button onClick={() => setCreateOpen(true)}>
            <Plus className="mr-2 h-4 w-4" /> Nouvel AO
          </Button>
        </div>
      </div>

      <div className="flex flex-col gap-4 lg:flex-row">
        <SearchBar
          value={filters.search}
          onChange={(v) => setFilters({ ...filters, search: v })}
          placeholder="Rechercher par titre, reference, acheteur..."
        />
        <TenderFilters filters={filters} onChange={setFilters} />
      </div>

      <DataTable
        columns={tenderColumns}
        data={data?.items ?? []}
        isLoading={isLoading}
        pagination={pagination}
        onPaginationChange={setPagination}
        totalCount={data?.total ?? 0}
      />
    </div>
  );
}
```

**Design Responsive :**
- Desktop : Filtres en ligne, table pleine largeur, pagination en bas
- Mobile : Filtres dans un drawer, table scrollable horizontalement, cards empilées en alternative

---

### 2.d. Fiche AO (/tenders/:id)

**Route :** `/tenders/:id` — Protégée (tous les rôles, edit manager+)

**Layout :** Standard, pleine largeur

**Onglets (Tabs shadcn/ui) :**

#### Onglet 1 : Details
- Formulaire avec tous les champs du tender
- Champs : reference, titre, description, acheteur, deadline, montant estime, CPV, lieu, type de marche, procedure
- Mode lecture (viewer) / edition (manager)
- Bouton Sauvegarder (mutation React Query avec invalidation cache)

#### Onglet 2 : Documents
- Liste des documents (DCE, RC, DPGF, etc.)
- Upload de nouveaux documents
- Statut de parsing pour chaque document (pending / processing / done / error)
- Preview PDF inline (iframe)

#### Onglet 3 : Qualification
- Resultat GO/NO-GO/MAYBE avec badge colore
- Barres de score par critere (eligibilite, technique, financier, calendrier, risques)
- Justification textuelle de l'agent
- Bouton "Relancer la qualification" (manager+)
- Historique des qualifications precedentes

#### Onglet 4 : Historique
- Timeline verticale des evenements (audit trail)
- Types : creation, modification, qualification, changement stage, upload document
- Auteur + date pour chaque evenement

```tsx
// src/pages/TenderDetailPage.tsx — structure onglets
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@components/ui/tabs";

export default function TenderDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: tender } = useTender(id!);

  return (
    <div className="space-y-6">
      {/* Header de la fiche */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold">{tender?.title}</h1>
            <QualificationBadge result={tender?.qualification} />
          </div>
          <p className="text-muted-foreground">Ref: {tender?.reference}</p>
        </div>
        <div className="flex gap-2">
          <DeadlineBadge date={tender?.deadline} />
          <Button onClick={() => triggerQualification(id!)}>
            <Sparkles className="mr-2 h-4 w-4" /> Qualifier
          </Button>
        </div>
      </div>

      <Tabs defaultValue="details" className="w-full">
        <TabsList className="w-full justify-start overflow-x-auto">
          <TabsTrigger value="details">Details</TabsTrigger>
          <TabsTrigger value="documents">Documents</TabsTrigger>
          <TabsTrigger value="qualification">Qualification</TabsTrigger>
          <TabsTrigger value="history">Historique</TabsTrigger>
        </TabsList>

        <TabsContent value="details">
          <TenderForm tender={tender} readOnly={!canEdit} />
        </TabsContent>

        <TabsContent value="documents">
          <DocumentsTab tenderId={id!} documents={tender?.documents} />
        </TabsContent>

        <TabsContent value="qualification">
          <QualificationTab tenderId={id!} qualification={tender?.qualification_result} />
        </TabsContent>

        <TabsContent value="history">
          <HistoryTimeline tenderId={id!} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

**Design Responsive :**
- Desktop : Tabs horizontales, formulaire 2 colonnes, timeline pleine largeur
- Mobile : Tabs scrollables horizontalement, formulaire 1 colonne, timeline compactee

---

### 2.e. Kanban Pipeline (/pipeline)

**Route :** `/pipeline` — Protégée (tous les rôles, DnD manager+)

**Layout :** Standard, pleine largeur sans padding lateral

**Composants :**
- `PipelineBoard` — conteneur DnD (@dnd-kit)
- `PipelineColumn` — colonne (stage) avec compteur
- `SortableTenderCard` — carte draggable
- `QualificationFilter` — filtre GO/NO-GO/MAYBE/TOUS

**Fonctionnalites DnD :**
- Drag & drop horizontal entre colonnes
- Reordonnancement vertical dans une colonne
- Animation fluide (CSS transitions)
- Confetti visuel lors d'un drop dans "Gagne" (option UX)

```tsx
// src/pages/PipelinePage.tsx — structure DnD
import { DndContext, DragOverlay, closestCorners } from "@dnd-kit/core";
import { SortableContext, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { PipelineColumn } from "@components/pipeline/PipelineColumn";
import { SortableTenderCard } from "@components/pipeline/SortableTenderCard";
import { TenderCard } from "@components/tenders/TenderCard";

export default function PipelinePage() {
  const { stages, tendersByStage, moveTender, reorderTender } = usePipeline();
  const [activeId, setActiveId] = useState<string | null>(null);
  const [qualFilter, setQualFilter] = useState<Qualification | "ALL">("ALL");

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over) return;

    const activeTender = findTender(active.id as string);
    const overStage = over.data.current?.stageId;

    if (overStage && activeTender.stage_id !== overStage) {
      moveTender({ tenderId: active.id as string, targetStage: overStage });
    }
    setActiveId(null);
  };

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col">
      {/* Header avec filtres */}
      <div className="flex items-center justify-between px-6 py-4">
        <div>
          <h1 className="text-3xl font-bold">Pipeline</h1>
          <p className="text-muted-foreground">Glissez-deposez pour avancer vos AO</p>
        </div>
        <QualificationFilter value={qualFilter} onChange={setQualFilter} />
      </div>

      {/* Board DnD */}
      <DndContext
        collisionDetection={closestCorners}
        onDragStart={({ active }) => setActiveId(active.id as string)}
        onDragEnd={handleDragEnd}
      >
        <div className="flex-1 flex gap-4 overflow-x-auto px-6 pb-4">
          {stages.map((stage) => (
            <PipelineColumn
              key={stage.id}
              stage={stage}
              tenders={(tendersByStage[stage.id] ?? []).filter(
                (t) => qualFilter === "ALL" || t.qualification === qualFilter
              )}
            />
          ))}
        </div>

        <DragOverlay>
          {activeId ? <TenderCard tender={findTender(activeId)} isDragging /> : null}
        </DragOverlay>
      </DndContext>
    </div>
  );
}
```

**Design Responsive :**
- Desktop : Colonnes fixes, scroll horizontal, cards larges (280px min)
- Mobile : Vue liste alternative (cards empilees par stage), DnD desactive

---

### 2.f. Upload DCE (/upload)

**Route :** `/upload` — Protégée (manager+)

**Layout :** Standard, centré

**Composants :**
- `FileUploadZone` — zone drag & drop
- `UploadProgress` — barre de progression
- `ParsedTenderPreview` — prévisualisation champs extraits
- `TenderCorrectionForm` — correction des champs avant validation

**Flux utilisateur :**
1. Drop fichier PDF ou clic pour selection
2. Upload avec barre de progression (Axios onUploadProgress)
3. Parsing côté backend (retour SSE ou polling)
4. Affichage des champs extraits (titre, reference, deadline, montant, acheteur, CPV)
5. Utilisateur corrige si besoin
6. Validation → création du tender + redirection fiche

```tsx
// src/pages/UploadPage.tsx — flux complet
export default function UploadPage() {
  const [step, setStep] = useState<"upload" | "parsing" | "preview" | "success">("upload");
  const [progress, setProgress] = useState(0);
  const [parsedData, setParsedData] = useState<ParsedTender | null>(null);
  const uploadMutation = useUploadDCE();

  const handleDrop = async (files: File[]) => {
    const file = files[0];
    if (!file || file.type !== "application/pdf") {
      toast.error("Veuillez deposer un fichier PDF");
      return;
    }

    setStep("upload");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const result = await uploadMutation.mutateAsync(
        { file, onProgress: setProgress },
        {
          onSuccess: (data) => {
            setParsedData(data);
            setStep("preview");
          },
        }
      );
    } catch (error) {
      setStep("upload");
      toast.error("Erreur lors de l'upload");
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Upload de DCE</h1>
        <p className="text-muted-foreground">
          Deposez un DCE PDF pour extraction automatique des informations
        </p>
      </div>

      {step === "upload" && (
        <FileUploadZone onDrop={handleDrop} accept=".pdf" maxSize={50 * 1024 * 1024} />
      )}

      {step === "parsing" && (
        <Card className="p-8">
          <div className="text-center space-y-4">
            <Loader2 className="h-8 w-8 animate-spin mx-auto text-taka-600" />
            <p>Analyse du document en cours...</p>
            <Progress value={progress} className="w-full" />
          </div>
        </Card>
      )}

      {step === "preview" && parsedData && (
        <ParsedTenderPreview
          data={parsedData}
          onConfirm={(corrected) => createTender(corrected)}
          onBack={() => setStep("upload")}
        />
      )}
    </div>
  );
}
```

**Design Responsive :**
- Desktop : Zone drop grande (400px hauteur), formulaire correction 2 colonnes
- Mobile : Zone drop pleine largeur, formulaire 1 colonne, steps en vertical

---

### 2.g. Memoire (/memory)

**Route :** `/memory` — Protégée (tous les rôles)

**Layout :** Standard

**Composants :**
- `MemorySearch` — input recherche avec similarité
- `MemoryResultCard` — card resultat (contenu + % similarité)
- `TagFilter` — filtres par tags/categories

**Fonctionnement :**
- Recherche textuelle envoyée à `/api/memory/search?q=...`
- Retour : chunks vectoriels avec score de similarité
- Affichage : cards avec extrait, similarité en badge, tags cliquables
- Highlight des termes recherchés dans les résultats

```tsx
// src/pages/MemoryPage.tsx
export default function MemoryPage() {
  const [query, setQuery] = useState("");
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const { data: results, isLoading } = useMemorySearch(query, selectedTags);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Memoire</h1>
        <p className="text-muted-foreground">
          Recherche semantique dans la base de connaissances
        </p>
      </div>

      <MemorySearch
        value={query}
        onChange={setQuery}
        placeholder="Rechercher par contenu semantique..."
      />

      <TagFilter
        tags={availableTags}
        selected={selectedTags}
        onChange={setSelectedTags}
      />

      {isLoading ? (
        <LoadingSkeleton count={6} />
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {results?.map((result) => (
            <MemoryResultCard
              key={result.id}
              content={result.content}
              similarity={result.similarity}
              tags={result.tags}
              source={result.source}
              onTagClick={(tag) => setSelectedTags((prev) => [...prev, tag])}
            />
          ))}
        </div>
      )}

      {results?.length === 0 && query && (
        <EmptyState
          icon="Search"
          title="Aucun resultat"
          description="Essayez avec d'autres termes"
        />
      )}
    </div>
  );
}
```

---

### 2.h. Parametres (/settings)

**Route :** `/settings` — Protégée (admin pour users, tous pour profil)

**Onglets :**

#### Profil
- Photo, nom, email, changement password

#### Regles de Qualification (admin)
- CPV whitelist/blacklist (textarea avec tags)
- Fourchette montants (min/max)
- Types de marche autorises (checkboxes)
- Seuil de score GO/MAYBE/NO-GO

#### Stages Pipeline (admin)
- Liste des stages (drag & drop pour reorder)
- Ajouter / Renommer / Supprimer un stage
- Couleur par stage

#### Utilisateurs (admin)
- Table des utilisateurs (nom, email, rôle, derniere connexion)
- Ajouter un utilisateur (invitation par email)
- Modifier rôle, Désactiver, Supprimer

```tsx
// src/pages/SettingsPage.tsx
export default function SettingsPage() {
  const { user } = useAuthStore();
  const isAdmin = user?.role === "admin";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Parametres</h1>
        <p className="text-muted-foreground">Configuration de votre espace TAKA OS</p>
      </div>

      <Tabs defaultValue="profile" orientation="vertical" className="flex gap-6">
        <TabsList className="flex-col h-fit w-48">
          <TabsTrigger value="profile">Profil</TabsTrigger>
          {isAdmin && (
            <>
              <TabsTrigger value="qualification">Regles de Qualification</TabsTrigger>
              <TabsTrigger value="pipeline">Pipeline</TabsTrigger>
              <TabsTrigger value="users">Utilisateurs</TabsTrigger>
            </>
          )}
        </TabsList>

        <div className="flex-1">
          <TabsContent value="profile"><ProfileSettings /></TabsContent>
          {isAdmin && (
            <>
              <TabsContent value="qualification"><QualificationRules /></TabsContent>
              <TabsContent value="pipeline"><PipelineSettings /></TabsContent>
              <TabsContent value="users"><UsersManagement /></TabsContent>
            </>
          )}
        </div>
      </Tabs>
    </div>
  );
}
```

**Design Responsive :**
- Desktop : Tabs verticales a gauche (sidebar 192px), contenu a droite
- Mobile : Tabs horizontales scrollables, contenu pleine largeur

---

### 2.i. Audit Logs (/admin/audit)

**Route :** `/admin/audit` — Admin uniquement (route guard)

**Layout :** Standard

**Composants :**
- `AuditFilters` — date range, user, action type
- `AuditTable` — table paginée
- `ExportButton` — export CSV/PDF

**Colonnes :** Date | Utilisateur | Action | Entite | Details | IP

```tsx
// src/pages/AuditLogsPage.tsx
export default function AuditLogsPage() {
  const { filters, setFilters, pagination, setPagination } = useAuditStore();
  const { data: logs, isLoading } = useAuditLogs({ filters, pagination });

  const handleExport = async (format: "csv" | "pdf") => {
    const blob = await exportAuditLogs(format, filters);
    downloadFile(blob, `audit-logs.${format}`);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Logs d'Audit</h1>
          <p className="text-muted-foreground">Historique complet des actions</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => handleExport("csv")}>
            <Download className="mr-2 h-4 w-4" /> CSV
          </Button>
          <Button variant="outline" onClick={() => handleExport("pdf")}>
            <Download className="mr-2 h-4 w-4" /> PDF
          </Button>
        </div>
      </div>

      <AuditFilters filters={filters} onChange={setFilters} />
      <AuditTable logs={logs?.items} isLoading={isLoading} pagination={pagination} />
    </div>
  );
}
```

---

### 2.j. Composants Reutilisables — Specifications Detailles

#### Layout (Sidebar + Header + Content)

```tsx
// src/components/layout/Layout.tsx
export function Layout() {
  const { sidebarOpen, toggleSidebar } = useUIStore();

  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar Desktop */}
      <aside
        className={cn(
          "fixed left-0 top-0 z-40 h-screen transition-all duration-300 bg-card border-r",
          sidebarOpen ? "w-64" : "w-16"
        )}
      >
        <Sidebar collapsed={!sidebarOpen} />
      </aside>

      {/* Main Content */}
      <div
        className={cn(
          "transition-all duration-300 min-h-screen flex flex-col",
          sidebarOpen ? "ml-64" : "ml-16"
        )}
      >
        <Header onMenuClick={toggleSidebar} />
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>

      {/* Mobile Bottom Nav */}
      <MobileNav className="lg:hidden" />
    </div>
  );
}
```

#### Sidebar

- Logo TAKA OS (réduit quand collapsed)
- Navigation items avec icons (Dashboard, AO, Pipeline, Upload, Memoire, Parametres)
- Section admin (Audit) conditionnelle
- Tenant name + user avatar en bas
- Tooltip quand collapsed

```tsx
const navItems = [
  { label: "Dashboard", icon: LayoutDashboard, href: "/dashboard" },
  { label: "Appels d'Offres", icon: FileText, href: "/tenders" },
  { label: "Pipeline", icon: Kanban, href: "/pipeline" },
  { label: "Upload DCE", icon: Upload, href: "/upload" },
  { label: "Memoire", icon: Brain, href: "/memory" },
  { label: "Parametres", icon: Settings, href: "/settings" },
];
```

#### TenderCard (Kanban)

```tsx
// src/components/tenders/TenderCard.tsx
interface TenderCardProps {
  tender: Tender;
  isDragging?: boolean;
  onClick?: () => void;
}

export function TenderCard({ tender, isDragging, onClick }: TenderCardProps) {
  return (
    <Card
      className={cn(
        "cursor-pointer hover:shadow-md transition-shadow",
        isDragging && "opacity-50 rotate-2 shadow-xl"
      )}
      onClick={onClick}
    >
      <CardContent className="p-3 space-y-2">
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-medium text-sm line-clamp-2">{tender.title}</h3>
          <QualificationBadge result={tender.qualification} size="sm" />
        </div>
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <DeadlineBadge date={tender.deadline} size="sm" />
          {tender.estimated_value && (
            <span>{formatCurrency(tender.estimated_value)}</span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
```

#### QualificationBadge

```tsx
// src/components/qualification/QualificationBadge.tsx
const qualConfig = {
  GO:      { label: "GO",      color: "bg-green-500",      light: "bg-green-100 text-green-800" },
  MAYBE:   { label: "MAYBE",   color: "bg-amber-500",      light: "bg-amber-100 text-amber-800" },
  "NO-GO": { label: "NO-GO",   color: "bg-red-500",        light: "bg-red-100 text-red-800" },
  PENDING: { label: "En attente", color: "bg-gray-400",     light: "bg-gray-100 text-gray-600" },
};

interface QualificationBadgeProps {
  result?: keyof typeof qualConfig;
  size?: "sm" | "md" | "lg";
}

export function QualificationBadge({ result = "PENDING", size = "md" }: QualificationBadgeProps) {
  const config = qualConfig[result];
  const sizeClasses = {
    sm: "text-[10px] px-1.5 py-0.5",
    md: "text-xs px-2.5 py-0.5",
    lg: "text-sm px-3 py-1",
  };

  return (
    <Badge className={cn(config.light, sizeClasses[size], "font-semibold")}>
      {config.label}
    </Badge>
  );
}
```

#### DeadlineBadge

```tsx
// src/components/shared/DeadlineBadge.tsx
export function DeadlineBadge({ date, size = "md" }: DeadlineBadgeProps) {
  if (!date) return null;

  const days = differenceInDays(parseISO(date), new Date());
  const config =
    days < 0 ? { label: "Expire", color: "bg-gray-500" }
    : days < 7 ? { label: `${days}j`, color: "bg-red-500" }
    : days < 14 ? { label: `${days}j`, color: "bg-amber-500" }
    : { label: `${days}j`, color: "bg-green-500" };

  return (
    <div className="flex items-center gap-1">
      <Clock className={cn("text-muted-foreground", size === "sm" ? "h-3 w-3" : "h-4 w-4")} />
      <span className={cn("font-medium", days < 7 && "text-red-600")}>
        {config.label}
      </span>
    </div>
  );
}
```

#### FileUploadZone

```tsx
// src/components/shared/FileUploadZone.tsx
export function FileUploadZone({ onDrop, accept = ".pdf", maxSize = 50 * 1024 * 1024 }) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxSize,
    multiple: false,
  });

  return (
    <div
      {...getRootProps()}
      className={cn(
        "border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors",
        isDragActive
          ? "border-taka-500 bg-taka-50"
          : "border-border hover:border-taka-300 hover:bg-accent"
      )}
    >
      <input {...getInputProps()} />
      <Upload className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
      <p className="text-lg font-medium">
        {isDragActive ? "Deposez le fichier ici" : "Glissez un PDF ici, ou cliquez pour selectionner"}
      </p>
      <p className="text-sm text-muted-foreground mt-2">
        PDF uniquement, max {Math.round(maxSize / 1024 / 1024)} MB
      </p>
    </div>
  );
}
```

#### KPICard

```tsx
// src/components/shared/KPICard.tsx
export function KPICard({ title, value, icon, trend, variant, href }: KPICardProps) {
  const Icon = ICONS[icon];
  return (
    <Card className={cn("hover:shadow-md transition-shadow", href && "cursor-pointer")}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">{title}</p>
            <p className="text-3xl font-bold">{value}</p>
            {trend !== undefined && (
              <div className={cn("flex items-center text-sm", trend >= 0 ? "text-green-600" : "text-red-600")}>
                {trend >= 0 ? <TrendingUp className="h-4 w-4 mr-1" /> : <TrendingDown className="h-4 w-4 mr-1" />}
                {Math.abs(trend)}%
              </div>
            )}
          </div>
          <div className={cn("p-3 rounded-full", VARIANTS[variant ?? "default"])}>
            <Icon className="h-6 w-6" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
```

#### SearchBar avec Filtres

```tsx
// src/components/shared/SearchBar.tsx
export function SearchBar({ value, onChange, placeholder }: SearchBarProps) {
  return (
    <div className="relative flex-1">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
      <Input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="pl-10"
      />
      {value && (
        <button onClick={() => onChange("")} className="absolute right-3 top-1/2 -translate-y-1/2">
          <X className="h-4 w-4 text-muted-foreground" />
        </button>
      )}
    </div>
  );
}
```

#### DataTable (TanStack Table)

```tsx
// src/components/shared/DataTable.tsx
export function DataTable<TData>({ columns, data, isLoading, pagination, onPaginationChange, totalCount }: DataTableProps<TData>) {
  const table = useReactTable({
    data,
    columns,
    pageCount: Math.ceil(totalCount / pagination.pageSize),
    state: { pagination },
    onPaginationChange,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    manualPagination: true,
  });

  return (
    <div className="space-y-4">
      <div className="rounded-md border overflow-x-auto">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((hg) => (
              <TableRow key={hg.id}>
                {hg.headers.map((header) => (
                  <TableHead key={header.id}>
                    {flexRender(header.column.columnDef.header, header.getContext())}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={columns.length}>
                  <LoadingSkeleton count={5} />
                </TableCell>
              </TableRow>
            ) : table.getRowModel().rows.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="text-center py-8">
                  Aucun resultat
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {pagination.pageIndex * pagination.pageSize + 1} -{" "}
          {Math.min((pagination.pageIndex + 1) * pagination.pageSize, totalCount)} sur {totalCount}
        </p>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()}>
            Precedent
          </Button>
          <Button variant="outline" size="sm" onClick={() => table.nextPage()} disabled={!table.getCanNextPage()}>
            Suivant
          </Button>
        </div>
      </div>
    </div>
  );
}
```



---

## 3. State Management (Zustand)

### 3.a. Philosophie

Zustand est utilise pour le state **client-only** (UI, auth, filtres). TanStack Query gère le state **serveur** (tenders, users, logs). Pas de duplication — Zustand ne stocke pas de données qui viennent du serveur.

### 3.b. authStore

```typescript
// src/stores/authStore.ts
import { create } from "zustand";
import { persist } from "zustand/middleware";
import { immer } from "zustand/middleware/immer";

interface User {
  id: string;
  email: string;
  name: string;
  role: "admin" | "manager" | "viewer";
  tenant_id: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;

  // Actions
  login: (credentials: { email: string; password: string }) => Promise<void>;
  logout: () => void;
  setUser: (user: User) => void;
  refreshToken: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  immer(
    persist(
      (set, get) => ({
        user: null,
        token: null,
        isLoading: false,
        isAuthenticated: false,

        login: async (credentials) => {
          set({ isLoading: true });
          try {
            const response = await authService.login(credentials);
            set({
              user: response.user,
              token: response.access_token,
              isAuthenticated: true,
              isLoading: false,
            });
          } catch (error) {
            set({ isLoading: false });
            throw error;
          }
        },

        logout: () => {
          authService.logout();
          set({ user: null, token: null, isAuthenticated: false });
          // Reset other stores
          useTenderStore.getState().reset();
          useUIStore.getState().reset();
        },

        setUser: (user) => set({ user }),

        refreshToken: async () => {
          try {
            const response = await authService.refresh();
            set({ token: response.access_token });
          } catch {
            get().logout();
          }
        },
      }),
      {
        name: "taka-auth",
        partialize: (state) => ({ token: state.token }),
      }
    )
  )
);

// Selector derive
export const useIsAdmin = () => useAuthStore((s) => s.user?.role === "admin");
export const useCanEdit = () => useAuthStore((s) => ["admin", "manager"].includes(s.user?.role ?? ""));
```

### 3.c. tenderStore

```typescript
// src/stores/tenderStore.ts
import { create } from "zustand";
import { immer } from "zustand/middleware/immer";

interface TenderFilters {
  search: string;
  stage: string | null;
  qualification: string | null;
  deadlineFrom: string | null;
  deadlineTo: string | null;
}

interface Pagination {
  pageIndex: number;
  pageSize: number;
}

interface TenderState {
  // Filtres
  filters: TenderFilters;
  setFilters: (filters: Partial<TenderFilters>) => void;
  resetFilters: () => void;

  // Pagination
  pagination: Pagination;
  setPagination: (pagination: Partial<Pagination>) => void;

  // Selection
  selectedTenderId: string | null;
  setSelectedTenderId: (id: string | null) => void;

  // UI
  isCreateOpen: boolean;
  setCreateOpen: (open: boolean) => void;
  isUploadOpen: boolean;
  setUploadOpen: (open: boolean) => void;

  // Reset
  reset: () => void;
}

const defaultFilters: TenderFilters = {
  search: "",
  stage: null,
  qualification: null,
  deadlineFrom: null,
  deadlineTo: null,
};

const defaultPagination: Pagination = {
  pageIndex: 0,
  pageSize: 25,
};

export const useTenderStore = create<TenderState>()(
  immer((set) => ({
    filters: { ...defaultFilters },
    pagination: { ...defaultPagination },
    selectedTenderId: null,
    isCreateOpen: false,
    isUploadOpen: false,

    setFilters: (filters) =>
      set((state) => {
        Object.assign(state.filters, filters);
        state.pagination.pageIndex = 0; // Reset page on filter change
      }),

    resetFilters: () => set({ filters: { ...defaultFilters }, pagination: { ...defaultPagination, pageSize: get().pagination.pageSize } }),

    setPagination: (pagination) =>
      set((state) => {
        Object.assign(state.pagination, pagination);
      }),

    setSelectedTenderId: (id) => set({ selectedTenderId: id }),
    setCreateOpen: (open) => set({ isCreateOpen: open }),
    setUploadOpen: (open) => set({ isUploadOpen: open }),

    reset: () =>
      set({
        filters: { ...defaultFilters },
        pagination: { ...defaultPagination },
        selectedTenderId: null,
        isCreateOpen: false,
        isUploadOpen: false,
      }),
  }))
);
```

### 3.d. pipelineStore

```typescript
// src/stores/pipelineStore.ts
import { create } from "zustand";
import { immer } from "zustand/middleware/immer";

interface PipelineState {
  stages: Stage[];
  setStages: (stages: Stage[]) => void;

  // Optimistic update DnD
  moveTenderOptimistic: (tenderId: string, targetStageId: string) => void;
  revertMove: (tenderId: string, originalStageId: string) => void;

  // Filters
  qualFilter: Qualification | "ALL";
  setQualFilter: (filter: Qualification | "ALL") => void;
}

export const usePipelineStore = create<PipelineState>()(
  immer((set) => ({
    stages: [],
    qualFilter: "ALL",

    setStages: (stages) => set({ stages }),

    moveTenderOptimistic: (tenderId, targetStageId) =>
      set((state) => {
        // Update tender stage in local state
        for (const stage of state.stages) {
          const idx = stage.tenders.findIndex((t) => t.id === tenderId);
          if (idx !== -1) {
            const [tender] = stage.tenders.splice(idx, 1);
            tender.stage_id = targetStageId;
            const targetStage = state.stages.find((s) => s.id === targetStageId);
            targetStage?.tenders.push(tender);
            break;
          }
        }
      }),

    setQualFilter: (filter) => set({ qualFilter: filter }),
  }))
);
```

### 3.e. uiStore

```typescript
// src/stores/uiStore.ts
import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import { persist } from "zustand/middleware";

interface Toast {
  id: string;
  title: string;
  description?: string;
  variant: "default" | "destructive" | "success";
}

interface UIState {
  // Sidebar
  sidebarOpen: boolean;
  toggleSidebar: () => void;

  // Modals
  activeModal: string | null;
  modalData: Record<string, unknown> | null;
  openModal: (modal: string, data?: Record<string, unknown>) => void;
  closeModal: () => void;

  // Toasts
  toasts: Toast[];
  addToast: (toast: Omit<Toast, "id">) => void;
  removeToast: (id: string) => void;

  // Theme
  theme: "light" | "dark" | "system";
  setTheme: (theme: "light" | "dark" | "system") => void;

  reset: () => void;
}

export const useUIStore = create<UIState>()(
  immer(
    persist(
      (set) => ({
        sidebarOpen: true,
        theme: "system",
        activeModal: null,
        modalData: null,
        toasts: [],

        toggleSidebar: () => set((state) => { state.sidebarOpen = !state.sidebarOpen; }),
        setTheme: (theme) => set({ theme }),

        openModal: (modal, data) => set({ activeModal: modal, modalData: data ?? null }),
        closeModal: () => set({ activeModal: null, modalData: null }),

        addToast: (toast) =>
          set((state) => {
            state.toasts.push({ ...toast, id: crypto.randomUUID() });
          }),

        removeToast: (id) =>
          set((state) => {
            state.toasts = state.toasts.filter((t) => t.id !== id);
          }),

        reset: () => set({ activeModal: null, modalData: null, toasts: [] }),
      }),
      {
        name: "taka-ui",
        partialize: (state) => ({ sidebarOpen: state.sidebarOpen, theme: state.theme }),
      }
    )
  )
);
```

### 3.f. API Service (Axios)

```typescript
// src/services/api.ts
import axios from "axios";
import { useAuthStore } from "@stores/authStore";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
});

// Request interceptor — injecte le token JWT
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor — gestion 401 + refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        await useAuthStore.getState().refreshToken();
        const newToken = useAuthStore.getState().token;
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api(originalRequest);
      } catch {
        useAuthStore.getState().logout();
        window.location.href = "/login";
        return Promise.reject(error);
      }
    }

    // Erreurs 500 — toast notification
    if (error.response?.status >= 500) {
      useUIStore.getState().addToast({
        title: "Erreur serveur",
        description: "Une erreur est survenue. Reessayez plus tard.",
        variant: "destructive",
      });
    }

    return Promise.reject(error);
  }
);
```

### 3.g. Hooks React Query

```typescript
// src/hooks/useTenders.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { tenderService } from "@services/tender.service";

export function useTenders(params: TenderListParams) {
  return useQuery({
    queryKey: ["tenders", params],
    queryFn: () => tenderService.list(params),
    placeholderData: (previousData) => previousData, // keepPreviousData
  });
}

export function useTender(id: string) {
  return useQuery({
    queryKey: ["tender", id],
    queryFn: () => tenderService.getById(id),
    enabled: !!id,
  });
}

export function useCreateTenderMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: tenderService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tenders"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useUpdateTenderMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: TenderUpdate }) =>
      tenderService.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["tender", variables.id] });
      queryClient.invalidateQueries({ queryKey: ["tenders"] });
    },
  });
}

export function useDeleteTenderMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: tenderService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tenders"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useQualifyTenderMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (tenderId: string) => tenderService.qualify(tenderId),
    onSuccess: (_, tenderId) => {
      queryClient.invalidateQueries({ queryKey: ["tender", tenderId] });
      queryClient.invalidateQueries({ queryKey: ["tenders"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}
```

```typescript
// src/hooks/useUpload.ts
import { useMutation } from "@tanstack/react-query";
import { uploadService } from "@services/upload.service";

export function useUploadDCE() {
  return useMutation({
    mutationFn: ({
      file,
      onProgress,
    }: {
      file: File;
      onProgress: (progress: number) => void;
    }) => uploadService.upload(file, onProgress),
  });
}
```

### 3.h. Router avec Guards

```tsx
// src/App.tsx
import { createBrowserRouter, Navigate, Outlet } from "react-router-dom";
import { Layout } from "@components/layout/Layout";
import { useAuthStore } from "@stores/authStore";
import { Suspense, lazy } from "react";
import { LoadingSkeleton } from "@components/shared/LoadingSkeleton";

// Lazy loading des pages
const LoginPage = lazy(() => import("@pages/LoginPage"));
const DashboardPage = lazy(() => import("@pages/DashboardPage"));
const TendersPage = lazy(() => import("@pages/TendersPage"));
const TenderDetailPage = lazy(() => import("@pages/TenderDetailPage"));
const PipelinePage = lazy(() => import("@pages/PipelinePage"));
const UploadPage = lazy(() => import("@pages/UploadPage"));
const MemoryPage = lazy(() => import("@pages/MemoryPage"));
const SettingsPage = lazy(() => import("@pages/SettingsPage"));
const AuditLogsPage = lazy(() => import("@pages/AuditLogsPage"));

// Route guard — authentification
function AuthGuard({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
}

// Route guard — admin uniquement
function AdminGuard({ children }: { children: React.ReactNode }) {
  const isAdmin = useAuthStore((s) => s.user?.role === "admin");
  return isAdmin ? <>{children}</> : <Navigate to="/dashboard" replace />;
}

// Route guard — manager+
function ManagerGuard({ children }: { children: React.ReactNode }) {
  const role = useAuthStore((s) => s.user?.role);
  const canEdit = role === "admin" || role === "manager";
  return canEdit ? <>{children}</> : <Navigate to="/dashboard" replace />;
}

// Layout wrapper avec suspense
function PageWrapper({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<LoadingSkeleton className="h-screen" />}>{children}</Suspense>;
}

export const router = createBrowserRouter([
  {
    path: "/login",
    element: (
      <PageWrapper>
        <LoginPage />
      </PageWrapper>
    ),
  },
  {
    path: "/",
    element: (
      <AuthGuard>
        <Layout />
      </AuthGuard>
    ),
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      {
        path: "dashboard",
        element: (
          <PageWrapper>
            <DashboardPage />
          </PageWrapper>
        ),
      },
      {
        path: "tenders",
        element: (
          <PageWrapper>
            <TendersPage />
          </PageWrapper>
        ),
      },
      {
        path: "tenders/:id",
        element: (
          <PageWrapper>
            <TenderDetailPage />
          </PageWrapper>
        ),
      },
      {
        path: "pipeline",
        element: (
          <PageWrapper>
            <PipelinePage />
          </PageWrapper>
        ),
      },
      {
        path: "upload",
        element: (
          <ManagerGuard>
            <PageWrapper>
              <UploadPage />
            </PageWrapper>
          </ManagerGuard>
        ),
      },
      {
        path: "memory",
        element: (
          <PageWrapper>
            <MemoryPage />
          </PageWrapper>
        ),
      },
      {
        path: "settings",
        element: (
          <PageWrapper>
            <SettingsPage />
          </PageWrapper>
        ),
      },
      {
        path: "admin/audit",
        element: (
          <AdminGuard>
            <PageWrapper>
              <AuditLogsPage />
            </PageWrapper>
          </AdminGuard>
        ),
      },
    ],
  },
]);
```

---

## 4. DevOps & Deploiement

### 4.a. Architecture Docker Compose (Production)

```yaml
# docker-compose.yml — Production
version: "3.8"

services:
  db:
    image: ankane/pgvector:pg15
    container_name: taka-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-takaos}
      POSTGRES_USER: ${POSTGRES_USER:-taka}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "127.0.0.1:5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-taka} -d ${POSTGRES_DB:-takaos}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    networks:
      - taka-network
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 256M

  api:
    image: ghcr.io/${GITHUB_OWNER}/taka-os-api:${TAG:-latest}
    container_name: taka-api
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-taka}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB:-takaos}
      SECRET_KEY: ${SECRET_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ENVIRONMENT: production
      LOG_LEVEL: INFO
      CORS_ORIGINS: ${CORS_ORIGINS:-https://${DOMAIN}}
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - uploads:/app/uploads
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 30s
    networks:
      - taka-network
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 256M

  web:
    image: ghcr.io/${GITHUB_OWNER}/taka-os-web:${TAG:-latest}
    container_name: taka-web
    restart: unless-stopped
    depends_on:
      - api
    networks:
      - taka-network
    deploy:
      resources:
        limits:
          memory: 128M

  nginx:
    image: nginx:1.25-alpine
    container_name: taka-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - certbot-data:/etc/letsencrypt
      - certbot-www:/var/www/certbot
    depends_on:
      - api
      - web
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 15s
      timeout: 5s
      retries: 3
    networks:
      - taka-network

  certbot:
    image: certbot/certbot:latest
    container_name: taka-certbot
    volumes:
      - certbot-data:/etc/letsencrypt
      - certbot-www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
    networks:
      - taka-network

volumes:
  pgdata:
    driver: local
  uploads:
    driver: local
  certbot-data:
    driver: local
  certbot-www:
    driver: local

networks:
  taka-network:
    driver: bridge
```

### 4.b. Dockerfile Frontend (Multi-stage)

```dockerfile
# frontend/Dockerfile — Multi-stage build
# ---- Stage 1: Build ----
FROM node:20-alpine AS builder

WORKDIR /app

# Dependencies
COPY package*.json ./
RUN npm ci --only=production=false

# Source + build
COPY . .
RUN npm run build

# ---- Stage 2: Serve (Nginx) ----
FROM nginx:1.25-alpine

# Copy build
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Security headers + SPA fallback
RUN echo 'server { \
    listen 80; \
    root /usr/share/nginx/html; \
    index index.html; \
    \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    \
    location /health { \
        access_log off; \
        return 200 "healthy\n"; \
        add_header Content-Type text/plain; \
    } \
    \
    gzip on; \
    gzip_types text/plain text/css application/json application/javascript text/xml; \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
```

### 4.c. Dockerfile Backend

```dockerfile
# backend/Dockerfile — Python 3.12 slim
FROM python:3.12-slim AS builder

WORKDIR /app

# Build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ---- Runtime ----
FROM python:3.12-slim

WORKDIR /app

# Runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Application
COPY . .

# Create uploads dir
RUN mkdir -p /app/uploads

# Migrations + start
CMD alembic upgrade head && \
    gunicorn app.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 2 \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

### 4.d. Configuration Nginx (Production)

```nginx
# nginx/conf.d/takaos.conf
upstream api_backend {
    server api:8000;
    keepalive 32;
}

upstream web_frontend {
    server web:80;
    keepalive 32;
}

# HTTP → HTTPS redirect
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name ${DOMAIN};

    # SSL
    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;

    # Security headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # API proxy
    location /api/ {
        proxy_pass http://api_backend/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Rate limiting
        limit_req zone=api_limit burst=20 nodelay;
    }

    # WebSocket (SSE pour parsing progress)
    location /api/v1/stream/ {
        proxy_pass http://api_backend/v1/stream/;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_read_timeout 86400s;
        proxy_buffering off;
    }

    # Frontend SPA
    location / {
        proxy_pass http://web_frontend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;

        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            proxy_pass http://web_frontend;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}

# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
```

### 4.e. Variables d'Environnement (.env)

```bash
# === TAKA OS — Configuration Production ===

# Domaine
DOMAIN=takaos.votre-domaine.fr

# Base de donnees
POSTGRES_DB=takaos
POSTGRES_USER=taka
POSTGRES_PASSWORD=<GENERER_MDP_FORT_32_CHARS>

# Securite
SECRET_KEY=<GENERER_CLE_ALEATOIRE_64_CHARS>

# OpenAI (qualification agentic)
OPENAI_API_KEY=sk-...

# GitHub Container Registry
GITHUB_OWNER=votre-org
GITHUB_TOKEN=ghp_...

# VPS
VPS_HOST=<IP_VPS>
VPS_USER=deploy
VPS_SSH_KEY=~/.ssh/id_ed25519_deploy

# CORS (production)
CORS_ORIGINS=https://takaos.votre-domaine.fr

# Backup (optionnel)
S3_ENDPOINT=s3.eu-central-1.amazonaws.com
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
S3_BUCKET=takaos-backups
```

### 4.f. CI/CD GitHub Actions

#### Workflow 1 — Tests (Pull Request)

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: ankane/pgvector:pg15
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: takaos_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"

      - name: Install dependencies
        working-directory: ./backend
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Lint (ruff)
        working-directory: ./backend
        run: ruff check .

      - name: Type check (mypy)
        working-directory: ./backend
        run: mypy .

      - name: Run tests
        working-directory: ./backend
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:test@localhost:5432/takaos_test
        run: pytest -xvs --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
          cache-dependency-path: ./frontend/package-lock.json

      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci

      - name: Lint (ESLint)
        working-directory: ./frontend
        run: npm run lint

      - name: Type check (tsc)
        working-directory: ./frontend
        run: npx tsc --noEmit

      - name: Build
        working-directory: ./frontend
        run: npm run build
```

#### Workflow 2 — Build & Push Images

```yaml
# .github/workflows/build.yml
name: Build & Push

on:
  push:
    branches: [main, develop]
    tags: ["v*"]

env:
  REGISTRY: ghcr.io
  IMAGE_API: ghcr.io/${{ github.repository_owner }}/taka-os-api
  IMAGE_WEB: ghcr.io/${{ github.repository_owner }}/taka-os-web

jobs:
  build-api:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Docker meta
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.IMAGE_API }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=sha,prefix={{branch}}-

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build & push
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  build-web:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Docker meta
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.IMAGE_WEB }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=sha,prefix={{branch}}-

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build & push
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          build-args: |
            VITE_API_URL=/api
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

#### Workflow 3 — Deploy VPS

```yaml
# .github/workflows/deploy.yml
name: Deploy to VPS

on:
  workflow_run:
    workflows: ["Build & Push"]
    branches: [main]
    types: [completed]

jobs:
  deploy:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    steps:
      - uses: actions/checkout@v4

      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /opt/takaos

            # Pull latest compose + env
            git pull origin main

            # Login GHCR
            echo ${{ secrets.GITHUB_TOKEN }} | docker login ghcr.io -u ${{ github.actor }} --password-stdin

            # Pull new images
            TAG=main docker compose pull

            # Database backup avant migration
            docker compose exec -T db pg_dump -U taka takaos | gzip > backups/pre-deploy-$(date +%Y%m%d-%H%M%S).sql.gz

            # Zero-downtime deploy
            docker compose up -d --no-deps --scale api=2 api
            sleep 10
            docker compose up -d --no-deps --scale api=1 api

            # Frontend + nginx
            docker compose up -d --no-deps web nginx

            # Cleanup
            docker system prune -f
            docker volume prune -f

            # Health check
            sleep 5
            curl -f http://localhost:8000/health || exit 1
```

### 4.g. Health Endpoint (Backend)

```python
# backend/app/api/health.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
import psutil
import shutil

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
async def health_check(db: AsyncSession = Depends(get_db)):
    checks = {}

    # DB check
    try:
        await db.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"
        raise HTTPException(status_code=503, detail=checks)

    # Disk check
    disk = shutil.disk_usage("/")
    disk_free_pct = disk.free / disk.total * 100
    checks["disk"] = {
        "status": "ok" if disk_free_pct > 10 else "warning",
        "free_percent": round(disk_free_pct, 1),
    }

    # Memory check
    memory = psutil.virtual_memory()
    checks["memory"] = {
        "status": "ok" if memory.percent < 90 else "warning",
        "used_percent": memory.percent,
    }

    return {
        "status": "healthy",
        "checks": checks,
        "version": "1.0.0",
    }
```

### 4.h. Logging Structure (Backend)

```python
# backend/app/core/logging.py
import structlog
import logging
import sys

# Configuration structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("takaos")

# Middleware FastAPI pour log des requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    logger.info(
        "request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=round(duration * 1000, 2),
        user=request.state.user.id if hasattr(request.state, "user") else None,
    )

    return response
```

### 4.i. Backup Automatique

```bash
#!/bin/bash
# scripts/backup.sh — Backup quotidien PostgreSQL + Uploads

set -euo pipefail

BACKUP_DIR="/opt/takaos/backups"
DATE=$(date +%Y%m%d-%H%M%S)
RETENTION_DAYS=7
S3_BUCKET="${S3_BUCKET:-}"

# PostgreSQL backup
echo "[+] Backup PostgreSQL..."
docker compose exec -T db pg_dump -U "${POSTGRES_USER}" "${POSTGRES_DB}" | gzip > "${BACKUP_DIR}/db-${DATE}.sql.gz"

# Uploads backup
echo "[+] Backup Uploads..."
tar czf "${BACKUP_DIR}/uploads-${DATE}.tar.gz" -C /opt/takaos uploads/

# Cleanup local (retention 7 jours)
echo "[+] Cleanup local backups (> ${RETENTION_DAYS} jours)..."
find "${BACKUP_DIR}" -name "*.sql.gz" -mtime +${RETENTION_DAYS} -delete
find "${BACKUP_DIR}" -name "*.tar.gz" -mtime +${RETENTION_DAYS} -delete

# Upload S3 (si configure)
if [ -n "$S3_BUCKET" ]; then
    echo "[+] Upload vers S3..."
    aws s3 cp "${BACKUP_DIR}/db-${DATE}.sql.gz" "s3://${S3_BUCKET}/db/"
    aws s3 cp "${BACKUP_DIR}/uploads-${DATE}.tar.gz" "s3://${S3_BUCKET}/uploads/"

    # Cleanup S3 (retention 30 jours)
    aws s3 ls "s3://${S3_BUCKET}/db/" | awk '$1 < "'$(date -d '30 days ago' +%Y-%m-%d)'" {print $4}' | xargs -I {} aws s3 rm "s3://${S3_BUCKET}/db/{}"
fi

echo "[+] Backup termine: ${DATE}"
```

```cron
# Crontab — Backup quotidien a 3h du matin
0 3 * * * /opt/takaos/scripts/backup.sh >> /var/log/takaos-backup.log 2>&1
```

### 4.j. Mise a Jour Zero-Downtime

**Strategie :** Blue-green via Docker Compose

```bash
#!/bin/bash
# scripts/deploy.sh — Zero-downtime deployment

set -e

echo "=== Deploiement TAKA OS ==="

# 1. Backup DB
docker compose exec -T db pg_dump -U taka takaos | gzip > "backups/pre-deploy-$(date +%s).sql.gz"

# 2. Pull images
docker compose pull

# 3. Start new containers (blue)
TAG=$TAG docker compose up -d --no-deps --scale api=2 --no-recreate api

# 4. Health check nouveau container
sleep 10
NEW_CONTAINER=$(docker compose ps -q api | tail -1)
docker exec "$NEW_CONTAINER" curl -f http://localhost:8000/health || {
    echo "[!] Health check failed — rollback"
    docker compose up -d --no-deps --scale api=1 api
    exit 1
}

# 5. Stop ancien container (green)
OLD_CONTAINER=$(docker compose ps -q api | head -1)
docker stop "$OLD_CONTAINER"
docker rm "$OLD_CONTAINER"

# 6. Scale back to 1
docker compose up -d --no-deps --scale api=1 api

# 7. Frontend + nginx
docker compose up -d --no-deps web nginx

# 8. Cleanup
docker system prune -f

echo "=== Deploiement OK ==="
```

### 4.k. Rollback

```bash
#!/bin/bash
# scripts/rollback.sh — Rollback vers version precedente

set -e

PREVIOUS_TAG=${1:-"$(git rev-parse HEAD~1)"}

echo "=== Rollback vers ${PREVIOUS_TAG} ==="

# Tag images precedentes
export TAG=${PREVIOUS_TAG}

# Redeploy
docker compose pull
docker compose up -d

echo "=== Rollback OK ==="
```

---

## 5. Securite Frontend

### 5.a. CSP Headers (via Nginx)

```nginx
# Ajouter dans le server block Nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self'; connect-src 'self' /api; frame-ancestors 'none'; base-uri 'self'; form-action 'self';" always;
```

### 5.b. Validation des Inputs (Zod)

```typescript
// src/lib/validators.ts
import { z } from "zod";

export const tenderSchema = z.object({
  reference: z.string().min(1, "Reference requise").max(100),
  title: z.string().min(1, "Titre requis").max(500),
  description: z.string().max(5000).optional(),
  buyer: z.string().min(1, "Acheteur requis").max(200),
  deadline: z.string().datetime("Date invalide"),
  estimated_value: z.number().min(0).optional(),
  cpv_code: z.string().regex(/^\d{8}-\d$/, "Code CPV invalide (format: 12345678-9)").optional(),
  location: z.string().max(200).optional(),
  procedure_type: z.enum(["open", "restricted", "negotiated", "dialogue"]).optional(),
});

export const loginSchema = z.object({
  email: z.string().email("Email invalide").max(255),
  password: z.string().min(8, "Min. 8 caracteres").max(128),
});

export const userInviteSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
  role: z.enum(["admin", "manager", "viewer"]),
});
```

### 5.c. Variables d'Environnement Vite

```bash
# .env.development
VITE_API_URL=http://localhost:8000

# .env.production
VITE_API_URL=/api
```

**Regles :**
- Toutes les variables Vite doivent commencer par `VITE_`
- Jamais de secrets (clés API, tokens) dans les variables Vite publics
- Les secrets backend restent côté backend uniquement
- `import.meta.env` pour accéder aux variables

### 5.d. Gestion des Tokens

```typescript
// src/services/auth.service.ts
class AuthService {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>("/auth/login", credentials);

    // Stockage securise
    this.setToken(response.data.access_token);

    return response.data;
  }

  private setToken(token: string): void {
    // En production : httpOnly cookie gere par le backend
    // En dev : stockage memoire Zustand uniquement
    if (import.meta.env.PROD) {
      // Le backend set un httpOnly cookie
      return;
    }
    useAuthStore.getState().token = token;
  }

  async refresh(): Promise<{ access_token: string }> {
    const response = await api.post("/auth/refresh");
    return response.data;
  }

  logout(): void {
    // Appel au backend pour invalider le token
    api.post("/auth/logout").catch(() => {});
  }
}

export const authService = new AuthService();
```

### 5.e. Sécurité Routing

```tsx
// Route guards deja definis dans App.tsx
// Protection supplementaire : hook usePermission

export function usePermission(permission: Permission): boolean {
  const { user } = useAuthStore();
  const rolePermissions: Record<Role, Permission[]> = {
    admin: ["read", "write", "delete", "manage_users", "manage_settings", "view_audit"],
    manager: ["read", "write", "delete", "manage_settings"],
    viewer: ["read"],
  };
  return user ? rolePermissions[user.role].includes(permission) : false;
}
```

### 5.f. Checklist Sécurite Frontend

| # | Controle | Statut | Implementation |
|---|----------|--------|----------------|
| 1 | HTTPS only | Obligatoire | Nginx redirect 80→443 + HSTS |
| 2 | CSP headers | Obligatoire | Nginx add_header CSP |
| 3 | X-Frame-Options | Obligatoire | Nginx SAMEORIGIN |
| 4 | X-Content-Type-Options | Obligatoire | Nginx nosniff |
| 5 | Input validation | Obligatoire | Zod schemas tous formulaires |
| 6 | Output encoding | Obligatoire | React JSX auto-escape |
| 7 | No secrets in code | Obligatoire | .env + variables d'environnement |
| 8 | JWT httpOnly cookie | Recommande | Backend set cookie, pas localStorage |
| 9 | Token refresh auto | Obligatoire | Axios interceptor 401 → refresh |
| 10 | Rate limiting | Obligatoire | Nginx limit_req 10r/s |
| 11 | Session timeout | Recommande | JWT expiry 15min, refresh 7j |
| 12 | Audit logging | Obligatoire | Toutes les actions CRUD loggees |
| 13 | Dependency scanning | Recommande | Dependabot + npm audit |

---

## 6. Annexes

### 6.a. package.json Frontend

```json
{
  "name": "takaos-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "lint:fix": "eslint . --ext ts,tsx --fix",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "@dnd-kit/core": "^6.1.0",
    "@dnd-kit/sortable": "^8.0.0",
    "@dnd-kit/utilities": "^3.2.2",
    "@hookform/resolvers": "^3.3.4",
    "@radix-ui/react-accordion": "^1.1.2",
    "@radix-ui/react-alert-dialog": "^1.0.5",
    "@radix-ui/react-avatar": "^1.0.4",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-label": "^2.0.2",
    "@radix-ui/react-popover": "^1.0.7",
    "@radix-ui/react-progress": "^1.0.3",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-separator": "^1.0.3",
    "@radix-ui/react-slot": "^1.0.2",
    "@radix-ui/react-switch": "^1.0.3",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-toast": "^1.1.5",
    "@radix-ui/react-tooltip": "^1.0.7",
    "@tanstack/react-query": "^5.17.0",
    "@tanstack/react-table": "^8.11.0",
    "axios": "^1.6.5",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "date-fns": "^3.0.6",
    "lucide-react": "^0.303.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-dropzone": "^14.2.3",
    "react-hook-form": "^7.49.2",
    "react-router-dom": "^6.21.1",
    "recharts": "^2.10.3",
    "tailwind-merge": "^2.2.0",
    "tailwindcss-animate": "^1.0.7",
    "zod": "^3.22.4",
    "zustand": "^4.4.7"
  },
  "devDependencies": {
    "@types/react": "^18.2.46",
    "@types/react-dom": "^18.2.18",
    "@typescript-eslint/eslint-plugin": "^6.16.0",
    "@typescript-eslint/parser": "^6.16.0",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "eslint": "^8.56.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.5",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.3.3",
    "vite": "^5.0.10"
  }
}
```

### 6.b. Structure des Types TypeScript

```typescript
// src/types/auth.ts
export interface User {
  id: string;
  email: string;
  name: string;
  role: "admin" | "manager" | "viewer";
  tenant_id: string;
  created_at: string;
  last_login: string | null;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// src/types/tender.ts
export type Stage = "draft" | "identified" | "qualified" | "preparing" | "submitted" | "awarded" | "lost" | "cancelled";

export type Qualification = "GO" | "MAYBE" | "NO-GO" | "PENDING";

export interface Tender {
  id: string;
  reference: string;
  title: string;
  description: string | null;
  buyer: string;
  deadline: string;
  estimated_value: number | null;
  cpv_code: string | null;
  location: string | null;
  procedure_type: string | null;
  stage: Stage;
  qualification: Qualification;
  qualification_result: QualificationResult | null;
  documents: Document[];
  created_at: string;
  updated_at: string;
  created_by: string;
  tenant_id: string;
}

export interface QualificationResult {
  id: string;
  tender_id: string;
  verdict: Qualification;
  overall_score: number;
  criteria_scores: Record<string, number>;
  justification: string;
  created_at: string;
}

// src/types/api.ts
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResult<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
```

### 6.c. Commandes Utiles

```bash
# === DEVELOPPEMENT ===
# Lancer le frontend
cd frontend && npm run dev        # http://localhost:3000

# Lancer le backend
cd backend && uvicorn app.main:app --reload --port 8000

# === DOCKER LOCAL ===
docker compose up -d              # Tout demarrer
docker compose logs -f api        # Logs API
docker compose exec db psql -U taka -d takaos  # Shell PostgreSQL

# === PRODUCTION ===
# Deploy
cd /opt/takaos && git pull && ./scripts/deploy.sh

# Backup manuel
cd /opt/takaos && ./scripts/backup.sh

# Logs production
docker compose logs -f --tail 100

# Stats ressources
docker stats
```

### 6.d. Matrice des Permissions

| Fonctionnalite | Admin | Manager | Viewer |
|----------------|-------|---------|--------|
| Dashboard | ✅ | ✅ | ✅ |
| Liste AO | ✅ | ✅ | ✅ |
| Fiche AO (lecture) | ✅ | ✅ | ✅ |
| Fiche AO (edition) | ✅ | ✅ | ❌ |
| Creer AO | ✅ | ✅ | ❌ |
| Supprimer AO | ✅ | ✅ | ❌ |
| Qualifier AO | ✅ | ✅ | ❌ |
| Pipeline Kanban (DnD) | ✅ | ✅ | ❌ |
| Pipeline Kanban (vue) | ✅ | ✅ | ✅ |
| Upload DCE | ✅ | ✅ | ❌ |
| Memoire (recherche) | ✅ | ✅ | ✅ |
| Parametres profil | ✅ | ✅ | ✅ |
| Parametres tenant | ✅ | ❌ | ❌ |
| Gestion utilisateurs | ✅ | ❌ | ❌ |
| Audit Logs | ✅ | ❌ | ❌ |

---

**Fin de la Section 4 — Frontend & DevOps**

*Ce document specifie l'integralite de l'architecture frontend et de l'infrastructure DevOps pour TAKA OS. Toutes les technologies, composants, stores, pipelines CI/CD et procedures de deploiement sont detailles avec des exemples de code fonctionnels.*
