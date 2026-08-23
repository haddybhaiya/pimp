"""PolicyRule domain validation schemas."""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class PolicyRuleBase(BaseModel):
    """Base fields for PolicyRule."""

    rule_type: Literal[
        "MAX_DISCOUNT_PCT", "MIN_MARGIN_PCT", "MAX_CART_VALUE", "AUTONOMY_LEVEL", "SHIPPING_FEE"
    ]
    target_scope: Literal["GLOBAL", "CATEGORY", "SKU"] = "GLOBAL"
    target_id: str | None = None
    rule_value: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class PolicyRuleCreate(PolicyRuleBase):
    """Schema for creating a policy rule."""

    merchant_id: uuid.UUID


class PolicyRuleRead(PolicyRuleBase):
    """Schema for reading a policy rule."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    merchant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
