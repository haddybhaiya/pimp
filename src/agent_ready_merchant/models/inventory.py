"""InventoryItem canonical entity model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agent_ready_merchant.db.base import GUID, Base, OptimisticLockMixin, utc_now

if TYPE_CHECKING:
    from agent_ready_merchant.models.product import ProductVariant


class InventoryItem(Base, OptimisticLockMixin):
    """Authoritative stock tracking with optimistic concurrency and reservation support."""

    __tablename__ = "inventory_items"

    __table_args__ = (
        CheckConstraint("available_quantity >= 0", name="ck_inventory_available_non_negative"),
        CheckConstraint("reserved_quantity >= 0", name="ck_inventory_reserved_non_negative"),
        CheckConstraint("safety_threshold >= 0", name="ck_inventory_safety_threshold_non_negative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    variant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("product_variants.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    available_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    reserved_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    safety_threshold: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    # Relationships
    variant: Mapped["ProductVariant"] = relationship(
        "ProductVariant",
        back_populates="inventory_item",
    )
