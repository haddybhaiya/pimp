"""Merchant authentication and onboarding schemas for Phase 5.1 web foundation."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from agent_ready_merchant.gateway.constants import (
    COMMERCE_PROTOCOL_VERSION,
    MAX_64BIT_INT,
)


class MerchantSignupRequest(BaseModel):
    """Request payload for merchant signup and store creation."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=2, max_length=255, description="Merchant store name")
    slug: str = Field(
        ...,
        min_length=2,
        max_length=100,
        pattern=r"^[a-z0-9-]+$",
        description="Unique store URL slug (lowercase alphanumeric and hyphens)",
    )
    email: EmailStr = Field(..., description="Primary merchant admin email")
    rzp_key_id: str = Field(
        default="rzp_test_placeholder",
        min_length=3,
        max_length=128,
        description="Razorpay API Key ID",
    )
    currency: Literal["INR"] = Field(default="INR", description="Store operating currency")
    initial_autonomy_level: int = Field(
        default=1,
        ge=0,
        le=2,
        description="0: Read-Only, 1: Bounded Autonomous, 2: Supervised HITL",
    )
    max_discount_percentage: float = Field(
        default=15.0, ge=0.0, le=50.0, description="Max allowed discount percentage"
    )
    min_margin_percentage: float = Field(
        default=20.0, ge=0.0, le=100.0, description="Minimum acceptable margin percentage"
    )
    max_single_transaction_paise: int = Field(
        default=5_000_000,
        ge=100,
        le=MAX_64BIT_INT,
        description="Maximum single transaction ceiling in paise",
    )


class MerchantLoginRequest(BaseModel):
    """Request payload for merchant portal login."""

    model_config = ConfigDict(extra="forbid")

    slug: str = Field(..., min_length=2, max_length=100, description="Merchant slug")
    rzp_key_id: str | None = Field(
        default=None,
        max_length=128,
        description="Optional API Key ID for merchant verification",
    )
    admin_token: str | None = Field(
        default=None,
        max_length=256,
        description="Required pre-existing admin token for a session refresh",
    )


class PolicySummaryItem(BaseModel):
    """Summary of active merchant policy rule configuration."""

    model_config = ConfigDict(extra="forbid")

    autonomy_level: int = Field(default=1, ge=0, le=2)
    max_discount_percentage: float = Field(default=15.0, ge=0.0, le=50.0)
    min_margin_percentage: float = Field(default=20.0, ge=0.0, le=100.0)
    max_single_transaction_paise: int = Field(default=5_000_000, ge=0)
    policy_hash: str = Field(..., description="Deterministic SHA-256 policy hash")
    protocol_version: str = Field(default=COMMERCE_PROTOCOL_VERSION)


class MerchantAuthResponse(BaseModel):
    """Authoritative response payload upon successful merchant authentication."""

    model_config = ConfigDict(extra="forbid")

    merchant_id: uuid.UUID = Field(..., description="Authoritative Merchant ID")
    name: str = Field(..., description="Merchant business name")
    slug: str = Field(..., description="Store unique slug")
    status: str = Field(..., description="Account status ('ACTIVE', 'PAUSED', 'SUSPENDED')")
    currency: str = Field(default="INR", description="Store currency")
    token: str | None = Field(
        default=None,
        description="Omitted from browser responses; stored in an HttpOnly session cookie",
    )
    expires_at: datetime = Field(..., description="Session expiration timestamp")
    onboarding_completed: bool = Field(..., description="Whether setup wizard is fully completed")
    policies: PolicySummaryItem = Field(..., description="Active policy bounds snapshot")


class MerchantSetupRequest(BaseModel):
    """Request payload to update merchant onboarding profile and policy bounds."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=2, max_length=255)
    rzp_key_id: str | None = Field(default=None, min_length=3, max_length=128)
    autonomy_level: int = Field(default=1, ge=0, le=2)
    max_discount_percentage: float = Field(default=15.0, ge=0.0, le=50.0)
    min_margin_percentage: float = Field(default=20.0, ge=0.0, le=100.0)
    max_single_transaction_paise: int = Field(default=5_000_000, ge=100, le=MAX_64BIT_INT)


class MerchantProfileResponse(BaseModel):
    """Detailed merchant profile returned for authenticated dashboard queries."""

    model_config = ConfigDict(extra="forbid")

    merchant_id: uuid.UUID = Field(..., description="Merchant UUID")
    name: str = Field(..., description="Merchant business name")
    slug: str = Field(..., description="Unique slug")
    status: str = Field(..., description="Merchant status")
    currency: str = Field(default="INR", description="Store currency")
    rzp_key_id: str = Field(..., description="Razorpay key identifier")
    onboarding_completed: bool = Field(..., description="Onboarding completion status")
    policies: PolicySummaryItem = Field(..., description="Active policy bounds")
    created_at: datetime = Field(..., description="Creation timestamp")
