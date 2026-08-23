"""Tests for SQLAlchemy database models, constraints, and relationships."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.inventory import InventoryItem
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.order import Order, OrderItem
from agent_ready_merchant.models.payment import PaymentAttempt
from agent_ready_merchant.models.product import Product, ProductVariant
from agent_ready_merchant.models.quote import PriceQuote, QuoteItem
from agent_ready_merchant.models.session import BuyerAgentSession
from agent_ready_merchant.models.transaction import TransactionRecord


@pytest.mark.asyncio
async def test_create_merchant_and_product_hierarchy(db_session: AsyncSession) -> None:
    """Verifies creation of Merchant, Product, ProductVariant, and InventoryItem."""
    merchant = Merchant(
        name="Apex Athletics",
        slug="apex-athletics",
        status="ACTIVE",
        currency="INR",
        rzp_key_id="rzp_test_Apex123",
    )
    db_session.add(merchant)
    await db_session.flush()

    assert merchant.id is not None
    assert merchant.version == 1
    assert merchant.created_at is not None

    # Add Product
    product = Product(
        merchant_id=merchant.id,
        sku="APEX-SHOE-01",
        title="Apex Velocity Pro",
        description="High performance running shoe",
        category="Shoes",
        base_price_paise=500000,
        floor_price_paise=450000,
        is_negotiable=True,
    )
    db_session.add(product)
    await db_session.flush()

    # Add Variant
    variant = ProductVariant(
        product_id=product.id,
        sku="APEX-SHOE-01-SZ9",
        title="Apex Velocity Pro - Size 9",
        attributes={"size": "9", "color": "black"},
    )
    db_session.add(variant)
    await db_session.flush()

    # Add Inventory Item
    inventory = InventoryItem(
        variant_id=variant.id,
        available_quantity=10,
        reserved_quantity=0,
        safety_threshold=2,
    )
    db_session.add(inventory)
    await db_session.flush()

    assert inventory.available_quantity == 10
    assert inventory.version == 1

    # Verify query through relationships
    stmt = (
        select(Merchant).options(selectinload(Merchant.products)).where(Merchant.id == merchant.id)
    )
    result = await db_session.execute(stmt)
    fetched_merchant = result.scalar_one()
    assert len(fetched_merchant.products) == 1
    assert fetched_merchant.products[0].sku == "APEX-SHOE-01"


@pytest.mark.asyncio
async def test_unique_constraint_merchant_slug(db_session: AsyncSession) -> None:
    """Verifies that duplicate merchant slugs trigger IntegrityError."""
    m1 = Merchant(
        name="Merchant One",
        slug="unique-merchant",
        rzp_key_id="rzp_test_1",
    )
    db_session.add(m1)
    await db_session.flush()

    m2 = Merchant(
        name="Merchant Two",
        slug="unique-merchant",  # Duplicate slug!
        rzp_key_id="rzp_test_2",
    )
    db_session.add(m2)
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_quote_to_order_and_payment_flow(db_session: AsyncSession) -> None:
    """Verifies full entity linkage: Session -> Quote -> Order -> PaymentAttempt -> TxRecord."""
    now = datetime.now(UTC)

    # 1. Merchant & Product Setup
    merchant = Merchant(name="Store", slug="store", rzp_key_id="rzp_test_store")
    db_session.add(merchant)
    await db_session.flush()

    product = Product(
        merchant_id=merchant.id,
        sku="SKU-1",
        title="Item 1",
        category="Cat",
        base_price_paise=100000,
        floor_price_paise=90000,
    )
    db_session.add(product)
    await db_session.flush()

    variant = ProductVariant(product_id=product.id, sku="SKU-1-V", title="Item 1 Var")
    db_session.add(variant)
    await db_session.flush()

    # 2. Buyer Session
    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="agent_buyer_007",
        auth_token_hash="hash_1234567890abcdef",
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    # 3. Price Quote
    quote = PriceQuote(
        session_id=session.id,
        merchant_id=merchant.id,
        status="ACCEPTED",
        subtotal_paise=100000,
        discount_paise=10000,
        shipping_paise=0,
        total_paise=90000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=str(uuid.uuid4()),
    )
    db_session.add(quote)
    await db_session.flush()

    quote_item = QuoteItem(
        quote_id=quote.id,
        variant_id=variant.id,
        quantity=1,
        unit_price_paise=90000,
        total_price_paise=90000,
    )
    db_session.add(quote_item)
    await db_session.flush()

    # 4. Order
    order = Order(
        quote_id=quote.id,
        merchant_id=merchant.id,
        status="PENDING_PAYMENT",
        amount_paise=90000,
        currency="INR",
        buyer_email="buyer@example.com",
        shipping_address={"city": "Bengaluru", "postal_code": "560001"},
        rzp_order_id="order_test_rzp_001",
    )
    db_session.add(order)
    await db_session.flush()

    order_item = OrderItem(
        order_id=order.id,
        variant_id=variant.id,
        quantity=1,
        unit_price_paise=90000,
        total_price_paise=90000,
    )
    db_session.add(order_item)
    await db_session.flush()

    # 5. Payment Attempt
    payment_attempt = PaymentAttempt(
        order_id=order.id,
        rzp_order_id="order_test_rzp_001",
        rzp_payment_id="pay_test_rzp_999",
        status="CAPTURED",
        amount_paise=90000,
        payment_method="card",
    )
    db_session.add(payment_attempt)
    await db_session.flush()

    # 6. Transaction Record (Append-only)
    tx = TransactionRecord(
        payment_attempt_id=payment_attempt.id,
        merchant_id=merchant.id,
        entry_type="CREDIT",
        amount_paise=90000,
        status="COMMITTED",
        settlement_ref="rzp_settle_ref_1",
    )
    db_session.add(tx)
    await db_session.flush()

    # 7. Audit Event
    audit = AuditEvent(
        merchant_id=merchant.id,
        session_id=session.id,
        actor_type="SYSTEM",
        event_type="PAYMENT_CAPTURED",
        payload={"amount_paise": 90000, "rzp_payment_id": "pay_test_rzp_999"},
        event_hash="hash_audit_event_1",
    )
    db_session.add(audit)
    await db_session.flush()

    assert tx.id is not None
    assert audit.id is not None
    assert order.amount_paise == 90000
