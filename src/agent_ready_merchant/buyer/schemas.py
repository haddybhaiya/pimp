"""Schemas and state definitions for the External AI Buyer Commerce Flow.

Adheres strictly to Phase 2.2 specifications:
- Explicit response states (DISCOVERED, PRODUCT_SELECTED, QUOTED, etc.)
- Explicit failure states (PAYMENT_FAILED, INVENTORY_CHANGED, POLICY_REJECTED, etc.)
- Strict Pydantic models with extra="forbid"
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BuyerCommerceState(StrEnum):
    """Authoritative lifecycle progression states for external AI buyer flows."""

    DISCOVERED = "DISCOVERED"
    PRODUCT_SELECTED = "PRODUCT_SELECTED"
    QUOTED = "QUOTED"
    NEGOTIATION_PENDING = "NEGOTIATION_PENDING"
    OFFER_ACCEPTED = "OFFER_ACCEPTED"
    ORDER_CREATED = "ORDER_CREATED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    PAYMENT_SUCCEEDED = "PAYMENT_SUCCEEDED"
    COMPLETED = "COMPLETED"


class BuyerFailureState(StrEnum):
    """Explicit failure and rejection states encountered during commerce flows."""

    PAYMENT_FAILED = "PAYMENT_FAILED"
    PAYMENT_EXPIRED = "PAYMENT_EXPIRED"
    AUTHORIZATION_REQUIRED = "AUTHORIZATION_REQUIRED"
    INVENTORY_CHANGED = "INVENTORY_CHANGED"
    PRICE_CHANGED = "PRICE_CHANGED"
    QUOTE_EXPIRED = "QUOTE_EXPIRED"
    POLICY_REJECTED = "POLICY_REJECTED"
    ORDER_EXPIRED = "ORDER_EXPIRED"
    RATE_LIMITED = "RATE_LIMITED"


class BuyerFlowStep(BaseModel):
    """Audit record of a single capability executed in the buyer flow."""

    model_config = ConfigDict(extra="forbid")

    step_name: str = Field(..., description="Executed capability or operation name")
    status: str = Field(..., description="Step outcome (SUCCESS, REJECTED, ERROR)")
    state_after_step: str = Field(..., description="Buyer state machine status after step")
    details: dict[str, Any] = Field(default_factory=dict, description="Step context or payload")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Step timestamp"
    )


class BuyerFlowContext(BaseModel):
    """In-memory session and transaction context for an active AI Buyer client."""

    model_config = ConfigDict(extra="forbid")

    merchant_id: uuid.UUID = Field(..., description="Target merchant identifier")
    buyer_agent_identifier: str = Field(..., description="AI Buyer identity")
    session_id: uuid.UUID | None = Field(default=None, description="Active session ID")
    auth_token_raw: str | None = Field(default=None, description="Session bearer auth token")
    current_state: BuyerCommerceState | None = Field(
        default=None, description="Current progress state"
    )
    current_failure: BuyerFailureState | None = Field(
        default=None, description="Failure state if rejected"
    )
    selected_sku: str | None = Field(default=None, description="Selected product SKU")
    selected_variant_sku: str | None = Field(default=None, description="Selected variant SKU")
    active_quote_id: uuid.UUID | None = Field(default=None, description="Active PriceQuote ID")
    active_quote_total_paise: int | None = Field(
        default=None, ge=0, description="Active quote total paise"
    )
    active_order_id: uuid.UUID | None = Field(default=None, description="Created Order ID")
    rzp_order_id: str | None = Field(default=None, description="Razorpay order ID")
    history: list[BuyerFlowStep] = Field(
        default_factory=list, description="Ordered flow execution history"
    )


class BuyerFlowResult(BaseModel):
    """End result returned upon completing or failing an AI buyer commerce flow."""

    model_config = ConfigDict(extra="forbid")

    is_success: bool = Field(..., description="Whether the flow reached COMPLETED state")
    final_state: str = Field(..., description="Final buyer commerce state or failure code")
    order_id: uuid.UUID | None = Field(default=None, description="Settled Order ID if created")
    quote_id: uuid.UUID | None = Field(default=None, description="Final Quote ID")
    amount_paise: int | None = Field(default=None, ge=0, description="Final settled amount")
    currency: str = Field(default="INR", description="Currency standard")
    payment_status: str | None = Field(default=None, description="Settlement state (PAID, etc.)")
    error_code: str | None = Field(default=None, description="Error code if flow failed")
    error_message: str | None = Field(default=None, description="Error message if flow failed")
    step_count: int = Field(..., ge=0, description="Total capability steps executed")
    history: list[BuyerFlowStep] = Field(
        default_factory=list, description="Step-by-step audit record"
    )
