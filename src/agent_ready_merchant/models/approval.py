"""MerchantApproval canonical entity model for Human-In-The-Loop (HITL) gates."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agent_ready_merchant.db.base import GUID, Base, OptimisticLockMixin, TimestampMixin

if TYPE_CHECKING:
    from agent_ready_merchant.models.merchant import Merchant
    from agent_ready_merchant.models.order import Order
    from agent_ready_merchant.models.quote import PriceQuote
    from agent_ready_merchant.models.session import BuyerAgentSession


class MerchantApproval(Base, TimestampMixin, OptimisticLockMixin):
    """Authoritative record of a merchant human-in-the-loop approval ticket."""

    __tablename__ = "merchant_approvals"

    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'APPROVED', 'REJECTED', 'EXPIRED')",
            name="ck_merchant_approvals_status_valid",
        ),
        CheckConstraint(
            "approval_type IN ('QUOTE_DISCOUNT', 'ORDER_LIMIT', 'GENERAL')",
            name="ck_merchant_approvals_type_valid",
        ),
        CheckConstraint(
            "requested_amount_paise >= 0",
            name="ck_merchant_approvals_requested_amount_non_negative",
        ),
        CheckConstraint(
            "proposed_discount_paise >= 0",
            name="ck_merchant_approvals_proposed_discount_non_negative",
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
    quote_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("price_quotes.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    order_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("orders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("buyer_agent_sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    approval_type: Mapped[str] = mapped_column(
        String(64),
        default="QUOTE_DISCOUNT",
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="PENDING",
        nullable=False,
        index=True,
    )
    requested_amount_paise: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=False,
    )
    proposed_discount_paise: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=False,
    )
    policy_decision_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    policy_rule_code: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    approver_identifier: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    merchant: Mapped["Merchant"] = relationship(
        "Merchant",
    )
    quote: Mapped[Optional["PriceQuote"]] = relationship(
        "PriceQuote",
    )
    order: Mapped[Optional["Order"]] = relationship(
        "Order",
    )
    session: Mapped[Optional["BuyerAgentSession"]] = relationship(
        "BuyerAgentSession",
    )
