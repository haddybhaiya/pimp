"""Shared-durable backing store for gateway hardening primitives.

Implements the multi-worker guarantees required by the Phase 2.3 hardening
review:

- **Idempotency claims** are persisted with a PRIMARY KEY uniqueness constraint,
  so the same financial mutation cannot execute twice across workers or across
  process restarts (INV-IDEM / fail-closed financial safety).
- **Rate-limit windows** are persisted as timestamp events keyed per client, so
  the configured limit is enforced globally rather than per worker.

Storage is intentionally dependency-neutral raw SQL executed over the
application's shared async engine (PostgreSQL in production, SQLite-compatible
DDL for local/test experimentation). Table names are module-owned constants —
never user input — so all statements below are static strings with bound
parameters only. Tables are created idempotently on first use and are also
declared in Alembic migration ``002_gateway_hardening_tables`` (the migration
is the canonical schema path; runtime creation exists so the opt-in flag can
never crash a deployment that missed it).
"""

from __future__ import annotations

import logging
import time

from sqlalchemy import text

from agent_ready_merchant.config import get_settings
from agent_ready_merchant.db.session import get_engine

logger = logging.getLogger("agent_ready_merchant.gateway.durable")

_IDEMPOTENCY_TABLE = "gateway_hardening_idempotency"
_RATE_EVENTS_TABLE = "gateway_hardening_rate_events"

_MAX_EVENT_AGE_SECONDS = 3600
_PRUNE_EVERY_N_CALLS = 50

_tables_ensured = False
_call_counter = 0

_Q_FETCH_COMPLETED = (
    f"SELECT state, envelope, payload_hash FROM {_IDEMPOTENCY_TABLE} "
    f"WHERE key = :key AND expires_at > :now"
)
_Q_DELETE_EXPIRED_CLAIM = (
    f"DELETE FROM {_IDEMPOTENCY_TABLE} WHERE key = :key AND expires_at <= :now"
)
_Q_INSERT_CLAIM = (
    f"INSERT INTO {_IDEMPOTENCY_TABLE} "
    f"(key, state, envelope, capability, payload_hash, created_at, expires_at) "
    f"VALUES (:key, 'IN_FLIGHT', NULL, NULL, NULL, :now, :expires) ON CONFLICT DO NOTHING"
)
_Q_UPSERT_COMPLETED = (
    f"INSERT INTO {_IDEMPOTENCY_TABLE} "
    f"(key, state, envelope, capability, payload_hash, created_at, expires_at) "
    f"VALUES (:key, 'COMPLETED', :envelope, :capability, :payload_hash, :now, :expires) "
    f"ON CONFLICT (key) DO UPDATE SET state = 'COMPLETED', envelope = :envelope, "
    f"capability = :capability, payload_hash = :payload_hash, "
    f"created_at = :now, expires_at = :expires"
)
_Q_RELEASE_CLAIM = f"DELETE FROM {_IDEMPOTENCY_TABLE} WHERE key = :key AND state = 'IN_FLIGHT'"
_Q_WINDOW_COUNT = (
    f"SELECT COUNT(*), MIN(ts) FROM {_RATE_EVENTS_TABLE} "
    f"WHERE client_key = :client_key AND ts > :cutoff"
)
_Q_INSERT_EVENT = f"INSERT INTO {_RATE_EVENTS_TABLE} (client_key, ts) VALUES (:client_key, :ts)"
_Q_PRUNE_EVENTS = f"DELETE FROM {_RATE_EVENTS_TABLE} WHERE ts < :stale"
_Q_RESET_IDEMPOTENCY = f"DELETE FROM {_IDEMPOTENCY_TABLE}"
_Q_RESET_RATE_EVENTS = f"DELETE FROM {_RATE_EVENTS_TABLE}"


def _is_sqlite() -> bool:
    return "sqlite" in get_settings().DATABASE_URL.get_secret_value().lower()


async def ensure_tables() -> None:
    """Idempotently creates the hardening tables (no-op after first success)."""
    global _tables_ensured
    if _tables_ensured:
        return

    if _is_sqlite():
        idem_pk = "TEXT PRIMARY KEY"
        rate_ddl = (
            f"CREATE TABLE IF NOT EXISTS {_RATE_EVENTS_TABLE} "
            f"(client_key TEXT NOT NULL, ts DOUBLE PRECISION NOT NULL)"
        )
    else:
        idem_pk = "VARCHAR(768) PRIMARY KEY"
        rate_ddl = (
            f"CREATE TABLE IF NOT EXISTS {_RATE_EVENTS_TABLE} "
            f"(client_key VARCHAR(768) NOT NULL, ts DOUBLE PRECISION NOT NULL)"
        )

    idem_ddl = (
        f"CREATE TABLE IF NOT EXISTS {_IDEMPOTENCY_TABLE} "
        f"(key {idem_pk}, state VARCHAR(16) NOT NULL, envelope TEXT, "
        f"capability VARCHAR(128), payload_hash VARCHAR(64), "
        f"created_at DOUBLE PRECISION NOT NULL, expires_at DOUBLE PRECISION NOT NULL)"
    )
    ix_rate = (
        f"CREATE INDEX IF NOT EXISTS ix_gwh_rate_key_ts ON {_RATE_EVENTS_TABLE} (client_key, ts)"
    )
    ix_expires = (
        f"CREATE INDEX IF NOT EXISTS ix_gwh_idem_expires ON {_IDEMPOTENCY_TABLE} (expires_at)"
    )

    async with get_engine().begin() as conn:
        await conn.execute(text(idem_ddl))
        await conn.execute(text(rate_ddl))
        await conn.execute(text(ix_rate))
        await conn.execute(text(ix_expires))

    _tables_ensured = True
    logger.info("Gateway hardening durable tables ensured")


# =============================================================================
# Idempotency claims (durable, cross-worker atomic)
# =============================================================================
async def fetch_completed(key: str) -> tuple[str, str | None] | None:
    """Returns cached response envelope JSON and payload hash for a completed claim, else None."""
    await ensure_tables()
    now = time.time()
    async with get_engine().connect() as conn:
        row = (await conn.execute(text(_Q_FETCH_COMPLETED), {"key": key, "now": now})).first()
    if row is None or row.state != "COMPLETED" or row.envelope is None:
        return None
    envelope: str = row.envelope
    payload_hash: str | None = getattr(row, "payload_hash", None)
    return envelope, payload_hash


async def claim(key: str, ttl_seconds: int) -> bool:
    """Atomically claims an in-flight mutation slot; False if already claimed/completed."""
    await ensure_tables()
    now = time.time()
    async with get_engine().begin() as conn:
        await conn.execute(
            text(_Q_DELETE_EXPIRED_CLAIM),
            {"key": key, "now": now},
        )
        result = await conn.execute(
            text(_Q_INSERT_CLAIM),
            {"key": key, "now": now, "expires": now + ttl_seconds},
        )
    claimed = bool(result.rowcount == 1)
    if not claimed:
        logger.info("Durable idempotency claim rejected duplicate for key '%s'", key)
    return claimed


async def complete(
    key: str,
    envelope_json: str,
    ttl_seconds: int,
    capability: str,
    payload_hash: str | None = None,
) -> None:
    """Persists the final response and payload hash for a claimed mutation key."""
    await ensure_tables()
    now = time.time()
    async with get_engine().begin() as conn:
        await conn.execute(
            text(_Q_UPSERT_COMPLETED),
            {
                "key": key,
                "envelope": envelope_json,
                "capability": capability[:128],
                "payload_hash": payload_hash,
                "now": now,
                "expires": now + ttl_seconds,
            },
        )


async def release(key: str) -> None:
    """Deletes an in-flight claim marker (failure/timeout path)."""
    await ensure_tables()
    async with get_engine().begin() as conn:
        await conn.execute(text(_Q_RELEASE_CLAIM), {"key": key})


# =============================================================================
# Rate limiting (shared sliding window)
# =============================================================================
async def rate_check_and_hit(client_key: str, limit: int, window_seconds: int) -> tuple[bool, int]:
    """Shared sliding-window check; records the hit when allowed.

    Returns (is_allowed, retry_after_seconds).
    """
    global _call_counter
    await ensure_tables()
    now = time.time()
    cutoff = now - window_seconds

    async with get_engine().begin() as conn:
        row = (
            await conn.execute(text(_Q_WINDOW_COUNT), {"client_key": client_key, "cutoff": cutoff})
        ).first()

        if row is None or row[0] is None:
            count, oldest = 0, now
        else:
            count, oldest_ts = int(row[0]), row[1]
            oldest = float(oldest_ts) if oldest_ts is not None else now

        if count >= limit:
            retry_after = max(1, int(window_seconds - (now - oldest)))
            logger.warning(
                "Durable rate limit exceeded for '%s': %d requests in %ds window",
                client_key,
                count,
                window_seconds,
            )
            return False, retry_after

        await conn.execute(text(_Q_INSERT_EVENT), {"client_key": client_key, "ts": now})

        _call_counter += 1
        if _call_counter % _PRUNE_EVERY_N_CALLS == 0:
            await conn.execute(
                text(_Q_PRUNE_EVENTS),
                {"stale": time.time() - _MAX_EVENT_AGE_SECONDS},
            )

    return True, 0


async def reset_all() -> None:
    """Clears both durable tables (used in testing)."""
    await ensure_tables()
    async with get_engine().begin() as conn:
        await conn.execute(text(_Q_RESET_IDEMPOTENCY))
        await conn.execute(text(_Q_RESET_RATE_EVENTS))


def durable_enabled() -> bool:
    """Whether opt-in durable hardening mode is active for this process."""
    setting: bool = bool(getattr(get_settings(), "GATEWAY_DURABLE_HARDENING", False))
    return setting
