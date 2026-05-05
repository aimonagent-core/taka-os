# TAKA OS - Plan de Phasing & Calendrier d'Activation

> **Document**: PHASING.md
> **Projet**: TAKA OS - Operating System Agentic pour Appels d'Offres (Open Source MIT)
> **Date**: Juin 2025
> **Version**: 1.0
> **Effectif total**: 30 agents / 11 pôles / 4 phases d'activation
> **Déploiement**: France ( siège ) + Maroc ( hub offshore )

---

## Sommaire

1. [Vue d'ensemble des phases](#1-vue-densemble-des-phases)
2. [Phase 1 — MVP (Mois 1, S1-S4)](#2-phase-1--mvp)
3. [Phase 2 — V1.1 + GTM FR (Mois 2-3, S5-S12)](#3-phase-2--v11--gtm-fr)
4. [Phase 3 — Multi-marché (Mois 4-6, S13-S24)](#4-phase-3--multi-marché)
5. [Phase 4 — Scale (Mois 7+, S25+)](#5-phase-4--scale)
6. [Diagramme de Gantt (ASCII)](#6-diagramme-de-gantt)
7. [Points de décision GO/NO-GO](#7-points-de-décision-gono-go)
8. [Risques par phase et mitigations](#8-risques-et-mitigations)
9. [Matrice de dépendances](#9-matrice-de-dépendances)
10. [Indicateurs de succès par phase](#10-indicateurs-de-succès)

---

## 1. Vue d'ensemble des phases

| Phase | Période | Semaines | Effectif | Agents actifs | Focus |
|-------|---------|----------|----------|--------------|-------|
| **P1** | Mois 1 | S1-S4 | 16 | 16 nouveaux | MVP Technique — Kernel + Agents IA |
| **P2** | Mois 2-3 | S5-S12 | 23 | +7 nouveaux | V1.1 Feature + GTM France |
| **P3** | Mois 4-6 | S13-S24 | 30 | +7 nouveaux | Multi-marché FR + MA |
| **P4** | Mois 7+ | S25+ | 30 | 0 nouveau | Scale & Optimisation |

```
Timeline globale (échelle : 1 caractère = 1 semaine)

    S1 S2 S3 S4   S5 S6 S7 S8   S9 S10 S11 S12  S13 S14 S15 S16  S17 S18 S19 S20  S21 S22 S23 S24  S25→
P1  [████████]    .    .    .     .     .    .      .     .     .      .     .     .      .     .     .
P2  .............[████████████████].....................................
P3  ........................................[████████████████████████]
P4  .............................................................................................[→

    M1            M2            M3              M4              M5              M6              M7→

P1: MVP Tech (16 agents)    ████
P2: V1.1 + GTM FR (23A)     ....    ████████████████████████████████
P3: Multi-marché (30A)      ................................    ████████████████████████████████
P4: Scale (30A)             ..................................................................    ████→
```

---

## 2. Phase 1 — MVP (Mois 1, Semaines 1-4)

### Objectif stratégique
Livrer un MVP fonctionnel du kernel TAKA OS capable de parser, analyser et scorer un Appel d'Offres avec l'assistance de 5 agents IA spécialisés.

### Agents activés (16)

| Pôle | Agent | Rôle | Mission P1 |
|------|-------|------|-----------|
| **Direction** | agent_001 (CTO) | Direction Technique | Architecture, stack, recrutement tech |
| **Direction** | agent_002 (COO) | Direction Opérationnelle | Organisation, processus, planning |
| **Direction** | agent_003 (CPO) | Direction Produit | Vision produit, roadmap, prioritisation |
| **Produit** | agent_004 (PM_AO) | Product Manager AO | Spécifications métiers AO, user stories |
| **Design** | agent_005 (UX) | UX Designer | Parcours utilisateur, wireframes MVP |
| **Backend** | agent_006 (Lead BE) | Lead Backend | Architecture kernel, review code |
| **Backend** | agent_007 (BE Kernel) | Backend Kernel | Moteur de parsing, orchestration agents |
| **Backend** | agent_008 (BE Agents) | Backend Agents | Framework d'agents, communication inter-agents |
| **Backend** | agent_009 (BE API) | Backend API | API REST, endpoints core |
| **DevOps** | agent_010 (DevOps) | DevOps/Infra | CI/CD, infra cloud, monitoring |
| **Frontend** | agent_011 (Lead FE) | Lead Frontend | Architecture UI, composants core |
| **Frontend** | agent_012 (FE UI) | Développeur UI | Interface utilisateur MVP |
| **IA** | agent_013 (Lead IA) | Lead IA | Architecture IA, choix des modèles |
| **IA** | agent_014 (IA NLP) | IA NLP | Parsing NLP, extraction entités AO |
| **IA** | agent_015 (IA Scoring) | IA Scoring | Algorithme de scoring, matrice décision |
| **IA** | agent_016 (IA Embeddings) | IA Embeddings | Vectorisation, similarité, RAG |

### Livrables clés P1

| Semaine | Livrable | Responsable | Critère d'acceptation |
|---------|----------|-------------|----------------------|
| S1 | Architecture Technique V1 | CTO + Lead BE + Lead IA | Document validé, stack figée |
| S1 | Wireframes MVP | UX + CPO | Maquettes cliquables Figma |
| S2 | Kernel Parser (MVP) | BE Kernel + IA NLP | Parse un AO PDF → JSON structuré (>80% précision) |
| S2 | Infra cloud déployée | DevOps | Environnements DEV/STAGING/PROD opérationnels |
| S3 | Framework agents V1 | BE Agents + Lead IA | 5 agents communicants, bus d'événements fonctionnel |
| S3 | API Core V1 | BE API | Endpoints auth, parsing, scoring documentés (Swagger) |
| S4 | Scoring Engine V1 | IA Scoring + IA Embeddings | Scoring de conformité et pertinence opérationnel |
| S4 | UI Dashboard V1 | Lead FE + FE UI | Dashboard React consultable, intégration API |
| S4 | **Release MVP 0.1** | CTO + CPO | Démo end-to-end : upload AO → analyse → scoring |

### Jalons P1

```
P1 — S1 → S4 (Mois 1)

S1      S2      S3      S4
|-------|-------|-------|
[Archi] [Parse] [Agnts] [Score]
[UX   ] [Infra] [API  ] [UI   ]
        [     Kernel     ]
                [  Agents  ]
                        [Scoring]
[=================================== MVP 0.1 ======================>]

GO/NO-GO P1→P2 ................................. ▶
```

### Dépendances critiques P1

- DevOps (S1) → Backend (S2) : L'infra doit être prête avant le développement
- BE Kernel (S2) → IA NLP (S2) : Le parser nécessite les modèles NLP
- BE Agents (S3) → Scoring (S4) : Le framework d'agents doit être stable
- API (S3) → UI (S4) : Le frontend consomme l'API

---

## 3. Phase 2 — V1.1 + GTM FR (Mois 2-3, Semaines 5-12)

### Objectif stratégique
Stabiliser le produit (V1.1), lancer la GTM France, et mettre en place la sécurité / conformité RGPD.

### Agents P1 maintenus (16)
Tous les agents de P1 restent actifs.

### Nouveaux agents activés (+7)

| Pôle | Agent | Rôle | Date d'activation | Mission P2 |
|------|-------|------|------------------|-----------|
| **Sales FR** | agent_017 (HEAD_SALES_FR) | Head of Sales France | S5 | Stratégie commerciale, pipeline, équipe SDR |
| **Sales FR** | agent_018 (SDR_FR) | SDR France | S5 | Prospection, qualification leads, démos |
| **Customer Success** | agent_019 (CSM_FR) | CSM France | S6 | Onboarding, support, rétention clients pilotes |
| **Marketing** | agent_020 (HEAD_MARKETING) | Head of Marketing | S5 | Stratégie marketing, positionnement, brand |
| **Marketing** | agent_021 (CONTENT_CREATOR) | Content Creator | S6 | Contenu SEO, blog, cas d'usage, réseaux sociaux |
| **Sécurité** | agent_022 (SEC_OFFICER) | Security Officer | S5 | Audit sécurité, hardening, pentests |
| **Conformité** | agent_023 (DPO) | DPO / RGPD | S5 | Conformité RGPD, registre des traitements |

### Livrables clés P2

| Semaine | Livrable | Responsable | Critère d'acceptation |
|---------|----------|-------------|----------------------|
| S5 | Stratégie GTM France | Head Sales + Head Marketing | Plan commercial, ICP défini, cibles 10K MME |
| S5 | Audit sécurité V1 | Security Officer | Rapport d'audit, plan de remédiation |
| S5 | Conformité RGPD V1 | DPO | Registre des traitements, DPA prêt |
| S6 | V1.0 Release | CTO + CPO | Version stable, tests e2e passants |
| S6 | Site vitrine + Blog | Head Marketing + Content | Site public, 3 articles publiés |
| S7 | Pipeline commercial actif | Head Sales + SDR | CRM configuré, 50 leads qualifiés/semaine |
| S7 | Customer Success process | CSM | Playbook onboarding, FAQ, support desk |
| S8 | V1.1 Feature Release | CPO + Lead BE + Lead IA | Multi-AO simultanés, templates réponses, exports |
| S9-10 | 5 pilotes clients | Head Sales + CSM | 5 entreprises actives, feedback collecté |
| S11 | Intégrations tierces V1 | Lead BE | Connecteurs BOAMP + 2 portails régionaux |
| S12 | **Release V1.1 + Bilan GTM Q1** | COO + CTO + CPO | 100 MAU, 5 pilotes actifs, NPS > 30 |

### Jalons P2

```
P2 — S5 → S12 (Mois 2-3)

S5    S6    S7    S8    S9    S10   S11   S12
|-----|-----|-----|-----|-----|-----|-----|
[GTM  ][V1.0][Pipe ][V1.1][Pilots     ][Integ][Q1   ]
[Sec  ][Site ][CS   ][     ][     5    ][     ][Bilan]
[ GDPR ][Blog ][     ][     ][     entreprises    ]

+ agent_017 HEAD_SALES (S5)
+ agent_018 SDR_FR (S5)
+ agent_020 HEAD_MARKETING (S5)
+ agent_022 SEC_OFFICER (S5)
+ agent_023 DPO (S5)
+ agent_019 CSM_FR (S6)
+ agent_021 CONTENT_CREATOR (S6)

GO/NO-GO P2→P3 .................................................... ▶
```

### Dépendances critiques P2

- MVP (P1) → V1.0 (S6) : La stabilité du MVP conditionne la V1.0
- Head Sales (S5) → Pipeline (S7) : Le commercial doit structurer avant l'action SDR
- Security Officer (S5) → V1.1 (S8) : Les vulnérabilités critiques doivent être corrigées
- Pilotes (S9) → P3 : Le feedback des pilotes valide (ou non) l'expansion multi-marché

---

## 4. Phase 3 — Multi-marché (Mois 4-6, Semaines 13-24)

### Objectif stratégique
Ouvrir le hub Maroc, internationaliser le produit, renforcer la conformité juridique et financière, et convertir les pilotes en clients payants.

### Agents P1+P2 maintenus (23)
Tous les agents des phases précédentes restent actifs.

### Nouveaux agents activés (+7)

| Pôle | Agent | Rôle | Date d'activation | Mission P3 |
|------|-------|------|------------------|-----------|
| **Maroc** | agent_024 (COUNTRY_MA) | Country Manager Maroc | S13 | Lancement hub MA, recrutement local, partenariats |
| **Maroc** | agent_025 (SALES_MA) | Sales Maroc | S14 | Prospection marché marocain, francophone Afrique |
| **Maroc** | agent_026 (CSM_MA) | CSM Maroc | S15 | Support client zone MA, onboarding clients locaux |
| **Legal** | agent_027 (LEGAL_EU) | Legal Counsel EU | S13 | Conformité européenne, CGV, contrats clients |
| **Maroc** | agent_028 (LEGAL_MA) | Legal Counsel Maroc | S13 | Conformité locale, droit marocain des marchés publics |
| **Finance** | agent_029 (CFO) | CFO | S13 | Contrôle de gestion, prévisions, relations investisseurs |
| **Opérations** | agent_030 (OFFICE_MGR) | Office Manager | S14 | Administration, RH, fournisseurs, bureaux |

### Livrables clés P3

| Semaine | Livrable | Responsable | Critère d'acceptation |
|---------|----------|-------------|----------------------|
| S13 | Hub Maroc opérationnel | Country Manager + CTO | Bureau MA, équipements, accès sécurisé aux systèmes |
| S13 | Stack juridique EU + MA | LEGAL_EU + LEGAL_MA | CGV, contrats, conformité marchés publics FR + MA |
| S13 | Tableaux de bord financiers | CFO | Budget, burn-rate, prévisions mensuelles |
| S14 | V2.0 Multi-marché | CPO + Lead BE + Lead IA | Support AO français + marocain, localisation AR/FR |
| S14 | Lancement commercial MA | Country Manager + Sales MA | 10 rendez-vous qualifiés/semaine zone MA |
| S15-16 | Conversion pilotes → clients | Head Sales FR + CSM FR | 3/5 pilotes convertis en contrats payants |
| S17-18 | Expansion features | Lead IA + Lead BE | Agent rédaction, agent conformité réglementaire |
| S19-20 | Partenariats intégration | Head Sales + Country Manager | 2 partenaires technologiques signés |
| S21-22 | Campagne marketing MA | Head Marketing + Country Manager | Landing page MA, contenu local, SEO marocain |
| S23-24 | **Release V2.0 + Bilan S1** | COO + CFO + CTO | 20 clients payants, 100k EUR ARR, unité éco MA viable |

### Jalons P3

```
P3 — S13 → S24 (Mois 4-6)

S13   S14   S15   S16   S17   S18   S19   S20   S21   S22   S23   S24
|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
[Hub  ][V2.0 ][Conv  ][     ][Expand][     ][Part  ][     ][Camp  ][Q2   ]
[Legal][     ][pilot→][     ][featur][     ][ner   ][     ][MA    ][Bilan]
[CFO  ][MA   ][client][     ][      ][     ][      ][     ][      ][     ]

+ agent_024 COUNTRY_MA (S13)
+ agent_027 LEGAL_EU (S13)
+ agent_028 LEGAL_MA (S13)
+ agent_029 CFO (S13)
+ agent_025 SALES_MA (S14)
+ agent_030 OFFICE_MGR (S14)
+ agent_026 CSM_MA (S15)

GO/NO-GO P3→P4 .................................................... ▶
```

### Dépendances critiques P3

- GTM FR (P2) → Hub MA (S13) : La traction France valide l'expansion
- LEGAL_EU + LEGAL_MA (S13) → V2.0 (S14) : La conformité juridique conditionne le multi-marché
- Pilotes convertis → Expansion features : Les revenus financent le développement
- Country Manager (S13) → Sales MA (S14) : Le CM doit structurer avant l'activation commerciale

---

## 5. Phase 4 — Scale (Mois 7+, Semaines 25+)

### Objectif stratégique
Accélérer la croissance, optimiser l'unité économique, et renforcer l'avantage compétitif par l'automatisation et l'IA générative.

### Effectif stable (30)
Aucun nouveau recrutement en P4. L'équipe de 30 agents est optimisée et réorganisée selon les besoins.

### Missions par pôle

| Pôle | Mission P4 | Objectifs |
|------|-----------|-----------|
| **Direction** (4 agents) | Stratégie Série A, board, vision produit | Levée de fonds ou rentabilité |
| **Produit & Design** (2 agents) | Roadmap V3.0, UX avancée, analytics | NPS > 50, churn < 5%/mois |
| **Backend** (4 agents) | Scalabilité, microservices, API publique | 10x capacité de traitement |
| **DevOps** (1 agent) | SRE, observabilité, cost optimization | 99,9% uptime, -30% coûts infra |
| **Frontend** (2 agents) | V3.0 UI, design system, mobile | Temps de chargement < 2s |
| **IA** (4 agents) | Fine-tuning modèles propriétaires, agent rédaction V2 | Précision scoring > 95% |
| **Sales FR** (3 agents) | Scale commerciale, enterprise, partenariats | 500k EUR ARR France |
| **Marketing** (2 agents) | Inbound marketing, communauté open source | 10 000 MAU, 500 stars GitHub |
| **Sécurité & Conformité** (3 agents) | SOC2, certification, conformité EU/MA | SOC2 Type I, conformité totale |
| **Maroc** (4 agents) | Croissance zone MA, expansion Afrique francophone | 200k EUR ARR zone MA |
| **Opérations** (1 agent) | RH, culture d'entreprise, processus | E-NPS > 40 |

### Livrables clés P4

| Trimestre | Livrable | Responsable | Critère d'acceptation |
|-----------|----------|-------------|----------------------|
| T3 (M7-9) | V3.0 avec agent rédaction V2 | Lead IA + CPO | Génération de réponses AO complètes, score qualité > 80% |
| T3 | API Publique + Marketplace | Lead BE + CTO | Store d'agents, API tierce documentée |
| T3 | SOC2 Type I | Security Officer + DPO | Audit externe réussi |
| T4 (M10-12) | Série A ou rentabilité | CEO/CFO | 1M EUR ARR ou cash-flow positif |
| T4 | Expansion Afrique francophone | Country Manager | 3 pays actifs (MA, SN, CI) |
| T4 | Communauté OSS 1000+ membres | Head Marketing | GitHub 1000 stars, Discord 500 membres |

---

## 6. Diagramme de Gantt

### Vue complète (échelle : █ = 1 semaine)

```
TAKA OS — Diagramme de Gantt Complet
═══════════════════════════════════════════════════════════════════════════════════════════

AGENTS & PÔLES                         S1  S2  S3  S4  S5  S6  S7  S8  S9  S10 S11 S12 S13 S14 S15 S16 S17 S18 S19 S20 S21 S22 S23 S24 S25→
────────────────────────────────────── ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PÔLE DIRECTION (4)
  agent_001 CTO                        [████████████████████████████████████████████████████████████████████████████████████████████→
  agent_002 COO                        [████████████████████████████████████████████████████████████████████████████████████████████→
  agent_003 CPO                        [████████████████████████████████████████████████████████████████████████████████████████████→
  agent_029 CFO                        ·············································[████████████████████████████████████████████████→

PÔLE PRODUIT & DESIGN (2)
  agent_004 PM_AO                      [████████████████████████████████████████████████████████████████████████████████████████████→
  agent_005 UX_DESIGNER                [████████████████████████████████████████████████████████████████████████████████████████████→

PÔLE BACKEND (4)
  agent_006 LEAD_BACKEND               [████████████████████████████████████████████████████████████████████████████████████████████→
  agent_007 BE_KERNEL                  [████████████████████████████████████████████████████████████████████████████████████████████→
  agent_008 BE_AGENTS                  [████████████████████████████████████████████████████████████████████████████████████████████→
  agent_009 BE_API                     [████████████████████████████████████████████████████████████████████████████████████████████→

PÔLE DEVOPS (1)
  agent_010 DEVOPS                     [████████████████████████████████████████████████████████████████████████████████████████████→

PÔLE FRONTEND (2)
  agent_011 LEAD_FRONTEND              [████████████████████████████████████████████████████████████████████████████████████████████→
  agent_012 FE_UI                      [████████████████████████████████████████████████████████████████████████████████████████████→

PÔLE IA (4)
  agent_013 LEAD_IA                    [████████████████████████████████████████████████████████████████████████████████████████████→
  agent_014 IA_NLP                     [████████████████████████████████████████████████████████████████████████████████████████████→
  agent_015 IA_SCORING                 [████████████████████████████████████████████████████████████████████████████████████████████→
  agent_016 IA_EMBEDDINGS              [████████████████████████████████████████████████████████████████████████████████████████████→

PÔLE VENTES FRANCE (3)
  agent_017 HEAD_SALES_FR              ················[████████████████████████████████████████████████████████████████████████████████→
  agent_018 SDR_FR                     ················[████████████████████████████████████████████████████████████████████████████████→
  agent_019 CSM_FR                     ·················[███████████████████████████████████████████████████████████████████████████████→

PÔLE MARKETING (2)
  agent_020 HEAD_MARKETING             ················[████████████████████████████████████████████████████████████████████████████████→
  agent_021 CONTENT_CREATOR            ·················[███████████████████████████████████████████████████████████████████████████████→

PÔLE SÉCURITÉ & CONFORMITÉ (3)
  agent_022 SEC_OFFICER                ················[████████████████████████████████████████████████████████████████████████████████→
  agent_023 DPO                        ················[████████████████████████████████████████████████████████████████████████████████→
  agent_027 LEGAL_EU                   ·················································[████████████████████████████████████████████████→

PÔLE MAROC (4)
  agent_024 COUNTRY_MA                 ·················································[████████████████████████████████████████████████→
  agent_025 SALES_MA                   ··················································[███████████████████████████████████████████████→
  agent_026 CSM_MA                     ···················································[██████████████████████████████████████████████→
  agent_028 LEGAL_MA                   ·················································[████████████████████████████████████████████████→

PÔLE OPÉRATIONS (1)
  agent_030 OFFICE_MGR                 ··················································[███████████████████████████████████████████████→

────────────────────────────────────── ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASES                                 M1              M2              M3              M4              M5              M6              M7→
  P1 MVP (16 agents)                   [████]
  P2 V1.1 + GTM FR (23 agents)         ····[████████████████████████████████]
  P3 Multi-marché (30 agents)          ····································[████████████████████████████████]
  P4 Scale (30 agents)                 ······································································[═══════════════════════════→

GO/NO-GO                               ▲               ▲                               ▲
  Checkpoint P1→P2                     │               │                               │
  Checkpoint P2→P3                     ················│                               │
  Checkpoint P3→P4                     ·················································│
────────────────────────────────────── ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LIVRABLES CLÉS
  MVP 0.1 (Kernel + Agents)                ▲
  V1.0 (Stabilisation)                                     ▲
  V1.1 (Features + GTM)                                          ▲
  V2.0 (Multi-marché)                                                                ▲
  V3.0 (Scale + IA gén.)                                                                                                         ▲
  SOC2 Type I                                                                                                                    ▲
═══════════════════════════════════════════════════════════════════════════════════════════
Légende : [████] Phase active  ···· Période inactive  ▲ Livrable  → Continuation
```

---

## 7. Points de décision GO / NO-GO

### Checkpoint P1 → P2 (Fin S4 / M1)

| Critère | Seuil | Décision |
|---------|-------|----------|
| MVP 0.1 fonctionnel | Démonstration end-to-end réussie | GO si OK, NO-GO si < 80% features |
| Précision parsing NLP | > 80% sur 10 AO de test | GO si > 80%, AJUSTEMENT si 60-80% |
| Architecture stable | Zero critical bug en staging | GO si OK, NO-GO si instable |
| Équipe P1 productive | Velocity conforme au sprint planning | GO si OK, RECRUTEMENT si sous-staffé |

**Décision attendue** : Validation par le CTO et le CPO de la qualité du MVP.

**En cas de NO-GO** :
- Scénario A : Allongement P1 de 2 semaines (S5-S6 dédiées à la stabilisation)
- Scénario B : Réduction du scope P2 (pas de GTM, focus technique uniquement)

---

### Checkpoint P2 → P3 (Fin S12 / M3)

| Critère | Seuil | Décision |
|---------|-------|----------|
| V1.1 stable en production | Uptime > 99%, zero bug critique | GO si OK |
| Pilotes clients actifs | ≥ 3 entreprises en pilote actif | GO si ≥ 3, AJUSTEMENT si 1-2 |
| Pipeline commercial | ≥ 50 leads qualifiés/semaine | GO si OK |
| Conformité RGPD | Audit DPO validé, DPA signé | GO si OK, BLOCAGE si non-conforme |
| Traction produit | MAU > 100, NPS pilotes > 20 | GO si OK, NO-GO si < 50 MAU |

**Décision attendue** : Comité de direction (CTO, COO, CPO) avec validation du Head Sales.

**En cas de NO-GO** :
- Scénario A : Allongement P2 de 4 semaines (focus conversion pilotes)
- Scénario B : Report P3 à M5 (hub Maroc en S17 au lieu de S13)
- Scénario C : Pivôt produit si traction insuffisante

---

### Checkpoint P3 → P4 (Fin S24 / M6)

| Critère | Seuil | Décision |
|---------|-------|----------|
| Clients payants France | ≥ 15 clients payants | GO si ≥ 15, NO-GO si < 10 |
| ARR France | ≥ 100k EUR ARR | GO si OK |
| Hub Maroc opérationnel | Bureau ouvert, 3+ agents productifs | GO si OK, AJUSTEMENT si retard |
| V2.0 multi-marché | Support FR + MA validé | GO si OK |
| Unité économique France | CAC < 3x LTV, churn < 10%/mois | GO si OK, ALERTE si CAC > 5x LTV |
| Santé financière | Runway > 6 mois post-P3 | GO si OK, LEVÉE URGENTE si < 3 mois |

**Décision attendue** : Board complet avec le CFO, décision sur levée Série A vs bootstrap.

**En cas de NO-GO** :
- Scénario A : Mode "lean" — réduction de 4 postes non-critiques, focus rentabilité
- Scénario B : Levée de fonds bridge (500k-1M EUR)
- Scénario C : Recentrage France uniquement, fermeture temporaire hub MA

---

## 8. Risques et mitigations

### Risques par phase

#### Phase 1 — Risques Tech (Niveau : ÉLEVÉ)

| Risque | Probabilité | Impact | Mitigation |
|--------|------------|--------|-----------|
| R1.1 : Complexité technique du kernel sous-estimée | Moyenne (40%) | Critique | POC technique en pré-P1, fallback sur solution hybride (règles + IA) |
| R1.2 : Recrutement Lead IA / Lead BE trop long | Élevée (60%) | Majeur | Pipeline de candidats avant J0, freelance senior en renfort si délai > S2 |
| R1.3 : Performance NLP insuffisante sur AO complexes | Moyenne (35%) | Majeur | Benchmark modèles (GPT-4, Claude, Mistral), fine-tuning si nécessaire |
| R1.4 : Dette technique dès le MVP | Élevée (50%) | Moyen | Sprints de refacto intégrés (20% du temps), revue de code systématique |

#### Phase 2 — Risques GTM & Conformité (Niveau : MOYEN)

| Risque | Probabilité | Impact | Mitigation |
|--------|------------|--------|-----------|
| R2.1 : Adoption des pilotes insuffisante | Moyenne (40%) | Majeur | CSM dédié, programme d'accompagnement, gratuite étendue si nécessaire |
| R2.2 : Conformité RGPD complexe | Moyenne (30%) | Majeur | DPO recruté tôt (S5), cabinet d'audit externe en support |
| R2.3 : Traction commerciale faible | Moyenne (35%) | Majeur | ICP affiné, pivot sur segment mid-market si enterprise trop long |
| R2.4 : Vulnérabilité sécurité critique | Faible (15%) | Critique | Pentest externe S8, bug bounty program, Security Officer dédié |

#### Phase 3 — Risques Expansion (Niveau : MOYEN)

| Risque | Probabilité | Impact | Mitigation |
|--------|------------|--------|-----------|
| R3.1 : Difficulté d'ouverture hub Maroc | Moyenne (35%) | Majeur | Partenariat avec cabinet local, visite terrain CTO en S13 |
| R3.2 : Différences réglementaires MA/FR | Moyenne (40%) | Majeur | Recrutement LEGAL_MA local, audit juridique avant lancement |
| R3.3 : Cash-burn trop élevé avec 30 agents | Élevée (45%) | Critique | Scénario minimal prêt (4 postes reportables), suivi CFO hebdo |
| R3.4 : Conversion pilotes → clients faible | Moyenne (35%) | Majeur | Pricing flexible, offre "founding customer", développement features prioritaires |

#### Phase 4 — Risques Scale (Niveau : FAIBLE)

| Risque | Probabilité | Impact | Mitigation |
|--------|------------|--------|-----------|
| R4.1 : Concurrence accrue | Élevée (55%) | Majeur | Open-source comme avantage, communauté, différenciation vertical AO |
| R4.2 : Rétention talents | Moyenne (35%) | Majeur | BSPCE, remote-friendly, culture tech forte, E-NPS suivi trimestriel |
| R4.3 : Scalabilité technique | Moyenne (30%) | Majeur | Architecture microservices dès V2.0, tests de charge réguliers |
| R4.4 : Dépendance à un seul marché | Faible (20%) | Majeur | Diversification Afrique francophone, expansion EU préparée |

### Heatmap des risques

```
Impact
  Critique ┃                            R1.1 R3.3
           ┃         R1.2 R1.3  R2.1  R2.3        R4.1
   Majeur  ┃  R1.4   R2.2       R3.1  R3.2  R3.4  R4.2  R4.3
           ┃                           R2.4               R4.4
   Moyen   ┃
           ┃
   Faible  ┃
           ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           Faible    Moyenne              Élevée
                              Probabilité
```

---

## 9. Matrice de dépendances

### Dépendances inter-phases

| Phase source | Livrable | Phase cible | Impact si retard |
|-------------|----------|------------|-----------------|
| P1 | MVP 0.1 stable | P2 | Blocage V1.0, décalage GTM entier |
| P1 | Architecture validée | P2-P3-P4 | Refonte coûteuse si changement post-P1 |
| P2 | V1.1 en production | P3 | Blocage V2.0 multi-marché |
| P2 | Pilotes actifs | P3 | Pas de validation marché → P3 risquée |
| P2 | Conformité RGPD | P3 | Blocage légal, impossible de facturer |
| P3 | Hub MA opérationnel | P4 | Recentrage France uniquement |
| P3 | Clients payants | P4 | Pas de Série A, mode bootstrap obligatoire |

### Dépendances intra-phase (P1)

```
DevOps (S1: Infra)
    │
    ▼
BE Kernel (S2: Parser) ◄──── IA NLP (S2: Modèles)
    │
    ▼
BE Agents (S3: Framework) ◄── Lead IA (S3: Architecture)
    │                           │
    ▼                           ▼
BE API (S3: Endpoints) ◄──── IA Scoring (S4: Scoring)
    │                           ▲
    ▼                           │
UI Dashboard (S4: Frontend) ◄─ IA Embeddings (S4: Vectors)
    │
    ▼
[MVP 0.1 Release]
```

---

## 10. Indicateurs de succès par phase

### Objectifs chiffrés

| Phase | KPI | Cible | Mesure |
|-------|-----|-------|--------|
| **P1** | Features MVP livrées | 100% scope MVP | Burndown chart |
| **P1** | Précision parsing NLP | > 80% | Jeu de test 50 AO |
| **P1** | Temps de réponse scoring | < 30s | Monitoring API |
| **P2** | Utilisateurs actifs mensuels (MAU) | > 100 | Analytics produit |
| **P2** | Pilotes actifs | ≥ 5 entreprises | CRM |
| **P2** | NPS pilotes | > 30 | Enquête mensuelle |
| **P2** | Leads qualifiés/semaine | > 50 | CRM HubSpot/Salesforce |
| **P3** | Clients payants | ≥ 20 | Facturation |
| **P3** | ARR (Annual Recurring Revenue) | ≥ 100k EUR | Tableau de bord CFO |
| **P3** | Clients Maroc actifs | ≥ 5 | CRM zone MA |
| **P3** | Uptime production | > 99,5% | Datadog/Grafana |
| **P4** | ARR total | ≥ 1M EUR | Tableau de bord CFO |
| **P4** | NPS global | > 50 | Enquête trimestrielle |
| **P4** | Churn mensuel | < 5% | Analytics |
| **P4** | Communauté OSS | 1000+ stars GitHub | GitHub API |
| **P4** | E-NPS équipe | > 40 | Enquête anonyme |

### Tableau de bord de progression

```
TAKA OS — Scorecard de progression
══════════════════════════════════════════════════════════════════

Phase P1 (M1) ─────────────────────────────────────────── [████░░░░░░] 40%
  [✓] Architecture technique     [✓] Infra cloud
  [✓] Wireframes MVP             [✗] Kernel Parser (en cours)
  [✗] Framework agents           [✗] Scoring engine
  [✗] UI Dashboard               [✗] Release MVP 0.1

Phase P2 (M2-M3) ──────────────────────────────────────── [░░░░░░░░░░] 0%
  [○] Stratégie GTM              [○] V1.0 Release
  [○] Audit sécurité             [○] V1.1 Release
  [○] Pipeline commercial        [○] 5 pilotes actifs

Phase P3 (M4-M6) ──────────────────────────────────────── [░░░░░░░░░░] 0%
  [○] Hub Maroc                  [○] V2.0 Multi-marché
  [○] 20 clients payants         [○] 100k EUR ARR

Phase P4 (M7+) ────────────────────────────────────────── [░░░░░░░░░░] 0%
  [○] V3.0 + IA générative       [○] SOC2 Type I
  [○] 1M EUR ARR                 [○] Communauté 1000+
══════════════════════════════════════════════════════════════════
Légende : [✓] Terminé  [✗] En cours  [○] Non démarré
```

---

## Annexes

### A. Récapitulatif des effectifs par phase

| Phase | P1 | P2 | P3 | P4 |
|-------|----|----|----|----|
| Direction | 3 | 3 | 4 | 4 |
| Produit & Design | 2 | 2 | 2 | 2 |
| Backend | 4 | 4 | 4 | 4 |
| DevOps | 1 | 1 | 1 | 1 |
| Frontend | 2 | 2 | 2 | 2 |
| IA | 4 | 4 | 4 | 4 |
| Sales FR | 0 | 3 | 3 | 3 |
| Marketing | 0 | 2 | 2 | 2 |
| Sécurité & Conformité | 0 | 2 | 3 | 3 |
| Maroc | 0 | 0 | 4 | 4 |
| Opérations | 0 | 0 | 1 | 1 |
| **Total** | **16** | **23** | **30** | **30** |
| **Nouveaux** | **16** | **+7** | **+7** | **+0** |

### B. Calendrier des recrutements

| Semaine | Recrutements | Détail |
|---------|-------------|--------|
| S-4 à S0 (pré-projet) | 4 postes | CTO, COO, CPO, Lead BE — cofondateurs/core team |
| S0 à S1 | 12 postes | Tous les autres agents P1 (batch de recrutement initial) |
| S4 à S5 | 5 postes | Head Sales, SDR, Head Marketing, Security Officer, DPO |
| S5 à S6 | 2 postes | CSM_FR, Content Creator |
| S12 à S13 | 5 postes | Country MA, Legal EU, Legal MA, CFO, Office Manager |
| S13 à S14 | 1 poste | Sales MA |
| S14 à S15 | 1 poste | CSM_MA |

### C. Glossaire

| Terme | Définition |
|-------|-----------|
| MVP | Minimum Viable Product — version minimale fonctionnelle |
| GTM | Go-To-Market — stratégie de mise sur le marché |
| SDR | Sales Development Representative — prospection commerciale |
| CSM | Customer Success Manager — accompagnement client |
| DPO | Data Protection Officer — délégué à la protection des données |
| ARR | Annual Recurring Revenue — revenus récurrents annuels |
| MAU | Monthly Active Users — utilisateurs actifs mensuels |
| NPS | Net Promoter Score — score de recommandation |
| ICP | Ideal Customer Profile — profil de client idéal |
| CAC | Customer Acquisition Cost — coût d'acquisition client |
| LTV | Lifetime Value — valeur vie client |
| AO | Appel d'Offres |
| BOAMP | Bulletin Officiel des Annonces des Marchés Publics |
| SOC2 | Service Organization Control 2 — certification sécurité |
| BSPCE | Bons de Souscription de Parts de Créateur d'Entreprise |

---

*Document produit le 17 juin 2025 - Version 1.0*
*Propriété : TAKA OS - Tous droits réservés*
