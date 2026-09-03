"""Persist rejected autonomy attempts for the anomaly circuit breaker.

Revision ID: 014_autonomy_failure_telemetry
Revises: 013_autonomy_proposal_delete
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "014_autonomy_failure_telemetry"
down_revision: str | None = "013_autonomy_proposal_delete"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create a durable, non-mutating failure-attempt ledger."""
    op.create_table(
        "merchant_autonomy_failures",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column(
            "merchant_id",
            sa.UUID(),
            sa.ForeignKey("merchants.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("proposal_id", sa.UUID(), nullable=True, index=True),
        sa.Column("action_type", sa.String(64), nullable=True, index=True),
        sa.Column("failure_code", sa.String(64), nullable=False),
        sa.Column("idempotency_key", sa.String(255), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint(
            "failure_code IN ('PRECONDITION_REJECTED', 'OPTIMISTIC_CONFLICT')",
            name="ck_merchant_autonomy_failures_code_valid",
        ),
    )
    op.create_index(
        "ix_merchant_autonomy_failures_merchant_created",
        "merchant_autonomy_failures",
        ["merchant_id", "created_at"],
    )


def downgrade() -> None:
    """Remove failure telemetry while leaving successful action history intact."""
    op.drop_index(
        "ix_merchant_autonomy_failures_merchant_created",
        table_name="merchant_autonomy_failures",
    )
    op.drop_table("merchant_autonomy_failures")
