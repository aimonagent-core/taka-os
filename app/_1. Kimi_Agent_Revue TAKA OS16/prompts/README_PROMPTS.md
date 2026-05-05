# TAKA OS — Prompts Officiels Kimi Code

## Dossier `/prompts/`

Ce dossier contient les 4 prompts de sprint mis a jour, prets pour Kimi Code. Aucun autre document ici n'est pertinent pour le developpement.

---

## Les 4 Prompts (ordre d'execution)

| # | Fichier | Lignes | Fichiers specifies | Semaine | Contenu |
|---|---------|--------|-------------------|---------|---------|
| 1 | **SPRINT_0_FONDATION.md** | 2 925 | 37 | Semaine 1 | FastAPI, PostgreSQL+pgvector, JWT, 5 roles, MFA, Sentry, Rate Limiting, Circuit Breaker, Backup PG, Feature Flags, Memoire 3 zones, Audit hash chain, Docker, CI/CD |
| 2 | **SPRINT_1_SENSORIMOTRICE_MEMOIRE.md** | 4 552 | 39 | Semaine 2 | Parsing PDF 4 niveaux, Upload, Embeddings pgvector, Client Mistral AI, 4 types memoire, N Gates validation, Autonomie HIL, Kill switch, Tests E2E Playwright |
| 3 | **SPRINT_2_QUALIFIEUR_KANBAN.md** | 5 009 | 74 | Semaine 3 | Scoring Engine V2 (5D YAML), Business Lines multi-metiers, Dashboard Admin 15+ widgets, Dashboard Collaborateur, Kanban drag-drop, Rationalisation KPIs |
| 4 | **SPRINT_3_TRACKER_SAAS.md** | 9 157 | 139 | Semaine 4 | Alertes, i18n (FR/NL/EN/AR), RGAA accessibilite, Traçabilite forensique, AI Act conformite, Docker production, CI/CD deploy, Documentation tours |

**Total : 21 643 lignes | 289 fichiers specifies | 4 semaines de developpement**

---

## Regle d'or d'utilisation

**Executer les prompts SEQUENTIELLEMENT.** Chaque prompt suppose que les precedents sont termines. Ne pas sauter d'etape.

```
Semaine 1 : Copier SPRINT_0_FONDATION.md dans Kimi Code -> Executer
Semaine 2 : Copier SPRINT_1_SENSORIMOTRICE_MEMOIRE.md dans Kimi Code -> Executer
Semaine 3 : Copier SPRINT_2_QUALIFIEUR_KANBAN.md dans Kimi Code -> Executer
Semaine 4 : Copier SPRINT_3_TRACKER_SAAS.md dans Kimi Code -> Executer
```

---

## Ce qui est integre dans chaque prompt

### Sprint 0 — Fondations de production (nouveautes par rapport a l'ancien)
- **Sentry** : Error tracking backend + frontend + Error Boundaries React
- **Backup PostgreSQL** : Script `backup-db.sh` + cron + restore test
- **Rate Limiting** : SlowAPI par IP/tenant, limites par endpoint
- **Circuit Breaker** : PyCircuitBreaker sur Mistral API et BOAMP
- **MFA/TOTP** : Setup, verification, QR code, codes de secours
- **5 roles** : super_admin, tenant_admin, tenant_manager, tenant_collaborator, viewer
- **Feature Flags** : Table + service + gating par plan + kill switch
- **Memoire 3 zones** : Global, Tenant, Session avec TTL
- **Audit hash chain** : SHA-256 chainee, immuable

### Sprint 1 — Sensorimotrice + Memoire (nouveautes)
- **N Gates validation** : 6 gates (syntaxe, semantique, RBAC, idempotence, deterministe, HIL)
- **4 types memoire** : Episodique, Semantique, Procedurale, Transactionnelle
- **Autonomie HIL** : 4 niveaux, panel validation, kill switch
- **Tests E2E Playwright** : 3 suites (auth, tender-flow, kanban)

### Sprint 2 — Qualifieur + Kanban (nouveautes)
- **Scoring Engine V2** : 5 dimensions YAML, 3 profils, ScoreCard XAI
- **Business Lines** : Multi-metiers pour groupes comme Equans/SPIE
- **Dashboard Admin** : 15+ widgets, selecteur BL, KPIs rationalises
- **Feature Flags gating** : Free/Starter/Pro/Enterprise

### Sprint 3 — Tracker + SaaS Production (nouveautes)
- **i18n** : FR/NL/EN/AR, RTL arabe, Babel backend, React i18next
- **RGAA** : Tooltips, keyboard nav, axe-core tests, declaration
- **Traçabilite forensique** : Timeline, 5 couches, export PDF
- **AI Act conformite** : Transparence, explication, contestation
- **Docker production** : Optimise, Nginx, SSL, CI/CD deploy

---

## Stack technique (verrouillee)

| Couche | Tech | Version |
|--------|------|---------|
| Backend | Python | 3.12+ (<3.14) |
| Framework | FastAPI | latest |
| ORM | SQLAlchemy | 2.0 async |
| DB | PostgreSQL + pgvector | 15+ |
| LLM | Mistral AI API | large-latest |
| Auth | JWT + bcrypt | - |
| MFA | PyOTP + QRCode | latest |
| Monitoring | Sentry SDK | latest |
| Rate Limit | SlowAPI | 0.1.9 |
| Circuit Breaker | PyBreaker | latest |
| Frontend | React + TypeScript | 18+ |
| Build | Vite | latest |
| CSS | Tailwind CSS | 3.x |
| UI | shadcn/ui | latest |
| i18n | React i18next | latest |
| E2E | Playwright | 1.42+ |
| Tours | React Joyride | latest |

---

## 5 regles absolues (non-negociables)

1. Un seul fichier modeles : `app/models/ao.py`
2. SQLAlchemy 2.0 async uniquement avec `expire_on_commit=False`
3. Python <3.14
4. Un seul conteneur DB (PostgreSQL+pgvector)
5. Pas de LangChain/CrewAI dans le MVP

---

## Fichiers dans ce dossier (etat final)

```
prompts/
├── README_PROMPTS.md              <- Ce fichier
├── SPRINT_0_FONDATION.md          <- Semaine 1 (Fondations)
├── SPRINT_1_SENSORIMOTRICE_MEMOIRE.md  <- Semaine 2 (Parsing + Memoire)
├── SPRINT_2_QUALIFIEUR_KANBAN.md       <- Semaine 3 (Scoring + Kanban)
└── SPRINT_3_TRACKER_SAAS.md            <- Semaine 4 (Production + Conformite)
```

**Aucun autre fichier n'est pertinent.** Les anciens prompts ont ete supprimes.

---

## Validation post-sprint

Apres chaque sprint, verifier que les fichiers suivants existent et fonctionnent :

### Post-Sprint 0
- [ ] `docker compose up` demarre sans erreur
- [ ] `http://localhost:8000/docs` affiche Swagger
- [ ] Login JWT fonctionne
- [ ] MFA setup fonctionne (QR code + verification)
- [ ] Sentry recoit les erreurs (tester avec une route /error)
- [ ] Rate limiting bloque apres 100 requetes/minute
- [ ] Backup `scripts/backup-db.sh` s'execute sans erreur
- [ ] Tests `pytest` passent (30+)

### Post-Sprint 1
- [ ] Upload PDF fonctionne
- [ ] Parsing 4 niveaux extrait texte + tableaux
- [ ] Embeddings pgvector fonctionnent
- [ ] N Gates bloquent les actions invalides
- [ ] Playwright E2E passent (3 suites)
- [ ] Memoire episodique stocke et recupere des souvenirs

### Post-Sprint 2
- [ ] Scoring 5D produit un ScoreCard JSON
- [ ] Kanban drag-drop fonctionne
- [ ] Dashboard Admin affiche les KPIs
- [ ] Business Lines isolent les donnees
- [ ] Feature Flags gatent selon le plan

### Post-Sprint 3
- [ ] Interface FR/NL/EN fonctionne
- [ ] RGAA axe-core tests passent
- [ ] Traçabilite forensique reconstitue une decision
- [ ] Docker production demarre
- [ ] CI/CD deploye automatiquement
