"""Durable replay receipts for merchant control-plane mutations."""

import uuid
from typing import Any

from sqlalchemy import JSON, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from agent_ready_merchant.db.base import GUID, Base, TimestampMixin


class MerchantMutationReceipt(Base, TimestampMixin):
    """Stores one completed response per merchant operation/idempotency key."""

    __tablename__ = "merchant_mutation_receipts"

    __table_args__ = (
        UniqueConstraint(
            "merchant_id",
            "operation",
            "idempotency_key",
            name="uq_merchant_mutation_receipts_operation_key",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("merchants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    operation: Mapped[str] = mapped_column(String(128), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    response_body: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    response_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
