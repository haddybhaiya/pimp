"""Tests for authoritative state machines and terminal state protection."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.db.concurrency import OptimisticLockError
from agent_ready_merchant.models.agent_run import AgentRun
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.intent import BuyerIntent
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.order import Order
from agent_ready_merchant.models.payment import PaymentAttempt
from agent_ready_merchant.models.quote import PriceQuote
from agent_ready_merchant.models.session import BuyerAgentSession
from agent_ready_merchant.models.transaction import TransactionRecord
from agent_ready_merchant.state_machines.agent_run import AgentRunStateMachine
from agent_ready_merchant.state_machines.base import (
    InvalidStateTransitionError,
    TerminalStateError,
)
from agent_ready_merchant.state_machines.buyer_intent import BuyerIntentStateMachine
from agent_ready_merchant.state_machines.order import OrderStateMachine
from agent_ready_merchant.state_machines.payment_attempt import PaymentAttemptStateMachine
from agent_ready_merchant.state_machines.price_quote import PriceQuoteStateMachine
from agent_ready_merchant.state_machines.transaction import TransactionStateMachine


@pytest.mark.asyncio
async def test_price_quote_valid_lifecycle(db_session: AsyncSession) -> None:
    """Verifies valid PriceQuote transition lifecycle."""
    now = datetime.now(UTC)
    merchant = Merchant(name="SM Store", slug="sm-store", rzp_key_id="rzp_test_sm")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="agent_quote_test",
        auth_token_hash="hash_q",
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    quote = PriceQuote(
        session_id=session.id,
        merchant_id=merchant.id,
        status="DRAFT",
        subtotal_paise=500000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=500000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=str(uuid.uuid4()),
    )
    db_session.add(quote)
    await db_session.flush()

    # 1. DRAFT -> PROPOSED
    res1 = await PriceQuoteStateMachine.transition(
        session=db_session,
        quote=quote,
        target_state="PROPOSED",
        expected_version=1,
    )
    assert res1.to_state == "PROPOSED"
    assert quote.version == 2

    # 2. PROPOSED -> NEGOTIATING
    res2 = await PriceQuoteStateMachine.transition(
        session=db_session,
        quote=quote,
        target_state="NEGOTIATING",
        expected_version=2,
    )
    assert res2.to_state == "NEGOTIATING"
    assert quote.version == 3

    # 3. NEGOTIATING -> PROPOSED (counter accepted)
    res3 = await PriceQuoteStateMachine.transition(
        session=db_session,
        quote=quote,
        target_state="PROPOSED",
        expected_version=3,
    )
    assert res3.to_state == "PROPOSED"
    assert quote.version == 4

    # 4. PROPOSED -> ACCEPTED (Terminal)
    res4 = await PriceQuoteStateMachine.transition(
        session=db_session,
        quote=quote,
        target_state="ACCEPTED",
        expected_version=4,
    )
    assert res4.to_state == "ACCEPTED"
    assert quote.version == 5

    # Verify audit events logged in DB
    audit_stmt = select(AuditEvent).where(AuditEvent.session_id == session.id)
    audit_res = await db_session.execute(audit_stmt)
    events = audit_res.scalars().all()
    assert len(events) == 4


@pytest.mark.asyncio
async def test_price_quote_terminal_state_rejection(db_session: AsyncSession) -> None:
    """Verifies that an ACCEPTED, EXPIRED, or REJECTED quote cannot transition further."""
    now = datetime.now(UTC)
    merchant = Merchant(name="StoreTerm", slug="store-term", rzp_key_id="rzp_test_term")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="agent_term",
        auth_token_hash="hash_term",
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    quote = PriceQuote(
        session_id=session.id,
        merchant_id=merchant.id,
        status="EXPIRED",  # Terminal state
        subtotal_paise=100000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=100000,
        expires_at=now - timedelta(minutes=1),
        idempotency_key=str(uuid.uuid4()),
    )
    db_session.add(quote)
    await db_session.flush()

    # Attempting to revive expired quote must raise TerminalStateError
    with pytest.raises(TerminalStateError):
        await PriceQuoteStateMachine.transition(
            session=db_session,
            quote=quote,
            target_state="PROPOSED",
            expected_version=1,
        )


@pytest.mark.asyncio
async def test_price_quote_expiry_guard(db_session: AsyncSession) -> None:
    """Verifies that quote past expires_at cannot transition to ACCEPTED."""
    now = datetime.now(UTC)
    merchant = Merchant(name="StoreExp", slug="store-exp", rzp_key_id="rzp_test_exp")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="agent_exp",
        auth_token_hash="hash_exp",
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    # Quote expires at now - 1 second
    quote = PriceQuote(
        session_id=session.id,
        merchant_id=merchant.id,
        status="PROPOSED",
        subtotal_paise=100000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=100000,
        expires_at=now - timedelta(seconds=1),
        idempotency_key=str(uuid.uuid4()),
    )
    db_session.add(quote)
    await db_session.flush()

    # Transitioning expired quote to ACCEPTED must raise InvalidStateTransitionError
    with pytest.raises(InvalidStateTransitionError) as exc_info:
        await PriceQuoteStateMachine.transition(
            session=db_session,
            quote=quote,
            target_state="ACCEPTED",
            expected_version=1,
            current_time=now,
        )
    assert "expired" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_order_state_machine_transitions(db_session: AsyncSession) -> None:
    """Verifies valid Order transitions progression."""
    now = datetime.now(UTC)
    merchant = Merchant(name="OrderStore", slug="order-store", rzp_key_id="rzp_test_ord")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="agent_ord",
        auth_token_hash="hash_ord",
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
        status="CREATED",
        amount_paise=100000,
        currency="INR",
        buyer_email="buyer@example.com",
    )
    db_session.add(order)
    await db_session.flush()

    # 1. CREATED -> PENDING_PAYMENT
    await OrderStateMachine.transition(db_session, order, "PENDING_PAYMENT", expected_version=1)
    assert order.status == "PENDING_PAYMENT"
    assert order.version == 2

    # 2. PENDING_PAYMENT -> PAYMENT_PROCESSING
    await OrderStateMachine.transition(db_session, order, "PAYMENT_PROCESSING", expected_version=2)
    assert order.status == "PAYMENT_PROCESSING"
    assert order.version == 3

    # 3. PAYMENT_PROCESSING -> PAID
    await OrderStateMachine.transition(db_session, order, "PAID", expected_version=3)
    assert order.status == "PAID"
    assert order.version == 4

    # 4. PAID -> FULFILLMENT_PENDING
    await OrderStateMachine.transition(db_session, order, "FULFILLMENT_PENDING", expected_version=4)
    assert order.status == "FULFILLMENT_PENDING"
    assert order.version == 5

    # 5. FULFILLMENT_PENDING -> COMPLETED (Terminal)
    await OrderStateMachine.transition(db_session, order, "COMPLETED", expected_version=5)
    assert order.status == "COMPLETED"
    assert order.version == 6

    # 6. Cannot transition from terminal COMPLETED state
    with pytest.raises(TerminalStateError):
        await OrderStateMachine.transition(db_session, order, "PAID", expected_version=6)


@pytest.mark.asyncio
async def test_order_stale_concurrency_failure(db_session: AsyncSession) -> None:
    """Verifies that Order transition with wrong version raises OptimisticLockError."""
    now = datetime.now(UTC)
    merchant = Merchant(name="OrderConcur", slug="order-concur", rzp_key_id="rzp_test_oc")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="agent_oc",
        auth_token_hash="hash_oc",
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
        status="CREATED",
        amount_paise=100000,
        currency="INR",
        buyer_email="buyer@example.com",
    )
    db_session.add(order)
    await db_session.flush()

    # Passing stale expected_version=99 must raise OptimisticLockError
    with pytest.raises(OptimisticLockError):
        await OrderStateMachine.transition(
            db_session, order, "PENDING_PAYMENT", expected_version=99
        )


@pytest.mark.asyncio
async def test_payment_attempt_state_machine(db_session: AsyncSession) -> None:
    """Verifies PaymentAttempt valid progression."""
    now = datetime.now(UTC)
    merchant = Merchant(name="PayStore", slug="pay-store", rzp_key_id="rzp_test_pay")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="agent_pay",
        auth_token_hash="hash_p",
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
        buyer_email="buyer@example.com",
    )
    db_session.add(order)
    await db_session.flush()

    payment = PaymentAttempt(
        order_id=order.id,
        rzp_order_id="order_rzp_123",
        status="INITIATED",
        amount_paise=100000,
    )
    db_session.add(payment)
    await db_session.flush()

    # 1. INITIATED -> ORDER_CREATED
    await PaymentAttemptStateMachine.transition(db_session, payment, "ORDER_CREATED")
    assert payment.status == "ORDER_CREATED"

    # 2. ORDER_CREATED -> PAYMENT_PENDING
    await PaymentAttemptStateMachine.transition(db_session, payment, "PAYMENT_PENDING")
    assert payment.status == "PAYMENT_PENDING"

    # 3. PAYMENT_PENDING -> CAPTURED
    await PaymentAttemptStateMachine.transition(db_session, payment, "CAPTURED")
    assert payment.status == "CAPTURED"

    # 4. CAPTURED -> REFUNDED (Terminal)
    await PaymentAttemptStateMachine.transition(db_session, payment, "REFUNDED")
    assert payment.status == "REFUNDED"

    # 5. Cannot transition from terminal REFUNDED
    with pytest.raises(TerminalStateError):
        await PaymentAttemptStateMachine.transition(db_session, payment, "CAPTURED")


@pytest.mark.asyncio
async def test_transaction_state_machine(db_session: AsyncSession) -> None:
    """Verifies TransactionRecord transitions: UNCOMMITTED -> COMMITTED -> REVERSED."""
    now = datetime.now(UTC)
    merchant = Merchant(name="TxStore", slug="tx-store", rzp_key_id="rzp_test_tx")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="agent_tx",
        auth_token_hash="hash_tx",
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
        status="PAID",
        amount_paise=100000,
        currency="INR",
        buyer_email="buyer@example.com",
    )
    db_session.add(order)
    await db_session.flush()

    payment = PaymentAttempt(
        order_id=order.id,
        rzp_order_id="order_rzp_tx",
        status="CAPTURED",
        amount_paise=100000,
    )
    db_session.add(payment)
    await db_session.flush()

    tx = TransactionRecord(
        payment_attempt_id=payment.id,
        merchant_id=merchant.id,
        entry_type="CREDIT",
        amount_paise=100000,
        status="UNCOMMITTED",
        settlement_ref="settle_tx_test_001",
    )
    db_session.add(tx)
    await db_session.flush()

    # 1. UNCOMMITTED -> COMMITTED
    await TransactionStateMachine.transition(db_session, tx, "COMMITTED")
    assert tx.status == "COMMITTED"

    # 2. COMMITTED -> REVERSED (Terminal)
    await TransactionStateMachine.transition(db_session, tx, "REVERSED")
    assert tx.status == "REVERSED"

    # 3. Cannot transition out of REVERSED
    with pytest.raises(TerminalStateError):
        await TransactionStateMachine.transition(db_session, tx, "COMMITTED")


@pytest.mark.asyncio
async def test_agent_run_step_limit_enforcement(db_session: AsyncSession) -> None:
    """Verifies that AgentRun enforces maximum 5 steps and rejects transition if exceeded."""
    now = datetime.now(UTC)
    merchant = Merchant(name="AgentStore", slug="agent-store", rzp_key_id="rzp_test_as")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="agent_step_tester",
        auth_token_hash="hash_step",
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    run = AgentRun(
        session_id=session.id,
        status="PENDING",
        step_count=5,
        total_tokens=1500,
    )
    db_session.add(run)
    await db_session.flush()

    # PENDING -> RUNNING at step 5 is valid
    await AgentRunStateMachine.transition(db_session, run, "RUNNING")
    assert run.status == "RUNNING"

    # If step_count becomes 6, transition to non-terminal state must fail
    run.step_count = 6
    with pytest.raises(InvalidStateTransitionError) as exc_info:
        await AgentRunStateMachine.transition(db_session, run, "AWAITING_TOOL")
    assert "Step limit exceeded" in str(exc_info.value)


@pytest.mark.asyncio
async def test_buyer_intent_validation_lifecycle(db_session: AsyncSession) -> None:
    """Verifies BuyerIntent transition from PENDING to VALIDATED/REJECTED/MALFORMED."""
    now = datetime.now(UTC)
    merchant = Merchant(name="IntentStore", slug="intent-store", rzp_key_id="rzp_test_is")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="agent_intent",
        auth_token_hash="hash_intent",
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    intent = BuyerIntent(
        session_id=session.id,
        raw_query="Looking for shoe size 9 under 4500",
        extracted_intent="SEARCH",
        extracted_entities={"category": "Shoes", "max_price": 4500},
        validation_status="PENDING",
    )
    db_session.add(intent)
    await db_session.flush()

    # PENDING -> VALIDATED (Terminal)
    await BuyerIntentStateMachine.transition(db_session, intent, "VALIDATED")
    assert intent.validation_status == "VALIDATED"

    # Terminal state rejection
    with pytest.raises(TerminalStateError):
        await BuyerIntentStateMachine.transition(db_session, intent, "REJECTED")
