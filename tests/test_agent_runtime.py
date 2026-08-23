"""Integration tests for AgentRuntime bounds, step limits, and multi-turn execution."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.agent.runtime import AgentRuntime
from agent_ready_merchant.llm.mock_provider import MockLLMProvider
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.product import Product
from agent_ready_merchant.models.session import BuyerAgentSession
from agent_ready_merchant.tools.base import GatewayContext


@pytest.mark.asyncio
async def test_runtime_step_limit_enforcement(db_session: AsyncSession) -> None:
    """Verifies that an agent proposing endless tool calls is stopped at max_steps (5)."""
    now = datetime.now(UTC)
    merchant = Merchant(name="LimitStore", slug="limit-store", rzp_key_id="rzp_test_limit")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="buyer_limit",
        auth_token_hash="hash_l",
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    endless_tool_response = """
    {
        "thought_process": "Searching catalog repeatedly.",
        "intent": "DISCOVER_CATALOG",
        "tool_call": {
            "tool_name": "discover_catalog",
            "parameters": {"limit": 1}
        },
        "buyer_facing_message": null
    }
    """
    mock_llm = MockLLMProvider(responses=[endless_tool_response] * 10)
    runtime = AgentRuntime(llm_provider=mock_llm)

    context = GatewayContext(
        merchant_id=merchant.id,
        session_id=session.id,
        capabilities={"buyer:discover"},
    )

    result = await runtime.run_turn(
        session=db_session,
        user_message="Find all products",
        context=context,
        max_steps=5,
    )

    assert result.status == "STEP_LIMIT_EXCEEDED"
    assert result.steps_taken == 5
    assert len(result.tool_calls_executed) == 5


@pytest.mark.asyncio
async def test_runtime_malformed_retry_and_recovery(db_session: AsyncSession) -> None:
    """Verifies that runtime gives structured feedback on malformed JSON and recovers on retry."""
    now = datetime.now(UTC)
    merchant = Merchant(name="RetryStore", slug="retry-store", rzp_key_id="rzp_test_retry")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="buyer_retry",
        auth_token_hash="hash_r",
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    malformed_first = "I am not a valid JSON!"
    valid_second = """
    {
        "thought_process": "Fixed JSON formatting.",
        "intent": "RESPOND_TO_BUYER",
        "tool_call": null,
        "buyer_facing_message": "Hello! How can I help you today?"
    }
    """
    mock_llm = MockLLMProvider(responses=[malformed_first, valid_second])
    runtime = AgentRuntime(llm_provider=mock_llm)

    context = GatewayContext(
        merchant_id=merchant.id,
        session_id=session.id,
        capabilities={"buyer:discover"},
    )

    result = await runtime.run_turn(
        session=db_session,
        user_message="Hello",
        context=context,
    )

    assert result.status == "COMPLETED"
    assert result.buyer_message == "Hello! How can I help you today?"
    assert result.steps_taken == 2


@pytest.mark.asyncio
async def test_runtime_happy_path_tool_to_buyer_message(db_session: AsyncSession) -> None:
    """Verifies a full turn where model invokes discover_catalog and synthesizes response."""
    now = datetime.now(UTC)
    merchant = Merchant(name="Book Store", slug="book-store", rzp_key_id="rzp_test_books")
    db_session.add(merchant)
    await db_session.flush()

    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier="buyer_books",
        auth_token_hash="hash_b",
        expires_at=now + timedelta(hours=1),
    )
    db_session.add(session)
    await db_session.flush()

    product = Product(
        merchant_id=merchant.id,
        sku="SKU-BOOK-01",
        title="Python Systems Design",
        category="Books",
        base_price_paise=300000,
        floor_price_paise=250000,
    )
    db_session.add(product)
    await db_session.flush()

    step1_response = """
    {
        "thought_process": "Searching for systems books.",
        "intent": "DISCOVER_CATALOG",
        "tool_call": {
            "tool_name": "discover_catalog",
            "parameters": {"query": "Systems", "limit": 5}
        },
        "buyer_facing_message": null
    }
    """
    step2_response = """
    {
        "thought_process": "Found Python Systems Design. Informing buyer.",
        "intent": "RESPOND_TO_BUYER",
        "tool_call": null,
        "buyer_facing_message": "We have 'Python Systems Design' available for ₹3,000."
    }
    """
    mock_llm = MockLLMProvider(responses=[step1_response, step2_response])
    runtime = AgentRuntime(llm_provider=mock_llm)

    context = GatewayContext(
        merchant_id=merchant.id,
        session_id=session.id,
        capabilities={"buyer:discover"},
    )

    result = await runtime.run_turn(
        session=db_session,
        user_message="Do you have any systems books?",
        context=context,
    )

    assert result.status == "COMPLETED"
    assert result.steps_taken == 2
    assert "Python Systems Design" in result.buyer_message
    assert len(result.tool_calls_executed) == 1
    assert result.tool_calls_executed[0]["status"] == "SUCCESS"
