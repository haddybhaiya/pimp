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

    # =========================================================================
    # Canonical Commerce Gateway Endpoints (Phase 2.1)
    # =========================================================================
    from agent_ready_merchant.gateway.canonical import CanonicalCommerceGateway
    from agent_ready_merchant.gateway.registry import CapabilityDefinition, CapabilityRegistry
    from agent_ready_merchant.gateway.representation import MerchantAIRepresentation
    from agent_ready_merchant.gateway.schemas import (
        AcceptQuoteGatewayRequest,
        AcceptQuoteGatewayResponse,
        CalculateShippingRequest,
        CalculateShippingResponse,
        CheckInventoryRequest,
        CheckInventoryResponse,
        CreateOrderGatewayRequest,
        CreateOrderGatewayResponse,
        DiscoverProductsRequest,
        DiscoverProductsResponse,
        GatewayResponseEnvelope,
        GetOrderStatusRequest,
        GetOrderStatusResponse,
        GetPaymentStatusRequest,
        GetPaymentStatusResponse,
        GetProductRequest,
        GetProductResponse,
        GetQuoteRequest,
        GetQuoteResponse,
        InitializeSessionRequest,
        InitializeSessionResponse,
        NegotiateQuoteGatewayRequest,
        NegotiateQuoteGatewayResponse,
        RequestCheckoutRequest,
        RequestCheckoutResponse,
        TerminateSessionRequest,
        TerminateSessionResponse,
    )
    from agent_ready_merchant.tools.base import GatewayContext

    def _get_context(
        merchant_id: uuid.UUID,
        session_id: uuid.UUID | None,
        capabilities_hdr: str | None,
        settings: Settings,
        request_id: uuid.UUID | None = None,
        idempotency_key: str | None = None,
    ) -> GatewayContext:
        if capabilities_hdr:
            caps = {c.strip() for c in capabilities_hdr.split(",") if c.strip()}
        else:
            caps = {
                "buyer:discover",
                "buyer:read",
                "buyer:quote",
                "buyer:negotiate",
                "buyer:checkout",
                "buyer:payment_status",
            }
        return GatewayContext(
            merchant_id=merchant_id,
            session_id=session_id or uuid.uuid4(),
            capabilities=caps,
            autonomy_level=settings.DEFAULT_MERCHANT_AUTONOMY_LEVEL,
            max_discount_percentage=settings.DEFAULT_MAX_DISCOUNT_PERCENTAGE,
            min_margin_percentage=settings.DEFAULT_MIN_MARGIN_PERCENTAGE,
            max_single_transaction_paise=settings.MAX_SINGLE_TRANSACTION_PAISE,
            request_id=request_id or uuid.uuid4(),
            idempotency_key=idempotency_key,
        )

    gateway_instance = CanonicalCommerceGateway()

    @app.get(
        "/api/v1/gateway/merchant-representation",
        summary="Get Authoritative Merchant AI Representation",
        tags=["Canonical Gateway"],
        response_model=MerchantAIRepresentation,
    )
    async def get_merchant_representation_endpoint(
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_session_id: uuid.UUID | None = Header(default=None, alias="X-Session-ID"),
        x_capabilities: str | None = Header(default=None, alias="X-Capabilities"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> MerchantAIRepresentation:
        ctx = _get_context(x_merchant_id, x_session_id, x_capabilities, current_settings)
        try:
            return await gateway_instance.get_merchant_representation(db, x_merchant_id, ctx)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get(
        "/api/v1/gateway/capabilities",
        summary="List Canonical Capabilities Catalog",
        tags=["Canonical Gateway"],
        response_model=list[CapabilityDefinition],
    )
    async def list_capabilities_endpoint() -> list[CapabilityDefinition]:
        return CapabilityRegistry.get_all_capabilities()

    class GatewayExecuteRequest(BaseModel):
        capability: str
        payload: dict[str, Any] = Field(default_factory=dict)

    @app.post(
        "/api/v1/gateway/execute",
        summary="Unified Gateway Capability Dispatcher",
        tags=["Canonical Gateway"],
        response_model=GatewayResponseEnvelope[Any],
    )
    async def execute_gateway_capability(
        req: GatewayExecuteRequest,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_session_id: uuid.UUID | None = Header(default=None, alias="X-Session-ID"),
        x_capabilities: str | None = Header(default=None, alias="X-Capabilities"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[Any]:
        ctx = _get_context(x_merchant_id, x_session_id, x_capabilities, current_settings)
        return await gateway_instance.execute_capability(db, req.capability, req.payload, ctx)

    @app.post(
        "/api/v1/gateway/discover-products",
        summary="Discover Products Capability",
        tags=["Canonical Gateway"],
        response_model=GatewayResponseEnvelope[DiscoverProductsResponse],
    )
    async def discover_products_endpoint(
        req: DiscoverProductsRequest,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_session_id: uuid.UUID | None = Header(default=None, alias="X-Session-ID"),
        x_capabilities: str | None = Header(default=None, alias="X-Capabilities"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[DiscoverProductsResponse]:
        ctx = _get_context(x_merchant_id, x_session_id, x_capabilities, current_settings)
        return await gateway_instance.discover_products(db, req, ctx)

    @app.get(
        "/api/v1/gateway/products/{sku}",
        summary="Get Product Details Capability",
        tags=["Canonical Gateway"],
        response_model=GatewayResponseEnvelope[GetProductResponse],
    )
    async def get_product_endpoint(
        sku: str,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_session_id: uuid.UUID | None = Header(default=None, alias="X-Session-ID"),
        x_capabilities: str | None = Header(default=None, alias="X-Capabilities"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[GetProductResponse]:
        ctx = _get_context(x_merchant_id, x_session_id, x_capabilities, current_settings)
        return await gateway_instance.get_product(db, GetProductRequest(sku=sku), ctx)

    @app.post(
        "/api/v1/gateway/inventory/check",
        summary="Check Inventory Capability",
        tags=["Canonical Gateway"],
        response_model=GatewayResponseEnvelope[CheckInventoryResponse],
    )
    async def check_inventory_endpoint(
        req: CheckInventoryRequest,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_session_id: uuid.UUID | None = Header(default=None, alias="X-Session-ID"),
        x_capabilities: str | None = Header(default=None, alias="X-Capabilities"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[CheckInventoryResponse]:
        ctx = _get_context(x_merchant_id, x_session_id, x_capabilities, current_settings)
        return await gateway_instance.check_inventory(db, req, ctx)

    @app.post(
        "/api/v1/gateway/quotes",
        summary="Get / Create Quote Capability",
        tags=["Canonical Gateway"],
        response_model=GatewayResponseEnvelope[GetQuoteResponse],
    )
    async def get_quote_endpoint(
        req: GetQuoteRequest,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_session_id: uuid.UUID | None = Header(default=None, alias="X-Session-ID"),
        x_capabilities: str | None = Header(default=None, alias="X-Capabilities"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[GetQuoteResponse]:
        ctx = _get_context(x_merchant_id, x_session_id, x_capabilities, current_settings)
        return await gateway_instance.get_quote(db, req, ctx)

    @app.post(
        "/api/v1/gateway/shipping/calculate",
        summary="Calculate Shipping Capability",
        tags=["Canonical Gateway"],
        response_model=GatewayResponseEnvelope[CalculateShippingResponse],
    )
    async def calculate_shipping_endpoint(
        req: CalculateShippingRequest,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_session_id: uuid.UUID | None = Header(default=None, alias="X-Session-ID"),
        x_capabilities: str | None = Header(default=None, alias="X-Capabilities"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[CalculateShippingResponse]:
        ctx = _get_context(x_merchant_id, x_session_id, x_capabilities, current_settings)
        return await gateway_instance.calculate_shipping(db, req, ctx)

    @app.post(
        "/api/v1/gateway/orders",
        summary="Create Order Capability",
        tags=["Canonical Gateway"],
        response_model=GatewayResponseEnvelope[CreateOrderGatewayResponse],
    )
    async def create_order_endpoint(
        req: CreateOrderGatewayRequest,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_session_id: uuid.UUID | None = Header(default=None, alias="X-Session-ID"),
        x_capabilities: str | None = Header(default=None, alias="X-Capabilities"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[CreateOrderGatewayResponse]:
        ctx = _get_context(x_merchant_id, x_session_id, x_capabilities, current_settings)
        return await gateway_instance.create_order(db, req, ctx)

    @app.post(
        "/api/v1/gateway/checkout",
        summary="Request Checkout Capability",
        tags=["Canonical Gateway"],
        response_model=GatewayResponseEnvelope[RequestCheckoutResponse],
    )
    async def request_checkout_endpoint(
        req: RequestCheckoutRequest,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_session_id: uuid.UUID | None = Header(default=None, alias="X-Session-ID"),
        x_capabilities: str | None = Header(default=None, alias="X-Capabilities"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[RequestCheckoutResponse]:
        ctx = _get_context(x_merchant_id, x_session_id, x_capabilities, current_settings)
        return await gateway_instance.request_checkout(db, req, ctx)

    @app.get(
        "/api/v1/gateway/payments/{order_id}/status",
        summary="Get Payment Status Capability",
        tags=["Canonical Gateway"],
        response_model=GatewayResponseEnvelope[GetPaymentStatusResponse],
    )
    async def get_payment_status_endpoint(
        order_id: uuid.UUID,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_session_id: uuid.UUID | None = Header(default=None, alias="X-Session-ID"),
        x_capabilities: str | None = Header(default=None, alias="X-Capabilities"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[GetPaymentStatusResponse]:
        ctx = _get_context(x_merchant_id, x_session_id, x_capabilities, current_settings)
        return await gateway_instance.get_payment_status(
            db, GetPaymentStatusRequest(order_id=order_id), ctx
        )

    @app.post(
        "/api/v1/gateway/sessions/initialize",
        summary="Initialize Buyer Session Capability",
        tags=["Canonical Gateway"],
        response_model=GatewayResponseEnvelope[InitializeSessionResponse],
    )
    async def initialize_session_endpoint(
        req: InitializeSessionRequest,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        db: AsyncSession = Depends(get_db_session),
    ) -> GatewayResponseEnvelope[InitializeSessionResponse]:
        return await gateway_instance.initialize_session(db, req, x_merchant_id)

    @app.post(
        "/api/v1/gateway/sessions/terminate",
        summary="Terminate Buyer Session Capability",
        tags=["Canonical Gateway"],
        response_model=GatewayResponseEnvelope[TerminateSessionResponse],
    )
    async def terminate_session_endpoint(
        req: TerminateSessionRequest,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_session_id: uuid.UUID | None = Header(default=None, alias="X-Session-ID"),
        x_capabilities: str | None = Header(default=None, alias="X-Capabilities"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[TerminateSessionResponse]:
        ctx = _get_context(x_merchant_id, x_session_id, x_capabilities, current_settings)
        return await gateway_instance.terminate_session(db, req, ctx)

    @app.post(
        "/api/v1/gateway/quotes/negotiate",
        summary="Negotiate Quote Capability",
        tags=["Canonical Gateway"],
        response_model=GatewayResponseEnvelope[NegotiateQuoteGatewayResponse],
    )
    async def negotiate_quote_endpoint(
        req: NegotiateQuoteGatewayRequest,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_session_id: uuid.UUID | None = Header(default=None, alias="X-Session-ID"),
        x_capabilities: str | None = Header(default=None, alias="X-Capabilities"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[NegotiateQuoteGatewayResponse]:
        ctx = _get_context(x_merchant_id, x_session_id, x_capabilities, current_settings)
        return await gateway_instance.negotiate_quote(db, req, ctx)

    @app.post(
        "/api/v1/gateway/quotes/accept",
        summary="Accept Quote Capability",
        tags=["Canonical Gateway"],
        response_model=GatewayResponseEnvelope[AcceptQuoteGatewayResponse],
    )
    async def accept_quote_endpoint(
        req: AcceptQuoteGatewayRequest,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_session_id: uuid.UUID | None = Header(default=None, alias="X-Session-ID"),
        x_capabilities: str | None = Header(default=None, alias="X-Capabilities"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[AcceptQuoteGatewayResponse]:
        ctx = _get_context(x_merchant_id, x_session_id, x_capabilities, current_settings)
        return await gateway_instance.accept_quote(db, req, ctx)

    @app.get(
        "/api/v1/gateway/orders/{order_id}/status",
        summary="Get Order Status Capability",
        tags=["Canonical Gateway"],
        response_model=GatewayResponseEnvelope[GetOrderStatusResponse],
    )
    async def get_order_status_endpoint(
        order_id: uuid.UUID,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_session_id: uuid.UUID | None = Header(default=None, alias="X-Session-ID"),
        x_capabilities: str | None = Header(default=None, alias="X-Capabilities"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[GetOrderStatusResponse]:
        ctx = _get_context(x_merchant_id, x_session_id, x_capabilities, current_settings)
        return await gateway_instance.get_order_status(
            db, GetOrderStatusRequest(order_id=order_id), ctx
        )

    # =========================================================================
    # Protocol Adapter Endpoints (Phase 2.3)
    # =========================================================================
    from agent_ready_merchant.protocols.acp import AgentCommerceProtocolAdapter
    from agent_ready_merchant.protocols.base import (
        ProtocolRequestMessage,
        ProtocolResponseMessage,
    )

    acp_adapter = AgentCommerceProtocolAdapter()

    @app.post(
        "/api/v1/protocol/acp",
        summary="Agent Commerce Protocol (ACP) Wire Endpoint",
        tags=["Protocols"],
        response_model=ProtocolResponseMessage,
    )
    async def acp_wire_endpoint(
        msg: ProtocolRequestMessage,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_session_id: uuid.UUID | None = Header(default=None, alias="X-Session-ID"),
        x_capabilities: str | None = Header(default=None, alias="X-Capabilities"),
        x_request_id: uuid.UUID | None = Header(default=None, alias="X-Request-ID"),
        x_idempotency_key: str | None = Header(default=None, alias="X-Idempotency-Key"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> ProtocolResponseMessage:
        """Translates ACP wire message to canonical gateway invocation and returns ACP response."""
        req_id = msg.request_id or x_request_id or uuid.uuid4()
        idemp_key = msg.idempotency_key or x_idempotency_key
        ctx = _get_context(
            merchant_id=x_merchant_id,
            session_id=x_session_id,
            capabilities_hdr=x_capabilities,
            settings=current_settings,
            request_id=req_id,
            idempotency_key=idemp_key,
        )

        try:
            capability, payload = acp_adapter.to_canonical_request(msg)
        except ValueError as exc:
            return acp_adapter.format_error_response(
                error_code="INVALID_PROTOCOL_MESSAGE",
                message=str(exc),
                request_id=req_id,
                action=msg.action,
                retryable=False,
            )

        envelope = await gateway_instance.execute_capability(db, capability, payload, ctx)
        return acp_adapter.from_canonical_envelope(capability, envelope, msg)

    return app


app = create_app()
