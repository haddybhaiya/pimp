"""Authoritative State Machine for BuyerIntent.

Adheres strictly to docs/state-machines.md §1 and docs/domain-model.md §2.5.
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.db.concurrency import update_with_version_check
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.intent import BuyerIntent
from agent_ready_merchant.models.session import BuyerAgentSession
from agent_ready_merchant.state_machines.base import (
    InvalidStateTransitionError,
    TerminalStateError,
    TransitionResult,
)


class BuyerIntentStateMachine:
    """State machine governing BuyerIntent validation status."""

    ALLOWED_TRANSITIONS: dict[str, set[str]] = {
        "PENDING": {"VALIDATED", "REJECTED", "MALFORMED"},
        "VALIDATED": set(),  # Terminal
        "REJECTED": set(),  # Terminal
        "MALFORMED": set(),  # Terminal
    }

    TERMINAL_STATES: set[str] = {"VALIDATED", "REJECTED", "MALFORMED"}
    MUTABLE_FIELDS: set[str] = {
        "raw_query",
        "extracted_intent",
        "extracted_entities",
        "confidence_score",
    }

    @classmethod
    def validate_transition(cls, intent: BuyerIntent, target_state: str) -> None:
        """Validates whether transitioning intent.validation_status to target_state is legal."""
        current_state = intent.validation_status

        if current_state in cls.TERMINAL_STATES:
            raise TerminalStateError(
                entity_name="BuyerIntent",
                entity_id=intent.id,
                current_state=current_state,
            )

        allowed = cls.ALLOWED_TRANSITIONS.get(current_state, set())
        if target_state not in allowed:
            raise InvalidStateTransitionError(
                entity_name="BuyerIntent",
                entity_id=intent.id,
                current_state=current_state,
                target_state=target_state,
                reason=f"Valid next states are {sorted(allowed) if allowed else 'none (terminal)'}",
            )

    @classmethod
    async def transition(
        cls,
        session: AsyncSession,
        intent: BuyerIntent,
        target_state: str,
        expected_version: int | None = None,
        actor_type: str = "SYSTEM",
        reason: str | None = None,
        additional_updates: dict[str, Any] | None = None,
    ) -> TransitionResult[BuyerIntent]:
        """Validates, atomically transitions status with version check, and writes audit event."""
        cls.validate_transition(intent, target_state)

        from_state = intent.validation_status
        updates: dict[str, Any] = {"validation_status": target_state}

        if additional_updates:
            for k, v in additional_updates.items():
                if k not in cls.MUTABLE_FIELDS:
                    raise ValueError(
                        f"Field '{k}' is protected and cannot be "
                        "modified during BuyerIntent transition"
                    )
                updates[k] = v

        version_to_check = expected_version or intent.version
        new_version = await update_with_version_check(
            session=session,
            model_class=BuyerIntent,
            entity_id=intent.id,
            expected_version=version_to_check,
            values=updates,
        )

        intent.validation_status = target_state
        intent.version = new_version
        if additional_updates:
            for k, v in additional_updates.items():
                if k in cls.MUTABLE_FIELDS:
                    setattr(intent, k, v)

        # Load session merchant_id safely
        if intent.session is not None:
            merchant_id = intent.session.merchant_id
        else:
            session_stmt = select(BuyerAgentSession.merchant_id).where(
                BuyerAgentSession.id == intent.session_id
            )
            merchant_id = (await session.execute(session_stmt)).scalar_one()

        audit_payload = {
            "entity": "BuyerIntent",
            "entity_id": str(intent.id),
            "session_id": str(intent.session_id),
            "extracted_intent": intent.extracted_intent,
            "from_state": from_state,
            "to_state": target_state,
            "reason": reason,
        }

        await AuditEvent.create_event(
            session=session,
            merchant_id=merchant_id,
            session_id=intent.session_id,
            actor_type=actor_type,
            event_type=f"INTENT_VALIDATION_{target_state}",
            payload=audit_payload,
        )

        return TransitionResult(
            entity=intent,
            from_state=from_state,
            to_state=target_state,
            version=new_version,
            audit_payload=audit_payload,
        )
