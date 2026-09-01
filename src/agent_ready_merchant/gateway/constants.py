"""Canonical Protocol and Gateway Constants.

Backward-compatibility re-export module. The authoritative definitions live in
``agent_ready_merchant.constants`` (dependency-neutral: importing them must not
execute the ``gateway`` package ``__init__``, which pulls in the full gateway
graph and creates a circular import with ``tools.base``).
"""

from agent_ready_merchant.constants import (
    COMMERCE_PROTOCOL_VERSION,
    DEFAULT_MAX_PAYLOAD_BYTES,
    MAX_64BIT_INT,
    MIN_64BIT_INT,
    PLATFORM_MAX_SINGLE_TRANSACTION_PAISE,
)

__all__ = [
    "COMMERCE_PROTOCOL_VERSION",
    "DEFAULT_MAX_PAYLOAD_BYTES",
    "MAX_64BIT_INT",
    "MIN_64BIT_INT",
    "PLATFORM_MAX_SINGLE_TRANSACTION_PAISE",
]
