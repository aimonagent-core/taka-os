# MEMO DE SESSION — TAKA OS
## Etat des lieux au 05 Mai 2026
## Contexte : Validation conceptuelle complete, pre-developpement

---

## 1. VISION PRODUIT (Validee)

TAKA OS = Systeme d'exploitation agentic open source (licence MIT) verticalise sur les Appels d'Offres publics. Cible : PME/ETI soumissionnaires + acheteurs publics en France, Belgique, Maroc.

**Decision strategique validee** : Concentration exclusive sur le vertical AO. La version Fiducial (experts-comptables) sera un vertical separe developpe APRES avoir 10+ clients payants sur AO et atteint la v1.0 stable.

**Pays cibles** : France (v0.1), Belgique (v0.5), Maroc (v1.0)

---

## 2. STACK TECHNIQUE (Verrouille)

| Couche | Technologie | Version |
|--------|-------------|---------|
| Backend | Python | 3.12+ (<3.14) |
| Framework | FastAPI | latest |
| ORM | SQLAlchemy | 2.0 async |
| DB | PostgreSQL + pgvector | 15+ |
| Vector | pgvector HNSW | 768d |
| LLM | Mistral AI API | large-latest |
| Frontend | React + TypeScript | 18+ |
| Build | Vite | latest |
| CSS | Tailwind CSS | 3.x |
| UI | shadcn/ui | latest |
| Auth | JWT + bcrypt | - |
| Container | Docker Compose | - |
| Reverse Proxy | Nginx | - |
| SSL | Let's Encrypt (Certbot) | - |

**5 regles non-negociables (lecons NEXA-MIND)** :
1. Un seul fichier modeles : app/models/ao.py
2. expire_on_commit=False obligatoire
3. Python <3.14
4. Un seul conteneur DB (PostgreSQL+pgvector)
5. Pas de LangChain/CrewAI dans le MVP

---

## 3. ARCHITECTURE (5 couches, validees)

| Couche | Nom | Statut | Version |
|--------|-----|--------|---------|
| 1 | Sensorimotrice (upload, parsing, connectors) | Specifie | v0.1 |
| 2 | Memoire (pgvector, 4 types, oubli selectif) | Specifie | v0.1-v1.1 |
| 3 | Agents (6 agents, swarm registry) | Specifie | v0.1-v0.5 |
| 4 | Deliberation (parlement, gouvernance) | Specifie | v0.3-v1.0 |
| 5 | Metacognition (TAKA LAB) | Specifie | v0.4-v1.0 |

**6 agents definis** : Veilleur, Scorer, Redacteur, Deposant, Auditor, Compliance Officer

---

## 4. MODELE ORGANISATIONNEL (5 roles, valide)

| Role | Niveau | Portee |
|------|--------|--------|
| Editeur (Super Admin) | Systeme | Tous les tenants, metriques globales, billing |
| Admin Soumissionnaire | Tenant | Collaborateurs, regles qualif, scoring, pipeline |
| Collaborateur Soumissionnaire | Tenant limite | AO assignes, upload, qualif, Kanban |
| Admin Acheteur Public | Tenant | Publication AO, candidatures, criteres |
| Collaborateur Acheteur | Tenant limite | CCTP, reponses questions, classement |

**Multi-metiers (Business Lines)** : Modele pour groupes comme Equans/SPIE/Sogetrel avec rationalisation N+1.

---

## 5. SCORING ENGINE V2 (Valide)

- 5 dimensions : Cohherence Metier, Viabilite Financiere, Accessibilite Geographique, Faisabilite Temporelle, Intelligence Concurrentielle
- 3 profils : Prudent, Opportuniste, Specialise
- 33 regles SI/ALORS en YAML
- Plugin architecture (dimensions configurables)
- ScoreCard JSON avec XAI (explicabilite)
- FeedbackLoop (apprentissage)

---

## 6. DOCUMENTS PRODUITS (21 documents, 15 161+ lignes)

### Documents de conception (produits dans cette session) :
1. TAKA_OS_Concept_Validation_Complete.md (2 281 lignes) — 5 roles, flows, onboarding
2. TAKA_OS_Dashboard_Rationalisation.md (1 116 lignes) — Multi-metiers, KPIs, cas Equans/SPIE
3. TAKA_OS_Audit_Complet_Honnete.md (1 412 lignes) — 80+ trous, notes par pilier
4. TAKA_OS_Validation_8_Points_Restants.md (1 209 lignes) — i18n, RGAA, Open Core, Memoire, N Gates, HIL, Forensique

### Documents de specification technique (sessions precedentes) :
5. Bible_TAKA_OS_Maitresse.md (1 469 lignes) — Roadmap v0.1→v2.0
6. blueprint_taka_os_v1.md (14 977 lignes) — Architecture complete
7. Manifeste_Kernel_TAKA_OS_v1.md (3 676 lignes) — Kernel, EventBus, Registry
8. Manifeste_Vertical_AO_TAKA_OS_v1.md (995 lignes) — 6 agents
9. Specs_Scoring_Engine_V2.md (4 472 lignes) — 5 dimensions, 33 regles

### Documents de support :
10-21. 12 documents supplementaires (Holo-1, Hermes, Ecosysteme, gRPC, Innovation, etc.)

### Fichiers de configuration YAML (produits) :
- config/event_mesh_v1.yaml
- config/swarm_registry_v1.yaml
- config/vertical_ao_v1.yaml
- config/scoring_dimensions/*.yaml (5 dimensions)
- config/features.yaml
- config/i18n.yaml
- config/autonomy.yaml

---

## 7. ROADMAP VALIDEE (v0.1 → v2.0)

| Version | Date | Contenu |
|---------|------|---------|
| v0.1 | Mai 2026 | MVP : Kernel asyncio, 3 agents, parsing PDF, scoring basique, Kanban |
| v0.2 | Juin 2026 | + Veille BOAMP/TED, memoire episodique, 5 agents |
| v0.3 | Juillet 2026 | + Auditor, deliberation, feedback loop, TAKA LAB basic |
| v0.4 | Aout 2026 | + Scoring V2, Redacteur template, scoring YAML configurable |
| v0.5 | Sept 2026 | + Swarm Registry, Business Lines, Lifecycle Manager, 6 agents |
| v1.0 | Oct-Nov 2026 | + NATS Event Mesh, SSO/LDAP, API publique, Compliance Officer |
| v1.1 | Nov-Dec 2026 | + Neo4j semantique, Memory Mesh 3 zones, i18n complet |
| v1.2 | Dec 2026-Jan 2027 | + TAKA Vision (Holo-1), Deposant automatique |
| v1.3-2.0 | 2027 | Marketplace, plugins, multi-vertical |

---

## 8. POINTS CRITIQUES A BOUCHER AVANT SPRINT 0

| # | Trou | Effort | Impact |
|---|------|--------|--------|
| 1 | Sentry + Error Boundaries | 0.5-1j | Visibility erreurs |
| 2 | Backup PostgreSQL auto | 1j | Protection donnees |
| 3 | Rate limiting + Circuit breaker | 2-3j | Protection abuse |
| 4 | Tests E2E Playwright | 3-4j | Qualite releases |
| 5 | MFA / TOTP | 2-3j | Credibilite SaaS |

---

## 9. DECISIONS EN ATTENTE (A valider par CEO)

- [ ] Formule Free : limiter a 10 AO et 1 user ? Ou plus genereux ?
- [ ] Priorite Belgique vs Maroc (v0.5 vs v1.0)
- [ ] Partenaire bancaire pour cautionnement (Bpifrance ? LCL ?)
- [ ] Strategie deploiement VPS (premiers clients) vs Cloud (scale)

---

## 10. PROCHAINES ETAPES

1. Mettre a jour les Prompts Sprint 0-3 avec toutes les specs validees
2. Creer le repo GitHub (structure, README, CI/CD)
3. Lancer Kimi Code — Sprint 0 (Foundation)
4. Deployer v0.1 sur VPS
5. Recruter 3 beta-testeurs (PME soumissionnaires)

---

## 11. CONTACTS ET RESSOURCES

- Stack : FastAPI, SQLAlchemy 2.0 async, PostgreSQL 15+pgvector, Mistral AI, React 18+TS
- LLM : Mistral AI (France, Apache 2.0) — PAS Kimi API (Chine/GDPR)
- Ecosysteme : Chift (compta FR), Pennylane, Yousign, HubSpot, Pipedrive
- VLA : Holo-1 7B (Apache 2.0) — v1.2 uniquement
- Licence : MIT (open source)

---

MEMO PRODUIT LE : 2026-05-05
STATUT : CONCEPTION COMPLETE — PRET POUR DEVELOPPEMENT
PROCHAIN JALON : Mise a jour Prompts Sprint 0 → Lancement Kimi Code
