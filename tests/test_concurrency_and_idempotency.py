"""Concurrency and Idempotency Verification Suite for Phase 1.5."""

import hashlib
import hmac
import json
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.order import Order
from agent_ready_merchant.models.payment import PaymentAttempt
from agent_ready_merchant.models.quote import PriceQuote
from agent_ready_merchant.models.session import BuyerAgentSession
from agent_ready_merchant.models.transaction import TransactionRecord
from agent_ready_merchant.services.payment_service import PaymentService


def _sign(body: bytes, secret: str) -> str:
    return hmac.new(key=secret.encode("utf-8"), msg=body, digestmod=hashlib.sha256).hexdigest()


@pytest.mark.asyncio
async def test_duplicate_webhook_burst_guarantees_single_transaction_record(
    db_session: AsyncSession,
) -> None:
    """Verifies that delivering the identical payment.captured webhook multiple times

    commits exactly ONE TransactionRecord and ignores subsequent deliveries idempotently.
    """
    now = datetime.now(UTC)
    merchant = Merchant(name="Burst Merchant", slug="burst-merchant", rzp_key_id="rzp_test_burst")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="buyer_burst",
        auth_token_hash="hash_burst",
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
        merchant_id=merchant.id,
        quote_id=quote.id,
        buyer_email="burst@example.com",
        status="PENDING_PAYMENT",
        amount_paise=350000,
        currency="INR",
        rzp_order_id="order_BURST_01",
    )
    db_session.add(order)
    await db_session.flush()

    webhook_payload = {
        "event": "payment.captured",
        "payload": {
            "order": {
                "entity": {
                    "id": "order_BURST_01",
                    "amount": 350000,
                    "currency": "INR",
                    "status": "paid",
                }
            },
            "payment": {
                "entity": {
                    "id": "pay_BURST_CAPTURED_01",
                    "order_id": "order_BURST_01",
                    "amount": 350000,
                    "currency": "INR",
                    "status": "captured",
                }
            },
        },
    }
    raw_body = json.dumps(webhook_payload).encode("utf-8")
    secret = "burst_secret"
    signature = _sign(raw_body, secret)

    # 1. First webhook delivery -> PROCESSED
    res1 = await PaymentService.process_payment_webhook(
        session=db_session,
        raw_body=raw_body,
        signature_header=signature,
        webhook_secret=secret,
    )
    assert res1["status"] == "PROCESSED"
    assert res1["order_status"] == "PAID"

    # 2. Second webhook delivery (replay/burst) -> DUPLICATE_IGNORED
    res2 = await PaymentService.process_payment_webhook(
        session=db_session,
        raw_body=raw_body,
        signature_header=signature,
        webhook_secret=secret,
    )
    assert res2["status"] == "DUPLICATE_IGNORED"

    # 3. Third webhook delivery -> DUPLICATE_IGNORED
    res3 = await PaymentService.process_payment_webhook(
        session=db_session,
        raw_body=raw_body,
        signature_header=signature,
        webhook_secret=secret,
    )
    assert res3["status"] == "DUPLICATE_IGNORED"

    # 4. Strict assertion: Exactly ONE PaymentAttempt and ONE TransactionRecord exist
    pay_count = len(
        (
            await db_session.execute(
                select(PaymentAttempt).where(PaymentAttempt.order_id == order.id)
            )
        )
        .scalars()
        .all()
    )
    assert pay_count == 1

    tx_count = len(
        (
            await db_session.execute(
                select(TransactionRecord).where(
                    TransactionRecord.settlement_ref == "pay_BURST_CAPTURED_01"
                )
            )
        )
        .scalars()
        .all()
    )
    assert tx_count == 1
