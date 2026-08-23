"""Inventory domain validation schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class InventoryItemBase(BaseModel):
    """Base fields for InventoryItem."""

    available_quantity: int = Field(default=0, ge=0)
    reserved_quantity: int = Field(default=0, ge=0)
    safety_threshold: int = Field(default=0, ge=0)


class InventoryItemCreate(InventoryItemBase):
    """Schema for initializing inventory for a variant."""

    variant_id: uuid.UUID


class InventoryItemRead(InventoryItemBase):
    """Schema for reading inventory state."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    variant_id: uuid.UUID
    updated_at: datetime
    version: int
