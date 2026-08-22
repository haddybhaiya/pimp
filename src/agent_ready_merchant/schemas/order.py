"""Order domain validation schemas."""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OrderItemCreate(BaseModel):
    """Schema for creating an order item."""

    variant_id: uuid.UUID
    quantity: int = Field(..., gt=0)
    unit_price_paise: int = Field(..., gt=0)


class OrderItemRead(OrderItemCreate):
    """Schema for reading an order item."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_id: uuid.UUID
    total_price_paise: int


class OrderBase(BaseModel):
    """Base fields for Order."""

    status: Literal[
        "CREATED",
        "PENDING_PAYMENT",
        "PAYMENT_PROCESSING",
        "PAID",
        "PAYMENT_FAILED",
        "FULFILLMENT_PENDING",
        "COMPLETED",
        "CANCELLED",
        "EXPIRED",
        "REFUNDED",
    ] = "CREATED"
    amount_paise: int = Field(..., gt=0)
    currency: Literal["INR"] = "INR"
    buyer_email: EmailStr
    shipping_address: dict[str, Any] = Field(default_factory=dict)
    rzp_order_id: str | None = None


class OrderCreate(OrderBase):
    """Schema for creating an Order from an accepted quote."""

    quote_id: uuid.UUID
    merchant_id: uuid.UUID
    items: list[OrderItemCreate] = Field(..., min_length=1)


class OrderRead(OrderBase):
    """Schema for reading an Order."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    quote_id: uuid.UUID
    merchant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    version: int
    items: list[OrderItemRead] = Field(default_factory=list)
