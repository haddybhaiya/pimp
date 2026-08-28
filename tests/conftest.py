"""Pytest configuration and test database fixtures."""

import os
from collections.abc import AsyncGenerator
from typing import Any

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

# Force test environment before importing application
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["DATABASE_URL_SYNC"] = "sqlite:///:memory:"
os.environ["RAZORPAY_KEY_ID"] = "rzp_test_placeholder"
os.environ["RAZORPAY_KEY_SECRET"] = "test_secret_key_placeholder"
os.environ["RAZORPAY_WEBHOOK_SECRET"] = "test_webhook_secret_12345"

import agent_ready_merchant.models  # noqa: F401 - Register models
from agent_ready_merchant.db.base import Base
from agent_ready_merchant.db.session import get_db_session
from agent_ready_merchant.main import create_app


@pytest_asyncio.fixture(scope="function")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Creates an isolated in-memory SQLite engine with foreign key enforcement."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    # Enable SQLite foreign key constraints
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    import agent_ready_merchant.db.session as db_session_module

    db_session_module._engine = engine
    db_session_module._session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    db_session_module._engine = None
    db_session_module._session_factory = None
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Yields a transactional session against the in-memory test database."""
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def session_factory(test_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Yields a session factory for creating independent sessions (concurrent tests)."""
    return async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


@pytest_asyncio.fixture(scope="function")
async def client(
    test_engine: AsyncEngine, db_session: AsyncSession
) -> AsyncGenerator[AsyncClient, None]:
    """FastAPI async test client with database dependency override."""
    app = create_app()

    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
