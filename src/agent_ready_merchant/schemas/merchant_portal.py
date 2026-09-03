"""Merchant Control Plane schemas for Phase 5.2."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from agent_ready_merchant.gateway.constants import (
    COMMERCE_PROTOCOL_VERSION,
    MAX_64BIT_INT,
)


class DashboardSummaryResponse(BaseModel):
    """Authoritative aggregated summary metrics for the merchant control plane."""

    model_config = ConfigDict(extra="forbid")

    merchant_id: uuid.UUID
    merchant_name: str
    status: str
    currency: str
    total_products: int = Field(default=0, ge=0)
    total_orders: int = Field(default=0, ge=0)
    total_revenue_paise: int = Field(default=0, ge=0)
    pending_approvals_count: int = Field(default=0, ge=0)
    active_quotes_count: int = Field(default=0, ge=0)
    autonomy_level: int = Field(default=1, ge=0, le=2)
    max_discount_percentage: float = Field(default=15.0, ge=0.0, le=50.0)
    min_margin_percentage: float = Field(default=20.0, ge=0.0, le=100.0)
    max_single_transaction_paise: int = Field(default=5_000_000, ge=0)
    policy_hash: str
    system_health: str = Field(default="HEALTHY")


class ProductItemResponse(BaseModel):
    """Authoritative product catalog item returned for merchant views."""

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    merchant_id: uuid.UUID
    sku: str
    title: str
    description: str
    category: str
    base_price_paise: int = Field(..., gt=0)
    floor_price_paise: int = Field(..., gt=0)
    is_negotiable: bool
    is_active: bool
    attributes: dict[str, Any] = Field(default_factory=dict)
    version: int = Field(..., ge=1)
    created_at: datetime
    available_stock: int = Field(default=0, ge=0)
    reserved_stock: int = Field(default=0, ge=0)


class ProductCreateRequest(BaseModel):
    """Payload to create a new merchant catalog product."""

    model_config = ConfigDict(extra="forbid")

    sku: str = Field(..., min_length=2, max_length=100)
    title: str = Field(..., min_length=2, max_length=255)
    description: str = Field(default="", max_length=2000)
    category: str = Field(..., min_length=2, max_length=100)
    base_price_paise: int = Field(..., gt=0, le=MAX_64BIT_INT)
    floor_price_paise: int = Field(..., gt=0, le=MAX_64BIT_INT)
    is_negotiable: bool = Field(default=True)
    is_active: bool = Field(default=True)
    initial_stock: int = Field(default=10, ge=0)
    safety_threshold: int = Field(default=2, ge=0)
    attributes: dict[str, Any] = Field(default_factory=dict)


class InventoryItemResponse(BaseModel):
    """Authoritative inventory item record."""

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    variant_id: uuid.UUID
    sku: str
    product_title: str
    available_quantity: int = Field(..., ge=0)
    reserved_quantity: int = Field(..., ge=0)
    safety_threshold: int = Field(..., ge=0)
    updated_at: datetime


class InventoryAdjustRequest(BaseModel):
    """Request payload to adjust inventory quantities."""

    model_config = ConfigDict(extra="forbid")

    sku: str = Field(..., min_length=1, max_length=100)
    quantity_delta: int = Field(..., description="Units to add (positive) or remove (negative)")
    reason: str = Field(default="MANUAL_ADJUSTMENT", max_length=255)


class QuoteItemDetail(BaseModel):
    """Quote line item detail."""

    model_config = ConfigDict(extra="forbid")

    sku: str
    title: str
    quantity: int = Field(..., gt=0)
    unit_price_paise: int = Field(..., gt=0)
    total_price_paise: int = Field(..., gt=0)


class QuoteDetailResponse(BaseModel):
    """Authoritative price quote representation."""

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    session_id: uuid.UUID
    merchant_id: uuid.UUID
    status: str
    subtotal_paise: int = Field(..., ge=0)
    discount_paise: int = Field(..., ge=0)
    shipping_paise: int = Field(..., ge=0)
    total_paise: int = Field(..., ge=0)
    discount_reason: str | None = None
    expires_at: datetime
    created_at: datetime
    items: list[QuoteItemDetail] = Field(default_factory=list)


class OrderDetailResponse(BaseModel):
    """Authoritative order record for merchant dashboard."""

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    quote_id: uuid.UUID
    merchant_id: uuid.UUID
    status: str
    amount_paise: int = Field(..., gt=0)
    currency: str = Field(default="INR")
    buyer_email: str
    shipping_address: dict[str, Any] = Field(default_factory=dict)
    rzp_order_id: str | None = None
    created_at: datetime
    payment_attempts_count: int = Field(default=0, ge=0)


class PaymentAttemptResponse(BaseModel):
    """Authoritative payment attempt record."""

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    order_id: uuid.UUID
    status: str
    amount_paise: int = Field(..., gt=0)
    rzp_payment_id: str | None = None
    rzp_order_id: str
    payment_method: str | None = None
    error_code: str | None = None
    error_description: str | None = None
    created_at: datetime


class ApprovalItemResponse(BaseModel):
    """Authoritative merchant approval ticket."""

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    merchant_id: uuid.UUID
    quote_id: uuid.UUID | None = None
    order_id: uuid.UUID | None = None
    session_id: uuid.UUID | None = None
    approval_type: str
    status: str
    requested_amount_paise: int = Field(..., ge=0)
    proposed_discount_paise: int = Field(..., ge=0)
    proposed_discount_percentage: float = Field(default=0.0, ge=0.0)
    policy_rule_code: str
    reason: str
    approver_identifier: str | None = None
    resolved_at: datetime | None = None
    expires_at: datetime
    created_at: datetime


class ResolveApprovalPayload(BaseModel):
    """Payload to resolve an approval ticket."""

    model_config = ConfigDict(extra="forbid")

    decision: Literal["APPROVE", "REJECT", "COUNTER_OFFER"]
    reason_note: str = Field(..., min_length=2, max_length=500)
    counter_amount_paise: int | None = Field(default=None, ge=100, le=MAX_64BIT_INT)


class PolicyRuleDetail(BaseModel):
    """Detailed policy rule representation."""

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    rule_type: str
    target_scope: str
    target_id: str | None = None
    rule_value: dict[str, Any]
    is_active: bool


class PolicyGovernanceResponse(BaseModel):
    """Policy rules snapshot with deterministic SHA-256 hash."""

    model_config = ConfigDict(extra="forbid")

    merchant_id: uuid.UUID
    autonomy_level: int
    max_discount_percentage: float
    min_margin_percentage: float
    max_single_transaction_paise: int
    policy_hash: str
    protocol_version: str = Field(default=COMMERCE_PROTOCOL_VERSION)
    rules: list[PolicyRuleDetail] = Field(default_factory=list)


class UpdatePoliciesPayload(BaseModel):
    """Payload to update policy rules."""

    model_config = ConfigDict(extra="forbid")

    autonomy_level: int = Field(default=1, ge=0, le=2)
    max_discount_percentage: float = Field(default=15.0, ge=0.0, le=50.0)
    min_margin_percentage: float = Field(default=20.0, ge=0.0, le=100.0)
    max_single_transaction_paise: int = Field(default=5_000_000, ge=100, le=MAX_64BIT_INT)


class AuditEventResponse(BaseModel):
    """Immutable audit event log."""

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    merchant_id: uuid.UUID
    actor_type: str
    session_id: uuid.UUID | None = None
    event_type: str
    payload: dict[str, Any]
    event_hash: str
    prev_event_hash: str | None = None
    created_at: datetime


class AuditLedgerCursor(BaseModel):
    """Stable keyset cursor for fetching older immutable audit events."""

    model_config = ConfigDict(extra="forbid")

    created_at: datetime
    id: uuid.UUID


class AuditLedgerResponse(BaseModel):
    """Full audit trail response with cryptographic chain validity badge."""

    model_config = ConfigDict(extra="forbid")

    events: list[AuditEventResponse]
    total_count: int
    chain_valid: bool
    chain_error: str | None = None
    next_cursor: AuditLedgerCursor | None = None
