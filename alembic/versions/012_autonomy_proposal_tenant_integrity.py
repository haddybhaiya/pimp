"""Bind autonomous-action proposals to the owning merchant.

Revision ID: 012_autonomy_proposal_integrity
Revises: 011_phase8_controlled_autonomy
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "012_autonomy_proposal_integrity"
down_revision: str | None = "011_phase8_controlled_autonomy"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Require autonomous action proposal references to remain tenant scoped."""
    # Existing production data must already satisfy the service-level ownership
    # check. Refuse the migration rather than silently repairing an audit link.
    op.execute(
        sa.text(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM merchant_autonomy_actions action
                    JOIN merchant_proposals proposal ON proposal.id = action.proposal_id
                    WHERE action.proposal_id IS NOT NULL
                      AND action.merchant_id <> proposal.merchant_id
                ) THEN
                    RAISE EXCEPTION
                        'Cannot apply 012: cross-merchant autonomous action proposal links exist';
                END IF;
            END $$;
            """
        )
    )
    op.create_unique_constraint(
        "uq_merchant_proposals_id_merchant",
        "merchant_proposals",
        ["id", "merchant_id"],
    )
    op.drop_constraint(
        "fk_merchant_autonomy_actions_proposal_id_merchant_proposals",
        "merchant_autonomy_actions",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_merchant_autonomy_actions_proposal_merchant",
        "merchant_autonomy_actions",
        "merchant_proposals",
        ["proposal_id", "merchant_id"],
        ["id", "merchant_id"],
    )


def downgrade() -> None:
    """Restore the previous ID-only proposal reference for a deliberate rollback."""
    op.drop_constraint(
        "fk_merchant_autonomy_actions_proposal_merchant",
        "merchant_autonomy_actions",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_merchant_autonomy_actions_proposal_id_merchant_proposals",
        "merchant_autonomy_actions",
        "merchant_proposals",
        ["proposal_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.drop_constraint(
        "uq_merchant_proposals_id_merchant",
        "merchant_proposals",
        type_="unique",
    )
