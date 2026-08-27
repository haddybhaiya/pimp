"""AuditEvent canonical entity model."""

import hashlib
import json
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import JSON, CheckConstraint, DateTime, ForeignKey, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agent_ready_merchant.db.base import GUID, Base, utc_now

if TYPE_CHECKING:
    from agent_ready_merchant.models.merchant import Merchant
    from agent_ready_merchant.models.session import BuyerAgentSession


class AuditEvent(Base):
    """Cryptographically tamper-evident, append-only audit event log."""

    __tablename__ = "audit_events"

    GENESIS_HASH: str = "0" * 64

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
        ForeignKey("merchants.id", ondelete="RESTRICT"),
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

    @classmethod
    def compute_digest(
        cls,
        prev_hash: str,
        merchant_id: uuid.UUID,
        session_id: uuid.UUID | None,
        actor_type: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> str:
        """Deterministically computes SHA-256 event digest."""
        payload_json = json.dumps(payload, sort_keys=True, default=str)
        raw = (
            f"{prev_hash}:{merchant_id}:{session_id or ''}:{actor_type}:{event_type}:{payload_json}"
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @classmethod
    async def create_event(
        cls,
        session: AsyncSession,
        merchant_id: uuid.UUID,
        actor_type: str,
        event_type: str,
        payload: dict[str, Any],
        session_id: uuid.UUID | None = None,
    ) -> "AuditEvent":
        """Appends a new audit event with deterministic cryptographic hash chaining."""
        # In PostgreSQL, serialize audit event appends per merchant to guarantee
        # linear chain integrity
        bind = session.get_bind()
        if bind is not None and getattr(bind.dialect, "name", "") == "postgresql":
            from agent_ready_merchant.models.merchant import Merchant

            m_stmt = select(Merchant.id).where(Merchant.id == merchant_id).with_for_update()
            await session.execute(m_stmt)

        stmt = (
            select(cls.event_hash)
            .where(cls.merchant_id == merchant_id)
            .order_by(cls.created_at.desc(), cls.id.desc())
            .limit(1)
        )
        prev_hash = (await session.execute(stmt)).scalar_one_or_none() or cls.GENESIS_HASH

        digest = cls.compute_digest(
            prev_hash=prev_hash,
            merchant_id=merchant_id,
            session_id=session_id,
            actor_type=actor_type,
            event_type=event_type,
            payload=payload,
        )

        event = cls(
            merchant_id=merchant_id,
            session_id=session_id,
            actor_type=actor_type,
            event_type=event_type,
            payload=payload,
            prev_event_hash=prev_hash,
            event_hash=digest,
        )
        session.add(event)
        await session.flush()
        return event

    @classmethod
    async def verify_chain(
        cls,
        session: AsyncSession,
        merchant_id: uuid.UUID,
    ) -> tuple[bool, str | None]:
        """Validates cryptographic hash chain integrity for a merchant's audit log."""
        stmt = (
            select(cls)
            .where(cls.merchant_id == merchant_id)
            .order_by(cls.created_at.asc(), cls.id.asc())
        )
        events = (await session.execute(stmt)).scalars().all()
        expected_prev = cls.GENESIS_HASH
        for idx, event in enumerate(events):
            if event.prev_event_hash != expected_prev:
                return (
                    False,
                    f"Broken chain at index {idx}: expected {expected_prev}, "
                    f"got {event.prev_event_hash}",
                )
            expected_digest = cls.compute_digest(
                prev_hash=event.prev_event_hash or cls.GENESIS_HASH,
                merchant_id=event.merchant_id,
                session_id=event.session_id,
                actor_type=event.actor_type,
                event_type=event.event_type,
                payload=event.payload,
            )
            if event.event_hash != expected_digest:
                return (
                    False,
                    f"Digest mismatch at index {idx}: expected {expected_digest}, "
                    f"got {event.event_hash}",
                )
            expected_prev = event.event_hash
        return True, None
