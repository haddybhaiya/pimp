"""Pydantic schemas and typed request/response models for Razorpay API.

Adheres strictly to docs/razorpay-integration-notes.md and integer paise representation.
"""

from typing import Any

from pydantic import BaseModel, Field


class RazorpayOrderCreateRequest(BaseModel):
    """Payload for POST /v1/orders."""

    amount: int = Field(..., gt=0, description="Amount in integer paise")
    currency: str = Field(default="INR", description="3-letter ISO currency code")
    receipt: str = Field(
        ..., max_length=40, description="Internal receipt identifier (max 40 chars)"
    )
    payment_capture: int = Field(default=1, description="1 for auto-capture, 0 for manual capture")
    notes: dict[str, Any] = Field(default_factory=dict, description="Custom metadata notes")


class RazorpayOrderResponse(BaseModel):
    """Response returned by POST /v1/orders and GET /v1/orders/{id}."""

    id: str = Field(..., description="Razorpay order ID (e.g. order_EKwxwAgItmmXdp)")
    entity: str = Field(default="order")
    amount: int = Field(..., gt=0, description="Order amount in integer paise")
    amount_paid: int = Field(default=0, ge=0, description="Amount paid in paise")
    amount_due: int = Field(default=0, ge=0, description="Amount due in paise")
    currency: str = Field(default="INR")
    receipt: str | None = None
    status: str = Field(..., description="'created', 'attempted', or 'paid'")
    attempts: int = Field(default=0)
    notes: dict[str, Any] = Field(default_factory=dict)
    created_at: int = Field(...)


class RazorpayPaymentResponse(BaseModel):
    """Response returned for payment entities."""

    id: str = Field(..., description="Razorpay payment ID (e.g. pay_29QQoUBcxrhErF)")
    entity: str = Field(default="payment")
    amount: int = Field(..., gt=0, description="Payment amount in integer paise")
    currency: str = Field(default="INR")
    status: str = Field(
        ..., description="'created', 'authorized', 'captured', 'refunded', 'failed'"
    )
    order_id: str | None = Field(default=None, description="Razorpay order ID")
    method: str | None = Field(
        default=None, description="Payment method (e.g. card, upi, netbanking)"
    )
    error_code: str | None = None
    error_description: str | None = None
    created_at: int | None = None


class RazorpayRefundResponse(BaseModel):
    """Response returned for refund entities."""

    id: str = Field(..., description="Razorpay refund ID (e.g. rfd_12345)")
    entity: str = Field(default="refund")
    amount: int = Field(..., gt=0, description="Refund amount in integer paise")
    currency: str = Field(default="INR")
    payment_id: str = Field(..., description="Razorpay payment ID")
    status: str = Field(..., description="'processed', 'pending', 'failed'")
    notes: dict[str, Any] = Field(default_factory=dict)
    created_at: int | None = None


class RazorpayPaymentCollection(BaseModel):
    """Collection returned by GET /v1/orders/{order_id}/payments."""

    entity: str = Field(default="collection")
    count: int = Field(default=0)
    items: list[RazorpayPaymentResponse] = Field(default_factory=list)


class RazorpayWebhookEvent(BaseModel):
    """Envelope for incoming Razorpay webhook payloads."""

    entity: str = Field(default="event")
    account_id: str | None = None
    event: str = Field(
        ..., description="Event name (e.g. order.paid, payment.captured, payment.failed)"
    )
    contains: list[str] = Field(default_factory=list)
    payload: dict[str, Any] = Field(..., description="Nested event data")
    created_at: int | None = None
