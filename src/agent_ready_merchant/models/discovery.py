"""Discovery Network database models for Agent-Ready Merchant.

Adheres strictly to Phase 9 specifications:
- Stores merchant-controlled discoverability state (PRIVATE, DISCOVERABLE, PAUSED, SUSPENDED)
- Safe public discovery metadata with deterministic SHA-256 hash
- Tenant-scoped discovery telemetry (SEARCH_RECEIVED, MERCHANT_RETURNED, etc.)
  with replay protection
"""

from __future__ import annotations

import enum
import hashlib
import json
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from agent_ready_merchant.db.base import GUID, Base, TimestampMixin

if TYPE_CHECKING:
    from agent_ready_merchant.models.merchant import Merchant


class DiscoverabilityState(enum.StrEnum):
    """Discoverability status of a merchant."""

    PRIVATE = "PRIVATE"
    DISCOVERABLE = "DISCOVERABLE"
    PAUSED = "PAUSED"
    SUSPENDED = "SUSPENDED"


class DiscoveryTelemetryEventType(enum.StrEnum):
    """Telemetry event types for discovery tracking."""

    SEARCH_RECEIVED = "SEARCH_RECEIVED"
    MERCHANT_RETURNED = "MERCHANT_RETURNED"
    MERCHANT_SELECTED = "MERCHANT_SELECTED"
    PRODUCT_SELECTED = "PRODUCT_SELECTED"
    HANDOFF_INITIATED = "HANDOFF_INITIATED"


def compute_discovery_metadata_hash(data: dict[str, Any]) -> str:
    """Computes a deterministic SHA-256 hash for discovery profile metadata."""
    canonical_json = json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


class MerchantDiscoveryProfile(Base, TimestampMixin):
    """Durable record of a merchant's public discoverability settings and safe metadata."""

    __tablename__ = "merchant_discovery_profiles"

    __table_args__ = (
        CheckConstraint(
            "discoverability_state IN ('PRIVATE', 'DISCOVERABLE', 'PAUSED', 'SUSPENDED')",
            name="ck_discovery_profiles_state_valid",
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
        unique=True,
        nullable=False,
        index=True,
    )
    discoverability_state: Mapped[str] = mapped_column(
        String(32),
        default=DiscoverabilityState.PRIVATE.value,
        nullable=False,
        index=True,
    )
    custom_tags: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )
    custom_description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    delivery_regions: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        nullable=False,
    )
    profile_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    metadata_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    last_refreshed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    merchant: Mapped[Merchant] = relationship(
        "Merchant",
        back_populates="discovery_profile",
    )


class MerchantDiscoveryTelemetry(Base):
    """Tenant-scoped discovery telemetry event with replay protection."""

    __tablename__ = "merchant_discovery_telemetry"

    __table_args__ = (
        CheckConstraint(
            "event_type IN ("
            "'SEARCH_RECEIVED', "
            "'MERCHANT_RETURNED', "
            "'MERCHANT_SELECTED', "
            "'PRODUCT_SELECTED', "
            "'HANDOFF_INITIATED'"
            ")",
            name="ck_discovery_telemetry_event_type_valid",
        ),
        UniqueConstraint(
            "merchant_id",
            "event_type",
            "correlation_id",
            name="uq_discovery_telemetry_replay",
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
    event_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    correlation_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    sanitized_query: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
