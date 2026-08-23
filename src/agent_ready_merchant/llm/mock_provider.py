"""Deterministic mock LLM provider for isolated testing."""

from collections.abc import Callable

from agent_ready_merchant.llm.base import BaseLLMProvider, LLMMessage, LLMResponse


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM provider that returns predetermined responses or calls a custom handler."""

    def __init__(
        self,
        responses: list[str] | None = None,
        handler: Callable[[list[LLMMessage]], str] | None = None,
        model: str = "mock-llm-model",
    ) -> None:
        self.responses = list(responses or [])
        self.handler = handler
        self.model = model
        self.call_history: list[list[LLMMessage]] = []

    async def generate_response(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.2,
        max_tokens: int = 2048,
        timeout: float = 15.0,
    ) -> LLMResponse:
        self.call_history.append(messages)

        if self.handler:
            content = self.handler(messages)
        elif self.responses:
            content = self.responses.pop(0)
        else:
            content = "{}"

        return LLMResponse(
            content=content,
            model=self.model,
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        )
