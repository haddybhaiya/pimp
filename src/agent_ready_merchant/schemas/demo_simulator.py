"""Pydantic schemas for the Phase 5.3 Interactive Demo & Sandbox Simulator."""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class DemoSimulationStepRequest(BaseModel):
    """Request payload to trigger an automated or stepped agent simulation."""

    model_config = ConfigDict(extra="forbid")

    scenario: Literal[
        "STANDARD_AUTO_COMMERCE",
        "HITL_ESCALATION_COMMERCE",
        "PAYMENT_RECONCILIATION",
    ] = Field(
        default="STANDARD_AUTO_COMMERCE",
        description="The deterministic commerce scenario to execute.",
    )
    sku: str | None = Field(
        default=None,
        description="Optional SKU to purchase. Defaults to standard demo product.",
    )
    quantity: int = Field(default=1, ge=1, le=10)
    target_discount_pct: float | None = Field(
        default=None,
        ge=0.0,
        le=50.0,
        description="Requested discount rate for negotiation.",
    )


class SimulationTraceStep(BaseModel):
    """An individual execution trace step in the simulation flow."""

    model_config = ConfigDict(extra="forbid")

    step_number: int
    actor: str
    action: str
    status: Literal["SUCCESS", "ESCALATED", "REJECTED", "SETTLED", "RECONCILED"]
    summary: str
    details: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime


class DemoSimulationStepResponse(BaseModel):
    """Authoritative response detailing the deterministic simulation execution."""

    model_config = ConfigDict(extra="forbid")

    scenario: str
    session_id: uuid.UUID
    quote_id: uuid.UUID | None = None
    approval_id: uuid.UUID | None = None
    order_id: uuid.UUID | None = None
    rzp_order_id: str | None = None
    rzp_payment_id: str | None = None
    status: str
    subtotal_paise: int = Field(..., ge=0)
    discount_paise: int = Field(..., ge=0)
    total_paise: int = Field(..., ge=0)
    policy_verdict: str
    policy_rule_code: str | None = None
    policy_hash: str
    audit_event_hash: str
    steps: list[SimulationTraceStep] = Field(default_factory=list)
    message: str


class DemoSeedResponse(BaseModel):
    """Response returned when initializing or resetting sandbox demo state."""

    model_config = ConfigDict(extra="forbid")

    merchant_id: uuid.UUID
    products_seeded: int
    policies_configured: bool
    message: str
