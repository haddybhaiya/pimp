"""Tests for FastAPI payment and webhook HTTP endpoints."""

import hashlib
import hmac
import json
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.config import get_settings
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.order import Order
from agent_ready_merchant.models.quote import PriceQuote
from agent_ready_merchant.models.session import BuyerAgentSession


def _sign(body: bytes, secret: str) -> str:
    return hmac.new(key=secret.encode("utf-8"), msg=body, digestmod=hashlib.sha256).hexdigest()


@pytest.mark.asyncio
async def test_api_webhook_valid_signature(client: AsyncClient, db_session: AsyncSession) -> None:
    """Verifies that POST /api/v1/payments/webhook processes valid signed payload."""
    now = datetime.now(UTC)
    settings = get_settings()
    secret = settings.RAZORPAY_WEBHOOK_SECRET.get_secret_value()

    merchant = Merchant(name="APIStore", slug="api-store", rzp_key_id="rzp_test_api")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="buyer_api",
        auth_token_hash="hash_api",
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
        status="PENDING_PAYMENT",
        amount_paise=100000,
        currency="INR",
        buyer_email="buyer@api.com",
        rzp_order_id="order_api_target_01",
    )
    db_session.add(order)
    await db_session.flush()

    payload = {
        "event": "order.paid",
        "payload": {
            "order": {
                "entity": {
                    "id": "order_api_target_01",
                    "amount": 100000,
                    "status": "paid",
                }
            },
            "payment": {
                "entity": {
                    "id": "pay_api_payment_01",
                    "order_id": "order_api_target_01",
                    "amount": 100000,
                    "status": "captured",
                    "method": "card",
                }
            },
        },
    }
    raw_body = json.dumps(payload).encode("utf-8")
    signature = _sign(raw_body, secret)

    response = await client.post(
        "/api/v1/payments/webhook",
        content=raw_body,
        headers={"X-Razorpay-Signature": signature, "Content-Type": "application/json"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PROCESSED"
    assert data["order_status"] == "PAID"


@pytest.mark.asyncio
async def test_api_webhook_invalid_signature_rejected(client: AsyncClient) -> None:
    """Verifies that invalid signature is rejected with HTTP 400 Bad Request."""
    raw_body = b'{"event":"payment.captured"}'
    response = await client.post(
        "/api/v1/payments/webhook",
        content=raw_body,
        headers={"X-Razorpay-Signature": "invalid_forged_sig", "Content-Type": "application/json"},
    )
    assert response.status_code == 400
    assert "Invalid webhook signature" in response.json()["detail"]


@pytest.mark.asyncio
async def test_api_webhook_fraud_mismatch_rejected(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Verifies that amount mismatch returns HTTP 422 Unprocessable Entity."""
    now = datetime.now(UTC)
    settings = get_settings()
    secret = settings.RAZORPAY_WEBHOOK_SECRET.get_secret_value()

    merchant = Merchant(name="FraudAPI", slug="fraud-api", rzp_key_id="rzp_test_fapi")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="buyer_fapi",
        auth_token_hash="hash_fapi",
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
        amount_paise=500000,  # Expected 500,000 paise
        currency="INR",
        buyer_email="buyer@fapi.com",
        rzp_order_id="order_fapi_target",
    )
    db_session.add(order)
    await db_session.flush()

    # Amount mismatch payload
    payload = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_fapi_bad",
                    "order_id": "order_fapi_target",
                    "amount": 10000,  # Only 10,000 paise
                    "status": "captured",
                }
            }
        },
    }
    raw_body = json.dumps(payload).encode("utf-8")
    signature = _sign(raw_body, secret)

    response = await client.post(
        "/api/v1/payments/webhook",
        content=raw_body,
        headers={"X-Razorpay-Signature": signature, "Content-Type": "application/json"},
    )
    assert response.status_code == 422
    assert "Amount mismatch fraud detected" in response.json()["detail"]
