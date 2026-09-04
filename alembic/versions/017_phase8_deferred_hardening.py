"""Constrain autonomy-rule experiment duration at the database boundary.

Revision ID: 017_phase8_deferred_hardening
Revises: 016_phase9_public_ids
"""

from collections.abc import Sequence

from alembic import op

revision: str = "017_phase8_deferred_hardening"
down_revision: str | None = "016_phase9_public_ids"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Reject invalid experiment durations from every database writer."""
    op.create_check_constraint(
        "ck_merchant_autonomy_rules_experiment_duration_bounds",
        "merchant_autonomy_rules",
        "experiment_duration_limit_days >= 1 AND experiment_duration_limit_days <= 365",
    )


def downgrade() -> None:
    """Remove the Phase 8 duration constraint."""
    op.drop_constraint(
        "ck_merchant_autonomy_rules_experiment_duration_bounds",
        "merchant_autonomy_rules",
        type_="check",
    )
