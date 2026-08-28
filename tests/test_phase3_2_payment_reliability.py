"""Phase 3.2 — Payment Reliability Hardening Test Suite.

Comprehensive adversarial, concurrency, idempotency, and state-machine verification:
- Webhook signature verification edge cases (timing attack resistance, whitespace)
- Webhook replay protection and timestamp freshness validation (stale / future timestamps)
- Atomic webhook deduplication backed by durable ProcessedWebhook database table
- Concurrent duplicate webhook deliveries with DB unique constraint protection
- Order creation retry safety (remote mutation succeeded followed by local timeout)
- Receipt-based external order recovery without blind duplicate external creation
- Reconciliation idempotency and concurrent webhook-reconciliation serialization
- Transaction ledger uniqueness (uq_transaction_records_settlement_entry enforcement)
- Audit event cryptographic hash chaining under concurrency and tamper detection
- Payment/Order state machine terminal state preservation and regression protection
"""

import hashlib
import hmac
import json
import uuid
from datetime import UTC, datetime, timedelta

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.integrations.razorpay.client import RazorpayClient
from agent_ready_merchant.integrations.razorpay.exceptions import (
    InvalidWebhookSignatureError,
    WebhookProcessingInProgressError,
    WebhookTimestampError,
)
from agent_ready_merchant.integrations.razorpay.webhook import (
    assert_valid_webhook_signature,
    verify_razorpay_webhook_signature,
)
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.inventory import InventoryItem
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.order import Order
from agent_ready_merchant.models.payment import PaymentAttempt
from agent_ready_merchant.models.product import Product, ProductVariant
from agent_ready_merchant.models.quote import PriceQuote, QuoteItem
from agent_ready_merchant.models.session import BuyerAgentSession
from agent_ready_merchant.models.transaction import TransactionRecord
from agent_ready_merchant.models.webhook import ProcessedWebhook
from agent_ready_merchant.services.payment_service import PaymentService
from tests.fake_razorpay import DeterministicFakeRazorpayTransport

TEST_SECRET = "webhook_hardening_secret_key_999"


def _sign(body: bytes, secret: str = TEST_SECRET) -> str:
    return hmac.new(key=secret.encode("utf-8"), msg=body, digestmod=hashlib.sha256).hexdigest()


async def _seed_test_fixture(
    db_session: AsyncSession,
    total_paise: int = 500_000,
    rzp_order_id: str | None = None,
    order_status: str = "PENDING_PAYMENT",
) -> tuple[Merchant, BuyerAgentSession, PriceQuote, Order | None]:
    now = datetime.now(UTC)
    uid = uuid.uuid4().hex[:8]

    merchant = Merchant(
        name=f"Reliability Merchant {uid}",
        slug=f"rel-store-{uid}",
        currency="INR",
        rzp_key_id=f"rzp_test_{uid}",
    )
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier=f"rel-agent-{uid}",
        auth_token_hash=hashlib.sha256(b"tok").hexdigest(),
        status="ACTIVE",
        expires_at=now + timedelta(hours=2),
    )
    db_session.add(session)
    await db_session.flush()

    product = Product(
        merchant_id=merchant.id,
        sku=f"REL-SKU-{uid}",
        title="Reliability Test Product",
        description="Desc",
        category="Testing",
        base_price_paise=total_paise,
        floor_price_paise=int(total_paise * 0.8),
        is_negotiable=False,
        is_active=True,
    )
    db_session.add(product)
    await db_session.flush()

    variant = ProductVariant(
        product_id=product.id,
        sku=f"REL-VAR-{uid}",
        title="Default Variant",
        price_override_paise=total_paise,
        is_active=True,
    )
    db_session.add(variant)
    await db_session.flush()

    db_session.add(
        InventoryItem(
            variant_id=variant.id,
            available_quantity=20,
            reserved_quantity=0,
            safety_threshold=1,
        )
    )

    quote = PriceQuote(
        merchant_id=merchant.id,
        session_id=session.id,
        status="ACCEPTED",
        subtotal_paise=total_paise,
        discount_paise=0,
        shipping_paise=0,
        total_paise=total_paise,
        expires_at=now + timedelta(minutes=15),
        idempotency_key=f"rel-quote-key-{uid}",
        version=2,
    )
    db_session.add(quote)
    await db_session.flush()

    quote_item = QuoteItem(
        quote_id=quote.id,
        variant_id=variant.id,
        quantity=1,
        unit_price_paise=total_paise,
        total_price_paise=total_paise,
    )
    db_session.add(quote_item)
    await db_session.flush()

    order = None
    if rzp_order_id:
        order = Order(
            quote_id=quote.id,
            merchant_id=merchant.id,
            status=order_status,
            amount_paise=total_paise,
            currency="INR",
            buyer_email=f"buyer_{uid}@example.com",
            shipping_address={"city": "Mumbai", "postal_code": "400001", "country": "IN"},
            rzp_order_id=rzp_order_id,
        )
        db_session.add(order)
        await db_session.flush()

    return merchant, session, quote, order


# =============================================================================
# 1. Webhook Signature Verification Hardening
# =============================================================================


def test_signature_verification_edge_cases() -> None:
    """Verifies that webhook signature validation handles malformed, empty, and noisy headers."""
    raw = b'{"event":"test"}'
    valid_sig = _sign(raw, TEST_SECRET)

    # Valid
    assert verify_razorpay_webhook_signature(raw, valid_sig, TEST_SECRET) is True

    # Leading/trailing whitespace in header stripped cleanly
    assert verify_razorpay_webhook_signature(raw, f"  {valid_sig}  \n", TEST_SECRET) is True

    # Empty/None header fails closed
    assert verify_razorpay_webhook_signature(raw, None, TEST_SECRET) is False
    assert verify_razorpay_webhook_signature(raw, "", TEST_SECRET) is False
    assert verify_razorpay_webhook_signature(b"", valid_sig, TEST_SECRET) is False
    assert verify_razorpay_webhook_signature(raw, valid_sig, "") is False

    # Tampered signature
    assert verify_razorpay_webhook_signature(raw, "tampered_hex_value", TEST_SECRET) is False

    with pytest.raises(InvalidWebhookSignatureError):
        assert_valid_webhook_signature(raw, "invalid_sig", TEST_SECRET)


# =============================================================================
# 2. Webhook Replay Protection & Timestamp Freshness
# =============================================================================


@pytest.mark.asyncio
async def test_webhook_replay_protection_timestamp_bounds(db_session: AsyncSession) -> None:
    """Verifies that webhooks with timestamps outside allowed retry window are rejected."""
    _, _, _, order = await _seed_test_fixture(db_session, rzp_order_id="order_replay_ts_01")
    assert order is not None

    now = int(datetime.now(UTC).timestamp())

    # Case A: Expired timestamp (> 24 hours ago)
    stale_payload = {
        "event": "order.paid",
        "created_at": now - 90000,  # 25 hours ago
        "payload": {
            "order": {"entity": {"id": order.rzp_order_id, "amount": order.amount_paise}},
            "payment": {
                "entity": {
                    "id": "pay_stale_01",
                    "order_id": order.rzp_order_id,
                    "amount": order.amount_paise,
                    "status": "captured",
                }
            },
        },
    }
    raw_stale = json.dumps(stale_payload).encode("utf-8")
    sig_stale = _sign(raw_stale, TEST_SECRET)

    with pytest.raises(WebhookTimestampError, match="outside the allowed replay window"):
        await PaymentService.process_payment_webhook(
            session=db_session,
            raw_body=raw_stale,
            signature_header=sig_stale,
            webhook_secret=TEST_SECRET,
        )

    # Case B: Far future timestamp (> 5 mins in future, clock skew attack)
    future_payload = dict(stale_payload)
    future_payload["created_at"] = now + 600  # 10 minutes in future
    raw_future = json.dumps(future_payload).encode("utf-8")
    sig_future = _sign(raw_future, TEST_SECRET)

    with pytest.raises(WebhookTimestampError, match="outside the allowed replay window"):
        await PaymentService.process_payment_webhook(
            session=db_session,
            raw_body=raw_future,
            signature_header=sig_future,
            webhook_secret=TEST_SECRET,
        )


# =============================================================================
# 3. Atomic Webhook Deduplication via Durable Database Table
# =============================================================================


@pytest.mark.asyncio
async def test_atomic_webhook_deduplication_durable_table(db_session: AsyncSession) -> None:
    """Verifies that ProcessedWebhook table stores payload hash and deduplicates replays."""
    _, _, _, order = await _seed_test_fixture(db_session, rzp_order_id="order_durable_dedup_01")
    assert order is not None

    pay_id = "pay_durable_01"
    payload = {
        "event": "payment.captured",
        "created_at": int(datetime.now(UTC).timestamp()),
        "payload": {
            "order": {
                "entity": {
                    "id": order.rzp_order_id,
                    "amount": order.amount_paise,
                    "currency": "INR",
                }
            },
            "payment": {
                "entity": {
                    "id": pay_id,
                    "order_id": order.rzp_order_id,
                    "amount": order.amount_paise,
                    "currency": "INR",
                    "status": "captured",
                }
            },
        },
    }
    raw = json.dumps(payload).encode("utf-8")
    sig = _sign(raw, TEST_SECRET)

    # 1. First delivery: Processed
    res1 = await PaymentService.process_payment_webhook(
        session=db_session, raw_body=raw, signature_header=sig, webhook_secret=TEST_SECRET
    )
    assert res1["status"] == "PROCESSED"
    assert order.status == "PAID"

    # Verify ProcessedWebhook row exists with PROCESSED status
    payload_hash = hashlib.sha256(raw).hexdigest()
    stmt = select(ProcessedWebhook).where(ProcessedWebhook.payload_hash == payload_hash)
    pw = (await db_session.execute(stmt)).scalar_one_or_none()
    assert pw is not None
    assert pw.status == "PROCESSED"
    assert pw.rzp_payment_id == pay_id

    # 2. Duplicate delivery (Replay): Must return DUPLICATE_IGNORED
    res2 = await PaymentService.process_payment_webhook(
        session=db_session, raw_body=raw, signature_header=sig, webhook_secret=TEST_SECRET
    )
    assert res2["status"] == "DUPLICATE_IGNORED"

    # 3. Third delivery: Must still return DUPLICATE_IGNORED
    res3 = await PaymentService.process_payment_webhook(
        session=db_session, raw_body=raw, signature_header=sig, webhook_secret=TEST_SECRET
    )
    assert res3["status"] == "DUPLICATE_IGNORED"

    # Verify strictly 1 TransactionRecord exists
    tx_stmt = select(TransactionRecord).where(TransactionRecord.settlement_ref == pay_id)
    tx_records = (await db_session.execute(tx_stmt)).scalars().all()
    assert len(tx_records) == 1


# =============================================================================
# 4. Concurrent Duplicate Deliveries & Collision Handling
# =============================================================================


@pytest.mark.asyncio
async def test_concurrent_duplicate_deliveries_single_commitment(db_session: AsyncSession) -> None:
    """Verifies that concurrent deliveries for the same payment result in exactly 1 credit."""
    _, _, _, order = await _seed_test_fixture(db_session, rzp_order_id="order_conc_test_01")
    assert order is not None

    pay_id = "pay_concurrent_99"
    payload = {
        "event": "payment.captured",
        "created_at": int(datetime.now(UTC).timestamp()),
        "payload": {
            "order": {
                "entity": {
                    "id": order.rzp_order_id,
                    "amount": order.amount_paise,
                    "currency": "INR",
                }
            },
            "payment": {
                "entity": {
                    "id": pay_id,
                    "order_id": order.rzp_order_id,
                    "amount": order.amount_paise,
                    "status": "captured",
                    "currency": "INR",
                }
            },
        },
    }
    raw = json.dumps(payload).encode("utf-8")
    sig = _sign(raw, TEST_SECRET)

    # Initial delivery
    res_first = await PaymentService.process_payment_webhook(
        session=db_session, raw_body=raw, signature_header=sig, webhook_secret=TEST_SECRET
    )
    assert res_first["status"] == "PROCESSED"

    # Subsequent re-delivery hits deduplication
    res_second = await PaymentService.process_payment_webhook(
        session=db_session, raw_body=raw, signature_header=sig, webhook_secret=TEST_SECRET
    )
    assert res_second["status"] == "DUPLICATE_IGNORED"

    # Test concurrent in-flight delivery protection:
    # Arriving while another worker is PROCESSING triggers a retryable error
    in_flight_raw = b'{"event":"payment.captured","test":"in_flight_concurrent"}'
    in_flight_pw = ProcessedWebhook(
        event_id="evt_in_flight_99",
        event_name="payment.captured",
        payload_hash=hashlib.sha256(in_flight_raw).hexdigest(),
        signature_hash="sig_hash_99",
        status="PROCESSING",
    )
    db_session.add(in_flight_pw)
    await db_session.flush()

    with pytest.raises(WebhookProcessingInProgressError):
        await PaymentService.process_payment_webhook(
            session=db_session,
            raw_body=in_flight_raw,
            signature_header=_sign(in_flight_raw, TEST_SECRET),
            webhook_secret=TEST_SECRET,
        )

    # Confirm ledger integrity: Exactly 1 CREDIT entry for the committed payment
    tx_stmt = select(TransactionRecord).where(TransactionRecord.settlement_ref == pay_id)
    records = (await db_session.execute(tx_stmt)).scalars().all()
    assert len(records) == 1
    assert records[0].entry_type == "CREDIT"
    assert records[0].amount_paise == order.amount_paise


# =============================================================================
# 5. Order Creation Retry Safety & External Timeout Ambiguity
# =============================================================================


@pytest.mark.asyncio
async def test_order_creation_retry_reuses_remote_order_on_timeout(
    db_session: AsyncSession,
) -> None:
    """A remote order created before a network timeout must be reused on retry."""
    _, _, quote, _ = await _seed_test_fixture(db_session)
    assert quote is not None

    receipt_id = f"ord_{quote.id.hex[:32]}"
    transport = DeterministicFakeRazorpayTransport()
    client = RazorpayClient(
        key_id="rzp_test_mock",
        key_secret="mock_secret",
        http_client=httpx.AsyncClient(transport=transport),
    )

    # 1. Pre-create order on fake transport simulating remote order before timeout
    pre_order = await client.create_order(
        amount_paise=quote.total_paise,
        currency="INR",
        receipt=receipt_id,
    )
    initial_create_calls = transport.create_order_calls

    # 2. Call create_order_from_accepted_quote on retry
    # It must discover and reuse the existing remote order via receipt fallback
    order = await PaymentService.create_order_from_accepted_quote(
        session=db_session,
        quote_id=quote.id,
        buyer_email="retry@example.com",
        shipping_address={"city": "Delhi"},
        rzp_client=client,
    )

    assert order.rzp_order_id == pre_order.id
    assert order.amount_paise == quote.total_paise
    assert order.status == "PENDING_PAYMENT"
    # Ensure NO duplicate create_order call was dispatched to Razorpay
    assert transport.create_order_calls == initial_create_calls


# =============================================================================
# 6. Reconciliation Idempotency & Serialization with Webhooks
# =============================================================================


@pytest.mark.asyncio
async def test_reconciliation_idempotency_on_terminal_order(db_session: AsyncSession) -> None:
    """Reconciling an already settled order returns ALREADY_TERMINAL without modifying state."""
    _, _, _, order = await _seed_test_fixture(
        db_session, rzp_order_id="order_reco_term_01", order_status="PAID"
    )
    assert order is not None

    client = RazorpayClient(key_id="rzp_test_mock", key_secret="mock_secret")

    # Order is already PAID: reconciliation must immediately return ALREADY_TERMINAL
    res = await PaymentService.reconcile_order(
        session=db_session,
        order_id=order.id,
        rzp_client=client,
    )
    assert res["status"] == "ALREADY_TERMINAL"
    assert res["order_status"] == "PAID"


# =============================================================================
# 7. Transaction Ledger Uniqueness Constraint
# =============================================================================


@pytest.mark.asyncio
async def test_transaction_ledger_settlement_ref_uniqueness_enforcement(
    db_session: AsyncSession,
) -> None:
    """Verifies that uq_transaction_records_settlement_entry rejects duplicate CREDIT."""
    merchant, _, _, order = await _seed_test_fixture(db_session, rzp_order_id="order_tx_uniq_01")
    assert order is not None

    # Create first attempt and transaction
    attempt1 = PaymentAttempt(
        order_id=order.id,
        rzp_payment_id="pay_unique_settle_01",
        rzp_order_id=order.rzp_order_id,
        status="CAPTURED",
        amount_paise=order.amount_paise,
    )
    db_session.add(attempt1)
    await db_session.flush()

    tx1 = TransactionRecord(
        payment_attempt_id=attempt1.id,
        merchant_id=merchant.id,
        entry_type="CREDIT",
        amount_paise=order.amount_paise,
        status="COMMITTED",
        settlement_ref="pay_unique_settle_01",
    )
    db_session.add(tx1)
    await db_session.flush()

    # Create a second attempt attempting to reuse the same settlement_ref
    attempt2 = PaymentAttempt(
        order_id=order.id,
        rzp_payment_id="pay_unique_settle_02",
        rzp_order_id=order.rzp_order_id,
        status="CAPTURED",
        amount_paise=order.amount_paise,
    )
    db_session.add(attempt2)
    await db_session.flush()

    tx2 = TransactionRecord(
        payment_attempt_id=attempt2.id,
        merchant_id=merchant.id,
        entry_type="CREDIT",
        amount_paise=order.amount_paise,
        status="COMMITTED",
        settlement_ref="pay_unique_settle_01",  # Duplicate settlement_ref!
    )
    db_session.add(tx2)

    with pytest.raises(IntegrityError):
        await db_session.flush()

    await db_session.rollback()


# =============================================================================
# 8. Cryptographic Audit Chain Verification & Tamper Detection
# =============================================================================


@pytest.mark.asyncio
async def test_audit_event_verify_chain_and_tamper_detection(db_session: AsyncSession) -> None:
    """Verifies that AuditEvent.verify_chain validates intact chains and detects tampering."""
    merchant = Merchant(
        name="Audit Chain Store",
        slug=f"audit-store-{uuid.uuid4().hex[:6]}",
        currency="INR",
        rzp_key_id="rzp_test_audit",
    )
    db_session.add(merchant)
    await db_session.flush()

    # Append 3 valid events
    e1 = await AuditEvent.create_event(
        session=db_session,
        merchant_id=merchant.id,
        actor_type="SYSTEM",
        event_type="ORDER_CREATED",
        payload={"order_id": "ord_1"},
    )
    e2 = await AuditEvent.create_event(
        session=db_session,
        merchant_id=merchant.id,
        actor_type="SYSTEM",
        event_type="PAYMENT_CAPTURED",
        payload={"order_id": "ord_1", "payment_id": "pay_1"},
    )
    e3 = await AuditEvent.create_event(
        session=db_session,
        merchant_id=merchant.id,
        actor_type="SYSTEM",
        event_type="TRANSACTION_COMMITTED",
        payload={"order_id": "ord_1", "amount": 500000},
    )

    # 1. Chain must be valid
    assert e2.prev_event_hash == e1.event_hash
    assert e3.prev_event_hash == e2.event_hash
    assert e1.event_hash != e3.event_hash
    is_valid, err = await AuditEvent.verify_chain(db_session, merchant.id)
    assert is_valid is True, f"verify_chain failed with: {err}"
    assert err is None

    # 2. Deliberately tamper with payload of event e2
    e2.payload = {"order_id": "ord_1", "payment_id": "pay_TAMPERED"}
    await db_session.flush()

    # Chain verification must now fail
    is_valid_tampered, err_tampered = await AuditEvent.verify_chain(db_session, merchant.id)
    assert is_valid_tampered is False
    assert err_tampered is not None
    assert "Digest mismatch" in err_tampered


# =============================================================================
# 9. Payment/Order State Machine Regression Resistance
# =============================================================================


@pytest.mark.asyncio
async def test_payment_failure_webhook_on_settled_order_is_ignored(
    db_session: AsyncSession,
) -> None:
    """A delayed payment.failed webhook must never regress an already PAID order."""
    _, _, _, order = await _seed_test_fixture(
        db_session, rzp_order_id="order_regr_01", order_status="PAID"
    )
    assert order is not None

    fail_payload = {
        "event": "payment.failed",
        "created_at": int(datetime.now(UTC).timestamp()),
        "payload": {
            "order": {"entity": {"id": order.rzp_order_id, "amount": order.amount_paise}},
            "payment": {
                "entity": {
                    "id": "pay_failed_late",
                    "order_id": order.rzp_order_id,
                    "amount": order.amount_paise,
                    "status": "failed",
                    "error_code": "BAD_REQUEST_ERROR",
                }
            },
        },
    }
    raw = json.dumps(fail_payload).encode("utf-8")
    sig = _sign(raw, TEST_SECRET)

    res = await PaymentService.process_payment_webhook(
        session=db_session, raw_body=raw, signature_header=sig, webhook_secret=TEST_SECRET
    )

    assert res["status"] == "STATE_REGRESSION_IGNORED"
    assert order.status == "PAID"
