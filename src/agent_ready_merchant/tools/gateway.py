"""Tool Gateway enforcing capability checks, schema validation, policy, and audit trails.

Adheres strictly to docs/tool-contract.md §1 and the mandatory Action Gateway pipeline.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.tools.base import BaseTool, GatewayContext
from agent_ready_merchant.tools.handlers import (
    CheckPaymentStatusTool,
    CreateOrderTool,
    DiscoverCatalogTool,
    GetProductDetailsTool,
    NegotiateQuoteTool,
    RequestPriceQuoteTool,
)
from agent_ready_merchant.tools.models import ToolExecutionResult

if TYPE_CHECKING:
    from agent_ready_merchant.agent.intent import ToolCallProposal

logger = logging.getLogger("agent_ready_merchant.gateway")


class ToolGateway:
    """Server-authoritative gateway through which all model tool proposals
    execute.
    """

    def __init__(self, custom_tools: list[BaseTool] | None = None) -> None:
        self._tools: dict[str, BaseTool] = {}
        default_tools: list[BaseTool] = [
            DiscoverCatalogTool(),
            GetProductDetailsTool(),
            RequestPriceQuoteTool(),
            NegotiateQuoteTool(),
            CreateOrderTool(),
            CheckPaymentStatusTool(),
        ]
        for tool in custom_tools or default_tools:
            self.register_tool(tool)

    def register_tool(self, tool: BaseTool) -> None:
        """Registers a tool into the gateway catalog."""
        self._tools[tool.name] = tool

    def get_tool(self, tool_name: str) -> BaseTool | None:
        """Retrieves a registered tool by name."""
        return self._tools.get(tool_name)

    async def execute_tool_call(
        self,
        session: AsyncSession,
        proposal: ToolCallProposal,
        context: GatewayContext,
    ) -> ToolExecutionResult:
        """Executes a tool proposal through the validation and security
        pipeline.
        """
        tool_name = proposal.tool_name

        # 1. Tool Existence Check
        tool = self.get_tool(tool_name)
        if not tool:
            logger.warning("Agent attempted unknown tool: '%s'", tool_name)
            res = ToolExecutionResult(
                status="ERROR",
                tool_name=tool_name,
                error={
                    "code": "UNKNOWN_TOOL",
                    "message": f"Tool '{tool_name}' is not registered.",
                    "retryable": False,
                },
            )
            await self._record_audit(session, proposal, res, context)
            return res

        # 2. Capability / Authorization Check
        if not context.has_capability(tool.required_capability):
            logger.warning(
                "Capability denied for tool '%s': required '%s'",
                tool_name,
                tool.required_capability,
            )
            res = ToolExecutionResult(
                status="REJECTED",
                tool_name=tool_name,
                error={
                    "code": "CAPABILITY_DENIED",
                    "message": f"Session missing required capability '{tool.required_capability}'.",
                    "retryable": False,
                },
            )
            await self._record_audit(session, proposal, res, context)
            return res

        # 3. Parameter Schema Validation
        try:
            validated_params = tool.param_schema.model_validate(proposal.parameters)
        except ValidationError as exc:
            logger.warning("Invalid tool arguments for '%s': %s", tool_name, exc)
            res = ToolExecutionResult(
                status="ERROR",
                tool_name=tool_name,
                error={
                    "code": "INVALID_TOOL_ARGUMENTS",
                    "message": f"Schema validation error: {exc}",
                    "retryable": True,
                },
            )
            await self._record_audit(session, proposal, res, context)
            return res

        # 4. Deterministic Execution
        try:
            raw_output = await tool.execute(session, validated_params, context)

            if "error" in raw_output:
                res = ToolExecutionResult(
                    status="REJECTED",
                    tool_name=tool_name,
                    error=raw_output["error"],
                )
            else:
                res = ToolExecutionResult(
                    status="SUCCESS",
                    tool_name=tool_name,
                    data=raw_output,
                )

            await self._record_audit(session, proposal, res, context)
            return res

        except Exception as exc:
            logger.error("Unexpected error executing tool '%s': %s", tool_name, exc, exc_info=True)
            res = ToolExecutionResult(
                status="ERROR",
                tool_name=tool_name,
                error={
                    "code": "TOOL_EXECUTION_ERROR",
                    "message": f"Internal execution error: {exc}",
                    "retryable": False,
                },
            )
            await self._record_audit(session, proposal, res, context)
            return res

    async def _record_audit(
        self,
        session: AsyncSession,
        proposal: ToolCallProposal,
        result: ToolExecutionResult,
        context: GatewayContext,
    ) -> None:
        """Appends an immutable audit log entry for every tool gateway execution."""
        audit_payload: dict[str, Any] = {
            "tool_name": proposal.tool_name,
            "parameters": proposal.parameters,
            "result_status": result.status,
            "result_data": result.data,
            "result_error": result.error,
        }
        await AuditEvent.create_event(
            session=session,
            merchant_id=context.merchant_id,
            session_id=context.session_id,
            actor_type="BUYER_AGENT",
            event_type="TOOL_EXECUTION",
            payload=audit_payload,
        )
