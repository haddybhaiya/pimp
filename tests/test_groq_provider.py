"""Unit tests for GroqProvider adapter and error mappings."""

import json

import httpx
import pytest
from pydantic import SecretStr

from agent_ready_merchant.llm.base import LLMMessage
from agent_ready_merchant.llm.exceptions import (
    LLMAuthenticationError,
    LLMProviderError,
    LLMTimeoutError,
)
from agent_ready_merchant.llm.groq_provider import GroqProvider


@pytest.mark.asyncio
async def test_groq_provider_success() -> None:
    """Verifies that GroqProvider correctly sends messages and parses JSON completion."""

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/openai/v1/chat/completions"
        assert request.headers["authorization"] == "Bearer gsk_valid_key_123"
        assert json.loads(request.content)["response_format"] == {"type": "json_object"}
        return httpx.Response(
            status_code=200,
            json={
                "id": "chatcmpl-123",
                "object": "chat.completion",
                "created": 1740000000,
                "model": "llama-3.3-70b-versatile",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": (
                                '{"thought_process":"test","intent":"TEST",'
                                '"tool_call":null,"buyer_facing_message":"Hello"}'
                            ),
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 15,
                    "completion_tokens": 25,
                    "total_tokens": 40,
                },
            },
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        provider = GroqProvider(
            api_key=SecretStr("gsk_valid_key_123"),
            http_client=http_client,
        )
        res = await provider.generate_response(
            messages=[LLMMessage(role="user", content="Hello")],
        )
        assert res.model == "llama-3.3-70b-versatile"
        assert "thought_process" in res.content
        assert res.usage["total_tokens"] == 40


@pytest.mark.asyncio
async def test_groq_provider_uses_strict_schema_for_gpt_oss() -> None:
    """GPT-OSS merchant analysis must use provider-enforced structured output."""
    schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["diagnoses", "proposals"],
        "properties": {"diagnoses": {"type": "array"}, "proposals": {"type": "array"}},
    }

    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        assert payload["response_format"] == {
            "type": "json_schema",
            "json_schema": {
                "name": "merchant_agent_analysis",
                "strict": True,
                "schema": schema,
            },
        }
        return httpx.Response(
            status_code=200,
            json={
                "model": "openai/gpt-oss-20b",
                "choices": [{"message": {"content": '{"diagnoses":[],"proposals":[]}'}}],
                "usage": {},
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        provider = GroqProvider(
            api_key=SecretStr("gsk_valid_key_123"),
            model="openai/gpt-oss-20b",
            http_client=http_client,
            response_schema=schema,
        )
        response = await provider.generate_response([LLMMessage(role="user", content="Hi")])

    assert response.content == '{"diagnoses":[],"proposals":[]}'


@pytest.mark.asyncio
async def test_groq_provider_auth_failure() -> None:
    """Verifies that HTTP 401 raises LLMAuthenticationError."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=401, json={"error": {"message": "Invalid API Key"}})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        provider = GroqProvider(
            api_key=SecretStr("gsk_invalid_key"),
            http_client=http_client,
        )
        with pytest.raises(LLMAuthenticationError):
            await provider.generate_response([LLMMessage(role="user", content="Hi")])


@pytest.mark.asyncio
async def test_groq_provider_timeout_error() -> None:
    """Verifies that request timeout raises LLMTimeoutError."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("Timeout")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        provider = GroqProvider(
            api_key=SecretStr("gsk_key"),
            http_client=http_client,
        )
        with pytest.raises(LLMTimeoutError):
            await provider.generate_response([LLMMessage(role="user", content="Hi")])


@pytest.mark.asyncio
async def test_groq_provider_api_error() -> None:
    """Verifies that non-200 responses raise LLMProviderError."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=500, json={"error": {"message": "Internal Groq Error"}})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        provider = GroqProvider(
            api_key=SecretStr("gsk_key"),
            http_client=http_client,
        )
        with pytest.raises(LLMProviderError) as exc_info:
            await provider.generate_response([LLMMessage(role="user", content="Hi")])
        assert exc_info.value.status_code == 500
        assert "Internal Groq Error" in str(exc_info.value)
