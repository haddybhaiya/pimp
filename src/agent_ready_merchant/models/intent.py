"""BuyerIntent canonical entity model."""

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, CheckConstraint, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agent_ready_merchant.db.base import GUID, Base, OptimisticLockMixin, TimestampMixin

if TYPE_CHECKING:
    from agent_ready_merchant.models.session import BuyerAgentSession


class BuyerIntent(Base, TimestampMixin, OptimisticLockMixin):
    """Model-interpreted intent parsed from buyer interaction."""

    __tablename__ = "buyer_intents"

    __table_args__ = (
        CheckConstraint(
            "validation_status IN ('PENDING', 'VALIDATED', 'REJECTED', 'MALFORMED')",
            name="ck_buyer_intents_validation_status_valid",
        ),
        CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_buyer_intents_confidence_score_range",
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
    raw_query: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    extracted_intent: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    extracted_entities: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    confidence_score: Mapped[Decimal] = mapped_column(
        Numeric(4, 3),
        default=Decimal("1.000"),
        nullable=False,
    )
    validation_status: Mapped[str] = mapped_column(
        String(32),
        default="VALIDATED",
        nullable=False,
    )

    # Relationships
    session: Mapped["BuyerAgentSession"] = relationship(
        "BuyerAgentSession",
        back_populates="intents",
    )
