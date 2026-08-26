"""External AI Buyer package for Agent-Ready Merchant.

Exposes:
- AIBuyerClient: Autonomous buyer client communicating strictly through the Commerce Gateway
- BuyerCommerceState: Explicit progression states
- BuyerFailureState: Explicit rejection / failure states
- BuyerFlowResult: Overall outcome structure
"""

from agent_ready_merchant.buyer.client import AIBuyerClient
from agent_ready_merchant.buyer.schemas import (
    BuyerCommerceState,
    BuyerFailureState,
    BuyerFlowContext,
    BuyerFlowResult,
    BuyerFlowStep,
)

__all__ = [
    "AIBuyerClient",
    "BuyerCommerceState",
    "BuyerFailureState",
    "BuyerFlowContext",
    "BuyerFlowResult",
    "BuyerFlowStep",
]
