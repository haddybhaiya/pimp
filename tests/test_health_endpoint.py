"""Tests for application health and root metadata endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_endpoint(client: AsyncClient) -> None:
    """Verifies that the /health endpoint reports healthy status and database connectivity."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "agent-ready-merchant"
    assert data["version"] == "0.1.0"
    assert data["database_connected"] is True


@pytest.mark.asyncio
async def test_root_descriptor_endpoint(client: AsyncClient) -> None:
    """Verifies that the root / endpoint returns machine-readable platform metadata."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Agent-Ready Merchant Platform"
    assert data["status"] == "active"
    assert data["version"] == "0.1.0"
