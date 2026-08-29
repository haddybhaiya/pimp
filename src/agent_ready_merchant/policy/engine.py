"""Deterministic Policy Engine with Fail-Closed Resolution.

Adheres strictly to docs/policy-model.md §3, INV-AGY-02, and Phase 4.2:
- Centralized policy decision record for consequential actions
- Policy version and deterministic policy hash tracking
- Explicit reason codes for ALLOW, DENY, and ESCALATE
- Governance limits and platform safety ceilings
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable
from typing import Any

from agent_ready_merchant.policy.models import (
    PolicyContext,
    PolicyDecisionRecord,
    PolicyEvaluationResult,
    PolicyVerdict,
    QuoteProposal,
)
from agent_ready_merchant.policy.rules import (
    evaluate_autonomy_and_negotiation,
    evaluate_capability,
    evaluate_floor_price,
    evaluate_governance_limits,
    evaluate_max_discount,
    evaluate_shipping,
    evaluate_transaction_limit,
)

logger = logging.getLogger("agent_ready_merchant.policy")


class DeterministicPolicyEngine:
    """Mathematical and rule-based gatekeeper for quote negotiation and commerce actions."""

    @classmethod
    def _make_result(
        cls,
        verdict: PolicyVerdict,
        rule_code: str,
        reason: str,
        context: PolicyContext,
        metadata: dict[str, Any] | None = None,
        required_capability: str | None = None,
        required_approval: bool = False,
        context_snapshot: dict[str, Any] | None = None,
    ) -> PolicyEvaluationResult:
        """Constructs a PolicyEvaluationResult with an attached PolicyDecisionRecord."""
        policy_hash = context.policy_hash
        snapshot = context_snapshot or {
            "autonomy_level": context.merchant_autonomy_level,
            "max_discount_percentage": context.max_discount_percentage,
            "max_single_transaction_paise": context.max_single_transaction_paise,
            "min_margin_percentage": context.min_margin_percentage,
        }
        decision = PolicyDecisionRecord(
            decision_id=uuid.uuid4(),
            policy_version=context.policy_version,
            policy_hash=policy_hash,
            verdict=verdict,
            rule_code=rule_code,
            reason=reason,
            context_snapshot=snapshot,
            metadata=metadata or {},
        )
        return PolicyEvaluationResult(
            verdict=verdict,
            rule_code=rule_code,
            reason=reason,
            metadata=metadata or {},
            required_capability=required_capability,
            required_approval=required_approval,
            policy_hash=policy_hash,
            policy_decision=decision,
        )

    @classmethod
    def _wrap_with_decision(
        cls,
        res: PolicyEvaluationResult,
        context: PolicyContext,
        proposal: QuoteProposal | None = None,
    ) -> PolicyEvaluationResult:
        """Enriches an evaluation result with policy_hash and PolicyDecisionRecord."""
        snapshot = {
            "autonomy_level": context.merchant_autonomy_level,
            "max_discount_percentage": context.max_discount_percentage,
            "max_single_transaction_paise": context.max_single_transaction_paise,
            "min_margin_percentage": context.min_margin_percentage,
        }
        if proposal:
            snapshot.update(
                {
                    "subtotal_paise": proposal.subtotal_paise,
                    "discount_paise": proposal.discount_paise,
                    "total_paise": proposal.total_paise,
                }
            )
        decision = PolicyDecisionRecord(
            decision_id=uuid.uuid4(),
            policy_version=context.policy_version,
            policy_hash=context.policy_hash,
            verdict=res.verdict,
            rule_code=res.rule_code,
            reason=res.reason,
            context_snapshot=snapshot,
            metadata=res.metadata,
        )
        return PolicyEvaluationResult(
            verdict=res.verdict,
            rule_code=res.rule_code,
            reason=res.reason,
            metadata=res.metadata,
            required_capability=res.required_capability,
            required_approval=res.required_approval,
            policy_hash=context.policy_hash,
            policy_decision=decision,
        )

    @classmethod
    def evaluate_quote(
        cls,
        proposal: QuoteProposal,
        context: PolicyContext,
        required_capability: str | None = "buyer:quote",
    ) -> PolicyEvaluationResult:
        """Evaluates all applicable policy rules for a quote proposal.

        Enforces Fail-Closed resolution:
        1. If ANY rule returns DENY, the proposal is rejected.
        2. Else if ANY rule returns ESCALATE_APPROVAL, merchant approval is required.
        3. Only if ALL rules return ALLOW is the proposal approved.
        """
        try:
            # 0. Platform Governance Limits Check
            gov_result = evaluate_governance_limits(proposal)
            if gov_result.is_denied:
                return cls._wrap_with_decision(gov_result, context, proposal)

            # 1. Capability Check
            cap_result = evaluate_capability(context, required_capability)
            if cap_result.is_denied:
                return cls._wrap_with_decision(cap_result, context, proposal)

            # 2. Floor Price Check on all line items
            for item in proposal.items:
                floor_result = evaluate_floor_price(item, context)
                if floor_result.is_denied:
                    return cls._wrap_with_decision(floor_result, context, proposal)

            # 3. Maximum Discount Ceiling Check
            discount_result = evaluate_max_discount(proposal, context)
            if discount_result.is_denied:
                return cls._wrap_with_decision(discount_result, context, proposal)

            # 4. Autonomy Level & Negotiation Rules
            autonomy_result = evaluate_autonomy_and_negotiation(proposal, context)
            if autonomy_result.is_denied:
                return cls._wrap_with_decision(autonomy_result, context, proposal)

            # 5. Shipping Policy Rules
            shipping_result = evaluate_shipping(proposal)
            if shipping_result.is_denied:
                return cls._wrap_with_decision(shipping_result, context, proposal)

            # 6. Single Transaction Limit Check
            tx_limit_result = evaluate_transaction_limit(proposal, context)
            if tx_limit_result.is_denied:
                return cls._wrap_with_decision(tx_limit_result, context, proposal)

            # Collect escalations if any
            if autonomy_result.requires_escalation:
                return cls._wrap_with_decision(autonomy_result, context, proposal)
            if tx_limit_result.requires_escalation:
                return cls._wrap_with_decision(tx_limit_result, context, proposal)

            return cls._make_result(
                verdict=PolicyVerdict.ALLOW,
                rule_code="POLICY_EVALUATION_PASSED",
                reason="All deterministic policy rules satisfied",
                context=context,
                metadata={"total_paise": proposal.total_paise},
                context_snapshot={
                    "autonomy_level": context.merchant_autonomy_level,
                    "discount_paise": proposal.discount_paise,
                    "max_discount_percentage": context.max_discount_percentage,
                    "max_single_transaction_paise": context.max_single_transaction_paise,
                    "min_margin_percentage": context.min_margin_percentage,
                    "subtotal_paise": proposal.subtotal_paise,
                    "total_paise": proposal.total_paise,
                },
            )

        except Exception as exc:
            # FAIL-CLOSED: Any evaluation failure or unexpected error rejects the action
            logger.error(
                "Policy evaluation encountered unexpected exception: %s", exc, exc_info=True
            )
            return cls._make_result(
                verdict=PolicyVerdict.DENY,
                rule_code="POLICY_EVALUATION_EXCEPTION",
                reason=f"Policy evaluation failed closed due to error: {str(exc)}",
                context=context,
                metadata={"exception_type": type(exc).__name__},
            )

    @classmethod
    def evaluate_order(
        cls,
        amount_paise: int,
        context: PolicyContext,
        required_capability: str | None = "buyer:checkout",
    ) -> PolicyEvaluationResult:
        """Evaluates basic policy limits on direct order creation."""
        try:
            # 1. Capability Check
            cap_result = evaluate_capability(context, required_capability)
            if cap_result.is_denied:
                return cls._wrap_with_decision(cap_result, context)

            # 2. Positive Amount Check
            if amount_paise <= 0:
                return cls._make_result(
                    verdict=PolicyVerdict.DENY,
                    rule_code="ORDER_AMOUNT_NON_POSITIVE",
                    reason="Order amount must be strictly positive",
                    context=context,
                )

            # 3. Platform Absolute Maximum Single Transaction Limit Check
            platform_max_single_tx_paise = 10_000_000
            if amount_paise > platform_max_single_tx_paise:
                return cls._make_result(
                    verdict=PolicyVerdict.DENY,
                    rule_code="GOVERNANCE_MAX_TRANSACTION_LIMIT_EXCEEDED",
                    reason=(
                        f"Order amount ₹{amount_paise / 100:.2f} exceeds absolute platform "
                        f"governance ceiling of ₹{platform_max_single_tx_paise / 100:.2f}"
                    ),
                    context=context,
                )

            # 4. Merchant Single Transaction Limit Check (HITL Escalation)
            if amount_paise > context.max_single_transaction_paise:
                return cls._make_result(
                    verdict=PolicyVerdict.ESCALATE_APPROVAL,
                    rule_code="ORDER_LIMIT_ESCALATION",
                    reason=(
                        f"Order amount ₹{amount_paise / 100:.2f} exceeds cap of "
                        f"₹{context.max_single_transaction_paise / 100:.2f}. "
                        "Merchant approval required."
                    ),
                    context=context,
                    required_approval=True,
                )

            return cls._make_result(
                verdict=PolicyVerdict.ALLOW,
                rule_code="ORDER_POLICY_PASSED",
                reason="Order creation satisfies policy limits",
                context=context,
            )

        except Exception as exc:
            logger.error("Order policy evaluation failed: %s", exc, exc_info=True)
            return cls._make_result(
                verdict=PolicyVerdict.DENY,
                rule_code="ORDER_POLICY_EXCEPTION",
                reason=f"Order evaluation failed closed due to error: {str(exc)}",
                context=context,
            )

    @classmethod
    def evaluate_rules_pipeline(
        cls,
        rules: list[Callable[[], PolicyEvaluationResult]],
        context: PolicyContext,
    ) -> PolicyEvaluationResult:
        """Generic pipeline evaluator enforcing fail-closed resolution."""
        effective_context = context
        try:
            escalation_result: PolicyEvaluationResult | None = None

            for rule in rules:
                result = rule()
                if result.is_denied:
                    return cls._wrap_with_decision(result, effective_context)
                if result.requires_escalation and escalation_result is None:
                    escalation_result = result

            if escalation_result is not None:
                return cls._wrap_with_decision(escalation_result, effective_context)

            return cls._make_result(
                verdict=PolicyVerdict.ALLOW,
                rule_code="ALL_RULES_PASSED",
                reason="All pipeline rules passed successfully",
                context=effective_context,
            )

        except Exception as exc:
            logger.error("Pipeline evaluation error: %s", exc, exc_info=True)
            return cls._make_result(
                verdict=PolicyVerdict.DENY,
                rule_code="PIPELINE_EVALUATION_EXCEPTION",
                reason=f"Pipeline evaluation failed closed: {str(exc)}",
                context=effective_context,
            )
