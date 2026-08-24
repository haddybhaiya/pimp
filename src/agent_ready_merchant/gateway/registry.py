"""Canonical Capability Registry for the Commerce Gateway.

Adheres strictly to Phase 2.1 & Phase 2.2 specifications:
- Full capability metadata declaration (schemas, classification, side-effects, etc.)
- Strict Pydantic models with extra="forbid"
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from agent_ready_merchant.gateway.schemas import (
    AcceptQuoteGatewayRequest,
    AcceptQuoteGatewayResponse,
    CalculateShippingRequest,
    CalculateShippingResponse,
    CheckInventoryRequest,
    CheckInventoryResponse,
    CreateOrderGatewayRequest,
    CreateOrderGatewayResponse,
    DiscoverProductsRequest,
    DiscoverProductsResponse,
    GetOrderStatusRequest,
    GetOrderStatusResponse,
    GetPaymentStatusRequest,
    GetPaymentStatusResponse,
    GetProductRequest,
    GetProductResponse,
    GetQuoteRequest,
    GetQuoteResponse,
    InitializeSessionRequest,
    InitializeSessionResponse,
    NegotiateQuoteGatewayRequest,
    NegotiateQuoteGatewayResponse,
    RequestCheckoutRequest,
    RequestCheckoutResponse,
    TerminateSessionRequest,
    TerminateSessionResponse,
)
from agent_ready_merchant.tools.base import GatewayContext


class CapabilityDefinition(BaseModel):
    """Authoritative declaration of an exposed commerce gateway capability."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Canonical capability identifier")
    description: str = Field(..., description="Capability functional description")
    input_schema_name: str = Field(..., description="Name of the input Pydantic schema")
    output_schema_name: str = Field(..., description="Name of the output Pydantic schema")
    input_schema: dict[str, Any] = Field(..., description="JSON schema specification for input")
    output_schema: dict[str, Any] = Field(..., description="JSON schema specification for output")
    classification: Literal["READ_ONLY", "TRANSIENT_STATE", "PRIVILEGED_FINANCIAL"] = Field(
        ..., description="Side-effect classification"
    )
    side_effects: list[str] = Field(..., description="List of side-effects caused by execution")
    monetary_impact: bool = Field(
        ..., description="Whether capability involves financial computation or movement"
    )
    required_capability: str = Field(..., description="Security capability required to execute")
    approval_requirement: str = Field(
        ..., description="Human or supervisor approval conditions if applicable"
    )
    idempotency_requirement: bool = Field(
        ..., description="Whether requests require idempotency key or deterministic deduplication"
    )
    failure_states: list[str] = Field(..., description="Declared failure outcome codes")


class CapabilityRegistry:
    """Central registry and catalog for all canonical merchant gateway capabilities."""

    _CAPABILITIES: dict[str, CapabilityDefinition] = {
        "initialize_session": CapabilityDefinition(
            name="initialize_session",
            description="Initialize an authoritative buyer agent session with the merchant.",
            input_schema_name="InitializeSessionRequest",
            output_schema_name="InitializeSessionResponse",
            input_schema=InitializeSessionRequest.model_json_schema(),
            output_schema=InitializeSessionResponse.model_json_schema(),
            classification="TRANSIENT_STATE",
            side_effects=["creates_buyer_session", "appends_audit_event"],
            monetary_impact=False,
            required_capability="buyer:discover",
            approval_requirement="NONE",
            idempotency_requirement=False,
            failure_states=["INVALID_MERCHANT", "UNAUTHORIZED"],
        ),
        "terminate_session": CapabilityDefinition(
            name="terminate_session",
            description="Terminate an active buyer agent session with the merchant.",
            input_schema_name="TerminateSessionRequest",
            output_schema_name="TerminateSessionResponse",
            input_schema=TerminateSessionRequest.model_json_schema(),
            output_schema=TerminateSessionResponse.model_json_schema(),
            classification="TRANSIENT_STATE",
            side_effects=["terminates_buyer_session", "appends_audit_event"],
            monetary_impact=False,
            required_capability="buyer:discover",
            approval_requirement="NONE",
            idempotency_requirement=False,
            failure_states=["SESSION_NOT_FOUND", "UNAUTHORIZED"],
        ),
        "discover_products": CapabilityDefinition(
            name="discover_products",
            description="Search and filter catalog products by query, category, and price.",
            input_schema_name="DiscoverProductsRequest",
            output_schema_name="DiscoverProductsResponse",
            input_schema=DiscoverProductsRequest.model_json_schema(),
            output_schema=DiscoverProductsResponse.model_json_schema(),
            classification="READ_ONLY",
            side_effects=["none"],
            monetary_impact=False,
            required_capability="buyer:discover",
            approval_requirement="NONE",
            idempotency_requirement=False,
            failure_states=["INVALID_FILTER", "RATE_LIMIT_EXCEEDED", "UNAUTHORIZED"],
        ),
        "get_product": CapabilityDefinition(
            name="get_product",
            description="Retrieve product specifications, attributes, pricing, and variants.",
            input_schema_name="GetProductRequest",
            output_schema_name="GetProductResponse",
            input_schema=GetProductRequest.model_json_schema(),
            output_schema=GetProductResponse.model_json_schema(),
            classification="READ_ONLY",
            side_effects=["none"],
            monetary_impact=False,
            required_capability="buyer:read",
            approval_requirement="NONE",
            idempotency_requirement=False,
            failure_states=["PRODUCT_NOT_FOUND", "PRODUCT_INACTIVE", "UNAUTHORIZED"],
        ),
        "check_inventory": CapabilityDefinition(
            name="check_inventory",
            description="Verify real-time stock levels and unreserved inventory quantities.",
            input_schema_name="CheckInventoryRequest",
            output_schema_name="CheckInventoryResponse",
            input_schema=CheckInventoryRequest.model_json_schema(),
            output_schema=CheckInventoryResponse.model_json_schema(),
            classification="READ_ONLY",
            side_effects=["none"],
            monetary_impact=False,
            required_capability="buyer:read",
            approval_requirement="NONE",
            idempotency_requirement=False,
            failure_states=["SKU_NOT_FOUND", "INSUFFICIENT_STOCK", "UNAUTHORIZED"],
        ),
        "get_quote": CapabilityDefinition(
            name="get_quote",
            description="Request a binding, time-limited price quote with deterministic pricing.",
            input_schema_name="GetQuoteRequest",
            output_schema_name="GetQuoteResponse",
            input_schema=GetQuoteRequest.model_json_schema(),
            output_schema=GetQuoteResponse.model_json_schema(),
            classification="TRANSIENT_STATE",
            side_effects=["creates_transient_price_quote", "appends_audit_event"],
            monetary_impact=True,
            required_capability="buyer:quote",
            approval_requirement="NONE_FOR_BASE_PRICE_ESCALATE_FOR_OFF_POLICY_DISCOUNT",
            idempotency_requirement=True,
            failure_states=[
                "SESSION_NOT_FOUND",
                "SKU_NOT_FOUND",
                "INSUFFICIENT_STOCK",
                "QUOTE_EXPIRED",
                "FLOOR_PRICE_BREACH",
                "MAX_DISCOUNT_EXCEEDED",
                "UNAUTHORIZED",
            ],
        ),
        "negotiate_quote": CapabilityDefinition(
            name="negotiate_quote",
            description="Submit a counter-offer against an active PriceQuote for evaluation.",
            input_schema_name="NegotiateQuoteGatewayRequest",
            output_schema_name="NegotiateQuoteGatewayResponse",
            input_schema=NegotiateQuoteGatewayRequest.model_json_schema(),
            output_schema=NegotiateQuoteGatewayResponse.model_json_schema(),
            classification="TRANSIENT_STATE",
            side_effects=["transitions_quote_state", "appends_audit_event"],
            monetary_impact=True,
            required_capability="buyer:negotiate",
            approval_requirement="ESCALATE_IF_EXCEEDS_DISCOUNT_OR_BELOW_MARGIN",
            idempotency_requirement=True,
            failure_states=[
                "QUOTE_NOT_FOUND",
                "QUOTE_EXPIRED",
                "FLOOR_PRICE_BREACH",
                "MAX_DISCOUNT_EXCEEDED",
                "POLICY_REJECTED",
                "UNAUTHORIZED",
            ],
        ),
        "accept_quote": CapabilityDefinition(
            name="accept_quote",
            description="Accept an active proposed PriceQuote to prepare for checkout.",
            input_schema_name="AcceptQuoteGatewayRequest",
            output_schema_name="AcceptQuoteGatewayResponse",
            input_schema=AcceptQuoteGatewayRequest.model_json_schema(),
            output_schema=AcceptQuoteGatewayResponse.model_json_schema(),
            classification="TRANSIENT_STATE",
            side_effects=["transitions_quote_state", "appends_audit_event"],
            monetary_impact=True,
            required_capability="buyer:quote",
            approval_requirement="NONE",
            idempotency_requirement=True,
            failure_states=[
                "QUOTE_NOT_FOUND",
                "QUOTE_EXPIRED",
                "INVALID_STATE_TRANSITION",
                "UNAUTHORIZED",
            ],
        ),
        "calculate_shipping": CapabilityDefinition(
            name="calculate_shipping",
            description="Compute logistics shipping fees and free shipping eligibility.",
            input_schema_name="CalculateShippingRequest",
            output_schema_name="CalculateShippingResponse",
            input_schema=CalculateShippingRequest.model_json_schema(),
            output_schema=CalculateShippingResponse.model_json_schema(),
            classification="READ_ONLY",
            side_effects=["none"],
            monetary_impact=True,
            required_capability="buyer:discover",
            approval_requirement="NONE",
            idempotency_requirement=False,
            failure_states=["UNSUPPORTED_COUNTRY", "INVALID_POSTAL_CODE", "UNAUTHORIZED"],
        ),
        "create_order": CapabilityDefinition(
            name="create_order",
            description="Convert accepted quote to Order, reserve stock, and initialize payment.",
            input_schema_name="CreateOrderGatewayRequest",
            output_schema_name="CreateOrderGatewayResponse",
            input_schema=CreateOrderGatewayRequest.model_json_schema(),
            output_schema=CreateOrderGatewayResponse.model_json_schema(),
            classification="PRIVILEGED_FINANCIAL",
            side_effects=[
                "atomically_reserves_inventory",
                "creates_local_order_record",
                "creates_razorpay_external_order",
                "appends_audit_event",
            ],
            monetary_impact=True,
            required_capability="buyer:checkout",
            approval_requirement="AUTOMATIC_IF_QUOTE_ACCEPTED",
            idempotency_requirement=True,
            failure_states=[
                "QUOTE_NOT_FOUND",
                "QUOTE_NOT_ACCEPTED",
                "QUOTE_EXPIRED",
                "INSUFFICIENT_STOCK",
                "CROSS_SESSION_FORBIDDEN",
                "PAYMENT_GATEWAY_ERROR",
                "UNAUTHORIZED",
            ],
        ),
        "request_checkout": CapabilityDefinition(
            name="request_checkout",
            description="Generate Razorpay checkout session parameters and payment metadata.",
            input_schema_name="RequestCheckoutRequest",
            output_schema_name="RequestCheckoutResponse",
            input_schema=RequestCheckoutRequest.model_json_schema(),
            output_schema=RequestCheckoutResponse.model_json_schema(),
            classification="PRIVILEGED_FINANCIAL",
            side_effects=[
                "creates_or_refreshes_razorpay_order",
                "initiates_payment_attempt_fsm",
                "appends_audit_event",
            ],
            monetary_impact=True,
            required_capability="buyer:checkout",
            approval_requirement="AUTOMATIC",
            idempotency_requirement=True,
            failure_states=[
                "ORDER_NOT_FOUND",
                "ORDER_ALREADY_PAID",
                "ORDER_CANCELLED",
                "PAYMENT_GATEWAY_ERROR",
                "UNAUTHORIZED",
            ],
        ),
        "get_payment_status": CapabilityDefinition(
            name="get_payment_status",
            description="Retrieve order payment status, attempts, and reconciliation state.",
            input_schema_name="GetPaymentStatusRequest",
            output_schema_name="GetPaymentStatusResponse",
            input_schema=GetPaymentStatusRequest.model_json_schema(),
            output_schema=GetPaymentStatusResponse.model_json_schema(),
            classification="READ_ONLY",
            side_effects=["none"],
            monetary_impact=True,
            required_capability="buyer:payment_status",
            approval_requirement="NONE",
            idempotency_requirement=False,
            failure_states=["ORDER_NOT_FOUND", "UNAUTHORIZED"],
        ),
        "get_order_status": CapabilityDefinition(
            name="get_order_status",
            description="Retrieve order details, shipping information, and settlement state.",
            input_schema_name="GetOrderStatusRequest",
            output_schema_name="GetOrderStatusResponse",
            input_schema=GetOrderStatusRequest.model_json_schema(),
            output_schema=GetOrderStatusResponse.model_json_schema(),
            classification="READ_ONLY",
            side_effects=["none"],
            monetary_impact=True,
            required_capability="buyer:read",
            approval_requirement="NONE",
            idempotency_requirement=False,
            failure_states=["ORDER_NOT_FOUND", "UNAUTHORIZED"],
        ),
    }

    @classmethod
    def get_all_capabilities(cls) -> list[CapabilityDefinition]:
        """Returns the full catalog of declared capabilities."""
        return list(cls._CAPABILITIES.values())

    @classmethod
    def get_capability(cls, capability_name: str) -> CapabilityDefinition | None:
        """Retrieves metadata definition for a specific capability name."""
        return cls._CAPABILITIES.get(capability_name)

    @classmethod
    def is_valid_capability(cls, capability_name: str) -> bool:
        """Checks if a capability name is registered in the canonical registry."""
        return capability_name in cls._CAPABILITIES

    @classmethod
    def check_authorization(
        cls, capability_name: str, context: GatewayContext
    ) -> tuple[bool, str | None]:
        """Validates if the provided GatewayContext has authority to execute capability."""
        cap = cls.get_capability(capability_name)
        if not cap:
            return False, f"Unknown capability '{capability_name}'"

        if not context.has_capability(cap.required_capability):
            return (
                False,
                f"Session missing capability '{cap.required_capability}' for '{capability_name}'",
            )

        return True, None
