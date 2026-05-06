# TAKA OS — Changelog

## v1.0.0 — 2025-05-07

### Première release stable

TAKA OS est un système d'exploitation IA open-source (MIT) pour la veille,
l'analyse, la rédaction et le dépôt automatisé d'appels d'offres publics
(France, Belgique, Maroc, Union Européenne).

### Architecture
- 5 couches agentiques : Sensorimoteur → Mémoire → Agents → Délibération → Métacognition
- 50 tables PostgreSQL + pgvector
- FastAPI backend + React frontend + Docker
- Mistral AI (embeddings 1024d + LLM)

### Agents (5/6)
- **Veilleur** : Veille sur 10 sources (BOAMP, JOUE/TED, e-Notification, Maroc,
  Régions, Départements, Métropoles, Marchés État, Agrégateurs FR)
- **Scorer** : Score multi-dimensionnel (5 dimensions × 3 profils) avec XAI
- **Rédacteur** : Génération de réponses IA avec templates métier
- **Déposant** : Soumission automatique (BOAMP, e-Notification) avec fallback mock
- **Auditor** : Audit trail complet, détection d'anomalies, rapports de conformité PDF

### Infrastructure
- **Authentification** : JWT + bcrypt + MFA + 5 rôles RBAC
- **Billing** : Stripe Checkout (3 tiers : Free/Pro/Enterprise) + Customer Portal
- **Email** : Alertes quotidiennes avec Resend (graceful degradation)
- **API Publique** : Clés API `tak_live_xxx`, rate limiting, permissions par scope
- **Collaboration** : Commentaires threaded, mentions @user, notifications in-app
- **Workflow** : Approbation multi-niveaux (Collaborateur → Manager → DG)
- **Analytics** : Funnel de conversion, ROI estimé, prédictions de gain (Mistral)
- **Import/Export** : CSV/Excel (multi-onglets), import bulk
- **Fiducial v0.1** : Écritures comptables partie double, export FEC A47FI-1
- **PWA** : Installable sur mobile, mode offline, service worker
- **Staging** : Docker Compose 5 services (nginx, backend, PostgreSQL, Redis, backup)

### Stack technique
Python 3.11, FastAPI, SQLAlchemy 2.0 async, PostgreSQL 15 + pgvector 0.5.1,
Pydantic v2, Mistral AI, React 18 + Vite + Tailwind + Zustand + Recharts,
Stripe, Resend, Docker Compose, ReportLab, Pandas, OpenPyXL.

### Licences
- Code : MIT License
- Dépendances : Voir pyproject.toml
