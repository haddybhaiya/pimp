"""Deterministic Policy Engine with Fail-Closed Resolution.

Adheres strictly to docs/policy-model.md §3 and INV-AGY-02.
"""

import logging
from collections.abc import Callable

from agent_ready_merchant.policy.models import (
    PolicyContext,
    PolicyEvaluationResult,
    PolicyVerdict,
    QuoteProposal,
)
from agent_ready_merchant.policy.rules import (
    evaluate_autonomy_and_negotiation,
    evaluate_capability,
    evaluate_floor_price,
    evaluate_max_discount,
    evaluate_shipping,
    evaluate_transaction_limit,
)

logger = logging.getLogger("agent_ready_merchant.policy")


class DeterministicPolicyEngine:
    """Mathematical and rule-based gatekeeper for quote negotiation and commerce actions."""

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
            # 1. Capability Check
            cap_result = evaluate_capability(context, required_capability)
            if cap_result.is_denied:
                return cap_result

            # 2. Floor Price Check on all line items
            for item in proposal.items:
                floor_result = evaluate_floor_price(item, context)
                if floor_result.is_denied:
                    return floor_result

            # 3. Maximum Discount Ceiling Check
            discount_result = evaluate_max_discount(proposal, context)
            if discount_result.is_denied:
                return discount_result

            # 4. Autonomy Level & Negotiation Rules
            autonomy_result = evaluate_autonomy_and_negotiation(proposal, context)
            if autonomy_result.is_denied:
                return autonomy_result

            # 5. Shipping Policy Rules
            shipping_result = evaluate_shipping(proposal)
            if shipping_result.is_denied:
                return shipping_result

            # 6. Single Transaction Limit Check
            tx_limit_result = evaluate_transaction_limit(proposal, context)
            if tx_limit_result.is_denied:
                return tx_limit_result

            # Collect escalations if any
            if autonomy_result.requires_escalation:
                return autonomy_result
            if tx_limit_result.requires_escalation:
                return tx_limit_result

            return PolicyEvaluationResult(
                verdict=PolicyVerdict.ALLOW,
                rule_code="POLICY_EVALUATION_PASSED",
                reason="All deterministic policy rules satisfied",
                metadata={"total_paise": proposal.total_paise},
            )

        except Exception as exc:
            # FAIL-CLOSED: Any evaluation failure or unexpected error rejects the action
            logger.error(
                "Policy evaluation encountered unexpected exception: %s", exc, exc_info=True
            )
            return PolicyEvaluationResult(
                verdict=PolicyVerdict.DENY,
                rule_code="POLICY_EVALUATION_EXCEPTION",
                reason=f"Policy evaluation failed closed due to error: {str(exc)}",
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
                return cap_result

            # 2. Positive Amount Check
            if amount_paise <= 0:
                return PolicyEvaluationResult(
                    verdict=PolicyVerdict.DENY,
                    rule_code="ORDER_AMOUNT_NON_POSITIVE",
                    reason="Order amount must be strictly positive",
                )

            # 3. Single Transaction Limit Check
            if amount_paise > context.max_single_transaction_paise:
                return PolicyEvaluationResult(
                    verdict=PolicyVerdict.ESCALATE_APPROVAL,
                    rule_code="ORDER_LIMIT_ESCALATION",
                    reason=(
                        f"Order amount ₹{amount_paise / 100:.2f} exceeds cap of "
                        f"₹{context.max_single_transaction_paise / 100:.2f}"
                    ),
                    required_approval=True,
                )

            return PolicyEvaluationResult(
                verdict=PolicyVerdict.ALLOW,
                rule_code="ORDER_POLICY_PASSED",
                reason="Order creation satisfies policy limits",
            )

        except Exception as exc:
            logger.error("Order policy evaluation failed: %s", exc, exc_info=True)
            return PolicyEvaluationResult(
                verdict=PolicyVerdict.DENY,
                rule_code="ORDER_POLICY_EXCEPTION",
                reason=f"Order evaluation failed closed due to error: {str(exc)}",
            )

    @classmethod
    def evaluate_rules_pipeline(
        cls,
        rules: list[Callable[[], PolicyEvaluationResult]],
    ) -> PolicyEvaluationResult:
        """Generic pipeline evaluator enforcing fail-closed resolution."""
        try:
            escalation_result: PolicyEvaluationResult | None = None

            for rule in rules:
                result = rule()
                if result.is_denied:
                    return result
                if result.requires_escalation and escalation_result is None:
                    escalation_result = result

            if escalation_result is not None:
                return escalation_result

            return PolicyEvaluationResult(
                verdict=PolicyVerdict.ALLOW,
                rule_code="ALL_RULES_PASSED",
                reason="All pipeline rules passed successfully",
            )

        except Exception as exc:
            logger.error("Pipeline evaluation error: %s", exc, exc_info=True)
            return PolicyEvaluationResult(
                verdict=PolicyVerdict.DENY,
                rule_code="PIPELINE_EVALUATION_EXCEPTION",
                reason=f"Pipeline evaluation failed closed: {str(exc)}",
            )
