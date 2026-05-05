# TAKA OS — Synthèse Exécutive

## 1. En une phrase

**TAKA OS** est un système d'exploitation agentic open source (licence MIT) verticalisé sur les Appels d'Offres publics pour les PME du BTP, opéré par une équipe de **30 agents IA** répartis sur **11 pôles fonctionnels**, activés progressivement en **4 phases** sur 6 mois.

---

## 2. Chiffres clés

| Indicateur | Valeur |
|---|---|
| **Agents IA** | 30 (2 C-Level direction, 13 tech, 8 business, 4 conformité, 3 finance/ops) |
| **Pôles** | 11 — Direction, Produit, Backend, Frontend, IA/ML, GTM France, GTM Maroc, Marketing, Juridique, Finance, Sécurité |
| **Phases d'activation** | 4 — P1 MVP (4 sem.), P2 V1.1 (2 mois), P3 Multi-marché (3 mois), P4 Scale |
| **Chantiers couverts** | 34 — du kernel technique à la conformité AI Act, en passant par le GTM France/Maroc |
| **Agents P1 (MVP)** | 16 agents actifs dès le jour 1 |
| **Stack technique** | Python 3.12, FastAPI, SQLAlchemy 2.0 async, PostgreSQL+pgvector, Mistral AI, React+Vite+Tailwind |
| **Infrastructure cible** | VPS 6-8€/mois en P1, scaling à 50€/mois en P4 |
| **Licence** | MIT — contribution open source prévue en P4 |

---

## 3. Architecture de l'équipe — Les 3 piliers

### Pilier TECH (13 agents) — Cœur du produit
Dirigé par le **CTO** (agent orchestrateur), ce pilier construit l'OS agentic de zéro :
- **Backend** (5 agents) : Kernel, API REST 28+ endpoints, base de données pgvector, agents métiers (Sourcer, Qualifieur, Tracker), DevOps
- **Frontend** (2 agents) : Interface React 9 pages, composants UI, PWA mobile
- **IA & ML** (4 agents) : Intégration Mistral AI, parsing PDF/UBL/XML, scoring GO/NO-GO (80% règles / 20% LLM), embeddings vectoriels, RAG
- **Produit & UX** (3 agents) : Vision produit, spécifications fonctionnelles AO, design system

### Pilier BUSINESS (8 agents) — Revenus et croissance
Sous la responsabilité du **COO** :
- **GTM France** (3 agents) : Head of Sales, SDR, CSM — cible 100K€ ARR fin P2
- **GTM Maroc** (3 agents) : Country Manager, Sales, CSM — activation P3
- **Marketing** (2 agents) : Stratégie brand/content, SEO, communauté OSS

### Pilier CONFORMITÉ (6 agents) — Risques et gouvernance
- **Juridique** (2 agents) : AI Act EU, RGPD, conformité marchés publics, licence MIT
- **Sécurité** (2 agents) : Pentests, audit sécu, patch management, DPO
- **Finance** (2 agents) : CFO (fundraising, unit economics), Office Manager/RH

### Hiérarchie de reporting
```
CEO (humain — fondateur)
├── CTO (orchestrateur IA)
│   ├── Lead Backend → 4 engineers
│   ├── Lead Frontend → 1 engineer
│   └── Lead IA → 3 engineers
├── CPO → PM AO → UX Designer
├── COO
│   ├── Head Sales FR → SDR + CSM
│   ├── Head Marketing → Content Creator
│   ├── Country Manager MA → Sales + CSM
│   ├── Security Officer + DPO
│   └── CFO + Office Manager (P3)
└── Legal EU + Legal MA (P3)
```

---

## 4. Timeline — Feuille de route 6 mois

| Phase | Période | Agents | Jalons clés |
|---|---|---|---|
| **P1 — MVP** | S1-S4 (mois 1) | 16 | Kernel stable, API REST, 3 agents métiers (Sourcer/Qualifieur/Tracker), mémoire pgvector, frontend React, Docker prod ready |
| **P2 — V1.1 + GTM FR** | S5-S12 (mois 2-3) | 25 (+9) | Délibération parlementaire, TAKA LAB, connecteurs BOAMP/TED, lancement commercial France, marketing actif |
| **P3 — Multi-marché** | S13-S24 (mois 4-6) | 29 (+4) | Déploiement Maroc, CFO en place, fundraising Seed, conformité Loi 09-08 |
| **P4 — Scale** | S25+ (mois 7+) | 30 (+1) | Optimisation coûts, maturité OSS, marque établie |

**Produit livrable dès P1** : une PME du BTP peut uploader un AO, obtenir un scoring GO/NO-GO, et suivre sa candidature dans un pipeline Kanban — le tout en 48h.

---

## 5. Masse salariale et budget

### Enjeu
A maturité (P3-P4), l'équipe complète représente une masse salariale cible de **~1,2M€ annuel** (fourchette 1,05M€ — 1,38M€), répartie France/Maroc.

### Détail par zone

| Zone | Effectif | Fourchette annuelle |
|---|---|---|
| **France** | ~17 agents | 600K€ — 780K€ |
| **Maroc** | ~10 agents | 200K€ — 330K€ |
| **Transversaux** | ~3 agents | 250K€ — 270K€ |
| **TOTAL** | **30 agents** | **~1,05M€ — 1,38M€** |

### Infrastructure et LLM

| Poste | P1 | P2 | P3 | P4 |
|---|---|---|---|---|
| VPS + services | 8€/mois | 15€/mois | 25€/mois | 50€/mois |
| API Mistral AI | ~50€/mois | ~200€/mois | ~500€/mois | ~1000€/mois |
| **Total tech** | **~60€/mois** | **~215€/mois** | **~525€/mois** | **~1050€/mois** |

**Levier** : Le modèle France/Maroc permet de diviser la masse salariale par ~1,4 par rapport à une équipe 100% France, tout en conservant une expertise technique de niveau sénior.

---

## 6. Risques principaux et mitigations

| Risque | Probabilité | Impact | Mitigation par l'équipe |
|---|---|---|---|
| **Délai MVP** (4 semaines ambitieux) | Moyenne | Critique | CTO orchestrateur + 16 agents P1 avec chaîne de dépendances documentée. Scope MVP figé — pas de scope creep. |
| **Qualité scoring IA** (faux positifs/négatifs) | Moyenne | Élevé | Architecture 80% règles / 20% LLM. TAKA LAB (P2) pour l'auto-ajustement. Validation humaine obligatoire (conformité marchés publics). |
| **Conformité AI Act + RGPD** | Élevée | Critique | Legal EU (P1) + DPO (P2) + Security Officer (P1). Badge IA, transparence algorithmique, droit à l'oubli dès le design. |
| **Adoption marché** | Moyenne | Élevé | PM AO Vertical spécialisé marchés publics. GTM France avec SDR + CSM. Time-to-First-Value <48h. |
| **Dépendance Mistral AI** | Faible | Moyen | Architecture LLM-agnostique (httpx + Jinja2). Circuit breaker + retry. Possibilité de bascule vers autre fournisseur. |
| **Fuite de données clients** | Faible | Critique | Chiffrement données sensibles, RBAC granulaire, audit trail complet, pentests réguliers (Security Officer). |
| **Complexité multi-marche** | Moyenne | Moyen | Country Manager Maroc (P3) + Legal MA. Activation progressive — France validée avant expansion. |

---

## 7. Prochaines étapes — 5 actions immédiates

| # | Action | Responsable | Délai | Livrable |
|---|---|---|---|---|
| **1** | **Valider l'architecture technique** — revue kernel, stack, dépendances | CTO (agent_001) | Jour 1-2 | Document `ARCHITECTURE.md` validé |
| **2** | **Lancer le développement P1** — kernel + DB + auth + API core | Lead Backend (agent_006) + équipe | Semaine 1 | 5 premiers endpoints opérationnels |
| **3** | **Finaliser les spécifications AO** — format parsing, règles scoring, pipeline Kanban | CPO (agent_003) + PM AO (agent_004) | Jour 2-3 | Specs fonctionnelles C5-C9 validées |
| **4** | **Mettre en place l'infrastructure DevOps** — repo Git, Docker Compose, CI/CD, VPS | DevOps (agent_010) | Jour 1-3 | Pipeline CI/CD opérationnelle, environnement staging |
| **5** | **Documenter la conformité P1** — AI Act, RGPD, validation humaine, licence MIT | Legal EU (agent_027) + Security Officer (agent_022) | Semaine 1 | Documentation conformité initiale + registre traitements |

---

## Synthèse décisionnelle

**TAKA OS dispose d'une équipe agentique complète (30 agents, 11 pôles) couvrant 34 chantiers techniques, business et réglementaires. L'activation progressive en 4 phases limite le risque : 16 agents seulement en P1 pour un MVP en 4 semaines. La masse salariale cible (~1,2M€) est maîtrisée grâce au modèle France/Maroc. Zéro trou de couverture — chaque chantier a un owner, chaque risque une mitigation.**

*Document produit par KIMI-TAKA-SWARM | Mai 2026*
