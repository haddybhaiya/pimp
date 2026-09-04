"""Phase 9 Discovery Network: MerchantDiscoveryProfile and MerchantDiscoveryTelemetry.

Revision ID: 015_phase9_discovery_network
Revises: 014_autonomy_failure_telemetry
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "015_phase9_discovery_network"
down_revision: str | None = "014_autonomy_failure_telemetry"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create discovery profile and telemetry tables."""
    # 1. merchant_discovery_profiles
    op.create_table(
        "merchant_discovery_profiles",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column(
            "merchant_id",
            sa.UUID(),
            sa.ForeignKey("merchants.id", ondelete="CASCADE"),
            unique=True,
            nullable=False,
            index=True,
        ),
        sa.Column(
            "discoverability_state",
            sa.String(32),
            nullable=False,
            server_default="PRIVATE",
            index=True,
        ),
        sa.Column(
            "custom_tags",
            sa.JSON().with_variant(postgresql.JSONB, "postgresql"),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("custom_description", sa.String(1000), nullable=True),
        sa.Column(
            "delivery_regions",
            sa.JSON().with_variant(postgresql.JSONB, "postgresql"),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("profile_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("metadata_hash", sa.String(64), nullable=False),
        sa.Column(
            "last_refreshed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "discoverability_state IN ('PRIVATE', 'DISCOVERABLE', 'PAUSED', 'SUSPENDED')",
            name="ck_discovery_profiles_state_valid",
        ),
    )

    # 2. merchant_discovery_telemetry
    op.create_table(
        "merchant_discovery_telemetry",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column(
            "merchant_id",
            sa.UUID(),
            sa.ForeignKey("merchants.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("event_type", sa.String(64), nullable=False, index=True),
        sa.Column("correlation_id", sa.String(255), nullable=False, index=True),
        sa.Column("sanitized_query", sa.String(255), nullable=True),
        sa.Column("product_id", sa.UUID(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "event_type IN ("
            "'SEARCH_RECEIVED', "
            "'MERCHANT_RETURNED', "
            "'MERCHANT_SELECTED', "
            "'PRODUCT_SELECTED', "
            "'HANDOFF_INITIATED'"
            ")",
            name="ck_discovery_telemetry_event_type_valid",
        ),
        sa.UniqueConstraint(
            "merchant_id",
            "event_type",
            "correlation_id",
            name="uq_discovery_telemetry_replay",
        ),
    )


def downgrade() -> None:
    """Drop discovery tables."""
    op.drop_table("merchant_discovery_telemetry")
    op.drop_table("merchant_discovery_profiles")
