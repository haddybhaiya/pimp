"""Phase 4.1: Security Boundary & Authorization Hardening Adversarial Test Suite.

Adheres strictly to Phase 4.1 specifications and INV-AGY-01 through INV-AGY-05,
INV-FIN-01 through INV-FIN-05, and INV-STA-01 through INV-STA-05:
- Buyer session authentication and constant-time token verification
- Merchant and session ownership checks on EVERY gateway capability
- Server-authoritative capability grants (never trust client-supplied permissions)
- Prevention of cross-merchant and cross-session access
- Protection of privileged financial capabilities separately from read-only capabilities
- Fail-closed behavior on missing/invalid/expired credentials
- Prevention of authorization bypass via replay, stale sessions, UUID guessing
- Authentication/authorization failures reveal zero sensitive resource existence
"""

import hashlib
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.gateway.canonical import CanonicalCommerceGateway
from agent_ready_merchant.gateway.hardening import GatewayErrorCode
from agent_ready_merchant.gateway.schemas import (
    AcceptQuoteGatewayRequest,
    CreateOrderGatewayRequest,
    GetOrderStatusRequest,
    GetPaymentStatusRequest,
    GetQuoteRequest,
    InitializeSessionRequest,
    NegotiateQuoteGatewayRequest,
    QuoteItemRequest,
    RequestCheckoutRequest,
    ShippingAddressGateway,
    TerminateSessionRequest,
)
from agent_ready_merchant.models.inventory import InventoryItem
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.order import Order
from agent_ready_merchant.models.product import Product, ProductVariant
from agent_ready_merchant.models.session import BuyerAgentSession
from agent_ready_merchant.tools.base import GatewayContext
from tests.fake_razorpay import DeterministicFakeRazorpayTransport


async def _seed_test_env(
    db_session: AsyncSession,
    base_price_paise: int = 500000,
    available_stock: int = 10,
    buyer_token: str | None = None,
    granted_capabilities: str | None = None,
) -> tuple[Merchant, BuyerAgentSession, Product, ProductVariant, InventoryItem, GatewayContext]:
    """Seeds an authoritative test environment with deterministic credentials."""
    now = datetime.now(UTC)
    uid = uuid.uuid4().hex[:8]
    actual_token = buyer_token or f"tok_{uuid.uuid4().hex}"

    merchant = Merchant(
        name=f"Merchant {uid}",
        slug=f"merchant-{uid}",
        currency="INR",
        rzp_key_id=f"rzp_test_{uid}",
        status="ACTIVE",
    )
    db_session.add(merchant)
    await db_session.flush()

    token_hash = hashlib.sha256(actual_token.encode("utf-8")).hexdigest()
    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier=f"buyer_agent_{uid}",
        auth_token_hash=token_hash,
        granted_capabilities=granted_capabilities,
        status="ACTIVE",
        expires_at=now + timedelta(hours=2),
    )
    db_session.add(session)
    await db_session.flush()

    product = Product(
        merchant_id=merchant.id,
        sku=f"PROD-{uid}",
        title=f"Secured Product {uid}",
        category="Hardening",
        base_price_paise=base_price_paise,
        floor_price_paise=int(base_price_paise * 0.8),
        is_negotiable=True,
        is_active=True,
    )
    db_session.add(product)
    await db_session.flush()

    variant = ProductVariant(
        product_id=product.id,
        sku=f"SKU-{uid}-V1",
        title="Secured Variant",
        price_override_paise=base_price_paise,
        is_active=True,
    )
    db_session.add(variant)
    await db_session.flush()

    inventory = InventoryItem(
        variant_id=variant.id,
        available_quantity=available_stock,
        reserved_quantity=0,
        safety_threshold=1,
    )
    db_session.add(inventory)
    await db_session.flush()

    context = GatewayContext(
        merchant_id=merchant.id,
        session_id=session.id,
        capabilities={
            "buyer:discover",
            "buyer:read",
            "buyer:quote",
            "buyer:negotiate",
            "buyer:checkout",
            "buyer:payment_status",
        },
        autonomy_level=1,
        auth_token=actual_token,
    )
    await db_session.commit()
    return merchant, session, product, variant, inventory, context


def _shipping_addr() -> ShippingAddressGateway:
    return ShippingAddressGateway(
        full_name="Security Auditor",
        address_line1="100 Defense Way",
        city="Bengaluru",
        postal_code="560001",
        country="IN",
    )


# =============================================================================
# 1. ADVERSARIAL: FORGED SESSION TOKEN
# =============================================================================


@pytest.mark.asyncio
async def test_forged_session_token_rejected_fail_closed(db_session: AsyncSession) -> None:
    """A buyer presenting a forged/manipulated auth token is rejected fail-closed."""
    merchant, session, product, variant, inventory, context = await _seed_test_env(
        db_session, buyer_token="real_buyer_token_abc"
    )
    gateway = CanonicalCommerceGateway()

    # Tamper with the token
    context.auth_token = "forged_malicious_token_xyz"

    resp = await gateway.execute_capability(
        db_session,
        "get_quote",
        {"session_id": str(session.id), "items": [{"sku": variant.sku, "quantity": 1}]},
        context,
    )
    assert resp.status == "REJECTED"
    assert resp.error is not None
    assert resp.error.code == GatewayErrorCode.AUTH_INVALID_CREDENTIAL.value
    assert "invalid" in resp.error.message.lower() or "token" in resp.error.message.lower()


@pytest.mark.asyncio
async def test_missing_session_token_when_required_rejected(db_session: AsyncSession) -> None:
    """When a session has an auth token hash, omitting the token entirely fails closed."""
    merchant, session, product, variant, inventory, context = await _seed_test_env(
        db_session, buyer_token="real_buyer_token_abc"
    )
    gateway = CanonicalCommerceGateway()

    # Omit the token
    context.auth_token = None

    resp = await gateway.execute_capability(
        db_session,
        "get_quote",
        {"session_id": str(session.id), "items": [{"sku": variant.sku, "quantity": 1}]},
        context,
    )
    assert resp.status == "REJECTED"
    assert resp.error is not None
    assert resp.error.code == GatewayErrorCode.AUTH_INVALID_CREDENTIAL.value


# =============================================================================
# 2. ADVERSARIAL: WRONG MERCHANT (CROSS-TENANT ISOLATION)
# =============================================================================


@pytest.mark.asyncio
async def test_wrong_merchant_rejected_fail_closed(db_session: AsyncSession) -> None:
    """Cross-tenant boundary test: Session A credentials cannot execute against Merchant B."""
    merchant_a, session_a, prod_a, var_a, inv_a, ctx_a = await _seed_test_env(db_session)
    merchant_b, session_b, prod_b, var_b, inv_b, ctx_b = await _seed_test_env(db_session)

    gateway = CanonicalCommerceGateway()

    # Target Merchant B with Session A's credentials
    ctx_tampered = GatewayContext(
        merchant_id=merchant_b.id,
        session_id=session_a.id,
        capabilities=ctx_a.capabilities,
        auth_token=ctx_a.auth_token,
    )

    resp = await gateway.execute_capability(
        db_session,
        "get_quote",
        {"session_id": str(session_a.id), "items": [{"sku": var_b.sku, "quantity": 1}]},
        ctx_tampered,
    )
    assert resp.status == "REJECTED"
    assert resp.error is not None
    assert resp.error.code == GatewayErrorCode.AUTH_SESSION_NOT_FOUND.value


@pytest.mark.asyncio
async def test_nonexistent_merchant_rejected_fail_closed(db_session: AsyncSession) -> None:
    """Calling capabilities or initializing session on a non-existent merchant UUID fails closed."""
    gateway = CanonicalCommerceGateway()
    fake_merchant_id = uuid.uuid4()

    # 1. Initialize session on non-existent merchant
    init_req = InitializeSessionRequest(
        buyer_agent_identifier="adversary",
        duration_minutes=30,
    )
    init_resp = await gateway.initialize_session(db_session, init_req, fake_merchant_id)
    assert init_resp.status == "REJECTED"
    assert init_resp.error is not None
    assert init_resp.error.code == GatewayErrorCode.AUTH_INVALID_MERCHANT.value

    # 2. Execute capability on non-existent merchant
    ctx = GatewayContext(
        merchant_id=fake_merchant_id,
        session_id=uuid.uuid4(),
        capabilities={"buyer:discover", "buyer:read"},
    )
    exec_resp = await gateway.execute_capability(db_session, "discover_products", {}, ctx)
    assert exec_resp.status == "REJECTED"
    assert exec_resp.error is not None
    assert exec_resp.error.code == GatewayErrorCode.AUTH_INVALID_MERCHANT.value


# =============================================================================
# 3. ADVERSARIAL: WRONG SESSION (CROSS-SESSION RESOURCE ISOLATION)
# =============================================================================


@pytest.mark.asyncio
async def test_cross_session_quote_and_order_access_rejected_with_uniform_not_found(
    db_session: AsyncSession,
) -> None:
    """Cross-session test: Session 2 cannot view or mutate Session 1 quotes or orders."""

    merchant, session1, prod, variant, inv, ctx1 = await _seed_test_env(
        db_session, buyer_token="token_session_1"
    )

    # Create a second distinct session for the same merchant
    now = datetime.now(UTC)
    session2 = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="buyer_agent_2",
        auth_token_hash=hashlib.sha256(b"token_session_2").hexdigest(),
        status="ACTIVE",
        expires_at=now + timedelta(hours=2),
    )
    db_session.add(session2)
    await db_session.flush()
    await db_session.commit()

    ctx2 = GatewayContext(
        merchant_id=merchant.id,
        session_id=session2.id,
        capabilities=ctx1.capabilities,
        auth_token="token_session_2",
    )

    fake_rzp = DeterministicFakeRazorpayTransport()
    gateway = CanonicalCommerceGateway(rzp_client=fake_rzp.build_client())

    # Session 1 generates and accepts a quote
    q_resp = await gateway.get_quote(
        db_session,
        GetQuoteRequest(
            session_id=session1.id, items=[QuoteItemRequest(sku=variant.sku, quantity=1)]
        ),
        ctx1,
    )
    assert q_resp.status == "SUCCESS"
    assert q_resp.data is not None
    quote1_id = q_resp.data.quote_id
    await db_session.commit()

    # Session 2 attempts to query Session 1's quote
    q2_query = await gateway.get_quote(
        db_session,
        GetQuoteRequest(session_id=session2.id, quote_id=quote1_id),
        ctx2,
    )
    assert q2_query.status == "REJECTED"
    assert q2_query.error is not None
    assert q2_query.error.code == "QUOTE_NOT_FOUND"

    # Session 2 attempts to negotiate Session 1's quote
    neg_resp = await gateway.negotiate_quote(
        db_session,
        NegotiateQuoteGatewayRequest(quote_id=quote1_id, proposed_total_paise=450000),
        ctx2,
    )
    assert neg_resp.status == "REJECTED"
    assert neg_resp.error is not None
    assert neg_resp.error.code == "QUOTE_NOT_FOUND"

    # Session 2 attempts to accept Session 1's quote
    acc_resp = await gateway.accept_quote(
        db_session,
        AcceptQuoteGatewayRequest(quote_id=quote1_id),
        ctx2,
    )
    assert acc_resp.status == "REJECTED"
    assert acc_resp.error is not None
    assert acc_resp.error.code == "QUOTE_NOT_FOUND"

    # Session 1 accepts its quote
    await gateway.accept_quote(
        db_session,
        AcceptQuoteGatewayRequest(quote_id=quote1_id),
        ctx1,
    )
    await db_session.commit()

    # Session 2 attempts to create an order from Session 1's accepted quote
    ord_resp = await gateway.create_order(
        db_session,
        CreateOrderGatewayRequest(
            quote_id=quote1_id,
            buyer_email="adversary@evil.com",
            shipping_address=_shipping_addr(),
        ),
        ctx2,
    )
    assert ord_resp.status == "REJECTED"
    assert ord_resp.error is not None
    assert ord_resp.error.code in {"ORDER_CREATION_FAILED", "QUOTE_NOT_FOUND"}

    # Session 1 successfully creates its order
    ord1_resp = await gateway.create_order(
        db_session,
        CreateOrderGatewayRequest(
            quote_id=quote1_id,
            buyer_email="legit@buyer.com",
            shipping_address=_shipping_addr(),
        ),
        ctx1,
    )
    assert ord1_resp.status == "SUCCESS"
    assert ord1_resp.data is not None
    order1_id = ord1_resp.data.order_id
    await db_session.commit()

    # Session 2 attempts to checkout Session 1's order
    chk_resp = await gateway.request_checkout(
        db_session,
        RequestCheckoutRequest(order_id=order1_id),
        ctx2,
    )
    assert chk_resp.status == "REJECTED"
    assert chk_resp.error is not None
    assert chk_resp.error.code == "ORDER_NOT_FOUND"

    # Session 2 attempts to read payment status of Session 1's order
    pay_stat = await gateway.get_payment_status(
        db_session,
        GetPaymentStatusRequest(order_id=order1_id),
        ctx2,
    )
    assert pay_stat.status == "REJECTED"
    assert pay_stat.error is not None
    assert pay_stat.error.code == "ORDER_NOT_FOUND"

    # Session 2 attempts to read order status of Session 1's order
    ord_stat = await gateway.get_order_status(
        db_session,
        GetOrderStatusRequest(order_id=order1_id),
        ctx2,
    )
    assert ord_stat.status == "REJECTED"
    assert ord_stat.error is not None
    assert ord_stat.error.code == "ORDER_NOT_FOUND"


# =============================================================================
# 4. ADVERSARIAL: FORGED CAPABILITIES (SERVER-AUTHORITATIVE GRANTS)
# =============================================================================


@pytest.mark.asyncio
async def test_forged_capabilities_cannot_elevate_privileges(db_session: AsyncSession) -> None:
    """A session granted only read permissions cannot execute checkout by forging capabilities."""
    merchant, session, product, variant, inventory, context = await _seed_test_env(
        db_session,
        buyer_token="limited_token",
        granted_capabilities="buyer:discover,buyer:read",  # Read-only session
    )
    gateway = CanonicalCommerceGateway()

    # Adversary attempts to forge execution capabilities in the request context
    context.capabilities = {
        "buyer:discover",
        "buyer:read",
        "buyer:quote",
        "buyer:negotiate",
        "buyer:checkout",
        "buyer:payment_status",
    }

    # Attempting get_quote (requires buyer:quote) fails closed
    q_resp = await gateway.execute_capability(
        db_session,
        "get_quote",
        {"session_id": str(session.id), "items": [{"sku": variant.sku, "quantity": 1}]},
        context,
    )
    assert q_resp.status == "REJECTED"
    assert q_resp.error is not None
    assert q_resp.error.code in {
        "CAPABILITY_DENIED",
        GatewayErrorCode.AUTH_UNAUTHORIZED_CAPABILITY.value,
    }

    # Attempting create_order (requires buyer:checkout) fails closed
    ord_resp = await gateway.execute_capability(
        db_session,
        "create_order",
        {
            "quote_id": str(uuid.uuid4()),
            "buyer_email": "attacker@evil.com",
            "shipping_address": _shipping_addr().model_dump(),
            "idempotency_key": "forged_cap_key_1",
        },
        context,
    )
    assert ord_resp.status == "REJECTED"
    assert ord_resp.error is not None
    assert ord_resp.error.code in {
        "CAPABILITY_DENIED",
        GatewayErrorCode.AUTH_UNAUTHORIZED_CAPABILITY.value,
    }


# =============================================================================
# 5. ADVERSARIAL: EXPIRED & TERMINATED SESSIONS
# =============================================================================


@pytest.mark.asyncio
async def test_expired_session_rejected_and_marked_in_database(db_session: AsyncSession) -> None:
    """A session past its expires_at timestamp is rejected and transitioned to EXPIRED."""
    merchant, session, product, variant, inventory, context = await _seed_test_env(
        db_session, buyer_token="expired_token"
    )
    gateway = CanonicalCommerceGateway()

    # Expire the session in database
    session.expires_at = datetime.now(UTC) - timedelta(minutes=5)
    await db_session.commit()

    resp = await gateway.execute_capability(
        db_session,
        "get_quote",
        {"session_id": str(session.id), "items": [{"sku": variant.sku, "quantity": 1}]},
        context,
    )
    assert resp.status == "REJECTED"
    assert resp.error is not None
    assert resp.error.code == GatewayErrorCode.AUTH_SESSION_EXPIRED.value

    # Verify session is transitioned in the database
    db_sess = (
        await db_session.execute(
            select(BuyerAgentSession).where(BuyerAgentSession.id == session.id)
        )
    ).scalar_one()
    assert db_sess.status == "EXPIRED"


@pytest.mark.asyncio
async def test_replayed_credentials_after_termination_rejected(db_session: AsyncSession) -> None:
    """Terminating a session invalidates subsequent credential reuse."""
    merchant, session, product, variant, inventory, context = await _seed_test_env(
        db_session, buyer_token="replay_token"
    )
    gateway = CanonicalCommerceGateway()

    # Terminate the session
    term_resp = await gateway.terminate_session(
        db_session,
        TerminateSessionRequest(session_id=session.id, reason="User logged out"),
        context,
    )
    assert term_resp.status == "SUCCESS"
    await db_session.commit()

    # Replay the same valid token and session_id
    replayed_resp = await gateway.execute_capability(
        db_session,
        "get_quote",
        {"session_id": str(session.id), "items": [{"sku": variant.sku, "quantity": 1}]},
        context,
    )
    assert replayed_resp.status == "REJECTED"
    assert replayed_resp.error is not None
    assert replayed_resp.error.code == GatewayErrorCode.AUTH_SESSION_EXPIRED.value


# =============================================================================
# 6. ADVERSARIAL: UNAUTHORIZED FINANCIAL MUTATION
# =============================================================================


@pytest.mark.asyncio
async def test_unauthorized_financial_mutation_rejected_fail_closed(
    db_session: AsyncSession,
) -> None:
    """Negotiate-only session cannot execute privileged financial operations (create_order)."""
    merchant, session, product, variant, inventory, context = await _seed_test_env(
        db_session,
        buyer_token="negotiate_only_token",
        granted_capabilities="buyer:discover,buyer:read,buyer:quote,buyer:negotiate",
    )
    gateway = CanonicalCommerceGateway()

    # Can get quote
    q_resp = await gateway.execute_capability(
        db_session,
        "get_quote",
        {"session_id": str(session.id), "items": [{"sku": variant.sku, "quantity": 1}]},
        context,
    )
    assert q_resp.status == "SUCCESS"
    assert q_resp.data is not None
    quote_id = q_resp.data.quote_id
    await db_session.commit()

    # Cannot create order (PRIVILEGED_FINANCIAL)
    ord_resp = await gateway.execute_capability(
        db_session,
        "create_order",
        {
            "quote_id": str(quote_id),
            "buyer_email": "buyer@ai.com",
            "shipping_address": _shipping_addr().model_dump(),
            "idempotency_key": "unauth_fin_key_1",
        },
        context,
    )
    assert ord_resp.status == "REJECTED"
    assert ord_resp.error is not None
    assert ord_resp.error.code in {
        "CAPABILITY_DENIED",
        GatewayErrorCode.AUTH_UNAUTHORIZED_CAPABILITY.value,
    }

    # Zero orders created in database
    ord_stmt = select(Order).where(Order.merchant_id == merchant.id)
    orders = (await db_session.execute(ord_stmt)).scalars().all()
    assert len(orders) == 0


# =============================================================================
# 7. ADVERSARIAL: ANONYMOUS CALLER (SESSION REQUIRED CAPABILITIES)
# =============================================================================


@pytest.mark.asyncio
async def test_session_required_capabilities_reject_anonymous_caller(
    db_session: AsyncSession,
) -> None:
    """Privileged and stateful capabilities strictly reject callers with no active session."""
    merchant, session, product, variant, inventory, context = await _seed_test_env(db_session)
    gateway = CanonicalCommerceGateway()

    anonymous_context = GatewayContext(
        merchant_id=merchant.id,
        session_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
        capabilities={"buyer:discover", "buyer:read"},
    )

    # 1. get_quote requires session
    q_resp = await gateway.execute_capability(
        db_session,
        "get_quote",
        {"items": [{"sku": variant.sku, "quantity": 1}]},
        anonymous_context,
    )
    assert q_resp.status == "REJECTED"
    assert q_resp.error is not None
    assert q_resp.error.code == GatewayErrorCode.AUTH_SESSION_NOT_FOUND.value

    # 2. create_order requires session
    ord_resp = await gateway.execute_capability(
        db_session,
        "create_order",
        {
            "quote_id": str(uuid.uuid4()),
            "buyer_email": "anon@test.com",
            "shipping_address": _shipping_addr().model_dump(),
            "idempotency_key": "anon_key_1",
        },
        anonymous_context,
    )
    assert ord_resp.status == "REJECTED"
    assert ord_resp.error is not None
    assert ord_resp.error.code == GatewayErrorCode.AUTH_SESSION_NOT_FOUND.value


@pytest.mark.asyncio
async def test_anonymous_catalog_discovery_permitted_for_active_merchant(
    db_session: AsyncSession,
) -> None:
    """Anonymous catalog browsing is permitted for active merchants."""
    merchant, session, product, variant, inventory, context = await _seed_test_env(db_session)
    gateway = CanonicalCommerceGateway()

    anonymous_context = GatewayContext(
        merchant_id=merchant.id,
        session_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
        capabilities={"buyer:discover", "buyer:read"},
    )

    # discover_products succeeds
    disc_resp = await gateway.execute_capability(
        db_session, "discover_products", {}, anonymous_context
    )
    assert disc_resp.status == "SUCCESS"
    assert disc_resp.data is not None
    assert len(disc_resp.data.products) == 1

    # get_product succeeds
    prod_resp = await gateway.execute_capability(
        db_session, "get_product", {"sku": product.sku}, anonymous_context
    )
    assert prod_resp.status == "SUCCESS"
    assert prod_resp.data is not None
    assert prod_resp.data.sku == product.sku

    # check_inventory succeeds
    inv_resp = await gateway.execute_capability(
        db_session,
        "check_inventory",
        {"sku": variant.sku, "requested_quantity": 1},
        anonymous_context,
    )
    assert inv_resp.status == "SUCCESS"
    assert inv_resp.data is not None
    assert inv_resp.data.can_fulfill is True


# =============================================================================
# 8. ADVERSARIAL: MALFORMED AUTHORIZATION CONTEXT
# =============================================================================


@pytest.mark.asyncio
async def test_malformed_protocol_version_fails_closed(db_session: AsyncSession) -> None:
    """A request with an unsupported protocol version is rejected without processing."""
    merchant, session, product, variant, inventory, context = await _seed_test_env(db_session)
    gateway = CanonicalCommerceGateway()

    context.schema_version = "1999-01-01-unsupported"

    resp = await gateway.execute_capability(db_session, "discover_products", {}, context)
    assert resp.status == "ERROR"
    assert resp.error is not None
    assert resp.error.code == GatewayErrorCode.UNSUPPORTED_PROTOCOL_VERSION.value
