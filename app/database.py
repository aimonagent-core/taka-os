# File: app/database.py
# Purpose: Async SQLAlchemy engine, session maker, and DB utilities
# Dependencies: app.config.settings, sqlalchemy.ext.asyncio, pgvector.sqlalchemy

from typing import AsyncGenerator

from pgvector.sqlalchemy import Vector
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app.config import settings

async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async DB session and rollback on exception."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Enable pgvector extension.

    NOTE: Les tables sont creees et gerees exclusivement par Alembic.
    Ne JAMAIS utiliser Base.metadata.create_all() en production.
    """
    async with async_engine.begin() as conn:
        from sqlalchemy import text
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
