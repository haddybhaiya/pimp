"""FastAPI application bootstrap, health, and payment webhook endpoints.

Establishes the deterministic application lifecycle for the Agent-Ready Merchant platform.
"""

import logging
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

import agent_ready_merchant
from agent_ready_merchant.config import Settings, get_settings
from agent_ready_merchant.db.session import close_db_engine, get_db_session, get_engine
from agent_ready_merchant.integrations.razorpay.client import RazorpayClient
from agent_ready_merchant.integrations.razorpay.exceptions import (
    AmountMismatchFraudError,
    InvalidWebhookSignatureError,
)
from agent_ready_merchant.services.payment_service import PaymentService

logger = logging.getLogger("agent_ready_merchant")


class CreateOrderFromQuoteRequest(BaseModel):
    """Request payload to create an order from an accepted quote."""

    quote_id: uuid.UUID
    buyer_email: EmailStr
    shipping_address: dict[str, Any] = Field(default_factory=dict)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application startup and graceful shutdown lifecycle."""
    settings = get_settings()
    engine = get_engine()

    if not settings.is_testing:
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
        except Exception as exc:
            logger.warning("Initial DB check failed: %s", exc)

    yield

    await close_db_engine()


def create_app() -> FastAPI:
    """Factory creating configured FastAPI application instance."""
    settings = get_settings()

    app = FastAPI(
        title="Agent-Ready Merchant Platform",
        description="Autonomous AI Commerce Control Plane on Razorpay Infrastructure",
        version=agent_ready_merchant.__version__,
        lifespan=lifespan,
        debug=settings.DEBUG,
    )

    @app.get(
        "/health",
        summary="Service Health Check",
        tags=["System"],
        status_code=status.HTTP_200_OK,
    )
    async def health_check(
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> dict[str, Any]:
        """Health check endpoint verifying application runtime and database connectivity."""
        db_healthy = False
        try:
            result = await db.execute(text("SELECT 1"))
            db_healthy = result.scalar() == 1
        except Exception:
            db_healthy = False

        return {
            "status": "healthy" if db_healthy else "degraded",
            "service": "agent-ready-merchant",
            "version": agent_ready_merchant.__version__,
            "environment": current_settings.ENVIRONMENT,
            "database_connected": db_healthy,
        }

    @app.get(
        "/",
        summary="Platform Root Descriptor",
        tags=["System"],
        status_code=status.HTTP_200_OK,
    )
    async def root_descriptor(
        current_settings: Settings = Depends(get_settings),
    ) -> dict[str, Any]:
        """Returns machine-readable platform metadata."""
        return {
            "name": "Agent-Ready Merchant Platform",
            "version": agent_ready_merchant.__version__,
            "status": "active",
            "docs_url": "/docs",
            "environment": current_settings.ENVIRONMENT,
        }

    @app.post(
        "/api/v1/payments/webhook",
        summary="Razorpay Webhook Receiver",
        tags=["Payments"],
        status_code=status.HTTP_200_OK,
    )
    async def razorpay_webhook(
        request: Request,
        x_razorpay_signature: str | None = Header(default=None, alias="X-Razorpay-Signature"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> dict[str, Any]:
        """Receives and processes signed Razorpay webhooks."""
        raw_body = await request.body()
        secret = current_settings.RAZORPAY_WEBHOOK_SECRET.get_secret_value()

        try:
            result = await PaymentService.process_payment_webhook(
                session=db,
                raw_body=raw_body,
                signature_header=x_razorpay_signature,
                webhook_secret=secret,
            )
            return result
        except InvalidWebhookSignatureError as exc:
            logger.warning("Rejected webhook with invalid signature: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook signature",
            ) from exc
        except AmountMismatchFraudError as exc:
            logger.error("Fraud attempt caught during webhook processing: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Amount mismatch fraud detected",
            ) from exc

    @app.post(
        "/api/v1/orders/create-from-quote",
        summary="Create Order From Quote",
        tags=["Orders"],
        status_code=status.HTTP_201_CREATED,
    )
    async def create_order_from_quote(
        payload: CreateOrderFromQuoteRequest,
        x_merchant_id: uuid.UUID | None = Header(default=None, alias="X-Merchant-ID"),
        x_session_id: uuid.UUID | None = Header(default=None, alias="X-Session-ID"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> dict[str, Any]:
        """Creates an Order and Razorpay Order from an accepted PriceQuote."""
        # Verify quote ownership if security headers provided
        if x_merchant_id or x_session_id:
            from agent_ready_merchant.models.quote import PriceQuote

            stmt = select(PriceQuote).where(PriceQuote.id == payload.quote_id)
            quote = (await db.execute(stmt)).scalar_one_or_none()
            if not quote:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"PriceQuote with ID {payload.quote_id} not found",
                )
            if x_merchant_id and quote.merchant_id != x_merchant_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Quote does not belong to the authenticated merchant",
                )
            if x_session_id and quote.session_id != x_session_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Quote does not belong to the active session",
                )

        rzp_client = RazorpayClient(
            key_id=current_settings.RAZORPAY_KEY_ID,
            key_secret=current_settings.RAZORPAY_KEY_SECRET,
            base_url=current_settings.RAZORPAY_API_BASE_URL,
        )
        try:
            order = await PaymentService.create_order_from_accepted_quote(
                session=db,
                quote_id=payload.quote_id,
                buyer_email=payload.buyer_email,
                shipping_address=payload.shipping_address,
                rzp_client=rzp_client,
                merchant_id=x_merchant_id,
                session_id=x_session_id,
            )
            return {
                "order_id": str(order.id),
                "rzp_order_id": order.rzp_order_id,
                "amount_paise": order.amount_paise,
                "status": order.status,
            }
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

    @app.post(
        "/api/v1/orders/{order_id}/reconcile",
        summary="Reconcile Order Payment",
        tags=["Orders"],
        status_code=status.HTTP_200_OK,
    )
    async def reconcile_order(
        order_id: uuid.UUID,
        x_merchant_id: uuid.UUID | None = Header(default=None, alias="X-Merchant-ID"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> dict[str, Any]:
        """Triggers out-of-band reconciliation against Razorpay."""
        if x_merchant_id:
            from agent_ready_merchant.models.order import Order

            order_stmt = select(Order).where(Order.id == order_id)
            existing_order = (await db.execute(order_stmt)).scalar_one_or_none()
            if existing_order and existing_order.merchant_id != x_merchant_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Order does not belong to authenticated merchant",
                )

        rzp_client = RazorpayClient(
            key_id=current_settings.RAZORPAY_KEY_ID,
            key_secret=current_settings.RAZORPAY_KEY_SECRET,
            base_url=current_settings.RAZORPAY_API_BASE_URL,
        )
        try:
            return await PaymentService.reconcile_order(
                session=db,
                order_id=order_id,
                rzp_client=rzp_client,
                merchant_id=x_merchant_id,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc

    return app


app = create_app()
