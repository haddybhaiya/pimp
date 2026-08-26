"""Production-grade verification test suite for Phase 2.3.

Covers:
1. Protocol-neutral external API boundary & ACP Adapter.
2. Canonical commerce contract versioning ("2026-03-01") & request IDs.
3. Production hardening:
   - Thread-safe idempotency manager
   - Sliding-window rate limiter
   - Bounded payload size guards (64 KB)
   - Timeout boundaries
   - Safe error sanitization (no internal leaks)
4. Reliability: Safe retry policy vs. blind financial retry prohibition.
5. Production-Grade Hackathon Demo Flow:
   Merchant -> AI-ready representation -> Independent AI buyer -> Discover ->
   Select -> Inventory check -> Quote -> Bounded negotiation -> Acceptance ->
   Checkout -> Razorpay test payment -> Order completion -> Audit trail.
6. Deliberate failure + safe recovery + immutable audit chain inspection.
7. FastAPI wire endpoint (/api/v1/protocol/acp) verification.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from agent_ready_merchant.config import get_settings
from agent_ready_merchant.gateway.canonical import CanonicalCommerceGateway
from agent_ready_merchant.gateway.constants import COMMERCE_PROTOCOL_VERSION
from agent_ready_merchant.gateway.hardening import (
    GatewayErrorCode,
    GatewayRateLimiter,
    IdempotencyManager,
    global_idempotency_manager,
    global_rate_limiter,
    sanitize_error_response,
    validate_payload_size,
)
from agent_ready_merchant.gateway.schemas import (
    GatewayResponseEnvelope,
    QuoteItemRequest,
    ShippingAddressGateway,
)
from agent_ready_merchant.integrations.razorpay.client import RazorpayClient
from agent_ready_merchant.integrations.razorpay.exceptions import InvalidWebhookSignatureError
from agent_ready_merchant.integrations.razorpay.models import RazorpayOrderResponse
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.inventory import InventoryItem
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.order import Order
from agent_ready_merchant.models.product import Product, ProductVariant
from agent_ready_merchant.models.quote import PriceQuote
from agent_ready_merchant.models.session import BuyerAgentSession
from agent_ready_merchant.models.transaction import TransactionRecord
from agent_ready_merchant.protocols.acp import AgentCommerceProtocolAdapter
from agent_ready_merchant.protocols.base import ProtocolRequestMessage
from agent_ready_merchant.protocols.client import AgentProtocolClient
from agent_ready_merchant.tools.base import GatewayContext


# =============================================================================
# Fixtures & Test Data Seeding
# =============================================================================
@pytest_asyncio.fixture
async def seed_hardening_data(db_session: AsyncSession) -> dict[str, Any]:
    """Seeds test merchants, products, inventory, and active sessions."""
    global_idempotency_manager.reset()
    global_rate_limiter.reset()

    # Merchant A (High autonomy athletic retailer)
    merchant_a = Merchant(
        name="Apex Athletics India",
        slug=f"apex-{uuid.uuid4().hex[:6]}",
        status="ACTIVE",
        currency="INR",
        rzp_key_id="rzp_test_apex123",
    )
    # Merchant B (Low autonomy boutique)
    merchant_b = Merchant(
        name="Zenith Goods",
        slug=f"zenith-{uuid.uuid4().hex[:6]}",
        status="ACTIVE",
        currency="INR",
        rzp_key_id="rzp_test_zenith456",
    )
    db_session.add_all([merchant_a, merchant_b])
    await db_session.flush()

    # Product 1: High stock running shoes (Negotiable)
    # Base: ₹12,000 (1,200,000 paise), Floor: ₹9,000 (900,000 paise)
    prod1 = Product(
        merchant_id=merchant_a.id,
        sku="RUN-SHOE-PRO",
        title="Pro Marathon Running Shoes",
        description="Carbon-plated elite racing shoe",
        category="Footwear",
        base_price_paise=1200000,
        floor_price_paise=900000,
        is_negotiable=True,
        is_active=True,
    )
    db_session.add(prod1)
    await db_session.flush()

    var1 = ProductVariant(
        product_id=prod1.id,
        sku="RUN-SHOE-PRO-UK9",
        title="UK 9 / Solar Red",
        price_override_paise=1200000,
        is_active=True,
    )
    db_session.add(var1)
    await db_session.flush()

    inv1 = InventoryItem(
        variant_id=var1.id,
        available_quantity=50,
        reserved_quantity=0,
        safety_threshold=2,
    )
    db_session.add(inv1)

    # Active Session for Merchant A
    token_a = "token_acp_12345"
    token_hash = hashlib.sha256(token_a.encode("utf-8")).hexdigest()
    session_a = BuyerAgentSession(
        merchant_id=merchant_a.id,
        buyer_agent_identifier="test_buyer_acp",
        auth_token_hash=token_hash,
        status="ACTIVE",
        expires_at=datetime.now(UTC) + timedelta(hours=2),
    )
    db_session.add(session_a)
    await db_session.flush()

    return {
        "merchant_a": merchant_a,
        "merchant_b": merchant_b,
        "product_a": prod1,
        "variant_a": var1,
        "inventory_a": inv1,
        "session_a": session_a,
        "token_a": token_a,
    }


# =============================================================================
# 1. Protocol Adapter Boundary Tests
# =============================================================================
def test_acp_adapter_action_translation_matrix() -> None:
    """Verifies bidirectional ACP protocol translation for all canonical capabilities."""
    adapter = AgentCommerceProtocolAdapter()

    # 1. discover_products
    req1 = ProtocolRequestMessage(
        protocol="acp",
        version=COMMERCE_PROTOCOL_VERSION,
        action="discover_products",
        params={"category": "Footwear", "limit": 10},
    )
    cap1, payload1 = adapter.to_canonical_request(req1)
    assert cap1 == "discover_products"
    assert payload1["category"] == "Footwear"
    assert payload1["limit"] == 10

    # 2. check_inventory
    req2 = ProtocolRequestMessage(
        protocol="acp",
        version=COMMERCE_PROTOCOL_VERSION,
        action="check_inventory",
        params={"sku": "RUN-SHOE-PRO-UK9", "requested_quantity": 2},
    )
    cap2, payload2 = adapter.to_canonical_request(req2)
    assert cap2 == "check_inventory"
    assert payload2["sku"] == "RUN-SHOE-PRO-UK9"

    # 3. get_quote
    req3 = ProtocolRequestMessage(
        protocol="acp",
        version=COMMERCE_PROTOCOL_VERSION,
        action="request_quote",
        params={"session_id": str(uuid.uuid4()), "items": [{"sku": "SKU1", "quantity": 1}]},
    )
    cap3, payload3 = adapter.to_canonical_request(req3)
    assert cap3 == "get_quote"

    # 4. negotiate_quote
    req4 = ProtocolRequestMessage(
        protocol="acp",
        version=COMMERCE_PROTOCOL_VERSION,
        action="negotiate_quote",
        params={"quote_id": str(uuid.uuid4()), "proposed_total_paise": 1000000},
    )
    cap4, payload4 = adapter.to_canonical_request(req4)
    assert cap4 == "negotiate_quote"


def test_acp_adapter_rejects_unsupported_version_and_unknown_action() -> None:
    """Verifies that the protocol adapter rejects unsupported versions and unknown actions."""
    adapter = AgentCommerceProtocolAdapter()

    # Unsupported contract version
    req_bad_ver = ProtocolRequestMessage(
        protocol="acp",
        version="1999-01-01",
        action="discover_products",
        params={},
    )
    with pytest.raises(ValueError, match="Unsupported protocol contract version"):
        adapter.to_canonical_request(req_bad_ver)

    # Unknown action
    req_bad_action = ProtocolRequestMessage(
        protocol="acp",
        version=COMMERCE_PROTOCOL_VERSION,
        action="execute_arbitrary_code",
        params={},
    )
    with pytest.raises(ValueError, match="Unknown or unsupported ACP action"):
        adapter.to_canonical_request(req_bad_action)


# =============================================================================
# 2. Production Hardening Tests
# =============================================================================
@pytest.mark.asyncio
async def test_hardening_request_id_tracing(
    db_session: AsyncSession, seed_hardening_data: dict[str, Any]
) -> None:
    """Verifies request_id is propagated from client request through to response envelope."""
    merchant = seed_hardening_data["merchant_a"]
    session_a = seed_hardening_data["session_a"]
    gateway = CanonicalCommerceGateway()

    custom_request_id = uuid.uuid4()
    context = GatewayContext(
        merchant_id=merchant.id,
        session_id=session_a.id,
        capabilities={"buyer:discover"},
        request_id=custom_request_id,
        auth_token=seed_hardening_data["token_a"],
    )

    envelope = await gateway.execute_capability(
        session=db_session,
        capability_name="discover_products",
        payload={"limit": 5},
        context=context,
    )
    assert envelope.status == "SUCCESS"
    assert envelope.request_id == custom_request_id
    assert envelope.schema_version == COMMERCE_PROTOCOL_VERSION


@pytest.mark.asyncio
async def test_hardening_idempotency_manager_deduplication(
    db_session: AsyncSession, seed_hardening_data: dict[str, Any]
) -> None:
    """Verifies IdempotencyManager prevents duplicate mutation and returns cached response."""
    mgr = IdempotencyManager()
    merchant_id = uuid.uuid4()
    session_id = uuid.uuid4()
    idemp_key = f"idemp_{uuid.uuid4().hex}"

    # Initially not present
    cached = await mgr.check_idempotency(merchant_id, session_id, idemp_key)
    assert cached is None

    # Acquire mutation lock
    lock1 = await mgr.acquire_mutation_lock(merchant_id, session_id, idemp_key)
    assert lock1 is True

    # Concurrent identical mutation fails to acquire lock
    lock2 = await mgr.acquire_mutation_lock(merchant_id, session_id, idemp_key)
    assert lock2 is False

    # Store executed envelope
    sample_envelope = GatewayResponseEnvelope[Any](
        status="SUCCESS",
        capability="create_order",
        data={"order_id": str(uuid.uuid4()), "status": "CREATED"},
        idempotency_key=idemp_key,
    )
    await mgr.record_idempotency(merchant_id, session_id, idemp_key, sample_envelope)

    # Subsequent check returns exact cached envelope
    cached_after = await mgr.check_idempotency(merchant_id, session_id, idemp_key)
    assert cached_after is not None
    assert cached_after.status == "SUCCESS"
    assert cached_after.data == sample_envelope.data


def test_hardening_bounded_payload_size_validator() -> None:
    """Verifies BoundedPayloadGuard rejects payloads exceeding 64 KB."""
    # Small payload (Valid)
    valid_payload = {"query": "shoes", "limit": 10}
    is_valid, size = validate_payload_size(valid_payload, max_bytes=65536)
    assert is_valid is True
    assert size > 0

    # Huge payload > 64 KB (Invalid)
    huge_payload = {"massive_blob": "X" * 70000}
    is_invalid, size_huge = validate_payload_size(huge_payload, max_bytes=65536)
    assert is_invalid is False
    assert size_huge >= 70000


@pytest.mark.asyncio
async def test_hardening_sliding_window_rate_limiter() -> None:
    """Verifies sliding-window rate limiter rejects excess calls with retry-after guidance."""
    limiter = GatewayRateLimiter()
    client_key = "test_rate_session_123"

    # Allow up to 3 requests in 60s window
    for _ in range(3):
        allowed, _ = await limiter.check_rate_limit(client_key, limit=3, window_seconds=60)
        assert allowed is True

    # 4th request must be rejected
    allowed_4th, retry_after = await limiter.check_rate_limit(
        client_key, limit=3, window_seconds=60
    )
    assert allowed_4th is False
    assert retry_after > 0


def test_hardening_safe_error_sanitization() -> None:
    """Verifies unexpected exceptions do not leak stack traces or DB details in production."""
    req_id = uuid.uuid4()
    raw_exception = RuntimeError("FATAL: connection to postgresql://admin:secret@db:5432 failed")

    # In non-testing / production mode:
    safe_envelope = sanitize_error_response(
        capability="create_order",
        exc=raw_exception,
        request_id=req_id,
        is_testing=False,
    )
    assert safe_envelope.status == "ERROR"
    assert safe_envelope.error is not None
    assert safe_envelope.error.code == GatewayErrorCode.INTERNAL_GATEWAY_ERROR.value
    # Ensure raw database credentials / stack traces are NOT in message
    assert "postgresql://" not in safe_envelope.error.message
    assert "secret" not in safe_envelope.error.message
    assert str(req_id) in safe_envelope.error.message or str(req_id) in str(
        safe_envelope.error.details
    )


# =============================================================================
# 3. Reliability & Safe Retry Policy Tests
# =============================================================================
@pytest.mark.asyncio
async def test_reliability_safe_read_retries_and_blind_mutation_prohibition(
    db_session: AsyncSession, seed_hardening_data: dict[str, Any]
) -> None:
    """Verifies client retries safe reads while refusing blind retries on mutations."""
    merchant = seed_hardening_data["merchant_a"]
    buyer = AgentProtocolClient(merchant_id=merchant.id)
    await buyer.initialize_session(db_session)

    # 1. Safe read actions are declared safe
    assert "discover_products" in buyer.SAFE_IDEMPOTENT_ACTIONS
    assert "get_product" in buyer.SAFE_IDEMPOTENT_ACTIONS
    assert "check_inventory" in buyer.SAFE_IDEMPOTENT_ACTIONS
    assert "get_payment_status" in buyer.SAFE_IDEMPOTENT_ACTIONS
    assert "get_order_status" in buyer.SAFE_IDEMPOTENT_ACTIONS

    # 2. Mutating actions are NOT safe unless idempotency key provided
    assert "create_order" not in buyer.SAFE_IDEMPOTENT_ACTIONS
    assert "request_checkout" not in buyer.SAFE_IDEMPOTENT_ACTIONS
    assert "negotiate_quote" not in buyer.SAFE_IDEMPOTENT_ACTIONS


# =============================================================================
# 4. Production-Grade Hackathon Demo Verification Flow
# =============================================================================
@pytest.mark.asyncio
async def test_production_demo_full_lifecycle(
    db_session: AsyncSession, seed_hardening_data: dict[str, Any]
) -> None:
    """Complete Production-Grade Demo Flow:
    Merchant -> AI-ready representation -> Independent AI buyer (via ACP Protocol)
    -> Discover -> Select Product -> Check Stock -> Request Quote -> Bounded Negotiation
    -> Accept Quote -> Shipping Calculation -> Create Order -> Checkout
    -> Razorpay Test Payment -> Order Completion -> Immutable Audit Trail.
    """
    merchant = seed_hardening_data["merchant_a"]
    buyer = AgentProtocolClient(
        merchant_id=merchant.id,
        buyer_agent_identifier="ai_agent_buyer_hackathon_demo",
    )

    shipping_addr = ShippingAddressGateway(
        full_name="Ananya Sharma",
        address_line1="10 Indiranagar 100ft Road",
        city="Bengaluru",
        postal_code="560038",
        country="IN",
    )

    # Base price is ₹12,000 (1,200,000 paise). Floor is ₹9,000 (900,000 paise).
    # Proposed price: ₹10,800 (1,080,000 paise) = 10% discount (allowed by policy).
    proposed_negotiated_paise = 1080000

    with patch.object(
        RazorpayClient,
        "create_order",
        return_value=RazorpayOrderResponse(
            id=f"order_{uuid.uuid4().hex[:14]}",
            amount=1080000,
            currency="INR",
            status="created",
            created_at=int(datetime.now(UTC).timestamp()),
        ),
    ):
        flow_result = await buyer.execute_full_commerce_flow(
            session=db_session,
            query="Marathon",
            target_sku="RUN-SHOE-PRO",
            target_variant_sku="RUN-SHOE-PRO-UK9",
            quantity=1,
            buyer_email="ananya.sharma@example.com",
            shipping_address=shipping_addr,
            negotiate_proposed_paise=proposed_negotiated_paise,
        )

    # 1. Verify Flow Result
    assert flow_result.is_success is True
    assert flow_result.final_state == "COMPLETED"
    assert flow_result.order_id is not None
    assert flow_result.quote_id is not None
    assert flow_result.amount_paise == 1080000
    assert flow_result.payment_status == "PAID"
    assert flow_result.step_count == 14

    # 2. Verify Database State
    order = (
        await db_session.execute(select(Order).where(Order.id == flow_result.order_id))
    ).scalar_one()
    assert order.status == "PAID"
    assert order.amount_paise == 1080000

    # 3. Verify Append-Only Transaction Ledger
    tx_stmt = select(TransactionRecord).where(
        TransactionRecord.merchant_id == merchant.id,
        TransactionRecord.entry_type == "CREDIT",
    )
    tx_rec = (await db_session.execute(tx_stmt)).scalar_one_or_none()
    assert tx_rec is not None
    assert tx_rec.amount_paise == 1080000
    assert tx_rec.status == "COMMITTED"

    # 4. Verify Immutable Hash-Chained Audit Trail
    audit_stmt = (
        select(AuditEvent)
        .where(AuditEvent.merchant_id == merchant.id)
        .order_by(AuditEvent.created_at.asc())
    )
    events = list((await db_session.execute(audit_stmt)).scalars().all())
    event_types = [e.event_type for e in events]

    assert "BUYER_SESSION_INITIALIZED" in event_types
    assert "PRICE_QUOTE_CREATED" in event_types
    assert "PRICE_QUOTE_NEGOTIATED" in event_types
    assert "PRICE_QUOTE_ACCEPTED" in event_types
    assert "ORDER_TRANSITION_PENDING_PAYMENT" in event_types
    assert "ORDER_TRANSITION_PAID" in event_types
    assert "BUYER_SESSION_TERMINATED" in event_types


# =============================================================================
# 5. Deliberate Failure + Safe Recovery + Audit Chain Inspection
# =============================================================================
@pytest.mark.asyncio
async def test_production_demo_deliberate_failure_and_safe_recovery(
    db_session: AsyncSession, seed_hardening_data: dict[str, Any]
) -> None:
    """Deliberately triggers payment failure, verifies safe fail-closed state,
    recovers via legitimate payment authorization, and verifies the audit log.
    """
    merchant = seed_hardening_data["merchant_a"]
    buyer = AgentProtocolClient(
        merchant_id=merchant.id,
        buyer_agent_identifier="failure_recovery_buyer",
    )
    await buyer.initialize_session(db_session)

    # 1. Quote & Accept
    q_res = await buyer.get_quote(
        db_session, items=[QuoteItemRequest(sku="RUN-SHOE-PRO-UK9", quantity=1)]
    )
    assert q_res.status == "SUCCESS"
    assert q_res.result is not None
    quote_id = uuid.UUID(q_res.result["quote_id"])

    acc_res = await buyer.accept_quote(db_session, quote_id=quote_id)
    assert acc_res.status == "SUCCESS"

    shipping_addr = ShippingAddressGateway(
        full_name="Rohit Verma",
        address_line1="55 MG Road",
        city="Pune",
        postal_code="411001",
        country="IN",
    )

    with patch.object(
        RazorpayClient,
        "create_order",
        return_value=RazorpayOrderResponse(
            id="order_mock_fail_recover_123",
            amount=1200000,
            currency="INR",
            status="created",
            created_at=int(datetime.now(UTC).timestamp()),
        ),
    ):
        ord_res = await buyer.create_order(
            db_session,
            quote_id=quote_id,
            buyer_email="rohit@example.com",
            shipping_address=shipping_addr,
        )
        assert ord_res.status == "SUCCESS"
        assert ord_res.result is not None
        order_id = uuid.UUID(ord_res.result["order_id"])

        await buyer.request_checkout(db_session, order_id=order_id)

    # 2. Deliberate Failure: Invalid Webhook Signature
    settings = get_settings()
    with pytest.raises(InvalidWebhookSignatureError):
        from agent_ready_merchant.services.payment_service import PaymentService

        await PaymentService.process_payment_webhook(
            session=db_session,
            raw_body=b'{"event":"payment.captured"}',
            signature_header="invalid_tampered_signature",
            webhook_secret=settings.RAZORPAY_WEBHOOK_SECRET.get_secret_value(),
        )

    # Verify Order is NOT marked PAID (still PENDING_PAYMENT)
    order_before = (
        await db_session.execute(select(Order).where(Order.id == order_id))
    ).scalar_one()
    assert order_before.status in {"PENDING_PAYMENT", "CREATED"}

    # 3. Recovery: Valid Authorized Payment Webhook
    await buyer.authorize_test_payment(db_session, order_id=order_id)

    # Verify Order is now PAID
    order_after = (await db_session.execute(select(Order).where(Order.id == order_id))).scalar_one()
    assert order_after.status == "PAID"

    # 4. Audit Chain Inspection
    audit_stmt = (
        select(AuditEvent)
        .where(AuditEvent.merchant_id == merchant.id)
        .order_by(AuditEvent.created_at.asc())
    )
    events = list((await db_session.execute(audit_stmt)).scalars().all())
    assert len(events) >= 3


# =============================================================================
# 6. FastAPI Protocol Wire Endpoint Verification
# =============================================================================
@pytest.mark.asyncio
async def test_fastapi_acp_wire_endpoint(
    client: AsyncClient, seed_hardening_data: dict[str, Any]
) -> None:
    """Verifies POST /api/v1/protocol/acp executes properly over HTTP."""
    merchant = seed_hardening_data["merchant_a"]
    session_a = seed_hardening_data["session_a"]

    headers = {
        "X-Merchant-ID": str(merchant.id),
        "X-Session-ID": str(session_a.id),
        "X-Auth-Token": seed_hardening_data["token_a"],
        "X-Commerce-Protocol-Version": COMMERCE_PROTOCOL_VERSION,
    }

    # 1. Discover products via ACP wire message
    req_msg = {
        "protocol": "acp",
        "version": COMMERCE_PROTOCOL_VERSION,
        "request_id": str(uuid.uuid4()),
        "action": "discover_products",
        "params": {"category": "Footwear", "limit": 5},
    }
    resp = await client.post("/api/v1/protocol/acp", json=req_msg, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["protocol"] == "acp"
    assert data["status"] == "SUCCESS"
    assert data["action"] == "discover_products"
    assert data["result"]["total_matched"] >= 1

    # 2. Check inventory via ACP wire message
    inv_msg = {
        "protocol": "acp",
        "version": COMMERCE_PROTOCOL_VERSION,
        "request_id": str(uuid.uuid4()),
        "action": "check_inventory",
        "params": {"sku": "RUN-SHOE-PRO-UK9", "requested_quantity": 1},
    }
    inv_resp = await client.post("/api/v1/protocol/acp", json=inv_msg, headers=headers)
    assert inv_resp.status_code == 200
    inv_data = inv_resp.json()
    assert inv_data["status"] == "SUCCESS"
    assert inv_data["result"]["in_stock"] is True
    assert inv_data["result"]["can_fulfill"] is True


# =============================================================================
# 7. Regression Tests for Architecture Hardening (Issues 1 - 4)
# =============================================================================
@pytest.mark.asyncio
async def test_regression_issue1_session_token_cryptographic_verification(
    db_session: AsyncSession, seed_hardening_data: dict[str, Any]
) -> None:
    """Issue 1: Verifies that presented session auth tokens are cryptographically validated."""
    merchant = seed_hardening_data["merchant_a"]
    gateway = CanonicalCommerceGateway()

    # 1. Create a session with a known token hash
    token_raw = "secret_agent_token_xyz"
    token_hash = hashlib.sha256(token_raw.encode("utf-8")).hexdigest()
    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="auth_tester",
        auth_token_hash=token_hash,
        status="ACTIVE",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.commit()

    # 2. Request with omitted token -> Rejection with AUTH_INVALID_CREDENTIAL (fail closed)
    omitted_ctx = GatewayContext(
        merchant_id=merchant.id,
        session_id=session.id,
        capabilities={"buyer:discover", "buyer:read"},
        auth_token=None,
    )
    res_omitted = await gateway.execute_capability(
        db_session, "discover_products", {"limit": 5}, omitted_ctx
    )
    assert res_omitted.status == "REJECTED"
    assert res_omitted.error is not None
    assert res_omitted.error.code == "AUTH_INVALID_CREDENTIAL"
    assert "required" in res_omitted.error.message.lower()

    # 3. Request with invalid token -> Rejection with AUTH_INVALID_CREDENTIAL
    bad_ctx = GatewayContext(
        merchant_id=merchant.id,
        session_id=session.id,
        capabilities={"buyer:discover", "buyer:read"},
        auth_token="wrong_token_here",
    )
    res_bad = await gateway.execute_capability(
        db_session, "discover_products", {"limit": 5}, bad_ctx
    )
    assert res_bad.status == "REJECTED"
    assert res_bad.error is not None
    assert res_bad.error.code == "AUTH_INVALID_CREDENTIAL"

    # 4. Request with valid token -> Success
    good_ctx = GatewayContext(
        merchant_id=merchant.id,
        session_id=session.id,
        capabilities={"buyer:discover", "buyer:read"},
        auth_token=token_raw,
    )
    res_good = await gateway.execute_capability(
        db_session, "discover_products", {"limit": 5}, good_ctx
    )
    assert res_good.status == "SUCCESS"


@pytest.mark.asyncio
async def test_regression_issue2_idempotency_payload_mismatch_rejection(
    db_session: AsyncSession, seed_hardening_data: dict[str, Any]
) -> None:
    """Issue 2: Verifies that reusing an idempotency key with a changed payload is rejected."""
    merchant = seed_hardening_data["merchant_a"]
    session_a = seed_hardening_data["session_a"]
    gateway = CanonicalCommerceGateway()
    idem_key = f"idem_mismatch_test_{uuid.uuid4().hex[:8]}"

    ctx = GatewayContext(
        merchant_id=merchant.id,
        session_id=session_a.id,
        capabilities={"buyer:quote", "buyer:read"},
        idempotency_key=idem_key,
        auth_token=seed_hardening_data["token_a"],
    )

    # 1. Initial request with quantity 1
    payload1 = {
        "session_id": str(session_a.id),
        "items": [{"sku": "RUN-SHOE-PRO-UK9", "quantity": 1}],
        "idempotency_key": idem_key,
    }
    res1 = await gateway.execute_capability(db_session, "get_quote", payload1, ctx)
    assert res1.status == "SUCCESS"
    assert res1.data is not None

    # 2. Replayed request with SAME key and SAME payload -> Cached response returned
    res1_replay = await gateway.execute_capability(db_session, "get_quote", payload1, ctx)
    assert res1_replay.status == "SUCCESS"
    assert res1_replay.data is not None

    # 3. Replayed request with SAME key but CHANGED payload (quantity=2) -> IDEMPOTENCY_CONFLICT
    payload2 = {
        "session_id": str(session_a.id),
        "items": [{"sku": "RUN-SHOE-PRO-UK9", "quantity": 2}],
        "idempotency_key": idem_key,
    }
    res2_conflict = await gateway.execute_capability(db_session, "get_quote", payload2, ctx)
    assert res2_conflict.status == "REJECTED"
    assert res2_conflict.error is not None
    assert res2_conflict.error.code == "IDEMPOTENCY_CONFLICT"


@pytest.mark.asyncio
async def test_regression_issue3_negotiated_order_line_items_pricing(
    db_session: AsyncSession, seed_hardening_data: dict[str, Any]
) -> None:
    """Issue 3: Verifies that an accepted negotiation updates QuoteItem line-item prices."""
    merchant = seed_hardening_data["merchant_a"]
    buyer = AgentProtocolClient(
        merchant_id=merchant.id,
        buyer_agent_identifier="line_item_pricing_buyer",
    )
    await buyer.initialize_session(db_session)

    # 1. Get initial quote (₹12,000 = 1,200,000 paise)
    q_res = await buyer.get_quote(
        db_session,
        items=[QuoteItemRequest(sku="RUN-SHOE-PRO-UK9", quantity=2)],
    )
    assert q_res.status == "SUCCESS"
    assert q_res.result is not None
    quote_id = uuid.UUID(q_res.result["quote_id"])

    # 2. Negotiate 10% discount: 2,400,000 -> 2,160,000 paise (₹21,600)
    neg_res = await buyer.negotiate_quote(
        db_session,
        quote_id=quote_id,
        proposed_total_paise=2160000,
        rationale="Volume discount for 2 pairs",
    )
    assert neg_res.status == "SUCCESS"

    # 3. Verify QuoteItem prices in DB are updated
    q_db = (
        await db_session.execute(
            select(PriceQuote)
            .where(PriceQuote.id == quote_id)
            .options(selectinload(PriceQuote.items))
        )
    ).scalar_one()
    assert q_db.items[0].unit_price_paise == 1080000
    assert q_db.items[0].total_price_paise == 2160000
    assert sum(itm.total_price_paise for itm in q_db.items) == 2160000

    # 4. Accept Quote and Create Order
    await buyer.accept_quote(db_session, quote_id=quote_id)
    shipping_address = ShippingAddressGateway(
        full_name="Alex Runner",
        address_line1="456 Indiranagar",
        city="Bengaluru",
        postal_code="560038",
        country="IN",
    )
    with patch.object(
        RazorpayClient,
        "create_order",
        return_value=RazorpayOrderResponse(
            id=f"order_{uuid.uuid4().hex[:14]}",
            amount=2160000,
            currency="INR",
            status="created",
            created_at=int(datetime.now(UTC).timestamp()),
        ),
    ):
        ord_res = await buyer.create_order(
            db_session,
            quote_id=quote_id,
            buyer_email="buyer@example.com",
            shipping_address=shipping_address,
        )
    assert ord_res.status == "SUCCESS"
    assert ord_res.result is not None
    order_id = uuid.UUID(ord_res.result["order_id"])

    # 5. Verify Order and OrderItem pricing matches negotiated total
    ord_db = (
        await db_session.execute(
            select(Order).where(Order.id == order_id).options(selectinload(Order.items))
        )
    ).scalar_one()
    assert ord_db.amount_paise == 2160000
    assert ord_db.items[0].unit_price_paise == 1080000
    assert ord_db.items[0].total_price_paise == 2160000
    assert sum(itm.total_price_paise for itm in ord_db.items) == ord_db.amount_paise


@pytest.mark.asyncio
async def test_regression_issue4_privileged_financial_timeout_not_retryable(
    db_session: AsyncSession, seed_hardening_data: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Issue 4: Verifies that a timeout during create_order returns retryable=False."""
    merchant = seed_hardening_data["merchant_a"]
    session_a = seed_hardening_data["session_a"]
    gateway = CanonicalCommerceGateway()

    # Mock _dispatch_internal to raise TimeoutError
    async def mock_timeout(*args: Any, **kwargs: Any) -> Any:
        raise TimeoutError("Simulated execution timeout")

    monkeypatch.setattr(gateway, "_dispatch_internal", mock_timeout)

    ctx = GatewayContext(
        merchant_id=merchant.id,
        session_id=session_a.id,
        capabilities={"buyer:checkout", "buyer:orders"},
        idempotency_key="financial_timeout_key_1",
        auth_token=seed_hardening_data["token_a"],
    )
    req_payload = {
        "quote_id": str(uuid.uuid4()),
        "buyer_email": "timeout_test@example.com",
        "shipping_address": {
            "full_name": "Alex Runner",
            "address_line1": "123 Main St",
            "city": "Bengaluru",
            "postal_code": "560001",
            "country": "IN",
        },
        "idempotency_key": "financial_timeout_key_1",
    }
    res = await gateway.execute_capability(db_session, "create_order", req_payload, ctx)
    assert res.status == "ERROR"
    assert res.error is not None
    assert res.error.code == "TIMEOUT_BOUNDARY_EXCEEDED"
    assert res.error.retryable is False
