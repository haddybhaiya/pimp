"""Authoritative State Machine for PriceQuote.

Adheres strictly to docs/state-machines.md §2 and INV-STA-04 (Quote Expiry Enforcement).
"""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.db.concurrency import update_with_version_check
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.quote import PriceQuote
from agent_ready_merchant.state_machines.base import (
    InvalidStateTransitionError,
    TerminalStateError,
    TransitionResult,
)


class PriceQuoteStateMachine:
    """State machine governing PriceQuote lifecycle."""

    ALLOWED_TRANSITIONS: dict[str, set[str]] = {
        "DRAFT": {"PROPOSED", "REJECTED"},
        "PROPOSED": {"NEGOTIATING", "ACCEPTED", "EXPIRED", "SUPERSEDED", "REJECTED"},
        "NEGOTIATING": {"PROPOSED", "REJECTED", "EXPIRED"},
        "ACCEPTED": set(),  # Terminal
        "EXPIRED": set(),  # Terminal
        "SUPERSEDED": set(),  # Terminal
        "REJECTED": set(),  # Terminal
    }

    TERMINAL_STATES: set[str] = {"ACCEPTED", "EXPIRED", "SUPERSEDED", "REJECTED"}

    @classmethod
    def validate_transition(
        cls,
        quote: PriceQuote,
        target_state: str,
        current_time: datetime | None = None,
    ) -> None:
        """Validates whether a transition from quote.status to target_state is legal.

        Raises:
            TerminalStateError: If current state is terminal.
            InvalidStateTransitionError: If transition is not allowed or quote has expired.
        """
        now = current_time or datetime.now(UTC)
        current_state = quote.status

        if current_state in cls.TERMINAL_STATES:
            raise TerminalStateError(
                entity_name="PriceQuote",
                entity_id=quote.id,
                current_state=current_state,
            )

        allowed = cls.ALLOWED_TRANSITIONS.get(current_state, set())
        if target_state not in allowed:
            raise InvalidStateTransitionError(
                entity_name="PriceQuote",
                entity_id=quote.id,
                current_state=current_state,
                target_state=target_state,
                reason=f"Valid next states are {sorted(allowed) if allowed else 'none (terminal)'}",
            )

        # Enforce expiry invariant: quote cannot be accepted or negotiated if now > expires_at
        if target_state in {"ACCEPTED", "NEGOTIATING"}:
            if now > quote.expires_at:
                raise InvalidStateTransitionError(
                    entity_name="PriceQuote",
                    entity_id=quote.id,
                    current_state=current_state,
                    target_state=target_state,
                    reason=(
                        f"Quote expired at {quote.expires_at.isoformat()}, "
                        f"current time {now.isoformat()}"
                    ),
                )

    @classmethod
    async def transition(
        cls,
        session: AsyncSession,
        quote: PriceQuote,
        target_state: str,
        expected_version: int,
        actor_type: str = "SYSTEM",
        reason: str | None = None,
        additional_updates: dict[str, Any] | None = None,
        current_time: datetime | None = None,
    ) -> TransitionResult[PriceQuote]:
        """Atomically validates, executes version check, and writes audit event."""
        cls.validate_transition(quote, target_state, current_time=current_time)

        from_state = quote.status
        update_payload: dict[str, Any] = {"status": target_state}
        if additional_updates:
            update_payload.update(additional_updates)

        # Apply version-checked atomic update
        new_version = await update_with_version_check(
            session=session,
            model_class=PriceQuote,
            entity_id=quote.id,
            expected_version=expected_version,
            values=update_payload,
        )

        quote.status = target_state
        quote.version = new_version
        if additional_updates:
            for k, v in additional_updates.items():
                setattr(quote, k, v)

        audit_payload = {
            "entity": "PriceQuote",
            "entity_id": str(quote.id),
            "from_state": from_state,
            "to_state": target_state,
            "version": new_version,
            "reason": reason,
        }

        # Append immutable audit event
        audit_event = AuditEvent(
            merchant_id=quote.merchant_id,
            session_id=quote.session_id,
            actor_type=actor_type,
            event_type=f"PRICE_QUOTE_TRANSITION_{target_state}",
            payload=audit_payload,
            event_hash=f"hash_quote_{quote.id}_{new_version}",
        )
        session.add(audit_event)
        await session.flush()

        return TransitionResult(
            entity=quote,
            from_state=from_state,
            to_state=target_state,
            version=new_version,
            audit_payload=audit_payload,
        )
