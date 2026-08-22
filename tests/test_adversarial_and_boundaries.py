"""Adversarial, boundary, and fail-closed security tests for state machines and policy engine."""

from agent_ready_merchant.policy.engine import DeterministicPolicyEngine
from agent_ready_merchant.policy.models import (
    PolicyContext,
    PolicyVerdict,
    QuoteItemProposal,
    QuoteProposal,
)


def test_adversarial_overflow_and_negative_prices() -> None:
    """Verifies that negative or zero prices are rejected with fail-closed verdicts."""
    item_negative = QuoteItemProposal(
        sku="SKU-MALICIOUS-1",
        quantity=1,
        unit_base_price_paise=100000,
        unit_floor_price_paise=80000,
        proposed_unit_price_paise=-1,  # Negative price injection!
        is_negotiable=True,
    )
    proposal = QuoteProposal(
        items=[item_negative],
        subtotal_paise=-1,
        discount_paise=0,
        shipping_paise=10000,
        total_paise=9999,
    )
    context = PolicyContext()
    res = DeterministicPolicyEngine.evaluate_quote(proposal, context)
    assert res.verdict == PolicyVerdict.DENY
    assert res.rule_code in {"PRICE_NON_POSITIVE", "POLICY_VIOLATION_BELOW_FLOOR_PRICE"}


def test_adversarial_excessive_discount_attempt() -> None:
    """Verifies that attempting 100% discount or discount > subtotal is rejected."""
    item = QuoteItemProposal(
        sku="SKU-STEAL",
        quantity=1,
        unit_base_price_paise=100000,
        unit_floor_price_paise=80000,
        proposed_unit_price_paise=100000,
        is_negotiable=True,
    )
    # Attempt 50% discount when policy permits max 15%
    proposal = QuoteProposal(
        items=[item],
        subtotal_paise=100000,
        discount_paise=50000,  # 50% discount
        shipping_paise=0,
        total_paise=50000,
    )
    context = PolicyContext(max_discount_percentage=15.0)
    res = DeterministicPolicyEngine.evaluate_quote(proposal, context)
    assert res.verdict == PolicyVerdict.DENY
    assert res.rule_code == "MAX_DISCOUNT_EXCEEDED"


def test_adversarial_unauthorized_capability() -> None:
    """Verifies that a session without checkout capability cannot evaluate orders."""
    context = PolicyContext(session_capabilities={"buyer:discover"})
    res = DeterministicPolicyEngine.evaluate_order(
        amount_paise=100000,
        context=context,
        required_capability="buyer:checkout",
    )
    assert res.verdict == PolicyVerdict.DENY
    assert res.rule_code == "CAPABILITY_DENIED"


def test_fail_closed_pipeline_with_denial() -> None:
    """Verifies that if any rule in pipeline denies, overall verdict is DENY."""
    item_bad = QuoteItemProposal(
        sku="SKU-BAD",
        quantity=1,
        unit_base_price_paise=100000,
        unit_floor_price_paise=90000,
        proposed_unit_price_paise=80000,  # Below floor
        is_negotiable=True,
    )
    proposal = QuoteProposal(
        items=[item_bad],
        subtotal_paise=80000,
        discount_paise=0,
        shipping_paise=10000,
        total_paise=90000,
    )
    context = PolicyContext()
    res = DeterministicPolicyEngine.evaluate_quote(proposal, context)
    assert res.verdict == PolicyVerdict.DENY
    assert res.rule_code == "POLICY_VIOLATION_BELOW_FLOOR_PRICE"
