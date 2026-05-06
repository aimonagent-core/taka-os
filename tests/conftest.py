# =============================================================================
# T1 — Configuration pytest — Fixtures async pour TAKA OS
# =============================================================================

"""
Fixtures async pour la suite de tests TAKA OS.

Strategie :
- db_engine : engine async sur base de test (taka_test) avec Alembic
- db_session : session dans une transaction avec rollback a la fin
- client : HTTP client async (httpx.AsyncClient)
- authenticated_user : user de test + JWT token
- tenant : tenant de test
- business_line : ligne metier de test
- sample_ao : AO de test avec scoring

Toutes les fixtures sont scope="function" pour l'isolation maximale.
La base est creee une seule fois par session de test (scope="session").
"""

import asyncio
import os
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.security import get_password_hash
from app.database import Base, get_db
from app.main import app
from app.models.ao import Tenant, TenantType, User, UserRole

# --- Configuration de la base de test ---
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://taka:password@localhost:5432/taka_test",
)


# --- Engine de test (session-scoped) ---
@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """GIVEN une configuration de base de donnees de test
    WHEN le moteur est cree
    THEN il est pret avec les tables migrees via Alembic.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )

    # Creer la base de test si elle n'existe pas
    admin_url = TEST_DATABASE_URL.rsplit("/", 1)[0] + "/postgres"
    admin_engine = create_async_engine(admin_url, poolclass=NullPool)
    db_name = TEST_DATABASE_URL.rsplit("/", 1)[-1]
    async with admin_engine.begin() as conn:
        # Terminer les connexions existantes
        await conn.execute(
            text(
                f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                f"WHERE datname = '{db_name}' AND pid <> pg_backend_pid()"
            )
        )
        # Recreer la base
        await conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
        await conn.execute(text(f"CREATE DATABASE {db_name}"))
    await admin_engine.dispose()

    # Installer l'extension pgvector
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

    # Appliquer les migrations Alembic
    from alembic.config import Config
    from alembic import command

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    command.upgrade(alembic_cfg, "head")

    yield engine

    # Cleanup
    await engine.dispose()


# --- Session DB avec rollback automatique ---
@pytest_asyncio.fixture
async def db_session(
    db_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """GIVEN une transaction ouverte
    WHEN le test s'execute
    THEN les changements sont rollback a la fin (isolation parfaite).
    """
    async with db_engine.begin() as connection:
        session_maker = async_sessionmaker(
            bind=connection,
            expire_on_commit=False,
            autoflush=False,
            class_=AsyncSession,
        )
        async with session_maker() as session:
            yield session
            # Rollback automatique — aucun commit ici


# --- Client HTTP async ---
@pytest_asyncio.fixture
async def client(
    db_engine: AsyncEngine,
) -> AsyncGenerator[AsyncClient, None]:
    """GIVEN l'application FastAPI demarree
    WHEN un client HTTP lance une requete
    THEN il recoit une reponse.
    """
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with db_engine.begin() as connection:
            session_maker = async_sessionmaker(
                bind=connection,
                expire_on_commit=False,
                autoflush=False,
                class_=AsyncSession,
            )
            async with session_maker() as session:
                yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# --- Tenant de test ---
@pytest_asyncio.fixture
async def test_tenant(db_session: AsyncSession) -> Tenant:
    tenant = Tenant(
        name="Test Tenant",
        type=TenantType.SOUMISSIONNAIRE,
        slug=f"test-tenant-{uuid.uuid4().hex[:8]}",
    )
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    return tenant


@pytest_asyncio.fixture
async def tenant(db_session: AsyncSession, test_tenant: Tenant) -> Tenant:
    """Alias de test_tenant pour compatibilite avec les nouveaux tests."""
    return test_tenant


# --- Utilisateurs de test ---
@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession, test_tenant: Tenant) -> User:
    user = User(
        tenant_id=test_tenant.id,
        email=f"viewer-{uuid.uuid4().hex[:8]}@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test Viewer",
        role=UserRole.VIEWER,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_admin(db_session: AsyncSession, test_tenant: Tenant) -> User:
    user = User(
        tenant_id=test_tenant.id,
        email=f"admin-{uuid.uuid4().hex[:8]}@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test Admin",
        role=UserRole.TENANT_ADMIN,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# --- Headers authentifies ---
@pytest_asyncio.fixture
async def auth_headers(test_user: User) -> dict:
    from app.core.security import create_access_token

    token = create_access_token(subject=str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_headers(test_admin: User) -> dict:
    from app.core.security import create_access_token

    token = create_access_token(subject=str(test_admin.id))
    return {"Authorization": f"Bearer {token}"}


# --- Utilisateur authentifie complet (prompt T1) ---
@pytest_asyncio.fixture
async def authenticated_user(
    client: AsyncClient,
    db_session: AsyncSession,
    tenant: Tenant,
) -> Dict[str, Any]:
    """GIVEN un tenant existe
    WHEN un utilisateur s'enregistre et se connecte
    THEN il recoit un token JWT valide.
    """
    password = "TestPassword123!"
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        email=f"test_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password=get_password_hash(password),
        full_name="Test User",
        role=UserRole.TENANT_ADMIN,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)

    token = create_access_token(
        data={"sub": str(user.id), "tenant_id": str(tenant.id), "role": user.role},
    )

    return {
        "user": user,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
        "password": password,
        "tenant": tenant,
    }


# --- Ligne metier de test ---
@pytest_asyncio.fixture
async def business_line(db_session: AsyncSession, tenant: Tenant) -> Any:
    from app.models.business_line import BusinessLine

    bl = BusinessLine(
        tenant_id=tenant.id,
        name="Developpement Logiciel",
        description="Services de developpement informatique",
        cpv_keywords=["informatique", "logiciel", "development"],
    )
    db_session.add(bl)
    await db_session.flush()
    await db_session.refresh(bl)
    return bl


# --- AO de test ---
@pytest_asyncio.fixture
async def sample_ao(
    db_session: AsyncSession,
    tenant: Tenant,
    business_line: Any,
) -> Any:
    from app.models.ao_s2 import AO

    ao = AO(
        id=uuid.uuid4(),
        source_id=None,  # sera defini si besoin
        external_id="TEST-2024-001",
        title="AO Test — Maintenance applicative",
        description="Appel d'offres pour la maintenance d'applications web",
        status="published",
        buyer_name="Administration Test",
        cpv_codes=["72000000-5"],
        estimated_amount=150000.00,
        currency="EUR",
        deadline_date=datetime(2024, 12, 31, 23, 59, tzinfo=timezone.utc),
        raw_data={"test": True, "business_line_id": str(business_line.id)},
    )
    db_session.add(ao)
    await db_session.flush()
    await db_session.refresh(ao)
    return ao


# --- AO de test avec scoring ---
@pytest_asyncio.fixture
async def sample_ao_scored(
    db_session: AsyncSession,
    sample_ao: Any,
    authenticated_user: Dict[str, Any],
) -> Dict[str, Any]:
    from app.models.scoring import ScoringRun

    scoring = ScoringRun(
        id=uuid.uuid4(),
        ao_id=sample_ao.id,
        profile="prudent",
        score_global=78.5,
        score_coherence=85.0,
        score_financiere=72.0,
        score_geographique=80.0,
        score_temporelle=75.0,
        score_concurrentielle=70.0,
        verdict="MAYBE",
        confidence=0.85,
        details={},
    )
    db_session.add(scoring)
    await db_session.flush()
    await db_session.refresh(scoring)

    return {"ao": sample_ao, "scoring": scoring}


# --- Markers pytest ---
def pytest_configure(config: pytest.Config) -> None:
    """Enregistre les markers custom pour les tests."""
    config.addinivalue_line("markers", "slow: marque les tests lents")
    config.addinivalue_line("markers", "integration: marque les tests d'integration")
    config.addinivalue_line("markers", "migrations: marque les tests de migration")
