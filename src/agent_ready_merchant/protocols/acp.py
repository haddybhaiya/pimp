"""Agent Commerce Protocol (ACP) Adapter implementation.

Adheres strictly to Phase 2.3 specifications:
- Minimal, clean adapter suitable for external AI buyer agents & hackathon demo
- Translates ACP protocol messages <-> Canonical Commerce requests/envelopes
- Strict schema and version validation
- Deterministic error mapping
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from agent_ready_merchant.gateway.constants import COMMERCE_PROTOCOL_VERSION
from agent_ready_merchant.gateway.schemas import (
    GatewayError,
    GatewayResponseEnvelope,
)
from agent_ready_merchant.protocols.base import (
    BaseProtocolAdapter,
    ProtocolRequestMessage,
    ProtocolResponseMessage,
)

logger = logging.getLogger("agent_ready_merchant.protocols.acp")


class AgentCommerceProtocolAdapter(BaseProtocolAdapter):
    """Concrete adapter translating Agent Commerce Protocol (ACP) wire messages."""

    protocol_name: str = "acp"
    supported_versions: set[str] = {COMMERCE_PROTOCOL_VERSION, "v1", "2026-03-01"}

    # Canonical Capability <-> Protocol Action Mapping
    ACTION_TO_CAPABILITY: dict[str, str] = {
        "discover_products": "discover_products",
        "search_catalog": "discover_products",
        "get_product": "get_product",
        "get_product_details": "get_product",
        "check_inventory": "check_inventory",
        "get_quote": "get_quote",
        "request_quote": "get_quote",
        "calculate_shipping": "calculate_shipping",
        "create_order": "create_order",
        "request_checkout": "request_checkout",
        "checkout": "request_checkout",
        "get_payment_status": "get_payment_status",
        "initialize_session": "initialize_session",
        "terminate_session": "terminate_session",
        "negotiate_quote": "negotiate_quote",
        "accept_quote": "accept_quote",
        "get_order_status": "get_order_status",
    }

    CAPABILITY_TO_ACTION: dict[str, str] = {
        "discover_products": "discover_products",
        "get_product": "get_product",
        "check_inventory": "check_inventory",
        "get_quote": "get_quote",
        "calculate_shipping": "calculate_shipping",
        "create_order": "create_order",
        "request_checkout": "request_checkout",
        "get_payment_status": "get_payment_status",
        "initialize_session": "initialize_session",
        "terminate_session": "terminate_session",
        "negotiate_quote": "negotiate_quote",
        "accept_quote": "accept_quote",
        "get_order_status": "get_order_status",
    }

    def parse_request(self, raw_input: dict[str, Any] | str | bytes) -> ProtocolRequestMessage:
        """Parses and validates raw external wire payload into a ProtocolRequestMessage."""
        if isinstance(raw_input, (bytes, str)):
            try:
                data = json.loads(raw_input)
            except Exception as exc:
                raise ValueError(f"Malformed JSON in protocol payload: {exc}") from exc
        else:
            data = raw_input

        if not isinstance(data, dict):
            raise ValueError("Protocol payload must be a JSON object")

        return ProtocolRequestMessage.model_validate(data)

    def to_canonical_request(
        self,
        protocol_req: ProtocolRequestMessage,
    ) -> tuple[str, dict[str, Any]]:
        """Translates ACP message into canonical capability name and parameter payload."""
        # 0. Protocol Validation
        if protocol_req.protocol != self.protocol_name:
            raise ValueError(
                f"Protocol mismatch: expected '{self.protocol_name}', "
                f"got '{protocol_req.protocol}'."
            )

        # 1. Version Validation
        if protocol_req.version not in self.supported_versions:
            raise ValueError(
                f"Unsupported protocol contract version '{protocol_req.version}'. "
                f"Supported versions: {sorted(self.supported_versions)}"
            )

        # 2. Action Mapping
        action = protocol_req.action
        capability = self.ACTION_TO_CAPABILITY.get(action)
        if not capability:
            raise ValueError(
                f"Unknown or unsupported ACP action '{action}'. "
                f"Supported actions: {sorted(self.ACTION_TO_CAPABILITY.keys())}"
            )

        # 3. Payload normalization
        payload = dict(protocol_req.params)

        # Propagate request-level idempotency key if not already in payload
        if protocol_req.idempotency_key and "idempotency_key" not in payload:
            payload["idempotency_key"] = protocol_req.idempotency_key

        return capability, payload

    def from_canonical_envelope(
        self,
        capability: str,
        envelope: GatewayResponseEnvelope[Any],
        protocol_req: ProtocolRequestMessage | None = None,
    ) -> ProtocolResponseMessage:
        """Translates canonical response envelope into ACP response message."""
        action = (
            protocol_req.action
            if protocol_req
            else self.CAPABILITY_TO_ACTION.get(capability, capability)
        )
        req_id = (
            protocol_req.request_id
            if protocol_req and protocol_req.request_id
            else envelope.request_id
        ) or uuid.uuid4()
        version = protocol_req.version if protocol_req else envelope.schema_version

        result_dict: dict[str, Any] | None = None
        if envelope.data is not None:
            if hasattr(envelope.data, "model_dump"):
                result_dict = envelope.data.model_dump(mode="json")
            elif isinstance(envelope.data, dict):
                result_dict = envelope.data
            else:
                result_dict = {"value": envelope.data}

        return ProtocolResponseMessage(
            protocol=self.protocol_name,
            version=version,
            request_id=req_id,
            status=envelope.status,
            action=action,
            result=result_dict,
            error=envelope.error,
            state_context=envelope.state,
            timestamp=envelope.timestamp,
            audit_event_id=envelope.audit_event_id,
        )

    def format_error_response(
        self,
        error_code: str,
        message: str,
        request_id: uuid.UUID,
        action: str = "unknown",
        retryable: bool = False,
        details: dict[str, Any] | None = None,
    ) -> ProtocolResponseMessage:
        """Constructs an ACP-compliant error response."""
        return ProtocolResponseMessage(
            protocol=self.protocol_name,
            version=COMMERCE_PROTOCOL_VERSION,
            request_id=request_id,
            status="ERROR" if retryable else "REJECTED",
            action=action,
            result=None,
            error=GatewayError(
                code=error_code,
                message=message,
                retryable=retryable,
                details=details,
            ),
            state_context=None,
            audit_event_id=None,
        )
