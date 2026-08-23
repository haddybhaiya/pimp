"""Domain models, contexts, and result types for the Deterministic Policy Engine.

Adheres strictly to docs/policy-model.md and INV-FIN-01 / INV-FIN-02 / INV-FIN-03.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PolicyVerdict(StrEnum):
    """Verdict emitted by deterministic policy evaluation."""

    ALLOW = "ALLOW"
    DENY = "DENY"
    ESCALATE_APPROVAL = "ESCALATE_APPROVAL"


@dataclass(frozen=True)
class PolicyEvaluationResult:
    """Detailed evaluation result emitted by the policy engine."""

    verdict: PolicyVerdict
    rule_code: str
    reason: str
    metadata: dict[str, Any] = field(default_factory=dict)
    required_capability: str | None = None
    required_approval: bool = False

    @property
    def is_allowed(self) -> bool:
        """Returns True if the verdict is explicitly ALLOW."""
        return self.verdict == PolicyVerdict.ALLOW

    @property
    def is_denied(self) -> bool:
        """Returns True if the verdict is explicitly DENY."""
        return self.verdict == PolicyVerdict.DENY

    @property
    def requires_escalation(self) -> bool:
        """Returns True if human-in-the-loop approval is required."""
        return self.verdict == PolicyVerdict.ESCALATE_APPROVAL


@dataclass(frozen=True)
class QuoteItemProposal:
    """Individual line item pricing proposal for policy validation."""

    sku: str
    quantity: int
    unit_base_price_paise: int
    unit_floor_price_paise: int
    proposed_unit_price_paise: int
    is_negotiable: bool = False
    unit_cost_price_paise: int | None = None


@dataclass(frozen=True)
class QuoteProposal:
    """Complete quote proposal submitted for policy validation."""

    items: list[QuoteItemProposal]
    subtotal_paise: int
    discount_paise: int
    shipping_paise: int
    total_paise: int
    shipping_country: str = "IN"
    shipping_postal_code: str | None = None


@dataclass(frozen=True)
class PolicyContext:
    """Authoritative merchant configuration and security context for policy checks."""

    merchant_autonomy_level: int = 1  # 0: Read-Only, 1: Bounded Auto, 2: Supervised HITL
    max_discount_percentage: float = 15.0
    min_margin_percentage: float = 20.0
    max_single_transaction_paise: int = 5_000_000  # ₹50,000 default (docs/policy-model.md §2.2)
    session_capabilities: set[str] = field(
        default_factory=lambda: {
            "buyer:discover",
            "buyer:quote",
            "buyer:negotiate",
            "buyer:checkout",
        }
    )
