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


def sanitize_audit_payload(payload: Any) -> Any:
    """Sanitizes an audit payload by redacting credentials, secrets, and masking PII.

    Preserves structural evidence without compromising security (INV-AGY-03).
    """
    sensitive_keys = {
        "auth_token",
        "auth_token_raw",
        "key_secret",
        "rzp_key_secret",
        "secret",
        "password",
        "raw_token",
        "token_raw",
        "api_key",
        "card_number",
        "cvv",
        "authorization",
        "bearer",
        "jwt",
        "access_token",
        "refresh_token",
        "private_key",
        "signature",
    }
    if isinstance(payload, dict):
        sanitized = {}
        for k, v in payload.items():
            k_lower = str(k).lower()
            if any(s in k_lower for s in sensitive_keys):
                sanitized[k] = "[REDACTED_SECRET]"
            elif k_lower in {"buyer_email", "email"} and isinstance(v, str) and "@" in v:
                parts = v.split("@", 1)
                user, domain = parts[0], parts[1]
                masked_user = f"{user[0]}***{user[-1]}" if len(user) > 2 else f"{user[:1]}***"
                sanitized[k] = f"{masked_user}@{domain}"
            elif isinstance(v, (dict, list)):
                sanitized[k] = sanitize_audit_payload(v)
            else:
                sanitized[k] = v
        return sanitized
    elif isinstance(payload, list):
        return [sanitize_audit_payload(item) for item in payload]
    return payload


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
        # Sanitize payload: strip credentials, secrets, and mask PII (INV-AGY-03)
        sanitized = sanitize_audit_payload(payload)

        # In PostgreSQL, serialize audit event appends per merchant to guarantee
        # linear chain integrity
        bind = session.get_bind()
        if bind is not None and getattr(bind.dialect, "name", "") == "postgresql":
            from agent_ready_merchant.models.merchant import Merchant

            m_stmt = select(Merchant.id).where(Merchant.id == merchant_id).with_for_update()
            await session.execute(m_stmt)

        # Select current leaf hash of the chain: event_hash not referenced as prev_event_hash
        subq = (
            select(cls.prev_event_hash)
            .where(
                cls.merchant_id == merchant_id,
                cls.prev_event_hash.is_not(None),
            )
            .scalar_subquery()
        )
        stmt = (
            select(cls.event_hash)
            .where(
                cls.merchant_id == merchant_id,
                cls.event_hash.not_in(subq),
            )
            .order_by(cls.created_at.desc())
            .limit(1)
        )
        prev_hash = (await session.execute(stmt)).scalar_one_or_none() or cls.GENESIS_HASH

        digest = cls.compute_digest(
            prev_hash=prev_hash,
            merchant_id=merchant_id,
            session_id=session_id,
            actor_type=actor_type,
            event_type=event_type,
            payload=sanitized,
        )

        event = cls(
            merchant_id=merchant_id,
            session_id=session_id,
            actor_type=actor_type,
            event_type=event_type,
            payload=sanitized,
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
        stmt = select(cls).where(cls.merchant_id == merchant_id)
        events = list((await session.execute(stmt)).scalars().all())
        if not events:
            return True, None

        # Build map: prev_event_hash -> list of child events.
        # Reject any event whose prev_event_hash is NULL — root events must store the explicit
        # GENESIS_HASH sentinel. A NULL indicates storage tampering (INV-STA-05).
        prev_map: dict[str, list[AuditEvent]] = {}
        for ev in events:
            if ev.prev_event_hash is None:
                return (
                    False,
                    f"Tampered chain: event {ev.id} has NULL prev_event_hash; "
                    "root events must store explicit GENESIS_HASH sentinel",
                )
            prev_map.setdefault(ev.prev_event_hash, []).append(ev)

        curr_hash = cls.GENESIS_HASH
        verified_count = 0
        while curr_hash in prev_map:
            children = prev_map[curr_hash]
            if len(children) > 1:
                return (
                    False,
                    f"Chain fork detected: multiple events reference parent hash '{curr_hash}'",
                )
            ev = children[0]
            assert ev.prev_event_hash is not None
            expected_digest = cls.compute_digest(
                prev_hash=ev.prev_event_hash,
                merchant_id=ev.merchant_id,
                session_id=ev.session_id,
                actor_type=ev.actor_type,
                event_type=ev.event_type,
                payload=ev.payload,
            )
            if ev.event_hash != expected_digest:
                return (
                    False,
                    f"Digest mismatch at event {ev.id}: expected {expected_digest}, "
                    f"got {ev.event_hash}",
                )
            curr_hash = ev.event_hash
            verified_count += 1

        if verified_count != len(events):
            unlinked = len(events) - verified_count
            return (
                False,
                f"Broken chain: {unlinked} unlinked or orphaned audit events detected",
            )

        return True, None
