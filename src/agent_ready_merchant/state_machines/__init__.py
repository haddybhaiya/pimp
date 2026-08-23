"""Authoritative State Machines package.

Exports all 6 finite state machines governing entity lifecycles.
"""

from agent_ready_merchant.state_machines.agent_run import AgentRunStateMachine
from agent_ready_merchant.state_machines.base import (
    InvalidStateTransitionError,
    StateMachineError,
    TerminalStateError,
    TransitionResult,
)
from agent_ready_merchant.state_machines.buyer_intent import BuyerIntentStateMachine
from agent_ready_merchant.state_machines.order import OrderStateMachine
from agent_ready_merchant.state_machines.payment_attempt import PaymentAttemptStateMachine
from agent_ready_merchant.state_machines.price_quote import PriceQuoteStateMachine
from agent_ready_merchant.state_machines.transaction import TransactionStateMachine

__all__ = [
    "StateMachineError",
    "InvalidStateTransitionError",
    "TerminalStateError",
    "TransitionResult",
    "BuyerIntentStateMachine",
    "PriceQuoteStateMachine",
    "OrderStateMachine",
    "PaymentAttemptStateMachine",
    "TransactionStateMachine",
    "AgentRunStateMachine",
]
