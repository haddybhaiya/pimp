"""Tests for external Razorpay order duplicate protection (timeout orphans).

Verifies that a PENDING external-order breadcrumb (written when Razorpay
accepted an order whose local transaction was subsequently lost) causes
create_order_from_accepted_quote to REUSE the remote order instead of creating
a duplicate — and that failed/stale breadcrumbs fall back to fresh creation.
"""

import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.integrations.razorpay.client import RazorpayClient
from agent_ready_merchant.integrations.razorpay.models import RazorpayOrderResponse
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.inventory import InventoryItem
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.product import Product, ProductVariant
from agent_ready_merchant.models.quote import PriceQuote, QuoteItem
from agent_ready_merchant.models.session import BuyerAgentSession
from agent_ready_merchant.services.payment_service import PaymentService

QUOTE_TOTAL = 1_080_000


async def _seed_accepted_quote(db_session: AsyncSession) -> PriceQuote:
    merchant = Merchant(
        name="Reuse Test Merchant",
        slug=f"reuse-{uuid.uuid4().hex[:6]}",
        status="ACTIVE",
        currency="INR",
        rzp_key_id="rzp_test_placeholder",
    )
    db_session.add(merchant)
    await db_session.flush()

    buyer_session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="reuse-test-agent",
        auth_token_hash=hashlib.sha256(b"tok").hexdigest(),
        status="ACTIVE",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    db_session.add(buyer_session)
    await db_session.flush()

    product = Product(
        merchant_id=merchant.id,
        title="Reuse Shoes",
        sku=f"REUSE-SKU-{uuid.uuid4().hex[:6]}",
        description="d",
        category="Footwear",
        base_price_paise=1_200_000,
        floor_price_paise=900_000,
        is_negotiable=True,
        is_active=True,
    )
    db_session.add(product)
    await db_session.flush()

    variant = ProductVariant(
        product_id=product.id,
        sku=f"REUSE-VAR-{uuid.uuid4().hex[:6]}",
        title="Size 9",
        price_override_paise=1_200_000,
        is_active=True,
    )
    db_session.add(variant)
    await db_session.flush()

    db_session.add(
        InventoryItem(
            variant_id=variant.id,
            available_quantity=10,
            reserved_quantity=0,
            safety_threshold=1,
        )
    )

    quote = PriceQuote(
        session_id=buyer_session.id,
        merchant_id=merchant.id,
        status="ACCEPTED",
        subtotal_paise=1_200_000,
        discount_paise=120_000,
        shipping_paise=0,
        total_paise=QUOTE_TOTAL,
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
        idempotency_key=f"reuse-quote-{uuid.uuid4().hex[:8]}",
        version=2,
    )
    db_session.add(quote)
    await db_session.flush()
    db_session.add(
        QuoteItem(
            quote_id=quote.id,
            variant_id=variant.id,
            quantity=1,
            unit_price_paise=QUOTE_TOTAL,
            total_price_paise=QUOTE_TOTAL,
        )
    )
    await db_session.flush()
    return quote


async def _seed_breadcrumb(
    db_session: AsyncSession, merchant_id: uuid.UUID, quote: PriceQuote, status: str
) -> None:
    await AuditEvent.create_event(
        session=db_session,
        merchant_id=merchant_id,
        actor_type="SYSTEM",
        event_type="EXTERNAL_ORDER_ATTEMPT",
        payload={
            "quote_id": str(quote.id),
            "rzp_order_id": "order_orphan_1234567890",
            "amount_paise": QUOTE_TOTAL,
            "status": status,
        },
    )
    await db_session.flush()


def _rzp_order(order_id: str, amount: int, status: str = "created") -> RazorpayOrderResponse:
    return RazorpayOrderResponse(
        id=order_id,
        amount=amount,
        currency="INR",
        status=status,
        created_at=int(datetime.now(UTC).timestamp()),
    )


def _client() -> RazorpayClient:
    return RazorpayClient(key_id="rzp_test_placeholder", key_secret="placeholder_secret")


@pytest.mark.asyncio
async def test_pending_breadcrumb_reuses_orphaned_remote_order(
    db_session: AsyncSession,
) -> None:
    """PENDING breadcrumb → reuse remote order; create_order must NOT be called."""
    quote = await _seed_accepted_quote(db_session)
    await _seed_breadcrumb(db_session, quote.merchant_id, quote, status="PENDING")

    remote = _rzp_order("order_orphan_1234567890", QUOTE_TOTAL)

    with (
        patch.object(RazorpayClient, "fetch_order", return_value=remote),
        patch.object(
            RazorpayClient,
            "create_order",
            side_effect=AssertionError("duplicate external order must not be created"),
        ),
    ):
        order = await PaymentService.create_order_from_accepted_quote(
            session=db_session,
            quote_id=quote.id,
            buyer_email="reuse@example.com",
            shipping_address={"city": "Bengaluru"},
            rzp_client=_client(),
        )

    assert order.rzp_order_id == "order_orphan_1234567890"
    assert order.amount_paise == QUOTE_TOTAL


@pytest.mark.asyncio
async def test_failed_breadcrumb_creates_fresh_external_order(
    db_session: AsyncSession,
) -> None:
    """A stale/failed breadcrumb must not block fresh external order creation."""
    quote = await _seed_accepted_quote(db_session)
    await _seed_breadcrumb(db_session, quote.merchant_id, quote, status="FAILED")

    fresh = _rzp_order("order_fresh_0987654321", QUOTE_TOTAL)

    with patch.object(RazorpayClient, "create_order", return_value=fresh):
        order = await PaymentService.create_order_from_accepted_quote(
            session=db_session,
            quote_id=quote.id,
            buyer_email="reuse@example.com",
            shipping_address={"city": "Bengaluru"},
            rzp_client=_client(),
        )

    assert order.rzp_order_id == "order_fresh_0987654321"


@pytest.mark.asyncio
async def test_consumed_outcome_is_atomic_with_local_order(
    db_session: AsyncSession,
) -> None:
    """CONSUMED breadcrumb event is written in the same transaction as the Order."""
    quote = await _seed_accepted_quote(db_session)

    fresh = _rzp_order("order_atomic_1122334455", QUOTE_TOTAL)

    with patch.object(RazorpayClient, "create_order", return_value=fresh):
        order = await PaymentService.create_order_from_accepted_quote(
            session=db_session,
            quote_id=quote.id,
            buyer_email="reuse@example.com",
            shipping_address={"city": "Bengaluru"},
            rzp_client=_client(),
        )

    outcome = (
        await db_session.execute(
            select(AuditEvent)
            .where(
                AuditEvent.merchant_id == quote.merchant_id,
                AuditEvent.event_type == "EXTERNAL_ORDER_OUTCOME",
            )
            .order_by(AuditEvent.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()

    assert order is not None
    assert outcome is not None
    payload: dict[str, Any] = outcome.payload
    assert payload["status"] == "CONSUMED"
    assert payload["quote_id"] == str(quote.id)
