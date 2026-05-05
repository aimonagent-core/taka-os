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

