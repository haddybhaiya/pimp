"""Tests for security hardening, audit hash chains, margin enforcement, and inventory reservation."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.integrations.razorpay.client import RazorpayClient
from agent_ready_merchant.models.agent_run import AgentRun
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.intent import BuyerIntent
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.quote import PriceQuote
from agent_ready_merchant.models.session import BuyerAgentSession
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
from agent_ready_merchant.tools.handlers import CreateOrderTool
from agent_ready_merchant.tools.models import CreateOrderParams, ShippingAddressParam


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
