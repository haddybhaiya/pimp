"""Product and ProductVariant domain validation schemas."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProductVariantBase(BaseModel):
    """Base fields for ProductVariant."""

    sku: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=255)
    price_override_paise: int | None = Field(None, gt=0)
    attributes: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class ProductVariantCreate(ProductVariantBase):
    """Schema for creating a product variant."""

    pass


class ProductVariantRead(ProductVariantBase):
    """Schema for reading a product variant."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    version: int


class ProductBase(BaseModel):
    """Base fields for Product."""

    sku: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(default="")
    category: str = Field(..., min_length=1, max_length=100)
    base_price_paise: int = Field(..., gt=0, description="Base list price in integer paise")
    floor_price_paise: int = Field(..., gt=0, description="Absolute floor price in integer paise")
    is_negotiable: bool = False
    is_active: bool = True
    attributes: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_floor_lte_base(self) -> "ProductBase":
        """Ensures floor price does not exceed base price."""
        if self.floor_price_paise > self.base_price_paise:
            raise ValueError(
                f"floor_price_paise ({self.floor_price_paise}) cannot exceed "
                f"base_price_paise ({self.base_price_paise})"
            )
        return self


class ProductCreate(ProductBase):
    """Schema for creating a product with variants."""

    merchant_id: uuid.UUID
    variants: list[ProductVariantCreate] = Field(default_factory=list)


class ProductRead(ProductBase):
    """Schema for reading a product."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    merchant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    version: int
    variants: list[ProductVariantRead] = Field(default_factory=list)
