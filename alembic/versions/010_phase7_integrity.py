"""Strengthen Phase 7 tenant, audit-linkage, and sandbox integrity constraints.

Revision ID: 010_phase7_integrity
Revises: 009_merchant_agent_runs
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "010_phase7_integrity"
down_revision: str | None = "009_merchant_agent_runs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add database-owned tenant and audit-linkage constraints without rewriting history."""
    op.create_unique_constraint("uq_agent_runs_id_merchant", "agent_runs", ["id", "merchant_id"])
    op.create_foreign_key(
        "fk_merchant_proposals_run_merchant",
        "merchant_proposals",
        "agent_runs",
        ["run_id", "merchant_id"],
        ["id", "merchant_id"],
    )

    op.create_unique_constraint(
        "uq_merchant_experiments_id_merchant",
        "merchant_experiments",
        ["id", "merchant_id"],
    )
    op.create_foreign_key(
        "fk_merchant_experiment_results_experiment_merchant",
        "merchant_experiment_results",
        "merchant_experiments",
        ["experiment_id", "merchant_id"],
        ["id", "merchant_id"],
        ondelete="CASCADE",
    )

    op.add_column(
        "merchant_proposals",
        sa.Column(
            "estimated_cost_paise",
            sa.BigInteger(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.create_check_constraint(
        "ck_merchant_proposals_estimated_cost_non_negative",
        "merchant_proposals",
        "estimated_cost_paise >= 0",
    )

    # This is intentionally not exposed through merchant catalog request schemas.
    # Backfill only legacy canonical demo records that carry the previous server
    # seed marker; future writes are owned exclusively by the demo seeder.
    op.add_column(
        "products",
        sa.Column(
            "is_demo_sandbox_product",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.execute(
        sa.text(
            """
            UPDATE products
            SET is_demo_sandbox_product = true
            WHERE sku IN ('RUN-PRO-01', 'AIR-VEST-02', 'PACE-BAND-03')
              AND attributes ->> 'demo_seeded' = 'true'
            """
        )
    )


def downgrade() -> None:
    """Remove forward-only Phase 7 integrity additions."""
    op.drop_column("products", "is_demo_sandbox_product")
    op.drop_constraint(
        "ck_merchant_proposals_estimated_cost_non_negative",
        "merchant_proposals",
        type_="check",
    )
    op.drop_column("merchant_proposals", "estimated_cost_paise")
    op.drop_constraint(
        "fk_merchant_experiment_results_experiment_merchant",
        "merchant_experiment_results",
        type_="foreignkey",
    )
    op.drop_constraint(
        "uq_merchant_experiments_id_merchant",
        "merchant_experiments",
        type_="unique",
    )
    op.drop_constraint(
        "fk_merchant_proposals_run_merchant",
        "merchant_proposals",
        type_="foreignkey",
    )
    op.drop_constraint("uq_agent_runs_id_merchant", "agent_runs", type_="unique")
