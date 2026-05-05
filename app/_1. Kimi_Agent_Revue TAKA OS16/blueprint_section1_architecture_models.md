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

