"""Merchant canonical entity model."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agent_ready_merchant.db.base import GUID, Base, OptimisticLockMixin, TimestampMixin

if TYPE_CHECKING:
    from agent_ready_merchant.models.audit import AuditEvent
    from agent_ready_merchant.models.order import Order
    from agent_ready_merchant.models.policy import PolicyRule
    from agent_ready_merchant.models.product import Product
    from agent_ready_merchant.models.quote import PriceQuote
    from agent_ready_merchant.models.session import BuyerAgentSession
    from agent_ready_merchant.models.transaction import TransactionRecord


class Merchant(Base, TimestampMixin, OptimisticLockMixin):
    """Authoritative record of a merchant in the Agent-Ready Merchant platform."""

    __tablename__ = "merchants"

    __table_args__ = (
        CheckConstraint(
            "status IN ('ACTIVE', 'PAUSED', 'SUSPENDED')",
            name="ck_merchants_status_valid",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="ACTIVE",
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="INR",
        nullable=False,
    )
    rzp_key_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    auth_user_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        unique=True,
        nullable=True,
        index=True,
    )

    # Relationships
    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="merchant",
        cascade="all, delete-orphan",
    )
    policy_rules: Mapped[list["PolicyRule"]] = relationship(
        "PolicyRule",
        back_populates="merchant",
        cascade="all, delete-orphan",
    )
    sessions: Mapped[list["BuyerAgentSession"]] = relationship(
        "BuyerAgentSession",
        back_populates="merchant",
        cascade="all, delete-orphan",
    )
    quotes: Mapped[list["PriceQuote"]] = relationship(
        "PriceQuote",
        back_populates="merchant",
        cascade="all, delete-orphan",
    )
    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="merchant",
        cascade="all, delete-orphan",
    )
    transaction_records: Mapped[list["TransactionRecord"]] = relationship(
        "TransactionRecord",
        back_populates="merchant",
    )
    audit_events: Mapped[list["AuditEvent"]] = relationship(
        "AuditEvent",
        back_populates="merchant",
    )
