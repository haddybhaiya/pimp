"""Integration tests for Phase 5.2 — Merchant Control Plane Operations & HITL."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.config import get_settings
from agent_ready_merchant.main import app
from agent_ready_merchant.models.approval import MerchantApproval
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.policy import PolicyRule
from agent_ready_merchant.models.quote import PriceQuote
from agent_ready_merchant.models.session import BuyerAgentSession
from agent_ready_merchant.services.merchant_auth_service import MerchantAuthService


@pytest_asyncio.fixture
async def setup_test_merchants(db_session: AsyncSession):
    """Fixture providing two distinct merchants with auth tokens for isolation tests."""
    settings = get_settings()
    secret = settings.RAZORPAY_WEBHOOK_SECRET.get_secret_value()

    # Merchant 1
    m1 = Merchant(
        name="Alpha Store",
        slug=f"alpha-store-{uuid.uuid4().hex[:6]}",
        status="ACTIVE",
        currency="INR",
        rzp_key_id="rzp_test_alpha123",
        created_at=datetime.now(UTC),
    )
    db_session.add(m1)
    await db_session.flush()

    expires = datetime.now(UTC) + timedelta(hours=24)
    token1 = MerchantAuthService._generate_admin_token(m1, expires, secret)

    # Merchant 2
    m2 = Merchant(
        name="Beta Store",
        slug=f"beta-store-{uuid.uuid4().hex[:6]}",
        status="ACTIVE",
        currency="INR",
        rzp_key_id="rzp_test_beta456",
        created_at=datetime.now(UTC),
    )
    db_session.add(m2)
    await db_session.flush()

    token2 = MerchantAuthService._generate_admin_token(m2, expires, secret)

    # Seed policy for Merchant 1
    p1 = PolicyRule(
        merchant_id=m1.id,
        rule_type="AUTONOMY_LEVEL",
        target_scope="GLOBAL",
        rule_value={"autonomy_level": 1},
        is_active=True,
    )
    p2 = PolicyRule(
        merchant_id=m1.id,
        rule_type="MAX_DISCOUNT_PCT",
        target_scope="GLOBAL",
        rule_value={"max_discount_pct": 15.0},
        is_active=True,
    )
    p3 = PolicyRule(
        merchant_id=m1.id,
        rule_type="MIN_MARGIN_PCT",
        target_scope="GLOBAL",
        rule_value={"min_margin_pct": 20.0},
        is_active=True,
    )
    p4 = PolicyRule(
        merchant_id=m1.id,
        rule_type="MAX_CART_VALUE",
        target_scope="GLOBAL",
        rule_value={"max_single_tx_paise": 5_000_000},
        is_active=True,
    )
    db_session.add_all([p1, p2, p3, p4])
    await db_session.flush()

    # Audit root for Merchant 1
    await AuditEvent.create_event(
        session=db_session,
        merchant_id=m1.id,
        actor_type="SYSTEM",
        event_type="MERCHANT_INITIALIZED",
        payload={"slug": m1.slug},
    )
    await db_session.commit()

    return {
        "m1": m1,
        "token1": token1,
        "m2": m2,
        "token2": token2,
    }


@pytest.mark.asyncio
async def test_dashboard_summary_kpis(setup_test_merchants):
    """Verifies that the dashboard summary aggregates authoritative metrics."""
    m1 = setup_test_merchants["m1"]
    token1 = setup_test_merchants["token1"]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(
            "/api/v1/merchant/dashboard/summary",
            headers={
                "X-Merchant-ID": str(m1.id),
                "X-Auth-Token": token1,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["merchant_id"] == str(m1.id)
        assert data["merchant_name"] == "Alpha Store"
        assert data["status"] == "ACTIVE"
        assert data["currency"] == "INR"
        assert data["autonomy_level"] == 1
        assert data["max_discount_percentage"] == 15.0
        assert data["system_health"] == "HEALTHY"
        assert len(data["policy_hash"]) == 64


@pytest.mark.asyncio
async def test_catalog_and_inventory_lifecycle(setup_test_merchants):
    """Verifies product creation, floor price validation, stock listing and adjustment."""
    m1 = setup_test_merchants["m1"]
    token1 = setup_test_merchants["token1"]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Invalid product (floor price > base price) rejected
        invalid_resp = await client.post(
            "/api/v1/merchant/products",
            headers={"X-Merchant-ID": str(m1.id), "X-Auth-Token": token1},
            json={
                "sku": "RUN-01",
                "title": "Invalid Shoe",
                "category": "FOOTWEAR",
                "base_price_paise": 400000,
                "floor_price_paise": 500000,  # Floor > Base is invalid
                "initial_stock": 10,
            },
        )
        assert invalid_resp.status_code == 400
        assert "Floor price cannot exceed base price" in invalid_resp.json()["detail"]

        # 2. Valid product creation
        create_resp = await client.post(
            "/api/v1/merchant/products",
            headers={"X-Merchant-ID": str(m1.id), "X-Auth-Token": token1},
            json={
                "sku": "RUN-01",
                "title": "Pro Runner 1",
                "description": "High performance shoes",
                "category": "FOOTWEAR",
                "base_price_paise": 500000,
                "floor_price_paise": 400000,
                "initial_stock": 20,
                "safety_threshold": 2,
            },
        )
        assert create_resp.status_code == 201
        prod_data = create_resp.json()
        assert prod_data["sku"] == "RUN-01"
        assert prod_data["available_stock"] == 20

        # 3. Duplicate SKU rejected
        dup_resp = await client.post(
            "/api/v1/merchant/products",
            headers={"X-Merchant-ID": str(m1.id), "X-Auth-Token": token1},
            json={
                "sku": "RUN-01",
                "title": "Duplicate Shoe",
                "category": "FOOTWEAR",
                "base_price_paise": 500000,
                "floor_price_paise": 400000,
            },
        )
        assert dup_resp.status_code == 400
        assert "already exists" in dup_resp.json()["detail"]

        # 4. List inventory
        inv_resp = await client.get(
            "/api/v1/merchant/inventory",
            headers={"X-Merchant-ID": str(m1.id), "X-Auth-Token": token1},
        )
        assert inv_resp.status_code == 200
        inv_list = inv_resp.json()
        assert len(inv_list) == 1
        assert inv_list[0]["sku"] == "RUN-01"
        assert inv_list[0]["available_quantity"] == 20

        # 5. Adjust inventory stock
        adj_resp = await client.post(
            "/api/v1/merchant/inventory/adjust",
            headers={"X-Merchant-ID": str(m1.id), "X-Auth-Token": token1},
            json={
                "sku": "RUN-01",
                "quantity_delta": 5,
                "reason": "SHIPMENT_RECEIVED",
            },
        )
        assert adj_resp.status_code == 200
        assert adj_resp.json()["available_quantity"] == 25

        # 6. Adjust inventory below zero rejected
        adj_fail = await client.post(
            "/api/v1/merchant/inventory/adjust",
            headers={"X-Merchant-ID": str(m1.id), "X-Auth-Token": token1},
            json={
                "sku": "RUN-01",
                "quantity_delta": -50,
            },
        )
        assert adj_fail.status_code == 400
        assert "Cannot adjust inventory below zero" in adj_fail.json()["detail"]


@pytest.mark.asyncio
async def test_approvals_hitl_resolution_flow(db_session: AsyncSession, setup_test_merchants):
    """Verifies HITL approval queue listing, approval, and rejection lifecycles."""
    m1 = setup_test_merchants["m1"]
    token1 = setup_test_merchants["token1"]

    # Seed buyer session and price quote
    session = BuyerAgentSession(
        merchant_id=m1.id,
        buyer_agent_identifier="test-buyer-agent",
        auth_token_hash="a" * 64,
        status="ACTIVE",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    quote = PriceQuote(
        session_id=session.id,
        merchant_id=m1.id,
        status="NEGOTIATING",
        subtotal_paise=500000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=500000,
        idempotency_key=f"quote-test-{uuid.uuid4()}",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    db_session.add(quote)
    await db_session.flush()

    # Seed pending approval ticket
    ticket = MerchantApproval(
        merchant_id=m1.id,
        quote_id=quote.id,
        session_id=session.id,
        approval_type="QUOTE_DISCOUNT",
        status="PENDING",
        requested_amount_paise=420000,
        proposed_discount_paise=80000,
        policy_decision_hash="0" * 64,
        policy_rule_code="MAX_DISCOUNT_PCT",
        reason="Requested 16% discount",
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
    )
    db_session.add(ticket)
    await db_session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. List pending approvals
        list_resp = await client.get(
            "/api/v1/merchant/approvals?status=PENDING",
            headers={"X-Merchant-ID": str(m1.id), "X-Auth-Token": token1},
        )
        assert list_resp.status_code == 200
        tickets = list_resp.json()
        assert len(tickets) == 1
        assert tickets[0]["id"] == str(ticket.id)
        assert tickets[0]["status"] == "PENDING"
        assert tickets[0]["requested_amount_paise"] == 420000

        # 2. Resolve approval ticket (APPROVE)
        res_resp = await client.post(
            f"/api/v1/merchant/approvals/{ticket.id}/resolve",
            headers={"X-Merchant-ID": str(m1.id), "X-Auth-Token": token1},
            json={
                "decision": "APPROVE",
                "reason_note": "Approved discount for loyal buyer",
            },
        )
        assert res_resp.status_code == 200
        resolved_data = res_resp.json()
        assert resolved_data["status"] == "APPROVED"
        assert resolved_data["reason"] == "Requested 16% discount"
        assert resolved_data["approver_identifier"] == "MERCHANT_ADMIN"

        # 3. Quote updated with approved terms
        await db_session.refresh(quote)
        assert quote.status == "PROPOSED"
        assert quote.discount_paise == 80000
        assert quote.total_paise == 420000

        # 4. Resolving already-resolved ticket is rejected
        res_dup = await client.post(
            f"/api/v1/merchant/approvals/{ticket.id}/resolve",
            headers={"X-Merchant-ID": str(m1.id), "X-Auth-Token": token1},
            json={
                "decision": "REJECT",
                "reason_note": "Try again",
            },
        )
        assert res_dup.status_code == 400
        assert "already resolved" in res_dup.json()["detail"]


@pytest.mark.asyncio
async def test_approvals_hitl_counter_offer_custom_amount(
    db_session: AsyncSession, setup_test_merchants
):
    """Verifies that COUNTER_OFFER applies the merchant's custom counter_amount_paise."""
    m1 = setup_test_merchants["m1"]
    token1 = setup_test_merchants["token1"]

    session = BuyerAgentSession(
        merchant_id=m1.id,
        buyer_agent_identifier="test-buyer-agent-counter",
        auth_token_hash="b" * 64,
        status="ACTIVE",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    quote = PriceQuote(
        session_id=session.id,
        merchant_id=m1.id,
        status="NEGOTIATING",
        subtotal_paise=500000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=500000,
        idempotency_key=f"quote-test-counter-{uuid.uuid4()}",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    db_session.add(quote)
    await db_session.flush()

    ticket = MerchantApproval(
        merchant_id=m1.id,
        quote_id=quote.id,
        session_id=session.id,
        approval_type="QUOTE_DISCOUNT",
        status="PENDING",
        requested_amount_paise=400000,
        proposed_discount_paise=100000,
        policy_decision_hash="1" * 64,
        policy_rule_code="MAX_DISCOUNT_PCT",
        reason="Requested 20% discount",
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
    )
    db_session.add(ticket)
    await db_session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Resolve with custom counter amount of 450,000 (10% discount counter)
        res_resp = await client.post(
            f"/api/v1/merchant/approvals/{ticket.id}/resolve",
            headers={"X-Merchant-ID": str(m1.id), "X-Auth-Token": token1},
            json={
                "decision": "COUNTER_OFFER",
                "counter_amount_paise": 450000,
                "reason_note": "Counter-offer at 10% discount",
            },
        )
        assert res_resp.status_code == 200
        resolved_data = res_resp.json()
        assert resolved_data["status"] == "APPROVED"
        assert resolved_data["requested_amount_paise"] == 450000

        await db_session.refresh(quote)
        assert quote.status == "PROPOSED"
        assert quote.total_paise == 450000
        assert quote.discount_paise == 50000
        assert quote.discount_reason is not None and "Counter-Offer" in quote.discount_reason


@pytest.mark.asyncio
async def test_policy_governance_update_and_bounds(setup_test_merchants):
    """Verifies fetching and updating policy governance with safety ceilings."""
    m1 = setup_test_merchants["m1"]
    token1 = setup_test_merchants["token1"]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Fetch current policy
        get_resp = await client.get(
            "/api/v1/merchant/policies",
            headers={"X-Merchant-ID": str(m1.id), "X-Auth-Token": token1},
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["max_discount_percentage"] == 15.0

        # 2. Update with invalid discount (>50%) rejected
        inv_resp = await client.put(
            "/api/v1/merchant/policies",
            headers={"X-Merchant-ID": str(m1.id), "X-Auth-Token": token1},
            json={
                "autonomy_level": 1,
                "max_discount_percentage": 55.0,  # exceeds 50% ceiling
                "min_margin_percentage": 20.0,
                "max_single_transaction_paise": 5000000,
            },
        )
        assert inv_resp.status_code == 422 or inv_resp.status_code == 400

        # 3. Valid policy update
        up_resp = await client.put(
            "/api/v1/merchant/policies",
            headers={"X-Merchant-ID": str(m1.id), "X-Auth-Token": token1},
            json={
                "autonomy_level": 2,
                "max_discount_percentage": 25.0,
                "min_margin_percentage": 15.0,
                "max_single_transaction_paise": 8000000,
            },
        )
        assert up_resp.status_code == 200
        updated = up_resp.json()
        assert updated["autonomy_level"] == 2
        assert updated["max_discount_percentage"] == 25.0
        assert len(updated["policy_hash"]) == 64


@pytest.mark.asyncio
async def test_audit_ledger_cryptographic_verification(setup_test_merchants):
    """Verifies audit ledger retrieval and SHA-256 hash chain integrity."""
    m1 = setup_test_merchants["m1"]
    token1 = setup_test_merchants["token1"]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(
            "/api/v1/merchant/audit?limit=20",
            headers={"X-Merchant-ID": str(m1.id), "X-Auth-Token": token1},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["chain_valid"] is True
        assert data["total_count"] >= 1
        assert len(data["events"]) >= 1
        assert data["events"][0]["event_type"] in ["MERCHANT_INITIALIZED", "POLICIES_UPDATED"]


@pytest.mark.asyncio
async def test_multi_tenant_isolation_at_api_boundary(setup_test_merchants):
    """Verifies strict cross-tenant isolation on all merchant control plane endpoints."""
    m2 = setup_test_merchants["m2"]
    token1 = setup_test_merchants["token1"]  # Token belonging to Merchant 1

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Attempting to query Merchant 2's dashboard with Merchant 1's token is rejected
        cross_dash = await client.get(
            "/api/v1/merchant/dashboard/summary",
            headers={"X-Merchant-ID": str(m2.id), "X-Auth-Token": token1},
        )
        assert cross_dash.status_code == 401

        # 2. Attempting to query Merchant 2's catalog with Merchant 1's token is rejected
        cross_cat = await client.get(
            "/api/v1/merchant/products",
            headers={"X-Merchant-ID": str(m2.id), "X-Auth-Token": token1},
        )
        assert cross_cat.status_code == 401

        # 3. Attempting to adjust Merchant 2's inventory with Merchant 1's token is rejected
        cross_inv = await client.post(
            "/api/v1/merchant/inventory/adjust",
            headers={"X-Merchant-ID": str(m2.id), "X-Auth-Token": token1},
            json={"sku": "RUN-01", "quantity_delta": 5},
        )
        assert cross_inv.status_code == 401

        # 4. Attempting to access Merchant 2's audit trail with Merchant 1's token is rejected
        cross_audit = await client.get(
            "/api/v1/merchant/audit",
            headers={"X-Merchant-ID": str(m2.id), "X-Auth-Token": token1},
        )
        assert cross_audit.status_code == 401
