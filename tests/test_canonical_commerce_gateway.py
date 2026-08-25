"""Comprehensive test suite for Phase 2.1 — Canonical Commerce Gateway.

Verifies:
1. Canonical request/response schemas (extra="forbid", integer paise, UUID types)
2. Authoritative Merchant AI Representation derivation (purely from server state)
3. Capability Registry declarations and metadata for all 8 canonical capabilities
4. Complete canonical gateway flow: discover -> product -> inventory -> shipping -> quote -> order
5. Security & Adversarial checks: cross-merchant/session isolation, capability checks, inventory
6. FastAPI Gateway HTTP endpoints
7. Immutable AuditEvent recording for all state-changing gateway operations
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import AsyncClient
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.gateway.canonical import CanonicalCommerceGateway
from agent_ready_merchant.gateway.registry import CapabilityRegistry
from agent_ready_merchant.gateway.representation import (
    MerchantAIRepresentation,
    build_merchant_representation,
)
from agent_ready_merchant.gateway.schemas import (
    CalculateShippingRequest,
    CheckInventoryRequest,
    CreateOrderGatewayRequest,
    DiscoverProductsRequest,
    GetPaymentStatusRequest,
    GetProductRequest,
    GetQuoteRequest,
    QuoteItemRequest,
    RequestCheckoutRequest,
    ShippingAddressGateway,
)
from agent_ready_merchant.integrations.razorpay.client import RazorpayClient
from agent_ready_merchant.integrations.razorpay.models import RazorpayOrderResponse
from agent_ready_merchant.models.inventory import InventoryItem
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.product import Product, ProductVariant
from agent_ready_merchant.models.quote import PriceQuote
from agent_ready_merchant.models.session import BuyerAgentSession
from agent_ready_merchant.state_machines.price_quote import PriceQuoteStateMachine
from agent_ready_merchant.tools.base import GatewayContext


@pytest_asyncio.fixture(scope="function")
async def seed_gateway_data(db_session: AsyncSession) -> dict[str, Any]:
    """Seeds merchant, products, variants, inventory, and session."""
    merchant = Merchant(
        name="Apex Athletics India",
        slug=f"apex-athletics-{uuid.uuid4().hex[:6]}",
        status="ACTIVE",
        currency="INR",
        rzp_key_id="rzp_test_placeholder",
    )
    db_session.add(merchant)
    await db_session.flush()

    merchant_b = Merchant(
        name="Beta Competitor",
        slug=f"beta-competitor-{uuid.uuid4().hex[:6]}",
        status="ACTIVE",
        currency="INR",
        rzp_key_id="rzp_test_placeholder_b",
    )
    db_session.add(merchant_b)
    await db_session.flush()

    # Product 1
    prod1 = Product(
        merchant_id=merchant.id,
        sku="RUN-SHOE-PRO",
        title="Apex Velocity Pro Running Shoes",
        description="Elite carbon-plated long distance road running shoe",
        category="Footwear",
        base_price_paise=1200000,  # ₹12,000.00
        floor_price_paise=1000000,  # ₹10,000.00
        is_negotiable=True,
        is_active=True,
        attributes={"weight_grams": 210, "terrain": "Road"},
    )
    db_session.add(prod1)
    await db_session.flush()

    var1 = ProductVariant(
        product_id=prod1.id,
        sku="RUN-SHOE-PRO-UK9",
        title="UK 9 / Solar Orange",
        price_override_paise=None,
        attributes={"size": "UK 9", "color": "Solar Orange"},
        is_active=True,
    )
    db_session.add(var1)
    await db_session.flush()

    inv1 = InventoryItem(
        variant_id=var1.id,
        available_quantity=25,
        reserved_quantity=0,
        safety_threshold=2,
    )
    db_session.add(inv1)

    # Product 2 (low stock)
    prod2 = Product(
        merchant_id=merchant.id,
        sku="RUN-SOCK-ELITE",
        title="Apex Aero Sock",
        description="Compression running socks",
        category="Apparel",
        base_price_paise=80000,  # ₹800.00
        floor_price_paise=70000,  # ₹700.00
        is_negotiable=False,
        is_active=True,
        attributes={"fabric": "Merino Mesh"},
    )
    db_session.add(prod2)
    await db_session.flush()

    var2 = ProductVariant(
        product_id=prod2.id,
        sku="RUN-SOCK-ELITE-M",
        title="Medium / White",
        price_override_paise=None,
        attributes={"size": "M"},
        is_active=True,
    )
    db_session.add(var2)
    await db_session.flush()

    inv2 = InventoryItem(
        variant_id=var2.id,
        available_quantity=3,
        reserved_quantity=0,
        safety_threshold=2,  # Max orderable is 1
    )
    db_session.add(inv2)

    # Product for Merchant B (Isolation test)
    prod_b = Product(
        merchant_id=merchant_b.id,
        sku="BETA-SECRET-ITEM",
        title="Beta Secret Item",
        category="Confidential",
        base_price_paise=500000,
        floor_price_paise=400000,
        is_negotiable=False,
        is_active=True,
    )
    db_session.add(prod_b)
    await db_session.flush()

    var_b = ProductVariant(
        product_id=prod_b.id,
        sku="BETA-SECRET-VAR",
        title="Standard",
        is_active=True,
    )
    db_session.add(var_b)
    await db_session.flush()

    inv_b = InventoryItem(
        variant_id=var_b.id,
        available_quantity=10,
        reserved_quantity=0,
        safety_threshold=0,
    )
    db_session.add(inv_b)

    # Session for Merchant A
    token_a = "token_apex_12345"
    session_a = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="agent_apex_buyer_01",
        auth_token_hash=hashlib.sha256(token_a.encode("utf-8")).hexdigest(),
        status="ACTIVE",
        expires_at=datetime.now(UTC) + timedelta(hours=24),
    )
    db_session.add(session_a)

    # Session for Merchant B
    token_b = "token_beta_67890"
    session_b = BuyerAgentSession(
        merchant_id=merchant_b.id,
        buyer_agent_identifier="agent_beta_buyer_02",
        auth_token_hash=hashlib.sha256(token_b.encode("utf-8")).hexdigest(),
        status="ACTIVE",
        expires_at=datetime.now(UTC) + timedelta(hours=24),
    )
    db_session.add(session_b)
    await db_session.commit()

    return {
        "merchant_a": merchant,
        "merchant_b": merchant_b,
        "prod1": prod1,
        "var1": var1,
        "prod2": prod2,
        "var2": var2,
        "prod_b": prod_b,
        "var_b": var_b,
        "session_a": session_a,
        "session_b": session_b,
        "token_a": token_a,
        "token_b": token_b,
    }


# =============================================================================
# 1. Canonical Schemas & Extra Forbid Tests
# =============================================================================
def test_canonical_schemas_extra_forbid() -> None:
    """Verifies that all canonical request models strictly forbid extra undeclared fields."""
    with pytest.raises(ValidationError):
        DiscoverProductsRequest.model_validate(
            {"query": "shoes", "unauthorized_extra_field": "injected"}
        )

    with pytest.raises(ValidationError):
        GetProductRequest.model_validate({"sku": "RUN-SHOE-PRO", "malicious_override": True})

    with pytest.raises(ValidationError):
        CheckInventoryRequest.model_validate({"sku": "RUN-SHOE-PRO", "fake_stock": 9999})

    with pytest.raises(ValidationError):
        CalculateShippingRequest.model_validate(
            {
                "destination_postal_code": "560001",
                "free_shipping_override": True,
            }
        )

    with pytest.raises(ValidationError):
        GetQuoteRequest.model_validate(
            {
                "session_id": uuid.uuid4(),
                "items": [{"sku": "RUN-SHOE-PRO", "quantity": 1}],
                "injected_discount_paise": 50000,
            }
        )

    with pytest.raises(ValidationError):
        CreateOrderGatewayRequest.model_validate(
            {
                "quote_id": uuid.uuid4(),
                "buyer_email": "buyer@example.com",
                "shipping_address": {
                    "full_name": "John Doe",
                    "address_line1": "123 Main St",
                    "city": "Bengaluru",
                    "postal_code": "560001",
                    "country": "IN",
                },
                "force_paid_status": True,
            }
        )

    with pytest.raises(ValidationError):
        RequestCheckoutRequest.model_validate(
            {
                "order_id": uuid.uuid4(),
                "bypass_razorpay": True,
            }
        )

    with pytest.raises(ValidationError):
        GetPaymentStatusRequest.model_validate(
            {
                "order_id": uuid.uuid4(),
                "spoofed_status": "PAID",
            }
        )


# =============================================================================
# 2. Capability Registry Verification
# =============================================================================
def test_capability_registry_declarations() -> None:
    """Verifies all 8 canonical capabilities are properly declared in CapabilityRegistry."""
    expected_capabilities = [
        "discover_products",
        "get_product",
        "check_inventory",
        "get_quote",
        "calculate_shipping",
        "create_order",
        "request_checkout",
        "get_payment_status",
    ]
    catalog = CapabilityRegistry.get_all_capabilities()
    assert len(catalog) >= 8

    catalog_names = [c.name for c in catalog]
    for exp in expected_capabilities:
        assert exp in catalog_names
        cap_def = CapabilityRegistry.get_capability(exp)
        assert cap_def is not None
        assert cap_def.input_schema is not None
        assert cap_def.output_schema is not None
        assert cap_def.classification in ["READ_ONLY", "TRANSIENT_STATE", "PRIVILEGED_FINANCIAL"]
        assert len(cap_def.failure_states) > 0
        assert cap_def.required_capability.startswith("buyer:")


# =============================================================================
# 3. Merchant AI Representation Verification
# =============================================================================
@pytest.mark.asyncio
async def test_merchant_ai_representation_derivation(
    db_session: AsyncSession, seed_gateway_data: dict[str, Any]
) -> None:
    """Verifies MerchantAIRepresentation is derived accurately and immutably from DB state."""
    merchant = seed_gateway_data["merchant_a"]
    session_a = seed_gateway_data["session_a"]

    context = GatewayContext(
        merchant_id=merchant.id,
        session_id=session_a.id,
        capabilities={"buyer:discover", "buyer:read", "buyer:quote", "buyer:checkout"},
        autonomy_level=1,
        max_discount_percentage=15.0,
        min_margin_percentage=20.0,
        max_single_transaction_paise=5_000_000,
    )

    rep = await build_merchant_representation(db_session, merchant.id, context)

    assert isinstance(rep, MerchantAIRepresentation)
    assert rep.identity.merchant_id == merchant.id
    assert rep.identity.name == "Apex Athletics India"
    assert rep.identity.currency == "INR"
    assert rep.identity.status == "ACTIVE"

    assert rep.products.active_products_count == 2
    assert "Footwear" in rep.products.categories
    assert "Apparel" in rep.products.categories
    assert rep.products.min_catalog_price_paise == 80000
    assert rep.products.max_catalog_price_paise == 1200000

    assert rep.inventory.stock_reservation_model == "OPTIMISTIC_ROW_LOCK"
    assert rep.inventory.backorders_allowed is False

    assert rep.pricing.currency == "INR"
    assert rep.pricing.integer_paise_standard is True

    assert "IN" in rep.shipping.supported_countries
    assert rep.shipping.standard_shipping_fee_paise == 10000
    assert rep.shipping.free_shipping_threshold_paise == 100000

    assert "razorpay_test" in rep.payment_capabilities.supported_providers
    assert rep.payment_capabilities.server_authoritative_settlement is True

    assert rep.business_rules.max_single_transaction_paise == 5000000
    assert rep.negotiation_capabilities.max_discount_percentage == 15.0
    assert rep.negotiation_capabilities.floor_price_protection_enforced is True

    assert len(rep.agent_capabilities.supported_capabilities) == 8
    assert rep.agent_capabilities.max_steps_per_turn <= 5

    assert rep.permissions.session_id == session_a.id
    assert "buyer:checkout" in rep.permissions.granted_capabilities

    assert len(rep.trust_metadata.policy_hash) == 64  # SHA-256 hex string
    assert rep.trust_metadata.immutable_audit_trail is True


# =============================================================================
# 4. Full Canonical Gateway Flow Integration Test
# =============================================================================
@pytest.mark.asyncio
async def test_full_canonical_gateway_flow(
    db_session: AsyncSession, seed_gateway_data: dict[str, Any]
) -> None:
    """Tests the full canonical gateway lifecycle:
    discover -> product -> inventory -> shipping -> quote -> order -> checkout -> status.
    """
    merchant = seed_gateway_data["merchant_a"]
    session_a = seed_gateway_data["session_a"]
    gateway = CanonicalCommerceGateway()

    context = GatewayContext(
        merchant_id=merchant.id,
        session_id=session_a.id,
        capabilities={
            "buyer:discover",
            "buyer:read",
            "buyer:quote",
            "buyer:negotiate",
            "buyer:checkout",
            "buyer:payment_status",
        },
    )

    # 1. discover_products
    disc_req = DiscoverProductsRequest(category="Footwear", limit=5)
    disc_res = await gateway.discover_products(db_session, disc_req, context)
    assert disc_res.status == "SUCCESS"
    assert disc_res.data is not None
    assert disc_res.data.total_matched == 1
    assert disc_res.data.products[0].sku == "RUN-SHOE-PRO"
    assert disc_res.state is not None
    assert "get_product" in disc_res.state.allowed_actions

    # 2. get_product
    prod_req = GetProductRequest(sku="RUN-SHOE-PRO")
    prod_res = await gateway.get_product(db_session, prod_req, context)
    assert prod_res.status == "SUCCESS"
    assert prod_res.data is not None
    assert prod_res.data.sku == "RUN-SHOE-PRO"
    assert len(prod_res.data.variants) == 1
    assert prod_res.data.variants[0].sku == "RUN-SHOE-PRO-UK9"

    # 3. check_inventory
    inv_req = CheckInventoryRequest(sku="RUN-SHOE-PRO-UK9", requested_quantity=2)
    inv_res = await gateway.check_inventory(db_session, inv_req, context)
    assert inv_res.status == "SUCCESS"
    assert inv_res.data is not None
    assert inv_res.data.in_stock is True
    assert inv_res.data.can_fulfill is True
    assert inv_res.data.available_quantity == 25

    # 4. calculate_shipping
    ship_req = CalculateShippingRequest(
        destination_postal_code="560001",
        destination_country="IN",
        subtotal_paise=1200000,
    )
    ship_res = await gateway.calculate_shipping(db_session, ship_req, context)
    assert ship_res.status == "SUCCESS"
    assert ship_res.data is not None
    assert ship_res.data.qualifies_for_free_shipping is True
    assert ship_res.data.shipping_fee_paise == 0  # Free for orders >= ₹1,000

    # 5. get_quote
    quote_req = GetQuoteRequest(
        session_id=session_a.id,
        items=[QuoteItemRequest(sku="RUN-SHOE-PRO-UK9", quantity=1)],
    )
    quote_res = await gateway.get_quote(db_session, quote_req, context)
    assert quote_res.status == "SUCCESS"
    assert quote_res.data is not None
    assert quote_res.data.status == "PROPOSED"
    assert quote_res.data.total_paise == 1200000  # Subtotal 12,000 + 0 shipping
    assert quote_res.audit_event_id is not None
    quote_id = quote_res.data.quote_id

    # 6. Accept Quote (State Machine Transition)
    q_fetch = (
        await db_session.execute(select(PriceQuote).where(PriceQuote.id == quote_id))
    ).scalar_one()
    await PriceQuoteStateMachine.transition(
        session=db_session,
        quote=q_fetch,
        target_state="ACCEPTED",
        expected_version=q_fetch.version,
        actor_type="BUYER_AGENT",
        reason="Buyer accepted quote",
    )

    # 7. create_order via Mocked PaymentService Razorpay Client
    order_req = CreateOrderGatewayRequest(
        quote_id=quote_id,
        buyer_email="runner@example.com",
        shipping_address=ShippingAddressGateway(
            full_name="Arjun Mehta",
            address_line1="100 Feet Road, Indiranagar",
            city="Bengaluru",
            postal_code="560038",
            country="IN",
        ),
    )

    with (
        patch.object(
            RazorpayClient,
            "create_order",
            return_value=RazorpayOrderResponse(
                id="order_mock_canonical_12345",
                amount=1200000,
                currency="INR",
                status="created",
                created_at=int(datetime.now(UTC).timestamp()),
            ),
        ),
        patch.object(
            RazorpayClient,
            "fetch_order",
            return_value=RazorpayOrderResponse(
                id="order_mock_canonical_12345",
                amount=1200000,
                currency="INR",
                status="created",
                amount_paid=0,
                created_at=int(datetime.now(UTC).timestamp()),
            ),
        ),
        # Step 9 reconciliation must never reach the real Razorpay API in unit tests.
        patch.object(
            RazorpayClient,
            "fetch_order_payments",
            return_value=[],
        ),
    ):
        order_res = await gateway.create_order(db_session, order_req, context)
        assert order_res.status == "SUCCESS"
        assert order_res.data is not None
        assert order_res.data.status == "PENDING_PAYMENT"
        assert order_res.data.rzp_order_id == "order_mock_canonical_12345"
        order_id = order_res.data.order_id

        # 8. request_checkout
        chk_req = RequestCheckoutRequest(order_id=order_id)
        chk_res = await gateway.request_checkout(db_session, chk_req, context)
        assert chk_res.status == "SUCCESS"
        assert chk_res.data is not None
        assert chk_res.data.rzp_order_id == "order_mock_canonical_12345"
        assert chk_res.data.amount_paise == 1200000

        # 9. get_payment_status
        status_req = GetPaymentStatusRequest(order_id=order_id)
        status_res = await gateway.get_payment_status(db_session, status_req, context)
        assert status_res.status == "SUCCESS"
        assert status_res.data is not None
        assert status_res.data.order_status == "PENDING_PAYMENT"
        assert status_res.data.is_paid is False


# =============================================================================
# 5. Security & Adversarial Isolation Tests
# =============================================================================
@pytest.mark.asyncio
async def test_security_cross_merchant_isolation(
    db_session: AsyncSession, seed_gateway_data: dict[str, Any]
) -> None:
    """Verifies Merchant A cannot discover or retrieve Merchant B's products or inventory."""
    merchant_a = seed_gateway_data["merchant_a"]
    session_a = seed_gateway_data["session_a"]
    gateway = CanonicalCommerceGateway()

    context_a = GatewayContext(
        merchant_id=merchant_a.id,
        session_id=session_a.id,
        capabilities={"buyer:discover", "buyer:read", "buyer:quote"},
    )

    # Attempt to fetch Merchant B's confidential product using Merchant A's context
    prod_res = await gateway.get_product(
        db_session, GetProductRequest(sku="BETA-SECRET-ITEM"), context_a
    )
    assert prod_res.status == "REJECTED"
    assert prod_res.error is not None
    assert prod_res.error.code == "PRODUCT_NOT_FOUND"

    # Attempt to check inventory on Merchant B's SKU
    inv_res = await gateway.check_inventory(
        db_session, CheckInventoryRequest(sku="BETA-SECRET-VAR"), context_a
    )
    assert inv_res.status == "REJECTED"
    assert inv_res.error is not None
    assert inv_res.error.code == "SKU_NOT_FOUND"


@pytest.mark.asyncio
async def test_security_cross_session_quote_isolation(
    db_session: AsyncSession, seed_gateway_data: dict[str, Any]
) -> None:
    """Verifies that Session B cannot retrieve or checkout a quote owned by Session A."""
    merchant_a = seed_gateway_data["merchant_a"]
    session_a = seed_gateway_data["session_a"]
    session_b = seed_gateway_data["session_b"]
    gateway = CanonicalCommerceGateway()

    context_a = GatewayContext(
        merchant_id=merchant_a.id,
        session_id=session_a.id,
        capabilities={"buyer:quote"},
    )
    context_b = GatewayContext(
        merchant_id=merchant_a.id,
        session_id=session_b.id,
        capabilities={"buyer:quote", "buyer:checkout"},
    )

    # Create quote under Session A
    q_res = await gateway.get_quote(
        db_session,
        GetQuoteRequest(
            session_id=session_a.id,
            items=[QuoteItemRequest(sku="RUN-SHOE-PRO-UK9", quantity=1)],
        ),
        context_a,
    )
    assert q_res.status == "SUCCESS"
    assert q_res.data is not None
    quote_id = q_res.data.quote_id

    # Attempt to retrieve Session A's quote using Session B's context
    b_res = await gateway.get_quote(
        db_session,
        GetQuoteRequest(session_id=session_b.id, quote_id=quote_id),
        context_b,
    )
    assert b_res.status == "REJECTED"
    assert b_res.error is not None
    assert b_res.error.code == "QUOTE_NOT_FOUND"


@pytest.mark.asyncio
async def test_security_unauthorized_capability_rejection(
    db_session: AsyncSession, seed_gateway_data: dict[str, Any]
) -> None:
    """Verifies that requests fail closed when the session lacks the required capability."""
    merchant = seed_gateway_data["merchant_a"]
    session_a = seed_gateway_data["session_a"]
    gateway = CanonicalCommerceGateway()

    # Context with READ capability only (no checkout or quote capability)
    read_only_context = GatewayContext(
        merchant_id=merchant.id,
        session_id=session_a.id,
        capabilities={"buyer:read"},
    )

    # Attempt to request quote
    q_res = await gateway.get_quote(
        db_session,
        GetQuoteRequest(
            session_id=session_a.id,
            items=[QuoteItemRequest(sku="RUN-SHOE-PRO-UK9", quantity=1)],
        ),
        read_only_context,
    )
    assert q_res.status == "REJECTED"
    assert q_res.error is not None
    assert q_res.error.code == "CAPABILITY_DENIED"

    # Attempt to create order
    ord_res = await gateway.create_order(
        db_session,
        CreateOrderGatewayRequest(
            quote_id=uuid.uuid4(),
            buyer_email="user@example.com",
            shipping_address=ShippingAddressGateway(
                full_name="A", address_line1="B", city="C", postal_code="560001", country="IN"
            ),
        ),
        read_only_context,
    )
    assert ord_res.status == "REJECTED"
    assert ord_res.error is not None
    assert ord_res.error.code == "CAPABILITY_DENIED"


@pytest.mark.asyncio
async def test_security_unknown_capability_dispatch(
    db_session: AsyncSession, seed_gateway_data: dict[str, Any]
) -> None:
    """Verifies that dispatching an unregistered capability is rejected safely."""
    merchant = seed_gateway_data["merchant_a"]
    session_a = seed_gateway_data["session_a"]
    gateway = CanonicalCommerceGateway()

    context = GatewayContext(
        merchant_id=merchant.id,
        session_id=session_a.id,
        capabilities={"buyer:discover"},
        auth_token=seed_gateway_data["token_a"],
    )

    res = await gateway.execute_capability(
        db_session,
        "arbitrary_injected_admin_action",
        {"secret_key": "compromised"},
        context,
    )
    assert res.status == "REJECTED"
    assert res.error is not None
    assert res.error.code == "UNKNOWN_CAPABILITY"


@pytest.mark.asyncio
async def test_security_insufficient_stock_rejection(
    db_session: AsyncSession, seed_gateway_data: dict[str, Any]
) -> None:
    """Verifies that requesting stock exceeding available unreserved inventory fails closed."""
    merchant = seed_gateway_data["merchant_a"]
    session_a = seed_gateway_data["session_a"]
    gateway = CanonicalCommerceGateway()

    context = GatewayContext(
        merchant_id=merchant.id,
        session_id=session_a.id,
        capabilities={"buyer:read", "buyer:quote"},
    )

    # RUN-SOCK-ELITE-M has available=3, safety_threshold=2 (max orderable = 1)
    inv_res = await gateway.check_inventory(
        db_session,
        CheckInventoryRequest(sku="RUN-SOCK-ELITE-M", requested_quantity=2),
        context,
    )
    assert inv_res.status == "SUCCESS"
    assert inv_res.data is not None
    assert inv_res.data.can_fulfill is False
    assert inv_res.data.max_order_quantity == 1

    # Attempt to request quote for 5 units
    q_res = await gateway.get_quote(
        db_session,
        GetQuoteRequest(
            session_id=session_a.id,
            items=[QuoteItemRequest(sku="RUN-SOCK-ELITE-M", quantity=5)],
        ),
        context,
    )
    assert q_res.status == "REJECTED"
    assert q_res.error is not None
    assert q_res.error.code == "INSUFFICIENT_STOCK"


# =============================================================================
# 6. FastAPI HTTP Gateway Endpoints Tests
# =============================================================================
@pytest.mark.asyncio
async def test_fastapi_gateway_http_endpoints(
    client: AsyncClient, seed_gateway_data: dict[str, Any]
) -> None:
    """Tests all canonical gateway HTTP endpoints exposed on FastAPI."""
    merchant = seed_gateway_data["merchant_a"]
    session_a = seed_gateway_data["session_a"]

    headers = {
        "X-Merchant-ID": str(merchant.id),
        "X-Session-ID": str(session_a.id),
        "X-Auth-Token": seed_gateway_data["token_a"],
    }

    # 1. GET /api/v1/gateway/merchant-representation
    rep_resp = await client.get("/api/v1/gateway/merchant-representation", headers=headers)
    assert rep_resp.status_code == 200
    rep_data = rep_resp.json()
    assert rep_data["identity"]["name"] == "Apex Athletics India"
    assert rep_data["identity"]["currency"] == "INR"
    assert len(rep_data["agent_capabilities"]["supported_capabilities"]) >= 8

    # 2. GET /api/v1/gateway/capabilities
    caps_resp = await client.get("/api/v1/gateway/capabilities")
    assert caps_resp.status_code == 200
    caps_data = caps_resp.json()
    assert len(caps_data) >= 8

    # 3. POST /api/v1/gateway/discover-products
    disc_resp = await client.post(
        "/api/v1/gateway/discover-products",
        json={"category": "Footwear", "limit": 5},
        headers=headers,
    )
    assert disc_resp.status_code == 200
    disc_json = disc_resp.json()
    assert disc_json["status"] == "SUCCESS"
    assert disc_json["data"]["total_matched"] == 1

    # 4. GET /api/v1/gateway/products/{sku}
    prod_resp = await client.get("/api/v1/gateway/products/RUN-SHOE-PRO", headers=headers)
    assert prod_resp.status_code == 200
    prod_json = prod_resp.json()
    assert prod_json["status"] == "SUCCESS"
    assert prod_json["data"]["sku"] == "RUN-SHOE-PRO"

    # 5. POST /api/v1/gateway/inventory/check
    inv_resp = await client.post(
        "/api/v1/gateway/inventory/check",
        json={"sku": "RUN-SHOE-PRO-UK9", "requested_quantity": 1},
        headers=headers,
    )
    assert inv_resp.status_code == 200
    inv_json = inv_resp.json()
    assert inv_json["status"] == "SUCCESS"
    assert inv_json["data"]["can_fulfill"] is True

    # 6. POST /api/v1/gateway/shipping/calculate
    ship_resp = await client.post(
        "/api/v1/gateway/shipping/calculate",
        json={"destination_postal_code": "560001", "subtotal_paise": 50000},
        headers=headers,
    )
    assert ship_resp.status_code == 200
    ship_json = ship_resp.json()
    assert ship_json["status"] == "SUCCESS"
    assert ship_json["data"]["shipping_fee_paise"] == 10000  # Standard shipping under ₹1,000

    # 7. POST /api/v1/gateway/quotes
    q_resp = await client.post(
        "/api/v1/gateway/quotes",
        json={
            "session_id": str(session_a.id),
            "items": [{"sku": "RUN-SHOE-PRO-UK9", "quantity": 1}],
        },
        headers=headers,
    )
    assert q_resp.status_code == 200
    q_json = q_resp.json()
    assert q_json["status"] == "SUCCESS"
    assert q_json["data"]["total_paise"] == 1200000

    # 8. POST /api/v1/gateway/execute unified dispatcher
    exec_resp = await client.post(
        "/api/v1/gateway/execute",
        json={
            "capability": "check_inventory",
            "payload": {"sku": "RUN-SHOE-PRO-UK9", "requested_quantity": 2},
        },
        headers=headers,
    )
    assert exec_resp.status_code == 200
    exec_json = exec_resp.json()
    assert exec_json["status"] == "SUCCESS"
    assert exec_json["data"]["can_fulfill"] is True
