"""Tests for database CHECK constraints, non-negative quantities, and foreign keys."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.models.agent_run import AgentRun
from agent_ready_merchant.models.inventory import InventoryItem
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.policy import PolicyRule
from agent_ready_merchant.models.product import Product, ProductVariant
from agent_ready_merchant.models.quote import PriceQuote, QuoteItem
from agent_ready_merchant.models.session import BuyerAgentSession


@pytest.mark.asyncio
async def test_inventory_negative_quantity_rejected(db_session: AsyncSession) -> None:
    """Verifies that available_quantity < 0 violates CHECK constraint."""
    merchant = Merchant(name="Shop", slug="shop-neg", rzp_key_id="rzp_test_1")
    db_session.add(merchant)
    await db_session.flush()

    product = Product(
        merchant_id=merchant.id,
        sku="SKU-NEG",
        title="Negative Item",
        category="Cat",
        base_price_paise=1000,
        floor_price_paise=900,
    )
    db_session.add(product)
    await db_session.flush()

    variant = ProductVariant(product_id=product.id, sku="SKU-NEG-V", title="Var")
    db_session.add(variant)
    await db_session.flush()

    # Attempting to insert negative quantity must raise IntegrityError
    invalid_inventory = InventoryItem(
        variant_id=variant.id,
        available_quantity=-1,  # Violates ck_inventory_available_non_negative
    )
    db_session.add(invalid_inventory)
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_quote_item_zero_quantity_rejected(db_session: AsyncSession) -> None:
    """Verifies that quote item quantity <= 0 violates CHECK constraint."""
    now = datetime.now(UTC)
    merchant = Merchant(name="ShopQ", slug="shop-q", rzp_key_id="rzp_test_q")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="buyer_1",
        auth_token_hash="hash_abc",
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    product = Product(
        merchant_id=merchant.id,
        sku="SKU-Q",
        title="Q Item",
        category="Cat",
        base_price_paise=1000,
        floor_price_paise=900,
    )
    db_session.add(product)
    await db_session.flush()

    variant = ProductVariant(product_id=product.id, sku="SKU-Q-V", title="Var Q")
    db_session.add(variant)
    await db_session.flush()

    quote = PriceQuote(
        session_id=session.id,
        merchant_id=merchant.id,
        status="PROPOSED",
        subtotal_paise=1000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=1000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key="key_q_1",
    )
    db_session.add(quote)
    await db_session.flush()

    # Attempting to insert zero quantity must raise IntegrityError
    invalid_item = QuoteItem(
        quote_id=quote.id,
        variant_id=variant.id,
        quantity=0,  # Violates ck_quote_items_quantity_positive
        unit_price_paise=1000,
        total_price_paise=0,
    )
    db_session.add(invalid_item)
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_policy_rule_valid_types_and_scopes(db_session: AsyncSession) -> None:
    """Verifies creation and constraints on PolicyRule."""
    merchant = Merchant(name="ShopPol", slug="shop-pol", rzp_key_id="rzp_test_pol")
    db_session.add(merchant)
    await db_session.flush()

    # Valid policy rule
    policy = PolicyRule(
        merchant_id=merchant.id,
        rule_type="MAX_DISCOUNT_PCT",
        target_scope="GLOBAL",
        rule_value={"max_discount_percentage": 15.0},
    )
    db_session.add(policy)
    await db_session.flush()
    assert policy.id is not None

    # Invalid rule_type should raise IntegrityError
    invalid_policy = PolicyRule(
        merchant_id=merchant.id,
        rule_type="UNAUTHORIZED_RULE_TYPE",
        target_scope="GLOBAL",
        rule_value={},
    )
    db_session.add(invalid_policy)
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_agent_run_step_count_bounded(db_session: AsyncSession) -> None:
    """Verifies that AgentRun enforces step_count <= 5."""
    now = datetime.now(UTC)
    merchant = Merchant(name="ShopAgent", slug="shop-agent", rzp_key_id="rzp_test_agent")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="buyer_agent_bound",
        auth_token_hash="hash_bound",
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    # Valid run (step_count = 5)
    valid_run = AgentRun(
        session_id=session.id,
        status="RUNNING",
        step_count=5,
        total_tokens=1000,
    )
    db_session.add(valid_run)
    await db_session.flush()
    assert valid_run.step_count == 5

    # Invalid run (step_count = 6 exceeds bounded limit)
    invalid_run = AgentRun(
        session_id=session.id,
        status="RUNNING",
        step_count=6,  # Violates ck_agent_runs_step_count_bounded
        total_tokens=1200,
    )
    db_session.add(invalid_run)
    with pytest.raises(IntegrityError):
        await db_session.flush()
