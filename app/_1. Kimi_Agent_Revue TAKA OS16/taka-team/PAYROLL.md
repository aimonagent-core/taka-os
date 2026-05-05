# TAKA OS - Masse Salariale & Budget Personnel

> **Document**: PAYROLL.md
> **Projet**: TAKA OS - Operating System Agentic pour Appels d'Offres (Open Source MIT)
> **Date**: Juin 2025
> **Version**: 1.0
> **Effectif total**: 30 agents repartis sur 11 pôles et 4 phases d'activation
> **Déploiement**: France ( siège ) + Maroc ( hub offshore )

---

## Sommaire

1. [Résumé exécutif](#1-résumé-exécutif)
2. [Masse salariale par phase](#2-masse-salariale-par-phase)
3. [Répartition France / Maroc](#3-répartition-france--maroc)
4. [Coûts chargés détaillés](#4-coûts-chargés-détaillés)
5. [Table récapitulative par agent](#5-table-récapitulative-par-agent)
6. [Évolution mensuelle (graphique textuel)](#6-évolution-mensuelle)
7. [Scénarios minimal vs complet](#7-scénarios-minimal-vs-complet)
8. [Analyse et recommandations](#8-analyse-et-recommandations)

---

## 1. Résumé exécutif

| Indicateur | Valeur |
|-----------|--------|
| Effectif total (année 1) | 30 agents |
| Activation progressive | 16 → 23 → 30 agents |
| Masse salariale brute annuelle max (P3-P4) | 1 985 899 EUR eq. |
| Masse salariale chargée annuelle max (P3-P4) | 2 849 829 EUR eq. |
| Coût total employeur Année 1 (cumulé) | **2 684 143 EUR** |
| Charges patronales France | +45% |
| Charges patronales Maroc | +20% + CNSS |
| Taux de conversion MAD→EUR | 10,90 |
| Ratio France / Maroc (P3-P4 en effectifs) | 80% / 20% |
| Ratio France / Maroc (P3-P4 en masse salariale eq.) | 95% / 5% |

### Structure par niveau d'expérience

| Niveau | Effectif | % Effectif | Masse brute FR | Masse brute MA (eq.EUR) | Total eq.EUR |
|--------|----------|-----------|---------------|------------------------|-------------|
| C-Level | 4 | 13,3% | 440 000 EUR | 0 EUR | 440 000 EUR |
| Head | 3 | 10,0% | 160 000 EUR | 44 037 EUR | 204 037 EUR |
| Senior | 14 | 46,7% | 935 000 EUR | 33 028 EUR | 968 028 EUR |
| Mid | 9 | 30,0% | 332 000 EUR | 41 835 EUR | 373 835 EUR |
| **Total** | **30** | **100%** | **1 867 000 EUR** | **118 899 EUR eq.** | **1 985 899 EUR eq.** |

---

## 2. Masse salariale par phase

### Phase 1 — MVP (Mois 1) : 16 agents Tech

| Poste | Agent | Niveau | Localisation | Brut annuel | Chargé annuel |
|-------|-------|--------|-------------|------------|--------------|
| CTO | agent_001 | C-Level | France | 120 000 EUR | 174 000 EUR |
| COO | agent_002 | C-Level | France | 110 000 EUR | 159 500 EUR |
| CPO | agent_003 | C-Level | France | 110 000 EUR | 159 500 EUR |
| PM AO | agent_004 | Senior | France | 75 000 EUR | 108 750 EUR |
| UX Designer | agent_005 | Senior | France | 65 000 EUR | 94 250 EUR |
| Lead Backend | agent_006 | Senior | France | 80 000 EUR | 116 000 EUR |
| BE Kernel | agent_007 | Senior | France | 70 000 EUR | 101 500 EUR |
| BE Agents | agent_008 | Senior | France | 70 000 EUR | 101 500 EUR |
| BE API | agent_009 | Mid | France | 55 000 EUR | 79 750 EUR |
| DevOps | agent_010 | Senior | France | 70 000 EUR | 101 500 EUR |
| Lead Frontend | agent_011 | Senior | France | 75 000 EUR | 108 750 EUR |
| FE UI | agent_012 | Mid | France | 50 000 EUR | 72 500 EUR |
| Lead IA | agent_013 | Senior | France | 80 000 EUR | 116 000 EUR |
| IA NLP | agent_014 | Senior | France | 70 000 EUR | 101 500 EUR |
| IA Scoring | agent_015 | Senior | France | 70 000 EUR | 101 500 EUR |
| IA Embeddings | agent_016 | Mid | France | 55 000 EUR | 79 750 EUR |
| | | | **Sous-total P1** | **1 225 000 EUR** | **1 776 250 EUR** |
| | | | **Coût mensuel P1** | **102 083 EUR** | **148 021 EUR** |

### Phase 2 — V1.1 + GTM FR (Mois 2-3) : 23 agents (+7)

Tous les agents P1 restent actifs. Ajouts :

| Poste | Agent | Niveau | Localisation | Brut annuel | Chargé annuel |
|-------|-------|--------|-------------|------------|--------------|
| Head Sales FR | agent_017 | Head | France | 85 000 EUR | 123 250 EUR |
| SDR FR | agent_018 | Mid | France | 45 000 EUR | 65 250 EUR |
| CSM FR | agent_019 | Mid | France | 45 000 EUR | 65 250 EUR |
| Head Marketing | agent_020 | Head | France | 75 000 EUR | 108 750 EUR |
| Content Creator | agent_021 | Mid | France | 40 000 EUR | 58 000 EUR |
| Security Officer | agent_022 | Senior | France | 70 000 EUR | 101 500 EUR |
| DPO | agent_023 | Senior | France | 65 000 EUR | 94 250 EUR |
| | | | **Sous-total ajouts P2** | **425 000 EUR** | **616 250 EUR** |
| | | | **Sous-total P2 (cumulé)** | **1 650 000 EUR** | **2 392 500 EUR** |
| | | | **Coût mensuel P2** | **137 500 EUR** | **199 375 EUR** |

### Phase 3 — Multi-marché (Mois 4-6) : 30 agents (+7)

Tous les agents P1+P2 restent actifs. Ajouts :

| Poste | Agent | Niveau | Localisation | Brut annuel | Chargé annuel |
|-------|-------|--------|-------------|------------|--------------|
| Country Manager MA | agent_024 | Head | Maroc | 480 000 MAD (44 037 EUR) | 576 000 MAD (52 844 EUR) |
| Sales MA | agent_025 | Mid | Maroc | 240 000 MAD (22 018 EUR) | 288 000 MAD (26 422 EUR) |
| CSM MA | agent_026 | Mid | Maroc | 216 000 MAD (19 817 EUR) | 259 200 MAD (23 780 EUR) |
| Legal EU | agent_027 | Senior | France | 75 000 EUR | 108 750 EUR |
| Legal MA | agent_028 | Senior | Maroc | 360 000 MAD (33 028 EUR) | 432 000 MAD (39 633 EUR) |
| CFO | agent_029 | C-Level | France | 100 000 EUR | 145 000 EUR |
| Office Manager | agent_030 | Mid | France | 42 000 EUR | 60 900 EUR |
| | | | **Sous-total ajouts P3** | 335 900 EUR eq. | 457 329 EUR eq. |
| | | | **Sous-total P3 (cumulé)** | **1 985 899 EUR eq.** | **2 849 829 EUR eq.** |
| | | | **Coût mensuel P3** | **165 492 EUR eq.** | **237 486 EUR eq.** |

### Phase 4 — Scale (Mois 7+) : 30 agents

Aucun ajout d'effectif en P4. L'équipe de 30 agents reste stable pour la croissance. Le focus est sur l'amélioration de l'efficacité et l'automatisation.

| | | | **Sous-total P4** | **1 985 899 EUR eq.** | **2 849 829 EUR eq.** |
| | | | **Coût mensuel P4** | **165 492 EUR eq.** | **237 486 EUR eq.** |

### Cumul annuel par phase

| Phase | Période | Effectif | Durée | Coût mensuel moyen | Coût total phase | Cumul annuel |
|-------|---------|----------|-------|-------------------|-----------------|-------------|
| P1 MVP | Mois 1 | 16 | 1 mois | 148 021 EUR | 148 021 EUR | 148 021 EUR |
| P2 V1.1 | Mois 2-3 | 23 | 2 mois | 199 375 EUR | 398 750 EUR | 546 771 EUR |
| P3 Multi-marché | Mois 4-6 | 30 | 3 mois | 237 486 EUR | 712 457 EUR | 1 259 228 EUR |
| P4 Scale | Mois 7-12 | 30 | 6 mois | 237 486 EUR | 1 424 914 EUR | 2 684 143 EUR |
| **Total Année 1** | | | **12 mois** | | | **2 684 143 EUR** |

---

## 3. Répartition France / Maroc

### En effectifs

| Phase | France | Maroc | Total | % France | % Maroc |
|-------|--------|-------|-------|----------|---------|
| P1 | 16 | 0 | 16 | 100% | 0% |
| P2 | 23 | 0 | 23 | 100% | 0% |
| P3 | 24 | 6 | 30 | 80% | 20% |
| P4 | 24 | 6 | 30 | 80% | 20% |

### En masse salariale (brute, équivalent EUR)

| Phase | France (EUR) | Maroc (eq.EUR) | Total eq.EUR | % France | % Maroc |
|-------|-------------|---------------|-------------|----------|---------|
| P1 | 1 225 000 | 0 | 1 225 000 | 100% | 0% |
| P2 | 1 650 000 | 0 | 1 650 000 | 100% | 0% |
| P3 | 1 867 000 | 118 899 | 1 985 899 | 94,0% | 6,0% |
| P4 | 1 867 000 | 118 899 | 1 985 899 | 94,0% | 6,0% |

### En masse salariale (chargée, équivalent EUR)

| Phase | France (EUR) | Maroc (eq.EUR) | Total eq.EUR | % France | % Maroc |
|-------|-------------|---------------|-------------|----------|---------|
| P1 | 1 776 250 | 0 | 1 776 250 | 100% | 0% |
| P2 | 2 392 500 | 0 | 2 392 500 | 100% | 0% |
| P3 | 2 707 150 | 142 679 | 2 849 829 | 95,0% | 5,0% |
| P4 | 2 707 150 | 142 679 | 2 849 829 | 95,0% | 5,0% |

### En monnaie locale (P3-P4)

| Localisation | Brut annuel | Charges | Chargé annuel |
|-------------|------------|---------|--------------|
| **France (24 agents)** | 1 867 000 EUR | +45% = 840 150 EUR | **2 707 150 EUR** |
| **Maroc (6 agents)** | 1 296 000 MAD | +20% = 259 200 MAD | **1 555 200 MAD** |

---

## 4. Coûts chargés détaillés

### Méthodologie de calcul

| Paramètre | Valeur | Détail |
|-----------|--------|--------|
| Charges patronales France | 45% | URSSAF, retraite complémentaire, prévoyance, mutuelle, taxes sur les salaires, formation professionnelle, médecine du travail |
| Charges patronales Maroc | 20% | CNSS (familial 6%, formation 1%, AMO 4%, retraite CS 3,6%, retraite CAM 4%, prévoyance ~1,4%) |
| Taux de conversion | 1 EUR = 10,90 MAD | Taux moyen estimé 2025 |

### Décomposition des charges France (+45%)

| Composante | Taux | Commentaire |
|-----------|------|-------------|
| Sécurité sociale (maladie, vieillesse) | ~20% | URSSAF |
| Complémentaire retraite | ~7% | AGIRC-ARRCO |
| Prévoyance + Mutuelle | ~5% | Couverture décès/invalidité + remboursement santé |
| Taxe sur les salaires | ~4,25% | Selon CA (abolie si < ca. 2M EUR) |
| Formation professionnelle | ~1% | OPCO |
| Accident du travail | ~2% | Selon risque (taux moyen bureautique) |
| Autres (médecine du travail, transport) | ~5,75% | Forfait |
| **Total** | **~45%** | Fourchette réaliste pour une startup tech |

### Décomposition des charges Maroc (+20%)

| Composante | Taux | Commentaire |
|-----------|------|-------------|
| CNSS préstations familiales | 6,4% | |
| CNSS formation professionnelle | 1,6% | |
| CNSS AMO (assurance maladie obligatoire) | 4,11% | |
| Caisse de retraite (CMR/CNRA) | ~6% | Régime de retraite |
| Prévoyance complémentaire | ~2% | |
| **Total** | **~20%** | Sujet à variations selon convention collective |

---

## 5. Table récapitulative par agent

| ID | Agent | Niveau | Loc. | Phases | Brut annuel | Chargé annuel | Coût mensuel chargé |
|----|-------|--------|------|--------|------------|--------------|-------------------|
| **PÔLE DIRECTION** ||||||||
| agent_001 | CTO | C-Level | FR | P1-P4 | 120 000 EUR | 174 000 EUR | 14 500 EUR |
| agent_002 | COO | C-Level | FR | P1-P4 | 110 000 EUR | 159 500 EUR | 13 292 EUR |
| agent_003 | CPO | C-Level | FR | P1-P4 | 110 000 EUR | 159 500 EUR | 13 292 EUR |
| agent_029 | CFO | C-Level | FR | P3-P4 | 100 000 EUR | 145 000 EUR | 12 083 EUR |
| **PÔLE PRODUIT & DESIGN** ||||||||
| agent_004 | PM_AO | Senior | FR | P1-P4 | 75 000 EUR | 108 750 EUR | 9 063 EUR |
| agent_005 | UX_DESIGNER | Senior | FR | P1-P4 | 65 000 EUR | 94 250 EUR | 7 854 EUR |
| **PÔLE ENGINEERING BACKEND** ||||||||
| agent_006 | LEAD_BACKEND | Senior | FR | P1-P4 | 80 000 EUR | 116 000 EUR | 9 667 EUR |
| agent_007 | BE_KERNEL | Senior | FR | P1-P4 | 70 000 EUR | 101 500 EUR | 8 458 EUR |
| agent_008 | BE_AGENTS | Senior | FR | P1-P4 | 70 000 EUR | 101 500 EUR | 8 458 EUR |
| agent_009 | BE_API | Mid | FR | P1-P4 | 55 000 EUR | 79 750 EUR | 6 646 EUR |
| **PÔLE DEVOPS & INFRA** ||||||||
| agent_010 | DEVOPS | Senior | FR | P1-P4 | 70 000 EUR | 101 500 EUR | 8 458 EUR |
| **PÔLE ENGINEERING FRONTEND** ||||||||
| agent_011 | LEAD_FRONTEND | Senior | FR | P1-P4 | 75 000 EUR | 108 750 EUR | 9 063 EUR |
| agent_012 | FE_UI | Mid | FR | P1-P4 | 50 000 EUR | 72 500 EUR | 6 042 EUR |
| **PÔLE INTELLIGENCE ARTIFICIELLE** ||||||||
| agent_013 | LEAD_IA | Senior | FR | P1-P4 | 80 000 EUR | 116 000 EUR | 9 667 EUR |
| agent_014 | IA_NLP | Senior | FR | P1-P4 | 70 000 EUR | 101 500 EUR | 8 458 EUR |
| agent_015 | IA_SCORING | Senior | FR | P1-P4 | 70 000 EUR | 101 500 EUR | 8 458 EUR |
| agent_016 | IA_EMBEDDINGS | Mid | FR | P1-P4 | 55 000 EUR | 79 750 EUR | 6 646 EUR |
| **PÔLE VENTES FRANCE** ||||||||
| agent_017 | HEAD_SALES_FR | Head | FR | P2-P4 | 85 000 EUR | 123 250 EUR | 10 271 EUR |
| agent_018 | SDR_FR | Mid | FR | P2-P4 | 45 000 EUR | 65 250 EUR | 5 438 EUR |
| agent_019 | CSM_FR | Mid | FR | P2-P4 | 45 000 EUR | 65 250 EUR | 5 438 EUR |
| **PÔLE MARKETING** ||||||||
| agent_020 | HEAD_MARKETING | Head | FR | P2-P4 | 75 000 EUR | 108 750 EUR | 9 063 EUR |
| agent_021 | CONTENT_CREATOR | Mid | FR | P2-P4 | 40 000 EUR | 58 000 EUR | 4 833 EUR |
| **PÔLE SÉCURITÉ & CONFORMITÉ** ||||||||
| agent_022 | SEC_OFFICER | Senior | FR | P2-P4 | 70 000 EUR | 101 500 EUR | 8 458 EUR |
| agent_023 | DPO | Senior | FR | P2-P4 | 65 000 EUR | 94 250 EUR | 7 854 EUR |
| agent_027 | LEGAL_EU | Senior | FR | P3-P4 | 75 000 EUR | 108 750 EUR | 9 063 EUR |
| **PÔLE MAROC** ||||||||
| agent_024 | COUNTRY_MA | Head | MA | P3-P4 | 480 000 MAD (44 037 EUR) | 576 000 MAD (52 844 EUR) | 4 403 EUR |
| agent_025 | SALES_MA | Mid | MA | P3-P4 | 240 000 MAD (22 018 EUR) | 288 000 MAD (26 422 EUR) | 2 202 EUR |
| agent_026 | CSM_MA | Mid | MA | P3-P4 | 216 000 MAD (19 817 EUR) | 259 200 MAD (23 780 EUR) | 1 982 EUR |
| agent_028 | LEGAL_MA | Senior | MA | P3-P4 | 360 000 MAD (33 028 EUR) | 432 000 MAD (39 633 EUR) | 3 303 EUR |
| **PÔLE OPÉRATIONS** ||||||||
| agent_030 | OFFICE_MGR | Mid | FR | P3-P4 | 42 000 EUR | 60 900 EUR | 5 075 EUR |

---

## 6. Évolution mensuelle

### Graphique textuel : Masse salariale mensuelle (coût employeur chargé, EUR)

```
Masse salariale mensuelle (kEUR) - Coût employeur chargé

240 |                                          ┌─────┬─────┬─────┬─────┬─────┬─────┐
    |                                          │ P4  │ P4  │ P4  │ P4  │ P4  │ P4  │
237 |                                          │SCALE│SCALE│SCALE│SCALE│SCALE│SCALE│
    |                                          │ 30A │ 30A │ 30A │ 30A │ 30A │ 30A │
234 |                                          │     │     │     │     │     │     │
    |                                ┌─────────┘     │     │     │     │     │     │
231 |                                │  P3   P3   P3 │     │     │     │     │     │
    |                                │MULTI MULTI MULT│    │     │     │     │     │
228 |                                │ 30A   30A  30A │    │     │     │     │     │
    |                                │               │    │     │     │     │     │
225 |                                │               │    │     │     │     │     │
    |          ┌─────────────────────┘               │    │     │     │     │     │
222 |          │  P2           P2                    │    │     │     │     │     │
    |          │ V1.1         V1.1                   │    │     │     │     │     │
219 |          │ 23A          23A                    │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
216 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
213 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
210 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
207 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
204 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
201 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
198 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
195 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
192 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
189 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
186 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
183 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
180 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
177 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
174 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
171 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
168 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
165 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
162 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
159 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
156 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
153 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
150 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
147 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
144 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
141 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
138 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
135 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
132 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
129 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
126 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
123 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
120 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
117 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
114 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
111 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
108 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
105 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
102 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 99 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 96 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 93 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 90 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 87 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 84 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 81 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 78 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 75 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 72 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 69 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 66 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 63 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 60 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 57 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 54 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 51 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 48 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 45 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 42 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 39 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 36 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 33 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 30 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 27 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 24 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 21 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 18 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 15 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
 12 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
  9 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
  6 |          │                                     │    │     │     │     │     │
    |          │                                     │    │     │     │     │     │
  3 |          │                                     │    │     │     │     │     │
    | ┌────────┘                                     │    │     │     │     │     │
  0 └─┘ P1                                          └────┘     └─────┘     └─────┘
    M1     M2      M3      M4      M5      M6      M7      M8      M9     M10     M11     M12

148k    199k    199k    237k    237k    237k    237k    237k    237k    237k    237k    237k
```

### Table d'évolution mensuelle

| Mois | Phase | Effectif | Coût mensuel FR (EUR) | Coût mensuel MA (MAD) | Coût mensuel total (EUR eq.) | Cumul (EUR) |
|------|-------|----------|----------------------|----------------------|----------------------------|-------------|
| M1 | P1 | 16 | 148 021 | 0 | 148 021 | 148 021 |
| M2 | P2 | 23 | 199 375 | 0 | 199 375 | 347 396 |
| M3 | P2 | 23 | 199 375 | 0 | 199 375 | 546 771 |
| M4 | P3 | 30 | 225 596 | 129 600 | 237 486 | 784 257 |
| M5 | P3 | 30 | 225 596 | 129 600 | 237 486 | 1 021 743 |
| M6 | P3 | 30 | 225 596 | 129 600 | 237 486 | 1 259 228 |
| M7 | P4 | 30 | 225 596 | 129 600 | 237 486 | 1 496 714 |
| M8 | P4 | 30 | 225 596 | 129 600 | 237 486 | 1 734 200 |
| M9 | P4 | 30 | 225 596 | 129 600 | 237 486 | 1 971 686 |
| M10 | P4 | 30 | 225 596 | 129 600 | 237 486 | 2 209 171 |
| M11 | P4 | 30 | 225 596 | 129 600 | 237 486 | 2 446 657 |
| M12 | P4 | 30 | 225 596 | 129 600 | 237 486 | 2 684 143 |

---

## 7. Scénarios minimal vs complet

### Scénario Complet (30 agents, tel que décrit)

| Période | Effectif | Coût mensuel | Durée | Sous-total | Cumul |
|---------|----------|-------------|-------|-----------|-------|
| P1 MVP (M1) | 16 | 148 021 EUR | 1 mois | 148 021 EUR | 148 021 EUR |
| P2 V1.1 (M2-M3) | 23 | 199 375 EUR | 2 mois | 398 750 EUR | 546 771 EUR |
| P3 Multi-marché (M4-M6) | 30 | 237 486 EUR | 3 mois | 712 457 EUR | 1 259 228 EUR |
| P4 Scale (M7-M12) | 30 | 237 486 EUR | 6 mois | 1 424 914 EUR | 2 684 143 EUR |
| **Total Année 1** | | | **12 mois** | | **2 684 143 EUR** |

### Scénario Minimal (sans nice-to-have)

Le scénario minimal retarde ou supprime les postes non critiques pour réduire le burn-rate.

| Poste supprimé / retardé | Économie annuelle (chargé) | Commentaire |
|-------------------------|---------------------------|-------------|
| agent_021 CONTENT_CREATOR | 58 000 EUR | Content externalisable |
| agent_030 OFFICE_MGR | 60 900 EUR | Rôle administratif partageable |
| agent_028 LEGAL_MA | 39 633 EUR | Remplaçable par conseil extérieur |
| agent_026 CSM_MA | 23 780 EUR | CSM_FR peut couvrir initialement |
| **Sous-total économie** | **182 313 EUR eq.** | 4 postes sur 30 |

#### Scénario Minimal — ajustements de phasing

| Phase | Ajustement | Effectif min | Économie mensuelle | Économie sur la période |
|-------|-----------|-------------|-------------------|------------------------|
| P1 | Aucun (déjà minimal) | 16 | 0 | 0 |
| P2 | Pas de CONTENT_CREATOR | 22 | 4 833 EUR/mois | 9 667 EUR |
| P3 | Pas de OFFICE_MGR, LEGAL_MA, CSM_MA | 26 | 10 527 EUR/mois | 31 581 EUR |
| P4 | Idem P3 + pas de CONTENT_CREATOR | 26 | 15 360 EUR/mois | 92 158 EUR |
| **Total économie Année 1** | | | | **133 406 EUR** |

#### Scénario Minimal — coûts ajustés

| Période | Effectif min | Coût mensuel | Durée | Sous-total | Cumul ajusté |
|---------|-------------|-------------|-------|-----------|-------------|
| P1 MVP (M1) | 16 | 148 021 EUR | 1 mois | 148 021 EUR | 148 021 EUR |
| P2 V1.1 (M2-M3) | 22 | 194 542 EUR | 2 mois | 389 083 EUR | 537 104 EUR |
| P3 Multi-marché (M4-M6) | 26 | 226 959 EUR | 3 mois | 680 876 EUR | 1 217 980 EUR |
| P4 Scale (M7-M12) | 26 | 222 126 EUR | 6 mois | 1 332 756 EUR | 2 550 736 EUR |
| **Total Année 1 (minimal)** | | | | | **2 550 736 EUR** |

**Économie réalisée : 133 407 EUR (-5,0%)**

### Scénario Alternatif — Hybrid (recommandé)

Un scénario intermédiaire qui retarde plutôt que supprime :

| Poste | Stratégie | Impact |
|-------|----------|--------|
| CONTENT_CREATOR | P2 en freelance, P3 interne | -58k EUR en P2, normal en P3+ |
| OFFICE_MGR | Démarrage M6 (mi-P3) au lieu de M4 | -30k EUR sur 6 mois |
| LEGAL_MA | Conseil extérieur P3, interne P4+ | -40k EUR en P3 uniquement |
| CSM_MA | Report en P4 (M7) | -24k EUR en P3 uniquement |

**Économie Année 1 (hybrid) : ~100 000 EUR (-3,7%) avec flexibilité de rattrapage.**

---

## 8. Analyse et recommandations

### KPIs salariaux clés

| Indicateur | Valeur | Benchmark startup B2B SaaS |
|-----------|--------|---------------------------|
| Coût moyen par agent (P3-P4 chargé) | 79 161 EUR eq./an | 65-85k EUR (OK) |
| % masse salariale C-Level | 15,4% | 10-20% (OK) |
| % masse salariale Tech (P1 core) | 64,5% en P1 | 60-70% (OK) |
| Ratio Senior/Mid | 2,56:1 | 2:1 à 3:1 (OK) |
| Répartition France/Maroc (masse) | 95% / 5% | Potentiel d'optimisation |

### Recommandations stratégiques

1. **Optimisation Maroc** : Avec seulement 6% de la masse salariale en Maroc, le hub offshore est sous-utilisé. Envisager le transfert de certains postes Tech (BE_API, IA_EMBEDDINGS, FE_UI) au Maroc pour réduire les coûts de 30-40%.

2. **Content Creator** : En P2, privilégier le freelance/CM externe (économie ~50k EUR) tant que le volume de contenu ne justifie pas un poste dédié.

3. **Legal** : En P3, le poste LEGAL_MA peut être couvert par un cabinet d'avocats local en régie (facturation à l'acte) avant d'être internalisé en P4.

4. **Timing CFO** : Le démarrage du CFO en P3 (M4) est cohérent. En cas de levée de fonds anticipée, avancer ce recrutement en P2.

5. **Flexibilité P4** : La P4 ne prévoit pas de nouveau recrutement. Prévoir une enveloppe de 200k EUR pour des renforts ciblés (SRE, Data Engineer, Account Executive) selon la traction commerciale.

### Burn-rate salarial mensuel

| Période | Burn-rate mensuel | Runway avec 3M EUR |
|---------|------------------|-------------------|
| P1 | 148k EUR/mois | 20 mois |
| P2 | 199k EUR/mois | 15 mois |
| P3-P4 | 237k EUR/mois | 12,6 mois |
| **Moyenne année 1** | **224k EUR/mois** | **13,4 mois** |

---

## Annexes

### A. Conversion MAD → EUR

| Salaire MAD/an | Salaire EUR eq./an | Salaire MAD/mois | Salaire EUR eq./mois |
|---------------|-------------------|-----------------|---------------------|
| 480 000 | 44 037 | 40 000 | 3 670 |
| 360 000 | 33 028 | 30 000 | 2 752 |
| 240 000 | 22 018 | 20 000 | 1 835 |
| 216 000 | 19 817 | 18 000 | 1 652 |

### B. Glossaire

| Terme | Définition |
|-------|-----------|
| Brut | Salaire brut annuel avant déduction des charges |
| Chargé | Coût total employeur incluant toutes les charges patronales |
| C-Level | Direction générale (CEO, CTO, CFO, COO, CPO) |
| Head | Responsable de pôle (reporting C-Level) |
| Senior | Profil expérimenté (5-10 ans) |
| Mid | Profil intermédiaire (2-5 ans) |
| SDR | Sales Development Representative |
| CSM | Customer Success Manager |
| DPO | Data Protection Officer |
| CNSS | Caisse Nationale de Sécurité Sociale (Maroc) |

---

*Document produit le 17 juin 2025 - Version 1.0*
*Propriété : TAKA OS - Tous droits réservés*
