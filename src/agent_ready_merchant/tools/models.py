"""Typed parameter and result schemas for all registered gateway tools.

Adheres strictly to docs/tool-contract.md §2 and zero-untyped-execution.
"""

import uuid
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class DiscoverCatalogParams(BaseModel):
    """Parameters for discover_catalog tool."""

    model_config = ConfigDict(extra="forbid")

    query: str | None = Field(default=None, max_length=100)
    category: str | None = Field(default=None, max_length=50)
    max_price_paise: int | None = Field(default=None, ge=0)
    limit: int = Field(default=5, ge=1, le=10)


class GetProductDetailsParams(BaseModel):
    """Parameters for get_product_details tool."""

    model_config = ConfigDict(extra="forbid")

    sku: str = Field(..., min_length=1, max_length=100)


class QuoteItemParam(BaseModel):
    """Item specification inside request_price_quote."""

    model_config = ConfigDict(extra="forbid")

    sku: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., ge=1, le=10)


class RequestPriceQuoteParams(BaseModel):
    """Parameters for request_price_quote tool."""

    model_config = ConfigDict(extra="forbid")

    session_id: uuid.UUID = Field(...)
    items: list[QuoteItemParam] = Field(..., min_length=1, max_length=5)


class NegotiateQuoteParams(BaseModel):
    """Parameters for negotiate_quote tool."""

    model_config = ConfigDict(extra="forbid")

    quote_id: uuid.UUID = Field(...)
    proposed_total_paise: int = Field(..., gt=0)
    rationale: str | None = Field(default=None, max_length=255)


class ShippingAddressParam(BaseModel):
    """Shipping address structure for create_order."""

    model_config = ConfigDict(extra="forbid")

    full_name: str = Field(..., min_length=1, max_length=100)
    address_line1: str = Field(..., min_length=1, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    postal_code: str = Field(..., min_length=1, max_length=20)
    country: str = Field(default="IN", max_length=2)


class CreateOrderParams(BaseModel):
    """Parameters for create_order tool."""

    model_config = ConfigDict(extra="forbid")

    quote_id: uuid.UUID = Field(...)
    buyer_email: EmailStr = Field(...)
    shipping_address: ShippingAddressParam = Field(...)


class CheckPaymentStatusParams(BaseModel):
    """Parameters for check_payment_status tool."""

    model_config = ConfigDict(extra="forbid")

    order_id: uuid.UUID = Field(...)


class ToolExecutionResult(BaseModel):
    """Standardized envelope returned by tool execution."""

    status: Literal["SUCCESS", "REJECTED", "ERROR"] = Field(...)
    tool_name: str = Field(...)
    data: dict[str, Any] | None = Field(default=None)
    error: dict[str, Any] | None = Field(default=None)
