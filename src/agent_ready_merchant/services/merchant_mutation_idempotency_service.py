"""Durable idempotency gate for direct merchant control-plane mutations."""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.gateway.hardening import compute_payload_hash
from agent_ready_merchant.models.merchant_mutation_receipt import MerchantMutationReceipt


class IdempotencyConflictError(ValueError):
    """Raised when a duplicate key cannot safely be replayed."""


class MerchantMutationIdempotencyService:
    """Claims and replays response bodies without repeating a mutation."""

    @classmethod
    async def claim_or_replay(
        cls,
        session: AsyncSession,
        *,
        merchant_id: uuid.UUID,
        operation: str,
        idempotency_key: str,
        payload: dict[str, Any],
    ) -> tuple[MerchantMutationReceipt | None, dict[str, Any] | None]:
        """Atomically claim a request or return its previously completed response.

        A payload mismatch is rejected so a client cannot reuse an idempotency key
        for a different financial mutation. A concurrent duplicate is rejected
        while the original request remains in progress.
        """
        payload_hash = compute_payload_hash(payload)
        receipt = MerchantMutationReceipt(
            merchant_id=merchant_id,
            operation=operation,
            idempotency_key=idempotency_key,
            payload_hash=payload_hash,
        )
        try:
            async with session.begin_nested():
                session.add(receipt)
                await session.flush()
        except IntegrityError:
            existing = (
                await session.execute(
                    select(MerchantMutationReceipt).where(
                        MerchantMutationReceipt.merchant_id == merchant_id,
                        MerchantMutationReceipt.operation == operation,
                        MerchantMutationReceipt.idempotency_key == idempotency_key,
                    )
                )
            ).scalar_one_or_none()
            if existing is None:
                raise IdempotencyConflictError(
                    "A matching request is still being processed."
                ) from None
            if existing.payload_hash != payload_hash:
                raise IdempotencyConflictError(
                    "Idempotency key was already used with a different payload."
                ) from None
            if existing.response_body is None:
                raise IdempotencyConflictError(
                    "A matching request is still being processed."
                ) from None
            return None, existing.response_body
        return receipt, None

    @classmethod
    async def complete(
        cls,
        session: AsyncSession,
        receipt: MerchantMutationReceipt,
        response_body: dict[str, Any],
        *,
        response_status: int = 200,
    ) -> None:
        """Persist a replay-safe response in the mutation's transaction."""
        receipt.response_body = response_body
        receipt.response_status = response_status
        await session.flush()
