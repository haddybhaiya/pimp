"""Canonical request, response, and envelope schemas for the Commerce Gateway.

Adheres strictly to Phase 2.1 - 2.3 specifications:
- Strict Pydantic models with extra="forbid"
- Versioned canonical contract ("2026-03-01")
- Request IDs and Idempotency Keys on mutations
- Explicit UUID types and non-negative 64-bit integer paise
- Deterministic response envelopes with state-oriented context
- Zero leakage of internal ORM models or database credentials
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from agent_ready_merchant.gateway.constants import (
    COMMERCE_PROTOCOL_VERSION as COMMERCE_PROTOCOL_VERSION,
)
from agent_ready_merchant.gateway.constants import (
    DEFAULT_MAX_PAYLOAD_BYTES as DEFAULT_MAX_PAYLOAD_BYTES,
)
from agent_ready_merchant.gateway.constants import (
    MAX_64BIT_INT as MAX_64BIT_INT,
)
from agent_ready_merchant.gateway.constants import (
    MIN_64BIT_INT as MIN_64BIT_INT,
)

T = TypeVar("T")


class GatewayError(BaseModel):
    """Structured error descriptor returned inside failure response envelopes."""

    model_config = ConfigDict(extra="forbid")

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error explanation")
    retryable: bool = Field(default=False, description="Whether this request may be retried")
    details: dict[str, Any] | None = Field(default=None, description="Optional diagnostic details")


class StateOrientedContext(BaseModel):
    """Authoritative commerce state context enabling clients to progress conversations."""

    model_config = ConfigDict(extra="forbid")

    entity_type: str = Field(..., description="Commerce entity type (e.g. PriceQuote, Order)")
    entity_id: uuid.UUID | str = Field(..., description="Primary identifier of the entity")
    state: str = Field(..., description="Current authoritative state machine status")
    version: int | None = Field(default=None, description="Optimistic locking version")
    allowed_actions: list[str] = Field(
        default_factory=list, description="Legal transitions/actions from current state"
    )
    next_action: str | None = Field(
        default=None, description="Recommended next action for the buyer/agent"
    )
    expires_at: datetime | None = Field(
        default=None, description="State expiration timestamp if applicable"
    )


class GatewayResponseEnvelope(BaseModel, Generic[T]):
    """Standardized deterministic response envelope for all canonical gateway operations."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field(
        default=COMMERCE_PROTOCOL_VERSION,
        description="Canonical commerce contract schema version",
    )
    request_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="Unique request trace identifier",
    )
    status: Literal["SUCCESS", "REJECTED", "ERROR"] = Field(
        ..., description="Overall execution outcome"
    )
    capability: str = Field(..., description="Canonical capability name executed")
    data: T | None = Field(default=None, description="Authoritative response payload on success")
    error: GatewayError | None = Field(
        default=None, description="Structured error details on rejection/error"
    )
    state: StateOrientedContext | None = Field(
        default=None, description="Commerce state context for follow-up actions"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="ISO-8601 UTC timestamp of execution",
    )
    audit_event_id: uuid.UUID | None = Field(
        default=None, description="Hash-chained audit event ID if state changed"
    )
    idempotency_key: str | None = Field(
        default=None,
        description="Client-supplied idempotency key if provided",
    )


# -----------------------------------------------------------------------------
# 1. discover_products
# -----------------------------------------------------------------------------
class DiscoverProductsRequest(BaseModel):
    """Request parameters to filter and search merchant product catalog."""

    model_config = ConfigDict(extra="forbid")

    query: str | None = Field(
        default=None, max_length=100, description="Keyword search in title/description"
    )
    category: str | None = Field(default=None, max_length=50, description="Product category filter")
    min_price_paise: int | None = Field(
        default=None, ge=0, le=MAX_64BIT_INT, description="Minimum base price filter in paise"
    )
    max_price_paise: int | None = Field(
        default=None, ge=0, le=MAX_64BIT_INT, description="Maximum base price filter in paise"
    )
    in_stock_only: bool = Field(default=False, description="Filter for in-stock products only")
    limit: int = Field(default=5, ge=1, le=20, description="Page size limit")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")


class ProductSummaryItem(BaseModel):
    """Summary item representation inside catalog discovery results."""

    model_config = ConfigDict(extra="forbid")

    sku: str = Field(..., description="Canonical product SKU")
    title: str = Field(..., description="Product title")
    category: str = Field(..., description="Product category")
    base_price_paise: int = Field(
        ..., gt=0, le=MAX_64BIT_INT, description="Base catalog price in integer paise"
    )
    currency: str = Field(default="INR", description="Currency standard (INR)")
    is_negotiable: bool = Field(..., description="Whether price negotiation is permitted")
    in_stock: bool = Field(..., description="General availability status")
    variant_count: int = Field(default=1, ge=1, description="Number of purchasable variants")


class DiscoverProductsResponse(BaseModel):
    """Catalog search results and pagination metadata."""

    model_config = ConfigDict(extra="forbid")

    products: list[ProductSummaryItem] = Field(..., description="Matching products list")
    total_matched: int = Field(..., ge=0, description="Total count of matched items")
    limit: int = Field(..., ge=1, description="Page size limit applied")
    offset: int = Field(..., ge=0, description="Offset applied")


# -----------------------------------------------------------------------------
# 2. get_product
# -----------------------------------------------------------------------------
class GetProductRequest(BaseModel):
    """Request parameter for retrieving comprehensive SKU details."""

    model_config = ConfigDict(extra="forbid")

    sku: str = Field(..., min_length=1, max_length=100, description="Target product SKU")


class VariantDetailItem(BaseModel):
    """Purchasable variant specification."""

    model_config = ConfigDict(extra="forbid")

    variant_id: uuid.UUID = Field(..., description="Variant unique identifier")
    sku: str = Field(..., description="Variant specific SKU")
    title: str = Field(..., description="Variant title (e.g. Size / Color)")
    price_override_paise: int | None = Field(
        default=None, gt=0, le=MAX_64BIT_INT, description="Optional variant price override in paise"
    )
    effective_price_paise: int = Field(
        ..., gt=0, le=MAX_64BIT_INT, description="Effective unit price in integer paise"
    )
    currency: str = Field(default="INR", description="Currency standard (INR)")
    is_active: bool = Field(..., description="Whether this variant is active")
    available_quantity: int = Field(..., ge=0, description="Available unreserved stock")
    in_stock: bool = Field(..., description="Whether stock is available above safety threshold")
    attributes: dict[str, Any] = Field(default_factory=dict, description="Structured attributes")


class GetProductResponse(BaseModel):
    """Detailed specifications and variants for a product SKU."""

    model_config = ConfigDict(extra="forbid")

    product_id: uuid.UUID = Field(..., description="Product unique identifier")
    sku: str = Field(..., description="Canonical product SKU")
    title: str = Field(..., description="Product title")
    description: str = Field(default="", description="Product description")
    category: str = Field(..., description="Product category")
    base_price_paise: int = Field(
        ..., gt=0, le=MAX_64BIT_INT, description="Base catalog price in paise"
    )
    currency: str = Field(default="INR", description="Currency standard (INR)")
    is_negotiable: bool = Field(..., description="Whether price negotiation is permitted")
    is_active: bool = Field(..., description="Whether product is active for purchase")
    attributes: dict[str, Any] = Field(default_factory=dict, description="Product attributes")
    variants: list[VariantDetailItem] = Field(
        default_factory=list, description="Available variants"
    )


# -----------------------------------------------------------------------------
# 3. check_inventory
# -----------------------------------------------------------------------------
class CheckInventoryRequest(BaseModel):
    """Request parameter to check real-time stock availability for a SKU or variant."""

    model_config = ConfigDict(extra="forbid")

    sku: str = Field(..., min_length=1, max_length=100, description="Product or Variant SKU")
    requested_quantity: int = Field(
        default=1, ge=1, le=100, description="Quantity requested to verify fulfillability"
    )


class CheckInventoryResponse(BaseModel):
    """Authoritative inventory stock levels and fulfillability result."""

    model_config = ConfigDict(extra="forbid")

    sku: str = Field(..., description="Requested SKU")
    variant_id: uuid.UUID = Field(..., description="Resolved variant identifier")
    available_quantity: int = Field(..., ge=0, description="Authoritative available quantity")
    reserved_quantity: int = Field(..., ge=0, description="Currently reserved quantity")
    safety_threshold: int = Field(..., ge=0, description="Configured safety stock threshold")
    in_stock: bool = Field(..., description="Whether item is in stock above safety threshold")
    can_fulfill: bool = Field(
        ..., description="Whether requested quantity can be fulfilled right now"
    )
    max_order_quantity: int = Field(..., ge=0, description="Maximum purchasable quantity right now")


# -----------------------------------------------------------------------------
# 4. get_quote
# -----------------------------------------------------------------------------
class QuoteItemRequest(BaseModel):
    """Individual line item request inside get_quote."""

    model_config = ConfigDict(extra="forbid")

    sku: str = Field(..., min_length=1, max_length=100, description="Product or Variant SKU")
    quantity: int = Field(..., ge=1, le=10, description="Purchasable unit quantity")


class GetQuoteRequest(BaseModel):
    """Request parameter to create or retrieve an authoritative binding price quote."""

    model_config = ConfigDict(extra="forbid")

    session_id: uuid.UUID = Field(..., description="Active buyer session identifier")
    items: list[QuoteItemRequest] = Field(
        default_factory=list, max_length=5, description="Items to quote if requesting new quote"
    )
    quote_id: uuid.UUID | None = Field(
        default=None, description="Optional quote ID if retrieving an existing quote"
    )
    shipping_country: str = Field(
        default="IN", max_length=2, description="Target destination country"
    )
    idempotency_key: str | None = Field(
        default=None, max_length=128, description="Optional client idempotency key"
    )


class QuoteLineItemDetail(BaseModel):
    """Detailed line item within an authoritative quote."""

    model_config = ConfigDict(extra="forbid")

    variant_id: uuid.UUID = Field(..., description="Variant identifier")
    sku: str = Field(..., description="Line item SKU")
    title: str = Field(..., description="Item title")
    quantity: int = Field(..., ge=1, description="Quantity")
    unit_price_paise: int = Field(
        ..., gt=0, le=MAX_64BIT_INT, description="Unit price in integer paise"
    )
    total_price_paise: int = Field(
        ..., gt=0, le=MAX_64BIT_INT, description="Line item subtotal in integer paise"
    )


class GetQuoteResponse(BaseModel):
    """Authoritative, binding, time-limited price quote."""

    model_config = ConfigDict(extra="forbid")

    quote_id: uuid.UUID = Field(..., description="Unique quote identifier")
    session_id: uuid.UUID = Field(..., description="Associated buyer session")
    status: str = Field(..., description="Authoritative quote status (PROPOSED, ACCEPTED, etc.)")
    currency: str = Field(default="INR", description="Currency standard (INR)")
    items: list[QuoteLineItemDetail] = Field(..., description="Line items")
    subtotal_paise: int = Field(
        ..., ge=0, le=MAX_64BIT_INT, description="Gross item subtotal in paise"
    )
    discount_paise: int = Field(
        ..., ge=0, le=MAX_64BIT_INT, description="Applied discount in paise"
    )
    shipping_paise: int = Field(..., ge=0, le=MAX_64BIT_INT, description="Shipping fee in paise")
    total_paise: int = Field(
        ..., gt=0, le=MAX_64BIT_INT, description="Final binding total amount in paise"
    )
    expires_at: datetime = Field(..., description="Quote expiration deadline (UTC)")
    is_expired: bool = Field(..., description="Whether quote is currently expired")


# -----------------------------------------------------------------------------
# 5. calculate_shipping
# -----------------------------------------------------------------------------
class CalculateShippingRequest(BaseModel):
    """Request parameters for authoritative shipping calculation."""

    model_config = ConfigDict(extra="forbid")

    destination_postal_code: str = Field(
        ..., min_length=1, max_length=20, description="Destination postal code"
    )
    destination_country: str = Field(
        default="IN", max_length=2, description="Destination country code"
    )
    subtotal_paise: int | None = Field(
        default=None, ge=0, le=MAX_64BIT_INT, description="Cart subtotal in paise"
    )
    quote_id: uuid.UUID | None = Field(
        default=None, description="Optional existing quote ID to calculate for"
    )


class CalculateShippingResponse(BaseModel):
    """Authoritative shipping fee and logistics information."""

    model_config = ConfigDict(extra="forbid")

    destination_country: str = Field(..., description="Destination country")
    destination_postal_code: str = Field(..., description="Destination postal code")
    shipping_fee_paise: int = Field(
        ..., ge=0, le=MAX_64BIT_INT, description="Computed shipping fee in paise"
    )
    currency: str = Field(default="INR", description="Currency standard (INR)")
    qualifies_for_free_shipping: bool = Field(
        ..., description="Whether subtotal meets free shipping threshold"
    )
    free_shipping_threshold_paise: int = Field(
        ..., ge=0, le=MAX_64BIT_INT, description="Merchant free shipping threshold in paise"
    )
    estimated_delivery_days: int = Field(
        default=3, ge=1, description="Estimated delivery window in days"
    )
    service_carrier: str = Field(
        default="Standard Logistics",
        description="Logistics service tier",
    )


# -----------------------------------------------------------------------------
# 6. create_order
# -----------------------------------------------------------------------------
class ShippingAddressGateway(BaseModel):
    """Shipping destination structure."""

    model_config = ConfigDict(extra="forbid")

    full_name: str = Field(..., min_length=1, max_length=100, description="Recipient full name")
    address_line1: str = Field(..., min_length=1, max_length=200, description="Street address")
    city: str = Field(..., min_length=1, max_length=100, description="City")
    postal_code: str = Field(..., min_length=1, max_length=20, description="Postal code")
    country: str = Field(default="IN", max_length=2, description="ISO country code")


class CreateOrderGatewayRequest(BaseModel):
    """Request parameter to convert an ACCEPTED quote into a locked Order."""

    model_config = ConfigDict(extra="forbid")

    quote_id: uuid.UUID = Field(..., description="ID of the ACCEPTED PriceQuote")
    buyer_email: EmailStr = Field(
        ...,
        description="Buyer email address for notifications and receipt",
    )
    shipping_address: ShippingAddressGateway = Field(
        ...,
        description="Destination shipping address",
    )
    idempotency_key: str | None = Field(
        default=None, max_length=128, description="Optional client idempotency key"
    )


class CreateOrderGatewayResponse(BaseModel):
    """Created authoritative merchant Order entity."""

    model_config = ConfigDict(extra="forbid")

    order_id: uuid.UUID = Field(..., description="Unique merchant order identifier")
    quote_id: uuid.UUID = Field(..., description="Originating quote identifier")
    status: str = Field(..., description="Authoritative order state (e.g. PENDING_PAYMENT)")
    amount_paise: int = Field(
        ..., gt=0, le=MAX_64BIT_INT, description="Total order amount in integer paise"
    )
    currency: str = Field(default="INR", description="Currency standard (INR)")
    buyer_email: str = Field(..., description="Buyer notification email")
    rzp_order_id: str | None = Field(
        default=None,
        description="External Razorpay order identifier",
    )
    shipping_address: ShippingAddressGateway = Field(
        ...,
        description="Destination shipping address",
    )
    created_at: datetime = Field(..., description="Order creation timestamp")


# -----------------------------------------------------------------------------
# 7. request_checkout
# -----------------------------------------------------------------------------
class RequestCheckoutRequest(BaseModel):
    """Request parameter to initiate checkout for an existing order or accepted quote."""

    model_config = ConfigDict(extra="forbid")

    order_id: uuid.UUID | None = Field(
        default=None, description="Existing Order ID to request checkout for"
    )
    quote_id: uuid.UUID | None = Field(
        default=None, description="Accepted Quote ID to convert to order and checkout"
    )
    buyer_email: EmailStr | None = Field(
        default=None, description="Required if creating order from quote"
    )
    shipping_address: ShippingAddressGateway | None = Field(
        default=None, description="Required if creating order from quote"
    )
    idempotency_key: str | None = Field(
        default=None, max_length=128, description="Optional client idempotency key"
    )


class RequestCheckoutResponse(BaseModel):
    """Authoritative checkout metadata and Razorpay payment parameters."""

    model_config = ConfigDict(extra="forbid")

    order_id: uuid.UUID = Field(..., description="Merchant order identifier")
    rzp_order_id: str = Field(..., description="External Razorpay order ID")
    amount_paise: int = Field(
        ..., gt=0, le=MAX_64BIT_INT, description="Charge amount in integer paise"
    )
    currency: str = Field(default="INR", description="Currency standard (INR)")
    status: str = Field(..., description="Order payment status (e.g. PENDING_PAYMENT)")
    key_id: str = Field(..., description="Razorpay public test key ID for client SDK")
    supported_payment_methods: list[str] = Field(
        default_factory=lambda: ["upi", "card", "netbanking", "wallet"],
        description="Supported payment methods",
    )
    callback_url: str | None = Field(
        default=None, description="Optional webhook or redirect verification target"
    )


# -----------------------------------------------------------------------------
# 8. get_payment_status
# -----------------------------------------------------------------------------
class GetPaymentStatusRequest(BaseModel):
    """Request parameter to query authoritative payment and reconciliation status."""

    model_config = ConfigDict(extra="forbid")

    order_id: uuid.UUID = Field(..., description="Merchant order ID to query")


class PaymentAttemptItem(BaseModel):
    """Summary of an individual payment attempt record."""

    model_config = ConfigDict(extra="forbid")

    payment_id: uuid.UUID = Field(..., description="Internal payment attempt identifier")
    rzp_payment_id: str | None = Field(default=None, description="Razorpay payment ID")
    status: str = Field(..., description="Attempt status (INITIATED, CAPTURED, FAILED)")
    amount_paise: int = Field(..., ge=0, le=MAX_64BIT_INT, description="Attempted amount in paise")
    payment_method: str | None = Field(default=None, description="Payment method used")
    error_code: str | None = Field(default=None, description="Failure error code if failed")
    created_at: datetime = Field(..., description="Attempt timestamp")


class GetPaymentStatusResponse(BaseModel):
    """Authoritative payment settlement status."""

    model_config = ConfigDict(extra="forbid")

    order_id: uuid.UUID = Field(..., description="Merchant order identifier")
    order_status: str = Field(
        ...,
        description="Authoritative order state (e.g. PAID, PENDING_PAYMENT)",
    )
    amount_paise: int = Field(
        ..., gt=0, le=MAX_64BIT_INT, description="Total order amount in paise"
    )
    currency: str = Field(default="INR", description="Currency standard (INR)")
    is_paid: bool = Field(
        ...,
        description="Whether payment has been authoritatively captured and settled",
    )
    rzp_order_id: str | None = Field(default=None, description="Associated Razorpay order ID")
    payment_attempts: list[PaymentAttemptItem] = Field(
        default_factory=list, description="Historical payment attempts recorded"
    )
    settled_at: datetime | None = Field(
        default=None, description="Settlement timestamp if order is paid"
    )


# -----------------------------------------------------------------------------
# 9. Session Lifecycle Schemas
# -----------------------------------------------------------------------------
class InitializeSessionRequest(BaseModel):
    """Request parameter to initialize an authoritative buyer agent session."""

    model_config = ConfigDict(extra="forbid")

    buyer_agent_identifier: str = Field(
        ..., min_length=1, max_length=255, description="Unique buyer agent identifier"
    )
    auth_token_raw: str | None = Field(
        default=None, min_length=8, description="Optional raw token to hash for session auth"
    )
    duration_minutes: int = Field(
        default=60, ge=5, le=1440, description="Session validity duration in minutes"
    )
    requested_capabilities: list[str] = Field(
        default_factory=lambda: [
            "buyer:discover",
            "buyer:read",
            "buyer:quote",
            "buyer:negotiate",
            "buyer:checkout",
            "buyer:payment_status",
        ],
        description="List of requested security capabilities",
    )
    idempotency_key: str | None = Field(
        default=None, max_length=128, description="Optional client idempotency key"
    )


class InitializeSessionResponse(BaseModel):
    """Created buyer agent session metadata."""

    model_config = ConfigDict(extra="forbid")

    session_id: uuid.UUID = Field(..., description="Authoritative session identifier")
    merchant_id: uuid.UUID = Field(..., description="Target merchant identifier")
    buyer_agent_identifier: str = Field(..., description="Registered buyer agent identity")
    status: str = Field(default="ACTIVE", description="Session state (ACTIVE, EXPIRED, TERMINATED)")
    granted_capabilities: list[str] = Field(..., description="Authorized capabilities for session")
    auth_token_hash: str = Field(..., description="Cryptographic SHA-256 hash of auth token")
    expires_at: datetime = Field(..., description="Session expiration timestamp")
    created_at: datetime = Field(..., description="Session initialization timestamp")


class TerminateSessionRequest(BaseModel):
    """Request parameter to explicitly terminate an active buyer agent session."""

    model_config = ConfigDict(extra="forbid")

    session_id: uuid.UUID = Field(..., description="Session identifier to terminate")
    reason: str | None = Field(
        default="Buyer session completed normally",
        description="Termination rationale",
    )


class TerminateSessionResponse(BaseModel):
    """Session termination confirmation."""

    model_config = ConfigDict(extra="forbid")

    session_id: uuid.UUID = Field(..., description="Terminated session ID")
    status: str = Field(default="TERMINATED", description="Updated session status")
    terminated_at: datetime = Field(..., description="Timestamp of termination")


# -----------------------------------------------------------------------------
# 10. Bounded Quote Negotiation & Acceptance Schemas
# -----------------------------------------------------------------------------
class NegotiateQuoteGatewayRequest(BaseModel):
    """Request parameter to submit a counter-offer against an active PriceQuote."""

    model_config = ConfigDict(extra="forbid")

    quote_id: uuid.UUID = Field(..., description="ID of the PriceQuote to negotiate")
    proposed_total_paise: int = Field(
        ..., gt=0, le=MAX_64BIT_INT, description="Buyer proposed total price in integer paise"
    )
    rationale: str | None = Field(
        default=None, max_length=500, description="Negotiation justification/rationale"
    )
    idempotency_key: str | None = Field(
        default=None, max_length=128, description="Optional client idempotency key"
    )


class NegotiateQuoteGatewayResponse(BaseModel):
    """Authoritative outcome of quote negotiation."""

    model_config = ConfigDict(extra="forbid")

    quote_id: uuid.UUID = Field(..., description="Negotiated quote ID")
    status: str = Field(
        ..., description="Quote status after negotiation (e.g. PROPOSED, PENDING_APPROVAL)"
    )
    currency: str = Field(default="INR", description="Currency code")
    subtotal_paise: int = Field(
        ..., ge=0, le=MAX_64BIT_INT, description="Subtotal before discounts"
    )
    discount_paise: int = Field(
        ..., ge=0, le=MAX_64BIT_INT, description="Applied discount in paise"
    )
    shipping_paise: int = Field(..., ge=0, le=MAX_64BIT_INT, description="Shipping cost in paise")
    total_paise: int = Field(..., gt=0, le=MAX_64BIT_INT, description="Effective total in paise")
    verdict: str = Field(
        ..., description="Policy evaluation verdict (ALLOW, ESCALATE_APPROVAL, DENY)"
    )
    rule_code: str | None = Field(default=None, description="Triggered policy rule code if any")
    reason: str | None = Field(default=None, description="Policy evaluation reason or requirement")
    expires_at: datetime = Field(..., description="Quote expiration timestamp")


class AcceptQuoteGatewayRequest(BaseModel):
    """Request parameter to accept a binding proposed PriceQuote."""

    model_config = ConfigDict(extra="forbid")

    quote_id: uuid.UUID = Field(..., description="ID of the PriceQuote to accept")
    idempotency_key: str | None = Field(
        default=None, max_length=128, description="Optional client idempotency key"
    )


class AcceptQuoteGatewayResponse(BaseModel):
    """Quote acceptance confirmation."""

    model_config = ConfigDict(extra="forbid")

    quote_id: uuid.UUID = Field(..., description="Accepted quote ID")
    status: str = Field(default="ACCEPTED", description="Authoritative quote status (ACCEPTED)")
    total_paise: int = Field(
        ..., gt=0, le=MAX_64BIT_INT, description="Final accepted total in paise"
    )
    currency: str = Field(default="INR", description="Currency standard (INR)")
    accepted_at: datetime = Field(..., description="Acceptance timestamp")
    expires_at: datetime = Field(..., description="Quote expiration timestamp")


# -----------------------------------------------------------------------------
# 11. get_order_status
# -----------------------------------------------------------------------------
class GetOrderStatusRequest(BaseModel):
    """Request parameter to query authoritative order details and status."""

    model_config = ConfigDict(extra="forbid")

    order_id: uuid.UUID = Field(..., description="Merchant order ID to query")


class GetOrderStatusResponse(BaseModel):
    """Authoritative order status and details."""

    model_config = ConfigDict(extra="forbid")

    order_id: uuid.UUID = Field(..., description="Unique merchant order identifier")
    quote_id: uuid.UUID = Field(..., description="Originating quote ID")
    status: str = Field(..., description="Order state (e.g. PAID, PENDING_PAYMENT, COMPLETED)")
    amount_paise: int = Field(
        ..., gt=0, le=MAX_64BIT_INT, description="Total order amount in paise"
    )
    currency: str = Field(default="INR", description="Currency standard (INR)")
    buyer_email: str = Field(..., description="Buyer notification email")
    rzp_order_id: str | None = Field(default=None, description="Associated Razorpay order ID")
    shipping_address: ShippingAddressGateway = Field(
        ..., description="Destination shipping address"
    )
    created_at: datetime = Field(..., description="Order creation timestamp")
    is_settled: bool = Field(
        ..., description="Whether payment for this order is captured and settled"
    )
