"""Unit tests for Structured Intent parsing and validation."""

import pytest

from agent_ready_merchant.agent.intent import (
    MalformedIntentError,
    StructuredIntent,
    parse_structured_intent,
)


def test_parse_valid_structured_intent() -> None:
    """Verifies that clean JSON parses into StructuredIntent correctly."""
    raw = """
    {
        "thought_process": "Buyer asked for shoe catalog.",
        "intent": "DISCOVER_CATALOG",
        "tool_call": {
            "tool_name": "discover_catalog",
            "parameters": {
                "category": "Footwear",
                "limit": 5
            }
        },
        "buyer_facing_message": "Let me look up available footwear for you."
    }
    """
    intent = parse_structured_intent(raw)
    assert isinstance(intent, StructuredIntent)
    assert intent.intent == "DISCOVER_CATALOG"
    assert intent.tool_call is not None
    assert intent.tool_call.tool_name == "discover_catalog"
    assert intent.tool_call.parameters["limit"] == 5


def test_parse_markdown_wrapped_json() -> None:
    """Verifies that JSON enclosed within ```json code fences is correctly extracted."""
    raw = """Here is the response:
```json
{
    "thought_process": "Responding with greetings.",
    "intent": "RESPOND_TO_BUYER",
    "tool_call": null,
    "buyer_facing_message": "Hello! How can I assist you today?"
}
```
"""
    intent = parse_structured_intent(raw)
    assert intent.intent == "RESPOND_TO_BUYER"
    assert intent.tool_call is None
    assert intent.buyer_facing_message == "Hello! How can I assist you today?"


def test_reject_malformed_json() -> None:
    """Verifies that non-JSON strings raise MalformedIntentError."""
    with pytest.raises(MalformedIntentError) as exc:
        parse_structured_intent("I am not a JSON object at all.")
    assert "Invalid JSON" in str(exc.value)


def test_reject_missing_required_fields() -> None:
    """Verifies that missing thought_process or intent raises MalformedIntentError."""
    raw = '{"intent": "TEST"}'  # missing thought_process
    with pytest.raises(MalformedIntentError) as exc:
        parse_structured_intent(raw)
    assert "Schema validation failed" in str(exc.value)


def test_reject_extra_unallowed_fields() -> None:
    """Verifies that unexpected extra fields raise MalformedIntentError."""
    raw = """
    {
        "thought_process": "test",
        "intent": "TEST",
        "tool_call": null,
        "buyer_facing_message": "Hi",
        "unauthorized_injection_field": 123
    }
    """
    with pytest.raises(MalformedIntentError) as exc:
        parse_structured_intent(raw)
    assert "Schema validation failed" in str(exc.value)
