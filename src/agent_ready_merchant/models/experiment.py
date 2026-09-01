"""MerchantExperiment and MerchantExperimentResult canonical models for Phase 7."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from agent_ready_merchant.db.base import GUID, Base, OptimisticLockMixin, TimestampMixin, utc_now

if TYPE_CHECKING:
    from agent_ready_merchant.models.merchant import Merchant
    from agent_ready_merchant.models.proposal import MerchantProposal


class MerchantExperiment(Base, TimestampMixin, OptimisticLockMixin):
    """Authoritative persistent record of a merchant optimization experiment."""

    __tablename__ = "merchant_experiments"

    __table_args__ = (
        CheckConstraint(
            "status IN ('DRAFT', 'PROPOSED', 'APPROVAL_REQUIRED', 'APPROVED', 'READY', 'RUNNING', "
            "'COMPLETED', 'STOPPED', 'ROLLED_BACK', 'REJECTED')",
            name="ck_merchant_experiments_status_valid",
        ),
        CheckConstraint(
            "approval_status IN ('PENDING', 'APPROVED', 'REJECTED')",
            name="ck_merchant_experiments_approval_status_valid",
        ),
        CheckConstraint(
            "risk_level IN ('READ_ONLY', 'LOW_RISK_REVERSIBLE', 'APPROVAL_REQUIRED', 'PROHIBITED')",
            name="ck_merchant_experiments_risk_level_valid",
        ),
        Index("ix_merchant_experiments_merchant_status", "merchant_id", "status"),
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
    proposal_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("merchant_proposals.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    hypothesis: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    target_metric: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    baseline_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    target_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    proposed_variation: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )
    risk_level: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="LOW_RISK_REVERSIBLE",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="PROPOSED",
        index=True,
    )
    approval_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="PENDING",
        index=True,
    )
    approved_by: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    stopping_condition: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )
    rollback_condition: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )
    start_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    end_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    merchant: Mapped[Merchant] = relationship("Merchant", back_populates="experiments")
    proposal: Mapped[MerchantProposal | None] = relationship(
        "MerchantProposal", back_populates="experiments"
    )
    results: Mapped[list[MerchantExperimentResult]] = relationship(
        "MerchantExperimentResult",
        back_populates="experiment",
        cascade="all, delete-orphan",
    )


class MerchantExperimentResult(Base):
    """Authoritative persistent record of a measured experiment outcome."""

    __tablename__ = "merchant_experiment_results"

    __table_args__ = (
        CheckConstraint(
            "recommendation IN ('KEEP', 'ROLLBACK', 'INCONCLUSIVE')",
            name="ck_merchant_experiment_results_rec_valid",
        ),
        CheckConstraint(
            "sample_size >= 0",
            name="ck_merchant_experiment_results_sample_non_negative",
        ),
        UniqueConstraint("experiment_id", name="uq_merchant_experiment_results_experiment"),
        Index("ix_merchant_exp_results_merchant_exp", "merchant_id", "experiment_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    experiment_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("merchant_experiments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("merchants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sample_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    baseline_metric: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    post_experiment_metric: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    absolute_change: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    percentage_change: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    confidence_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    limitations: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=list,
    )
    recommendation: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="INCONCLUSIVE",
        index=True,
    )
    deterministic_evidence: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    # Relationships
    experiment: Mapped[MerchantExperiment] = relationship(
        "MerchantExperiment", back_populates="results"
    )
    merchant: Mapped[Merchant] = relationship("Merchant")
