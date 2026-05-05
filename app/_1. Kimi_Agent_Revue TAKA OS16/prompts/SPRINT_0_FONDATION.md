# SPRINT 0 - MISE A JOUR - PROMPT KIMI CODE

## AVERTISSEMENT

Ce document est le prompt principal du projet. Kimi Code l'execute en premiere position, sans poser de question. Toutes les specifications ci-dessous sont absolues, non-negociables et auto-suffisantes. L'agent doit produire le code source complet, fichier par fichier, sans demander de clarification.

---

# 1. CONTEXTE PROJET

Projet TAKA - Plateforme d'appels d'offres automatises par IA.
Backend FastAPI, PostgreSQL+pgvector, authentification JWT avec 5 roles organisationnels, feature flags, memoire persistante a 3 niveaux, tracabilite forensique complete avec hash chain.
Ce Sprint 0 pose les fondations techniques de production.

---

# 2. STACK TECHNIQUE

| Couche              | Technologie                              |
|---------------------|------------------------------------------|
| Framework API       | FastAPI 0.115+                           |
| ORM                 | SQLAlchemy 2.0 (async)                   |
| Base de donnees     | PostgreSQL 16 + pgvector                 |
| Auth                | JWT (python-jose) + bcrypt + pyotp MFA   |
| Rate Limiting       | SlowAPI 0.1.10+                          |
| Monitoring          | Sentry SDK (sentry-sdk[fastapi])         |
| Circuit Breaker     | PyCircuitBreaker (0.8+)                  |
| Tests               | pytest, pytest-asyncio, httpx            |
| Conteneurisation    | Docker + Docker Compose                  |
| CI/CD               | GitHub Actions                           |
| Frontend            | React 18 + TypeScript + Vite             |
| QR Code MFA         | qrcode (Python)                          |

### NOUVEAUX PACKAGES pyproject.toml (section [tool.poetry.dependencies] ou requirements)

```
sentry-sdk[fastapi]>=2.0.0
slowapi>=0.1.10
pyotp>=2.9.0
qrcode[pil]>=7.4.2
pybreaker>=0.8.0
```

Les packages existants restent inchanges : fastapi, uvicorn, sqlalchemy[asyncio], asyncpg, pgvector, alembic, python-jose[cryptography], passlib[bcrypt], python-multipart, pydantic-settings, pytest, pytest-asyncio, httpx, email-validator.

---

# 3. REGLES ABSOLUES

R1. **Aucune question a l'utilisateur.** Si une specification est incomplete, l'agent fait un choix technique raisonnable et le documente dans un commentaire TODO.

R2. **Tout le code est anglais.** Noms de variables, fonctions, classes, fichiers en anglais. Seuls les commentaires explicatifs peuvent etre en francais.

R3. **Type hints obligatoires partout.** Fonctions, methodes, variables. Pas de `Any` sauf justification en commentaire. SQLAlchemy 2.0 style obligatoire.

R4. **Pydantic v2 partout.** Tous les schemas utilisent BaseModel v2. Pas de .dict(), seulement .model_dump().

R5. **Async/await obligatoire.** Toutes les routes sont async. Tous les appels DB passent par AsyncSession.

R6. **Zero secrets en clair.** Aucune cle d'API, mot de passe, DSN dans le code source. Tout passe par variables d'environnement via Pydantic Settings.

R7. **Toutes les reponses API suivent le meme schema JSON** :
```json
{
  "status": "success" | "error",
  "data": <payload> | null,
  "message": "string explicatif" | null,
  "meta": { "page": 1, "per_page": 20, "total": 100 } | null
}
```

R8. **Chaque fichier cree doit avoir son header.** Format :
```python
# File: <path>
# Purpose: <description en une phrase>
# Dependencies: <liste des imports internes cles>
```

R9. **Les routes d'erreur sont centralisees.** Un seul exception handler global dans main.py. Aucun try/except silencieux.

R10. **Circuit breaker sur tous les appels externes.** Sentry, LLM APIs, services tiers passent obligatoirement par le circuit breaker.

R11. **Rate limiting par defaut sur toutes les routes protegees.** 100 requetes/minute par user_id. Routes auth : 10 requetes/minute par IP.

R12. **Timeout 30s sur tous les endpoints.** Middleware global. Les endpoints de generation LLM peuvent lever a 120s via override explicite.

R13. **Feature flags evalues a chaque requete.** Le service verifie l'etat actuel du flag, pas de cache client hors TTL memoire.

R14. **Audit log inseres en transaction.** Jamais d'audit log sans la transaction parente. Hash chain recalcule a chaque insertion.

R15. **Les 5 roles sont hierarchiques.** super_admin > tenant_admin > tenant_manager > tenant_collaborator > viewer. Chaque role herite des permissions du role inferieur.

R16. **Pas de suppression physique des donnees.** Tous les modeles ont deleted_at (soft delete). L'audit preserve l'integrite meme apres soft delete.

---

# 4. MISSION

Produire un backend FastAPI complet de production avec les caracteristiques suivantes :

1. **Authentification JWT** avec refresh tokens, 5 roles organisationnels, invitations par token, MFA TOTP optionnel
2. **Multi-tenant** avec TenantType (soumissionnaire/acheteur), isolation des donnees par tenant_id
3. **8 tables principales** etendues avec feature flags, memoire 3 zones, audit hash chain, logs d'appels LLM
4. **Sentry** integre avec contexte enrichi (user_id, tenant_id, role)
5. **Rate limiting** par endpoint avec SlowAPI et Redis (fallback en memoire)
6. **Circuit breaker** sur les appels externes
7. **Timeout middleware** 30s par defaut
8. **Backup/restore** PostgreSQL via scripts shell
9. **Frontend React** avec ErrorBoundary Sentry et structure Vite+TS
10. **Tests pytest** couverture > 80% sur auth, models, services
11. **Docker Compose** complet avec PostgreSQL 16+pgvector, backend, frontend, redis
12. **CI GitHub Actions** avec lint, tests, build, security scan (bandit)

Livrable final : repository structure complet, tous les fichiers listes ci-dessous, docker-compose up --build fonctionnel en une commande.

---

# 5. FICHIER PAR FICHIER

## GROUPE A : CONFIG & STRUCTURE (7 fichiers)

---

### A1. pyproject.toml

**Description** : Configuration du projet Python avec Poetry. Inclut tous les packages existants ET les nouveaux packages de production.

**Dependances** : Aucune (fichier racine).

**Contenu attendu** :

```toml
[tool.poetry]
name = "taka-api"
version = "0.2.0"
description = "TAKA - Plateforme d'appels d'offres automatises"
authors = ["TAKA Team"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.115.0"
uvicorn = { extras = ["standard"], version = "^0.32.0" }
sqlalchemy = { extras = ["asyncio"], version = "^2.0.36" }
asyncpg = "^0.30.0"
pgvector = "^0.3.0"
alembic = "^1.14.0"
python-jose = { extras = ["cryptography"], version = "^3.3.0" }
passlib = { extras = ["bcrypt"], version = "^1.7.4" }
python-multipart = "^0.0.17"
pydantic = "^2.9.0"
pydantic-settings = "^2.6.0"
email-validator = "^2.2.0"
httpx = "^0.27.0"
python-dotenv = "^1.0.0"

# NOUVEAUX PACKAGES DE PRODUCTION
sentry-sdk = { extras = ["fastapi"], version = "^2.0.0" }
slowapi = "^0.1.10"
pyotp = "^2.9.0"
qrcode = { extras = ["pil"], version = "^7.4.2" }
pybreaker = "^0.8.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.3.0"
pytest-asyncio = "^0.24.0"
pytest-cov = "^6.0.0"
black = "^24.10.0"
isort = "^5.13.0"
flake8 = "^7.1.0"
bandit = "^1.7.10"
mypy = "^1.13.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 88
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "--cov=app --cov-report=term-missing --cov-fail-under=80"
```

---

### A2. .env.template

**Description** : Template de toutes les variables d'environnement. Aucune valeur sensible par defaut.

**Dependances** : Aucune.

**Contenu attendu** :

```bash
# === APP CONFIG ===
APP_NAME=TAKA API
APP_VERSION=0.2.0
ENVIRONMENT=development
DEBUG=false

# === DATABASE ===
DATABASE_URL=postgresql+asyncpg://taka:taka_password@db:5432/taka_db
DATABASE_URL_SYNC=postgresql://taka:taka_password@db:5432/taka_db
POSTGRES_USER=taka
POSTGRES_PASSWORD=taka_password
POSTGRES_DB=taka_db

# === AUTH ===
SECRET_KEY=change-me-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# === SENTRY ===
SENTRY_DSN=
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=0.1

# === RATE LIMITING / REDIS ===
REDIS_URL=redis://redis:6379/0
RATE_LIMIT_DEFAULT=100/minute
RATE_LIMIT_AUTH=10/minute
RATE_LIMIT_HEALTH=60/minute

# === MFA ===
MFA_ENABLED=true
MFA_ISSUER_NAME=TAKA Platform

# === BACKUP S3 ===
S3_BACKUP_BUCKET=taka-db-backups
S3_BACKUP_ENDPOINT=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
BACKUP_RETENTION_DAYS=30

# === CORS ===
FRONTEND_URL=http://localhost:5173
```

---

### A3. app/config.py

**Description** : Configuration Pydantic Settings centralisee. Enrichie avec APP_VERSION, ENVIRONMENT, SENTRY_DSN, sections S3 backup et MFA.

**Dependances** : pydantic-settings.

**Contenu attendu** (specification detaillee) :

- Classe `Settings` heritant de `BaseSettings`
- Champs existants : `app_name`, `debug`, `database_url`, `secret_key`, `algorithm`, `access_token_expire_minutes`, `refresh_token_expire_days`, `frontend_url`
- NOUVEAUX champs obligatoires :
  - `app_version: str = "0.2.0"`
  - `environment: str = "development"` (dev/staging/production)
  - `sentry_dsn: str | None = None`
  - `sentry_environment: str = "development"`
  - `sentry_traces_sample_rate: float = 0.1`
  - `redis_url: str = "redis://localhost:6379/0"`
  - `rate_limit_default: str = "100/minute"`
  - `rate_limit_auth: str = "10/minute"`
  - `rate_limit_health: str = "60/minute"`
  - `mfa_enabled: bool = True`
  - `mfa_issuer_name: str = "TAKA Platform"`
  - `s3_backup_bucket: str | None = None`
  - `s3_backup_endpoint: str | None = None`
  - `aws_access_key_id: str | None = None`
  - `aws_secret_access_key: str | None = None`
  - `backup_retention_days: int = 30`
- `model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")`
- Instance singleton `settings = Settings()`
- Propriete `is_production` : return `self.environment == "production"`
- Propriete `sentry_enabled` : return `bool(self.sentry_dsn)`
- Propriete `s3_backup_enabled` : return `bool(self.s3_backup_bucket and self.aws_access_key_id)`

---

### A4. app/core/sentry.py

**Description** : Initialisation et utilitaires Sentry. Initialise le SDK Sentry avec contexte FastAPI, enrichit le scope avec user_id, tenant_id, role.

**Dependances** : `app.config.settings`

**Contenu attendu** :

```python
# File: app/core/sentry.py
# Purpose: Sentry SDK initialization and utility helpers
# Dependencies: app.config.settings

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from app.config import settings


def init_sentry() -> None:
    """Initialize Sentry SDK if DSN is configured."""
    if not settings.sentry_enabled:
        return
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment,
        release=settings.app_version,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        profiles_sample_rate=0.1 if settings.is_production else 0.0,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
        ],
        attach_stacktrace=True,
        include_source_context=True,
        before_send=strip_sensitive_data,
    )


def strip_sensitive_data(event: dict, hint: dict) -> dict | None:
    """Remove sensitive fields from Sentry events before sending."""
    if "request" in event and "data" in event["request"]:
        for key in ["password", "token", "secret", "credit_card", "mfa_code"]:
            if key in event["request"]["data"]:
                event["request"]["data"][key] = "[FILTERED]"
    return event


def set_sentry_user(user_id: str, tenant_id: str | None, role: str) -> None:
    """Enrich Sentry scope with user context."""
    if not settings.sentry_enabled:
        return
    sentry_sdk.set_user({
        "id": user_id,
        "tenant_id": tenant_id,
        "role": role,
    })


def clear_sentry_user() -> None:
    """Clear user context from Sentry scope (logout)."""
    if not settings.sentry_enabled:
        return
    sentry_sdk.set_user(None)
```

---

### A5. app/core/rate_limit.py

**Description** : Configuration SlowAPI avec Redis (fallback memoire). Limites par categorie d'endpoint, exemptees pour health checks internes.

**Dependances** : `app.config.settings`, slowapi, redis (ou FakeRedis).

**Contenu attendu** :

```python
# File: app/core/rate_limit.py
# Purpose: Rate limiting configuration using SlowAPI with Redis fallback
# Dependencies: app.config.settings, slowapi, redis (fakeredis fallback)

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, status
from fastapi.responses import JSONResponse
import redis.asyncio as redis
import fakeredis.aioredis
from app.config import settings


def _get_limiter_backend() -> redis.Redis:
    """Return Redis client or FakeRedis if Redis is unavailable."""
    try:
        return redis.from_url(settings.redis_url, decode_responses=True)
    except Exception:
        return fakeredis.aioredis.FakeRedis()


limiter = Limiter(
    key_func=lambda req: _derive_key(req),
    storage_uri=settings.redis_url,
    strategy="fixed-window",
)


def _derive_key(request: Request) -> str:
    """Derive rate limit key from user_id if authenticated, else IP."""
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return f"user:{user_id}"
    return f"ip:{get_remote_address(request)}"


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Global handler for rate limit exceeded."""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "status": "error",
            "data": None,
            "message": f"Rate limit exceeded: {exc.detail}",
            "meta": None,
        },
    )


def get_default_limit() -> str:
    return settings.rate_limit_default


def get_auth_limit() -> str:
    return settings.rate_limit_auth


def get_health_limit() -> str:
    return settings.rate_limit_health
```

---

### A6. app/core/circuit_breaker.py

**Description** : Circuit breaker global avec PyCircuitBreaker. Un breaker par service externe (sentry, llm_api, email).

**Dependances** : `pybreaker`, `app.config.settings`.

**Contenu attendu** :

```python
# File: app/core/circuit_breaker.py
# Purpose: Circuit breaker definitions for external service calls
# Dependencies: pybreaker

import logging
from pybreaker import CircuitBreaker
from functools import wraps
from typing import Callable, TypeVar, Any

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])

# Default breaker config: 5 failures, 60s recovery timeout, 10s expected call duration
_BREAKER_CONFIG = {
    "fail_max": 5,
    "timeout_duration": 60,
    "expected_exception": Exception,
}

sentry_breaker = CircuitBreaker(name="sentry", **_BREAKER_CONFIG)
llm_api_breaker = CircuitBreaker(name="llm_api", fail_max=3, timeout_duration=120)
email_breaker = CircuitBreaker(name="email", fail_max=5, timeout_duration=60)
storage_breaker = CircuitBreaker(name="storage", fail_max=5, timeout_duration=60)


def circuit_breaker_call(breaker: CircuitBreaker, func: F) -> F:
    """Decorator to wrap a function with a circuit breaker."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return breaker(func)(*args, **kwargs)
    return wrapper  # type: ignore[return-value]


def get_breaker_status() -> dict[str, str]:
    """Return current status of all circuit breakers."""
    breakers = {
        "sentry": sentry_breaker,
        "llm_api": llm_api_breaker,
        "email": email_breaker,
        "storage": storage_breaker,
    }
    return {name: str(brk.current_state) for name, brk in breakers.items()}
```

---

### A7. app/core/audit.py

**Description** : Utilitaires pour l'audit forensique. Hash chain SHA-256, calcul du hash du record precedent.

**Dependances** : `hashlib`, `sqlalchemy`.

**Contenu attendu** :

```python
# File: app/core/audit.py
# Purpose: Forensic audit utilities with SHA-256 hash chain
# Dependencies: hashlib, datetime

import hashlib
from datetime import datetime, timezone
from typing import Any


def compute_audit_hash(
    previous_hash: str | None,
    record_data: dict[str, Any],
    timestamp: datetime,
) -> str:
    """
    Compute SHA-256 hash for an audit record.
    The hash covers: previous_hash + canonical record_data + ISO timestamp.
    This creates an immutable chain.
    """
    canonical_data = "|".join(
        f"{k}={str(v)}" for k, v in sorted(record_data.items()) if v is not None
    )
    payload = f"{previous_hash or 'genesis'}|{canonical_data}|{timestamp.isoformat()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def verify_hash_chain(records: list[dict[str, Any]]) -> bool:
    """
    Verify integrity of a sequence of audit records.
    Each record must have 'hash' and 'previous_hash' keys.
    """
    for i, rec in enumerate(records):
        expected_prev = records[i - 1]["hash"] if i > 0 else None
        if rec.get("previous_hash") != expected_prev:
            return False
        rec_hash = compute_audit_hash(
            rec["previous_hash"],
            {k: v for k, v in rec.items() if k not in ("hash", "previous_hash", "created_at")},
            rec["created_at"],
        )
        if rec_hash != rec["hash"]:
            return False
    return True


def now_utc() -> datetime:
    return datetime.now(timezone.utc)
```

---

## GROUPE B : BASE DE DONNEES (2 fichiers)

---

### B1. app/database.py

**Description** : Moteur SQLAlchemy async, session maker, gestionnaire de contexte pour les sessions DB, gestion du vecteur pgvector.

**Dependances** : `app.config.settings`, `sqlalchemy.ext.asyncio`, `pgvector.sqlalchemy`.

**Contenu attendu** (specification detaillee) :

- `async_engine` : `create_async_engine(settings.database_url, echo=settings.debug, future=True)`
- `AsyncSessionLocal` : `async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)`
- `async def get_db() -> AsyncGenerator[AsyncSession, None]` : context manager qui yield une session et fait rollback sur exception
- `async def init_db() -> None` : cree les tables via `Base.metadata.create_all(bind=async_engine)` et execute `CREATE EXTENSION IF NOT EXISTS vector`
- `Base = declarative_base()` avec metadata contenant `pgvector.register_vector()`

---

### B2. app/models/ao.py

**Description** : Modeles SQLAlchemy complets. Ce fichier est le coeur du modele de donnees. Il contient : 5 roles, TenantType, UserInvitation, FeatureFlag, MemoryGlobal, MemoryTenant, MemorySession, AuditLog, LLMCallLog, EventLog, StateSnapshot, et les modeles existants (User, Tenant, AO, Document, Conversation, Message).

**Dependances** : `app.database.Base`, `pgvector.sqlalchemy.Vector`, `sqlalchemy.orm`, `app.core.audit.compute_audit_hash`.

**Contenu attendu** :

#### Enums (SQLAlchemy native Enum)

```python
class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    TENANT_ADMIN = "tenant_admin"
    TENANT_MANAGER = "tenant_manager"
    TENANT_COLLABORATOR = "tenant_collaborator"
    VIEWER = "viewer"

class TenantType(str, enum.Enum):
    SOUMISSIONNAIRE = "soumissionnaire"
    ACHETEUR = "acheteur"

class InvitationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"

class FeatureFlagScope(str, enum.Enum):
    GLOBAL = "global"
    TENANT = "tenant"
    USER = "user"

class AuditAction(str, enum.Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    INVITATION_SENT = "invitation_sent"
    INVITATION_ACCEPTED = "invitation_accepted"
```

#### Modele Tenant (etendu)

```python
class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[TenantType] = mapped_column(Enum(TenantType), nullable=False, default=TenantType.SOUMISSIONNAIRE)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    settings: Mapped[dict | None] = mapped_column(JSON, default=dict)
    billing_plan: Mapped[str | None] = mapped_column(String(50), default="free")
    max_users: Mapped[int | None] = mapped_column(Integer, default=5)
    max_storage_mb: Mapped[int | None] = mapped_column(Integer, default=100)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    users: Mapped[list["User"]] = relationship("User", back_populates="tenant", lazy="selectin")
    feature_flags: Mapped[list["FeatureFlag"]] = relationship("FeatureFlag", back_populates="tenant", lazy="selectin")
    memory_entries: Mapped[list["MemoryTenant"]] = relationship("MemoryTenant", back_populates="tenant", lazy="selectin")
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="tenant", lazy="selectin")
```

#### Modele User (etendu avec role et MFA)

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.VIEWER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    mfa_secret: Mapped[str | None] = mapped_column(Text, nullable=True)  # Encrypted TOTP secret
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="users")
    conversations: Mapped[list["Conversation"]] = relationship("Conversation", back_populates="user")
    invitations_sent: Mapped[list["UserInvitation"]] = relationship("UserInvitation", foreign_keys="UserInvitation.invited_by_id", back_populates="inviter")
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="user")
    memory_entries: Mapped[list["MemorySession"]] = relationship("MemorySession", back_populates="user")
```

#### Modele UserInvitation (nouveau)

```python
class UserInvitation(Base):
    __tablename__ = "user_invitations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)  # Secure random token
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.VIEWER)
    status: Mapped[InvitationStatus] = mapped_column(Enum(InvitationStatus), default=InvitationStatus.PENDING)
    invited_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tenant: Mapped["Tenant"] = relationship("Tenant")
    inviter: Mapped["User"] = relationship("User", foreign_keys=[invited_by_id], back_populates="invitations_sent")
```

#### Modele FeatureFlag (nouveau)

```python
class FeatureFlag(Base):
    __tablename__ = "feature_flags"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    scope: Mapped[FeatureFlagScope] = mapped_column(Enum(FeatureFlagScope), nullable=False, default=FeatureFlagScope.GLOBAL)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    kill_switch: Mapped[bool] = mapped_column(Boolean, default=False)  # Emergency off
    gated_by_plan: Mapped[str | None] = mapped_column(String(50))  # e.g. "pro", "enterprise"
    rollout_percentage: Mapped[int] = mapped_column(Integer, default=100)  # 0-100
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    tenant: Mapped["Tenant | None"] = relationship("Tenant", back_populates="feature_flags")
    user: Mapped["User | None"] = relationship("User")
```

#### Modele MemoryGlobal (nouveau)

```python
class MemoryGlobal(Base):
    __tablename__ = "memory_global"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    value: Mapped[dict] = mapped_column(JSON, nullable=False)
    data_type: Mapped[str | None] = mapped_column(String(50))  # "preference", "learning", "pattern"
    source: Mapped[str | None] = mapped_column(String(100))  # "user_feedback", "llm_extraction", "system"
    ttl_seconds: Mapped[int | None] = mapped_column(Integer)  # TTL, null = permanent
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    importance_score: Mapped[float] = mapped_column(Float, default=1.0)  # 0.0 - 10.0 for selective forgetting
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

#### Modele MemoryTenant (nouveau)

```python
class MemoryTenant(Base):
    __tablename__ = "memory_tenant"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    value: Mapped[dict] = mapped_column(JSON, nullable=False)
    data_type: Mapped[str | None] = mapped_column(String(50))
    source: Mapped[str | None] = mapped_column(String(100))
    ttl_seconds: Mapped[int | None] = mapped_column(Integer)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    importance_score: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="memory_entries")
```

#### Modele MemorySession (nouveau)

```python
class MemorySession(Base):
    __tablename__ = "memory_session"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)  # Client session identifier
    key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    value: Mapped[dict] = mapped_column(JSON, nullable=False)
    data_type: Mapped[str | None] = mapped_column(String(50))
    ttl_seconds: Mapped[int | None] = mapped_column(Integer, default=3600)  # Default 1h TTL
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="memory_entries")
```

#### Modele AuditLog (nouveau - tracabilite forensique)

```python
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)  # "user", "ao", "tenant", etc.
    entity_id: Mapped[str | None] = mapped_column(String(255))  # UUID as string for flexibility
    payload_before: Mapped[dict | None] = mapped_column(JSON)
    payload_after: Mapped[dict | None] = mapped_column(JSON)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(Text)
    previous_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # SHA-256 of previous record
    hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256 of this record
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tenant: Mapped["Tenant | None"] = relationship("Tenant", back_populates="audit_logs")
    user: Mapped["User | None"] = relationship("User", back_populates="audit_logs")
```

#### Modele LLMCallLog (nouveau)

```python
class LLMCallLog(Base):
    __tablename__ = "llm_call_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # "openai", "anthropic", etc.
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer)
    completion_tokens: Mapped[int | None] = mapped_column(Integer)
    total_tokens: Mapped[int | None] = mapped_column(Integer)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    prompt_preview: Mapped[str | None] = mapped_column(Text)  # First 500 chars
    response_preview: Mapped[str | None] = mapped_column(Text)  # First 500 chars
    status: Mapped[str] = mapped_column(String(20), default="success")  # success, error, timeout
    error_message: Mapped[str | None] = mapped_column(Text)
    metadata: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

#### Modele EventLog (nouveau)

```python
class EventLog(Base):
    __tablename__ = "event_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), default="info")  # debug, info, warning, error, critical
    payload: Mapped[dict | None] = mapped_column(JSON)
    source: Mapped[str | None] = mapped_column(String(100))  # service/component name
    trace_id: Mapped[str | None] = mapped_column(String(255), index=True)  # Distributed trace correlation
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

#### Modele StateSnapshot (nouveau)

```python
class StateSnapshot(Base):
    __tablename__ = "state_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(255), nullable=False)
    state_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    snapshot_reason: Mapped[str | None] = mapped_column(String(100))  # "manual", "scheduled", "pre_migration"
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

#### Modeles existants (a conserver)

Les modeles AO, Document, Conversation, Message restent avec leur structure existante mais avec les ameliorations suivantes :
- `AO` : ajouter `tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"))`, relation vers Tenant
- `Document` : ajouter `tenant_id`, `vector_embedding` (pgvector Vector(1536))
- `Conversation` : ajouter `tenant_id`, relation existante vers User conservee
- `Message` : ajouter `tenant_id`, `vector_embedding` optionnel

---

## GROUPE C : SECURITE & AUTH (4 fichiers)

---

### C1. app/core/security.py (etendu avec MFA/TOTP)

**Description** : Hashage de mots de passe, creation/verification JWT, generation/verification TOTP MFA, cryptage du secret MFA.

**Dependances** : `app.config.settings`, `passlib`, `python-jose`, `pyotp`.

**Contenu attendu** :

```python
# File: app/core/security.py
# Purpose: Password hashing, JWT tokens, and MFA/TOTP handling
# Dependencies: app.config.settings, passlib, python-jose, pyotp

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext
import pyotp
import base64

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = settings.algorithm


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str | Any, expires_delta: timedelta | None = None, extra_claims: dict | None = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    if extra_claims:
        to_encode.update(extra_claims)
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: str | Any) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# === MFA / TOTP ===

def generate_mfa_secret() -> str:
    """Generate a new TOTP secret (base32)."""
    return pyotp.random_base32()


def get_totp_uri(secret: str, user_email: str) -> str:
    """Generate the otpauth:// URI for QR code generation."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=user_email, issuer_name=settings.mfa_issuer_name)


def verify_totp(secret: str, token: str) -> bool:
    """Verify a TOTP code against a secret. Window=1 (30s before/after)."""
    if not secret or not token:
        return False
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)


def encrypt_mfa_secret(secret: str, encryption_key: str | None = None) -> str:
    """
    Encrypt the MFA secret before storage.
    Fallback: XOR with a derived key from SECRET_KEY if no encryption_key provided.
    TODO: Replace with proper Fernet encryption in production.
    """
    key = (encryption_key or settings.secret_key)[:32].encode("utf-8")
    secret_bytes = secret.encode("utf-8")
    encrypted = bytes(s ^ key[i % len(key)] for i, s in enumerate(secret_bytes))
    return base64.b64encode(encrypted).decode("ascii")


def decrypt_mfa_secret(encrypted_secret: str, encryption_key: str | None = None) -> str:
    """Decrypt the MFA secret."""
    key = (encryption_key or settings.secret_key)[:32].encode("utf-8")
    encrypted_bytes = base64.b64decode(encrypted_secret.encode("ascii"))
    decrypted = bytes(e ^ key[i % len(key)] for i, e in enumerate(encrypted_bytes))
    return decrypted.decode("utf-8")
```

---

### C2. app/dependencies.py

**Description** : Dependances FastAPI reutilisables : DB session, current user avec role check, tenant injection, feature flag check.

**Dependances** : `app.database.get_db`, `app.models.ao.User`, `app.core.security.decode_token`.

**Contenu attendu** :

```python
# File: app/dependencies.py
# Purpose: Reusable FastAPI dependencies for auth, DB, roles, and tenant
# Dependencies: app.database, app.models.ao, app.core.security, app.services.feature_flags

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from app.database import get_db
from app.models.ao import User, UserRole, Tenant
from app.core.security import decode_token
from app.core.sentry import set_sentry_user

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not credentials:
        raise credentials_exception
    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("sub") is None or payload.get("type") != "access":
        raise credentials_exception
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id, User.is_active == True, User.deleted_at.is_(None)))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    # Set Sentry context
    set_sentry_user(str(user.id), str(user.tenant_id) if user.tenant_id else None, user.role.value)
    return user


class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user


require_admin = RoleChecker([UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN])
require_manager = RoleChecker([UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN, UserRole.TENANT_MANAGER])
require_collaborator = RoleChecker([UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN, UserRole.TENANT_MANAGER, UserRole.TENANT_COLLABORATOR])
require_any_authenticated = RoleChecker(list(UserRole))


async def get_current_tenant(user: User = Depends(get_current_user)) -> Tenant:
    if user.tenant is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User has no tenant")
    return user.tenant


async def set_request_state_user(request: Request, user: User = Depends(get_current_user)) -> User:
    """Store user_id in request.state for rate limiting key derivation."""
    request.state.user_id = str(user.id)
    return user
```

---

### C3. app/api/v1/auth.py (etendu avec invitations)

**Description** : Routes d'authentification : register, login avec MFA challenge, refresh token, logout, invitation par token.

**Dependances** : `app.dependencies.get_current_user`, `app.core.security`, `app.models.ao`, `app.database`.

**Contenu attendu** (specification detaillee) :

- `POST /auth/register` : Inscription publique. Cree un user avec role VIEWER et un tenant par defaut de type SOUMISSIONNAIRE. Validation email unique. Hashage mot de passe.
- `POST /auth/login` : Login. Si MFA active pour cet utilisateur, retourne `mfa_required: true` + token temporaire `mfa_token` (expire 5min). Si MFA non active, retourne access_token + refresh_token directement.
- `POST /auth/mfa/verify` : Verifie le code TOTP. Echange le `mfa_token` contre access_token + refresh_token. Route dans ce fichier, delegue a `app.core.security.verify_totp`.
- `POST /auth/refresh` : Echange refresh_token valide contre nouveau access_token.
- `POST /auth/logout` : Revocation cote client (stateless JWT). Clear Sentry user context.
- `POST /auth/invitation/accept` : Accepte une invitation via token. Cree le compte user avec le role de l'invitation. Met a jour l'invitation status ACCEPTED.
- `GET /auth/me` : Retourne les infos de l'utilisateur connecte avec son tenant.

Toutes les reponses suivent le schema standardise {status, data, message, meta}.

---

### C4. app/api/v1/auth_mfa.py

**Description** : Routes MFA dediees : activer MFA (generate QR), desactiver MFA, verifier un code de test.

**Dependances** : `app.dependencies.get_current_user`, `app.core.security`, `qrcode`.

**Contenu attendu** :

```python
# File: app/api/v1/auth_mfa.py
# Purpose: MFA setup and management endpoints
# Dependencies: app.dependencies, app.core.security, app.models.ao, qrcode, io, base64

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from io import BytesIO
import base64
import qrcode

from app.dependencies import get_current_user, get_db
from app.core.security import generate_mfa_secret, get_totp_uri, verify_totp, encrypt_mfa_secret, decrypt_mfa_secret
from app.models.ao import User
from app.core.audit import now_utc

router = APIRouter(prefix="/mfa", tags=["MFA"])


@router.post("/enable")
async def enable_mfa(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate MFA secret and return QR code as base64 PNG."""
    if user.mfa_enabled:
        raise HTTPException(status_code=400, detail="MFA already enabled")
    secret = generate_mfa_secret()
    uri = get_totp_uri(secret, user.email)
    # Generate QR code
    qr = qrcode.make(uri)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_b64 = base64.b64encode(buffer.getvalue()).decode("ascii")
    # Store encrypted secret (not yet enabled until verified)
    user.mfa_secret = encrypt_mfa_secret(secret)
    await db.commit()
    return {
        "status": "success",
        "data": {"qr_code_base64": f"data:image/png;base64,{qr_b64}", "secret": secret},
        "message": "Scan the QR code with your authenticator app, then verify to enable",
        "meta": None,
    }


@router.post("/verify-and-enable")
async def verify_and_enable_mfa(
    code: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify TOTP code and permanently enable MFA."""
    if not user.mfa_secret:
        raise HTTPException(status_code=400, detail="MFA not set up. Call /enable first.")
    secret = decrypt_mfa_secret(user.mfa_secret)
    if not verify_totp(secret, code):
        raise HTTPException(status_code=400, detail="Invalid TOTP code")
    user.mfa_enabled = True
    await db.commit()
    return {
        "status": "success",
        "data": {"mfa_enabled": True},
        "message": "MFA enabled successfully",
        "meta": None,
    }


@router.post("/disable")
async def disable_mfa(
    code: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Disable MFA after verifying a TOTP code."""
    if not user.mfa_enabled or not user.mfa_secret:
        raise HTTPException(status_code=400, detail="MFA is not enabled")
    secret = decrypt_mfa_secret(user.mfa_secret)
    if not verify_totp(secret, code):
        raise HTTPException(status_code=400, detail="Invalid TOTP code")
    user.mfa_enabled = False
    user.mfa_secret = None
    await db.commit()
    return {
        "status": "success",
        "data": {"mfa_enabled": False},
        "message": "MFA disabled successfully",
        "meta": None,
    }
```

---

## GROUPE D : API (4 fichiers)

---

### D1. app/api/v1/router.py

**Description** : Router principal API v1. Regroupe tous les sous-routers avec leurs prefixes.

**Dependances** : `app.api.v1.auth`, `app.api.v1.auth_mfa`, `app.api.v1.endpoints.health`, `app.api.v1.endpoints.tenants`, `app.api.v1.endpoints.users`.

**Contenu attendu** :

```python
# File: app/api/v1/router.py
# Purpose: Main API v1 router aggregator
# Dependencies: all v1 endpoint modules

from fastapi import APIRouter
from app.api.v1 import auth, auth_mfa
from app.api.v1.endpoints import health, tenants, users

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(auth_mfa.router, prefix="/auth", tags=["MFA"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["Tenants"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
```

---

### D2. app/api/v1/endpoints/health.py

**Description** : Endpoints de health check avec circuit breaker status, rate limit exempt.

**Dependances** : `app.core.circuit_breaker.get_breaker_status`, `app.database`.

**Contenu attendu** :

```python
# File: app/api/v1/endpoints/health.py
# Purpose: Health check and system status endpoints
# Dependencies: app.core.circuit_breaker, app.database, app.config.settings

from fastapi import APIRouter, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.circuit_breaker import get_breaker_status
from app.config import settings

router = APIRouter()


@router.get("/live")
async def health_live() -> dict:
    """Liveness probe - lightweight."""
    return {"status": "success", "data": {"alive": True}, "message": "Service is alive", "meta": None}


@router.get("/ready")
async def health_ready(db: AsyncSession = Depends(get_db)) -> dict:
    """Readiness probe - checks DB connectivity."""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "success", "data": {"ready": True}, "message": "Service is ready", "meta": None}
    except Exception as exc:
        return {"status": "error", "data": {"ready": False}, "message": str(exc), "meta": None}


@router.get("/status")
async def health_status(db: AsyncSession = Depends(get_db)) -> dict:
    """Full status with circuit breakers and version."""
    breaker_status = get_breaker_status()
    return {
        "status": "success",
        "data": {
            "version": settings.app_version,
            "environment": settings.environment,
            "circuit_breakers": breaker_status,
        },
        "message": "System status",
        "meta": None,
    }
```

---

### D3. app/api/v1/endpoints/tenants.py

**Description** : CRUD tenants avec protection par role. Super admin peut tout voir, tenant_admin ne voit que son tenant.

**Dependances** : `app.dependencies`, `app.models.ao`, `app.database`.

**Contenu attendu** (specification detaillee) :

- `GET /tenants/` : Liste paginee. Super_admin voit tous les tenants (meme soft-deleted via query param). Tenant_admin/tenant_manager ne voit que leur tenant. Response standardisee.
- `GET /tenants/{tenant_id}` : Detail. Meme regles de visibilite.
- `POST /tenants/` : Creation. Super_admin ou Tenant_admin (si permissions). Cree tenant avec slug unique.
- `PATCH /tenants/{tenant_id}` : Update partiel. Seuls super_admin et tenant_admin (sur son tenant) peuvent modifier.
- `DELETE /tenants/{tenant_id}` : Soft delete. Seul super_admin peut supprimer. Met a jour deleted_at.
- Toutes les routes protegees par `require_admin` ou `require_manager` selon l'operation.

---

### D4. app/api/v1/endpoints/users.py

**Description** : CRUD utilisateurs avec gestion des invitations, changement de role, soft delete.

**Dependances** : `app.dependencies`, `app.models.ao`, `app.database`, `app.services.audit_service`.

**Contenu attendu** (specification detaillee) :

- `GET /users/` : Liste paginee d'utilisateurs du tenant courant. Super_admin voit tous. Filtre par role.
- `GET /users/{user_id}` : Detail d'un user du meme tenant (ou tous pour super_admin).
- `POST /users/invite` : Envoi d'invitation. Cree un UserInvitation avec token securise (secrets.token_urlsafe). Email simule ou envoi reel via email_breaker. Audit log insertion.
- `PATCH /users/{user_id}/role` : Changement de role. Seul super_admin ou tenant_admin peut changer les roles. Impossible de promouvoir au-dela de son propre niveau (un tenant_admin ne peut pas creer de super_admin).
- `DELETE /users/{user_id}` : Soft delete. Seul super_admin ou tenant_admin peut supprimer. Un user ne peut pas se supprimer lui-meme.

---

## GROUPE E : SERVICES (2 fichiers)

---

### E1. app/services/feature_flags.py

**Description** : Service de gestion des feature flags. Evaluation par utilisateur/tenant/global, gating par plan, kill switch, rollout percentage.

**Dependances** : `app.models.ao.FeatureFlag`, `app.models.ao.FeatureFlagScope`, `app.database`.

**Contenu attendu** :

```python
# File: app/services/feature_flags.py
# Purpose: Feature flag evaluation with plan gating, kill switch, and rollout
# Dependencies: app.models.ao, sqlalchemy.ext.asyncio

import hashlib
from typing import Any
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ao import FeatureFlag, FeatureFlagScope


class FeatureFlagService:
    """
    Evaluate feature flags with the following precedence:
    1. Kill switch (global OFF wins)
    2. User-specific flag
    3. Tenant-specific flag
    4. Global flag
    5. Plan gating
    6. Rollout percentage (consistent hash on user_id)
    """

    @staticmethod
    async def is_enabled(
        db: AsyncSession,
        flag_name: str,
        user_id: str | None = None,
        tenant_id: str | None = None,
        user_plan: str | None = None,
    ) -> bool:
        # Build query matching most-specific to least-specific
        query = select(FeatureFlag).where(
            FeatureFlag.name == flag_name,
            FeatureFlag.deleted_at.is_(None),
            FeatureFlag.enabled == True,
        )
        result = await db.execute(query)
        flags = result.scalars().all()

        if not flags:
            return False

        # Check kill switch on any flag
        if any(f.kill_switch for f in flags):
            return False

        # Sort by scope specificity
        scope_priority = {FeatureFlagScope.USER: 0, FeatureFlagScope.TENANT: 1, FeatureFlagScope.GLOBAL: 2}
        flags_sorted = sorted(flags, key=lambda f: scope_priority.get(f.scope, 3))

        for flag in flags_sorted:
            # Skip if plan-gated and user plan doesn't match
            if flag.gated_by_plan and flag.gated_by_plan != user_plan:
                continue

            # Scope matching
            if flag.scope == FeatureFlagScope.USER and str(flag.user_id) != user_id:
                continue
            if flag.scope == FeatureFlagScope.TENANT and str(flag.tenant_id) != tenant_id:
                continue

            # Rollout check
            if flag.rollout_percentage < 100 and user_id:
                user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16) % 100
                if user_hash >= flag.rollout_percentage:
                    continue

            return True

        return False

    @staticmethod
    async def get_all_for_context(
        db: AsyncSession,
        user_id: str | None = None,
        tenant_id: str | None = None,
        user_plan: str | None = None,
    ) -> dict[str, bool]:
        """Return all active flags for a given context."""
        result = await db.execute(
            select(FeatureFlag).where(FeatureFlag.deleted_at.is_(None))
        )
        flags = result.scalars().all()
        flag_names = {f.name for f in flags}
        return {
            name: await FeatureFlagService.is_enabled(db, name, user_id, tenant_id, user_plan)
            for name in flag_names
        }
```

---

### E2. app/services/audit_service.py

**Description** : Service d'insertion d'audit logs avec hash chain. Insere dans la meme transaction DB que l'operation parente.

**Dependances** : `app.models.ao.AuditLog`, `app.core.audit.compute_audit_hash`, `app.core.audit.now_utc`.

**Contenu attendu** :

```python
# File: app/services/audit_service.py
# Purpose: Forensic audit log insertion with hash chain integrity
# Dependencies: app.models.ao, app.core.audit, sqlalchemy.ext.asyncio

from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ao import AuditLog, AuditAction
from app.core.audit import compute_audit_hash, now_utc


class AuditService:
    """
    Insert audit logs maintaining an immutable SHA-256 hash chain.
    Each new record references the hash of the previous record for the same tenant.
    """

    @staticmethod
    async def log(
        db: AsyncSession,
        action: AuditAction,
        entity_type: str,
        entity_id: str | None = None,
        payload_before: dict | None = None,
        payload_after: dict | None = None,
        user_id: str | None = None,
        tenant_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuditLog:
        """
        Insert an audit record with hash chain linking.
        Must be called within an active DB transaction.
        """
        # Fetch previous hash for this tenant
        previous_hash = await AuditService._get_last_hash(db, tenant_id)

        timestamp = now_utc()
        record_data = {
            "tenant_id": str(tenant_id) if tenant_id else None,
            "user_id": str(user_id) if user_id else None,
            "action": action.value,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "payload_before": payload_before,
            "payload_after": payload_after,
        }

        audit_hash = compute_audit_hash(previous_hash, record_data, timestamp)

        log_entry = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            payload_before=payload_before,
            payload_after=payload_after,
            ip_address=ip_address,
            user_agent=user_agent,
            previous_hash=previous_hash,
            hash=audit_hash,
        )
        db.add(log_entry)
        return log_entry

    @staticmethod
    async def _get_last_hash(db: AsyncSession, tenant_id: str | None) -> str | None:
        """Fetch the hash of the most recent audit log for a tenant."""
        query = (
            select(AuditLog)
            .where(AuditLog.tenant_id == tenant_id)
            .order_by(AuditLog.created_at.desc())
            .limit(1)
        )
        result = await db.execute(query)
        last = result.scalar_one_or_none()
        return last.hash if last else None

    @staticmethod
    async def verify_chain(db: AsyncSession, tenant_id: str | None) -> bool:
        """Verify the integrity of the audit chain for a tenant."""
        from app.core.audit import verify_hash_chain
        result = await db.execute(
            select(AuditLog)
            .where(AuditLog.tenant_id == tenant_id)
            .order_by(AuditLog.created_at.asc())
        )
        records = [
            {
                "hash": r.hash,
                "previous_hash": r.previous_hash,
                "created_at": r.created_at,
                **{k: getattr(r, k) for k in ("tenant_id", "user_id", "action", "entity_type", "entity_id", "payload_before", "payload_after")},
            }
            for r in result.scalars().all()
        ]
        return verify_hash_chain(records)
```

---

## GROUPE F : SCRIPTS (2 fichiers)

---

### F1. scripts/backup-db.sh

**Description** : Script de backup PostgreSQL avec compression, upload S3 optionnel, rotation des backups.

**Dependances** : `pg_dump`, `gzip`, `awscli` (optionnel).

**Contenu attendu** :

```bash
#!/usr/bin/env bash
# File: scripts/backup-db.sh
# Purpose: Backup PostgreSQL database with compression and optional S3 upload
# Dependencies: pg_dump, gzip, awscli (optional)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="${PROJECT_ROOT}/.env"

# Load env vars if .env exists
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

# Defaults
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${POSTGRES_USER:-taka}"
DB_NAME="${POSTGRES_DB:-taka_db}"
DB_PASS="${POSTGRES_PASSWORD:-}"
BACKUP_DIR="${BACKUP_DIR:-/tmp/taka-backups}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
S3_BUCKET="${S3_BACKUP_BUCKET:-}"
S3_ENDPOINT="${S3_BACKUP_ENDPOINT:-}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_${DB_NAME}_${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"

echo "[BACKUP] Starting backup of $DB_NAME at $TIMESTAMP"

# Run pg_dump with compression
export PGPASSWORD="$DB_PASS"
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" --no-owner --no-privileges | gzip > "${BACKUP_DIR}/${BACKUP_FILE}"
unset PGPASSWORD

FILE_SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_FILE}" | cut -f1)
echo "[BACKUP] Completed: ${BACKUP_FILE} ($FILE_SIZE)"

# Upload to S3 if configured
if [ -n "$S3_BUCKET" ] && [ -n "$S3_ENDPOINT" ]; then
    echo "[BACKUP] Uploading to S3..."
    aws --endpoint-url "$S3_ENDPOINT" s3 cp "${BACKUP_DIR}/${BACKUP_FILE}" "s3://${S3_BUCKET}/${BACKUP_FILE}"
    echo "[BACKUP] S3 upload complete"
fi

# Local rotation
find "$BACKUP_DIR" -name "backup_${DB_NAME}_*.sql.gz" -mtime +$RETENTION_DAYS -delete
echo "[BACKUP] Cleaned up backups older than $RETENTION_DAYS days"

# If cron mode, log to syslog
if [ "${CRON_MODE:-0}" = "1" ]; then
    logger -t taka-backup "Database backup completed: ${BACKUP_FILE} ($FILE_SIZE)"
fi

echo "[BACKUP] Done"
```

---

### F2. scripts/restore-db.sh

**Description** : Script de restauration PostgreSQL depuis un backup local ou S3. Teste la restauration sur une base temporaire.

**Dependances** : `pg_restore`/`psql`, `gunzip`, `awscli` (optionnel).

**Contenu attendu** :

```bash
#!/usr/bin/env bash
# File: scripts/restore-db.sh
# Purpose: Restore PostgreSQL database from a backup file
# Dependencies: psql, gunzip, awscli (optional)

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <backup_file_or_s3_path> [--test]"
    echo "  backup_file: local path or s3://bucket/path"
    echo "  --test: restore to a temporary database for validation"
    exit 1
fi

BACKUP_SOURCE="$1"
TEST_MODE=0
if [ "${2:-}" = "--test" ]; then
    TEST_MODE=1
fi

ENV_FILE="$(dirname "$(dirname "$(realpath "$0")")")/.env"
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${POSTGRES_USER:-taka}"
DB_NAME="${POSTGRES_DB:-taka_db}"
DB_PASS="${POSTGRES_PASSWORD:-}"

export PGPASSWORD="$DB_PASS"

# Determine backup file path
if [[ "$BACKUP_SOURCE" == s3://* ]]; then
    LOCAL_BACKUP="/tmp/restore_$(basename "$BACKUP_SOURCE")"
    echo "[RESTORE] Downloading from S3..."
    aws s3 cp "$BACKUP_SOURCE" "$LOCAL_BACKUP"
else
    LOCAL_BACKUP="$BACKUP_SOURCE"
fi

# Decompress if needed
if [[ "$LOCAL_BACKUP" == *.gz ]]; then
    echo "[RESTORE] Decompressing..."
    gunzip -c "$LOCAL_BACKUP" > /tmp/restore_dump.sql
    SQL_FILE="/tmp/restore_dump.sql"
else
    SQL_FILE="$LOCAL_BACKUP"
fi

# Test mode: create temp DB
if [ "$TEST_MODE" -eq 1 ]; then
    TEST_DB="${DB_NAME}_test_restore_$(date +%s)"
    echo "[RESTORE] TEST MODE - Creating temp database $TEST_DB"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "CREATE DATABASE $TEST_DB;"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB" -f "$SQL_FILE"
    TABLE_COUNT=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB" -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';")
    echo "[RESTORE] Test restore successful. Tables restored: $TABLE_COUNT"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "DROP DATABASE $TEST_DB;"
    echo "[RESTORE] Temp database dropped"
else
    echo "[RESTORE] WARNING: This will overwrite database $DB_NAME"
    echo "[RESTORE] Press Ctrl+C within 5 seconds to cancel..."
    sleep 5
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$SQL_FILE"
    echo "[RESTORE] Database restored successfully"
fi

unset PGPASSWORD
rm -f /tmp/restore_dump.sql

echo "[RESTORE] Done"
```

---

## GROUPE G : DOCKER & DEVOPS (3 fichiers)

---

### G1. docker-compose.yml

**Description** : Compose complet avec PostgreSQL+pgvector, Redis, backend, frontend. Healthchecks, volumes, reseau.

**Dependances** : Dockerfile (backend), Dockerfile (frontend).

**Contenu attendu** :

```yaml
version: "3.9"

services:
  db:
    image: ankane/pgvector:latest
    container_name: taka-db
    restart: unless-stopped
    environment:
      POSTGRES_USER: taka
      POSTGRES_PASSWORD: taka_password
      POSTGRES_DB: taka_db
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./scripts/backup-db.sh:/usr/local/bin/backup-db.sh:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U taka -d taka_db"]
      interval: 10s
      timeout: 5s
      retries: 5
    ports:
      - "5432:5432"
    networks:
      - taka-network

  redis:
    image: redis:7-alpine
    container_name: taka-redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    ports:
      - "6379:6379"
    networks:
      - taka-network

  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: taka-backend
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    env_file:
      - .env
    environment:
      - DATABASE_URL=postgresql+asyncpg://taka:taka_password@db:5432/taka_db
      - REDIS_URL=redis://redis:6379/0
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app/app:ro
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health/live"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    networks:
      - taka-network
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: taka-frontend
    restart: unless-stopped
    depends_on:
      - backend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000/api/v1
    volumes:
      - ./frontend:/app:cached
      - /app/node_modules
    networks:
      - taka-network
    command: npm run dev -- --host 0.0.0.0

volumes:
  pgdata:

networks:
  taka-network:
    driver: bridge
```

---

### G2. Dockerfile

**Description** : Image Python multi-stage pour le backend. Poetry install, sans dev deps en production.

**Dependances** : `pyproject.toml`, `poetry.lock`.

**Contenu attendu** :

```dockerfile
# File: Dockerfile
# Purpose: Backend Docker image
# Dependencies: pyproject.toml, poetry.lock

FROM python:3.11-slim AS builder

WORKDIR /app

RUN pip install --no-cache-dir poetry==1.8.0

COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi --no-root

COPY app ./app

FROM python:3.11-slim AS runtime

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY app ./app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### G3. .github/workflows/ci.yml

**Description** : Pipeline CI GitHub Actions : lint (black, flake8, mypy), security scan (bandit), tests pytest avec coverage, build Docker.

**Dependances** : `pyproject.toml`, `pytest.ini` (ou section dans pyproject.toml).

**Contenu attendu** :

```yaml
# File: .github/workflows/ci.yml
# Purpose: CI pipeline with lint, security scan, tests, and Docker build
# Dependencies: pyproject.toml

name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: ankane/pgvector:latest
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Poetry
        uses: snok/install-poetry@v1
        with:
          version: 1.8.0

      - name: Install dependencies
        run: |
          poetry install --with dev

      - name: Run Black check
        run: poetry run black --check app tests

      - name: Run isort check
        run: poetry run isort --check-only app tests

      - name: Run flake8
        run: poetry run flake8 app tests

      - name: Run mypy
        run: poetry run mypy app

      - name: Run Bandit security scan
        run: poetry run bandit -r app -f json -o bandit-report.json || true

      - name: Run tests with coverage
        env:
          DATABASE_URL: postgresql+asyncpg://test:test@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/1
          SECRET_KEY: test-secret-key-32-chars-long
        run: |
          poetry run pytest --cov=app --cov-report=xml --cov-fail-under=80

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml

  build-docker:
    runs-on: ubuntu-latest
    needs: lint-and-test
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build backend image
        run: docker build -t taka-backend:test .

      - name: Build frontend image
        run: docker build -t taka-frontend:test ./frontend
```

---

## GROUPE H : TESTS (4 fichiers)

---

### H1. tests/conftest.py

**Description** : Fixtures pytest partagees : event loop, DB de test, client HTTP async, utilisateur de test, token JWT.

**Dependances** : `pytest-asyncio`, `httpx`, `app.database`, `app.models.ao`.

**Contenu attendu** :

- Fixture `event_loop` : `asyncio.get_event_loop_policy().new_event_loop()`
- Fixture `db_engine` : `create_async_engine(TEST_DATABASE_URL)`
- Fixture `db_session` : AsyncSession avec rollback a la fin de chaque test
- Fixture `client` : `AsyncClient(app=app, base_url="http://test")`
- Fixture `test_tenant` : Cree un tenant dans la session de test
- Fixture `test_user` : Cree un user VIEWER lie au tenant de test
- Fixture `test_admin` : Cree un user TENANT_ADMIN lie au tenant de test
- Fixture `auth_headers` : Headers `Authorization: Bearer <token>` pour test_user
- Fixture `admin_headers` : Headers pour test_admin

---

### H2. tests/test_auth.py

**Description** : Tests couverture authentification : register, login, MFA flow, refresh, invitation, me.

**Dependances** : `tests.conftest` fixtures.

**Contenu attendu** (specification detaillee) :

- `test_register_success` : POST /auth/register retourne 201, user cree, tenant cree
- `test_register_duplicate_email` : 409 conflict
- `test_login_success` : retourne access_token + refresh_token
- `test_login_mfa_required` : user avec mfa_enabled=True retourne mfa_required: true + mfa_token
- `test_mfa_verify_success` : echange mfa_token contre tokens
- `test_mfa_verify_invalid_code` : 400
- `test_refresh_token` : echange refresh valide
- `test_refresh_invalid` : 401
- `test_invitation_accept` : token valide, creation user, invitation passe a accepted
- `test_get_me` : retourne user avec tenant

---

### H3. tests/test_tenants.py

**Description** : Tests CRUD tenants avec permissions par role.

**Dependances** : `tests.conftest` fixtures.

**Contenu attendu** :

- `test_list_tenants_as_admin` : 200, liste contient le tenant
- `test_list_tenants_as_viewer` : 403 ou liste filtree au tenant
- `test_create_tenant_as_super_admin` : 201, slug unique
- `test_create_tenant_as_viewer` : 403
- `test_update_tenant` : PATCH partiel
- `test_soft_delete_tenant` : deleted_at non null, mais record existe

---

### H4. tests/test_services.py

**Description** : Tests des services : FeatureFlagService, AuditService.

**Dependances** : `tests.conftest` fixtures.

**Contenu attendu** :

- `test_feature_flag_global_enabled` : is_enabled retourne True
- `test_feature_flag_kill_switch` : kill_switch=True force False
- `test_feature_flag_plan_gating` : plan mismatch retourne False
- `test_feature_flag_rollout_percentage` : hash deterministe, pourcentage respecte
- `test_audit_log_hash_chain` : 2 logs consecutifs, le second a previous_hash == hash du premier
- `test_audit_verify_chain` : verify_chain retourne True pour chain valide

---

## GROUPE I : FRONTEND REACT (3 fichiers)

---

### I1. frontend/src/main.tsx

**Description** : Point d'entree React avec Sentry initialise, router, providers.

**Dependances** : `@sentry/react`, `react-router-dom`.

**Contenu attendu** :

```tsx
// File: frontend/src/main.tsx
// Purpose: React application entry point with Sentry initialization
// Dependencies: @sentry/react, react-router-dom

import React from "react";
import ReactDOM from "react-dom/client";
import * as Sentry from "@sentry/react";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./index.css";

const SENTRY_DSN = import.meta.env.VITE_SENTRY_DSN;
const APP_VERSION = import.meta.env.VITE_APP_VERSION || "0.2.0";
const ENVIRONMENT = import.meta.env.VITE_ENVIRONMENT || "development";

if (SENTRY_DSN) {
  Sentry.init({
    dsn: SENTRY_DSN,
    release: APP_VERSION,
    environment: ENVIRONMENT,
    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.replayIntegration({
        maskAllText: false,
        blockAllMedia: false,
      }),
    ],
    tracesSampleRate: ENVIRONMENT === "production" ? 0.1 : 1.0,
    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,
  });
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
```

---

### I2. frontend/src/components/ErrorBoundary.tsx

**Description** : ErrorBoundary React avec reporting Sentry, fallback UI.

**Dependances** : `@sentry/react`, `react`.

**Contenu attendu** :

```tsx
// File: frontend/src/components/ErrorBoundary.tsx
// Purpose: React Error Boundary with Sentry error reporting
// Dependencies: @sentry/react, react

import React, { Component, ReactNode } from "react";
import * as Sentry from "@sentry/react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    Sentry.captureException(error, {
      extra: { componentStack: errorInfo.componentStack },
    });
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return (
        <div className="error-boundary">
          <h2>Something went wrong.</h2>
          <p>The error has been reported. Please refresh the page.</p>
          {import.meta.env.DEV && this.state.error && (
            <pre>{this.state.error.stack}</pre>
          )}
          <button onClick={() => window.location.reload()}>Refresh</button>
        </div>
      );
    }
    return this.props.children;
  }
}
```

---

### I3. frontend/src/App.tsx

**Description** : Composant App racine avec ErrorBoundary, layout de base, routes principales.

**Dependances** : `react-router-dom`, `./components/ErrorBoundary`.

**Contenu attendu** (specification detaillee) :

- `<ErrorBoundary>` en wrapper racine
- Routes : `/` (home), `/login`, `/register`, `/dashboard`, `/admin/users`, `/admin/tenants`
- Navigation basique avec liens
- Context provider pour auth (meme si minimal)
- Utilisation de Sentry.UserFeedback si disponible

---

# 6. LIVRABLE FINAL & VALIDATION

## Structure attendue du repository

```
taka/
├── .env.template
├── .github/
│   └── workflows/
│       └── ci.yml
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── README.md
├── scripts/
│   ├── backup-db.sh
│   └── restore-db.sh
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── sentry.py
│   │   ├── rate_limit.py
│   │   ├── circuit_breaker.py
│   │   ├── security.py
│   │   └── audit.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── ao.py
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py
│   │       ├── auth.py
│   │       ├── auth_mfa.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── health.py
│   │           ├── tenants.py
│   │           └── users.py
│   └── services/
│       ├── __init__.py
│       ├── feature_flags.py
│       └── audit_service.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_tenants.py
│   └── test_services.py
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── index.css
        └── components/
            └── ErrorBoundary.tsx
```

## Validation post-generation

L'agent doit verifier les points suivants apres generation :

V1. `docker-compose up --build` demarre sans erreur (backend accessible sur :8000, frontend sur :5173, DB sur :5432, Redis sur :6379).
V2. `curl http://localhost:8000/api/v1/health/live` retourne `{"status":"success","data":{"alive":true}}`.
V3. `curl http://localhost:8000/api/v1/health/status` retourne la version et les circuit breakers.
V4. `poetry run pytest` passe avec couverture >= 80%.
V5. `poetry run bandit -r app` ne retourne pas de HIGH severity.
V6. Les 8 tables principales (users, tenants, ao, documents, conversations, messages, feature_flags, user_invitations) + tables audit (audit_logs, llm_call_logs, event_logs, state_snapshots) + tables memoire (memory_global, memory_tenant, memory_session) existent dans la DB.
V7. Le fichier `app/models/ao.py` contient les enums UserRole (5 valeurs), TenantType (2 valeurs), et les 3 tables de memoire.
V8. Le fichier `app/core/security.py` expose `generate_mfa_secret`, `verify_totp`, `encrypt_mfa_secret`.
V9. Les scripts `scripts/backup-db.sh` et `scripts/restore-db.sh` sont executables (`chmod +x`) et syntaxiquement valides (`bash -n`).
V10. Le CI GitHub Actions est syntaxiquement valide (pas d'erreur YAML).

---

# 7. REGLES DE VALIDATION

## Validation du code genere

Apres execution de ce prompt, l'agent DOIT verifier :

1. **Comptage des fichiers** : Au moins 30 fichiers crees avec leur contenu complet (pas de stubs vides).
2. **Comptage des tables** : 14+ tables definies dans `app/models/ao.py`.
3. **Comptage des routes** : Au moins 20 routes definies dans les routers.
4. **Tests executables** : `pytest` passe sans erreur de syntaxe.
5. **Type coverage** : Pas de `Any` injustifie dans le code de production.
6. **Secrets** : Verification que `settings.secret_key` et `settings.sentry_dsn` ne sont jamais hardcodes.
7. **Hash chain** : Les AuditLog ont `previous_hash` et `hash` non null.
8. **Feature flags** : Le service supporte kill_switch, plan gating, rollout percentage.
9. **MFA** : Les routes /mfa/enable, /mfa/verify-and-enable, /mfa/disable existent.
10. **Sentry** : Le SDK est initialise conditionnellement dans main.py via `init_sentry()`.

## Ordre de creation recommande

1. `pyproject.toml` + `.env.template`
2. `app/config.py`
3. `app/database.py`
4. `app/core/` (audit.py, security.py, sentry.py, rate_limit.py, circuit_breaker.py)
5. `app/models/ao.py`
6. `app/services/` (feature_flags.py, audit_service.py)
7. `app/dependencies.py`
8. `app/api/v1/` (router, auth, auth_mfa, endpoints)
9. `app/main.py`
10. `scripts/` (backup-db.sh, restore-db.sh)
11. `tests/` (conftest + tests)
12. Docker & CI (Dockerfile, docker-compose, ci.yml)
13. Frontend (main.tsx, ErrorBoundary, App.tsx)

---

## FICHIERS ADDITIONNELS MANQUANTS DANS LES GROUPES PRECEDENTS

Ces fichiers n'ont pas ete places dans les groupes A-I mais sont OBLIGATOIRES pour un projet fonctionnel.

---

### app/main.py

**Description** : Point d'entree FastAPI. Initialise Sentry, le rate limiter, le timeout middleware, les handlers d'exception, les routes, et la DB au demarrage.

**Dependances** : `app.config.settings`, `app.core.sentry.init_sentry`, `app.core.rate_limit.limiter`, `app.core.rate_limit.rate_limit_exceeded_handler`, `app.api.v1.router.api_router`, `app.database.init_db`.

**Contenu attendu** :

```python
# File: app/main.py
# Purpose: FastAPI application entry point with Sentry, rate limiting, timeout middleware
# Dependencies: app.config, app.core.sentry, app.core.rate_limit, app.api.v1.router, app.database

import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.core.sentry import init_sentry
from app.core.rate_limit import limiter, rate_limit_exceeded_handler
from app.api.v1.router import api_router
from app.database import init_db

# Initialize Sentry before app creation
init_sentry()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: init DB on startup."""
    logger.info("Starting up TAKA API v%s", settings.app_version)
    await init_db()
    yield
    logger.info("Shutting down TAKA API")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="TAKA - Plateforme d'appels d'offres automatises",
    lifespan=lifespan,
)

# === MIDDLEWARES ===

# 1. Timeout middleware (30s default)
@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    """Global 30s timeout on all requests. Override via X-Request-Timeout header (max 120s)."""
    import asyncio
    timeout_seconds = 30
    timeout_header = request.headers.get("x-request-timeout")
    if timeout_header and timeout_header.isdigit():
        timeout_seconds = min(int(timeout_header), 120)
    try:
        return await asyncio.wait_for(call_next(request), timeout=timeout_seconds)
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={
                "status": "error",
                "data": None,
                "message": f"Request timeout after {timeout_seconds}s",
                "meta": None,
            },
        )

# 2. Rate limiter state injection
@app.middleware("http")
async def rate_limit_state_middleware(request: Request, call_next):
    """Attach rate limiter to request.state for SlowAPI key derivation."""
    request.state.limiter = limiter
    response = await call_next(request)
    return response

# 3. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === EXCEPTION HANDLERS ===

@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return rate_limit_exceeded_handler(request, exc)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "data": None,
            "message": "Internal server error",
            "meta": None,
        },
    )

# === ROUTES ===

app.state.limiter = limiter
app.include_router(api_router)

# Health at root level for probes
@app.get("/health", tags=["Health"])
async def root_health():
    return {"status": "success", "data": {"alive": True}, "message": "OK", "meta": None}
```

---

### app/__init__.py

**Description** : Init package app. Vide ou avec version.

**Contenu attendu** :

```python
# File: app/__init__.py
# Purpose: App package root
# Dependencies: None

__version__ = "0.2.0"
```

---

### app/core/__init__.py

**Description** : Init package core.

**Contenu attendu** : Fichier vide.

---

### app/models/__init__.py

**Description** : Init package models. Re-exporte les classes principales.

**Contenu attendu** :

```python
# File: app/models/__init__.py
# Purpose: Re-export all models for convenient imports
# Dependencies: app.models.ao

from app.models.ao import (
    User,
    Tenant,
    AO,
    Document,
    Conversation,
    Message,
    UserInvitation,
    FeatureFlag,
    MemoryGlobal,
    MemoryTenant,
    MemorySession,
    AuditLog,
    LLMCallLog,
    EventLog,
    StateSnapshot,
    UserRole,
    TenantType,
    InvitationStatus,
    FeatureFlagScope,
    AuditAction,
)
```

---

### app/api/__init__.py

**Description** : Init package api. Vide.

**Contenu attendu** : Fichier vide.

---

### app/api/v1/__init__.py

**Description** : Init package v1. Vide.

**Contenu attendu** : Fichier vide.

---

### app/api/v1/endpoints/__init__.py

**Description** : Init package endpoints. Vide.

**Contenu attendu** : Fichier vide.

---

### app/services/__init__.py

**Description** : Init package services. Re-exporte les services.

**Contenu attendu** :

```python
# File: app/services/__init__.py
# Purpose: Re-export all services
# Dependencies: app.services.feature_flags, app.services.audit_service

from app.services.feature_flags import FeatureFlagService
from app.services.audit_service import AuditService
```

---

### tests/__init__.py

**Description** : Init package tests. Vide.

**Contenu attendu** : Fichier vide.

---

### frontend/Dockerfile

**Description** : Image Docker pour le frontend React+Vite.

**Dependances** : `package.json`.

**Contenu attendu** :

```dockerfile
# File: frontend/Dockerfile
# Purpose: Frontend React Docker image
# Dependencies: package.json

FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine AS runtime

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

---

### frontend/package.json

**Description** : Configuration npm du frontend avec React 18, TypeScript, Vite, Sentry, React Router.

**Dependances** : `npm`.

**Contenu attendu** :

```json
{
  "name": "taka-frontend",
  "version": "0.2.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0"
  },
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "^6.27.0",
    "@sentry/react": "^8.0.0",
    "@sentry/browser": "^8.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.0",
    "typescript": "^5.6.0",
    "vite": "^5.4.0",
    "eslint": "^9.0.0",
    "@eslint/js": "^9.0.0",
    "eslint-plugin-react-hooks": "^5.0.0",
    "eslint-plugin-react-refresh": "^0.4.0"
  }
}
```

---

### frontend/vite.config.ts

**Description** : Configuration Vite pour le build React.

**Dependances** : `vite`.

**Contenu attendu** :

```typescript
// File: frontend/vite.config.ts
// Purpose: Vite configuration for React build
// Dependencies: vite, @vitejs/plugin-react

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
```

---

### frontend/tsconfig.json

**Description** : Configuration TypeScript standard pour React.

**Dependances** : `typescript`.

**Contenu attendu** :

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

---

### frontend/tsconfig.node.json

**Description** : Configuration TypeScript pour Vite config.

**Contenu attendu** :

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

---

### frontend/src/index.css

**Description** : Styles globaux minimaux.

**Contenu attendu** :

```css
/* File: frontend/src/index.css */
/* Purpose: Global styles */

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  background-color: #f5f5f5;
  color: #333;
  line-height: 1.5;
}

.error-boundary {
  padding: 2rem;
  text-align: center;
}

.error-boundary h2 {
  color: #dc3545;
  margin-bottom: 1rem;
}

.error-boundary pre {
  text-align: left;
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  margin: 1rem 0;
}
```

---

### frontend/src/components/AuthContext.tsx

**Description** : Context React minimal pour l'authentification (token, user, login, logout).

**Dependances** : `react`.

**Contenu attendu** :

```tsx
// File: frontend/src/components/AuthContext.tsx
// Purpose: Authentication context provider
// Dependencies: react

import React, { createContext, useContext, useState, useCallback, ReactNode } from "react";

interface User {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  tenant_id: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string, user: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem("token"));

  const login = useCallback((newToken: string, newUser: User) => {
    localStorage.setItem("token", newToken);
    setToken(newToken);
    setUser(newUser);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
```

---

### frontend/nginx.conf

**Description** : Configuration nginx pour servir le frontend et proxyfier /api.

**Contenu attendu** :

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000/api;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## DETAILS SUPPLEMENTAIRES SUR LES SCHEMAS PYDANTIC

Bien que les schemas ne soient pas des fichiers separes dans la structure de ce prompt, l'agent DOIT creer un repertoire `app/schemas/` avec les classes suivantes. Chaque schema DOIT heriter de `BaseModel` v2 et utiliser `ConfigDict`.

### Schemas Auth (app/schemas/auth.py)

- `UserRegister` : email (EmailStr), password (min 8), full_name (optional), tenant_name (optional)
- `UserLogin` : email, password, mfa_code (optional)
- `TokenResponse` : access_token, refresh_token, token_type="bearer", mfa_required (bool), mfa_token (optional)
- `UserResponse` : id, email, full_name, role, is_active, tenant_id, mfa_enabled, created_at
- `InvitationCreate` : email, role
- `InvitationAccept` : token, password, full_name

### Schemas Tenant (app/schemas/tenant.py)

- `TenantCreate` : name (str), type (TenantType), slug (optional, auto-generated from name)
- `TenantUpdate` : name (optional), type (optional), settings (optional), billing_plan (optional), max_users (optional), is_active (optional)
- `TenantResponse` : id, name, type, slug, settings, billing_plan, max_users, is_active, created_at, updated_at

### Schemas Feature Flag (app/schemas/feature_flag.py)

- `FeatureFlagCreate` : name, description (optional), scope, tenant_id (optional), user_id (optional), enabled, gated_by_plan (optional), rollout_percentage (int, 0-100)
- `FeatureFlagResponse` : id, name, scope, enabled, kill_switch, gated_by_plan, rollout_percentage, created_at

### Schemas Audit (app/schemas/audit.py)

- `AuditLogResponse` : id, action, entity_type, entity_id, user_id, tenant_id, created_at, hash (readonly)

---

## DETAILS SUPPLEMENTAIRES SUR app/api/v1/endpoints/tenants.py

Ce fichier doit contenir EXACTEMENT les routes suivantes avec les protections indiquees :

| Methode | Route | Auth | Role | Description |
|---------|-------|------|------|-------------|
| GET | /tenants/ | Bearer | require_any_authenticated | Liste paginee (page, per_page query params) |
| GET | /tenants/{tenant_id} | Bearer | require_any_authenticated | Detail d'un tenant accessible |
| POST | /tenants/ | Bearer | require_admin | Creation avec validation slug unique |
| PATCH | /tenants/{tenant_id} | Bearer | require_admin | Update partielle, interdit sur deleted tenant |
| DELETE | /tenants/{tenant_id} | Bearer | require_admin | Soft delete, mise a jour deleted_at |

Chaque route DOIT inserer un AuditLog via AuditService.log() avec l'action correspondante (CREATE, UPDATE, DELETE, READ).
La route DELETE doit aussi soft-delete les users associes (cascade logique).

---

## DETAILS SUPPLEMENTAIRES SUR app/api/v1/endpoints/users.py

Ce fichier doit contenir EXACTEMENT les routes suivantes :

| Methode | Route | Auth | Role | Description |
|---------|-------|------|------|-------------|
| GET | /users/ | Bearer | require_collaborator | Liste paginee, filtree au tenant |
| GET | /users/{user_id} | Bearer | require_collaborator | Detail user du meme tenant |
| POST | /users/invite | Bearer | require_manager | Cree UserInvitation, log audit |
| PATCH | /users/{user_id}/role | Bearer | require_admin | Changement role, validation hierarchique |
| DELETE | /users/{user_id} | Bearer | require_admin | Soft delete, interdiction d'auto-suppression |

La route POST /users/invite DOIT :
1. Generer un token securise via `secrets.token_urlsafe(32)`
2. Calculer expires_at = now + 7 jours
3. Inserer UserInvitation dans la DB
4. Log audit INVITATION_SENT
5. Retourner l'invitation avec le token (dans un vrai systeme, l'email serait envoye)

La route PATCH /users/{user_id}/role DOIT respecter la hierarchie :
- Un TENANT_ADMIN ne peut pas promouvoir au-dela de TENANT_ADMIN
- Un SUPER_ADMIN peut assigner n'importe quel role
- Un user ne peut pas se retrograder lui-meme

---

## DETAILS SUPPLEMENTAIRES SUR app/api/v1/auth.py

La route POST /auth/login DOIT implementer le flow MFA suivant :

```
1. Verifier email + password
2. Si user.mfa_enabled == True :
   a. Generer un mfa_token (JWT avec sub=user.id, type="mfa_challenge", exp=5min)
   b. Retourner { mfa_required: true, mfa_token: "..." }
3. Si user.mfa_enabled == False :
   a. Generer access_token + refresh_token
   b. Mettre a jour last_login_at
   c. Retourner { access_token, refresh_token, token_type: "bearer" }
```

La route POST /auth/mfa/verify (dans auth.py, delegation a auth_mfa.py possible) DOIT :
1. Decoder le mfa_token (type="mfa_challenge")
2. Verifier le code TOTP avec verify_totp
3. Si valide : generer access_token + refresh_token, retourner TokenResponse
4. Si invalide : 400 avec message "Invalid MFA code"

---

## NOTE FINAL POUR KIMI CODE

Tu es en mode execution autonome. Tu ne poses AUCUNE question. Tu produis le code complet fichier par fichier. Tu respectes absolument les 16 regles absolues (R1-R16). Tu verifies les 10 points de validation (V1-V10) avant de declarer la mission terminee.

Le livrable est un projet fonctionnel, teste, conteneurise, avec monitoring, rate limiting, circuit breaker, MFA, feature flags, memoire persistante, tracabilite forensique complete, et CI/CD.

FIN DU PROMPT SPRINT 0 MIS A JOUR
