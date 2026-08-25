"""002_gateway_hardening_tables

Shared durable backing tables for the gateway hardening primitives:

- gateway_hardening_idempotency: cross-worker exactly-once claim registry for
  financial mutations (PRIMARY KEY uniqueness is the atomicity primitive).
- gateway_hardening_rate_events: shared sliding-window rate-limit events.

Both tables are only exercised when GATEWAY_DURABLE_HARDENING=true; the
runtime layer (gateway/durable.py) also creates them idempotently as a
deployment safety net.

Revision ID: 002_gateway_hardening
Revises: 001_initial_schema
Create Date: 2026-08-25 00:00:00.000000 UTC
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "002_gateway_hardening"
down_revision: str | None = "001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "gateway_hardening_idempotency",
        sa.Column("key", sa.String(768), primary_key=True),
        sa.Column("state", sa.String(16), nullable=False),
        sa.Column("envelope", sa.Text(), nullable=True),
        sa.Column("capability", sa.String(128), nullable=True),
        sa.Column("payload_hash", sa.String(64), nullable=True),
        sa.Column("created_at", sa.Double(), nullable=False),
        sa.Column("expires_at", sa.Double(), nullable=False),
    )
    op.create_index(
        "ix_gwh_idem_expires",
        "gateway_hardening_idempotency",
        ["expires_at"],
    )

    op.create_table(
        "gateway_hardening_rate_events",
        sa.Column("client_key", sa.String(768), nullable=False),
        sa.Column("ts", sa.Double(), nullable=False),
    )
    op.create_index(
        "ix_gwh_rate_key_ts",
        "gateway_hardening_rate_events",
        ["client_key", "ts"],
    )


def downgrade() -> None:
    op.drop_table("gateway_hardening_rate_events")
    op.drop_table("gateway_hardening_idempotency")
