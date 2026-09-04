"""Use opaque discovery identifiers instead of merchant database identifiers.

Revision ID: 016_phase9_public_discovery_identifiers
Revises: 015_phase9_discovery_network
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "016_phase9_public_discovery_identifiers"
down_revision: str | None = "015_phase9_discovery_network"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add a stable, opaque public ID to every discovery profile."""
    op.add_column(
        "merchant_discovery_profiles",
        sa.Column("public_id", sa.UUID(), nullable=True),
    )
    # Existing profile IDs are random UUIDs and are not merchant identifiers.
    # Reusing them for the one-time backfill avoids a database-extension dependency.
    op.execute("UPDATE merchant_discovery_profiles SET public_id = id WHERE public_id IS NULL")
    op.alter_column("merchant_discovery_profiles", "public_id", nullable=False)
    op.create_unique_constraint(
        "uq_discovery_profiles_public_id",
        "merchant_discovery_profiles",
        ["public_id"],
    )
    op.create_index(
        "ix_discovery_profiles_public_id",
        "merchant_discovery_profiles",
        ["public_id"],
    )


def downgrade() -> None:
    """Remove the opaque public identifier."""
    op.drop_index("ix_discovery_profiles_public_id", table_name="merchant_discovery_profiles")
    op.drop_constraint(
        "uq_discovery_profiles_public_id",
        "merchant_discovery_profiles",
        type_="unique",
    )
    op.drop_column("merchant_discovery_profiles", "public_id")
