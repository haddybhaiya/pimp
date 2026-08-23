"""Authoritative State Machine for TransactionRecord.

Adheres strictly to docs/state-machines.md §1 and INV-STA-05 (Immutable Financial Ledger).
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.db.concurrency import update_with_version_check
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
    MUTABLE_FIELDS: set[str] = {"settlement_ref"}

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
        expected_version: int | None = None,
        actor_type: str = "SYSTEM",
        reason: str | None = None,
        additional_updates: dict[str, Any] | None = None,
    ) -> TransitionResult[TransactionRecord]:
        """Validates, atomically transitions state with version check, and writes audit event."""
        cls.validate_transition(tx, target_state)

        from_state = tx.status
        updates: dict[str, Any] = {"status": target_state}

        if additional_updates:
            for k, v in additional_updates.items():
                if k not in cls.MUTABLE_FIELDS:
                    raise ValueError(
                        f"Field '{k}' is protected and cannot be "
                        "modified during TransactionRecord transition"
                    )
                updates[k] = v

        version_to_check = expected_version or tx.version
        new_version = await update_with_version_check(
            session=session,
            model_class=TransactionRecord,
            entity_id=tx.id,
            expected_version=version_to_check,
            values=updates,
        )

        tx.status = target_state
        tx.version = new_version
        if additional_updates:
            for k, v in additional_updates.items():
                if k in cls.MUTABLE_FIELDS:
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

        await AuditEvent.create_event(
            session=session,
            merchant_id=tx.merchant_id,
            session_id=None,
            actor_type=actor_type,
            event_type=f"TX_TRANSITION_{target_state}",
            payload=audit_payload,
        )

        return TransitionResult(
            entity=tx,
            from_state=from_state,
            to_state=target_state,
            version=new_version,
            audit_payload=audit_payload,
        )
