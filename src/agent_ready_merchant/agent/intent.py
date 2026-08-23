"""Structured Intent Protocol parsing and validation for LLM outputs.

Adheres strictly to docs/agent-contract.md §3 and zero-unstructured-execution doctrine.
"""

import json
import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class MalformedIntentError(Exception):
    """Raised when LLM output violates JSON syntax or the StructuredIntent schema."""

    def __init__(self, raw_content: str, details: str) -> None:
        self.raw_content = raw_content
        self.details = details
        super().__init__(f"Malformed LLM output: {details}")


class ToolCallProposal(BaseModel):
    """Proposal for a tool invocation emitted by the untrusted model."""

    model_config = ConfigDict(extra="forbid")

    tool_name: str = Field(
        ..., min_length=1, max_length=100, description="Name of the registered tool"
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Typed parameters for the tool"
    )


class StructuredIntent(BaseModel):
    """Canonical structured intent contract returned by model generation."""

    model_config = ConfigDict(extra="forbid")

    thought_process: str = Field(..., description="Internal chain of thought rationale")
    intent: str = Field(
        ..., min_length=1, max_length=50, description="High-level classified intent"
    )
    tool_call: ToolCallProposal | None = Field(
        default=None, description="Optional tool call proposal"
    )
    buyer_facing_message: str | None = Field(
        default=None, description="Customer-facing conversational text"
    )


def _extract_json_substring(text: str) -> str:
    """Extracts a JSON object from text, stripping markdown fences if present."""
    trimmed = text.strip()
    # If wrapped in markdown code fence
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", trimmed, re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()

    # If already starting and ending with braces
    if trimmed.startswith("{") and trimmed.endswith("}"):
        return trimmed

    # Look for first { and last }
    first_brace = trimmed.find("{")
    last_brace = trimmed.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return trimmed[first_brace : last_brace + 1]

    return trimmed


def parse_structured_intent(raw_text: str) -> StructuredIntent:
    """Parses and strictly validates raw model text into StructuredIntent.

    Raises MalformedIntentError on invalid JSON, unexpected fields, or schema violations.
    """
    if not raw_text or not raw_text.strip():
        raise MalformedIntentError(raw_text, "Empty LLM output")

    json_str = _extract_json_substring(raw_text)

    try:
        data = json.loads(json_str)
    except Exception as exc:
        raise MalformedIntentError(raw_text, f"Invalid JSON syntax: {exc}") from exc

    if not isinstance(data, dict):
        raise MalformedIntentError(raw_text, "LLM output must be a JSON object")

    try:
        return StructuredIntent.model_validate(data)
    except ValidationError as exc:
        raise MalformedIntentError(raw_text, f"Schema validation failed: {exc}") from exc
