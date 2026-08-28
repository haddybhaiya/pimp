"""Integration tests for PaymentService, order lifecycle, webhooks, and reconciliation."""

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

from agent_ready_merchant.integrations.razorpay.client import RazorpayClient
from agent_ready_merchant.integrations.razorpay.exceptions import (
    AmountMismatchFraudError,
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


def _sign(body: bytes, secret: str) -> str:
    return hmac.new(key=secret.encode("utf-8"), msg=body, digestmod=hashlib.sha256).hexdigest()


@pytest.mark.asyncio
async def test_order_creation_from_accepted_quote(db_session: AsyncSession) -> None:
    """Verifies that an ACCEPTED quote generates a Razorpay Order and local Order entity."""
    now = datetime.now(UTC)
    merchant = Merchant(name="Apex Store", slug="apex-store", rzp_key_id="rzp_test_apex")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="buyer_apex",
        auth_token_hash="hash_a",
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    product = Product(
        merchant_id=merchant.id,
        sku="SKU-APEX-1",
        title="Apex Shoe",
        category="Footwear",
        base_price_paise=500000,
        floor_price_paise=400000,
    )
    db_session.add(product)
    await db_session.flush()

    variant = ProductVariant(product_id=product.id, sku="SKU-APEX-1-V", title="Size 10")
    db_session.add(variant)
    await db_session.flush()

    quote = PriceQuote(
        session_id=session.id,
        merchant_id=merchant.id,
        status="ACCEPTED",  # Must be ACCEPTED
        subtotal_paise=500000,
        discount_paise=50000,
        shipping_paise=0,
        total_paise=450000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=str(uuid.uuid4()),
    )
    db_session.add(quote)
    await db_session.flush()

    quote_item = QuoteItem(
        quote_id=quote.id,
        variant_id=variant.id,
        quantity=1,
        unit_price_paise=450000,
        total_price_paise=450000,
    )
    db_session.add(quote_item)
    await db_session.flush()

    # Mock Razorpay API response
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={
                "id": "order_EKwxwAgItmmXdp",
                "entity": "order",
                "amount": 450000,
                "amount_paid": 0,
                "amount_due": 450000,
                "currency": "INR",
                "receipt": f"ord_{quote.id.hex[:32]}",
                "status": "created",
                "attempts": 0,
                "created_at": int(now.timestamp()),
            },
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = RazorpayClient(
            key_id="rzp_test_apex",
            key_secret=SecretStr("secret"),
            http_client=http_client,
        )
        order = await PaymentService.create_order_from_accepted_quote(
            session=db_session,
            quote_id=quote.id,
            buyer_email="buyer@example.com",
            shipping_address={"city": "Bengaluru", "postal_code": "560001", "country": "IN"},
            rzp_client=client,
        )

    assert order.id is not None
    assert order.rzp_order_id == "order_EKwxwAgItmmXdp"
    assert order.status == "PENDING_PAYMENT"
    assert order.amount_paise == 450000

    # Verify idempotency: calling again returns the existing order
    order_dup = await PaymentService.create_order_from_accepted_quote(
        session=db_session,
        quote_id=quote.id,
        buyer_email="buyer@example.com",
        shipping_address={"city": "Bengaluru"},
        rzp_client=client,
    )
    assert order_dup.id == order.id


@pytest.mark.asyncio
async def test_webhook_payment_success_and_idempotency(db_session: AsyncSession) -> None:
    """Verifies order.paid webhook settles Order and records transaction idempotently."""
    now = datetime.now(UTC)
    webhook_secret = "rzp_webhook_secret_xyz"

    merchant = Merchant(name="WebStore", slug="web-store", rzp_key_id="rzp_test_web")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="buyer_web",
        auth_token_hash="hash_w",
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    quote = PriceQuote(
        session_id=session.id,
        merchant_id=merchant.id,
        status="ACCEPTED",
        subtotal_paise=500000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=500000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=str(uuid.uuid4()),
    )
    db_session.add(quote)
    await db_session.flush()

    order = Order(
        quote_id=quote.id,
        merchant_id=merchant.id,
        status="PENDING_PAYMENT",
        amount_paise=500000,
        currency="INR",
        buyer_email="buyer@web.com",
        rzp_order_id="order_rzp_target_01",
    )
    db_session.add(order)
    await db_session.flush()

    # 1. Simulate order.paid webhook payload
    webhook_payload_dict = {
        "event": "order.paid",
        "payload": {
            "order": {
                "entity": {
                    "id": "order_rzp_target_01",
                    "amount": 500000,
                    "currency": "INR",
                    "status": "paid",
                }
            },
            "payment": {
                "entity": {
                    "id": "pay_test_payment_99",
                    "order_id": "order_rzp_target_01",
                    "amount": 500000,
                    "currency": "INR",
                    "status": "captured",
                    "method": "upi",
                }
            },
        },
    }
    raw_body = json.dumps(webhook_payload_dict).encode("utf-8")
    signature = _sign(raw_body, webhook_secret)

    # 2. Process first webhook delivery
    res = await PaymentService.process_payment_webhook(
        session=db_session,
        raw_body=raw_body,
        signature_header=signature,
        webhook_secret=webhook_secret,
    )
    assert res["status"] == "PROCESSED"
    assert res["order_status"] == "PAID"

    # Verify Order is PAID
    assert order.status == "PAID"

    # Verify PaymentAttempt created
    pay_stmt = select(PaymentAttempt).where(PaymentAttempt.order_id == order.id)
    payment = (await db_session.execute(pay_stmt)).scalar_one()
    assert payment.status == "CAPTURED"
    assert payment.rzp_payment_id == "pay_test_payment_99"

    # Verify TransactionRecord in ledger
    tx_stmt = select(TransactionRecord).where(TransactionRecord.payment_attempt_id == payment.id)
    tx_records = (await db_session.execute(tx_stmt)).scalars().all()
    assert len(tx_records) == 1
    assert tx_records[0].amount_paise == 500000
    assert tx_records[0].entry_type == "CREDIT"
    assert tx_records[0].status == "COMMITTED"

    # 3. Process DUPLICATE webhook delivery
    res_dup = await PaymentService.process_payment_webhook(
        session=db_session,
        raw_body=raw_body,
        signature_header=signature,
        webhook_secret=webhook_secret,
    )
    assert res_dup["status"] == "DUPLICATE_IGNORED"

    # Verify NO duplicate TransactionRecord was created
    tx_records_after_dup = (await db_session.execute(tx_stmt)).scalars().all()
    assert len(tx_records_after_dup) == 1


@pytest.mark.asyncio
async def test_webhook_fraud_amount_mismatch_detection(db_session: AsyncSession) -> None:
    """Verifies amount mismatch raises AmountMismatchFraudError and logs fraud audit."""
    now = datetime.now(UTC)
    webhook_secret = "rzp_secret"

    merchant = Merchant(name="FraudStore", slug="fraud-store", rzp_key_id="rzp_test_fraud")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="buyer_fraud",
        auth_token_hash="hash_f",
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    quote = PriceQuote(
        session_id=session.id,
        merchant_id=merchant.id,
        status="ACCEPTED",
        subtotal_paise=500000,  # ₹5,000
        discount_paise=0,
        shipping_paise=0,
        total_paise=500000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=str(uuid.uuid4()),
    )
    db_session.add(quote)
    await db_session.flush()

    order = Order(
        quote_id=quote.id,
        merchant_id=merchant.id,
        status="PENDING_PAYMENT",
        amount_paise=500000,  # Local order expects ₹5,000 (500,000 paise)
        currency="INR",
        buyer_email="buyer@fraud.com",
        rzp_order_id="order_rzp_fraud_01",
    )
    db_session.add(order)
    await db_session.flush()

    # Webhook attempts to claim payment captured with only 10,000 paise (₹100)
    fake_payload = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_fake_cheap",
                    "order_id": "order_rzp_fraud_01",
                    "amount": 10000,  # Only ₹100!
                    "currency": "INR",
                    "status": "captured",
                }
            }
        },
    }
    raw_body = json.dumps(fake_payload).encode("utf-8")
    signature = _sign(raw_body, webhook_secret)

    with pytest.raises(AmountMismatchFraudError):
        await PaymentService.process_payment_webhook(
            session=db_session,
            raw_body=raw_body,
            signature_header=signature,
            webhook_secret=webhook_secret,
        )

    # Order must NOT be marked PAID
    assert order.status == "PENDING_PAYMENT"

    # Audit event must record fraud attempt
    audit_stmt = select(AuditEvent).where(AuditEvent.event_type == "PAYMENT_AMOUNT_FRAUD_DETECTED")
    audit_event = (await db_session.execute(audit_stmt)).scalar_one_or_none()
    assert audit_event is not None
    assert audit_event.payload["expected_amount_paise"] == 500000
    assert audit_event.payload["received_amount_paise"] == 10000


@pytest.mark.asyncio
async def test_reconciliation_recovers_missing_webhook(db_session: AsyncSession) -> None:
    """Verifies that out-of-band reconciliation queries Razorpay and completes settlement."""
    now = datetime.now(UTC)
    merchant = Merchant(name="ReconStore", slug="recon-store", rzp_key_id="rzp_test_recon")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="buyer_recon",
        auth_token_hash="hash_r",
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    quote = PriceQuote(
        session_id=session.id,
        merchant_id=merchant.id,
        status="ACCEPTED",
        subtotal_paise=250000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=250000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=str(uuid.uuid4()),
    )
    db_session.add(quote)
    await db_session.flush()

    order = Order(
        quote_id=quote.id,
        merchant_id=merchant.id,
        status="PENDING_PAYMENT",  # Webhook was lost in network
        amount_paise=250000,
        currency="INR",
        buyer_email="buyer@recon.com",
        rzp_order_id="order_rzp_recon_99",
    )
    db_session.add(order)
    await db_session.flush()

    # Mock Razorpay GET /v1/orders/{id}/payments returning captured payment
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/orders/order_rzp_recon_99/payments"
        return httpx.Response(
            status_code=200,
            json={
                "entity": "collection",
                "count": 1,
                "items": [
                    {
                        "id": "pay_recon_recovered_01",
                        "entity": "payment",
                        "amount": 250000,
                        "currency": "INR",
                        "status": "captured",
                        "order_id": "order_rzp_recon_99",
                        "method": "netbanking",
                    }
                ],
            },
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = RazorpayClient(
            key_id="rzp_test_recon",
            key_secret=SecretStr("secret"),
            http_client=http_client,
        )
        res = await PaymentService.reconcile_order(
            session=db_session,
            order_id=order.id,
            rzp_client=client,
        )

    assert res["status"] == "PROCESSED"
    assert order.status == "PAID"

    # Verify transaction record was committed
    tx_stmt = select(TransactionRecord).where(TransactionRecord.merchant_id == merchant.id)
    tx = (await db_session.execute(tx_stmt)).scalar_one()
    assert tx.status == "COMMITTED"
    assert tx.amount_paise == 250000
    assert tx.settlement_ref == "pay_recon_recovered_01"
