"""Pydantic schemas for Phase 7 Merchant Agent intelligence layer."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat


class ObservationCategory(StrEnum):
    """Categorization of commerce observations."""

    OBSERVED = "OBSERVED"
    DERIVED = "DERIVED"
    ESTIMATED = "ESTIMATED"


class ObservationTelemetryItem(BaseModel):
    """Single authoritative telemetry item in the merchant observation snapshot."""

    model_config = ConfigDict(extra="forbid")

    category: ObservationCategory
    metric_name: str
    value: float | int | str
    formatted_value: str
    unit: str
    sample_size: int = Field(default=0, ge=0)
    window_days: int = Field(default=30, ge=1)
    description: str


class MerchantObservationSnapshot(BaseModel):
    """Bounded, tenant-scoped intelligence snapshot presented to the reasoning engine."""

    model_config = ConfigDict(extra="forbid")

    merchant_id: uuid.UUID
    store_name: str
    currency: str = "INR"
    autonomy_level: int = Field(default=1, ge=0, le=2)
    active_policies: dict[str, Any] = Field(default_factory=dict)
    catalog_summary: dict[str, Any] = Field(default_factory=dict)
    telemetry: list[ObservationTelemetryItem] = Field(default_factory=list)
    signals: list[dict[str, Any]] = Field(default_factory=list)
    recent_proposals: list[dict[str, Any]] = Field(default_factory=list)
    recent_experiments: list[dict[str, Any]] = Field(default_factory=list)
    generated_at: datetime


class DiagnosisPattern(StrEnum):
    """Supported diagnostic pattern classifications."""

    REPEATED_BUYER_CONFUSION = "REPEATED_BUYER_CONFUSION"
    MISSING_PRODUCT_INFO = "MISSING_PRODUCT_INFO"
    WEAK_DISCOVERY_METADATA = "WEAK_DISCOVERY_METADATA"
    CHECKOUT_FRICTION = "CHECKOUT_FRICTION"
    FAILED_PAYMENT_PATTERNS = "FAILED_PAYMENT_PATTERNS"
    POOR_OFFER_ACCEPTANCE = "POOR_OFFER_ACCEPTANCE"
    LOW_CONVERSION_PRODUCTS = "LOW_CONVERSION_PRODUCTS"
    INVENTORY_LOST_DEMAND = "INVENTORY_LOST_DEMAND"
    REPEATED_DELIVERY_QUESTIONS = "REPEATED_DELIVERY_QUESTIONS"


class MerchantDiagnosisItem(BaseModel):
    """Structured diagnostic finding with explicit evidence references."""

    model_config = ConfigDict(extra="forbid")

    pattern: DiagnosisPattern
    summary: str
    severity: Literal["LOW", "MEDIUM", "HIGH"]
    evidence_references: list[str] = Field(default_factory=list)
    affected_entities: list[str] = Field(default_factory=list)


class ProposalType(StrEnum):
    """Supported MVP proposal types."""

    IMPROVE_PRODUCT_DESCRIPTION = "IMPROVE_PRODUCT_DESCRIPTION"
    EXPOSE_DELIVERY_ETA = "EXPOSE_DELIVERY_ETA"
    REORDER_RECOMMENDATIONS = "REORDER_RECOMMENDATIONS"
    IMPROVE_DISCOVERY_METADATA = "IMPROVE_DISCOVERY_METADATA"
    SUGGEST_BUNDLE = "SUGGEST_BUNDLE"
    SUGGEST_PROMOTIONAL_OFFER = "SUGGEST_PROMOTIONAL_OFFER"
    SUGGEST_BOUNDED_EXPERIMENT = "SUGGEST_BOUNDED_EXPERIMENT"


class ProposalRiskLevel(StrEnum):
    """Server-authoritative risk classifications."""

    READ_ONLY = "READ_ONLY"
    LOW_RISK_REVERSIBLE = "LOW_RISK_REVERSIBLE"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    PROHIBITED = "PROHIBITED"


class ProposalStatus(StrEnum):
    """Proposal lifecycle status."""

    PROPOSED = "PROPOSED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CONVERTED_TO_EXPERIMENT = "CONVERTED_TO_EXPERIMENT"
    ARCHIVED = "ARCHIVED"


class MerchantProposalCreate(BaseModel):
    """Structured proposal payload outputted by the LLM reasoning step."""

    model_config = ConfigDict(extra="forbid")

    proposal_type: ProposalType
    title: str = Field(..., min_length=5, max_length=255)
    observation: str = Field(..., min_length=10)
    evidence: list[str] = Field(..., min_length=1)
    hypothesis: str = Field(..., min_length=10)
    proposed_change: str = Field(..., min_length=10)
    target_entity: str = Field(default="general", max_length=128)
    expected_effect: str = Field(..., min_length=5)
    expected_metric: str = Field(..., max_length=64)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    estimated_cost_paise: int = Field(default=0, ge=0)
    metadata_payload: dict[str, Any] = Field(default_factory=dict)


class MerchantProposalResponse(BaseModel):
    """Authoritative API response for a merchant proposal."""

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    merchant_id: uuid.UUID
    run_id: uuid.UUID | None = None
    proposal_type: str
    title: str
    observation: str
    evidence: list[str]
    hypothesis: str
    proposed_change: str
    target_entity: str
    expected_effect: str
    expected_metric: str
    confidence: float
    estimated_cost_paise: int
    risk_level: str
    status: str
    rejection_reason: str | None = None
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    metadata_payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class MerchantProposalReviewRequest(BaseModel):
    """Payload for human review of a proposal."""

    model_config = ConfigDict(extra="forbid")

    decision: Literal["APPROVE", "REJECT", "CONVERT_TO_EXPERIMENT"]
    rejection_reason: str | None = Field(default=None, max_length=1000)


class ExperimentStatus(StrEnum):
    """Lifecycle states for merchant optimization experiments."""

    DRAFT = "DRAFT"
    PROPOSED = "PROPOSED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    APPROVED = "APPROVED"
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    STOPPED = "STOPPED"
    ROLLED_BACK = "ROLLED_BACK"
    REJECTED = "REJECTED"


class ExperimentCreateRequest(BaseModel):
    """Payload for registering a structured merchant experiment."""

    model_config = ConfigDict(extra="forbid")

    proposal_id: uuid.UUID | None = None
    title: str = Field(..., min_length=5, max_length=255)
    hypothesis: str = Field(..., min_length=10)
    target_metric: str = Field(..., min_length=2, max_length=64)
    baseline_value: float = Field(default=0.0)
    target_value: FiniteFloat = Field(default=0.0, ge=0.0)
    proposed_variation: dict[str, Any] = Field(default_factory=dict)
    stopping_condition: dict[str, Any] = Field(default_factory=dict)
    rollback_condition: dict[str, Any] = Field(default_factory=dict)


class ExperimentResultResponse(BaseModel):
    """Authoritative deterministic measurement result for an experiment."""

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    experiment_id: uuid.UUID
    merchant_id: uuid.UUID
    sample_size: int = Field(..., ge=0)
    baseline_metric: float
    post_experiment_metric: float
    absolute_change: float
    percentage_change: float
    confidence_score: float
    limitations: list[str] = Field(default_factory=list)
    recommendation: Literal["KEEP", "ROLLBACK", "INCONCLUSIVE"]
    deterministic_evidence: dict[str, Any] = Field(default_factory=dict)
    recorded_at: datetime


class ExperimentResponse(BaseModel):
    """Authoritative API response for a merchant experiment."""

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    merchant_id: uuid.UUID
    proposal_id: uuid.UUID | None = None
    title: str
    hypothesis: str
    target_metric: str
    baseline_value: float
    target_value: float
    proposed_variation: dict[str, Any]
    risk_level: str
    status: str
    approval_status: str
    approved_by: str | None = None
    approved_at: datetime | None = None
    stopping_condition: dict[str, Any]
    rollback_condition: dict[str, Any]
    start_time: datetime | None = None
    end_time: datetime | None = None
    created_at: datetime
    updated_at: datetime
    results: list[ExperimentResultResponse] = Field(default_factory=list)


class MerchantAgentAnalyzeResponse(BaseModel):
    """Complete structured response of a Merchant Agent optimization run."""

    model_config = ConfigDict(extra="forbid")

    run_id: uuid.UUID
    merchant_id: uuid.UUID
    status: str
    snapshot: MerchantObservationSnapshot
    diagnoses: list[MerchantDiagnosisItem]
    proposals: list[MerchantProposalResponse]
    step_count: int
    total_tokens: int
    execution_duration_ms: float
    executed_at: datetime
    message: str
