"""PaymentAttempt canonical entity model."""

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, BigInteger, CheckConstraint, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agent_ready_merchant.db.base import GUID, Base, OptimisticLockMixin, TimestampMixin

if TYPE_CHECKING:
    from agent_ready_merchant.models.order import Order
    from agent_ready_merchant.models.transaction import TransactionRecord


class PaymentAttempt(Base, TimestampMixin, OptimisticLockMixin):
    """Lifecycle record for an individual payment attempt with optimistic concurrency."""

    __tablename__ = "payment_attempts"

    __table_args__ = (
        CheckConstraint(
            "status IN ('INITIATED', 'ORDER_CREATED', 'PAYMENT_PENDING', 'AUTHORIZED', "
            "'CAPTURED', 'FAILED', 'REFUNDED', 'TIMED_OUT')",
            name="ck_payment_attempts_status_valid",
        ),
        CheckConstraint("amount_paise > 0", name="ck_payment_attempts_amount_positive"),
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
    rzp_payment_id: Mapped[str | None] = mapped_column(
        String(64),
        unique=True,
        nullable=True,
        index=True,
    )
    rzp_order_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="INITIATED",
        nullable=False,
        index=True,
    )
    amount_paise: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    payment_method: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )
    error_code: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    error_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    webhook_payload: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # Relationships
    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="payment_attempts",
    )
    transaction_records: Mapped[list["TransactionRecord"]] = relationship(
        "TransactionRecord",
        back_populates="payment_attempt",
    )
