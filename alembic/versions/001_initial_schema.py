"""001_initial_schema

Initial migration establishing the 12 canonical domain tables:
- merchants
- products
- product_variants
- inventory_items
- buyer_agent_sessions
- buyer_intents
- price_quotes
- quote_items
- orders
- order_items
- payment_attempts
- transaction_records
- policy_rules
- audit_events
- agent_runs

Revision ID: 001_initial_schema
Revises: None
Create Date: 2026-08-22 00:00:00.000000 UTC
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Merchants Table
    op.create_table(
        "merchants",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="ACTIVE"),
        sa.Column("currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("rzp_key_id", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.BigInteger(), nullable=False, server_default="1"),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'PAUSED', 'SUSPENDED')",
            name="ck_merchants_status_valid",
        ),
    )
    op.create_index("ix_merchants_slug", "merchants", ["slug"], unique=True)

    # 2. Products Table
    op.create_table(
        "products",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "merchant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("merchants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sku", sa.String(100), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("base_price_paise", sa.BigInteger(), nullable=False),
        sa.Column("floor_price_paise", sa.BigInteger(), nullable=False),
        sa.Column("is_negotiable", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("attributes", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.BigInteger(), nullable=False, server_default="1"),
        sa.UniqueConstraint("merchant_id", "sku", name="uq_products_merchant_sku"),
        sa.CheckConstraint("base_price_paise > 0", name="ck_products_base_price_positive"),
        sa.CheckConstraint("floor_price_paise > 0", name="ck_products_floor_price_positive"),
        sa.CheckConstraint(
            "floor_price_paise <= base_price_paise",
            name="ck_products_floor_lte_base_price",
        ),
    )
    op.create_index("ix_products_merchant_id", "products", ["merchant_id"])
    op.create_index("ix_products_sku", "products", ["sku"])
    op.create_index("ix_products_category", "products", ["category"])

    # 3. Product Variants Table
    op.create_table(
        "product_variants",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "product_id",
            UUID(as_uuid=True),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sku", sa.String(100), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("price_override_paise", sa.BigInteger(), nullable=True),
        sa.Column("attributes", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.BigInteger(), nullable=False, server_default="1"),
        sa.UniqueConstraint("product_id", "sku", name="uq_product_variants_product_sku"),
        sa.CheckConstraint(
            "price_override_paise IS NULL OR price_override_paise > 0",
            name="ck_product_variants_price_override_positive",
        ),
    )
    op.create_index("ix_product_variants_product_id", "product_variants", ["product_id"])
    op.create_index("ix_product_variants_sku", "product_variants", ["sku"])

    # 4. Inventory Items Table
    op.create_table(
        "inventory_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "variant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("product_variants.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("available_quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reserved_quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("safety_threshold", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.BigInteger(), nullable=False, server_default="1"),
        sa.CheckConstraint(
            "available_quantity >= 0",
            name="ck_inventory_available_non_negative",
        ),
        sa.CheckConstraint(
            "reserved_quantity >= 0",
            name="ck_inventory_reserved_non_negative",
        ),
        sa.CheckConstraint(
            "safety_threshold >= 0",
            name="ck_inventory_safety_threshold_non_negative",
        ),
    )
    op.create_index("ix_inventory_items_variant_id", "inventory_items", ["variant_id"], unique=True)

    # 5. Buyer Agent Sessions Table
    op.create_table(
        "buyer_agent_sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "merchant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("merchants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("buyer_agent_identifier", sa.String(255), nullable=False),
        sa.Column("auth_token_hash", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="ACTIVE"),
        sa.Column("total_tool_calls", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'EXPIRED', 'TERMINATED')",
            name="ck_buyer_sessions_status_valid",
        ),
        sa.CheckConstraint(
            "total_tool_calls >= 0",
            name="ck_buyer_sessions_tool_calls_non_negative",
        ),
    )
    op.create_index("ix_buyer_agent_sessions_merchant_id", "buyer_agent_sessions", ["merchant_id"])
    op.create_index(
        "ix_buyer_agent_sessions_buyer_agent_identifier",
        "buyer_agent_sessions",
        ["buyer_agent_identifier"],
    )

    # 6. Buyer Intents Table
    op.create_table(
        "buyer_intents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            UUID(as_uuid=True),
            sa.ForeignKey("buyer_agent_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("raw_query", sa.Text(), nullable=False),
        sa.Column("extracted_intent", sa.String(64), nullable=False),
        sa.Column("extracted_entities", sa.JSON(), nullable=False),
        sa.Column("confidence_score", sa.Numeric(4, 3), nullable=False, server_default="1.000"),
        sa.Column("validation_status", sa.String(32), nullable=False, server_default="VALIDATED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "validation_status IN ('VALIDATED', 'REJECTED', 'MALFORMED')",
            name="ck_buyer_intents_validation_status_valid",
        ),
        sa.CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_buyer_intents_confidence_score_range",
        ),
    )
    op.create_index("ix_buyer_intents_session_id", "buyer_intents", ["session_id"])
    op.create_index("ix_buyer_intents_extracted_intent", "buyer_intents", ["extracted_intent"])

    # 7. Price Quotes Table
    op.create_table(
        "price_quotes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            UUID(as_uuid=True),
            sa.ForeignKey("buyer_agent_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "merchant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("merchants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(32), nullable=False, server_default="PROPOSED"),
        sa.Column("subtotal_paise", sa.BigInteger(), nullable=False),
        sa.Column("discount_paise", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("shipping_paise", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("total_paise", sa.BigInteger(), nullable=False),
        sa.Column("discount_reason", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.BigInteger(), nullable=False, server_default="1"),
        sa.UniqueConstraint("idempotency_key", name="uq_price_quotes_idempotency_key"),
        sa.CheckConstraint(
            "status IN ('DRAFT', 'PROPOSED', 'NEGOTIATING', 'ACCEPTED', 'EXPIRED', "
            "'SUPERSEDED', 'REJECTED')",
            name="ck_price_quotes_status_valid",
        ),
        sa.CheckConstraint("subtotal_paise >= 0", name="ck_price_quotes_subtotal_non_negative"),
        sa.CheckConstraint("discount_paise >= 0", name="ck_price_quotes_discount_non_negative"),
        sa.CheckConstraint("shipping_paise >= 0", name="ck_price_quotes_shipping_non_negative"),
        sa.CheckConstraint("total_paise >= 0", name="ck_price_quotes_total_non_negative"),
        sa.CheckConstraint(
            "total_paise = subtotal_paise - discount_paise + shipping_paise",
            name="ck_price_quotes_total_arithmetic",
        ),
    )
    op.create_index("ix_price_quotes_session_id", "price_quotes", ["session_id"])
    op.create_index("ix_price_quotes_merchant_id", "price_quotes", ["merchant_id"])
    op.create_index("ix_price_quotes_status", "price_quotes", ["status"])
    op.create_index("ix_price_quotes_expires_at", "price_quotes", ["expires_at"])
    op.create_index(
        "ix_price_quotes_idempotency_key", "price_quotes", ["idempotency_key"], unique=True
    )

    # 8. Quote Items Table
    op.create_table(
        "quote_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "quote_id",
            UUID(as_uuid=True),
            sa.ForeignKey("price_quotes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "variant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("product_variants.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("unit_price_paise", sa.BigInteger(), nullable=False),
        sa.Column("total_price_paise", sa.BigInteger(), nullable=False),
        sa.CheckConstraint("quantity > 0", name="ck_quote_items_quantity_positive"),
        sa.CheckConstraint("unit_price_paise > 0", name="ck_quote_items_unit_price_positive"),
        sa.CheckConstraint(
            "total_price_paise = unit_price_paise * quantity",
            name="ck_quote_items_total_arithmetic",
        ),
    )
    op.create_index("ix_quote_items_quote_id", "quote_items", ["quote_id"])
    op.create_index("ix_quote_items_variant_id", "quote_items", ["variant_id"])

    # 9. Orders Table
    op.create_table(
        "orders",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "quote_id",
            UUID(as_uuid=True),
            sa.ForeignKey("price_quotes.id", ondelete="RESTRICT"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "merchant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("merchants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(32), nullable=False, server_default="CREATED"),
        sa.Column("amount_paise", sa.BigInteger(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("buyer_email", sa.String(255), nullable=False),
        sa.Column("shipping_address", sa.JSON(), nullable=False),
        sa.Column("rzp_order_id", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.BigInteger(), nullable=False, server_default="1"),
        sa.CheckConstraint(
            "status IN ('CREATED', 'PENDING_PAYMENT', 'PAYMENT_PROCESSING', 'PAID', "
            "'PAYMENT_FAILED', 'FULFILLMENT_PENDING', 'COMPLETED', 'CANCELLED', "
            "'EXPIRED', 'REFUNDED')",
            name="ck_orders_status_valid",
        ),
        sa.CheckConstraint("amount_paise > 0", name="ck_orders_amount_positive"),
    )
    op.create_index("ix_orders_quote_id", "orders", ["quote_id"], unique=True)
    op.create_index("ix_orders_merchant_id", "orders", ["merchant_id"])
    op.create_index("ix_orders_status", "orders", ["status"])
    op.create_index("ix_orders_rzp_order_id", "orders", ["rzp_order_id"], unique=True)

    # 10. Order Items Table
    op.create_table(
        "order_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "order_id",
            UUID(as_uuid=True),
            sa.ForeignKey("orders.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "variant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("product_variants.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("unit_price_paise", sa.BigInteger(), nullable=False),
        sa.Column("total_price_paise", sa.BigInteger(), nullable=False),
        sa.CheckConstraint("quantity > 0", name="ck_order_items_quantity_positive"),
        sa.CheckConstraint("unit_price_paise > 0", name="ck_order_items_unit_price_positive"),
        sa.CheckConstraint(
            "total_price_paise = unit_price_paise * quantity",
            name="ck_order_items_total_arithmetic",
        ),
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])
    op.create_index("ix_order_items_variant_id", "order_items", ["variant_id"])

    # 11. Payment Attempts Table
    op.create_table(
        "payment_attempts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "order_id",
            UUID(as_uuid=True),
            sa.ForeignKey("orders.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("rzp_payment_id", sa.String(64), nullable=True),
        sa.Column("rzp_order_id", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="INITIATED"),
        sa.Column("amount_paise", sa.BigInteger(), nullable=False),
        sa.Column("payment_method", sa.String(32), nullable=True),
        sa.Column("error_code", sa.String(64), nullable=True),
        sa.Column("error_description", sa.Text(), nullable=True),
        sa.Column("webhook_payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('INITIATED', 'ORDER_CREATED', 'PAYMENT_PENDING', 'AUTHORIZED', "
            "'CAPTURED', 'FAILED', 'REFUNDED', 'TIMED_OUT')",
            name="ck_payment_attempts_status_valid",
        ),
        sa.CheckConstraint("amount_paise > 0", name="ck_payment_attempts_amount_positive"),
    )
    op.create_index("ix_payment_attempts_order_id", "payment_attempts", ["order_id"])
    op.create_index(
        "ix_payment_attempts_rzp_payment_id", "payment_attempts", ["rzp_payment_id"], unique=True
    )
    op.create_index("ix_payment_attempts_rzp_order_id", "payment_attempts", ["rzp_order_id"])
    op.create_index("ix_payment_attempts_status", "payment_attempts", ["status"])

    # 12. Transaction Records Table
    op.create_table(
        "transaction_records",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "payment_attempt_id",
            UUID(as_uuid=True),
            sa.ForeignKey("payment_attempts.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "merchant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("merchants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("entry_type", sa.String(32), nullable=False),
        sa.Column("amount_paise", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="COMMITTED"),
        sa.Column("settlement_ref", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "entry_type IN ('CREDIT', 'DEBIT_REFUND')",
            name="ck_transaction_records_entry_type_valid",
        ),
        sa.CheckConstraint("amount_paise > 0", name="ck_transaction_records_amount_positive"),
        sa.CheckConstraint(
            "status IN ('UNCOMMITTED', 'COMMITTED', 'REVERSED')",
            name="ck_transaction_records_status_valid",
        ),
    )
    op.create_index(
        "ix_transaction_records_payment_attempt_id",
        "transaction_records",
        ["payment_attempt_id"],
    )
    op.create_index("ix_transaction_records_merchant_id", "transaction_records", ["merchant_id"])
    op.create_index("ix_transaction_records_entry_type", "transaction_records", ["entry_type"])
    op.create_index("ix_transaction_records_status", "transaction_records", ["status"])
    op.create_index("ix_transaction_records_created_at", "transaction_records", ["created_at"])

    # 13. Policy Rules Table
    op.create_table(
        "policy_rules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "merchant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("merchants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("rule_type", sa.String(64), nullable=False),
        sa.Column("target_scope", sa.String(64), nullable=False, server_default="GLOBAL"),
        sa.Column("target_id", sa.String(128), nullable=True),
        sa.Column("rule_value", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "rule_type IN ('MAX_DISCOUNT_PCT', 'MIN_MARGIN_PCT', 'MAX_CART_VALUE', "
            "'AUTONOMY_LEVEL', 'SHIPPING_FEE')",
            name="ck_policy_rules_type_valid",
        ),
        sa.CheckConstraint(
            "target_scope IN ('GLOBAL', 'CATEGORY', 'SKU')",
            name="ck_policy_rules_scope_valid",
        ),
    )
    op.create_index("ix_policy_rules_merchant_id", "policy_rules", ["merchant_id"])
    op.create_index("ix_policy_rules_rule_type", "policy_rules", ["rule_type"])
    op.create_index("ix_policy_rules_is_active", "policy_rules", ["is_active"])

    # 14. Audit Events Table
    op.create_table(
        "audit_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "merchant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("merchants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "session_id",
            UUID(as_uuid=True),
            sa.ForeignKey("buyer_agent_sessions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("actor_type", sa.String(32), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("prev_event_hash", sa.String(64), nullable=True),
        sa.Column("event_hash", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "actor_type IN ('BUYER_AGENT', 'LLM_MODEL', 'MERCHANT_ADMIN', 'SYSTEM')",
            name="ck_audit_events_actor_type_valid",
        ),
    )
    op.create_index("ix_audit_events_merchant_id", "audit_events", ["merchant_id"])
    op.create_index("ix_audit_events_session_id", "audit_events", ["session_id"])
    op.create_index("ix_audit_events_actor_type", "audit_events", ["actor_type"])
    op.create_index("ix_audit_events_event_type", "audit_events", ["event_type"])
    op.create_index("ix_audit_events_created_at", "audit_events", ["created_at"])

    # 15. Agent Runs Table
    op.create_table(
        "agent_runs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            UUID(as_uuid=True),
            sa.ForeignKey("buyer_agent_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(32), nullable=False, server_default="PENDING"),
        sa.Column("step_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('PENDING', 'RUNNING', 'AWAITING_TOOL', 'EVALUATING_POLICY', "
            "'EXECUTING_ACTION', 'COMPLETED', 'FAILED', 'KILLED')",
            name="ck_agent_runs_status_valid",
        ),
        sa.CheckConstraint(
            "step_count >= 0 AND step_count <= 5",
            name="ck_agent_runs_step_count_bounded",
        ),
        sa.CheckConstraint("total_tokens >= 0", name="ck_agent_runs_tokens_non_negative"),
    )
    op.create_index("ix_agent_runs_session_id", "agent_runs", ["session_id"])
    op.create_index("ix_agent_runs_status", "agent_runs", ["status"])


def downgrade() -> None:
    op.drop_table("agent_runs")
    op.drop_table("audit_events")
    op.drop_table("policy_rules")
    op.drop_table("transaction_records")
    op.drop_table("payment_attempts")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("quote_items")
    op.drop_table("price_quotes")
    op.drop_table("buyer_intents")
    op.drop_table("buyer_agent_sessions")
    op.drop_table("inventory_items")
    op.drop_table("product_variants")
    op.drop_table("products")
    op.drop_table("merchants")
