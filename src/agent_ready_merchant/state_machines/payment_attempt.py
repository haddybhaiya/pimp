"""Authoritative State Machine for PaymentAttempt.

Adheres strictly to docs/state-machines.md §4 and INV-FIN-05 (Server-Authoritative Settlement).
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.db.concurrency import update_with_version_check
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.order import Order
from agent_ready_merchant.models.payment import PaymentAttempt
from agent_ready_merchant.state_machines.base import (
    InvalidStateTransitionError,
    TerminalStateError,
    TransitionResult,
)


class PaymentAttemptStateMachine:
    """State machine governing PaymentAttempt lifecycle."""

    ALLOWED_TRANSITIONS: dict[str, set[str]] = {
        "INITIATED": {"ORDER_CREATED", "FAILED", "TIMED_OUT"},
        "ORDER_CREATED": {"PAYMENT_PENDING", "AUTHORIZED", "CAPTURED", "FAILED", "TIMED_OUT"},
        "PAYMENT_PENDING": {"AUTHORIZED", "CAPTURED", "FAILED", "TIMED_OUT"},
        "AUTHORIZED": {"CAPTURED", "FAILED"},
        "CAPTURED": {"REFUNDED"},
        "FAILED": set(),  # Terminal
        "REFUNDED": set(),  # Terminal
        "TIMED_OUT": set(),  # Terminal
    }

    TERMINAL_STATES: set[str] = {"FAILED", "REFUNDED", "TIMED_OUT"}
    MUTABLE_FIELDS: set[str] = {
        "payment_method",
        "error_code",
        "error_description",
        "webhook_payload",
    }

    @classmethod
    def validate_transition(cls, payment: PaymentAttempt, target_state: str) -> None:
        """Validates whether transitioning payment.status to target_state is legal."""
        current_state = payment.status

        if current_state in cls.TERMINAL_STATES:
            raise TerminalStateError(
                entity_name="PaymentAttempt",
                entity_id=payment.id,
                current_state=current_state,
            )

        allowed = cls.ALLOWED_TRANSITIONS.get(current_state, set())
        if target_state not in allowed:
            raise InvalidStateTransitionError(
                entity_name="PaymentAttempt",
                entity_id=payment.id,
                current_state=current_state,
                target_state=target_state,
                reason=f"Valid next states are {sorted(allowed) if allowed else 'none (terminal)'}",
            )

    @classmethod
    async def transition(
        cls,
        session: AsyncSession,
        payment: PaymentAttempt,
        target_state: str,
        expected_version: int | None = None,
        actor_type: str = "SYSTEM",
        reason: str | None = None,
        additional_updates: dict[str, Any] | None = None,
    ) -> TransitionResult[PaymentAttempt]:
        """Validates, atomically transitions state with version check, and writes audit event."""
        cls.validate_transition(payment, target_state)

        from_state = payment.status
        updates: dict[str, Any] = {"status": target_state}

        if additional_updates:
            for k, v in additional_updates.items():
                if k not in cls.MUTABLE_FIELDS:
                    raise ValueError(
                        f"Field '{k}' is protected and cannot be "
                        "modified during PaymentAttempt transition"
                    )
                updates[k] = v

        version_to_check = expected_version or payment.version
        new_version = await update_with_version_check(
            session=session,
            model_class=PaymentAttempt,
            entity_id=payment.id,
            expected_version=version_to_check,
            values=updates,
        )

        payment.status = target_state
        payment.version = new_version
        if additional_updates:
            for k, v in additional_updates.items():
                if k in cls.MUTABLE_FIELDS:
                    setattr(payment, k, v)

        # Load order merchant_id safely
        if payment.order is not None:
            merchant_id = payment.order.merchant_id
        else:
            order_stmt = select(Order.merchant_id).where(Order.id == payment.order_id)
            merchant_id = (await session.execute(order_stmt)).scalar_one()

        audit_payload = {
            "entity": "PaymentAttempt",
            "entity_id": str(payment.id),
            "order_id": str(payment.order_id),
            "from_state": from_state,
            "to_state": target_state,
            "reason": reason,
        }

        await AuditEvent.create_event(
            session=session,
            merchant_id=merchant_id,
            session_id=None,
            actor_type=actor_type,
            event_type=f"PAYMENT_TRANSITION_{target_state}",
            payload=audit_payload,
        )

        return TransitionResult(
            entity=payment,
            from_state=from_state,
            to_state=target_state,
            version=new_version,
            audit_payload=audit_payload,
        )
