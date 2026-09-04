"""Pydantic schemas for Phase 8 Controlled Autonomy governance and execution."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, StrictBool

from agent_ready_merchant.models.autonomy import (
    AnomalyState,
    AutonomyActionStatus,
    AutonomyActionType,
    AutonomyClassification,
    RollbackStatus,
)


class AutonomyRuleResponse(BaseModel):
    """Authoritative representation of a merchant autonomy rule."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    merchant_id: uuid.UUID
    action_type: AutonomyActionType
    is_enabled: bool
    classification: AutonomyClassification
    max_executions_per_hour: int
    max_executions_per_day: int
    cooldown_seconds: int
    experiment_duration_limit_days: int
    experiment_exposure_limit: int | None = None
    rollback_required: bool
    approval_required: bool
    policy_version: int
    policy_hash: str
    bounded_monetary_limit_paise: int
    version: int
    created_at: datetime
    updated_at: datetime


class AutonomyRuleUpdateRequest(BaseModel):
    """Schema for human-only updates to an autonomy rule.

    Extra fields are strictly forbidden (INV-AGY-01).
    """

    model_config = ConfigDict(extra="forbid")

    is_enabled: bool | None = None
    classification: AutonomyClassification | None = None
    max_executions_per_hour: int | None = Field(default=None, ge=1, le=100)
    max_executions_per_day: int | None = Field(default=None, ge=1, le=1000)
    cooldown_seconds: int | None = Field(default=None, ge=0, le=86400)
    experiment_duration_limit_days: int | None = Field(default=None, ge=1, le=365)
    experiment_exposure_limit: int | None = Field(default=None, ge=1)
    rollback_required: bool | None = None
    approval_required: bool | None = None
    bounded_monetary_limit_paise: int | None = Field(default=None, ge=0)
    expected_version: int = Field(..., ge=1)


class AutonomyActionResponse(BaseModel):
    """Authoritative ledger entry for an autonomous action."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    merchant_id: uuid.UUID
    agent_run_id: uuid.UUID | None = None
    proposal_id: uuid.UUID | None = None
    experiment_id: uuid.UUID | None = None
    action_type: AutonomyActionType
    target_entity_type: str
    target_entity_id: uuid.UUID
    target_version_before: int
    target_version_after: int
    deterministic_classification: str
    autonomy_rule_hash: str
    autonomy_rule_version: int
    hourly_budget_consumed: int
    daily_budget_consumed: int
    status: AutonomyActionStatus
    rollback_snapshot: dict[str, Any]
    rollback_status: RollbackStatus
    rolled_back_at: datetime | None = None
    rolled_back_by: str | None = None
    stopping_reason: str | None = None
    anomaly_state: AnomalyState
    idempotency_key: str
    created_at: datetime


class AutonomousExecutionRequest(BaseModel):
    """Request to autonomously execute an approved or auto-eligible proposal."""

    model_config = ConfigDict(extra="forbid")

    proposal_id: uuid.UUID
    expected_target_version: int = Field(..., ge=1)


class AutonomousExecutionResponse(BaseModel):
    """Response returned upon autonomous execution completion."""

    model_config = ConfigDict(extra="forbid")

    action: AutonomyActionResponse
    message: str
    status: str


class RollbackRequest(BaseModel):
    """Request to deterministically roll back an autonomous action."""

    model_config = ConfigDict(extra="forbid")

    reason: str = Field(..., min_length=3, max_length=500)
    expected_target_version: int = Field(..., ge=1)


class StopExperimentRequest(BaseModel):
    """Strict human request to stop or roll back an experiment."""

    model_config = ConfigDict(extra="forbid")

    reason: str = Field(default="Human merchant requested stop", min_length=3, max_length=500)
    require_rollback: StrictBool = False


class RollbackResponse(BaseModel):
    """Response from an authoritative rollback operation."""

    model_config = ConfigDict(extra="forbid")

    action_id: uuid.UUID
    rollback_status: RollbackStatus
    target_entity_id: uuid.UUID
    target_entity_type: str
    target_version_reverted_to: int
    target_current_version: int
    rolled_back_at: datetime
    message: str


class KillSwitchUpdateRequest(BaseModel):
    """Request to enable or disable the merchant master kill switch."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool
    reason: str = Field(default="Merchant administrative kill switch trigger", max_length=500)


class KillSwitchResponse(BaseModel):
    """Response containing updated kill switch status."""

    model_config = ConfigDict(extra="forbid")

    kill_switch_enabled: bool
    merchant_id: uuid.UUID
    updated_at: datetime


class AutonomyStatusResponse(BaseModel):
    """Comprehensive autonomy health, kill switch, anomaly, and budget status."""

    model_config = ConfigDict(extra="forbid")

    merchant_id: uuid.UUID
    kill_switch_enabled: bool
    anomaly_state: AnomalyState
    anomaly_reasons: list[str] = Field(default_factory=list)
    hourly_executions_count: int
    daily_executions_count: int
    recent_actions: list[AutonomyActionResponse] = Field(default_factory=list)
    rules: list[AutonomyRuleResponse] = Field(default_factory=list)
