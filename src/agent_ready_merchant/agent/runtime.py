"""Bounded Agent Runtime coordinating LLM reasoning, structured intent, and the Tool Gateway.

Adheres strictly to docs/agent-contract.md §4, §5, §6 and INV-AGY-02 / INV-AGY-04.
"""

import json
import logging
from typing import Any, Literal

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.agent.intent import (
    MalformedIntentError,
    StructuredIntent,
    parse_structured_intent,
)
from agent_ready_merchant.agent.prompt import (
    build_system_prompt,
    format_untrusted_buyer_message,
)
from agent_ready_merchant.llm.base import BaseLLMProvider, LLMMessage
from agent_ready_merchant.llm.exceptions import LLMError
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.tools.base import GatewayContext
from agent_ready_merchant.tools.gateway import ToolGateway

logger = logging.getLogger("agent_ready_merchant.agent.runtime")


class AgentRunResult(BaseModel):
    """Result of a bounded agent interaction turn."""

    status: Literal["COMPLETED", "STEP_LIMIT_EXCEEDED", "MALFORMED_OUTPUT", "ERROR"] = Field(...)
    buyer_message: str = Field(...)
    steps_taken: int = Field(...)
    tool_calls_executed: list[dict[str, Any]] = Field(default_factory=list)
    structured_intents: list[StructuredIntent] = Field(default_factory=list)


class AgentRuntime:
    """Deterministic orchestrator executing bounded multi-step reasoning turns."""

    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        tool_gateway: ToolGateway | None = None,
    ) -> None:
        self.llm = llm_provider
        self.gateway = tool_gateway or ToolGateway()

    async def run_turn(
        self,
        session: AsyncSession,
        user_message: str,
        context: GatewayContext,
        merchant_name: str = "Demo Store",
        max_steps: int = 5,
        timeout_seconds: float = 15.0,
    ) -> AgentRunResult:
        """Executes a single conversational turn with max_steps bounding and strict tool gating."""
        available_tools = list(self.gateway._tools.keys())
        system_prompt = build_system_prompt(
            merchant_name=merchant_name,
            autonomy_level=context.autonomy_level,
            available_tools=available_tools,
        )

        messages: list[LLMMessage] = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=format_untrusted_buyer_message(user_message)),
        ]

        steps_taken = 0
        malformed_retries = 0
        max_malformed_retries = 2
        tool_calls_log: list[dict[str, Any]] = []
        intents_log: list[StructuredIntent] = []

        while steps_taken < max_steps:
            steps_taken += 1

            # 1. LLM Generation
            try:
                llm_res = await self.llm.generate_response(
                    messages=messages,
                    timeout=timeout_seconds,
                )
            except LLMError as exc:
                logger.error("LLM generation failure during turn: %s", exc)
                return AgentRunResult(
                    status="ERROR",
                    buyer_message="I encountered an unexpected service error. Please try again.",
                    steps_taken=steps_taken,
                    tool_calls_executed=tool_calls_log,
                    structured_intents=intents_log,
                )

            # 2. Parse & Validate Structured Intent
            try:
                intent = parse_structured_intent(llm_res.content)
                intents_log.append(intent)
            except MalformedIntentError as exc:
                malformed_retries += 1
                logger.warning(
                    "Malformed LLM output (attempt %d/%d): %s",
                    malformed_retries,
                    max_malformed_retries,
                    exc,
                )
                if malformed_retries <= max_malformed_retries:
                    # Provide structured feedback to model to fix schema
                    messages.append(
                        LLMMessage(
                            role="user",
                            content=(
                                f"Your previous output was invalid: {exc.details}. "
                                "Output ONLY valid JSON matching the schema."
                            ),
                        )
                    )
                    continue
                else:
                    # Exceeded malformed retries: Terminate run safely
                    return AgentRunResult(
                        status="MALFORMED_OUTPUT",
                        buyer_message="I'm having trouble formulating a response right now.",
                        steps_taken=steps_taken,
                        tool_calls_executed=tool_calls_log,
                        structured_intents=intents_log,
                    )

            # 3. Process Tool Call if proposed
            if intent.tool_call:
                tool_res = await self.gateway.execute_tool_call(
                    session=session,
                    proposal=intent.tool_call,
                    context=context,
                )
                tool_calls_log.append(
                    {
                        "step": steps_taken,
                        "tool_name": intent.tool_call.tool_name,
                        "parameters": intent.tool_call.parameters,
                        "status": tool_res.status,
                        "data": tool_res.data,
                        "error": tool_res.error,
                    }
                )

                # Feed tool result back to model context
                tool_output_str = json.dumps(
                    {"status": tool_res.status, "data": tool_res.data, "error": tool_res.error}
                )
                messages.append(
                    LLMMessage(
                        role="assistant",
                        content=json.dumps(intent.model_dump()),
                    )
                )
                messages.append(
                    LLMMessage(
                        role="tool",
                        content=tool_output_str,
                    )
                )

                # If the model already provided a final buyer message and finished, we can complete
                if intent.buyer_facing_message and not intent.tool_call:
                    break

            else:
                # No tool call proposed: Return final buyer-facing message
                buyer_msg = (
                    intent.buyer_facing_message or "How may I help you with our catalog today?"
                )
                await self._record_run_audit(session, context, steps_taken, "COMPLETED")
                return AgentRunResult(
                    status="COMPLETED",
                    buyer_message=buyer_msg,
                    steps_taken=steps_taken,
                    tool_calls_executed=tool_calls_log,
                    structured_intents=intents_log,
                )

        # Reached Step Limit
        logger.warning("Agent run reached step limit (%d)", max_steps)
        await self._record_run_audit(session, context, steps_taken, "STEP_LIMIT_EXCEEDED")
        fallback_msg = (
            intents_log[-1].buyer_facing_message
            if (intents_log and intents_log[-1].buyer_facing_message)
            else "I have reached the processing limit. How would you like to proceed?"
        )
        return AgentRunResult(
            status="STEP_LIMIT_EXCEEDED",
            buyer_message=fallback_msg,
            steps_taken=steps_taken,
            tool_calls_executed=tool_calls_log,
            structured_intents=intents_log,
        )

    async def _record_run_audit(
        self,
        session: AsyncSession,
        context: GatewayContext,
        steps: int,
        status: str,
    ) -> None:
        """Records agent run completion audit."""
        audit = AuditEvent(
            merchant_id=context.merchant_id,
            session_id=context.session_id,
            actor_type="BUYER_AGENT",
            event_type="AGENT_RUN_COMPLETED",
            payload={"steps_taken": steps, "status": status},
            event_hash=f"agent_run_{context.session_id}_{steps}_{status}",
        )
        session.add(audit)
        await session.flush()
