"""Integration tests for ToolGateway validation, capabilities, execution, and audit logging."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.agent.intent import ToolCallProposal
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.product import Product, ProductVariant
from agent_ready_merchant.models.session import BuyerAgentSession
from agent_ready_merchant.tools.base import GatewayContext
from agent_ready_merchant.tools.gateway import ToolGateway


@pytest.mark.asyncio
async def test_gateway_rejects_unknown_tool(db_session: AsyncSession) -> None:
    """Verifies that calling an unregistered tool returns UNKNOWN_TOOL error."""
    now = datetime.now(UTC)
    merchant = Merchant(name="M1", slug="m1", rzp_key_id="rzp_test_m1")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="buyer_m1",
        auth_token_hash="hash_m1",
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    gateway = ToolGateway()
    context = GatewayContext(
        merchant_id=merchant.id,
        session_id=session.id,
        capabilities={"buyer:discover"},
    )
    proposal = ToolCallProposal(
        tool_name="unregistered_arbitrary_tool",
        parameters={"foo": "bar"},
    )
    res = await gateway.execute_tool_call(db_session, proposal, context)
    assert res.status == "ERROR"
    assert res.error is not None
    assert res.error["code"] == "UNKNOWN_TOOL"


@pytest.mark.asyncio
async def test_gateway_rejects_unauthorized_capability(db_session: AsyncSession) -> None:
    """Verifies that missing required capability returns CAPABILITY_DENIED."""
    now = datetime.now(UTC)
    merchant = Merchant(name="M2", slug="m2", rzp_key_id="rzp_test_m2")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="buyer_m2",
        auth_token_hash="hash_m2",
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    gateway = ToolGateway()
    context = GatewayContext(
        merchant_id=merchant.id,
        session_id=session.id,
        capabilities={"buyer:discover"},  # Missing buyer:quote
    )
    proposal = ToolCallProposal(
        tool_name="request_price_quote",
        parameters={"session_id": str(session.id), "items": [{"sku": "SKU-1", "quantity": 1}]},
    )
    res = await gateway.execute_tool_call(db_session, proposal, context)
    assert res.status == "REJECTED"
    assert res.error is not None
    assert res.error["code"] == "CAPABILITY_DENIED"


@pytest.mark.asyncio
async def test_gateway_rejects_invalid_parameters(db_session: AsyncSession) -> None:
    """Verifies that malformed parameters return INVALID_TOOL_ARGUMENTS."""
    now = datetime.now(UTC)
    merchant = Merchant(name="M3", slug="m3", rzp_key_id="rzp_test_m3")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="buyer_m3",
        auth_token_hash="hash_m3",
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    gateway = ToolGateway()
    context = GatewayContext(
        merchant_id=merchant.id,
        session_id=session.id,
        capabilities={"buyer:discover"},
    )
    proposal = ToolCallProposal(
        tool_name="discover_catalog",
        parameters={"limit": 999},  # exceeds max 10
    )
    res = await gateway.execute_tool_call(db_session, proposal, context)
    assert res.status == "ERROR"
    assert res.error is not None
    assert res.error["code"] == "INVALID_TOOL_ARGUMENTS"


@pytest.mark.asyncio
async def test_gateway_executes_discover_and_product_details(db_session: AsyncSession) -> None:
    """Verifies discover_catalog and get_product_details read-only execution."""
    now = datetime.now(UTC)
    merchant = Merchant(name="Gadget Store", slug="gadget-store", rzp_key_id="rzp_test_gadget")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="buyer_gadget",
        auth_token_hash="hash_g",
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    product = Product(
        merchant_id=merchant.id,
        sku="SKU-PHONE-01",
        title="Smart Phone Pro",
        category="Electronics",
        base_price_paise=5000000,
        floor_price_paise=4500000,
    )
    db_session.add(product)
    await db_session.flush()

    variant = ProductVariant(product_id=product.id, sku="SKU-PHONE-01-V", title="256GB")
    db_session.add(variant)
    await db_session.flush()

    gateway = ToolGateway()
    context = GatewayContext(
        merchant_id=merchant.id,
        session_id=session.id,
        capabilities={"buyer:discover", "buyer:read"},
    )

    # 1. Discover Catalog
    disc_prop = ToolCallProposal(
        tool_name="discover_catalog",
        parameters={"category": "Electronics", "limit": 5},
    )
    disc_res = await gateway.execute_tool_call(db_session, disc_prop, context)
    assert disc_res.status == "SUCCESS"
    assert disc_res.data is not None
    assert disc_res.data["total_matched"] == 1
    assert disc_res.data["products"][0]["sku"] == "SKU-PHONE-01"

    # 2. Get Product Details
    details_prop = ToolCallProposal(
        tool_name="get_product_details",
        parameters={"sku": "SKU-PHONE-01"},
    )
    details_res = await gateway.execute_tool_call(db_session, details_prop, context)
    assert details_res.status == "SUCCESS"
    assert details_res.data is not None
    assert details_res.data["title"] == "Smart Phone Pro"

    # 3. Verify Audit Log
    audit_stmt = select(AuditEvent).where(AuditEvent.merchant_id == merchant.id)
    audits = (await db_session.execute(audit_stmt)).scalars().all()
    assert len(audits) >= 2


@pytest.mark.asyncio
async def test_gateway_request_quote_and_policy_negotiation(db_session: AsyncSession) -> None:
    """Verifies request_price_quote and negotiate_quote execution with policy engine."""
    now = datetime.now(UTC)
    merchant = Merchant(name="Shoe Store", slug="shoe-store", rzp_key_id="rzp_test_shoe")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="buyer_shoes",
        auth_token_hash="hash_s",
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    product = Product(
        merchant_id=merchant.id,
        sku="SKU-SHOE-01",
        title="Runner Shoes",
        category="Footwear",
        base_price_paise=500000,  # ₹5,000
        floor_price_paise=400000,  # ₹4,000 floor
        is_negotiable=True,
    )
    db_session.add(product)
    await db_session.flush()

    variant = ProductVariant(product_id=product.id, sku="SKU-SHOE-01-V", title="Size 9")
    db_session.add(variant)
    await db_session.flush()

    gateway = ToolGateway()
    context = GatewayContext(
        merchant_id=merchant.id,
        session_id=session.id,
        capabilities={"buyer:quote", "buyer:negotiate"},
        autonomy_level=1,
        max_discount_percentage=15.0,  # Max 15% discount
    )

    # 1. Request Quote
    req_prop = ToolCallProposal(
        tool_name="request_price_quote",
        parameters={
            "session_id": str(session.id),
            "items": [{"sku": "SKU-SHOE-01", "quantity": 1}],
        },
    )
    req_res = await gateway.execute_tool_call(db_session, req_prop, context)
    assert req_res.status == "SUCCESS"
    assert req_res.data is not None
    quote_id = req_res.data["quote_id"]
    assert req_res.data["subtotal_paise"] == 500000

    # 2. Negotiate Quote (10% discount: ₹4,500 = 450,000 paise - Within 15% limit)
    neg_prop = ToolCallProposal(
        tool_name="negotiate_quote",
        parameters={
            "quote_id": quote_id,
            "proposed_total_paise": 450000,
            "rationale": "Buyer requested 10% discount",
        },
    )
    neg_res = await gateway.execute_tool_call(db_session, neg_prop, context)
    assert neg_res.status == "SUCCESS"
    assert neg_res.data is not None
    assert neg_res.data["status"] == "ACCEPTED"
    assert neg_res.data["total_paise"] == 450000

    # 3. Attempt Negotiate Quote below floor price (₹3,000 = 300,000 paise - Breaches floor)
    bad_prop = ToolCallProposal(
        tool_name="negotiate_quote",
        parameters={
            "quote_id": quote_id,
            "proposed_total_paise": 300000,
        },
    )
    bad_res = await gateway.execute_tool_call(db_session, bad_prop, context)
    assert bad_res.status == "SUCCESS"
    assert bad_res.data is not None
    assert bad_res.data["status"] == "REJECTED"
    assert "Counter-offer rejected by policy" in bad_res.data["message"]
