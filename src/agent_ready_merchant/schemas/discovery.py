"""Discovery Network Pydantic schemas.

Adheres strictly to Phase 9 specifications:
- Strict Pydantic models with extra="forbid"
- Integer paise representation for all monetary values (INV-FIN-01)
- Explicit allowlist of safe public metadata (zero secrets, zero private policies)
- Bounded buyer discovery intent schemas with overflow protection
- Explainable reason codes for deterministic ranking
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class DiscoverabilityState(enum.StrEnum):
    """Discoverability state of a merchant."""

    PRIVATE = "PRIVATE"
    DISCOVERABLE = "DISCOVERABLE"
    PAUSED = "PAUSED"
    SUSPENDED = "SUSPENDED"


class PublicCapabilityNode(BaseModel):
    """Descriptive node in the public capability graph."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Canonical capability identifier")
    protocol_version: str = Field("1.0.0", description="Supported protocol version")
    classification: Literal["READ_ONLY", "TRANSIENT_STATE", "PRIVILEGED_FINANCIAL"] = Field(
        ..., description="Coarse side-effect classification"
    )
    side_effect_classification: str = Field(..., description="Description of side-effects")
    monetary_impact_classification: str = Field(
        ..., description="Description of monetary operations involved"
    )
    authorization_requirement: str = Field(
        ..., description="Authorization model required for invocation"
    )
    approval_requirement: str = Field(
        ..., description="Human-in-the-loop or policy approval requirement"
    )
    idempotency_requirement: bool = Field(
        ..., description="Whether invocation requires an idempotency key"
    )
    supported_adapters: list[str] = Field(
        default_factory=lambda: ["ACP", "REST"],
        description="Supported wire protocol adapters",
    )
    coarse_availability: Literal["AVAILABLE", "RESTRICTED", "UNAVAILABLE"] = Field(
        "AVAILABLE", description="Coarse availability signal"
    )


class PublicCapabilityGraphResponse(BaseModel):
    """Descriptive capability graph response."""

    model_config = ConfigDict(extra="forbid")

    capabilities: list[PublicCapabilityNode] = Field(
        ..., description="List of exposed capabilities"
    )
    schema_version: str = Field("1.0.0", description="Capability graph schema version")


class PublicProductSummary(BaseModel):
    """Safe public summary of a merchant's product for discovery."""

    model_config = ConfigDict(extra="forbid")

    product_sku: str = Field(..., description="Public merchant-scoped product SKU")
    title: str = Field(..., description="Sanitized product title")
    category: str | None = Field(default=None, description="Product category")
    description: str | None = Field(default=None, description="Public product description")
    price_range_paise: dict[str, int] = Field(
        ...,
        description=(
            "Non-binding price range in integer paise. Authoritative only at transaction time."
        ),
    )
    in_stock: bool = Field(..., description="Coarse availability flag")
    attributes: dict[str, Any] = Field(
        default_factory=dict, description="Safe allowlisted product attributes"
    )


class PublicMerchantProfile(BaseModel):
    """Safe, versioned public discovery representation of a merchant."""

    model_config = ConfigDict(extra="forbid")

    public_id: str = Field(..., description="Opaque public discovery identifier")
    slug: str = Field(..., description="Merchant store slug")
    display_name: str = Field(..., description="Merchant brand display name")
    category: str | None = Field(default=None, description="Primary store category")
    description: str | None = Field(default=None, description="Public store summary")
    discovery_tags: list[str] = Field(default_factory=list, description="Public discovery keywords")
    safe_product_summaries: list[PublicProductSummary] = Field(
        default_factory=list, description="Allowlisted product summaries"
    )
    supported_currencies: list[str] = Field(
        default_factory=lambda: ["INR"], description="Supported currency codes"
    )
    price_range_paise: dict[str, int] = Field(
        ...,
        description="Overall catalog non-binding price range in integer paise.",
    )
    safe_delivery_regions: list[str] = Field(
        default_factory=list, description="Authoritative supported delivery regions"
    )
    inventory_summary: str = Field(
        default="AVAILABLE",
        description="Coarse inventory state (IN_STOCK, LOW_STOCK, OUT_OF_STOCK)",
    )
    negotiation_supported: bool = Field(
        default=False, description="Whether merchant policy allows AI buyer price negotiation"
    )
    checkout_available: bool = Field(
        default=True, description="Whether checkout capability is active and available"
    )
    supported_canonical_capabilities: list[str] = Field(
        default_factory=list, description="List of canonical capabilities supported"
    )
    supported_protocol_versions: list[str] = Field(
        default_factory=lambda: ["ACP/1.0", "REST/1.0"],
        description="Supported wire protocols and versions",
    )
    discovery_schema_version: str = Field(default="1.0.0", description="Discovery schema version")
    profile_version: int = Field(default=1, description="Sequential merchant profile version")
    updated_at: str = Field(..., description="ISO 8601 timestamp of last profile refresh")
    verified_trust_signals: list[str] = Field(
        default_factory=list, description="Coarse verified platform trust signals"
    )


class BuyerDiscoveryIntent(BaseModel):
    """Strict, bounded buyer discovery search intent.

    All text fields are treated as untrusted search strings.
    Prompt injection payloads are treated as search text only.
    """

    model_config = ConfigDict(extra="forbid")

    query: str | None = Field(
        default=None,
        max_length=200,
        description="Search query or product title keywords",
    )
    category: str | None = Field(
        default=None,
        max_length=100,
        description="Target category filter",
    )
    product_sku: str | None = Field(
        default=None,
        max_length=100,
        description="Specific public merchant-scoped product SKU if known",
    )
    maximum_budget_paise: int | None = Field(
        default=None,
        ge=0,
        le=100_000_000,
        description="Maximum budget per unit or total in integer paise (₹1,00,000 max)",
    )
    currency: str = Field(
        default="INR",
        max_length=3,
        description="Requested currency code (default: INR)",
    )
    quantity: int = Field(
        default=1,
        ge=1,
        le=1000,
        description="Desired quantity (bounded between 1 and 1000)",
    )
    required_attributes: dict[str, str] = Field(
        default_factory=dict,
        description="Key-value product attributes required (e.g. size, color)",
    )
    delivery_region: str | None = Field(
        default=None,
        max_length=100,
        description="Delivery country, state, or region code",
    )
    delivery_deadline: datetime | None = Field(
        default=None,
        description="Desired delivery deadline",
    )
    negotiation_preference: str | None = Field(
        default=None,
        pattern="^(WANTED|NOT_WANTED|INDIFFERENT)$",
        description="Buyer preference for negotiation",
    )
    required_capabilities: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="Capabilities that merchant must support",
    )
    merchant_preferences: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="Safe preference tags",
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=50,
        description="Maximum discovery results in this bounded page",
    )
    cursor: str | None = Field(
        default=None,
        max_length=100,
        description="Deterministic continuation cursor from a previous discovery response",
    )


class DiscoveryMatchResult(BaseModel):
    """A single matched merchant and relevant product summaries."""

    model_config = ConfigDict(extra="forbid")

    merchant: PublicMerchantProfile = Field(..., description="Public merchant profile")
    matching_products: list[PublicProductSummary] = Field(
        default_factory=list, description="Matching products for this merchant"
    )
    rank: int = Field(..., description="Deterministic rank position (1-indexed)")
    score: int = Field(..., description="Deterministic match score integer")
    reason_codes: list[str] = Field(
        default_factory=list,
        description="Explainable reason codes for match and ranking",
    )
    next_actions: list[str] = Field(
        default_factory=lambda: ["START_BUYER_SESSION", "GET_PRODUCT", "GET_QUOTE"],
        description="Allowed next canonical commerce actions",
    )


class DiscoverySearchResponse(BaseModel):
    """Deterministic search response for buyer discovery queries."""

    model_config = ConfigDict(extra="forbid")

    results: list[DiscoveryMatchResult] = Field(
        default_factory=list, description="Ranked list of eligible matches"
    )
    total_matches: int = Field(
        ..., description="Count of eligible merchants returned in this bounded page"
    )
    correlation_id: str = Field(
        ..., description="Replay-safe correlation ID for subsequent selection and handoff events"
    )
    discovery_schema_version: str = Field(default="1.0.0", description="Discovery contract version")
    next_cursor: str | None = Field(
        default=None,
        description="Continuation cursor when more eligible discovery candidates remain",
    )
    next_canonical_action: str = Field(
        default="START_BUYER_SESSION",
        description="Next authoritative action for the external buyer agent",
    )


class DiscoveryProfileLookupRequest(BaseModel):
    """Protocol-neutral public-profile lookup contract."""

    model_config = ConfigDict(extra="forbid")

    public_id: str = Field(..., min_length=1, max_length=100)


class DiscoveryHandoffRequest(BaseModel):
    """Explicit bridge from public discovery to the existing buyer-session gateway."""

    model_config = ConfigDict(extra="forbid")

    buyer_agent_identifier: str = Field(..., min_length=1, max_length=255)
    requested_capabilities: list[str] = Field(default_factory=list, max_length=10)
    duration_minutes: int = Field(default=60, ge=5, le=1440)
    auth_token_raw: str | None = Field(default=None, min_length=8, max_length=512)
    idempotency_key: str | None = Field(default=None, max_length=128)
    correlation_id: str = Field(..., min_length=1, max_length=255)
    selected_product_sku: str | None = Field(default=None, min_length=1, max_length=100)


class DiscoverabilityUpdateRequest(BaseModel):
    """Request payload to update discoverability settings (Human MERCHANT_ADMIN only)."""

    model_config = ConfigDict(extra="forbid")

    expected_profile_version: int = Field(
        ...,
        ge=1,
        description="Current discovery-profile version required for an optimistic update",
    )

    discoverability_state: str | None = Field(
        default=None,
        pattern="^(PRIVATE|DISCOVERABLE|PAUSED)$",
        description="Target discoverability status",
    )
    custom_tags: list[str] | None = Field(
        default=None,
        max_length=20,
        description="Allowlisted discovery tags",
    )
    custom_description: str | None = Field(
        default=None,
        max_length=1000,
        description="Custom public merchant description",
    )
    delivery_regions: list[str] | None = Field(
        default=None,
        max_length=50,
        description="Supported delivery regions",
    )


class DiscoverabilityStatusResponse(BaseModel):
    """Merchant control-plane discoverability management status."""

    model_config = ConfigDict(extra="forbid")

    discoverability_state: str = Field(..., description="Current discoverability state")
    profile: PublicMerchantProfile | None = Field(
        default=None, description="Safe public profile if discoverable"
    )
    metrics: dict[str, int] = Field(
        default_factory=dict, description="Authoritative discovery metrics"
    )
    public_capability_graph: list[PublicCapabilityNode] = Field(
        default_factory=list, description="Public capability graph for store"
    )
    supported_protocols: list[str] = Field(
        default_factory=lambda: ["ACP/1.0", "REST/1.0"],
        description="Supported wire protocol versions",
    )
    profile_version: int = Field(default=1, description="Profile version number")
    updated_at: str = Field(..., description="ISO 8601 timestamp of last profile update")
