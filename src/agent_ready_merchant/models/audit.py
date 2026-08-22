"""AuditEvent canonical entity model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import JSON, CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agent_ready_merchant.db.base import GUID, Base, utc_now

if TYPE_CHECKING:
    from agent_ready_merchant.models.merchant import Merchant
    from agent_ready_merchant.models.session import BuyerAgentSession


class AuditEvent(Base):
    """Cryptographically tamper-evident, append-only audit event log."""

    __tablename__ = "audit_events"

    __table_args__ = (
        CheckConstraint(
            "actor_type IN ('BUYER_AGENT', 'LLM_MODEL', 'MERCHANT_ADMIN', 'SYSTEM')",
            name="ck_audit_events_actor_type_valid",
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
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("buyer_agent_sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    actor_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    prev_event_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    event_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    # Relationships
    merchant: Mapped["Merchant"] = relationship(
        "Merchant",
        back_populates="audit_events",
    )
    session: Mapped[Optional["BuyerAgentSession"]] = relationship(
        "BuyerAgentSession",
        back_populates="audit_events",
    )
