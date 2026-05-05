# Compte-Rendu du Groupe Architecture & Technique
## Réunion KIMI-TAKA-SWARM — Cycle de Délibération Technique

**Date** : Session asynchrone validée  
**Groupe** : Architecture & Technique (7 agents)  
**Projet** : TAKA OS — OS Agentic Open Source verticalisé Appels d'Offres  
**Licence** : MIT  
**Stack de référence** : Python 3.12+, FastAPI, SQLAlchemy 2.0 async, PostgreSQL 15+pgvector, Mistral AI, React 18+TypeScript  

---

## Membres du groupe et domaines de responsabilité

| Agent | Rôle | Domaine principal |
|---|---|---|
| SYS | Architecte Système | Architecture globale, cohérence technique, EventBus, Circuit Breaker |
| DATA | Architecte Data | Modélisation données, pgvector, embeddings, partitionnement |
| BACK | Backend Senior | FastAPI, SQLAlchemy, modèles, API design, performance |
| DEVOPS | DevOps Engineer | CI/CD, Docker, Kubernetes, déploiement, observabilité |
| AI | AI Engineer | Intégration LLM, prompts, orchestration agents, fallback LLM |
| ML | ML Engineer | Embeddings, scoring ML, mémoire épisodique, recherche |
| DBA | DBA / Database Engineer | PostgreSQL, indexation, partitionnement, tuning |
| INFRA | Infra Engineer | Infrastructure cloud, VPS, scaling, coûts |

---

## Vue d'ensemble des décisions

| Q | Thème | Décision | Version cible | Statut |
|---|---|---|---|---|
| Q1 | EventBus asyncio in-memory | **DIFFERE** — PostgreSQL LISTEN/NOTIFY en v0.2, NATS en v0.5 | v0.2 / v0.5 | DIFFERE |
| Q2 | pgvector à 10 000+ AO | **GO** — HNSW + index composite, partitionnement v0.3 | v0.1 / v0.3 | GO |
| Q3 | Un seul fichier models/ao.py | **GO** — Split par domaine dès v0.2 | v0.2 | GO |
| Q4 | Vendor lock-in Mistral AI | **GO** — LLMClient multi-provider, plan B OpenRouter | v0.2 | GO |
| Q5 | Docker Compose vs Kubernetes | **DIFFERE** — Docker Compose + systemd jusqu'à v0.6, K8s v0.7+ | v0.7 | DIFFERE |
| Q6 | React 18 + Vite + Tailwind pérennité | **GO** — Pinner versions majeures, migration React 19 v0.5 | v0.5 | GO |
| Q7 | Mémoire épisodique TTL v0.2 | **GO** — TTL fixe 365j, oubli probabiliste v0.4 | v0.2 / v0.4 | GO |
| Q8 | Circuit Breaker Mistral API | **GO** — 3 échecs/30s, réessai 60s, half-open 5 requêtes | v0.2 | GO |
| Q9 | Async SQLAlchemy 2.0 + connection pooling | **GO** — Pool asyncpg, max_overflow=20, pool_timeout=30s | v0.1 | GO |
| Q10 | Sécurité multi-tenant (tenant_id) | **GO** — RLS PostgreSQL + middleware FastAPI, audit v0.2 | v0.1 / v0.2 | GO |
| Q11 | Swarm Registry v0.5 scaling | **DIFFERE** — Redis backend v0.4, état partagé v0.5 | v0.4 / v0.5 | DIFFERE |
| Q12 | Scoring Engine V2 calibration | **GO** — Dataset interne 500 AO, A/B testing v0.3 | v0.3 | GO |

---

## Q1 — EventBus asyncio in-memory est-il suffisant pour le MVP ?

### 1. Positions

**SYS — Architecte Système** (Position : asyncio pur v0.1-v0.4)  
> "L'EventBus asyncio in-memory est suffisant pour les phases v0.1 à v0.4. La raison est simple : nous n'avons pas encore de multi-instance déployée. Un seul process Python gère l'intégralité du swarm sur une seule machine. À ce stade, introduire Redis, NATS ou même RabbitMQ est de l'over-engineering pur. Le coût cognitif de maintenance d'une infra message broker pour moins de 100 tenants n'est pas justifié. Le pattern pub/sub asyncio avec `asyncio.Queue` et un dispatcher central répond à 100% des besoins du MVP. De plus, cela réduit la surface d'attaque et le nombre de points de défaillance."

**DEVOPS — DevOps Engineer** (Position : Redis Streams dès v0.1)  
> "Catégoriquement non. L'argument du SYS ignore un risque fondamental : la persistance des événements. Si le processus serveur redémarre — crash, déploiement, OOM killer, mise à jour OS — tous les événements en mémoire sont perdus sans recours. Dans un système agentic où les 6 agents communiquent par événements, cela signifie qu'un appel d'offres en cours de scoring peut disparaître purement et simplement. Redis Streams coûte quasiment rien en infra (un conteneur Redis, 512 Mo RAM), apporte la persistance AOF, la relecture des streams, et prépare la future scalabilité horizontale. Ne pas le mettre dès v0.1, c'est créer une dette technique que nous paierons au prix du sang en v0.5."

**DBA — Database Engineer** (Position : PostgreSQL LISTEN/NOTIFY)  
> "Il existe une troisième voie que personne n'évoque : PostgreSQL LISTEN/NOTIFY. Nous avons déjà PostgreSQL 15+ dans la stack. LISTEN/NOTIFY est un vrai bus de messages pub/sub intégré au moteur, avec une garantie exactly-once par canal, sans dépendance externe. Cela évite d'ajouter Redis à l'architecture. Les canaux peuvent être `agent.veilleur`, `agent.scorer`, etc. La latence est de l'ordre de la milliseconde. Par contre, NOTIFY a une limitation à 8 000 octets par payload, ce qui oblige à passer des références (UUID d'événement) plutôt que les payloads complets. Et il n'y a pas de persistance native — si le subscriber est déconnecté au moment du NOTIFY, le message est perdu. Donc à utiliser avec un buffer d'événements en table PostgreSQL."

**BACK — Backend Senior** (Position : asyncio pur avec persistance en base)  
> "Je rejoins le DBA sur le principe, mais avec une nuance. L'EventBus asyncio in-memory peut rester le dispatcher principal, mais chaque événement doit être persisté immédiatement dans une table `events` PostgreSQL avant d'être publié. En cas de crash, un recovery service relit la table au redémarrage et rejoue les événements non traités. C'est le pattern Event Sourcing light. Cela donne la résilience sans la complexité d'un broker externe. Le coût : une écriture INSERT par événement, donc ~50-100 INSERT/s max dans notre charge prévisible. PostgreSQL encaisse ça sans problème."

### 2. Débat

**DEVOPS réplique à SYS** : "Ton argument du '100 tenants max' est un faux confort. Le MVP sera déployé chez des groupes comme Equans ou SPIE. Ils ont 50+ filiales. Chaque filiale est un tenant. On atteint 100 tenants en production dès le premier client payant. Et si ce client a besoin de HA (High Availability) avec deux instances pour le SLA ? L'EventBus in-memory ne fonctionne plus du tout entre instances. Tu crées une architecture qui ne scale pas horizontalement d'emblée."

**SYS réplique** : "J'ai bien précisé 'une seule instance' pour le MVP. Le passage à multi-instance est prévu en v0.5 avec NATS. Ce n'est pas du ignoring, c'est du sequencing. NATS est déjà dans la roadmap v0.5. Pourquoi payer le coût de deux migrations (asyncio → Redis → NATS) au lieu d'une seule (asyncio → NATS) ? Redis Streams serait une étape intermédiaire morte."

**DBA réplique** : "Le sequencing du SYS est logique, mais il néglige le risque opérationnel. Un crash en production sur un AO en cours de rédaction, c'est un client qui perd des milliers d'euros de travail. Même en MVP, la persistance des événements métier est non négociable. Ma proposition LISTEN/NOTIFY + table events est une solution hybride : pas d'infra supplémentaire, persistance garantie, migration vers NATS transparente en v0.5 car l'interface pub/sub reste la même."

**INFRA — Infra Engineer** (intervient) : "Sur le plan coût, Redis Streams ajoute ~5€/mois de RAM sur un VPS dédié. Ce n'est pas le coût qui doit décider. C'est la complexité opérationnelle. Un Redis de plus = un backup de plus, un monitoring de plus, un failover de plus. LISTEN/NOTIFY utilise l'infra existante. C'est un argument de poids pour le MVP."

**AI — AI Engineer** (intervient) : "Du point de vue des agents, l'EventBus est l'épine dorsale du swarm. Si un agent 'Rédacteur' émet un événement 'section_complétée' et que cet événement est perdu, l'agent 'Déposant' ne démarre jamais. Le système agentic est fondamentalement asynchrone et dépend de la fiabilité du bus. Je vote pour la persistance obligatoire, peu importe la technologie."

### 3. Décision

**Verdict : DIFFERE avec plan de migration**

| Phase | Version | Technologie | Justification |
|---|---|---|---|
| MVP immédiat | v0.1 | EventBus asyncio in-memory + table `events` PostgreSQL (persistance synchronisée) | Résilience minimale sans infra supplémentaire |
| Amélioration | v0.2 | PostgreSQL LISTEN/NOTIFY comme dispatcher, table `events` comme log | Vrai pub/sub avec persistance, toujours sans infra externe |
| Production multi-instance | v0.5 | NATS Streaming / JetStream | Scalabilité horizontale, HA, replay, découvert de service |

La migration asyncio → LISTEN/NOTIFY → NATS est validée comme séquence unique. Pas de Redis intermédiaire.

### 4. Action

| Action | Responsable | Deadline | Détails |
|---|---|---|---|
| A1.1 — Implémenter EventBus asyncio avec persistance PostgreSQL | BACK | v0.1-beta | Table `events` (id, type, payload, agent_source, agent_dest, status, created_at). INSERT synchrone avant publish. Recovery service au boot. |
| A1.2 — Concevoir interface abstraite EventBus | SYS | v0.1-alpha | Protocol/abstract class `EventBusBackend` avec méthodes `publish`, `subscribe`, `replay`. Permet le swap LISTEN/NOTIFY puis NATS. |
| A1.3 — POC LISTEN/NOTIFY avec canaux agents | DBA | v0.1-rc | Canaux : `agent.veilleur`, `agent.scorer`, `agent.redacteur`, `agent.deposant`, `agent.auditor`, `agent.compliance`. Test de charge 1000 events/s. |
| A1.4 — Benchmark NATS JetStream vs LISTEN/NOTIFY | DEVOPS | v0.4 | Préparation de la v0.5. Mesures : latence p99, throughput, memory usage. |

---

## Q2 — pgvector pour les embeddings 768d : va-t-on buter sur les performances à 10 000+ AO ?

### 1. Positions

**DATA — Architecte Data** (Position : pgvector HNSW tient le choc)  
> "pgvector avec l'index HNSW (Hierarchical Navigable Small World) est benchmarké à des millions de vecteurs 768d avec des temps de recherche < 10ms. À 10 000 AO, même avec 100 chunks par AO (1 000 000 vecteurs), on est encore trois ordres de magnitude en dessous des limites. La communauté reporte des cas à 100M+ vecteurs. La clé est l'index HNSW avec `m=16`, `ef_construction=200`. PostgreSQL 15 gère pgvector 0.5.1 sans souci. Donc oui, on a de la marge considérable."

**ML — ML Engineer** (Position : filtrage par tenant_id va ralentir)  
> "Le raisonnement du DATA est théoriquement correct sur la recherche pure. Mais notre cas d'usage n'est pas une recherche pure. Chaque requête de similarité doit être filtrée par `tenant_id` (multi-tenant). Et souvent aussi par `business_line_id`. Un index HNSW ne supporte pas nativement le filtrage combiné. La requête devient : `SELECT ... WHERE tenant_id = X ORDER BY embedding <=> query_embedding LIMIT 10`. Sans index composite sur `(tenant_id, embedding)`, PostgreSQL fait un seqscan sur le tenant ou un index scan HNSW sans filtre préalable. À 1M vecteurs par tenant, c'est catastrophique. Il faut un index composite ou du partitionnement."

**DBA — Database Engineer** (Position : partitionnement par tenant_id dès v0.3)  
> "Je confirme l'analyse du ML. La requête `WHERE tenant_id = X ORDER BY embedding <=> query LIMIT K` est le cas d'usage principal. Sans partitionnement, le planner choisit soit un BitmapAnd entre l'index B-tree sur tenant_id et l'index HNSW sur embedding, soit un seqscan si les statistiques sont mauvaises. Avec 10 000 tenants × 100 chunks = 1M lignes, ça passe encore. Avec 100 000 tenants, non. Le partitionnement par `tenant_id` en tables dérivées (partitioning natif PostgreSQL 15) permet de réduire la recherche à une seule partition. Chaque partition a son propre index HNSW. Le surcoût est gérable."

**BACK — Backend Senior** (Position : requêtes pré-filtrées avec CTE)  
> "Avant de partitionner, on peut optimiser avec des CTE : pré-filtrer les IDs candidats par tenant_id + business_line, puis faire la similarité sur un sous-ensemble. `WITH candidates AS (SELECT id FROM chunks WHERE tenant_id = X) SELECT c.id, c.embedding <=> query FROM candidates c JOIN chunks ON c.id = chunks.id ORDER BY 2 LIMIT 10`. Mais cela suppose que le sous-ensemble est petit. À 10 000 chunks par tenant, la CTE ne change pas grand-chose."

### 2. Débat

**ML réplique au DATA** : "Tes benchmarks à 100M vecteurs sont des benchmarks de recherche ANN pure. Montre-moi un benchmark HNSW + filtrage RLS multi-tenant à 1M vecteurs. Je t'attends. La réalité c'est que pgvector HNSW a des limitations documentées sur les requêtes avec conditions WHERE complexes. Le filtre est appliqué POST-recherche HNSW, pas PRE-recherche."

**DATA réplique** : "Exact. C'est une limitation connue. La solution est l'index `ivfflat` avec des listes paramétrées par tenant, ou mieux : la nouvelle fonctionnalité `hnsw` avec `vector` + `int` (en développement dans pgvector). Mais aujourd'hui, la meilleure approche est le partitionnement comme le propose le DBA. Je ne suis pas en désaccord avec le partitionnement. Je suis en désaccord avec l'idée qu'on va 'buter' en v0.1. On ne va pas buter. On va ralentir. Et le ralentissement est acceptable en v0.1-v0.2."

**DBA ajoute** : "Le partitionnement natif PostgreSQL 15 supporte le declarative partitioning. On crée une table `embeddings` partitionnée par HASH(tenant_id) ou RANGE(tenant_id). Chaque partition contient ~1000 tenants. Les index HNSW sont par partition, donc plus petits et plus rapides. Le maintenance est automatisé. Le seul point de vigilance : `pgvector` HNSW sur partition nécessite un index par partition, pas un index global. C'est gérable."

**SYS intervient** : "N'oublions pas que les embeddings servent deux cas d'usage : (1) recherche de similarité sur corpus d'AO historiques pour le scoring, et (2) mémoire sémantique du swarm pour la contextualisation. Le cas (2) est moins volumineux mais plus sensible à la latence. Si le Scorer met 500ms à trouver les chunks similaires, l'expérience utilisateur est dégradée."

### 3. Décision

**Verdict : GO avec roadmap d'optimisation progressive**

| Phase | Version | Optimisation | Seuil déclencheur |
|---|---|---|---|
| MVP | v0.1 | Index HNSW simple sur `embedding`, B-tree sur `tenant_id` | < 100 000 vecteurs total |
| Optimisation | v0.2 | Index composite expérimental, CTE pré-filtrage | > 100ms p99 sur requêtes |
| Scalabilité | v0.3 | Partitionnement natif PostgreSQL par `tenant_id` (HASH) | > 1M vecteurs total |
| Expert | v0.5 | Évaluation pgvector advanced features ou migration Qdrant/Pinecone si pgvector ne tient pas | > 10M vecteurs, latence > 200ms p99 |

### 4. Action

| Action | Responsable | Deadline | Détails |
|---|---|---|---|
| A2.1 — Créer index HNSW paramétré | DBA | v0.1-alpha | `CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops) WITH (m=16, ef_construction=200);` + B-tree sur tenant_id. |
| A2.2 — Implémenter requête avec CTE pré-filtrage | BACK | v0.1-beta | Fonction `search_similar_chunks(tenant_id, query_embedding, limit)` avec CTE candidates. |
| A2.3 — Script de benchmark requête embedding | ML | v0.1-rc | Génération 1M vecteurs 768d aléatoires, mesure latence p50/p95/p99 avec et sans filtre tenant_id. |
| A2.4 — POC partitionnement déclaratif | DBA | v0.3-alpha | Table `embeddings` partitionnée par HASH(tenant_id) en 16 partitions. Test d'insertion et recherche. |
| A2.5 — Veille pgvector roadmap | DATA | Continue | Suivi des releases pgvector pour HNSW+filter, année 2024-2025. |

---

## Q3 — Un seul fichier models/ao.py — est-ce tenable à 50+ tables ?

### 1. Positions

**BACK — Backend Senior** (Position : splitter par domaine dès maintenant)  
> "Non, un seul fichier `models/ao.py` n'est pas tenable. À 20 tables, le fichier fait 2000+ lignes. À 50 tables, 5000+ lignes. C'est illisible, impossible à reviewer efficacement, et les conflits Git sur ce fichier unique vont être constants avec 4 développeurs. La structuration par domaine est standard : `models/auth.py` (User, Role, Permission), `models/ao.py` (AppelOffre, Lot, Criteres), `models/memory.py` (MemoryEpisodic, MemorySemantic, Chunk), `models/audit.py` (AuditLog, EventLog). SQLAlchemy 2.0 supporte parfaitement les imports croisés avec `relationship()` et `Mapped[]`."

**SYS — Architecte Système** (Position : garder un seul fichier mais organisé)  
> "La règle NEXA-MIND impose un seul fichier de modèles pour éviter les cycles d'import et les conflits de merge. L'expérience montre que les projets avec 15 fichiers models finissent par avoir des imports circulaires inextricables (`auth.py` importe `ao.py` qui importe `memory.py` qui importe `auth.py`). C'est un piège classique SQLAlchemy. Ma proposition : un seul fichier `models/domain.py` mais structuré avec des classes internes regroupées par section commentée, et l'utilisation de `TYPE_CHECKING` pour les imports. On peut atteindre 3000 lignes dans un fichier bien organisé sans perdre en lisibilité."

**DATA — Architecte Data** (Position : séparation logique sans import circulaire)  
> "Le risque d'import circulaire est réel, mais gérable. La solution n'est pas le monofichier, c'est l'architecture. Chaque module de modèle expose uniquement les classes. Les relationships sont définies avec des strings `'ClassName'` et non des imports directs. SQLAlchemy 2.0 avec `Mapped["ClassName"]` résout ce problème élégamment. Il faut un fichier `models/__init__.py` qui importe tout dans le bon ordre, et un `models/base.py` avec la déclarative base. Les fichiers par domaine importent uniquement `base.py`. Pas de cycles."

### 2. Débat

**BACK réplique au SYS** : "Ta solution du monofichier avec TYPE_CHECKING est un hack. TYPE_CHECKING masque les imports à l'exécution mais pas le problème fondamental : la codebase devient un plat de spaghetti. Quand un développeur veut trouver le modèle `BusinessLine`, il ouvre `models.py` à 3000 lignes et cherche 30 secondes. Avec un fichier `models/organization.py`, c'est instantané. Et les reviews GitHub sur des fichiers de 3000 lignes sont impossibles — GitHub tronque l'affichage."

**SYS réplique** : "L'argument de review GitHub est valide. Mais l'argument de conflits de merge est bidirectionnel : un seul fichier = un seul point de conflit. 15 fichiers = 15 points de conflit possibles. Dans une équipe de 4 développeurs sur les modèles, la probabilité de conflit augmente avec le nombre de fichiers. Et résoudre un conflit sur un fichier de 3000 lignes n'est pas plus dur que sur 15 fichiers si le fichier est bien structuré avec des sections clairement délimitées."

**BACK ajoute** : "Concrètement, aujourd'hui nous avons déjà 12 tables : User, Organization, Tenant, BusinessLine, AppelOffre, Lot, Critere, Chunk, MemoryEpisodic, MemorySemantic, ScoreCard, AuditLog. En v0.2, nous ajouterons : Document, SectionAO, VersionAO, Commentaire, Workflow, Task, Notification, Subscription, BillingEvent. Ça fait 20 tables. Et en v0.4-v0.5 : Template, PromptRegistry, AgentState, SwarmEvent, CircuitBreakerLog. 30 tables. Tu imagines `models.py` à 6000 lignes ?"

**AI intervient** : "Du point de vue des agents, les modèles sont la représentation du monde. Le Scorer lit `AppelOffre`, `Critere`, `ScoreCard`. Le Rédacteur lit `AppelOffre`, `Document`, `SectionAO`. L'Auditor lit `AuditLog`, `Workflow`. Si les modèles sont dispersés dans 10 fichiers, la compréhension du domaine métier par l'agent est plus complexe. Un seul fichier donne une vision d'ensemble."

**DATA conclut** : "Le compromis est un fichier `models/all.py` qui ré-exporte tout pour les imports globaux, et des fichiers par domaine pour l'implémentation. Le développeur écrit `from models import AppelOffre` sans savoir d'où ça vient. Mais l'implémentation est modularisée."

### 3. Décision

**Verdict : GO — Split par domaine avec ré-export centralisé**

La structure suivante est adoptée :

```
models/
├── __init__.py          # Ré-export de toutes les classes
├── base.py              # Base déclarative, mixins communs (TimestampMixin, TenantMixin)
├── auth.py              # User, Role, Permission, Session
├── organization.py      # Organization, Tenant, BusinessLine, Subscription
├── ao.py                # AppelOffre, Lot, Critere, Document, SectionAO, VersionAO
├── memory.py            # MemoryEpisodic, MemorySemantic, Chunk, Embedding
├── scoring.py           # ScoreCard, ScoreDimension, ProfilScoring
├── workflow.py          # Workflow, Task, Notification, Commentaire
├── audit.py             # AuditLog, EventLog, CircuitBreakerLog
└── agent.py             # AgentState, SwarmEvent, PromptRegistry, Template
```

Règles strictes :
1. Chaque fichier n'importe que `base.py` et éventuellement `TYPE_CHECKING` imports
2. Les `relationship()` utilisent des string references : `Mapped[List["Chunk"]]`
3. `__init__.py` importe dans l'ordre : base → auth → organization → ao → memory → scoring → workflow → audit → agent
4. Aucun fichier ne fait plus de 500 lignes. Si dépassement, créer un sous-module.

### 4. Action

| Action | Responsable | Deadline | Détails |
|---|---|---|---|
| A3.1 — Créer structure fichiers modèles | BACK | v0.1-beta | Mise en place du répertoire et des 9 fichiers avec imports corrects. |
| A3.2 — Migrer modèles existants depuis ao.py monolithique | BACK | v0.2-alpha | Refactoring sans changement de schéma DB. Tests de non-régression. |
| A3.3 — Documenter règles anti-circulaire | SYS | v0.2-alpha | Fichier `docs/adr/003-model-splitting.md` avec les règles d'import. |
| A3.4 — Linter custom pour détecter imports directs croisés | DEVOPS | v0.2-beta | Script CI qui vérifie qu'aucun fichier models/*.py n'importe directement un autre fichier models/*.py (hors base.py). |

---

## Q4 — Mistral AI API : risque de vendor lock-in ? Quel plan B crédible ?

### 1. Positions

**AI — AI Engineer** (Position : vendor lock-in réel et dangereux)  
> "Le vendor lock-in sur Mistral AI est un risque concret. En 2023-2024, nous avons vu Anthropic fermer l'accès API à certains pays, OpenAI multiplier ses tarifs par 3 en 12 mois, et des startups IA disparaître du jour au lendemain. Mistral est bien financée (Series B, 600M€), mais c'est une entreprise française en compétition mondiale. Si elle pivote vers le enterprise-only, augmente ses prix de 300%, ou subit une acquisition hostile avec changement de politique API, TAKA OS est en dépendance critique. Nous avons 6 agents qui font 50+ appels API Mistral par AO. Un arrêt API = arrêt produit."

**SYS — Architecte Système** (Position : LLMClient abstrait + fallback existant)  
> "Nous avons déjà anticipé ce risque. Le module `core/llm_client.py` définit une abstraction `LLMProvider` avec des implémentations `MistralProvider`, `OpenRouterProvider`, `OllamaProvider`. Le switch se fait par configuration `LLM_PROVIDER=mistral` → `LLM_PROVIDER=openrouter`. C'est du runtime swap. Le lock-in est technique, pas architectural. Tant que nous maintenons les 3 implémentations à jour, le risque est mitigé."

**ML — ML Engineer** (Position : Ollama local n'est pas viable économiquement)  
> "Le fallback Ollama est une illusion. Le SYS parle de 'runtime swap' vers Ollama, mais sur quelle infra ? Un modèle 7B (Mistral 7B, Llama 3 8B) nécessite 8-16 Go VRAM pour des performances acceptables. Un VPS à 20€/mois (4 vCPU, 8 Go RAM, pas de GPU) fait tourner un 7B à 2 tokens/seconde. C'est inutilisable pour la génération de réponses structurées JSON sur des AO de 50 pages. Pour du vrai local inference, il faut un GPU A100 40Go (~500€/mois cloud) ou un on-premise avec RTX 4090. Ce n'est PAS un plan B crédible pour un produit SaaS à 200€/mois/client."

**INFRA — Infra Engineer** (Position : coût du plan B)  
> "Je confirme les chiffres du ML. AWS g4dn.xlarge (T4 16Go) = ~0.50€/heure = ~360€/mois. C'est le minimum pour un 7B confortable. Pour un 70B (Llama 3 70B, Mistral Large), il faut 2×A100 80Go = ~2000€/mois. Notre modèle économique ne supporte pas ce coût. Le plan B ne peut pas être le local inference."

### 2. Débat

**AI réplique au SYS** : "L'abstraction LLMClient est nécessaire mais pas suffisante. Avoir 3 providers dans le code, mais n'en tester qu'un en production, c'est du 'future faking'. Si nous ne testons pas régulièrement OpenRouter et Ollama, le switch d'urgence sera un désastre. L'abstraction doit être validée par des tests d'intégration continus sur les 3 providers."

**SYS réplique** : "D'accord sur les tests continus. Mon point est que l'architecture est correcte. Le plan B crédible n'est pas Ollama local, c'est OpenRouter. OpenRouter est un agrégateur d'API qui expose Mistral, Anthropic, OpenAI, Cohere, et des modèles open source via des hosts tiers. Si Mistral ferme, OpenRouter redirige automatiquement vers un provider alternatif. C'est le plan B crédible."

**ML réplique** : "OpenRouter est un bon plan B, mais c'est un SPOF (Single Point of Failure) aussi. Si OpenRouter a une panne, on est bloqué. Il faut un plan C : au moins 2 agrégateurs (OpenRouter + Together AI) ou la capacité de switch manuel entre providers directs. Et le coût : OpenRouter ajoute une marge 10-20% sur les appels API. Sur 10 000 appels/jour, c'est significatif."

**DATA intervient** : "Sur le plan métier, le risque le plus probable n'est pas la fermeture de Mistral, c'est la dégradation de qualité. Si Mistral change son modèle fine-tuné pour les réponses structurées JSON, notre parsing échoue. Nous devons versionner les prompts par modèle et avoir des tests de non-régression sur chaque modèle supporté."

**BACK intervient** : "Et il y a le rate limiting. Mistral free tier = 1 req/s. Pro tier = 10 req/s. Enterprise = à négocier. Si nous avons 6 agents parallèles sur un AO urgent, on peut saturer le rate limit. L'abstraction LLMClient doit intégrer un rate limiter par provider avec queue et backoff exponentiel."

### 3. Décision

**Verdict : GO — Stratégie multi-provider avec OpenRouter comme plan B principal**

| Niveau | Provider | Usage | Seuil d'activation |
|---|---|---|---|
| Primaire | Mistral API direct | Par défaut, coût optimal | — |
| Fallback 1 | OpenRouter (Mistral via OR) | Si Mistral direct indisponible | 3 échecs consécutifs |
| Fallback 2 | OpenRouter (autre modèle, ex: Llama 3 70B via OR) | Si Mistral indisponible partout | Fallback 1 échoue 3× |
| Dégradé | Cache local + queue async | Si tout est down | Stocker dans `llm_queue` table, rejouer plus tard |
| Hors scope | Ollama local | Pas viable économiquement | Nécessite GPU dédié, reporté v2.0 |

Exigences :
1. Chaque provider a son propre rate limiter (token bucket)
2. Les prompts sont versionnés par modèle (`prompt_v2_mistral`, `prompt_v2_llama`)
3. Tests CI hebdomadaires sur les 2 providers actifs
4. Monitoring du coût par provider et par appel

### 4. Action

| Action | Responsable | Deadline | Détails |
|---|---|---|---|
| A4.1 — Finaliser LLMClient avec 3 providers | AI | v0.1-beta | `MistralProvider`, `OpenRouterProvider`, `FallbackProvider`. Rate limiter intégré. |
| A4.2 — Implémenter switch automatique provider | AI | v0.2-alpha | Circuit breaker par provider, retry avec fallback, health check toutes les 60s. |
| A4.3 — Versionnement des prompts par modèle | AI | v0.2-alpha | Dossier `prompts/v1/mistral/`, `prompts/v1/openrouter/`. YAML avec template Jinja2. |
| A4.4 — Tests CI hebdomadaires multi-provider | DEVOPS | v0.2-beta | Job GitHub Actions exécutant la suite de tests sur Mistral direct ET OpenRouter. |
| A4.5 — Table `llm_call_log` avec coût et latence | BACK | v0.1-rc | Tracking de chaque appel : provider, modèle, tokens_in, tokens_out, latence, coût estimé. |
| A4.6 — POC Ollama local documenté | ML | v0.3 | Documentation du coût et des perfs pour référence future, non intégré au produit. |

---

## Q5 — Docker Compose vs Kubernetes : quand basculer ?

### 1. Positions

**DEVOPS — DevOps Engineer** (Position : Kubernetes dès v0.5)  
> "Kubernetes (K8s) dès la v0.5 pour l'auto-scaling, le self-healing, et le déploiement blue/green. Docker Compose est un outil de développement, pas de production. À 1000 utilisateurs concurrents, on a besoin de 3-4 replicas de l'API FastAPI, 1-2 workers Celery/RQ, PostgreSQL avec replica read-only, et Redis/NATS en cluster. K8s gère ça nativement avec HPA (Horizontal Pod Autoscaler), PDB (Pod Disruption Budget), et des rolling updates sans downtime. Attendre v0.7, c'est migrer sous pression avec des clients en production."

**INFRA — Infra Engineer** (Position : Docker Compose + systemd jusqu'à 1000 utilisateurs)  
> "Overkill complet. Docker Compose + systemd sur 2-3 VPS dédiés suffit amplement jusqu'à 1000 utilisateurs. K8s ajoute une complexité opérationnelle énorme : etcd, kubelet, ingress controllers, cert-manager, monitoring stack (Prometheus+Grafana), log aggregation. Il faut un ingénieur K8s à plein temps. Nous n'avons pas cette ressource. Un VPS 8 vCPU / 32 Go RAM à 40€/mois fait tourner l'ensemble du stack TAKA OS avec 500 utilisateurs actifs. En ajoutant un second VPS pour la BDD et un troisième pour les workers, on tient 1000 utilisateurs. K8s n'est pas une question de technologie, c'est une question de TCO (Total Cost of Ownership)."

**SYS — Architecte Système** (Position : seuil de bascule mesurable)  
> "Ni l'un ni l'autre n'a tort, mais le débat manque de métriques concrètes. La bascule vers K8s doit être déclenchée par des seuils mesurables, pas par une version arbitraire. Seuils proposés : (1) plus de 3 instances d'API nécessaires, (2) besoin de zero-downtime deployment obligatoire (SLA 99.9%), (3) équipe Ops de 2+ personnes dédiées, (4) budget infra > 500€/mois. Tant que ces seuils ne sont pas atteints, Docker Compose swarm mode (pas K8s) est une étape intermédiaire valide."

**BACK — Backend Senior** (Position : scaling horizontal sans K8s)  
> "Le scaling horizontal de FastAPI peut se faire avec Docker Compose + un reverse proxy nginx upstream. C'est du scaling stateless simple. Ce qui force vers K8s, c'est le scaling stateful (PostgreSQL, Redis) et l'orchestration complexe. Mais PostgreSQL en HA, c'est Patroni/etcd ou Cloud SQL managed. Si on prend Cloud SQL managed, le besoin K8s diminue."

### 2. Débat

**DEVOPS réplique à INFRA** : "Ton calcul de TCO ignore le coût de l'indisponibilité. Si TAKA OS est down 4 heures pendant un déploiement manuel sur Docker Compose, et qu'un client perd un AO à 2M€ à cause de ça, le coût de l'indispo est bien supérieur au coût K8s. Les rolling updates de K8s sont zero-downtime. Docker Compose require `docker compose up -d` qui recrée les conteneurs avec interruption de service."

**INFRA réplique** : "Le zero-downtime est résoluble avec Docker Compose + Traefik ou nginx reload. `docker compose up -d` fait un rolling update par défaut si le healthcheck est configuré. Et le coût de l'indispo est un argument de vente, pas technique. En v0.5-v0.6, nous n'avons pas de SLA 99.9%. Nous avons un SLA 99%. 4h d'indispo par mois sont acceptables contractuellement. K8s pour un SLA 99% est un gaspillage."

**DEVOPS ajoute** : "Mais le monitoring ! K8s avec Prometheus et Grafana donne une observabilité native. Sur Docker Compose, il faut installer et configurer manuellement Prometheus, cAdvisor, node-exporter. C'est du boulot aussi."

**INFRA réplique** : "Oui, et ce boulot est fait une fois. La stack monitoring Docker Compose est documentée et reproductible. Elle ne justifie pas K8s."

**SYS tranche** : "Arrêtons de caricaturer. K8s n'est pas le diable, Docker Compose n'est pas une solution de pauvre. La vraie question est : à quel moment le coût de la complexité K8s devient inférieur au coût de la complexité Docker Compose à grande échelle ? Ma réponse : quand on a plus de 5 services stateless à orchestrer avec des contraintes de placement, ou quand on a besoin de scaling automatique basé sur la charge CPU/mémoire."

### 3. Décision

**Verdict : DIFFERE — Docker Compose en production jusqu'à v0.6, K8s évalué en v0.7**

| Phase | Version | Infrastructure | Seuil déclencheur |
|---|---|---|---|
| MVP / Early | v0.1-v0.4 | Docker Compose + systemd, 1-2 VPS | < 500 utilisateurs actifs |
| Growth | v0.5-v0.6 | Docker Compose Swarm Mode ou 3 VPS avec nginx upstream | 500-1500 utilisateurs, besoin de réplicas API |
| Scale | v0.7+ | Évaluation Kubernetes ou managed cloud (ECS/Fargate, Cloud Run, Railway) | > 1500 utilisateurs, SLA 99.9%, équipe Ops 2+ personnes |

Conditions de bascule K8s (toutes doivent être vraies) :
1. > 1500 utilisateurs actifs mensuels
2. SLA contractuel 99.9% ou supérieur
3. Besoin de scaling automatique (HPA) avéré par métriques
4. Équipe Ops de 2 ingénieurs minimum
5. Budget infra > 800€/mois

### 4. Action

| Action | Responsable | Deadline | Détails |
|---|---|---|---|
| A5.1 — Production-ready Docker Compose | DEVOPS | v0.1-beta | `docker-compose.yml` + `docker-compose.prod.yml` avec healthchecks, restart policies, secrets. |
| A5.2 — Script de déploiement blue/green | DEVOPS | v0.2-alpha | Bash script avec nginx reload zero-downtime pour Docker Compose. |
| A5.3 — Monitoring stack Docker Compose | INFRA | v0.2-beta | Prometheus + Grafana + cAdvisor + node-exporter + Alertmanager. |
| A5.4 — Document de décision K8s (ADR) | SYS | v0.3 | ADR-005 avec les 5 conditions de bascule et les alternatives évaluées (ECS, Fargate, Railway, K3s). |
| A5.5 — Benchmark charge Docker Compose | INFRA | v0.4 | Test à 1000 utilisateurs simulés sur stack Docker Compose. Métriques : CPU, RAM, latence p99, erreurs. |

---

## Q6 — React 18 + Vite + Tailwind : ce stack tient-il 3 ans ?

### 1. Positions

**FRONT — Frontend Senior** (Position : stack solide pour 3 ans)  
> "React 18 + Vite + Tailwind CSS est un stack mature et pérenne. React 19 est en release candidate, la migration est annoncée comme 'drop-in replacement' sans breaking changes majeurs pour les cas d'usage classiques. Vite est devenu le standard de l'industrie, stable depuis 3 ans, avec un écosystème plug-in riche. Tailwind CSS v3 est mature, v4 est en preview mais reste compatible. Ce stack est utilisé par des centaines de milliers de projets en production. Il tiendra 3 ans sans problème."

**UI/UX — UI/UX Designer** (Position : risque shadcn/ui)  
> "Le risque n'est pas sur React, Vite ou Tailwind. Le risque est sur `shadcn/ui`, la bibliothèque de composants que nous avons choisie. shadcn/ui n'est pas une bibliothèque npm classique : c'est une collection de composants copiés dans le projet via CLI. Quand shadcn/ui fait un breaking change (v2 en préparation), la migration n'est pas un `npm update`. C'est un recopiage manuel de composants. Et les composants shadcn dépendent de Radix UI primitives, qui évoluent aussi. En 12 mois, nous avons eu 3 versions majeures de Radix. Le coût de maintenance est sous-estimé."

**SYS — Architecte Système** (Position : pinner les versions)  
> "La décision claire est de pinner les versions majeures dans `package.json` avec `exact` versions, pas de ranges. React 18.3.1 exact, Vite 5.x exact, Tailwind 3.4.x exact, shadcn/ui CLI version locked. Les mises à jour se font par décision explicite, pas par `npm update` automatique. Cela évite les breaking changes surprises. Une migration planifiée tous les 6 mois vers les versions LTS suivantes."

**BACK intervient** : "Côté API, nous avons le même problème avec les versions. Le frontend et le backend doivent être versionnés ensemble. Si le frontend passe à React 19 mais que le backend reste en FastAPI 0.110, les incompatibilités sont potentielles sur les types TypeScript générés depuis OpenAPI."

### 2. Débat

**FRONT réplique à UI/UX** : "Le risque shadcn/ui est réel, mais exagéré. shadcn/ui est fondamentalement du code que nous possédons. Les composants sont dans notre repo, pas dans `node_modules`. Si shadcn/ui disparaît demain, nos composants continuent de fonctionner. C'est un avantage, pas un risque. Le 'vendor lock-in' inversé. Et les breaking changes Radix sont gérables car nous n'utilisons pas 100% des primitives — seulement Dialog, Dropdown, Tabs, Tooltip, etc."

**UI/UX réplique** : "L'argument 'nous possédons le code' est faux en pratique. Quand un composant shadcn a un bug de accessibilité corrigé en upstream, tu ne reçois pas la correction automatiquement. Tu dois suivre les releases, comparer les diffs, et merger manuellement. À 20 composants shadcn, c'est 20 merges manuels par release. Personne ne le fait. Résultat : les projets shadcn accumulent des bugs connus et non patchés."

**FRONT réplique** : "C'est pour ça que je propose de pinner shadcn/ui à une version stable, et de ne mettre à jour que pour des bugs critiques ou des features nécessaires. Pas de 'suivre latest'."

**SYS conclut** : "Le consensus émerge : pinner tout, migrer planifié. React 19 migration en v0.5 (pas d'urgence), Tailwind 4 migration en v0.6 (si compatible), shadcn/ui reste en version actuelle jusqu'à preuve de besoin."

### 3. Décision

**Verdict : GO — Pinner les versions majeures, migration planifiée**

| Dépendance | Version pinnée | Migration cible | Version cible | Date estimée |
|---|---|---|---|---|
| React | 18.3.1 | v0.5 | 19.x LTS | T2 2025 |
| Vite | 5.4.x | v0.5 | 6.x | T2 2025 |
| Tailwind CSS | 3.4.x | v0.6 | 4.x | T3 2025 |
| shadcn/ui CLI | 0.x (current) | v0.6 | v2 si nécessaire | T3 2025 |
| TypeScript | 5.5.x | v0.5 | 5.6+ | T2 2025 |
| Radix primitives | versions exactes | Au cas par cas | — | — |

Règles de gestion :
1. `package.json` utilise des versions exactes (pas `^`, pas `~`)
2. `package-lock.json` est commité et audité
3. Les mises à jour de sécurité passent par Dependabot avec approbation manuelle
4. Un ADR est requis pour toute migration de version majeure

### 4. Action

| Action | Responsable | Deadline | Détails |
|---|---|---|---|
| A6.1 — Fixer versions exactes dans package.json | FRONT | v0.1-beta | Suppression de tous les `^` et `~`. Versions exactes pour React, Vite, Tailwind, shadcn/ui. |
| A6.2 — Documenter stratégie de mise à jour frontend | SYS | v0.1-rc | ADR-004 avec le calendrier de migration et les critères de décision. |
| A6.3 — Setup Dependabot avec approbation manuelle | DEVOPS | v0.1-beta | PR automatiques pour security updates uniquement, merge bloqué sans review. |
| A6.4 — POC migration React 19 | FRONT | v0.5-alpha | Branche feature, test de compatibilité, mesure des breaking changes. |

---

## Q7 — Mémoire épisodique avec TTL/oubli : implémentable en v0.2 ?

### 1. Positions

**ML — ML Engineer** (Position : trop complexe pour v0.2)  
> "La mémoire épisodique avec TTL adaptatif et oubli probabiliste n'est PAS implémentable en v0.2. C'est un sujet de recherche active en neuro-symbolic AI. On ne sait pas quel TTL est optimal. Un TTL fixe de 365 jours est naïf : certaines informations méritent d'être retenues 1 jour, d'autres 10 ans. L'oubli probabiliste (comme le fait le cerveau humain avec la courbe d'Ebbinghaus) nécessite un modèle de décay paramétré par la fréquence d'accès, l'importance sémantique, et la redondance. Implémenter ça correctement, c'est 3-6 mois de recherche et développement. En v0.2, c'est du scope creep."

**AI — AI Engineer** (Position : TTL fixe comme point de départ)  
> "Le ML a raison sur la complexité de la mémoire biologique. Mais il a tort sur l'impossibilité. On peut commencer avec une simplification radicale : TTL fixe de 365 jours pour tous les épisodes, avec une suppression automatique par cron job. C'est 20 lignes de SQL : `DELETE FROM memory_episodic WHERE created_at < NOW() - INTERVAL '365 days'`. Pas de recherche, pas de modèle de decay. Cela donne déjà la valeur métier principale : la mémoire ne grossit pas indéfiniment. Et nous itérons vers un TTL adaptatif en v0.4. Le 'parfait' est l'ennemi du 'bien'."

**DATA — Architecte Data** (Position : catégorisation par importance)  
> "Un intermédiaire est possible : catégoriser les épisodes par importance au moment de la création. Par exemple : `importance='critique'` (durée 5 ans), `importance='important'` (2 ans), `importance='standard'` (1 an), `importance='fugace'` (7 jours). L'agent émetteur taggue l'importance. C'est un TTL semi-adaptatif sans modèle complexe. Ça tient en v0.2 et c'est nettement mieux qu'un TTL unique."

### 2. Débat

**ML réplique au AI** : "Ton TTL fixe de 365 jours est dangereux. Imagine : l'agent mémorise 'le client X préfère les réponses courtes' en janvier 2024. En janvier 2025, le TTL expire, l'information est supprimée. L'agent redevient verbeux, le client est mécontent. Un TTL fixe sans compréhension de la valeur de l'information est une regression."

**AI réplique** : "C'est un risque accepté en v0.2. Le document ADR dira explicitement : 'La mémoire TTL fixe peut supprimer des informations encore pertinentes. C'est une limitation connue.' En v0.4, nous ajouterons un mécanisme de 'refresh' : chaque accès à un épisode reset son TTL. C'est du LRU (Least Recently Used) simple et efficace."

**ML réplique** : "Le LRU par accès est déjà beaucoup mieux. Pourquoi ne pas le faire dès v0.2 ?"

**AI** : "Parce que le LRU nécessite de tracker chaque accès, ce qui crée des écritures supplémentaires. À 1000 accès/jour sur la mémoire, c'est 1000 UPDATE. Sur un MVP, c'est du bruit."

**DATA** : "Le compromis est le tagging d'importance. Pas d'UPDATE, juste un champ à la création. Le cron job supprime par tranches d'importance. C'est viable."

### 3. Décision

**Verdict : GO — Mémoire épisodique simplifiée en v0.2, TTL adaptatif en v0.4**

| Version | Mécanisme | Détails |
|---|---|---|
| v0.2 | TTL par catégorie d'importance | `importance ∈ {fugace(7j), standard(365j), important(730j), critique(1825j)}`. Tagging par l'agent émetteur. Cron quotidien. |
| v0.3 | LRU refresh | Mise à jour de `last_accessed_at` à chaque lecture. Le TTL est recalculé depuis `last_accessed_at`. |
| v0.4 | Oubli probabiliste (v1) | Decay exponentiel pondéré par : fréquence d'accès, importance initiale, redondance sémantique. Algorithme : p(oubli) = 1 - exp(-λ × age / importance). |
| v0.5+ | Mémoire consolidée | Fusion des épisodes redondants en mémoire sémantique. Recherche de patterns récurrents. |

### 4. Action

| Action | Responsable | Deadline | Détails |
|---|---|---|---|
| A7.1 — Ajouter champ `importance` et `ttl_expires_at` à `memory_episodic` | BACK | v0.2-alpha | Migration Alembic. Valeur par défaut : `standard`. |
| A7.2 — Implémenter cron de purge mémoire | DEVOPS | v0.2-alpha | Job quotidien 3h du matin, suppression en batch de 1000 lignes. |
| A7.3 — Documenter limitations mémoire v0.2 | ML | v0.2-beta | Section dans la documentation : "Mémoire à durée limitée — risque de perte d'information pertinente." |
| A7.4 — Concevoir algorithme oubli probabiliste v0.4 | ML | v0.3 | Spécification mathématique du decay, paramètres λ et pondération. |
| A7.5 — Benchmark mémoire avec 100K épisodes | DATA | v0.3 | Test de performance de la purge et de la recherche avec volume. |

---

## Q8 — Circuit breaker sur Mistral API : quelle configuration exacte ?

### 1. Positions

**SYS — Architecte Système** (Position : 5 échecs/60s, réessai 120s)  
> "La configuration proposée est : 5 échecs consécutifs dans une fenêtre glissante de 60 secondes déclenchent l'ouverture du circuit breaker. Le circuit reste ouvert pendant 120 secondes, puis passe en half-open (5 requêtes de test). Si les 5 requêtes de test réussissent, le circuit se ferme. Sinon, il se rouvre pour 120s supplémentaires. Cette configuration est permissive : elle tolère les pics de latence temporaires sans ouvrir le circuit prématurément. Dans un système agentic, un circuit trop agressif (3 échecs) provoque des cascades de fallback qui dégradent la qualité des réponses."

**DEVOPS — DevOps Engineer** (Position : 3 échecs/30s, réessai 60s)  
> "5 échecs en 60 secondes est beaucoup trop permissif. Sur un AO en cours de rédaction, 5 échecs = 5 sections non générées = l'AO est bloqué. En 60 secondes, l'utilisateur attend déjà depuis 30s et rafraîchit la page. La frustration est maximale. 3 échecs en 30 secondes est le standard industriel (Netflix Hystrix, AWS Circuit Breaker). Le réessai après 60s est aussi standard. Un circuit trop lent à s'ouvrir expose le système à des storms de retry qui surcharge le provider déjà en difficulté. Et un réessai après 120s, c'est une éternité pour un utilisateur."

**BACK — Backend Senior** (Position : circuit par agent, pas global)  
> "Le débat manque une nuance critique : le circuit breaker doit-il être global (tous les agents partagent le même circuit) ou par agent ? Ma position est par agent. Le `Rédacteur` qui génère des sections longues a un pattern d'appel différent du `Scorer` qui fait des appels courts et fréquents. Un circuit global pénalise tous les agents pour une défaillance d'un seul. Un circuit par agent (`circuit_redacteur`, `circuit_scorer`, etc.) isole les défaillances."

**AI — AI Engineer** (Position : half-open avec 1 requête, pas 5)  
> "Le half-open avec 5 requêtes de test est risqué. Si le provider est en recovery partiel (ex: 50% de réussite), 5 requêtes de test ont une probabilité non négligeable d'échouer toutes ou en majorité, ce qui rouvre le circuit. En half-open, 1 requête de test suffit. Si elle réussit, on ferme. Si elle échoue, on rouvre. C'est plus réactif."

### 2. Débat

**SYS réplique à DEVOPS** : "Ton argument utilisateur est valide, mais il confond latence et échec. Un appel API qui met 10s n'est pas un échec. C'est une lenteur. Le circuit breaker ne mesure que les échecs HTTP (timeout, 5xx, 429). Les timeouts sont configurés à 30s. Donc un appel lent n'est pas compté comme échec. Les 5 échecs en 60s supposent 5 vraies erreurs réseau/serveur. Ça n'arrive que si Mistral est vraiment down."

**DEVOPS réplique** : "Mais le timeout à 30s est lui-même un problème. Si Mistral répond en 25s avec un 500, c'est un échec. Et l'utilisateur a attendu 25s pour rien. 3 échecs × 25s = 75s d'attente totale. C'est déjà trop. Mon argument reste : le circuit doit s'ouvrir vite pour préserver l'expérience."

**BACK intervient** : "Ajoutons une dimension : le backoff exponentiel entre retries. Avant d'ouvrir le circuit, on fait 3 retries avec backoff 1s, 2s, 4s. Si les 3 retries échouent, ça compte pour 1 échec du circuit. Ainsi, 3 échecs de circuit = 9 échecs réels. C'est plus robuste."

**SYS** : "Le backoff exponentiel entre retries et le circuit breaker sont deux mécanismes différents mais complémentaires. Je suis d'accord pour les combiner. Mais cela renforce mon argument : avec backoff, 3 échecs de circuit représentent beaucoup plus de vraies erreurs. Donc 5 échecs de circuit avec backoff = ~15 échecs réels. C'est trop."

**AI intervient** : "Et le rate limiting ? Si Mistral renvoie 429 (rate limit exceeded), ce n'est pas une erreur du provider, c'est une erreur de notre consommation. Le circuit breaker ne devrait pas compter les 429 comme échecs, ou du moins pas de la même manière."

**DEVOPS réplique** : "D'accord sur les 429. Les 429 doivent déclencher un rate limiter côté client (token bucket) et ne pas compter dans le circuit breaker."

### 3. Décision

**Verdict : GO — Configuration définitive du Circuit Breaker**

| Paramètre | Valeur | Justification |
|---|---|---|
| **Échecs avant ouverture** | 3 échecs | Standard industriel, réactivité suffisante |
| **Fenêtre glissante** | 30 secondes | Détection rapide des dégradations |
| **Durée ouverture** | 60 secondes | Temps de recovery du provider, acceptable utilisateur |
| **Half-open requêtes de test** | 1 requête | Réactivité maximale, évite les faux négatifs |
| **Timeout appel API** | 30 secondes | Limite supérieure acceptable pour LLM |
| **Retries avant circuit** | 2 retries max | Backoff exponentiel : 1s, 2s |
| **429 Rate Limit** | Exclu du compteur circuit | Géré par rate limiter dédié (token bucket) |
| **Par agent** | Oui | Circuit indépendant par agent : `cb_redacteur`, `cb_scorer`, `cb_veilleur`, `cb_deposant`, `cb_auditor`, `cb_compliance` |

**Transitions d'état :**
- `CLOSED` → `OPEN` : 3 échecs (non-429) dans 30s
- `OPEN` → `HALF_OPEN` : après 60s
- `HALF_OPEN` → `CLOSED` : 1 requête test réussie
- `HALF_OPEN` → `OPEN` : 1 requête test échoue → OPEN pour 60s supplémentaires

### 4. Action

| Action | Responsable | Deadline | Détails |
|---|---|---|---|
| A8.1 — Implémenter CircuitBreaker class per-agent | BACK | v0.2-alpha | Classe Python `CircuitBreaker` avec états CLOSED/OPEN/HALF_OPEN. Thread-safe. |
| A8.2 — Intégrer CB dans LLMClient | AI | v0.2-alpha | Wrapper `call_with_circuit()` pour chaque provider. 6 instances CB (1 par agent). |
| A8.3 — Rate limiter par provider (token bucket) | AI | v0.2-beta | `RateLimiter` avec capacity/refill par provider. Gère les 429 sans ouvrir le circuit. |
| A8.4 — Tests unitaires CB (scénarios complets) | BACK | v0.2-beta | Mock du provider, simulation des 3 échecs, test des transitions d'état. |
| A8.5 — Dashboard monitoring CB | DEVOPS | v0.3 | Métriques Prometheus : `circuit_breaker_state`, `circuit_breaker_failures_total`, `circuit_breaker_latency`. |

---

## Q9 — Async SQLAlchemy 2.0 + connection pooling : quelle stratégie ?

### 1. Positions

**BACK — Backend Senior** (Position : pool asyncpg optimisé)  
> "SQLAlchemy 2.0 async avec asyncpg est le standard. La configuration du pool est critique. Par défaut, SQLAlchemy crée un `NullPool` si on ne configure rien. Pour un FastAPI async, il faut un `AsyncAdaptedQueuePool` avec : `pool_size=10` (connections maintenues chaudes), `max_overflow=20` (connections d'urgence), `pool_timeout=30` (timeout d'attente), `pool_recycle=1800` (recycle toutes les 30 min pour éviter les connections stale). Avec 6 agents potentiellement actifs + requêtes API concurrentes, on peut atteindre 30 connections simultanées. PostgreSQL par défaut accepte 100 connections. On a de la marge, mais il faut surveiller."

**DBA — Database Engineer** (Position : connection pooling côté PostgreSQL aussi)  
> "Le pool côté application n'est pas suffisant. Il faut aussi PgBouncer en mode transaction pooling entre l'application et PostgreSQL. PgBouncer multiplexe les connections application vers un pool plus petit de connections PostgreSQL. C'est standard en production. Sans PgBouncer, 30 connections FastAPI × 2 instances = 60 connections. Avec PgBouncer, on réduit à 20 connections PostgreSQL réelles. C'est particulièrement important quand nous aurons des workers Celery/RQ en plus de l'API."

**SYS — Architecte Système** (Position : start simple, complexifier quand mesuré)  
> "PgBouncer est un outil de production, pas de MVP. Commençons avec le pool SQLAlchemy bien configuré et mesurons. Si nous voyons `FATAL: sorry, too many clients` dans les logs, alors on ajoute PgBouncer. Prématurer PgBouncer ajoute une dépendance, un monitoring, et un point de défaillance. Le principe est : mesurer d'abord, optimiser ensuite."

### 2. Débat

**DBA réplique** : "Le 'too many clients' en production, c'est une panne. Ce n'est pas un signal d'alerte agréable. C'est une erreur qui bloque les utilisateurs. Attendre de voir l'erreur pour ajouter PgBouncer, c'est du réactif. Le coût d'ajouter PgBouncer dès le début est négligeable : c'est un conteneur Docker de 10 Mo."

**SYS réplique** : "D'accord sur le coût négligeable, mais le coût cognitif n'est pas négligeable. L'équipe doit comprendre PgBouncer, son mode (transaction vs session), son fichier de config. Et en mode transaction pooling, les prepared statements et les transactions longues ne fonctionnent pas de la même manière. SQLAlchemy 2.0 avec asyncpg utilise des prepared statements. Il faut vérifier la compatibilité."

**BACK** : "SQLAlchemy 2.0 + asyncpg + PgBouncer mode transaction = compatibilité partielle. Les prepared statements sont désactivés par défaut dans ce setup. Il faut `prepared_statement_cache_size=0` dans la connexion SQLAlchemy. C'est documenté mais c'est une contrainte."

### 3. Décision

**Verdict : GO — Pool SQLAlchemy optimisé en v0.1, PgBouncer évalué en v0.3**

| Phase | Version | Configuration | Seuil |
|---|---|---|---|
| MVP | v0.1 | `AsyncAdaptedQueuePool`, pool_size=10, max_overflow=20, pool_timeout=30s, pool_recycle=1800s | < 50 connections simultanées |
| Optimisation | v0.3 | Évaluation PgBouncer si métriques > 40 connections actives | > 40 connections actives p95 |
| Production scale | v0.5 | PgBouncer mode transaction si multi-instance | Multi-instance API |

Configuration exacte v0.1 :
```python
engine = create_async_engine(
    DATABASE_URL,
    poolclass=AsyncAdaptedQueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,  # Vérifie la validité avant usage
    echo=False,
)
```

### 4. Action

| Action | Responsable | Deadline | Détails |
|---|---|---|---|
| A9.1 — Configurer engine SQLAlchemy avec pool optimisé | BACK | v0.1-alpha | Fichier `core/database.py` avec la configuration exacte. |
| A9.2 — Monitoring des connections actives | DEVOPS | v0.1-beta | Métrique `sqlalchemy_pool_size`, `sqlalchemy_overflow`, `sqlalchemy_checkedout`. Alertes si > 25 connections. |
| A9.3 — Évaluation PgBouncer | DBA | v0.3 | POC avec conteneur Docker, test de compatibilité asyncpg, benchmark. |

---

## Q10 — Sécurité multi-tenant (tenant_id) : RLS + middleware

### 1. Positions

**BACK — Backend Senior** (Position : middleware FastAPI + RLS PostgreSQL)  
> "Le multi-tenant dans TAKA OS est critique : un utilisateur de SPIE ne doit jamais voir les AO d'Equans. La défense doit être en profondeur. Couche 1 : middleware FastAPI qui injecte `tenant_id` depuis le JWT token dans le `request.state`. Couche 2 : chaque requête SQLAlchemy filtre automatiquement sur `tenant_id`. Couche 3 : Row Level Security (RLS) PostgreSQL qui rejette toute requête sans `tenant_id` correspondant. Avec RLS activé, même un développeur avec accès psql ne peut pas lire les données d'un autre tenant sans SET le bon `app.current_tenant`."

**DBA — Database Engineer** (Position : RLS obligatoire, pas optionnel)  
> "Le RLS n'est pas optionnel, c'est obligatoire. Sans RLS, une injection SQL ou une erreur de filtre côté application expose toutes les données de tous les tenants. L'histoire des SaaS est remplie de breaches multi-tenant dues à un `WHERE tenant_id = ?` oublié. RLS est la dernière ligne de défense. Configuration : `CREATE POLICY tenant_isolation ON appel_offres USING (tenant_id = current_setting('app.current_tenant')::UUID);`. Chaque connection SQLAlchemy fait `SET app.current_tenant = 'xxx'` au checkout du pool."

**SYS — Architecte Système** (Position : performance impact de RLS)  
> "RLS a un impact performance. Chaque requête ajoute un prédicat implicite. Sur une table avec 10M lignes, le planner doit tenir compte du RLS pour chaque plan d'exécution. Cela peut désactiver certains index ou changer les plans. Il faut des tests de performance avant et après RLS. Et les super-admins (rôle Super Admin) doivent avoir une policy BYPASS."

### 2. Débat

**BACK réplique** : "L'impact RLS est mesurable mais faible. Les benchmarks PostgreSQL montrent un overhead < 5% pour des policies simples (égalité sur UUID). Notre policy `tenant_id = current_setting(...)` est exactement ce cas. L'index B-tree sur `tenant_id` est utilisé normalement."

**DBA ajoute** : "Et pour les super-admins, une policy `FOR ROLE superadmin USING (true)` bypass tout. C'est standard."

**SYS** : "D'accord sur le principe. Mais ajoutons une contrainte : le `tenant_id` doit être présent dans TOUS les modèles SQLAlchemy via un mixin `TenantMixin`. Aucune table ne doit pouvoir exister sans `tenant_id` nullable=False."

### 3. Décision

**Verdict : GO — RLS + middleware + TenantMixin obligatoires**

| Couche | Mécanisme | Implémentation |
|---|---|---|
| 1. Authentification | JWT avec claim `tenant_id` | Token contient `tenant_id`, `business_line_ids`, `role` |
| 2. Middleware FastAPI | `TenantMiddleware` extrait `tenant_id` du JWT, le stocke dans `request.state.tenant_id` | Avant chaque route protégée |
| 3. SQLAlchemy session | `session.execute(text("SET app.current_tenant = :tid"), {"tid": tenant_id})` au `session.begin()` | Hook sur `before_cursor_execute` |
| 4. Filtre application | `TenantMixin` ajoute `tenant_id: Mapped[UUID]` à tous les modèles | `query.filter_by(tenant_id=tenant_id)` par défaut |
| 5. RLS PostgreSQL | Policy `tenant_isolation` sur chaque table multi-tenant | Activation automatique via migration |
| 6. Bypass admin | Policy `admin_bypass` pour rôle Super Admin | `FOR ROLE superadmin USING (true)` |
| 7. Audit | Log de bypass RLS | Table `audit_rls_bypass` pour tracer les accès admin |

### 4. Action

| Action | Responsable | Deadline | Détails |
|---|---|---|---|
| A10.1 — Créer TenantMixin | BACK | v0.1-alpha | `tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenant.id"), nullable=False, index=True)` |
| A10.2 — Implémenter TenantMiddleware FastAPI | BACK | v0.1-alpha | Extraction JWT, validation tenant access, stockage request.state. |
| A10.3 — Activer RLS sur toutes les tables multi-tenant | DBA | v0.1-beta | Migration Alembic avec `CREATE POLICY` par table. |
| A10.4 — Hook SQLAlchemy pour SET tenant | BACK | v0.1-beta | `event.listen(engine, "connect", set_tenant_on_connect)` |
| A10.5 — Tests de non-régression RLS (tentative accès croisé) | BACK | v0.1-rc | Test : utilisateur tenant A tente de lire données tenant B → doit échouer avec RLS. |
| A10.6 — Audit log pour bypass admin | BACK | v0.2 | Table `audit_rls_bypass` avec timestamp, admin_id, table, action. |

---

## Q11 — Swarm Registry v0.5 : quand passer à backend distribué ?

### 1. Positions

**SYS — Architecte Système** (Position : Redis backend v0.4)  
> "Le Swarm Registry v0.5+ stocke l'état des agents, leurs capacités, et leur disponibilité. Actuellement c'est en mémoire Python (dict). Quand nous aurons 2+ instances de l'API, le Registry en mémoire diverge : l'instance A pense que l'agent Veilleur est sur l'instance A, mais il est sur l'instance B. Il faut un backend partagé. Redis est le choix naturel : pub/sub pour les changements d'état, SET pour les registres, EXPIRE pour le heartbeat. Transition en v0.4 pour être prêt pour la v0.5 multi-instance."

**DEVOPS — DevOps Engineer** (Position : NATS KV comme alternative)  
> "Redis est bien, mais NATS JetStream KV (Key-Value) est mieux intégré à notre future stack v0.5. Si nous passons à NATS pour l'EventBus en v0.5, utiliser NATS KV pour le Swarm Registry évite d'ajouter Redis. NATS KV supporte TTL, watch (notifications de changement), et est déjà repliqué si NATS est en cluster. C'est un argument de cohérence technologique."

**BACK — Backend Senior** (Position : abstraction du registry backend)  
> "Peu importe Redis ou NATS KV. Ce qui compte est l'abstraction. Un `SwarmRegistryBackend` protocol avec `register()`, `deregister()`, `heartbeat()`, `discover()`, `watch()`. L'implémentation in-memory pour v0.1-v0.3, Redis pour v0.4, NATS KV pour v0.5. Le swap est transparent pour le code métier."

### 2. Débat

**SYS réplique à DEVOPS** : "NATS KV est intéressant, mais c'est de la tech très récente (v2.10+). La documentation est limitée. Redis est battle-tested depuis 15 ans. Pour un composant aussi critique que le Swarm Registry, je privilégie la maturité."

**DEVOPS réplique** : "NATS 2.10 est sorti en 2023. Ça fait 18 mois. Et NATS est utilisé par Siemens, Tesla, VMware en production. Ce n'est pas de l'expérimental."

**SYS** : "D'accord sur la maturité NATS en général. Mais NATS KV spécifiquement est moins utilisé que Redis. Mon point est : commençons par l'abstraction, implémentons Redis en v0.4, et gardons NATS KV comme option en v0.5 si l'intégration EventBus+KV est fluide."

### 3. Décision

**Verdict : DIFFERE — Abstraction en v0.2, Redis backend en v0.4, NATS KV évalué en v0.5**

| Phase | Version | Backend | Justification |
|---|---|---|---|
| MVP | v0.1-v0.3 | In-memory (dict) | Mono-instance, pas de besoin de partage |
| Growth | v0.4 | Redis | Maturité, TTL, pub/sub, préparation multi-instance |
| Scale | v0.5 | Évaluation NATS KV | Si NATS JetStream est déjà en place pour EventBus, cohérence tech |

### 4. Action

| Action | Responsable | Deadline | Détails |
|---|---|---|---|
| A11.1 — Définir protocol SwarmRegistryBackend | SYS | v0.2-alpha | Abstract class avec register/deregister/heartbeat/discover/watch. |
| A11.2 — Implémenter InMemoryRegistry | BACK | v0.2-alpha | Dict Python avec locks asyncio. |
| A11.3 — Implémenter RedisRegistry | BACK | v0.4-alpha | Redis avec redis-py async, TTL, pub/sub pour watch. |
| A11.4 — POC NATS KV Registry | DEVOPS | v0.4-beta | Implémentation alternative, benchmark vs RedisRegistry. |

---

## Q12 — Scoring Engine V2 : calibration et validation

### 1. Positions

**ML — ML Engineer** (Position : calibration nécessaire avant production)  
> "Le Scoring Engine V2 avec 5 dimensions YAML et 3 profils est bien conçu sur le papier. Mais les poids des dimensions (ex: Prix 40%, Technique 30%, Délai 15%, Garantie 10%, Innovation 5%) sont des hypothèses. Sans calibration sur des données réelles, le scoring est arbitraire. Il faut un dataset interne de 500 AO historiques avec les vrais scores (gagné/perdu, montant, retour client). Sur ces 500 AO, nous calibrons les poids et les seuils par profil."

**DATA — Architecte Data** (Position : A/B testing en production)  
> "La calibration interne est utile mais insuffisante. Le vrai test est en production : A/B testing où 50% des AO utilisent le scoring V2 et 50% la méthode manuelle de l'utilisateur. Nous mesurons la corrélation entre le score prédit et le résultat réel. Mais c'est éthiquement sensible : si le scoring V2 est mauvais, nous avons conseillé mal un client. Il faut un mode 'shadow' où le scoring V2 s'exécute en parallèle sans impacter la décision utilisateur."

**AI — AI Engineer** (Position : scoring hybride ML + règles)  
> "Le scoring V2 est 100% règles (YAML). C'est interprétable mais limité. En v0.3, nous devons évaluer un scoring hybride : les 5 dimensions restent, mais les poids sont ajustés par un modèle léger (ex: logistic regression sur les features extraites de l'AO). Le modèle apprend des 500 AO historiques. C'est du ML supervisé simple, pas du deep learning. Et ça reste interprétable avec SHAP ou feature importance."

### 2. Débat

**ML réplique au DATA** : "Le shadow mode est la bonne approche. Mais il faut le définir clairement : le scoring V2 calcule un score, l'affiche à l'utilisateur avec un disclaimer 'score expérimental', mais ne bloque pas l'action. L'utilisateur peut ignorer le score. Nous collectons le feedback implicite (l'utilisateur a suivi le score ou pas ?)."

**DATA** : "Exact. Et le dataset de 500 AO doit être diversifié : AO publics, AO privés, petits marchés (< 100K€), gros marchés (> 5M€), différents secteurs (BTP, IT, services). Un modèle calibré uniquement sur du BTP public sera mauvais sur du IT privé."

**SYS** : "Qui fournit les 500 AO ? Ce sont des données clients sensibles. Nous ne pouvons pas utiliser les AO de nos clients beta sans consentement explicite."

**BACK** : "Le consentement est dans les CGU v0.2. Et les AO utilisés pour la calibration sont anonymisés : suppression du nom du client, du lieu précis, des montants exacts (remplacés par des fourchettes)."

### 3. Décision

**Verdict : GO — Scoring V2 règles en v0.2, calibration v0.3, ML hybride v0.4**

| Phase | Version | Scoring | Méthode |
|---|---|---|---|
| MVP | v0.2 | Règles YAML, poids par défaut | Interprétable, pas de calibration nécessaire |
| Calibration | v0.3 | Règles YAML, poids ajustés sur dataset 500 AO | Shadow mode, collecte feedback utilisateur |
| ML hybride | v0.4 | Règles + logistic regression | Features : dimensions YAML + metadata AO. SHAP pour interprétabilité. |
| Avancé | v0.6+ | Évaluation gradient boosting / XGBoost | Si LR insuffisant, modèle plus complexe avec régularisation |

Règles de calibration :
1. Dataset : 500 AO minimum, diversifiés secteur/montant/type
2. Anonymisation obligatoire avant stockage dans dataset
3. Shadow mode : score affiché comme "expérimental", décision utilisateur non contrainte
4. Métrique principale : AUC-ROC sur prédiction gagné/perdu
5. Métrique secondaire : correlation score / marge réalisée

### 4. Action

| Action | Responsable | Deadline | Détails |
|---|---|---|---|
| A12.1 — Implémenter Scoring Engine V2 règles | BACK | v0.2-alpha | 5 dimensions YAML, 3 profils, ScoreCard. Engine Python pur. |
| A12.2 — Collecte dataset 500 AO anonymisé | DATA | v0.2-beta | Process d'anonymisation, stockage dans `datasets/scoring_v2/`. |
| A12.3 — Implémenter shadow mode scoring | BACK | v0.3-alpha | Flag `shadow=True` sur l'appel scoring, résultat loggué mais non bloquant. |
| A12.4 — Script de calibration des poids | ML | v0.3-beta | Optimisation des poids par profil sur le dataset. Grid search + validation croisée. |
| A12.5 — POC scoring hybride LR | ML | v0.4-alpha | Features depuis YAML + metadata. scikit-learn. SHAP analysis. |
| A12.6 — Métriques scoring dashboard | DEVOPS | v0.3 | Grafana : AUC-ROC par profil, correlation score/résultat, taux de suivi du score. |

---

## Synthèse des actions prioritaires

### Actions critiques (bloquantes pour v0.1)

| ID | Action | Responsable | Deadline | Priorité |
|---|---|---|---|---|
| A1.1 | EventBus asyncio + persistance PostgreSQL | BACK | v0.1-beta | CRITIQUE |
| A1.2 | Interface abstraite EventBus | SYS | v0.1-alpha | CRITIQUE |
| A2.1 | Index HNSW pgvector | DBA | v0.1-alpha | CRITIQUE |
| A3.1 | Structure fichiers modèles | BACK | v0.1-beta | CRITIQUE |
| A4.1 | LLMClient 3 providers | AI | v0.1-beta | CRITIQUE |
| A4.5 | Table llm_call_log | BACK | v0.1-rc | CRITIQUE |
| A8.1 | CircuitBreaker class | BACK | v0.2-alpha | CRITIQUE |
| A9.1 | Engine SQLAlchemy pool | BACK | v0.1-alpha | CRITIQUE |
| A10.1 | TenantMixin | BACK | v0.1-alpha | CRITIQUE |
| A10.2 | TenantMiddleware | BACK | v0.1-alpha | CRITIQUE |
| A10.3 | RLS PostgreSQL | DBA | v0.1-beta | CRITIQUE |
| A10.5 | Tests RLS non-régression | BACK | v0.1-rc | CRITIQUE |
| A5.1 | Docker Compose production | DEVOPS | v0.1-beta | CRITIQUE |
| A6.1 | Versions exactes package.json | FRONT | v0.1-beta | CRITIQUE |

### Actions importantes (v0.2)

| ID | Action | Responsable | Deadline | Priorité |
|---|---|---|---|---|
| A1.3 | POC LISTEN/NOTIFY | DBA | v0.1-rc | IMPORTANT |
| A2.3 | Benchmark embedding | ML | v0.1-rc | IMPORTANT |
| A3.2 | Migration modèles split | BACK | v0.2-alpha | IMPORTANT |
| A3.4 | Linter anti-circulaire | DEVOPS | v0.2-beta | IMPORTANT |
| A4.2 | Switch automatique provider | AI | v0.2-alpha | IMPORTANT |
| A4.3 | Versionnement prompts | AI | v0.2-alpha | IMPORTANT |
| A4.4 | Tests CI multi-provider | DEVOPS | v0.2-beta | IMPORTANT |
| A7.1 | TTL mémoire épisodique | BACK | v0.2-alpha | IMPORTANT |
| A7.2 | Cron purge mémoire | DEVOPS | v0.2-alpha | IMPORTANT |
| A8.2 | CB dans LLMClient | AI | v0.2-alpha | IMPORTANT |
| A8.3 | Rate limiter provider | AI | v0.2-beta | IMPORTANT |
| A11.1 | Protocol SwarmRegistry | SYS | v0.2-alpha | IMPORTANT |
| A12.1 | Scoring Engine V2 | BACK | v0.2-alpha | IMPORTANT |

---

## Risques et mitigations identifiés

| Risque | Probabilité | Impact | Mitigation | Responsable |
|---|---|---|---|---|
| Perte d'événements en mémoire (crash serveur) | Moyenne | Critique | Persistance PostgreSQL + recovery service (A1.1) | BACK |
| Dégradation pgvector à fort volume | Moyenne | Élevé | Partitionnement v0.3 (A2.4), veille Qdrant | DBA |
| Vendor lock-in Mistral (prix/fermeture) | Faible | Critique | Multi-provider + OpenRouter fallback (A4.1-A4.2) | AI |
| Fuite données cross-tenant | Faible | Critique | RLS + TenantMiddleware + tests (A10.x) | BACK/DBA |
| Circuit breaker trop agressif/lent | Moyenne | Élevé | Configuration 3/30/60 testée (A8.4) | BACK |
| Shadcn/ui breaking changes | Moyenne | Moyen | Versions pinnées, migration planifiée (A6.1) | FRONT |
| Mémoire épisodique non fiable (TTL naïf) | Élevée | Moyen | Shadow mode, disclaimer, itération (A7.3) | ML |
| Scaling Docker Compose insuffisant | Moyenne | Élevé | Benchmark charge v0.4 (A5.5), ADR K8s v0.3 (A5.4) | INFRA |

---

## Prochaines réunions planifiées

| Réunion | Date cible | Ordre du jour |
|---|---|---|
| Architecture & Technique — Revue v0.1 | Fin sprint v0.1 | Validation des actions critiques, revue des métriques RLS/pool/pgvector |
| Architecture & Technique — Plan v0.2 | Début v0.2 | EventBus LISTEN/NOTIFY, split modèles, LLMClient fallback, CB, mémoire TTL |
| Architecture & Technique — Revue v0.2 | Fin sprint v0.2 | Validation scoring V2, circuit breaker, multi-tenant tests |
| Architecture & Technique — Plan v0.3 | Début v0.3 | Partitionnement pgvector, calibration scoring, PgBouncer, Swarm Redis |

---

## Glossaire

| Terme | Définition |
|---|---|
| **AO** | Appel d'Offres |
| **CB** | Circuit Breaker |
| **RLS** | Row Level Security (PostgreSQL) |
| **HNSW** | Hierarchical Navigable Small World (index pgvector) |
| **TTL** | Time To Live (durée de vie) |
| **MVP** | Minimum Viable Product |
| **ADR** | Architecture Decision Record |
| **SPOF** | Single Point of Failure |
| **LRU** | Least Recently Used |
| **HA** | High Availability |
| **SLA** | Service Level Agreement |
| **TCO** | Total Cost of Ownership |

---

*Document validé par le Groupe Architecture & Technique*  
*Signatures virtuelles : SYS, DATA, BACK, DEVOPS, AI, ML, DBA, INFRA*  
*Cycle : KIMI-TAKA-SWARM Architecture & Technique*


---

## Annexe A — Matrice de décision consolidée

### Tableau récapitulatif exhaustif

| Question | Thème technique | Décision | Version cible | GO / NO-GO / DIFFERE | Responsable validation | Deadline validation |
|---|---|---|---|---|---|---|
| Q1 | EventBus asyncio in-memory vs persistance | DIFFERE — asyncio pur + PG persistence v0.1, LISTEN/NOTIFY v0.2, NATS v0.5 | v0.1 / v0.2 / v0.5 | DIFFERE | SYS | v0.2-rc |
| Q2 | pgvector HNSW performances 10K+ AO | GO — HNSW simple v0.1, composite v0.2, partitionnement v0.3 | v0.1 / v0.2 / v0.3 | GO | DATA | v0.3-rc |
| Q3 | Modèles SQLAlchemy mono vs multi-fichiers | GO — Split par domaine avec ré-export centralisé | v0.2 | GO | SYS | v0.2-rc |
| Q4 | Vendor lock-in Mistral AI API | GO — Multi-provider (Mistral direct → OpenRouter → queue async) | v0.2 | GO | AI | v0.2-rc |
| Q5 | Docker Compose vs Kubernetes | DIFFERE — Compose v0.1-v0.6, K8s évalué v0.7 | v0.7 | DIFFERE | SYS | v0.6-rc |
| Q6 | React 18 + Vite + Tailwind pérennité | GO — Versions exactes pinnées, migration planifiée semestrielle | v0.5 | GO | SYS | v0.5-rc |
| Q7 | Mémoire épisodique TTL/oubli v0.2 | GO — TTL par catégorie v0.2, LRU v0.3, oubli probabiliste v0.4 | v0.2 / v0.3 / v0.4 | GO | ML | v0.4-rc |
| Q8 | Circuit Breaker Mistral API | GO — 3 échecs/30s, ouverture 60s, half-open 1 requête, par agent | v0.2 | GO | BACK | v0.2-rc |
| Q9 | Async SQLAlchemy 2.0 connection pooling | GO — AsyncAdaptedQueuePool pool_size=10, max_overflow=20, PgBouncer v0.3 | v0.1 / v0.3 | GO | DBA | v0.3-rc |
| Q10 | Sécurité multi-tenant RLS + middleware | GO — TenantMixin + TenantMiddleware + RLS PG + bypass audit | v0.1 / v0.2 | GO | BACK | v0.1-rc |
| Q11 | Swarm Registry backend distribué | DIFFERE — In-memory v0.1-v0.3, Redis v0.4, NATS KV évalué v0.5 | v0.4 / v0.5 | DIFFERE | SYS | v0.5-rc |
| Q12 | Scoring Engine V2 calibration | GO — Règles v0.2, calibration dataset 500 AO v0.3, ML hybride v0.4 | v0.2 / v0.3 / v0.4 | GO | ML | v0.4-rc |

### Principes architecturaux validés par le groupe

1. **Mesurer avant d'optimiser** — Aucune optimisation prématurée (PgBouncer, K8s, partitionnement) sans métriques de charge réelles.
2. **Abstraction avant implémentation** — Chaque composant potentiellement swappable (EventBus, LLMClient, SwarmRegistry, Scoring) expose un protocol/abstract class.
3. **Défense en profondeur** — Sécurité multi-tenant avec 3 couches : application (middleware), ORM (filtres), base de données (RLS).
4. **Shadow mode pour le ML** — Toute feature ML/IA à impact métier s'exécute d'abord en mode shadow avec collecte de feedback.
5. **Pinner, ne pas suivre latest** — Toutes les dépendances critiques en versions exactes, migration planifiée par ADR.
6. **Mono-instance jusqu'à preuve du contraire** — Pas de distributed computing avant mesure de la nécessité (swarm registry, EventBus).

---

## Annexe B — Diagramme de séquence des actions critiques v0.1

```
[Sprint v0.1] Semaines 1-4
├── Semaine 1
│   ├── BACK : Engine SQLAlchemy pool (A9.1)
│   ├── BACK : TenantMixin (A10.1)
│   ├── BACK : TenantMiddleware (A10.2)
│   └── SYS : Interface EventBus (A1.2)
├── Semaine 2
│   ├── DBA : Index HNSW pgvector (A2.1)
│   ├── BACK : EventBus asyncio + persistance (A1.1)
│   ├── BACK : Structure fichiers modèles (A3.1)
│   └── AI : LLMClient 3 providers (A4.1)
├── Semaine 3
│   ├── DBA : RLS PostgreSQL (A10.3)
│   ├── BACK : Table llm_call_log (A4.5)
│   ├── DEVOPS : Docker Compose prod (A5.1)
│   └── FRONT : Versions exactes package.json (A6.1)
└── Semaine 4
    ├── BACK : Tests RLS non-régression (A10.5)
    ├── BACK : Hook SQLAlchemy SET tenant (A10.4)
    ├── DBA : POC LISTEN/NOTIFY (A1.3)
    ├── ML : Benchmark embedding (A2.3)
    └── SYS : Revue architecture v0.1
```

---

## Annexe C — Checklist de validation avant merge v0.1

- [ ] EventBus persiste chaque événement dans PostgreSQL avant publish
- [ ] Recovery service relit la table `events` au boot et rejoue les non-traités
- [ ] Index HNSW créé sur `chunks.embedding` avec m=16, ef_construction=200
- [ ] Requête `search_similar_chunks` utilise CTE pré-filtrage par tenant_id
- [ ] `models/` est structuré en 9 fichiers avec ré-export centralisé
- [ ] Aucun import circulaire détecté par le linter
- [ ] LLMClient supporte Mistral direct et OpenRouter avec switch runtime
- [ ] Table `llm_call_log` enregistre provider, tokens, latence, coût
- [ ] TenantMiddleware extrait tenant_id du JWT et le stocke dans request.state
- [ ] RLS activé sur toutes les tables multi-tenant avec policy tenant_isolation
- [ ] Bypass admin audité dans `audit_rls_bypass`
- [ ] Docker Compose prod avec healthchecks, restart policies, secrets
- [ ] package.json utilise des versions exactes (pas ^ ni ~)
- [ ] Métriques Prometheus exposées pour pool SQLAlchemy, EventBus, LLM calls

---

*Fin du compte-rendu — Groupe Architecture & Technique — KIMI-TAKA-SWARM*
