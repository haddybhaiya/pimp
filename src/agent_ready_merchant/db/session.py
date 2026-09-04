"""Database connection and session factory management."""

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from agent_ready_merchant.config import get_settings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Retrieves or initializes the global AsyncEngine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        db_url = settings.DATABASE_URL.get_secret_value()
        engine_kwargs: dict[str, Any] = {
            "echo": settings.DB_ECHO,
        }
        # SQLite doesn't support pool_size / max_overflow
        if "sqlite" not in db_url:
            engine_kwargs["pool_size"] = settings.DB_POOL_SIZE
            engine_kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW
            # Managed PostgreSQL providers may close idle TCP connections.  Test
            # a checked-out connection and retire it before the provider's
            # typical idle timeout instead of surfacing a transient 500.
            engine_kwargs["pool_pre_ping"] = True
            engine_kwargs["pool_recycle"] = settings.DB_POOL_RECYCLE_SECONDS

        _engine = create_async_engine(db_url, **engine_kwargs)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Retrieves or initializes the global async_sessionmaker."""
    global _session_factory
    if _session_factory is None:
        engine = get_engine()
        _session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding an isolated transaction-managed AsyncSession."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def close_db_engine() -> None:
    """Disposes the engine during application shutdown."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
