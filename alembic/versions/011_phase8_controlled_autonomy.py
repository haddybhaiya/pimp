"""Phase 8 Controlled Autonomy tables, constraints, and kill switch.

Revision ID: 011_phase8_controlled_autonomy
Revises: 010_phase7_integrity
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "011_phase8_controlled_autonomy"
down_revision: str | None = "010_phase7_integrity"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Add kill_switch_enabled column to merchants
    op.add_column(
        "merchants",
        sa.Column(
            "kill_switch_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    # 2. Create merchant_autonomy_rules table
    op.create_table(
        "merchant_autonomy_rules",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column(
            "merchant_id",
            sa.UUID(),
            sa.ForeignKey("merchants.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("action_type", sa.String(64), nullable=False, index=True),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "classification",
            sa.String(32),
            nullable=False,
            server_default=sa.text("'AUTO_LOW_RISK'"),
        ),
        sa.Column(
            "max_executions_per_hour", sa.Integer(), nullable=False, server_default=sa.text("5")
        ),
        sa.Column(
            "max_executions_per_day", sa.Integer(), nullable=False, server_default=sa.text("20")
        ),
        sa.Column("cooldown_seconds", sa.Integer(), nullable=False, server_default=sa.text("300")),
        sa.Column(
            "experiment_duration_limit_days",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("30"),
        ),
        sa.Column("experiment_exposure_limit", sa.Integer(), nullable=True),
        sa.Column(
            "rollback_required", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column(
            "approval_required", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column("policy_version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("policy_hash", sa.String(64), nullable=False),
        sa.Column(
            "bounded_monetary_limit_paise",
            sa.BigInteger(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint(
            "merchant_id", "action_type", name="uq_merchant_autonomy_rules_merchant_action"
        ),
        sa.CheckConstraint(
            "action_type IN ('IMPROVE_PRODUCT_DESCRIPTION', 'IMPROVE_DISCOVERY_METADATA', "
            "'REORDER_RECOMMENDATIONS', 'EXPOSE_DELIVERY_ETA', 'SUGGEST_BOUNDED_EXPERIMENT')",
            name="ck_merchant_autonomy_rules_action_type_valid",
        ),
        sa.CheckConstraint(
            "classification IN ('READ_ONLY', 'AUTO_LOW_RISK', "
            "'APPROVAL_REQUIRED', 'HUMAN_ONLY', 'PROHIBITED')",
            name="ck_merchant_autonomy_rules_classification_valid",
        ),
        sa.CheckConstraint(
            "max_executions_per_hour >= 1 AND max_executions_per_hour <= 100",
            name="ck_merchant_autonomy_rules_hourly_limit_bounds",
        ),
        sa.CheckConstraint(
            "max_executions_per_day >= 1 AND max_executions_per_day <= 1000",
            name="ck_merchant_autonomy_rules_daily_limit_bounds",
        ),
        sa.CheckConstraint(
            "cooldown_seconds >= 0 AND cooldown_seconds <= 86400",
            name="ck_merchant_autonomy_rules_cooldown_bounds",
        ),
        sa.CheckConstraint(
            "bounded_monetary_limit_paise >= 0",
            name="ck_merchant_autonomy_rules_monetary_limit_non_negative",
        ),
    )
    op.create_index(
        "ix_merchant_autonomy_rules_merchant_type",
        "merchant_autonomy_rules",
        ["merchant_id", "action_type"],
    )

    # 3. Create merchant_autonomy_actions table
    op.create_table(
        "merchant_autonomy_actions",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column(
            "merchant_id",
            sa.UUID(),
            sa.ForeignKey("merchants.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("agent_run_id", sa.UUID(), nullable=True, index=True),
        sa.Column(
            "proposal_id",
            sa.UUID(),
            sa.ForeignKey("merchant_proposals.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column("experiment_id", sa.UUID(), nullable=True, index=True),
        sa.Column("action_type", sa.String(64), nullable=False, index=True),
        sa.Column("target_entity_type", sa.String(64), nullable=False),
        sa.Column("target_entity_id", sa.UUID(), nullable=False, index=True),
        sa.Column("target_version_before", sa.Integer(), nullable=False),
        sa.Column("target_version_after", sa.Integer(), nullable=False),
        sa.Column("deterministic_classification", sa.String(32), nullable=False),
        sa.Column("autonomy_rule_hash", sa.String(64), nullable=False),
        sa.Column("autonomy_rule_version", sa.Integer(), nullable=False),
        sa.Column(
            "hourly_budget_consumed", sa.Integer(), nullable=False, server_default=sa.text("1")
        ),
        sa.Column(
            "daily_budget_consumed", sa.Integer(), nullable=False, server_default=sa.text("1")
        ),
        sa.Column("status", sa.String(32), nullable=False, server_default=sa.text("'EXECUTED'")),
        sa.Column("rollback_snapshot", sa.JSON(), nullable=False),
        sa.Column(
            "rollback_status", sa.String(32), nullable=False, server_default=sa.text("'AVAILABLE'")
        ),
        sa.Column("rolled_back_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rolled_back_by", sa.String(255), nullable=True),
        sa.Column("stopping_reason", sa.Text(), nullable=True),
        sa.Column(
            "anomaly_state", sa.String(32), nullable=False, server_default=sa.text("'NORMAL'")
        ),
        sa.Column("idempotency_key", sa.String(128), nullable=False, index=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["agent_run_id", "merchant_id"],
            ["agent_runs.id", "agent_runs.merchant_id"],
            name="fk_merchant_autonomy_actions_run_merchant",
        ),
        sa.ForeignKeyConstraint(
            ["experiment_id", "merchant_id"],
            ["merchant_experiments.id", "merchant_experiments.merchant_id"],
            name="fk_merchant_autonomy_actions_experiment_merchant",
        ),
        sa.CheckConstraint(
            "action_type IN ('IMPROVE_PRODUCT_DESCRIPTION', 'IMPROVE_DISCOVERY_METADATA', "
            "'REORDER_RECOMMENDATIONS', 'EXPOSE_DELIVERY_ETA', 'SUGGEST_BOUNDED_EXPERIMENT')",
            name="ck_merchant_autonomy_actions_action_type_valid",
        ),
        sa.CheckConstraint(
            "status IN ('EXECUTED', 'ROLLED_BACK', 'STOPPED', 'FAILED')",
            name="ck_merchant_autonomy_actions_status_valid",
        ),
        sa.CheckConstraint(
            "rollback_status IN ('AVAILABLE', 'ROLLED_BACK', 'EXPIRED', 'CONFLICT_REJECTED')",
            name="ck_merchant_autonomy_actions_rollback_status_valid",
        ),
        sa.CheckConstraint(
            "anomaly_state IN ('NORMAL', 'WARN', 'PAUSE_AUTONOMY', 'REQUIRE_HUMAN_REVIEW')",
            name="ck_merchant_autonomy_actions_anomaly_state_valid",
        ),
    )
    op.create_index(
        "ix_merchant_autonomy_actions_merchant_created",
        "merchant_autonomy_actions",
        ["merchant_id", "created_at"],
    )
    op.create_index(
        "ix_merchant_autonomy_actions_idempotency",
        "merchant_autonomy_actions",
        ["merchant_id", "idempotency_key"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_merchant_autonomy_actions_idempotency", table_name="merchant_autonomy_actions"
    )
    op.drop_index(
        "ix_merchant_autonomy_actions_merchant_created", table_name="merchant_autonomy_actions"
    )
    op.drop_table("merchant_autonomy_actions")

    op.drop_index("ix_merchant_autonomy_rules_merchant_type", table_name="merchant_autonomy_rules")
    op.drop_table("merchant_autonomy_rules")

    op.drop_column("merchants", "kill_switch_enabled")
