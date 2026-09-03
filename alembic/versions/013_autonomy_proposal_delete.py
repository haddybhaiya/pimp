"""Preserve autonomy history when an optional proposal is deleted.

Revision ID: 013_autonomy_proposal_delete
Revises: 012_autonomy_proposal_integrity
"""

from collections.abc import Sequence

from alembic import op

revision: str = "013_autonomy_proposal_delete"
down_revision: str | None = "012_autonomy_proposal_integrity"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Clear only proposal_id while retaining the tenant-scoped action ledger."""
    op.drop_constraint(
        "fk_merchant_autonomy_actions_proposal_merchant",
        "merchant_autonomy_actions",
        type_="foreignkey",
    )
    op.execute(
        """
        ALTER TABLE merchant_autonomy_actions
        ADD CONSTRAINT fk_merchant_autonomy_actions_proposal_merchant
        FOREIGN KEY (proposal_id, merchant_id)
        REFERENCES merchant_proposals (id, merchant_id)
        ON DELETE SET NULL (proposal_id)
        """
    )


def downgrade() -> None:
    """Restore migration 012's tenant-coupled NO ACTION behavior."""
    op.drop_constraint(
        "fk_merchant_autonomy_actions_proposal_merchant",
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
