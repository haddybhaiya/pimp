"""Authoritative State Machine for AgentRun.

Adheres strictly to docs/state-machines.md §5 and INV-AGY-04 (Bounded Agent Execution).
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.db.concurrency import update_with_version_check
from agent_ready_merchant.models.agent_run import AgentRun
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.session import BuyerAgentSession
from agent_ready_merchant.state_machines.base import (
    InvalidStateTransitionError,
    TerminalStateError,
    TransitionResult,
)


class AgentRunStateMachine:
    """State machine governing untrusted intelligence agent execution steps."""

    ALLOWED_TRANSITIONS: dict[str, set[str]] = {
        "PENDING": {"RUNNING", "KILLED", "FAILED"},
        "RUNNING": {"AWAITING_TOOL", "COMPLETED", "FAILED", "KILLED"},
        "AWAITING_TOOL": {"EVALUATING_POLICY", "FAILED", "KILLED"},
        "EVALUATING_POLICY": {"EXECUTING_ACTION", "AWAITING_TOOL", "FAILED", "KILLED"},
        "EXECUTING_ACTION": {"RUNNING", "FAILED", "KILLED"},
        "COMPLETED": set(),  # Terminal
        "FAILED": set(),  # Terminal
        "KILLED": set(),  # Terminal
    }

    TERMINAL_STATES: set[str] = {"COMPLETED", "FAILED", "KILLED"}
    MAX_ALLOWED_STEPS: int = 5
    MUTABLE_FIELDS: set[str] = {"step_count", "total_tokens", "error_message"}

    @classmethod
    def validate_transition(cls, run: AgentRun, target_state: str) -> None:
        """Validates whether transitioning run.status to target_state is legal."""
        current_state = run.status

        if current_state in cls.TERMINAL_STATES:
            raise TerminalStateError(
                entity_name="AgentRun",
                entity_id=run.id,
                current_state=current_state,
            )

        allowed = cls.ALLOWED_TRANSITIONS.get(current_state, set())
        if target_state not in allowed:
            raise InvalidStateTransitionError(
                entity_name="AgentRun",
                entity_id=run.id,
                current_state=current_state,
                target_state=target_state,
                reason=f"Valid next states are {sorted(allowed) if allowed else 'none (terminal)'}",
            )

        # Enforce step limit: transition to non-terminal state fails if step_count > 5
        if target_state not in cls.TERMINAL_STATES and run.step_count > cls.MAX_ALLOWED_STEPS:
            raise InvalidStateTransitionError(
                entity_name="AgentRun",
                entity_id=run.id,
                current_state=current_state,
                target_state=target_state,
                reason=f"Step limit exceeded: {run.step_count} > {cls.MAX_ALLOWED_STEPS}",
            )

    @classmethod
    async def transition(
        cls,
        session: AsyncSession,
        run: AgentRun,
        target_state: str,
        expected_version: int | None = None,
        actor_type: str = "SYSTEM",
        reason: str | None = None,
        additional_updates: dict[str, Any] | None = None,
    ) -> TransitionResult[AgentRun]:
        """Validates, atomically transitions state with version check, and writes audit event."""
        cls.validate_transition(run, target_state)

        from_state = run.status
        updates: dict[str, Any] = {"status": target_state}

        if additional_updates:
            for k, v in additional_updates.items():
                if k not in cls.MUTABLE_FIELDS:
                    raise ValueError(
                        f"Field '{k}' is protected and cannot be "
                        "modified during AgentRun transition"
                    )
                updates[k] = v

        version_to_check = expected_version or run.version
        new_version = await update_with_version_check(
            session=session,
            model_class=AgentRun,
            entity_id=run.id,
            expected_version=version_to_check,
            values=updates,
        )

        run.status = target_state
        run.version = new_version
        if additional_updates:
            for k, v in additional_updates.items():
                if k in cls.MUTABLE_FIELDS:
                    setattr(run, k, v)

        # Explicitly load merchant_id from BuyerAgentSession
        if run.session is not None:
            merchant_id = run.session.merchant_id
        else:
            session_stmt = select(BuyerAgentSession.merchant_id).where(
                BuyerAgentSession.id == run.session_id
            )
            merchant_id = (await session.execute(session_stmt)).scalar_one()

        audit_payload = {
            "entity": "AgentRun",
            "entity_id": str(run.id),
            "session_id": str(run.session_id),
            "from_state": from_state,
            "to_state": target_state,
            "step_count": run.step_count,
            "total_tokens": run.total_tokens,
            "reason": reason,
        }

        await AuditEvent.create_event(
            session=session,
            merchant_id=merchant_id,
            session_id=run.session_id,
            actor_type=actor_type,
            event_type=f"AGENT_RUN_TRANSITION_{target_state}",
            payload=audit_payload,
        )

        return TransitionResult(
            entity=run,
            from_state=from_state,
            to_state=target_state,
            version=new_version,
            audit_payload=audit_payload,
        )
