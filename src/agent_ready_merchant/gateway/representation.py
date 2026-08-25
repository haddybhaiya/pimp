"""Authoritative Merchant AI Representation builder.

Adheres strictly to Phase 2.1 specifications:
- Derives entirely from authoritative server and database state
- Client and LLM inputs NEVER define or override merchant capabilities or boundaries
- Strict Pydantic models with extra="forbid"
"""

from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.config import get_settings
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.policy import PolicyRule
from agent_ready_merchant.models.product import Product
from agent_ready_merchant.tools.base import GatewayContext


class MerchantIdentityInfo(BaseModel):
    """Authoritative merchant identity and tenant boundaries."""

    model_config = ConfigDict(extra="forbid")

    merchant_id: uuid.UUID = Field(..., description="Unique merchant UUID")
    name: str = Field(..., description="Legal merchant business name")
    slug: str = Field(..., description="Unique URL slug")
    status: str = Field(..., description="Merchant operational status (ACTIVE, PAUSED, SUSPENDED)")
    currency: str = Field(default="INR", description="Standard operating currency")
    is_verified: bool = Field(default=True, description="Whether merchant account is verified")


class CatalogProductsSummary(BaseModel):
    """Authoritative catalog overview for buyer discovery."""

    model_config = ConfigDict(extra="forbid")

    active_products_count: int = Field(..., ge=0, description="Total active catalog products")
    categories: list[str] = Field(default_factory=list, description="Available product categories")
    min_catalog_price_paise: int | None = Field(
        default=None, description="Lowest active product price in paise"
    )
    max_catalog_price_paise: int | None = Field(
        default=None, description="Highest active product price in paise"
    )


class InventoryCapabilityInfo(BaseModel):
    """Authoritative inventory tracking and reservation policies."""

    model_config = ConfigDict(extra="forbid")

    stock_reservation_model: str = Field(
        default="OPTIMISTIC_ROW_LOCK", description="Concurrency control model for inventory"
    )
    backorders_allowed: bool = Field(
        default=False, description="Whether out-of-stock items can be purchased"
    )
    safety_threshold_active: bool = Field(
        default=True, description="Whether merchant enforces safety buffer quantities"
    )
    reservation_ttl_minutes: int = Field(
        default=15, description="Minutes reserved inventory is held before quote expiration"
    )


class PricingStandardsInfo(BaseModel):
    """Authoritative pricing rules and currency standards."""

    model_config = ConfigDict(extra="forbid")

    currency: str = Field(default="INR", description="Currency standard (INR)")
    integer_paise_standard: bool = Field(
        default=True, description="Strict 64-bit integer paise arithmetic enforced"
    )
    tax_inclusive: bool = Field(
        default=True, description="Whether displayed prices include all applicable taxes"
    )


class ShippingPolicyInfo(BaseModel):
    """Authoritative shipping and geographical fulfillment boundaries."""

    model_config = ConfigDict(extra="forbid")

    supported_countries: list[str] = Field(
        default_factory=lambda: ["IN"],
        description="List of supported destination ISO country codes",
    )
    standard_shipping_fee_paise: int = Field(
        default=10_000, ge=0, description="Standard flat shipping charge in paise (₹100)"
    )
    free_shipping_threshold_paise: int = Field(
        default=100_000, ge=0, description="Order subtotal qualifying for free shipping (₹1,000)"
    )
    estimated_delivery_days: int = Field(
        default=3, ge=1, description="Standard logistics fulfillment timeline"
    )


class PaymentCapabilitiesInfo(BaseModel):
    """Authoritative payment gateway configuration and accepted methods."""

    model_config = ConfigDict(extra="forbid")

    supported_providers: list[str] = Field(
        default_factory=lambda: ["razorpay_test"], description="Payment integration providers"
    )
    supported_methods: list[str] = Field(
        default_factory=lambda: ["upi", "card", "netbanking", "wallet"],
        description="Supported buyer payment instruments",
    )
    server_authoritative_settlement: bool = Field(
        default=True,
        description="Settlement verified via cryptographic HMAC webhooks or server fetch",
    )
    capture_mode: str = Field(default="AUTOMATIC", description="Payment capture authorization mode")


class BusinessRulesInfo(BaseModel):
    """Authoritative operational limits and security boundaries."""

    model_config = ConfigDict(extra="forbid")

    max_single_transaction_paise: int = Field(
        default=5_000_000, description="Maximum single order monetary cap (₹50,000 in paise)"
    )
    default_quote_ttl_minutes: int = Field(
        default=15, description="Validity period for price quotes in minutes"
    )
    session_rate_limit_per_minute: int = Field(
        default=20, description="Rate limit on API requests per buyer session"
    )
    max_active_quotes_per_buyer: int = Field(
        default=3, description="Maximum concurrent unexpired quotes allowed per buyer"
    )


class NegotiationCapabilitiesInfo(BaseModel):
    """Authoritative negotiation limits and policy engine parameters."""

    model_config = ConfigDict(extra="forbid")

    negotiation_enabled: bool = Field(
        default=True, description="Whether merchant permits AI-driven price negotiations"
    )
    max_discount_percentage: float = Field(
        default=15.0, ge=0.0, le=100.0, description="Ceiling discount percentage allowed"
    )
    min_margin_percentage: float = Field(
        default=20.0, ge=0.0, description="Minimum required margin percentage above unit cost"
    )
    floor_price_protection_enforced: bool = Field(
        default=True, description="Strict SKU floor price mathematical guarantee (INV-FIN-02)"
    )
    autonomy_level: int = Field(
        default=1,
        ge=0,
        le=2,
        description="Merchant autonomy level (0: Read-Only, 1: Auto, 2: HITL)",
    )
    escalation_required_above_threshold: bool = Field(
        default=True, description="Whether exceeding bounds triggers human approval"
    )


class AgentCapabilitiesInfo(BaseModel):
    """Capabilities and execution constraints exposed to AI agents."""

    model_config = ConfigDict(extra="forbid")

    supported_capabilities: list[str] = Field(
        default_factory=lambda: [
            "discover_products",
            "get_product",
            "check_inventory",
            "get_quote",
            "calculate_shipping",
            "create_order",
            "request_checkout",
            "get_payment_status",
        ],
        description="List of canonical gateway capabilities",
    )
    max_steps_per_turn: int = Field(default=5, ge=1, le=5, description="Bounded step limit")
    turn_timeout_seconds: int = Field(
        default=15, ge=1, le=30, description="Turn deadline in seconds"
    )
    max_context_tokens: int = Field(default=8192, description="Maximum conversation context budget")


class SessionPermissionsInfo(BaseModel):
    """Active security context and granted capabilities for the caller."""

    model_config = ConfigDict(extra="forbid")

    session_id: uuid.UUID | None = Field(
        default=None, description="Active session ID if authenticated"
    )
    granted_capabilities: list[str] = Field(
        default_factory=list, description="Explicit capabilities granted to this session"
    )
    role: str = Field(default="BUYER_AGENT", description="Caller security role")


class TrustAuditMetadata(BaseModel):
    """Verification and immutable audit trail integrity metadata."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field(
        default="2.1.0", description="Gateway representation schema version"
    )
    policy_hash: str = Field(..., description="Cryptographic SHA-256 hash of active merchant rules")
    immutable_audit_trail: bool = Field(
        default=True, description="Strict append-only SHA-256 hash-chained ledger (INV-STA-05)"
    )
    hash_chain_algorithm: str = Field(default="SHA-256", description="Ledger chaining algorithm")


class MerchantAIRepresentation(BaseModel):
    """Authoritative, complete merchant profile and capability contract for AI buyers."""

    model_config = ConfigDict(extra="forbid")

    identity: MerchantIdentityInfo = Field(..., description="Merchant identity")
    products: CatalogProductsSummary = Field(..., description="Catalog products overview")
    inventory: InventoryCapabilityInfo = Field(..., description="Inventory policies")
    pricing: PricingStandardsInfo = Field(..., description="Pricing and currency standards")
    shipping: ShippingPolicyInfo = Field(..., description="Shipping policies")
    payment_capabilities: PaymentCapabilitiesInfo = Field(..., description="Payment instruments")
    business_rules: BusinessRulesInfo = Field(..., description="Operational rules and limits")
    negotiation_capabilities: NegotiationCapabilitiesInfo = Field(
        ..., description="Negotiation constraints"
    )
    agent_capabilities: AgentCapabilitiesInfo = Field(
        ..., description="Agent execution constraints"
    )
    permissions: SessionPermissionsInfo = Field(..., description="Active session permissions")
    trust_metadata: TrustAuditMetadata = Field(..., description="Trust and audit metadata")


async def build_merchant_representation(
    session: AsyncSession,
    merchant_id: uuid.UUID,
    context: GatewayContext | None = None,
) -> MerchantAIRepresentation:
    """Derives a complete, authoritative MerchantAIRepresentation from database and server state."""
    settings = get_settings()

    # 1. Fetch Authoritative Merchant Entity
    stmt = select(Merchant).where(Merchant.id == merchant_id)
    merchant = (await session.execute(stmt)).scalar_one_or_none()
    if not merchant:
        raise ValueError(f"Merchant with ID '{merchant_id}' not found")

    # 2. Derive Catalog Overview from Database
    prod_stmt = select(
        func.count(Product.id),
        func.min(Product.base_price_paise),
        func.max(Product.base_price_paise),
    ).where(Product.merchant_id == merchant_id, Product.is_active.is_(True))
    prod_res = (await session.execute(prod_stmt)).one()
    active_count, min_price, max_price = prod_res

    cat_stmt = (
        select(Product.category)
        .where(Product.merchant_id == merchant_id, Product.is_active.is_(True))
        .distinct()
    )
    categories = list((await session.execute(cat_stmt)).scalars().all())

    # 3. Derive Policy Rules & Compute Cryptographic Policy Hash
    rule_stmt = select(PolicyRule).where(
        PolicyRule.merchant_id == merchant_id,
        PolicyRule.is_active.is_(True),
    )
    rules = list((await session.execute(rule_stmt)).scalars().all())

    autonomy = context.autonomy_level if context else settings.DEFAULT_MERCHANT_AUTONOMY_LEVEL
    max_disc = (
        context.max_discount_percentage if context else settings.DEFAULT_MAX_DISCOUNT_PERCENTAGE
    )
    min_margin = (
        context.min_margin_percentage if context else settings.DEFAULT_MIN_MARGIN_PERCENTAGE
    )
    max_tx = (
        context.max_single_transaction_paise if context else settings.MAX_SINGLE_TRANSACTION_PAISE
    )

    for r in rules:
        if r.rule_type == "MAX_DISCOUNT_PCT":
            val = r.rule_value.get("percentage") or r.rule_value.get("value")
            if val is not None:
                max_disc = float(val)
        elif r.rule_type == "MIN_MARGIN_PCT":
            val = r.rule_value.get("percentage") or r.rule_value.get("value")
            if val is not None:
                min_margin = float(val)
        elif r.rule_type == "MAX_CART_VALUE":
            val = r.rule_value.get("max_paise") or r.rule_value.get("value")
            if val is not None:
                max_tx = int(val)
        elif r.rule_type == "AUTONOMY_LEVEL":
            val = r.rule_value.get("level") or r.rule_value.get("value")
            if val is not None:
                autonomy = int(val)

    policy_dict: dict[str, Any] = {
        "max_discount_percentage": max_disc,
        "min_margin_percentage": min_margin,
        "max_single_transaction_paise": max_tx,
        "autonomy_level": autonomy,
        "currency": merchant.currency,
        "merchant_id": str(merchant.id),
    }
    policy_hash = hashlib.sha256(
        json.dumps(policy_dict, sort_keys=True).encode("utf-8")
    ).hexdigest()

    is_verified = merchant.status == "ACTIVE"

    return MerchantAIRepresentation(
        identity=MerchantIdentityInfo(
            merchant_id=merchant.id,
            name=merchant.name,
            slug=merchant.slug,
            status=merchant.status,
            currency=merchant.currency,
            is_verified=is_verified,
        ),
        products=CatalogProductsSummary(
            active_products_count=active_count or 0,
            categories=categories,
            min_catalog_price_paise=min_price,
            max_catalog_price_paise=max_price,
        ),
        inventory=InventoryCapabilityInfo(
            stock_reservation_model="OPTIMISTIC_ROW_LOCK",
            backorders_allowed=False,
            safety_threshold_active=True,
            reservation_ttl_minutes=settings.DEFAULT_QUOTE_TTL_MINUTES,
        ),
        pricing=PricingStandardsInfo(
            currency=merchant.currency,
            integer_paise_standard=True,
            tax_inclusive=True,
        ),
        shipping=ShippingPolicyInfo(
            supported_countries=["IN"],
            standard_shipping_fee_paise=10_000,
            free_shipping_threshold_paise=100_000,
            estimated_delivery_days=3,
        ),
        payment_capabilities=PaymentCapabilitiesInfo(
            supported_providers=["razorpay_test"],
            supported_methods=["upi", "card", "netbanking", "wallet"],
            server_authoritative_settlement=True,
            capture_mode="AUTOMATIC",
        ),
        business_rules=BusinessRulesInfo(
            max_single_transaction_paise=max_tx,
            default_quote_ttl_minutes=settings.DEFAULT_QUOTE_TTL_MINUTES,
            session_rate_limit_per_minute=settings.SESSION_RATE_LIMIT_PER_MINUTE,
            max_active_quotes_per_buyer=settings.MAX_ACTIVE_QUOTES_PER_BUYER,
        ),
        negotiation_capabilities=NegotiationCapabilitiesInfo(
            negotiation_enabled=(autonomy > 0),
            max_discount_percentage=max_disc,
            min_margin_percentage=min_margin,
            floor_price_protection_enforced=True,
            autonomy_level=autonomy,
            escalation_required_above_threshold=True,
        ),
        agent_capabilities=AgentCapabilitiesInfo(
            supported_capabilities=[
                "discover_products",
                "get_product",
                "check_inventory",
                "get_quote",
                "calculate_shipping",
                "create_order",
                "request_checkout",
                "get_payment_status",
            ],
            max_steps_per_turn=settings.LLM_STEP_LIMIT,
            turn_timeout_seconds=settings.LLM_TIMEOUT_SECONDS,
            max_context_tokens=8192,
        ),
        permissions=SessionPermissionsInfo(
            session_id=context.session_id if context else None,
            granted_capabilities=list(context.capabilities) if context else [],
            role="BUYER_AGENT",
        ),
        trust_metadata=TrustAuditMetadata(
            schema_version="2.1.0",
            policy_hash=policy_hash,
            immutable_audit_trail=True,
            hash_chain_algorithm="SHA-256",
        ),
    )
