# TAKA OS — Bible Maîtresse
## Du MVP Graine à la Cathédrale v2.0 | Plan de développement intégral avec Kimi Code & Swarms Agentic
### Version : GO-2026-05-03 | CEO : Toi | CTO : Swarm Coordinateur

---

# MANIFESTE

> **"Nous ne construisons pas un outil. Nous construisons un OS agentic qui grandira avec ses utilisateurs. Le MVP v0.1 est la graine. La cathédrale v2.0 est l'arbre. Chaque version est une étape de croissance — jamais une destination finale."**

**Philosophie de développement :**
- **Parcimonie** : on n'ajoute que ce qui est strictement nécessaire à chaque version
- **Validation marché** : chaque version doit prouver qu'elle résout un problème réel
- **Reconstruction progressive** : on reintègre les couches de la vision originale une par une
- **CEO au centre** : chaque version est validée par toi avant passage à la suivante
- **CTO coordinateur** : les swarms agentic produisent, je coordonne, tu décides

---

# PARTIE I — ARCHITECTURE ÉVOLUTIVE (v0.1 → v2.0)

## 1.1 Vision Finale : La Cathédrale v2.0 (Mois 12)

```
┌─────────────────────────────────────────────────────────────────┐
│ COUCHE 5 : MÉTACOGNITION                                       │
│ ├─ Self-Model : TAKA se représente lui-même                    │
│ ├─ TAKA LAB : Auto-ajustement scoring, génération règles      │
│ ├─ Governance Engine : Règles métier, kill switch             │
│ └─ Monitor : Supervision temps réel, alertes anomalies          │
├─────────────────────────────────────────────────────────────────┤
│ COUCHE 4 : DÉLIBÉRATION                                         │
│ ├─ Parlement : 5+ agents votent sur décisions sensibles         │
│ ├─ Vote : Majoritaire / Borda / Consensus                        │
│ ├─ Minority Report : Dissidences enregistrées                   │
│ └─ Transcript : Journal immuable de chaque délibération         │
├─────────────────────────────────────────────────────────────────┤
│ COUCHE 3 : AGENTS                                               │
│ ├─ Registry : CRUD dynamique, découverte capabilities           │
│ ├─ 10+ agents spécialisés (extractor, coder, controller,        │
│ │   reporter, writer, auditor, compliance, sales, support)     │
│ ├─ CrewAI Bridge : Équipes d'agents collaboratifs             │
│ ├─ Hermès Bridge : Runtime agentic bas niveau                   │
│ └─ Status : idle / busy / debating / learning                 │
├─────────────────────────────────────────────────────────────────┤
│ COUCHE 2 : MÉMOIRE (4 types)                                   │
│ ├─ Épisodique : Qdrant / pgvector — souvenirs candidatures      │
│ ├─ Sémantique : Neo4j — graphe connaissances CPV/métier        │
│ ├─ Transactionnelle : PostgreSQL — états, logs, audit         │
│ ├─ Procédurale : YAML + DB — SOPs, checklists, séquences      │
│ └─ Unified API + Oubli sélectif (importance, TTL, recency)    │
├─────────────────────────────────────────────────────────────────┤
│ COUCHE 1 : SENSORIMOTRICE                                       │
│ ├─ Connecteurs : Peppol BIS 3.0, MyPeopleDoc, EBICS,          │
│ │   Email IMAP/SMTP, CRM générique, API bancaires, BOAMP, TED  │
│ ├─ Parseurs : PDF (tableaux/lignes), XML UBL, OCR, CSV         │
│ ├─ TAKA Vision : Holo-1 7B / UI-TARS / Qwen3 — action visuelle │
│ └─ Actionners : Email sender, Webhook, API POST, dépôt visuel  │
├─────────────────────────────────────────────────────────────────┤
│ KERNEL TAKA                                                       │
│ ├─ Event Bus : Redis / NATS (distribué)                         │
│ ├─ Scheduler : Celery (distribué)                              │
│ ├─ RBAC : 3 rôles + permissions granulaires                    │
│ ├─ Multi-tenancy : Row-level security PostgreSQL                 │
│ ├─ Vault : Coffre-fort credentials chiffré                       │
│ └─ Audit : Append-only, hash chain SHA-256                     │
└─────────────────────────────────────────────────────────────────┘
```

## 1.2 Architecture par Version (Évolution Visuelle)

### v0.1 — Cabane (Mois 1) : 3 couches
```
Couche 3 : Agents (3 codés en dur)
  Sourcer | Qualifieur | Tracker
Couche 2 : Mémoire (1 type)
  PostgreSQL + pgvector
Couche 1 : Sensorimotrice
  Upload PDF manuel
Kernel : EventBus asyncio in-memory
```
**Objectif :** Prouver que la qualification AO assistée par IA a un marché.

### v0.2 — Cabane + Cheminée (Mois 2) : 3 couches + connecteurs
```
Couche 3 : Agents (3)
Couche 2 : Mémoire (1)
Couche 1 : Sensorimotrice + CONNECTEURS API
  Upload PDF + BOAMP API + TED + e-marchespublics
```
**Objectif :** Automatiser la veille (plus d'upload manuel).

### v0.3 — Maison (Mois 2-3) : 4 couches
```
Couche 4 : DÉLIBÉRATION (nouveau)
  Parlement : 3 agents votent
  Vote majoritaire
  Transcript immuable
Couche 3 : Agents (3)
Couche 2 : Mémoire (1)
Couche 1 : Sensorimotrice + Connecteurs
Kernel : + Vault (coffre-fort credentials)
```
**Objectif :** Démocratie agentic + sécurité credentials.

### v0.4 — Maison + Étage (Mois 3) : 4 couches + métacognition
```
Couche 4 : Délibération
Couche 3 : Agents (3)
Couche 2 : Mémoire (1)
Couche 1 : Sensorimotrice + Connecteurs
Kernel : + Vault
PLUS : TAKA LAB (métacognition lite)
  Auto-ajustement scoring
  Génération règles depuis logs
```
**Objectif :** TAKA apprend tout seul.

### v0.5 — Immeuble RDC (Mois 3-4) : 4 couches + registry
```
Couche 4 : Délibération
Couche 3 : Agents + REGISTRY (nouveau)
  CRUD dynamique
  5+ agents spécialisés
  Capabilities (Pydantic)
Couche 2 : Mémoire (1)
Couche 1 : Sensorimotrice + Connecteurs
Kernel : + Vault
PLUS : TAKA LAB
```
**Objectif :** Diversité agentic — TAKA n'est plus un outil mono-tâche.

### v1.0 — Immeuble (Mois 4-5) : 4 couches + distribué
```
Couche 4 : Délibération
Couche 3 : Agents + Registry (5+)
Couche 2 : Mémoire (1)
Couche 1 : Sensorimotrice + Connecteurs
Kernel : EventBus REDIS/NATS (distribué)
  + Celery Scheduler (distribué)
  + Multi-tenancy RLS PostgreSQL
  + Vault
PLUS : TAKA LAB
```
**Objectif :** Scalabilité — 100+ clients.

### v1.1 — Immeuble + Ascenseur (Mois 5-6) : 5 couches (sémantique)
```
Couche 5 : Métacognition (TAKA LAB complet)
Couche 4 : Délibération
Couche 3 : Agents + Registry (5+)
Couche 2 : Mémoire ÉPISODIQUE + SÉMANTIQUE (nouveau)
  Neo4j graphe connaissances
Couche 1 : Sensorimotrice + Connecteurs
Kernel : Distribué + Vault
```
**Objectif :** Relations complexes CPV/métier/sous-traitants.

### v1.2 — Palais (Mois 6-8) : 5 couches + vision
```
Couche 5 : Métacognition
Couche 4 : Délibération
Couche 3 : Agents + Registry (5+)
Couche 2 : Mémoire (2 types)
Couche 1 : Sensorimotrice + Connecteurs + TAKA VISION (nouveau)
  Holo-1 7B / UI-TARS / Qwen3
  Action visuelle portails AO
Kernel : Distribué + Vault
```
**Objectif :** Dépôt AO automatique — killer feature.

### v1.3-v1.4 — Palais + Ailes (Mois 8-10) : Connecteurs métier + Hermès
```
+ Connecteurs métier : Peppol, MyPeopleDoc, EBICS, CRM
+ Hermès Runtime : Abstraction agentic profonde
+ Mémoire PROCÉDURALE : SOPs, checklists YAML
```
**Objectif :** Intégration écosystème comptable/bancaire.

### v2.0 — Cathédrale (Mois 10-12) : 5 couches complètes
```
Couche 5 : Métacognition COMPLET
  Self-Model | TAKA LAB | Governance | Kill Switch | Monitor
Couche 4 : Délibération COMPLET
  Parlement | Vote | Consensus | Minority Report | Transcript
Couche 3 : Agents COMPLET
  Registry | 10+ agents | CrewAI | Hermès | Capabilities
Couche 2 : Mémoire COMPLET (4 types)
  Épisodique | Sémantique (Neo4j) | Transactionnelle | Procédurale
  + Oubli sélectif (importance, TTL, recency)
Couche 1 : Sensorimotrice COMPLET
  Connecteurs (10+) | Parseurs (4 niveaux) | TAKA Vision
  Actionners (email, webhook, API, dépôt visuel)
Kernel COMPLET
  EventBus distribué | Scheduler distribué | RBAC granulaire
  Multi-tenancy RLS | Vault | Audit append-only
```
**Objectif :** Vision originale NEXA-MIND réalisée — mais avec 12 mois de feedback client.

---

# PARTIE II — ROADMAP DÉTAILLÉE (v0.1 → v2.0)

## 2.1 v0.1 — Cabane (Semaines 1-4, Mois 1)

### Objectif
Prouver que la qualification AO assistée par IA a un marché.

### Démo client
> "Uploadez un DCE PDF. En 5 secondes, TAKA vous dit GO, NO-GO ou MAYBE."

### Livrables
| # | Fichier | Description |
|---|---------|-------------|
| 1 | `pyproject.toml` | Poetry, Python 3.12+ |
| 2 | `app/config.py` | Pydantic-Settings |
| 3 | `app/models/ao.py` | 8 tables SQLAlchemy 2.0 |
| 4 | `app/database.py` | Engine async, expire_on_commit=False |
| 5 | `app/kernel/bus.py` | EventBus asyncio |
| 6 | `app/kernel/security.py` | JWT, bcrypt |
| 7 | `app/kernel/auth.py` | Dev-login + login réel |
| 8 | `app/api/v1/endpoints/auth.py` | POST /auth/dev-login, /auth/login |
| 9 | `app/api/v1/endpoints/health.py` | GET /health |
| 10 | `app/api/v1/endpoints/tenders.py` | CRUD AO + filtres |
| 11 | `app/api/v1/endpoints/pipeline_stages.py` | GET /pipeline-stages |
| 12 | `app/services/pipeline.py` | 8 stages par défaut |
| 13 | `app/services/parsing/pypdf_parser.py` | Extraction texte simple |
| 14 | `app/services/parsing/pdfplumber_parser.py` | Extraction tableaux |
| 15 | `app/services/parsing/pipeline.py` | Orchestrateur parsing |
| 16 | `app/services/qualification/rules_engine.py` | Scoring règles 80% |
| 17 | `app/services/qualification/qualifier.py` | GO/NO-GO/MAYBE |
| 18 | `app/services/llm/client.py` | MistralLLMClient |
| 19 | `app/services/tracker/alerter.py` | Alertes deadlines |
| 20 | `frontend/src/pages/Dashboard.tsx` | KPIs |
| 21 | `frontend/src/pages/TendersList.tsx` | Table AO |
| 22 | `frontend/src/pages/TenderDetail.tsx` | Fiche détail |
| 23 | `frontend/src/pages/KanbanBoard.tsx` | Pipeline drag-drop |
| 24 | `frontend/src/pages/Upload.tsx` | Zone drop |
| 25 | `docker-compose.yml` | PostgreSQL + App |
| 26 | `README.md` | Quickstart 5 minutes |

### Tests
- 30+ tests unitaires + intégration
- Taux parsing CPV : 80%
- Taux parsing montant : 70%
- Taux parsing deadline : 75%

### KPIs succès
| Métrique | Cible |
|----------|-------|
| Parsing réussi (CPV) | ≥80% |
| Scoring règles (aucun LLM) | ≥80% |
| Temps qualification | <5s |
| Tests verts | 100% |

### Checkpoint CEO
**Tu valides :** "L'outil qualifie correctement un DCE PDF que je lui donne."

---

## 2.2 v0.2 — Cabane + Cheminée (Semaines 5-8, Mois 2)

### Objectif
Automatiser la veille — plus d'upload manuel.

### Démo client
> "TAKA surveille BOAMP pour vous. Quand un AO correspond à vos règles, il apparaît dans votre liste."

### Nouveaux livrables
| # | Feature | Description |
|---|---------|-------------|
| 1 | **Connecteur BOAMP** | Scraping/API (API disponible ?) des annonces |
| 2 | **Connecteur TED** | Tenders Electronic Daily (UE) |
| 3 | **Connecteur e-marchespublics** | Scraping + parsing |
| 4 | **Agent Sourcer (upgrade)** | Polling automatique 6h/12h/24h |
| 5 | **Alertes nouveaux AO** | Email "Nouvel AO détecté" |
| 6 | **Filtres avancés** | CPV, montant, région, deadline |

### Stack ajoutée
- `requests` / `httpx` pour polling
- `APScheduler` pour cron jobs
- `beautifulsoup4` / `scrapy` pour scraping

### Tests
- 15+ tests connecteurs
- Mock des réponses API
- Tests offline

### KPIs succès
| Métrique | Cible |
|----------|-------|
| AO détectés/jour | ≥10 (moyenne France) |
| Faux positifs | <20% |
| Latence détection | <6h |

### Checkpoint CEO
**Tu valides :** "Je reçois un email quand un nouveau AO correspond à mes règles."

---

## 2.3 v0.3 — Maison (Semaines 9-12, Mois 2-3)

### Objectif
Démocratie agentic — les agents débattent avant de décider.

### Démo client
> "3 agents analysent cet AO. Ils votent. Vous voyez le débat et la décision finale."

### Nouveaux livrables
| # | Feature | Description |
|---|---------|-------------|
| 1 | **Parlement (Couche 4)** | 3 agents votent sur scoring |
| 2 | **Agent Auditor** | Vérifie la cohérence du scoring |
| 3 | **Agent Compliance** | Vérifie la conformité réglementaire |
| 4 | **Vote majoritaire** | 2/3 = décision |
| 5 | **Minority Report** | Dissidence enregistrée si 1 agent contre |
| 6 | **Transcript** | Journal immuable de chaque délibération |
| 7 | **Vault** | Coffre-fort credentials chiffré (simplifié) |
| 8 | **Toggle Parlement** | ON/OFF par tenant |

### Stack ajoutée
- Table `deliberations` (PostgreSQL)
- Table `votes` (PostgreSQL)
- Module `app/services/parliament/`
- Module `app/services/vault/`

### Tests
- 20+ tests délibération
- Test vote 2/3
- Test minority report
- Test toggle

### KPIs succès
| Métrique | Cible |
|----------|-------|
| Décision Parlement == Décision solo | ≥90% (cohérence) |
| Minority report déclenché | <10% (pas de blocage) |
| Temps délibération | <30s |

### Checkpoint CEO
**Tu valides :** "Les 3 agents débattent d'un AO et je vois qui a voté quoi."

---

## 2.4 v0.4 — Maison + Étage (Semaines 13-16, Mois 3-4)

### Objectif
TAKA apprend tout seul — auto-ajustement du scoring.

### Démo client
> "TAKA a remarqué que vous gagnez 80% des AO CPV 45233200. Il a augmenté le poids de ce CPV."

### Nouveaux livrables
| # | Feature | Description |
|---|---------|-------------|
| 1 | **TAKA LAB** | Analyse hebdomadaire des logs de scoring |
| 2 | **Auto-ajustement poids** | Pondération CPV ajustée selon résultats |
| 3 | **Détection biais** | Alerte si score systématiquement faux |
| 4 | **Suggestion règles** | "Ajouter CPV X ?" proposé à l'utilisateur |
| 5 | **Dashboard Learning** | Graphiques : taux de gain par CPV, par montant |

### Stack ajoutée
- Table `learning_logs` (PostgreSQL)
- Module `app/services/taka_lab/`
- Algorithmie statistique simple (pandas)

### Tests
- 15+ tests TAKA LAB
- Test auto-ajustement
- Test détection biais

### KPIs succès
| Métrique | Cible |
|----------|-------|
| Précision scoring (post-ajustement) | +10% vs v0.3 |
| Suggestions règles acceptées | ≥50% |
| Biais détectés/corrigés | ≥80% |

### Checkpoint CEO
**Tu valides :** "TAKA m'a suggéré d'ajuster mes règles et c'était pertinent."

---

## 2.5 v0.5 — Immeuble RDC (Semaines 17-20, Mois 4-5)

### Objectif
Diversité agentic — TAKA n'est plus un outil mono-tâche.

### Démo client
> "TAKA a 5 agents maintenant. Celui qui parse, celui qui qualifie, celui qui écrit, celui qui vérifie, celui qui relance."

### Nouveaux livrables
| # | Feature | Description |
|---|---------|-------------|
| 1 | **Agent Registry** | CRUD dynamique des agents |
| 2 | **Agent Writer** | Copilote rédaction mémoire technique (RAG mémoires) |
| 3 | **Agent Reporter** | Analytics, exports, rapports |
| 4 | **Agent Controller** | Validation qualité avant action |
| 5 | **Capabilities** | Pydantic schemas par agent |
| 6 | **CrewAI minimal** | Équipes d'agents pour tâches complexes |

### Stack ajoutée
- Table `agents_registry` (PostgreSQL)
- Module `app/services/registry/`
- `crewai` (minimal, pas de full framework)

### Tests
- 20+ tests registry
- Test équipe agents
- Test capabilities

### KPIs succès
| Métrique | Cible |
|----------|-------|
| Agents actifs | ≥5 |
| Tâches complexes résolues | ≥80% |
| Latence équipe agents | <10s |

### Checkpoint CEO
**Tu valides :** "Je peux voir les 5 agents de TAKA et leur statut en temps réel."

---

## 2.6 v1.0 — Immeuble (Semaines 21-24, Mois 5-6)

### Objectif
Scalabilité — 100+ clients.

### Dévo client
> "TAKA gère 100 PME sans ralentir. Chaque PME voit seulement ses données."

### Nouveaux livrables
| # | Feature | Description |
|---|---------|-------------|
| 1 | **Event Bus Redis/NATS** | Distribué, multi-instance |
| 2 | **Scheduler Celery** | Tâches distribuées, retry, monitoring |
| 3 | **Multi-tenancy RLS** | Row-Level Security PostgreSQL |
| 4 | **Rate limiting avancé** | Par tenant, par endpoint |
| 5 | **Caching Redis** | Cache API, cache embeddings |
| 6 | **Load balancing** | Nginx upstream multiple instances |

### Stack ajoutée
- `redis` (EventBus + cache)
- `celery[redis]` (scheduler)
- `nats-py` (alternative EventBus)
- Nginx config upgrade

### Infra upgrade
- VPS : CX31 → CPX31 (4 vCPU / 8GB → 8 vCPU / 16GB)
- Ou : 2× CX31 avec load balancer

### Tests
- 15+ tests distribué
- Test charge (100 req/s)
- Test isolation multi-tenant

### KPIs succès
| Métrique | Cible |
|----------|-------|
| Clients actifs | ≥100 |
| Latence p95 | <500ms |
| Uptime | ≥99.5% |
| Isolation multi-tenant | 100% (0 fuite) |

### Checkpoint CEO
**Tu valides :** "100 clients utilisent TAKA en simultané sans ralentir."

---

## 2.7 v1.1 — Immeuble + Ascenseur (Semaines 25-28, Mois 6-7)

### Objectif
Mémoire sémantique — relations complexes.

### Démo client
> "TAKA sait que CPV 45233200 (Travaux bâtiment) est lié à 45233210 (Gros oeuvre) et 45233220 (Second oeuvre)."

### Nouveaux livrables
| # | Feature | Description |
|---|---------|-------------|
| 1 | **Neo4j graphe** | CPV, métiers, sous-traitants, relations |
| 2 | **Unified Memory API** | pgvector (épisodique) + Neo4j (sémantique) |
| 3 | **Recherche hybride** | Similarité vectorielle + graphe relations |
| 4 | **Inférence relation** | "Vous avez gagné des AO similaires à..." |

### Stack ajoutée
- `neo4j` (graphe)
- `neo4j-python-driver`
- Docker Compose + service neo4j

### Tests
- 15+ tests graphe
- Test recherche hybride
- Test inférence

### KPIs succès
| Métrique | Cible |
|----------|-------|
| Relations CPV découvertes | ≥1000 |
| Précision inférence | ≥80% |
| Temps recherche hybride | <100ms |

### Checkpoint CEO
**Tu valides :** "TAKA me suggère des AO parce qu'il comprend les relations entre métiers."

---

## 2.8 v1.2 — Palais (Semaines 29-36, Mois 7-9)

### Objectif
TAKA Vision — action visuelle, dépôt AO automatique.

### Démo client
> "TAKA ouvre le portail BOAMP, remplit le formulaire, télécharge votre mémoire technique, et clique sur 'Soumettre'. Vous validez."

### Nouveaux livrables
| # | Feature | Description |
|---|---------|-------------|
| 1 | **TAKA Vision Module** | Sidecar Docker VLA |
| 2 | **HoloProvider** | Holo1.5-7B (Apache 2.0) — navigation web |
| 3 | **UI_TARSProvider** | UI-TARS-1.5-7B — localisation pixel |
| 4 | **QwenProvider** | Qwen3 VL — OCR multilingue |
| 5 | **GemmaProvider** | Gemma 3 4B — edge/CPU fallback |
| 6 | **Agent Depositor** | Orchestration dépôt visuel |
| 7 | **Mode humain au centre** | Validation obligatoire clic sensibles |
| 8 | **Audit trail visuel** | Screenshot + action + résultat |

### Stack ajoutée
- `docker-compose.yml` + service `taka-vision`
- `httpx` + API interne `/v1/vision/*`
- GPU optionnel (ou CPU INT8)

### Infra upgrade
- VPS GPU optionnel : Hetzner GPU (€50-100/mois)
- Ou : API H Company cloud

### Tests
- 25+ tests vision
- Test dépôt simulé
- Test fallback providers
- Test sécurité credentials

### KPIs succès
| Métrique | Cible |
|----------|-------|
| Taux réussite dépôt visuel | ≥85% |
| Temps dépôt (humain inclus) | <5 min |
| Fallback provider activé | <15% |
| Fuite données (audit) | 0 |

### Checkpoint CEO
**Tu valides :** "TAKA a déposé un AO pour moi sur un portail. J'ai validé chaque étape."

---

## 2.9 v1.3-v1.4 — Palais + Ailes (Semaines 37-44, Mois 9-10)

### Objectif
Intégration écosystème comptable/bancaire.

### Démo client
> "TAKA a récupéré le bon de commande dans Peppol, créé la facture dans Sage, et relancé le paiement."

### Nouveaux livrables
| # | Feature | Description |
|---|---------|-------------|
| 1 | **Connecteur Peppol** | EDI BIS 3.0 — facturation électronique |
| 2 | **Connecteur MyPeopleDoc** | Portail fournisseurs |
| 3 | **Connecteur EBICS** | Virement bancaire automatique |
| 4 | **Connecteur CRM générique** | HubSpot, Pipedrive, Salesforce |
| 5 | **Hermès Runtime** | Abstraction agentic bas niveau |
| 6 | **Mémoire procédurale** | SOPs YAML — "Comment répondre à un DC1" |
| 7 | **Oubli sélectif** | Importance, TTL, recency weight |

### Stack ajoutée
- `peppol` (lib EDI)
- `ebics` (lib bancaire)
- `hermes-runtime` (module Python)
- `pyyaml` (SOPs)

### Tests
- 20+ tests connecteurs métier
- Test EDI
- Test SOPs

### KPIs succès
| Métrique | Cible |
|----------|-------|
| Connecteurs métier actifs | ≥5 |
| Documents EDI traités/jour | ≥50 |
| SOPs exécutés sans erreur | ≥95% |

### Checkpoint CEO
**Tu valides :** "TAKA gère la facturation et le paiement sans que j'intervienne."

---

## 2.10 v2.0 — Cathédrale (Semaines 45-52, Mois 10-12)

### Objectif
Vision originale NEXA-MIND réalisée — avec 12 mois de feedback client.

### Démo client
> "TAKA est votre OS agentic complet. Il sait ce que vous faites, apprend de vos succès, débat avec ses agents, et agit sur n'importe quelle interface."

### Nouveaux livrables
| # | Feature | Description |
|---|---------|-------------|
| 1 | **Self-Model** | TAKA se représente lui-même (capacités, limites, préférences) |
| 2 | **Governance Engine** | Règles métier granulaires, kill switch |
| 3 | **Monitor** | Supervision temps réel, alertes anomalies |
| 4 | **Consensus** | Vote Borda, pas seulement majoritaire |
| 5 | **10+ agents** | Extractor, Coder, Controller, Reporter, Writer, Auditor, Compliance, Sales, Support, Researcher |
| 6 | **CrewAI complet** | Équipes d'agents pour projets complexes |
| 7 | **Hermès complet** | Runtime agentic bas niveau |
| 8 | **Mémoire complète** | 4 types + oubli sélectif |
| 9 | **Sensorimotrice complète** | 10+ connecteurs + TAKA Vision + actionners |

### Stack finale
- PostgreSQL + pgvector + Neo4j + Redis + Qdrant (optionnel)
- FastAPI + SQLAlchemy 2.0 + Celery + Redis EventBus
- React + Vite + Tailwind + Zustand
- Holo-1 7B + UI-TARS + Qwen3 + Gemma 3

### Tests
- 100+ tests (unitaires, intégration, E2E)
- Pentest annuel
- Audit conformité AI Act

### KPIs succès
| Métrique | Cible |
|----------|-------|
| Clients actifs | ≥500 |
| MRR | ≥25 000€ |
| Taux rétention annuel | ≥80% |
| NPS | ≥50 |
| Agents actifs | ≥10 |
| Couverture connecteurs | ≥10 |
| Temps dépôt AO complet | <10 min (vs 2h manuel) |

### Checkpoint CEO
**Tu valides :** "TAKA est devenu l'OS agentic que j'imaginais il y a 12 mois. Il vaut 10× plus que le MVP."

---

# PARTIE III — CAHIER DES CHARGES DÉTAILLÉ PAR VERSION

## 3.1 CDC v0.1 — Cabane (Détaillé)

### 3.1.1 Backend

#### Configuration
- **Fichier** : `app/config.py`
- **Classe** : `Settings(BaseSettings)`
- **Préfixe** : `TAKA_OS_`
- **Variables** : DB_URL, JWT_SECRET, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES (15), JWT_REFRESH_TOKEN_EXPIRE_DAYS (7), MISTRAL_API_KEY, MISTRAL_MODEL, LLM_TIMEOUT (30), LLM_MAX_RETRIES (3), UPLOAD_MAX_SIZE_MB (50), ALLOWED_MIME_TYPES, FRONTEND_URL

#### Base de données
- **Fichier** : `app/models/ao.py`
- **Tables** : tenants, users, pipeline_stages, tenders, tender_documents, memory_vectors, audit_logs, qualification_rules
- **Index** : tenant_id sur toutes les tables, deadline_submission sur tenders, email sur users (unique per tenant)
- **Contraintes** : FK avec ondelete, CHECK (role IN ('admin', 'manager', 'viewer')), CHECK (qualification_result IN ('GO', 'NO-GO', 'MAYBE', NULL))

#### Kernel
- **EventBus** : InMemoryEventBus (asyncio.Lock), publish/subscribe, persistance DB
- **Security** : JWT encode/decode (python-jose[cryptography]), bcrypt hash (cost 12), password verify
- **Auth** : Dev login (pas de password check, retourne JWT), Login réel (bcrypt verify)

#### API
- **Router** : `/api/v1` avec prefix
- **Endpoints** : 28+ endpoints (voir Partie IV CDC Technique)
- **Documentation** : Swagger UI auto (/docs)

#### Services
- **Pipeline** : create_default_pipeline_stages() idempotent
- **Parsing** : Pipeline 4 niveaux (pypdf → pdfplumber → OCR → LLM)
- **Qualification** : RulesEngine (80%) + LLM fallback (20%) → GO/NO-GO/MAYBE
- **LLM Client** : MistralLLMClient, circuit breaker, retry 3x exponentiel, timeout 30s
- **Tracker** : APScheduler, alertes J-30/14/7/3/1

### 3.1.2 Frontend

#### Pages (9)
1. **Login** : Email + password + dev login + "Mot de passe oublié" (P2)
2. **Dashboard** : KPI cards (AO actifs, deadlines 7j, taux GO), graphique pipeline, table AO récents
3. **Liste AO** : Table filtrable (search, stage, qualification, deadline), pagination, boutons Nouvel AO + Upload
4. **Fiche AO** : Onglets Détails / Documents / Qualification / Historique
5. **Kanban** : 8 colonnes drag-drop (DndKit), cards avec badges
6. **Upload** : Zone drop, progression, résultat parsing, correction champs extraits
7. **Mémoire** : Recherche texte, résultats similarité, tags
8. **Paramètres** : Profil, règles qualif, stages pipeline, users (admin)
9. **Audit** : Table filtrable logs, export CSV/PDF (admin)

#### Composants (25+)
- Layout, Sidebar, Header, MobileNav
- TenderCard, TenderTable, TenderForm, TenderFilters
- PipelineBoard, PipelineColumn, SortableTenderCard
- QualificationBadge, QualificationResult, QualificationTrigger, QualificationPanel
- DocumentList, FileUploadZone
- KPICard, DeadlineBadge, SearchBar, DataTable, StatusBadge
- ConfirmDialog, EmptyState, LoadingSkeleton
- AIBadge, AIActDisclaimer, HumanValidation

#### State (Zustand)
- authStore, tenderStore, pipelineStore, uiStore

### 3.1.3 DevOps

#### Docker Compose
- **Services** : db (ankane/pgvector:pg15), app (FastAPI + Uvicorn), web (Nginx reverse proxy)
- **Healthchecks** : pg_isready (5s interval), /health (app), nginx stub_status
- **Restart** : unless-stopped

#### Nginx
- Reverse proxy /api → app:8000
- Servir frontend buildé /
- SSL Let's Encrypt (Certbot)
- Rate limiting 100 req/min
- Compression gzip
- Headers sécurité (HSTS, X-Frame-Options, CSP)

### 3.1.4 Tests
- **Backend** : pytest + pytest-asyncio + TestClient
- **Frontend** : Vitest + React Testing Library
- **E2E** : Playwright (5 scénarios critiques)
- **Couverture** : ≥80% backend, ≥60% frontend

### 3.1.5 Sécurité
- JWT 15min + refresh 7j + rotation
- RBAC 3 rôles (viewer/manager/admin)
- Multi-tenancy row-level filtering
- Audit trail append-only + hash chain
- Rate limiting sliding window
- File upload : MIME validation, magic bytes, 50MB max
- SQL injection : SQLAlchemy 2.0 parameterized queries
- XSS : Content-Type JSON strict
- CSRF : SameSite Strict cookies

---

## 3.2 CDC v0.2 — Connecteurs (Mois 2)

### Nouveaux modules

#### Connecteur BOAMP
- **Polling** : Toutes les 6h (configurable)
- **Parsing** : XML BOAMP → Tender
- **Filtres** : CPV, montant, région, deadline
- **Alertes** : Email "Nouvel AO détecté"

#### Connecteur TED
- **API** : Tenders Electronic Daily (REST)
- **Parsing** : XML TED → Tender

#### Connecteur e-marchespublics
- **Scraping** : BeautifulSoup / Scrapy
- **Parsing** : HTML → Tender
- **Résilience** : Retry 3x, backoff exponentiel

### Tests
- Mock des réponses API
- Tests offline
- Tests résilience (API down)

---

## 3.3 CDC v0.3 — Parlement (Mois 2-3)

### Nouveaux modules

#### Parlement
- **Table** : `deliberations` (id, tender_id, status, created_at)
- **Table** : `votes` (id, deliberation_id, agent_name, vote, justification)
- **Agents votants** : Agent Auditor, Agent Compliance, Agent Qualifieur
- **Règles vote** : 2/3 = décision, timeout 30s
- **Minority Report** : Enregistré si 1 agent contre
- **Transcript** : JSON immuable stocké

#### Vault
- **Table** : `credentials` (id, tenant_id, service, encrypted_data)
- **Chiffrement** : Fernet (symétrique) ou AES-256
- **Accès** : Seulement agents autorisés

### Tests
- Test vote 2/3
- Test timeout
- Test minority report
- Test chiffrement/déchiffrement

---

## 3.4 CDC v0.4 — TAKA LAB (Mois 3-4)

### Nouveaux modules

#### TAKA LAB
- **Table** : `learning_logs` (id, tenant_id, tender_id, action, result, timestamp)
- **Analyse** : Hebdomadaire (pandas)
- **Auto-ajustement** : Pondération CPV ajustée selon taux de gain
- **Détection biais** : Écart-type des scores > seuil = alerte
- **Suggestion** : "Ajouter CPV X ?" (top 5 CPV gagnants non dans whitelist)

#### Dashboard Learning
- Graphiques : taux gain par CPV, par montant, par deadline
- Table : suggestions règles avec bouton "Accepter"

### Tests
- Test auto-ajustement
- Test détection biais
- Test suggestion

---

## 3.5 CDC v0.5 — Registry (Mois 4-5)

### Nouveaux modules

#### Agent Registry
- **Table** : `agents_registry` (id, tenant_id, name, slug, capabilities, status, config)
- **CRUD** : Create, Read, Update, Delete, Activate, Deactivate
- **Discovery** : GET /agents → liste capabilities

#### 5+ agents spécialisés
- **Agent Writer** : Copilote rédaction (RAG mémoires procéduraux)
- **Agent Reporter** : Analytics, exports CSV/PDF
- **Agent Controller** : Validation qualité avant action
- **Agent Auditor** : Vérification cohérence (existe déjà en v0.3)
- **Agent Compliance** : Vérification réglementaire (existe déjà en v0.3)

#### CrewAI minimal
- Équipe "Qualification" : Qualifieur + Auditor + Compliance
- Équipe "Dépôt" : Writer + Controller + Depositor (v1.2)
- Orchestration simple (pas full CrewAI framework)

### Tests
- Test CRUD registry
- Test équipe agents
- Test capabilities

---

## 3.6 CDC v1.0 — Scalabilité (Mois 5-6)

### Nouveaux modules

#### Event Bus Redis
- **Service** : Redis (pub/sub)
- **Remplacement** : InMemoryEventBus → RedisEventBus
- **Avantage** : Multi-instance, persistance, monitoring

#### Scheduler Celery
- **Service** : Celery + Redis broker
- **Remplacement** : APScheduler local → Celery distribué
- **Avantage** : Retry, monitoring (Flower), scale

#### Multi-tenancy RLS
- **PostgreSQL** : Row-Level Security policies
- **Avantage** : Isolation garantie au niveau DB (pas juste app)

#### Caching Redis
- **Cache** : API responses, embeddings, sessions
- **TTL** : Configurable par type

### Infra
- 2× VPS CX31 + load balancer Nginx
- Ou 1× CPX31 (8 vCPU / 16GB)

### Tests
- Test charge (k6 / locust)
- Test isolation multi-tenant
- Test failover

---

## 3.7 CDC v1.1 — Neo4j (Mois 6-7)

### Nouveaux modules

#### Neo4j Graphe
- **Service** : Neo4j Community (Docker)
- **Nodes** : CPV, Métier, Sous-traitant, Acheteur, AO
- **Relations** : :IS_RELATED_TO, :HAS_WON, :HAS_LOST, :SUBCONTRACTS

#### Unified Memory API
- **Interface** : `MemoryManager`
- **Méthodes** : store_episodic(), store_semantic(), search_hybrid(), forget()

#### Recherche hybride
- Étape 1 : Recherche pgvector (similarité)
- Étape 2 : Recherche Neo4j (relations)
- Étape 3 : Fusion résultats (ranking combiné)

### Tests
- Test graphe
- Test recherche hybride
- Test inférence

---

## 3.8 CDC v1.2 — TAKA Vision (Mois 7-9)

### Nouveaux modules

#### TAKA Vision (Sidecar Docker)
- **Service** : `taka-vision` (Docker)
- **API** : `/v1/vision/localize`, `/navigate`, `/extract`, `/validate`
- **Providers** : HoloProvider, QwenProvider, UI_TARSProvider, GemmaProvider
- **Fallback** : Holo → Qwen3 → UI-TARS → Gemma3 → Humain

#### Agent Depositor
- **Mission** : Déposer AO sur portail via TAKA Vision
- **Séquence** : Connexion → Navigation → Upload → Validation → Soumission
- **Mode** : L1 (humain valide chaque clic) / L2 (humain valide à la fin) / L3 (autonome avec supervision)

#### Sécurité VLA
- Coffre-fort credentials chiffré
- Screenshots anonymisés (masquage champs sensibles)
- Audit trail visuel (screenshot + action + résultat)
- Rétention 30j max

### Infra
- GPU optionnel : Hetzner GPU instance
- Ou : API H Company cloud

### Tests
- Test dépôt simulé (portail de test)
- Test fallback providers
- Test sécurité credentials

---

## 3.9 CDC v1.3-v1.4 — Connecteurs Métier (Mois 9-10)

### Nouveaux modules

#### Connecteurs
- **Peppol** : EDI BIS 3.0 (lib `peppol`)
- **MyPeopleDoc** : API REST (OAuth2)
- **EBICS** : Virement automatique (lib `ebics`)
- **CRM** : HubSpot, Pipedrive, Salesforce (API REST)

#### Hermès Runtime
- **Module** : `app/services/hermes/`
- **Rôle** : Abstraction agentic bas niveau
- **Interface** : `AgentRuntime` (start, stop, pause, resume)

#### Mémoire Procédurale
- **Format** : YAML (SOPs)
- **Stockage** : `procedures/` (repo) + DB (index)
- **Exemple** : `sop_depot_boamp.yaml` — étape par étape

#### Oubli Sélectif
- **Importance** : Score 0-1 (manuel ou auto)
- **TTL** : Time-to-live configurable
- **Recency** : Poids décroissant avec le temps

### Tests
- Test EDI
- Test EBICS (sandbox)
- Test SOPs
- Test oubli

---

## 3.10 CDC v2.0 — Cathédrale (Mois 10-12)

### Nouveaux modules

#### Métacognition Complète
- **Self-Model** : `app/services/self_model/` — représentation interne
- **Governance Engine** : Règles métier, kill switch, limites
- **Monitor** : Supervision temps réel, alertes anomalies

#### Délibération Complète
- **Consensus** : Vote Borda (pondéré)
- **10+ agents** : Extractor, Coder, Controller, Reporter, Writer, Auditor, Compliance, Sales, Support, Researcher
- **CrewAI complet** : Équipes dynamiques pour projets complexes

#### Mémoire Complète
- **4 types** : Épisodique, Sémantique, Transactionnelle, Procédurale
- **Oubli sélectif** : Importance + TTL + recency

#### Sensorimotrice Complète
- **10+ connecteurs** : BOAMP, TED, Peppol, MyPeopleDoc, EBICS, CRM, Email, TAKA Vision
- **Parseurs** : PDF 4 niveaux, XML UBL, OCR, CSV
- **Actionners** : Email, Webhook, API POST, dépôt visuel

### Tests
- 100+ tests
- Pentest annuel
- Audit conformité AI Act

---

# PARTIE IV — WORKFLOW DE DÉVELOPPEMENT

## 4.1 Processus Global

```
CEO (Toi)
    │
    ├──► Décision version N (GO / AJUSTE / STOP)
    │
    ├──► Brief fonctionnel (priorités, démo, KPIs)
    │
    └──► Validation livrable version N (tests, démo, retours)
         │
         ├──► GO version N+1
         ├──► AJUSTE (retour au développement)
         └──► STOP (projet en pause)

CTO (Swarm Coordinateur)
    │
    ├──► Rédige prompts Kimi Code (Sprint par Sprint)
    │
    ├──► Coordination swarms agentic (Ingénieur Prompt, Relecteur, Testeur)
    │
    ├──► Audit code produit (checklist qualité)
    │
    └──► Rapport CEO (livrable, risques, recommandation GO/NO-GO)

Kimi Code
    │
    ├──► Lit prompt Sprint
    │
    ├──► Génère code (fichier par fichier)
    │
    ├──► Commit + push
    │
    └──► Signale fin Sprint

Swarms Agentic
    ├──► Ingénieur Prompt : rédige les prompts
    ├──► Architecte Backend : valide architecture
    ├──► Architecte Frontend : valide composants
    ├──► Relecteur Code : review PR
    ├──► Testeur : écrit et exécute tests
    └──► Documentateur : met à jour README/docs
```

## 4.2 Rôles des Swarms Agentic

| Rôle | Agent | Mission | Quand |
|------|-------|---------|-------|
| **Ingénieur Prompt** | agent_prompt | Rédige les prompts Kimi Code Sprint par Sprint | Avant chaque Sprint |
| **Architecte Backend** | agent_archi_be | Valide modèles, API, patterns | Après chaque Sprint backend |
| **Architecte Frontend** | agent_archi_fe | Valide composants, state, design | Après chaque Sprint frontend |
| **Relecteur Code** | agent_reviewer | Review PR (style, sécurité, perf) | Après chaque commit |
| **Testeur** | agent_tester | Écrit tests, exécute, rapporte couverture | Après chaque Sprint |
| **Documentateur** | agent_docs | Met à jour README, API docs, guides | Après chaque version |
| **Auditeur Sécurité** | agent_sec | Audit sécurité, pentest léger | Avant chaque version majeure |
| **Release Manager** | agent_release | Tag, changelog, release notes | Avant chaque version |

## 4.3 Cycle de Sprint (1 semaine)

| Jour | Action | Qui |
|------|--------|-----|
| Lundi | Brief CEO → CTO (priorités, ajustements) | CEO |
| Lundi | CTO rédige prompt Sprint N | CTO |
| Mardi | Kimi Code reçoit prompt, commence développement | Kimi Code |
| Mardi-Jeudi | Kimi Code génère code, commit, push | Kimi Code |
| Jeudi | Swarms agentic review (relecteur + testeur) | Swarms |
| Vendredi | CTO audit code, checklist qualité | CTO |
| Vendredi | Rapport CEO : livrable, tests, risques | CTO |
| Samedi | CEO teste, donne retours | CEO |
| Dimanche | Décision : GO / AJUSTE / STOP | CEO |

## 4.4 Checklist Qualité CTO (par Sprint)

### Backend
- [ ] `expire_on_commit=False` présent
- [ ] Un seul fichier `app/models/ao.py`
- [ ] Python <3.14
- [ ] SQLAlchemy 2.0 async uniquement (pas de Query)
- [ ] Tests verts (pytest)
- [ ] Coverage ≥80%
- [ ] Pas de fuite données cross-tenant
- [ ] Circuit breaker LLM testé
- [ ] Audit log append-only

### Frontend
- [ ] TypeScript strict (no any)
- [ ] Composants shadcn/ui utilisés
- [ ] Responsive testé (mobile)
- [ ] Zustand stores testés
- [ ] Axios intercepteurs JWT
- [ ] Pas de secrets dans le code

### DevOps
- [ ] Docker Compose démarre en 1 commande
- [ ] Healthcheck passant
- [ ] README quickstart testé
- [ ] Seed script fonctionnel

## 4.5 Gestion des Retours CEO

| Type de retour | Action | Délais |
|----------------|--------|--------|
| **GO** | Passer au Sprint suivant | Immédiat |
| **AJUSTE mineur** (bug, style) | Fix dans Sprint courant | 1-2 jours |
| **AJUSTE majeur** (architecture, feature manquante) | Retour au prompt, nouveau Sprint | 1 semaine |
| **STOP** | Pause projet, réunion stratégique | Immédiat |

---

# PARTIE V — STACK ÉVOLUTIF

## 5.1 Ce qui reste constant (toutes versions)

| Élément | Technologie | Pourquoi |
|---------|-------------|----------|
| Langage | Python 3.12+ | Stable, LTS |
| Framework | FastAPI | Performant, async, auto-docs |
| ORM | SQLAlchemy 2.0 async | Mature, type-safe |
| Base principale | PostgreSQL 15+ | Transactionnelle, fiable |
| Auth | JWT maison | Contrôle total |
| Frontend | React 18 + TypeScript | Écosystème mature |
| Styling | Tailwind CSS | Utility-first, maintenable |
| Package | Poetry | Reproductible |
| Test backend | pytest + pytest-asyncio | Standard Python |
| Licence | MIT | Open source |

## 5.2 Ce qui évolue version par version

| Version | Ajout | Retrait/Modification |
|---------|-------|---------------------|
| v0.1 | PostgreSQL + pgvector | — |
| v0.2 | requests, beautifulsoup4 | — |
| v0.3 | Tables deliberations, votes, vault | — |
| v0.4 | pandas (TAKA LAB) | — |
| v0.5 | crewai (minimal) | — |
| v1.0 | redis, celery, nats-py | EventBus in-memory → Redis |
| v1.1 | neo4j-python-driver | — |
| v1.2 | httpx (déjà là), sidecar Docker | — |
| v1.3 | peppol, ebics, pyyaml | — |
| v2.0 | — | (stack stable) |

## 5.3 Infra par Version

| Version | VPS | Services Docker | Coût/mois |
|---------|-----|----------------|-----------|
| v0.1 | Hetzner CX31 (4vCPU/8GB) | db + app + web | 8.50€ |
| v0.2-v0.5 | CX31 | db + app + web | 8.50€ |
| v1.0 | CPX31 (8vCPU/16GB) ou 2×CX31 | db + app + web + redis | 14.70€ ou 17€ |
| v1.1 | CPX31 + storage | + neo4j | 20€ |
| v1.2 | CPX31 + GPU optionnel | + taka-vision | 20-70€ |
| v1.3-v2.0 | CPX41 (16vCPU/32GB) | + services métier | 35-50€ |

---

# PARTIE VI — MÉTRIQUES & CHECKPOINTS

## 6.1 KPIs par Version

| Version | KPI principal | Cible | Seuil GO | Seuil STOP |
|---------|--------------|-------|----------|------------|
| v0.1 | Parsing CPV réussi | ≥80% | ≥75% | <60% |
| v0.1 | Scoring règles | ≥80% | ≥75% | <60% |
| v0.2 | AO détectés/jour | ≥10 | ≥5 | <3 |
| v0.3 | Décisions Parlement cohérentes | ≥90% | ≥85% | <70% |
| v0.4 | Précision post-TAKA LAB | +10% | +5% | 0% |
| v0.5 | Agents actifs | ≥5 | ≥3 | <2 |
| v1.0 | Clients actifs | ≥100 | ≥50 | <20 |
| v1.1 | Relations graphe découvertes | ≥1000 | ≥500 | <200 |
| v1.2 | Dépôt visuel réussi | ≥85% | ≥75% | <60% |
| v1.3 | Connecteurs métier actifs | ≥5 | ≥3 | <2 |
| v2.0 | MRR | ≥25K€ | ≥15K€ | <5K€ |
| v2.0 | Clients | ≥500 | ≥200 | <50 |

## 6.2 Points de GO/NO-GO entre Versions

| Transition | Question CEO | Seuil GO | Seuil NO-GO |
|------------|-----------|----------|-------------|
| v0.1 → v0.2 | "Le parsing et scoring fonctionnent-ils sur 5 vrais DCE ?" | 4/5 OK | <3/5 |
| v0.2 → v0.3 | "Les connecteurs détectent-ils des AO réels ?" | ≥5 AO/semaine | <3 |
| v0.3 → v0.4 | "Le Parlement améliore-t-il les décisions ?" | NPS >30 | NPS <0 |
| v0.4 → v0.5 | "TAKA LAB suggère-t-il des règles pertinentes ?" | ≥50% acceptées | <20% |
| v0.5 → v1.0 | "Les clients paient-ils et restent-ils ?" | 10 clients, churn <10% | <5 clients |
| v1.0 → v1.1 | "La scalabilité tient-elle la charge ?" | 100 clients, p95 <500ms | >1s |
| v1.1 → v1.2 | "Le graphe apporte-t-il de la valeur ?" | NPS >40 | NPS <10 |
| v1.2 → v1.3 | "Le dépôt visuel fonctionne-t-il ?" | ≥3 dépôts réussis | 0 |
| v1.3 → v2.0 | "L'écosystème comptable est-il utile ?" | ≥5 connexions actives | <2 |

---

# PARTIE VII — RISQUES & MITIGATIONS (12 mois)

| # | Risque | Probabilité | Impact | Mitigation | Version concernée |
|---|--------|------------|--------|------------|------------------|
| 1 | Parsing PDF échoue | Moyenne | Élevé | Pipeline 4 niveaux + fallback | v0.1 |
| 2 | Timeout LLM Mistral | Moyenne | Élevé | Circuit breaker + retry + règles | v0.1 |
| 3 | SQLAlchemy async errors | Faible | Élevé | expire_on_commit=False | v0.1 |
| 4 | Concurrence Tenderbolt/Nextend | Moyenne | Moyen | Open source + prix 10× inférieur | v0.1-v1.0 |
| 5 | Parlement bloque décisions | Moyenne | Moyen | Timeout 30s + mode solo fallback | v0.3 |
| 6 | TAKA LAB biaisé | Moyenne | Moyen | Détection biais + humain valide | v0.4 |
| 7 | Scalabilité insuffisante | Faible | Élevé | Redis + Celery + RLS | v1.0 |
| 8 | TAKA Vision échoue (8%) | Moyenne | Élevé | Fallback 4 providers + humain | v1.2 |
| 9 | Licences VLA restrictives | Moyenne | Élevé | Holo1.5-7B Apache 2.0 uniquement | v1.2 |
| 10 | Coût infra dépasse revenus | Faible | Élevé | Facturation usage GPU | v1.2 |
| 11 | Connecteurs métier fragiles | Moyenne | Moyen | Fallback API + saisie manuelle | v1.3 |
| 12 | Complexité v2.0 inmaintenable | Faible | Élevé | Tests 100+ + documentation + modulaire | v2.0 |

---

# PARTIE VIII — GLOSSAIRE & RÉFÉRENCES

## Glossaire

| Terme | Définition |
|-------|-----------|
| **AO** | Appel d'Offres — consultation publique |
| **DCE** | Dossier de Consultation des Entreprises |
| **CPV** | Common Procurement Vocabulary — classification EU |
| **GO/NO-GO** | Décision candidature |
| **VLA** | Vision-Language-Action — modèle IA qui voit et agit |
| **TAKA LAB** | Module auto-amélioration par apprentissage |
| **Parlement** | Délibération multi-agents avec vote |
| **Registry** | Catalogue dynamique des agents |
| **RLS** | Row-Level Security — isolation DB |
| **TTL** | Time-To-Live — durée de vie données |

## Références

| Document | Chemin | Description |
|----------|--------|-------------|
| Bible Maîtresse | `/mnt/agents/output/Bible_TAKA_OS_Maitresse.md` | Ce document |
| Blueprint Technique | `/mnt/agents/output/blueprint_taka_os_v1.md` | 14 977 lignes |
| Prompt Sprint 0 | `/mnt/agents/output/prompts/sprint_0_fondation.md` | 2 513 lignes |
| Prompt Sprint 1 | `/mnt/agents/output/prompts/sprint_1_sensorimotrice_memoire.md` | 3 846 lignes |
| Prompt Sprint 2 | `/mnt/agents/output/prompts/sprint_2_qualifieur_kanban.md` | 4 323 lignes |
| Prompt Sprint 3 | `/mnt/agents/output/prompts/sprint_3_tracker_saas.md` | 5 478 lignes |
| Équipe Agentique | `/mnt/agents/output/taka-team/` | 30 agents |
| TAKA Vision | `/mnt/agents/output/taka-vision/` | Module VLA |
| Analyse Holo-1 | `/mnt/agents/output/Analyse_Holo1_TAKA_OS.docx` | Stratégie VLA |

---

# ANNEXE A — COMMANDES DE LANCEMENT MVP (v0.1)

```bash
# 1. Clone
git clone https://github.com/taka-os/taka-os.git && cd taka-os

# 2. Config
cp .env.template .env
# Éditer .env avec vos valeurs

# 3. Lancer
docker-compose up -d

# 4. Migrations
docker-compose exec app alembic upgrade head

# 5. Seed
docker-compose exec app python scripts/seed_dev.py

# 6. Accès
# API : http://localhost:8000/docs
# Frontend : http://localhost:3000
# Health : http://localhost:8000/health
```

---

# ANNEXE B — STRUCTURE DU REPO (v0.1 → v2.0)

```
taka-os/
├── .env
├── .env.template
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── alembic.ini
├── README.md
├── LICENSE
├── CONTRIBUTING.md
│
├── alembic/
│   └── versions/
│       └── 001_create_all_tables.py
│
├── scripts/
│   ├── seed_dev.py
│   └── seed_prod.py
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── exceptions.py
│   ├── database.py
│   ├── models/
│   │   └── ao.py              # 8 tables
│   ├── schemas/               # Pydantic v2
│   │   ├── tenant.py
│   │   ├── user.py
│   │   ├── tender.py
│   │   ├── document.py
│   │   ├── qualification.py
│   │   └── memory.py
│   ├── api/
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py
│   │       └── endpoints/
│   │           ├── auth.py
│   │           ├── health.py
│   │           ├── tenders.py
│   │           ├── documents.py
│   │           ├── pipeline_stages.py
│   │           ├── qualification.py
│   │           ├── memory.py
│   │           ├── alerts.py
│   │           └── admin.py
│   ├── services/
│   │   ├── pipeline.py
│   │   ├── parsing/
│   │   │   ├── base_parser.py
│   │   │   ├── pypdf_parser.py
│   │   │   ├── pdfplumber_parser.py
│   │   │   ├── ocr_parser.py
│   │   │   ├── llm_parser.py
│   │   │   ├── pipeline.py
│   │   │   ├── extractors.py
│   │   │   ├── constants.py
│   │   │   └── worker.py
│   │   ├── qualification/
│   │   │   ├── rules_engine.py
│   │   │   ├── llm_scorer.py
│   │   │   └── qualifier.py
│   │   ├── tracker/
│   │   │   ├── scheduler.py
│   │   │   ├── alerter.py
│   │   │   └── notifications.py
│   │   ├── memory.py
│   │   ├── llm/
│   │   │   ├── client.py
│   │   │   └── templates.py
│   │   └── vault.py           # v0.3
│   ├── kernel/
│   │   ├── types.py
│   │   ├── bus.py
│   │   ├── security.py
│   │   └── auth.py
│   └── services/              # v0.3+
│       ├── parliament/        # v0.3
│       ├── taka_lab/         # v0.4
│       ├── registry/          # v0.5
│       └── hermes/           # v1.4
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── Dockerfile
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── index.css
│       ├── lib/
│       │   └── utils.ts
│       ├── types/
│       ├── services/
│       │   └── api.ts
│       ├── stores/
│       │   ├── authStore.ts
│       │   ├── tenderStore.ts
│       │   ├── pipelineStore.ts
│       │   └── uiStore.ts
│       ├── hooks/
│       ├── pages/
│       │   ├── Login.tsx
│       │   ├── Dashboard.tsx
│       │   ├── TendersList.tsx
│       │   ├── TenderDetail.tsx
│       │   ├── KanbanBoard.tsx
│       │   ├── Upload.tsx
│       │   ├── Memory.tsx
│       │   ├── Settings.tsx
│       │   └── AuditLogs.tsx
│       └── components/
│           ├── ui/            # shadcn/ui
│           ├── Layout.tsx
│           ├── Sidebar.tsx
│           ├── Header.tsx
│           ├── KPICard.tsx
│           ├── TenderCard.tsx
│           ├── TenderTable.tsx
│           ├── PipelineColumn.tsx
│           ├── QualificationBadge.tsx
│           ├── DeadlineBadge.tsx
│           ├── FileUploadZone.tsx
│           ├── SearchBar.tsx
│           ├── DataTable.tsx
│           ├── AIBadge.tsx
│           ├── AIActDisclaimer.tsx
│           └── HumanValidation.tsx
│
├── nginx/
│   └── nginx.conf
│
├── tests/
│   ├── conftest.py
│   ├── test_bus.py
│   ├── test_auth.py
│   ├── test_upload.py
│   ├── test_parsing.py
│   ├── test_qualification.py
│   ├── test_pipeline.py
│   ├── test_memory.py
│   ├── test_tracker.py
│   ├── test_e2e.py
│   └── test_compliance.py
│
└── docs/
    ├── architecture.md
    ├── api.md
    ├── onboarding.md
    └── changelog.md
```

---

# CONCLUSION — GO POUR LE LANCEMENT

## Le contrat CEO/CTO/Swarms

| Rôle | Responsabilité | Livrable | Fréquence |
|------|---------------|----------|-----------|
| **CEO (Toi)** | Vision, décisions GO/NO-GO, tests, retours | Validation version N | Fin de chaque version |
| **CTO (Moi)** | Coordination, audit qualité, roadmap | Prompts, rapports, checklists | Continu |
| **Swarms Agentic** | Prompts, review, tests, docs | Code review, tests, documentation | Par Sprint |
| **Kimi Code** | Développement autonome | Code, commits, tests | Par Sprint |

## Les 5 engagements

1. **Le MVP v0.1 est une graine** — pas une cathédrale. Il prouvera le marché en 4 semaines.
2. **Chaque version ajoute une couche** — jamais de saut. v0.1 → v0.2 → v0.3... jusqu'à v2.0.
3. **Le CEO valide chaque version** — pas de passage à N+1 sans GO explicite.
4. **Le CTO coordonne les swarms** — qualité, cohérence, sécurité.
5. **12 mois = cathédrale** — la vision originale NEXA-MIND sera réalisée, mais avec des clients qui paient.

## La promesse

> **"En 12 mois, TAKA OS sera l'OS agentic complet que nous avions imaginé. Mais cette fois, il sera utilisé par des centaines de PME, il aura appris de leurs succès et échecs, et il sera maintenu par une communauté open source."**

## GO

**✅ GO validé pour le lancement du MVP v0.1.**

**Prochaine action :** Rédiger le Prompt Sprint 0 et l'envoyer à Kimi Code.

**Timeline :**
- Semaine 1 (maintenant) : Prompt Sprint 0 → Kimi Code → Développement
- Semaine 2 : Sprint 1 — Parsing + Mémoire
- Semaine 3 : Sprint 2 — Qualifieur + Kanban
- Semaine 4 : Sprint 3 — Tracker + SaaS Packaging → v0.1 TAG
- Semaine 5 : Tests CEO → Validation v0.1 → GO v0.2

**C'est parti.** 🚀

---

*Document produit par l'équipe CTO TAKA OS | Mai 2026*
*GO CEO validé le 2026-05-03 | 4 OUI sur 4*
*Ce document est la Bible Maîtresse du projet — référence unique pour 12 mois*
