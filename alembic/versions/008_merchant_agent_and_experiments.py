"""Create merchant proposals, experiments, and experiment results tables for Phase 7.

Revision ID: 008_merchant_agent_and_experiments
Revises: 007_merchant_auth_user_binding
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "008_merchant_agent_and_experiments"
down_revision: str | None = "007_merchant_auth_user_binding"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. merchant_proposals
    op.create_table(
        "merchant_proposals",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("merchant_id", sa.UUID(), nullable=False),
        sa.Column("run_id", sa.UUID(), nullable=True),
        sa.Column("proposal_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("observation", sa.Text(), nullable=False),
        sa.Column("evidence", sa.JSON().with_variant(JSONB, "postgresql"), nullable=False),
        sa.Column("hypothesis", sa.Text(), nullable=False),
        sa.Column("proposed_change", sa.Text(), nullable=False),
        sa.Column("target_entity", sa.String(length=128), nullable=False),
        sa.Column("expected_effect", sa.Text(), nullable=False),
        sa.Column("expected_metric", sa.String(length=64), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("risk_level", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("reviewed_by", sa.String(length=128), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_payload", sa.JSON().with_variant(JSONB, "postgresql"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "proposal_type IN ('IMPROVE_PRODUCT_DESCRIPTION', 'EXPOSE_DELIVERY_ETA', "
            "'REORDER_RECOMMENDATIONS', 'IMPROVE_DISCOVERY_METADATA', 'SUGGEST_BUNDLE', "
            "'SUGGEST_PROMOTIONAL_OFFER', 'SUGGEST_BOUNDED_EXPERIMENT')",
            name="ck_merchant_proposals_type_valid",
        ),
        sa.CheckConstraint(
            "risk_level IN ('READ_ONLY', 'LOW_RISK_REVERSIBLE', 'APPROVAL_REQUIRED', 'PROHIBITED')",
            name="ck_merchant_proposals_risk_level_valid",
        ),
        sa.CheckConstraint(
            "status IN ('PROPOSED', 'UNDER_REVIEW', 'APPROVED', 'REJECTED', "
            "'CONVERTED_TO_EXPERIMENT', 'ARCHIVED')",
            name="ck_merchant_proposals_status_valid",
        ),
        sa.CheckConstraint(
            "confidence >= 0.0 AND confidence <= 1.0",
            name="ck_merchant_proposals_confidence_bounds",
        ),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_merchant_proposals_merchant_id", "merchant_proposals", ["merchant_id"])
    op.create_index("ix_merchant_proposals_run_id", "merchant_proposals", ["run_id"])
    op.create_index("ix_merchant_proposals_status", "merchant_proposals", ["status"])
    op.create_index("ix_merchant_proposals_proposal_type", "merchant_proposals", ["proposal_type"])
    op.create_index("ix_merchant_proposals_risk_level", "merchant_proposals", ["risk_level"])
    op.create_index(
        "ix_merchant_proposals_merchant_status", "merchant_proposals", ["merchant_id", "status"]
    )

    # 2. merchant_experiments
    op.create_table(
        "merchant_experiments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("merchant_id", sa.UUID(), nullable=False),
        sa.Column("proposal_id", sa.UUID(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("hypothesis", sa.Text(), nullable=False),
        sa.Column("target_metric", sa.String(length=64), nullable=False),
        sa.Column("baseline_value", sa.Float(), nullable=False),
        sa.Column("target_value", sa.Float(), nullable=False),
        sa.Column(
            "proposed_variation", sa.JSON().with_variant(JSONB, "postgresql"), nullable=False
        ),
        sa.Column("risk_level", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("approval_status", sa.String(length=32), nullable=False),
        sa.Column("approved_by", sa.String(length=128), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "stopping_condition", sa.JSON().with_variant(JSONB, "postgresql"), nullable=False
        ),
        sa.Column(
            "rollback_condition", sa.JSON().with_variant(JSONB, "postgresql"), nullable=False
        ),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('DRAFT', 'PROPOSED', 'APPROVAL_REQUIRED', 'APPROVED', 'READY', 'RUNNING', "
            "'COMPLETED', 'STOPPED', 'ROLLED_BACK', 'REJECTED')",
            name="ck_merchant_experiments_status_valid",
        ),
        sa.CheckConstraint(
            "approval_status IN ('PENDING', 'APPROVED', 'REJECTED')",
            name="ck_merchant_experiments_approval_status_valid",
        ),
        sa.CheckConstraint(
            "risk_level IN ('READ_ONLY', 'LOW_RISK_REVERSIBLE', 'APPROVAL_REQUIRED', 'PROHIBITED')",
            name="ck_merchant_experiments_risk_level_valid",
        ),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["proposal_id"], ["merchant_proposals.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_merchant_experiments_merchant_id", "merchant_experiments", ["merchant_id"])
    op.create_index("ix_merchant_experiments_proposal_id", "merchant_experiments", ["proposal_id"])
    op.create_index("ix_merchant_experiments_status", "merchant_experiments", ["status"])
    op.create_index(
        "ix_merchant_experiments_approval_status", "merchant_experiments", ["approval_status"]
    )
    op.create_index(
        "ix_merchant_experiments_merchant_status", "merchant_experiments", ["merchant_id", "status"]
    )

    # 3. merchant_experiment_results
    op.create_table(
        "merchant_experiment_results",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("experiment_id", sa.UUID(), nullable=False),
        sa.Column("merchant_id", sa.UUID(), nullable=False),
        sa.Column("sample_size", sa.Integer(), nullable=False),
        sa.Column("baseline_metric", sa.Float(), nullable=False),
        sa.Column("post_experiment_metric", sa.Float(), nullable=False),
        sa.Column("absolute_change", sa.Float(), nullable=False),
        sa.Column("percentage_change", sa.Float(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("limitations", sa.JSON().with_variant(JSONB, "postgresql"), nullable=False),
        sa.Column("recommendation", sa.String(length=32), nullable=False),
        sa.Column(
            "deterministic_evidence", sa.JSON().with_variant(JSONB, "postgresql"), nullable=False
        ),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "recommendation IN ('KEEP', 'ROLLBACK', 'INCONCLUSIVE')",
            name="ck_merchant_experiment_results_rec_valid",
        ),
        sa.CheckConstraint(
            "sample_size >= 0",
            name="ck_merchant_experiment_results_sample_non_negative",
        ),
        sa.ForeignKeyConstraint(["experiment_id"], ["merchant_experiments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_merchant_experiment_results_experiment_id",
        "merchant_experiment_results",
        ["experiment_id"],
    )
    op.create_index(
        "ix_merchant_experiment_results_merchant_id",
        "merchant_experiment_results",
        ["merchant_id"],
    )
    op.create_index(
        "ix_merchant_experiment_results_recommendation",
        "merchant_experiment_results",
        ["recommendation"],
    )
    op.create_index(
        "ix_merchant_exp_results_merchant_exp",
        "merchant_experiment_results",
        ["merchant_id", "experiment_id"],
    )


def downgrade() -> None:
    op.drop_table("merchant_experiment_results")
    op.drop_table("merchant_experiments")
    op.drop_table("merchant_proposals")
