"""Tests for the shared durable hardening backend (multi-worker safety).

Verifies that with ``GATEWAY_DURABLE_HARDENING`` enabled:
- idempotency claims are atomic across repeated acquire attempts (exactly-once),
- completed responses are replayed for duplicate keys,
- the sliding-window limiter enforces the limit across repeated checks.

The durable module targets a file-backed SQLite database here so all
connections observe the same tables (mirrors cross-process PostgreSQL usage).
"""

import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from agent_ready_merchant.config import get_settings
from agent_ready_merchant.gateway import durable
from agent_ready_merchant.gateway.hardening import (
    GatewayRateLimiter,
    IdempotencyManager,
)
from agent_ready_merchant.gateway.schemas import GatewayResponseEnvelope


@pytest.fixture()
def durable_sqlite(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    db_path = tmp_path / "hardening_durable.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    get_settings.cache_clear()
    durable._tables_ensured = False
    yield
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_durable_idempotency_exactly_once(durable_sqlite: None) -> None:
    """Second claim on the same key must be rejected; completed response replays."""
    manager = IdempotencyManager(ttl_seconds=300)
    merchant_id = uuid.uuid4()
    session_id = uuid.uuid4()

    key_args = (merchant_id, session_id, "retry-key-1", "create_order")

    assert await manager.check_idempotency(*key_args[:3], key_args[3]) is None

    assert await manager.acquire_mutation_lock(*key_args) is True
    assert await manager.acquire_mutation_lock(*key_args) is False

    envelope = GatewayResponseEnvelope[dict[str, Any]](
        status="SUCCESS",
        capability="create_order",
        data={"order_id": "ord_123"},
    )
    await manager.record_idempotency(*key_args[:3], envelope, key_args[3])

    replayed = await manager.check_idempotency(*key_args[:3], key_args[3])
    assert replayed is not None
    assert replayed.status == "SUCCESS"

    await manager.release_mutation_lock(*key_args[:3], key_args[3])


@pytest.mark.asyncio
async def test_durable_idempotency_payload_mismatch_rejection(durable_sqlite: None) -> None:
    """Replaying an idempotency key with a changed payload in durable mode
    must return IDEMPOTENCY_CONFLICT.
    """
    manager = IdempotencyManager(ttl_seconds=300)
    merchant_id = uuid.uuid4()
    session_id = uuid.uuid4()

    key_args = (merchant_id, session_id, "retry-payload-key-1", "create_order")
    payload1 = {"sku": "SHOE-1", "quantity": 1}
    payload2 = {"sku": "SHOE-1", "quantity": 2}

    assert await manager.acquire_mutation_lock(*key_args) is True

    envelope = GatewayResponseEnvelope[dict[str, Any]](
        status="SUCCESS",
        capability="create_order",
        data={"order_id": "ord_123"},
    )
    await manager.record_idempotency(*key_args[:3], envelope, key_args[3], payload=payload1)

    # Replay with same payload -> Success
    replayed = await manager.check_idempotency(*key_args[:3], key_args[3], payload=payload1)
    assert replayed is not None
    assert replayed.status == "SUCCESS"

    # Replay with modified payload -> IDEMPOTENCY_CONFLICT
    conflict = await manager.check_idempotency(*key_args[:3], key_args[3], payload=payload2)
    assert conflict is not None
    assert conflict.status == "REJECTED"
    assert conflict.error is not None
    assert conflict.error.code == "IDEMPOTENCY_CONFLICT"

    await manager.release_mutation_lock(*key_args[:3], key_args[3])


@pytest.mark.asyncio
async def test_durable_rate_limit_shared_window(durable_sqlite: None) -> None:
    """Limit is enforced globally across repeated check calls (simulated workers)."""
    limiter = GatewayRateLimiter()
    client_key = f"worker-{uuid.uuid4()}"

    results = [
        await limiter.check_rate_limit(client_key, limit=3, window_seconds=60) for _ in range(5)
    ]

    assert results[:3] == [(True, 0), (True, 0), (True, 0)]
    assert results[3][0] is False and results[4][0] is False
    assert results[3][1] >= 1


@pytest.mark.asyncio
async def test_in_memory_fallback_when_flag_off() -> None:
    """Without the flag, behavior remains the bounded process-local implementation."""
    assert durable.durable_enabled() is False
    manager = IdempotencyManager(ttl_seconds=300)
    args = (uuid.uuid4(), uuid.uuid4(), "local-key", "get_quote")
    assert await manager.acquire_mutation_lock(*args) is True
    assert await manager.acquire_mutation_lock(*args) is False
