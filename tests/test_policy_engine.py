"""Tests for Deterministic Policy Engine and fail-closed security rules."""

from agent_ready_merchant.policy.engine import DeterministicPolicyEngine
from agent_ready_merchant.policy.models import (
    PolicyContext,
    PolicyVerdict,
    QuoteItemProposal,
    QuoteProposal,
)
from agent_ready_merchant.policy.rules import (
    evaluate_capability,
    evaluate_floor_price,
    evaluate_max_discount,
    evaluate_shipping,
    evaluate_transaction_limit,
)


def test_floor_price_boundary_enforcement() -> None:
    """Verifies that proposed unit price strictly rejects values below floor price."""
    # 1. Price below floor -> DENY
    below_floor_item = QuoteItemProposal(
        sku="SKU-TEST-01",
        quantity=1,
        unit_base_price_paise=500000,  # ₹5,000
        unit_floor_price_paise=450000,  # ₹4,500
        proposed_unit_price_paise=449900,  # ₹4,499 (100 paise below floor!)
        is_negotiable=True,
    )
    result = evaluate_floor_price(below_floor_item)
    assert result.verdict == PolicyVerdict.DENY
    assert result.rule_code == "POLICY_VIOLATION_BELOW_FLOOR_PRICE"
    assert "below the allowed floor price" in result.reason

    # 2. Price exactly at floor -> ALLOW
    exact_floor_item = QuoteItemProposal(
        sku="SKU-TEST-01",
        quantity=1,
        unit_base_price_paise=500000,
        unit_floor_price_paise=450000,
        proposed_unit_price_paise=450000,
        is_negotiable=True,
    )
    result_exact = evaluate_floor_price(exact_floor_item)
    assert result_exact.verdict == PolicyVerdict.ALLOW

    # 3. Non-positive price -> DENY
    zero_price_item = QuoteItemProposal(
        sku="SKU-TEST-01",
        quantity=1,
        unit_base_price_paise=500000,
        unit_floor_price_paise=450000,
        proposed_unit_price_paise=0,
        is_negotiable=True,
    )
    assert evaluate_floor_price(zero_price_item).verdict == PolicyVerdict.DENY


def test_max_discount_boundary_enforcement() -> None:
    """Verifies that discount exceeding configured percentage is rejected."""
    context = PolicyContext(max_discount_percentage=15.0)  # 15% max

    item = QuoteItemProposal(
        sku="SKU-1",
        quantity=1,
        unit_base_price_paise=100000,  # ₹1,000
        unit_floor_price_paise=80000,
        proposed_unit_price_paise=100000,
        is_negotiable=True,
    )

    # 1. 16% discount on ₹1,000 subtotal (16,000 paise > 15,000 paise) -> DENY
    excessive_discount_proposal = QuoteProposal(
        items=[item],
        subtotal_paise=100000,
        discount_paise=16000,
        shipping_paise=0,
        total_paise=84000,
    )
    res1 = evaluate_max_discount(excessive_discount_proposal, context)
    assert res1.verdict == PolicyVerdict.DENY
    assert res1.rule_code == "MAX_DISCOUNT_EXCEEDED"

    # 2. Exactly 15% discount (15,000 paise) -> ALLOW
    exact_discount_proposal = QuoteProposal(
        items=[item],
        subtotal_paise=100000,
        discount_paise=15000,
        shipping_paise=0,
        total_paise=85000,
    )
    res2 = evaluate_max_discount(exact_discount_proposal, context)
    assert res2.verdict == PolicyVerdict.ALLOW

    # 3. Negative discount -> DENY
    negative_discount_proposal = QuoteProposal(
        items=[item],
        subtotal_paise=100000,
        discount_paise=-500,
        shipping_paise=0,
        total_paise=100500,
    )
    assert evaluate_max_discount(negative_discount_proposal, context).verdict == PolicyVerdict.DENY


def test_capability_enforcement() -> None:
    """Verifies that missing session capabilities cause policy rejection."""
    context = PolicyContext(session_capabilities={"buyer:discover", "buyer:quote"})

    # Check allowed capability
    res_allow = evaluate_capability(context, "buyer:quote")
    assert res_allow.verdict == PolicyVerdict.ALLOW

    # Check denied capability
    res_deny = evaluate_capability(context, "buyer:negotiate")
    assert res_deny.verdict == PolicyVerdict.DENY
    assert res_deny.rule_code == "CAPABILITY_DENIED"


def test_autonomy_level_matrix() -> None:
    """Verifies behavior across Autonomy Level 0, Level 1, and Level 2."""
    item_discounted = QuoteItemProposal(
        sku="SKU-DISC",
        quantity=1,
        unit_base_price_paise=100000,
        unit_floor_price_paise=80000,
        proposed_unit_price_paise=90000,  # Discounted
        is_negotiable=True,
    )
    proposal = QuoteProposal(
        items=[item_discounted],
        subtotal_paise=90000,
        discount_paise=0,
        shipping_paise=10000,
        total_paise=100000,
    )

    # 1. Level 0 (Read-Only): Negotiation is completely disabled -> DENY
    ctx_lvl0 = PolicyContext(merchant_autonomy_level=0)
    res_lvl0 = DeterministicPolicyEngine.evaluate_quote(proposal, ctx_lvl0)
    assert res_lvl0.verdict == PolicyVerdict.DENY
    assert res_lvl0.rule_code == "NEGOTIATION_DISABLED_AUTONOMY_LEVEL_ZERO"

    # 2. Level 1 (Bounded Auto): Price >= floor and discount <= max -> ALLOW
    ctx_lvl1 = PolicyContext(merchant_autonomy_level=1)
    res_lvl1 = DeterministicPolicyEngine.evaluate_quote(proposal, ctx_lvl1)
    assert res_lvl1.verdict == PolicyVerdict.ALLOW

    # 3. Level 2 (Supervised HITL): Requires human approval -> ESCALATE_APPROVAL
    ctx_lvl2 = PolicyContext(merchant_autonomy_level=2)
    res_lvl2 = DeterministicPolicyEngine.evaluate_quote(proposal, ctx_lvl2)
    assert res_lvl2.verdict == PolicyVerdict.ESCALATE_APPROVAL
    assert res_lvl2.required_approval is True


def test_non_negotiable_item_rejection() -> None:
    """Verifies that attempting price discount on non-negotiable item is rejected."""
    item_fixed = QuoteItemProposal(
        sku="SKU-FIXED",
        quantity=1,
        unit_base_price_paise=100000,
        unit_floor_price_paise=80000,
        proposed_unit_price_paise=90000,
        is_negotiable=False,  # Not negotiable!
    )
    proposal = QuoteProposal(
        items=[item_fixed],
        subtotal_paise=90000,
        discount_paise=0,
        shipping_paise=10000,
        total_paise=100000,
    )
    context = PolicyContext(merchant_autonomy_level=1)
    res = DeterministicPolicyEngine.evaluate_quote(proposal, context)
    assert res.verdict == PolicyVerdict.DENY
    assert res.rule_code == "ITEM_NOT_NEGOTIABLE"


def test_shipping_policy_enforcement() -> None:
    """Verifies shipping fee calculations and country restrictions."""
    item = QuoteItemProposal(
        sku="SKU-1",
        quantity=1,
        unit_base_price_paise=50000,
        unit_floor_price_paise=40000,
        proposed_unit_price_paise=50000,
        is_negotiable=True,
    )

    # 1. Unsupported country (e.g. US) -> DENY
    foreign_proposal = QuoteProposal(
        items=[item],
        subtotal_paise=50000,
        discount_paise=0,
        shipping_paise=10000,
        total_paise=60000,
        shipping_country="US",
    )
    assert evaluate_shipping(foreign_proposal).verdict == PolicyVerdict.DENY

    # 2. Subtotal < ₹1,000 requires flat ₹100 shipping
    cheap_order_valid_shipping = QuoteProposal(
        items=[item],
        subtotal_paise=50000,  # ₹500
        discount_paise=0,
        shipping_paise=10000,  # ₹100
        total_paise=60000,
        shipping_country="IN",
    )
    assert evaluate_shipping(cheap_order_valid_shipping).verdict == PolicyVerdict.ALLOW

    # 3. Subtotal >= ₹1,000 requires ₹0 shipping (Free)
    expensive_item = QuoteItemProposal(
        sku="SKU-EXP",
        quantity=1,
        unit_base_price_paise=150000,
        unit_floor_price_paise=120000,
        proposed_unit_price_paise=150000,
        is_negotiable=True,
    )
    expensive_order_free_shipping = QuoteProposal(
        items=[expensive_item],
        subtotal_paise=150000,  # ₹1,500
        discount_paise=0,
        shipping_paise=0,  # Free shipping
        total_paise=150000,
        shipping_country="IN",
    )
    assert evaluate_shipping(expensive_order_free_shipping).verdict == PolicyVerdict.ALLOW


def test_transaction_cap_and_escalation() -> None:
    """Verifies that quotes exceeding single transaction cap trigger ESCALATE_APPROVAL."""
    context = PolicyContext(max_single_transaction_paise=5_000_000)  # ₹50,000 cap

    item = QuoteItemProposal(
        sku="SKU-HIGH",
        quantity=1,
        unit_base_price_paise=6_000_000,
        unit_floor_price_paise=5_000_000,
        proposed_unit_price_paise=6_000_000,  # ₹60,000
        is_negotiable=True,
    )
    proposal = QuoteProposal(
        items=[item],
        subtotal_paise=6_000_000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=6_000_000,
    )

    res = evaluate_transaction_limit(proposal, context)
    assert res.verdict == PolicyVerdict.ESCALATE_APPROVAL
    assert res.required_approval is True


def test_policy_engine_fail_closed_on_error() -> None:
    """Verifies that unexpected errors fail closed with DENY."""
    # Pass None as proposal to trigger exception in engine
    result = DeterministicPolicyEngine.evaluate_quote(None, PolicyContext())  # type: ignore[arg-type]
    assert result.verdict == PolicyVerdict.DENY
    assert result.rule_code == "POLICY_EVALUATION_EXCEPTION"
