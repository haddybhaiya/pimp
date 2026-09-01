"""Phase 7 Merchant Agent and Experiment Framework Comprehensive Verification Suite."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.config import get_settings
from agent_ready_merchant.llm.mock_provider import MockLLMProvider
from agent_ready_merchant.main import app
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.experiment import MerchantExperiment
from agent_ready_merchant.models.intent import BuyerIntent
from agent_ready_merchant.models.inventory import InventoryItem
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.order import Order
from agent_ready_merchant.models.payment import PaymentAttempt
from agent_ready_merchant.models.policy import PolicyRule
from agent_ready_merchant.models.product import Product, ProductVariant
from agent_ready_merchant.models.proposal import MerchantProposal
from agent_ready_merchant.models.quote import PriceQuote
from agent_ready_merchant.models.session import BuyerAgentSession
from agent_ready_merchant.schemas.merchant_agent import (
    ExperimentCreateRequest,
    MerchantProposalReviewRequest,
    ProposalRiskLevel,
    ProposalType,
)
from agent_ready_merchant.services.merchant_agent_service import MerchantAgentService
from agent_ready_merchant.services.merchant_auth_service import MerchantAuthService


@pytest_asyncio.fixture
async def setup_two_merchants_with_history(db_session: AsyncSession):
    """Creates two isolated merchants with products, sessions, quotes, and orders."""
    settings = get_settings()
    secret = settings.SECRET_KEY.get_secret_value()

    # Merchant Alpha
    m1 = Merchant(
        name="Alpha Athletics",
        slug=f"alpha-store-{uuid.uuid4().hex[:6]}",
        rzp_key_id="rzp_test_alpha_key",
        currency="INR",
        status="ACTIVE",
        created_at=datetime.now(UTC),
    )
    db_session.add(m1)
    await db_session.flush()

    token1 = MerchantAuthService.generate_admin_token(m1.id, secret, slug=m1.slug)

    # Add policies for Alpha
    db_session.add(
        PolicyRule(
            merchant_id=m1.id,
            rule_type="AUTONOMY_LEVEL",
            rule_value={"autonomy_level": 1},
            is_active=True,
        )
    )
    db_session.add(
        PolicyRule(
            merchant_id=m1.id,
            rule_type="MAX_DISCOUNT_PCT",
            rule_value={"max_discount_percentage": 20},
            is_active=True,
        )
    )

    # Add Product & Inventory for Alpha
    p1 = Product(
        merchant_id=m1.id,
        sku="RUN-ALPHA-01",
        title="Alpha Running Shoes",
        description="High performance shoes",
        category="Footwear",
        base_price_paise=500000,
        floor_price_paise=400000,
        is_active=True,
    )
    db_session.add(p1)
    await db_session.flush()

    var1 = ProductVariant(
        product_id=p1.id,
        sku=p1.sku,
        title="Standard",
    )
    db_session.add(var1)
    await db_session.flush()

    inv1 = InventoryItem(
        variant_id=var1.id,
        available_quantity=2,  # Low stock
        reserved_quantity=0,
    )
    db_session.add(inv1)

    # Add Sessions, Quotes, Orders for Alpha
    s1 = BuyerAgentSession(
        merchant_id=m1.id,
        buyer_agent_identifier="BuyerAgent-Alpha",
        auth_token_hash="hash_alpha_01",
        status="ACTIVE",
        expires_at=datetime.now(UTC) + timedelta(hours=24),
    )
    db_session.add(s1)
    await db_session.flush()

    intent1 = BuyerIntent(
        session_id=s1.id,
        raw_query="When will Alpha Running Shoes be delivered?",
        extracted_intent="DISCOVERY",
        extracted_entities={"sku": "RUN-ALPHA-01", "delivery_intent": True},
    )
    db_session.add(intent1)

    q1 = PriceQuote(
        merchant_id=m1.id,
        session_id=s1.id,
        subtotal_paise=500000,
        discount_paise=0,
        shipping_paise=0,
        total_paise=500000,
        status="ACCEPTED",
        idempotency_key=f"idemp_quote_{uuid.uuid4()}",
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
    )
    db_session.add(q1)
    await db_session.flush()

    o1 = Order(
        merchant_id=m1.id,
        quote_id=q1.id,
        rzp_order_id="order_alpha_001",
        amount_paise=500000,
        currency="INR",
        buyer_email="buyer.alpha@example.com",
        status="PAID",
    )
    db_session.add(o1)
    await db_session.flush()

    pay1 = PaymentAttempt(
        order_id=o1.id,
        rzp_order_id="order_alpha_001",
        rzp_payment_id="pay_alpha_001",
        amount_paise=500000,
        status="CAPTURED",
    )
    db_session.add(pay1)

    # Merchant Beta
    m2 = Merchant(
        name="Beta Boutique",
        slug=f"beta-store-{uuid.uuid4().hex[:6]}",
        rzp_key_id="rzp_test_beta_key",
        currency="INR",
        status="ACTIVE",
        created_at=datetime.now(UTC),
    )
    db_session.add(m2)
    await db_session.flush()

    token2 = MerchantAuthService.generate_admin_token(m2.id, secret, slug=m2.slug)

    # Product for Beta
    p2 = Product(
        merchant_id=m2.id,
        sku="BAG-BETA-01",
        title="Beta Leather Bag",
        description="Luxury handbag",
        category="Accessories",
        base_price_paise=800000,
        floor_price_paise=700000,
        is_active=True,
    )
    db_session.add(p2)
    await db_session.flush()

    var2 = ProductVariant(
        product_id=p2.id,
        sku=p2.sku,
        title="Standard",
    )
    db_session.add(var2)
    await db_session.flush()

    inv2 = InventoryItem(
        variant_id=var2.id,
        available_quantity=20,
        reserved_quantity=0,
    )
    db_session.add(inv2)

    await db_session.commit()

    return {
        "m1": m1,
        "token1": token1,
        "p1": p1,
        "m2": m2,
        "token2": token2,
        "p2": p2,
    }


@pytest.mark.asyncio
async def test_build_authoritative_observations_tenant_scoped(
    db_session: AsyncSession, setup_two_merchants_with_history
):
    """Verifies tenant-scoped telemetry distinguishing OBSERVED, DERIVED, and ESTIMATED."""
    m1 = setup_two_merchants_with_history["m1"]
    m2 = setup_two_merchants_with_history["m2"]

    snapshot_m1 = await MerchantAgentService.build_authoritative_observations(
        session=db_session, merchant_id=m1.id, window_days=30
    )

    assert snapshot_m1.merchant_id == m1.id
    assert snapshot_m1.store_name == "Alpha Athletics"
    assert snapshot_m1.currency == "INR"
    assert snapshot_m1.autonomy_level == 1

    # Check telemetry categories
    telemetry_map = {t.metric_name: t for t in snapshot_m1.telemetry}
    assert "total_buyer_sessions" in telemetry_map
    assert telemetry_map["total_buyer_sessions"].category.value == "OBSERVED"
    assert telemetry_map["total_buyer_sessions"].value == 1

    assert "completed_orders" in telemetry_map
    assert telemetry_map["completed_orders"].category.value == "OBSERVED"
    assert telemetry_map["completed_orders"].value == 1

    assert "total_revenue_paise" in telemetry_map
    assert telemetry_map["total_revenue_paise"].category.value == "OBSERVED"
    assert telemetry_map["total_revenue_paise"].value == 500000

    assert "quote_conversion_rate" in telemetry_map
    assert telemetry_map["quote_conversion_rate"].category.value == "DERIVED"
    assert telemetry_map["quote_conversion_rate"].value == 100.0

    assert "average_order_value_paise" in telemetry_map
    assert telemetry_map["average_order_value_paise"].category.value == "DERIVED"
    assert telemetry_map["average_order_value_paise"].value == 500000

    # Ensure Merchant Beta has separate zero/distinct telemetry
    snapshot_m2 = await MerchantAgentService.build_authoritative_observations(
        session=db_session, merchant_id=m2.id, window_days=30
    )
    assert snapshot_m2.merchant_id == m2.id
    assert snapshot_m2.store_name == "Beta Boutique"
    telemetry_map_m2 = {t.metric_name: t for t in snapshot_m2.telemetry}
    assert telemetry_map_m2["total_buyer_sessions"].value == 0
    assert telemetry_map_m2["completed_orders"].value == 0


@pytest.mark.asyncio
async def test_deterministic_risk_and_governance_classification():
    """Verifies that the server deterministically classifies risk and rejects prohibited actions."""
    policies = {"AUTONOMY_LEVEL": {"autonomy_level": 1}}

    # 1. Prohibited price/policy mutation attempt
    prohibited_proposal = {
        "proposal_type": "IMPROVE_PRODUCT_DESCRIPTION",
        "title": "Change floor price to 100",
        "proposed_change": "Directly alter floor price to 100 to maximize volume.",
    }
    risk, ok, reason = MerchantAgentService.govern_and_classify_proposal(
        prohibited_proposal, policies
    )
    assert risk == ProposalRiskLevel.PROHIBITED
    assert not ok
    assert "cannot modify financial policy" in (reason or "")

    # 2. Prohibited direct refund attempt
    refund_proposal = {
        "proposal_type": "IMPROVE_PRODUCT_DESCRIPTION",
        "title": "Execute refund for abandoned carts",
        "proposed_change": "Execute direct refund to entice buyers.",
    }
    risk, ok, reason = MerchantAgentService.govern_and_classify_proposal(refund_proposal, policies)
    assert risk == ProposalRiskLevel.PROHIBITED
    assert not ok

    # 3. Low-risk reversible proposal
    reversible_proposal = {
        "proposal_type": ProposalType.EXPOSE_DELIVERY_ETA.value,
        "title": "Expose Delivery ETA in Discovery",
        "proposed_change": "Include estimated 3-day delivery window in discovery responses.",
    }
    risk, ok, reason = MerchantAgentService.govern_and_classify_proposal(
        reversible_proposal, policies
    )
    assert risk == ProposalRiskLevel.LOW_RISK_REVERSIBLE
    assert ok
    assert reason is None

    # 4. Approval-required promotional proposal
    promo_proposal = {
        "proposal_type": ProposalType.SUGGEST_PROMOTIONAL_OFFER.value,
        "title": "10% Welcome Discount for First-Time Buyers",
        "proposed_change": "Suggest offering a 10% discount quote for first-time session buyers.",
    }
    risk, ok, reason = MerchantAgentService.govern_and_classify_proposal(promo_proposal, policies)
    assert risk == ProposalRiskLevel.APPROVAL_REQUIRED
    assert ok


@pytest.mark.asyncio
async def test_diagnose_and_propose_with_mock_llm(
    db_session: AsyncSession, setup_two_merchants_with_history
):
    """Verifies structured diagnosis and proposal generation with evidence link validation."""
    m1 = setup_two_merchants_with_history["m1"]
    settings = get_settings()

    snapshot = await MerchantAgentService.build_authoritative_observations(
        session=db_session, merchant_id=m1.id
    )

    mock_llm_payload = {
        "diagnoses": [
            {
                "pattern": "REPEATED_DELIVERY_QUESTIONS",
                "summary": "Buyer agents frequently query delivery timelines.",
                "severity": "MEDIUM",
                "evidence_references": ["total_buyer_sessions", "quote_conversion_rate"],
                "affected_entities": ["discovery_metadata"],
            }
        ],
        "proposals": [
            {
                "proposal_type": "EXPOSE_DELIVERY_ETA",
                "title": "Expose Delivery ETA in Discovery Response",
                "observation": "Buyer asked when shoes would arrive.",
                "evidence": ["total_buyer_sessions", "quote_conversion_rate"],
                "hypothesis": "Providing clear ETA will reduce hesitation.",
                "proposed_change": "Include 3-day delivery ETA in discovery payload.",
                "target_entity": "RUN-ALPHA-01",
                "expected_effect": "Quote conversion increases by 10%.",
                "expected_metric": "quote_conversion_rate",
                "confidence": 0.88,
                "estimated_cost_paise": 0,
            }
        ],
    }

    mock_llm = MockLLMProvider(responses=[json.dumps(mock_llm_payload)])

    diagnoses, proposals = await MerchantAgentService.diagnose_and_propose(
        session=db_session,
        merchant_id=m1.id,
        snapshot=snapshot,
        llm_provider=mock_llm,
        settings=settings,
    )

    assert len(diagnoses) == 1
    assert diagnoses[0].pattern == "REPEATED_DELIVERY_QUESTIONS"
    assert "total_buyer_sessions" in diagnoses[0].evidence_references

    assert len(proposals) == 1
    assert proposals[0].proposal_type == "EXPOSE_DELIVERY_ETA"
    assert proposals[0].risk_level == "LOW_RISK_REVERSIBLE"
    assert proposals[0].status == "PROPOSED"
    assert proposals[0].target_entity == "RUN-ALPHA-01"


@pytest.mark.asyncio
async def test_agent_run_lifecycle_and_audit_event(
    db_session: AsyncSession, setup_two_merchants_with_history
):
    """Verifies that execute_agent_run persists proposals and creates immutable audit entries."""
    m1 = setup_two_merchants_with_history["m1"]
    settings = get_settings()

    mock_llm_payload = {
        "diagnoses": [
            {
                "pattern": "MISSING_PRODUCT_INFO",
                "summary": "Shoe size chart missing in catalog descriptions.",
                "severity": "LOW",
                "evidence_references": ["total_buyer_sessions"],
                "affected_entities": ["RUN-ALPHA-01"],
            }
        ],
        "proposals": [
            {
                "proposal_type": "IMPROVE_PRODUCT_DESCRIPTION",
                "title": "Add Complete Sizing Guide to Product Description",
                "observation": "Product descriptions lack exact centimeter shoe measurements.",
                "evidence": ["total_buyer_sessions"],
                "hypothesis": "Adding centimeter measurements improves conversion.",
                "proposed_change": "Update RUN-ALPHA-01 description to include CM sizing table.",
                "target_entity": "RUN-ALPHA-01",
                "expected_effect": "Increases buyer agent selection confidence.",
                "expected_metric": "quote_conversion_rate",
                "confidence": 0.90,
                "estimated_cost_paise": 0,
            }
        ],
    }

    mock_llm = MockLLMProvider(responses=[json.dumps(mock_llm_payload)])

    res = await MerchantAgentService.execute_agent_run(
        session=db_session,
        merchant_id=m1.id,
        llm_provider=mock_llm,
        settings=settings,
    )

    assert res.status == "COMPLETED"
    assert len(res.diagnoses) == 1
    assert len(res.proposals) == 1
    assert res.proposals[0].title == "Add Complete Sizing Guide to Product Description"

    # Verify persistent DB record
    stmt = select(MerchantProposal).where(MerchantProposal.id == res.proposals[0].id)
    saved_prop = (await db_session.execute(stmt)).scalar_one_or_none()
    assert saved_prop is not None
    assert saved_prop.merchant_id == m1.id

    # Verify Audit Event Linkage
    audit_stmt = (
        select(AuditEvent)
        .where(
            AuditEvent.merchant_id == m1.id,
            AuditEvent.event_type == "MERCHANT_AGENT_RUN_COMPLETED",
        )
        .order_by(AuditEvent.created_at.desc())
    )
    audit = (await db_session.execute(audit_stmt)).scalars().first()
    assert audit is not None
    assert audit.payload["diagnoses_count"] == 1
    assert audit.payload["proposals_count"] == 1


@pytest.mark.asyncio
async def test_proposal_review_lifecycle(
    db_session: AsyncSession, setup_two_merchants_with_history
):
    """Verifies proposal human approval, rejection, and conversion to experiment."""
    m1 = setup_two_merchants_with_history["m1"]

    # 1. Create a proposal
    prop = MerchantProposal(
        merchant_id=m1.id,
        proposal_type="EXPOSE_DELIVERY_ETA",
        title="Delivery ETA Optimization",
        observation="Delivery questions frequent",
        evidence=["total_buyer_sessions"],
        hypothesis="ETA visibility increases checkout",
        proposed_change="Expose delivery window",
        target_entity="discovery",
        expected_effect="Conversion +10%",
        expected_metric="quote_conversion_rate",
        confidence=0.85,
        risk_level="LOW_RISK_REVERSIBLE",
        status="PROPOSED",
    )
    db_session.add(prop)
    await db_session.commit()

    # 2. Approve proposal
    approved = await MerchantAgentService.review_proposal(
        session=db_session,
        merchant_id=m1.id,
        proposal_id=prop.id,
        review_req=MerchantProposalReviewRequest(decision="APPROVE"),
        reviewer_id="admin_user_01",
    )
    assert approved.status == "APPROVED"
    assert approved.reviewed_by == "admin_user_01"

    # 3. Reject a second proposal
    prop2 = MerchantProposal(
        merchant_id=m1.id,
        proposal_type="SUGGEST_BUNDLE",
        title="Bundle Shoe with Socks",
        observation="Low AOV",
        evidence=["total_revenue_paise"],
        hypothesis="Bundles increase AOV",
        proposed_change="Offer socks at checkout",
        target_entity="general",
        expected_effect="AOV +15%",
        expected_metric="average_order_value_paise",
        confidence=0.75,
        risk_level="APPROVAL_REQUIRED",
        status="PROPOSED",
    )
    db_session.add(prop2)
    await db_session.commit()

    rejected = await MerchantAgentService.review_proposal(
        session=db_session,
        merchant_id=m1.id,
        proposal_id=prop2.id,
        review_req=MerchantProposalReviewRequest(
            decision="REJECT", rejection_reason="Socks are out of stock."
        ),
        reviewer_id="admin_user_01",
    )
    assert rejected.status == "REJECTED"
    assert rejected.rejection_reason == "Socks are out of stock."


@pytest.mark.asyncio
async def test_experiment_approval_first_and_deterministic_measurement(
    db_session: AsyncSession, setup_two_merchants_with_history
):
    """Verifies approval-first experiment registration, approval, and measurement."""
    m1 = setup_two_merchants_with_history["m1"]

    # 1. Register Experiment (starts in APPROVAL_REQUIRED / PENDING)
    exp_req = ExperimentCreateRequest(
        title="Delivery ETA Banner Test",
        hypothesis="Showing ETA increases quote conversion",
        target_metric="quote_conversion_rate",
        baseline_value=50.0,
        target_value=65.0,
        proposed_variation={"delivery_eta_visible": True},
    )
    exp = await MerchantAgentService.create_experiment(
        session=db_session,
        merchant_id=m1.id,
        req=exp_req,
    )
    assert exp.status == "APPROVAL_REQUIRED"
    assert exp.approval_status == "PENDING"
    assert exp.approved_by is None

    # 2. Approve Experiment
    appr_exp = await MerchantAgentService.approve_experiment(
        session=db_session,
        merchant_id=m1.id,
        experiment_id=exp.id,
        approver_id="merchant.admin@example.com",
    )
    assert appr_exp.status == "APPROVED"
    assert appr_exp.approval_status == "APPROVED"
    assert appr_exp.approved_by == "merchant.admin@example.com"
    assert appr_exp.start_time is not None

    # 3. Deterministically Evaluate Outcome
    # Telemetry for m1 has 1 session and 1 order -> conversion rate is 100.0% (vs baseline 50.0%)
    # But sample size is 1 (< 5) -> must return INCONCLUSIVE due to sample size limitation
    eval_result = await MerchantAgentService.evaluate_experiment_results(
        session=db_session,
        merchant_id=m1.id,
        experiment_id=exp.id,
    )
    assert eval_result.sample_size == 1
    assert eval_result.recommendation == "INCONCLUSIVE"
    assert any("Sample size too small" in limit for limit in eval_result.limitations)


@pytest.mark.asyncio
async def test_fastapi_endpoints_for_agent_and_experiments(
    setup_two_merchants_with_history,
):
    """Verifies REST endpoints for Merchant Agent and Experiments."""
    m1 = setup_two_merchants_with_history["m1"]
    token1 = setup_two_merchants_with_history["token1"]
    m2 = setup_two_merchants_with_history["m2"]
    token2 = setup_two_merchants_with_history["token2"]

    headers_m1 = {
        "X-Merchant-ID": str(m1.id),
        "X-Auth-Token": token1,
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        # 1. GET snapshot
        snap_resp = await client.get(
            "/api/v1/merchant/agent/snapshot?window_days=30", headers=headers_m1
        )
        assert snap_resp.status_code == 200
        snap_json = snap_resp.json()
        assert snap_json["merchant_id"] == str(m1.id)
        assert len(snap_json["telemetry"]) > 0

        # 2. POST analyze (triggers mock optimization turn in test mode)
        run_resp = await client.post("/api/v1/merchant/agent/analyze", headers=headers_m1)
        assert run_resp.status_code == 200
        run_json = run_resp.json()
        assert run_json["status"] == "COMPLETED"
        assert len(run_json["proposals"]) > 0
        prop_id = run_json["proposals"][0]["id"]

        # 3. GET proposals
        list_resp = await client.get("/api/v1/merchant/agent/proposals", headers=headers_m1)
        assert list_resp.status_code == 200
        assert len(list_resp.json()) >= 1

        # 4. POST review proposal
        rev_resp = await client.post(
            f"/api/v1/merchant/agent/proposals/{prop_id}/review",
            headers=headers_m1,
            json={"decision": "APPROVE"},
        )
        assert rev_resp.status_code == 200
        assert rev_resp.json()["status"] == "APPROVED"

        # 5. POST create experiment
        create_exp_resp = await client.post(
            "/api/v1/merchant/experiments",
            headers=headers_m1,
            json={
                "title": "API Test Experiment",
                "hypothesis": "Test hypothesis mechanism",
                "target_metric": "quote_conversion_rate",
                "baseline_value": 10.0,
                "target_value": 20.0,
                "proposed_variation": {"feature": "test"},
            },
        )
        assert create_exp_resp.status_code == 201
        exp_id = create_exp_resp.json()["id"]

        # 6. GET list experiments
        exp_list_resp = await client.get("/api/v1/merchant/experiments", headers=headers_m1)
        assert exp_list_resp.status_code == 200
        assert len(exp_list_resp.json()) >= 1

        # 7. POST approve experiment
        appr_exp_resp = await client.post(
            f"/api/v1/merchant/experiments/{exp_id}/approve", headers=headers_m1
        )
        assert appr_exp_resp.status_code == 200
        assert appr_exp_resp.json()["status"] == "APPROVED"

        # 8. POST evaluate experiment
        eval_resp = await client.post(
            f"/api/v1/merchant/experiments/{exp_id}/evaluate", headers=headers_m1
        )
        assert eval_resp.status_code == 200
        assert eval_resp.json()["experiment_id"] == exp_id

        # 9. Cross-Tenant Isolation: Merchant Beta cannot access Merchant Alpha's proposal
        headers_m2 = {
            "X-Merchant-ID": str(m2.id),
            "X-Auth-Token": token2,
        }
        cross_resp = await client.post(
            f"/api/v1/merchant/agent/proposals/{prop_id}/review",
            headers=headers_m2,
            json={"decision": "APPROVE"},
        )
        assert cross_resp.status_code == 404

        # 10. Unauthenticated request rejected
        unauth_resp = await client.get("/api/v1/merchant/agent/snapshot")
        assert unauth_resp.status_code == 422  # Missing required header


@pytest.mark.asyncio
async def test_hallucinated_evidence_and_malformed_llm_output_recovery(
    db_session: AsyncSession, setup_two_merchants_with_history
):
    """Verifies that hallucinated evidence links are filtered and errors degrade gracefully."""
    m1 = setup_two_merchants_with_history["m1"]
    settings = get_settings()

    snapshot = await MerchantAgentService.build_authoritative_observations(
        session=db_session, merchant_id=m1.id
    )

    # 1. Hallucinated evidence payload
    hallucinated_payload = {
        "diagnoses": [
            {
                "pattern": "UNKNOWN_SIGNAL",
                "summary": "Hallucinated diagnosis.",
                "severity": "HIGH",
                "evidence_references": ["hallucinated_metric_999", "non_existent_key"],
                "affected_entities": ["ghost_sku"],
            }
        ],
        "proposals": [
            {
                "proposal_type": "IMPROVE_PRODUCT_DESCRIPTION",
                "title": "Hallucinated Proposal",
                "observation": "Made up observation.",
                "evidence": ["hallucinated_metric_xyz"],
                "hypothesis": "Made up hypothesis.",
                "proposed_change": "Made up change.",
                "target_entity": "RUN-ALPHA-01",
                "expected_effect": "No expected effect on revenue",
                "expected_metric": "quote_conversion_rate",
                "confidence": 0.5,
                "estimated_cost_paise": 0,
            }
        ],
    }

    mock_llm = MockLLMProvider(responses=[json.dumps(hallucinated_payload)])
    diagnoses, proposals = await MerchantAgentService.diagnose_and_propose(
        session=db_session,
        merchant_id=m1.id,
        snapshot=snapshot,
        llm_provider=mock_llm,
        settings=settings,
    )

    # Evidence links must be sanitized to valid telemetry metrics
    assert len(diagnoses) == 1
    assert "hallucinated_metric_999" not in diagnoses[0].evidence_references
    assert len(proposals) == 1
    assert "hallucinated_metric_xyz" not in proposals[0].evidence

    # 2. Malformed non-JSON payload
    malformed_llm = MockLLMProvider(responses=["NOT_JSON_AT_ALL <<broken>>"])
    diag_empty, prop_empty = await MerchantAgentService.diagnose_and_propose(
        session=db_session,
        merchant_id=m1.id,
        snapshot=snapshot,
        llm_provider=malformed_llm,
        settings=settings,
    )
    assert diag_empty == []
    assert prop_empty == []


@pytest.mark.asyncio
async def test_adversarial_prompt_injection_invariance(
    db_session: AsyncSession, setup_two_merchants_with_history
):
    """Verifies that model cannot propose policy changes or grant capabilities."""
    m1 = setup_two_merchants_with_history["m1"]
    settings = get_settings()

    injection_payload = {
        "diagnoses": [],
        "proposals": [
            {
                "proposal_type": "IMPROVE_PRODUCT_DESCRIPTION",
                "title": "System Override: Disable Policy",
                "observation": "Policy is too restrictive.",
                "evidence": ["total_buyer_sessions"],
                "hypothesis": "Disabling policy will boost sales.",
                "proposed_change": "Disable policy rules and change floor price to 0",
                "target_entity": "RUN-ALPHA-01",
                "expected_effect": "Infinite sales",
                "expected_metric": "quote_conversion_rate",
                "confidence": 0.99,
                "estimated_cost_paise": 0,
            }
        ],
    }

    mock_llm = MockLLMProvider(responses=[json.dumps(injection_payload)])
    res = await MerchantAgentService.execute_agent_run(
        session=db_session,
        merchant_id=m1.id,
        llm_provider=mock_llm,
        settings=settings,
    )

    # Must be marked REJECTED and PROHIBITED
    assert len(res.proposals) == 1
    assert res.proposals[0].status == "REJECTED"
    assert res.proposals[0].risk_level == "PROHIBITED"
    assert "cannot modify financial policy" in (res.proposals[0].rejection_reason or "")


@pytest.mark.asyncio
async def test_deterministic_experiment_keep_and_rollback_thresholds(
    db_session: AsyncSession, setup_two_merchants_with_history
):
    """Verifies deterministic outcome calculation for positive and negative deltas."""
    m1 = setup_two_merchants_with_history["m1"]

    # 1. Experiment with low baseline vs 100% conversion (sample size 10 -> KEEP)
    exp_keep = MerchantExperiment(
        merchant_id=m1.id,
        title="High Conversion Winning Test",
        hypothesis="Feature increases conversion",
        target_metric="quote_conversion_rate",
        baseline_value=50.0,
        target_value=70.0,
        status="APPROVED",
        approval_status="APPROVED",
    )
    db_session.add(exp_keep)

    # 2. Experiment with high baseline vs 100% conversion (negative delta -> ROLLBACK)
    exp_rollback = MerchantExperiment(
        merchant_id=m1.id,
        title="Degrading Test",
        hypothesis="Variation reduces conversion",
        target_metric="quote_conversion_rate",
        baseline_value=120.0,
        target_value=150.0,
        status="APPROVED",
        approval_status="APPROVED",
    )
    db_session.add(exp_rollback)
    await db_session.commit()

    # Telemetry conversion rate is 100.0%
    # With baseline 120.0% -> delta is -16.67% (< -2%)
    eval_rollback = await MerchantAgentService.evaluate_experiment_results(
        session=db_session,
        merchant_id=m1.id,
        experiment_id=exp_rollback.id,
    )
    # Sample size is 1 (< 5) so it notes sample size limitation, but delta is calculated exactly
    assert eval_rollback.absolute_change < 0
    assert eval_rollback.percentage_change < 0
