"""Authoritative Controlled Autonomy Controller and Execution Gateway for Phase 8.

Enforces fail-closed governance, bounded budgets, kill switches, immutable rollback snapshots,
and atomic cryptographic audit logs.
"""

from __future__ import annotations

import uuid
from datetime import timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.db.base import utc_now
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.autonomy import (
    AnomalyState,
    AutonomyActionStatus,
    AutonomyActionType,
    AutonomyClassification,
    MerchantAutonomyAction,
    MerchantAutonomyFailure,
    MerchantAutonomyRule,
    RollbackStatus,
    compute_autonomy_rule_hash,
)
from agent_ready_merchant.models.experiment import MerchantExperiment
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.product import Product
from agent_ready_merchant.models.proposal import MerchantProposal
from agent_ready_merchant.schemas.controlled_autonomy import (
    AutonomyRuleUpdateRequest,
)
from agent_ready_merchant.schemas.merchant_agent import ProposalRiskLevel
from agent_ready_merchant.services.merchant_agent_service import MerchantAgentService
from agent_ready_merchant.services.merchant_mutation_idempotency_service import (
    MerchantMutationIdempotencyService,
)


class AutonomySecurityError(ValueError):
    """Raised when an agent or unauthorized actor attempts to modify governance boundaries."""


class AutonomyExecutionError(ValueError):
    """Raised when an autonomous action fails pre-execution policy checks."""


class OptimisticLockError(ValueError):
    """Raised when target resource or rule expected version does not match."""


class RollbackConflictError(ValueError):
    """Raised when target resource has been modified after autonomous mutation."""


class ControlledAutonomyService:
    """Authoritative execution boundary and lifecycle controller for autonomous mutations."""

    ALLOWED_AUTONOMOUS_ACTIONS: set[str] = {
        AutonomyActionType.IMPROVE_PRODUCT_DESCRIPTION.value,
        AutonomyActionType.IMPROVE_DISCOVERY_METADATA.value,
        AutonomyActionType.REORDER_RECOMMENDATIONS.value,
        AutonomyActionType.EXPOSE_DELIVERY_ETA.value,
        AutonomyActionType.SUGGEST_BOUNDED_EXPERIMENT.value,
    }

    @classmethod
    async def get_or_create_default_rules(
        cls, session: AsyncSession, merchant_id: uuid.UUID
    ) -> list[MerchantAutonomyRule]:
        """Ensures default server-authoritative autonomy rules exist for allowed actions."""
        # Serialize first-time rule provisioning per merchant.  This makes the
        # unique merchant/action constraint a defence in depth check rather than
        # the normal concurrent-control path.
        merchant = (
            await session.execute(
                select(Merchant).where(Merchant.id == merchant_id).with_for_update()
            )
        ).scalar_one_or_none()
        if merchant is None:
            raise ValueError(f"Merchant '{merchant_id}' not found.")

        stmt = select(MerchantAutonomyRule).where(MerchantAutonomyRule.merchant_id == merchant_id)
        existing = list((await session.execute(stmt)).scalars().all())
        existing_types = {r.action_type for r in existing}

        default_configs = [
            {
                "action_type": AutonomyActionType.IMPROVE_PRODUCT_DESCRIPTION.value,
                "is_enabled": False,
                "classification": AutonomyClassification.AUTO_LOW_RISK.value,
                "max_executions_per_hour": 5,
                "max_executions_per_day": 20,
                "cooldown_seconds": 300,
                "experiment_duration_limit_days": 30,
                "rollback_required": True,
                "approval_required": False,
                "bounded_monetary_limit_paise": 0,
            },
            {
                "action_type": AutonomyActionType.IMPROVE_DISCOVERY_METADATA.value,
                "is_enabled": False,
                "classification": AutonomyClassification.AUTO_LOW_RISK.value,
                "max_executions_per_hour": 5,
                "max_executions_per_day": 20,
                "cooldown_seconds": 300,
                "experiment_duration_limit_days": 30,
                "rollback_required": True,
                "approval_required": False,
                "bounded_monetary_limit_paise": 0,
            },
            {
                "action_type": AutonomyActionType.REORDER_RECOMMENDATIONS.value,
                "is_enabled": False,
                "classification": AutonomyClassification.AUTO_LOW_RISK.value,
                "max_executions_per_hour": 5,
                "max_executions_per_day": 20,
                "cooldown_seconds": 300,
                "experiment_duration_limit_days": 30,
                "rollback_required": True,
                "approval_required": False,
                "bounded_monetary_limit_paise": 0,
            },
            {
                "action_type": AutonomyActionType.EXPOSE_DELIVERY_ETA.value,
                "is_enabled": False,
                "classification": AutonomyClassification.AUTO_LOW_RISK.value,
                "max_executions_per_hour": 5,
                "max_executions_per_day": 20,
                "cooldown_seconds": 300,
                "experiment_duration_limit_days": 30,
                "rollback_required": True,
                "approval_required": False,
                "bounded_monetary_limit_paise": 0,
            },
            {
                "action_type": AutonomyActionType.SUGGEST_BOUNDED_EXPERIMENT.value,
                "is_enabled": False,
                "classification": AutonomyClassification.AUTO_LOW_RISK.value,
                "max_executions_per_hour": 2,
                "max_executions_per_day": 10,
                "cooldown_seconds": 600,
                "experiment_duration_limit_days": 30,
                "rollback_required": True,
                "approval_required": False,
                "bounded_monetary_limit_paise": 0,
            },
        ]

        created = False
        for cfg in default_configs:
            if cfg["action_type"] not in existing_types:
                rule_hash = compute_autonomy_rule_hash(cfg)
                rule = MerchantAutonomyRule(
                    merchant_id=merchant_id,
                    action_type=cfg["action_type"],
                    is_enabled=cfg["is_enabled"],
                    classification=cfg["classification"],
                    max_executions_per_hour=cfg["max_executions_per_hour"],
                    max_executions_per_day=cfg["max_executions_per_day"],
                    cooldown_seconds=cfg["cooldown_seconds"],
                    experiment_duration_limit_days=cfg["experiment_duration_limit_days"],
                    rollback_required=cfg["rollback_required"],
                    approval_required=cfg["approval_required"],
                    policy_version=1,
                    policy_hash=rule_hash,
                    bounded_monetary_limit_paise=cfg["bounded_monetary_limit_paise"],
                )
                session.add(rule)
                existing.append(rule)
                created = True

        if created:
            await session.flush()
        return existing

    @classmethod
    async def update_autonomy_rule(
        cls,
        session: AsyncSession,
        *,
        merchant_id: uuid.UUID,
        action_type: str,
        req: AutonomyRuleUpdateRequest,
        actor_type: str,
        actor_id: uuid.UUID | str,
    ) -> MerchantAutonomyRule:
        """Updates a merchant autonomy rule. Strictly restricted to human merchant admin."""
        # Non-negotiable security boundary: Agent or LLM can NEVER update rules or budgets
        if actor_type != "MERCHANT_ADMIN":
            raise AutonomySecurityError(
                f"Actor type '{actor_type}' is not authorized to modify autonomy rules or budgets."
            )

        if action_type not in cls.ALLOWED_AUTONOMOUS_ACTIONS:
            raise ValueError(f"Action type '{action_type}' is not configurable.")

        stmt = (
            select(MerchantAutonomyRule)
            .where(
                MerchantAutonomyRule.merchant_id == merchant_id,
                MerchantAutonomyRule.action_type == action_type,
            )
            .with_for_update()
        )
        rule = (await session.execute(stmt)).scalar_one_or_none()
        if not rule:
            # Create rule first if missing
            await cls.get_or_create_default_rules(session, merchant_id)
            rule = (await session.execute(stmt)).scalar_one()

        if rule.version != req.expected_version:
            msg = f"Rule version mismatch: expected {req.expected_version}, current {rule.version}."
            raise OptimisticLockError(msg)

        # Apply human-specified updates
        if req.is_enabled is not None:
            rule.is_enabled = req.is_enabled
        if req.classification is not None:
            rule.classification = req.classification.value
        if req.max_executions_per_hour is not None:
            rule.max_executions_per_hour = req.max_executions_per_hour
        if req.max_executions_per_day is not None:
            rule.max_executions_per_day = req.max_executions_per_day
        if req.cooldown_seconds is not None:
            rule.cooldown_seconds = req.cooldown_seconds
        if req.experiment_duration_limit_days is not None:
            rule.experiment_duration_limit_days = req.experiment_duration_limit_days
        if req.experiment_exposure_limit is not None:
            rule.experiment_exposure_limit = req.experiment_exposure_limit
        if req.rollback_required is not None:
            rule.rollback_required = req.rollback_required
        if req.approval_required is not None:
            rule.approval_required = req.approval_required
        if req.bounded_monetary_limit_paise is not None:
            rule.bounded_monetary_limit_paise = req.bounded_monetary_limit_paise

        # Increment rule policy version and optimistic lock version
        rule.policy_version += 1
        rule.version += 1

        # Recompute policy hash
        rule_data = {
            "action_type": rule.action_type,
            "is_enabled": rule.is_enabled,
            "classification": rule.classification,
            "max_executions_per_hour": rule.max_executions_per_hour,
            "max_executions_per_day": rule.max_executions_per_day,
            "cooldown_seconds": rule.cooldown_seconds,
            "experiment_duration_limit_days": rule.experiment_duration_limit_days,
            "experiment_exposure_limit": rule.experiment_exposure_limit,
            "rollback_required": rule.rollback_required,
            "approval_required": rule.approval_required,
            "policy_version": rule.policy_version,
            "bounded_monetary_limit_paise": rule.bounded_monetary_limit_paise,
        }
        rule.policy_hash = compute_autonomy_rule_hash(rule_data)
        await session.flush()

        # Append audit event
        await AuditEvent.create_event(
            session=session,
            merchant_id=merchant_id,
            actor_type="MERCHANT_ADMIN",
            event_type="AUTONOMY_RULE_UPDATED",
            payload={
                "action_type": rule.action_type,
                "policy_version": rule.policy_version,
                "policy_hash": rule.policy_hash,
                "classification": rule.classification,
                "is_enabled": rule.is_enabled,
                "max_executions_per_hour": rule.max_executions_per_hour,
                "max_executions_per_day": rule.max_executions_per_day,
                "actor_id": str(actor_id),
            },
        )
        return rule

    @classmethod
    async def set_kill_switch(
        cls,
        session: AsyncSession,
        *,
        merchant_id: uuid.UUID,
        enabled: bool,
        actor_type: str,
        actor_id: uuid.UUID | str,
        reason: str,
    ) -> Merchant:
        """Toggles the merchant master kill switch."""
        if actor_type != "MERCHANT_ADMIN":
            raise AutonomySecurityError("Only merchant admin can toggle the kill switch.")

        merchant = (
            await session.execute(
                select(Merchant).where(Merchant.id == merchant_id).with_for_update()
            )
        ).scalar_one_or_none()
        if not merchant:
            raise ValueError(f"Merchant '{merchant_id}' not found.")

        merchant.kill_switch_enabled = enabled
        merchant.version += 1
        await session.flush()

        await AuditEvent.create_event(
            session=session,
            merchant_id=merchant_id,
            actor_type="MERCHANT_ADMIN",
            event_type="AUTONOMY_KILL_SWITCH_TOGGLED",
            payload={
                "kill_switch_enabled": enabled,
                "reason": reason,
                "actor_id": str(actor_id),
            },
        )

        # If kill switch was enabled, stop running autonomous experiments
        if enabled:
            stmt = select(MerchantExperiment).where(
                MerchantExperiment.merchant_id == merchant_id,
                MerchantExperiment.status == "RUNNING",
            )
            running_exps = list((await session.execute(stmt.with_for_update())).scalars().all())
            for exp in running_exps:
                exp.status = "STOPPED"
                cond = (
                    dict(exp.stopping_condition) if isinstance(exp.stopping_condition, dict) else {}
                )
                cond["stopped_by_kill_switch"] = True
                cond["stopping_reason"] = f"Merchant kill switch activated: {reason}"
                exp.stopping_condition = cond
                exp.version += 1
                await AuditEvent.create_event(
                    session=session,
                    merchant_id=merchant_id,
                    actor_type="SYSTEM",
                    event_type="MERCHANT_EXPERIMENT_STOPPED",
                    payload={
                        "experiment_id": str(exp.id),
                        "reason": f"Merchant kill switch activated: {reason}",
                    },
                )
            await session.flush()

        return merchant

    @classmethod
    async def evaluate_anomaly_state(
        cls, session: AsyncSession, merchant_id: uuid.UUID
    ) -> tuple[AnomalyState, list[str]]:
        """Evaluates operational anomalies for the merchant."""
        merchant = (
            await session.execute(select(Merchant).where(Merchant.id == merchant_id))
        ).scalar_one_or_none()
        reasons: list[str] = []

        if merchant and merchant.kill_switch_enabled:
            reasons.append("Merchant kill switch is active.")
            return AnomalyState.PAUSE_AUTONOMY, reasons

        # Check for repeated failed actions in the past hour
        one_hour_ago = utc_now() - timedelta(hours=1)
        failed_stmt = select(func.count(MerchantAutonomyFailure.id)).where(
            MerchantAutonomyFailure.merchant_id == merchant_id,
            MerchantAutonomyFailure.created_at >= one_hour_ago,
        )
        failed_count = (await session.execute(failed_stmt)).scalar() or 0
        if failed_count >= 3:
            reasons.append(f"High failure frequency: {failed_count} failures in the past hour.")
            return AnomalyState.REQUIRE_HUMAN_REVIEW, reasons

        return AnomalyState.NORMAL, []

    @classmethod
    async def check_budget_and_cooldown(
        cls,
        session: AsyncSession,
        merchant_id: uuid.UUID,
        rule: MerchantAutonomyRule,
    ) -> tuple[int, int]:
        """Checks rate limits and cooldown for an action type.

        Raises AutonomyExecutionError if limits are reached or cooldown is active.
        Returns (hourly_consumed, daily_consumed) for the pending execution.
        """
        # All autonomous executions for a merchant share this transaction lock.
        # Aggregate counts alone cannot reserve a rate-limit slot under races.
        merchant = (
            await session.execute(
                select(Merchant).where(Merchant.id == merchant_id).with_for_update()
            )
        ).scalar_one_or_none()
        if merchant is None:
            raise AutonomyExecutionError(f"Merchant '{merchant_id}' does not exist.")

        now = utc_now()
        one_hour_ago = now - timedelta(hours=1)
        one_day_ago = now - timedelta(days=1)

        # Count executions in the last hour
        stmt_hour = select(func.count(MerchantAutonomyAction.id)).where(
            MerchantAutonomyAction.merchant_id == merchant_id,
            MerchantAutonomyAction.action_type == rule.action_type,
            MerchantAutonomyAction.created_at >= one_hour_ago,
            MerchantAutonomyAction.status != AutonomyActionStatus.FAILED.value,
        )
        hourly_count = (await session.execute(stmt_hour)).scalar() or 0

        # Count executions in the last day
        stmt_day = select(func.count(MerchantAutonomyAction.id)).where(
            MerchantAutonomyAction.merchant_id == merchant_id,
            MerchantAutonomyAction.action_type == rule.action_type,
            MerchantAutonomyAction.created_at >= one_day_ago,
            MerchantAutonomyAction.status != AutonomyActionStatus.FAILED.value,
        )
        daily_count = (await session.execute(stmt_day)).scalar() or 0

        if hourly_count >= rule.max_executions_per_hour:
            raise AutonomyExecutionError(
                f"Hourly execution limit ({rule.max_executions_per_hour}) reached. "
                f"Exhausted ({hourly_count}/{rule.max_executions_per_hour})."
            )

        if daily_count >= rule.max_executions_per_day:
            raise AutonomyExecutionError(
                f"Daily execution limit ({rule.max_executions_per_day}) reached. "
                f"Exhausted ({daily_count}/{rule.max_executions_per_day})."
            )

        # Cooldown check: most recent execution
        stmt_last = (
            select(MerchantAutonomyAction)
            .where(
                MerchantAutonomyAction.merchant_id == merchant_id,
                MerchantAutonomyAction.action_type == rule.action_type,
                MerchantAutonomyAction.status != AutonomyActionStatus.FAILED.value,
            )
            .order_by(MerchantAutonomyAction.created_at.desc())
            .limit(1)
        )
        last_action = (await session.execute(stmt_last)).scalar_one_or_none()
        if last_action:
            elapsed = (now - last_action.created_at).total_seconds()
            if elapsed < rule.cooldown_seconds:
                remaining = int(rule.cooldown_seconds - elapsed)
                raise AutonomyExecutionError(
                    f"Cooldown active. Cooldown period active ({remaining}s remaining)."
                )

        return hourly_count + 1, daily_count + 1

    @classmethod
    async def execute_autonomous_action(
        cls,
        session: AsyncSession,
        *,
        merchant_id: uuid.UUID,
        proposal_id: uuid.UUID,
        expected_target_version: int,
        idempotency_key: str,
        actor_id: uuid.UUID | str | None = None,
    ) -> dict[str, Any]:
        """Execute through a savepoint and durably record rejected attempts.

        The nested transaction ensures a gate failure cannot leave a claimed
        idempotency receipt, target edit, or partial ledger row behind.  The
        failure telemetry and its audit event are then committed by the caller
        in the enclosing request transaction.
        """
        try:
            async with session.begin_nested():
                return await cls._execute_autonomous_action(
                    session=session,
                    merchant_id=merchant_id,
                    proposal_id=proposal_id,
                    expected_target_version=expected_target_version,
                    idempotency_key=idempotency_key,
                    actor_id=actor_id,
                )
        except (AutonomyExecutionError, OptimisticLockError) as exc:
            await cls._record_execution_failure(
                session=session,
                merchant_id=merchant_id,
                proposal_id=proposal_id,
                idempotency_key=idempotency_key,
                failure_code=(
                    "OPTIMISTIC_CONFLICT"
                    if isinstance(exc, OptimisticLockError)
                    else "PRECONDITION_REJECTED"
                ),
                actor_id=actor_id,
            )
            raise

    @classmethod
    async def _record_execution_failure(
        cls,
        *,
        session: AsyncSession,
        merchant_id: uuid.UUID,
        proposal_id: uuid.UUID,
        idempotency_key: str,
        failure_code: str,
        actor_id: uuid.UUID | str | None,
    ) -> None:
        """Append non-mutating failure telemetry after a rejected execution gate."""
        proposal = (
            await session.execute(
                select(MerchantProposal).where(
                    MerchantProposal.id == proposal_id,
                    MerchantProposal.merchant_id == merchant_id,
                )
            )
        ).scalar_one_or_none()
        failure = MerchantAutonomyFailure(
            merchant_id=merchant_id,
            proposal_id=proposal.id if proposal else None,
            action_type=proposal.proposal_type if proposal else None,
            failure_code=failure_code,
            idempotency_key=idempotency_key,
        )
        session.add(failure)
        await session.flush()
        await AuditEvent.create_event(
            session=session,
            merchant_id=merchant_id,
            actor_type="MERCHANT_ADMIN",
            event_type="AUTONOMOUS_ACTION_REJECTED",
            payload={
                "failure_id": str(failure.id),
                "proposal_id": str(proposal_id),
                "action_type": failure.action_type,
                "failure_code": failure_code,
                "actor_id": str(actor_id) if actor_id is not None else None,
            },
        )

    @classmethod
    async def _execute_autonomous_action(
        cls,
        session: AsyncSession,
        *,
        merchant_id: uuid.UUID,
        proposal_id: uuid.UUID,
        expected_target_version: int,
        idempotency_key: str,
        actor_id: uuid.UUID | str | None = None,
    ) -> dict[str, Any]:
        """Executes an approved/auto-eligible proposal autonomously through 18 pre-condition gates.

        Commits target mutation, autonomy action ledger, receipt, and audit event atomically.
        """
        # Gate 15: Claim idempotency receipt first
        claim_payload = {
            "proposal_id": str(proposal_id),
            "expected_target_version": expected_target_version,
        }
        receipt, replayed = await MerchantMutationIdempotencyService.claim_or_replay(
            session=session,
            merchant_id=merchant_id,
            operation="AUTONOMOUS_ACTION_EXECUTE",
            idempotency_key=idempotency_key,
            payload=claim_payload,
        )
        if replayed is not None:
            return replayed

        assert receipt is not None

        # Gate 1: Authenticated merchant identity verification
        merchant = (
            await session.execute(
                select(Merchant).where(Merchant.id == merchant_id).with_for_update()
            )
        ).scalar_one_or_none()
        if not merchant:
            raise AutonomyExecutionError(f"Merchant '{merchant_id}' does not exist.")

        # Gate 10: Kill switch check
        if merchant.kill_switch_enabled:
            raise AutonomyExecutionError("Execution blocked: Merchant kill switch is active.")

        # Gate 17: Anomaly state check
        anomaly_state, anomaly_reasons = await cls.evaluate_anomaly_state(session, merchant_id)
        if anomaly_state in (AnomalyState.PAUSE_AUTONOMY, AnomalyState.REQUIRE_HUMAN_REVIEW):
            details = "; ".join(anomaly_reasons)
            raise AutonomyExecutionError(
                f"Execution blocked by anomaly state {anomaly_state.value}: {details}"
            )

        # Gate 2: Proposal tenant ownership
        prop_stmt = (
            select(MerchantProposal)
            .where(
                MerchantProposal.id == proposal_id,
                MerchantProposal.merchant_id == merchant_id,
            )
            .with_for_update()
        )
        proposal = (await session.execute(prop_stmt)).scalar_one_or_none()
        if not proposal:
            raise AutonomyExecutionError(f"Proposal '{proposal_id}' not found for merchant.")

        # Gate 3: Valid evidence-backed proposal
        if not proposal.evidence:
            raise AutonomyExecutionError("Proposal lacks authoritative evidence references.")

        # Gate 4 & 5: Deterministic risk classification and structured normalization
        proposal_dict = {
            "proposal_type": proposal.proposal_type,
            "title": proposal.title,
            "observation": proposal.observation,
            "proposed_change": proposal.proposed_change,
            "hypothesis": proposal.hypothesis,
            "target_entity": proposal.target_entity,
            "expected_effect": proposal.expected_effect,
            "metadata_payload": proposal.metadata_payload,
            "structured_action": proposal.metadata_payload.get("structured_action")
            if isinstance(proposal.metadata_payload, dict)
            else None,
        }
        risk_level, valid_evidence, rejection_reason = (
            MerchantAgentService.govern_and_classify_proposal(proposal_dict, {})
        )
        if risk_level == ProposalRiskLevel.PROHIBITED or not valid_evidence:
            detail = rejection_reason or "Risk level prohibited"
            raise AutonomyExecutionError(
                f"Action is PROHIBITED by server-authoritative governance: {detail}"
            )

        # Gate 6: Typed action allowlist
        action_type = proposal.proposal_type
        if action_type not in cls.ALLOWED_AUTONOMOUS_ACTIONS:
            raise AutonomyExecutionError(
                f"Proposal type '{action_type}' is not on the autonomous execution allowlist."
            )

        # Gate 7: Autonomy rule lookup
        await cls.get_or_create_default_rules(session, merchant_id)
        rule = (
            await session.execute(
                select(MerchantAutonomyRule)
                .where(
                    MerchantAutonomyRule.merchant_id == merchant_id,
                    MerchantAutonomyRule.action_type == action_type,
                )
                .with_for_update()
            )
        ).scalar_one_or_none()
        if not rule or not rule.is_enabled:
            raise AutonomyExecutionError(
                f"Autonomy rule for '{action_type}' is disabled or not configured."
            )
        if rule.classification != AutonomyClassification.AUTO_LOW_RISK.value:
            raise AutonomyExecutionError(
                f"Autonomy rule classification '{rule.classification}' is not AUTO_LOW_RISK."
            )

        # Gate 8: Rule version and hash integrity
        rule_data = {
            "action_type": rule.action_type,
            "is_enabled": rule.is_enabled,
            "classification": rule.classification,
            "max_executions_per_hour": rule.max_executions_per_hour,
            "max_executions_per_day": rule.max_executions_per_day,
            "cooldown_seconds": rule.cooldown_seconds,
            "experiment_duration_limit_days": rule.experiment_duration_limit_days,
            "experiment_exposure_limit": rule.experiment_exposure_limit,
            "rollback_required": rule.rollback_required,
            "approval_required": rule.approval_required,
            "policy_version": rule.policy_version,
            "bounded_monetary_limit_paise": rule.bounded_monetary_limit_paise,
        }
        expected_hash = compute_autonomy_rule_hash(rule_data)
        if rule.policy_hash != expected_hash:
            raise AutonomyExecutionError(
                "Autonomy rule integrity verification failed (hash mismatch)."
            )

        # Gate 9: Budget, rate limits, and cooldown
        hourly_consumed, daily_consumed = await cls.check_budget_and_cooldown(
            session, merchant_id, rule
        )

        # Gate 11: only a live auto-eligible proposal, or an explicitly approved
        # proposal when the rule requires it, may enter the execution boundary.
        # Rejected/archived proposals must never regain authority through an API
        # call, and autonomous execution must not fabricate a human approval.
        if rule.approval_required:
            if proposal.status != "APPROVED":
                raise AutonomyExecutionError(
                    f"Action '{action_type}' requires explicit merchant approval before execution."
                )
        elif proposal.status not in {"PROPOSED", "APPROVED"}:
            raise AutonomyExecutionError(
                f"Proposal status '{proposal.status}' is not eligible for autonomous execution."
            )

        # Gate 12 & 13: Target resource existence, ownership, and expected version
        target_product: Product | None = None
        target_experiment: MerchantExperiment | None = None
        target_entity_type = "product"
        target_entity_id: uuid.UUID

        if action_type == AutonomyActionType.SUGGEST_BOUNDED_EXPERIMENT.value:
            target_entity_type = "merchant_experiment"
            # Find linked experiment
            exp_stmt = (
                select(MerchantExperiment)
                .where(
                    MerchantExperiment.merchant_id == merchant_id,
                    MerchantExperiment.proposal_id == proposal.id,
                )
                .with_for_update()
            )
            target_experiment = (await session.execute(exp_stmt)).scalar_one_or_none()
            if not target_experiment:
                raise AutonomyExecutionError("Linked merchant experiment not found.")
            target_entity_id = target_experiment.id
            if target_experiment.version != expected_target_version:
                msg = (
                    f"Target experiment version mismatch: expected {expected_target_version}, "
                    f"current {target_experiment.version}."
                )
                raise OptimisticLockError(msg)
            if (
                target_experiment.status != "APPROVED"
                or target_experiment.approval_status != "APPROVED"
                or target_experiment.start_time is None
            ):
                raise AutonomyExecutionError(
                    "Experiment must be merchant-approved before autonomous start."
                )
            # No deterministic variant router exists in the buyer/discovery path.
            # Exposure-limited experiments therefore fail closed instead of
            # claiming an unenforceable traffic percentage.
            if rule.experiment_exposure_limit is not None:
                raise AutonomyExecutionError(
                    "Traffic exposure limits are not executable without deterministic routing."
                )
        else:
            # Find target product by affected_entities or metadata
            product_id_str = None
            if isinstance(proposal.metadata_payload, dict):
                product_id_str = proposal.metadata_payload.get(
                    "target_product_id"
                ) or proposal.metadata_payload.get("product_id")
            if not product_id_str and proposal.target_entity:
                product_id_str = proposal.target_entity

            if not product_id_str or str(product_id_str).strip().casefold() == "general":
                raise AutonomyExecutionError("Proposal does not identify a target product.")

            target_prod_stmt = select(Product).where(Product.merchant_id == merchant_id)
            if product_id_str:
                try:
                    p_uuid = uuid.UUID(str(product_id_str))
                    target_prod_stmt = target_prod_stmt.where(Product.id == p_uuid)
                except ValueError:
                    target_prod_stmt = target_prod_stmt.where(Product.sku == str(product_id_str))

            target_product = (
                await session.execute(target_prod_stmt.limit(1).with_for_update())
            ).scalar_one_or_none()
            if not target_product:
                raise AutonomyExecutionError(
                    "Target product for optimization does not exist or belong to merchant."
                )
            target_entity_id = target_product.id
            if target_product.version != expected_target_version:
                msg = (
                    f"Target product version mismatch: expected {expected_target_version}, "
                    f"current {target_product.version}."
                )
                raise OptimisticLockError(msg)

        # Gate 16: No conflicting active autonomous action on same target
        active_conflict_stmt = select(MerchantAutonomyAction).where(
            MerchantAutonomyAction.merchant_id == merchant_id,
            MerchantAutonomyAction.target_entity_id == target_entity_id,
            MerchantAutonomyAction.status == AutonomyActionStatus.EXECUTED.value,
            MerchantAutonomyAction.rollback_status == RollbackStatus.AVAILABLE.value,
        )
        conflicting = (await session.execute(active_conflict_stmt.limit(1))).scalar_one_or_none()
        if conflicting:
            msg = f"Conflicting action '{conflicting.id}' is already active on this target."
            raise AutonomyExecutionError(msg)

        # Gate 14: Deterministic rollback snapshot creation
        before_version: int
        after_version: int
        original_state: dict[str, Any]
        changed_state: dict[str, Any]

        if target_product:
            before_version = target_product.version
            original_state = {
                "description": target_product.description,
                "attributes": dict(target_product.attributes),
            }

            # Execute narrow, typed mutation
            if action_type == AutonomyActionType.IMPROVE_PRODUCT_DESCRIPTION.value:
                new_desc = proposal.proposed_change
                target_product.description = new_desc
                current_attr = dict(target_product.attributes)
                current_attr["ai_description"] = new_desc
                target_product.attributes = current_attr
                changed_state = {"description": new_desc, "ai_description": new_desc}
            elif action_type == AutonomyActionType.IMPROVE_DISCOVERY_METADATA.value:
                current_attr = dict(target_product.attributes)
                tags = (
                    proposal.metadata_payload.get("tags")
                    if isinstance(proposal.metadata_payload, dict)
                    else None
                )
                if not tags:
                    tags = [t.strip() for t in proposal.proposed_change.split(",") if t.strip()]
                current_attr["tags"] = tags
                target_product.attributes = current_attr
                changed_state = {"attributes": {"tags": tags}}
            elif action_type == AutonomyActionType.REORDER_RECOMMENDATIONS.value:
                current_attr = dict(target_product.attributes)
                display_order = 1
                if (
                    isinstance(proposal.metadata_payload, dict)
                    and "display_order" in proposal.metadata_payload
                ):
                    display_order = int(proposal.metadata_payload["display_order"])
                current_attr["display_order"] = display_order
                target_product.attributes = current_attr
                changed_state = {"attributes": {"display_order": display_order}}
            elif action_type == AutonomyActionType.EXPOSE_DELIVERY_ETA.value:
                current_attr = dict(target_product.attributes)
                delivery_info = {
                    "expose_eta": True,
                    "estimated_days": 3,
                    "details": proposal.proposed_change,
                }
                current_attr["delivery_info"] = delivery_info
                target_product.attributes = current_attr
                changed_state = {"attributes": {"delivery_info": delivery_info}}
            else:
                raise AutonomyExecutionError(f"Unsupported action type '{action_type}'.")

            target_product.version += 1
            after_version = target_product.version

        elif target_experiment:
            before_version = target_experiment.version
            original_state = {
                "status": target_experiment.status,
            }
            target_experiment.status = "RUNNING"
            target_experiment.end_time = utc_now() + timedelta(
                days=rule.experiment_duration_limit_days
            )
            target_experiment.version += 1
            after_version = target_experiment.version
            changed_state = {"status": "RUNNING"}

        # Construct immutable rollback snapshot
        rollback_snapshot = {
            "merchant_id": str(merchant_id),
            "target_resource_type": target_entity_type,
            "target_resource_id": str(target_entity_id),
            "target_resource_version": before_version,
            "original_state": original_state,
            "changed_state": changed_state,
            "rule_version": rule.policy_version,
            "rule_hash": rule.policy_hash,
            "rollback_condition": "On performance drop, anomaly trigger, or human request",
            "idempotency_key": idempotency_key,
            "timestamp": utc_now().isoformat(),
        }

        # Gate 18: Create autonomy action record
        action_record = MerchantAutonomyAction(
            merchant_id=merchant_id,
            agent_run_id=proposal.run_id,
            proposal_id=proposal.id,
            experiment_id=target_experiment.id if target_experiment else None,
            action_type=action_type,
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
            target_version_before=before_version,
            target_version_after=after_version,
            deterministic_classification=AutonomyClassification.AUTO_LOW_RISK.value,
            autonomy_rule_hash=rule.policy_hash,
            autonomy_rule_version=rule.policy_version,
            hourly_budget_consumed=hourly_consumed,
            daily_budget_consumed=daily_consumed,
            status=AutonomyActionStatus.EXECUTED.value,
            rollback_snapshot=rollback_snapshot,
            rollback_status=RollbackStatus.AVAILABLE.value,
            anomaly_state=anomaly_state.value,
            idempotency_key=idempotency_key,
        )
        session.add(action_record)

        await session.flush()

        # Append immutable AuditEvent
        await AuditEvent.create_event(
            session=session,
            merchant_id=merchant_id,
            actor_type="SYSTEM",
            event_type="MERCHANT_AUTONOMY_ACTION_EXECUTED",
            payload={
                "action_id": str(action_record.id),
                "proposal_id": str(proposal.id),
                "action_type": action_type,
                "target_entity_type": target_entity_type,
                "target_entity_id": str(target_entity_id),
                "target_version_before": before_version,
                "target_version_after": after_version,
                "rule_hash": rule.policy_hash,
                "rule_version": rule.policy_version,
                "hourly_budget_consumed": hourly_consumed,
                "daily_budget_consumed": daily_consumed,
                "idempotency_key": idempotency_key,
            },
        )

        response_body = {
            "action": {
                "id": str(action_record.id),
                "merchant_id": str(merchant_id),
                "agent_run_id": str(action_record.agent_run_id)
                if action_record.agent_run_id
                else None,
                "proposal_id": str(proposal.id),
                "experiment_id": str(action_record.experiment_id)
                if action_record.experiment_id
                else None,
                "action_type": action_type,
                "target_entity_type": target_entity_type,
                "target_entity_id": str(target_entity_id),
                "target_version_before": before_version,
                "target_version_after": after_version,
                "deterministic_classification": AutonomyClassification.AUTO_LOW_RISK.value,
                "autonomy_rule_hash": rule.policy_hash,
                "autonomy_rule_version": rule.policy_version,
                "hourly_budget_consumed": hourly_consumed,
                "daily_budget_consumed": daily_consumed,
                "status": AutonomyActionStatus.EXECUTED.value,
                "rollback_snapshot": rollback_snapshot,
                "rollback_status": RollbackStatus.AVAILABLE.value,
                "rolled_back_at": None,
                "rolled_back_by": None,
                "stopping_reason": None,
                "anomaly_state": anomaly_state.value,
                "idempotency_key": idempotency_key,
                "created_at": action_record.created_at.isoformat(),
            },
            "message": f"Autonomous action '{action_type}' executed successfully.",
            "status": "SUCCESS",
        }

        await MerchantMutationIdempotencyService.complete(
            session=session,
            receipt=receipt,
            response_body=response_body,
        )
        return response_body

    @classmethod
    async def rollback_action(
        cls,
        session: AsyncSession,
        *,
        merchant_id: uuid.UUID,
        action_id: uuid.UUID,
        expected_target_version: int,
        reason: str,
        idempotency_key: str,
        actor_id: uuid.UUID | str | None = None,
    ) -> dict[str, Any]:
        """Deterministically rolls back an autonomous action to its pre-mutation snapshot.

        Enforces tenant isolation, version checking, idempotency, and audit logging.
        Fails closed if the resource was modified by a newer merchant change.
        """
        claim_payload = {
            "action_id": str(action_id),
            "expected_target_version": expected_target_version,
            "reason": reason,
        }
        receipt, replayed = await MerchantMutationIdempotencyService.claim_or_replay(
            session=session,
            merchant_id=merchant_id,
            operation="AUTONOMOUS_ACTION_ROLLBACK",
            idempotency_key=idempotency_key,
            payload=claim_payload,
        )
        if replayed is not None:
            return replayed

        assert receipt is not None

        stmt = (
            select(MerchantAutonomyAction)
            .where(
                MerchantAutonomyAction.id == action_id,
                MerchantAutonomyAction.merchant_id == merchant_id,
            )
            .with_for_update()
        )
        action = (await session.execute(stmt)).scalar_one_or_none()
        if not action:
            raise ValueError(f"Autonomous action '{action_id}' not found for merchant.")

        # Idempotent return if already rolled back
        if action.rollback_status == RollbackStatus.ROLLED_BACK.value:
            response_body = {
                "action_id": str(action.id),
                "rollback_status": RollbackStatus.ROLLED_BACK.value,
                "target_entity_id": str(action.target_entity_id),
                "target_entity_type": action.target_entity_type,
                "target_version_reverted_to": action.target_version_before,
                "target_current_version": action.target_version_after,
                "rolled_back_at": action.rolled_back_at.isoformat()
                if action.rolled_back_at
                else utc_now().isoformat(),
                "message": "Action was already rolled back.",
            }
            await MerchantMutationIdempotencyService.complete(
                session=session,
                receipt=receipt,
                response_body=response_body,
            )
            return response_body

        if action.rollback_status != RollbackStatus.AVAILABLE.value:
            raise AutonomyExecutionError(
                f"Rollback unavailable: action status is '{action.rollback_status}'."
            )

        snapshot = action.rollback_snapshot
        original_state = snapshot.get("original_state", {})

        current_target_version: int
        if action.target_entity_type == "product":
            prod_stmt = (
                select(Product)
                .where(
                    Product.id == action.target_entity_id,
                    Product.merchant_id == merchant_id,
                )
                .with_for_update()
            )
            product = (await session.execute(prod_stmt)).scalar_one_or_none()
            if not product:
                raise ValueError("Target product not found for rollback.")

            # Version check: if current product version is greater than post-mutation version,
            # a newer human merchant change occurred. Must fail closed!
            if product.version > action.target_version_after:
                action.rollback_status = RollbackStatus.CONFLICT_REJECTED.value
                action.stopping_reason = (
                    f"Rollback rejected: Product modified by newer change "
                    f"(version {product.version} > {action.target_version_after})."
                )
                await AuditEvent.create_event(
                    session=session,
                    merchant_id=merchant_id,
                    actor_type="SYSTEM",
                    event_type="MERCHANT_AUTONOMY_ROLLBACK_CONFLICT",
                    payload={
                        "action_id": str(action.id),
                        "target_entity_type": action.target_entity_type,
                        "target_entity_id": str(action.target_entity_id),
                        "current_version": product.version,
                        "expected_post_action_version": action.target_version_after,
                    },
                )
                await session.flush()
                msg = (
                    f"Rollback rejected: target resource version ({product.version}) "
                    f"exceeds expected post-action version ({action.target_version_after}). "
                    "A newer merchant modification exists."
                )
                raise RollbackConflictError(msg)

            if product.version != expected_target_version:
                msg = (
                    f"Target product version mismatch: expected {expected_target_version}, "
                    f"current {product.version}."
                )
                raise OptimisticLockError(msg)

            # Revert to original snapshot
            if "description" in original_state:
                product.description = str(original_state["description"])
            if "attributes" in original_state and isinstance(original_state["attributes"], dict):
                product.attributes = dict(original_state["attributes"])

            product.version += 1
            current_target_version = product.version

        elif action.target_entity_type == "merchant_experiment":
            exp_stmt = (
                select(MerchantExperiment)
                .where(
                    MerchantExperiment.id == action.target_entity_id,
                    MerchantExperiment.merchant_id == merchant_id,
                )
                .with_for_update()
            )
            exp = (await session.execute(exp_stmt)).scalar_one_or_none()
            if not exp:
                raise ValueError("Target experiment not found for rollback.")

            if exp.version > action.target_version_after:
                action.rollback_status = RollbackStatus.CONFLICT_REJECTED.value
                action.stopping_reason = (
                    "Rollback rejected: experiment modified by newer change "
                    f"(version {exp.version} > {action.target_version_after})."
                )
                await AuditEvent.create_event(
                    session=session,
                    merchant_id=merchant_id,
                    actor_type="SYSTEM",
                    event_type="MERCHANT_AUTONOMY_ROLLBACK_CONFLICT",
                    payload={
                        "action_id": str(action.id),
                        "target_entity_type": action.target_entity_type,
                        "target_entity_id": str(action.target_entity_id),
                        "current_version": exp.version,
                        "expected_post_action_version": action.target_version_after,
                    },
                )
                await session.flush()
                msg = (
                    f"Rollback rejected: experiment version ({exp.version}) "
                    "exceeds post-action version."
                )
                raise RollbackConflictError(msg)

            if exp.version != expected_target_version:
                msg = (
                    f"Target experiment version mismatch: expected {expected_target_version}, "
                    f"current {exp.version}."
                )
                raise OptimisticLockError(msg)

            exp.status = "ROLLED_BACK"
            exp.version += 1
            current_target_version = exp.version
        else:
            raise ValueError(f"Unknown target entity type '{action.target_entity_type}'.")

        now = utc_now()
        action.status = AutonomyActionStatus.ROLLED_BACK.value
        action.rollback_status = RollbackStatus.ROLLED_BACK.value
        action.rolled_back_at = now
        action.rolled_back_by = str(actor_id) if actor_id else "MERCHANT_ADMIN"
        action.stopping_reason = reason
        action.version += 1
        await session.flush()

        await AuditEvent.create_event(
            session=session,
            merchant_id=merchant_id,
            actor_type="MERCHANT_ADMIN",
            event_type="MERCHANT_AUTONOMY_ACTION_ROLLED_BACK",
            payload={
                "action_id": str(action.id),
                "target_entity_type": action.target_entity_type,
                "target_entity_id": str(action.target_entity_id),
                "reverted_to_version": action.target_version_before,
                "new_version": current_target_version,
                "reason": reason,
                "actor_id": str(actor_id),
            },
        )

        response_body = {
            "action_id": str(action.id),
            "rollback_status": RollbackStatus.ROLLED_BACK.value,
            "target_entity_id": str(action.target_entity_id),
            "target_entity_type": action.target_entity_type,
            "target_version_reverted_to": action.target_version_before,
            "target_current_version": current_target_version,
            "rolled_back_at": now.isoformat(),
            "message": "Autonomous action rolled back successfully.",
        }

        await MerchantMutationIdempotencyService.complete(
            session=session,
            receipt=receipt,
            response_body=response_body,
        )
        return response_body

    @classmethod
    async def stop_experiment(
        cls,
        session: AsyncSession,
        *,
        merchant_id: uuid.UUID,
        experiment_id: uuid.UUID,
        reason: str,
        require_rollback: bool,
        idempotency_key: str,
        actor_id: uuid.UUID | str | None = None,
    ) -> dict[str, Any]:
        """Stops a running experiment and optionally triggers deterministic rollback."""
        claim_payload = {
            "experiment_id": str(experiment_id),
            "reason": reason,
            "require_rollback": require_rollback,
        }
        receipt, replayed = await MerchantMutationIdempotencyService.claim_or_replay(
            session=session,
            merchant_id=merchant_id,
            operation="MERCHANT_EXPERIMENT_STOP",
            idempotency_key=idempotency_key,
            payload=claim_payload,
        )
        if replayed is not None:
            return replayed

        assert receipt is not None

        exp_stmt = (
            select(MerchantExperiment)
            .where(
                MerchantExperiment.id == experiment_id,
                MerchantExperiment.merchant_id == merchant_id,
            )
            .with_for_update()
        )
        experiment = (await session.execute(exp_stmt)).scalar_one_or_none()
        if not experiment:
            raise ValueError(f"Experiment '{experiment_id}' not found for merchant.")

        autonomy_action: MerchantAutonomyAction | None = None
        if require_rollback:
            action_stmt = (
                select(MerchantAutonomyAction)
                .where(
                    MerchantAutonomyAction.merchant_id == merchant_id,
                    MerchantAutonomyAction.experiment_id == experiment_id,
                    MerchantAutonomyAction.target_entity_type == "merchant_experiment",
                    MerchantAutonomyAction.status == AutonomyActionStatus.EXECUTED.value,
                    MerchantAutonomyAction.rollback_status == RollbackStatus.AVAILABLE.value,
                )
                .order_by(MerchantAutonomyAction.created_at.desc())
                .limit(1)
                .with_for_update()
            )
            autonomy_action = (await session.execute(action_stmt)).scalar_one_or_none()

        if autonomy_action is not None:
            # Reuse the authoritative action rollback path so the target state,
            # action ledger, idempotency receipt, and audit chain transition as
            # one transaction.  The operation namespace makes the shared key
            # safe alongside the enclosing experiment-stop receipt.
            await cls.rollback_action(
                session=session,
                merchant_id=merchant_id,
                action_id=autonomy_action.id,
                expected_target_version=autonomy_action.target_version_after,
                reason=reason,
                idempotency_key=idempotency_key,
                actor_id=actor_id,
            )
            response_body = {
                "experiment_id": str(experiment_id),
                "status": "ROLLED_BACK",
                "reason": reason,
                "autonomy_action_id": str(autonomy_action.id),
                "message": "Experiment and its autonomous action were rolled back.",
            }
            await MerchantMutationIdempotencyService.complete(
                session=session,
                receipt=receipt,
                response_body=response_body,
            )
            return response_body

        experiment.status = "ROLLED_BACK" if require_rollback else "STOPPED"
        experiment.version += 1
        await session.flush()

        await AuditEvent.create_event(
            session=session,
            merchant_id=merchant_id,
            actor_type="MERCHANT_ADMIN",
            event_type="MERCHANT_EXPERIMENT_STOPPED",
            payload={
                "experiment_id": str(experiment.id),
                "reason": reason,
                "status": experiment.status,
                "actor_id": str(actor_id),
            },
        )

        response_body = {
            "experiment_id": str(experiment.id),
            "status": experiment.status,
            "reason": reason,
            "message": f"Experiment transitioned to {experiment.status}.",
        }

        await MerchantMutationIdempotencyService.complete(
            session=session,
            receipt=receipt,
            response_body=response_body,
        )
        return response_body
