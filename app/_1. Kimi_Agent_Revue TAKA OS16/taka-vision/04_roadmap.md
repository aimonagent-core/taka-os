# Plan d'Intégration TAKA Vision v1.2
## Roadmap Sprints — Du Benchmark à la Production

> Document de planification projet pour l'intégration du module TAKA Vision dans TAKA OS v1.2.  
> Horizon : Mois 7-9 (Q3 2026).  
> Méthodologie : Sprints de 3 semaines avec milestone gates.

---

## 1. Vue d'ensemble du planning

```
2026 ──────────────────────────────────────────────────────────────►

Mois 6 (Juin)          Mois 7 (Juillet)       Mois 8 (Août)          Mois 9 (Sept)
   │                        │                      │                      │
   │  Sprint A               │  Sprint B            │  Sprint C            │  Sprint D
   │  (3 sem.)               │  (3 sem.)            │  (3 sem.)            │  (3 sem.)
   │                        │                      │                      │
   ├─ Benchmark 3 providers ├─ Abstraction Layer   ├─ Agent Depositor     ├─ Mémoire visuelle
   │  sur 3 portails réels   │  + 2 providers       │  + Humain au centre  │  + Séquences
   │                        │                      │                      │
   ├─ Définition séquences  ├─ API REST interne    ├─ L1/L2 validation    ├─ Optimisation
   │  types AO               │  + Sidecar Docker    │  + Dashboard         │  + Perf
   │                        │                      │                      │
   ├─ Sélection provider    ├─ Sécurité V1         ├─ Audit trail V1      ├─ Documentation
   │  par défaut             │  (chiffrement)       │  visuel              │  + Formation
   │                        │                      │                      │
   ▼                        ▼                      ▼                      ▼
Milestone A                Milestone B            Milestone C            Milestone D
"Portails validés"         "Infra prête"          "Agent fonctionnel"    "Production-ready"

Release : TAKA OS v1.2 — Fin Mois 9 (Freeze code Mois 8.3)
```

---

## 2. Sprint A — Benchmark des Providers sur Portails Réels

**Durée** : 3 semaines (Mois 7, semaines 1-3)  
**Objectif** : Valider empiriquement les choix de providers sur des portails d'appels d'offres réels.  
**Équipe** : 1 ML engineer + 1 backend engineer + 1 QA

### Livrables

| # | Livrable | Description | Critère d'acceptation |
|---|----------|-------------|----------------------|
| A1 | Matrice benchmark portails | Évaluation de Holo-1 7B, UI-TARS 7B, Qwen3 VL sur 3 portails | Document technique validé |
| A2 | Corpus screenshots anonymisé | 500+ screenshots par portail (train/test) | Stocké dans S3 interne chiffré |
| A3 | Rapport de sélection provider | Recommandation provider par défaut + chaîne fallback | Approbation tech lead |
| A4 | Spécification séquences types | Inventaire des 20 séquences visuelles les plus fréquentes | Review architecte |

### Portails cibles

| Portail | Type | Complexité UI | Fréquence AO PME |
|---------|------|--------------|------------------|
| **BOAMP** (boamp.fr) | Public | Moyenne (formulaires longs) | Haute |
| **Place** (marches-publics.gouv.fr) | Public | Élevée (multi-étapes, auth complexe) | Haute |
| **Achat Public** (achatpublic.com) | Privé | Moyenne (portail marketplace) | Moyenne |

### Tâches détaillées — Sprint A

```
Semaine 1 : Collecte & Anonymisation
├── J1-2 : Accès et configuration environnement test (VM isolée, VPN si nécessaire)
├── J3-4 : Capture screenshots sur parcours complets (connexion → recherche → dépôt)
├── J5 : Anonymisation corpus (pipeline regex + revue manuelle échantillon)

Semaine 2 : Benchmark Automatisé
├── J1-2 : Déploiement Holo-1 7B (vLLM) + UI-TARS 7B (vLLM) sur GPU cloud
├── J3-4 : Script benchmark standardisé (localisation 50 éléments + navigation 10 parcours)
├── J5 : Intégration Qwen3 VL via API (navigation + OCR)

Semaine 3 : Analyse & Recommandation
├── J1-2 : Scoring + analyse erreurs (faux positifs, faux négatifs, timeouts)
├── J3-4 : Rédaction rapport + présentation milestone
├── J5 : Revue milestone A → Go/No-Go Sprint B
```

### Milestone A — Critères de sortie

| Critère | Seuil | Validation |
|---------|-------|------------|
| Holo-1 7B : succès navigation BOAMP | ≥ 85% | Test scripté 10 parcours |
| UI-TARS 7B : précision localisation | ≥ 90% | ScreenSpot-like interne |
| Qwen3 VL : OCR document | ≥ 95% accuracy | 50 documents multilingues |
| Corpus anonymisé | 0 PII détecté (échantillon 10%) | Audit regex + manuel |
| Décision provider | Document signé | Tech lead + PO |

> **Gate** : Si Holo-1 7B < 80% sur BOAMP, réévaluer chaîne fallback (prioriser UI-TARS ou Qwen3).

---

## 3. Sprint B — Abstraction Layer + Infrastructure

**Durée** : 3 semaines (Mois 7.3 — Mois 8.1)  
**Objectif** : Implémenter la couche d'abstraction provider-agnostique et l'infrastructure sidecar.  
**Équipe** : 2 backend engineers + 1 DevOps

### Livrables

| # | Livrable | Description | Critère d'acceptation |
|---|----------|-------------|----------------------|
| B1 | `VLAProvider` ABC + implémentations | HoloProvider + QwenProvider + FallbackProvider | Tests unitaires ≥ 90% coverage |
| B2 | API REST TAKA Vision | 6 endpoints (/localize, /navigate, /extract, /validate, /batch, /status) | Contract OpenAPI validé |
| B3 | Sidecar Docker | Conteneur vLLM pour Holo-1 7B + UI-TARS 7B | Déploiement < 5 min |
| B4 | File d'attente Redis | Pub/sub async avec retry + fallback | Load test 100 tâches/min |
| B5 | Cache screenshots | Redis TTL 1h + chiffrement AES-GCM | Penetration test interne |
| B6 | Sécurité V1 | Vault credentials + anonymisation regex | Audit sécurité passé |

### Architecture livrée à la fin du Sprint B

```
TAKA Vision Infrastructure (Milestone B)
├── taka-vision-controller (FastAPI, port 8080)
│   ├── /v1/vision/* (6 endpoints)
│   ├── ProviderRegistry (Holo, Qwen, UI-TARS, Gemma)
│   ├── TaskQueue (Redis Streams)
│   ├── ScreenshotCache (Redis + AES-GCM)
│   └── SecretManager (Vault interface)
├── sidecar-holo-7b (Docker, vLLM, port 8001)
│   └── Modèle : Holo1.5-7B (GGUF ou FP16)
├── sidecar-uitars-7b (Docker, vLLM, port 8002)
│   └── Modèle : UI-TARS-1.5-7B
├── sidecar-gemma-4b (Docker, llama.cpp, port 8003)
│   └── Modèle : Gemma 3 4B (CPU fallback)
└── redis-cluster (cache + queue)
```

### Tâches détaillées — Sprint B

```
Semaine 1 : Abstraction Layer
├── J1-2 : Implémentation VLAProvider ABC + dataclasses
├── J3-4 : HoloProvider (prompt Surfer-H, parsing JSON, health check)
├── J5 : QwenProvider (API Dashscope, format prompt Qwen3-VL)

Semaine 2 : API + Queue + Cache
├── J1-2 : FastAPI controller + 6 endpoints + validation Pydantic
├── J3-4 : Redis Streams (producer/consumer) + retry logic
├── J5 : Cache Redis (clé sha256, chiffrement, TTL, anonymisation)

Semaine 3 : Sécurité + Intégration TAKA
├── J1-2 : SecretManager (Vault interface + file provider)
├── J3-4 : Anonymisation pipeline (regex + revue) + tests
├── J5 : Intégration Layer 1 TAKA OS (sensorimoteur) + revue milestone
```

### Milestone B — Critères de sortie

| Critère | Seuil | Validation |
|---------|-------|------------|
| Coverage tests | ≥ 90% | pytest --cov |
| Latence API / localize | ≤ 2000 ms (p95) | Load test k6 |
| Fallback automatique | Fonctionnel A → B → C | Test injection panne |
| Chiffrement cache | AES-256-GCM, clés par tenant | Audit crypto interne |
| Anonymisation | 0 PII dans cache (échantillon) | Scan regex |
| Déploiement sidecar | < 5 min `docker compose up` | Test fresh VM |

---

## 4. Sprint C — Agent Depositor + Mode Humain au Centre

**Durée** : 3 semaines (Mois 8.1 — Mois 8.3)  
**Objectif** : Créer l'Agent Depositor et implémenter les 3 niveaux de validation humaine.  
**Équipe** : 2 backend engineers + 1 frontend engineer + 1 UX designer

### Livrables

| # | Livrable | Description | Critère d'acceptation |
|---|----------|-------------|----------------------|
| C1 | Agent Depositor (Layer 3) | Agent orchestrant navigation + formulaire + upload + validation | Tests E2E 10 parcours complets |
| C2 | Mode L0 (autonome) | Exécution sans validation pour tâches routine | 100% autonome sur parcours validés |
| C3 | Mode L1 (supervisé) | Pause + notification pour données sensibles | Temps réponse humaine < 2 min (test) |
| C4 | Mode L2 (bloquant) | Confirmation biométrique/token pour actions critiques | Impossible de bypass |
| C5 | Dashboard TAKA UI | Vue temps réel des tâches visuelles + file d'attente | UX validée par 3 testeurs |
| C6 | Audit trail V1 | Log visuel immutable dans Layer 5 | Export JSON signé valide |

### Parcours Agent Depositor ( livré Sprint C )

```
Agent Depositor — Séquence type "Déposer AO sur BOAMP"

Étape 1 : Récupération séquence mémorisée (Layer 2)
    └─ Si existe et confiance > 0.90 → exécution L0 (autonome)
    └─ Sinon → inférence VLA (Holo-1 7B)

Étape 2 : Navigation web (boucle VLA)
    ├─ Screenshot → TAKA Vision /navigate → NextAction
    ├─ Exécution action (click / type / scroll)
    ├─ Validation résultat (TAKA Vision /validate)
    └─ Retry / fallback si échec

Étape 3 : Remplissage formulaire
    ├─ OCR champ (Qwen3 fallback si Holo échoue)
    ├─ Saisie valeur (TypeAction)
    └─ Validation par champ

Étape 4 : Upload documents
    ├─ Localisation zone drag-and-drop
    ├─ Simulation drop fichier
    └─ Vérification confirmation upload

Étape 5 : Validation finale
    ├─ Récapitulatif visuel (before/after)
    ├─ Si L1 requis → notification humaine
    ├─ Si L2 requis → token 2FA
    └─ Confirmation ou correction

Étape 6 : Archivage
    ├─ Séquence réussie → Layer 2 (mémorisation)
    ├─ Audit trail → Layer 5 (log signé)
    └─ Notification tenant (email/Slack)
```

### Tâches détaillées — Sprint C

```
Semaine 1 : Agent Depositor Core
├── J1-2 : Définition états (finite state machine) + transitions
├── J3-4 : Implémentation boucle navigate + fallback
├── J5 : Intégration formulaire (OCR + saisie séquentielle)

Semaine 2 : Validation Humaine + Dashboard
├── J1-2 : Implémentation L0/L1/L2 (règles configurables)
├── J3-4 : Dashboard TAKA UI (Vue React : tâches en cours, file, historique)
├── J5 : Système notification (SSE push, email, webhook Slack)

Semaine 3 : Audit + E2E
├── J1-2 : Audit trail visuel (screenshot + action + signature)
├── J3-4 : Tests E2E (10 parcours complets sur 3 portails)
├── J5 : Revue milestone C → Go/No-Go Sprint D
```

### Milestone C — Critères de sortie

| Critère | Seuil | Validation |
|---------|-------|------------|
| Parcours complet BOAMP (L0) | ≥ 8/10 succès | Test E2E automatisé |
| Temps parcours moyen | ≤ 10 min | Chronométrage E2E |
| Latence L1 (humain notifié) | ≤ 5s (push) | Test notification |
| Dashboard UX | Score SUS ≥ 70 | Test utilisateur |
| Audit trail complet | 100% des actions loggées | Vérification DB |
| Bypass L2 impossible | 0 bypass sur 100 tentatives | Test sécurité |

---

## 5. Sprint D — Mémoire Visuelle + Optimisation Production

**Durée** : 3 semaines (Mois 8.3 — Mois 9.3)  
**Objectif** : Capitaliser les séquences, optimiser les performances, documenter, former.  
**Équipe** : 1 backend engineer + 1 ML engineer + 1 technical writer

### Livrables

| # | Livrable | Description | Critère d'acceptation |
|---|----------|-------------|----------------------|
| D1 | Mémoire visuelle (Layer 2) | Stockage + retrieval séquences réussies | 20 séquences types stockées |
| D2 | Apprentissage séquences | Auto-update séquences après succès/échec | Taux adaptation > 80% |
| D3 | Optimisation latence | Cache + batching + warm-up modèles | p95 < 1000 ms (localise) |
| D4 | Documentation | Guide admin + Guide développeur + API reference | Review technique |
| D5 | Formation | Session 2h pour équipes support + premiers clients | Quiz passé > 80% |
| D6 | Release v1.2 | Tag git + CHANGELOG + migration guide | CI/CD green |

### Format mémoire visuelle (livré D1)

```json
{
  "sequence_version": "2.1",
  "platform_id": "boamp-fr",
  "task_type": "deposer_ao",
  "steps": [
    {"order": 1, "action": "navigate", "url": "https://www.boamp.fr/"},
    {"order": 2, "action": "click", "element_label": "Connexion", "bbox": [0.82, 0.04, 0.91, 0.09], "confidence": 0.94},
    {"order": 3, "action": "type", "element_label": "SIRET", "bbox": [0.25, 0.35, 0.75, 0.40], "value_ref": "{{tenant.siret}}"},
    {"order": 4, "action": "click", "element_label": "Se connecter", "bbox": [0.40, 0.55, 0.60, 0.62], "confidence": 0.91},
    {"order": 5, "action": "click", "element_label": "Déposer un dossier", "bbox": [0.35, 0.60, 0.65, 0.68], "confidence": 0.88}
  ],
  "success_rate": 0.93,
  "last_success": "2026-09-01T10:23:00Z",
  "total_executions": 47,
  "failure_count": 3,
  "auto_updated": true
}
```

### Tâches détaillées — Sprint D

```
Semaine 1 : Mémoire + Learning
├── J1-2 : CRUD séquences (Layer 2) + indexation platform_id + task_type
├── J3-4 : Auto-update séquences (ajustement bbox après échec réussi)
├── J5 : Matching fuzzy séquences (platform_id similaire = suggestion)

Semaine 2 : Performance + Robustesse
├── J1-2 : Warm-up modèles (keep-alive) + batching inférences
├── J3-4 : Stress test (50 tenants × 10 tâches/min)
├── J5 : Optimisation Docker (layers, cache, GPU sharing)

Semaine 3 : Documentation + Release
├── J1-2 : Rédaction docs (admin + dev + API reference)
├── J3-4 : Session formation interne + matériel client
├── J5 : Release v1.2 (tag, changelog, migration guide, annonce)
```

### Milestone D — Critères de sortie

| Critère | Seuil | Validation |
|---------|-------|------------|
| Séquences mémorisées | ≥ 20 types | Inventaire validé |
| Réutilisation séquences | ≥ 60% des tâches | Métriques Layer 2 |
| Latence p95 / localize | ≤ 1000 ms | Load test k6 |
| Latence p95 / navigate | ≤ 2000 ms | Load test k6 |
| Uptime sidecar GPU | ≥ 99.5% (7 jours) | Monitoring Prometheus |
| Documentation complète | 3 guides publiés | Review tech writer |
| Formation équipe | ≥ 5 personnes formées | Attestations |

---

## 6. Matrice de risques

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Holo-1 7B indisponible (licence) | Faible | Élevé | Chaîne fallback UI-TARS + Qwen3 + Gemma |
| Changement UI portail (breaking) | Élevée | Moyen | Séquences versionnées + détection auto + alerte |
| Latence > 2s sur navigation | Moyenne | Moyen | Cache + warm-up + batching + provider MoE (Holo3) |
| Fuite PII dans screenshots | Faible | Critique | Anonymisation obligatoire + audit regex + chiffrement |
| Échec validation humaine L1/L2 | Moyenne | Moyen | Timeout configurable + escalation manager + log complet |
| Scalabilité > 100 tenants | Faible | Moyen | Architecture stateless + Redis cluster + GPU pool |
| Performance GPU cloud instable | Moyenne | Moyen | Monitoring + auto-restart + fallback Gemma CPU |

---

## 7. KPIs de suivi

| KPI | Baseline (v1.1) | Objectif v1.2 | Mesure |
|-----|-------------------|---------------|--------|
| Temps moyen dépôt AO | 45 min (manuel) | 10 min (agent) | E2E chronométrage |
| Taux succès navigation | N/A | ≥ 90% | Tests E2E |
| Coût inference / AO | N/A | ≤ $0.10 | Metering TAKA |
| Taux utilisation séquences | 0% | ≥ 60% | Métriques Layer 2 |
| Temps réponse humaine L1 | N/A | ≤ 2 min | Logs notification |
| Satisfaction utilisateur | N/A | ≥ 7/10 | NPS mensuel |
| Incidents sécurité | 0 | 0 | Audit trimestriel |

---

## 8. Dépendances externes

| Dépendance | Fournisseur | Statut | Impact si retard |
|------------|-------------|--------|------------------|
| Holo1.5-7B weights | HuggingFace / Qwen Research | Disponible | Critique (provider principal) |
| UI-TARS-1.5-7B weights | HuggingFace / ByteDance | Disponible | Moyen (fallback) |
| Qwen3 VL API | Alibaba Cloud | À valider | Moyen (fallback OCR) |
| GPU cloud (A10G / RTX) | OVH / Scaleway / AWS | Disponible | Critique (infra sidecar) |
| Redis 7.2+ | Redis Labs / self-host | Disponible | Faible |

---

*Fin du document. TAKA Vision v1.2 — Spécification complète. Prochaine étape : Revue architecture + Kick-off Sprint A.*
