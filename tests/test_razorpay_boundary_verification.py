"""Comprehensive Razorpay Test-Mode Payment Boundary Verification Suite.

Tests the full payment boundary under realistic test-mode conditions:
1. Live test-mode order creation via Razorpay API.
2. Webhook -> HMAC -> PaymentService -> FSM -> TransactionRecord -> AuditEvent.
3. Simulated payment failure handling.
4. Webhook replay / idempotency protection against duplicate financial ledger entries.
5. Tampered payload and invalid signature rejection.
6. Out-of-band reconciliation recovering state from missing webhooks.
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
from agent_ready_merchant.integrations.razorpay.exceptions import InvalidWebhookSignatureError
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.order import Order
from agent_ready_merchant.models.payment import PaymentAttempt
from agent_ready_merchant.models.product import Product, ProductVariant
from agent_ready_merchant.models.quote import PriceQuote, QuoteItem
from agent_ready_merchant.models.session import BuyerAgentSession
from agent_ready_merchant.models.transaction import TransactionRecord
from agent_ready_merchant.services.payment_service import PaymentService


def _sign(body: bytes, secret: str) -> str:
    return hmac.new(key=secret.encode("utf-8"), msg=body, digestmod=hashlib.sha256).hexdigest()


@pytest.mark.asyncio
async def test_full_boundary_successful_payment_flow(db_session: AsyncSession) -> None:
    """Tests Order -> Webhook -> HMAC -> PaymentService -> FSM -> TxRecord -> AuditEvent."""
    now = datetime.now(UTC)
    settings = get_settings()
    webhook_secret = (
        settings.RAZORPAY_WEBHOOK_SECRET.get_secret_value() or "test_webhook_secret_12345"
    )

    # 1. Setup Domain Entities
    merchant = Merchant(
        name="Boundary Store", slug="boundary-store", rzp_key_id=settings.RAZORPAY_KEY_ID
    )
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="agent_boundary_tester",
        auth_token_hash="hash_b1",
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    product = Product(
        merchant_id=merchant.id,
        sku="SKU-BOUND-01",
        title="Boundary Verification Item",
        category="Hardware",
        base_price_paise=50000,  # ₹500
        floor_price_paise=40000,
    )
    db_session.add(product)
    await db_session.flush()

    variant = ProductVariant(product_id=product.id, sku="SKU-BOUND-01-V", title="Standard")
    db_session.add(variant)
    await db_session.flush()

    quote = PriceQuote(
        session_id=session.id,
        merchant_id=merchant.id,
        status="ACCEPTED",
        subtotal_paise=50000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=50000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=str(uuid.uuid4()),
    )
    db_session.add(quote)
    await db_session.flush()

    quote_item = QuoteItem(
        quote_id=quote.id,
        variant_id=variant.id,
        quantity=1,
        unit_price_paise=50000,
        total_price_paise=50000,
    )
    db_session.add(quote_item)
    await db_session.flush()

    # 2. Step 1: Create Order via Razorpay Client (Live Sandbox if configured)
    rzp_client = RazorpayClient(
        key_id=settings.RAZORPAY_KEY_ID,
        key_secret=settings.RAZORPAY_KEY_SECRET,
        base_url=settings.RAZORPAY_API_BASE_URL,
    )

    order = await PaymentService.create_order_from_accepted_quote(
        session=db_session,
        quote_id=quote.id,
        buyer_email="tester@boundary.com",
        shipping_address={"city": "Mumbai", "postal_code": "400001", "country": "IN"},
        rzp_client=rzp_client,
    )

    assert order.id is not None
    assert order.status == "PENDING_PAYMENT"
    assert order.amount_paise == 50000
    assert order.rzp_order_id is not None
    assert order.rzp_order_id.startswith("order_")

    # 3. Step 2 & 3: Simulate payment success webhook with HMAC signature
    sim_payment_id = f"pay_test_sim_{uuid.uuid4().hex[:12]}"
    webhook_payload = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": sim_payment_id,
                    "order_id": order.rzp_order_id,
                    "amount": 50000,
                    "status": "captured",
                    "method": "upi",
                    "currency": "INR",
                }
            }
        },
    }
    raw_body = json.dumps(webhook_payload).encode("utf-8")
    valid_signature = _sign(raw_body, webhook_secret)

    # Process webhook through PaymentService
    webhook_res = await PaymentService.process_payment_webhook(
        session=db_session,
        raw_body=raw_body,
        signature_header=valid_signature,
        webhook_secret=webhook_secret,
    )

    assert webhook_res["status"] == "PROCESSED"
    assert webhook_res["order_status"] == "PAID"
    assert order.status == "PAID"

    # Verify PaymentAttempt entity
    pay_stmt = select(PaymentAttempt).where(PaymentAttempt.order_id == order.id)
    payment = (await db_session.execute(pay_stmt)).scalar_one()
    assert payment.status == "CAPTURED"
    assert payment.rzp_payment_id == sim_payment_id
    assert payment.amount_paise == 50000

    # Verify Append-Only TransactionRecord
    tx_stmt = select(TransactionRecord).where(TransactionRecord.payment_attempt_id == payment.id)
    tx = (await db_session.execute(tx_stmt)).scalar_one()
    assert tx.status == "COMMITTED"
    assert tx.amount_paise == 50000
    assert tx.entry_type == "CREDIT"
    assert tx.settlement_ref == sim_payment_id

    # Verify AuditEvent recorded
    audit_stmt = select(AuditEvent).where(AuditEvent.merchant_id == merchant.id)
    audit_events = (await db_session.execute(audit_stmt)).scalars().all()
    assert len(audit_events) >= 2  # Order transition and payment transition events

    # 4. Step 5: Webhook Replay / Idempotency Test
    replay_res = await PaymentService.process_payment_webhook(
        session=db_session,
        raw_body=raw_body,
        signature_header=valid_signature,
        webhook_secret=webhook_secret,
    )
    assert replay_res["status"] == "DUPLICATE_IGNORED"

    # Ensure NO duplicate transaction record was created
    all_txs = (await db_session.execute(tx_stmt)).scalars().all()
    assert len(all_txs) == 1


@pytest.mark.asyncio
async def test_boundary_failed_payment_handling(db_session: AsyncSession) -> None:
    """Tests simulated failed payment webhook handling."""
    now = datetime.now(UTC)
    webhook_secret = "test_webhook_secret_12345"

    merchant = Merchant(name="FailStore", slug="fail-store", rzp_key_id="rzp_test_fail")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="buyer_fail_test",
        auth_token_hash="hash_fail",
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    quote = PriceQuote(
        session_id=session.id,
        merchant_id=merchant.id,
        status="ACCEPTED",
        subtotal_paise=100000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=100000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=str(uuid.uuid4()),
    )
    db_session.add(quote)
    await db_session.flush()

    order = Order(
        quote_id=quote.id,
        merchant_id=merchant.id,
        status="PAYMENT_PROCESSING",
        amount_paise=100000,
        currency="INR",
        buyer_email="buyer@fail.com",
        rzp_order_id="order_rzp_fail_target",
    )
    db_session.add(order)
    await db_session.flush()

    sim_failed_payment_id = "pay_test_failed_01"
    failed_payload = {
        "event": "payment.failed",
        "payload": {
            "payment": {
                "entity": {
                    "id": sim_failed_payment_id,
                    "order_id": "order_rzp_fail_target",
                    "amount": 100000,
                    "status": "failed",
                    "error_code": "BAD_REQUEST_ERROR",
                    "error_description": "Payment declined by customer bank",
                }
            }
        },
    }
    raw_body = json.dumps(failed_payload).encode("utf-8")
    signature = _sign(raw_body, webhook_secret)

    res = await PaymentService.process_payment_webhook(
        session=db_session,
        raw_body=raw_body,
        signature_header=signature,
        webhook_secret=webhook_secret,
    )
    assert res["status"] == "FAILURE_RECORDED"
    assert order.status == "PAYMENT_FAILED"

    # Verify failed PaymentAttempt stored with error details
    pay_stmt = select(PaymentAttempt).where(PaymentAttempt.order_id == order.id)
    payment = (await db_session.execute(pay_stmt)).scalar_one()
    assert payment.status == "FAILED"
    assert payment.error_code == "BAD_REQUEST_ERROR"
    assert "Payment declined" in str(payment.error_description)

    # Verify NO TransactionRecord was created for failed payment
    tx_stmt = select(TransactionRecord).where(TransactionRecord.payment_attempt_id == payment.id)
    tx = (await db_session.execute(tx_stmt)).scalar_one_or_none()
    assert tx is None


@pytest.mark.asyncio
async def test_boundary_tampered_webhook_rejection(db_session: AsyncSession) -> None:
    """Verifies that tampered payloads and invalid signatures are strictly rejected."""
    webhook_secret = "test_webhook_secret_12345"
    raw_body = b'{"event":"payment.captured","amount":50000}'
    tampered_sig = "a1b2c3d4e5f60718293a4b5c6d7e8f90"  # Invalid forged signature

    with pytest.raises(InvalidWebhookSignatureError):
        await PaymentService.process_payment_webhook(
            session=db_session,
            raw_body=raw_body,
            signature_header=tampered_sig,
            webhook_secret=webhook_secret,
        )


@pytest.mark.asyncio
async def test_boundary_reconciliation_missing_webhook(db_session: AsyncSession) -> None:
    """Tests out-of-band reconciliation recovery when webhook was completely dropped/lost."""
    now = datetime.now(UTC)
    merchant = Merchant(name="ReconStoreB", slug="recon-store-b", rzp_key_id="rzp_test_recon_b")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="buyer_recon_test_b",
        auth_token_hash="hash_recon_b",
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    quote = PriceQuote(
        session_id=session.id,
        merchant_id=merchant.id,
        status="ACCEPTED",
        subtotal_paise=350000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=350000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=str(uuid.uuid4()),
    )
    db_session.add(quote)
    await db_session.flush()

    order = Order(
        quote_id=quote.id,
        merchant_id=merchant.id,
        status="PENDING_PAYMENT",  # Webhook dropped; order still pending
        amount_paise=350000,
        currency="INR",
        buyer_email="buyer@lostwebhook.com",
        rzp_order_id="order_rzp_lost_webhook",
    )
    db_session.add(order)
    await db_session.flush()

    # Mock Razorpay GET /v1/orders/{id}/payments returning captured payment
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/orders/order_rzp_lost_webhook/payments"
        return httpx.Response(
            status_code=200,
            json={
                "entity": "collection",
                "count": 1,
                "items": [
                    {
                        "id": "pay_lost_reconciled_99",
                        "entity": "payment",
                        "amount": 350000,
                        "currency": "INR",
                        "status": "captured",
                        "order_id": "order_rzp_lost_webhook",
                        "method": "upi",
                    }
                ],
            },
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = RazorpayClient(
            key_id="rzp_test_recon_b",
            key_secret=SecretStr("secret"),
            http_client=http_client,
        )
        recon_res = await PaymentService.reconcile_order(
            session=db_session,
            order_id=order.id,
            rzp_client=client,
        )

    assert recon_res["status"] == "PROCESSED"
    assert order.status == "PAID"

    # Verify PaymentAttempt and TransactionRecord were created during reconciliation
    pay_stmt = select(PaymentAttempt).where(PaymentAttempt.order_id == order.id)
    payment = (await db_session.execute(pay_stmt)).scalar_one()
    assert payment.status == "CAPTURED"
    assert payment.rzp_payment_id == "pay_lost_reconciled_99"

    tx_stmt = select(TransactionRecord).where(TransactionRecord.payment_attempt_id == payment.id)
    tx = (await db_session.execute(tx_stmt)).scalar_one()
    assert tx.status == "COMMITTED"
    assert tx.amount_paise == 350000
