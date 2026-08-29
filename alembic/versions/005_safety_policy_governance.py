"""005_safety_policy_governance

Adds:
- merchant_approvals table for Human-In-The-Loop (HITL) approval gates and governance

Revision ID: 005_safety_policy_governance
Revises: 004_payment_reliability
Create Date: 2026-08-28 00:00:00.000000 UTC
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "005_safety_policy_governance"
down_revision: str | None = "004_payment_reliability"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "merchant_approvals",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column(
            "merchant_id",
            sa.UUID(),
            sa.ForeignKey("merchants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "quote_id",
            sa.UUID(),
            sa.ForeignKey("price_quotes.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column(
            "order_id",
            sa.UUID(),
            sa.ForeignKey("orders.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "session_id",
            sa.UUID(),
            sa.ForeignKey("buyer_agent_sessions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("approval_type", sa.String(64), nullable=False, server_default="QUOTE_DISCOUNT"),
        sa.Column("status", sa.String(32), nullable=False, server_default="PENDING"),
        sa.Column("requested_amount_paise", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("proposed_discount_paise", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("policy_decision_hash", sa.String(64), nullable=False),
        sa.Column("policy_rule_code", sa.String(64), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("approver_identifier", sa.String(128), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.BigInteger(), nullable=False, server_default="1"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint(
            "status IN ('PENDING', 'APPROVED', 'REJECTED', 'EXPIRED')",
            name="ck_merchant_approvals_status_valid",
        ),
        sa.CheckConstraint(
            "approval_type IN ('QUOTE_DISCOUNT', 'ORDER_LIMIT', 'GENERAL')",
            name="ck_merchant_approvals_type_valid",
        ),
        sa.CheckConstraint(
            "requested_amount_paise >= 0",
            name="ck_merchant_approvals_requested_amount_non_negative",
        ),
        sa.CheckConstraint(
            "proposed_discount_paise >= 0",
            name="ck_merchant_approvals_proposed_discount_non_negative",
        ),
    )
    op.create_index("ix_merchant_approvals_merchant_id", "merchant_approvals", ["merchant_id"])
    op.create_index("ix_merchant_approvals_quote_id", "merchant_approvals", ["quote_id"])
    op.create_index("ix_merchant_approvals_order_id", "merchant_approvals", ["order_id"])
    op.create_index("ix_merchant_approvals_session_id", "merchant_approvals", ["session_id"])
    op.create_index("ix_merchant_approvals_status", "merchant_approvals", ["status"])
    op.create_index("ix_merchant_approvals_expires_at", "merchant_approvals", ["expires_at"])


def downgrade() -> None:
    op.drop_table("merchant_approvals")
