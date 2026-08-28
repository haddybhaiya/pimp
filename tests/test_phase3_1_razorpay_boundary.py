"""Phase 3.1 — Razorpay Payment Boundary Verification Suite.

Validates the authoritative payment boundary under strict invariant enforcement:
1. Successful payment settlement via verified webhook.
2. Wrong amount rejection and fraud detection (INV-FIN-01, INV-FIN-02).
3. Wrong currency rejection (server-authoritative currency invariant).
4. Wrong order binding violation detection.
5. Unknown payment / missing payment ID handling.
6. Duplicate payment replay idempotency (INV-FIN-04).
7. Delayed webhook handling without state corruption.
8. Webhook and out-of-band reconciliation race safety.
9. Razorpay API timeout handling without false payment success.
10. Razorpay HTTP 4xx client errors and 5xx server errors normalization.
11. PaymentAttempt and Order state regression prevention (INV-STA-01).
12. Strict multi-entity transaction binding invariant verification (INV-STA-05).
"""

import hashlib
import hmac
import json
import uuid
from datetime import UTC, datetime, timedelta

import httpx
import pytest
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.config import get_settings
from agent_ready_merchant.integrations.razorpay.client import RazorpayClient
from agent_ready_merchant.integrations.razorpay.exceptions import (
    AmountMismatchFraudError,
    CurrencyMismatchFraudError,
    OrderMismatchError,
    RazorpayBadRequestError,
    RazorpayNotFoundError,
    RazorpayRateLimitError,
    RazorpayServerError,
    TransactionBindingError,
)
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.order import Order
from agent_ready_merchant.models.payment import PaymentAttempt
from agent_ready_merchant.models.product import Product, ProductVariant
from agent_ready_merchant.models.quote import PriceQuote, QuoteItem
from agent_ready_merchant.models.session import BuyerAgentSession
from agent_ready_merchant.models.transaction import TransactionRecord
from agent_ready_merchant.services.payment_service import PaymentService
from agent_ready_merchant.state_machines.base import (
    InvalidStateTransitionError,
    TerminalStateError,
)
from agent_ready_merchant.state_machines.order import OrderStateMachine
from agent_ready_merchant.state_machines.payment_attempt import PaymentAttemptStateMachine

TEST_WEBHOOK_SECRET: str = get_settings().RAZORPAY_WEBHOOK_SECRET.get_secret_value()


def _sign(body: bytes, secret: str = TEST_WEBHOOK_SECRET) -> str:
    """Computes HMAC SHA-256 webhook signature."""
    return hmac.new(key=secret.encode("utf-8"), msg=body, digestmod=hashlib.sha256).hexdigest()


async def _seed_test_order(
    db_session: AsyncSession,
    amount_paise: int = 500000,
    currency: str = "INR",
    rzp_order_id: str = "order_rzp_test_123",
) -> tuple[Merchant, BuyerAgentSession, PriceQuote, Order]:
    """Helper fixture to seed database with merchant, session, quote, and pending order."""
    now = datetime.now(UTC)
    merchant = Merchant(
        name=f"Merchant_{uuid.uuid4().hex[:8]}",
        slug=f"merchant-{uuid.uuid4().hex[:8]}",
        rzp_key_id="rzp_test_fixture",
    )
    db_session.add(merchant)
    await db_session.flush()

    raw_token = f"token_{uuid.uuid4().hex}"
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="buyer_agent_p31",
        auth_token_hash=token_hash,
        granted_capabilities="buyer:discover,buyer:read,buyer:quote,buyer:checkout,buyer:payment_status",
        expires_at=now + timedelta(hours=2),
    )
    db_session.add(session)
    await db_session.flush()

    product = Product(
        merchant_id=merchant.id,
        sku=f"SKU-{uuid.uuid4().hex[:6]}",
        title="Phase 3.1 Test Item",
        category="Test",
        base_price_paise=amount_paise,
        floor_price_paise=int(amount_paise * 0.8),
    )
    db_session.add(product)
    await db_session.flush()

    variant = ProductVariant(product_id=product.id, sku=f"{product.sku}-V", title="Standard")
    db_session.add(variant)
    await db_session.flush()

    quote = PriceQuote(
        session_id=session.id,
        merchant_id=merchant.id,
        status="ACCEPTED",
        subtotal_paise=amount_paise,
        discount_paise=0,
        shipping_paise=0,
        total_paise=amount_paise,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=str(uuid.uuid4()),
    )
    db_session.add(quote)
    await db_session.flush()

    quote_item = QuoteItem(
        quote_id=quote.id,
        variant_id=variant.id,
        quantity=1,
        unit_price_paise=amount_paise,
        total_price_paise=amount_paise,
    )
    db_session.add(quote_item)
    await db_session.flush()

    order = Order(
        quote_id=quote.id,
        merchant_id=merchant.id,
        status="PENDING_PAYMENT",
        amount_paise=amount_paise,
        currency=currency,
        buyer_email="buyer@testboundary.com",
        rzp_order_id=rzp_order_id,
    )
    db_session.add(order)
    await db_session.flush()

    return merchant, session, quote, order


# =============================================================================
# 1. Successful Payment
# =============================================================================
@pytest.mark.asyncio
async def test_successful_payment(db_session: AsyncSession) -> None:
    """Verifies that a valid signed webhook settles the order and creates transaction record."""
    merchant, session, quote, order = await _seed_test_order(
        db_session, amount_paise=300000, rzp_order_id="order_success_p31"
    )
    secret = TEST_WEBHOOK_SECRET

    payload = {
        "event": "order.paid",
        "payload": {
            "order": {
                "entity": {
                    "id": "order_success_p31",
                    "amount": 300000,
                    "currency": "INR",
                    "status": "paid",
                }
            },
            "payment": {
                "entity": {
                    "id": "pay_success_999",
                    "order_id": "order_success_p31",
                    "amount": 300000,
                    "currency": "INR",
                    "status": "captured",
                    "method": "upi",
                }
            },
        },
    }
    raw_body = json.dumps(payload).encode("utf-8")
    sig = _sign(raw_body, secret)

    result = await PaymentService.process_payment_webhook(
        session=db_session,
        raw_body=raw_body,
        signature_header=sig,
        webhook_secret=secret,
    )

    assert result["status"] == "PROCESSED"
    assert result["order_status"] == "PAID"
    assert order.status == "PAID"

    # Verify PaymentAttempt created with CAPTURED status
    pay_stmt = select(PaymentAttempt).where(PaymentAttempt.order_id == order.id)
    attempt = (await db_session.execute(pay_stmt)).scalar_one()
    assert attempt.status == "CAPTURED"
    assert attempt.rzp_payment_id == "pay_success_999"
    assert attempt.amount_paise == 300000

    # Verify TransactionRecord created in immutable ledger
    tx_stmt = select(TransactionRecord).where(TransactionRecord.payment_attempt_id == attempt.id)
    tx = (await db_session.execute(tx_stmt)).scalar_one()
    assert tx.entry_type == "CREDIT"
    assert tx.amount_paise == 300000
    assert tx.status == "COMMITTED"
    assert tx.settlement_ref == "pay_success_999"


# =============================================================================
# 2. Wrong Amount Rejection & Anti-Fraud Detection
# =============================================================================
@pytest.mark.asyncio
async def test_wrong_amount(db_session: AsyncSession) -> None:
    """Verifies that an amount mismatch raises AmountMismatchFraudError and logs fraud audit."""
    merchant, session, quote, order = await _seed_test_order(
        db_session, amount_paise=500000, rzp_order_id="order_wrong_amount_p31"
    )
    secret = TEST_WEBHOOK_SECRET

    # Webhook claims to pay only 1000 paise (₹10) for a 500,000 paise (₹5000) order
    payload = {
        "event": "payment.captured",
        "payload": {
            "order": {
                "entity": {
                    "id": "order_wrong_amount_p31",
                    "amount": 1000,
                    "currency": "INR",
                }
            },
            "payment": {
                "entity": {
                    "id": "pay_fraud_cheap_01",
                    "order_id": "order_wrong_amount_p31",
                    "amount": 1000,
                    "currency": "INR",
                    "status": "captured",
                }
            },
        },
    }
    raw_body = json.dumps(payload).encode("utf-8")
    sig = _sign(raw_body, secret)

    with pytest.raises(AmountMismatchFraudError) as exc_info:
        await PaymentService.process_payment_webhook(
            session=db_session,
            raw_body=raw_body,
            signature_header=sig,
            webhook_secret=secret,
        )

    assert exc_info.value.expected_amount_paise == 500000
    assert exc_info.value.received_amount_paise == 1000

    # Order must remain un-settled
    assert order.status == "PENDING_PAYMENT"

    # Audit event must record fraud attempt
    audit_stmt = select(AuditEvent).where(
        AuditEvent.event_type == "PAYMENT_AMOUNT_FRAUD_DETECTED",
        AuditEvent.merchant_id == merchant.id,
    )
    audit = (await db_session.execute(audit_stmt)).scalar_one_or_none()
    assert audit is not None
    assert audit.payload["expected_amount_paise"] == 500000
    assert audit.payload["received_amount_paise"] == 1000


# =============================================================================
# 3. Wrong Currency Rejection
# =============================================================================
@pytest.mark.asyncio
async def test_wrong_currency(db_session: AsyncSession) -> None:
    """Verifies that currency mismatch raises CurrencyMismatchFraudError and logs fraud audit."""
    merchant, session, quote, order = await _seed_test_order(
        db_session, amount_paise=500000, currency="INR", rzp_order_id="order_wrong_curr_p31"
    )
    secret = TEST_WEBHOOK_SECRET

    # Webhook presents payment in USD instead of INR
    payload = {
        "event": "order.paid",
        "payload": {
            "order": {
                "entity": {
                    "id": "order_wrong_curr_p31",
                    "amount": 500000,
                    "currency": "USD",
                }
            },
            "payment": {
                "entity": {
                    "id": "pay_usd_01",
                    "order_id": "order_wrong_curr_p31",
                    "amount": 500000,
                    "currency": "USD",
                    "status": "captured",
                }
            },
        },
    }
    raw_body = json.dumps(payload).encode("utf-8")
    sig = _sign(raw_body, secret)

    with pytest.raises(CurrencyMismatchFraudError) as exc_info:
        await PaymentService.process_payment_webhook(
            session=db_session,
            raw_body=raw_body,
            signature_header=sig,
            webhook_secret=secret,
        )

    assert exc_info.value.expected_currency == "INR"
    assert exc_info.value.received_currency == "USD"
    assert order.status == "PENDING_PAYMENT"

    # Verify audit event emitted
    audit_stmt = select(AuditEvent).where(
        AuditEvent.event_type == "PAYMENT_CURRENCY_FRAUD_DETECTED",
        AuditEvent.merchant_id == merchant.id,
    )
    audit = (await db_session.execute(audit_stmt)).scalar_one_or_none()
    assert audit is not None
    assert audit.payload["expected_currency"] == "INR"
    assert audit.payload["received_currency"] == "USD"


# =============================================================================
# 4. Wrong Order Binding Mismatch
# =============================================================================
@pytest.mark.asyncio
async def test_wrong_order(db_session: AsyncSession) -> None:
    """Verifies that mismatch between payment and order rzp_order_id raises OrderMismatchError."""
    merchant, session, quote, order = await _seed_test_order(
        db_session, amount_paise=250000, rzp_order_id="order_legit_001"
    )
    secret = TEST_WEBHOOK_SECRET

    # Webhook references order_legit_001 on outer envelope but pay entity binds to different order
    payload = {
        "event": "payment.captured",
        "payload": {
            "order": {
                "entity": {
                    "id": "order_legit_001",
                    "amount": 250000,
                }
            },
            "payment": {
                "entity": {
                    "id": "pay_foreign_999",
                    "order_id": "order_foreign_999",  # Mismatch!
                    "amount": 250000,
                    "currency": "INR",
                    "status": "captured",
                }
            },
        },
    }
    raw_body = json.dumps(payload).encode("utf-8")
    sig = _sign(raw_body, secret)

    with pytest.raises(OrderMismatchError) as exc_info:
        await PaymentService.process_payment_webhook(
            session=db_session,
            raw_body=raw_body,
            signature_header=sig,
            webhook_secret=secret,
        )

    assert exc_info.value.expected_order_id == "order_legit_001"
    assert exc_info.value.received_order_id == "order_foreign_999"
    assert order.status == "PENDING_PAYMENT"


# =============================================================================
# 5. Unknown Payment & Unknown Order Handling
# =============================================================================
@pytest.mark.asyncio
async def test_unknown_payment(db_session: AsyncSession) -> None:
    """Verifies graceful handling of unknown payments, missing IDs, or nonexistent orders."""
    merchant, session, quote, order = await _seed_test_order(
        db_session, amount_paise=200000, rzp_order_id="order_unknown_p31"
    )
    secret = TEST_WEBHOOK_SECRET

    # Case A: Missing payment ID in capture event
    payload_no_pid = {
        "event": "order.paid",
        "payload": {
            "order": {"entity": {"id": "order_unknown_p31", "amount": 200000}},
            "payment": {"entity": {"amount": 200000}},  # No 'id'!
        },
    }
    raw_body = json.dumps(payload_no_pid).encode("utf-8")
    res_no_pid = await PaymentService.process_payment_webhook(
        session=db_session,
        raw_body=raw_body,
        signature_header=_sign(raw_body, secret),
        webhook_secret=secret,
    )
    assert res_no_pid["status"] == "IGNORED"
    assert res_no_pid["reason"] == "missing_payment_id"
    assert order.status == "PENDING_PAYMENT"

    # Case B: Unknown Order ID not found in database
    payload_unknown_ord = {
        "event": "order.paid",
        "payload": {
            "order": {"entity": {"id": "order_ghost_nonexistent_999", "amount": 200000}},
            "payment": {
                "entity": {
                    "id": "pay_ghost_01",
                    "order_id": "order_ghost_nonexistent_999",
                    "amount": 200000,
                }
            },
        },
    }
    raw_body_ghost = json.dumps(payload_unknown_ord).encode("utf-8")
    res_ghost = await PaymentService.process_payment_webhook(
        session=db_session,
        raw_body=raw_body_ghost,
        signature_header=_sign(raw_body_ghost, secret),
        webhook_secret=secret,
    )
    assert res_ghost["status"] == "IGNORED"
    assert res_ghost["reason"] == "order_not_found"


# =============================================================================
# 6. Duplicate Payment Idempotency
# =============================================================================
@pytest.mark.asyncio
async def test_duplicate_payment(db_session: AsyncSession) -> None:
    """Verifies that replaying an identical webhook is strictly idempotent."""
    merchant, session, quote, order = await _seed_test_order(
        db_session, amount_paise=400000, rzp_order_id="order_dup_p31"
    )
    secret = TEST_WEBHOOK_SECRET

    payload = {
        "event": "order.paid",
        "payload": {
            "order": {"entity": {"id": "order_dup_p31", "amount": 400000, "currency": "INR"}},
            "payment": {
                "entity": {
                    "id": "pay_dup_001",
                    "order_id": "order_dup_p31",
                    "amount": 400000,
                    "currency": "INR",
                    "status": "captured",
                }
            },
        },
    }
    raw_body = json.dumps(payload).encode("utf-8")
    sig = _sign(raw_body, secret)

    # First delivery: processes successfully
    res1 = await PaymentService.process_payment_webhook(
        session=db_session, raw_body=raw_body, signature_header=sig, webhook_secret=secret
    )
    assert res1["status"] == "PROCESSED"
    assert order.status == "PAID"

    # Second delivery: deduplicated
    res2 = await PaymentService.process_payment_webhook(
        session=db_session, raw_body=raw_body, signature_header=sig, webhook_secret=secret
    )
    assert res2["status"] == "DUPLICATE_IGNORED"

    # Third delivery: still deduplicated
    res3 = await PaymentService.process_payment_webhook(
        session=db_session, raw_body=raw_body, signature_header=sig, webhook_secret=secret
    )
    assert res3["status"] == "DUPLICATE_IGNORED"

    # Verify exactly 1 TransactionRecord and 1 PaymentAttempt exist
    tx_count_stmt = select(TransactionRecord).where(
        TransactionRecord.merchant_id == merchant.id,
        TransactionRecord.settlement_ref == "pay_dup_001",
    )
    tx_rows = (await db_session.execute(tx_count_stmt)).scalars().all()
    assert len(tx_rows) == 1

    pay_stmt = select(PaymentAttempt).where(PaymentAttempt.order_id == order.id)
    pay_rows = (await db_session.execute(pay_stmt)).scalars().all()
    assert len(pay_rows) == 1


# =============================================================================
# 7. Delayed Webhook
# =============================================================================
@pytest.mark.asyncio
async def test_delayed_webhook(db_session: AsyncSession) -> None:
    """Verifies delayed webhooks arriving after reconciliation do not corrupt state."""
    merchant, session, quote, order = await _seed_test_order(
        db_session, amount_paise=150000, rzp_order_id="order_delayed_p31"
    )
    secret = TEST_WEBHOOK_SECRET

    # Step 1: Simulate out-of-band reconciliation settling the order first
    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={
                "entity": "collection",
                "count": 1,
                "items": [
                    {
                        "id": "pay_delayed_recovered_01",
                        "entity": "payment",
                        "amount": 150000,
                        "currency": "INR",
                        "status": "captured",
                        "order_id": "order_delayed_p31",
                        "method": "card",
                    }
                ],
            },
        )

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        rzp_client = RazorpayClient(
            key_id="rzp_test_fixture",
            key_secret=SecretStr("secret"),
            http_client=http_client,
        )
        recon_res = await PaymentService.reconcile_order(
            session=db_session, order_id=order.id, rzp_client=rzp_client
        )
    assert recon_res["status"] == "PROCESSED"
    assert order.status == "PAID"

    # Step 2: Delayed webhook for this payment arrives much later
    payload = {
        "event": "payment.captured",
        "payload": {
            "order": {"entity": {"id": "order_delayed_p31", "amount": 150000, "currency": "INR"}},
            "payment": {
                "entity": {
                    "id": "pay_delayed_recovered_01",
                    "order_id": "order_delayed_p31",
                    "amount": 150000,
                    "currency": "INR",
                    "status": "captured",
                }
            },
        },
    }
    raw_body = json.dumps(payload).encode("utf-8")
    sig = _sign(raw_body, secret)

    delayed_res = await PaymentService.process_payment_webhook(
        session=db_session, raw_body=raw_body, signature_header=sig, webhook_secret=secret
    )
    assert delayed_res["status"] == "DUPLICATE_IGNORED"
    assert order.status == "PAID"

    # Step 3: Delayed payment.failed webhook arrives after order is already PAID
    fail_payload = {
        "event": "payment.failed",
        "payload": {
            "order": {"entity": {"id": "order_delayed_p31", "amount": 150000}},
            "payment": {
                "entity": {
                    "id": "pay_delayed_recovered_01",
                    "order_id": "order_delayed_p31",
                    "amount": 150000,
                    "status": "failed",
                }
            },
        },
    }
    raw_fail_body = json.dumps(fail_payload).encode("utf-8")
    fail_sig = _sign(raw_fail_body, secret)

    stale_fail_res = await PaymentService.process_payment_webhook(
        session=db_session, raw_body=raw_fail_body, signature_header=fail_sig, webhook_secret=secret
    )
    assert stale_fail_res["status"] == "STATE_REGRESSION_IGNORED"
    assert order.status == "PAID"


# =============================================================================
# 8. Webhook / Reconciliation Race
# =============================================================================
@pytest.mark.asyncio
async def test_webhook_reconciliation_race(db_session: AsyncSession) -> None:
    """Verifies concurrent webhook and reconciliation settle cleanly without duplicates."""
    merchant, session, quote, order = await _seed_test_order(
        db_session, amount_paise=180000, rzp_order_id="order_race_p31"
    )
    secret = TEST_WEBHOOK_SECRET
    payment_id = "pay_race_concurrent_01"

    # Webhook payload
    payload = {
        "event": "order.paid",
        "payload": {
            "order": {"entity": {"id": "order_race_p31", "amount": 180000, "currency": "INR"}},
            "payment": {
                "entity": {
                    "id": payment_id,
                    "order_id": "order_race_p31",
                    "amount": 180000,
                    "currency": "INR",
                    "status": "captured",
                }
            },
        },
    }
    raw_body = json.dumps(payload).encode("utf-8")
    sig = _sign(raw_body, secret)

    # Reconciliation client mock
    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={
                "entity": "collection",
                "count": 1,
                "items": [
                    {
                        "id": payment_id,
                        "entity": "payment",
                        "amount": 180000,
                        "currency": "INR",
                        "status": "captured",
                        "order_id": "order_race_p31",
                    }
                ],
            },
        )

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        rzp_client = RazorpayClient(
            key_id="rzp_test_fixture",
            key_secret=SecretStr("secret"),
            http_client=http_client,
        )

        # Run webhook first, then reconciliation
        res_webhook = await PaymentService.process_payment_webhook(
            session=db_session, raw_body=raw_body, signature_header=sig, webhook_secret=secret
        )
        res_recon = await PaymentService.reconcile_order(
            session=db_session, order_id=order.id, rzp_client=rzp_client
        )

    assert res_webhook["status"] == "PROCESSED"
    assert res_recon["status"] == "ALREADY_TERMINAL"
    assert order.status == "PAID"

    # Assert exactly 1 transaction record exists
    tx_stmt = select(TransactionRecord).where(
        TransactionRecord.merchant_id == merchant.id, TransactionRecord.settlement_ref == payment_id
    )
    tx_rows = (await db_session.execute(tx_stmt)).scalars().all()
    assert len(tx_rows) == 1


# =============================================================================
# 9. Razorpay Timeout Handling
# =============================================================================
@pytest.mark.asyncio
async def test_razorpay_timeout(db_session: AsyncSession) -> None:
    """Verifies Razorpay timeout during reconciliation fails safely without false success."""
    merchant, session, quote, order = await _seed_test_order(
        db_session, amount_paise=120000, rzp_order_id="order_timeout_p31"
    )

    def timeout_handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("Connection timed out waiting for Razorpay API")

    transport = httpx.MockTransport(timeout_handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = RazorpayClient(
            key_id="rzp_test_fixture",
            key_secret=SecretStr("secret"),
            http_client=http_client,
            timeout=1.0,
        )
        result = await PaymentService.reconcile_order(
            session=db_session, order_id=order.id, rzp_client=client
        )

    assert result["status"] == "RECONCILIATION_FAILED"
    assert result["retryable"] is True
    assert "timed out" in result["error"].lower()

    # Invariant: Order must NEVER be marked PAID on timeout!
    assert order.status == "PENDING_PAYMENT"

    # Invariant: Zero TransactionRecords committed
    tx_stmt = select(TransactionRecord).where(TransactionRecord.merchant_id == merchant.id)
    tx_rows = (await db_session.execute(tx_stmt)).scalars().all()
    assert len(tx_rows) == 0


# =============================================================================
# 10. Razorpay HTTP 4xx / 5xx Normalization
# =============================================================================
@pytest.mark.asyncio
async def test_razorpay_4xx_5xx(db_session: AsyncSession) -> None:
    """Verifies normalized exception hierarchy and retryability for HTTP 400, 404, 429, and 5xx."""

    # Test 400 Bad Request
    def handler_400(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=400,
            json={"error": {"code": "BAD_REQUEST_ERROR", "description": "Invalid amount"}},
        )

    transport_400 = httpx.MockTransport(handler_400)
    async with httpx.AsyncClient(transport=transport_400) as http_client:
        client = RazorpayClient("k", SecretStr("s"), http_client=http_client)
        with pytest.raises(RazorpayBadRequestError) as exc400:
            await client.fetch_order("order_xyz")
        assert exc400.value.status_code == 400
        assert exc400.value.is_client_error is True
        assert exc400.value.is_server_error is False
        assert exc400.value.is_retryable is False

    # Test 404 Not Found
    def handler_404(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=404,
            json={"error": {"code": "BAD_REQUEST_ERROR", "description": "Order not found"}},
        )

    transport_404 = httpx.MockTransport(handler_404)
    async with httpx.AsyncClient(transport=transport_404) as http_client:
        client = RazorpayClient("k", SecretStr("s"), http_client=http_client)
        with pytest.raises(RazorpayNotFoundError) as exc404:
            await client.fetch_order("order_nonexistent")
        assert exc404.value.status_code == 404
        assert exc404.value.is_retryable is False

    # Test 429 Rate Limit
    def handler_429(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=429,
            json={"error": {"code": "RATE_LIMIT_EXCEEDED", "description": "Too many requests"}},
        )

    transport_429 = httpx.MockTransport(handler_429)
    async with httpx.AsyncClient(transport=transport_429) as http_client:
        client = RazorpayClient("k", SecretStr("s"), http_client=http_client)
        with pytest.raises(RazorpayRateLimitError) as exc429:
            await client.fetch_order("order_xyz")
        assert exc429.value.status_code == 429
        assert exc429.value.is_retryable is True

    # Test 500 Server Error
    def handler_500(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=500,
            json={"error": {"code": "GATEWAY_ERROR", "description": "Internal server error"}},
        )

    transport_500 = httpx.MockTransport(handler_500)
    async with httpx.AsyncClient(transport=transport_500) as http_client:
        client = RazorpayClient("k", SecretStr("s"), http_client=http_client)
        with pytest.raises(RazorpayServerError) as exc500:
            await client.fetch_order("order_xyz")
        assert exc500.value.status_code == 500
        assert exc500.value.is_server_error is True
        assert exc500.value.is_retryable is True

    # Test reconcile_order handling 500 gracefully
    merchant, session, quote, order = await _seed_test_order(
        db_session, amount_paise=220000, rzp_order_id="order_500_p31"
    )
    async with httpx.AsyncClient(transport=transport_500) as http_client:
        client = RazorpayClient("k", SecretStr("s"), http_client=http_client)
        recon_500 = await PaymentService.reconcile_order(
            session=db_session, order_id=order.id, rzp_client=client
        )
    assert recon_500["status"] == "RECONCILIATION_FAILED"
    assert recon_500["retryable"] is True
    assert order.status == "PENDING_PAYMENT"


# =============================================================================
# 11. Payment State Regression Prevention
# =============================================================================
@pytest.mark.asyncio
async def test_payment_state_regression(db_session: AsyncSession) -> None:
    """Verifies that legal state transitions are enforced and regressions are rejected."""
    merchant, session, quote, order = await _seed_test_order(
        db_session, amount_paise=350000, rzp_order_id="order_regression_p31"
    )

    # 1. PaymentAttempt state machine validations
    payment = PaymentAttempt(
        order_id=order.id,
        rzp_order_id=order.rzp_order_id,
        rzp_payment_id="pay_regress_01",
        status="CAPTURED",
        amount_paise=350000,
    )
    db_session.add(payment)
    await db_session.flush()

    # Attempting to regress from CAPTURED to FAILED must raise InvalidStateTransitionError
    with pytest.raises(InvalidStateTransitionError):
        PaymentAttemptStateMachine.validate_transition(payment, "FAILED")

    # Attempting to regress from CAPTURED to INITIATED must raise InvalidStateTransitionError
    with pytest.raises(InvalidStateTransitionError):
        PaymentAttemptStateMachine.validate_transition(payment, "INITIATED")

    # Terminal state transition rejection: from FAILED to CAPTURED raises TerminalStateError
    payment_failed = PaymentAttempt(
        order_id=order.id,
        rzp_order_id=order.rzp_order_id,
        rzp_payment_id="pay_regress_failed",
        status="FAILED",
        amount_paise=350000,
    )
    db_session.add(payment_failed)
    await db_session.flush()

    with pytest.raises(TerminalStateError):
        PaymentAttemptStateMachine.validate_transition(payment_failed, "CAPTURED")

    # 2. Order state machine validation: from PAID back to PENDING_PAYMENT or CREATED
    order.status = "PAID"
    with pytest.raises(InvalidStateTransitionError):
        OrderStateMachine.validate_transition(order, "PENDING_PAYMENT")

    with pytest.raises(InvalidStateTransitionError):
        OrderStateMachine.validate_transition(order, "CREATED")


# =============================================================================
# 12. Strict Transaction Binding Invariant Verification
# =============================================================================
@pytest.mark.asyncio
async def test_transaction_binding_violation(db_session: AsyncSession) -> None:
    """Verifies validate_transaction_binding raises TransactionBindingError on mismatch."""
    merchant, session, quote, order = await _seed_test_order(
        db_session, amount_paise=500000, rzp_order_id="order_binding_p31"
    )

    valid_attempt = PaymentAttempt(
        id=uuid.uuid4(),
        order_id=order.id,
        rzp_order_id=order.rzp_order_id,
        rzp_payment_id="pay_bind_valid",
        status="CAPTURED",
        amount_paise=500000,
    )

    # Valid binding passes without error
    PaymentService.validate_transaction_binding(
        payment_attempt=valid_attempt,
        order=order,
        merchant_id=merchant.id,
        amount_paise=500000,
    )

    # Violation 1: PaymentAttempt belongs to a different order
    wrong_order_attempt = PaymentAttempt(
        id=uuid.uuid4(),
        order_id=uuid.uuid4(),  # Different order ID!
        rzp_order_id=order.rzp_order_id,
        rzp_payment_id="pay_bind_wrong_order",
        status="CAPTURED",
        amount_paise=500000,
    )
    with pytest.raises(TransactionBindingError, match="does not match target order"):
        PaymentService.validate_transaction_binding(
            payment_attempt=wrong_order_attempt,
            order=order,
            merchant_id=merchant.id,
            amount_paise=500000,
        )

    # Violation 2: Merchant ID mismatch
    wrong_merchant_id = uuid.uuid4()
    with pytest.raises(TransactionBindingError, match="does not match order merchant"):
        PaymentService.validate_transaction_binding(
            payment_attempt=valid_attempt,
            order=order,
            merchant_id=wrong_merchant_id,
            amount_paise=500000,
        )

    # Violation 3: PaymentAttempt is not CAPTURED (e.g. FAILED or INITIATED)
    uncaptured_attempt = PaymentAttempt(
        id=uuid.uuid4(),
        order_id=order.id,
        rzp_order_id=order.rzp_order_id,
        rzp_payment_id="pay_bind_uncaptured",
        status="FAILED",
        amount_paise=500000,
    )
    with pytest.raises(TransactionBindingError, match="must be 'CAPTURED'"):
        PaymentService.validate_transaction_binding(
            payment_attempt=uncaptured_attempt,
            order=order,
            merchant_id=merchant.id,
            amount_paise=500000,
        )

    # Violation 4: Amount mismatch between transaction and order / attempt
    with pytest.raises(TransactionBindingError, match="amount 499999 does not match"):
        PaymentService.validate_transaction_binding(
            payment_attempt=valid_attempt,
            order=order,
            merchant_id=merchant.id,
            amount_paise=499999,
        )
