# REASONING — Dimensionnement équipe agentique TAKA OS
## Phase 0 : Analyse stratégique pré-génération

---

## 1. Décomposition des chantiers TAKA OS

### Chantiers Produit & Technique (core)

| # | Chantier | Description | Complexité | Phase |
|---|----------|-------------|------------|-------|
| C1 | **Kernel TAKA OS** | EventBus, Config, Sécurité, RBAC, Audit, Multi-tenancy | Élevée | P1 |
| C2 | **Base de données** | PostgreSQL + pgvector, migrations, seed, backup | Moyenne | P1 |
| C3 | **API REST** | 28+ endpoints, FastAPI, validation, documentation | Élevée | P1 |
| C4 | **Auth & Sécurité** | JWT, RBAC, audit trail, rate limiting, hash chain | Élevée | P1 |
| C5 | **Agent Sourcer** | Upload, parsing PDF/UBL/XML, détection format | Élevée | P1 |
| C6 | **Agent Qualifieur** | Scoring 80% règles / 20% LLM, algorithmie GO/NO-GO | Très élevée | P1 |
| C7 | **Agent Tracker** | Alertes deadlines, APScheduler, notifications multi-canaux | Moyenne | P1 |
| C8 | **Mémoire pgvector** | Embeddings, index HNSW, recherche similarité, capitalisation | Élevée | P1 |
| C9 | **Pipeline Kanban** | 8 stages, drag-drop, API changement d'état | Moyenne | P1 |
| C10 | **Frontend React** | 9 pages, composants UI, state management, responsive | Élevée | P1 |
| C11 | **Intégration Mistral AI** | httpx + Jinja2, circuit breaker, retry, templates | Élevée | P1 |
| C12 | **DevOps & Infra** | Docker Compose, Nginx, SSL, CI/CD, monitoring, backup | Élevée | P1 |

### Chantiers Produit (post-MVP)

| # | Chantier | Description | Phase |
|---|----------|-------------|-------|
| C13 | **Délibération parlementaire** | Toggle, 3 agents votent, timeout 30s | P2 |
| C14 | **TAKA LAB auto-ajustement** | Apprentissage passif scoring, logs de performance | P2 |
| C15 | **Agent Writer (Copilote)** | RAG mémoires procéduraux, suggestions rédaction | P2 |
| C16 | **Connecteurs places de marché** | BOAMP, e-marchespublics, TED, Mercell | P2 |
| C17 | **Génération documents** | Templates DC1/DC2, pré-remplissage, validation humaine | P2 |
| C18 | **API publique** | Webhooks, API tierce, intégrations | P2 |
| C19 | **Mobile (PWA)** | Responsive avancé, offline, notifications push | P2 |
| C20 | **Analytics & Reporting** | Dashboards KPI, exports, ROI | P2 |

### Chantiers Business (GTM)

| # | Chantier | Description | Phase |
|---|----------|-------------|-------|
| C21 | **Go-to-Market France** | Prospection PME BTP, démos, POC, closing | P1-P2 |
| C22 | **Go-to-Market Belgique** | Extension marché belge, partenariats | P3 |
| C23 | **Go-to-Market Maroc** | Adaptation légale, prospection, partenariats locaux | P3 |
| C24 | **Marketing & Content** | Blog, SEO, cas d'usage, témoignages, communauté OSS | P1-P4 |
| C25 | **Pricing & Packaging** | Plans tarifaires, upsell, churn management | P2 |
| C26 | **Support client** | Tickets, FAQ, onboarding, formation | P2 |

### Chantiers Juridique & Conformité

| # | Chantier | Description | Phase |
|---|----------|-------------|-------|
| C27 | **Conformité AI Act EU** | Badge IA, transparence, documentation technique | P1 |
| C28 | **RGPD / Loi 09-08 Maroc** | DPO, droit à l'oubli, portabilité, minimisation | P1 |
| C29 | **Conformité marchés publics** | Validation humaine, non-responsabilité, audit trail | P1 |
| C30 | **Licence & IP** | MIT, CLA, contributions externes, marque | P1 |

### Chantiers Finance & Ops

| # | Chantier | Description | Phase |
|---|----------|-------------|-------|
| C31 | **Modèle économique** | CAC, LTV, churn, MRR, unit economics | P1 |
| C32 | **Fundraising** | Pitch deck, due diligence, relations investisseurs | P3 |
| C33 | **Opérations SaaS** | Onboarding, provisioning, billing, facturation | P2 |
| C34 | **Sécurité ops** | Pentests, SOC, patch management, incident response | P2 |

---

## 2. Effectif minimal ET suffisant par chantier

### Principes de dimensionnement
- **1 agent = 1 responsabilité claire et non-redondante**
- **Poste creux** : on n'en crée pas. Chaque agent a un livrable hebdomadaire mesurable.
- **Poste manquant** : on n'en laisse pas. Chaque chantier a un owner.
- **Surcharge acceptable** : un agent senior peut porter 2-3 chantiers mineurs.
- **Pairing naturel** : certains agents collaborent systématiquement (ex: Frontend + Backend API).

### Dimensionnement par pôle

#### PÔLE DIRECTION (3 agents)
| Agent | Chantiers | Justification |
|-------|-----------|---------------|
| CEO (l'utilisateur humain) | Tous | Vision, fundraising, relations clients stratégiques |
| CTO (Kimi orchestrateur) | Tous tech | Architecture, revue de code, direction technique |
| COO | C31, C33, C34 | Opérations SaaS, scaling, process |

→ **2 agents IA** (CEO est humain, CTO est l'orchestrateur = moi)

#### PÔLE PRODUIT (3 agents)
| Agent | Chantiers | Justification |
|-------|-----------|---------------|
| CPO (Chief Product Officer) | C1-C20, C21-C26 | Vision produit, roadmap, priorisation |
| Product Manager — AO Vertical | C5-C9, C13-C17 | Spécification fonctionnelle, UX métier |
| UX/UI Designer | C10, C19 | Design system, maquettes, composants |

→ **3 agents IA**

#### PÔLE ENGINEERING — BACKEND (5 agents)
| Agent | Chantiers | Justification |
|-------|-----------|---------------|
| Lead Backend Engineer | C1-C4, C11-C12 | Architecture, revue, qualité |
| Backend Engineer — Kernel & Auth | C1, C4 | EventBus, config, RBAC, audit |
| Backend Engineer — Agents & IA | C5-C8, C13-C15 | Agents Sourcer/Qualifieur/Tracker, mémoire |
| Backend Engineer — API & Data | C2, C3, C9 | Endpoints, SQL, pgvector, pipeline |
| DevOps & Infra Engineer | C12 | Docker, Nginx, CI/CD, monitoring, backup |

→ **5 agents IA** (le Lead peut être l'CTO en phase 1)

#### PÔLE ENGINEERING — FRONTEND (2 agents)
| Agent | Chantiers | Justification |
|-------|-----------|---------------|
| Lead Frontend Engineer | C10, C19 | Architecture React, state management, review |
| Frontend Engineer — UI/UX | C10, C19 | Composants, pages, responsive, animations |

→ **2 agents IA**

#### PÔLE IA & ML (4 agents)
| Agent | Chantiers | Justification |
|-------|-----------|---------------|
| Lead IA Engineer | C6, C8, C11, C13-C15 | Architecture IA, choix des modèles, gouvernance |
| IA Engineer — NLP & Parsing | C5, C11 | Parsing PDF, extraction entités, templates LLM |
| IA Engineer — Scoring & Qualification | C6, C14 | Algorithmie scoring, TAKA LAB, feedback loop |
| IA Engineer — Embeddings & RAG | C8, C15, C16 | pgvector, embeddings, recherche similarité |

→ **4 agents IA**

#### PÔLE GTM — FRANCE (3 agents)
| Agent | Chantiers | Justification |
|-------|-----------|---------------|
| Head of Sales France | C21 | Stratégie commerciale France, closing |
| Sales Development Rep France | C21 | Prospection, démos, qualification leads |
| Customer Success Manager France | C26, C33 | Onboarding, support, churn prevention |

→ **3 agents IA** (P2-P3)

#### PÔLE GTM — MAROC (3 agents)
| Agent | Chantiers | Justification |
|-------|-----------|---------------|
| Country Manager Maroc | C23 | Stratégie locale, partenariats |
| Sales Rep Maroc | C23 | Prospection, démos, closing |
| Customer Success Maroc | C23, C26 | Support local, onboarding |

→ **3 agents IA** (P3)

#### PÔLE MARKETING & CONTENT (2 agents)
| Agent | Chantiers | Justification |
|-------|-----------|---------------|
| Head of Marketing | C24, C25 | Stratégie marketing, brand, pricing |
| Content Creator | C24 | Blog, SEO, cas d'usage, docs, tutoriels |

→ **2 agents IA**

#### PÔLE JURIDIQUE & COMPLIANCE (2 agents)
| Agent | Chantiers | Justification |
|-------|-----------|---------------|
| Legal & Compliance Officer EU | C27-C30 | AI Act, RGPD, marchés publics EU |
| Legal & Compliance Officer MA | C28, C30 | Loi 09-08, droit marocain, adaptation |

→ **2 agents IA**

#### PÔLE FINANCE & ADMIN (2 agents)
| Agent | Chantiers | Justification |
|-------|-----------|---------------|
| CFO / Finance Manager | C31, C32 | Comptabilité, fundraising, unit economics |
| Office Manager / RH | — | Recrutement, admin, bien-être équipe |

→ **2 agents IA** (P3)

#### PÔLE SÉCURITÉ (2 agents)
| Agent | Chantiers | Justification |
|-------|-----------|---------------|
| Security Officer | C4, C12, C34 | Pentest, audit sécu, patch management |
| DPO (Data Protection Officer) | C27, C28 | RGPD, Loi 09-08, droit à l'oubli |

→ **2 agents IA**

---

## 3. Synthèse effectif

### Par pôle

| # | Pôle | Agents | Phase d'activation |
|---|------|--------|-------------------|
| 1 | Direction | 2 | P1 |
| 2 | Produit | 3 | P1 (CPO+PM) / P1 (UX) |
| 3 | Engineering Backend | 5 | P1 (3) / P2 (2) |
| 4 | Engineering Frontend | 2 | P1 |
| 5 | IA & ML | 4 | P1 (3) / P2 (1) |
| 6 | GTM France | 3 | P2 |
| 7 | GTM Maroc | 3 | P3 |
| 8 | Marketing & Content | 2 | P2 |
| 9 | Juridique & Compliance | 2 | P1 (1) / P3 (1) |
| 10 | Finance & Admin | 2 | P3 |
| 11 | Sécurité | 2 | P1 (1) / P2 (1) |
| **TOTAL** | | **30 agents IA** | |

### Par criticité

| Criticité | Nombre | Agents |
|-----------|--------|--------|
| **CRITICAL** | 12 | CEO (humain), CTO, CPO, Lead Backend, Backend Kernel/Auth, Backend Agents/IA, Backend API/Data, Lead IA, IA NLP/Parsing, IA Scoring, Lead Frontend, Security Officer |
| **IMPORTANT** | 12 | COO, PM AO Vertical, UX/UI Designer, Backend DevOps, Frontend UI, IA Embeddings/RAG, Head Sales FR, SDR FR, Head Marketing, Legal EU, DPO, CFO |
| **NICE-TO-HAVE** | 3 | CSM FR, Content Creator, Office Manager/RH |
| **OUTSOURCEABLE** | 3 | CSM Maroc, Sales Rep Maroc, Country Manager Maroc (P3) |

### Par phase d'activation

| Phase | Période | Agents activés | Cumul |
|-------|---------|----------------|-------|
| **P1 — MVP** | S1-S4 (1er mois) | 16 | 16 |
| **P2 — V1.1** | S5-S12 (mois 2-3) | +9 | 25 |
| **P3 — Multi-marché** | S13-S24 (mois 4-6) | +4 | 29 |
| **P4 — Scale** | S25+ (mois 7+) | +1 | 30 |

---

## 4. Hiérarchie et reporting lines

```
CEO (humain — toi)
│
├── CTO (Kimi orchestrateur — moi)
│   ├── Pôle Engineering Backend
│   │   ├── Lead Backend Engineer
│   │   │   ├── Backend Engineer — Kernel & Auth
│   │   │   ├── Backend Engineer — Agents & IA
│   │   │   └── Backend Engineer — API & Data
│   │   └── DevOps & Infra Engineer
│   │
│   ├── Pôle Engineering Frontend
│   │   ├── Lead Frontend Engineer
│   │   └── Frontend Engineer — UI/UX
│   │
│   └── Pôle IA & ML
│       ├── Lead IA Engineer
│       │   ├── IA Engineer — NLP & Parsing
│       │   ├── IA Engineer — Scoring & Qualification
│       │   └── IA Engineer — Embeddings & RAG
│       │
├── CPO
│   └── Product Manager — AO Vertical
│       └── UX/UI Designer (dotted line)
│
├── COO
│   ├── Pôle GTM France (P2)
│   │   ├── Head of Sales France
│   │   │   └── Sales Development Rep France
│   │   └── Customer Success Manager France
│   │
│   ├── Pôle GTM Maroc (P3)
│   │   ├── Country Manager Maroc
│   │   │   └── Sales Rep Maroc
│   │   └── Customer Success Maroc
│   │
│   ├── Pôle Marketing & Content (P2)
│   │   ├── Head of Marketing
│   │   └── Content Creator
│   │
│   ├── Pôle Finance & Admin (P3)
│   │   ├── CFO / Finance Manager
│   │   └── Office Manager / RH
│   │
│   └── Pôle Sécurité (P1-P2)
│       ├── Security Officer
│       └── DPO (dotted line → Legal)
│
└── Pôle Juridique & Compliance
    ├── Legal & Compliance Officer EU
    └── Legal & Compliance Officer MA (P3)
```

---

## 5. Dépendances critiques

### Chaîne de dépendances techniques (P1)
```
Kernel (EventBus + Config + Security)
    → Base de données (PostgreSQL + pgvector)
        → API REST (endpoints)
            → Auth & RBAC (JWT)
                → Agent Sourcer (upload)
                    → Parsing PDF
                        → Agent Qualifieur (scoring)
                            → Pipeline Kanban
                                → Frontend React
                                    → DevOps (Docker + deploy)
```

### Dépendances cross-pôles
- **IA & ML** dépend de **Backend** pour les endpoints et la DB
- **Frontend** dépend de **Backend** pour les API
- **Produit** pilote tous les pôles techniques
- **GTM** dépend de **Produit** pour les démos
- **Legal** impacte **IA** (conformité LLM) et **Backend** (audit trail)
- **Sécurité** impacte tous les pôles techniques

---

## 6. Couverture chantiers — validation

| Chantier | Owner | Pôle | Statut |
|----------|-------|------|--------|
| C1 Kernel | Backend Kernel & Auth | Eng Backend | ✅ |
| C2 Base de données | Backend API & Data | Eng Backend | ✅ |
| C3 API REST | Backend API & Data | Eng Backend | ✅ |
| C4 Auth & Sécurité | Backend Kernel & Auth + Security Officer | Eng Backend + Sec | ✅ |
| C5 Agent Sourcer | Backend Agents & IA + IA NLP | Eng Backend + IA | ✅ |
| C6 Agent Qualifieur | Backend Agents & IA + IA Scoring | Eng Backend + IA | ✅ |
| C7 Agent Tracker | Backend Agents & IA | Eng Backend | ✅ |
| C8 Mémoire pgvector | Backend API & Data + IA Embeddings | Eng Backend + IA | ✅ |
| C9 Pipeline Kanban | Backend API & Data + Frontend | Eng Backend + Frontend | ✅ |
| C10 Frontend React | Lead Frontend + Frontend UI | Eng Frontend | ✅ |
| C11 Intégration Mistral | IA NLP + Backend Agents | IA + Eng Backend | ✅ |
| C12 DevOps & Infra | DevOps & Infra Engineer | Eng Backend | ✅ |
| C13 Délibération | IA Scoring + Backend Agents | IA + Eng Backend | ✅ |
| C14 TAKA LAB | IA Scoring | IA | ✅ |
| C15 Agent Writer | IA Embeddings + Backend Agents | IA + Eng Backend | ✅ |
| C16 Connecteurs PM | IA NLP + Backend Agents | IA + Eng Backend | ✅ |
| C17 Génération docs | Backend Agents + IA NLP | Eng Backend + IA | ✅ |
| C18 API publique | Backend API & Data | Eng Backend | ✅ |
| C19 Mobile PWA | Frontend UI | Eng Frontend | ✅ |
| C20 Analytics | Backend API & Data + Frontend | Eng Backend + Frontend | ✅ |
| C21 GTM France | Head Sales FR + SDR FR | GTM FR | ✅ |
| C22 GTM Belgique | Head Sales FR (interim) | GTM FR | ✅ |
| C23 GTM Maroc | Country Manager Maroc | GTM MA | ✅ |
| C24 Marketing | Head Marketing + Content Creator | Marketing | ✅ |
| C25 Pricing | CFO + CPO | Finance + Produit | ✅ |
| C26 Support | CSM FR + CSM MA | GTM FR + GTM MA | ✅ |
| C27 AI Act | Legal EU + DPO | Legal + Sec | ✅ |
| C28 RGPD | DPO + Legal EU | Sec + Legal | ✅ |
| C29 Conformité MP | Legal EU | Legal | ✅ |
| C30 Licence & IP | Legal EU | Legal | ✅ |
| C31 Modèle éco | CFO | Finance | ✅ |
| C32 Fundraising | CEO + CFO | Direction + Finance | ✅ |
| C33 Ops SaaS | COO + CSM FR | Direction + GTM | ✅ |
| C34 Sécurité ops | Security Officer | Sécurité | ✅ |

**34 chantiers couverts. 0 trou. ✅**

---

*Document de raisonnement produit par KIMI-TAKA-SWARM | Mai 2026*
*Justification : 30 agents IA répartis sur 11 pôles, activation progressive sur 4 phases*
