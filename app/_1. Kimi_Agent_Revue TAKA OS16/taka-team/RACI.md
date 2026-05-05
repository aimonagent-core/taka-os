# TAKA OS — Matrice RACI des Processus Cles

> **Version** : 1.0  
> **Date** : 2025-06-11  
> **Projet** : TAKA OS — Operating System Agentic Open Source (MIT)  
> **Vertical** : Appels d'Offres (AO)  
> **Processus couverts** : 15  
> **Agents impliques** : 30 sur 30  

---

## Legende

| Code | Signification | Definition |
|------|---------------|------------|
| **R** | **Responsible** | Execute le travail, realise la tache |
| **A** | **Accountable** | Unique personne redevable du resultat, valide |
| **C** | **Consulted** | Consulte avant decision, apporte expertise |
| **I** | **Informed** | Informe du resultat, en retour |

> **Regle d'or** : Chaque processus a **1 et 1 seul A (Accountable)**.  
> Un agent peut cumuler R+A. Le C est actif (bidirectionnel), l'I est passif (notification).

---

## Sommaire des 15 Processus

| ID | Processus | Domaine | Phase critique |
|----|-----------|---------|----------------|
| P1 | Release MVP | Engineering | S1-S4 |
| P2 | Parsing DCE | IA / Backend | S2-S3 |
| P3 | Scoring qualif | IA / Produit | S2-S3 |
| P4 | Deploiement infra | DevOps | S1-S4 |
| P5 | Incident securite | Securite | Permanent |
| P6 | Onboarding client | GTM / CS | S3-S4 |
| P7 | Vente & closing | GTM / Sales | S3-S4 |
| P8 | Support client | GTM / CS | S3-S4 |
| P9 | Conformite RGPD | Juridique | S2-S4 |
| P10 | Conformite AI Act | Juridique / IA | S3-S4 |
| P11 | Content marketing | Marketing | S2-S4 |
| P12 | Fundraising | Direction | S2-S4 |
| P13 | Recrutement | RH / Direction | Permanent |
| P14 | Backup & recovery | DevOps / Securite | Permanent |
| P15 | Mise a jour LLM | IA / Engineering | S3-S4 |

---

## Matrice RACI Complete

### P1 — Release MVP
> **Description** : Cycle de release complet (planning, developpement, test, deploiement) sur les Sprints S1 a S4.  
> **Frequence** : Bi-hebdomadaire (sprints agiles)  
> **Livrable** : Increment deployable, notes de release, changelog

| Agent | Role | R | A | C | I | Justification |
|-------|------|---|---|---|---|---------------|
| `agent_001` | CTO | — | **A** | — | — | Valide la release, decision go/no-go production |
| `agent_003` | CPO | — | — | **C** | — | Valide l'adéquation produit des livrables |
| `agent_004` | PM_AO | **R** | — | — | — | Pilotage du sprint, priorisation du backlog |
| `agent_005` | UX_DESIGNER | **R** | — | **C** | — | Livraison des maquettes, validation UX |
| `agent_006` | LEAD_BACKEND | **R** | — | **C** | — | Coordination backend, revue de code |
| `agent_007` | BE_KERNEL | **R** | — | — | — | Dev features kernel & auth |
| `agent_008` | BE_AGENTS | **R** | — | — | — | Dev features agents & orchestration |
| `agent_009` | BE_API | **R** | — | — | — | Dev endpoints API, tests integration |
| `agent_010` | DEVOPS | **R** | — | **C** | — | Pipeline CI/CD, deploiement staging/prod |
| `agent_011` | LEAD_FRONTEND | **R** | — | **C** | — | Coordination frontend, revue de code |
| `agent_012` | FE_UI | **R** | — | — | — | Dev composants UI, integration API |
| `agent_013` | LEAD_IA | **R** | — | **C** | — | Coordination features IA, validation modeles |
| `agent_014` | IA_NLP | **R** | — | — | — | Dev features parsing NLP |
| `agent_015` | IA_SCORING | **R** | — | — | — | Dev features scoring & qualification |
| `agent_016` | IA_EMBEDDINGS | **R** | — | — | — | Dev features RAG & embeddings |
| `agent_022` | SEC_OFFICER | — | — | **C** | — | Audit securite pre-release |
| `agent_002` | COO | — | — | — | **I** | Information sur la roadmap release |
| `agent_017` | HEAD_SALES_FR | — | — | — | **I** | Information pour anticiper demos |
| `agent_029` | CFO | — | — | — | **I** | Information budgetaire |

**Responsables (R)** : agent_004, agent_005, agent_006, agent_007, agent_008, agent_009, agent_010, agent_011, agent_012, agent_013, agent_014, agent_015, agent_016  
**Consultés (C)** : agent_003, agent_006, agent_011, agent_013, agent_022  
**Informés (I)** : agent_002, agent_017, agent_029

---

### P2 — Parsing DCE
> **Description** : Pipeline de parsing des documents de consultation (DCE) au format PDF, UBL, DOCX. Extraction structuree des exigences, eligibilite, calendrier.  
> **Frequence** : A chaque upload de DCE (temps reel)  
> **Livrable** : JSON structure, objets metier AO, alertes anomalies

| Agent | Role | R | A | C | I | Justification |
|-------|------|---|---|---|---|---------------|
| `agent_013` | LEAD_IA | — | **A** | — | — | Architecture et qualite du pipeline parsing |
| `agent_014` | IA_NLP | **R** | — | — | — | Implementation modeles NLP, NER, classification |
| `agent_008` | BE_AGENTS | **R** | — | — | — | Orchestration agentique, workflow parsing |
| `agent_009` | BE_API | — | — | **C** | — | Contrat API, format JSON de sortie |
| `agent_004` | PM_AO | — | — | **C** | — | Specification metier des champs a extraire |
| `agent_016` | IA_EMBEDDINGS | — | — | **C** | — | Indexation vectorielle des DCE pour recherche |
| `agent_003` | CPO | — | — | — | **I** | Vision produit parsing |
| `agent_017` | HEAD_SALES_FR | — | — | — | **I** | Feedback clients sur qualite parsing |

**Responsables (R)** : agent_014, agent_008  
**Consultés (C)** : agent_009, agent_004, agent_016  
**Informés (I)** : agent_003, agent_017

---

### P3 — Scoring qualif
> **Description** : Algorithme GO/NO-GO evaluant l'eligibilite d'une entreprise a repondre a un AO. Scoring multi-criteres (eligibilite, marge, calendrier, concurrence).  
> **Frequence** : A chaque parsing de DCE valide  
> **Livrable** : Score (0-100), preconisation GO/NO-GO, justification

| Agent | Role | R | A | C | I | Justification |
|-------|------|---|---|---|---|---------------|
| `agent_013` | LEAD_IA | — | **A** | — | — | Qualite et calibration du scoring |
| `agent_015` | IA_SCORING | **R** | — | — | — | Implementation du moteur de scoring |
| `agent_014` | IA_NLP | **R** | — | — | — | Features linguistiques pour le scoring |
| `agent_004` | PM_AO | — | — | **C** | — | Definition des regles metier et poids |
| `agent_009` | BE_API | — | — | **C** | — | Endpoint scoring, stockage resultats |
| `agent_019` | CSM_FR | — | — | **C** | — | Feedback terrain sur pertinence scores |
| `agent_003` | CPO | — | — | — | **I** | Validation produit scoring |
| `agent_017` | HEAD_SALES_FR | — | — | — | **I** | Utilisation scores pour qualification leads |

**Responsables (R)** : agent_015, agent_014  
**Consultés (C)** : agent_004, agent_009, agent_019  
**Informés (I)** : agent_003, agent_017

---

### P4 — Deploiement infra
> **Description** : Mise en place et maintenance de l'infrastructure cloud (Docker, Nginx, SSL, BDD, monitoring). Deploiements blue/green, scaling.  
> **Frequence** : Permanent + a chaque release  
> **Livrable** : Infra operationnelle, certificats SSL valides, monitoring actif

| Agent | Role | R | A | C | I | Justification |
|-------|------|---|---|---|---|---------------|
| `agent_006` | LEAD_BACKEND | — | **A** | — | — | Architecture infra, decisions techniques |
| `agent_010` | DEVOPS | **R** | — | — | — | Implementation, IaC, pipelines deploy |
| `agent_007` | BE_KERNEL | — | — | **C** | — | Contraintes infra auth, BDD, cache |
| `agent_022` | SEC_OFFICER | — | — | **C** | — | Hardening, configuration SSL/TLS, audits |
| `agent_009` | BE_API | — | — | — | **C** | Contraintes DB, performance API |
| `agent_001` | CTO | — | — | — | **I** | Vision technique infra |
| `agent_002` | COO | — | — | — | **I** | Budget infra, SLA clients |

**Responsables (R)** : agent_010  
**Consultés (C)** : agent_007, agent_022, agent_009  
**Informés (I)** : agent_001, agent_002

---

### P5 — Incident securite
> **Description** : Reponse aux incidents de securite (detection, analyse, containment, eradication, recovery). Application de patches.  
> **Frequence** : A la detection (processus reactif)  
> **Livrable** : Rapport d'incident, patch applique, communication client

| Agent | Role | R | A | C | I | Justification |
|-------|------|---|---|---|---|---------------|
| `agent_001` | CTO | — | **A** | — | — | Decision strategique, communication board |
| `agent_022` | SEC_OFFICER | **R** | — | — | — | Detection, analyse, coordination reponse |
| `agent_010` | DEVOPS | **R** | — | — | — | Application patches, isolation infra |
| `agent_007` | BE_KERNEL | **R** | — | — | — | Patch auth, BDD, composants critiques |
| `agent_027` | LEGAL_EU | — | — | **C** | — | Obligations legales notification CNIL |
| `agent_023` | DPO | — | — | **C** | — | Impact donnees personnelles, mesures RGPD |
| `agent_013` | LEAD_IA | — | — | **C** | — | Si incident sur modeles IA (poisoning, fuite) |
| `agent_006` | LEAD_BACKEND | — | — | — | **I** | Coordination equipe backend |
| `agent_011` | LEAD_FRONTEND | — | — | — | **I** | Coordination equipe frontend |
| `agent_002` | COO | — | — | — | **I** | Impact operations, communication client |
| `agent_029` | CFO | — | — | — | **I** | Impact financier, assurance |

**Responsables (R)** : agent_022, agent_010, agent_007  
**Consultés (C)** : agent_027, agent_023, agent_013  
**Informés (I)** : agent_006, agent_011, agent_002, agent_029

---

### P6 — Onboarding client
> **Description** : Processus complet d'integration d'un nouveau client : provisioning tenant, configuration SSO, formation equipe, parametrique metier.  
> **Frequence** : A chaque nouveau client signe  
> **Livrable** : Tenant operationnel, comptes actifs, session formation realisee

| Agent | Role | R | A | C | I | Justification |
|-------|------|---|---|---|---|---------------|
| `agent_002` | COO | — | **A** | — | — | Qualite et KPI onboarding client |
| `agent_019` | CSM_FR | **R** | — | — | — | Coordination onboarding, formation, suivi |
| `agent_009` | BE_API | **R** | — | — | — | Provisioning tenant, API configuration |
| `agent_010` | DEVOPS | **R** | — | — | — | Deploiement environnement client, DNS |
| `agent_004` | PM_AO | — | — | **C** | — | Parametrage metier, configuration produit |
| `agent_017` | HEAD_SALES_FR | — | — | **C** | — | Transfert connaissance client post-closing |
| `agent_018` | SDR_FR | — | — | — | **I** | Information contexte client |
| `agent_029` | CFO | — | — | — | **I** | Activation facturation, reconnaissance revenu |
| `agent_027` | LEGAL_EU | — | — | — | **I** | Validation contrat, DPA signe |

**Responsables (R)** : agent_019, agent_009, agent_010  
**Consultés (C)** : agent_004, agent_017  
**Informés (I)** : agent_018, agent_029, agent_027

---

### P7 — Vente & closing
> **Description** : Cycle commercial complet : prospection, qualification, demo, proposition commerciale, negociation, signature.  
> **Frequence** : Permanent  
> **Livrable** : Contrat signe, bon de commande, planning d'onboarding

| Agent | Role | R | A | C | I | Justification |
|-------|------|---|---|---|---|---------------|
| `agent_002` | COO | — | **A** | — | — | Objectifs commerciaux, validation offres |
| `agent_017` | HEAD_SALES_FR | **R** | — | — | — | Strategie commerciale, closing grands comptes |
| `agent_018` | SDR_FR | **R** | — | — | — | Prospection, qualification, rendez-vous |
| `agent_004` | PM_AO | — | — | **C** | — | Support demo, reponses techniques |
| `agent_003` | CPO | — | — | **C** | — | Positioning produit, roadmap |
| `agent_027` | LEGAL_EU | — | — | **C** | — | Validation contrats, negociation juridique |
| `agent_001` | CEO | — | — | — | **I** | Suivi pipe strategique |
| `agent_029` | CFO | — | — | — | **I** | Validation conditions financieres |
| `agent_019` | CSM_FR | — | — | — | **I** | Anticipation onboarding post-signature |

**Responsables (R)** : agent_017, agent_018  
**Consultés (C)** : agent_004, agent_003, agent_027  
**Informés (I)** : agent_001, agent_029, agent_019

---

### P8 — Support client
> **Description** : Traitement des tickets support, maintenance de la FAQ, escalade des incidents, mesure de satisfaction (CSAT/NPS).  
> **Frequence** : Permanent  
> **Livrable** : Ticket resolu, FAQ mise a jour, rapport CSAT

| Agent | Role | R | A | C | I | Justification |
|-------|------|---|---|---|---|---------------|
| `agent_002` | COO | — | **A** | — | — | Niveau de service, escalation finale |
| `agent_019` | CSM_FR | **R** | — | — | — | Traitement tickets L1/L2, relation client |
| `agent_009` | BE_API | **R** | — | — | — | Resolution incidents techniques L3 |
| `agent_010` | DEVOPS | — | — | **C** | — | Incidents infrastructure |
| `agent_004` | PM_AO | — | — | **C** | — | Bugs produit, feature requests |
| `agent_017` | HEAD_SALES_FR | — | — | — | **I** | Alertes churn, opportunites upsell |
| `agent_003` | CPO | — | — | — | **I** | Tendances feedback produit |

**Responsables (R)** : agent_019, agent_009  
**Consultés (C)** : agent_010, agent_004  
**Informés (I)** : agent_017, agent_003

---

### P9 — Conformite RGPD
> **Description** : Mise en conformite RGPD : droit a l'oubli, registre des traitements, DPIA, consentements, exercice des droits des personnes.  
> **Frequence** : Permanent + audits annuels  
> **Livrable** : Registre des traitements a jour, DPIA, preuve de conformite

| Agent | Role | R | A | C | I | Justification |
|-------|------|---|---|---|---|---------------|
| `agent_027` | LEGAL_EU | — | **A** | — | — | Responsabilite juridique conformite |
| `agent_023` | DPO | **R** | — | — | — | Pilotage operational RGPD, registre, DPIA |
| `agent_007` | BE_KERNEL | — | — | **C** | — | Implementation droit a l'oubli, anonymisation |
| `agent_010` | DEVOPS | — | — | **C** | — | Chiffrement, logs, politique de retention |
| `agent_022` | SEC_OFFICER | — | — | **C** | — | Securite des donnees, mesures techniques |
| `agent_001` | CEO | — | — | — | **I** | Responsabilite penale |
| `agent_002` | COO | — | — | — | **I** | Politique RH liee aux donnees |
| `agent_003` | CPO | — | — | — | **I** | Consentements produit |

**Responsables (R)** : agent_023  
**Consultes (C)** : agent_007, agent_010, agent_022  
**Informes (I)** : agent_001, agent_002, agent_003

---

### P10 — Conformite AI Act
> **Description** : Mise en conformite Reglement europeen sur l'IA : badge IA, transparence, documentation technique, evaluation des risques, registre IA.  
> **Frequence** : A chaque nouveau modele / feature IA  
> **Livrable** : Fiche conformite IA, documentation technique, registre EU

| Agent | Role | R | A | C | I | Justification |
|-------|------|---|---|---|---|---------------|
| `agent_027` | LEGAL_EU | — | **A** | — | — | Interpretation reglementaire, registre UE |
| `agent_013` | LEAD_IA | **R** | — | — | — | Documentation technique, evaluation risques |
| `agent_014` | IA_NLP | — | — | **C** | — | Documentation modeles NLP, biais |
| `agent_015` | IA_SCORING | — | — | **C** | — | Documentation scoring, explainability |
| `agent_003` | CPO | — | — | **C** | — | Transparence produit, notices utilisateurs |
| `agent_004` | PM_AO | — | — | **C** | — | Specification fonctionnelle, cas d'usage |
| `agent_001` | CEO | — | — | — | **I** | Risque reglementaire |
| `agent_002` | COO | — | — | — | **I** | Impact operationnel |

**Responsables (R)** : agent_013  
**Consultes (C)** : agent_014, agent_015, agent_003, agent_004  
**Informes (I)** : agent_001, agent_002

---

### P11 — Content marketing
> **Description** : Production et diffusion de contenu : blog, SEO, newsletter, community management, evenements, cas d'usage.  
> **Frequence** : Hebdomadaire  
> **Livrable** : Articles, posts, newsletters, webinars, rapport trafic

| Agent | Role | R | A | C | I | Justification |
|-------|------|---|---|---|---|---------------|
| `agent_020` | HEAD_MARKETING | — | **A** | — | — | Strategie content, calendrier editorial |
| `agent_021` | CONTENT_CREATOR | **R** | — | — | — | Redaction, creation visuelle, publication |
| `agent_004` | PM_AO | — | — | **C** | — | Contenu produit, fonctionnalites, roadmap |
| `agent_003` | CPO | — | — | **C** | — | Positioning, messaging |
| `agent_017` | HEAD_SALES_FR | — | — | **C** | — | Besoins contenu commerciaux, temoignages |
| `agent_002` | COO | — | — | — | **I** | ROI marketing, budget |
| `agent_001` | CEO | — | — | — | **I** | Branding, voix de la marque |

**Responsables (R)** : agent_021  
**Consultes (C)** : agent_004, agent_003, agent_017  
**Informes (I)** : agent_002, agent_001

---

### P12 — Fundraising
> **Description** : Preparation et execution des levees de fonds : pitch deck, due diligence, dataroom, negociation term sheet, closing.  
> **Frequence** : Par levee (typiquement 2-3x par an)  
> **Livrable** : Pitch deck, dataroom complete, term sheet signe

| Agent | Role | R | A | C | I | Justification |
|-------|------|---|---|---|---|---------------|
| `agent_001` | CEO | — | **A** | — | — | Vision, pitch, negociation |
| `agent_029` | CFO | **R** | — | — | — | Dataroom financiere, modele, projections |
| `agent_001` | CTO | **R** | — | — | — | Dataroom technique, roadmap produit |
| `agent_002` | COO | — | — | **C** | — | Operations, KPI, plan de deploiement |
| `agent_003` | CPO | — | — | **C** | — | Vision produit, traction, roadmap |
| `agent_027` | LEGAL_EU | — | — | **C** | — | Due diligence juridique, term sheet |
| `agent_006` | LEAD_BACKEND | — | — | — | **I** | Architecture technique pour due diligence |
| `agent_013` | LEAD_IA | — | — | — | **I** | Stack IA pour due diligence |
| `agent_017` | HEAD_SALES_FR | — | — | — | **I** | Pipe, traction commerciale |
| `agent_020` | HEAD_MARKETING | — | — | — | **I** | Traction marketing, metrics |

**Responsables (R)** : agent_029, agent_001 (CTO)  
**Consultes (C)** : agent_002, agent_003, agent_027  
**Informes (I)** : agent_006, agent_013, agent_017, agent_020

---

### P13 — Recrutement
> **Description** : Processus de recrutement : definition du besoin, sourcing, entretiens, offre, onboarding administratif.  
> **Frequence** : Permanent  
> **Livrable** : Contrat de travail signe, plan d'integration, poste pourvu

| Agent | Role | R | A | C | I | Justification |
|-------|------|---|---|---|---|---------------|
| `agent_002` | COO | — | **A** | — | — | Budget RH, validation recrutements |
| `agent_030` | OFFICE_MGR | **R** | — | — | — | Sourcing, entretiens admin, integration |
| `agent_001` | CTO | — | — | **C** | — | Validation profils tech (back, front, IA) |
| `agent_003` | CPO | — | — | **C** | — | Validation profils produit, UX |
| `agent_029` | CFO | — | — | **C** | — | Enveloppe budgetaire, package salarial |
| `agent_027` | LEGAL_EU | — | — | **C** | — | Contrats de travail, clauses |
| `agent_001` | CEO | — | — | — | **I** | Recrutements C-Level |
| `agent_006` | LEAD_BACKEND | — | — | — | **I** | Besoins equipe backend |
| `agent_011` | LEAD_FRONTEND | — | — | — | **I** | Besoins equipe frontend |
| `agent_013` | LEAD_IA | — | — | — | **I** | Besoins equipe IA |
| `agent_017` | HEAD_SALES_FR | — | — | — | **I** | Besoins equipe sales |
| `agent_020` | HEAD_MARKETING | — | — | — | **I** | Besoins equipe marketing |

**Responsables (R)** : agent_030  
**Consultes (C)** : agent_001 (CTO), agent_003, agent_029, agent_027  
**Informes (I)** : agent_001 (CEO), agent_006, agent_011, agent_013, agent_017, agent_020

---

### P14 — Backup & recovery
> **Description** : Politique de sauvegarde, tests de restoration, plan de reprise d'activite (PRA), RTO/RPO.  
> **Frequence** : Sauvegardes quotidiennes, test mensuel  
> **Livrable** : Sauvegardes valides, test PRA, documentation

| Agent | Role | R | A | C | I | Justification |
|-------|------|---|---|---|---|---------------|
| `agent_006` | LEAD_BACKEND | — | **A** | — | — | Architecture backup, RTO/RPO |
| `agent_010` | DEVOPS | **R** | — | — | — | Implementation backup, tests restore |
| `agent_009` | BE_API | **R** | — | — | — | Consistence BDD, dumps |
| `agent_022` | SEC_OFFICER | — | — | **C** | — | Chiffrement backups, securite |
| `agent_029` | CFO | — | — | **C** | — | Assurance, impact financier |
| `agent_001` | CTO | — | — | — | **I** | Validation strategie PRA |
| `agent_002` | COO | — | — | — | **I** | Impact operations, SLA |

**Responsables (R)** : agent_010, agent_009  
**Consultes (C)** : agent_022, agent_029  
**Informes (I)** : agent_001, agent_002

---

### P15 — Mise a jour LLM
> **Description** : Changement de modele de langage (LLM), evaluation, fine-tuning, A/B testing, rollback.  
> **Frequence** : Par release modele (trimestriel ou evenementiel)  
> **Livrable** : Nouveau modele deploye, rapport eval, plan rollback

| Agent | Role | R | A | C | I | Justification |
|-------|------|---|---|---|---|---------------|
| `agent_001` | CTO | — | **A** | — | — | Decision changement modele, risque |
| `agent_013` | LEAD_IA | **R** | — | — | — | Coordination migration, evaluation |
| `agent_014` | IA_NLP | **R** | — | — | — | Evaluation NLP, regression tests |
| `agent_016` | IA_EMBEDDINGS | **R** | — | — | — | Re-indexation, tests RAG |
| `agent_008` | BE_AGENTS | — | — | **C** | — | Impact orchestration, compatibilite |
| `agent_003` | CPO | — | — | **C** | — | Impact produit, UX |
| `agent_004` | PM_AO | — | — | **C** | — | Tests fonctionnels, cas d'usage |
| `agent_002` | COO | — | — | — | **I** | Budget inference (cout/call) |
| `agent_017` | HEAD_SALES_FR | — | — | — | **I** | Impact performances demo |

**Responsables (R)** : agent_013, agent_014, agent_016  
**Consultes (C)** : agent_008, agent_003, agent_004  
**Informes (I)** : agent_002, agent_017

---

## Synthese Globale RACI

### Repartition des roles A (Accountable) par agent

| Agent | Compte A | Processus ou il est Accountable |
|-------|----------|--------------------------------|
| `agent_001` (CTO) | 4 | P1, P5, P12, P15 |
| `agent_002` (COO) | 4 | P6, P7, P8, P13 |
| `agent_027` (LEGAL_EU) | 2 | P9, P10 |
| `agent_006` (LEAD_BACKEND) | 2 | P4, P14 |
| `agent_013` (LEAD_IA) | 1 | P2 |
| `agent_020` (HEAD_MARKETING) | 1 | P11 |
| `agent_029` (CFO) | 0 | — (R sur P12) |

> **Note** : Le CEO (humain) est Accountable sur P12 (Fundraising) en complement du CTO.

### Taux de couverture des agents

```
Agents actifs (R, A ou C) sur au moins 1 processus : 30/30 (100%)

Agents avec role A (Accountable)     :  7 agents
Agents avec role R (Responsible)     : 25 agents
Agents avec role C (Consulted)       : 28 agents
Agents avec role I (Informed)        : 28 agents
```

### Heatmap des processus les plus transverses

```
P1  Release MVP          ████████████████████  18 agents impliques
P5  Incident securite    ████████████████░░░░  11 agents impliques
P12 Fundraising          ██████████████░░░░░░  10 agents impliques
P13 Recrutement          ██████████████░░░░░░  12 agents impliques
P6  Onboarding client    ████████████░░░░░░░░   9 agents impliques
P7  Vente & closing      ████████████░░░░░░░░   9 agents impliques
P2  Parsing DCE          ████████░░░░░░░░░░░░   8 agents impliques
P3  Scoring qualif       ████████░░░░░░░░░░░░   8 agents impliques
P9  Conformite RGPD      ████████████░░░░░░░░   9 agents impliques
P10 Conformite AI Act    ████████░░░░░░░░░░░░   8 agents impliques
P14 Backup & recovery    ██████████░░░░░░░░░░   7 agents impliques
P4  Deploiement infra    ████████░░░░░░░░░░░░   7 agents impliques
P15 Mise a jour LLM      ██████████░░░░░░░░░░   9 agents impliques
P8  Support client       ████████░░░░░░░░░░░░   7 agents impliques
P11 Content marketing    ████████░░░░░░░░░░░░   7 agents impliques
```

---

## Glossary

| Terme | Definition |
|-------|------------|
| **DCE** | Document de Consultation des Entreprises (cahier des charges de l'AO) |
| **DPIA** | Data Protection Impact Assessment (analyse d'impact RGPD) |
| **LLM** | Large Language Model (modele de langage, ex: GPT-4, Claude, Mistral) |
| **RAG** | Retrieval-Augmented Generation (architecture IA combinant recherche et generation) |
| **RTO** | Recovery Time Objective (temps cible de reprise d'activite) |
| **RPO** | Recovery Point Objective (perte de donnees maximale acceptable) |
| **PRA** | Plan de Reprise d'Activite |
| **CSAT** | Customer Satisfaction Score |
| **NPS** | Net Promoter Score |
| **SSO** | Single Sign-On |
| **DPA** | Data Processing Agreement |
| **IaC** | Infrastructure as Code |

---

*Document genere automatiquement pour TAKA OS. Derniere mise a jour : 2025-06-11*
