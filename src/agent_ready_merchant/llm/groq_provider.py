"""Groq LLM provider adapter using OpenAI-compatible chat completion endpoints."""

import logging
from typing import Any

import httpx
from pydantic import SecretStr

from agent_ready_merchant.llm.base import BaseLLMProvider, LLMMessage, LLMResponse
from agent_ready_merchant.llm.exceptions import (
    LLMAuthenticationError,
    LLMProviderError,
    LLMTimeoutError,
)

logger = logging.getLogger("agent_ready_merchant.llm.groq")

_STRICT_JSON_SCHEMA_MODELS = frozenset({"openai/gpt-oss-20b", "openai/gpt-oss-120b"})


class GroqProvider(BaseLLMProvider):
    """Groq API provider implementing BaseLLMProvider."""

    def __init__(
        self,
        api_key: SecretStr | str,
        model: str = "llama-3.3-70b-versatile",
        base_url: str = "https://api.groq.com/openai/v1",
        http_client: httpx.AsyncClient | None = None,
        response_schema: dict[str, Any] | None = None,
    ) -> None:
        self._api_key = api_key.get_secret_value() if isinstance(api_key, SecretStr) else api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self._custom_client = http_client
        self._response_schema = response_schema

    def _response_format(self) -> dict[str, Any]:
        """Returns the strongest supported JSON constraint for the configured model."""
        if self._response_schema is not None and self.model in _STRICT_JSON_SCHEMA_MODELS:
            return {
                "type": "json_schema",
                "json_schema": {
                    "name": "merchant_agent_analysis",
                    "strict": True,
                    "schema": self._response_schema,
                },
            }
        # JSON object mode makes all existing Groq-backed structured callers
        # syntactically safe even when a model lacks strict schema support.
        return {"type": "json_object"}

    async def generate_response(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.2,
        max_tokens: int = 2048,
        timeout: float = 15.0,
    ) -> LLMResponse:
        """Sends chat messages to Groq API and parses the response."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": self._response_format(),
        }

        async def _send(client: httpx.AsyncClient) -> httpx.Response:
            return await client.post(url, headers=headers, json=payload, timeout=timeout)

        try:
            if self._custom_client:
                response = await _send(self._custom_client)
            else:
                async with httpx.AsyncClient() as client:
                    response = await _send(client)

            if response.status_code == 401:
                logger.error("Groq API authentication failed (HTTP 401)")
                raise LLMAuthenticationError("Invalid Groq API key")

            if response.is_error:
                error_detail = response.text
                try:
                    err_json = response.json()
                    error_detail = err_json.get("error", {}).get("message", response.text)
                except Exception as parse_exc:
                    logger.debug("Failed parsing Groq error JSON: %s", parse_exc)

                logger.warning(
                    "Groq API returned error status %d: %s",
                    response.status_code,
                    error_detail,
                )
                raise LLMProviderError(status_code=response.status_code, message=error_detail)

            data = response.json()
            choice = data.get("choices", [{}])[0]
            content = choice.get("message", {}).get("content") or ""
            usage_data = data.get("usage", {})
            usage = {
                "prompt_tokens": usage_data.get("prompt_tokens", 0),
                "completion_tokens": usage_data.get("completion_tokens", 0),
                "total_tokens": usage_data.get("total_tokens", 0),
            }

            return LLMResponse(
                content=content,
                model=data.get("model", self.model),
                usage=usage,
                raw_response=data,
            )

        except httpx.TimeoutException as exc:
            logger.error("Timeout connecting to Groq API after %.1fs", timeout)
            raise LLMTimeoutError(f"Groq API request timed out after {timeout}s") from exc
        except httpx.NetworkError as exc:
            logger.error("Network error communicating with Groq API: %s", exc)
            raise LLMProviderError(
                status_code=503, message=f"Network error connecting to Groq: {exc}"
            ) from exc
