"""Pure, deterministic policy rule functions.

Adheres strictly to docs/policy-model.md §2 and INV-FIN-02 / INV-FIN-03.
"""

from agent_ready_merchant.policy.models import (
    PolicyContext,
    PolicyEvaluationResult,
    PolicyVerdict,
    QuoteItemProposal,
    QuoteProposal,
)


def evaluate_capability(
    context: PolicyContext,
    required_capability: str | None,
) -> PolicyEvaluationResult:
    """Verifies whether the current security context possesses the required capability."""
    if required_capability is None:
        return PolicyEvaluationResult(
            verdict=PolicyVerdict.ALLOW,
            rule_code="CAPABILITY_OK",
            reason="No specific capability required",
        )

    if required_capability not in context.session_capabilities:
        return PolicyEvaluationResult(
            verdict=PolicyVerdict.DENY,
            rule_code="CAPABILITY_DENIED",
            reason=f"Session lacks required capability: '{required_capability}'",
            required_capability=required_capability,
            metadata={"session_capabilities": list(context.session_capabilities)},
        )

    return PolicyEvaluationResult(
        verdict=PolicyVerdict.ALLOW,
        rule_code="CAPABILITY_OK",
        reason=f"Capability '{required_capability}' verified",
        required_capability=required_capability,
    )


def evaluate_floor_price(
    item: QuoteItemProposal,
    context: PolicyContext | None = None,
) -> PolicyEvaluationResult:
    """Enforces that item unit price cannot breach the SKU floor price or minimum margin."""
    if item.proposed_unit_price_paise <= 0:
        return PolicyEvaluationResult(
            verdict=PolicyVerdict.DENY,
            rule_code="PRICE_NON_POSITIVE",
            reason=f"Proposed price for SKU '{item.sku}' must be strictly > 0 paise",
            metadata={"sku": item.sku, "proposed_price_paise": item.proposed_unit_price_paise},
        )

    cost_floor = 0
    if item.unit_cost_price_paise is not None and context is not None:
        cost_floor = int(item.unit_cost_price_paise * (1.0 + context.min_margin_percentage / 100.0))

    effective_floor_paise = max(item.unit_floor_price_paise, cost_floor)

    if item.proposed_unit_price_paise < effective_floor_paise:
        if effective_floor_paise == cost_floor and cost_floor > item.unit_floor_price_paise:
            margin_pct = context.min_margin_percentage if context else 0
            reason = (
                f"Proposed unit price ₹{item.proposed_unit_price_paise / 100:.2f} "
                f"for SKU '{item.sku}' is below the required minimum margin price of "
                f"₹{cost_floor / 100:.2f} (margin: {margin_pct}%)"
            )
            rule_code = "POLICY_VIOLATION_BELOW_MIN_MARGIN"
        else:
            reason = (
                f"Proposed unit price ₹{item.proposed_unit_price_paise / 100:.2f} "
                f"for SKU '{item.sku}' is below the allowed floor price of "
                f"₹{item.unit_floor_price_paise / 100:.2f}"
            )
            rule_code = "POLICY_VIOLATION_BELOW_FLOOR_PRICE"

        return PolicyEvaluationResult(
            verdict=PolicyVerdict.DENY,
            rule_code=rule_code,
            reason=reason,
            metadata={
                "sku": item.sku,
                "proposed_unit_price_paise": item.proposed_unit_price_paise,
                "floor_price_paise": item.unit_floor_price_paise,
                "cost_price_paise": item.unit_cost_price_paise,
                "effective_floor_paise": effective_floor_paise,
            },
        )

    return PolicyEvaluationResult(
        verdict=PolicyVerdict.ALLOW,
        rule_code="FLOOR_PRICE_OK",
        reason=f"SKU '{item.sku}' unit price satisfies floor and margin constraints",
    )


def evaluate_max_discount(
    proposal: QuoteProposal,
    context: PolicyContext,
) -> PolicyEvaluationResult:
    """Enforces that total order discount percentage does not exceed configured ceiling."""
    if proposal.discount_paise < 0:
        return PolicyEvaluationResult(
            verdict=PolicyVerdict.DENY,
            rule_code="DISCOUNT_NEGATIVE",
            reason="Discount amount cannot be negative",
            metadata={"discount_paise": proposal.discount_paise},
        )

    if proposal.subtotal_paise <= 0 and proposal.discount_paise > 0:
        return PolicyEvaluationResult(
            verdict=PolicyVerdict.DENY,
            rule_code="DISCOUNT_ON_ZERO_SUBTOTAL",
            reason="Cannot apply discount to zero subtotal",
        )

    max_allowed_discount_paise = int(
        proposal.subtotal_paise * (context.max_discount_percentage / 100.0)
    )

    if proposal.discount_paise > max_allowed_discount_paise:
        return PolicyEvaluationResult(
            verdict=PolicyVerdict.DENY,
            rule_code="MAX_DISCOUNT_EXCEEDED",
            reason=(
                f"Total discount ₹{proposal.discount_paise / 100:.2f} exceeds "
                f"max allowed discount of {context.max_discount_percentage}% "
                f"(₹{max_allowed_discount_paise / 100:.2f})"
            ),
            metadata={
                "subtotal_paise": proposal.subtotal_paise,
                "discount_paise": proposal.discount_paise,
                "max_allowed_discount_paise": max_allowed_discount_paise,
                "max_discount_percentage": context.max_discount_percentage,
            },
        )

    return PolicyEvaluationResult(
        verdict=PolicyVerdict.ALLOW,
        rule_code="MAX_DISCOUNT_OK",
        reason="Discount is within allowable ceiling",
    )


def evaluate_transaction_limit(
    proposal: QuoteProposal,
    context: PolicyContext,
) -> PolicyEvaluationResult:
    """Enforces transaction volume caps and triggers approval escalation when exceeded."""
    if proposal.total_paise <= 0:
        return PolicyEvaluationResult(
            verdict=PolicyVerdict.DENY,
            rule_code="TOTAL_NON_POSITIVE",
            reason="Quote total must be strictly positive",
            metadata={"total_paise": proposal.total_paise},
        )

    if proposal.total_paise > context.max_single_transaction_paise:
        return PolicyEvaluationResult(
            verdict=PolicyVerdict.ESCALATE_APPROVAL,
            rule_code="TRANSACTION_LIMIT_ESCALATION",
            reason=(
                f"Transaction total ₹{proposal.total_paise / 100:.2f} exceeds single "
                f"transaction cap of ₹{context.max_single_transaction_paise / 100:.2f}. "
                "Merchant approval required."
            ),
            required_approval=True,
            metadata={
                "total_paise": proposal.total_paise,
                "max_single_transaction_paise": context.max_single_transaction_paise,
            },
        )

    return PolicyEvaluationResult(
        verdict=PolicyVerdict.ALLOW,
        rule_code="TRANSACTION_LIMIT_OK",
        reason="Transaction total is within allowed threshold",
    )


def evaluate_autonomy_and_negotiation(
    proposal: QuoteProposal,
    context: PolicyContext,
) -> PolicyEvaluationResult:
    """Enforces merchant autonomy levels and SKU negotiability rules."""
    has_discounted_items = False
    for item in proposal.items:
        if item.proposed_unit_price_paise < item.unit_base_price_paise:
            has_discounted_items = True
            if not item.is_negotiable:
                return PolicyEvaluationResult(
                    verdict=PolicyVerdict.DENY,
                    rule_code="ITEM_NOT_NEGOTIABLE",
                    reason=f"SKU '{item.sku}' is not marked as negotiable by merchant",
                    metadata={"sku": item.sku},
                )

    if has_discounted_items or proposal.discount_paise > 0:
        # Autonomy Level 0: Read-Only (no negotiation allowed)
        if context.merchant_autonomy_level == 0:
            return PolicyEvaluationResult(
                verdict=PolicyVerdict.DENY,
                rule_code="NEGOTIATION_DISABLED_AUTONOMY_LEVEL_ZERO",
                reason="Merchant operates at Autonomy Level 0 (Read-Only); negotiation is disabled",
            )

        # Autonomy Level 2: Supervised HITL (all discounts require approval)
        if context.merchant_autonomy_level == 2:
            return PolicyEvaluationResult(
                verdict=PolicyVerdict.ESCALATE_APPROVAL,
                rule_code="HITL_DISCOUNT_APPROVAL_REQUIRED",
                reason="Merchant operates at Autonomy Level 2; discount requires approval",
                required_approval=True,
            )

    return PolicyEvaluationResult(
        verdict=PolicyVerdict.ALLOW,
        rule_code="AUTONOMY_OK",
        reason="Negotiation meets merchant autonomy rules",
    )


def evaluate_shipping(proposal: QuoteProposal) -> PolicyEvaluationResult:
    """Enforces geographical and minimum shipping charge policies."""
    if proposal.shipping_country != "IN":
        return PolicyEvaluationResult(
            verdict=PolicyVerdict.DENY,
            rule_code="UNSUPPORTED_SHIPPING_COUNTRY",
            reason=f"Shipping to country '{proposal.shipping_country}' is not supported (IN only)",
            metadata={"shipping_country": proposal.shipping_country},
        )

    # Free shipping threshold: >= ₹1,000 (100,000 paise)
    free_shipping_threshold_paise = 100_000
    if proposal.subtotal_paise >= free_shipping_threshold_paise:
        if proposal.shipping_paise != 0:
            return PolicyEvaluationResult(
                verdict=PolicyVerdict.DENY,
                rule_code="FREE_SHIPPING_FEE_MISMATCH",
                reason="Orders over ₹1,000 qualify for free shipping (shipping charge must be 0)",
                metadata={"shipping_paise": proposal.shipping_paise},
            )
    else:
        # Flat ₹100 (10,000 paise) required for orders below ₹1,000
        standard_shipping_paise = 10_000
        if proposal.shipping_paise != standard_shipping_paise:
            return PolicyEvaluationResult(
                verdict=PolicyVerdict.DENY,
                rule_code="STANDARD_SHIPPING_FEE_MISMATCH",
                reason=(
                    f"Orders under ₹1,000 require standard ₹100.00 shipping fee "
                    f"({standard_shipping_paise} paise)"
                ),
                metadata={
                    "actual_shipping_paise": proposal.shipping_paise,
                    "expected_shipping_paise": standard_shipping_paise,
                },
            )

    return PolicyEvaluationResult(
        verdict=PolicyVerdict.ALLOW,
        rule_code="SHIPPING_POLICY_OK",
        reason="Shipping details satisfy merchant shipping rules",
    )


def evaluate_governance_limits(proposal: QuoteProposal) -> PolicyEvaluationResult:
    """Enforces platform-wide governance boundaries and safety ceilings (Phase 4.2)."""
    # 1. Platform-wide Item Quantity Limit (max 20 units per order)
    total_quantity = sum(item.quantity for item in proposal.items)
    if total_quantity > 20:
        return PolicyEvaluationResult(
            verdict=PolicyVerdict.DENY,
            rule_code="MAX_ITEMS_PER_QUOTE_EXCEEDED",
            reason=f"Order quantity {total_quantity} exceeds platform safety ceiling of 20 units",
            metadata={"total_quantity": total_quantity, "max_allowed": 20},
        )

    # 2. Platform Absolute Maximum Discount Ceiling (50%)
    if proposal.subtotal_paise > 0:
        discount_ratio = proposal.discount_paise / proposal.subtotal_paise
        if discount_ratio > 0.50:
            return PolicyEvaluationResult(
                verdict=PolicyVerdict.DENY,
                rule_code="GOVERNANCE_MAX_DISCOUNT_CEILING_EXCEEDED",
                reason=(
                    f"Discount ratio {discount_ratio * 100:.1f}% exceeds absolute "
                    "platform governance ceiling of 50.0%"
                ),
                metadata={"discount_ratio": discount_ratio, "max_ceiling": 0.50},
            )

    # 3. Platform Absolute Maximum Single Transaction Limit (₹1,00,000 / 10,000,000 paise)
    platform_max_single_tx_paise = 10_000_000
    if proposal.total_paise > platform_max_single_tx_paise:
        return PolicyEvaluationResult(
            verdict=PolicyVerdict.DENY,
            rule_code="GOVERNANCE_MAX_TRANSACTION_LIMIT_EXCEEDED",
            reason=(
                f"Transaction total ₹{proposal.total_paise / 100:.2f} exceeds absolute "
                f"platform transaction limit of ₹{platform_max_single_tx_paise / 100:.2f}"
            ),
            metadata={
                "total_paise": proposal.total_paise,
                "platform_max_single_tx_paise": platform_max_single_tx_paise,
            },
        )

    return PolicyEvaluationResult(
        verdict=PolicyVerdict.ALLOW,
        rule_code="GOVERNANCE_LIMITS_OK",
        reason="Proposal satisfies platform-wide governance safety boundaries",
    )
