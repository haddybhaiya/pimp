"""Merchant domain validation schemas."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MerchantBase(BaseModel):
    """Base fields for merchant entity."""

    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    status: Literal["ACTIVE", "PAUSED", "SUSPENDED"] = "ACTIVE"
    currency: Literal["INR"] = "INR"
    rzp_key_id: str = Field(..., min_length=1, max_length=128)


class MerchantCreate(MerchantBase):
    """Schema for creating a new merchant."""

    pass


class MerchantRead(MerchantBase):
    """Schema for reading a merchant entity."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    version: int
