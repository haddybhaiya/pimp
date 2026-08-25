"""Production-grade hardening utilities for the Canonical Commerce Gateway.

Adheres strictly to Phase 2.3 specifications and INV-AGY-03 (Zero Secret Leakage):
- Deterministic hierarchical error codes
- Thread-safe idempotency coordinator for mutation deduplication
- Sliding-window rate limiter with retry-after guidance
- Bounded payload size guards (max 64 KB)
- Timeout boundary guards
- Structured observability logging
- Safe error sanitization preventing internal exception leakage
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from agent_ready_merchant.gateway.constants import (
    COMMERCE_PROTOCOL_VERSION,
    DEFAULT_MAX_PAYLOAD_BYTES,
)
from agent_ready_merchant.gateway.schemas import (
    GatewayError,
    GatewayResponseEnvelope,
)

logger = logging.getLogger("agent_ready_merchant.gateway.hardening")


# =============================================================================
# 1. Deterministic Hierarchical Error Codes
# =============================================================================
class GatewayErrorCode(StrEnum):
    """Standardized deterministic machine-readable error codes."""

    # Authorization & Security
    AUTH_UNAUTHORIZED_CAPABILITY = "AUTH_UNAUTHORIZED_CAPABILITY"
    AUTH_SESSION_EXPIRED = "AUTH_SESSION_EXPIRED"
    AUTH_SESSION_NOT_FOUND = "AUTH_SESSION_NOT_FOUND"
    AUTH_INVALID_MERCHANT = "AUTH_INVALID_MERCHANT"
    AUTH_FORBIDDEN_RESOURCE = "AUTH_FORBIDDEN_RESOURCE"

    # Commerce Domain & Entity Errors
    COMMERCE_PRODUCT_NOT_FOUND = "COMMERCE_PRODUCT_NOT_FOUND"
    COMMERCE_PRODUCT_INACTIVE = "COMMERCE_PRODUCT_INACTIVE"
    COMMERCE_INSUFFICIENT_STOCK = "COMMERCE_INSUFFICIENT_STOCK"
    COMMERCE_QUOTE_NOT_FOUND = "COMMERCE_QUOTE_NOT_FOUND"
    COMMERCE_QUOTE_EXPIRED = "COMMERCE_QUOTE_EXPIRED"
    COMMERCE_QUOTE_ALREADY_ACCEPTED = "COMMERCE_QUOTE_ALREADY_ACCEPTED"
    COMMERCE_ORDER_NOT_FOUND = "COMMERCE_ORDER_NOT_FOUND"
    COMMERCE_ORDER_ALREADY_PAID = "COMMERCE_ORDER_ALREADY_PAID"
    COMMERCE_PAYMENT_GATEWAY_ERROR = "COMMERCE_PAYMENT_GATEWAY_ERROR"

    # Policy & Governance
    POLICY_FLOOR_PRICE_BREACH = "POLICY_FLOOR_PRICE_BREACH"
    POLICY_MAX_DISCOUNT_EXCEEDED = "POLICY_MAX_DISCOUNT_EXCEEDED"
    POLICY_NON_NEGOTIABLE = "POLICY_NON_NEGOTIABLE"
    POLICY_REJECTED = "POLICY_REJECTED"
    POLICY_ESCALATED = "POLICY_ESCALATED"

    # Gateway Infrastructure & Operational Safety
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    PAYLOAD_SIZE_EXCEEDED = "PAYLOAD_SIZE_EXCEEDED"
    TIMEOUT_BOUNDARY_EXCEEDED = "TIMEOUT_BOUNDARY_EXCEEDED"
    IDEMPOTENCY_CONFLICT = "IDEMPOTENCY_CONFLICT"
    IDEMPOTENCY_REQUIRED = "IDEMPOTENCY_REQUIRED"
    AMBIGUOUS_SKU = "AMBIGUOUS_SKU"
    MAX_ACTIVE_QUOTES_EXCEEDED = "MAX_ACTIVE_QUOTES_EXCEEDED"
    MALFORMED_REQUEST_SCHEMA = "MALFORMED_REQUEST_SCHEMA"
    UNSUPPORTED_PROTOCOL_VERSION = "UNSUPPORTED_PROTOCOL_VERSION"
    UNKNOWN_CAPABILITY = "UNKNOWN_CAPABILITY"
    INTERNAL_GATEWAY_ERROR = "INTERNAL_GATEWAY_ERROR"


# =============================================================================
# 2. Thread-Safe Idempotency Coordinator
# =============================================================================
@dataclass
class IdempotencyRecord:
    """Cached idempotent response record with execution metadata."""

    envelope: GatewayResponseEnvelope[Any]
    merchant_id: uuid.UUID
    capability: str = "unknown"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class IdempotencyManager:
    """In-memory coordinator ensuring mutating operations execute exactly once.

    Prevents race conditions, double reservations, and duplicate charges.
    Note: This is a process-local implementation bounded by LRU/TTL eviction.
    In a distributed multi-worker cluster, this coordinator should be backed by
    a shared Redis/PostgreSQL distributed locking table.
    """

    def __init__(self, ttl_seconds: int = 86400, max_entries: int = 10_000) -> None:
        self._ttl_seconds = ttl_seconds
        self._max_entries = max_entries
        self._cache: dict[str, IdempotencyRecord] = {}
        self._in_flight: set[str] = set()
        self._lock = asyncio.Lock()

    def _build_key(
        self,
        merchant_id: uuid.UUID,
        session_id: uuid.UUID | None,
        idempotency_key: str,
        capability: str | None = None,
    ) -> str:
        s_part = str(session_id) if session_id else "global"
        c_part = capability or "any"
        return f"{merchant_id}:{s_part}:{c_part}:{idempotency_key}"

    async def check_idempotency(
        self,
        merchant_id: uuid.UUID,
        session_id: uuid.UUID | None,
        idempotency_key: str | None,
        capability: str | None = None,
    ) -> GatewayResponseEnvelope[Any] | None:
        """Checks if a cached result exists for the given idempotency key."""
        if not idempotency_key:
            return None

        key = self._build_key(merchant_id, session_id, idempotency_key, capability)
        async with self._lock:
            record = self._cache.get(key)
            if not record:
                return None

            now = datetime.now(UTC)
            age = (now - record.created_at).total_seconds()
            if age > self._ttl_seconds:
                del self._cache[key]
                return None

            logger.info("Idempotency hit for key '%s'", idempotency_key)
            return record.envelope

    async def acquire_mutation_lock(
        self,
        merchant_id: uuid.UUID,
        session_id: uuid.UUID | None,
        idempotency_key: str | None,
        capability: str | None = None,
    ) -> bool:
        """Acquires lock for in-flight mutation; returns False if concurrent duplicate in-flight."""
        if not idempotency_key:
            return True

        key = self._build_key(merchant_id, session_id, idempotency_key, capability)
        async with self._lock:
            if key in self._in_flight:
                return False
            self._in_flight.add(key)
            return True

    async def release_mutation_lock(
        self,
        merchant_id: uuid.UUID,
        session_id: uuid.UUID | None,
        idempotency_key: str | None,
        capability: str | None = None,
    ) -> None:
        """Releases the in-flight mutation lock."""
        if not idempotency_key:
            return

        key = self._build_key(merchant_id, session_id, idempotency_key, capability)
        async with self._lock:
            self._in_flight.discard(key)

    async def record_idempotency(
        self,
        merchant_id: uuid.UUID,
        session_id: uuid.UUID | None,
        idempotency_key: str | None,
        envelope: GatewayResponseEnvelope[Any],
        capability: str | None = None,
    ) -> None:
        """Caches the final response envelope for an idempotency key with bounded eviction."""
        if not idempotency_key:
            return

        key = self._build_key(merchant_id, session_id, idempotency_key, capability)
        async with self._lock:
            now = datetime.now(UTC)
            # Evict if capacity reached
            if len(self._cache) >= self._max_entries:
                expired_keys = [
                    k
                    for k, r in self._cache.items()
                    if (now - r.created_at).total_seconds() > self._ttl_seconds
                ]
                for k in expired_keys:
                    del self._cache[k]
                # If still over capacity, evict oldest entries
                if len(self._cache) >= self._max_entries:
                    sorted_keys = sorted(
                        self._cache.keys(), key=lambda k: self._cache[k].created_at
                    )
                    for k in sorted_keys[: len(self._cache) // 10]:
                        del self._cache[k]

            self._cache[key] = IdempotencyRecord(
                envelope=envelope,
                merchant_id=merchant_id,
                capability=capability or "unknown",
                created_at=now,
            )
            self._in_flight.discard(key)
            logger.debug("Cached idempotency record for '%s'", idempotency_key)

    def reset(self) -> None:
        """Clears all cached idempotency keys (used in testing)."""
        self._cache.clear()
        self._in_flight.clear()


# Global shared singleton idempotency manager
global_idempotency_manager = IdempotencyManager()


# =============================================================================
# 3. Sliding-Window Rate Limiter
# =============================================================================
class GatewayRateLimiter:
    """In-memory sliding-window rate limiter per session or client identifier.

    Note: This is a process-local limiter. In a distributed multi-worker cluster,
    this should be backed by Redis sliding-window zset counters.
    """

    def __init__(self, max_clients: int = 10_000) -> None:
        self._max_clients = max_clients
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def check_rate_limit(
        self,
        client_key: str,
        limit: int = 60,
        window_seconds: int = 60,
    ) -> tuple[bool, int]:
        """Checks rate limit. Returns (is_allowed, retry_after_seconds)."""
        now = time.time()
        cutoff = now - window_seconds

        async with self._lock:
            # Capacity guard: prune dead keys if map is full
            if len(self._requests) >= self._max_clients and client_key not in self._requests:
                dead_keys = [
                    k for k, ts in self._requests.items() if not [t for t in ts if t > cutoff]
                ]
                for k in dead_keys:
                    del self._requests[k]
                if len(self._requests) >= self._max_clients:
                    # Evict oldest 10%
                    oldest_keys = list(self._requests.keys())[: len(self._requests) // 10]
                    for k in oldest_keys:
                        del self._requests[k]

            timestamps = self._requests[client_key]
            # Prune old timestamps
            active_timestamps = [t for t in timestamps if t > cutoff]

            if not active_timestamps:
                if client_key in self._requests:
                    del self._requests[client_key]
            else:
                self._requests[client_key] = active_timestamps

            if len(self._requests.get(client_key, [])) >= limit:
                oldest = self._requests[client_key][0]
                retry_after = max(1, int(window_seconds - (now - oldest)))
                logger.warning(
                    "Rate limit exceeded for '%s': %d requests in %ds window (retry in %ds)",
                    client_key,
                    len(self._requests[client_key]),
                    window_seconds,
                    retry_after,
                )
                return False, retry_after

            if client_key not in self._requests:
                self._requests[client_key] = []
            self._requests[client_key].append(now)
            return True, 0

    def reset(self) -> None:
        """Resets all recorded rate limit windows (used in testing)."""
        self._requests.clear()


# Global shared singleton rate limiter
global_rate_limiter = GatewayRateLimiter()


# =============================================================================
# 4. Bounded Payload Size Validator
# =============================================================================
def validate_payload_size(
    payload: dict[str, Any] | str | bytes,
    max_bytes: int = DEFAULT_MAX_PAYLOAD_BYTES,
) -> tuple[bool, int]:
    """Validates that a request payload does not exceed the maximum allowed size.

    Returns (is_valid, size_in_bytes).
    """
    if isinstance(payload, bytes):
        size = len(payload)
    elif isinstance(payload, str):
        size = len(payload.encode("utf-8"))
    elif isinstance(payload, dict):
        try:
            size = len(json.dumps(payload).encode("utf-8"))
        except Exception:
            size = 0
    else:
        size = 0

    if size > max_bytes:
        logger.warning(
            "Payload size %d bytes exceeded bounded limit of %d bytes",
            size,
            max_bytes,
        )
        return False, size

    return True, size


# =============================================================================
# 5. Safe Error Sanitization
# =============================================================================
def sanitize_error_response(
    capability: str,
    exc: Exception,
    request_id: uuid.UUID,
    is_testing: bool = False,
) -> GatewayResponseEnvelope[Any]:
    """Generates a safe error envelope with zero internal stack traces or credential leaks.

    Full traceback is logged to secure server-side logging.
    """
    logger.error(
        "Internal exception during gateway execution of '%s' (request_id=%s): %s",
        capability,
        request_id,
        exc,
        exc_info=True,
    )

    safe_message = (
        f"Gateway error during '{capability}': {exc}"
        if is_testing
        else f"An internal error occurred during '{capability}'. Reference Request-ID: {request_id}"
    )

    return GatewayResponseEnvelope[Any](
        status="ERROR",
        capability=capability,
        data=None,
        error=GatewayError(
            code=GatewayErrorCode.INTERNAL_GATEWAY_ERROR.value,
            message=safe_message,
            retryable=False,
            details={"request_id": str(request_id)},
        ),
        request_id=request_id,
        schema_version=COMMERCE_PROTOCOL_VERSION,
    )
