"""Abstract base class for all gateway tools."""

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class GatewayContext:
    """Session security and merchant boundary context passed into tool execution."""

    merchant_id: uuid.UUID
    session_id: uuid.UUID
    capabilities: set[str]
    autonomy_level: int = 1  # 0: Read-Only, 1: Bounded Auto, 2: HITL
    max_discount_percentage: float = 15.0
    min_margin_percentage: float = 20.0
    max_single_transaction_paise: int = 10_000_000

    def has_capability(self, required_cap: str | None) -> bool:
        if not required_cap:
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
