"""PolicyRule canonical entity model."""

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Boolean, CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agent_ready_merchant.db.base import GUID, Base, TimestampMixin

if TYPE_CHECKING:
    from agent_ready_merchant.models.merchant import Merchant


class PolicyRule(Base, TimestampMixin):
    """Deterministic merchant policy rule governing discounts, margins, and limits."""

    __tablename__ = "policy_rules"

    __table_args__ = (
        CheckConstraint(
            "rule_type IN ('MAX_DISCOUNT_PCT', 'MIN_MARGIN_PCT', 'MAX_CART_VALUE', "
            "'AUTONOMY_LEVEL', 'SHIPPING_FEE')",
            name="ck_policy_rules_type_valid",
        ),
        CheckConstraint(
            "target_scope IN ('GLOBAL', 'CATEGORY', 'SKU')",
            name="ck_policy_rules_scope_valid",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("merchants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rule_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    target_scope: Mapped[str] = mapped_column(
        String(64),
        default="GLOBAL",
        nullable=False,
    )
    target_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )
    rule_value: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    # Relationships
    merchant: Mapped["Merchant"] = relationship(
        "Merchant",
        back_populates="policy_rules",
    )
