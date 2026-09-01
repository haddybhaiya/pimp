"""Dependency-neutral protocol and gateway constants.

This module MUST remain import-free (stdlib only, no package imports) so that
low-level modules such as ``agent_ready_merchant.tools.base`` can consume it
without triggering the ``gateway`` package ``__init__`` (which eagerly imports
the canonical gateway and creates a circular import).
"""

COMMERCE_PROTOCOL_VERSION: str = "2026-03-01"
DEFAULT_MAX_PAYLOAD_BYTES: int = 65_536  # 64 KB bounded payload limit
MAX_64BIT_INT: int = 9_223_372_036_854_775_807
MIN_64BIT_INT: int = -9_223_372_036_854_775_808
# This is a platform governance ceiling, not a merchant-configurable default.
PLATFORM_MAX_SINGLE_TRANSACTION_PAISE: int = 10_000_000
