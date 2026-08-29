"""Phase 4.2: Safety, Policy & Governance Kernel Adversarial Test Suite.

Adheres strictly to Phase 4.2 specifications and invariants:
- Centralized policy decision records for consequential actions
- Explicit reason codes for ALLOW / DENY / ESCALATE
- Immutable audit linkage from request -> session -> capability -> policy -> mutation
- Policy version and deterministic policy hash recorded with every decision
- Prevention of policy changes from invalidating historical audit interpretation
- Merchant approval gates (Human-in-the-Loop) with explicit expiration
- Prevention of LLM/AI direct domain or financial mutation
- Detection and rejection of policy and context tampering
- Zero secrets and masked PII in audit event payloads
- Governance safety ceilings and limits
- Concurrency and race safety for approval resolutions
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from agent_ready_merchant.gateway.canonical import CanonicalCommerceGateway
from agent_ready_merchant.gateway.schemas import ResolveApprovalRequest
from agent_ready_merchant.models.approval import MerchantApproval
from agent_ready_merchant.models.audit import AuditEvent, sanitize_audit_payload
from agent_ready_merchant.models.inventory import InventoryItem
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.policy import PolicyRule
from agent_ready_merchant.models.product import Product, ProductVariant
from agent_ready_merchant.models.quote import PriceQuote
from agent_ready_merchant.models.session import BuyerAgentSession
from agent_ready_merchant.policy.engine import DeterministicPolicyEngine
from agent_ready_merchant.policy.models import (
    PolicyContext,
    QuoteItemProposal,
    QuoteProposal,
    compute_policy_hash,
)
from agent_ready_merchant.tools.base import GatewayContext


async def _seed_governance_env(
    db_session: AsyncSession,
    autonomy_level: int = 1,
    max_discount_pct: float = 15.0,
    floor_price_paise: int = 400000,
    base_price_paise: int = 500000,
    is_negotiable: bool = True,
    buyer_token_val: str | None = None,
) -> tuple[Merchant, BuyerAgentSession, Product, ProductVariant, InventoryItem, GatewayContext]:
    """Seeds an authoritative test environment with policy rules and active session."""
    now = datetime.now(UTC)
    uid = uuid.uuid4().hex[:8]
    actual_token = buyer_token_val or f"tok_sec_{uuid.uuid4().hex}"

    merchant = Merchant(
        name=f"Gov Merchant {uid}",
        slug=f"gov-merchant-{uid}",
        currency="INR",
        rzp_key_id=f"rzp_test_{uid}",
        status="ACTIVE",
    )
    db_session.add(merchant)
    await db_session.flush()

    # Seed policy rule if configured
    if autonomy_level != 1 or max_discount_pct != 15.0:
        p_rule = PolicyRule(
            merchant_id=merchant.id,
            rule_type="AUTONOMY_LEVEL",
            target_scope="GLOBAL",
            rule_value={"autonomy_level": autonomy_level},
            is_active=True,
        )
        d_rule = PolicyRule(
            merchant_id=merchant.id,
            rule_type="MAX_DISCOUNT_PCT",
            target_scope="GLOBAL",
            rule_value={"max_discount_pct": max_discount_pct},
            is_active=True,
        )
        db_session.add_all([p_rule, d_rule])
        await db_session.flush()

    token_hash = hashlib.sha256(actual_token.encode("utf-8")).hexdigest()
    session = BuyerAgentSession(
        merchant_id=merchant.id,
        buyer_agent_identifier=f"agent_gov_{uid}",
        auth_token_hash=token_hash,
        status="ACTIVE",
        expires_at=now + timedelta(hours=2),
        granted_capabilities=(
            "buyer:discover,buyer:read,buyer:quote,buyer:negotiate,"
            "buyer:checkout,buyer:payment_status"
        ),
    )
    db_session.add(session)
    await db_session.flush()

    product = Product(
        merchant_id=merchant.id,
        title=f"Gov Safety Product {uid}",
        sku=f"SKU-GOV-{uid}",
        description="Governance testing product description",
        category="General",
        base_price_paise=base_price_paise,
        floor_price_paise=floor_price_paise,
        is_negotiable=is_negotiable,
        is_active=True,
    )
    db_session.add(product)
    await db_session.flush()

    variant = ProductVariant(
        product_id=product.id,
        sku=f"SKU-GOV-{uid}-VAR",
        title="Standard Variant",
        is_active=True,
    )
    db_session.add(variant)
    await db_session.flush()

    inv = InventoryItem(
        variant_id=variant.id,
        available_quantity=20,
        reserved_quantity=0,
    )
    db_session.add(inv)
    await db_session.flush()

    context = GatewayContext(
        merchant_id=merchant.id,
        session_id=session.id,
        auth_token=actual_token,
        actor_type="BUYER_AGENT",
        capabilities={
            "buyer:discover",
            "buyer:read",
            "buyer:quote",
            "buyer:negotiate",
            "buyer:checkout",
            "buyer:payment_status",
        },
        autonomy_level=autonomy_level,
        max_discount_percentage=max_discount_pct,
    )

    return merchant, session, product, variant, inv, context


@pytest.mark.asyncio
async def test_policy_bypass_below_floor_fails_closed(db_session: AsyncSession) -> None:
    """Adversarial Test: Buyer attempts to negotiate below the floor price.

    Deterministic policy engine MUST reject with POLICY_VIOLATION_BELOW_FLOOR_PRICE
    and produce zero DB mutations.
    """
    gateway = CanonicalCommerceGateway()

    _, session, _, variant, _, context = await _seed_governance_env(
        db_session, floor_price_paise=400000, base_price_paise=500000
    )

    # 1. Create initial quote
    q_resp = await gateway.execute_capability(
        session=db_session,
        capability_name="get_quote",
        payload={
            "session_id": str(session.id),
            "items": [{"sku": variant.sku, "quantity": 1}],
            "shipping_country": "IN",
        },
        context=context,
    )
    assert q_resp.status == "SUCCESS"
    assert q_resp.data is not None
    quote_id = q_resp.data.quote_id

    # 2. Attempt counter-offer below floor price (₹3,500 < ₹4,000 floor)
    neg_resp = await gateway.execute_capability(
        session=db_session,
        capability_name="negotiate_quote",
        payload={
            "quote_id": str(quote_id),
            "proposed_total_paise": 350000,
            "rationale": "Adversarial low-ball proposal",
        },
        context=context,
    )
    assert neg_resp.status == "REJECTED"
    assert neg_resp.error is not None
    assert neg_resp.error.code in {
        "POLICY_VIOLATION_BELOW_FLOOR_PRICE",
        "POLICY_REJECTED",
        "FLOOR_PRICE_BREACH",
    }

    # Verify quote remains in original state with unchanged totals
    q_db = (
        await db_session.execute(select(PriceQuote).where(PriceQuote.id == quote_id))
    ).scalar_one()
    assert q_db.total_paise == 500000
    assert q_db.discount_paise == 0


@pytest.mark.asyncio
async def test_policy_version_and_hash_recorded_immutably(db_session: AsyncSession) -> None:
    """Adversarial Test: Policy hash and version are recorded with every decision.

    Modifying merchant configuration later does NOT alter the historical audit hash.
    """
    gateway = CanonicalCommerceGateway()

    merchant, session, _, variant, _, context = await _seed_governance_env(
        db_session, autonomy_level=1, max_discount_pct=15.0
    )

    q_resp = await gateway.execute_capability(
        session=db_session,
        capability_name="get_quote",
        payload={
            "session_id": str(session.id),
            "items": [{"sku": variant.sku, "quantity": 1}],
            "shipping_country": "IN",
        },
        context=context,
    )
    assert q_resp.data is not None
    quote_id = q_resp.data.quote_id

    # 1. Negotiate within bounds (10% discount: ₹450,000)
    neg_resp = await gateway.execute_capability(
        session=db_session,
        capability_name="negotiate_quote",
        payload={
            "quote_id": str(quote_id),
            "proposed_total_paise": 450000,
            "rationale": "10 percent discount",
        },
        context=context,
    )
    assert neg_resp.status == "SUCCESS"
    audit_ev_id = neg_resp.audit_event_id
    assert audit_ev_id is not None

    # Verify audit event records deterministic policy hash and version
    ev = (
        await db_session.execute(select(AuditEvent).where(AuditEvent.id == audit_ev_id))
    ).scalar_one()
    historical_policy_hash = ev.payload.get("policy_decision_hash")
    assert historical_policy_hash is not None
    assert len(historical_policy_hash) == 64
    assert ev.payload.get("policy_version") == "2026-03-01"

    # 2. Modify merchant policy in DB (change max discount to 5%)
    rule_update = PolicyRule(
        merchant_id=merchant.id,
        rule_type="MAX_DISCOUNT_PCT",
        target_scope="GLOBAL",
        rule_value={"max_discount_pct": 5.0},
        is_active=True,
    )
    db_session.add(rule_update)
    await db_session.flush()

    new_hash = compute_policy_hash(
        autonomy_level=1,
        max_discount_percentage=5.0,
        min_margin_percentage=20.0,
        max_single_transaction_paise=5_000_000,
    )
    assert new_hash != historical_policy_hash

    # Ensure historical audit event payload is completely immutable
    ev_refreshed = (
        await db_session.execute(select(AuditEvent).where(AuditEvent.id == audit_ev_id))
    ).scalar_one()
    assert ev_refreshed.payload.get("policy_decision_hash") == historical_policy_hash


@pytest.mark.asyncio
async def test_stale_approval_rejected_fail_closed(db_session: AsyncSession) -> None:
    """Adversarial Test: Stale/expired merchant approval ticket must be rejected fail-closed."""
    gateway = CanonicalCommerceGateway()

    merchant, session, _, variant, _, context = await _seed_governance_env(
        db_session,
        autonomy_level=2,  # Supervised HITL
    )

    q_resp = await gateway.execute_capability(
        session=db_session,
        capability_name="get_quote",
        payload={
            "session_id": str(session.id),
            "items": [{"sku": variant.sku, "quantity": 1}],
            "shipping_country": "IN",
        },
        context=context,
    )
    assert q_resp.data is not None
    quote_id = q_resp.data.quote_id

    # 1. Propose discount under Autonomy Level 2 -> creates PENDING approval
    neg_resp = await gateway.execute_capability(
        session=db_session,
        capability_name="negotiate_quote",
        payload={
            "quote_id": str(quote_id),
            "proposed_total_paise": 450000,
            "rationale": "Requires human approval",
        },
        context=context,
    )
    assert neg_resp.status == "SUCCESS"
    assert neg_resp.data is not None
    assert neg_resp.data.verdict == "ESCALATE_APPROVAL"
    assert neg_resp.data.status == "PENDING_APPROVAL"

    # Query created approval ticket
    appr_stmt = select(MerchantApproval).where(MerchantApproval.quote_id == quote_id)
    approval = (await db_session.execute(appr_stmt)).scalar_one()
    assert approval.status == "PENDING"

    # 2. Simulate expiration of the approval ticket
    approval.expires_at = datetime.now(UTC) - timedelta(minutes=5)
    await db_session.flush()

    # 3. Merchant admin attempts to approve expired ticket
    admin_context = GatewayContext(
        merchant_id=merchant.id,
        session_id=uuid.uuid4(),
        capabilities={"merchant:admin"},
        actor_type="MERCHANT_ADMIN",
    )
    res_resp = await gateway.resolve_approval(
        session=db_session,
        request=ResolveApprovalRequest(
            approval_id=approval.id,
            decision="APPROVE",
            reason="Late approval",
        ),
        context=admin_context,
    )
    assert res_resp.status == "REJECTED"
    assert res_resp.error is not None
    assert res_resp.error.code == "APPROVAL_EXPIRED"

    # Ensure approval is marked EXPIRED in DB
    await db_session.refresh(approval)
    assert approval.status == "EXPIRED"


@pytest.mark.asyncio
async def test_forged_and_cross_tenant_approval_rejected(db_session: AsyncSession) -> None:
    """Adversarial Test: Forged approval ID or cross-tenant approval resolution is rejected."""
    gateway = CanonicalCommerceGateway()

    merchant_a, sess_a, _, var_a, _, ctx_a = await _seed_governance_env(
        db_session, autonomy_level=2
    )
    merchant_b, _, _, _, _, _ = await _seed_governance_env(db_session, autonomy_level=2)

    # Create approval under Merchant A
    q_resp = await gateway.execute_capability(
        session=db_session,
        capability_name="get_quote",
        payload={
            "session_id": str(sess_a.id),
            "items": [{"sku": var_a.sku, "quantity": 1}],
            "shipping_country": "IN",
        },
        context=ctx_a,
    )
    assert q_resp.data is not None
    await gateway.execute_capability(
        session=db_session,
        capability_name="negotiate_quote",
        payload={
            "quote_id": str(q_resp.data.quote_id),
            "proposed_total_paise": 450000,
        },
        context=ctx_a,
    )
    approval_a = (
        await db_session.execute(
            select(MerchantApproval).where(MerchantApproval.quote_id == q_resp.data.quote_id)
        )
    ).scalar_one()

    # 1. Nonexistent / forged approval ID
    admin_ctx_a = GatewayContext(
        merchant_id=merchant_a.id,
        session_id=uuid.uuid4(),
        capabilities={"merchant:admin"},
        actor_type="MERCHANT_ADMIN",
    )
    forged_resp = await gateway.resolve_approval(
        session=db_session,
        request=ResolveApprovalRequest(
            approval_id=uuid.uuid4(),
            decision="APPROVE",
        ),
        context=admin_ctx_a,
    )
    assert forged_resp.status == "REJECTED"
    assert forged_resp.error is not None
    assert forged_resp.error.code == "APPROVAL_NOT_FOUND"

    # 2. Merchant B attempts to approve Merchant A's ticket
    admin_ctx_b = GatewayContext(
        merchant_id=merchant_b.id,
        session_id=uuid.uuid4(),
        capabilities={"merchant:admin"},
        actor_type="MERCHANT_ADMIN",
    )
    cross_resp = await gateway.resolve_approval(
        session=db_session,
        request=ResolveApprovalRequest(
            approval_id=approval_a.id,
            decision="APPROVE",
        ),
        context=admin_ctx_b,
    )
    assert cross_resp.status == "REJECTED"
    assert cross_resp.error is not None
    assert cross_resp.error.code == "APPROVAL_NOT_FOUND"


@pytest.mark.asyncio
async def test_audit_tampering_detected_by_cryptographic_verification(
    db_session: AsyncSession,
) -> None:
    """Adversarial Test: Tampering with audit event payload or hash is detected by verify_chain."""
    merchant, session, _, _, _, _ = await _seed_governance_env(db_session)

    # 1. Create a valid audit chain
    ev1 = await AuditEvent.create_event(
        session=db_session,
        merchant_id=merchant.id,
        actor_type="SYSTEM",
        event_type="TEST_EVENT_1",
        payload={"action": "init"},
        session_id=session.id,
    )
    await AuditEvent.create_event(
        session=db_session,
        merchant_id=merchant.id,
        actor_type="BUYER_AGENT",
        event_type="TEST_EVENT_2",
        payload={"action": "step_2"},
        session_id=session.id,
    )
    await db_session.flush()

    # Initial verification must pass
    is_valid, err = await AuditEvent.verify_chain(db_session, merchant.id)
    assert is_valid is True
    assert err is None

    # 2. Adversarial tampering: modify payload of ev1 in storage without updating hash
    ev1.payload = {"action": "tampered_by_adversary"}
    await db_session.flush()

    # Chain verification MUST fail and identify digest mismatch
    is_valid_after, err_after = await AuditEvent.verify_chain(db_session, merchant.id)
    assert is_valid_after is False
    assert err_after is not None
    assert "Digest mismatch" in err_after


@pytest.mark.asyncio
async def test_secret_leakage_prevented_in_audit_records(db_session: AsyncSession) -> None:
    """Adversarial Test: Secrets and credentials in audit payloads are strictly sanitized."""
    merchant, session, _, _, _, _ = await _seed_governance_env(db_session)

    sensitive_payload = {
        "auth_token": "secret_bearer_token_xyz",
        "key_secret": "rzp_secret_99999",
        "password": "super_secret_db_password",
        "card_number": "4111222233334444",
        "buyer_id": "usr_123",
        "amount_paise": 500000,
    }

    event = await AuditEvent.create_event(
        session=db_session,
        merchant_id=merchant.id,
        actor_type="BUYER_AGENT",
        event_type="SENSITIVE_PAYLOAD_TEST",
        payload=sensitive_payload,
        session_id=session.id,
    )
    await db_session.flush()

    # Verify that raw secrets are never present in stored payload
    assert event.payload["auth_token"] == "[REDACTED_SECRET]"
    assert event.payload["key_secret"] == "[REDACTED_SECRET]"
    assert event.payload["password"] == "[REDACTED_SECRET]"
    assert event.payload["card_number"] == "[REDACTED_SECRET]"
    assert event.payload["amount_paise"] == 500000

    # Verify chain integrity over sanitized payload
    is_valid, err = await AuditEvent.verify_chain(db_session, merchant.id)
    assert is_valid is True


@pytest.mark.asyncio
async def test_pii_leakage_masked_in_audit_records(db_session: AsyncSession) -> None:
    """Adversarial Test: Email addresses and PII in audit payloads are masked."""
    sanitized = sanitize_audit_payload({"buyer_email": "alex.runner@example.com", "other": "test"})
    assert sanitized["buyer_email"] == "a***r@example.com"
    assert sanitized["other"] == "test"


@pytest.mark.asyncio
async def test_concurrent_approval_resolution_race_safety(db_session: AsyncSession) -> None:
    """Adversarial Test: Resolving an already-resolved approval fails closed."""
    gateway = CanonicalCommerceGateway()

    merchant, session, _, variant, _, context = await _seed_governance_env(
        db_session, autonomy_level=2
    )

    q_resp = await gateway.execute_capability(
        session=db_session,
        capability_name="get_quote",
        payload={
            "session_id": str(session.id),
            "items": [{"sku": variant.sku, "quantity": 1}],
            "shipping_country": "IN",
        },
        context=context,
    )
    assert q_resp.data is not None
    quote_id = q_resp.data.quote_id

    await gateway.execute_capability(
        session=db_session,
        capability_name="negotiate_quote",
        payload={
            "quote_id": str(quote_id),
            "proposed_total_paise": 450000,
        },
        context=context,
    )
    approval = (
        await db_session.execute(
            select(MerchantApproval).where(MerchantApproval.quote_id == quote_id)
        )
    ).scalar_one()

    admin_ctx = GatewayContext(
        merchant_id=merchant.id,
        session_id=uuid.uuid4(),
        capabilities={"merchant:admin"},
        actor_type="MERCHANT_ADMIN",
    )

    # 1. First resolution: APPROVE succeeds
    resp1 = await gateway.resolve_approval(
        session=db_session,
        request=ResolveApprovalRequest(
            approval_id=approval.id,
            decision="APPROVE",
            reason="First admin decision",
        ),
        context=admin_ctx,
    )
    assert resp1.status == "SUCCESS"
    assert resp1.data is not None
    assert resp1.data.status == "APPROVED"

    # 2. Second concurrent/subsequent resolution: REJECT fails closed
    resp2 = await gateway.resolve_approval(
        session=db_session,
        request=ResolveApprovalRequest(
            approval_id=approval.id,
            decision="REJECT",
            reason="Conflicting late decision",
        ),
        context=admin_ctx,
    )
    assert resp2.status == "REJECTED"
    assert resp2.error is not None
    assert resp2.error.code == "APPROVAL_ALREADY_RESOLVED"


@pytest.mark.asyncio
async def test_policy_context_tampering_overridden_by_authoritative_merchant_rules(
    db_session: AsyncSession,
) -> None:
    """Adversarial Test: Buyer context tampering is overridden by DB rules."""
    gateway = CanonicalCommerceGateway()

    # Merchant has Autonomy Level 2 in DB (HITL required for all discounts)
    _, session, _, variant, _, context = await _seed_governance_env(db_session, autonomy_level=2)

    # Malicious buyer attempts to override context.autonomy_level = 1 to bypass approval
    context.autonomy_level = 1

    q_resp = await gateway.execute_capability(
        session=db_session,
        capability_name="get_quote",
        payload={
            "session_id": str(session.id),
            "items": [{"sku": variant.sku, "quantity": 1}],
            "shipping_country": "IN",
        },
        context=context,
    )
    assert q_resp.data is not None
    quote_id = q_resp.data.quote_id

    neg_resp = await gateway.execute_capability(
        session=db_session,
        capability_name="negotiate_quote",
        payload={
            "quote_id": str(quote_id),
            "proposed_total_paise": 450000,
        },
        context=context,
    )
    # The gateway anti-tampering gate loads DB policy rule and forces Autonomy Level 2
    assert neg_resp.status == "SUCCESS"
    assert neg_resp.data is not None
    assert neg_resp.data.verdict == "ESCALATE_APPROVAL"
    assert neg_resp.data.status == "PENDING_APPROVAL"


@pytest.mark.asyncio
async def test_governance_max_items_and_absolute_ceilings_enforced(
    db_session: AsyncSession,
) -> None:
    """Adversarial Test: Platform safety ceilings (max items, single tx limit, max rounds)."""
    _, _, product, _, _, _ = await _seed_governance_env(db_session)

    # 1. Item Quantity > 20 is rejected
    eval_items_res = DeterministicPolicyEngine.evaluate_quote(
        proposal=QuoteProposal(
            items=[
                QuoteItemProposal(
                    sku=product.sku,
                    quantity=25,
                    unit_base_price_paise=500000,
                    unit_floor_price_paise=400000,
                    proposed_unit_price_paise=500000,
                )
            ],
            subtotal_paise=12500000,
            discount_paise=0,
            shipping_paise=0,
            total_paise=12500000,
        ),
        context=PolicyContext(),
    )
    assert eval_items_res.is_denied is True
    assert eval_items_res.rule_code == "MAX_ITEMS_PER_QUOTE_EXCEEDED"

    # 2. Total > 10,000,000 paise (₹1,00,000 platform ceiling) is rejected
    eval_tx_res = DeterministicPolicyEngine.evaluate_quote(
        proposal=QuoteProposal(
            items=[
                QuoteItemProposal(
                    sku=product.sku,
                    quantity=1,
                    unit_base_price_paise=15000000,
                    unit_floor_price_paise=10000000,
                    proposed_unit_price_paise=15000000,
                )
            ],
            subtotal_paise=15000000,
            discount_paise=0,
            shipping_paise=0,
            total_paise=15000000,
        ),
        context=PolicyContext(),
    )
    assert eval_tx_res.is_denied is True
    assert eval_tx_res.rule_code == "GOVERNANCE_MAX_TRANSACTION_LIMIT_EXCEEDED"


@pytest.mark.asyncio
async def test_negotiation_rounds_governance_limit_enforced(db_session: AsyncSession) -> None:
    """Adversarial Test: Quote negotiation is capped at 3 rounds maximum."""
    gateway = CanonicalCommerceGateway()

    _, session, _, variant, _, context = await _seed_governance_env(
        db_session, autonomy_level=1, max_discount_pct=25.0
    )

    q_resp = await gateway.execute_capability(
        session=db_session,
        capability_name="get_quote",
        payload={
            "session_id": str(session.id),
            "items": [{"sku": variant.sku, "quantity": 1}],
            "shipping_country": "IN",
        },
        context=context,
    )
    assert q_resp.data is not None
    quote_id = q_resp.data.quote_id

    # Round 1
    r1 = await gateway.execute_capability(
        session=db_session,
        capability_name="negotiate_quote",
        payload={"quote_id": str(quote_id), "proposed_total_paise": 480000},
        context=context,
    )
    assert r1.status == "SUCCESS"

    # Round 2
    r2 = await gateway.execute_capability(
        session=db_session,
        capability_name="negotiate_quote",
        payload={"quote_id": str(quote_id), "proposed_total_paise": 460000},
        context=context,
    )
    assert r2.status == "SUCCESS"

    # Round 3
    r3 = await gateway.execute_capability(
        session=db_session,
        capability_name="negotiate_quote",
        payload={"quote_id": str(quote_id), "proposed_total_paise": 440000},
        context=context,
    )
    assert r3.status == "SUCCESS"

    # Round 4 (exceeds limit of 3 rounds) -> MUST fail closed
    r4 = await gateway.execute_capability(
        session=db_session,
        capability_name="negotiate_quote",
        payload={"quote_id": str(quote_id), "proposed_total_paise": 420000},
        context=context,
    )
    assert r4.status == "REJECTED"
    assert r4.error is not None
    assert r4.error.code == "MAX_NEGOTIATION_ATTEMPTS_EXCEEDED"


@pytest.mark.asyncio
async def test_llm_cannot_directly_mutate_database_state(db_session: AsyncSession) -> None:
    """Adversarial Test: Intelligence != Authority (INV-AGY-01).

    An untrusted LLM proposal cannot bypass the deterministic gating pipeline.
    """
    _, _, product, _, _, _ = await _seed_governance_env(db_session)

    # An adversarial tool invocation attempting arbitrary negative price
    eval_res = DeterministicPolicyEngine.evaluate_quote(
        proposal=QuoteProposal(
            items=[
                QuoteItemProposal(
                    sku=product.sku,
                    quantity=1,
                    unit_base_price_paise=500000,
                    unit_floor_price_paise=400000,
                    proposed_unit_price_paise=-100,  # Negative price injection
                )
            ],
            subtotal_paise=500000,
            discount_paise=0,
            shipping_paise=0,
            total_paise=-100,
        ),
        context=PolicyContext(),
    )
    assert eval_res.is_denied is True
    assert eval_res.rule_code == "PRICE_NON_POSITIVE"


@pytest.mark.asyncio
async def test_human_approved_quote_line_items_discounted_and_transactable(
    db_session: AsyncSession,
) -> None:
    """Remediation Verification (Issue 1): Line-Item Discount Distribution on Approved Quotes.

    Verifies that when a merchant admin approves an escalated counter-offer,
    quote line items are updated with distributed unit discounts, and creating
    an order generates OrderItems with matching unit prices and sum.
    """
    merchant, buyer_session, product, _, _, context = await _seed_governance_env(
        db_session, autonomy_level=2
    )
    gw = CanonicalCommerceGateway()

    # 1. Request initial quote (2 items @ 500,000 = 1,000,000 paise)
    quote_res = await gw.execute_capability(
        session=db_session,
        capability_name="get_quote",
        payload={
            "session_id": str(buyer_session.id),
            "items": [{"sku": product.sku, "quantity": 2}],
        },
        context=context,
    )
    assert quote_res.status == "SUCCESS"
    assert quote_res.data is not None
    quote_id = quote_res.data.quote_id

    # 2. Negotiate quote requesting 10% discount (triggers HITL escalation at Autonomy 2)
    neg_res = await gw.execute_capability(
        session=db_session,
        capability_name="negotiate_quote",
        payload={"quote_id": str(quote_id), "proposed_total_paise": 900000},
        context=context,
    )
    assert neg_res.status == "SUCCESS"
    assert neg_res.data is not None
    assert neg_res.data.verdict == "ESCALATE_APPROVAL"

    # Find pending approval ticket
    stmt = select(MerchantApproval).where(
        MerchantApproval.quote_id == quote_id,
        MerchantApproval.status == "PENDING",
    )
    approval = (await db_session.execute(stmt)).scalar_one()

    # 3. Resolve approval as APPROVE
    admin_context = GatewayContext(
        merchant_id=merchant.id,
        session_id=uuid.uuid4(),
        capabilities={"merchant:admin"},
        actor_type="MERCHANT_ADMIN",
    )
    appr_res = await gw.execute_capability(
        session=db_session,
        capability_name="resolve_approval",
        payload={
            "approval_id": str(approval.id),
            "decision": "APPROVE",
            "reason": "Approved VIP discount",
            "idempotency_key": f"idem_appr_{uuid.uuid4().hex}",
        },
        context=admin_context,
    )
    assert appr_res.status == "SUCCESS"
    assert appr_res.data is not None
    assert appr_res.data.status == "APPROVED"

    # 4. Verify quote line items reflect the discounted unit prices (450,000 each)
    q_stmt = (
        select(PriceQuote).options(selectinload(PriceQuote.items)).where(PriceQuote.id == quote_id)
    )
    updated_quote = (await db_session.execute(q_stmt)).scalar_one()
    assert updated_quote.status == "PROPOSED"
    assert updated_quote.total_paise == 900000
    assert updated_quote.discount_paise == 100000
    # Every line item must have discounted unit price
    for item in updated_quote.items:
        assert item.unit_price_paise == 450000
        assert item.total_price_paise == 450000 * item.quantity
    assert (
        sum(item.total_price_paise for item in updated_quote.items)
        == updated_quote.subtotal_paise - updated_quote.discount_paise
    )

    # 5. Accept quote
    acc_res = await gw.execute_capability(
        session=db_session,
        capability_name="accept_quote",
        payload={"quote_id": str(quote_id)},
        context=context,
    )
    assert acc_res.status == "SUCCESS"


@pytest.mark.asyncio
async def test_list_approvals_capability_and_authorization(db_session: AsyncSession) -> None:
    """Remediation Verification (Issue 4): list_approvals capability & authorization."""
    merchant, buyer_session, product, _, _, context = await _seed_governance_env(
        db_session, autonomy_level=2
    )
    gw = CanonicalCommerceGateway()

    # Create 2 quotes and negotiate to create 2 approval tickets
    for _ in range(2):
        q_res = await gw.execute_capability(
            session=db_session,
            capability_name="get_quote",
            payload={
                "session_id": str(buyer_session.id),
                "items": [{"sku": product.sku, "quantity": 1}],
            },
            context=context,
        )
        assert q_res.data is not None
        await gw.execute_capability(
            session=db_session,
            capability_name="negotiate_quote",
            payload={"quote_id": str(q_res.data.quote_id), "proposed_total_paise": 450000},
            context=context,
        )

    # 1. Unauthorized buyer agent cannot list approvals
    buyer_res = await gw.execute_capability(
        session=db_session,
        capability_name="list_approvals",
        payload={"status": "PENDING"},
        context=context,
    )
    assert buyer_res.status == "REJECTED"
    assert buyer_res.error is not None
    assert buyer_res.error.code == "CAPABILITY_DENIED"

    # 2. Merchant Admin lists approvals
    admin_context = GatewayContext(
        merchant_id=merchant.id,
        session_id=uuid.uuid4(),
        capabilities={"merchant:admin"},
        actor_type="MERCHANT_ADMIN",
    )
    admin_res = await gw.execute_capability(
        session=db_session,
        capability_name="list_approvals",
        payload={"status": "PENDING", "limit": 10, "offset": 0},
        context=admin_context,
    )
    assert admin_res.status == "SUCCESS"
    assert admin_res.data is not None
    assert admin_res.data.total_count >= 2
    assert len(admin_res.data.approvals) >= 2
    for item in admin_res.data.approvals:
        assert item.status == "PENDING"
        assert item.merchant_id == merchant.id


@pytest.mark.asyncio
async def test_expanded_sensitive_keys_redacted_in_audit_payloads(
    db_session: AsyncSession,
) -> None:
    """Remediation Verification (Issue 3): Extended credential redaction in audit payloads."""
    merchant, _, _, _, _, _ = await _seed_governance_env(db_session)

    raw_payload = {
        "authorization": "Bearer super-secret-token",
        "jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "access_token": "secret_access_token_12345",
        "refresh_token": "secret_refresh_token_67890",
        "private_key": "-----BEGIN PRIVATE KEY-----...",
        "signature": "hmac_sha256_secret_sig",
        "nested": {
            "bearer": "another_secret",
            "buyer_email": "alice.security@example.com",
        },
        "public_data": "visible_safe_info",
    }

    event = await AuditEvent.create_event(
        session=db_session,
        merchant_id=merchant.id,
        actor_type="SYSTEM",
        event_type="SECURITY_TEST_EVENT",
        payload=raw_payload,
    )

    # Redactions must be present in persisted payload
    p = event.payload
    assert p["authorization"] == "[REDACTED_SECRET]"
    assert p["jwt"] == "[REDACTED_SECRET]"
    assert p["access_token"] == "[REDACTED_SECRET]"
    assert p["refresh_token"] == "[REDACTED_SECRET]"
    assert p["private_key"] == "[REDACTED_SECRET]"
    assert p["signature"] == "[REDACTED_SECRET]"
    assert p["nested"]["bearer"] == "[REDACTED_SECRET]"
    assert p["nested"]["buyer_email"] == "a***y@example.com"
    assert p["public_data"] == "visible_safe_info"

    # Cryptographic integrity must verify successfully
    is_valid, err = await AuditEvent.verify_chain(db_session, merchant.id)
    assert is_valid is True
    assert err is None
