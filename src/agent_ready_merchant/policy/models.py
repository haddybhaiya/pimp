"""Domain models, contexts, and result types for the Deterministic Policy Engine.

Adheres strictly to docs/policy-model.md and INV-FIN-01 / INV-FIN-02 / INV-FIN-03 / INV-AGY-02.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from agent_ready_merchant.gateway.constants import COMMERCE_PROTOCOL_VERSION


class PolicyVerdict(StrEnum):
    """Verdict emitted by deterministic policy evaluation."""

    ALLOW = "ALLOW"
    DENY = "DENY"
    ESCALATE_APPROVAL = "ESCALATE_APPROVAL"


def compute_policy_hash(
    autonomy_level: int,
    max_discount_percentage: float,
    min_margin_percentage: float,
    max_single_transaction_paise: int,
    version: str = COMMERCE_PROTOCOL_VERSION,
    additional_rules: list[dict[str, Any]] | None = None,
) -> str:
    """Computes deterministic SHA-256 hash of active merchant policy configuration.

    Guarantees that historical audit interpretation remains immutable even if
    merchant configuration changes later in the database (INV-AGY-02).
    """
    clean_rules = additional_rules or []
    canonical_dict = {
        "autonomy_level": int(autonomy_level),
        "max_discount_percentage": float(max_discount_percentage),
        "max_single_transaction_paise": int(max_single_transaction_paise),
        "min_margin_percentage": float(min_margin_percentage),
        "rules": clean_rules,
        "version": str(version),
    }
    serialized = json.dumps(canonical_dict, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class PolicyDecisionRecord:
    """Immutable, auditable snapshot of a consequential policy decision."""

    decision_id: uuid.UUID
    policy_version: str
    policy_hash: str
    verdict: PolicyVerdict
    rule_code: str
    reason: str
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    context_snapshot: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PolicyEvaluationResult:
    """Detailed evaluation result emitted by the policy engine."""

    verdict: PolicyVerdict
    rule_code: str
    reason: str
    metadata: dict[str, Any] = field(default_factory=dict)
    required_capability: str | None = None
    required_approval: bool = False
    policy_hash: str | None = None
    policy_decision: PolicyDecisionRecord | None = None

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
    policy_version: str = COMMERCE_PROTOCOL_VERSION
    additional_rules: list[dict[str, Any]] = field(default_factory=list)

    @property
    def policy_hash(self) -> str:
        """Computes deterministic SHA-256 hash for this policy context."""
        return compute_policy_hash(
            autonomy_level=self.merchant_autonomy_level,
            max_discount_percentage=self.max_discount_percentage,
            min_margin_percentage=self.min_margin_percentage,
            max_single_transaction_paise=self.max_single_transaction_paise,
            version=self.policy_version,
            additional_rules=self.additional_rules,
        )
