"""Optional live integration test against Groq API using configured credentials."""

import pytest

from agent_ready_merchant.agent.intent import parse_structured_intent
from agent_ready_merchant.agent.prompt import build_system_prompt, format_untrusted_buyer_message
from agent_ready_merchant.config import get_settings
from agent_ready_merchant.llm.base import LLMMessage
from agent_ready_merchant.llm.exceptions import LLMError
from agent_ready_merchant.llm.groq_provider import GroqProvider


@pytest.mark.asyncio
async def test_live_groq_structured_intent_generation() -> None:
    """Verifies that the live Groq API generates valid StructuredIntent JSON."""
    settings = get_settings()
    api_key = settings.GROQ_API_KEY.get_secret_value()

    if not api_key or not api_key.startswith("gsk_"):
        pytest.skip("No live Groq API key configured; skipping live Groq test.")

    provider = GroqProvider(
        api_key=settings.GROQ_API_KEY,
        model=settings.LLM_MODEL_NAME,
    )

    system_prompt = build_system_prompt(
        merchant_name="Live Test Store",
        autonomy_level=1,
        available_tools=["discover_catalog", "get_product_details"],
    )

    user_msg = format_untrusted_buyer_message("Can you show me what shoes you have in stock?")
    messages = [
        LLMMessage(role="system", content=system_prompt),
        LLMMessage(role="user", content=user_msg),
    ]

    try:
        res = await provider.generate_response(messages=messages, timeout=15.0)
    except LLMError as exc:
        pytest.skip(f"Groq API live call skipped due to provider response: {exc}")

    assert res.content is not None
    assert len(res.content) > 0

    # Verify model output conforms to StructuredIntent schema
    intent = parse_structured_intent(res.content)
    assert intent.thought_process is not None
    assert intent.intent is not None
