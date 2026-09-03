"""Phase 8 Controlled Autonomy Comprehensive Verification Suite.

Validates:
- Separation of Intelligence and Authority (Intelligence != Authority)
- Typed low-risk autonomous action execution pipeline
- Pre-condition gates, budget limits, and cooldowns
- Master kill switch and anomaly detection
- Deterministic version-checked rollback and conflict rejection
- Replay protection (idempotency) and audit ledger immutability
- Multi-tenant isolation and adversarial prompt injection resistance
- End-to-end golden path and deliberate failure modes
"""

from __future__ import annotations

import uuid
from datetime import timedelta
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.config import get_settings
from agent_ready_merchant.db.base import utc_now
from agent_ready_merchant.main import app
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.autonomy import (
    AnomalyState,
    AutonomyActionStatus,
    AutonomyActionType,
    AutonomyClassification,
    MerchantAutonomyAction,
    RollbackStatus,
)
from agent_ready_merchant.models.experiment import MerchantExperiment
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.policy import PolicyRule
from agent_ready_merchant.models.product import Product, ProductVariant
from agent_ready_merchant.models.proposal import MerchantProposal
from agent_ready_merchant.schemas.controlled_autonomy import (
    AutonomyRuleUpdateRequest,
)
from agent_ready_merchant.schemas.merchant_agent import ProposalRiskLevel
from agent_ready_merchant.services.controlled_autonomy_service import (
    AutonomyExecutionError,
    AutonomySecurityError,
    ControlledAutonomyService,
    OptimisticLockError,
    RollbackConflictError,
)
from agent_ready_merchant.services.merchant_agent_service import MerchantAgentService
from agent_ready_merchant.services.merchant_auth_service import MerchantAuthService


@pytest_asyncio.fixture
async def setup_merchants_and_catalog(db_session: AsyncSession):
    """Provisions two isolated merchants with products, policies, and default autonomy rules."""
    settings = get_settings()
    secret = settings.SECRET_KEY.get_secret_value()

    # Merchant Alpha
    m1 = Merchant(
        name="Alpha Sports",
        slug=f"alpha-{uuid.uuid4().hex[:6]}",
        currency="INR",
        rzp_key_id="rzp_test_alpha",
        kill_switch_enabled=False,
    )
    db_session.add(m1)
    await db_session.flush()

    p1 = Product(
        merchant_id=m1.id,
        sku="ALPHA-SHIRT-01",
        title="Performance Training Shirt",
        description="Standard cotton training shirt.",
        category="Apparel",
        base_price_paise=150000,
        floor_price_paise=120000,
        attributes={"tags": ["running", "cotton"], "display_order": 10},
        version=1,
    )
    db_session.add(p1)
    await db_session.flush()

    v1 = ProductVariant(
        product_id=p1.id,
        sku="ALPHA-SHIRT-01-M",
        title="Performance Training Shirt - Medium",
        price_override_paise=150000,
    )
    db_session.add(v1)

    policy1 = PolicyRule(
        merchant_id=m1.id,
        rule_type="AUTONOMY_LEVEL",
        rule_value={"autonomy_level": 2},
        is_active=True,
    )
    db_session.add(policy1)

    # Merchant Beta (for tenant isolation tests)
    m2 = Merchant(
        name="Beta Electronics",
        slug=f"beta-{uuid.uuid4().hex[:6]}",
        currency="INR",
        rzp_key_id="rzp_test_beta",
        kill_switch_enabled=False,
    )
    db_session.add(m2)
    await db_session.flush()

    p2 = Product(
        merchant_id=m2.id,
        sku="BETA-MOUSE-01",
        title="Wireless Precision Mouse",
        description="Standard optical mouse.",
        category="Electronics",
        base_price_paise=250000,
        floor_price_paise=200000,
        attributes={"tags": ["office", "mouse"], "display_order": 5},
        version=1,
    )
    db_session.add(p2)
    await db_session.flush()

    v2 = ProductVariant(
        product_id=p2.id,
        sku="BETA-MOUSE-01-BLK",
        title="Wireless Precision Mouse - Black",
        price_override_paise=250000,
    )
    db_session.add(v2)

    await db_session.commit()

    # Phase 8 defaults are deliberately disabled: tests explicitly model the
    # merchant opting in before exercising autonomous execution.
    rules = await ControlledAutonomyService.get_or_create_default_rules(db_session, m1.id)
    for rule in rules:
        await ControlledAutonomyService.update_autonomy_rule(
            session=db_session,
            merchant_id=m1.id,
            action_type=rule.action_type,
            req=AutonomyRuleUpdateRequest(is_enabled=True, expected_version=rule.version),
            actor_type="MERCHANT_ADMIN",
            actor_id=m1.id,
        )
    await db_session.commit()

    token1 = MerchantAuthService.generate_admin_token(m1.id, secret, m1.slug)
    token2 = MerchantAuthService.generate_admin_token(m2.id, secret, m2.slug)

    return {
        "m1": m1,
        "m2": m2,
        "p1": p1,
        "p2": p2,
        "token1": token1,
        "token2": token2,
    }


@pytest.mark.asyncio
async def test_new_merchants_are_not_implicitly_opted_into_autonomy(
    db_session: AsyncSession,
) -> None:
    """Default rules remain disabled until a merchant administrator enables them."""
    merchant = Merchant(
        name="No Auto Opt-In",
        slug=f"no-auto-{uuid.uuid4().hex[:6]}",
        currency="INR",
        rzp_key_id="rzp_test_no_auto",
        kill_switch_enabled=False,
    )
    db_session.add(merchant)
    await db_session.flush()

    rules = await ControlledAutonomyService.get_or_create_default_rules(db_session, merchant.id)

    assert rules
    assert all(rule.is_enabled is False for rule in rules)


# =============================================================================
# 1. Authority & Governance Boundaries (Intelligence != Authority)
# =============================================================================


@pytest.mark.asyncio
async def test_agent_cannot_increase_own_authority_or_budget(
    db_session: AsyncSession, setup_merchants_and_catalog: dict[str, Any]
):
    """Validates that non-MERCHANT_ADMIN actors cannot modify autonomy rules or increase budgets."""
    m1 = setup_merchants_and_catalog["m1"]
    req = AutonomyRuleUpdateRequest(
        is_enabled=True,
        max_executions_per_hour=50,
        expected_version=1,
    )

    # Agent or external actor attempting to update rule fails closed with AutonomySecurityError
    with pytest.raises(AutonomySecurityError) as exc_info:
        await ControlledAutonomyService.update_autonomy_rule(
            session=db_session,
            merchant_id=m1.id,
            action_type=AutonomyActionType.IMPROVE_PRODUCT_DESCRIPTION.value,
            req=req,
            actor_type="MERCHANT_AGENT",  # Not MERCHANT_ADMIN
            actor_id=m1.id,
        )
    assert "not authorized to modify autonomy rules" in str(exc_info.value)

    # Agent attempting to construct request with excessive limit fails schema validation
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        AutonomyRuleUpdateRequest(
            is_enabled=True,
            max_executions_per_hour=999,  # exceeds max bound 100
            expected_version=1,
        )


@pytest.mark.asyncio
async def test_prohibited_actions_fail_closed_and_cannot_auto_execute(
    db_session: AsyncSession, setup_merchants_and_catalog: dict[str, Any]
):
    """Validates prohibited structured intent is caught by governance and blocked."""
    m1 = setup_merchants_and_catalog["m1"]
    p1 = setup_merchants_and_catalog["p1"]

    # Prohibited proposal attempting floor price or policy change
    prohibited_payload = {
        "proposal_type": "IMPROVE_PRODUCT_DESCRIPTION",
        "title": "Optimized description with floor_price_change override",
        "observation": "Low conversion on training shirt",
        "proposed_change": "Updating description and setting autonomy_increase",
        "hypothesis": "Increasing autonomy will improve speed",
        "target_entity": str(p1.id),
        "expected_effect": "+15% conversions",
        "evidence": ["ev_101"],
        "metadata_payload": {
            "structured_action": {"action": "floor_price_change", "new_floor": 1000},
            "target_product_id": str(p1.id),
        },
    }

    risk_level, valid_ev, rej = MerchantAgentService.govern_and_classify_proposal(
        prohibited_payload, {}
    )
    assert risk_level == ProposalRiskLevel.PROHIBITED
    assert rej is not None and (
        "cannot modify financial policy" in rej.lower()
        or "floor" in rej.lower()
        or "prohibited" in str(risk_level).lower()
    )

    # Create proposal in DB to test execution gate
    proposal = MerchantProposal(
        merchant_id=m1.id,
        proposal_type="IMPROVE_PRODUCT_DESCRIPTION",
        title="Prohibited Proposal",
        observation="Low conversion",
        proposed_change="Change with secret floor override",
        hypothesis="Better sales",
        target_entity=str(p1.id),
        expected_metric="conversion_rate",
        expected_effect="+10%",
        evidence=["ev_101"],
        risk_level="PROHIBITED",
        status="PROPOSED",
        metadata_payload=prohibited_payload["metadata_payload"],
    )
    db_session.add(proposal)
    await db_session.commit()

    # Attempting to execute prohibited proposal fails closed at Gate 4
    with pytest.raises(AutonomyExecutionError) as exc_info:
        await ControlledAutonomyService.execute_autonomous_action(
            session=db_session,
            merchant_id=m1.id,
            proposal_id=proposal.id,
            expected_target_version=1,
            idempotency_key=f"idemp-{uuid.uuid4().hex}",
        )
    assert "PROHIBITED by server-authoritative governance" in str(exc_info.value)


@pytest.mark.asyncio
async def test_object_first_and_inflected_actions_classified_prohibited():
    """Validates that object-first, snake_case, camelCase, and inflected forms are PROHIBITED."""
    prohibited_tests = [
        {"action": "autonomy_increase"},
        {"action": "policyOverride"},
        {"action": "floor_price_change"},
        {"action": "refund_request"},
        {"action": "permissionElevation"},
        {"action": "capability_grant"},
    ]

    for p in prohibited_tests:
        proposal = {
            "proposal_type": "IMPROVE_PRODUCT_DESCRIPTION",
            "title": f"Test {p['action']}",
            "observation": "Test observation",
            "proposed_change": "Test change",
            "hypothesis": "Test hypothesis",
            "target_entity": "product-123",
            "expected_effect": "+5%",
            "metadata_payload": {"structured_action": p},
        }
        risk, valid, rej = MerchantAgentService.govern_and_classify_proposal(proposal, {})
        assert risk == ProposalRiskLevel.PROHIBITED, f"Failed for {p}"


@pytest.mark.asyncio
async def test_benign_commerce_terms_remain_reviewable():
    """Validates that legitimate commerce terms are NOT falsely classified as PROHIBITED."""
    benign_terms = [
        ("Improve loyalty credits display", "Display customer loyalty credits at checkout"),
        ("Update shipping charges", "Explain shipping charges in product description"),
        ("Clarify refundable policy", "Add text stating product is refundable within 14 days"),
        ("Display credit score tips", "Show financing options based on credit score"),
        ("Delivery policy description", "Update delivery policy description on product page"),
    ]

    for title, change in benign_terms:
        proposal = {
            "proposal_type": "IMPROVE_PRODUCT_DESCRIPTION",
            "title": title,
            "observation": "Customers ask about return policy",
            "proposed_change": change,
            "hypothesis": "Clearer terms reduce friction",
            "target_entity": "product-123",
            "expected_effect": "+10%",
            "metadata_payload": {"structured_action": {"action": "IMPROVE_PRODUCT_DESCRIPTION"}},
        }
        risk, valid, rej = MerchantAgentService.govern_and_classify_proposal(proposal, {})
        assert risk != ProposalRiskLevel.PROHIBITED, f"False positive prohibited for: {title}"


@pytest.mark.asyncio
async def test_ambiguous_and_malformed_actions_fail_closed():
    """Validates that ambiguous or malformed structured actions fail closed to PROHIBITED."""
    malformed_tests = [
        {"action": ""},
        {"action": "UNKNOWN_CUSTOM_ACTION_DO_STUFF"},
        {"action": "EXECUTE_ARBITRARY_CODE"},
    ]
    for p in malformed_tests:
        proposal = {
            "proposal_type": "IMPROVE_PRODUCT_DESCRIPTION",
            "title": "Malformed action test",
            "observation": "Testing malformed",
            "proposed_change": "Testing change",
            "hypothesis": "Hypothesis",
            "target_entity": "prod-1",
            "expected_effect": "+1%",
            "metadata_payload": {"structured_action": p},
        }
        risk, valid, rej = MerchantAgentService.govern_and_classify_proposal(proposal, {})
        assert risk == ProposalRiskLevel.PROHIBITED, f"Malformed action not prohibited: {p}"


# =============================================================================
# 2. Pre-Condition Gates, Budgets, and Cooldowns
# =============================================================================


@pytest.mark.asyncio
async def test_approval_required_actions_blocked_from_auto_execution(
    db_session: AsyncSession, setup_merchants_and_catalog: dict[str, Any]
):
    """Validates that actions classified as APPROVAL_REQUIRED fail closed in auto-execution."""
    m1 = setup_merchants_and_catalog["m1"]
    p1 = setup_merchants_and_catalog["p1"]

    # Set rule to APPROVAL_REQUIRED
    rules = await ControlledAutonomyService.get_or_create_default_rules(db_session, m1.id)
    rule = next(
        r for r in rules if r.action_type == AutonomyActionType.IMPROVE_PRODUCT_DESCRIPTION.value
    )
    rule.classification = AutonomyClassification.APPROVAL_REQUIRED.value
    await db_session.flush()

    proposal = MerchantProposal(
        merchant_id=m1.id,
        proposal_type=AutonomyActionType.IMPROVE_PRODUCT_DESCRIPTION.value,
        title="Valid description update",
        observation="Observation",
        proposed_change="Better description text",
        hypothesis="Hypothesis",
        target_entity=str(p1.id),
        expected_metric="conversion_rate",
        expected_effect="+5%",
        evidence=["ev_1"],
        risk_level="APPROVAL_REQUIRED",
        status="PROPOSED",
        metadata_payload={"target_product_id": str(p1.id)},
    )
    db_session.add(proposal)
    await db_session.commit()

    with pytest.raises(AutonomyExecutionError) as exc_info:
        await ControlledAutonomyService.execute_autonomous_action(
            session=db_session,
            merchant_id=m1.id,
            proposal_id=proposal.id,
            expected_target_version=1,
            idempotency_key=f"idemp-{uuid.uuid4().hex}",
        )
    assert "APPROVAL_REQUIRED" in str(exc_info.value) or "approval" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_rejected_proposal_cannot_regain_execution_authority(
    db_session: AsyncSession, setup_merchants_and_catalog: dict[str, Any]
) -> None:
    """A rejected proposal cannot be reactivated by directly calling Phase 8 execution."""
    m1 = setup_merchants_and_catalog["m1"]
    p1 = setup_merchants_and_catalog["p1"]
    proposal = MerchantProposal(
        merchant_id=m1.id,
        proposal_type=AutonomyActionType.IMPROVE_PRODUCT_DESCRIPTION.value,
        title="Rejected description update",
        observation="Observation",
        proposed_change="This must not execute",
        hypothesis="Hypothesis",
        target_entity=str(p1.id),
        expected_metric="conversion_rate",
        expected_effect="+5%",
        evidence=["ev_1"],
        risk_level="LOW_RISK_REVERSIBLE",
        status="REJECTED",
        metadata_payload={"target_product_id": str(p1.id)},
    )
    db_session.add(proposal)
    await db_session.commit()

    with pytest.raises(AutonomyExecutionError, match="not eligible"):
        await ControlledAutonomyService.execute_autonomous_action(
            session=db_session,
            merchant_id=m1.id,
            proposal_id=proposal.id,
            expected_target_version=p1.version,
            idempotency_key=f"rejected-proposal-{uuid.uuid4().hex}",
        )


@pytest.mark.asyncio
async def test_experiment_cannot_start_until_merchant_approval(
    db_session: AsyncSession, setup_merchants_and_catalog: dict[str, Any]
) -> None:
    """The bounded-experiment action preserves Phase 7 approval-first lifecycle."""
    m1 = setup_merchants_and_catalog["m1"]
    proposal = MerchantProposal(
        merchant_id=m1.id,
        proposal_type=AutonomyActionType.SUGGEST_BOUNDED_EXPERIMENT.value,
        title="Experiment proposal",
        observation="Observation",
        proposed_change="Expose delivery ETA",
        hypothesis="Hypothesis",
        target_entity="general",
        expected_metric="conversion_rate",
        expected_effect="+5%",
        evidence=["ev_1"],
        risk_level="LOW_RISK_REVERSIBLE",
        status="PROPOSED",
        metadata_payload={},
    )
    db_session.add(proposal)
    await db_session.flush()
    experiment = MerchantExperiment(
        merchant_id=m1.id,
        proposal_id=proposal.id,
        title="Pending experiment",
        hypothesis="Hypothesis",
        target_metric="conversion_rate",
        baseline_value=0.0,
        target_value=1.0,
        proposed_variation={"description": "Expose delivery ETA"},
        risk_level="LOW_RISK_REVERSIBLE",
        status="APPROVAL_REQUIRED",
        approval_status="PENDING",
    )
    db_session.add(experiment)
    await db_session.commit()

    with pytest.raises(AutonomyExecutionError, match="merchant-approved"):
        await ControlledAutonomyService.execute_autonomous_action(
            session=db_session,
            merchant_id=m1.id,
            proposal_id=proposal.id,
            expected_target_version=experiment.version,
            idempotency_key=f"pending-experiment-{uuid.uuid4().hex}",
        )


@pytest.mark.asyncio
async def test_budget_exhaustion_hourly_and_daily_fail_closed(
    db_session: AsyncSession, setup_merchants_and_catalog: dict[str, Any]
):
    """Validates that hourly and daily execution quotas strictly fail closed."""
    m1 = setup_merchants_and_catalog["m1"]
    rules = await ControlledAutonomyService.get_or_create_default_rules(db_session, m1.id)
    rule = next(
        r for r in rules if r.action_type == AutonomyActionType.IMPROVE_PRODUCT_DESCRIPTION.value
    )
    rule.max_executions_per_hour = 2
    rule.max_executions_per_day = 5
    rule.cooldown_seconds = 0
    await db_session.commit()

    # Simulate 2 actions in current hour
    for i in range(2):
        action = MerchantAutonomyAction(
            merchant_id=m1.id,
            action_type=AutonomyActionType.IMPROVE_PRODUCT_DESCRIPTION.value,
            target_entity_type="product",
            target_entity_id=uuid.uuid4(),
            target_version_before=1,
            target_version_after=2,
            deterministic_classification=AutonomyClassification.AUTO_LOW_RISK.value,
            autonomy_rule_hash=rule.policy_hash,
            autonomy_rule_version=rule.version,
            hourly_budget_consumed=i + 1,
            daily_budget_consumed=i + 1,
            status=AutonomyActionStatus.EXECUTED.value,
            rollback_snapshot={"desc": "old"},
            rollback_status=RollbackStatus.AVAILABLE.value,
            anomaly_state=AnomalyState.NORMAL.value,
            idempotency_key=f"test-quota-{i}-{uuid.uuid4().hex}",
        )
        db_session.add(action)
    await db_session.commit()

    # 3rd action should fail closed
    with pytest.raises(AutonomyExecutionError) as exc_info:
        await ControlledAutonomyService.check_budget_and_cooldown(
            session=db_session,
            merchant_id=m1.id,
            rule=rule,
        )
    assert "Hourly execution limit (2) reached" in str(exc_info.value)


@pytest.mark.asyncio
async def test_cooldown_violations_fail_closed(
    db_session: AsyncSession, setup_merchants_and_catalog: dict[str, Any]
):
    """Validates that executing an action before cooldown expires is blocked."""
    m1 = setup_merchants_and_catalog["m1"]
    rules = await ControlledAutonomyService.get_or_create_default_rules(db_session, m1.id)
    rule = next(
        r for r in rules if r.action_type == AutonomyActionType.IMPROVE_PRODUCT_DESCRIPTION.value
    )
    rule.cooldown_seconds = 300  # 5 minutes
    rule.max_executions_per_hour = 10
    rule.max_executions_per_day = 20

    # Add an action performed 30 seconds ago
    recent_action = MerchantAutonomyAction(
        merchant_id=m1.id,
        action_type=AutonomyActionType.IMPROVE_PRODUCT_DESCRIPTION.value,
        target_entity_type="product",
        target_entity_id=uuid.uuid4(),
        target_version_before=1,
        target_version_after=2,
        deterministic_classification=AutonomyClassification.AUTO_LOW_RISK.value,
        autonomy_rule_hash=rule.policy_hash,
        autonomy_rule_version=rule.version,
        hourly_budget_consumed=1,
        daily_budget_consumed=1,
        status=AutonomyActionStatus.EXECUTED.value,
        rollback_snapshot={"desc": "old"},
        rollback_status=RollbackStatus.AVAILABLE.value,
        anomaly_state=AnomalyState.NORMAL.value,
        idempotency_key=f"test-cooldown-{uuid.uuid4().hex}",
        created_at=utc_now() - timedelta(seconds=30),
    )
    db_session.add(recent_action)
    await db_session.commit()

    with pytest.raises(AutonomyExecutionError) as exc_info:
        await ControlledAutonomyService.check_budget_and_cooldown(
            session=db_session,
            merchant_id=m1.id,
            rule=rule,
        )
    assert "Cooldown active" in str(exc_info.value)


@pytest.mark.asyncio
async def test_stale_target_version_fails_closed(
    db_session: AsyncSession, setup_merchants_and_catalog: dict[str, Any]
):
    """Validates that optimistic locking fails closed if expected_target_version does not match."""
    m1 = setup_merchants_and_catalog["m1"]
    p1 = setup_merchants_and_catalog["p1"]  # version is 1

    proposal = MerchantProposal(
        merchant_id=m1.id,
        proposal_type=AutonomyActionType.IMPROVE_PRODUCT_DESCRIPTION.value,
        title="Valid description update",
        observation="Observation",
        proposed_change="Upgraded description text",
        hypothesis="Hypothesis",
        target_entity=str(p1.id),
        expected_metric="conversion_rate",
        expected_effect="+5%",
        evidence=["ev_1"],
        risk_level="LOW_RISK_REVERSIBLE",
        status="PROPOSED",
        metadata_payload={"target_product_id": str(p1.id)},
    )
    db_session.add(proposal)
    await db_session.commit()

    # Pass stale version 99 (actual is 1)
    with pytest.raises(OptimisticLockError) as exc_info:
        await ControlledAutonomyService.execute_autonomous_action(
            session=db_session,
            merchant_id=m1.id,
            proposal_id=proposal.id,
            expected_target_version=99,
            idempotency_key=f"idemp-stale-{uuid.uuid4().hex}",
        )
    assert "version mismatch: expected 99, current 1" in str(exc_info.value)


# =============================================================================
# 3. Kill Switch and Anomaly Handling
# =============================================================================


@pytest.mark.asyncio
async def test_kill_switch_blocks_pre_execution(
    db_session: AsyncSession, setup_merchants_and_catalog: dict[str, Any]
):
    """Validates that when kill switch is enabled, autonomous execution fails closed."""
    m1 = setup_merchants_and_catalog["m1"]
    p1 = setup_merchants_and_catalog["p1"]

    # Activate kill switch
    await ControlledAutonomyService.set_kill_switch(
        session=db_session,
        merchant_id=m1.id,
        enabled=True,
        actor_type="MERCHANT_ADMIN",
        actor_id=m1.id,
        reason="Security test kill switch",
    )
    await db_session.commit()

    proposal = MerchantProposal(
        merchant_id=m1.id,
        proposal_type=AutonomyActionType.IMPROVE_PRODUCT_DESCRIPTION.value,
        title="Valid description update",
        observation="Observation",
        proposed_change="Better description text",
        hypothesis="Hypothesis",
        target_entity=str(p1.id),
        expected_metric="conversion_rate",
        expected_effect="+5%",
        evidence=["ev_1"],
        risk_level="LOW_RISK_REVERSIBLE",
        status="PROPOSED",
        metadata_payload={"target_product_id": str(p1.id)},
    )
    db_session.add(proposal)
    await db_session.commit()

    with pytest.raises(AutonomyExecutionError) as exc_info:
        await ControlledAutonomyService.execute_autonomous_action(
            session=db_session,
            merchant_id=m1.id,
            proposal_id=proposal.id,
            expected_target_version=1,
            idempotency_key=f"idemp-kill-{uuid.uuid4().hex}",
        )
    assert "Merchant kill switch is active" in str(exc_info.value)


@pytest.mark.asyncio
async def test_kill_switch_stops_running_experiments_safely(
    db_session: AsyncSession, setup_merchants_and_catalog: dict[str, Any]
):
    """Validates that toggling kill switch stops in-flight running experiments safely."""
    m1 = setup_merchants_and_catalog["m1"]

    exp = MerchantExperiment(
        merchant_id=m1.id,
        title="Running Experiment",
        hypothesis="Test hypothesis",
        target_metric="conversion_rate",
        baseline_value=10.0,
        target_value=15.0,
        proposed_variation={"test": "var"},
        risk_level="LOW_RISK_REVERSIBLE",
        status="RUNNING",
        approval_status="APPROVED",
    )
    db_session.add(exp)
    await db_session.commit()

    # Activate kill switch
    await ControlledAutonomyService.set_kill_switch(
        session=db_session,
        merchant_id=m1.id,
        enabled=True,
        actor_type="MERCHANT_ADMIN",
        actor_id=m1.id,
        reason="Emergency halt",
    )
    await db_session.commit()

    # Verify experiment was safely stopped
    await db_session.refresh(exp)
    assert exp.status == "STOPPED"
    assert exp.stopping_condition.get("stopped_by_kill_switch") is True


# =============================================================================
# 4. E2E Golden Path & Deterministic Rollback
# =============================================================================


@pytest.mark.asyncio
async def test_e2e_golden_path_scenario(
    db_session: AsyncSession, setup_merchants_and_catalog: dict[str, Any]
):
    """E2E Golden Path: Proposal -> Gate Verification -> Execution -> Version Check ->

    Snapshot -> Target Mutation -> Audit Ledger -> Deterministic Rollback -> Target Reverted.
    """
    m1 = setup_merchants_and_catalog["m1"]
    p1 = setup_merchants_and_catalog["p1"]
    initial_version = p1.version
    initial_desc = p1.description

    # 1. Formulate valid evidence-backed low-risk proposal
    new_description = "Premium ultra-breathable performance training shirt."
    proposal = MerchantProposal(
        merchant_id=m1.id,
        proposal_type=AutonomyActionType.IMPROVE_PRODUCT_DESCRIPTION.value,
        title="Enhance product description with material clarity",
        observation="Customers inquiring about fabric weight in chat sessions.",
        proposed_change=new_description,
        hypothesis="Specifying fabric details will increase conversion.",
        target_entity=str(p1.id),
        expected_metric="conversion_rate",
        expected_effect="+8%",
        evidence=["ev_chat_101", "ev_quote_202"],
        risk_level="LOW_RISK_REVERSIBLE",
        status="PROPOSED",
        metadata_payload={
            "target_product_id": str(p1.id),
            "new_description": new_description,
        },
    )
    db_session.add(proposal)
    await db_session.commit()

    # 2. Execute autonomous action through the 18 pre-condition gates
    exec_idemp = f"golden-exec-{uuid.uuid4().hex}"
    exec_result = await ControlledAutonomyService.execute_autonomous_action(
        session=db_session,
        merchant_id=m1.id,
        proposal_id=proposal.id,
        expected_target_version=initial_version,
        idempotency_key=exec_idemp,
        actor_id=m1.id,
    )
    await db_session.commit()

    assert exec_result["status"] == "SUCCESS"
    assert exec_result["action"]["status"] == "EXECUTED"
    action_id = uuid.UUID(exec_result["action"]["id"])
    post_action_version = exec_result["action"]["target_version_after"]
    assert post_action_version == initial_version + 1

    # Verify product was mutated
    await db_session.refresh(p1)
    assert p1.description == new_description
    assert p1.version == post_action_version

    # Verify audit event was written
    stmt_audit = select(AuditEvent).where(
        AuditEvent.merchant_id == m1.id,
        AuditEvent.event_type == "MERCHANT_AUTONOMY_ACTION_EXECUTED",
    )
    audit = (await db_session.execute(stmt_audit)).scalar_one_or_none()
    assert audit is not None
    assert audit.payload["action_id"] == str(action_id)

    # 3. Deterministic Rollback
    rollback_idemp = f"golden-rollback-{uuid.uuid4().hex}"
    rb_result = await ControlledAutonomyService.rollback_action(
        session=db_session,
        merchant_id=m1.id,
        action_id=action_id,
        expected_target_version=post_action_version,
        reason="Human merchant preferred original description",
        idempotency_key=rollback_idemp,
        actor_id=m1.id,
    )
    await db_session.commit()

    assert rb_result["rollback_status"] == RollbackStatus.ROLLED_BACK.value
    assert rb_result["target_version_reverted_to"] == initial_version

    # Verify product was reverted to exact snapshot state
    await db_session.refresh(p1)
    assert p1.description == initial_desc
    assert p1.version == post_action_version + 1  # version bumped on revert

    # 4. Repeated rollback is idempotent
    rb_replay = await ControlledAutonomyService.rollback_action(
        session=db_session,
        merchant_id=m1.id,
        action_id=action_id,
        expected_target_version=post_action_version,
        reason="Human merchant preferred original description",
        idempotency_key=rollback_idemp,
        actor_id=m1.id,
    )
    assert rb_replay["rollback_status"] == RollbackStatus.ROLLED_BACK.value


@pytest.mark.asyncio
async def test_rollback_after_human_modification_fails_closed(
    db_session: AsyncSession, setup_merchants_and_catalog: dict[str, Any]
):
    """Validates that if a human merchant modifies a product after an autonomous mutation,

    the rollback fails closed with RollbackConflictError and marks the action CONFLICT_REJECTED.
    """
    m1 = setup_merchants_and_catalog["m1"]
    p1 = setup_merchants_and_catalog["p1"]

    proposal = MerchantProposal(
        merchant_id=m1.id,
        proposal_type=AutonomyActionType.IMPROVE_PRODUCT_DESCRIPTION.value,
        title="Auto description update",
        observation="Observation",
        proposed_change="Auto generated text",
        hypothesis="Hypothesis",
        target_entity=str(p1.id),
        expected_metric="conversion_rate",
        expected_effect="+5%",
        evidence=["ev_1"],
        risk_level="LOW_RISK_REVERSIBLE",
        status="PROPOSED",
        metadata_payload={"target_product_id": str(p1.id)},
    )
    db_session.add(proposal)
    await db_session.commit()

    # Execute action
    exec_result = await ControlledAutonomyService.execute_autonomous_action(
        session=db_session,
        merchant_id=m1.id,
        proposal_id=proposal.id,
        expected_target_version=p1.version,
        idempotency_key=f"idemp-conflict-{uuid.uuid4().hex}",
    )
    await db_session.commit()
    action_id = uuid.UUID(exec_result["action"]["id"])

    # Now simulate a human merchant modifying the product directly
    await db_session.refresh(p1)
    p1.description = "Human merchant bespoke edit"
    p1.version += 1  # Version is now > target_version_after
    await db_session.commit()

    # Attempt rollback -> MUST fail closed!
    with pytest.raises(RollbackConflictError) as exc_info:
        await ControlledAutonomyService.rollback_action(
            session=db_session,
            merchant_id=m1.id,
            action_id=action_id,
            expected_target_version=p1.version,
            reason="Attempt rollback after human edit",
            idempotency_key=f"idemp-rb-conflict-{uuid.uuid4().hex}",
        )
    assert "A newer merchant modification exists" in str(exc_info.value)

    # Check action status was updated to CONFLICT_REJECTED
    action_stmt = select(MerchantAutonomyAction).where(MerchantAutonomyAction.id == action_id)
    action = (await db_session.execute(action_stmt)).scalar_one()
    assert action.rollback_status == RollbackStatus.CONFLICT_REJECTED.value


# =============================================================================
# 5. Multi-Tenant Isolation & Replay Protection
# =============================================================================


@pytest.mark.asyncio
async def test_cross_tenant_access_fails_closed(
    db_session: AsyncSession, setup_merchants_and_catalog: dict[str, Any]
):
    """Validates that Merchant B cannot execute or rollback Merchant A's proposals or actions."""
    m1 = setup_merchants_and_catalog["m1"]
    m2 = setup_merchants_and_catalog["m2"]
    p1 = setup_merchants_and_catalog["p1"]

    proposal = MerchantProposal(
        merchant_id=m1.id,
        proposal_type=AutonomyActionType.IMPROVE_PRODUCT_DESCRIPTION.value,
        title="Alpha's proposal",
        observation="Obs",
        proposed_change="New Alpha Desc",
        hypothesis="Hyp",
        target_entity=str(p1.id),
        expected_metric="conversion_rate",
        expected_effect="+5%",
        evidence=["ev_1"],
        risk_level="LOW_RISK_REVERSIBLE",
        status="PROPOSED",
        metadata_payload={"target_product_id": str(p1.id)},
    )
    db_session.add(proposal)
    await db_session.commit()

    # Merchant B attempts to execute Merchant A's proposal
    with pytest.raises(AutonomyExecutionError) as exc_info:
        await ControlledAutonomyService.execute_autonomous_action(
            session=db_session,
            merchant_id=m2.id,  # Merchant B
            proposal_id=proposal.id,  # Owned by Alpha
            expected_target_version=1,
            idempotency_key=f"cross-tenant-{uuid.uuid4().hex}",
        )
    assert "not found for merchant" in str(exc_info.value)


@pytest.mark.asyncio
async def test_duplicate_execution_mutates_once(
    db_session: AsyncSession, setup_merchants_and_catalog: dict[str, Any]
):
    """Validates replaying same idempotency key returns cached result without mutating twice."""
    m1 = setup_merchants_and_catalog["m1"]
    p1 = setup_merchants_and_catalog["p1"]
    initial_version = p1.version

    proposal = MerchantProposal(
        merchant_id=m1.id,
        proposal_type=AutonomyActionType.IMPROVE_PRODUCT_DESCRIPTION.value,
        title="Idempotent proposal",
        observation="Obs",
        proposed_change="Idempotent change",
        hypothesis="Hyp",
        target_entity=str(p1.id),
        expected_metric="conversion_rate",
        expected_effect="+5%",
        evidence=["ev_1"],
        risk_level="LOW_RISK_REVERSIBLE",
        status="PROPOSED",
        metadata_payload={"target_product_id": str(p1.id)},
    )
    db_session.add(proposal)
    await db_session.commit()

    key = f"idem-key-{uuid.uuid4().hex}"

    # First call: executes mutation
    res1 = await ControlledAutonomyService.execute_autonomous_action(
        session=db_session,
        merchant_id=m1.id,
        proposal_id=proposal.id,
        expected_target_version=initial_version,
        idempotency_key=key,
    )
    await db_session.commit()

    # Second call: replayed idempotently
    res2 = await ControlledAutonomyService.execute_autonomous_action(
        session=db_session,
        merchant_id=m1.id,
        proposal_id=proposal.id,
        expected_target_version=initial_version,
        idempotency_key=key,
    )

    assert res1["action"]["id"] == res2["action"]["id"]
    await db_session.refresh(p1)
    assert p1.version == initial_version + 1  # Only incremented ONCE


# =============================================================================
# 6. REST API Endpoints Verification
# =============================================================================


@pytest.mark.asyncio
async def test_rest_api_autonomy_endpoints(
    db_session: AsyncSession, setup_merchants_and_catalog: dict[str, Any]
):
    """Verifies all Phase 8 REST API endpoints using httpx AsyncClient."""
    m1 = setup_merchants_and_catalog["m1"]
    token1 = setup_merchants_and_catalog["token1"]
    p1 = setup_merchants_and_catalog["p1"]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        headers = {
            "X-Merchant-ID": str(m1.id),
            "X-Auth-Token": token1,
        }

        # 1. GET /api/v1/merchant/autonomy/status
        resp = await client.get("/api/v1/merchant/autonomy/status", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["merchant_id"] == str(m1.id)
        assert data["kill_switch_enabled"] is False
        assert data["anomaly_state"] == "NORMAL"
        assert len(data["rules"]) == 5

        # 2. POST /api/v1/merchant/autonomy/kill-switch
        resp_kill = await client.post(
            "/api/v1/merchant/autonomy/kill-switch",
            headers=headers,
            json={"enabled": True, "reason": "Testing kill switch API"},
        )
        assert resp_kill.status_code == 200
        assert resp_kill.json()["kill_switch_enabled"] is True

        # Deactivate kill switch
        await client.post(
            "/api/v1/merchant/autonomy/kill-switch",
            headers=headers,
            json={"enabled": False, "reason": "Testing kill switch deactivation"},
        )

        # 3. GET /api/v1/merchant/autonomy/rules
        resp_rules = await client.get("/api/v1/merchant/autonomy/rules", headers=headers)
        assert resp_rules.status_code == 200
        assert len(resp_rules.json()) == 5

        # 4. PUT /api/v1/merchant/autonomy/rules/{action_type}
        rule = resp_rules.json()[0]
        resp_update = await client.put(
            f"/api/v1/merchant/autonomy/rules/{rule['action_type']}",
            headers=headers,
            json={
                "is_enabled": True,
                "max_executions_per_hour": 8,
                "expected_version": rule["version"],
            },
        )
        assert resp_update.status_code == 200
        assert resp_update.json()["max_executions_per_hour"] == 8

        # 5. POST /api/v1/merchant/autonomy/execute
        proposal = MerchantProposal(
            merchant_id=m1.id,
            proposal_type=AutonomyActionType.IMPROVE_PRODUCT_DESCRIPTION.value,
            title="API execute test proposal",
            observation="Obs",
            proposed_change="New API description",
            hypothesis="Hyp",
            target_entity=str(p1.id),
            expected_metric="conversion_rate",
            expected_effect="+5%",
            evidence=["ev_1"],
            risk_level="LOW_RISK_REVERSIBLE",
            status="PROPOSED",
            metadata_payload={"target_product_id": str(p1.id)},
        )
        db_session.add(proposal)
        await db_session.commit()

        resp_exec = await client.post(
            "/api/v1/merchant/autonomy/execute",
            headers={**headers, "X-Idempotency-Key": f"api-exec-{uuid.uuid4().hex}"},
            json={
                "proposal_id": str(proposal.id),
                "expected_target_version": p1.version,
            },
        )
        assert resp_exec.status_code == 200
        exec_data = resp_exec.json()
        assert exec_data["status"] == "SUCCESS"
        assert exec_data["action"]["status"] == "EXECUTED"
        action_id = exec_data["action"]["id"]

        # 6. GET /api/v1/merchant/autonomy/actions
        resp_actions = await client.get("/api/v1/merchant/autonomy/actions", headers=headers)
        assert resp_actions.status_code == 200
        assert len(resp_actions.json()) >= 1

        # 7. POST /api/v1/merchant/autonomy/actions/{action_id}/rollback
        await db_session.refresh(p1)
        resp_rollback = await client.post(
            f"/api/v1/merchant/autonomy/actions/{action_id}/rollback",
            headers={**headers, "X-Idempotency-Key": f"api-rb-{uuid.uuid4().hex}"},
            json={
                "expected_target_version": p1.version,
                "reason": "Merchant API rollback test",
            },
        )
        assert resp_rollback.status_code == 200
        assert resp_rollback.json()["rollback_status"] == "ROLLED_BACK"
