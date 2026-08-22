"""Base state machine definitions, exceptions, and audit interfaces.

Adheres strictly to INV-STA-01 (Legal State Transitions Only), INV-STA-02 (Optimistic Locking),
and INV-STA-05 (Immutable Financial Ledger).
"""

import uuid
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from agent_ready_merchant.db.base import Base

T = TypeVar("T", bound=Base)


class StateMachineError(Exception):
    """Base exception for all state machine transition errors."""

    pass


class InvalidStateTransitionError(StateMachineError):
    """Raised when an illegal state transition is attempted."""

    def __init__(
        self,
        entity_name: str,
        entity_id: uuid.UUID | str,
        current_state: str,
        target_state: str,
        reason: str | None = None,
    ) -> None:
        self.entity_name = entity_name
        self.entity_id = entity_id
        self.current_state = current_state
        self.target_state = target_state
        self.reason = reason
        detail = f": {reason}" if reason else ""
        super().__init__(
            f"Illegal state transition on {entity_name}(id={entity_id}) "
            f"from '{current_state}' to '{target_state}'{detail}"
        )


class TerminalStateError(StateMachineError):
    """Raised when an attempt is made to transition out of a terminal state."""

    def __init__(
        self,
        entity_name: str,
        entity_id: uuid.UUID | str,
        current_state: str,
    ) -> None:
        self.entity_name = entity_name
        self.entity_id = entity_id
        self.current_state = current_state
        super().__init__(
            f"Cannot transition out of terminal state '{current_state}' "
            f"on {entity_name}(id={entity_id})"
        )


@dataclass(frozen=True)
class TransitionResult(Generic[T]):
    """Immutable result of a successful state transition."""

    entity: T
    from_state: str
    to_state: str
    version: int
    audit_payload: dict[str, Any]
