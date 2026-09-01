"""Bind merchants to verified InsForge users.

Revision ID: 007_merchant_auth_user_binding
Revises: 006_merchant_mutation_receipts
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "007_merchant_auth_user_binding"
down_revision: str | None = "006_merchant_mutation_receipts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("merchants", sa.Column("auth_user_id", sa.UUID(), nullable=True))
    op.create_index("ix_merchants_auth_user_id", "merchants", ["auth_user_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_merchants_auth_user_id", table_name="merchants")
    op.drop_column("merchants", "auth_user_id")
