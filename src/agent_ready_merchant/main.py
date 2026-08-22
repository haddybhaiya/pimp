"""FastAPI application bootstrap and health endpoints.

Establishes the deterministic application lifecycle for the Agent-Ready Merchant platform.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

import agent_ready_merchant
from agent_ready_merchant.config import Settings, get_settings
from agent_ready_merchant.db.session import close_db_engine, get_db_session, get_engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application startup and graceful shutdown lifecycle."""
    settings = get_settings()
    # Eagerly initialize the database engine
    engine = get_engine()

    # In non-test environments, perform connectivity check
    if not settings.is_testing:
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
        except Exception as exc:
            # We allow startup in dev mode if DB is not immediately reachable
            import logging

            logging.getLogger("agent_ready_merchant").warning("Initial DB check failed: %s", exc)

    yield

    # Clean up engine connection pools
    await close_db_engine()


def create_app() -> FastAPI:
    """Factory creating configured FastAPI application instance."""
    settings = get_settings()

    app = FastAPI(
        title="Agent-Ready Merchant Platform",
        description="Autonomous AI Commerce Control Plane on Razorpay Infrastructure",
        version=agent_ready_merchant.__version__,
        lifespan=lifespan,
        debug=settings.DEBUG,
    )

    @app.get(
        "/health",
        summary="Service Health Check",
        tags=["System"],
        status_code=status.HTTP_200_OK,
    )
    async def health_check(
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> dict[str, Any]:
        """Health check endpoint verifying application runtime and database connectivity."""
        db_healthy = False
        try:
            result = await db.execute(text("SELECT 1"))
            db_healthy = result.scalar() == 1
        except Exception:
            db_healthy = False

        return {
            "status": "healthy" if db_healthy else "degraded",
            "service": "agent-ready-merchant",
            "version": agent_ready_merchant.__version__,
            "environment": current_settings.ENVIRONMENT,
            "database_connected": db_healthy,
        }

    @app.get(
        "/",
        summary="Platform Root Descriptor",
        tags=["System"],
        status_code=status.HTTP_200_OK,
    )
    async def root_descriptor(
        current_settings: Settings = Depends(get_settings),
    ) -> dict[str, Any]:
        """Returns machine-readable platform metadata."""
        return {
            "name": "Agent-Ready Merchant Platform",
            "version": agent_ready_merchant.__version__,
            "status": "active",
            "docs_url": "/docs",
            "environment": current_settings.ENVIRONMENT,
        }

    return app


app = create_app()
