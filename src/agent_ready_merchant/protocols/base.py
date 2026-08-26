"""Abstract protocol adapter boundary interface.

Adheres strictly to Phase 2.3 specifications:
- External Protocol -> Protocol Adapter -> Canonical Commerce Request -> Commerce Gateway
- Protocol neutrality: replaceable adapter infrastructure
- Strict bidirectional mapping of actions, parameters, states, and errors
- Zero leakage of raw internal database records or payment provider secrets
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from agent_ready_merchant.gateway.constants import COMMERCE_PROTOCOL_VERSION
from agent_ready_merchant.gateway.schemas import (
    GatewayError,
    GatewayResponseEnvelope,
    StateOrientedContext,
)


class ProtocolRequestMessage(BaseModel):
    """Normalized wire message received from an external AI protocol."""

    model_config = ConfigDict(extra="forbid")

    protocol: str = Field(..., description="External protocol identifier (e.g. acp, jsonrpc)")
    version: str = Field(
        default=COMMERCE_PROTOCOL_VERSION,
        description="Negotiated protocol contract version",
    )
    request_id: uuid.UUID | None = Field(
        default=None,
        description="Trace identifier for request tracking and audit",
    )
    action: str = Field(..., description="Requested external protocol action")
    params: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured parameter dictionary for the action",
    )
    idempotency_key: str | None = Field(
        default=None,
        max_length=128,
        description="Client-supplied idempotency key for replay deduplication",
    )


class ProtocolResponseMessage(BaseModel):
    """Normalized wire response returned to an external AI protocol."""

    model_config = ConfigDict(extra="forbid")

    protocol: str = Field(..., description="External protocol identifier")
    version: str = Field(
        default=COMMERCE_PROTOCOL_VERSION,
        description="Negotiated protocol contract version",
    )
    request_id: uuid.UUID = Field(..., description="Trace identifier matching request")
    status: Literal["SUCCESS", "REJECTED", "ERROR"] = Field(
        ..., description="Overall execution outcome"
    )
    action: str = Field(..., description="Action that was executed")
    result: dict[str, Any] | None = Field(
        default=None,
        description="Authoritative result payload on success",
    )
    error: GatewayError | None = Field(
        default=None,
        description="Structured error details on rejection/failure",
    )
    state_context: StateOrientedContext | None = Field(
        default=None,
        description="Server-authoritative state machine context for progression",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Execution timestamp (UTC)",
    )
    audit_event_id: uuid.UUID | None = Field(
        default=None,
        description="Associated immutable audit event ID",
    )


class BaseProtocolAdapter(ABC):
    """Abstract interface defining contract between external protocols and the Commerce Gateway."""

    protocol_name: str
    supported_versions: set[str]

    @abstractmethod
    def parse_request(self, raw_input: dict[str, Any] | str | bytes) -> ProtocolRequestMessage:
        """Parses and validates raw external protocol input into a normalized message."""
        pass

    @abstractmethod
    def to_canonical_request(
        self,
        protocol_req: ProtocolRequestMessage,
    ) -> tuple[str, dict[str, Any]]:
        """Translates protocol action and params into canonical capability and payload."""
        pass

    @abstractmethod
    def from_canonical_envelope(
        self,
        capability: str,
        envelope: GatewayResponseEnvelope[Any],
        protocol_req: ProtocolRequestMessage | None = None,
    ) -> ProtocolResponseMessage:
        """Translates canonical gateway response envelope into normalized protocol response."""
        pass

    @abstractmethod
    def format_error_response(
        self,
        error_code: str,
        message: str,
        request_id: uuid.UUID,
        action: str = "unknown",
        retryable: bool = False,
        details: dict[str, Any] | None = None,
    ) -> ProtocolResponseMessage:
        """Constructs a compliant error response message."""
        pass
