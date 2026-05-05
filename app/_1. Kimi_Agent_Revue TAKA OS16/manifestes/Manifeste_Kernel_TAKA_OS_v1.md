# Manifeste Kernel TAKA OS v1

> **Version:** 1.0.0-alpha
> **Date:** 2025-01-09
> **Statut:** SPEC EXECUTABLE — pret pour Kimi Code
> **Stack:** Python 3.12+ | FastAPI | SQLAlchemy 2.0 async | PostgreSQL 15+pgvector | Mistral AI API
> **License:** MIT
> **Contrainte:** `<3.14`, `expire_on_commit=False`, un seul conteneur DB, pas de LangChain/CrewAI

---

## SECTION 1 — Vue d'ensemble

### 1.1 Architecture Kernel en 2 niveaux

Le Kernel TAKA OS est le coeur distribue de l'OS agentic. Il est concu autour du principe **"bootstrap evolutif"** : le kernel MVP (v0.1) est minimal mais 100% compatible ascendante avec la cible (v1.0). Chaque composant MVP est remplacable sans rupture de contrat.

| Niveau | Version | EventBus | Registry | Memory Mesh | Governance | Lifecycle |
|--------|---------|----------|----------|-------------|------------|-----------|
| MVP    | v0.1    | asyncio in-memory | Non | PostgreSQL only | Non | Non |
| Cible  | v1.0    | NATS/RabbitMQ | Swarm Registry v0.5+ | 3 zones | Governance Core v0.3+ | Lifecycle Manager v0.5+ |

### 1.2 Principe: Bootstrap evolutif

Chaque composant MVP expose la **meme interface** que sa version cible. Le remplacement est un "drop-in" :

1. `EventBus` MVP (asyncio.Queue) -> v1.0 (NATS) : meme classe, meme methodes `publish/subscribe/unsubscribe`
2. `Memory` MVP (PostgreSQL) -> v1.1 (3 zones + Neo4j) : abstraction `MemoryMesh` preservee
3. `Audit` MVP (append-only SQL) -> v1.0 (hash chain distribuee) : schema identique, hash chain identique
4. `Agent` MVP (fonctions Python) -> v0.5 (Swarm Registry) : interface abstraite `Agent` des v0.5

### 1.3 Diagramme ASCII — Kernel Complet (v1.0)

```
+-----------------------------------------------------------------------+
|                        TAKA OS KERNEL v1.0                             |
|  +------------------+  +------------------+  +---------------------+  |
|  |  Event Mesh      |  |  Swarm Registry  |  |  Memory Mesh v1.1   |  |
|  |  (NATS/RabbitMQ) |  |  (Capabilities)  |  |  - Global           |  |
|  |  - Wildcards     |  |  - Discovery     |  |  - Tenant (pgvector)|  |
|  |  - DLQ           |  |  - Heartbeat     |  |  - Session (TTL)    |  |
|  |  - QoS           |  |  - Lifecycle     |  |  - Neo4j (v1.1+)    |  |
|  +--------+---------+  +--------+---------+  +----------+----------+  |
|           |                     |                       |              |
|           +----------+----------+-----------+-----------+              |
|                      |          |           |                          |
|  +-------------------v----------v-----------v----------------------+  |
|  |                    GOVERNANCE CORE v0.3+                         |  |
|  |  - DeliberationSession (majority/borda/consensus/unanimous)     |  |
|  |  - Transcript (append-only, immuable)                           |  |
|  |  - Audit Trail (hash chain SHA-256)                             |  |
|  +------------------------------------------------------------------+  |
|                      |                                                |
|  +-------------------v----------------------------------------------+  |
|  |                  LIFECYCLE MANAGER v0.5+                          |  |
|  |  - FSM: registered -> idle -> busy -> debating -> learning       |  |
|  |  - Heartbeat monitor (timeout 60s)                                |  |
|  |  - Auto-respawn agents critiques                                   |  |
|  |  - GC sessions expirees                                            |  |
|  +------------------------------------------------------------------+  |
|                      |                                                |
|  +-------------------v----------------------------------------------+  |
|  |                      KERNEL MVP v0.1 (COMPAT)                     |  |
|  |  - EventBus asyncio in-memory (meme API que NATS)                |  |
|  |  - Security: JWT + bcrypt                                        |  |
|  |  - Audit: hash chain SHA-256 (append-only SQL)                   |  |
|  |  - Un seul fichier modeles: app/models/ao.py                     |  |
|  +------------------------------------------------------------------+  |
+-----------------------------------------------------------------------+
           |                    |                    |
   +-------v-------+   +--------v--------+   +-------v--------+
   |  Couche 1     |   |  Couche 2       |   |  Couche 3      |
   |  Sensorimotr. |   |  Memoire        |   |  Agents        |
   |  PDF/API      |   |  PostgreSQL     |   |  Qualifier     |
   +---------------+   +-----------------+   |  Scorer        |
                                             |  Tracker       |
   +---------------+   +-----------------+   |  Sourcer       |
   |  Couche 4     |   |  Couche 5       |   +----------------+
   |  Deliberation |   |  Metacognition  |
   |  Parlement    |   |  TAKA LAB       |
   +---------------+   +-----------------+
```

### 1.4 Fichiers du Kernel (arborescence)

```
app/
├── kernel/
│   ├── __init__.py          # Exports publics du kernel
│   ├── bus.py               # EventBus MVP (v0.1) / EventMesh (v1.0)
│   ├── config.py            # Pydantic-Settings (reference a app/config.py)
│   ├── security.py          # JWT + bcrypt (deja specifie)
│   ├── audit.py             # Audit trail append-only avec hash chain
│   ├── agent.py             # Interface abstraite Agent (v0.5+)
│   ├── memory.py            # Memory Mesh abstraction (v1.0+)
│   ├── governance.py        # Deliberation engine (v0.3+)
│   ├── lifecycle.py         # Lifecycle Manager FSM (v0.5+)
│   └── schemas.py           # Modeles Pydantic partages du kernel
├── config.py                # Pydantic-Settings principal (Settings)
└── models/
    └── ao.py                # UNIQUE fichier modeles SQLAlchemy
```

---

## SECTION 2 — Kernel MVP v0.1

### 2.1 `app/kernel/bus.py` — EventBus asyncio in-memory

**Statut:** MVP v0.1 — remplace par EventMesh NATS en v1.0 sans changement d'API.

```python
"""
app/kernel/bus.py — EventBus asyncio in-memory (MVP v0.1)

EventBus minimal base sur asyncio.Queue et asyncio.Lock.
Compatible ascendante : la version NATS (v1.0) expose la meme interface.

Topics canoniques:
    ao.new          — Nouvel AO detecte (upload PDF ou connector API)
    ao.qualified    — AO qualifie par l'agent Qualifier
    ao.stage_changed— Changement d'etape dans le pipeline
    memory.index    — Demande d'indexation d'un document
    alert.deadline  — Alerte echeance imminente

Usage:
    bus = EventBus()
    await bus.subscribe("ao.new", mon_handler)
    await bus.publish(Event(topic="ao.new", payload={"ao_id": "123"}))
"""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine, Dict, List, Optional, Set
from enum import Enum


class EventPriority(Enum):
    """Priorite d'evenement du plus urgent au moins urgent."""
    CRITICAL = 0    # Echeances, alertes securite
    HIGH = 1        # Qualification, scoring
    NORMAL = 2      # Indexation, logging
    LOW = 3         # Metriques, analytics


@dataclass(frozen=True)
class Event:
    """
    Evenement immuable du kernel.

    Attributes:
        topic: Topic de routage (ex: "ao.new")
        payload: Donnees de l'evenement (JSON-serialisable)
        priority: Niveau de priorite pour l'ordonnancement
        tenant_id: Identifiant du tenant (multi-tenant isolation)
        timestamp: Unix timestamp de creation (auto)
        event_id: UUID v4 unique (auto)
    """
    topic: str
    payload: dict[str, Any]
    priority: EventPriority = EventPriority.NORMAL
    tenant_id: str = "default"
    timestamp: float = field(default_factory=time.time)
    event_id: str = field(default_factory=lambda: __import__('uuid').uuid4().hex)

    def to_json(self) -> str:
        """Serialisation JSON pour persistence/transmission."""
        return json.dumps({
            "event_id": self.event_id,
            "topic": self.topic,
            "payload": self.payload,
            "priority": self.priority.value,
            "tenant_id": self.tenant_id,
            "timestamp": self.timestamp,
        }, default=str)


class Subscriber:
    """
    Abonnement a un topic.

    Attributes:
        topic: Topic souscrit (supporte les wildcards "*" uniquement en suffixe)
        handler: Coroutine appellee a chaque evenement
        subscriber_id: Identifiant unique de l'abonnement
    """

    def __init__(
        self,
        topic: str,
        handler: Callable[[Event], Coroutine[Any, Any, None]],
        subscriber_id: str,
    ) -> None:
        self.topic: str = topic
        self.handler: Callable[[Event], Coroutine[Any, Any, None]] = handler
        self.subscriber_id: str = subscriber_id
        self._match_cache: Dict[str, bool] = {}

    def matches(self, topic: str) -> bool:
        """
        Verifie si le topic d'un evenement correspond a l'abonnement.
        Supporte le wildcard suffixe: "ao.*" match "ao.new", "ao.qualified", etc.
        """
        if topic in self._match_cache:
            return self._match_cache[topic]

        if self.topic.endswith(".*"):
            prefix = self.topic[:-1]
            result = topic.startswith(prefix)
        else:
            result = self.topic == topic

        self._match_cache[topic] = result
        return result


class EventBus:
    """
    EventBus asyncio in-memory avec routing par topic et wildcards.

    MVP v0.1 : utilise asyncio.Queue et asyncio.Lock.
    v1.0 : remplace par EventMesh NATS — interface identique.

    Attributes:
        _subscribers: Dict[topic_pattern, List[Subscriber]]
        _lock: asyncio.Lock pour la coherence souscriptions
        _queue: asyncio.Queue ordonnee par priorite
        _running: Etat du dispatcher
        _task: Tache asyncio du dispatcher
        _dropped_events: Compteur d'evenements abandonnes (queue pleine)

    Configuration (Settings):
        EVENTBUS_QUEUE_SIZE: Taille max de la queue (defaut: 10_000)
        EVENTBUS_DISPATCHER_WORKERS: Nombre de workers parallele (defaut: 3)
    """

    def __init__(
        self,
        queue_size: int = 10_000,
        dispatcher_workers: int = 3,
    ) -> None:
        self._subscribers: Dict[str, List[Subscriber]] = {}
        self._subscribers_by_id: Dict[str, Subscriber] = {}
        self._lock: asyncio.Lock = asyncio.Lock()
        self._queue: asyncio.PriorityQueue[tuple[int, Event]] = asyncio.PriorityQueue(
            maxsize=queue_size
        )
        self._running: bool = False
        self._dispatcher_workers: int = dispatcher_workers
        self._tasks: List[asyncio.Task[None]] = []
        self._dropped_events: int = 0
        self._processed_events: int = 0

    async def start(self) -> None:
        """Demarre le dispatcher d'evenements. Idempotent."""
        if self._running:
            return
        self._running = True
        self._tasks = [
            asyncio.create_task(self._dispatcher_loop(), name=f"eventbus-dispatcher-{i}")
            for i in range(self._dispatcher_workers)
        ]

    async def stop(self) -> None:
        """Arrete le dispatcher. Attend la fin des workers en cours."""
        self._running = False
        # Injecte des sentinelles pour debloquer les workers
        for _ in self._tasks:
            try:
                self._queue.put_nowait((-1, None))  # type: ignore
            except asyncio.QueueFull:
                pass
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()

    async def publish(self, event: Event) -> None:
        """
        Publie un evenement sur le bus.

        Args:
            event: Instance de Event a propager

        Raises:
            asyncio.QueueFull: Si la queue est pleine et l'evenement est dropped.
                               Incremente le compteur `_dropped_events`.
        """
        try:
            # Priorite numerique inversee : 0 (CRITICAL) a plus de poids
            priority_key = event.priority.value
            await self._queue.put((priority_key, event))
        except asyncio.QueueFull:
            self._dropped_events += 1
            raise

    async def subscribe(
        self,
        topic: str,
        handler: Callable[[Event], Coroutine[Any, Any, None]],
    ) -> str:
        """
        Souscrit un handler a un topic.

        Args:
            topic: Pattern de topic (ex: "ao.new", "ao.*", "*")
            handler: Coroutine `async def handler(event: Event) -> None`

        Returns:
            subscriber_id: Identifiant de l'abonnement (pour unsubscribe)
        """
        subscriber_id = f"sub_{topic}_{id(handler)}_{__import__('uuid').uuid4().hex[:8]}"
        subscriber = Subscriber(topic=topic, handler=handler, subscriber_id=subscriber_id)

        async with self._lock:
            if topic not in self._subscribers:
                self._subscribers[topic] = []
            self._subscribers[topic].append(subscriber)
            self._subscribers_by_id[subscriber_id] = subscriber

        return subscriber_id

    async def unsubscribe(self, subscriber_id: str) -> bool:
        """
        Supprime un abonnement par son identifiant.

        Args:
            subscriber_id: ID retourne par `subscribe()`

        Returns:
            True si l'abonnement existait et a ete supprime, False sinon.
        """
        async with self._lock:
            subscriber = self._subscribers_by_id.pop(subscriber_id, None)
            if subscriber is None:
                return False
            topic_subs = self._subscribers.get(subscriber.topic, [])
            if subscriber in topic_subs:
                topic_subs.remove(subscriber)
            if not topic_subs:
                del self._subscribers[subscriber.topic]
            return True

    async def _dispatcher_loop(self) -> None:
        """
        Boucle principale du dispatcher.
        Consomme la queue et dispatche aux subscribers.
        """
        while self._running:
            try:
                priority_key, event = await self._queue.get()
                if event is None:  # Sentinelle d'arret
                    self._queue.task_done()
                    break

                await self._dispatch(event)
                self._processed_events += 1
                self._queue.task_done()
            except Exception:
                # Le dispatcher ne doit jamais mourir
                continue

    async def _dispatch(self, event: Event) -> None:
        """Dispatche un evenement a tous les subscribers correspondants."""
        handlers: List[Coroutine[Any, Any, None]] = []

        async with self._lock:
            for topic_pattern, subscribers in self._subscribers.items():
                for subscriber in subscribers:
                    if subscriber.matches(event.topic):
                        handlers.append(subscriber.handler(event))

        if handlers:
            # Execution en parallele, pas de garantie d'ordre inter-handler
            await asyncio.gather(*handlers, return_exceptions=True)

    @property
    def stats(self) -> dict[str, Any]:
        """Metriques du bus : subscribers, queue size, dropped, processed."""
        return {
            "subscribers_count": len(self._subscribers_by_id),
            "topics": list(self._subscribers.keys()),
            "queue_size": self._queue.qsize(),
            "dropped_events": self._dropped_events,
            "processed_events": self._processed_events,
            "running": self._running,
        }
```

### 2.2 `app/kernel/config.py` — Configuration Kernel

**Statut:** Reference — la source de verite est `app/config.py` (Pydantic-Settings).

```python
"""
app/kernel/config.py — Configuration du Kernel TAKA OS

Ce fichier est un re-export des parametres kernel depuis app/config.py.
La source de verite unique est Settings (app/config.py) pour eviter
la duplication.

Parametres kernel requis:
    - DATABASE_URL: asyncpg connection string
    - MISTRAL_API_KEY: cle API Mistral AI
    - JWT_SECRET: secret pour la signature JWT
    - JWT_ALGORITHM: algorithme JWT (defaut: HS256)
    - JWT_EXPIRATION_MINUTES: duree de validite (defaut: 60)
    - EVENTBUS_QUEUE_SIZE: taille max queue EventBus (defaut: 10_000)
    - EVENTBUS_DISPATCHER_WORKERS: workers parallele (defaut: 3)
"""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

# Re-export depuis la source de verite
from app.config import Settings as _Settings


class KernelSettings:
    """
    Wrapper type-safe pour les parametres kernel.
    Expose uniquement les cles pertinentes pour le kernel.
    """

    def __init__(self, settings: Optional[_Settings] = None) -> None:
        self._s = settings or _Settings()

    @property
    def database_url(self) -> str:
        return str(self._s.DATABASE_URL)

    @property
    def jwt_secret(self) -> str:
        return str(self._s.JWT_SECRET)

    @property
    def jwt_algorithm(self) -> str:
        return getattr(self._s, "JWT_ALGORITHM", "HS256")

    @property
    def jwt_expiration_minutes(self) -> int:
        return int(getattr(self._s, "JWT_EXPIRATION_MINUTES", 60))

    @property
    def eventbus_queue_size(self) -> int:
        return int(getattr(self._s, "EVENTBUS_QUEUE_SIZE", 10_000))

    @property
    def eventbus_dispatcher_workers(self) -> int:
        return int(getattr(self._s, "EVENTBUS_DISPATCHER_WORKERS", 3))


@lru_cache
def get_kernel_settings() -> KernelSettings:
    """Singleton settings pour le kernel."""
    return KernelSettings()
```

### 2.3 `app/kernel/security.py` — JWT + bcrypt

**Statut:** Specifie dans la documentation existante — re-produit ici pour completude.

```python
"""
app/kernel/security.py — Authentification et autorisation Kernel

- Hashage mots de passe avec bcrypt (12 rounds)
- Generation et verification JWT (HS256)
- Dependance FastAPI `get_current_user()`
- RBAC basique (roles: admin, manager, user, viewer)
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.kernel.config import get_kernel_settings

# --- Configuration securite ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security_scheme = HTTPBearer(auto_error=False)

# --- Modeles Pydantic ---


class TokenPayload(BaseModel):
    """Payload JWT decode."""
    sub: str          # user_id
    tenant_id: str    # tenant pour RLS
    role: str         # role RBAC
    exp: Optional[float] = None


class UserContext(BaseModel):
    """Contexte utilisateur injecte dans les routes protegees."""
    user_id: str
    tenant_id: str
    role: str
    permissions: list[str] = []


# --- Fonctions publiques ---


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifie un mot de passe contre son hash bcrypt."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash un mot de passe avec bcrypt (12 rounds)."""
    return pwd_context.hash(password)


def create_access_token(
    user_id: str,
    tenant_id: str,
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Genere un JWT d'acces.

    Args:
        user_id: Identifiant unique de l'utilisateur
        tenant_id: Tenant pour la isolation RLS
        role: Role RBAC (admin, manager, user, viewer)
        expires_delta: Duree de validite (defaut: 60 minutes)

    Returns:
        Token JWT encode (string)
    """
    settings = get_kernel_settings()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.jwt_expiration_minutes)
    )
    payload = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "role": role,
        "exp": expire,
    }
    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> UserContext:
    """
    Dependance FastAPI : extrait et verifie le JWT de l'en-tete Authorization.

    Raises:
        HTTPException 401: Si le token est manquant, invalide ou expire.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token d'authentification manquant",
            headers={"WWW-Authenticate": "Bearer"},
        )

    settings = get_kernel_settings()
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        token = TokenPayload(**payload)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token invalide: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserContext(
        user_id=token.sub,
        tenant_id=token.tenant_id,
        role=token.role,
    )


def require_role(*allowed_roles: str):
    """
    Factory de dependances FastAPI pour le controle d'acces RBAC.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_role("admin"))])
    """
    async def _checker(user: UserContext = Depends(get_current_user)) -> UserContext:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role}' non autorise. Requis: {allowed_roles}",
            )
        return user
    return _checker
```

### 2.4 `app/kernel/audit.py` — Audit Trail append-only avec hash chain

**Statut:** MVP v0.1 — schema identique en v1.0, distribution ajoutee.

```python
"""
app/kernel/audit.py — Audit Trail append-only avec hash chain SHA-256

Principe: Chaque entree d'audit contient le hash de l'entree precedente,
formant une chaine immuable detectant toute modification.

Chaine:
    hash_current = SHA256(hash_prev || action || entity_id || timestamp)

Usage:
    audit = AuditService(session)
    await audit.log_action(
        action="ao.created",
        entity_type="ao",
        entity_id="123",
        details={"source": "upload_pdf", "filename": "ao.pdf"},
    )
"""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Column, DateTime, ForeignKey, Index, Integer, String, text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Mapped, mapped_column

# Import depuis le fichier modeles unique
from app.models.ao import Base


# ---------------------------------------------------------------------------
# Modele SQLAlchemy — app/models/ao.py (section Audit)
# ---------------------------------------------------------------------------


class AuditLog(Base):
    """
    Entree de journal d'audit append-only.

    Table: audit_logs
    Contrainte: IMMUABLE — aucune operation UPDATE/DELETE n'est autorisee.

    Colonnes:
        id: PK auto-increment
        tenant_id: Tenant pour RLS
        user_id: Utilisateur ayant effectue l'action
        action: Type d'action (ex: "ao.created", "ao.updated", "agent.executed")
        entity_type: Type d'entite concernee (ex: "ao", "agent", "deliberation")
        entity_id: Identifiant de l'entite concernee
        details: Donnees supplementaires (JSONB)
        hash_prev: Hash SHA-256 de l'entree precedente (chainage)
        hash_current: Hash SHA-256 de cette entree (inclut hash_prev)
        created_at: Timestamp de creation (UTC)
    """
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    action: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    details: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    hash_prev: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    hash_current: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )

    __table_args__ = (
        # Index composite pour les recherches par tenant + type d'entite
        Index("ix_audit_logs_tenant_entity", "tenant_id", "entity_type", "entity_id"),
        # Index pour la verification de la chaine
        Index("ix_audit_logs_hash_current", "hash_current", unique=True),
    )

    def verify_chain(self, expected_hash_prev: Optional[str] = None) -> bool:
        """
        Verifie l'integrite de cette entree d'audit.

        Args:
            expected_hash_prev: Le hash_prev attendu (verification chaine complete)

        Returns:
            True si le hash_current est valide et correspond au chainage.
        """
        # Verifie que hash_current est bien calcule
        computed = self._compute_hash()
        if computed != self.hash_current:
            return False

        # Verifie le chainage
        if expected_hash_prev is not None and self.hash_prev != expected_hash_prev:
            return False

        return True

    def _compute_hash(self) -> str:
        """Calcule le hash SHA-256 de cette entree."""
        data = f"{self.hash_prev or ''}{self.action}{self.entity_id}{self.created_at.isoformat()}"
        return hashlib.sha256(data.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Service Audit
# ---------------------------------------------------------------------------


class AuditService:
    """
    Service d'audit append-only avec hash chain.

    Garanties:
        - Immuabilite: aucun UPDATE/DELETE sur audit_logs
        - Integrite: chaine de hash SHA-256 verifiable
        - Tracabilite: chaque action liee a un tenant + user
        - Non-repudiation: le chainage empeche la falsification
    """

    def __init__(self, session: AsyncSession, tenant_id: str = "default") -> None:
        self._session: AsyncSession = session
        self._tenant_id: str = tenant_id

    async def log_action(
        self,
        action: str,
        entity_type: str,
        entity_id: str,
        details: Optional[dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> AuditLog:
        """
        Cree une entree d'audit avec chainage hash.

        Le hash_prev est le hash_current de la derniere entree du meme tenant.
        Le hash_current inclut hash_prev + action + entity_id + timestamp.

        Args:
            action: Type d'action (ex: "ao.created")
            entity_type: Type d'entite (ex: "ao")
            entity_id: ID de l'entite
            details: Donnees JSON supplementaires
            user_id: ID de l'utilisateur responsable

        Returns:
            L'entree AuditLog creee (deja committed)
        """
        # Recupere le dernier hash du tenant
        last_hash = await self._get_last_hash()

        # Prepare l'entree avec un timestamp precis
        now = datetime.now(timezone.utc)

        # Calcule le hash_current
        hash_input = f"{last_hash or ''}{action}{entity_id}{now.isoformat()}"
        hash_current = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

        log = AuditLog(
            tenant_id=self._tenant_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details or {},
            hash_prev=last_hash,
            hash_current=hash_current,
            created_at=now,
        )

        self._session.add(log)
        await self._session.commit()
        return log

    async def verify_chain_integrity(self) -> tuple[bool, Optional[int]]:
        """
        Verifie l'integrite complete de la chaine d'audit du tenant.

        Returns:
            (True, None) si la chaine est valide
            (False, id) si une corruption est detectee a l'entree `id`
        """
        result = await self._session.execute(
            select(AuditLog)
            .where(AuditLog.tenant_id == self._tenant_id)
            .order_by(AuditLog.id.asc())
        )
        logs: List[AuditLog] = result.scalars().all()

        expected_hash_prev: Optional[str] = None
        for log in logs:
            if not log.verify_chain(expected_hash_prev):
                return False, log.id
            expected_hash_prev = log.hash_current

        return True, None

    async def get_entity_history(
        self,
        entity_type: str,
        entity_id: str,
        limit: int = 100,
    ) -> List[AuditLog]:
        """
        Recupere l'historique d'audit d'une entite specifique.

        Args:
            entity_type: Type d'entite
            entity_id: ID de l'entite
            limit: Nombre max d'entrees

        Returns:
            Liste chronologique des AuditLog
        """
        result = await self._session.execute(
            select(AuditLog)
            .where(
                AuditLog.tenant_id == self._tenant_id,
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_id,
            )
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def _get_last_hash(self) -> Optional[str]:
        """Recupere le hash_current de la derniere entree du tenant."""
        result = await self._session.execute(
            select(AuditLog.hash_current)
            .where(AuditLog.tenant_id == self._tenant_id)
            .order_by(AuditLog.id.desc())
            .limit(1)
        )
        row = result.scalar_one_or_none()
        return row


# ---------------------------------------------------------------------------
# Decorateur pour audit automatique
# ---------------------------------------------------------------------------


def auditable(action: str, entity_type: str, entity_id_key: str = "id"):
    """
    Decorateur pour l'audit automatique des methodes de service.

    Usage:
        @auditable(action="ao.created", entity_type="ao")
        async def create_ao(self, ...) -> AO:
            ...
    """
    def decorator(func):
        async def wrapper(self, *args, **kwargs):
            result = await func(self, *args, **kwargs)
            # Audit post-execution
            session = getattr(self, "_session", None)
            tenant_id = getattr(self, "_tenant_id", "default")
            if session is not None:
                audit = AuditService(session, tenant_id)
                entity_id = getattr(result, entity_id_key, str(result))
                await audit.log_action(
                    action=action,
                    entity_type=entity_type,
                    entity_id=str(entity_id),
                    details={"method": func.__name__, "args": str(args), "kwargs_keys": list(kwargs.keys())},
                )
            return result
        return wrapper
    return decorator
```

---

## SECTION 3 — Event Mesh v1.0 (NATS/RabbitMQ)

Le Event Mesh v1.0 remplace le EventBus asyncio in-memory par une infrastructure distribuee basee sur NATS (par defaut) ou RabbitMQ. L'interface Python reste identique — seule l'implementation change.

### 3.1 Schema YAML de configuration

Voir fichier : `config/event_mesh_v1.yaml`

```yaml
# ============================================================
# Event Mesh TAKA OS v1.0 — Configuration NATS/RabbitMQ
# ============================================================
# Ce fichier definit la topologie des topics, les QoS,
# les retentions et les Dead Letter Queues du Event Mesh.
#
# Usage:
#   Le fichier est charge au demarrage du kernel v1.0+
#   et applique automatiquement sur le broker NATS/RabbitMQ.
# ============================================================

version: "1.0"
broker: "nats"  # Options: "nats" | "rabbitmq" | "redis"

# --- Configuration broker ---
connection:
  nats:
    urls:
      - "nats://localhost:4222"
    reconnect_time_wait: 2          # secondes entre tentatives
    max_reconnect_attempts: 10
    ping_interval: 120              # secondes (keepalive)
  rabbitmq:
    host: "localhost"
    port: 5672
    username: "taka"
    password: "${RABBITMQ_PASSWORD}"  # Interpole depuis env
    virtual_host: "/taka"
    heartbeat: 600                  # secondes

# --- Topologie des topics NATS ---
# Les topics utilisent la notation NATS avec wildcards:
#   - "*"  : match un seul token (ex: "taka.ao.*" match "taka.ao.new")
#   - ">"  : match zero ou plusieurs tokens (suffixe uniquement)
topics:
  # --- Domaine Appels d'Offres ---
  - name: "taka.ao.new"
    description: "Nouvel AO detecte (upload PDF ou connector API)"
    qos: "at-least-once"
    retention: "7d"
    dlq: "taka.dlq.ao"
    consumer_groups: ["qualifier", "scorer"]

  - name: "taka.ao.qualified"
    description: "AO qualifie par l'agent Qualifier"
    qos: "at-least-once"
    retention: "7d"
    dlq: "taka.dlq.ao"
    consumer_groups: ["scorer", "tracker"]

  - name: "taka.ao.scored"
    description: "AO note par l'agent Scorer"
    qos: "at-least-once"
    retention: "7d"
    dlq: "taka.dlq.ao"
    consumer_groups: ["tracker"]

  - name: "taka.ao.stage_changed"
    description: "Changement d'etape dans le pipeline AO"
    qos: "at-least-once"
    retention: "30d"
    dlq: "taka.dlq.ao"
    consumer_groups: ["tracker", "notifier"]

  # --- Domaine Agents ---
  - name: "taka.agent.*"
    description: "Wildcard: tous les evenements agents"
    qos: "at-least-once"
    retention: "7d"
    dlq: "taka.dlq.agent"
    consumer_groups: ["lifecycle", "registry"]

  - name: "taka.agent.heartbeat"
    description: "Heartbeat periodique des agents"
    qos: "at-most-once"
    retention: "24h"
    dlq: null  # Pas de DLQ pour heartbeats (donnees transitoires)
    consumer_groups: ["lifecycle"]

  - name: "taka.agent.executed"
    description: "Agent ayant termine une tache"
    qos: "at-least-once"
    retention: "7d"
    dlq: "taka.dlq.agent"
    consumer_groups: ["registry"]

  # --- Domaine Memoire ---
  - name: "taka.memory.index"
    description: "Demande d'indexation d'un document dans pgvector"
    qos: "at-least-once"
    retention: "7d"
    dlq: "taka.dlq.memory"
    consumer_groups: ["indexer"]

  - name: "taka.memory.search"
    description: "Requete de recherche semantique"
    qos: "at-most-once"
    retention: "24h"
    dlq: null
    consumer_groups: ["searcher"]

  - name: "taka.memory.gc"
    description: "Declenchement garbage collection sessions"
    qos: "at-most-once"
    retention: "24h"
    dlq: null
    consumer_groups: ["gc"]

  # --- Domaine Gouvernance ---
  - name: "taka.governance.deliberation.start"
    description: "Demarrage d'une session de deliberation"
    qos: "at-least-once"
    retention: "30d"
    dlq: "taka.dlq.governance"
    consumer_groups: ["governance"]

  - name: "taka.governance.deliberation.vote"
    description: "Vote emis dans une deliberation"
    qos: "at-least-once"
    retention: "30d"
    dlq: "taka.dlq.governance"
    consumer_groups: ["governance"]

  - name: "taka.governance.deliberation.complete"
    description: "Deliberation terminee avec decision"
    qos: "at-least-once"
    retention: "30d"
    dlq: "taka.dlq.governance"
    consumer_groups: ["tracker", "notifier"]

  # --- Domaine Alertes ---
  - name: "taka.alert.deadline"
    description: "Alerte echeance imminente"
    qos: "at-least-once"
    retention: "7d"
    dlq: "taka.dlq.alerts"
    consumer_groups: ["notifier"]

  - name: "taka.alert.security"
    description: "Alerte securite (audit, intrusion)"
    qos: "at-least-once"
    retention: "90d"
    dlq: "taka.dlq.alerts"
    consumer_groups: ["security"]

  # --- Domaine Metriques (fire-and-forget) ---
  - name: "taka.metrics.*"
    description: "Wildcard: toutes les metriques systeme"
    qos: "at-most-once"
    retention: "24h"
    dlq: null
    consumer_groups: ["metrics-aggregator"]

# --- Configuration QoS ---
qos_policies:
  at_least_once:
    description: "L'evenement est livre au moins une fois. Le consumer doit gerer la deduplication."
    ack_mode: "explicit"           # Le consumer doit ack explicitement
    delivery_timeout: 30           # secondes avant retry
    max_retries: 5
    retry_backoff: "exponential"   # linear | exponential | fixed

  at_most_once:
    description: "L'evenement est livre au plus une fois. Perte acceptable."
    ack_mode: "auto"               # Auto-ack, pas de retry
    delivery_timeout: 5
    max_retries: 0

# --- Configuration retention ---
retention_policies:
  "7d":
    max_age: "168h"                # 7 jours
    max_bytes: 1073741824          # 1 GiB par topic
    cleanup_policy: "delete"       # delete | compact

  "24h":
    max_age: "24h"
    max_bytes: 268435456           # 256 MiB par topic
    cleanup_policy: "delete"

  "30d":
    max_age: "720h"                # 30 jours
    max_bytes: 5368709120          # 5 GiB par topic
    cleanup_policy: "delete"

  "90d":
    max_age: "2160h"               # 90 jours
    max_bytes: 10737418240         # 10 GiB par topic
    cleanup_policy: "delete"

# --- Dead Letter Queues ---
dlq:
  enabled: true
  max_deliveries: 5                # Nombre max de tentatives avant DLQ
  retention: "30d"
  topics:
    - name: "taka.dlq.ao"
      source_wildcard: "taka.ao.*"
    - name: "taka.dlq.agent"
      source_wildcard: "taka.agent.*"
    - name: "taka.dlq.memory"
      source_wildcard: "taka.memory.*"
    - name: "taka.dlq.governance"
      source_wildcard: "taka.governance.*"
    - name: "taka.dlq.alerts"
      source_wildcard: "taka.alert.*"

# --- Consumer Groups ---
# Chaque tenant obtient son propre consumer group pour l'isolation
consumer_groups:
  naming_pattern: "taka.cg.{tenant_id}.{topic_short}"
  defaults:
    ack_wait: 30                    # secondes
    max_deliver: 5
    replay_policy: "original"       # original | start_from_beginning
    max_ack_pending: 1000           # messages en attente max

# --- Multi-tenancy ---
# Isolation des topics par tenant via prefixes
multitenancy:
  mode: "prefix"                   # prefix | header | none
  prefix_format: "taka.{tenant_id}."
  default_tenant: "default"
  system_tenant: "taka-system"

# --- Health Check ---
health:
  enabled: true
  topic: "taka.system.health"
  interval: 30                     # secondes
  payload:
    version: "1.0"
    timestamp: "${now}"
```

### 3.2 Classe Python `EventMesh` (v1.0 — meme API que EventBus)

```python
"""
EventMesh v1.0 — Implementation NATS du EventBus.

Expose la meme interface que EventBus (v0.1):
    - publish(event: Event) -> None
    - subscribe(topic: str, handler: Callable) -> str
    - unsubscribe(subscriber_id: str) -> bool
    - start() / stop()

Usage: remplacement drop-in de EventBus.
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Coroutine, Optional

# nats-py : pip install nats-py
import nats
from nats.aio.client import Client as NATSClient
from nats.aio.subscription import Subscription

from app.kernel.bus import Event, EventPriority, Subscriber  # Memes modeles


class EventMesh:
    """
    EventMesh base sur NATS — remplacement v1.0 du EventBus MVP.

    Interface 100% compatible avec EventBus. Le changement est transparent
    pour le reste de l'application.
    """

    def __init__(
        self,
        nats_urls: list[str] = None,
        tenant_id: str = "default",
    ) -> None:
        self._urls: list[str] = nats_urls or ["nats://localhost:4222"]
        self._tenant_id: str = tenant_id
        self._nc: Optional[NATSClient] = None
        self._subscriptions: dict[str, Subscription] = {}
        self._handlers: dict[str, Callable[[Event], Coroutine[Any, Any, None]]] = {}
        self._running: bool = False

    async def start(self) -> None:
        """Connecte au cluster NATS et demarre le mesh."""
        self._nc = await nats.connect(
            servers=self._urls,
            name=f"taka-kernel-{self._tenant_id}",
            reconnect_time_wait=2,
            max_reconnect_attempts=10,
        )
        self._running = True

    async def stop(self) -> None:
        """Deconnecte proprement du cluster NATS."""
        self._running = False
        for sub in self._subscriptions.values():
            await sub.unsubscribe()
        if self._nc:
            await self._nc.close()

    async def publish(self, event: Event) -> None:
        """
        Publie un evenement sur NATS.
        Le topic est prefixe par le tenant si mode multitenant.
        """
        if not self._nc:
            raise RuntimeError("EventMesh non connecte. Appeler start() d'abord.")
        topic = f"taka.{self._tenant_id}.{event.topic}"
        await self._nc.publish(topic, event.to_json().encode())

    async def subscribe(
        self,
        topic: str,
        handler: Callable[[Event], Coroutine[Any, Any, None]],
    ) -> str:
        """
        Souscrit a un topic NATS (avec support wildcards * et >).
        """
        if not self._nc:
            raise RuntimeError("EventMesh non connecte.")
        subscriber_id = f"sub_{topic}_{id(handler)}"
        nats_topic = f"taka.{self._tenant_id}.{topic}"

        async def _nats_handler(msg):
            payload = msg.data.decode()
            data = __import__("json").loads(payload)
            event = Event(
                topic=data["topic"],
                payload=data["payload"],
                priority=EventPriority(data.get("priority", 2)),
                tenant_id=data.get("tenant_id", self._tenant_id),
                timestamp=data["timestamp"],
                event_id=data["event_id"],
            )
            await handler(event)

        sub = await self._nc.subscribe(nats_topic, cb=_nats_handler)
        self._subscriptions[subscriber_id] = sub
        self._handlers[subscriber_id] = handler
        return subscriber_id

    async def unsubscribe(self, subscriber_id: str) -> bool:
        """Supprime une souscription NATS."""
        sub = self._subscriptions.pop(subscriber_id, None)
        self._handlers.pop(subscriber_id, None)
        if sub:
            await sub.unsubscribe()
            return True
        return False

    @property
    def stats(self) -> dict[str, Any]:
        """Metriques du EventMesh."""
        return {
            "connected": self._nc.is_connected if self._nc else False,
            "subscriptions_count": len(self._subscriptions),
            "tenant_id": self._tenant_id,
            "running": self._running,
        }
```

---

## SECTION 4 — Swarm Registry v0.5+

### 4.1 Schema YAML de configuration

Voir fichier : `config/swarm_registry_v1.yaml`

```yaml
# ============================================================
# Swarm Registry TAKA OS v0.5+ — Configuration
# ============================================================
# Le Swarm Registry gere les agents disponibles, leurs capabilities,
# leur statut et leur decouverte.
#
# Ce fichier definit la configuration par defaut du registry.
# Les donnees dynamiques (agents enregistres) sont stockees
# dans PostgreSQL (table `agents`).
# ============================================================

version: "0.5"

# --- Capabilities pre-enregistrees ---
# Chaque capability est un contrat d'interface : input_schema + output_schema
default_capabilities:
  - name: "ao.qualify"
    description: "Qualifie un AO selon les criteres du tenant"
    version: "1.0"
    input_schema:
      type: "object"
      required: ["ao_id", "content", "criteria"]
      properties:
        ao_id: { type: "string" }
        content: { type: "string" }
        criteria: { type: "array", items: { type: "string" } }
    output_schema:
      type: "object"
      required: ["qualified", "score", "reason"]
      properties:
        qualified: { type: "boolean" }
        score: { type: "number", minimum: 0, maximum: 100 }
        reason: { type: "string" }

  - name: "ao.score"
    description: "Attribue un score a un AO qualifie"
    version: "1.0"
    input_schema:
      type: "object"
      required: ["ao_id", "qualification_result"]
      properties:
        ao_id: { type: "string" }
        qualification_result: { type: "object" }
    output_schema:
      type: "object"
      required: ["total_score", "criteria_scores", "recommendation"]
      properties:
        total_score: { type: "number", minimum: 0, maximum: 100 }
        criteria_scores: { type: "object" }
        recommendation: { type: "string", enum: ["pursue", "watch", "ignore"] }

  - name: "ao.track"
    description: "Suit l'avancement d'un AO dans le pipeline"
    version: "1.0"
    input_schema:
      type: "object"
      required: ["ao_id", "stage"]
      properties:
        ao_id: { type: "string" }
        stage: { type: "string", enum: ["new", "qualified", "scored", "bidding", "submitted", "awarded", "lost"] }
    output_schema:
      type: "object"
      required: ["tracked", "next_actions"]
      properties:
        tracked: { type: "boolean" }
        next_actions: { type: "array", items: { type: "string" } }

  - name: "ao.source"
    description: "Recherche de nouveaux AOs sur les plateformes publiques"
    version: "1.0"
    input_schema:
      type: "object"
      required: ["platforms", "keywords"]
      properties:
        platforms: { type: "array", items: { type: "string" } }
        keywords: { type: "array", items: { type: "string" } }
        date_range: { type: "string" }
    output_schema:
      type: "object"
      required: ["aos_found", "count"]
      properties:
        aos_found: { type: "array", items: { type: "object" } }
        count: { type: "integer", minimum: 0 }

  - name: "memory.search"
    description: "Recherche semantique dans la memoire tenant"
    version: "1.0"
    input_schema:
      type: "object"
      required: ["query", "top_k"]
      properties:
        query: { type: "string" }
        top_k: { type: "integer", minimum: 1, maximum: 100 }
        filters: { type: "object" }
    output_schema:
      type: "object"
      required: ["results", "total"]
      properties:
        results: { type: "array", items: { type: "object" } }
        total: { type: "integer" }

  - name: "deliberation.vote"
    description: "Emission d'un vote dans une deliberation"
    version: "1.0"
    input_schema:
      type: "object"
      required: ["session_id", "agent_id", "vote"]
      properties:
        session_id: { type: "string" }
        agent_id: { type: "string" }
        vote: { type: "object" }
    output_schema:
      type: "object"
      required: ["accepted", "vote_id"]
      properties:
        accepted: { type: "boolean" }
        vote_id: { type: "string" }

# --- Configuration discovery ---
discovery:
  endpoint: "/api/v1/agents"
  query_params:
    - name: "capability"
      description: "Filtrer par nom de capability"
      type: "string"
    - name: "status"
      description: "Filtrer par statut d'agent"
      type: "string"
      enum: ["idle", "busy", "debating", "learning", "dead"]
    - name: "vertical_id"
      description: "Filtrer par vertical metier"
      type: "string"
  caching:
    enabled: true
    ttl_seconds: 30

# --- Heartbeat ---
heartbeat:
  interval_seconds: 30
  timeout_seconds: 60
  max_missed: 2                     # Apres 2 heartbeats manques -> status "dead"
  grace_period_seconds: 300         # Delai avant suppression d'un agent "dead"

# --- Auto-respawn ---
auto_respawn:
  enabled: true
  critical_agents:
    - "qualifier"
    - "scorer"
    - "tracker"
  max_respawn_per_hour: 10
  backoff_seconds: [5, 10, 30, 60, 300]
```

### 4.2 Modeles SQLAlchemy — app/models/ao.py (section Swarm Registry)

```python
# app/models/ao.py — EXTRAITS Swarm Registry
# (a integrer dans le fichier unique app/models/ao.py)

import enum
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    ARRAY, Column, DateTime, Float, ForeignKey, Index, Integer,
    String, Text, text,
)
from sqlalchemy.dialects.postgresql import JSONB, ENUM as PGEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship


class AgentStatus(str, enum.Enum):
    """Statuts possibles d'un agent dans le Swarm Registry."""
    IDLE = "idle"           # Pret a executer une tache
    BUSY = "busy"           # En execution d'une tache
    DEBATING = "debating"   # Participe a une deliberation
    LEARNING = "learning"   # En apprentissage (TAKA LAB)
    DEAD = "dead"           # Heartbeat timeout ou crash


class AgentCapabilityModel(Base):
    """
    Capability d'agent enregistree dans le registry.
    
    Table: agent_capabilities
    Une capability est un contrat d'interface (input/output schema).
    """
    __tablename__ = "agent_capabilities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    input_schema: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    output_schema: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    version: Mapped[str] = mapped_column(String(16), nullable=False, default="1.0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )


class AgentModel(Base):
    """
    Agent enregistre dans le Swarm Registry.
    
    Table: agents
    Chaque agent est identifie par un ID unique et expose
    ses capabilities pour la decouverte.
    """
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    vertical_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    capabilities: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )
    status: Mapped[AgentStatus] = mapped_column(
        PGEnum(AgentStatus, name="agent_status"),
        nullable=False,
        default=AgentStatus.IDLE,
        index=True,
    )
    heartbeat_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        onupdate=text("now()"),
        nullable=False,
    )

    __table_args__ = (
        # Index GIN pour la recherche par capabilities
        Index("ix_agents_capabilities_gin", "capabilities", postgresql_using="gin"),
        # Index composite pour la discovery
        Index("ix_agents_status_vertical", "status", "vertical_id"),
    )
```

### 4.3 Interface Python abstraite `Agent`

```python
"""
app/kernel/agent.py — Interface abstraite Agent (Swarm Registry v0.5+)

Tout agent du systeme TAKA OS doit implementer cette interface.
Les agents concrets (Qualifier, Scorer, Tracker, Sourcer) heritent
de cette classe abstraite.

Cycle de vie d'un agent:
    registered -> idle -> busy -> debating -> learning -> dead -> archived

Usage:
    class QualifierAgent(Agent):
        capabilities = [AgentCapability(name="ao.qualify", ...)]

        async def execute(self, task: dict) -> dict:
            # Logique de qualification
            return {"qualified": True, "score": 85}
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from app.kernel.bus import Event, EventBus


# ---------------------------------------------------------------------------
# Modeles de donnees
# ---------------------------------------------------------------------------


class AgentCapability(BaseModel):
    """
    Capability d'un agent — contrat d'interface.

    Attributes:
        name: Nom unique de la capability (ex: "ao.qualify")
        version: Version semver de la capability
        input_schema: Schema JSON des parametres d'entree
        output_schema: Schema JSON des valeurs de sortie
        description: Description fonctionnelle
    """
    name: str = Field(..., min_length=1, max_length=128)
    version: str = Field(default="1.0", pattern=r"^\d+\.\d+\.?\d*$")
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    description: Optional[str] = Field(default=None, max_length=512)


class AgentStatus(str, Enum):
    """Statuts du cycle de vie d'un agent."""
    IDLE = "idle"
    BUSY = "busy"
    DEBATING = "debating"
    LEARNING = "learning"
    DEAD = "dead"


class AgentConfig(BaseModel):
    """Configuration d'un agent."""
    agent_id: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=128)
    vertical_id: Optional[str] = Field(default=None)
    tenant_id: str = Field(default="default")
    heartbeat_interval: int = Field(default=30, ge=5, le=300)  # secondes
    timeout_seconds: int = Field(default=60, ge=10, le=600)
    max_retries: int = Field(default=3, ge=0, le=10)
    critical: bool = Field(default=False)  # Auto-respawn si True


# ---------------------------------------------------------------------------
# Classe abstraite Agent
# ---------------------------------------------------------------------------


class Agent(ABC):
    """
    Interface abstraite que tout agent TAKA OS doit implementer.

    Attributes:
        config: Configuration de l'agent (AgentConfig)
        capabilities: Liste des capabilities supportees
        status: Statut courant (idle|busy|debating|learning|dead)
        bus: Reference vers l'EventBus/EventMesh
        _heartbeat_task: Tache asyncio du heartbeat
        _current_task: Tache courante en execution

    Methode execute:
        Point d'entree principal. Recoit un task (dict) et retourne un resultat (dict).
        Le mapping task -> capability se fait via le champ 'capability' du task.

    Methode heartbeat:
        Envoie un signal de vie periodique au Swarm Registry.

    Methode on_event:
        Gestionnaire d'evenements du EventBus. Permet la communication
        inter-agents et la reaction aux evenements du systeme.
    """

    def __init__(
        self,
        config: AgentConfig,
        bus: EventBus,
    ) -> None:
        self.config: AgentConfig = config
        self.capabilities: list[AgentCapability] = []
        self.status: Literal["idle", "busy", "debating", "learning", "dead"] = "idle"
        self.bus: EventBus = bus
        self._heartbeat_task: Optional[Any] = None
        self._current_task: Optional[Any] = None
        self._execution_count: int = 0
        self._error_count: int = 0
        self._last_execution_at: Optional[datetime] = None

    @abstractmethod
    async def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Execute une tache et retourne le resultat.

        Args:
            task: Dict contenant au minimum:
                - capability: str — nom de la capability a executer
                - params: dict — parametres d'entree

        Returns:
            Dict contenant les resultats selon le output_schema de la capability.

        Raises:
            ValueError: Si la capability demandee n'est pas supportee.
            RuntimeError: Si l'agent est en statut "dead".
        """
        ...

    @abstractmethod
    async def heartbeat(self) -> dict[str, Any]:
        """
        Signale que l'agent est en vie au Swarm Registry.

        Returns:
            Dict avec les metriques de l'agent:
                - agent_id: str
                - status: str
                - capabilities: list[str]
                - execution_count: int
                - error_count: int
                - timestamp: float
        """
        ...

    @abstractmethod
    async def on_event(self, event: Event) -> None:
        """
        Gestionnaire d'evenements du EventBus.

        Permet a l'agent de reagir aux evenements du systeme
        sans execution explicite. Ex: un agent Tracker peut
        ecouter 'ao.stage_changed' pour mettre a jour son suivi.

        Args:
            event: Evenement du EventBus
        """
        ...

    # --- Methodes concretes (non abstraites) ---

    def supports(self, capability_name: str) -> bool:
        """Verifie si l'agent supporte une capability."""
        return any(c.name == capability_name for c in self.capabilities)

    def get_capability(self, capability_name: str) -> Optional[AgentCapability]:
        """Recupere la definition d'une capability."""
        for c in self.capabilities:
            if c.name == capability_name:
                return c
        return None

    async def start_heartbeat(self) -> None:
        """Demarre la boucle de heartbeat periodique."""
        if self._heartbeat_task is not None:
            return
        self._heartbeat_task = asyncio.create_task(
            self._heartbeat_loop(), name=f"heartbeat-{self.config.agent_id}"
        )

    async def stop_heartbeat(self) -> None:
        """Arrete la boucle de heartbeat."""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None

    async def _heartbeat_loop(self) -> None:
        """Boucle de heartbeat infinie."""
        while self.status != "dead":
            try:
                heartbeat_data = await self.heartbeat()
                await self.bus.publish(
                    Event(
                        topic="agent.heartbeat",
                        payload=heartbeat_data,
                        tenant_id=self.config.tenant_id,
                    )
                )
            except Exception:
                self._error_count += 1
            await asyncio.sleep(self.config.heartbeat_interval)

    @property
    def metrics(self) -> dict[str, Any]:
        """Metriques d'execution de l'agent."""
        return {
            "agent_id": self.config.agent_id,
            "name": self.config.name,
            "status": self.status,
            "capabilities": [c.name for c in self.capabilities],
            "execution_count": self._execution_count,
            "error_count": self._error_count,
            "last_execution_at": (
                self._last_execution_at.isoformat()
                if self._last_execution_at else None
            ),
            "critical": self.config.critical,
        }
```

---

## SECTION 5 — Memory Mesh v1.1+

### 5.1 Vue d'ensemble des 3 zones memoire

Le Memory Mesh v1.1 organise la memoire en 3 zones isolees:

| Zone | Scope | Persistence | Backend | Use Case |
|------|-------|-------------|---------|----------|
| **Global** | Systeme | Persistante | PostgreSQL | Configuration, regles globales, indexes |
| **Tenant** | Tenant | Persistante | PostgreSQL + pgvector | Donnees metiers, embeddings, historique |
| **Session** | Session | Ephemere (TTL 24h) | PostgreSQL + asyncio TTL | Contexte conversationnel, etat transient |

### 5.2 Modeles SQLAlchemy — app/models/ao.py (section Memory Mesh)

```python
# app/models/ao.py — EXTRAITS Memory Mesh
# (a integrer dans le fichier unique app/models/ao.py)

from sqlalchemy.dialects.postgresql import JSONB, ARRAY, FLOAT
from pgvector.sqlalchemy import Vector  # pip install pgvector


# --- Zone Global ---

class MemoryGlobal(Base):
    """
    Memoire globale — configuration systeme et regles.
    
    Table: memory_global
    Cle-valeur JSONB pour la flexibilite. Pas d'embedding
    car ce sont des donnees structurees, pas semantiques.
    """
    __tablename__ = "memory_global"

    key: Mapped[str] = mapped_column(String(256), primary_key=True)
    value: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        onupdate=text("now()"),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_memory_global_updated", "updated_at"),
    )


# --- Zone Tenant ---

class MemoryTenant(Base):
    """
    Memoire tenant — donnees metiers avec embeddings vectoriels.
    
    Table: memory_tenant
    Stocke les donnees metiers par tenant avec recherche
    semantique via pgvector. Chaque entree a un niveau
    d'importance et des tags pour le filtrage.
    
    Dimensions d'embedding: 1024 (Mistral embed)
    """
    __tablename__ = "memory_tenant"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    key: Mapped[str] = mapped_column(String(256), nullable=False)
    value: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    # Embedding vectoriel Mistral (1024 dimensions)
    embedding: Mapped[Optional[Any]] = mapped_column(
        Vector(1024), nullable=True
    )
    tags: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )
    importance: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.5
    )
    ttl: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0  # 0 = pas de TTL
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        onupdate=text("now()"),
        nullable=False,
    )

    __table_args__ = (
        # Contrainte d'unicite tenant + cle
        Index("ix_memory_tenant_tenant_key", "tenant_id", "key", unique=True),
        # Index HNSW pour la recherche vectorielle (pgvector)
        Index(
            "ix_memory_tenant_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
        # Index GIN pour les tags
        Index("ix_memory_tenant_tags_gin", "tags", postgresql_using="gin"),
        # Index pour le filtrage par importance
        Index("ix_memory_tenant_importance", "tenant_id", "importance"),
    )


# --- Zone Session ---

class MemorySession(Base):
    """
    Memoire session — contexte conversationnel ephemere.
    
    Table: memory_session
    Stocke le contexte d'une session utilisateur avec TTL.
    Le garbage collector efface les sessions expirees.
    
    TTL: 24h par defaut (86400 secondes).
    """
    __tablename__ = "memory_session"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    context: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    messages: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        onupdate=text("now()"),
        nullable=False,
    )

    __table_args__ = (
        # Index composite pour le GC (sessions expirees par tenant)
        Index("ix_memory_session_expires", "tenant_id", "expires_at"),
        # Index pour les sessions actives d'un utilisateur
        Index("ix_memory_session_user", "tenant_id", "user_id", "created_at"),
    )
```

### 5.3 Service Memory Mesh

```python
"""
app/kernel/memory.py — Memory Mesh Service (v1.1)

Abstraction unifiee sur les 3 zones de memoire.
Le service expose une API coherente quel que soit la zone.

Usage:
    memory = MemoryMesh(session, tenant_id="acme")
    
    # Zone Global
    await memory.global_set("system.prompt", {"text": "..."})
    
    # Zone Tenant (avec embedding automatique)
    await memory.tenant_set("ao.123", {"title": "..."}, embedding=vector)
    results = await memory.tenant_search("construction batiment", top_k=5)
    
    # Zone Session
    await memory.session_create("sess_abc", user_id="user_1")
    await memory.session_append_message("sess_abc", {"role": "user", "content": "..."})
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select, text, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.ao import MemoryGlobal, MemoryTenant, MemorySession


class MemoryMesh:
    """
    Service Memory Mesh — abstraction unifiee des 3 zones.

    Attributes:
        _session: Session SQLAlchemy async
        _tenant_id: Tenant courant (isolation RLS)
        _embedding_dim: Dimension des embeddings (defaut: 1024)
    """

    def __init__(
        self,
        session: AsyncSession,
        tenant_id: str = "default",
        embedding_dim: int = 1024,
    ) -> None:
        self._session: AsyncSession = session
        self._tenant_id: str = tenant_id
        self._embedding_dim: int = embedding_dim

    # === Zone Global ===

    async def global_get(self, key: str) -> Optional[dict[str, Any]]:
        """Recupere une valeur de la memoire globale."""
        result = await self._session.execute(
            select(MemoryGlobal).where(MemoryGlobal.key == key)
        )
        row = result.scalar_one_or_none()
        return row.value if row else None

    async def global_set(self, key: str, value: dict[str, Any]) -> MemoryGlobal:
        """Cree ou met a jour une valeur dans la memoire globale."""
        result = await self._session.execute(
            select(MemoryGlobal).where(MemoryGlobal.key == key)
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.value = value
            existing.updated_at = datetime.now(timezone.utc)
            await self._session.commit()
            return existing

        entry = MemoryGlobal(key=key, value=value)
        self._session.add(entry)
        await self._session.commit()
        return entry

    # === Zone Tenant (avec pgvector) ===

    async def tenant_set(
        self,
        key: str,
        value: dict[str, Any],
        embedding: Optional[List[float]] = None,
        tags: Optional[List[str]] = None,
        importance: float = 0.5,
        ttl: int = 0,
    ) -> MemoryTenant:
        """
        Stocke une donnee dans la memoire tenant.

        Args:
            key: Cle unique dans le tenant
            value: Donnees JSONB
            embedding: Vecteur d'embedding (1024 dims) pour recherche semantique
            tags: Tags pour le filtrage
            importance: Score d'importance (0.0 - 1.0)
            ttl: Time-to-live en secondes (0 = infini)
        """
        result = await self._session.execute(
            select(MemoryTenant).where(
                MemoryTenant.tenant_id == self._tenant_id,
                MemoryTenant.key == key,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.value = value
            if embedding is not None:
                existing.embedding = embedding
            if tags is not None:
                existing.tags = tags
            existing.importance = importance
            existing.ttl = ttl
            existing.updated_at = datetime.now(timezone.utc)
            await self._session.commit()
            return existing

        entry = MemoryTenant(
            tenant_id=self._tenant_id,
            key=key,
            value=value,
            embedding=embedding,
            tags=tags or [],
            importance=importance,
            ttl=ttl,
        )
        self._session.add(entry)
        await self._session.commit()
        return entry

    async def tenant_search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        tags: Optional[List[str]] = None,
        min_importance: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Recherche semantique par similarite cosinus dans la memoire tenant.

        Args:
            query_embedding: Vecteur de la requete (1024 dims)
            top_k: Nombre max de resultats
            tags: Filtrer par tags (AND logique)
            min_importance: Importance minimum

        Returns:
            Liste de dicts: {key, value, similarity, tags, importance}
        """
        # Requete pgvector avec cosine similarity
        stmt = select(
            MemoryTenant.key,
            MemoryTenant.value,
            MemoryTenant.tags,
            MemoryTenant.importance,
            (1 - MemoryTenant.embedding.cosine_distance(query_embedding)).label("similarity"),
        ).where(
            MemoryTenant.tenant_id == self._tenant_id,
            MemoryTenant.importance >= min_importance,
        ).order_by(
            MemoryTenant.embedding.cosine_distance(query_embedding)
        ).limit(top_k)

        if tags:
            for tag in tags:
                stmt = stmt.where(MemoryTenant.tags.contains([tag]))

        result = await self._session.execute(stmt)
        rows = result.all()

        return [
            {
                "key": row.key,
                "value": row.value,
                "similarity": float(row.similarity),
                "tags": row.tags,
                "importance": row.importance,
            }
            for row in rows
        ]

    async def tenant_get(self, key: str) -> Optional[dict[str, Any]]:
        """Recupere une valeur de la memoire tenant par cle."""
        result = await self._session.execute(
            select(MemoryTenant).where(
                MemoryTenant.tenant_id == self._tenant_id,
                MemoryTenant.key == key,
            )
        )
        row = result.scalar_one_or_none()
        return row.value if row else None

    async def tenant_delete(self, key: str) -> bool:
        """Supprime une entree de la memoire tenant."""
        result = await self._session.execute(
            delete(MemoryTenant).where(
                MemoryTenant.tenant_id == self._tenant_id,
                MemoryTenant.key == key,
            )
        )
        await self._session.commit()
        return result.rowcount > 0

    # === Zone Session ===

    async def session_create(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
        ttl_hours: int = 24,
    ) -> MemorySession:
        """
        Cree une nouvelle session avec TTL.

        Args:
            session_id: Identifiant unique de session
            user_id: Utilisateur associe
            context: Contexte initial
            ttl_hours: Duree de vie en heures (defaut: 24)
        """
        expires_at = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)
        session = MemorySession(
            session_id=session_id,
            tenant_id=self._tenant_id,
            user_id=user_id,
            context=context or {},
            messages=[],
            expires_at=expires_at,
        )
        self._session.add(session)
        await self._session.commit()
        return session

    async def session_get(self, session_id: str) -> Optional[MemorySession]:
        """Recupere une session par ID (verifie l'expiration)."""
        result = await self._session.execute(
            select(MemorySession).where(
                MemorySession.session_id == session_id,
                MemorySession.tenant_id == self._tenant_id,
            )
        )
        session = result.scalar_one_or_none()
        if session and session.expires_at < datetime.now(timezone.utc):
            return None  # Session expiree
        return session

    async def session_append_message(
        self,
        session_id: str,
        message: dict[str, Any],
    ) -> Optional[MemorySession]:
        """
        Ajoute un message a la session.

        Args:
            session_id: ID de la session
            message: Dict avec au moins 'role' et 'content'
        """
        session = await self.session_get(session_id)
        if not session:
            return None

        message["timestamp"] = datetime.now(timezone.utc).isoformat()
        session.messages.append(message)
        session.updated_at = datetime.now(timezone.utc)
        await self._session.commit()
        return session

    async def session_update_context(
        self,
        session_id: str,
        context: dict[str, Any],
    ) -> Optional[MemorySession]:
        """Met a jour le contexte d'une session."""
        session = await self.session_get(session_id)
        if not session:
            return None
        session.context.update(context)
        session.updated_at = datetime.now(timezone.utc)
        await self._session.commit()
        return session

    async def session_delete(self, session_id: str) -> bool:
        """Supprime une session manuellement."""
        result = await self._session.execute(
            delete(MemorySession).where(
                MemorySession.session_id == session_id,
                MemorySession.tenant_id == self._tenant_id,
            )
        )
        await self._session.commit()
        return result.rowcount > 0

    # === Garbage Collection ===

    async def gc_expired_sessions(self) -> int:
        """
        Efface les sessions expirees. A appeler par un cronjob
        ou l'agent de maintenance.

        Returns:
            Nombre de sessions supprimees.
        """
        now = datetime.now(timezone.utc)
        result = await self._session.execute(
            delete(MemorySession).where(
                MemorySession.tenant_id == self._tenant_id,
                MemorySession.expires_at < now,
            )
        )
        await self._session.commit()
        return result.rowcount or 0

    async def gc_expired_tenant_entries(self) -> int:
        """
        Efface les entrees tenant dont le TTL est expire.
        
        Returns:
            Nombre d'entrees supprimees.
        """
        now = datetime.now(timezone.utc)
        result = await self._session.execute(
            delete(MemoryTenant).where(
                MemoryTenant.tenant_id == self._tenant_id,
                MemoryTenant.ttl > 0,
                MemoryTenant.created_at < now - text("interval '1 second' * memory_tenant.ttl"),
            )
        )
        await self._session.commit()
        return result.rowcount or 0
```

---

## SECTION 6 — Governance Core v0.3+

### 6.1 Vue d'ensemble

Le Governance Core gere les deliberations multi-agents (parlement d'agents). Un processus de deliberation:

1. **Initialisation**: Un `DeliberationSession` est cree avec un sujet et N agents participants
2. **Vote**: Chaque agent emet un vote selon le mode de vote defini
3. **Resolution**: Les votes sont agreges selon le mode (majority, borda, consensus, unanimous)
4. **Transcription**: Le transcript complet est sauvegarde (append-only, immuable)

### 6.2 Modeles SQLAlchemy — app/models/ao.py (section Governance)

```python
# app/models/ao.py — EXTRAITS Governance Core
# (a integrer dans le fichier unique app/models/ao.py)

import enum


class VoteMode(str, enum.Enum):
    """Modes de vote supportes par le Governance Core."""
    MAJORITY = "majority"      # >50% des voix
    BORDA = "borda"            # Comptage Borda (classement pondere)
    CONSENSUS = "consensus"    # >66% des voix
    UNANIMOUS = "unanimous"    # 100% des voix


class DeliberationStatus(str, enum.Enum):
    """Statuts d'une session de deliberation."""
    PENDING = "pending"        # En attente de demarrage
    ACTIVE = "active"          # Deliberation en cours
    VOTING = "voting"          # Phase de vote
    COMPLETED = "completed"    # Deliberation terminee
    CANCELLED = "cancelled"    # Annulee


class DeliberationSession(Base):
    """
    Session de deliberation multi-agents.
    
    Table: deliberation_sessions
    Represente une deliberation sur un sujet specifique
    avec un ensemble d'agents votants.
    """
    __tablename__ = "deliberation_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    topic: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mode: Mapped[VoteMode] = mapped_column(
        PGEnum(VoteMode, name="vote_mode"),
        nullable=False,
    )
    status: Mapped[DeliberationStatus] = mapped_column(
        PGEnum(DeliberationStatus, name="deliberation_status"),
        nullable=False,
        default=DeliberationStatus.PENDING,
    )
    agent_ids: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False
    )
    quorum: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1
    )
    result: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )

    # Relations
    votes: Mapped[List["DeliberationVote"]] = relationship(
        "DeliberationVote",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    transcripts: Mapped[List["DeliberationTranscript"]] = relationship(
        "DeliberationTranscript",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="DeliberationTranscript.sequence.asc()",
    )


class DeliberationVote(Base):
    """
    Vote emis dans une deliberation.
    
    Table: deliberation_votes
    Chaque vote est lie a une session et un agent.
    Le payload du vote depend du mode (bool, ranking, score).
    """
    __tablename__ = "deliberation_votes"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    session_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("deliberation_sessions.id"), nullable=False, index=True
    )
    agent_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    vote_payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False  # Structure depend du mode de vote
    )
    weight: Mapped[float] = mapped_column(
        Float, nullable=False, default=1.0
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )

    # Relation
    session: Mapped["DeliberationSession"] = relationship(
        "DeliberationSession", back_populates="votes"
    )

    __table_args__ = (
        # Un seul vote par agent par session
        Index("ix_votes_session_agent", "session_id", "agent_id", unique=True),
    )


class DeliberationTranscript(Base):
    """
    Transcript immuable d'une deliberation.
    
    Table: deliberation_transcripts
    Journal append-only de chaque etape de la deliberation.
    Immuable — aucune modification n'est autorisee apres creation.
    
    Types d'entree:
        - session.started   : Demarrage de la session
        - agent.joined      : Agent rejoint
        - agent.voted       : Agent a vote
        - vote.recorded     : Vote enregistre
        - result.computed   : Resultat calcule
        - session.completed : Session terminee
        - agent.reasoning   : Raisonnement d'un agent
    """
    __tablename__ = "deliberation_transcripts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    session_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("deliberation_sessions.id"), nullable=False, index=True
    )
    sequence: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    entry_type: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )
    agent_id: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, index=True
    )
    content: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )

    # Relation
    session: Mapped["DeliberationSession"] = relationship(
        "DeliberationSession", back_populates="transcripts"
    )

    __table_args__ = (
        # Ordre chronologique garanti par sequence
        Index("ix_transcripts_session_seq", "session_id", "sequence"),
    )
```

### 6.3 Service Governance Core

```python
"""
app/kernel/governance.py — Governance Core Service (v0.3+)

Moteur de deliberation multi-agents. Gere le cycle complet:
  creation -> vote -> resolution -> transcript

Modes de vote:
    majority  : >50% des voix ponderees
    borda     : Comptage de Borda (classement par preference)
    consensus : >66% des voix ponderees
    unanimous : 100% des voix

Usage:
    gov = GovernanceService(session, bus)
    session = await gov.create_session(
        topic="Qualifier cet AO?",
        mode=VoteMode.MAJORITY,
        agent_ids=["qualifier", "scorer"],
    )
    await gov.submit_vote(session.id, "qualifier", {"decision": True, "confidence": 0.9})
    result = await gov.resolve_session(session.id)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.kernel.bus import Event, EventBus
from app.models.ao import (
    DeliberationSession, DeliberationVote, DeliberationTranscript,
    VoteMode, DeliberationStatus,
)


class VoteResult(BaseModel):
    """Resultat d'une deliberation."""
    decision: Any                            # Valeur decidee
    confidence: float                        # Score de confiance (0-1)
    votes_cast: int                          # Nombre de votes
    votes_required: int                      # Quorum requis
    vote_breakdown: Dict[str, Any]           # Detail par option/vote
    mode: str                                # Mode de vote utilise
    unanimous: bool                          # Unanimite atteinte?


class GovernanceService:
    """
    Service de gouvernance et deliberation multi-agents.

    Attributes:
        _session: Session SQLAlchemy async
        _bus: EventBus pour la publication des evenements
        _audit: AuditService pour la tracabilite
    """

    def __init__(
        self,
        session: AsyncSession,
        bus: EventBus,
        tenant_id: str = "default",
    ) -> None:
        self._session: AsyncSession = session
        self._bus: EventBus = bus
        self._tenant_id: str = tenant_id

    async def create_session(
        self,
        topic: str,
        mode: VoteMode,
        agent_ids: List[str],
        description: Optional[str] = None,
        quorum: Optional[int] = None,
    ) -> DeliberationSession:
        """
        Cree une nouvelle session de deliberation.

        Args:
            topic: Sujet de la deliberation
            mode: Mode de vote (majority/borda/consensus/unanimous)
            agent_ids: Liste des IDs d'agents participants
            description: Description optionnelle
            quorum: Nombre minimum de votes (defaut: ceil(len(agent_ids) / 2))

        Returns:
            La session creee
        """
        session_id = f"delib_{__import__('uuid').uuid4().hex[:12]}"
        effective_quorum = quorum or max(1, (len(agent_ids) + 1) // 2)

        session = DeliberationSession(
            id=session_id,
            tenant_id=self._tenant_id,
            topic=topic,
            description=description,
            mode=mode,
            status=DeliberationStatus.PENDING,
            agent_ids=agent_ids,
            quorum=effective_quorum,
        )
        self._session.add(session)
        await self._session.commit()

        # Transcript: session creee
        await self._append_transcript(session_id, 0, "session.created", None, {
            "topic": topic, "mode": mode.value, "agents": agent_ids,
        })

        # Publie evenement
        await self._bus.publish(Event(
            topic="governance.deliberation.start",
            payload={"session_id": session_id, "topic": topic, "agents": agent_ids},
            tenant_id=self._tenant_id,
        ))

        return session

    async def start_session(self, session_id: str) -> DeliberationSession:
        """Demarre la session (transition PENDING -> ACTIVE)."""
        session = await self._get_session(session_id)
        if session.status != DeliberationStatus.PENDING:
            raise ValueError(f"Session {session_id} n'est pas en attente (status: {session.status})")

        session.status = DeliberationStatus.ACTIVE
        session.started_at = datetime.now(timezone.utc)
        await self._session.commit()

        # Transcript
        seq = len(session.transcripts)
        await self._append_transcript(session_id, seq, "session.started", None, {})

        for agent_id in session.agent_ids:
            seq += 1
            await self._append_transcript(session_id, seq, "agent.joined", agent_id, {})

        return session

    async def submit_vote(
        self,
        session_id: str,
        agent_id: str,
        vote_payload: dict[str, Any],
        weight: float = 1.0,
    ) -> DeliberationVote:
        """
        Soumet un vote pour un agent dans une session.

        Args:
            session_id: ID de la session
            agent_id: ID de l'agent votant
            vote_payload: Contenu du vote (structure selon le mode)
            weight: Poids du vote (defaut: 1.0)

        Raises:
            ValueError: Si l'agent n'est pas participant ou a deja vote.
        """
        session = await self._get_session(session_id)

        if agent_id not in session.agent_ids:
            raise ValueError(f"Agent {agent_id} n'est pas participant")

        if session.status not in (DeliberationStatus.ACTIVE, DeliberationStatus.VOTING):
            raise ValueError(f"Session {session_id} n'accepte pas de votes (status: {session.status})")

        # Verifie si l'agent a deja vote
        existing = await self._session.execute(
            select(DeliberationVote).where(
                DeliberationVote.session_id == session_id,
                DeliberationVote.agent_id == agent_id,
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Agent {agent_id} a deja vote dans cette session")

        vote_id = f"vote_{__import__('uuid').uuid4().hex[:12]}"
        vote = DeliberationVote(
            id=vote_id,
            session_id=session_id,
            agent_id=agent_id,
            vote_payload=vote_payload,
            weight=weight,
        )
        self._session.add(vote)

        # Transition vers VOTING si premier vote
        if session.status == DeliberationStatus.ACTIVE:
            session.status = DeliberationStatus.VOTING

        await self._session.commit()

        # Transcript
        seq = await self._next_sequence(session_id)
        await self._append_transcript(session_id, seq, "vote.recorded", agent_id, {
            "vote_id": vote_id,
            "weight": weight,
        })

        # Evenement
        await self._bus.publish(Event(
            topic="governance.deliberation.vote",
            payload={"session_id": session_id, "agent_id": agent_id, "vote_id": vote_id},
            tenant_id=self._tenant_id,
        ))

        return vote

    async def resolve_session(self, session_id: str) -> VoteResult:
        """
        Resout la deliberation en agregant les votes.

        Args:
            session_id: ID de la session a resoudre

        Returns:
            VoteResult avec la decision et les metadonnees

        Raises:
            ValueError: Si le quorum n'est pas atteint.
        """
        session = await self._get_session(session_id)

        # Recupere tous les votes
        result = await self._session.execute(
            select(DeliberationVote).where(
                DeliberationVote.session_id == session_id
            )
        )
        votes: List[DeliberationVote] = list(result.scalars().all())

        if len(votes) < session.quorum:
            raise ValueError(
                f"Quorum non atteint: {len(votes)}/{session.quorum} votes"
            )

        # Agregation selon le mode
        if session.mode == VoteMode.MAJORITY:
            vote_result = self._resolve_majority(votes)
        elif session.mode == VoteMode.BORDA:
            vote_result = self._resolve_borda(votes)
        elif session.mode == VoteMode.CONSENSUS:
            vote_result = self._resolve_consensus(votes)
        elif session.mode == VoteMode.UNANIMOUS:
            vote_result = self._resolve_unanimous(votes)
        else:
            raise ValueError(f"Mode de vote inconnu: {session.mode}")

        # Met a jour la session
        session.result = vote_result.model_dump()
        session.status = DeliberationStatus.COMPLETED
        session.completed_at = datetime.now(timezone.utc)
        await self._session.commit()

        # Transcript final
        seq = await self._next_sequence(session_id)
        await self._append_transcript(session_id, seq, "result.computed", None, {
            "result": vote_result.model_dump(),
        })
        seq += 1
        await self._append_transcript(session_id, seq, "session.completed", None, {})

        # Evenement
        await self._bus.publish(Event(
            topic="governance.deliberation.complete",
            payload={
                "session_id": session_id,
                "decision": vote_result.decision,
                "confidence": vote_result.confidence,
            },
            tenant_id=self._tenant_id,
        ))

        return vote_result

    # === Methodes de resolution ===

    def _resolve_majority(self, votes: List[DeliberationVote]) -> VoteResult:
        """Resolution par majorite simple (>50%)."""
        total_weight = sum(v.weight for v in votes)
        options: Dict[str, float] = {}

        for v in votes:
            decision = str(v.vote_payload.get("decision", "abstain"))
            options[decision] = options.get(decision, 0.0) + v.weight

        if not options:
            return VoteResult(decision=None, confidence=0.0, votes_cast=len(votes), votes_required=0, vote_breakdown={}, mode="majority", unanimous=False)

        winner = max(options, key=options.get)
        confidence = options[winner] / total_weight if total_weight > 0 else 0

        return VoteResult(
            decision=winner,
            confidence=confidence,
            votes_cast=len(votes),
            votes_required=int(total_weight / 2) + 1,
            vote_breakdown=options,
            mode="majority",
            unanimous=confidence == 1.0,
        )

    def _resolve_borda(self, votes: List[DeliberationVote]) -> VoteResult:
        """Resolution par comptage de Borda (classement pondere)."""
        scores: Dict[str, float] = {}

        for v in votes:
            ranking = v.vote_payload.get("ranking", [])
            n = len(ranking)
            for idx, option in enumerate(ranking):
                borda_score = (n - idx) * v.weight
                scores[option] = scores.get(option, 0.0) + borda_score

        if not scores:
            return VoteResult(decision=None, confidence=0.0, votes_cast=len(votes), votes_required=0, vote_breakdown={}, mode="borda", unanimous=False)

        winner = max(scores, key=scores.get)
        total = sum(scores.values())
        confidence = scores[winner] / total if total > 0 else 0

        return VoteResult(
            decision=winner,
            confidence=confidence,
            votes_cast=len(votes),
            votes_required=1,
            vote_breakdown=scores,
            mode="borda",
            unanimous=False,
        )

    def _resolve_consensus(self, votes: List[DeliberationVote]) -> VoteResult:
        """Resolution par consensus (>66%)."""
        total_weight = sum(v.weight for v in votes)
        options: Dict[str, float] = {}

        for v in votes:
            decision = str(v.vote_payload.get("decision", "abstain"))
            options[decision] = options.get(decision, 0.0) + v.weight

        if not options:
            return VoteResult(decision=None, confidence=0.0, votes_cast=len(votes), votes_required=0, vote_breakdown={}, mode="consensus", unanimous=False)

        winner = max(options, key=options.get)
        confidence = options[winner] / total_weight if total_weight > 0 else 0
        threshold = total_weight * 2 / 3

        return VoteResult(
            decision=winner if options[winner] > threshold else None,
            confidence=confidence,
            votes_cast=len(votes),
            votes_required=int(threshold) + 1,
            vote_breakdown=options,
            mode="consensus",
            unanimous=confidence == 1.0,
        )

    def _resolve_unanimous(self, votes: List[DeliberationVote]) -> VoteResult:
        """Resolution a l'unanimite (100%)."""
        decisions = [str(v.vote_payload.get("decision")) for v in votes]
        unique = set(decisions)

        is_unanimous = len(unique) == 1 and len(decisions) > 0
        decision = decisions[0] if is_unanimous else None

        return VoteResult(
            decision=decision,
            confidence=1.0 if is_unanimous else len(unique) / len(decisions) if decisions else 0,
            votes_cast=len(votes),
            votes_required=len(votes),
            vote_breakdown={d: decisions.count(d) for d in unique},
            mode="unanimous",
            unanimous=is_unanimous,
        )

    # === Helpers ===

    async def _get_session(self, session_id: str) -> DeliberationSession:
        """Recupere une session avec ses relations."""
        result = await self._session.execute(
            select(DeliberationSession).where(
                DeliberationSession.id == session_id,
                DeliberationSession.tenant_id == self._tenant_id,
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise ValueError(f"Session {session_id} introuvable")
        return session

    async def _append_transcript(
        self,
        session_id: str,
        sequence: int,
        entry_type: str,
        agent_id: Optional[str],
        content: dict[str, Any],
    ) -> DeliberationTranscript:
        """Ajoute une entree au transcript."""
        transcript = DeliberationTranscript(
            id=f"trans_{__import__('uuid').uuid4().hex[:12]}",
            session_id=session_id,
            sequence=sequence,
            entry_type=entry_type,
            agent_id=agent_id,
            content=content,
        )
        self._session.add(transcript)
        await self._session.commit()
        return transcript

    async def _next_sequence(self, session_id: str) -> int:
        """Calcule la prochaine sequence pour un transcript."""
        result = await self._session.execute(
            select(func.count(DeliberationTranscript.id)).where(
                DeliberationTranscript.session_id == session_id
            )
        )
        return result.scalar() or 0

    async def get_session_transcript(self, session_id: str) -> List[DeliberationTranscript]:
        """Recupere le transcript complet d'une session."""
        session = await self._get_session(session_id)
        return list(session.transcripts)
```

---

## SECTION 7 — Lifecycle Manager v0.5+

### 7.1 Vue d'ensemble

Le Lifecycle Manager gere le cycle de vie des agents via une machine a etats (FSM). Il assure:

- **Enregistrement**: Les agents s'enregistrent au demarrage
- **Monitoring**: Heartbeat periodique avec timeout de 60s
- **Transitions**: Changements d'etat valides avec guards
- **Auto-respawn**: Redemarrage automatique des agents critiques
- **GC**: Nettoyage des sessions expirees et agents morts

### 7.2 Diagramme d'etats

```
+-----------+    register     +------+    claim_task    +------+
|           | --------------> |      | --------------> |      |
|REGISTERED |                 | IDLE |                 | BUSY |
|           |                 |      | <-------------- |      |
+-----------+                 +------+   release_task  +------+
                                    ^                       |
                                    |                       | join_delib
                                    |    end_delib          v
                              +------+ <-------------- +----------+
                              |      |                 |DEBATING  |
                              |LEARN | <-------------- |          |
                              |      |   end_learn     +----------+
                              +------+                       |
                                    ^                        |
                                    |    respawn             | timeout
                                    |                        v
                              +------+                 +----------+
                              |      |                 |   DEAD   |
                              |ARCHIV| <-------------- |          |
                              |      |   archive       +----------+
                              +------+
```

### 7.3 Transitions valides

| Transition | From | To | Guard |
|------------|------|-----|-------|
| register | — | registered | — |
| activate | registered | idle | — |
| claim_task | idle | busy | capability match |
| release_task | busy | idle | task complete |
| join_delib | idle | debating | invitation acceptee |
| end_delib | debating | idle | deliberation terminee |
| learn | idle | learning | TAKA LAB active |
| end_learn | learning | idle | apprentissage termine |
| timeout | busy/debating/learning | dead | heartbeat manque x2 |
| respawn | dead | registered | agent critique uniquement |
| archive | dead | archived | apres grace period (5min) |

### 7.4 Modeles SQLAlchemy — app/models/ao.py (section Lifecycle)

```python
# app/models/ao.py — EXTRAITS Lifecycle Manager
# (a integrer dans le fichier unique app/models/ao.py)


class AgentLifecycleLog(Base):
    """
    Journal des transitions de cycle de vie des agents.
    
    Table: agent_lifecycle_logs
    Append-only — trace toutes les transitions d'etat.
    """
    __tablename__ = "agent_lifecycle_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    from_status: Mapped[str] = mapped_column(String(32), nullable=False)
    to_status: Mapped[str] = mapped_column(String(32), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )

    __table_args__ = (
        Index("ix_lifecycle_agent_time", "agent_id", "created_at"),
    )
```

### 7.5 Service Lifecycle Manager

```python
"""
app/kernel/lifecycle.py — Lifecycle Manager Service (v0.5+)

Gestionnaire de cycle de vie des agents avec FSM, heartbeat
monitoring, auto-respawn et garbage collection.

Usage:
    lifecycle = LifecycleManager(session, bus)
    
    # Enregistrement
    await lifecycle.register_agent(agent_id="qualifier", name="Qualifier Agent", ...)
    
    # Transition
    await lifecycle.transition("qualifier", "busy", reason="Claimed task ao.123")
    
    # Heartbeat processing
    await lifecycle.process_heartbeat("qualifier")
    
    # GC
    dead_count = await lifecycle.gc_dead_agents()
    expired = await lifecycle.gc_expired_sessions()
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from pydantic import BaseModel
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.kernel.bus import Event, EventBus
from app.models.ao import AgentModel, AgentStatus, AgentLifecycleLog


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


class LifecycleConfig(BaseModel):
    """Configuration du Lifecycle Manager."""
    heartbeat_interval: int = 30          # secondes entre heartbeats
    heartbeat_timeout: int = 60           # secondes avant status "dead"
    max_missed_heartbeats: int = 2        # nombre max de heartbeats manques
    grace_period_seconds: int = 300       # delai avant archivage d'un agent "dead"
    auto_respawn: bool = True             # activer l'auto-respawn
    critical_agents: List[str] = [        # IDs des agents critiques
        "qualifier", "scorer", "tracker",
    ]
    max_respawn_per_hour: int = 10
    respawn_backoff: List[int] = [5, 10, 30, 60, 300]  # secondes
    gc_interval_seconds: int = 300        # intervalle de garbage collection


# ---------------------------------------------------------------------------
# FSM Transitions
# ---------------------------------------------------------------------------


# Transitions valides: (from_status, to_status) -> guard description
VALID_TRANSITIONS: Dict[Tuple[str, str], Optional[str]] = {
    ("registered", "idle"): None,
    ("idle", "busy"): "capability_match",
    ("busy", "idle"): "task_complete",
    ("idle", "debating"): "invitation_accepted",
    ("debating", "idle"): "deliberation_complete",
    ("idle", "learning"): "lab_active",
    ("learning", "idle"): "learning_complete",
    ("busy", "dead"): "heartbeat_timeout",
    ("debating", "dead"): "heartbeat_timeout",
    ("learning", "dead"): "heartbeat_timeout",
    ("idle", "dead"): "heartbeat_timeout",
    ("dead", "registered"): "auto_respawn",
    ("dead", "archived"): "grace_period_expired",
}


# Etats terminaux (pas de transition sortante sauf respawn/archive)
TERMINAL_STATES: Set[str] = {"dead", "archived"}


class LifecycleManager:
    """
    Gestionnaire de cycle de vie des agents.

    Responsabilites:
        1. Enregistrement et desenregistrement des agents
        2. Transitions d'etat avec validation FSM
        3. Monitoring des heartbeats (timeout -> dead)
        4. Auto-respawn des agents critiques
        5. Garbage collection des agents morts et sessions expirees
    """

    def __init__(
        self,
        session: AsyncSession,
        bus: EventBus,
        config: Optional[LifecycleConfig] = None,
        tenant_id: str = "default",
    ) -> None:
        self._session: AsyncSession = session
        self._bus: EventBus = bus
        self._config: LifecycleConfig = config or LifecycleConfig()
        self._tenant_id: str = tenant_id
        self._respawn_counts: Dict[str, int] = {}  # agent_id -> count (reset hourly)
        self._respawn_reset_at: datetime = datetime.now(timezone.utc)

    # === Enregistrement ===

    async def register_agent(
        self,
        agent_id: str,
        name: str,
        capabilities: List[str],
        vertical_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> AgentModel:
        """
        Enregistre un nouvel agent dans le Swarm Registry.

        Args:
            agent_id: ID unique de l'agent
            name: Nom affiche
            capabilities: Liste des noms de capabilities
            vertical_id: Vertical metier (optionnel)
            metadata: Metadonnees supplementaires

        Returns:
            L'AgentModel cree
        """
        result = await self._session.execute(
            select(AgentModel).where(
                AgentModel.id == agent_id,
                AgentModel.tenant_id == self._tenant_id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            # Mise a jour de l'agent existant (re-enregistrement)
            existing.name = name
            existing.capabilities = capabilities
            existing.vertical_id = vertical_id
            existing.metadata = metadata or {}
            existing.status = AgentStatus.IDLE
            existing.heartbeat_at = datetime.now(timezone.utc)
            await self._session.commit()
            await self._log_transition(agent_id, "registered", "idle", "re_register")
            return existing

        agent = AgentModel(
            id=agent_id,
            name=name,
            vertical_id=vertical_id,
            capabilities=capabilities,
            status=AgentStatus.IDLE,
            heartbeat_at=datetime.now(timezone.utc),
            metadata=metadata or {},
        )
        self._session.add(agent)
        await self._session.commit()

        await self._log_transition(agent_id, "none", "registered", "register")
        await self._log_transition(agent_id, "registered", "idle", "activate")

        await self._bus.publish(Event(
            topic="agent.registered",
            payload={"agent_id": agent_id, "name": name, "capabilities": capabilities},
            tenant_id=self._tenant_id,
        ))

        return agent

    async def unregister_agent(self, agent_id: str) -> bool:
        """
        Desenregistre un agent (transition vers 'archived').

        Returns:
            True si l'agent existait et a ete archive.
        """
        agent = await self._get_agent(agent_id)
        if not agent:
            return False

        agent.status = AgentStatus.DEAD
        await self._session.commit()
        await self.transition(agent_id, "archived", reason="manual_unregister")

        await self._bus.publish(Event(
            topic="agent.unregistered",
            payload={"agent_id": agent_id},
            tenant_id=self._tenant_id,
        ))
        return True

    # === Transitions FSM ===

    async def transition(
        self,
        agent_id: str,
        to_status: str,
        reason: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> AgentModel:
        """
        Effectue une transition d'etat valide.

        Args:
            agent_id: ID de l'agent
            to_status: Nouvel etat cible
            reason: Raison de la transition
            metadata: Metadonnees supplementaires

        Raises:
            ValueError: Si la transition n'est pas valide.
        """
        agent = await self._get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} introuvable")

        from_status = agent.status.value if isinstance(agent.status, AgentStatus) else agent.status

        # Verifie la validite de la transition
        if (from_status, to_status) not in VALID_TRANSITIONS:
            raise ValueError(
                f"Transition invalide: {from_status} -> {to_status}. "
                f"Transitions valides depuis {from_status}: "
                f"{[t[1] for t in VALID_TRANSITIONS if t[0] == from_status]}"
            )

        # Guard: auto_respawn uniquement pour agents critiques
        guard = VALID_TRANSITIONS[(from_status, to_status)]
        if guard == "auto_respawn" and agent_id not in self._config.critical_agents:
            raise ValueError(f"Auto-respawn refuse: {agent_id} n'est pas un agent critique")

        # Execute la transition
        agent.status = AgentStatus(to_status) if to_status in [s.value for s in AgentStatus] else to_status
        agent.heartbeat_at = datetime.now(timezone.utc)
        await self._session.commit()

        # Log
        await self._log_transition(agent_id, from_status, to_status, reason, metadata)

        # Evenement
        await self._bus.publish(Event(
            topic="agent.status_changed",
            payload={
                "agent_id": agent_id,
                "from": from_status,
                "to": to_status,
                "reason": reason,
            },
            tenant_id=self._tenant_id,
        ))

        return agent

    # === Heartbeat Monitoring ===

    async def process_heartbeat(self, agent_id: str) -> AgentModel:
        """
        Traite un heartbeat d'un agent.

        Args:
            agent_id: ID de l'agent ayant envoye le heartbeat

        Returns:
            L'AgentModel mis a jour

        Raises:
            ValueError: Si l'agent n'est pas enregistre.
        """
        agent = await self._get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} non enregistre — heartbeat ignore")

        now = datetime.now(timezone.utc)
        agent.heartbeat_at = now

        # Si l'agent etait "dead", le ramene a "idle" (auto-recovery)
        if agent.status == AgentStatus.DEAD:
            agent.status = AgentStatus.IDLE
            await self._log_transition(agent_id, "dead", "idle", "heartbeat_recovery")

        await self._session.commit()
        return agent

    async def check_heartbeat_timeouts(self) -> List[str]:
        """
        Verifie les agents dont le heartbeat a expire.
        Marque comme "dead" ceux en timeout.

        Returns:
            Liste des IDs d'agents passes a "dead".
        """
        timeout_threshold = datetime.now(timezone.utc) - timedelta(
            seconds=self._config.heartbeat_timeout
        )

        result = await self._session.execute(
            select(AgentModel).where(
                AgentModel.tenant_id == self._tenant_id,
                AgentModel.status.in_(["idle", "busy", "debating", "learning"]),
                AgentModel.heartbeat_at < timeout_threshold,
            )
        )
        timed_out = list(result.scalars().all())

        dead_ids: List[str] = []
        for agent in timed_out:
            old_status = agent.status.value if isinstance(agent.status, AgentStatus) else str(agent.status)
            agent.status = AgentStatus.DEAD
            dead_ids.append(agent.id)
            await self._log_transition(
                agent.id, old_status, "dead",
                reason=f"heartbeat_timeout (> {self._config.heartbeat_timeout}s)",
            )

        if dead_ids:
            await self._session.commit()
            for agent_id in dead_ids:
                await self._bus.publish(Event(
                    topic="agent.dead",
                    payload={"agent_id": agent_id, "reason": "heartbeat_timeout"},
                    tenant_id=self._tenant_id,
                ))

        return dead_ids

    # === Auto-respawn ===

    async def respawn_dead_agents(self) -> List[str]:
        """
        Tente de faire respawn les agents critiques morts.

        Returns:
            Liste des IDs d'agents respawned.
        """
        if not self._config.auto_respawn:
            return []

        # Reset du compteur horaire
        now = datetime.now(timezone.utc)
        if (now - self._respawn_reset_at).total_seconds() >= 3600:
            self._respawn_counts.clear()
            self._respawn_reset_at = now

        result = await self._session.execute(
            select(AgentModel).where(
                AgentModel.tenant_id == self._tenant_id,
                AgentModel.status == AgentStatus.DEAD,
                AgentModel.id.in_(self._config.critical_agents),
            )
        )
        dead_critical = list(result.scalars().all())

        respawned: List[str] = []
        for agent in dead_critical:
            count = self._respawn_counts.get(agent.id, 0)
            if count >= self._config.max_respawn_per_hour:
                continue

            # Calcul du backoff
            backoff = self._config.respawn_backoff[
                min(count, len(self._config.respawn_backoff) - 1)
            ]
            # En vrai: declencher un nouveau conteneur/process
            # Ici: transition FSM
            agent.status = AgentStatus.IDLE
            agent.heartbeat_at = now
            self._respawn_counts[agent.id] = count + 1
            respawned.append(agent.id)

            await self._log_transition(agent.id, "dead", "idle", f"auto_respawn (backoff={backoff}s)")

            await self._bus.publish(Event(
                topic="agent.respawned",
                payload={"agent_id": agent.id, "backoff": backoff, "attempt": count + 1},
                tenant_id=self._tenant_id,
            ))

        if respawned:
            await self._session.commit()

        return respawned

    # === Garbage Collection ===

    async def gc_dead_agents(self) -> int:
        """
        Archive les agents morts depuis plus de la grace period.

        Returns:
            Nombre d'agents archives.
        """
        archive_threshold = datetime.now(timezone.utc) - timedelta(
            seconds=self._config.grace_period_seconds
        )

        result = await self._session.execute(
            select(AgentModel).where(
                AgentModel.tenant_id == self._tenant_id,
                AgentModel.status == AgentStatus.DEAD,
                AgentModel.heartbeat_at < archive_threshold,
            )
        )
        to_archive = list(result.scalars().all())

        for agent in to_archive:
            agent.status = "archived"  # HORS enum — etat terminal
            await self._log_transition(agent.id, "dead", "archived", "grace_period_expired")

        if to_archive:
            await self._session.commit()

        return len(to_archive)

    async def get_agent_stats(self) -> Dict[str, Any]:
        """Statistiques globales des agents."""
        result = await self._session.execute(
            select(AgentModel.status, func.count(AgentModel.id))
            .where(AgentModel.tenant_id == self._tenant_id)
            .group_by(AgentModel.status)
        )
        status_counts = {str(row[0]): row[1] for row in result.all()}

        return {
            "total": sum(status_counts.values()),
            "by_status": status_counts,
            "critical_agents": self._config.critical_agents,
            "respawn_counts_hour": self._respawn_counts,
            "heartbeat_timeout": self._config.heartbeat_timeout,
        }

    # === Helpers ===

    async def _get_agent(self, agent_id: str) -> Optional[AgentModel]:
        """Recupere un agent par ID."""
        result = await self._session.execute(
            select(AgentModel).where(
                AgentModel.id == agent_id,
                AgentModel.tenant_id == self._tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def _log_transition(
        self,
        agent_id: str,
        from_status: str,
        to_status: str,
        reason: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> AgentLifecycleLog:
        """Journalise une transition de cycle de vie."""
        log = AgentLifecycleLog(
            agent_id=agent_id,
            tenant_id=self._tenant_id,
            from_status=from_status,
            to_status=to_status,
            reason=reason,
            metadata=metadata or {},
        )
        self._session.add(log)
        await self._session.commit()
        return log
```

---

## SECTION 8 — Compatibilite Versions

### 8.1 Tableau de correspondance

| Version | EventBus | Swarm Registry | Memory Mesh | Governance Core | Lifecycle Manager | Etat |
|---------|----------|----------------|-------------|-----------------|-------------------|------|
| **v0.1** | asyncio in-memory (bus.py) | Non | PostgreSQL only (memory_tenant) | Non | Non | MVP |
| **v0.2** | asyncio in-memory | Non | PostgreSQL only | Non | Non | Connecteurs API |
| **v0.3** | asyncio in-memory | Non | PostgreSQL only | **Oui** (governance.py) | Non | Deliberation |
| **v0.4** | asyncio in-memory | Non | PostgreSQL only | Oui | Non | Parser PDF |
| **v0.5** | asyncio in-memory | **Oui** (agent.py + registry YAML) | PostgreSQL only | Oui | **Oui** (lifecycle.py) | Agents autonomes |
| **v1.0** | **NATS/RabbitMQ** (event_mesh_v1.yaml) | Oui | **3 zones** (memory.py) | Oui | Oui | Event mesh distribue |
| **v1.1** | NATS/RabbitMQ | Oui | **3 zones + Neo4j** | Oui | Oui | Graphe de relations |

### 8.2 Regles de migration

**v0.1 -> v0.3**: Ajout des tables `deliberation_sessions`, `deliberation_votes`, `deliberation_transcripts`. Aucun impact sur le EventBus.

**v0.3 -> v0.5**: Ajout des tables `agents`, `agent_capabilities`, `agent_lifecycle_logs`. Ajout de `app/kernel/agent.py` et `app/kernel/lifecycle.py`.

**v0.5 -> v1.0**: Remplacement de `EventBus` (asyncio) par `EventMesh` (NATS). Drop-in : interface identique. Ajout des tables `memory_global`, `memory_session`. Ajout de `app/kernel/memory.py`.

**v1.0 -> v1.1**: Ajout de Neo4j en option pour le graphe de relations entre AOs. Le Memory Mesh PostgreSQL reste la source de verite.

### 8.3 Points d'ancrage compatibles

Chaque version preserve les points d'ancrage suivants:

1. **Schema `audit_logs`**: Inchange depuis v0.1 (hash chain SHA-256)
2. **Interface `Agent.execute()`**: Inchangee depuis v0.5
3. **Interface `EventBus.publish/subscribe/unsubscribe`**: Inchangee depuis v0.1
4. **Table `memory_tenant`**: Inchangee depuis v0.1 (ajout de colonnes optionnelles uniquement)
5. **Fichier modeles unique `app/models/ao.py`**: Preserve dans toutes les versions

### 8.4 Ordre d'implementation recommande

Pour implementer le kernel de v0.1 a v1.0, suivre cet ordre:

1. **Jour 1**: `app/kernel/bus.py` (EventBus MVP) + `app/kernel/audit.py`
2. **Jour 2**: `app/kernel/security.py` + Integration FastAPI
3. **Jour 3**: `app/kernel/governance.py` + tables deliberation (v0.3)
4. **Jour 4**: `app/kernel/agent.py` + tables agents/capabilities (v0.5)
5. **Jour 5**: `app/kernel/lifecycle.py` + tables lifecycle (v0.5)
6. **Jour 6-7**: `app/kernel/memory.py` + tables 3 zones (v1.0)
7. **Jour 8+**: `EventMesh` NATS + `event_mesh_v1.yaml` (v1.0)

---

## ANNEXE A — Schema SQL complet (extrait app/models/ao.py)

```sql
-- ============================================================
-- Schema Kernel TAKA OS v1.0 (toutes versions aggregees)
-- A integrer dans les migrations Alembic
-- ============================================================

-- Types enum
CREATE TYPE agent_status AS ENUM ('idle', 'busy', 'debating', 'learning', 'dead');
CREATE TYPE vote_mode AS ENUM ('majority', 'borda', 'consensus', 'unanimous');
CREATE TYPE deliberation_status AS ENUM ('pending', 'active', 'voting', 'completed', 'cancelled');

-- Audit (v0.1+)
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64),
    action VARCHAR(128) NOT NULL,
    entity_type VARCHAR(64) NOT NULL,
    entity_id VARCHAR(128) NOT NULL,
    details JSONB,
    hash_prev VARCHAR(64),
    hash_current VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);
CREATE INDEX ix_audit_logs_tenant ON audit_logs(tenant_id);
CREATE INDEX ix_audit_logs_tenant_entity ON audit_logs(tenant_id, entity_type, entity_id);
CREATE UNIQUE INDEX ix_audit_logs_hash_current ON audit_logs(hash_current);

-- Agent Capabilities (v0.5+)
CREATE TABLE agent_capabilities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL UNIQUE,
    description TEXT,
    input_schema JSONB NOT NULL DEFAULT '{}',
    output_schema JSONB NOT NULL DEFAULT '{}',
    version VARCHAR(16) NOT NULL DEFAULT '1.0',
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- Agents / Swarm Registry (v0.5+)
CREATE TABLE agents (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    vertical_id VARCHAR(64),
    capabilities VARCHAR(128)[],
    status agent_status NOT NULL DEFAULT 'idle',
    heartbeat_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);
CREATE INDEX ix_agents_status ON agents(status);
CREATE INDEX ix_agents_vertical ON agents(vertical_id);
CREATE INDEX ix_agents_capabilities ON agents USING gin(capabilities);
CREATE INDEX ix_agents_status_vertical ON agents(status, vertical_id);

-- Lifecycle Logs (v0.5+)
CREATE TABLE agent_lifecycle_logs (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(64) NOT NULL,
    tenant_id VARCHAR(64) NOT NULL,
    from_status VARCHAR(32) NOT NULL,
    to_status VARCHAR(32) NOT NULL,
    reason TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);
CREATE INDEX ix_lifecycle_agent ON agent_lifecycle_logs(agent_id);
CREATE INDEX ix_lifecycle_agent_time ON agent_lifecycle_logs(agent_id, created_at);

-- Memory Global (v1.0+)
CREATE TABLE memory_global (
    key VARCHAR(256) PRIMARY KEY,
    value JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- Memory Tenant (v0.1+, enrichi v1.0+)
CREATE TABLE memory_tenant (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    key VARCHAR(256) NOT NULL,
    value JSONB NOT NULL DEFAULT '{}',
    embedding vector(1024),
    tags VARCHAR(128)[],
    importance FLOAT NOT NULL DEFAULT 0.5,
    ttl INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    UNIQUE(tenant_id, key)
);
CREATE INDEX ix_memory_tenant_tenant ON memory_tenant(tenant_id);
CREATE INDEX ix_memory_tenant_tenant_key ON memory_tenant(tenant_id, key);
CREATE INDEX ix_memory_tenant_embedding ON memory_tenant
    USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
CREATE INDEX ix_memory_tenant_tags ON memory_tenant USING gin(tags);
CREATE INDEX ix_memory_tenant_importance ON memory_tenant(tenant_id, importance);

-- Memory Session (v1.0+)
CREATE TABLE memory_session (
    session_id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64),
    context JSONB NOT NULL DEFAULT '{}',
    messages JSONB NOT NULL DEFAULT '[]',
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);
CREATE INDEX ix_memory_session_tenant ON memory_session(tenant_id);
CREATE INDEX ix_memory_session_expires ON memory_session(tenant_id, expires_at);
CREATE INDEX ix_memory_session_user ON memory_session(tenant_id, user_id, created_at);

-- Deliberation Sessions (v0.3+)
CREATE TABLE deliberation_sessions (
    id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    topic TEXT NOT NULL,
    description TEXT,
    mode vote_mode NOT NULL,
    status deliberation_status NOT NULL DEFAULT 'pending',
    agent_ids VARCHAR(64)[],
    quorum INT NOT NULL DEFAULT 1,
    result JSONB,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);
CREATE INDEX ix_deliberation_tenant ON deliberation_sessions(tenant_id);
CREATE INDEX ix_deliberation_status ON deliberation_sessions(status);

-- Deliberation Votes (v0.3+)
CREATE TABLE deliberation_votes (
    id VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL REFERENCES deliberation_sessions(id) ON DELETE CASCADE,
    agent_id VARCHAR(64) NOT NULL,
    vote_payload JSONB NOT NULL,
    weight FLOAT NOT NULL DEFAULT 1.0,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    UNIQUE(session_id, agent_id)
);
CREATE INDEX ix_votes_session ON deliberation_votes(session_id);
CREATE INDEX ix_votes_agent ON deliberation_votes(agent_id);

-- Deliberation Transcripts (v0.3+)
CREATE TABLE deliberation_transcripts (
    id VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL REFERENCES deliberation_sessions(id) ON DELETE CASCADE,
    sequence INT NOT NULL,
    entry_type VARCHAR(64) NOT NULL,
    agent_id VARCHAR(64),
    content JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);
CREATE INDEX ix_transcripts_session ON deliberation_transcripts(session_id);
CREATE INDEX ix_transcripts_session_seq ON deliberation_transcripts(session_id, sequence);
CREATE INDEX ix_transcripts_type ON deliberation_transcripts(entry_type);
```

---

## ANNEXE B — Glossaire

| Terme | Definition |
|-------|------------|
| **AO** | Appel d'Offres public |
| **Capability** | Contrat d'interface d'un agent (input/output schema) |
| **Dead Letter Queue (DLQ)** | Queue de stockage des messages non delivrables |
| **Event Mesh** | Infrastructure de messagerie distribuee (NATS/RabbitMQ) |
| **FSM** | Finite State Machine — machine a etats finis |
| **HNSW** | Hierarchical Navigable Small World — index vectoriel pgvector |
| **RLS** | Row Level Security — securite au niveau des lignes PostgreSQL |
| **Swarm Registry** | Registre des agents et de leurs capabilities |
| **Tenant** | Client isole (multi-tenancy) |
| **Transcript** | Journal immuable d'une deliberation |
| **TTL** | Time To Live — duree de vie d'une donnee ephemere |
| **Wildcard** | Caractere joker pour le pattern matching de topics |

---

> **Fin du Manifeste Kernel TAKA OS v1.0**
>
> Ce document est un **SPEC EXECUTABLE**. Kimi Code peut implementer
> directement a partir de ce manifeste. Chaque section contient:
> - Les imports exacts
> - Les signatures de methodes typees
> - Les docstrings
> - Les schemas SQL
> - Les fichiers YAML de configuration
>
> Pour toute question d'implementation, se referer aux
> **schemas SQL de l'Annexe A** comme source de verite.
