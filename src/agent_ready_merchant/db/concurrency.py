"""Optimistic concurrency primitives and exception definitions.

Adheres to ADR-005 (Optimistic Concurrency Control) and INV-STA-02.
"""

from typing import Any, TypeVar

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.db.base import Base

T = TypeVar("T", bound=Base)


class OptimisticLockError(Exception):
    """Raised when an update fails because the entity version is stale."""

    def __init__(self, entity_name: str, entity_id: Any, expected_version: int) -> None:
        self.entity_name = entity_name
        self.entity_id = entity_id
        self.expected_version = expected_version
        super().__init__(
            f"Optimistic lock conflict on {entity_name}(id={entity_id}): "
            f"expected version {expected_version}, but entity was modified concurrently."
        )


async def update_with_version_check(
    session: AsyncSession,
    model_class: type[T],
    entity_id: Any,
    expected_version: int,
    values: dict[str, Any],
) -> int:
    """Executes a version-checked atomic UPDATE query.

    Increments the version by 1 and applies the given values only if the current
    database version matches expected_version.

    Raises:
        OptimisticLockError: If no row was matched/updated (version mismatch or deleted).

    Returns:
        The new version integer (expected_version + 1).
    """
    new_version = expected_version + 1
    update_payload = {**values, "version": new_version}

    stmt = (
        update(model_class)
        .where(
            model_class.id == entity_id,  # type: ignore[attr-defined]
            model_class.version == expected_version,  # type: ignore[attr-defined]
        )
        .values(**update_payload)
    )

    result = await session.execute(stmt)
    rowcount = getattr(result, "rowcount", 0)
    if rowcount == 0:
        raise OptimisticLockError(
            entity_name=model_class.__name__,
            entity_id=entity_id,
            expected_version=expected_version,
        )

    return new_version
