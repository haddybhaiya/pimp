"""Order and OrderItem canonical entity models."""

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, BigInteger, CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agent_ready_merchant.db.base import GUID, Base, OptimisticLockMixin, TimestampMixin

if TYPE_CHECKING:
    from agent_ready_merchant.models.merchant import Merchant
    from agent_ready_merchant.models.payment import PaymentAttempt
    from agent_ready_merchant.models.product import ProductVariant
    from agent_ready_merchant.models.quote import PriceQuote


class Order(Base, TimestampMixin, OptimisticLockMixin):
    """Authoritative order record committed to the merchant ledger."""

    __tablename__ = "orders"

    __table_args__ = (
        CheckConstraint(
            "status IN ('CREATED', 'PENDING_PAYMENT', 'PAYMENT_PROCESSING', 'PAID', "
            "'PAYMENT_FAILED', 'FULFILLMENT_PENDING', 'COMPLETED', 'CANCELLED', "
            "'EXPIRED', 'REFUNDED')",
            name="ck_orders_status_valid",
        ),
        CheckConstraint("amount_paise > 0", name="ck_orders_amount_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    quote_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("price_quotes.id", ondelete="RESTRICT"),
        unique=True,
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
        default="CREATED",
        nullable=False,
        index=True,
    )
    amount_paise: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="INR",
        nullable=False,
    )
    buyer_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    shipping_address: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    rzp_order_id: Mapped[str | None] = mapped_column(
        String(64),
        unique=True,
        nullable=True,
        index=True,
    )

    # Relationships
    merchant: Mapped["Merchant"] = relationship(
        "Merchant",
        back_populates="orders",
    )
    quote: Mapped["PriceQuote"] = relationship(
        "PriceQuote",
        back_populates="order",
    )
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )
    payment_attempts: Mapped[list["PaymentAttempt"]] = relationship(
        "PaymentAttempt",
        back_populates="order",
        cascade="all, delete-orphan",
    )


class OrderItem(Base):
    """Line item in a committed Order."""

    __tablename__ = "order_items"

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_items_quantity_positive"),
        CheckConstraint("unit_price_paise > 0", name="ck_order_items_unit_price_positive"),
        CheckConstraint(
            "total_price_paise = unit_price_paise * quantity",
            name="ck_order_items_total_arithmetic",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("orders.id", ondelete="CASCADE"),
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
    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="items",
    )
    variant: Mapped["ProductVariant"] = relationship(
        "ProductVariant",
        back_populates="order_items",
    )
