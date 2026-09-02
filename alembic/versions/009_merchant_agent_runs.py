"""Allow durable merchant-scoped AgentRun records for Phase 7 intelligence turns.

Revision ID: 009_merchant_agent_runs
Revises: 008_merchant_agent_experiments
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "009_merchant_agent_runs"
down_revision: str | None = "008_merchant_agent_experiments"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("agent_runs", sa.Column("merchant_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "fk_agent_runs_merchant_id_merchants",
        "agent_runs",
        "merchants",
        ["merchant_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_agent_runs_merchant_id", "agent_runs", ["merchant_id"])
    op.alter_column("agent_runs", "session_id", existing_type=sa.UUID(), nullable=True)
    op.create_check_constraint(
        "ck_agent_runs_session_or_merchant_required",
        "agent_runs",
        "session_id IS NOT NULL OR merchant_id IS NOT NULL",
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM agent_runs WHERE session_id IS NULL) THEN
                    RAISE EXCEPTION
                        'Cannot downgrade 009_merchant_agent_runs while merchant-scoped '
                        'AgentRun records exist. '
                        'Archive or explicitly dispose of those records before rollback.';
                END IF;
            END $$;
            """
        )
    )
    op.drop_constraint("ck_agent_runs_session_or_merchant_required", "agent_runs", type_="check")
    op.alter_column("agent_runs", "session_id", existing_type=sa.UUID(), nullable=False)
    op.drop_index("ix_agent_runs_merchant_id", table_name="agent_runs")
    op.drop_constraint("fk_agent_runs_merchant_id_merchants", "agent_runs", type_="foreignkey")
    op.drop_column("agent_runs", "merchant_id")
