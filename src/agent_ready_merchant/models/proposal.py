"""MerchantProposal canonical model for Phase 7 Merchant Agent intelligence layer."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
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


class MerchantProposal(Base, TimestampMixin, OptimisticLockMixin):
    """Authoritative persistent record of an optimization proposal."""

    __tablename__ = "merchant_proposals"

    __table_args__ = (
        CheckConstraint(
            "proposal_type IN ('IMPROVE_PRODUCT_DESCRIPTION', 'EXPOSE_DELIVERY_ETA', "
            "'REORDER_RECOMMENDATIONS', 'IMPROVE_DISCOVERY_METADATA', 'SUGGEST_BUNDLE', "
            "'SUGGEST_PROMOTIONAL_OFFER', 'SUGGEST_BOUNDED_EXPERIMENT')",
            name="ck_merchant_proposals_type_valid",
        ),
        CheckConstraint(
            "risk_level IN ('READ_ONLY', 'LOW_RISK_REVERSIBLE', 'APPROVAL_REQUIRED', 'PROHIBITED')",
            name="ck_merchant_proposals_risk_level_valid",
        ),
        CheckConstraint(
            "status IN ('PROPOSED', 'UNDER_REVIEW', 'APPROVED', 'REJECTED', "
            "'CONVERTED_TO_EXPERIMENT', 'ARCHIVED')",
            name="ck_merchant_proposals_status_valid",
        ),
        CheckConstraint(
            "confidence >= 0.0 AND confidence <= 1.0",
            name="ck_merchant_proposals_confidence_bounds",
        ),
        CheckConstraint(
            "estimated_cost_paise >= 0",
            name="ck_merchant_proposals_estimated_cost_non_negative",
        ),
        UniqueConstraint("id", "merchant_id", name="uq_merchant_proposals_id_merchant"),
        ForeignKeyConstraint(
            ["run_id", "merchant_id"],
            ["agent_runs.id", "agent_runs.merchant_id"],
            name="fk_merchant_proposals_run_merchant",
        ),
        Index("ix_merchant_proposals_merchant_status", "merchant_id", "status"),
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
    run_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        nullable=True,
        index=True,
    )
    estimated_cost_paise: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
    )
    proposal_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    observation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    evidence: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=list,
    )
    hypothesis: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    proposed_change: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    target_entity: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        default="general",
    )
    expected_effect: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    expected_metric: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.8,
    )
    risk_level: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="LOW_RISK_REVERSIBLE",
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="PROPOSED",
        index=True,
    )
    rejection_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    reviewed_by: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    metadata_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )

    # Relationships
    merchant: Mapped[Merchant] = relationship("Merchant", back_populates="proposals")
    experiments: Mapped[list[MerchantExperiment]] = relationship(
        "MerchantExperiment", back_populates="proposal"
    )
