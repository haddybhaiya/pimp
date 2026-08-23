"""TransactionRecord canonical entity model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agent_ready_merchant.db.base import GUID, Base, OptimisticLockMixin, utc_now

if TYPE_CHECKING:
    from agent_ready_merchant.models.merchant import Merchant
    from agent_ready_merchant.models.payment import PaymentAttempt


class TransactionRecord(Base, OptimisticLockMixin):
    """Append-only immutable financial ledger entry with optimistic concurrency."""

    __tablename__ = "transaction_records"

    __table_args__ = (
        CheckConstraint(
            "entry_type IN ('CREDIT', 'DEBIT_REFUND')",
            name="ck_transaction_records_entry_type_valid",
        ),
        CheckConstraint("amount_paise > 0", name="ck_transaction_records_amount_positive"),
        CheckConstraint(
            "status IN ('UNCOMMITTED', 'COMMITTED', 'REVERSED')",
            name="ck_transaction_records_status_valid",
        ),
        UniqueConstraint(
            "payment_attempt_id",
            "entry_type",
            name="uq_transaction_records_attempt_entry",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    payment_attempt_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("payment_attempts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("merchants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    entry_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )
    amount_paise: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="COMMITTED",
        nullable=False,
        index=True,
    )
    settlement_ref: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    # Relationships
    payment_attempt: Mapped["PaymentAttempt"] = relationship(
        "PaymentAttempt",
        back_populates="transaction_records",
    )
    merchant: Mapped["Merchant"] = relationship(
        "Merchant",
        back_populates="transaction_records",
    )
