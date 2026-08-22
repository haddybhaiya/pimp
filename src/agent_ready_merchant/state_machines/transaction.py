"""Authoritative State Machine for TransactionRecord.

Adheres strictly to docs/state-machines.md §1 and INV-STA-05 (Immutable Financial Ledger).
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.transaction import TransactionRecord
from agent_ready_merchant.state_machines.base import (
    InvalidStateTransitionError,
    TerminalStateError,
    TransitionResult,
)


class TransactionStateMachine:
    """State machine governing TransactionRecord financial ledger settlement."""

    ALLOWED_TRANSITIONS: dict[str, set[str]] = {
        "UNCOMMITTED": {"COMMITTED", "REVERSED"},
        "COMMITTED": {"REVERSED"},
        "REVERSED": set(),  # Terminal
    }

    TERMINAL_STATES: set[str] = {"REVERSED"}

    @classmethod
    def validate_transition(cls, tx: TransactionRecord, target_state: str) -> None:
        """Validates whether transitioning tx.status to target_state is legal."""
        current_state = tx.status

        if current_state in cls.TERMINAL_STATES:
            raise TerminalStateError(
                entity_name="TransactionRecord",
                entity_id=tx.id,
                current_state=current_state,
            )

        allowed = cls.ALLOWED_TRANSITIONS.get(current_state, set())
        if target_state not in allowed:
            raise InvalidStateTransitionError(
                entity_name="TransactionRecord",
                entity_id=tx.id,
                current_state=current_state,
                target_state=target_state,
                reason=f"Valid next states are {sorted(allowed) if allowed else 'none (terminal)'}",
            )

    @classmethod
    async def transition(
        cls,
        session: AsyncSession,
        tx: TransactionRecord,
        target_state: str,
        actor_type: str = "SYSTEM",
        reason: str | None = None,
        additional_updates: dict[str, Any] | None = None,
    ) -> TransitionResult[TransactionRecord]:
        """Validates, transitions state, and writes audit event."""
        cls.validate_transition(tx, target_state)

        from_state = tx.status
        tx.status = target_state
        if additional_updates:
            for k, v in additional_updates.items():
                setattr(tx, k, v)

        audit_payload = {
            "entity": "TransactionRecord",
            "entity_id": str(tx.id),
            "amount_paise": tx.amount_paise,
            "entry_type": tx.entry_type,
            "from_state": from_state,
            "to_state": target_state,
            "reason": reason,
        }

        audit_event = AuditEvent(
            merchant_id=tx.merchant_id,
            session_id=None,
            actor_type=actor_type,
            event_type=f"TX_TRANSITION_{target_state}",
            payload=audit_payload,
            event_hash=f"hash_tx_{tx.id}_{target_state}",
        )
        session.add(audit_event)
        await session.flush()

        return TransitionResult(
            entity=tx,
            from_state=from_state,
            to_state=target_state,
            version=1,
            audit_payload=audit_payload,
        )
