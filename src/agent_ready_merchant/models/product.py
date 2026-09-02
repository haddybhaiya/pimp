"""Product and ProductVariant canonical entity models."""

import uuid
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agent_ready_merchant.db.base import GUID, Base, OptimisticLockMixin, TimestampMixin

if TYPE_CHECKING:
    from agent_ready_merchant.models.inventory import InventoryItem
    from agent_ready_merchant.models.merchant import Merchant
    from agent_ready_merchant.models.order import OrderItem
    from agent_ready_merchant.models.quote import QuoteItem


class Product(Base, TimestampMixin, OptimisticLockMixin):
    """Catalog product definition structured for AI discovery and deterministic pricing."""

    __tablename__ = "products"

    __table_args__ = (
        UniqueConstraint("merchant_id", "sku", name="uq_products_merchant_sku"),
        CheckConstraint("base_price_paise > 0", name="ck_products_base_price_positive"),
        CheckConstraint("floor_price_paise > 0", name="ck_products_floor_price_positive"),
        CheckConstraint(
            "floor_price_paise <= base_price_paise",
            name="ck_products_floor_lte_base_price",
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
    sku: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    base_price_paise: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    floor_price_paise: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    is_negotiable: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_demo_sandbox_product: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    attributes: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    # Relationships
    merchant: Mapped["Merchant"] = relationship(
        "Merchant",
        back_populates="products",
    )
    variants: Mapped[list["ProductVariant"]] = relationship(
        "ProductVariant",
        back_populates="product",
        cascade="all, delete-orphan",
    )


class ProductVariant(Base, TimestampMixin, OptimisticLockMixin):
    """Specific purchasable variant (e.g. Size, Color) of a product."""

    __tablename__ = "product_variants"

    __table_args__ = (
        UniqueConstraint("product_id", "sku", name="uq_product_variants_product_sku"),
        CheckConstraint(
            "price_override_paise IS NULL OR price_override_paise > 0",
            name="ck_product_variants_price_override_positive",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sku: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    price_override_paise: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )
    attributes: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Relationships
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="variants",
    )
    inventory_item: Mapped[Optional["InventoryItem"]] = relationship(
        "InventoryItem",
        back_populates="variant",
        uselist=False,
        cascade="all, delete-orphan",
    )
    quote_items: Mapped[list["QuoteItem"]] = relationship(
        "QuoteItem",
        back_populates="variant",
    )
    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="variant",
    )
