"""Add durable merchant control-plane idempotency receipts.

Revision ID: 006_merchant_mutation_receipts
Revises: 005_safety_policy_governance
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "006_merchant_mutation_receipts"
down_revision: str | None = "005_safety_policy_governance"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "merchant_mutation_receipts",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column(
            "merchant_id",
            sa.UUID(),
            sa.ForeignKey("merchants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("operation", sa.String(length=128), nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("response_body", sa.JSON(), nullable=True),
        sa.Column("response_status", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint(
            "merchant_id",
            "operation",
            "idempotency_key",
            name="uq_merchant_mutation_receipts_operation_key",
        ),
    )
    op.create_index(
        "ix_merchant_mutation_receipts_merchant_id",
        "merchant_mutation_receipts",
        ["merchant_id"],
    )


def downgrade() -> None:
    op.drop_table("merchant_mutation_receipts")
