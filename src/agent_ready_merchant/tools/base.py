"""Abstract base class for all gateway tools."""

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.constants import COMMERCE_PROTOCOL_VERSION


@dataclass
class GatewayContext:
    """Session security and merchant boundary context passed into tool execution."""

    merchant_id: uuid.UUID
    session_id: uuid.UUID
    capabilities: set[str]
    actor_type: str = "BUYER_AGENT"
    autonomy_level: int = 1  # 0: Read-Only, 1: Bounded Auto, 2: HITL
    max_discount_percentage: float = 15.0
    min_margin_percentage: float = 20.0
    max_single_transaction_paise: int = 5_000_000
    request_id: uuid.UUID | None = None
    idempotency_key: str | None = None
    auth_token: str | None = None
    schema_version: str = COMMERCE_PROTOCOL_VERSION

    def has_capability(self, required_cap: str | None) -> bool:
        if required_cap is None:
            return True
        return required_cap in self.capabilities


class BaseTool(ABC):
    """Abstract interface for all registered gateway tools."""

    name: str
    description: str
    side_effect_class: Literal["READ_ONLY", "TRANSIENT_STATE", "PRIVILEGED_FINANCIAL"]
    required_capability: str | None
    param_schema: type[BaseModel]

    @abstractmethod
    async def execute(
        self,
        session: AsyncSession,
        params: BaseModel,
        context: GatewayContext,
    ) -> dict[str, Any]:
        """Executes the tool logic deterministically within the provided DB session."""
        pass
