"""Authoritative State Machine for BuyerIntent.

Adheres strictly to docs/state-machines.md §1 and docs/domain-model.md §2.5.
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.intent import BuyerIntent
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
        actor_type: str = "SYSTEM",
        reason: str | None = None,
        additional_updates: dict[str, Any] | None = None,
    ) -> TransitionResult[BuyerIntent]:
        """Validates, transitions validation status, and writes audit event."""
        cls.validate_transition(intent, target_state)

        from_state = intent.validation_status
        intent.validation_status = target_state
        if additional_updates:
            for k, v in additional_updates.items():
                setattr(intent, k, v)

        audit_payload = {
            "entity": "BuyerIntent",
            "entity_id": str(intent.id),
            "session_id": str(intent.session_id),
            "extracted_intent": intent.extracted_intent,
            "from_state": from_state,
            "to_state": target_state,
            "reason": reason,
        }

        merchant_id = intent.session.merchant_id if intent.session else intent.session_id
        audit_event = AuditEvent(
            merchant_id=merchant_id,
            session_id=intent.session_id,
            actor_type=actor_type,
            event_type=f"INTENT_VALIDATION_{target_state}",
            payload=audit_payload,
            event_hash=f"hash_intent_{intent.id}_{target_state}",
        )
        session.add(audit_event)
        await session.flush()

        return TransitionResult(
            entity=intent,
            from_state=from_state,
            to_state=target_state,
            version=1,
            audit_payload=audit_payload,
        )
