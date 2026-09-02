"""AgentRun canonical entity model."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agent_ready_merchant.db.base import GUID, Base, OptimisticLockMixin, TimestampMixin

if TYPE_CHECKING:
    from agent_ready_merchant.models.session import BuyerAgentSession


class AgentRun(Base, TimestampMixin, OptimisticLockMixin):
    """Execution lifecycle record governing untrusted intelligence bounds."""

    __tablename__ = "agent_runs"

    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'RUNNING', 'AWAITING_TOOL', 'EVALUATING_POLICY', "
            "'EXECUTING_ACTION', 'COMPLETED', 'FAILED', 'KILLED')",
            name="ck_agent_runs_status_valid",
        ),
        CheckConstraint(
            "step_count >= 0 AND step_count <= 5",
            name="ck_agent_runs_step_count_bounded",
        ),
        CheckConstraint(
            "total_tokens >= 0",
            name="ck_agent_runs_tokens_non_negative",
        ),
        CheckConstraint(
            "session_id IS NOT NULL OR merchant_id IS NOT NULL",
            name="ck_agent_runs_session_or_merchant_required",
        ),
        UniqueConstraint("id", "merchant_id", name="uq_agent_runs_id_merchant"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("buyer_agent_sessions.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    merchant_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("merchants.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="PENDING",
        nullable=False,
        index=True,
    )
    step_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    total_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    session: Mapped["BuyerAgentSession | None"] = relationship(
        "BuyerAgentSession",
        back_populates="agent_runs",
    )
