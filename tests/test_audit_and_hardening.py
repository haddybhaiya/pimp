"""Tests for security hardening, audit hash chains, margin enforcement, and concurrency."""

import asyncio
import hashlib
import hmac
import json
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from agent_ready_merchant.integrations.razorpay.client import RazorpayClient
from agent_ready_merchant.models.agent_run import AgentRun
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.intent import BuyerIntent
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.order import Order
from agent_ready_merchant.models.payment import PaymentAttempt
from agent_ready_merchant.models.product import Product, ProductVariant
from agent_ready_merchant.models.quote import PriceQuote, QuoteItem
from agent_ready_merchant.models.session import BuyerAgentSession
from agent_ready_merchant.models.transaction import TransactionRecord
from agent_ready_merchant.policy.engine import DeterministicPolicyEngine
from agent_ready_merchant.policy.models import (
    PolicyContext,
    PolicyVerdict,
    QuoteItemProposal,
    QuoteProposal,
)
from agent_ready_merchant.services.payment_service import PaymentService
from agent_ready_merchant.state_machines.agent_run import AgentRunStateMachine
from agent_ready_merchant.state_machines.buyer_intent import BuyerIntentStateMachine
from agent_ready_merchant.tools.base import GatewayContext
from agent_ready_merchant.tools.handlers import (
    CreateOrderTool,
    NegotiateQuoteTool,
)
from agent_ready_merchant.tools.models import (
    CreateOrderParams,
    NegotiateQuoteParams,
    ShippingAddressParam,
)


def _sign(body: bytes, secret: str) -> str:
    return hmac.new(key=secret.encode("utf-8"), msg=body, digestmod=hashlib.sha256).hexdigest()


@pytest.mark.asyncio
async def test_audit_event_hash_chaining(db_session: AsyncSession) -> None:
    """Verifies that sequential audit events form a deterministic SHA-256 hash chain."""
    merchant = Merchant(
        name="Hash Chain Merchant",
        slug=f"hash-chain-{uuid.uuid4().hex[:8]}",
        currency="INR",
        rzp_key_id="rzp_test_123",
    )
    db_session.add(merchant)
    await db_session.flush()

    e1 = await AuditEvent.create_event(
        session=db_session,
        merchant_id=merchant.id,
        actor_type="SYSTEM",
        event_type="TEST_EVENT_1",
        payload={"step": 1},
    )
    assert e1.prev_event_hash == AuditEvent.GENESIS_HASH
    assert len(e1.event_hash) == 64

    e2 = await AuditEvent.create_event(
        session=db_session,
        merchant_id=merchant.id,
        actor_type="SYSTEM",
        event_type="TEST_EVENT_2",
        payload={"step": 2},
    )
    assert e2.prev_event_hash == e1.event_hash
    assert len(e2.event_hash) == 64
    assert e2.event_hash != e1.event_hash


@pytest.mark.asyncio
async def test_policy_min_margin_percentage_enforcement() -> None:
    """Verifies that evaluate_floor_price enforces cost-plus-min-margin floor."""
    # Cost = 4,000, Floor = 4,000, Base = 5,000. With 20% min margin, effective floor is 4,800.
    item = QuoteItemProposal(
        sku="TEST-SKU",
        quantity=1,
        unit_base_price_paise=500_000,
        unit_floor_price_paise=400_000,
        proposed_unit_price_paise=450_000,  # Above floor (400k) but below cost+margin (480k)
        unit_cost_price_paise=400_000,
    )
    context = PolicyContext(
        min_margin_percentage=20.0,
    )
    proposal = QuoteProposal(
        items=[item],
        subtotal_paise=500_000,
        discount_paise=50_000,
        shipping_paise=0,
        total_paise=450_000,
    )
    res = DeterministicPolicyEngine.evaluate_quote(proposal, context)
    assert res.verdict == PolicyVerdict.DENY
    assert res.rule_code == "POLICY_VIOLATION_BELOW_MIN_MARGIN"


@pytest.mark.asyncio
async def test_state_machines_reject_protected_fields(db_session: AsyncSession) -> None:
    """Verifies that state machines reject modification of protected fields in updates."""
    merchant = Merchant(
        name="SM Test Merchant",
        slug=f"sm-merchant-{uuid.uuid4().hex[:8]}",
        currency="INR",
        rzp_key_id="rzp_test_123",
    )
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="agent_01",
        auth_token_hash="hash123",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    # 1. AgentRun
    run = AgentRun(session_id=session.id, status="PENDING")
    db_session.add(run)
    await db_session.flush()

    with pytest.raises(ValueError, match="protected"):
        await AgentRunStateMachine.transition(
            session=db_session,
            run=run,
            target_state="RUNNING",
            additional_updates={"status": "FORGED_STATUS"},
        )

    # 2. BuyerIntent
    intent = BuyerIntent(
        session_id=session.id,
        raw_query="hello",
        extracted_intent="browse",
        validation_status="PENDING",
    )
    db_session.add(intent)
    await db_session.flush()

    with pytest.raises(ValueError, match="protected"):
        await BuyerIntentStateMachine.transition(
            session=db_session,
            intent=intent,
            target_state="VALIDATED",
            additional_updates={"session_id": uuid.uuid4()},
        )


@pytest.mark.asyncio
async def test_escalate_approval_zero_quote_mutation(db_session: AsyncSession) -> None:
    """Regression test: ESCALATE_APPROVAL returns PENDING_APPROVAL with ZERO quote mutations."""
    merchant = Merchant(
        name="HITL Merchant",
        slug=f"hitl-merchant-{uuid.uuid4().hex[:8]}",
        currency="INR",
        rzp_key_id="rzp_test_123",
    )
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="agent_hitl",
        auth_token_hash="hash_hitl",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    product = Product(
        merchant_id=merchant.id,
        title="Negotiable Widget",
        sku="WIDGET-001",
        category="General",
        base_price_paise=100_000,
        floor_price_paise=80_000,
        is_negotiable=True,
    )
    db_session.add(product)
    await db_session.flush()

    variant = ProductVariant(product_id=product.id, title="Standard", sku="WIDGET-001-STD")
    db_session.add(variant)
    await db_session.flush()

    quote = PriceQuote(
        merchant_id=merchant.id,
        session_id=session.id,
        status="PROPOSED",
        subtotal_paise=100_000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=100_000,
        idempotency_key=f"idem_{uuid.uuid4().hex}",
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
    )
    db_session.add(quote)
    await db_session.flush()

    q_item = QuoteItem(
        quote_id=quote.id,
        variant_id=variant.id,
        quantity=1,
        unit_price_paise=100_000,
        total_price_paise=100_000,
    )
    db_session.add(q_item)
    await db_session.flush()

    # Initial state snapshot
    initial_version = quote.version
    initial_status = quote.status
    initial_total = quote.total_paise
    initial_discount = quote.discount_paise

    tool = NegotiateQuoteTool()
    # autonomy_level = 2 (HITL: requires merchant escalation for discounts)
    context = GatewayContext(
        merchant_id=merchant.id,
        session_id=session.id,
        capabilities={"buyer:quote", "buyer:negotiate"},
        autonomy_level=2,
    )

    result = await tool.execute(
        session=db_session,
        params=NegotiateQuoteParams(
            quote_id=quote.id,
            proposed_total_paise=90_000,
            rationale="Bulk inquiry discount requested",
        ),
        context=context,
    )

    # Verify structured PENDING_APPROVAL result
    assert result["status"] == "PENDING_APPROVAL"
    assert "Counter-offer requires merchant approval" in result["message"]

    # Re-query quote from database to prove ZERO mutation
    stmt = select(PriceQuote).where(PriceQuote.id == quote.id)
    refreshed_quote = (await db_session.execute(stmt)).scalar_one()

    assert refreshed_quote.status == initial_status
    assert refreshed_quote.status == "PROPOSED"
    assert refreshed_quote.version == initial_version
    assert refreshed_quote.total_paise == initial_total
    assert refreshed_quote.total_paise == 100_000
    assert refreshed_quote.discount_paise == initial_discount
    assert refreshed_quote.discount_paise == 0


@pytest.mark.asyncio
async def test_denied_negotiation_zero_quote_mutation(db_session: AsyncSession) -> None:
    """Regression test: DENY verdict returns REJECTED with ZERO quote mutations."""
    merchant = Merchant(
        name="Strict Merchant",
        slug=f"strict-merchant-{uuid.uuid4().hex[:8]}",
        currency="INR",
        rzp_key_id="rzp_test_123",
    )
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="agent_strict",
        auth_token_hash="hash_strict",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    product = Product(
        merchant_id=merchant.id,
        title="Fixed Item",
        sku="FIXED-001",
        category="General",
        base_price_paise=100_000,
        floor_price_paise=90_000,
        is_negotiable=False,  # Not negotiable
    )
    db_session.add(product)
    await db_session.flush()

    variant = ProductVariant(product_id=product.id, title="Default", sku="FIXED-001-DEF")
    db_session.add(variant)
    await db_session.flush()

    quote = PriceQuote(
        merchant_id=merchant.id,
        session_id=session.id,
        status="PROPOSED",
        subtotal_paise=100_000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=100_000,
        idempotency_key=f"idem_{uuid.uuid4().hex}",
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
    )
    db_session.add(quote)
    await db_session.flush()

    q_item = QuoteItem(
        quote_id=quote.id,
        variant_id=variant.id,
        quantity=1,
        unit_price_paise=100_000,
        total_price_paise=100_000,
    )
    db_session.add(q_item)
    await db_session.flush()

    tool = NegotiateQuoteTool()
    context = GatewayContext(
        merchant_id=merchant.id,
        session_id=session.id,
        capabilities={"buyer:quote", "buyer:negotiate"},
        autonomy_level=1,
    )

    result = await tool.execute(
        session=db_session,
        params=NegotiateQuoteParams(
            quote_id=quote.id,
            proposed_total_paise=50_000,
        ),
        context=context,
    )

    assert result["status"] == "REJECTED"
    assert quote.status == "PROPOSED"
    assert quote.total_paise == 100_000
    assert quote.discount_paise == 0


@pytest.mark.asyncio
async def test_concurrent_identical_webhook_delivery_atomic_deduplication(
    test_engine: AsyncEngine,
    db_session: AsyncSession,
) -> None:
    """Regression test: Concurrent webhooks execute atomically without 500s or duplicates."""
    from collections.abc import AsyncGenerator

    from httpx import ASGITransport

    from agent_ready_merchant.config import get_settings
    from agent_ready_merchant.db.session import get_db_session
    from agent_ready_merchant.main import create_app

    merchant = Merchant(
        name="Concurrent Store",
        slug=f"concurrent-store-{uuid.uuid4().hex[:8]}",
        currency="INR",
        rzp_key_id="rzp_test_concurrent",
    )
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="agent_conc",
        auth_token_hash="hash_conc",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    quote = PriceQuote(
        merchant_id=merchant.id,
        session_id=session.id,
        status="ACCEPTED",
        subtotal_paise=250_000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=250_000,
        idempotency_key=f"idem_{uuid.uuid4().hex}",
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
    )
    db_session.add(quote)
    await db_session.flush()

    rzp_order_id = f"order_conc_{uuid.uuid4().hex[:12]}"
    rzp_payment_id = f"pay_conc_{uuid.uuid4().hex[:12]}"

    order = Order(
        quote_id=quote.id,
        merchant_id=merchant.id,
        status="PENDING_PAYMENT",
        amount_paise=250_000,
        currency="INR",
        buyer_email="concurrency@test.com",
        shipping_address={"line1": "Street", "city": "Bangalore", "postal_code": "560001"},
        rzp_order_id=rzp_order_id,
    )
    db_session.add(order)
    await db_session.flush()
    await db_session.commit()

    secret = get_settings().RAZORPAY_WEBHOOK_SECRET.get_secret_value()
    webhook_payload = {
        "entity": "event",
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": rzp_payment_id,
                    "order_id": rzp_order_id,
                    "amount": 250_000,
                    "status": "captured",
                    "method": "upi",
                }
            },
            "order": {
                "entity": {
                    "id": rzp_order_id,
                    "amount": 250_000,
                    "status": "paid",
                }
            },
        },
    }
    raw_body = json.dumps(webhook_payload).encode("utf-8")
    sig = _sign(raw_body, secret)

    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as s:
            try:
                yield s
                await s.commit()
            except Exception:
                await s.rollback()
                raise

    app = create_app()
    app.dependency_overrides[get_db_session] = override_get_db_session
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as concurrent_client:
        # Initial delivery succeeds and processes payment
        initial_resp = await concurrent_client.post(
            "/api/v1/payments/webhook",
            content=raw_body,
            headers={"X-Razorpay-Signature": sig, "Content-Type": "application/json"},
        )
        assert initial_resp.status_code == 200
        assert initial_resp.json()["status"] == "PROCESSED"

        # Concurrent duplicate deliveries must all be safely deduplicated
        tasks = [
            concurrent_client.post(
                "/api/v1/payments/webhook",
                content=raw_body,
                headers={"X-Razorpay-Signature": sig, "Content-Type": "application/json"},
            )
            for _ in range(5)
        ]
        responses = await asyncio.gather(*tasks)

    # All concurrent duplicate requests must return HTTP 200 OK (never HTTP 500)
    for resp in responses:
        assert resp.status_code == 200
        assert resp.json()["status"] == "DUPLICATE_IGNORED"

    # Reset transaction snapshot to see data committed by webhook handlers
    await db_session.rollback()

    # Assert DB invariants: exactly 1 payment_attempt and 1 transaction_record
    pay_stmt = select(PaymentAttempt).where(PaymentAttempt.order_id == order.id)
    payment_attempts = (await db_session.execute(pay_stmt)).scalars().all()
    assert len(payment_attempts) == 1
    assert payment_attempts[0].rzp_payment_id == rzp_payment_id
    assert payment_attempts[0].status == "CAPTURED"

    tx_stmt = select(TransactionRecord).where(
        TransactionRecord.payment_attempt_id == payment_attempts[0].id
    )
    tx_records = (await db_session.execute(tx_stmt)).scalars().all()
    assert len(tx_records) == 1
    assert tx_records[0].entry_type == "CREDIT"
    assert tx_records[0].amount_paise == 250_000

    await db_session.refresh(order)
    assert order.status == "PAID"


@pytest.mark.asyncio
async def test_create_order_rejects_expired_quote(db_session: AsyncSession) -> None:
    """Verifies that PaymentService rejects expired quotes before calling Razorpay."""
    merchant = Merchant(
        name="Expiry Test Merchant",
        slug=f"expiry-merchant-{uuid.uuid4().hex[:8]}",
        currency="INR",
        rzp_key_id="rzp_test_123",
    )
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="agent_02",
        auth_token_hash="hash123",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    # Expired quote (10 minutes in the past)
    quote = PriceQuote(
        merchant_id=merchant.id,
        session_id=session.id,
        status="ACCEPTED",
        subtotal_paise=100_000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=100_000,
        idempotency_key=f"idem_{uuid.uuid4().hex}",
        expires_at=datetime.now(UTC) - timedelta(minutes=10),
    )
    db_session.add(quote)
    await db_session.flush()

    rzp_client = RazorpayClient(key_id="k", key_secret=SecretStr("s"))
    with pytest.raises(ValueError, match="expired"):
        await PaymentService.create_order_from_accepted_quote(
            session=db_session,
            quote_id=quote.id,
            buyer_email="buyer@test.com",
            shipping_address={"country": "IN", "city": "Bangalore", "postal_code": "560001"},
            rzp_client=rzp_client,
        )


@pytest.mark.asyncio
async def test_create_order_tool_enforces_quote_session_ownership(
    db_session: AsyncSession,
) -> None:
    """Verifies that CreateOrderTool rejects quotes from different sessions."""
    merchant = Merchant(
        name="Ownership Test Merchant",
        slug=f"ownership-merchant-{uuid.uuid4().hex[:8]}",
        currency="INR",
        rzp_key_id="rzp_test_123",
    )
    db_session.add(merchant)
    await db_session.flush()

    session1 = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="agent_03",
        auth_token_hash="hash123",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    session2 = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="agent_04",
        auth_token_hash="hash123",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    db_session.add_all([session1, session2])
    await db_session.flush()

    quote = PriceQuote(
        merchant_id=merchant.id,
        session_id=session1.id,  # Belongs to session 1
        status="ACCEPTED",
        subtotal_paise=100_000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=100_000,
        idempotency_key=f"idem_{uuid.uuid4().hex}",
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
    )
    db_session.add(quote)
    await db_session.flush()

    tool = CreateOrderTool()
    context2 = GatewayContext(
        merchant_id=merchant.id,
        session_id=session2.id,  # Caller is session 2
        capabilities={"buyer:checkout"},
    )
    res = await tool.execute(
        session=db_session,
        params=CreateOrderParams(
            quote_id=quote.id,
            buyer_email="buyer@test.com",
            shipping_address=ShippingAddressParam(
                full_name="Buyer Name",
                address_line1="123 Street",
                city="Bangalore",
                postal_code="560001",
            ),
        ),
        context=context2,
    )
    assert "error" in res
    assert res["error"]["code"] == "QUOTE_NOT_FOUND"
