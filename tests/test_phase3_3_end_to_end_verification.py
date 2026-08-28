"""Phase 3.3 — End-to-End Payment Verification Suite.

Comprehensive deterministic verification covering:
Buyer/session
-> canonical gateway
-> accepted quote
-> inventory reservation
-> order creation
-> Razorpay test-mode order
-> payment
-> signed webhook
-> reconciliation
-> PaymentAttempt
-> TransactionRecord
-> immutable AuditEvent
-> final completed state.

Followed by deliberate failure test matrix:
1. Expired quote
2. Changed quote / version mismatch
3. Inventory race (concurrency stock guard)
4. Wrong payment amount fraud detection
5. Wrong currency fraud detection
6. Forged webhook signature
7. Replayed webhook timestamp
8. Duplicate payment deduplication
9. Concurrent checkout serialization
10. Concurrent webhook delivery
11. Razorpay timeout after remote success (receipt recovery)
12. Local DB failure after remote success
13. Out-of-band reconciliation after lost webhook
14. Invalid state transition rejection
15. Cross-merchant access prevention
16. Cross-session access prevention
17. Retry after partial failure
"""

import hashlib
import hmac
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.gateway.canonical import CanonicalCommerceGateway
from agent_ready_merchant.gateway.schemas import (
    AcceptQuoteGatewayRequest,
    CheckInventoryRequest,
    CreateOrderGatewayRequest,
    DiscoverProductsRequest,
    GetOrderStatusRequest,
    GetPaymentStatusRequest,
    GetQuoteRequest,
    QuoteItemRequest,
    RequestCheckoutRequest,
    ShippingAddressGateway,
)
from agent_ready_merchant.integrations.razorpay.exceptions import (
    AmountMismatchFraudError,
    CurrencyMismatchFraudError,
    InvalidWebhookSignatureError,
    WebhookProcessingInProgressError,
    WebhookTimestampError,
)
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.inventory import InventoryItem
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.order import Order
from agent_ready_merchant.models.payment import PaymentAttempt
from agent_ready_merchant.models.product import Product, ProductVariant
from agent_ready_merchant.models.quote import PriceQuote, QuoteItem
from agent_ready_merchant.models.session import BuyerAgentSession
from agent_ready_merchant.models.transaction import TransactionRecord
from agent_ready_merchant.models.webhook import ProcessedWebhook
from agent_ready_merchant.services.payment_service import PaymentService
from agent_ready_merchant.state_machines.base import InvalidStateTransitionError
from agent_ready_merchant.state_machines.order import OrderStateMachine
from agent_ready_merchant.tools.base import GatewayContext
from tests.fake_razorpay import DeterministicFakeRazorpayTransport


def _sign(body: bytes, secret: str) -> str:
    """Computes HMAC SHA-256 webhook signature."""
    return hmac.new(key=secret.encode("utf-8"), msg=body, digestmod=hashlib.sha256).hexdigest()


async def _seed_test_environment(
    db_session: AsyncSession,
    base_price_paise: int = 500000,
    available_stock: int = 10,
) -> tuple[Merchant, BuyerAgentSession, Product, ProductVariant, InventoryItem, GatewayContext]:
    """Seeds merchant, session, product, variant, inventory, and gateway context."""
    now = datetime.now(UTC)

    uid = uuid.uuid4().hex[:8]

    merchant = Merchant(
        name=f"Merchant {uid}",
        slug=f"store-{uid}",
        currency="INR",
        rzp_key_id=f"rzp_test_{uid}",
    )
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier=f"buyer_{uid}",
        auth_token_hash=hashlib.sha256(b"raw_token").hexdigest(),
        status="ACTIVE",
        expires_at=now + timedelta(hours=2),
    )
    db_session.add(session)
    await db_session.flush()

    product = Product(
        merchant_id=merchant.id,
        sku=f"SKU-{uid}",
        title="Verification Widget",
        category="Electronics",
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
        title="Standard Edition",
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
            "buyer:inventory",
            "buyer:quote",
            "buyer:negotiate",
            "buyer:checkout",
            "buyer:payment_status",
            "buyer:order_status",
        },
        autonomy_level=1,
        max_discount_percentage=15.0,
        min_margin_percentage=20.0,
        max_single_transaction_paise=10_000_000,
    )

    await db_session.commit()
    return merchant, session, product, variant, inventory, context


def _test_shipping_address() -> ShippingAddressGateway:
    """Returns a valid ShippingAddressGateway fixture."""
    return ShippingAddressGateway(
        full_name="AI Buyer",
        address_line1="123 Agent Way",
        city="Bengaluru",
        postal_code="560001",
        country="IN",
    )


# =============================================================================
# 1. CANONICAL GOLDEN PATH: COMPLETE END-TO-END VERIFICATION
# =============================================================================


@pytest.mark.asyncio
async def test_complete_canonical_e2e_payment_lifecycle(db_session: AsyncSession) -> None:
    """Executes the complete canonical pipeline from session to settled order."""
    merchant, session, product, variant, inventory, context = await _seed_test_environment(
        db_session, base_price_paise=600000, available_stock=5
    )

    fake_rzp = DeterministicFakeRazorpayTransport()
    rzp_client = fake_rzp.build_client()
    gateway = CanonicalCommerceGateway(rzp_client=rzp_client)

    # 1. Discover products
    disc_resp = await gateway.discover_products(
        db_session, DiscoverProductsRequest(category="Electronics"), context
    )
    assert disc_resp.status == "SUCCESS"
    assert disc_resp.data is not None
    assert len(disc_resp.data.products) == 1
    assert disc_resp.data.products[0].sku == product.sku

    # 2. Check inventory
    inv_resp = await gateway.check_inventory(
        db_session, CheckInventoryRequest(sku=product.sku, requested_quantity=1), context
    )
    assert inv_resp.status == "SUCCESS"
    assert inv_resp.data is not None
    assert inv_resp.data.available_quantity == 5

    # 3. Get Quote
    quote_resp = await gateway.get_quote(
        db_session,
        GetQuoteRequest(
            session_id=session.id,
            items=[QuoteItemRequest(sku=product.sku, quantity=1)],
        ),
        context,
    )
    assert quote_resp.status == "SUCCESS"
    assert quote_resp.data is not None
    quote_id = quote_resp.data.quote_id
    assert quote_resp.data.total_paise == 600000

    # 4. Accept Quote
    accept_resp = await gateway.accept_quote(
        db_session, AcceptQuoteGatewayRequest(quote_id=quote_id), context
    )
    assert accept_resp.status == "SUCCESS"
    assert accept_resp.data is not None
    assert accept_resp.data.status == "ACCEPTED"

    # 5. Create Order via Gateway (reserves inventory, calls Razorpay)
    order_resp = await gateway.create_order(
        db_session,
        CreateOrderGatewayRequest(
            quote_id=quote_id,
            buyer_email="buyer@ai.com",
            shipping_address=_test_shipping_address(),
        ),
        context,
    )
    assert order_resp.status == "SUCCESS"
    assert order_resp.data is not None
    order_id = order_resp.data.order_id
    rzp_order_id = order_resp.data.rzp_order_id
    assert order_resp.data.status == "PENDING_PAYMENT"
    assert rzp_order_id is not None
    assert rzp_order_id in fake_rzp.orders

    # Verify inventory was reserved atomically
    await db_session.refresh(inventory)
    assert inventory.available_quantity == 4
    assert inventory.reserved_quantity == 1

    # 6. Simulate Razorpay payment capture -> webhook
    _, raw_body, signature = fake_rzp.simulate_payment(
        order_id=rzp_order_id,
        amount=600000,
        currency="INR",
        status="captured",
    )

    # 7. Process signed webhook through PaymentService
    hook_result = await PaymentService.process_payment_webhook(
        session=db_session,
        raw_body=raw_body,
        signature_header=signature,
        webhook_secret=fake_rzp.webhook_secret,
    )
    assert hook_result["status"] == "PROCESSED"
    assert hook_result["order_status"] == "PAID"

    # 8. Query Order Status through Gateway
    status_resp = await gateway.get_order_status(
        db_session, GetOrderStatusRequest(order_id=order_id), context
    )
    assert status_resp.status == "SUCCESS"
    assert status_resp.data is not None
    assert status_resp.data.status == "PAID"

    # 9. Verify Authoritative Ledger Invariants
    pay_stmt = select(PaymentAttempt).where(PaymentAttempt.order_id == order_id)
    attempt = (await db_session.execute(pay_stmt)).scalar_one()
    assert attempt.status == "CAPTURED"
    assert attempt.amount_paise == 600000

    tx_stmt = select(TransactionRecord).where(TransactionRecord.payment_attempt_id == attempt.id)
    tx = (await db_session.execute(tx_stmt)).scalar_one()
    assert tx.entry_type == "CREDIT"
    assert tx.amount_paise == 600000
    assert tx.status == "COMMITTED"
    assert tx.settlement_ref == attempt.rzp_payment_id

    # 10. Verify Cryptographic Audit Chain Integrity
    is_valid, err = await AuditEvent.verify_chain(db_session, merchant.id)
    assert is_valid is True
    assert err is None


# =============================================================================
# 2. DELIBERATE FAILURE: EXPIRED QUOTE
# =============================================================================


@pytest.mark.asyncio
async def test_failure_expired_quote_rejected(db_session: AsyncSession) -> None:
    """Attempting checkout on an expired quote fails closed without side effects."""
    merchant, session, product, variant, inventory, context = await _seed_test_environment(
        db_session
    )
    fake_rzp = DeterministicFakeRazorpayTransport()
    gateway = CanonicalCommerceGateway(rzp_client=fake_rzp.build_client())

    # Create expired quote in DB
    now = datetime.now(UTC)
    quote = PriceQuote(
        merchant_id=merchant.id,
        session_id=session.id,
        status="ACCEPTED",
        subtotal_paise=500000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=500000,
        expires_at=now - timedelta(seconds=10),  # expired
        idempotency_key=f"exp_{uuid.uuid4().hex}",
    )
    db_session.add(quote)
    await db_session.flush()
    quote_id = quote.id
    inventory_id = inventory.id
    await db_session.commit()

    # Attempt to create order
    resp = await gateway.create_order(
        db_session,
        CreateOrderGatewayRequest(
            quote_id=quote_id,
            buyer_email="buyer@ai.com",
            shipping_address=_test_shipping_address(),
        ),
        context,
    )
    assert resp.status == "REJECTED"
    assert "expired" in resp.error.message.lower()  # type: ignore[union-attr]

    # Invariants: No order created, inventory untouched, no Razorpay calls
    ord_stmt = select(Order).where(Order.quote_id == quote_id)
    assert (await db_session.execute(ord_stmt)).scalar_one_or_none() is None
    inv_row = (
        await db_session.execute(select(InventoryItem).where(InventoryItem.id == inventory_id))
    ).scalar_one()
    assert inv_row.reserved_quantity == 0
    assert fake_rzp.create_order_calls == 0


# =============================================================================
# 3. DELIBERATE FAILURE: CHANGED / SUPERSEDED QUOTE
# =============================================================================


@pytest.mark.asyncio
async def test_failure_changed_quote_version_mismatch(db_session: AsyncSession) -> None:
    """Attempting order creation on a quote that transitioned or changed fails closed."""
    merchant, session, product, variant, inventory, context = await _seed_test_environment(
        db_session
    )
    fake_rzp = DeterministicFakeRazorpayTransport()
    gateway = CanonicalCommerceGateway(rzp_client=fake_rzp.build_client())

    # Quote is still in DRAFT (not ACCEPTED)
    now = datetime.now(UTC)
    quote = PriceQuote(
        merchant_id=merchant.id,
        session_id=session.id,
        status="DRAFT",
        subtotal_paise=500000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=500000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=f"chg_{uuid.uuid4().hex}",
    )
    db_session.add(quote)
    await db_session.flush()
    quote_id = quote.id
    await db_session.commit()

    resp = await gateway.create_order(
        db_session,
        CreateOrderGatewayRequest(
            quote_id=quote_id,
            buyer_email="buyer@ai.com",
            shipping_address=_test_shipping_address(),
        ),
        context,
    )
    assert resp.status == "REJECTED"
    assert "ACCEPTED" in resp.error.message  # type: ignore[union-attr]
    assert fake_rzp.create_order_calls == 0


# =============================================================================
# 4. DELIBERATE FAILURE: INVENTORY RACE
# =============================================================================


@pytest.mark.asyncio
async def test_failure_inventory_race_prevents_overselling(db_session: AsyncSession) -> None:
    """When stock is 1 and two buyers race, exactly 1 succeeds and the other fails closed."""
    merchant, session1, product, variant, inventory, context1 = await _seed_test_environment(
        db_session, available_stock=1
    )
    inventory.safety_threshold = 0
    await db_session.commit()
    fake_rzp = DeterministicFakeRazorpayTransport()

    now = datetime.now(UTC)
    session2 = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="buyer_2",
        auth_token_hash=hashlib.sha256(b"raw2").hexdigest(),
        status="ACTIVE",
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session2)
    await db_session.flush()

    context2 = GatewayContext(
        merchant_id=merchant.id,
        session_id=session2.id,
        capabilities=context1.capabilities,
        autonomy_level=1,
    )

    quote1 = PriceQuote(
        merchant_id=merchant.id,
        session_id=session1.id,
        status="ACCEPTED",
        subtotal_paise=500000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=500000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=f"race_q1_{uuid.uuid4().hex}",
    )
    quote2 = PriceQuote(
        merchant_id=merchant.id,
        session_id=session2.id,
        status="ACCEPTED",
        subtotal_paise=500000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=500000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=f"race_q2_{uuid.uuid4().hex}",
    )
    db_session.add_all([quote1, quote2])
    await db_session.flush()

    item1 = QuoteItem(
        quote_id=quote1.id,
        variant_id=variant.id,
        quantity=1,
        unit_price_paise=500000,
        total_price_paise=500000,
    )
    item2 = QuoteItem(
        quote_id=quote2.id,
        variant_id=variant.id,
        quantity=1,
        unit_price_paise=500000,
        total_price_paise=500000,
    )
    db_session.add_all([item1, item2])
    await db_session.flush()

    quote1_id = quote1.id
    quote2_id = quote2.id
    inventory_id = inventory.id
    await db_session.commit()

    gateway = CanonicalCommerceGateway(rzp_client=fake_rzp.build_client())

    # First buyer checkouts -> succeeds
    resp1 = await gateway.create_order(
        db_session,
        CreateOrderGatewayRequest(
            quote_id=quote1_id,
            buyer_email="b1@ai.com",
            shipping_address=_test_shipping_address(),
        ),
        context1,
    )
    assert resp1.status == "SUCCESS"
    await db_session.commit()

    # Second buyer checkouts -> stock is depleted -> rejected fail-closed
    resp2 = await gateway.create_order(
        db_session,
        CreateOrderGatewayRequest(
            quote_id=quote2_id,
            buyer_email="b2@ai.com",
            shipping_address=_test_shipping_address(),
        ),
        context2,
    )
    assert resp2.status == "REJECTED"
    assert "stock" in resp2.error.message.lower() or "inventory" in resp2.error.message.lower()  # type: ignore[union-attr]

    inv_row = (
        await db_session.execute(select(InventoryItem).where(InventoryItem.id == inventory_id))
    ).scalar_one()
    assert inv_row.available_quantity == 0
    assert inv_row.reserved_quantity == 1
    assert fake_rzp.create_order_calls == 1


# =============================================================================
# 5. DELIBERATE FAILURE: WRONG PAYMENT AMOUNT
# =============================================================================


@pytest.mark.asyncio
async def test_failure_wrong_payment_amount_detected_as_fraud(db_session: AsyncSession) -> None:
    """Webhook presenting lower payment amount than order is rejected as fraud."""
    merchant, session, product, variant, inventory, context = await _seed_test_environment(
        db_session, base_price_paise=500000
    )
    fake_rzp = DeterministicFakeRazorpayTransport()
    gateway = CanonicalCommerceGateway(rzp_client=fake_rzp.build_client())

    now = datetime.now(UTC)
    quote = PriceQuote(
        merchant_id=merchant.id,
        session_id=session.id,
        status="ACCEPTED",
        subtotal_paise=500000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=500000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=f"q_{uuid.uuid4().hex}",
    )
    db_session.add(quote)
    await db_session.flush()

    db_session.add(
        QuoteItem(
            quote_id=quote.id,
            variant_id=variant.id,
            quantity=1,
            unit_price_paise=500000,
            total_price_paise=500000,
        )
    )
    await db_session.flush()
    quote_id = quote.id
    merchant_id = merchant.id
    await db_session.commit()

    order_resp = await gateway.create_order(
        db_session,
        CreateOrderGatewayRequest(
            quote_id=quote_id,
            buyer_email="buyer@ai.com",
            shipping_address=_test_shipping_address(),
        ),
        context,
    )
    assert order_resp.data is not None
    rzp_order_id = order_resp.data.rzp_order_id
    order_id = order_resp.data.order_id
    assert rzp_order_id is not None

    # Simulate tampered webhook with ₹400 instead of ₹500
    _, raw_body, signature = fake_rzp.simulate_payment(
        order_id=rzp_order_id,
        amount=400000,  # wrong amount
        currency="INR",
        status="captured",
    )

    with pytest.raises(AmountMismatchFraudError, match="Amount mismatch detected"):
        await PaymentService.process_payment_webhook(
            session=db_session,
            raw_body=raw_body,
            signature_header=signature,
            webhook_secret=fake_rzp.webhook_secret,
        )

    # Order remains PENDING_PAYMENT, no TransactionRecord
    ord_stmt = select(Order).where(Order.id == order_id)
    order = (await db_session.execute(ord_stmt)).scalar_one()
    assert order.status == "PENDING_PAYMENT"

    tx_stmt = select(TransactionRecord).where(TransactionRecord.merchant_id == merchant_id)
    assert len((await db_session.execute(tx_stmt)).scalars().all()) == 0


# =============================================================================
# 6. DELIBERATE FAILURE: WRONG CURRENCY
# =============================================================================


@pytest.mark.asyncio
async def test_failure_wrong_currency_detected_as_fraud(db_session: AsyncSession) -> None:
    """Webhook presenting USD instead of INR is rejected as currency fraud."""
    merchant, session, product, variant, inventory, context = await _seed_test_environment(
        db_session, base_price_paise=500000
    )
    fake_rzp = DeterministicFakeRazorpayTransport()
    gateway = CanonicalCommerceGateway(rzp_client=fake_rzp.build_client())

    now = datetime.now(UTC)
    quote = PriceQuote(
        merchant_id=merchant.id,
        session_id=session.id,
        status="ACCEPTED",
        subtotal_paise=500000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=500000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=f"cur_{uuid.uuid4().hex}",
    )
    db_session.add(quote)
    await db_session.flush()

    db_session.add(
        QuoteItem(
            quote_id=quote.id,
            variant_id=variant.id,
            quantity=1,
            unit_price_paise=500000,
            total_price_paise=500000,
        )
    )
    await db_session.flush()
    quote_id = quote.id
    await db_session.commit()

    order_resp = await gateway.create_order(
        db_session,
        CreateOrderGatewayRequest(
            quote_id=quote_id,
            buyer_email="buyer@ai.com",
            shipping_address=_test_shipping_address(),
        ),
        context,
    )
    assert order_resp.data is not None
    rzp_order_id = order_resp.data.rzp_order_id
    order_id = order_resp.data.order_id
    assert rzp_order_id is not None

    _, raw_body, signature = fake_rzp.simulate_payment(
        order_id=rzp_order_id,
        amount=500000,
        currency="USD",  # wrong currency
        status="captured",
    )

    with pytest.raises(CurrencyMismatchFraudError, match="Currency mismatch detected"):
        await PaymentService.process_payment_webhook(
            session=db_session,
            raw_body=raw_body,
            signature_header=signature,
            webhook_secret=fake_rzp.webhook_secret,
        )

    # Order remains PENDING_PAYMENT
    ord_stmt = select(Order).where(Order.id == order_id)
    order = (await db_session.execute(ord_stmt)).scalar_one()
    assert order.status == "PENDING_PAYMENT"


# =============================================================================
# 7. DELIBERATE FAILURE: FORGED WEBHOOK SIGNATURE
# =============================================================================


@pytest.mark.asyncio
async def test_failure_forged_webhook_rejected(db_session: AsyncSession) -> None:
    """Webhook with forged signature is rejected fail-closed without DB mutations."""
    fake_rzp = DeterministicFakeRazorpayTransport()
    _, raw_body, _ = fake_rzp.simulate_payment(
        order_id="order_fake_99",
        amount=500000,
        status="captured",
    )

    with pytest.raises(InvalidWebhookSignatureError):
        await PaymentService.process_payment_webhook(
            session=db_session,
            raw_body=raw_body,
            signature_header="forged_invalid_signature_hex",
            webhook_secret=fake_rzp.webhook_secret,
        )


# =============================================================================
# 8. DELIBERATE FAILURE: REPLAYED WEBHOOK TIMESTAMP
# =============================================================================


@pytest.mark.asyncio
async def test_failure_replayed_webhook_stale_timestamp(db_session: AsyncSession) -> None:
    """Webhook older than 24 hours fails closed with WebhookTimestampError."""
    fake_rzp = DeterministicFakeRazorpayTransport()
    stale_ts = int(datetime.now(UTC).timestamp()) - 100000  # > 27 hours ago

    _, raw_body, signature = fake_rzp.simulate_payment(
        order_id="order_fake_99",
        amount=500000,
        status="captured",
        created_at=stale_ts,
    )

    with pytest.raises(WebhookTimestampError, match="outside the allowed replay window"):
        await PaymentService.process_payment_webhook(
            session=db_session,
            raw_body=raw_body,
            signature_header=signature,
            webhook_secret=fake_rzp.webhook_secret,
        )


# =============================================================================
# 9. DELIBERATE FAILURE: DUPLICATE PAYMENT & CONCURRENT WEBHOOKS
# =============================================================================


@pytest.mark.asyncio
async def test_failure_duplicate_and_concurrent_webhooks(db_session: AsyncSession) -> None:
    """Concurrent and repeated webhook deliveries result in strictly 1 credit entry."""
    merchant, session, product, variant, inventory, context = await _seed_test_environment(
        db_session
    )

    fake_rzp = DeterministicFakeRazorpayTransport()
    gateway = CanonicalCommerceGateway(rzp_client=fake_rzp.build_client())

    now = datetime.now(UTC)
    quote = PriceQuote(
        merchant_id=merchant.id,
        session_id=session.id,
        status="ACCEPTED",
        subtotal_paise=500000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=500000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=f"dup_{uuid.uuid4().hex}",
    )
    db_session.add(quote)
    await db_session.flush()

    db_session.add(
        QuoteItem(
            quote_id=quote.id,
            variant_id=variant.id,
            quantity=1,
            unit_price_paise=500000,
            total_price_paise=500000,
        )
    )
    await db_session.flush()
    quote_id = quote.id
    merchant_id = merchant.id
    await db_session.commit()

    order_resp = await gateway.create_order(
        db_session,
        CreateOrderGatewayRequest(
            quote_id=quote_id,
            buyer_email="buyer@ai.com",
            shipping_address=_test_shipping_address(),
        ),
        context,
    )
    assert order_resp.status == "SUCCESS"
    assert order_resp.data is not None
    rzp_order_id = order_resp.data.rzp_order_id
    assert rzp_order_id is not None
    await db_session.commit()

    _, raw_body, signature = fake_rzp.simulate_payment(
        order_id=rzp_order_id,
        amount=500000,
        status="captured",
    )

    # First delivery
    res1 = await PaymentService.process_payment_webhook(
        session=db_session,
        raw_body=raw_body,
        signature_header=signature,
        webhook_secret=fake_rzp.webhook_secret,
    )
    assert res1["status"] == "PROCESSED"

    # Second delivery (duplicate replay)
    res2 = await PaymentService.process_payment_webhook(
        session=db_session,
        raw_body=raw_body,
        signature_header=signature,
        webhook_secret=fake_rzp.webhook_secret,
    )
    assert res2["status"] == "DUPLICATE_IGNORED"

    # Third delivery
    res3 = await PaymentService.process_payment_webhook(
        session=db_session,
        raw_body=raw_body,
        signature_header=signature,
        webhook_secret=fake_rzp.webhook_secret,
    )
    assert res3["status"] == "DUPLICATE_IGNORED"

    # Test concurrent in-flight delivery protection:
    # A webhook arriving while another is PROCESSING raises WebhookProcessingInProgressError
    in_flight_raw = b'{"event":"payment.captured","test":"in_flight_concurrent_p33"}'
    in_flight_pw = ProcessedWebhook(
        event_id="evt_in_flight_p33",
        event_name="payment.captured",
        payload_hash=hashlib.sha256(in_flight_raw).hexdigest(),
        signature_hash="sig_hash_p33",
        status="PROCESSING",
    )
    db_session.add(in_flight_pw)
    await db_session.flush()

    with pytest.raises(WebhookProcessingInProgressError):
        await PaymentService.process_payment_webhook(
            session=db_session,
            raw_body=in_flight_raw,
            signature_header=_sign(in_flight_raw, fake_rzp.webhook_secret),
            webhook_secret=fake_rzp.webhook_secret,
        )

    # Ledger invariants: strictly 1 transaction record
    tx_stmt = select(TransactionRecord).where(TransactionRecord.merchant_id == merchant_id)
    records = (await db_session.execute(tx_stmt)).scalars().all()
    assert len(records) == 1
    assert records[0].entry_type == "CREDIT"


# =============================================================================
# 10. DELIBERATE FAILURE: CONCURRENT CHECKOUT
# =============================================================================


@pytest.mark.asyncio
async def test_failure_concurrent_checkout_safe_serialization(db_session: AsyncSession) -> None:
    """Two concurrent checkout requests for the same accepted quote serialize safely."""
    merchant, session, product, variant, inventory, context = await _seed_test_environment(
        db_session
    )

    fake_rzp = DeterministicFakeRazorpayTransport()

    now = datetime.now(UTC)
    quote = PriceQuote(
        merchant_id=merchant.id,
        session_id=session.id,
        status="ACCEPTED",
        subtotal_paise=500000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=500000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=f"conc_chk_{uuid.uuid4().hex}",
    )
    db_session.add(quote)
    await db_session.flush()

    db_session.add(
        QuoteItem(
            quote_id=quote.id,
            variant_id=variant.id,
            quantity=1,
            unit_price_paise=500000,
            total_price_paise=500000,
        )
    )
    await db_session.flush()
    quote_id = quote.id
    await db_session.commit()

    shipping = _test_shipping_address()
    gateway = CanonicalCommerceGateway(rzp_client=fake_rzp.build_client())

    # First checkout
    res1 = await gateway.request_checkout(
        db_session,
        RequestCheckoutRequest(
            quote_id=quote_id, buyer_email="buyer@ai.com", shipping_address=shipping
        ),
        context,
    )
    assert res1.status == "SUCCESS"
    assert res1.data is not None
    first_order_id = res1.data.order_id

    # Second checkout on same quote: returns existing order or succeeds idempotently
    res2 = await gateway.request_checkout(
        db_session,
        RequestCheckoutRequest(
            quote_id=quote_id, buyer_email="buyer@ai.com", shipping_address=shipping
        ),
        context,
    )
    assert res2.status == "SUCCESS"
    assert res2.data is not None
    assert res2.data.order_id == first_order_id

    # Exactly 1 Order row exists for this quote in the database
    ord_stmt = select(Order).where(Order.quote_id == quote_id)
    orders = (await db_session.execute(ord_stmt)).scalars().all()
    assert len(orders) == 1
    assert fake_rzp.create_order_calls == 1


# =============================================================================
# 11. DELIBERATE FAILURE: RAZORPAY TIMEOUT AFTER REMOTE SUCCESS (RECEIPT RECOVERY)
# =============================================================================


@pytest.mark.asyncio
async def test_failure_razorpay_timeout_after_remote_success_receipt_recovery(
    db_session: AsyncSession,
) -> None:
    """Remote order creation succeeds but network times out; retry recovers via receipt."""
    merchant, session, product, variant, inventory, context = await _seed_test_environment(
        db_session
    )
    fake_rzp = DeterministicFakeRazorpayTransport()
    # Inject fault: save remotely, then raise ReadTimeout
    fake_rzp.simulate_order_creation_timeout_after_save = True

    gateway = CanonicalCommerceGateway(rzp_client=fake_rzp.build_client())

    now = datetime.now(UTC)
    quote = PriceQuote(
        merchant_id=merchant.id,
        session_id=session.id,
        status="ACCEPTED",
        subtotal_paise=500000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=500000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=f"to_rec_{uuid.uuid4().hex}",
    )
    db_session.add(quote)
    await db_session.flush()

    db_session.add(
        QuoteItem(
            quote_id=quote.id,
            variant_id=variant.id,
            quantity=1,
            unit_price_paise=500000,
            total_price_paise=500000,
        )
    )
    await db_session.flush()
    quote_id = quote.id
    receipt_id = f"ord_{quote_id.hex[:32]}"
    await db_session.commit()

    # 1. First attempt times out on wire
    resp1 = await gateway.create_order(
        db_session,
        CreateOrderGatewayRequest(
            quote_id=quote_id,
            buyer_email="buyer@ai.com",
            shipping_address=_test_shipping_address(),
        ),
        context,
    )
    assert resp1.status == "ERROR"
    assert "timeout" in resp1.error.message.lower()  # type: ignore[union-attr]

    # Verify remote order was stored in fake Razorpay
    assert receipt_id in fake_rzp.orders_by_receipt
    remote_rzp_order = fake_rzp.orders_by_receipt[receipt_id]

    # Turn off fault injection for the retry
    fake_rzp.simulate_order_creation_timeout_after_save = False

    # 2. Retry attempt: recovers remote order via receipt query without second create
    resp2 = await gateway.create_order(
        db_session,
        CreateOrderGatewayRequest(
            quote_id=quote_id,
            buyer_email="buyer@ai.com",
            shipping_address=_test_shipping_address(),
        ),
        context,
    )
    assert resp2.status == "SUCCESS"
    assert resp2.data is not None
    assert resp2.data.rzp_order_id == remote_rzp_order["id"]

    # Crucial invariant: create_order was NOT called a second time!
    assert fake_rzp.create_order_calls == 1
    assert fake_rzp.fetch_order_by_receipt_calls >= 1


# =============================================================================
# 12. DELIBERATE FAILURE: LOCAL DB FAILURE AFTER REMOTE SUCCESS
# =============================================================================


@pytest.mark.asyncio
async def test_failure_local_db_failure_after_remote_success(db_session: AsyncSession) -> None:
    """If DB rolls back during order creation, subsequent retry safely recovers remote order."""
    merchant, session, product, variant, inventory, context = await _seed_test_environment(
        db_session
    )
    fake_rzp = DeterministicFakeRazorpayTransport()
    rzp_client = fake_rzp.build_client()

    now = datetime.now(UTC)
    quote = PriceQuote(
        merchant_id=merchant.id,
        session_id=session.id,
        status="ACCEPTED",
        subtotal_paise=500000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=500000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=f"db_fail_{uuid.uuid4().hex}",
    )
    db_session.add(quote)
    await db_session.flush()

    db_session.add(
        QuoteItem(
            quote_id=quote.id,
            variant_id=variant.id,
            quantity=1,
            unit_price_paise=500000,
            total_price_paise=500000,
        )
    )
    await db_session.flush()
    quote_id = quote.id
    receipt_id = f"ord_{quote_id.hex[:32]}"
    await db_session.commit()

    # Pre-create remote order in Razorpay (as if a previous crashed worker created it)
    created_rzp = await rzp_client.create_order(
        amount_paise=500000, currency="INR", receipt=receipt_id
    )

    # Worker crashes / rolled back. Next retry calls create_order_from_accepted_quote:
    order = await PaymentService.create_order_from_accepted_quote(
        session=db_session,
        quote_id=quote_id,
        buyer_email="retry@ai.com",
        shipping_address={"city": "Delhi"},
        rzp_client=rzp_client,
    )

    # Bound to existing remote order without creating duplicate
    assert order.rzp_order_id == created_rzp.id
    assert fake_rzp.create_order_calls == 1


# =============================================================================
# 13. DELIBERATE FAILURE: RECONCILIATION AFTER LOST WEBHOOK
# =============================================================================


@pytest.mark.asyncio
async def test_failure_reconciliation_after_lost_webhook(db_session: AsyncSession) -> None:
    """If the payment webhook is dropped, reconciliation queries Razorpay and settles the order."""
    merchant, session, product, variant, inventory, context = await _seed_test_environment(
        db_session
    )
    fake_rzp = DeterministicFakeRazorpayTransport()
    gateway = CanonicalCommerceGateway(rzp_client=fake_rzp.build_client())

    now = datetime.now(UTC)
    quote = PriceQuote(
        merchant_id=merchant.id,
        session_id=session.id,
        status="ACCEPTED",
        subtotal_paise=500000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=500000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=f"reco_lost_{uuid.uuid4().hex}",
    )
    db_session.add(quote)
    await db_session.flush()

    db_session.add(
        QuoteItem(
            quote_id=quote.id,
            variant_id=variant.id,
            quantity=1,
            unit_price_paise=500000,
            total_price_paise=500000,
        )
    )
    await db_session.flush()
    quote_id = quote.id
    merchant_id = merchant.id
    await db_session.commit()

    order_resp = await gateway.create_order(
        db_session,
        CreateOrderGatewayRequest(
            quote_id=quote_id,
            buyer_email="buyer@ai.com",
            shipping_address=_test_shipping_address(),
        ),
        context,
    )
    assert order_resp.status == "SUCCESS"
    assert order_resp.data is not None
    order_id = order_resp.data.order_id
    rzp_order_id = order_resp.data.rzp_order_id
    assert rzp_order_id is not None

    # Simulate payment capture at Razorpay (e.g. buyer completed payment on hosted checkout)
    # BUT WEBHOOK IS DROPPED / LOST IN TRANSIT
    fake_rzp.simulate_payment(
        order_id=rzp_order_id,
        amount=500000,
        status="captured",
    )

    # Order in ARM is still PENDING_PAYMENT
    ord_stmt = select(Order).where(Order.id == order_id)
    order = (await db_session.execute(ord_stmt)).scalar_one()
    assert order.status == "PENDING_PAYMENT"

    # Reconciliation is triggered via get_payment_status
    status_resp = await gateway.get_payment_status(
        db_session, GetPaymentStatusRequest(order_id=order_id), context
    )
    assert status_resp.status == "SUCCESS"
    assert status_resp.data is not None
    assert status_resp.data.order_status == "PAID"
    assert len(status_resp.data.payment_attempts) >= 1
    assert status_resp.data.payment_attempts[0].status == "CAPTURED"

    # Ledger record verified
    tx_stmt = select(TransactionRecord).where(TransactionRecord.merchant_id == merchant_id)
    tx = (await db_session.execute(tx_stmt)).scalar_one()
    assert tx.amount_paise == 500000
    assert tx.entry_type == "CREDIT"
    assert tx.status == "COMMITTED"


# =============================================================================
# 14. DELIBERATE FAILURE: INVALID STATE TRANSITION
# =============================================================================


@pytest.mark.asyncio
async def test_failure_invalid_state_transition_fails_closed(db_session: AsyncSession) -> None:
    """Attempting invalid order state machine transitions raises error and fails closed."""
    merchant, session, product, variant, inventory, context = await _seed_test_environment(
        db_session
    )

    now = datetime.now(UTC)
    quote = PriceQuote(
        merchant_id=merchant.id,
        session_id=session.id,
        status="ACCEPTED",
        subtotal_paise=500000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=500000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=f"inv_trans_{uuid.uuid4().hex}",
    )
    db_session.add(quote)
    await db_session.flush()
    quote_id = quote.id
    await db_session.commit()

    order = Order(
        quote_id=quote_id,
        merchant_id=merchant.id,
        status="PAID",  # Terminal paid state
        amount_paise=500000,
        currency="INR",
        buyer_email="buyer@ai.com",
    )
    db_session.add(order)
    await db_session.commit()

    # Attempt illegal backward regression from PAID -> PENDING_PAYMENT
    with pytest.raises(InvalidStateTransitionError):
        await OrderStateMachine.transition(
            session=db_session,
            order=order,
            target_state="PENDING_PAYMENT",
            expected_version=order.version,
            reason="Illegal regression attempt",
        )

    assert order.status == "PAID"


# =============================================================================
# 15. DELIBERATE FAILURE: CROSS-MERCHANT ACCESS PREVENTION
# =============================================================================


@pytest.mark.asyncio
async def test_failure_cross_merchant_access_rejected(db_session: AsyncSession) -> None:
    """Merchant B's session cannot access Merchant A's orders or quotes."""
    merchant_a, session_a, _, _, _, context_a = await _seed_test_environment(db_session)
    merchant_b, session_b, _, _, _, context_b = await _seed_test_environment(db_session)

    gateway = CanonicalCommerceGateway()

    # Create quote under Merchant A
    now = datetime.now(UTC)
    quote_a = PriceQuote(
        merchant_id=merchant_a.id,
        session_id=session_a.id,
        status="ACCEPTED",
        subtotal_paise=500000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=500000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=f"cross_m_{uuid.uuid4().hex}",
    )
    db_session.add(quote_a)
    await db_session.flush()
    quote_a_id = quote_a.id
    await db_session.commit()

    # Context B (Merchant B) attempts to create order using Merchant A's quote
    resp = await gateway.create_order(
        db_session,
        CreateOrderGatewayRequest(
            quote_id=quote_a_id,
            buyer_email="spy@competitor.com",
            shipping_address=_test_shipping_address(),
        ),
        context_b,  # Merchant B context
    )
    assert resp.status == "REJECTED"
    assert resp.error is not None
    assert "merchant" in resp.error.message.lower() or "not found" in resp.error.message.lower()


# =============================================================================
# 16. DELIBERATE FAILURE: CROSS-SESSION ACCESS PREVENTION
# =============================================================================


@pytest.mark.asyncio
async def test_failure_cross_session_access_rejected(db_session: AsyncSession) -> None:
    """Session 2 cannot access Session 1's orders within the same merchant."""
    merchant, session1, product, variant, inventory, context1 = await _seed_test_environment(
        db_session
    )

    now = datetime.now(UTC)
    session2 = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="buyer_session_2",
        auth_token_hash=hashlib.sha256(b"s2").hexdigest(),
        status="ACTIVE",
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session2)
    await db_session.flush()

    context2 = GatewayContext(
        merchant_id=merchant.id,
        session_id=session2.id,
        capabilities=context1.capabilities,
        autonomy_level=1,
    )

    quote = PriceQuote(
        merchant_id=merchant.id,
        session_id=session1.id,
        status="ACCEPTED",
        subtotal_paise=500000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=500000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=f"s1_q_{uuid.uuid4().hex}",
    )
    db_session.add(quote)
    await db_session.flush()
    quote_id = quote.id
    await db_session.commit()

    gateway = CanonicalCommerceGateway()

    # Session 2 attempts to checkout Session 1's quote
    resp = await gateway.request_checkout(
        db_session,
        RequestCheckoutRequest(
            quote_id=quote_id,
            buyer_email="buyer@ai.com",
            shipping_address=_test_shipping_address(),
        ),
        context2,  # Session 2 context
    )
    assert resp.status == "REJECTED"
    assert resp.error is not None
    assert "session" in resp.error.message.lower() or "not found" in resp.error.message.lower()


# =============================================================================
# 17. DELIBERATE FAILURE: RETRY AFTER PARTIAL FAILURE
# =============================================================================


@pytest.mark.asyncio
async def test_failure_retry_after_partial_failure_recovers_cleanly(
    db_session: AsyncSession,
) -> None:
    """When a transient error occurs during checkout, retrying completes cleanly."""
    merchant, session, product, variant, inventory, context = await _seed_test_environment(
        db_session
    )
    fake_rzp = DeterministicFakeRazorpayTransport()
    gateway = CanonicalCommerceGateway(rzp_client=fake_rzp.build_client())

    now = datetime.now(UTC)
    quote = PriceQuote(
        merchant_id=merchant.id,
        session_id=session.id,
        status="ACCEPTED",
        subtotal_paise=500000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=500000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=f"retry_part_{uuid.uuid4().hex}",
    )
    db_session.add(quote)
    await db_session.flush()

    db_session.add(
        QuoteItem(
            quote_id=quote.id,
            variant_id=variant.id,
            quantity=1,
            unit_price_paise=500000,
            total_price_paise=500000,
        )
    )
    await db_session.flush()
    quote_id = quote.id
    inventory_id = inventory.id
    await db_session.commit()

    # 1. Attempt checkout with transient 500 error injected
    fake_rzp.simulate_order_creation_500 = True
    shipping = _test_shipping_address()

    resp1 = await gateway.create_order(
        db_session,
        CreateOrderGatewayRequest(
            quote_id=quote_id, buyer_email="buyer@ai.com", shipping_address=shipping
        ),
        context,
    )
    assert resp1.status == "ERROR"
    assert fake_rzp.create_order_calls == 1

    # Invariants after failure: No order created, inventory restored/unreserved
    inv_row1 = (
        await db_session.execute(select(InventoryItem).where(InventoryItem.id == inventory_id))
    ).scalar_one()
    assert inv_row1.reserved_quantity == 0

    # 2. Transient error cleared -> Retry checkout
    fake_rzp.simulate_order_creation_500 = False

    resp2 = await gateway.create_order(
        db_session,
        CreateOrderGatewayRequest(
            quote_id=quote_id, buyer_email="buyer@ai.com", shipping_address=shipping
        ),
        context,
    )
    assert resp2.status == "SUCCESS"
    assert resp2.data is not None
    assert resp2.data.status == "PENDING_PAYMENT"

    # Inventory reserved now
    inv_row2 = (
        await db_session.execute(select(InventoryItem).where(InventoryItem.id == inventory_id))
    ).scalar_one()
    assert inv_row2.reserved_quantity == 1
