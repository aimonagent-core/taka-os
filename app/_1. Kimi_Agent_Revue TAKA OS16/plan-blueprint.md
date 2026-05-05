# Plan — Blueprint TAKA OS v1.0
## Document de Conception Technique Complete

### Contexte
Apres 5 GO du CEO, production du document de conception exhaustive avant developpement Kimi Code.
TAKA OS = OS agentic open source, vertical Appels d'Offres, stack simplifiee (lecons NEXA-MIND integrees).

### Sections a produire (en parallele)

**Agent 1 — Architecture & Modeles de Donnees**
- Vue d'ensemble architecturale (diagramme ASCII 3 couches MVP)
- Modeles SQLAlchemy 2.0 complets (tous les champs, types, index, contraintes)
- Modeles Pydantic v2 (request/response/validation)
- Diagramme entite-relation
- Migrations Alembic

**Agent 2 — API REST & Securite**
- Specification complete de tous les endpoints (method, path, body, response, codes)
- Auth JWT (dev-login, login reel, refresh token)
- RBAC (roles, permissions)
- Audit trail append-only
- Rate limiting
- Multi-tenancy isolation

**Agent 3 — Agents TAKA & Systeme de Memoire**
- Architecture des 3 agents (Sourcer, Qualifieur, Tracker)
- Flux de donnees complets (entree → traitement → sortie)
- Algorithme de scoring GO/NO-GO (regles + LLM fallback)
- pgvector : embeddings, index HNSW, recherche similarite
- Pipeline parsing PDF stratifie
- Integration Mistral AI (httpx + Jinja2, circuit breaker)

**Agent 4 — Frontend & DevOps**
- Architecture React + Vite + Tailwind
- Pages et composants (Kanban, fiche AO, upload, settings)
- Etats globaux (Zustand)
- Docker-compose production
- CI/CD GitHub Actions
- Monitoring et logging
- Backup PostgreSQL

**Agent 5 — Assembleur**
- Assembler les 4 sections en document coherente
- Table des matieres, numerotation, cross-references
- Roadmap detaillee (4 semaines)
- Plan de tests (unite, integration, E2E)
- Glossaire
- Production du .docx final

### Contraintes techniques (appliquees partout)
- Python 3.12+ (jamais 3.14)
- SQLAlchemy 2.0 async, expire_on_commit=False
- PostgreSQL 15 + pgvector (base unique)
- FastAPI, aucun framework ORM supplementaire
- Mistral AI (pas Kimi API)
- httpx + Jinja2 (pas LangChain)
- EventBus asyncio in-memory (pas Redis)
- JWT + passlib (pas Auth0)
- React + Vite + Tailwind (pas Next.js)
- Docker compose 1 VPS 6-8EUR
