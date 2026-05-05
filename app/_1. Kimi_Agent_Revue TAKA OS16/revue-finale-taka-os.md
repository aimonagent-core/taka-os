# TAKA OS — Revue Finale Avant Developpement
## Document de synthese CTO | Mai 2026

---

## RESUME EXECUTIF POUR LE CEO

TAKA OS est **GO CONDITIONNEL**. L'audit multi-dimension (concurrence, reglementation, technique) converge vers un verdict : le projet est viable, la faille bleue ocean existe, mais **trois ajustements critiques** doivent etre faits AVANT le premier commit. Si tu les valides, on code demain.

| Dimension | Score | Seuil | Statut |
|-----------|-------|-------|--------|
| Architecture technique | 8.5/10 | 6/10 | GO |
| Differenciation vs concurrence | 8/10 | 6/10 | GO |
| Viabilite reglementaire EU | 7.5/10 | 6/10 | GO |
| Utilite metier | 7/10 | 6/10 | GO |
| Facilite deploiement MVP | 7/10 | 6/10 | GO |
| Adoptabilite PME | 6.5/10 | 6/10 | GO |
| Viabilite economique | 6.5/10 | 6/10 | GO |

**Verdict global : GO — sous reserve des 3 prerequis ci-dessous.**

---

## PREREQUIS #1 : REMPLACER KIMI API PAR MISTRAL AI (ou self-hosted EU)

**C'est non-negociable.** L'analyse reglementaire est sans appel.

| Risque Kimi API (Chine) | Niveau | Consequence |
|------------------------|--------|-------------|
| Transfert RGPD vers pays non-adequat | CRITIQUE | Sanctions jusqu'a 20M EUR ou 4% du CA |
| Acces potentiel autorites chinoises | CRITIQUE | Loi chinoise cybersurete 2017 + loi securite des donnees 2021 |
| Distillation industrielle (accusation US avril 2026) | ELEVEE | Risque geopolitique, restrictions croissantes |
| Conflit souverainete numerique EU | ELEVEE | Incompatible avec le positionnement "OS souverain" |

**La solution : Mistral AI (France)**
- API hebergee en France/UE, conforme RGPD native
- Modeles Mistral Large / Medium disponibles via API
- Alternative : Mixtral 8x22B ou Llama 4 self-hosted sur le VPS (zero donnee sortante)
- Cout comparable a Kimi, qualite equivalente pour du parsing/du scoring

**Impact sur le code :** Remplacer `llm_base_url` et `llm_model` dans la config. Aucun impact architectural. Le client httpx + Jinja2 est agnostique du provider.

**Ma recommandation CTO :** Commencer avec l'API Mistral (zero friction), basculer sur un modele local quand on a >50 clients et que le cout LLM devient significatif.

---

## PREREQUIS #2 : VALIDER LE DECOUPAGE 4 SEMAINES (et pas plus)

Le risque #1 de mort de TAKA OS, comme NEXA-MIND avant lui, c'est la **sur-ingenierie**. Voici le plan verrouille, point par point.

### Semaine 1 — OS de Fondation (Kernel + Auth + DB)
- pyproject.toml, structure de projet, config Pydantic-Settings
- PostgreSQL + pgvector, Alembic migrations, 7 tables SQL
- Auth JWT (dev-login + login reel), RBAC basique
- EventBus in-memory asyncio, Health checks
- **Livrable** : API qui demarre, auth fonctionnel, tests verts

### Semaine 2 — Sensorimotrice + Memoire
- Upload PDF/UBL, pipeline de parsing stratifie (pypdf -> pdfplumber -> OCR fallback)
- Extraction regles d'abord (CPV, montant, deadline, criteres) + LLM fallback pour champs manquants
- pgvector : stockage embeddings DCE, recherche similarite (index HNSW)
- **Livrable** : POST /ao/parse-pdf retourne JSON structure, recherche similarite fonctionnelle

### Semaine 3 — Agent Qualifieur + Pipeline Kanban
- Scoring GO/NO-GO (80% regles : CPV referentiel, fourchette montant, deadline, memoire episodique / 20% LLM fallback cas ambigus)
- Pipeline Kanban : 8 stages, API changement d'etat
- Dashboard React : liste AO, fiche detail, filtres
- **Livrable** : DCE uploade -> score GO/NO-GO/MAYBE en <5s (regles) ou <10s (LLM)

### Semaine 4 — Agent Tracker + SaaS Packaging
- Alertes email (7j/3j/1j avant deadline), relances
- Audit trail complet, badge IA (AI Act Art. 50), checkbox validation humaine
- Docker-compose production, seed script, README, LICENCE MIT
- **Livrable** : v0.1 taggee, deployable en 5 minutes sur VPS

### CE QUI EST EXCLU DE V0.1 (planifie pour v0.2/v0.3)
- Deliberation parlementaire (v0.3)
- TAKA LAB auto-ameliorant (v0.2 : logs de scores seulement)
- Generation automatique de memoires techniques (v0.2 : assistant copilote uniquement)
- Connecteurs places de marche payants (v0.2 : upload manuel + parsing)
- CrewAI (jamais, sauf si besoin specifique prouve)
- Redis/NATS/Qdrant/Neo4j (jamais avant 50+ users)
- Multi-tenancy RLS PostgreSQL (v0.2, application-level suffit en v0.1)

---

## PREREQUIS #3 : ACCEPTER 3 DECISIONS TECHNIQUES NON-NEGOCIABLES

Ces 3 points ont fait echouer NEXA-MIND. Ils ne feront pas echouer TAKA OS.

### Decision 1 : expire_on_commit=False (obligatoire)
```python
async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # SANS CECI, NEXA-MIND EST MORT
    autocommit=False,
    autoflush=False,
)
```
**Pourquoi :** Sans ce flag, SQLAlchemy tente de "recharger" les objets apres un commit en mode async, ce qui declenche des lazy loading errors en cascade. C'est le bug #1 de NEXA-MIND.

### Decision 2 : Circuit breaker sur TOUS les appels LLM (obligatoire)
```python
@retry(stop=stop_after_attempt(3), wait=wait_exponential_jitter(initial=1, max=10))
async def complete(self, prompt: str) -> str:
    if not self.circuit.can_execute():
        raise CircuitOpenError("LLM indisponible — scoring regles uniquement")
    # ... appel API avec timeout 30s
```
**Pourquoi :** Un timeout LLM = l'API bloquee 30s+ = l'utilisateur ferme l'onglet. Un circuit breaker ouvert = fallback immediat sur le scoring regles (80% des cas fonctionnent sans LLM).

### Decision 3 : Parsing PDF en tache de fond asynchrone (obligatoire)
```python
@app.post("/tenders/upload")
async def upload_document(file: UploadFile):
    # 1. Sauvegarde du fichier (instantane)
    doc_id = await save_file(file)
    # 2. Lancement parsing en background (pas bloquant)
    asyncio.create_task(parse_document_background(doc_id))
    # 3. Reponse immediate a l'utilisateur
    return {"id": doc_id, "status": "parsing_en_cours"}
```
**Pourquoi :** Un DCE de 200 pages peut prendre 10-30s a parser. Si l'API attend, le client (React) timeout apres 10s. L'utilisateur voit "Analyse en cours..." et recoit une notification quand c'est pret.

---

## ANALYSE CONCURRENCE — FAILLE BLEUE OCEAN CONFIRMEE

### Le marche en chiffres (2026)
- Marche RFP software global : 3.55 Mds USD (2025) -> 7.61 Mds USD (2034), CAGR 10%
- PME francaises candidates regulieres : ~60 000 (BTP, services, conseil, IT, securite)
- Belgique : ~8 000-12 000 candidates supplementaires
- 39% des PME francaises utilisent deja l'IA (+15 points en 1 an)
- **52% craignent le vol de donnees, 32% exigent un fournisseur EU**

### Les 2 concurrents a surveiller

**Tenderbolt.AI (France, 2024)** — DANGEREUX
- Prix : 500-2 000 EUR/mois (estime, sales-led, opaque)
- Forces : leader EU marches publics, analyse CCTP/CCAP, generation memoire technique, SOC2
- Faiblesses : pas open source, pas de Kanban natif, pas de memoire vectorielle explicite, prix PME inaccessible
- Position vs TAKA OS : ils font la reponse, TAKA OS fait tout le cycle (veille -> qualif -> suivi) a 10-20x moins cher

**Nextend.ai (France)** — DANGEREUX
- Prix : 200-1 500 EUR/mois (estime)
- Forces : le plus complet du marche francais, DC1/DC2 automatises, coordination groupements, infra France
- Faiblesses : pas open source, pas de Kanban mentionne, probablement cher pour PME
- Position vs TAKA OS : ils sont plus avances sur la generation de reponses. TAKA OS gagne sur le prix, l'open source, le Kanban, et la memoire episodique.

### Notre positionnement unique (les 3 piliers)

1. **Open Source MIT + Self-Hosted + Souverainete EU** = AUCUN concurrent ne combine les trois. C'est un fossé defensif qu'on peut creuser avec une communaute.

2. **Architecture 3 couches agentic integree** (Veille + Qualification + Suivi Kanban) = Tenderbolt/Nextend couvrent qualif+reponse mais pas le suivi pipeline. Tendium fait veille+qualif mais pas Kanban. Personne ne fait les 3.

3. **Prix 10-20x inferieur** : 49-499 EUR/mois vs 500-2 000 EUR pour les solutions AI equivalentes. Le plan Solo a 49 EUR/mois capte les PME qui utilisent Excel+alertes mail.

### Verdict concurrence

> **FENÊTRE DE 12-18 MOIS.** La faille existe aujourd'hui mais se resserre. Tenderbolt et Nextend sont bien financés et peuvent ajouter un Kanban ou baisser leurs prix. L'open source + la communaute sont la seule defense durable. **Il faut avancer vite.**

---

## ANALYSE REGLEMENTAIRE — VIABLE AVEC 3 AJUSTEMENTS

### AI Act (applicable aout 2026) — Risque limite
TAKA OS est classifie **"risque limite"** (Article 50). Uniquement des obligations de transparence :
- Badge "Assistant IA — TAKA OS" visible des la 1re interaction
- Marquage des suggestions generees par IA
- Disclaimer dans l'interface et les exports

**Sanction si non-conforme** : jusqu'a 7.5 M EUR ou 1% du CA mondial. Mitigation : badge + metadata + footer sur exports. Cout : 2 heures de dev frontend.

### RGPD — EXCELLENT en mode self-hosted
Le modele open source self-hosted est le meilleur modele RGPD possible :
- Donnees sous controle de l'utilisateur (serveur EU)
- Zero transfert international (si stack EU + Mistral)
- Droit a l'oubli = suppression des vecteurs pgvector (fonction purge a implementer v0.2)
- Portabilite = export PostgreSQL natif

### Marchés publics — Aucune interdiction
Ni la directive EU 2014/24, ni le Code de la commande publique francais, ni la legislation belge n'interdisent l'IA pour preparer une candidature. L'utilisateur reste pleinement responsable du contenu soumis.

### Ce qui est autorise et protégé
- Parsing des DCE : LEGAL (TA Caen 2009 : DCE n'est pas une oeuvre de l'esprit)
- Stockage/vectorisation des DCE : LEGAL (donnees publiques, licence ouverte)
- API BOAMP : LEGAL (licence Etalab v2.0)
- Assistance IA a la redaction : LEGAL (outil d'aide, pas de decision automatisee)

### 3 risques juridiques a adresser

| Rang | Risque | Mitigation | Delai |
|------|--------|------------|-------|
| 1 | LLM chinois (Kimi) -> RGPD | **Remplacer par Mistral AI** | S1 |
| 2 | Transparence AI Act Art. 50 | Badge IA + metadata + disclaimer | S4 |
| 3 | Hallucination LLM | Checkbox validation humaine + audit trail + clause non-responsabilite MIT | S3-S4 |

---

## ANALYSE TECHNIQUE — ARCHITECTURE VIABLE (Score 4.2/5)

### Ce qui marche
- **FastAPI + SQLAlchemy 2.0 async** : stack mature, 10K-18K req/s simple, 200-500 req/s avec vecteurs
- **pgvector HNSW** : parfait a l'echelle MVP (~10K vecteurs/tenant), latence 5-15ms, recall 95%+
- **EventBus in-memory + persistance DB** : suffisant pour <50 users, zero dependance externe
- **JWT + refresh token rotation** : pattern de securite eprouve
- **1 VPS 6-8 EUR** : tient la charge pour 10 clients simultanes

### Les 3 risques techniques qui tueraient le projet

#### #1 — Parsing PDF des DCE (LE PLUS GROS RISQUE)
Un DCE public type = 50-300 pages, tableaux complexes, formats variables (PDF texte 60%, PDF scanne 15%, DOCX 15%, ZIP 8%, XML 2%).

| Type de champ | Taux reussite regles | Taux reussite regles+LLM |
|---------------|---------------------|--------------------------|
| CPV | 85-90% | 90-95% |
| Montant | 70-80% | 85-90% |
| Deadline | 75-85% | 90-95% |
| Criteres d'attribution | 50-60% | 80-85% |
| Lots | 60-70% | 75-80% |

**Mitigation** : Pipeline stratifie — pypdf -> pdfplumber -> OCR fallback. Traitement asynchrone (background task). Saisie manuelle possible quand tout echoue. Objectif MVP : >80% de taux de reussite sur CPV + montant + deadline.

#### #2 — Appels LLM sans protection
Sans circuit breaker, un timeout LLM = API bloquee = utilisateur qui part. Sans retry exponentiel, un 502 temporaire = erreur brute exposee.

**Mitigation** : `tenacity` (retry 3x exponentiel) + `CircuitBreaker` (5 failures -> OPEN 60s) + fallback scoring regles immediat.

#### #3 — Sessions async SQLAlchemy (le tueur de NEXA-MIND)
`expire_on_commit=False` OBLIGATOIRE. Pool size = 5 max sur VPS 4GB. `pool_pre_ping=True` pour eviter les connexions zombies. Alembic via `sync_engine`.

---

## STACK TECHNIQUE VERROUILLEE

| Couche | Outil | Alternative exclue |
|--------|-------|-------------------|
| Langage | Python 3.12 (LTS) | Python 3.14 (NEVER) |
| Framework | FastAPI | Django, Flask |
| ORM | SQLAlchemy 2.0 async | SQLAlchemy 1.x (NEVER) |
| Base de donnees | PostgreSQL 15 + pgvector | Qdrant, Redis, Neo4j |
| Index vectoriel | HNSW (pgvector) | IVFFlat (moins bon recall) |
| LLM | Mistral AI API (France) | Kimi API (Chine, NEVER) |
| Appels LLM | httpx + Jinja2 | LangChain, CrewAI |
| Parsing PDF | pypdf + pdfplumber | PyMuPDF (AGPL, risque) |
| Auth | python-jose + passlib | Auth0 (coût) |
| EventBus | asyncio natif + DB outbox | Redis, RabbitMQ, NATS |
| Front | React + Vite + Tailwind | Next.js (trop lourd) |
| Test | pytest + pytest-asyncio | unittest |
| Lint | ruff | black + isort + flake8 |
| Package | poetry | pip |
| Deploiement | Docker compose | Kubernetes (overkill) |
| Infra | VPS Hetzner 6-8 EUR | AWS/GCP (couts) |

---

## MODELE ECONOMIQUE "SMART & CHEAP"

### Couts d'infrastructure (par client, pour toi)

| Poste | Cout mensuel |
|-------|-------------|
| VPS Hetzner CX31 (4vCPU, 8GB, 10 clients) | 8.50 EUR |
| PostgreSQL self-hosted | 0 EUR |
| Backup Hetzner Storage Box 100GB | 3 EUR |
| API Mistral (~500 appels/client) | ~8 EUR/client |
| **Total par client** | **~2-3 EUR infra + 8 EUR LLM = ~10-11 EUR** |

### Prix de vente

| Plan | Prix | Ce qui est inclus | Marge estimée |
|------|------|-------------------|---------------|
| **Solo** | 49 EUR/mois | 1 user, 20 AO/mois, parsing basique | ~35 EUR |
| **Pro** | 149 EUR/mois | 3 users, 100 AO/mois, pgvector actif, similarite | ~125 EUR |
| **Enterprise** | 499 EUR/mois | Illimite, on-premise, support, API | ~450 EUR |

### Seuil de rentabilite
**3 clients Pro = 447 EUR de revenu, ~33 EUR de cout = 414 EUR de marge nette.** Tu es rentable des le 3eme client.

---

## FEUILLE DE ROUTE SI GO

| Jour | Action | Responsable |
|------|--------|-------------|
| J0 (aujourd'hui) | Creer le repo GitHub `taka-os` ou `taka-ao` | CEO (toi) |
| J0 | Ouvrir Issue #1 "Sprint 0 — Fondation" avec le prompt complet | CEO |
| J0 | Configurer .env avec API Mistral (pas Kimi) | CEO |
| J1-J2 | Copier le prompt Sprint 0 dans Kimi Code, iterer | CEO + Kimi Code |
| J3 | **Audit CTO** : review du code produit, checklist 3 risques | CTO (moi) |
| J3-J4 | Corrections + merge sur main | CEO + Kimi Code |
| J5 | Debut Sprint 1 (Sensorimotrice + Memoire) | CEO + Kimi Code |

---

## DECISION EXIGEE DU CEO

Reponds par OUI ou NON a chaque point. Si un seul NON, on discute avant de coder.

| # | Question | Ma recommandation |
|---|----------|-------------------|
| 1 | Remplacer Kimi API par Mistral AI des le Sprint 0 ? | **OUI obligatoire** (risque RGPD) |
| 2 | Valider le decoupage 4 semaines et les exclusions v0.1 ? | **OUI recommande** (eviter sur-ingenierie) |
| 3 | Accepter les 3 decisions techniques non-negociables ? | **OUI obligatoire** (eviter echec NEXA-MIND) |
| 4 | Cibler les PME du BTP et services en priorite ? | **OUI recommande** (46% des marches, sensibles au prix) |
| 5 | Prix d'entree a 49 EUR/mois pour le plan Solo ? | **OUI recommande** (capturer le marche Excel) |

**Si 5 OUI** -> GO immediat. J'envoie le prompt finalise pour Kimi Code et on commence demain.

**Si 1-2 NON** -> On ajuste le concept, pas de probleme. Mieux vaut 2 jours de discussion qu'un echoue de 3 mois.

**Si 3+ NON** -> Le projet dans sa forme actuelle n'est pas viable. Il faut reprendre la conception.

---

*Document de revue produit par le CTO | Synthese de 3 audits parallels (concurrence, reglementation, technique) | Mai 2026*
