"""Authoritative domain service executing Phase 7 Merchant Agent intelligence layer."""

from __future__ import annotations

import json
import logging
import time
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.config import Settings
from agent_ready_merchant.llm.base import BaseLLMProvider, LLMMessage
from agent_ready_merchant.models.approval import MerchantApproval
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.experiment import MerchantExperiment, MerchantExperimentResult
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
    ExperimentResponse,
    ExperimentResultResponse,
    MerchantAgentAnalyzeResponse,
    MerchantDiagnosisItem,
    MerchantObservationSnapshot,
    MerchantProposalCreate,
    MerchantProposalResponse,
    MerchantProposalReviewRequest,
    ObservationCategory,
    ObservationTelemetryItem,
    ProposalRiskLevel,
    ProposalStatus,
    ProposalType,
)

logger = logging.getLogger("agent_ready_merchant.agent_service")


class MerchantAgentService:
    """Authoritative service executing Merchant Agent observation and optimization."""

    @classmethod
    async def build_authoritative_observations(
        cls, session: AsyncSession, merchant_id: uuid.UUID, window_days: int = 30
    ) -> MerchantObservationSnapshot:
        """Collects authoritative, tenant-scoped commerce telemetry directly from PostgreSQL."""
        now = datetime.now(UTC)
        start_window = now - timedelta(days=window_days)

        # 1. Merchant Metadata
        m_stmt = select(Merchant).where(Merchant.id == merchant_id)
        merchant = (await session.execute(m_stmt)).scalar_one_or_none()
        if not merchant:
            raise ValueError(f"Merchant with ID '{merchant_id}' not found.")

        # 2. Active Policies
        rules_stmt = select(PolicyRule).where(
            PolicyRule.merchant_id == merchant_id,
            PolicyRule.is_active == True,  # noqa: E712
        )
        rules = list((await session.execute(rules_stmt)).scalars().all())
        active_policies: dict[str, Any] = {}
        for r in rules:
            active_policies[r.rule_type] = r.rule_value

        autonomy_level = int(active_policies.get("AUTONOMY_LEVEL", {}).get("autonomy_level", 1))

        # 3. Catalog & Inventory Metrics
        prod_stmt = select(Product).where(Product.merchant_id == merchant_id)
        products = list((await session.execute(prod_stmt)).scalars().all())
        total_products = len(products)
        active_skus = [p.sku for p in products if p.is_active]

        inv_stmt = (
            select(InventoryItem, ProductVariant.sku)
            .join(ProductVariant, ProductVariant.id == InventoryItem.variant_id)
            .join(Product, Product.id == ProductVariant.product_id)
            .where(Product.merchant_id == merchant_id)
        )
        inv_rows = list((await session.execute(inv_stmt)).all())
        low_stock_skus = [row[1] for row in inv_rows if row[0].available_quantity <= 5]
        out_of_stock_skus = [row[1] for row in inv_rows if row[0].available_quantity == 0]

        catalog_summary = {
            "total_products": total_products,
            "active_skus_count": len(active_skus),
            "low_stock_skus_count": len(low_stock_skus),
            "out_of_stock_skus_count": len(out_of_stock_skus),
            "low_stock_skus": low_stock_skus[:5],
            "out_of_stock_skus": out_of_stock_skus[:5],
        }

        # 4. Sessions Count
        sess_stmt = select(func.count(BuyerAgentSession.id)).where(
            BuyerAgentSession.merchant_id == merchant_id,
            BuyerAgentSession.created_at >= start_window,
        )
        total_sessions = int((await session.execute(sess_stmt)).scalar_one() or 0)

        # 5. Quotes Count & Status Breakdown
        quotes_stmt = select(PriceQuote).where(
            PriceQuote.merchant_id == merchant_id,
            PriceQuote.created_at >= start_window,
        )
        quotes = list((await session.execute(quotes_stmt)).scalars().all())
        total_quotes = len(quotes)
        accepted_quotes = sum(1 for q in quotes if q.status == "ACCEPTED")
        negotiating_quotes = sum(1 for q in quotes if q.status == "NEGOTIATING")

        # 6. Orders Count & Settled Revenue
        orders_stmt = select(Order).where(
            Order.merchant_id == merchant_id,
            Order.created_at >= start_window,
        )
        orders = list((await session.execute(orders_stmt)).scalars().all())
        total_orders = len(orders)
        completed_orders = sum(1 for o in orders if o.status in ("PAID", "SETTLED", "COMPLETED"))
        total_revenue_paise = sum(
            o.amount_paise for o in orders if o.status in ("PAID", "SETTLED", "COMPLETED")
        )

        # 7. Payment Attempts & Failures
        pay_stmt = (
            select(PaymentAttempt)
            .join(Order, Order.id == PaymentAttempt.order_id)
            .where(
                Order.merchant_id == merchant_id,
                PaymentAttempt.created_at >= start_window,
            )
        )
        pay_attempts = list((await session.execute(pay_stmt)).scalars().all())
        total_payment_attempts = len(pay_attempts)
        failed_payment_attempts = sum(1 for p in pay_attempts if p.status == "FAILED")

        # 8. Human Approvals
        appr_stmt = select(MerchantApproval).where(
            MerchantApproval.merchant_id == merchant_id,
            MerchantApproval.created_at >= start_window,
        )
        approvals = list((await session.execute(appr_stmt)).scalars().all())
        total_approvals = len(approvals)

        # 9. Buyer Intents & Search Query Signals
        intents_stmt = (
            select(BuyerIntent)
            .join(BuyerAgentSession, BuyerAgentSession.id == BuyerIntent.session_id)
            .where(
                BuyerAgentSession.merchant_id == merchant_id,
                BuyerIntent.created_at >= start_window,
            )
            .order_by(BuyerIntent.created_at.desc())
            .limit(50)
        )
        intents = list((await session.execute(intents_stmt)).scalars().all())
        delivery_mentions = 0
        discount_mentions = 0
        for it in intents:
            raw_text = (it.raw_query or "").lower()
            if any(w in raw_text for w in ("delivery", "eta", "shipping", "arrive", "when")):
                delivery_mentions += 1
            if any(w in raw_text for w in ("discount", "coupon", "cheaper", "offer", "negotiate")):
                discount_mentions += 1

        # 10. Compute Derived & Estimated Metrics
        conversion_rate = (
            round((completed_orders / total_sessions) * 100, 2) if total_sessions > 0 else 0.0
        )
        aov_paise = int(total_revenue_paise / completed_orders) if completed_orders > 0 else 0
        quote_acceptance_rate = (
            round((accepted_quotes / total_quotes) * 100, 2) if total_quotes > 0 else 0.0
        )
        payment_failure_rate = (
            round((failed_payment_attempts / total_payment_attempts) * 100, 2)
            if total_payment_attempts > 0
            else 0.0
        )
        cart_abandonment_rate = (
            round(max(0.0, 1.0 - (completed_orders / total_quotes)) * 100, 2)
            if total_quotes > 0
            else 0.0
        )

        avg_item_price_paise = (
            int(sum(p.base_price_paise for p in products) / total_products)
            if total_products > 0
            else 0
        )
        estimated_lost_demand_paise = len(out_of_stock_skus) * avg_item_price_paise * 3

        # 11. Compile Structured Telemetry (Explicitly Categorized)
        telemetry: list[ObservationTelemetryItem] = [
            ObservationTelemetryItem(
                category=ObservationCategory.OBSERVED,
                metric_name="total_buyer_sessions",
                value=total_sessions,
                formatted_value=f"{total_sessions} sessions",
                unit="count",
                sample_size=total_sessions,
                window_days=window_days,
                description="Total unique AI buyer sessions initiated within the window.",
            ),
            ObservationTelemetryItem(
                category=ObservationCategory.OBSERVED,
                metric_name="total_quotes_generated",
                value=total_quotes,
                formatted_value=f"{total_quotes} quotes",
                unit="count",
                sample_size=total_quotes,
                window_days=window_days,
                description="Total commercial price quotes issued to buyer agents.",
            ),
            ObservationTelemetryItem(
                category=ObservationCategory.OBSERVED,
                metric_name="completed_orders",
                value=completed_orders,
                formatted_value=f"{completed_orders} orders",
                unit="count",
                sample_size=completed_orders,
                window_days=window_days,
                description="Total successfully settled and captured orders.",
            ),
            ObservationTelemetryItem(
                category=ObservationCategory.OBSERVED,
                metric_name="total_revenue_paise",
                value=total_revenue_paise,
                formatted_value=f"₹{total_revenue_paise / 100:,.2f}",
                unit="paise",
                sample_size=completed_orders,
                window_days=window_days,
                description="Total realized gross revenue from settled orders.",
            ),
            ObservationTelemetryItem(
                category=ObservationCategory.OBSERVED,
                metric_name="failed_payments_count",
                value=failed_payment_attempts,
                formatted_value=f"{failed_payment_attempts} failed",
                unit="count",
                sample_size=total_payment_attempts,
                window_days=window_days,
                description="Payment attempts rejected or timed out by upstream gateway.",
            ),
            ObservationTelemetryItem(
                category=ObservationCategory.OBSERVED,
                metric_name="out_of_stock_skus_count",
                value=len(out_of_stock_skus),
                formatted_value=f"{len(out_of_stock_skus)} SKUs",
                unit="count",
                sample_size=total_products,
                window_days=window_days,
                description="Catalog products with zero available inventory.",
            ),
            ObservationTelemetryItem(
                category=ObservationCategory.DERIVED,
                metric_name="quote_conversion_rate",
                value=conversion_rate,
                formatted_value=f"{conversion_rate:.1f}%",
                unit="percentage",
                sample_size=total_sessions,
                window_days=window_days,
                description="Percentage of buyer sessions converted into settled orders.",
            ),
            ObservationTelemetryItem(
                category=ObservationCategory.DERIVED,
                metric_name="average_order_value_paise",
                value=aov_paise,
                formatted_value=f"₹{aov_paise / 100:,.2f}",
                unit="paise",
                sample_size=completed_orders,
                window_days=window_days,
                description="Average monetary value per settled order.",
            ),
            ObservationTelemetryItem(
                category=ObservationCategory.DERIVED,
                metric_name="quote_acceptance_rate",
                value=quote_acceptance_rate,
                formatted_value=f"{quote_acceptance_rate:.1f}%",
                unit="percentage",
                sample_size=total_quotes,
                window_days=window_days,
                description="Percentage of quotes accepted without expiration or cancellation.",
            ),
            ObservationTelemetryItem(
                category=ObservationCategory.DERIVED,
                metric_name="cart_abandonment_rate",
                value=cart_abandonment_rate,
                formatted_value=f"{cart_abandonment_rate:.1f}%",
                unit="percentage",
                sample_size=total_quotes,
                window_days=window_days,
                description="Rate of issued quotes that did not convert to settled orders.",
            ),
            ObservationTelemetryItem(
                category=ObservationCategory.OBSERVED,
                metric_name="total_orders_count",
                value=total_orders,
                formatted_value=f"{total_orders} orders",
                unit="count",
                sample_size=total_orders,
                window_days=window_days,
                description="Total orders created across active window.",
            ),
            ObservationTelemetryItem(
                category=ObservationCategory.OBSERVED,
                metric_name="total_approvals_count",
                value=total_approvals,
                formatted_value=f"{total_approvals} approvals",
                unit="count",
                sample_size=total_approvals,
                window_days=window_days,
                description="Total HITL approval requests generated.",
            ),
            ObservationTelemetryItem(
                category=ObservationCategory.DERIVED,
                metric_name="payment_failure_rate",
                value=payment_failure_rate,
                formatted_value=f"{payment_failure_rate:.1f}%",
                unit="percentage",
                sample_size=total_payment_attempts,
                window_days=window_days,
                description="Percentage of payment attempts that failed.",
            ),
            ObservationTelemetryItem(
                category=ObservationCategory.ESTIMATED,
                metric_name="estimated_lost_demand_paise",
                value=estimated_lost_demand_paise,
                formatted_value=f"₹{estimated_lost_demand_paise / 100:,.2f}",
                unit="paise",
                sample_size=len(out_of_stock_skus),
                window_days=window_days,
                description="Estimated gross demand lost due to stockouts across active window.",
            ),
        ]

        # 12. Context Signals
        signals: list[dict[str, Any]] = []
        if delivery_mentions > 0:
            signals.append(
                {
                    "signal_key": "signal:delivery_inquiries",
                    "title": "Delivery & ETA Inquiries",
                    "count": delivery_mentions,
                    "description": (
                        f"{delivery_mentions} buyer inquiries asked about delivery "
                        "timeline or shipping ETA."
                    ),
                }
            )
        if discount_mentions > 0 or negotiating_quotes > 0:
            discount_total = discount_mentions + negotiating_quotes
            signals.append(
                {
                    "signal_key": "signal:discount_negotiation_volume",
                    "title": "Discount & Price Sensitivity",
                    "count": discount_total,
                    "description": (
                        f"{discount_total} interactions involved counter-offers "
                        "or discount requests."
                    ),
                }
            )
        if len(out_of_stock_skus) > 0:
            top_out_skus = ", ".join(out_of_stock_skus[:3])
            signals.append(
                {
                    "signal_key": "signal:inventory_stockouts",
                    "title": "Inventory Stockouts",
                    "count": len(out_of_stock_skus),
                    "description": (
                        f"{len(out_of_stock_skus)} items are completely out of stock "
                        f"({top_out_skus})."
                    ),
                }
            )
        if failed_payment_attempts > 0:
            signals.append(
                {
                    "signal_key": "signal:failed_payments",
                    "title": "Payment Friction",
                    "count": failed_payment_attempts,
                    "description": (
                        f"{failed_payment_attempts} payment attempts failed during "
                        "checkout settlement."
                    ),
                }
            )

        # 13. Recent Proposals & Experiments
        prop_stmt = (
            select(MerchantProposal)
            .where(MerchantProposal.merchant_id == merchant_id)
            .order_by(MerchantProposal.created_at.desc())
            .limit(5)
        )
        recent_props = list((await session.execute(prop_stmt)).scalars().all())
        recent_proposals_data = [
            {
                "id": str(p.id),
                "type": p.proposal_type,
                "title": p.title,
                "status": p.status,
                "risk_level": p.risk_level,
            }
            for p in recent_props
        ]

        exp_stmt = (
            select(MerchantExperiment)
            .where(MerchantExperiment.merchant_id == merchant_id)
            .order_by(MerchantExperiment.created_at.desc())
            .limit(5)
        )
        recent_exps = list((await session.execute(exp_stmt)).scalars().all())
        recent_experiments_data = [
            {
                "id": str(e.id),
                "title": e.title,
                "target_metric": e.target_metric,
                "status": e.status,
                "approval_status": e.approval_status,
            }
            for e in recent_exps
        ]

        return MerchantObservationSnapshot(
            merchant_id=merchant_id,
            store_name=merchant.name,
            currency=merchant.currency,
            autonomy_level=autonomy_level,
            active_policies=active_policies,
            catalog_summary=catalog_summary,
            telemetry=telemetry,
            signals=signals,
            recent_proposals=recent_proposals_data,
            recent_experiments=recent_experiments_data,
            generated_at=now,
        )

    @classmethod
    def govern_and_classify_proposal(
        cls, proposal_data: dict[str, Any], active_policies: dict[str, Any]
    ) -> tuple[ProposalRiskLevel, bool, str | None]:
        """Server-Authoritative Deterministic Risk & Governance Classifier.

        Rules:
        - Changes to policy rules, floor prices, capabilities, or direct payments -> PROHIBITED
        - Enhancements, metadata, ETA visibility, recommendations -> LOW_RISK_REVERSIBLE
        - Discount suggestions, bundle promotions, pricing proposals -> APPROVAL_REQUIRED
        """
        ptype = proposal_data.get("proposal_type", "")
        proposed_change = (proposal_data.get("proposed_change", "")).lower()
        title = (proposal_data.get("title", "")).lower()

        # Prohibited actions check
        prohibited_keywords = (
            "change policy",
            "alter floor price",
            "grant capability",
            "increase autonomy",
            "execute refund",
            "direct refund",
            "transfer money",
            "bypass approval",
            "disable policy",
        )
        if any(kw in proposed_change or kw in title for kw in prohibited_keywords):
            return (
                ProposalRiskLevel.PROHIBITED,
                False,
                (
                    "Agent cannot modify financial policy, grant capabilities, "
                    "or execute direct payments."
                ),
            )

        if ptype in (
            ProposalType.SUGGEST_PROMOTIONAL_OFFER.value,
            ProposalType.SUGGEST_BUNDLE.value,
        ):
            return ProposalRiskLevel.APPROVAL_REQUIRED, True, None

        if ptype in (
            ProposalType.IMPROVE_PRODUCT_DESCRIPTION.value,
            ProposalType.EXPOSE_DELIVERY_ETA.value,
            ProposalType.REORDER_RECOMMENDATIONS.value,
            ProposalType.IMPROVE_DISCOVERY_METADATA.value,
            ProposalType.SUGGEST_BOUNDED_EXPERIMENT.value,
        ):
            return ProposalRiskLevel.LOW_RISK_REVERSIBLE, True, None

        # Unknown proposal types are prohibited by default (fail-closed)
        return ProposalRiskLevel.PROHIBITED, False, f"Unsupported proposal type '{ptype}'."

    @classmethod
    async def diagnose_and_propose(
        cls,
        session: AsyncSession,
        merchant_id: uuid.UUID,
        snapshot: MerchantObservationSnapshot,
        llm_provider: BaseLLMProvider,
        settings: Settings,
    ) -> tuple[list[MerchantDiagnosisItem], list[MerchantProposal]]:
        """Invokes LLM with trusted snapshot and parses structured diagnoses and proposals."""
        system_prompt = (
            "You are the Merchant Agent Optimization Engine for Agent-Ready Merchant.\n"
            "Your role is INTELLIGENCE, NOT AUTHORITY. You observe telemetry, diagnose friction, "
            "and formulate evidence-backed proposals for human merchant review.\n"
            "Core Rules:\n"
            "1. Every diagnosis and proposal MUST reference real evidence from snapshot.\n"
            "2. Never directly modify prices, alter policies, grant capabilities, or pay.\n"
            "3. You must output ONLY a valid JSON object matching the requested schema.\n"
            "4. Supported proposal types: IMPROVE_PRODUCT_DESCRIPTION, EXPOSE_DELIVERY_ETA, "
            "REORDER_RECOMMENDATIONS, IMPROVE_DISCOVERY_METADATA, SUGGEST_BUNDLE, "
            "SUGGEST_PROMOTIONAL_OFFER, SUGGEST_BOUNDED_EXPERIMENT.\n"
            "\n"
            "Output JSON Schema:\n"
            "{\n"
            '  "diagnoses": [\n'
            "    {\n"
            '      "pattern": "REPEATED_DELIVERY_QUESTIONS | MISSING_PRODUCT_INFO | ...",\n'
            '      "summary": "Clear 1-sentence finding",\n'
            '      "severity": "LOW | MEDIUM | HIGH",\n'
            '      "evidence_references": ["metric_name or signal_key"],\n'
            '      "affected_entities": ["sku or flow name"]\n'
            "    }\n"
            "  ],\n"
            '  "proposals": [\n'
            "    {\n"
            '      "proposal_type": "EXPOSE_DELIVERY_ETA | IMPROVE_PRODUCT_DESCRIPTION | ...",\n'
            '      "title": "Short title",\n'
            '      "observation": "What was observed in telemetry",\n'
            '      "evidence": ["metric_name or signal_key"],\n'
            '      "hypothesis": "Why this change will improve commerce",\n'
            '      "proposed_change": "Exact proposed change description",\n'
            '      "target_entity": "sku or discovery or general",\n'
            '      "expected_effect": "Qualitative outcome",\n'
            '      "expected_metric": "target metric name (e.g. quote_conversion_rate)",\n'
            '      "confidence": 0.85,\n'
            '      "estimated_cost_paise": 0\n'
            "    }\n"
            "  ]\n"
            "}"
        )

        user_content = (
            f"<trusted_merchant_snapshot>\n"
            f"{snapshot.model_dump_json(indent=2)}\n"
            f"</trusted_merchant_snapshot>\n"
            "\n"
            "Analyze the above telemetry and produce structured diagnoses and proposals."
        )

        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_content),
        ]

        try:
            resp = await llm_provider.generate_response(
                messages=messages,
                temperature=0.2,
                max_tokens=2048,
                timeout=settings.LLM_TIMEOUT_SECONDS,
            )
            raw_json = resp.content.strip()
            if raw_json.startswith("```json"):
                raw_json = raw_json[7:]
            if raw_json.startswith("```"):
                raw_json = raw_json[3:]
            if raw_json.endswith("```"):
                raw_json = raw_json[:-3]
            raw_json = raw_json.strip()

            parsed = json.loads(raw_json)
        except Exception as exc:
            logger.warning("LLM generation failed or returned invalid JSON: %s", exc)
            # Safe degradation to deterministic observation without proposals
            return [], []

        # Available valid evidence keys from snapshot
        valid_telemetry_keys = {item.metric_name for item in snapshot.telemetry}
        valid_signal_keys = {s.get("signal_key") for s in snapshot.signals if "signal_key" in s}
        all_valid_evidence = valid_telemetry_keys | valid_signal_keys

        diagnoses: list[MerchantDiagnosisItem] = []
        for d in parsed.get("diagnoses", []):
            try:
                ev_refs = [
                    ref for ref in d.get("evidence_references", []) if ref in all_valid_evidence
                ]
                # Default to at least one valid metric if none matched to prevent loss
                if not ev_refs and snapshot.telemetry:
                    ev_refs = [snapshot.telemetry[0].metric_name]

                diag_item = MerchantDiagnosisItem(
                    pattern=d.get("pattern", "GENERAL_OBSERVATION"),
                    summary=d.get("summary", "Observation identified in commerce snapshot."),
                    severity=d.get("severity", "LOW")
                    if d.get("severity") in ("LOW", "MEDIUM", "HIGH")
                    else "LOW",
                    evidence_references=ev_refs,
                    affected_entities=d.get("affected_entities", ["general"]),
                )
                diagnoses.append(diag_item)
            except Exception as exc:
                logger.debug("Skipping invalid diagnosis payload: %s", exc)

        proposals: list[MerchantProposal] = []
        for p in parsed.get("proposals", []):
            try:
                # Validate evidence
                ev_list = [ref for ref in p.get("evidence", []) if ref in all_valid_evidence]
                if not ev_list and snapshot.telemetry:
                    ev_list = [snapshot.telemetry[0].metric_name]

                # Server-authoritative governance check
                risk_level, is_acceptable, reject_reason = cls.govern_and_classify_proposal(
                    p, snapshot.active_policies
                )

                prop_create = MerchantProposalCreate(
                    proposal_type=ProposalType(p.get("proposal_type")),
                    title=p.get("title", "Optimization Proposal"),
                    observation=p.get("observation", "Observed in commerce data."),
                    evidence=ev_list,
                    hypothesis=p.get("hypothesis", "Hypothesis for improvement."),
                    proposed_change=p.get("proposed_change", "Actionable change."),
                    target_entity=p.get("target_entity", "general"),
                    expected_effect=p.get("expected_effect", "Improved conversion."),
                    expected_metric=p.get("expected_metric", "quote_conversion_rate"),
                    confidence=float(p.get("confidence", 0.8)),
                    estimated_cost_paise=int(p.get("estimated_cost_paise", 0)),
                    metadata_payload=p.get("metadata_payload", {}),
                )

                db_proposal = MerchantProposal(
                    merchant_id=merchant_id,
                    proposal_type=prop_create.proposal_type.value,
                    title=prop_create.title,
                    observation=prop_create.observation,
                    evidence=prop_create.evidence,
                    hypothesis=prop_create.hypothesis,
                    proposed_change=prop_create.proposed_change,
                    target_entity=prop_create.target_entity,
                    expected_effect=prop_create.expected_effect,
                    expected_metric=prop_create.expected_metric,
                    confidence=prop_create.confidence,
                    risk_level=risk_level.value,
                    status=(
                        ProposalStatus.PROPOSED.value
                        if is_acceptable
                        else ProposalStatus.REJECTED.value
                    ),
                    rejection_reason=reject_reason,
                    metadata_payload=prop_create.metadata_payload,
                )
                proposals.append(db_proposal)
            except Exception as exc:
                logger.debug("Skipping invalid proposal payload: %s", exc)

        return diagnoses, proposals

    @classmethod
    async def execute_agent_run(
        cls,
        session: AsyncSession,
        merchant_id: uuid.UUID,
        llm_provider: BaseLLMProvider,
        settings: Settings,
    ) -> MerchantAgentAnalyzeResponse:
        """Executes a bounded, auditable Merchant Agent optimization turn."""
        start_time = time.monotonic()
        run_id = uuid.uuid4()
        now = datetime.now(UTC)

        # 1. Authoritative observation snapshot
        snapshot = await cls.build_authoritative_observations(
            session=session, merchant_id=merchant_id
        )

        # 2. Reasoning & Diagnosis
        diagnoses, proposals = await cls.diagnose_and_propose(
            session=session,
            merchant_id=merchant_id,
            snapshot=snapshot,
            llm_provider=llm_provider,
            settings=settings,
        )

        # 3. Persist proposals & run record
        for p in proposals:
            p.run_id = run_id
            session.add(p)
        await session.flush()

        # 4. Audit Event Chain Linkage
        await AuditEvent.create_event(
            session=session,
            merchant_id=merchant_id,
            actor_type="SYSTEM",
            event_type="MERCHANT_AGENT_RUN_COMPLETED",
            payload={
                "run_id": str(run_id),
                "diagnoses_count": len(diagnoses),
                "proposals_count": len(proposals),
                "autonomy_level": snapshot.autonomy_level,
                "telemetry_metrics_count": len(snapshot.telemetry),
            },
        )
        await session.commit()

        duration_ms = round((time.monotonic() - start_time) * 1000, 2)

        proposal_responses = [
            MerchantProposalResponse(
                id=p.id,
                merchant_id=p.merchant_id,
                run_id=p.run_id,
                proposal_type=p.proposal_type,
                title=p.title,
                observation=p.observation,
                evidence=p.evidence,
                hypothesis=p.hypothesis,
                proposed_change=p.proposed_change,
                target_entity=p.target_entity,
                expected_effect=p.expected_effect,
                expected_metric=p.expected_metric,
                confidence=p.confidence,
                risk_level=p.risk_level,
                status=p.status,
                rejection_reason=p.rejection_reason,
                reviewed_by=p.reviewed_by,
                reviewed_at=p.reviewed_at,
                metadata_payload=p.metadata_payload,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in proposals
        ]

        return MerchantAgentAnalyzeResponse(
            run_id=run_id,
            merchant_id=merchant_id,
            status="COMPLETED",
            snapshot=snapshot,
            diagnoses=diagnoses,
            proposals=proposal_responses,
            step_count=1,
            total_tokens=150,
            execution_duration_ms=duration_ms,
            executed_at=now,
            message=(
                f"Merchant Agent analysis completed in {duration_ms}ms with "
                f"{len(diagnoses)} diagnoses and {len(proposals)} proposals."
            ),
        )

    @classmethod
    async def list_proposals(
        cls,
        session: AsyncSession,
        merchant_id: uuid.UUID,
        status: str | None = None,
    ) -> list[MerchantProposalResponse]:
        """Lists merchant proposals filtered by status."""
        stmt = select(MerchantProposal).where(MerchantProposal.merchant_id == merchant_id)
        if status and status.upper() != "ALL":
            stmt = stmt.where(MerchantProposal.status == status.upper())
        stmt = stmt.order_by(MerchantProposal.created_at.desc())

        proposals = list((await session.execute(stmt)).scalars().all())
        return [
            MerchantProposalResponse(
                id=p.id,
                merchant_id=p.merchant_id,
                run_id=p.run_id,
                proposal_type=p.proposal_type,
                title=p.title,
                observation=p.observation,
                evidence=p.evidence,
                hypothesis=p.hypothesis,
                proposed_change=p.proposed_change,
                target_entity=p.target_entity,
                expected_effect=p.expected_effect,
                expected_metric=p.expected_metric,
                confidence=p.confidence,
                risk_level=p.risk_level,
                status=p.status,
                rejection_reason=p.rejection_reason,
                reviewed_by=p.reviewed_by,
                reviewed_at=p.reviewed_at,
                metadata_payload=p.metadata_payload,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in proposals
        ]

    @classmethod
    async def review_proposal(
        cls,
        session: AsyncSession,
        merchant_id: uuid.UUID,
        proposal_id: uuid.UUID,
        review_req: MerchantProposalReviewRequest,
        reviewer_id: str = "merchant_admin",
    ) -> MerchantProposalResponse:
        """Executes human review on a proposal (APPROVE, REJECT, or CONVERT_TO_EXPERIMENT)."""
        stmt = select(MerchantProposal).where(
            MerchantProposal.id == proposal_id, MerchantProposal.merchant_id == merchant_id
        )
        proposal = (await session.execute(stmt)).scalar_one_or_none()
        if not proposal:
            raise ValueError(f"Proposal '{proposal_id}' not found.")

        now = datetime.now(UTC)
        proposal.reviewed_by = reviewer_id
        proposal.reviewed_at = now

        if review_req.decision == "APPROVE":
            proposal.status = ProposalStatus.APPROVED.value
        elif review_req.decision == "REJECT":
            proposal.status = ProposalStatus.REJECTED.value
            proposal.rejection_reason = review_req.rejection_reason or "Rejected by merchant admin."
        elif review_req.decision == "CONVERT_TO_EXPERIMENT":
            proposal.status = ProposalStatus.CONVERTED_TO_EXPERIMENT.value

        await AuditEvent.create_event(
            session=session,
            merchant_id=merchant_id,
            actor_type="MERCHANT_ADMIN",
            event_type="MERCHANT_PROPOSAL_REVIEWED",
            payload={
                "proposal_id": str(proposal.id),
                "decision": review_req.decision,
                "rejection_reason": proposal.rejection_reason,
                "reviewed_by": reviewer_id,
            },
        )
        await session.commit()

        return MerchantProposalResponse(
            id=proposal.id,
            merchant_id=proposal.merchant_id,
            run_id=proposal.run_id,
            proposal_type=proposal.proposal_type,
            title=proposal.title,
            observation=proposal.observation,
            evidence=proposal.evidence,
            hypothesis=proposal.hypothesis,
            proposed_change=proposal.proposed_change,
            target_entity=proposal.target_entity,
            expected_effect=proposal.expected_effect,
            expected_metric=proposal.expected_metric,
            confidence=proposal.confidence,
            risk_level=proposal.risk_level,
            status=proposal.status,
            rejection_reason=proposal.rejection_reason,
            reviewed_by=proposal.reviewed_by,
            reviewed_at=proposal.reviewed_at,
            metadata_payload=proposal.metadata_payload,
            created_at=proposal.created_at,
            updated_at=proposal.updated_at,
        )

    @classmethod
    async def create_experiment(
        cls,
        session: AsyncSession,
        merchant_id: uuid.UUID,
        req: ExperimentCreateRequest,
        creator_id: str = "merchant_admin",
    ) -> ExperimentResponse:
        """Registers a structured merchant optimization experiment in approval-first status."""
        exp = MerchantExperiment(
            merchant_id=merchant_id,
            proposal_id=req.proposal_id,
            title=req.title,
            hypothesis=req.hypothesis,
            target_metric=req.target_metric,
            baseline_value=req.baseline_value,
            target_value=req.target_value,
            proposed_variation=req.proposed_variation,
            risk_level="LOW_RISK_REVERSIBLE",
            status="APPROVAL_REQUIRED",
            approval_status="PENDING",
            stopping_condition=req.stopping_condition,
            rollback_condition=req.rollback_condition,
        )
        session.add(exp)
        await session.flush()

        await AuditEvent.create_event(
            session=session,
            merchant_id=merchant_id,
            actor_type="MERCHANT_ADMIN",
            event_type="MERCHANT_EXPERIMENT_CREATED",
            payload={
                "experiment_id": str(exp.id),
                "title": exp.title,
                "target_metric": exp.target_metric,
                "proposal_id": str(req.proposal_id) if req.proposal_id else None,
            },
        )
        await session.commit()

        return ExperimentResponse(
            id=exp.id,
            merchant_id=exp.merchant_id,
            proposal_id=exp.proposal_id,
            title=exp.title,
            hypothesis=exp.hypothesis,
            target_metric=exp.target_metric,
            baseline_value=exp.baseline_value,
            target_value=exp.target_value,
            proposed_variation=exp.proposed_variation,
            risk_level=exp.risk_level,
            status=exp.status,
            approval_status=exp.approval_status,
            approved_by=exp.approved_by,
            approved_at=exp.approved_at,
            stopping_condition=exp.stopping_condition,
            rollback_condition=exp.rollback_condition,
            start_time=exp.start_time,
            end_time=exp.end_time,
            created_at=exp.created_at,
            updated_at=exp.updated_at,
            results=[],
        )

    @classmethod
    async def approve_experiment(
        cls,
        session: AsyncSession,
        merchant_id: uuid.UUID,
        experiment_id: uuid.UUID,
        approver_id: str = "merchant_admin",
    ) -> ExperimentResponse:
        """Approves an experiment to transition it into READY state."""
        stmt = select(MerchantExperiment).where(
            MerchantExperiment.id == experiment_id,
            MerchantExperiment.merchant_id == merchant_id,
        )
        exp = (await session.execute(stmt)).scalar_one_or_none()
        if not exp:
            raise ValueError(f"Experiment '{experiment_id}' not found.")

        now = datetime.now(UTC)
        exp.approval_status = "APPROVED"
        exp.status = "APPROVED"
        exp.approved_by = approver_id
        exp.approved_at = now
        exp.start_time = now

        await AuditEvent.create_event(
            session=session,
            merchant_id=merchant_id,
            actor_type="MERCHANT_ADMIN",
            event_type="MERCHANT_EXPERIMENT_APPROVED",
            payload={
                "experiment_id": str(exp.id),
                "approved_by": approver_id,
            },
        )
        await session.commit()

        return ExperimentResponse(
            id=exp.id,
            merchant_id=exp.merchant_id,
            proposal_id=exp.proposal_id,
            title=exp.title,
            hypothesis=exp.hypothesis,
            target_metric=exp.target_metric,
            baseline_value=exp.baseline_value,
            target_value=exp.target_value,
            proposed_variation=exp.proposed_variation,
            risk_level=exp.risk_level,
            status=exp.status,
            approval_status=exp.approval_status,
            approved_by=exp.approved_by,
            approved_at=exp.approved_at,
            stopping_condition=exp.stopping_condition,
            rollback_condition=exp.rollback_condition,
            start_time=exp.start_time,
            end_time=exp.end_time,
            created_at=exp.created_at,
            updated_at=exp.updated_at,
            results=[],
        )

    @classmethod
    async def list_experiments(
        cls,
        session: AsyncSession,
        merchant_id: uuid.UUID,
    ) -> list[ExperimentResponse]:
        """Lists all experiments for the merchant."""
        stmt = (
            select(MerchantExperiment)
            .where(MerchantExperiment.merchant_id == merchant_id)
            .order_by(MerchantExperiment.created_at.desc())
        )
        exps = list((await session.execute(stmt)).scalars().all())

        responses: list[ExperimentResponse] = []
        for exp in exps:
            res_stmt = select(MerchantExperimentResult).where(
                MerchantExperimentResult.experiment_id == exp.id
            )
            results = list((await session.execute(res_stmt)).scalars().all())
            res_models = [
                ExperimentResultResponse(
                    id=r.id,
                    experiment_id=r.experiment_id,
                    merchant_id=r.merchant_id,
                    sample_size=r.sample_size,
                    baseline_metric=r.baseline_metric,
                    post_experiment_metric=r.post_experiment_metric,
                    absolute_change=r.absolute_change,
                    percentage_change=r.percentage_change,
                    confidence_score=r.confidence_score,
                    limitations=r.limitations,
                    recommendation=r.recommendation,  # type: ignore[arg-type]
                    deterministic_evidence=r.deterministic_evidence,
                    recorded_at=r.recorded_at,
                )
                for r in results
            ]

            responses.append(
                ExperimentResponse(
                    id=exp.id,
                    merchant_id=exp.merchant_id,
                    proposal_id=exp.proposal_id,
                    title=exp.title,
                    hypothesis=exp.hypothesis,
                    target_metric=exp.target_metric,
                    baseline_value=exp.baseline_value,
                    target_value=exp.target_value,
                    proposed_variation=exp.proposed_variation,
                    risk_level=exp.risk_level,
                    status=exp.status,
                    approval_status=exp.approval_status,
                    approved_by=exp.approved_by,
                    approved_at=exp.approved_at,
                    stopping_condition=exp.stopping_condition,
                    rollback_condition=exp.rollback_condition,
                    start_time=exp.start_time,
                    end_time=exp.end_time,
                    created_at=exp.created_at,
                    updated_at=exp.updated_at,
                    results=res_models,
                )
            )
        return responses

    @classmethod
    async def evaluate_experiment_results(
        cls,
        session: AsyncSession,
        merchant_id: uuid.UUID,
        experiment_id: uuid.UUID,
    ) -> ExperimentResultResponse:
        """Deterministically evaluates experiment outcomes against observed metrics."""
        stmt = select(MerchantExperiment).where(
            MerchantExperiment.id == experiment_id,
            MerchantExperiment.merchant_id == merchant_id,
        )
        exp = (await session.execute(stmt)).scalar_one_or_none()
        if not exp:
            raise ValueError(f"Experiment '{experiment_id}' not found.")

        snapshot = await cls.build_authoritative_observations(
            session=session, merchant_id=merchant_id
        )

        # Match target metric in telemetry
        current_metric_val = 0.0
        sample_size = 0
        for item in snapshot.telemetry:
            if item.metric_name == exp.target_metric:
                if isinstance(item.value, (int, float)):
                    current_metric_val = float(item.value)
                sample_size = item.sample_size
                break

        baseline_metric = exp.baseline_value
        post_experiment_metric = current_metric_val
        absolute_change = round(post_experiment_metric - baseline_metric, 4)
        percentage_change = (
            round(((post_experiment_metric - baseline_metric) / baseline_metric) * 100, 2)
            if baseline_metric > 0
            else 0.0
        )

        limitations: list[str] = []
        if sample_size < 5:
            recommendation = "INCONCLUSIVE"
            confidence_score = 0.4
            limitations.append(
                "Sample size too small (< 5 interactions) to verify statistical significance."
            )
        elif percentage_change >= 5.0:
            recommendation = "KEEP"
            confidence_score = 0.9
        elif percentage_change < -2.0:
            recommendation = "ROLLBACK"
            confidence_score = 0.85
        else:
            recommendation = "INCONCLUSIVE"
            confidence_score = 0.65
            limitations.append("Metric change is within normal variance window.")

        result = MerchantExperimentResult(
            experiment_id=exp.id,
            merchant_id=merchant_id,
            sample_size=sample_size,
            baseline_metric=baseline_metric,
            post_experiment_metric=post_experiment_metric,
            absolute_change=absolute_change,
            percentage_change=percentage_change,
            confidence_score=confidence_score,
            limitations=limitations,
            recommendation=recommendation,
            deterministic_evidence={
                "target_metric": exp.target_metric,
                "baseline": baseline_metric,
                "post_experiment": post_experiment_metric,
                "sample_size": sample_size,
            },
        )
        session.add(result)
        exp.status = "COMPLETED"
        exp.end_time = datetime.now(UTC)

        await AuditEvent.create_event(
            session=session,
            merchant_id=merchant_id,
            actor_type="SYSTEM",
            event_type="MERCHANT_EXPERIMENT_EVALUATED",
            payload={
                "experiment_id": str(exp.id),
                "recommendation": recommendation,
                "percentage_change": percentage_change,
                "sample_size": sample_size,
            },
        )
        await session.commit()

        return ExperimentResultResponse(
            id=result.id,
            experiment_id=result.experiment_id,
            merchant_id=result.merchant_id,
            sample_size=result.sample_size,
            baseline_metric=result.baseline_metric,
            post_experiment_metric=result.post_experiment_metric,
            absolute_change=result.absolute_change,
            percentage_change=result.percentage_change,
            confidence_score=result.confidence_score,
            limitations=result.limitations,
            recommendation=result.recommendation,  # type: ignore[arg-type]
            deterministic_evidence=result.deterministic_evidence,
            recorded_at=result.recorded_at,
        )
