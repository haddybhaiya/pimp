"""PriceQuote and QuoteItem canonical entity models."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agent_ready_merchant.db.base import GUID, Base, OptimisticLockMixin, utc_now

if TYPE_CHECKING:
    from agent_ready_merchant.models.merchant import Merchant
    from agent_ready_merchant.models.order import Order
    from agent_ready_merchant.models.product import ProductVariant
    from agent_ready_merchant.models.session import BuyerAgentSession


class PriceQuote(Base, OptimisticLockMixin):
    """Binding, time-limited commercial offer issued by the deterministic policy engine."""

    __tablename__ = "price_quotes"

    __table_args__ = (
        CheckConstraint(
            "status IN ('DRAFT', 'PROPOSED', 'NEGOTIATING', 'ACCEPTED', 'EXPIRED', "
            "'SUPERSEDED', 'REJECTED')",
            name="ck_price_quotes_status_valid",
        ),
        CheckConstraint("subtotal_paise >= 0", name="ck_price_quotes_subtotal_non_negative"),
        CheckConstraint("discount_paise >= 0", name="ck_price_quotes_discount_non_negative"),
        CheckConstraint("shipping_paise >= 0", name="ck_price_quotes_shipping_non_negative"),
        CheckConstraint("total_paise >= 0", name="ck_price_quotes_total_non_negative"),
        CheckConstraint(
            "total_paise = subtotal_paise - discount_paise + shipping_paise",
            name="ck_price_quotes_total_arithmetic",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("buyer_agent_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("merchants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="PROPOSED",
        nullable=False,
        index=True,
    )
    subtotal_paise: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    discount_paise: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=False,
    )
    shipping_paise: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=False,
    )
    total_paise: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    discount_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    # Relationships
    session: Mapped["BuyerAgentSession"] = relationship(
        "BuyerAgentSession",
        back_populates="quotes",
    )
    merchant: Mapped["Merchant"] = relationship(
        "Merchant",
        back_populates="quotes",
    )
    items: Mapped[list["QuoteItem"]] = relationship(
        "QuoteItem",
        back_populates="quote",
        cascade="all, delete-orphan",
    )
    order: Mapped[Optional["Order"]] = relationship(
        "Order",
        back_populates="quote",
        uselist=False,
    )


class QuoteItem(Base):
    """Line item in a PriceQuote."""

    __tablename__ = "quote_items"

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_quote_items_quantity_positive"),
        CheckConstraint("unit_price_paise > 0", name="ck_quote_items_unit_price_positive"),
        CheckConstraint(
            "total_price_paise = unit_price_paise * quantity",
            name="ck_quote_items_total_arithmetic",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    quote_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("price_quotes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    variant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("product_variants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    unit_price_paise: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    total_price_paise: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    # Relationships
    quote: Mapped["PriceQuote"] = relationship(
        "PriceQuote",
        back_populates="items",
    )
    variant: Mapped["ProductVariant"] = relationship(
        "ProductVariant",
        back_populates="quote_items",
    )
