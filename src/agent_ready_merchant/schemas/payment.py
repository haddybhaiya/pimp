"""PaymentAttempt and TransactionRecord domain schemas."""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class PaymentAttemptBase(BaseModel):
    """Base fields for PaymentAttempt."""

    rzp_order_id: str = Field(..., min_length=1, max_length=64)
    rzp_payment_id: str | None = Field(None, max_length=64)
    status: Literal[
        "INITIATED",
        "ORDER_CREATED",
        "PAYMENT_PENDING",
        "AUTHORIZED",
        "CAPTURED",
        "FAILED",
        "REFUNDED",
        "TIMED_OUT",
    ] = "INITIATED"
    amount_paise: int = Field(..., gt=0)
    payment_method: str | None = None
    error_code: str | None = None
    error_description: str | None = None
    webhook_payload: dict[str, Any] | None = None


class PaymentAttemptCreate(PaymentAttemptBase):
    """Schema for recording a new payment attempt."""

    order_id: uuid.UUID


class PaymentAttemptRead(PaymentAttemptBase):
    """Schema for reading a payment attempt."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TransactionRecordBase(BaseModel):
    """Base schema for immutable financial transaction ledger."""

    entry_type: Literal["CREDIT", "DEBIT_REFUND"]
    amount_paise: int = Field(..., gt=0)
    status: Literal["UNCOMMITTED", "COMMITTED", "REVERSED"] = "COMMITTED"
    settlement_ref: str | None = None


class TransactionRecordCreate(TransactionRecordBase):
    """Schema for creating a transaction record."""

    payment_attempt_id: uuid.UUID
    merchant_id: uuid.UUID


class TransactionRecordRead(TransactionRecordBase):
    """Schema for reading a transaction record."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    payment_attempt_id: uuid.UUID
    merchant_id: uuid.UUID
    created_at: datetime
