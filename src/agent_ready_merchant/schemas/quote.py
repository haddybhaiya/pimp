"""PriceQuote domain validation schemas."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class QuoteItemCreate(BaseModel):
    """Schema for quote line item creation."""

    variant_id: uuid.UUID
    quantity: int = Field(..., gt=0)
    unit_price_paise: int = Field(..., gt=0)


class QuoteItemRead(QuoteItemCreate):
    """Schema for reading quote line item."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    quote_id: uuid.UUID
    total_price_paise: int


class PriceQuoteBase(BaseModel):
    """Base schema for PriceQuote."""

    status: Literal[
        "DRAFT", "PROPOSED", "NEGOTIATING", "ACCEPTED", "EXPIRED", "SUPERSEDED", "REJECTED"
    ] = "PROPOSED"
    subtotal_paise: int = Field(..., ge=0)
    discount_paise: int = Field(default=0, ge=0)
    shipping_paise: int = Field(default=0, ge=0)
    total_paise: int = Field(..., ge=0)
    discount_reason: str | None = None
    expires_at: datetime
    idempotency_key: str = Field(..., min_length=1, max_length=128)

    @model_validator(mode="after")
    def validate_total_arithmetic(self) -> "PriceQuoteBase":
        """Validates that total_paise equals subtotal - discount + shipping."""
        expected_total = self.subtotal_paise - self.discount_paise + self.shipping_paise
        if self.total_paise != expected_total:
            raise ValueError(
                f"total_paise ({self.total_paise}) does not match "
                f"subtotal ({self.subtotal_paise}) - discount ({self.discount_paise}) + "
                f"shipping ({self.shipping_paise}) = {expected_total}"
            )
        return self


class PriceQuoteCreate(PriceQuoteBase):
    """Schema for creating a PriceQuote."""

    session_id: uuid.UUID
    merchant_id: uuid.UUID
    items: list[QuoteItemCreate] = Field(..., min_length=1)


class PriceQuoteRead(PriceQuoteBase):
    """Schema for reading a PriceQuote."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    session_id: uuid.UUID
    merchant_id: uuid.UUID
    created_at: datetime
    version: int
    items: list[QuoteItemRead] = Field(default_factory=list)
