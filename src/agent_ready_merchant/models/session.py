"""BuyerAgentSession canonical entity model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agent_ready_merchant.db.base import GUID, Base, utc_now

if TYPE_CHECKING:
    from agent_ready_merchant.models.agent_run import AgentRun
    from agent_ready_merchant.models.audit import AuditEvent
    from agent_ready_merchant.models.intent import BuyerIntent
    from agent_ready_merchant.models.merchant import Merchant
    from agent_ready_merchant.models.quote import PriceQuote


class BuyerAgentSession(Base):
    """Session boundary and security context for autonomous buyer interactions."""

    __tablename__ = "buyer_agent_sessions"

    __table_args__ = (
        CheckConstraint(
            "status IN ('ACTIVE', 'EXPIRED', 'TERMINATED')",
            name="ck_buyer_sessions_status_valid",
        ),
        CheckConstraint(
            "total_tool_calls >= 0",
            name="ck_buyer_sessions_tool_calls_non_negative",
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
    buyer_agent_identifier: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    auth_token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="ACTIVE",
        nullable=False,
    )
    total_tool_calls: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    # Relationships
    merchant: Mapped["Merchant"] = relationship(
        "Merchant",
        back_populates="sessions",
    )
    intents: Mapped[list["BuyerIntent"]] = relationship(
        "BuyerIntent",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    quotes: Mapped[list["PriceQuote"]] = relationship(
        "PriceQuote",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    agent_runs: Mapped[list["AgentRun"]] = relationship(
        "AgentRun",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    audit_events: Mapped[list["AuditEvent"]] = relationship(
        "AuditEvent",
        back_populates="session",
    )
