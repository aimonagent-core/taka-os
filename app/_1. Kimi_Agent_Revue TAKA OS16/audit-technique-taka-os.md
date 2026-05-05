# AUDIT TECHNIQUE — TAKA OS MVP v0.1
## Architecture Agentic Open Source | Vertical Appels d'Offres

**Date** : Juillet 2025
**Auditeur** : Architecte Logiciel Senior — Python/FastAPI, PostgreSQL, Systèmes Agentic IA
**Version cible** : MVP 4 semaines
**Statut** : PRE-LANCEMENT — Audit préventif post-mortem NEXA-MIND

---

## Contexte & Historique des Échecs (NEXA-MIND)

| Échec NEXA-MIND | Cause racine | Mitigation dans TAKA OS |
|---|---|---|
| Conflits de modules SQLAlchemy | Mélange sync/async, version incompatible | SQLAlchemy 2.0 uniquement async + `expire_on_commit=False` |
| Python 3.14 incompatible | Trop bleeding-edge | Python 3.12 LTS (stable, supporté jusqu'en 2028) |
| Stack trop lourde (4 conteneurs) | Complexité opérationnelle excessive | 1 conteneur app + PostgreSQL intégré |
| Auth cassé | JWT maison mal implémenté, pas de refresh tokens | Pattern refresh token rotation + stockage DB |

---

## 1. FASTAPI + SQLALCHEMY 2.0 ASYNC + POSTGRESQL

### 1.1 Patterns Architecture — Repository + Dependency Injection

**Analyse** : La combinaison FastAPI + SQLAlchemy 2.0 async + repository pattern est éprouvée et documentée. Le pattern `Annotated[..., Depends()]` de FastAPI permet une injection propre des repositories. SQLAlchemy 2.0 avec `async_sessionmaker`, `create_async_engine` et `AsyncSession` fournit une stack async mature.

**Points d'attention critiques** :

```python
# ✅ PATTERN RECOMMANDÉ — Database.py
create_async_engine(
    DATABASE_URL,
    pool_size=5,               # VPS 2-4 vCPU : ne pas dépasser
    max_overflow=2,            # Buffer pour pics
    pool_pre_ping=True,        # VITAL : évite "connection lost"
    pool_recycle=3600,         # Recycle les connexions
    echo=False,                # Production : désactiver
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,    # INDISPENSABLE en async
    autocommit=False,
    autoflush=False,
)

# ✅ Lifespan manager (remplace les on_event dépréciés)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

# ✅ Repository pattern avec DI
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_repo(session: AsyncSession = Depends(get_db)):
    return TenderRepository(session)
```

### 1.2 Performance sur VPS 6-8€ Hetzner

**Analyse chiffrée** :

| Type de requête | Performance attendue (VPS 2 vCPU / 4GB) | Source |
|---|---|---|
| Endpoint "Hello World" (JSON) | 10 000 – 18 000 req/s | Benchmarks TechEmpower / Uvicorn |
| Endpoint DB simple (SELECT) | 800 – 1 500 req/s | Réaliste avec asyncpg + pool |
| Endpoint DB complexe (JOIN+vecteurs) | 200 – 500 req/s | Dominé par PostgreSQL + pgvector |
| Upload PDF + parsing + embedding | 1 – 3 req/s concurrents | Bottleneck : parsing + API LLM |

**Verdict** : Pour un MVP avec peu d'utilisateurs simultanés (<50), le VPS tient largement la route. Le bottleneck ne sera PAS FastAPI mais le parsing PDF et les appels LLM.

### 1.3 Alembic Async — Migrations en Production

**Analyse** : Alembic ne supporte pas nativement l'async. La solution éprouvée : utiliser le `sync_engine` sous-jacent (`async_engine.sync_engine`) pour les migrations. Pas besoin de boucle asyncio dans Alembic.

**⚠️ CRITIQUE — Pattern obligatoire** :

```python
# env.py — Gestion du moteur async pour Alembic
if url.startswith("postgresql+asyncpg"):
    async_engine = create_async_engine(url)
    connectable = async_engine.sync_engine  # Moteur sync sous-jacent
else:
    connectable = engine_from_config(...)
```

**Bonnes pratiques pour les migrations** :
- Toujours vérifier les migrations autogénérées manuellement (renommage de colonnes = data loss)
- Séparer les migrations de schéma des migrations de données
- Ajouter les colonnes en `nullable=True` d'abord, backfill, puis `NOT NULL`
- Pour les grosses tables : `CREATE INDEX CONCURRENTLY` pour éviter les locks
- Toujours implémenter `downgrade` ou lever `NotImplementedError` explicitement

---

| Risque | Niveau | Action corrective |
|---|---|---|
| Oublier `expire_on_commit=False` | 🔴 CRITIQUE | Checklist de code review obligatoire |
| Pool size trop grand sur VPS | 🟡 ATTENTION | `pool_size=5`, `max_overflow=2` maximum |
| Alembic avec asyncpg mal configuré | 🔴 CRITIQUE | Utiliser `sync_engine` dans env.py |
| Pas de `pool_pre_ping` | 🟡 ATTENTION | Connexions "zombie" en production |

---

## 2. PGVECTOR — PERFORMANCE ET LIMITES

### 2.1 IVFFlat vs HNSW — Recommandation pour TAKA OS

**Contexte** : ~10K vecteurs/tenant, embeddings 768 dimensions (typique des modèles sentence-transformers ou API Kimi/OpenAI).

| Critère | IVFFlat | HNSW | Recommandation |
|---|---|---|---|
| Build time | Rapide (secondes) | Lent (minutes) | HNSW OK pour 10K vecteurs |
| Query time | 45ms+ | 5-15ms | **HNSW** |
| Recall (défaut) | 70-80% | 95%+ | **HNSW** |
| Incrémental updates | Se dégrade | Gère bien | **HNSW** |
| RAM index | Compact | 2-5x plus | OK pour 10K vecteurs |
| Besoin de tuning | `lists`, `probes` | `m`, `ef_search` | HNSW plus robuste |

**Recommandation : HNSW, sans hésitation.** À l'échelle de TAKA OS (10K vecteurs/tenant), le build est rapide (<30s), la RAM nécessaire est négligeable (~50-100MB), et le recall est supérieur sans tuning complexe.

```sql
-- ✅ Index HNSW recommandé
CREATE INDEX idx_memory_vectors_embedding
ON memory_vectors USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- ef_construction=64 suffisant pour 10K vecteurs
-- m=16 est le défaut, bien équilibré
```

### 2.2 Requêtes Vectorielles + Filtrage par tenant_id

**Pattern SQL recommandé** :

```sql
-- ✅ AVEC RLS (Row-Level Security) — le tenant_id est implicite
SET app.current_tenant = 'tenant-uuid';
SELECT id, content, embedding <=> query_embedding AS distance
FROM memory_vectors
WHERE embedding <=> query_embedding < 0.3
ORDER BY embedding <=> query_embedding
LIMIT 10;

-- ✅ SANS RLS — filtrage explicite
SELECT id, content, embedding <=> query_embedding AS distance
FROM memory_vectors
WHERE tenant_id = :tenant_id
ORDER BY embedding <=> query_embedding
LIMIT 10;
```

**⚠️ Point critique** : Combiner `WHERE tenant_id = X` avec `ORDER BY embedding <=> query` nécessite que PostgreSQL utilise un index composite ou que le filtre `tenant_id` soit appliqué AVANT le tri vectoriel. Sur 10K vecteurs/tenant, l'impact est minime. Sur 1M+ vecteurs, créer un index partiel par tenant ou utiliser un partitionnement.

### 2.3 Limites de pgvector — Quand basculer ?

| Limite | Seuil de problème | Seuil TAKA OS |
|---|---|---|
| Nombre de vecteurs | >1-10M vecteurs total | ~10K/tenant × N tenants = OK |
| Dimensions | 8KB page = ~1600 floats max | 768 dims = OK |
| Latence p99 | Besoin <10ms | 15-30ms acceptable |
| Index build RAM | HNSW 10GB+ sur millions | Quelques MB = OK |
| Hybrid search | Nécessite FTS manuel | Doable avec tsvector |

**Seuil de bascule vers Qdrant/Milvus** :
- > 1 million de vecteurs total
- Besoin de latence <10ms p99
- Besoin de hybrid search avancé natif
- Besoin de sharding automatique

**Pour TAKA OS MVP : pgvector suffit amplement.** La bascule n'est pas justifiée avant 12-18 mois.

### 2.4 Génération d'Embeddings : API vs Local

| Option | Latence | RAM | Coût | Qualité |
|---|---|---|---|---|
| **Kimi API / OpenAI API** | 50-200ms | 0 | ~0.10€/1M tokens | Excellente |
| **all-MiniLM-L6-v2 local** | 10-50ms | ~100-200MB | 0 CPU | Bonne (384 dims) |
| **all-mpnet-base-v2 local** | 20-100ms | ~400-600MB | 0 CPU | Très bonne (768 dims) |

**Recommandation pour VPS 6-8€** :

```
Stratégie hybride recommandée :
├── Phase MVP (4 semaines) : API externe (Kimi/OpenAI)
│   └── Avantage : zéro RAM serveur, qualité constante, pas de config
│   └── Inconvénient : latence réseau, coût à la consommation
│
└── Phase post-MVP (>500 documents/mois) : all-MiniLM-L6-v2 local
    └── Avantage : 0 coût marginal, latence locale
    └── Inconvénient : ~150MB RAM permanente, qualité légèrement inférieure
```

**⚠️ Risque VPS** : all-mpnet-base-v2 (768 dims, meilleure qualité) consomme 400-600MB RAM. Sur un VPS 4GB avec PostgreSQL + FastAPI + parsing PDF, ça laisse peu de marge. Préférer all-MiniLM-L6-v2 (384 dims, ~150MB) ou API externe pour le MVP.

---

| Risque | Niveau | Action corrective |
|---|---|---|
| HNSW build OOM sur millions de vecteurs | 🟢 OK — pas applicable à l'échelle MVP | Monitorer `pg_relation_size` |
| Embedding local trop gourmand en RAM | 🟡 ATTENTION | Commencer par API externe |
| Pas de partitionnement par tenant | 🟡 ATTENTION | Ajouter index partiels si >100K vecteurs |
| Hybrid search non implémenté | 🟡 ATTENTION | Prévoir colonne `tsvector` + GIN index dès le départ |

---

## 3. PARSING PDF DES DCE (DOSSIERS DE CONSULTATION DES ENTREPRISES)

### 3.1 Formats de DCE en France/Belgique

| Format | Fréquence | Traitement |
|---|---|---|
| **PDF texte (généré)** | ~60% | Extraction directe possible |
| **PDF scanné (image)** | ~15% | OCR obligatoire (Tesseract/EasyOCR) |
| **DOCX** | ~15% | python-docx ou conversion |
| **ZIP multi-fichiers** | ~8% | Extraction + parsing récursif |
| **XML UBL (BOAMP)** | ~2% | Parsing XML natif (xml.etree) |

**⚠️ Défi majeur** : Un DCE type fait 50-300 pages, contient des tableaux complexes (lots, critères d'attribution, calendrier), des sections imbriquées, et parfois des annexes scannées.

### 3.2 pypdf vs pdfplumber vs PyMuPDF — Décision Matrix

| Critère | pypdf | pdfplumber | PyMuPDF (fitz) |
|---|---|---|---|
| Vitesse | Lente | Lente | **Rapide** (5-10x) |
| Extraction texte | Correcte | Correcte | **Excellente** |
| Extraction tableaux | Non | **Excellente** | Manuel (nécessite heuristiques) |
| Métadonnées | Limitées | Bonnes | **Excellentes** |
| Coordonnées layout | Non | Oui | **Oui** |
| OCR intégré | Non | Non | API Tesseract |
| Licence | MIT | MIT | **AGPL** ⚠️ |

**⚠️ CRITIQUE — Licence PyMuPDF** : PyMuPDF est sous AGPL. Si TAKA OS est open source, c'est OK. Si vous prévoyez une version SaaS propriétaire, il faut soit :
- Acheter une licence commerciale PyMuPDF
- Utiliser pypdf + pdfplumber en alternative (plus lente mais MIT)
- Rester 100% open source (AGPL compatible)

### 3.3 Architecture de Parsing Recommandée — Pipeline Stratifiée

```python
# ✅ PIPELINE DE PARSING RECOMMANDÉ

async def parse_dce(file_path: str, mime_type: str) -> DceParseResult:
    result = DceParseResult()
    
    # Étape 1 : Extraction brute de texte (stratégie fallback)
    text = await extract_text_with_fallback(file_path, mime_type)
    result.raw_text = text
    result.extraction_method = used_method
    
    # Étape 2 : Extraction des tableaux (si PDF/DOCX)
    tables = await extract_tables(file_path, mime_type)
    result.tables = tables
    
    # Étape 3 : Extraction structurée — RÈGLES D'ABORD
    structured = extract_structured_rules_first(text, tables)
    result.structured_data = structured
    
    # Étape 4 : Complétion avec LLM pour les champs manquants
    if structured.confidence < 0.8:
        llm_enhanced = await extract_structured_llm_fallback(text, tables, structured)
        result.structured_data = llm_enhanced
        result.used_llm_fallback = True
    
    # Étape 5 : Validation
    result.is_valid = validate_minimum_fields(result.structured_data)
    
    return result

# --- Extraction de texte avec fallback ---
async def extract_text_with_fallback(file_path: str, mime_type: str) -> str:
    """Stratégie : PyMuPDF > pypdf > OCR"""
    
    if mime_type == "application/pdf":
        # Tentative 1 : PyMuPDF (rapide, bon layout)
        try:
            text = await extract_with_pymupdf(file_path)
            if is_meaningful_text(text):
                return text, "pymupdf"
        except Exception:
            pass
        
        # Tentative 2 : pypdf (fallback léger)
        try:
            text = await extract_with_pypdf(file_path)
            if is_meaningful_text(text):
                return text, "pypdf"
        except Exception:
            pass
        
        # Tentative 3 : OCR (PDF scanné)
        return await extract_with_ocr(file_path), "ocr"
    
    elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return await extract_with_docx(file_path), "docx"
    
    elif mime_type == "application/zip":
        return await extract_from_zip(file_path), "zip"
    
    raise UnsupportedFormatError(f"Format non supporté: {mime_type}")
```

### 3.4 Extraction des Champs Clés d'un DCE

```python
# ✅ EXEMPLE D'EXTRACTION RÈGLES D'ABORD (70-80% des cas)
import re
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class DceStructuredData:
    cpv_codes: list[str]
    montant_estime: Optional[float]
    deadline: Optional[datetime]
    criteres_attribution: list[dict]  # [{"nom": "Prix", "poids": 60}, ...]
    lots: list[dict]  # [{"numero": 1, "description": "...", "montant": 50000}]
    duree_marche: Optional[str]
    type_procedure: Optional[str]  # "Ouverte", "Restreinte", "Dialogue compétitif"
    confidence: float  # 0.0 - 1.0

def extract_structured_rules_first(text: str, tables: list) -> DceStructuredData:
    """Extraction déterministe avant d'appeler le LLM."""
    result = DceStructuredData(confidence=0.0)
    
    # CPV — Regex fiable
    cpv_matches = re.findall(r'\b(\d{8}-\d)\b', text)
    result.cpv_codes = list(set(cpv_matches))
    
    # Montant estimé — Patterns communs
    montant_patterns = [
        r'montant estim[ée]\s*:?\s*([\d\s.,]+)\s*(?:EUR|€|euros?)',
        r'valeur totale estim[ée]e\s*:?\s*([\d\s.,]+)',
        r'budget\s*:?\s*([\d\s.,]+)\s*(?:EUR|€)',
    ]
    for pattern in montant_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            raw = match.group(1).replace(' ', '').replace(',', '.')
            try:
                result.montant_estime = float(raw)
                break
            except ValueError:
                pass
    
    # Deadline — Dates ISO ou format FR
    date_patterns = [
        r'date limite.*?:(\d{2}/\d{2}/\d{4})',
        r'remise des offres.*?:(\d{2}/\d{2}/\d{4})',
        r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})',
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                result.deadline = parse_french_date(match.group(1))
                break
            except:
                pass
    
    # Critères d'attribution — Extraction depuis tableaux
    for table in tables:
        for row in table:
            row_text = ' '.join(str(c) for c in row if c)
            if any(k in row_text.lower() for k in ['critère', 'poids', 'pondération', 'note']):
                # Parsing du tableau de critères
                pass
    
    # Calcul du confidence score
    filled_fields = sum(1 for f in [result.montant_estime, result.deadline, 
                                     result.cpv_codes, result.criteres_attribution] if f)
    result.confidence = filled_fields / 4.0
    
    return result
```

### 3.5 Taux de Réussite Attendus

| Type de champ | Méthode règles | Méthode LLM fallback | Combiné |
|---|---|---|---|
| CPV | 85-90% | 90-95% | **90-95%** |
| Montant estimé | 70-80% | 85-90% | **85-90%** |
| Deadline | 75-85% | 90-95% | **90-95%** |
| Critères d'attribution | 50-60% | 80-85% | **80-85%** |
| Lots | 60-70% | 75-80% | **75-80%** |
| Type de procédure | 80-90% | 90-95% | **90-95%** |

**Stratégie fallback quand tout échoue** : Stocker le texte brut, marquer le document comme `PARSE_ERROR`, et permettre à l'utilisateur de saisir manuellement les champs clés. Le LLM peut suggérer les valeurs à partir du texte brut affiché dans l'UI.

---

| Risque | Niveau | Action corrective |
|---|---|---|
| PyMuPDF AGPL = conflit licence si SaaS propriétaire | 🔴 CRITIQUE | Vérifier la licence du projet OU acheter licence commerciale |
| PDF scanné non détecté → parsing vide silencieux | 🔴 CRITIQUE | Fonction `is_meaningful_text()` + fallback OCR obligatoire |
| Taux de réussite extraction <80% → utilisateurs frustrés | 🟡 ATTENTION | Pipeline règles + LLM + saisie manuelle |
| Parsing synchrone bloque l'API pendant 30s+ | 🔴 CRITIQUE | Traitement asynchrone (background task ou queue) |

---

## 4. ARCHITECTURE AGENTIC — PATTERNS ET ANTI-PATTERNS

### 4.1 InMemoryEventBus Asyncio — Analyse des Risques

```python
# ✅ IMPLEMENTATION MINIMALE MAIS SÛRE
import asyncio
from typing import Callable, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Event:
    type: str
    payload: dict
    timestamp: datetime
    tenant_id: str

class InMemoryEventBus:
    """EventBus asyncio in-memory — MVP uniquement."""
    
    def __init__(self):
        self._handlers: dict[str, list[Callable]] = {}
        self._event_log: list[Event] = []  # Pour le debug
        self._max_log_size = 1000
    
    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    async def publish(self, event: Event):
        # Log pour debug/audit (volatile)
        self._event_log.append(event)
        if len(self._event_log) > self._max_log_size:
            self._event_log = self._event_log[-self._max_log_size:]
        
        # Distribution aux handlers — avec isolation d'erreurs
        handlers = self._handlers.get(event.type, [])
        results = await asyncio.gather(
            *[self._safe_handle(h, event) for h in handlers],
            return_exceptions=True
        )
        
        # Log des échecs
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Handler {handlers[i].__name__} failed: {result}")
    
    async def _safe_handle(self, handler: Callable, event: Event):
        try:
            await handler(event)
        except Exception as e:
            logger.exception(f"Event handler error for {event.type}")
            # Ne pas propager l'erreur — isolation
    
    # Persistance de secours pour les events critiques
    async def publish_critical(self, event: Event, db_session: AsyncSession):
        """Pour les events qui NE DOIVENT PAS être perdus."""
        # 1. Persister en DB d'abord
        await persist_event_to_db(event, db_session)
        # 2. Publier sur le bus
        await self.publish(event)
```

**Limites identifiées** :

| Limite | Impact | Mitigation |
|---|---|---|
| Perte d'événements au restart | Events non traités = disparus | Persister les events critiques en DB avant publication |
| Pas de redelivery | Handler qui plante = event perdu | Table `event_outbox` avec retry count |
| Un seul process | Pas de scaling horizontal | Acceptable pour MVP single-VPS |
| Pas d'ordre garanti | Ordre de traitement non déterministe | Acceptable si les agents sont idempotents |

### 4.2 Quand Ajouter Redis/NATS ? — Seuils de Fiabilité

```
┌─────────────────────────────────────────────────────────────────┐
│                    MATURITÉ DU SYSTÈME                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MVP (4 sem)    →  InMemoryEventBus + persistance DB critique   │
│                  │  [SUFFISANT]                                  │
│                  ▼                                              │
│  10+ users actifs →  Outbox pattern + retry DB                  │
│                  │  [RECOMMANDÉ]                                 │
│                  ▼                                              │
│  50+ users / multi-instance →  Redis Streams ou NATS           │
│                  │  [NÉCESSAIRE pour scaling horizontal]         │
│                  ▼                                              │
│  500+ users / multi-region  →  NATS JetStream / RabbitMQ       │
│                     [NÉCESSAIRE pour fiabilité + scale]         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Verdict** : Pour le MVP, InMemoryEventBus + persistance DB des events critiques suffit. Prévoir un refactoring vers un Outbox pattern (table PostgreSQL) dès la semaine 3-4.

### 4.3 Appels LLM via httpx — Pattern Production

```python
# ✅ PATTERN CIRCUIT BREAKER + RETRY POUR LLM
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # Fonctionnement normal
    OPEN = "open"          # Rejet immédiat
    HALF_OPEN = "half_open"  # Test de récupération

class LLMClient:
    """Client LLM avec circuit breaker, retry, et fallback."""
    
    def __init__(self, api_key: str, base_url: str):
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=5.0),
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
        )
        self.api_key = api_key
        self.base_url = base_url
        self.circuit = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            half_open_requests=2
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(initial=1, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        reraise=True
    )
    async def complete(self, prompt: str, context: dict = None) -> str:
        # Vérifier le circuit breaker
        if not self.circuit.can_execute():
            raise CircuitOpenError("LLM API circuit is OPEN — service unavailable")
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": "kimi-latest",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2000,
                    "temperature": 0.1,  # Bas pour l'extraction structurée
                }
            )
            response.raise_for_status()
            result = response.json()["choices"][0]["message"]["content"]
            
            self.circuit.record_success()
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                self.circuit.record_failure()
            raise
        except (httpx.TimeoutException, httpx.NetworkError):
            self.circuit.record_failure()
            raise
    
    async def extract_dce_fields(self, raw_text: str) -> dict:
        """Extraction structurée avec template Jinja2."""
        template = load_template("dce_extraction.jinja2")
        prompt = template.render(document_text=raw_text[:8000])  # Truncation
        
        response = await self.complete(prompt)
        
        # Parsing de la réponse JSON structurée
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback : extraction regex du JSON
            return extract_json_from_markdown(response)
```

### 4.4 Pattern "Règles d'Abord, LLM en Fallback"

```python
# ✅ ARCHITECTURE EN COUCHES

class ExtractionPipeline:
    """
    Layer 1 : Règles (regex, tableaux) → 70-80% des champs, <100ms
    Layer 2 : LLM structuré → Champs manquants, 1-3s
    Layer 3 : Saisie manuelle UI → Validation humaine
    """
    
    async def process(self, document: Document) -> ExtractionResult:
        # --- COUCHE 1 : RÈGLES ---
        rule_result = self.rules_engine.extract(document)
        
        if rule_result.confidence >= 0.9:
            # Tout est là, pas besoin de LLM
            return ExtractionResult(
                data=rule_result.data,
                method="rules_only",
                confidence=rule_result.confidence
            )
        
        # --- COUCHE 2 : LLM FALLBACK ---
        missing_fields = rule_result.get_missing_fields()
        llm_result = await self.llm_client.extract_missing(
            document.raw_text,
            missing_fields,
            partial_data=rule_result.data
        )
        
        # Merge règles + LLM (règles ont priorité)
        merged = {**llm_result.data, **rule_result.data}
        confidence = self._compute_merged_confidence(rule_result, llm_result)
        
        if confidence >= 0.75:
            return ExtractionResult(
                data=merged,
                method="rules+llm",
                confidence=confidence
            )
        
        # --- COUCHE 3 : REVUE MANUELLE ---
        return ExtractionResult(
            data=merged,
            method="rules+llm+manual_review",
            confidence=confidence,
            needs_review=True
        )
```

### 4.5 Séparation Pydantic vs SQLAlchemy

```python
# ✅ DOMAINE PYDANTIC (validation, API, LLM)
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal

class TenderCreate(BaseModel):
    """DTO pour création d'un appel d'offres."""
    title: str = Field(..., min_length=5, max_length=500)
    cpv_codes: list[str] = Field(..., pattern=r'^\d{8}-\d$')
    estimated_amount: Decimal = Field(..., ge=0)
    deadline: datetime
    description: str | None = Field(None, max_length=10000)

class TenderScore(BaseModel):
    """Résultat du scoring GO/NO-GO."""
    score: float = Field(..., ge=0, le=100)
    decision: Literal["GO", "NO-GO", "MAYBE"]
    reasons: list[str]
    confidence: float = Field(..., ge=0, le=1)

# --- Modèles SQLAlchemy (persistence) ---
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Numeric, DateTime, JSON

class Base(DeclarativeBase):
    pass

class TenderModel(Base):
    __tablename__ = "tenders"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), index=True)
    title: Mapped[str] = mapped_column(String(500))
    cpv_codes: Mapped[list[str]] = mapped_column(JSON)
    estimated_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_score: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    
    # Relationship
    documents: Mapped[list["TenderDocumentModel"]] = relationship(back_populates="tender")

    def to_dto(self) -> TenderCreate:
        """Conversion vers DTO Pydantic."""
        return TenderCreate.model_validate(self)
```

---

| Risque | Niveau | Action corrective |
|---|---|---|
| EventBus in-memory perd les events au restart | 🟡 ATTENTION | Persister events critiques en DB (outbox pattern) |
| Pas de circuit breaker sur les appels LLM | 🔴 CRITIQUE | Implémenter CircuitBreaker + tenacity obligatoire |
| Timeout LLM bloque l'API | 🔴 CRITIQUE | httpx timeout=30s + background tasks pour parsing |
| Modèles Pydantic = Modèles SQLAlchemy | 🔴 CRITIQUE | Séparation stricte : DTO Pydantic vs Model SQLAlchemy |
| LLM appelé pour tous les champs (coût+latence) | 🟡 ATTENTION | Règles d'abord → LLM seulement pour champs manquants |

---

## 5. SÉCURITÉ ET HARDENING

### 5.1 JWT Security — Architecture Complète

```python
# ✅ ARCHITECTURE JWT COMPLÈTE — Access + Refresh Tokens

import secrets
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

# Configuration
SECRET_KEY = os.environ["JWT_SECRET_KEY"]  # 256 bits min, généré via secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TokenManager:
    """Gestion complète des tokens avec rotation et révocation."""
    
    async def create_token_pair(self, user_id: str, tenant_id: str) -> tuple[str, str]:
        """Crée un couple access_token + refresh_token."""
        # Access token (court, stateless)
        access_token = jwt.encode(
            {
                "sub": user_id,
                "tenant_id": tenant_id,
                "type": "access",
                "jti": secrets.token_urlsafe(16),
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            },
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        
        # Refresh token (long, stocké en DB pour révocation)
        refresh_jti = secrets.token_urlsafe(16)
        refresh_token = jwt.encode(
            {
                "sub": user_id,
                "type": "refresh",
                "jti": refresh_jti,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            },
            REFRESH_SECRET_KEY,  # Clé séparée !
            algorithm=ALGORITHM
        )
        
        # Stockage du refresh token en DB (pour révocation)
        await self.store_refresh_token(refresh_jti, user_id, tenant_id)
        
        return access_token, refresh_token
    
    async def rotate_refresh_token(self, refresh_token: str) -> tuple[str, str]:
        """Rotation : un refresh token ne peut être utilisé qu'une fois."""
        payload = self.decode_refresh_token(refresh_token)
        jti = payload["jti"]
        user_id = payload["sub"]
        
        # Vérifier en DB que le token n'est pas révoqué
        token_record = await self.get_refresh_token(jti)
        if not token_record or token_record["revoked"]:
            # DÉTECTION DE RÉUTILISATION = compromission possible
            await self.revoke_all_user_tokens(user_id)
            raise SecurityError("Refresh token reuse detected — all sessions revoked")
        
        # Révoquer l'ancien
        await self.revoke_refresh_token(jti)
        
        # Créer un nouveau couple
        return await self.create_token_pair(user_id, token_record["tenant_id"])

# --- Schéma DB pour les refresh tokens ---
CREATE TABLE refresh_tokens (
    jti VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id),
    tenant_id VARCHAR(36) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    family_id VARCHAR(255) NOT NULL  -- Pour révocation en masse
);

CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens(expires_at) 
    WHERE revoked = FALSE;
```

### 5.2 Multi-Tenancy Isolation

**Option 1 : Row-Level Security (RLS) PostgreSQL** — Recommandé

```sql
-- Activer RLS sur toutes les tables multi-tenant
ALTER TABLE tenders ENABLE ROW LEVEL SECURITY;
ALTER TABLE tender_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_vectors ENABLE ROW LEVEL SECURITY;

-- Politique : chaque tenant ne voit que ses données
CREATE POLICY tenant_isolation ON tenders
    USING (tenant_id = current_setting('app.current_tenant', true));

CREATE POLICY tenant_isolation ON tender_documents
    USING (tenant_id = current_setting('app.current_tenant', true));

-- Définir le contexte tenant par session
SET app.current_tenant = 'tenant-uuid';
```

**Avantages RLS** :
- Isolation au niveau base de données (sécurité de défense en profondeur)
- Overhead minimal : 1-5% sur les performances
- Protection contre les requêtes oubliant le `tenant_id` WHERE clause

**Option 2 : Application-level filtering** — Acceptable pour MVP

```python
# Middleware FastAPI qui injecte le tenant dans le contexte
@app.middleware("http")
async def tenant_middleware(request: Request, call_next):
    tenant_id = extract_tenant_from_jwt(request)
    request.state.tenant_id = tenant_id
    return await call_next(request)

# Repository qui filtre systématiquement
async def get_tenders(session: AsyncSession, tenant_id: str):
    result = await session.execute(
        select(Tender).where(Tender.tenant_id == tenant_id)
    )
    return result.scalars().all()
```

**Recommandation** : RLS pour la production, application-level pour le MVP (plus simple à debugger). Migrer vers RLS en semaine 3-4.

### 5.3 Audit Trail Append-Only

```sql
-- ✅ TABLE AUDIT APPEND-ONLY
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36),
    action VARCHAR(50) NOT NULL,        -- CREATE, UPDATE, DELETE, LOGIN, etc.
    entity_type VARCHAR(50) NOT NULL,    -- tender, document, user
    entity_id VARCHAR(36),               -- ID de l'entité concernée
    old_values JSONB,                    -- Avant modification
    new_values JSONB,                    -- Après modification
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Contraintes pour garantir l'intégrité
    CONSTRAINT no_update CHECK (false) NO INHERIT  -- Empêche UPDATE (append-only)
);

-- Partitionnement par mois pour performance
CREATE TABLE audit_logs_2025_07 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');

-- Index pour requêtes courantes
CREATE INDEX idx_audit_tenant_time ON audit_logs(tenant_id, created_at DESC);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);

-- Règle pour bloquer les UPDATE/DELETE
CREATE RULE audit_no_update AS ON UPDATE TO audit_logs
    DO INSTEAD NOTHING;
CREATE RULE audit_no_delete AS ON DELETE TO audit_logs
    DO INSTEAD NOTHING;
```

### 5.4 Protection contre les Attaques Courantes

| Menace | Protection implémentée |
|---|---|
| **Injection SQL async** | SQLAlchemy ORM + paramètres bind uniquement. JAMAIS de f-string dans les requêtes |
| **XSS** | Pydantic validation des entrées + escaping côté front (React auto-escape) |
| **CSRF** | JWT dans header Authorization (pas de cookie) + SameSite=Strict si cookie refresh |
| **Brute force auth** | Rate limiting (5 tentatives/minute) via slowapi |
| **Exposition données** | RLS + tenant_id obligatoire dans toutes les requêtes |
| **Fuite secrets** | Variables d'environnement uniquement, jamais dans le code |

```python
# ✅ Rate limiting sur les endpoints auth
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: LoginCredentials):
    ...
```

---

| Risque | Niveau | Action corrective |
|---|---|---|
| Access token longue durée (>30min) | 🔴 CRITIQUE | 15 minutes max, refresh token séparé |
| Pas de stockage refresh token en DB | 🔴 CRITIQUE | Table `refresh_tokens` avec flag `revoked` |
| Pas de rotation des refresh tokens | 🟡 ATTENTION | Implémenter rotation + détection de réutilisation |
| Pas de RLS PostgreSQL | 🟡 ATTENTION | Migrer vers RLS en semaine 3-4 |
| Audit log modifiable (pas append-only) | 🔴 CRITIQUE | Règles PostgreSQL + partitionnement |
| Secrets en dur dans le code | 🔴 CRITIQUE | Vérifier via pre-commit hook + CI scan |

---

## 6. DÉPLOIEMENT ET OPS

### 6.1 Docker Compose Production-Ready

```yaml
# docker-compose.yml — Configuration de production
version: '3.8'

services:
  app:
    image: takaos/app:${VERSION:-latest}
    container_name: takaos_app
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
    ports:
      - "127.0.0.1:8000:8000"  # Localhost uniquement, Nginx en front
    environment:
      - DATABASE_URL=postgresql+asyncpg://takaos:${DB_PASSWORD}@postgres:5432/takaos
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - LLM_API_KEY=${LLM_API_KEY}
      - ENVIRONMENT=production
    deploy:
      resources:
        limits:
          cpus: '1.5'
          memory: 1.5G
        reservations:
          cpus: '0.5'
          memory: 512M
    healthcheck:
      test: ["CMD-SHELL", "python -c 'import urllib.request; urllib.request.urlopen(\"http://localhost:8000/health\")'"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s  # Temps de démarrage
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
        compress: "true"

  postgres:
    image: pgvector/pgvector:pg15
    container_name: takaos_postgres
    restart: unless-stopped
    environment:
      - POSTGRES_USER=takaos
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=takaos
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    deploy:
      resources:
        limits:
          cpus: '1.5'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U takaos -d takaos"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
        compress: "true"

  # Front-end statique servi par Nginx
  frontend:
    image: takaos/frontend:${VERSION:-latest}
    container_name: takaos_frontend
    restart: unless-stopped
    ports:
      - "127.0.0.1:3000:80"
    depends_on:
      app:
        condition: service_healthy
    logging:
      driver: json-file
      options:
        max-size: "5m"
        max-file: "2"

  # Reverse proxy Nginx (SSL termination + routing)
  nginx:
    image: nginx:alpine
    container_name: takaos_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - certbot_data:/etc/letsencrypt
    depends_on:
      - app
      - frontend
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  postgres_data:
  certbot_data:
```

**⚠️ Points critiques** :
- `pgvector/pgvector:pg15` inclut l'extension pgvector préinstallée
- `restart: unless-stopped` — ne pas utiliser `always` (redémarrage après `docker stop` manuel)
- `start_period` obligatoire pour les healthchecks (évite les faux négatifs au boot)
- Log rotation : `max-size: 10m` + `max-file: 3` = 30MB max par conteneur
- Limites mémoire : conteneur tué par OOM killer si dépassé — préserver de la marge

### 6.2 Backup PostgreSQL Automatisé

```bash
#!/bin/bash
# backup.sh — Script de backup quotidien via cron

BACKUP_DIR="/backups"
DB_NAME="takaos"
DB_USER="takaos"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# Backup complet
pg_dump -h localhost -U $DB_USER -d $DB_NAME \
    -F custom -f "$BACKUP_DIR/takaos_${TIMESTAMP}.dump"

# Compression
gzip "$BACKUP_DIR/takaos_${TIMESTAMP}.dump"

# Upload vers S3 (optionnel, recommandé)
aws s3 cp "$BACKUP_DIR/takaos_${TIMESTAMP}.dump.gz" \
    s3://takaos-backups/postgres/

# Nettoyage des vieux backups
find $BACKUP_DIR -name "takaos_*.dump.gz" -mtime +$RETENTION_DAYS -delete
```

```cron
# Crontab — Backup quotidien à 3h du matin
0 3 * * * /opt/takaos/scripts/backup.sh >> /var/log/takaos/backup.log 2>&1
```

### 6.3 Monitoring Minimal

**Option A : Logging structuré (recommandé pour MVP)**

```python
# ✅ LOGGING STRUCTURÉ AVEC STRUCTLOG
import structlog
import logging
import sys

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),  # Sortie JSON pour parsing
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Utilisation
logger.info(
    "tender_created",
    tender_id=str(tender.id),
    tenant_id=tenant_id,
    cpv_codes=tender.cpv_codes,
    estimated_amount=float(tender.estimated_amount),
    duration_ms=42.5,
)
```

**Option B : Prometheus + Grafana (si temps disponible semaine 4)**

```python
# ✅ MÉTRIQUES PROMETHEUS (optionnel)
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app, include_in_schema=False)

# Métriques custom
from prometheus_client import Counter, Histogram

tender_parsed = Counter('takaos_tenders_parsed_total', 'Total tenders parsed', ['status', 'method'])
parsing_duration = Histogram('takaos_parsing_duration_seconds', 'PDF parsing duration')
llm_requests = Counter('takaos_llm_requests_total', 'LLM API requests', ['status', 'model'])
```

### 6.4 Zero-Downtime Deployment sur VPS Unique

**Architecture Blue-Green avec Nginx**

```
[Internet] → [Nginx :80/:443] → [App Bleu :8001]  ← Actuel
                                → [App Vert :8002]  ← Nouvelle version
```

```bash
#!/bin/bash
# deploy.sh — Déploiement zero-downtime

VERSION=$1
CURRENT_PORT=$(docker port takaos_app | grep 8000 | cut -d: -f2)

if [ "$CURRENT_PORT" = "8001" ]; then
    NEW_PORT=8002
    NEW_NAME="takaos_app_green"
    OLD_NAME="takaos_app_blue"
else
    NEW_PORT=8001
    NEW_NAME="takaos_app_blue"
    OLD_NAME="takaos_app_green"
fi

# 1. Démarrer la nouvelle version
docker run -d \
    --name $NEW_NAME \
    -p 127.0.0.1:$NEW_PORT:8000 \
    -e DATABASE_URL="..." \
    --memory=1.5g \
    takaos/app:$VERSION

# 2. Health check
echo "Attente du health check..."
sleep 15
for i in {1..10}; do
    if curl -sf http://127.0.0.1:$NEW_PORT/health > /dev/null; then
        echo "✅ Health check OK"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "❌ Health check FAILED — rollback"
        docker stop $NEW_NAME && docker rm $NEW_NAME
        exit 1
    fi
    sleep 3
done

# 3. Switch Nginx
cp nginx/app-$NEW_PORT.conf nginx/active.conf
nginx -t && nginx -s reload

# 4. Cleanup (après 30s de grace)
sleep 30
docker stop $OLD_NAME && docker rm $OLD_NAME
docker image prune -f

echo "✅ Déploiement $VERSION terminé sur le port $NEW_PORT"
```

**⚠️ Limitation** : Sur un VPS unique avec 4GB RAM, faire tourner 2 instances d'application simultanément est risqué. Prévoir :
- App : 1.5GB max par instance
- PostgreSQL : 2GB
- Nginx : ~50MB
- Marge système : ~500MB
- **Total avec 2 apps : 5.5GB+ → DANGER OOM sur 4GB**

**Recommandation** : Pour le MVP, accepter 5-10s de downtime lors du déploiement (`docker compose down && docker compose up -d`). Le blue-green n'est viable qu'avec ≥6GB RAM ou un VPS dédié app + un autre pour la DB.

---

| Risque | Niveau | Action corrective |
|---|---|---|
| Pas de healthchecks Docker | 🔴 CRITIQUE | Healthchecks sur app + postgres + Nginx |
| Pas de log rotation | 🔴 CRITIQUE | `max-size: 10m` + `max-file: 3` sur tous les services |
| Pas de backup automatisé | 🔴 CRITIQUE | Cron quotidien + upload S3 |
| Blue-green sur 4GB RAM | 🔴 CRITIQUE | Accepté le downtime court pour MVP, migrer vers 8GB pour zero-downtime |
| Pas de monitoring | 🟡 ATTENTION | Logging structuré minimum ; Prometheus si temps |
| Secrets dans docker-compose.yml | 🔴 CRITIQUE | Variables d'environnement + `.env` non versionné |

---

## VERDICT GLOBAL — L'ARCHITECTURE TIENT-ELLE LA ROUTE ?

### Évaluation par axe (sur 5)

| Axe | Score | Commentaire |
|---|---|---|
| FastAPI + SQLAlchemy 2.0 async | ⭐⭐⭐⭐⭐ | Stack mature, patterns éprouvés, performance suffisante |
| pgvector | ⭐⭐⭐⭐⭐ | Parfaitement adapté à l'échelle MVP (10K vecteurs/tenant) |
| Parsing PDF DCE | ⭐⭐⭐☆☆ | Le plus gros risque technique — pipeline règles+LLM nécessaire |
| Architecture agentic | ⭐⭐⭐⭐☆ | InMemoryEventBus OK pour MVP, prévoir outbox pattern |
| Sécurité | ⭐⭐⭐⭐☆ | JWT + RLS + audit trail = solide si bien implémenté |
| Déploiement Ops | ⭐⭐⭐⭐☆ | Docker compose propre, backup OK, monitoring minimal |

**Score global : 4.2/5 — Architecture viable pour MVP 4 semaines**

---

## 🔴 LES 3 POINTS QUI VONT FAIRE ÉCHOUER LE PROJET SI MAL GÉRÉS

### 1. PARSING PDF DES DCE — Le goulot d'étranglement

**Pourquoi ça va péter** :
- Les DCE sont des documents complexes (50-300 pages, tableaux, formats variés)
- Un parsing synchrone bloque l'API pendant 30+ secondes
- Si l'extraction rate est <70%, les utilisateurs abandonnent
- PyMuPDF AGPL = bombe à retardement si version SaaS propriétaire

**Ce qu'il faut faire dès la semaine 1** :
- Architecture pipeline asynchrone (background task, pas de blocage API)
- Stratégie règles (70% cas) + LLM fallback (champs manquants) + saisie manuelle
- Fallback OCR pour les PDF scannés (15% des cas)
- Traçage complet de chaque étape de parsing (debugging indispensable)

### 2. APPELS LLM SANS CIRCUIT BREAKER — Le point de fragilité

**Pourquoi ça va péter** :
- API Kimi/OpenAI peut être indisponible, lente, ou rate-limiter
- Sans circuit breaker, un timeout en cascade fait tomber tout le système
- Sans retry exponentiel, les erreurs temporaires deviennent des failures
- Chaque appel LLM coûte de l'argent — les boucles infinies sont un risque financier

**Ce qu'il faut faire dès la semaine 1** :
- httpx avec timeout=30s, limits sur les connexions
- tenacity avec retry exponentiel + jitter (3 tentatives max)
- Circuit breaker : 5 failures → OPEN pendant 60s
- Fallback : si LLM indisponible, extraction règles seule + flag `NEEDS_REVIEW`
- Logging métrique des appels LLM (coût, latence, taux de succès)

### 3. SESSIONS ASYNC SQLALCHEMY — Le piège qui a tué NEXA-MIND

**Pourquoi ça va péter** :
- `expire_on_commit=False` oublié = lazy loading errors en cascade
- Mauvaise gestion du pool de connexions = "too many connections" ou connexions zombies
- Alembic async mal configuré = migrations qui échouent en production
- Mélange sync/async dans SQLAlchemy = conflits de modules (le cauchemar de NEXA-MIND)

**Ce qu'il faut faire dès la semaine 1** :
- `expire_on_commit=False` dans le `async_sessionmaker` (non négociable)
- `pool_pre_ping=True` pour détecter les connexions mortes
- Pool size = 5 max sur VPS (PostgreSQL default max_connections = 100)
- Alembic avec `sync_engine` sous-jacent (pas de asyncio dans les migrations)
- Pas un seul appel synchrone à la DB dans le code async

---

## FEUILLE DE ROUTE TECHNIQUE — 4 SEMAINES

```
Semaine 1 — Fondations (risque max si mal fait)
├── J1-2 : Setup projet, SQLAlchemy async, Alembic, modèles DB
├── J2-3 : Auth JWT (access + refresh), register/login/logout
├── J3-4 : Repository pattern, CRUD tenders, multi-tenancy (app-level)
├── J4-5 : Upload documents, pipeline parsing (règles d'abord)
└── 🔴 LIVRABLE : API fonctionnelle, auth, upload, parsing basique

Semaine 2 — Agents Core
├── J6-7 : Agent Sourcer (upload + extraction champs DCE)
├── J7-8 : Agent Qualifieur (scoring GO/NO-GO avec LLM)
├── J8-9 : Agent Tracker (surveillance deadlines, alertes)
├── J9-10 : EventBus in-memory + persistance critique DB
└── 🔴 LIVRABLE : 3 agents fonctionnels, scoring, alertes

Semaine 3 — RAG + Sécurité
├── J11-12 : pgvector setup, embeddings, recherche vectorielle
├── J12-13 : Hybrid search (vector + full-text RRF)
├── J13-14 : RLS PostgreSQL, audit trail append-only
├── J14-15 : Hardering JWT, rate limiting, input validation
└── 🟡 LIVRABLE : Recherche sémantique, RLS, audit complet

Semaine 4 — Front + Ops
├── J16-18 : React + Vite + Tailwind, intégration API
├── J18-19 : Docker compose production, healthchecks, backups
├── J19-20 : Monitoring, logging structuré, alerting basique
├── J20 : Tests E2E, documentation, déploiement
└── 🟢 LIVRABLE : MVP complet, déployé, documenté
```

---

## RECOMMANDATIONS ARCHITECTURALES CLÉS

1. **Ne pas réinventer** — Utiliser `prometheus_fastapi_instrumentator`, `slowapi`, `tenacity` (bibliothèques éprouvées)
2. **Commencer simple, monitorer tôt** — Un logging structuré vaut mieux qu'un monitoring complexe qui ne fonctionne pas
3. **Tout ce qui peut échouer, va échouer** — Circuit breaker sur LLM, fallback OCR sur PDF, saisie manuelle sur extraction
4. **Le MVP n'a pas besoin de scale** — InMemoryEventBus suffit, pgvector suffit, un VPS suffit
5. **Tester le parsing dès la semaine 1** — C'est le point le plus risqué, pas le plus visible

---

*Document généré pour l'équipe TAKA OS. Ce reste un guide technique, pas un remplacement aux bonnes pratiques de développement et de code review.*
