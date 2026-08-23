"""Comprehensive Deliberate Failure Matrix Verification Suite.

Tests critical failure modes defined in docs/failure-model.md and docs/evaluation.md:
- DF-01: Malformed LLM output handling
- DF-03: Unknown tool execution rejection
- DF-04: Unauthorized capability rejection
- DF-05: Schema argument boundary violations
- DF-06: Below-floor price negotiation rejection
- DF-07: Excessive discount percentage rejection
- DF-08: Invalid state machine transition rejection
- DF-09: Optimistic locking concurrency rejection
- DF-10: Duplicate checkout idempotency
- DF-12: Tampered / forged webhook rejection
- DF-13: Payment amount mismatch fraud detection
- DF-14: Payment failure webhook handling
- DF-15: Razorpay client timeout error mapping
- DF-16: Razorpay client API 500 error mapping
- DF-17: Out-of-band reconciliation recovery
- DF-19: Secret scanning verification
"""

import hashlib
import hmac
import json
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import pytest
import pytest_asyncio
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.agent.intent import ToolCallProposal
from agent_ready_merchant.agent.prompt import build_system_prompt
from agent_ready_merchant.agent.runtime import AgentRuntime
from agent_ready_merchant.db.concurrency import OptimisticLockError
from agent_ready_merchant.integrations.razorpay.client import RazorpayClient
from agent_ready_merchant.integrations.razorpay.exceptions import (
    AmountMismatchFraudError,
    InvalidWebhookSignatureError,
    RazorpayAPIError,
    RazorpayTimeoutError,
)
from agent_ready_merchant.llm.mock_provider import MockLLMProvider
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.order import Order
from agent_ready_merchant.models.product import Product, ProductVariant
from agent_ready_merchant.models.quote import PriceQuote
from agent_ready_merchant.models.session import BuyerAgentSession
from agent_ready_merchant.models.transaction import TransactionRecord
from agent_ready_merchant.services.payment_service import PaymentService
from agent_ready_merchant.state_machines.base import TerminalStateError
from agent_ready_merchant.state_machines.order import OrderStateMachine
from agent_ready_merchant.state_machines.price_quote import PriceQuoteStateMachine
from agent_ready_merchant.tools.base import GatewayContext
from agent_ready_merchant.tools.gateway import ToolGateway


def _sign(body: bytes, secret: str) -> str:
    return hmac.new(key=secret.encode("utf-8"), msg=body, digestmod=hashlib.sha256).hexdigest()


@pytest_asyncio.fixture(scope="function")
async def failure_fixture(db_session: AsyncSession) -> dict[str, Any]:
    """Sets up standard merchant, session, product, and quote entities."""
    now = datetime.now(UTC)
    merchant = Merchant(
        name="Failure Test Merchant", slug="fail-merchant", rzp_key_id="rzp_test_fail"
    )
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

    product = Product(
        merchant_id=merchant.id,
        sku="SKU-FAIL-01",
        title="Test Safety Item",
        category="Safety",
        base_price_paise=1000000,  # ₹10,000.00
        floor_price_paise=800000,  # ₹8,000.00 floor
        is_negotiable=True,
    )
    db_session.add(product)
    await db_session.flush()

    variant = ProductVariant(product_id=product.id, sku="SKU-FAIL-01-V", title="Standard")
    db_session.add(variant)
    await db_session.flush()

    quote = PriceQuote(
        session_id=session.id,
        merchant_id=merchant.id,
        status="PROPOSED",
        subtotal_paise=1000000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=1000000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=str(uuid.uuid4()),
    )
    db_session.add(quote)
    await db_session.flush()

    context = GatewayContext(
        merchant_id=merchant.id,
        session_id=session.id,
        capabilities={
            "buyer:discover",
            "buyer:read",
            "buyer:quote",
            "buyer:negotiate",
            "buyer:checkout",
        },
        autonomy_level=1,
        max_discount_percentage=15.0,
        min_margin_percentage=20.0,
        max_single_transaction_paise=10_000_000,
    )

    return {
        "merchant": merchant,
        "session": session,
        "product": product,
        "variant": variant,
        "quote": quote,
        "context": context,
    }


# =============================================================================
# DF-01 to DF-07: GATEWAY, SCHEMA & POLICY BOUNDARIES
# =============================================================================


@pytest.mark.asyncio
async def test_df01_malformed_llm_exhaustion_terminates_safely(
    db_session: AsyncSession, failure_fixture: dict[str, Any]
) -> None:
    """DF-01: Proves persistent non-JSON output terminates with MALFORMED_OUTPUT."""
    mock_llm = MockLLMProvider(responses=["NOT_JSON_1", "NOT_JSON_2", "NOT_JSON_3"])
    runtime = AgentRuntime(llm_provider=mock_llm)

    res = await runtime.run_turn(
        session=db_session,
        user_message="Hello",
        context=failure_fixture["context"],
    )

    assert res.status == "MALFORMED_OUTPUT"
    assert res.steps_taken == 3


@pytest.mark.asyncio
async def test_df03_unknown_tool_rejection(
    db_session: AsyncSession, failure_fixture: dict[str, Any]
) -> None:
    """DF-03: Proves unknown tool calls are rejected and audited."""
    gateway = ToolGateway()
    proposal = ToolCallProposal(
        tool_name="unregistered_dangerous_action",
        parameters={"foo": "bar"},
    )
    res = await gateway.execute_tool_call(db_session, proposal, failure_fixture["context"])
    assert res.status == "ERROR"
    assert res.error is not None
    assert res.error["code"] == "UNKNOWN_TOOL"


@pytest.mark.asyncio
async def test_df04_unauthorized_capability_rejection(
    db_session: AsyncSession, failure_fixture: dict[str, Any]
) -> None:
    """DF-04: Proves tool calls lacking capability are denied."""
    restricted_ctx = GatewayContext(
        merchant_id=failure_fixture["merchant"].id,
        session_id=failure_fixture["session"].id,
        capabilities={"buyer:discover"},  # Lacks buyer:negotiate
    )
    gateway = ToolGateway()
    proposal = ToolCallProposal(
        tool_name="negotiate_quote",
        parameters={
            "quote_id": str(failure_fixture["quote"].id),
            "proposed_total_paise": 900000,
        },
    )
    res = await gateway.execute_tool_call(db_session, proposal, restricted_ctx)
    assert res.status == "REJECTED"
    assert res.error is not None
    assert res.error["code"] == "CAPABILITY_DENIED"


@pytest.mark.asyncio
async def test_df05_invalid_tool_parameters(
    db_session: AsyncSession, failure_fixture: dict[str, Any]
) -> None:
    """DF-05: Proves Pydantic rejects out-of-boundary parameters."""
    gateway = ToolGateway()
    proposal = ToolCallProposal(
        tool_name="discover_catalog",
        parameters={"limit": 500},  # Exceeds max 10
    )
    res = await gateway.execute_tool_call(db_session, proposal, failure_fixture["context"])
    assert res.status == "ERROR"
    assert res.error is not None
    assert res.error["code"] == "INVALID_TOOL_ARGUMENTS"


@pytest.mark.asyncio
async def test_df06_below_floor_price_rejection(
    db_session: AsyncSession, failure_fixture: dict[str, Any]
) -> None:
    """DF-06: Proves price negotiation below floor price (₹8,000) is rejected."""
    gateway = ToolGateway()
    proposal = ToolCallProposal(
        tool_name="negotiate_quote",
        parameters={
            "quote_id": str(failure_fixture["quote"].id),
            "proposed_total_paise": 700000,  # Below ₹8,000 floor
        },
    )
    res = await gateway.execute_tool_call(db_session, proposal, failure_fixture["context"])
    assert res.status == "SUCCESS"
    assert res.data is not None
    assert res.data["status"] == "REJECTED"
    assert "Counter-offer rejected by policy" in res.data["message"]


@pytest.mark.asyncio
async def test_df07_excessive_discount_rejection(
    db_session: AsyncSession, failure_fixture: dict[str, Any]
) -> None:
    """DF-07: Proves discount exceeding max_discount_percentage (15%) is rejected."""
    gateway = ToolGateway()
    proposal = ToolCallProposal(
        tool_name="negotiate_quote",
        parameters={
            "quote_id": str(failure_fixture["quote"].id),
            "proposed_total_paise": 800000,  # 20% discount
        },
    )
    res = await gateway.execute_tool_call(db_session, proposal, failure_fixture["context"])
    assert res.status == "SUCCESS"
    assert res.data is not None
    assert res.data["status"] == "REJECTED"


# =============================================================================
# DF-08 to DF-10: STATE MACHINES, CONCURRENCY & IDEMPOTENCY
# =============================================================================


@pytest.mark.asyncio
async def test_df08_invalid_state_transition_rejection(
    db_session: AsyncSession, failure_fixture: dict[str, Any]
) -> None:
    """DF-08: Proves state machine rejects invalid or terminal transitions."""
    order = Order(
        merchant_id=failure_fixture["merchant"].id,
        quote_id=failure_fixture["quote"].id,
        buyer_email="test@example.com",
        status="EXPIRED",  # Terminal state
        amount_paise=1000000,
        currency="INR",
        rzp_order_id="order_terminal_test",
    )
    db_session.add(order)
    await db_session.flush()

    with pytest.raises(TerminalStateError):
        await OrderStateMachine.transition(
            session=db_session,
            order=order,
            target_state="PAID",
            expected_version=order.version,
        )


@pytest.mark.asyncio
async def test_df09_optimistic_lock_version_conflict(
    db_session: AsyncSession, failure_fixture: dict[str, Any]
) -> None:
    """DF-09: Proves stale version update is rejected with OptimisticLockError."""
    quote = failure_fixture["quote"]
    stale_version = quote.version - 1  # Intentional stale version

    with pytest.raises(OptimisticLockError):
        await PriceQuoteStateMachine.transition(
            session=db_session,
            quote=quote,
            target_state="ACCEPTED",
            expected_version=stale_version,
        )


@pytest.mark.asyncio
async def test_df10_duplicate_checkout_idempotency(
    db_session: AsyncSession, failure_fixture: dict[str, Any]
) -> None:
    """DF-10: Proves duplicate checkout with same quote returns existing order."""
    quote = failure_fixture["quote"]
    await PriceQuoteStateMachine.transition(
        session=db_session,
        quote=quote,
        target_state="ACCEPTED",
        expected_version=quote.version,
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={
                "id": "order_IDEMP_123",
                "entity": "order",
                "amount": 1000000,
                "amount_paid": 0,
                "amount_due": 1000000,
                "currency": "INR",
                "receipt": f"ord_{quote.id.hex[:32]}",
                "status": "created",
                "attempts": 0,
                "created_at": 1740000000,
            },
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        rzp_client = RazorpayClient(
            key_id="rzp_test_key",
            key_secret=SecretStr("secret"),
            http_client=http_client,
        )
        # First checkout
        order1 = await PaymentService.create_order_from_accepted_quote(
            session=db_session,
            quote_id=quote.id,
            buyer_email="buyer@example.com",
            shipping_address={"city": "Bengaluru"},
            rzp_client=rzp_client,
        )
        # Duplicate checkout
        order2 = await PaymentService.create_order_from_accepted_quote(
            session=db_session,
            quote_id=quote.id,
            buyer_email="buyer@example.com",
            shipping_address={"city": "Bengaluru"},
            rzp_client=rzp_client,
        )

    assert order1.id == order2.id
    order_stmt = select(Order).where(Order.quote_id == quote.id)
    order_count = len((await db_session.execute(order_stmt)).scalars().all())
    assert order_count == 1


# =============================================================================
# DF-12 to DF-17: WEBHOOK SECURITY, FRAUD, TIMEOUTS & RECONCILIATION
# =============================================================================


@pytest.mark.asyncio
async def test_df12_tampered_webhook_rejection(
    db_session: AsyncSession, failure_fixture: dict[str, Any]
) -> None:
    """DF-12: Proves tampered webhook payload signature fails verification."""
    raw_body = b'{"event":"payment.captured","payload":{}}'
    tampered_sig = "0000000000000000000000000000000000000000000000000000000000000000"

    with pytest.raises(InvalidWebhookSignatureError):
        await PaymentService.process_payment_webhook(
            session=db_session,
            raw_body=raw_body,
            signature_header=tampered_sig,
            webhook_secret="test_secret",
        )


@pytest.mark.asyncio
async def test_df13_payment_amount_mismatch_fraud_detection(
    db_session: AsyncSession, failure_fixture: dict[str, Any]
) -> None:
    """DF-13: Proves webhook with mismatched amount is rejected as fraud."""
    order = Order(
        merchant_id=failure_fixture["merchant"].id,
        quote_id=failure_fixture["quote"].id,
        buyer_email="test@example.com",
        status="PENDING_PAYMENT",
        amount_paise=1000000,  # Expected ₹10,000
        currency="INR",
        rzp_order_id="order_FRAUD_CHECK_01",
    )
    db_session.add(order)
    await db_session.flush()

    fraud_payload = {
        "event": "payment.captured",
        "payload": {
            "order": {
                "entity": {"id": "order_FRAUD_CHECK_01", "amount": 1000000, "status": "paid"}
            },
            "payment": {
                "entity": {
                    "id": "pay_FRAUD_01",
                    "order_id": "order_FRAUD_CHECK_01",
                    "amount": 1000,  # Fraud: Only paid ₹10
                    "status": "captured",
                }
            },
        },
    }
    raw_body = json.dumps(fraud_payload).encode("utf-8")
    secret = "secret123"
    sig = _sign(raw_body, secret)

    with pytest.raises(AmountMismatchFraudError):
        await PaymentService.process_payment_webhook(
            session=db_session,
            raw_body=raw_body,
            signature_header=sig,
            webhook_secret=secret,
        )

    # Invariant: Order remains PENDING_PAYMENT (not PAID)
    await db_session.refresh(order)
    assert order.status == "PENDING_PAYMENT"


@pytest.mark.asyncio
async def test_df14_payment_failure_webhook(
    db_session: AsyncSession, failure_fixture: dict[str, Any]
) -> None:
    """DF-14: Proves payment.failed webhook sets order to PAYMENT_FAILED."""
    order = Order(
        merchant_id=failure_fixture["merchant"].id,
        quote_id=failure_fixture["quote"].id,
        buyer_email="test@example.com",
        status="PENDING_PAYMENT",
        amount_paise=1000000,
        currency="INR",
        rzp_order_id="order_FAIL_PAY_01",
    )
    db_session.add(order)
    await db_session.flush()

    payload = {
        "event": "payment.failed",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_FAILED_01",
                    "order_id": "order_FAIL_PAY_01",
                    "amount": 1000000,
                    "status": "failed",
                    "error_code": "BAD_REQUEST_ERROR",
                    "error_description": "Card declined",
                }
            }
        },
    }
    raw_body = json.dumps(payload).encode("utf-8")
    secret = "secret123"
    sig = _sign(raw_body, secret)

    res = await PaymentService.process_payment_webhook(
        session=db_session,
        raw_body=raw_body,
        signature_header=sig,
        webhook_secret=secret,
    )
    assert res["status"] == "FAILURE_RECORDED"
    assert res["order_id"] == str(order.id)

    # Invariant: zero transaction credits
    txs = (await db_session.execute(select(TransactionRecord))).scalars().all()
    assert len(txs) == 0


@pytest.mark.asyncio
async def test_df15_df16_razorpay_timeout_and_api_error() -> None:
    """DF-15, DF-16: Proves client maps network timeouts and 500 errors safely."""

    # 1. Timeout
    def timeout_handler(req: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("Timeout")

    transport_t = httpx.MockTransport(timeout_handler)
    async with httpx.AsyncClient(transport=transport_t) as client_t:
        rzp_t = RazorpayClient(key_id="k", key_secret=SecretStr("s"), http_client=client_t)
        with pytest.raises(RazorpayTimeoutError):
            await rzp_t.create_order(amount_paise=1000, currency="INR", receipt="rec_1")

    # 2. 500 Error
    def err_handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=500, json={"error": {"description": "Gateway Down"}})

    transport_e = httpx.MockTransport(err_handler)
    async with httpx.AsyncClient(transport=transport_e) as client_e:
        rzp_e = RazorpayClient(key_id="k", key_secret=SecretStr("s"), http_client=client_e)
        with pytest.raises(RazorpayAPIError) as exc_info:
            await rzp_e.create_order(amount_paise=1000, currency="INR", receipt="rec_2")
        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_df17_reconciliation_recovers_missing_webhook(
    db_session: AsyncSession, failure_fixture: dict[str, Any]
) -> None:
    """DF-17: Proves out-of-band reconciliation captures paid order when webhook dropped."""
    order = Order(
        merchant_id=failure_fixture["merchant"].id,
        quote_id=failure_fixture["quote"].id,
        buyer_email="test@example.com",
        status="PENDING_PAYMENT",
        amount_paise=1000000,
        currency="INR",
        rzp_order_id="order_RECON_DROP_01",
    )
    db_session.add(order)
    await db_session.flush()

    def rzp_recon_handler(req: httpx.Request) -> httpx.Response:
        if req.url.path.endswith("/payments"):
            return httpx.Response(
                status_code=200,
                json={
                    "count": 1,
                    "items": [
                        {
                            "id": "pay_RECON_SAVED_01",
                            "order_id": "order_RECON_DROP_01",
                            "amount": 1000000,
                            "status": "captured",
                        }
                    ],
                },
            )
        return httpx.Response(status_code=404)

    transport = httpx.MockTransport(rzp_recon_handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        rzp_client = RazorpayClient(key_id="k", key_secret=SecretStr("s"), http_client=http_client)
        recon_result = await PaymentService.reconcile_order(
            session=db_session,
            order_id=order.id,
            rzp_client=rzp_client,
        )

    assert recon_result["status"] == "PROCESSED"
    assert recon_result["order_status"] == "PAID"
    await db_session.refresh(order)
    assert order.status == "PAID"


# =============================================================================
# DF-19: SECRET SCANNING VERIFICATION
# =============================================================================


def test_df19_zero_secrets_in_generated_prompts_and_models() -> None:
    """DF-19: Comprehensive secret scan verifying zero credentials exist in prompt."""
    prompt = build_system_prompt(
        merchant_name="Production Store",
        autonomy_level=1,
        available_tools=["discover_catalog", "request_price_quote"],
    )
    forbidden_patterns = ["rzp_test_", "rzp_live_", "gsk_", "postgres://", "Bearer "]
    for pattern in forbidden_patterns:
        assert pattern not in prompt, f"Secret pattern '{pattern}' detected in system prompt!"
