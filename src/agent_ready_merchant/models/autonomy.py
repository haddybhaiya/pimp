"""Phase 8 Controlled Autonomy database models and enums."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from agent_ready_merchant.db.base import GUID, Base, OptimisticLockMixin, TimestampMixin

if TYPE_CHECKING:
    from agent_ready_merchant.models.experiment import MerchantExperiment
    from agent_ready_merchant.models.merchant import Merchant
    from agent_ready_merchant.models.proposal import MerchantProposal


class AutonomyActionType(StrEnum):
    """Allowed actions eligible for controlled autonomy execution."""

    IMPROVE_PRODUCT_DESCRIPTION = "IMPROVE_PRODUCT_DESCRIPTION"
    IMPROVE_DISCOVERY_METADATA = "IMPROVE_DISCOVERY_METADATA"
    REORDER_RECOMMENDATIONS = "REORDER_RECOMMENDATIONS"
    EXPOSE_DELIVERY_ETA = "EXPOSE_DELIVERY_ETA"
    SUGGEST_BOUNDED_EXPERIMENT = "SUGGEST_BOUNDED_EXPERIMENT"


class AutonomyClassification(StrEnum):
    """Authoritative tier classification for autonomy actions."""

    READ_ONLY = "READ_ONLY"
    AUTO_LOW_RISK = "AUTO_LOW_RISK"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    HUMAN_ONLY = "HUMAN_ONLY"
    PROHIBITED = "PROHIBITED"


class AutonomyActionStatus(StrEnum):
    """Execution lifecycle status of an autonomous action."""

    EXECUTED = "EXECUTED"
    ROLLED_BACK = "ROLLED_BACK"
    STOPPED = "STOPPED"
    FAILED = "FAILED"


class RollbackStatus(StrEnum):
    """Availability and state of deterministic rollback."""

    AVAILABLE = "AVAILABLE"
    ROLLED_BACK = "ROLLED_BACK"
    EXPIRED = "EXPIRED"
    CONFLICT_REJECTED = "CONFLICT_REJECTED"


class AnomalyState(StrEnum):
    """Operational anomaly state for merchant autonomy controller."""

    NORMAL = "NORMAL"
    WARN = "WARN"
    PAUSE_AUTONOMY = "PAUSE_AUTONOMY"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"


def compute_autonomy_rule_hash(rule_data: dict[str, Any]) -> str:
    """Computes a deterministic SHA-256 hash of an autonomy rule's configuration."""
    canonical_data = {
        "action_type": str(rule_data.get("action_type", "")),
        "is_enabled": bool(rule_data.get("is_enabled", False)),
        "classification": str(rule_data.get("classification", "")),
        "max_executions_per_hour": int(rule_data.get("max_executions_per_hour", 0)),
        "max_executions_per_day": int(rule_data.get("max_executions_per_day", 0)),
        "cooldown_seconds": int(rule_data.get("cooldown_seconds", 0)),
        "experiment_duration_limit_days": int(rule_data.get("experiment_duration_limit_days", 0)),
        "experiment_exposure_limit": rule_data.get("experiment_exposure_limit"),
        "rollback_required": bool(rule_data.get("rollback_required", True)),
        "approval_required": bool(rule_data.get("approval_required", False)),
        "policy_version": int(rule_data.get("policy_version", 1)),
        "bounded_monetary_limit_paise": int(rule_data.get("bounded_monetary_limit_paise", 0)),
    }
    encoded = json.dumps(canonical_data, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class MerchantAutonomyRule(Base, TimestampMixin, OptimisticLockMixin):
    """Durable, merchant-configurable, server-authoritative autonomy rule."""

    __tablename__ = "merchant_autonomy_rules"

    __table_args__ = (
        CheckConstraint(
            "action_type IN ('IMPROVE_PRODUCT_DESCRIPTION', 'IMPROVE_DISCOVERY_METADATA', "
            "'REORDER_RECOMMENDATIONS', 'EXPOSE_DELIVERY_ETA', 'SUGGEST_BOUNDED_EXPERIMENT')",
            name="ck_merchant_autonomy_rules_action_type_valid",
        ),
        CheckConstraint(
            "classification IN ('READ_ONLY', 'AUTO_LOW_RISK', "
            "'APPROVAL_REQUIRED', 'HUMAN_ONLY', 'PROHIBITED')",
            name="ck_merchant_autonomy_rules_classification_valid",
        ),
        CheckConstraint(
            "max_executions_per_hour >= 1 AND max_executions_per_hour <= 100",
            name="ck_merchant_autonomy_rules_hourly_limit_bounds",
        ),
        CheckConstraint(
            "max_executions_per_day >= 1 AND max_executions_per_day <= 1000",
            name="ck_merchant_autonomy_rules_daily_limit_bounds",
        ),
        CheckConstraint(
            "cooldown_seconds >= 0 AND cooldown_seconds <= 86400",
            name="ck_merchant_autonomy_rules_cooldown_bounds",
        ),
        CheckConstraint(
            "bounded_monetary_limit_paise >= 0",
            name="ck_merchant_autonomy_rules_monetary_limit_non_negative",
        ),
        UniqueConstraint(
            "merchant_id", "action_type", name="uq_merchant_autonomy_rules_merchant_action"
        ),
        Index("ix_merchant_autonomy_rules_merchant_type", "merchant_id", "action_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("merchants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    classification: Mapped[str] = mapped_column(
        String(32),
        default=AutonomyClassification.AUTO_LOW_RISK.value,
        nullable=False,
    )
    max_executions_per_hour: Mapped[int] = mapped_column(
        Integer,
        default=5,
        nullable=False,
    )
    max_executions_per_day: Mapped[int] = mapped_column(
        Integer,
        default=20,
        nullable=False,
    )
    cooldown_seconds: Mapped[int] = mapped_column(
        Integer,
        default=300,
        nullable=False,
    )
    experiment_duration_limit_days: Mapped[int] = mapped_column(
        Integer,
        default=30,
        nullable=False,
    )
    experiment_exposure_limit: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    rollback_required: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    approval_required: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    policy_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    policy_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    bounded_monetary_limit_paise: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=False,
    )

    # Relationships
    merchant: Mapped[Merchant] = relationship("Merchant", back_populates="autonomy_rules")


class MerchantAutonomyAction(Base, TimestampMixin, OptimisticLockMixin):
    """Authoritative ledger entry for an autonomous mutation and its rollback snapshot."""

    __tablename__ = "merchant_autonomy_actions"

    __table_args__ = (
        CheckConstraint(
            "action_type IN ('IMPROVE_PRODUCT_DESCRIPTION', 'IMPROVE_DISCOVERY_METADATA', "
            "'REORDER_RECOMMENDATIONS', 'EXPOSE_DELIVERY_ETA', 'SUGGEST_BOUNDED_EXPERIMENT')",
            name="ck_merchant_autonomy_actions_action_type_valid",
        ),
        CheckConstraint(
            "status IN ('EXECUTED', 'ROLLED_BACK', 'STOPPED', 'FAILED')",
            name="ck_merchant_autonomy_actions_status_valid",
        ),
        CheckConstraint(
            "rollback_status IN ('AVAILABLE', 'ROLLED_BACK', 'EXPIRED', 'CONFLICT_REJECTED')",
            name="ck_merchant_autonomy_actions_rollback_status_valid",
        ),
        CheckConstraint(
            "anomaly_state IN ('NORMAL', 'WARN', 'PAUSE_AUTONOMY', 'REQUIRE_HUMAN_REVIEW')",
            name="ck_merchant_autonomy_actions_anomaly_state_valid",
        ),
        ForeignKeyConstraint(
            ["proposal_id", "merchant_id"],
            ["merchant_proposals.id", "merchant_proposals.merchant_id"],
            name="fk_merchant_autonomy_actions_proposal_merchant",
        ),
        ForeignKeyConstraint(
            ["agent_run_id", "merchant_id"],
            ["agent_runs.id", "agent_runs.merchant_id"],
            name="fk_merchant_autonomy_actions_run_merchant",
        ),
        ForeignKeyConstraint(
            ["experiment_id", "merchant_id"],
            ["merchant_experiments.id", "merchant_experiments.merchant_id"],
            name="fk_merchant_autonomy_actions_experiment_merchant",
        ),
        Index("ix_merchant_autonomy_actions_merchant_created", "merchant_id", "created_at"),
        Index("ix_merchant_autonomy_actions_idempotency", "merchant_id", "idempotency_key"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("merchants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent_run_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        nullable=True,
        index=True,
    )
    proposal_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        nullable=True,
        index=True,
    )
    experiment_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        nullable=True,
        index=True,
    )
    action_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    target_entity_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    target_entity_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        nullable=False,
        index=True,
    )
    target_version_before: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    target_version_after: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    deterministic_classification: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    autonomy_rule_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    autonomy_rule_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    hourly_budget_consumed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    daily_budget_consumed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default=AutonomyActionStatus.EXECUTED.value,
        nullable=False,
        index=True,
    )
    rollback_snapshot: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )
    rollback_status: Mapped[str] = mapped_column(
        String(32),
        default=RollbackStatus.AVAILABLE.value,
        nullable=False,
        index=True,
    )
    rolled_back_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    rolled_back_by: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    stopping_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    anomaly_state: Mapped[str] = mapped_column(
        String(32),
        default=AnomalyState.NORMAL.value,
        nullable=False,
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    # Relationships
    merchant: Mapped[Merchant] = relationship(
        "Merchant", back_populates="autonomy_actions", overlaps="experiment,proposal"
    )
    proposal: Mapped[MerchantProposal | None] = relationship(
        "MerchantProposal",
        primaryjoin=(
            "and_(MerchantAutonomyAction.proposal_id == MerchantProposal.id, "
            "MerchantAutonomyAction.merchant_id == MerchantProposal.merchant_id)"
        ),
        foreign_keys=[proposal_id, merchant_id],
        overlaps="experiment,merchant",
    )
    experiment: Mapped[MerchantExperiment | None] = relationship(
        "MerchantExperiment",
        primaryjoin=(
            "and_(MerchantAutonomyAction.experiment_id == MerchantExperiment.id, "
            "MerchantAutonomyAction.merchant_id == MerchantExperiment.merchant_id)"
        ),
        foreign_keys=[experiment_id, merchant_id],
        overlaps="autonomy_actions,merchant,proposal",
    )
