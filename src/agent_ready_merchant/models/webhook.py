"""ProcessedWebhook canonical entity model for atomic deduplication and replay protection."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from agent_ready_merchant.db.base import GUID, Base, TimestampMixin


class ProcessedWebhook(Base, TimestampMixin):
    """Durable record of received Razorpay webhooks for atomic deduplication and replay safety."""

    __tablename__ = "processed_webhooks"

    __table_args__ = (
        UniqueConstraint(
            "payload_hash",
            name="uq_processed_webhooks_payload_hash",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    event_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )
    event_name: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    payload_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    signature_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    rzp_order_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )
    rzp_payment_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="PROCESSING",
        nullable=False,
        index=True,
    )
    response_payload: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
