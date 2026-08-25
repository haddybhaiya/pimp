"""003_session_capability_grants

Persists the authoritative capability grant on BuyerAgentSession so the
dispatcher can derive authorization server-side instead of trusting
session presence (fail-closed capability derivation).

Nullable by design: legacy rows without a stored grant retain the previous
full-default-grant behavior; newly initialized sessions always persist an
explicit grant.

Revision ID: 003_session_capability_grants
Revises: 002_gateway_hardening
Create Date: 2026-08-25 00:00:00.000000 UTC
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "003_session_capability_grants"
down_revision: str | None = "002_gateway_hardening"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "buyer_agent_sessions",
        sa.Column("granted_capabilities", sa.String(512), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("buyer_agent_sessions", "granted_capabilities")
