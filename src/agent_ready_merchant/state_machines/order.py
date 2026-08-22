"""Authoritative State Machine for Order.

Adheres strictly to docs/state-machines.md §3 and INV-STA-01 / INV-STA-02.
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.db.concurrency import update_with_version_check
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.order import Order
from agent_ready_merchant.state_machines.base import (
    InvalidStateTransitionError,
    TerminalStateError,
    TransitionResult,
)


class OrderStateMachine:
    """State machine governing Order lifecycle progression."""

    ALLOWED_TRANSITIONS: dict[str, set[str]] = {
        "CREATED": {"PENDING_PAYMENT", "CANCELLED"},
        "PENDING_PAYMENT": {"PAYMENT_PROCESSING", "CANCELLED", "EXPIRED"},
        "PAYMENT_PROCESSING": {"PAID", "PAYMENT_FAILED"},
        "PAYMENT_FAILED": {"PENDING_PAYMENT", "EXPIRED", "CANCELLED"},
        "PAID": {"FULFILLMENT_PENDING", "REFUNDED"},
        "FULFILLMENT_PENDING": {"COMPLETED", "REFUNDED"},
        "COMPLETED": set(),  # Terminal
        "CANCELLED": set(),  # Terminal
        "EXPIRED": set(),  # Terminal
        "REFUNDED": set(),  # Terminal
    }

    TERMINAL_STATES: set[str] = {"COMPLETED", "CANCELLED", "EXPIRED", "REFUNDED"}

    @classmethod
    def validate_transition(cls, order: Order, target_state: str) -> None:
        """Validates whether transitioning order.status to target_state is legal.

        Raises:
            TerminalStateError: If current state is terminal.
            InvalidStateTransitionError: If transition is not allowed.
        """
        current_state = order.status

        if current_state in cls.TERMINAL_STATES:
            raise TerminalStateError(
                entity_name="Order",
                entity_id=order.id,
                current_state=current_state,
            )

        allowed = cls.ALLOWED_TRANSITIONS.get(current_state, set())
        if target_state not in allowed:
            raise InvalidStateTransitionError(
                entity_name="Order",
                entity_id=order.id,
                current_state=current_state,
                target_state=target_state,
                reason=f"Valid next states are {sorted(allowed) if allowed else 'none (terminal)'}",
            )

    @classmethod
    async def transition(
        cls,
        session: AsyncSession,
        order: Order,
        target_state: str,
        expected_version: int,
        actor_type: str = "SYSTEM",
        reason: str | None = None,
        additional_updates: dict[str, Any] | None = None,
    ) -> TransitionResult[Order]:
        """Atomically validates, executes version check, updates state, and logs audit event."""
        cls.validate_transition(order, target_state)

        from_state = order.status
        update_payload: dict[str, Any] = {"status": target_state}
        if additional_updates:
            update_payload.update(additional_updates)

        new_version = await update_with_version_check(
            session=session,
            model_class=Order,
            entity_id=order.id,
            expected_version=expected_version,
            values=update_payload,
        )

        order.status = target_state
        order.version = new_version
        if additional_updates:
            for k, v in additional_updates.items():
                setattr(order, k, v)

        audit_payload = {
            "entity": "Order",
            "entity_id": str(order.id),
            "from_state": from_state,
            "to_state": target_state,
            "version": new_version,
            "reason": reason,
        }

        audit_event = AuditEvent(
            merchant_id=order.merchant_id,
            session_id=None,
            actor_type=actor_type,
            event_type=f"ORDER_TRANSITION_{target_state}",
            payload=audit_payload,
            event_hash=f"hash_order_{order.id}_{new_version}",
        )
        session.add(audit_event)
        await session.flush()

        return TransitionResult(
            entity=order,
            from_state=from_state,
            to_state=target_state,
            version=new_version,
            audit_payload=audit_payload,
        )
