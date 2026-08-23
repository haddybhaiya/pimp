"""End-to-End Golden Path Integration Test for Agent-Ready Merchant.

Executes the complete canonical golden path:
Buyer Request
-> Bounded LLM Reasoning
-> Structured Intent
-> Tool Gateway
-> Policy Engine Validation
-> Price Quote Draft
-> Bounded Negotiation (10% discount within floor)
-> Quote Acceptance
-> Order Creation via Razorpay Client
-> Razorpay Test-Mode Payment Simulation
-> Cryptographic HMAC Webhook Verification
-> Order State Settlement to PAID
-> Append-Only TransactionRecord Ledger Entry
-> Immutable Audit Trail
"""

import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta

import httpx
import pytest
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.agent.runtime import AgentRuntime
from agent_ready_merchant.config import get_settings
from agent_ready_merchant.integrations.razorpay.client import RazorpayClient
from agent_ready_merchant.llm.mock_provider import MockLLMProvider
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.payment import PaymentAttempt
from agent_ready_merchant.models.product import Product, ProductVariant
from agent_ready_merchant.models.quote import PriceQuote
from agent_ready_merchant.models.session import BuyerAgentSession
from agent_ready_merchant.models.transaction import TransactionRecord
from agent_ready_merchant.services.payment_service import PaymentService
from agent_ready_merchant.state_machines.price_quote import PriceQuoteStateMachine
from agent_ready_merchant.tools.base import GatewayContext


def _sign(body: bytes, secret: str) -> str:
    return hmac.new(key=secret.encode("utf-8"), msg=body, digestmod=hashlib.sha256).hexdigest()


@pytest.mark.asyncio
async def test_complete_golden_path_commerce_lifecycle(db_session: AsyncSession) -> None:
    """Executes the full end-to-end golden path from discovery to settlement."""
    now = datetime.now(UTC)
    settings = get_settings()
    webhook_secret = (
        settings.RAZORPAY_WEBHOOK_SECRET.get_secret_value() or "golden_webhook_secret_123"
    )

    # =========================================================================
    # 1. SETUP CATALOG & MERCHANT ENTITIES
    # =========================================================================
    merchant = Merchant(
        name="Apex Athletics",
        slug="apex-athletics",
        rzp_key_id=settings.RAZORPAY_KEY_ID,
    )
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="buyer_agent_alpha",
        auth_token_hash="hash_alpha",
        expires_at=now + timedelta(hours=2),
    )
    db_session.add(session)
    await db_session.flush()

    product = Product(
        merchant_id=merchant.id,
        sku="SKU-APEX-RUNNER",
        title="Apex Velocity Running Shoe",
        category="Footwear",
        base_price_paise=500000,  # ₹5,000.00
        floor_price_paise=400000,  # ₹4,000.00 floor
        is_negotiable=True,
    )
    db_session.add(product)
    await db_session.flush()

    variant = ProductVariant(
        product_id=product.id,
        sku="SKU-APEX-RUNNER-V10",
        title="Size 10 / Midnight Blue",
    )
    db_session.add(variant)
    await db_session.flush()

    gateway_context = GatewayContext(
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

    # =========================================================================
    # 2. TURN 1: DISCOVERY & QUOTE GENERATION
    # =========================================================================
    # Step 1: Model proposes discover_catalog -> gets product
    step1_json = """
    {
        "thought_process": "Buyer wants shoes. Searching footwear catalog.",
        "intent": "DISCOVER_CATALOG",
        "tool_call": {
            "tool_name": "discover_catalog",
            "parameters": {"category": "Footwear", "limit": 5}
        },
        "buyer_facing_message": null
    }
    """
    # Step 2: Model proposes request_price_quote for SKU-APEX-RUNNER
    step2_json = f"""
    {{
        "thought_process": "Requesting quote for SKU-APEX-RUNNER.",
        "intent": "REQUEST_QUOTE",
        "tool_call": {{
            "tool_name": "request_price_quote",
            "parameters": {{
                "session_id": "{session.id}",
                "items": [{{"sku": "SKU-APEX-RUNNER", "quantity": 1}}]
            }}
        }},
        "buyer_facing_message": null
    }}
    """
    # Step 3: Model presents quote to buyer
    step3_json = """
    {
        "thought_process": "Quote created. Presenting ₹5,000 price to buyer.",
        "intent": "RESPOND_TO_BUYER",
        "tool_call": null,
        "buyer_facing_message": "I found the Apex Velocity Running Shoes. The quote is ₹5,000."
    }
    """

    mock_llm_turn1 = MockLLMProvider(responses=[step1_json, step2_json, step3_json])
    runtime = AgentRuntime(llm_provider=mock_llm_turn1)

    turn1_result = await runtime.run_turn(
        session=db_session,
        user_message="Looking for running shoes.",
        context=gateway_context,
        merchant_name="Apex Athletics",
    )

    assert turn1_result.status == "COMPLETED"
    assert turn1_result.steps_taken == 3
    assert len(turn1_result.tool_calls_executed) == 2
    assert "₹5,000" in turn1_result.buyer_message

    # Verify PriceQuote created in DB
    quote_stmt = select(PriceQuote).where(PriceQuote.merchant_id == merchant.id)
    quote = (await db_session.execute(quote_stmt)).scalar_one()
    assert quote.status == "PROPOSED"
    assert quote.subtotal_paise == 500000
    assert quote.total_paise == 500000

    # =========================================================================
    # 3. TURN 2: NEGOTIATION (10% Discount Request)
    # =========================================================================
    # Model proposes negotiate_quote to ₹4,500 (450,000 paise)
    turn2_step1_json = f"""
    {{
        "thought_process": "Buyer requested 10% discount. Proposing ₹4,500.",
        "intent": "NEGOTIATE_QUOTE",
        "tool_call": {{
            "tool_name": "negotiate_quote",
            "parameters": {{
                "quote_id": "{quote.id}",
                "proposed_total_paise": 450000,
                "rationale": "10% promotional discount"
            }}
        }},
        "buyer_facing_message": null
    }}
    """
    turn2_step2_json = """
    {
        "thought_process": "Negotiation accepted. Confirming revised quote with buyer.",
        "intent": "RESPOND_TO_BUYER",
        "tool_call": null,
        "buyer_facing_message": "Great news! I can offer you the shoes for ₹4,500."
    }
    """

    mock_llm_turn2 = MockLLMProvider(responses=[turn2_step1_json, turn2_step2_json])
    runtime_turn2 = AgentRuntime(llm_provider=mock_llm_turn2)

    turn2_result = await runtime_turn2.run_turn(
        session=db_session,
        user_message="Can I get a 10% discount?",
        context=gateway_context,
        merchant_name="Apex Athletics",
    )

    assert turn2_result.status == "COMPLETED"
    assert "₹4,500" in turn2_result.buyer_message

    # Verify quote updated in DB with negotiated total
    await db_session.refresh(quote)
    assert quote.status == "PROPOSED"
    assert quote.total_paise == 450000
    assert quote.discount_paise == 50000

    # =========================================================================
    # 4. QUOTE ACCEPTANCE & ORDER CREATION
    # =========================================================================
    # Buyer accepts the revised quote -> transition to ACCEPTED
    await PriceQuoteStateMachine.transition(
        session=db_session,
        quote=quote,
        target_state="ACCEPTED",
        expected_version=quote.version,
        reason="Buyer accepted revised quote",
    )
    assert quote.status == "ACCEPTED"

    # Mock Razorpay API for order creation
    def rzp_handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/orders"
        return httpx.Response(
            status_code=200,
            json={
                "id": "order_GOLDEN_PATH_123",
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

    rzp_transport = httpx.MockTransport(rzp_handler)
    async with httpx.AsyncClient(transport=rzp_transport) as http_client:
        rzp_client = RazorpayClient(
            key_id=settings.RAZORPAY_KEY_ID,
            key_secret=SecretStr("rzp_secret"),
            http_client=http_client,
        )

        order = await PaymentService.create_order_from_accepted_quote(
            session=db_session,
            quote_id=quote.id,
            buyer_email="buyer.alpha@example.com",
            shipping_address={"city": "Bengaluru", "postal_code": "560001", "country": "IN"},
            rzp_client=rzp_client,
        )

    assert order.id is not None
    assert order.status == "PENDING_PAYMENT"
    assert order.amount_paise == 450000
    assert order.rzp_order_id == "order_GOLDEN_PATH_123"

    # =========================================================================
    # 5. PAYMENT CAPTURE VIA CRYPTOGRAPHIC WEBHOOK
    # =========================================================================
    simulated_payment_id = "pay_GOLDEN_SUCCESS_99"
    webhook_payload = {
        "event": "payment.captured",
        "payload": {
            "order": {
                "entity": {
                    "id": "order_GOLDEN_PATH_123",
                    "amount": 450000,
                    "status": "paid",
                }
            },
            "payment": {
                "entity": {
                    "id": simulated_payment_id,
                    "order_id": "order_GOLDEN_PATH_123",
                    "amount": 450000,
                    "status": "captured",
                    "method": "upi",
                }
            },
        },
    }
    raw_body = json.dumps(webhook_payload).encode("utf-8")
    signature = _sign(raw_body, webhook_secret)

    # Process webhook through PaymentService
    proc_result = await PaymentService.process_payment_webhook(
        session=db_session,
        raw_body=raw_body,
        signature_header=signature,
        webhook_secret=webhook_secret,
    )

    assert proc_result["status"] == "PROCESSED"
    assert proc_result["order_status"] == "PAID"

    # =========================================================================
    # 6. END-TO-END LEDGER & AUDIT INTEGRITY PROOFS
    # =========================================================================
    # Verify Order is PAID
    await db_session.refresh(order)
    assert order.status == "PAID"

    # Verify PaymentAttempt is CAPTURED
    pay_stmt = select(PaymentAttempt).where(PaymentAttempt.order_id == order.id)
    payment_attempt = (await db_session.execute(pay_stmt)).scalar_one()
    assert payment_attempt.status == "CAPTURED"
    assert payment_attempt.rzp_payment_id == simulated_payment_id
    assert payment_attempt.amount_paise == 450000

    # Verify TransactionRecord is COMMITTED in append-only ledger
    tx_stmt = select(TransactionRecord).where(
        TransactionRecord.payment_attempt_id == payment_attempt.id
    )
    tx_record = (await db_session.execute(tx_stmt)).scalar_one()
    assert tx_record.status == "COMMITTED"
    assert tx_record.entry_type == "CREDIT"
    assert tx_record.amount_paise == 450000
    assert tx_record.settlement_ref == simulated_payment_id

    # Verify comprehensive AuditEvent trail exists
    audit_stmt = select(AuditEvent).where(AuditEvent.merchant_id == merchant.id)
    all_audits = (await db_session.execute(audit_stmt)).scalars().all()
    event_types = [a.event_type for a in all_audits]

    assert "TOOL_EXECUTION" in event_types
    assert "AGENT_RUN_COMPLETED" in event_types
    assert "ORDER_TRANSITION_PENDING_PAYMENT" in event_types
    assert "ORDER_TRANSITION_PAID" in event_types
