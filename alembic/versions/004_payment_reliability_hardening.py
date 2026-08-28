"""004_payment_reliability_hardening

Adds:
- processed_webhooks table for atomic deduplication and replay protection
- unique constraint uq_transaction_records_settlement_entry on transaction_records

Revision ID: 004_payment_reliability
Revises: 003_session_capability_grants
Create Date: 2026-08-27 00:00:00.000000 UTC
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "004_payment_reliability"
down_revision: str | None = "003_session_capability_grants"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "processed_webhooks",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("event_id", sa.String(128), nullable=True),
        sa.Column("event_name", sa.String(64), nullable=False),
        sa.Column("payload_hash", sa.String(64), nullable=False),
        sa.Column("signature_hash", sa.String(64), nullable=False),
        sa.Column("rzp_order_id", sa.String(64), nullable=True),
        sa.Column("rzp_payment_id", sa.String(64), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="PROCESSING"),
        sa.Column("response_payload", sa.JSON(), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint("payload_hash", name="uq_processed_webhooks_payload_hash"),
    )
    op.create_index("ix_processed_webhooks_event_id", "processed_webhooks", ["event_id"])
    op.create_index("ix_processed_webhooks_event_name", "processed_webhooks", ["event_name"])
    op.create_index("ix_processed_webhooks_payload_hash", "processed_webhooks", ["payload_hash"])
    op.create_index("ix_processed_webhooks_rzp_order_id", "processed_webhooks", ["rzp_order_id"])
    op.create_index(
        "ix_processed_webhooks_rzp_payment_id", "processed_webhooks", ["rzp_payment_id"]
    )
    op.create_index("ix_processed_webhooks_status", "processed_webhooks", ["status"])

    op.alter_column(
        "transaction_records",
        "settlement_ref",
        existing_type=sa.String(128),
        nullable=False,
    )

    op.create_unique_constraint(
        "uq_transaction_records_settlement_entry",
        "transaction_records",
        ["settlement_ref", "entry_type"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_transaction_records_settlement_entry",
        "transaction_records",
        type_="unique",
    )
    op.alter_column(
        "transaction_records",
        "settlement_ref",
        existing_type=sa.String(128),
        nullable=True,
    )
    op.drop_table("processed_webhooks")
