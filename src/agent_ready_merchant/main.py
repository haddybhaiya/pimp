"""FastAPI application bootstrap, health, and payment webhook endpoints.

Establishes the deterministic application lifecycle for the Agent-Ready Merchant platform.
"""

import logging
import uuid
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, status
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

import agent_ready_merchant
from agent_ready_merchant.config import Settings, get_settings
from agent_ready_merchant.db.session import close_db_engine, get_db_session, get_engine
from agent_ready_merchant.integrations.razorpay.client import RazorpayClient
from agent_ready_merchant.integrations.razorpay.exceptions import (
    AmountMismatchFraudError,
    CurrencyMismatchFraudError,
    InvalidWebhookSignatureError,
    OrderMismatchError,
    TransactionBindingError,
    WebhookProcessingInProgressError,
    WebhookReplayError,
    WebhookTimestampError,
)
from agent_ready_merchant.llm.base import BaseLLMProvider
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.services.payment_service import PaymentService

logger = logging.getLogger("agent_ready_merchant")

ADMIN_SESSION_COOKIE = "arm_admin_session"
ADMIN_SESSION_MAX_AGE_SECONDS = 24 * 60 * 60


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

    @app.middleware("http")
    async def attach_admin_session_cookie(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Use an HttpOnly browser session without exposing it to SPA JavaScript."""
        if (
            request.url.path.startswith("/api/v1/merchant/")
            and "x-auth-token" not in request.headers
        ):
            admin_session = request.cookies.get(ADMIN_SESSION_COOKIE)
            if admin_session:
                request.scope["headers"] = [
                    *request.scope["headers"],
                    (b"x-auth-token", admin_session.encode("latin-1")),
                ]
        return await call_next(request)

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
            "application_alive": True,
            "database_reachable": db_healthy,
            "database_connected": db_healthy,
            "configuration_valid": True,
        }

    static_dir = Path(__file__).parent / "static"
    if (static_dir / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")

    @app.get(
        "/",
        summary="Platform Root Descriptor & Web Surface",
        tags=["System"],
        status_code=status.HTTP_200_OK,
    )
    async def root_descriptor(
        request: Request,
        current_settings: Settings = Depends(get_settings),
    ) -> Any:
        """Returns machine-readable metadata or web control plane surface based on Accept header."""
        accept_header = request.headers.get("accept", "")
        index_file = static_dir / "index.html"
        if "text/html" in accept_header and index_file.exists():
            return FileResponse(str(index_file), media_type="text/html")
        return {
            "name": "Agent-Ready Merchant Platform",
            "version": agent_ready_merchant.__version__,
            "status": "active",
            "docs_url": "/docs",
            "environment": current_settings.ENVIRONMENT,
        }

    # SPA Client-Side Routing Fallbacks for Web Control Plane
    for web_route in [
        "/login",
        "/signup",
        "/onboarding",
        "/dashboard",
        "/approvals",
        "/catalog",
        "/inventory",
        "/quotes",
        "/orders",
        "/payments",
        "/negotiations",
        "/policies",
        "/audit",
        "/settings",
        "/demo",
        "/agent",
        "/experiments",
        "/unauthorized",
    ]:

        def _make_route_handler(route_name: str) -> Callable[[], Awaitable[Any]]:
            async def _handler() -> Any:
                index_file = static_dir / "index.html"
                if index_file.exists():
                    return FileResponse(str(index_file), media_type="text/html")
                return HTMLResponse(
                    "<html><body><h1>Agent-Ready Merchant Control Plane</h1></body></html>"
                )

            return _handler

        app.add_api_route(
            web_route,
            _make_route_handler(web_route),
            methods=["GET"],
            include_in_schema=False,
            response_class=HTMLResponse,
        )

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
        except (WebhookReplayError, WebhookTimestampError) as exc:
            logger.warning("Rejected replay or stale webhook: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        except WebhookProcessingInProgressError as exc:
            logger.info("Concurrent webhook processing in progress: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Webhook event is currently processing; retryable",
                headers={"Retry-After": "1"},
            ) from exc
        except AmountMismatchFraudError as exc:
            logger.error("Fraud attempt caught during webhook processing: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Amount mismatch fraud detected",
            ) from exc
        except CurrencyMismatchFraudError as exc:
            logger.error("Currency fraud attempt caught during webhook processing: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Currency mismatch fraud detected",
            ) from exc
        except OrderMismatchError as exc:
            logger.error("Order mismatch caught during webhook processing: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=str(exc),
            ) from exc
        except TransactionBindingError as exc:
            logger.error("Transaction binding violation during webhook processing: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Transaction binding violation",
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
        GetOrderStatusResponse,
        GetPaymentStatusResponse,
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
        auth_token: str | None = None,
    ) -> GatewayContext:
        if session_id:
            caps = {
                "buyer:discover",
                "buyer:read",
                "buyer:quote",
                "buyer:negotiate",
                "buyer:checkout",
                "buyer:payment_status",
            }
        else:
            caps = {"buyer:discover", "buyer:read"}

        if capabilities_hdr:
            requested = {c.strip() for c in capabilities_hdr.split(",") if c.strip()}
            caps = caps.intersection(requested)

        return GatewayContext(
            merchant_id=merchant_id,
            session_id=session_id or uuid.UUID("00000000-0000-0000-0000-000000000000"),
            capabilities=caps,
            autonomy_level=settings.DEFAULT_MERCHANT_AUTONOMY_LEVEL,
            max_discount_percentage=settings.DEFAULT_MAX_DISCOUNT_PERCENTAGE,
            min_margin_percentage=settings.DEFAULT_MIN_MARGIN_PERCENTAGE,
            max_single_transaction_paise=settings.MAX_SINGLE_TRANSACTION_PAISE,
            request_id=request_id or uuid.uuid4(),
            idempotency_key=idempotency_key,
            auth_token=auth_token,
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
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> MerchantAIRepresentation:
        ctx = _get_context(
            x_merchant_id,
            x_session_id,
            x_capabilities,
            current_settings,
            auth_token=x_auth_token,
        )
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
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[Any]:
        ctx = _get_context(
            x_merchant_id,
            x_session_id,
            x_capabilities,
            current_settings,
            auth_token=x_auth_token,
        )
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
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[Any]:
        ctx = _get_context(
            x_merchant_id, x_session_id, x_capabilities, current_settings, auth_token=x_auth_token
        )
        return await gateway_instance.execute_capability(
            db, "discover_products", req.model_dump(mode="json"), ctx
        )

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
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[Any]:
        ctx = _get_context(
            x_merchant_id, x_session_id, x_capabilities, current_settings, auth_token=x_auth_token
        )
        return await gateway_instance.execute_capability(db, "get_product", {"sku": sku}, ctx)

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
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[Any]:
        ctx = _get_context(
            x_merchant_id, x_session_id, x_capabilities, current_settings, auth_token=x_auth_token
        )
        return await gateway_instance.execute_capability(
            db, "check_inventory", req.model_dump(mode="json"), ctx
        )

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
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[Any]:
        ctx = _get_context(
            x_merchant_id, x_session_id, x_capabilities, current_settings, auth_token=x_auth_token
        )
        return await gateway_instance.execute_capability(
            db, "get_quote", req.model_dump(mode="json"), ctx
        )

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
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[Any]:
        ctx = _get_context(
            x_merchant_id, x_session_id, x_capabilities, current_settings, auth_token=x_auth_token
        )
        return await gateway_instance.execute_capability(
            db, "calculate_shipping", req.model_dump(mode="json"), ctx
        )

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
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[Any]:
        ctx = _get_context(
            x_merchant_id, x_session_id, x_capabilities, current_settings, auth_token=x_auth_token
        )
        return await gateway_instance.execute_capability(
            db, "create_order", req.model_dump(mode="json"), ctx
        )

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
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[Any]:
        ctx = _get_context(
            x_merchant_id, x_session_id, x_capabilities, current_settings, auth_token=x_auth_token
        )
        return await gateway_instance.execute_capability(
            db, "request_checkout", req.model_dump(mode="json"), ctx
        )

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
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[Any]:
        ctx = _get_context(
            x_merchant_id, x_session_id, x_capabilities, current_settings, auth_token=x_auth_token
        )
        return await gateway_instance.execute_capability(
            db, "get_payment_status", {"order_id": str(order_id)}, ctx
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
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[Any]:
        ctx = _get_context(
            x_merchant_id, x_session_id, x_capabilities, current_settings, auth_token=x_auth_token
        )
        return await gateway_instance.execute_capability(
            db, "terminate_session", req.model_dump(mode="json"), ctx
        )

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
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[Any]:
        ctx = _get_context(
            x_merchant_id, x_session_id, x_capabilities, current_settings, auth_token=x_auth_token
        )
        return await gateway_instance.execute_capability(
            db, "negotiate_quote", req.model_dump(mode="json"), ctx
        )

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
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[Any]:
        ctx = _get_context(
            x_merchant_id, x_session_id, x_capabilities, current_settings, auth_token=x_auth_token
        )
        return await gateway_instance.execute_capability(
            db, "accept_quote", req.model_dump(mode="json"), ctx
        )

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
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> GatewayResponseEnvelope[Any]:
        ctx = _get_context(
            x_merchant_id, x_session_id, x_capabilities, current_settings, auth_token=x_auth_token
        )
        return await gateway_instance.execute_capability(
            db, "get_order_status", {"order_id": str(order_id)}, ctx
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
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
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
            auth_token=x_auth_token,
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

    # =========================================================================
    # Merchant Auth & Portal Control Plane Endpoints (Phase 5.1)
    # =========================================================================
    from agent_ready_merchant.schemas.merchant_auth import (
        MerchantAuthResponse,
        MerchantLoginRequest,
        MerchantProfileResponse,
        MerchantSetupRequest,
        MerchantSignupRequest,
    )
    from agent_ready_merchant.services.insforge_auth_service import InsforgeAuthService
    from agent_ready_merchant.services.merchant_auth_service import MerchantAuthService

    def _extract_bearer_token(authorization: str | None) -> str | None:
        if not authorization:
            return None
        scheme, _, token = authorization.partition(" ")
        return token if scheme.lower() == "bearer" and token else None

    @app.post(
        "/api/v1/merchant/auth/signup",
        summary="Merchant Registration & Store Creation",
        tags=["Merchant Portal"],
        response_model=MerchantAuthResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def merchant_signup_endpoint(
        req: MerchantSignupRequest,
        response: Response,
        authorization: str | None = Header(default=None, alias="Authorization"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> MerchantAuthResponse:
        """Registers a new merchant, seeds initial policy bounds, and issues admin session."""
        try:
            bearer_token = _extract_bearer_token(authorization)
            identity = (
                await InsforgeAuthService.verify_access_token(bearer_token, current_settings)
                if bearer_token
                else None
            )
            if identity and identity.email != req.email.lower():
                raise ValueError("Merchant email must match the verified InsForge account.")
            auth_response = await MerchantAuthService.register_merchant(
                db,
                req,
                current_settings,
                auth_user_id=identity.user_id if identity else None,
            )
            _set_admin_session_cookie(response, auth_response.token, current_settings)
            return auth_response.model_copy(update={"token": None})
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.post(
        "/api/v1/merchant/auth/login",
        summary="Merchant Admin Login",
        tags=["Merchant Portal"],
        response_model=MerchantAuthResponse,
        status_code=status.HTTP_200_OK,
    )
    async def merchant_login_endpoint(
        req: MerchantLoginRequest,
        request: Request,
        response: Response,
        authorization: str | None = Header(default=None, alias="Authorization"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> MerchantAuthResponse:
        """Authenticates merchant by slug and issues active bearer session."""
        try:
            bearer_token = _extract_bearer_token(authorization)
            if bearer_token:
                identity = await InsforgeAuthService.verify_access_token(
                    bearer_token, current_settings
                )
                auth_response = await MerchantAuthService.authenticate_insforge_merchant(
                    db, identity.user_id, current_settings
                )
            else:
                cookie_token = request.cookies.get(ADMIN_SESSION_COOKIE)
                if req.admin_token is None and cookie_token:
                    req = req.model_copy(update={"admin_token": cookie_token})
                auth_response = await MerchantAuthService.authenticate_merchant(
                    db, req, current_settings
                )
            _set_admin_session_cookie(response, auth_response.token, current_settings)
            return auth_response.model_copy(update={"token": None})
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    @app.post(
        "/api/v1/merchant/auth/logout",
        summary="Merchant Admin Logout",
        tags=["Merchant Portal"],
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def merchant_logout_endpoint(response: Response) -> Response:
        """Clears the browser-only administrative session cookie."""
        response.delete_cookie(key=ADMIN_SESSION_COOKIE, path="/api/v1/merchant")
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    def _set_admin_session_cookie(
        response: Response, token: str | None, current_settings: Settings
    ) -> None:
        if token is None:
            raise RuntimeError("Cannot establish an empty merchant admin session.")
        response.set_cookie(
            key=ADMIN_SESSION_COOKIE,
            value=token,
            max_age=ADMIN_SESSION_MAX_AGE_SECONDS,
            httponly=True,
            secure=current_settings.ENVIRONMENT == "production",
            samesite="strict",
            path="/api/v1/merchant",
        )

    async def _require_merchant_auth(
        merchant_id: uuid.UUID,
        auth_token: str | None,
        settings: Settings,
        db: AsyncSession,
    ) -> None:
        """Helper to enforce valid admin session token on protected merchant operations."""
        if not auth_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin session token is required (X-Auth-Token header missing).",
            )
        secret = settings.SECRET_KEY.get_secret_value()
        is_valid, tok_m_id, err = MerchantAuthService.verify_admin_token(auth_token, secret)
        if not is_valid or tok_m_id != merchant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=err or "Invalid or expired admin session token.",
            )
        merchant = await db.get(Merchant, merchant_id)
        if merchant is None or merchant.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Merchant account is not active.",
            )

    @app.get(
        "/api/v1/merchant/auth/me",
        summary="Get Authenticated Merchant Profile",
        tags=["Merchant Portal"],
        response_model=MerchantProfileResponse,
    )
    async def merchant_me_endpoint(
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> MerchantProfileResponse:
        """Fetches active merchant profile and policy configuration."""
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)

        try:
            return await MerchantAuthService.get_merchant_profile(db, x_merchant_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/merchant/setup/complete",
        summary="Complete Onboarding & Update Policies",
        tags=["Merchant Portal"],
        response_model=MerchantProfileResponse,
    )
    async def merchant_complete_setup_endpoint(
        req: MerchantSetupRequest,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> MerchantProfileResponse:
        """Updates merchant profile and policy bounds upon setup wizard completion."""
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)

        try:
            return await MerchantAuthService.complete_merchant_setup(db, x_merchant_id, req)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    # =========================================================================
    # Merchant Control Plane Operations Endpoints (Phase 5.2)
    # =========================================================================
    from agent_ready_merchant.schemas.merchant_portal import (
        ApprovalItemResponse,
        AuditLedgerResponse,
        DashboardSummaryResponse,
        InventoryAdjustRequest,
        InventoryItemResponse,
        OrderDetailResponse,
        PaymentAttemptResponse,
        PolicyGovernanceResponse,
        ProductCreateRequest,
        ProductItemResponse,
        QuoteDetailResponse,
        ResolveApprovalPayload,
        UpdatePoliciesPayload,
    )
    from agent_ready_merchant.services.merchant_mutation_idempotency_service import (
        IdempotencyConflictError,
        MerchantMutationIdempotencyService,
    )
    from agent_ready_merchant.services.merchant_portal_service import MerchantPortalService

    @app.get(
        "/api/v1/merchant/dashboard/summary",
        summary="Get Merchant Dashboard Summary KPIs",
        tags=["Merchant Control Plane"],
        response_model=DashboardSummaryResponse,
    )
    async def get_dashboard_summary_endpoint(
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> DashboardSummaryResponse:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        try:
            return await MerchantPortalService.get_dashboard_summary(db, x_merchant_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get(
        "/api/v1/merchant/products",
        summary="List Merchant Products & Inventory Availability",
        tags=["Merchant Control Plane"],
        response_model=list[ProductItemResponse],
    )
    async def list_products_endpoint(
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> list[ProductItemResponse]:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        return await MerchantPortalService.list_products(db, x_merchant_id)

    @app.post(
        "/api/v1/merchant/products",
        summary="Create New Catalog Product",
        tags=["Merchant Control Plane"],
        response_model=ProductItemResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_product_endpoint(
        req: ProductCreateRequest,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> ProductItemResponse:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        try:
            return await MerchantPortalService.create_product(db, x_merchant_id, req)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get(
        "/api/v1/merchant/inventory",
        summary="List Merchant Inventory Stocks",
        tags=["Merchant Control Plane"],
        response_model=list[InventoryItemResponse],
    )
    async def list_inventory_endpoint(
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> list[InventoryItemResponse]:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        return await MerchantPortalService.list_inventory(db, x_merchant_id)

    @app.post(
        "/api/v1/merchant/inventory/adjust",
        summary="Adjust Inventory Quantity",
        tags=["Merchant Control Plane"],
        response_model=InventoryItemResponse,
    )
    async def adjust_inventory_endpoint(
        req: InventoryAdjustRequest,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        x_idempotency_key: str = Header(
            ..., min_length=1, max_length=255, alias="X-Idempotency-Key"
        ),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> InventoryItemResponse:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        try:
            receipt, replay = await MerchantMutationIdempotencyService.claim_or_replay(
                db,
                merchant_id=x_merchant_id,
                operation="inventory.adjust",
                idempotency_key=x_idempotency_key,
                payload=req.model_dump(mode="json"),
            )
            if replay is not None:
                return InventoryItemResponse.model_validate(replay)
            result = await MerchantPortalService.adjust_inventory(db, x_merchant_id, req)
            assert receipt is not None
            await MerchantMutationIdempotencyService.complete(
                db, receipt, result.model_dump(mode="json")
            )
            return result
        except IdempotencyConflictError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get(
        "/api/v1/merchant/quotes",
        summary="List Merchant Price Quotes",
        tags=["Merchant Control Plane"],
        response_model=list[QuoteDetailResponse],
    )
    async def list_quotes_endpoint(
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> list[QuoteDetailResponse]:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        return await MerchantPortalService.list_quotes(db, x_merchant_id)

    @app.get(
        "/api/v1/merchant/orders",
        summary="List Merchant Orders",
        tags=["Merchant Control Plane"],
        response_model=list[OrderDetailResponse],
    )
    async def list_orders_endpoint(
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> list[OrderDetailResponse]:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        return await MerchantPortalService.list_orders(db, x_merchant_id)

    @app.get(
        "/api/v1/merchant/payments",
        summary="List Payment Attempts & Settlement Records",
        tags=["Merchant Control Plane"],
        response_model=list[PaymentAttemptResponse],
    )
    async def list_payments_endpoint(
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> list[PaymentAttemptResponse]:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        return await MerchantPortalService.list_payments(db, x_merchant_id)

    @app.get(
        "/api/v1/merchant/approvals",
        summary="List Human-In-The-Loop Approval Tickets",
        tags=["Merchant Control Plane"],
        response_model=list[ApprovalItemResponse],
    )
    async def list_approvals_endpoint(
        status: str | None = None,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> list[ApprovalItemResponse]:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        return await MerchantPortalService.list_approvals(db, x_merchant_id, status)

    @app.post(
        "/api/v1/merchant/approvals/{approval_id}/resolve",
        summary="Resolve Pending HITL Approval Ticket",
        tags=["Merchant Control Plane"],
        response_model=ApprovalItemResponse,
    )
    async def resolve_approval_endpoint(
        approval_id: uuid.UUID,
        req: ResolveApprovalPayload,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> ApprovalItemResponse:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        try:
            return await MerchantPortalService.resolve_approval(db, x_merchant_id, approval_id, req)
        except ValueError as exc:
            if str(exc) == "Approval ticket has expired.":
                await db.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get(
        "/api/v1/merchant/policies",
        summary="Get Policy Rules and Governance Configuration",
        tags=["Merchant Control Plane"],
        response_model=PolicyGovernanceResponse,
    )
    async def get_policies_endpoint(
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> PolicyGovernanceResponse:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        try:
            return await MerchantPortalService.get_policies(db, x_merchant_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.put(
        "/api/v1/merchant/policies",
        summary="Update Policy Rules Atomically",
        tags=["Merchant Control Plane"],
        response_model=PolicyGovernanceResponse,
    )
    async def update_policies_endpoint(
        req: UpdatePoliciesPayload,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> PolicyGovernanceResponse:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        try:
            return await MerchantPortalService.update_policies(
                db,
                x_merchant_id,
                autonomy_level=req.autonomy_level,
                max_discount_pct=req.max_discount_percentage,
                min_margin_pct=req.min_margin_percentage,
                max_tx_paise=req.max_single_transaction_paise,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get(
        "/api/v1/merchant/audit",
        summary="Get Immutable Audit Event Ledger",
        tags=["Merchant Control Plane"],
        response_model=AuditLedgerResponse,
    )
    async def get_audit_ledger_endpoint(
        limit: int = 50,
        before_created_at: datetime | None = None,
        before_id: uuid.UUID | None = None,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> AuditLedgerResponse:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        if not 1 <= limit <= 100:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Audit pagination must use a limit from 1 to 100.",
            )
        if (before_created_at is None) != (before_id is None):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Audit cursor requires both before_created_at and before_id.",
            )
        return await MerchantPortalService.get_audit_ledger(
            db,
            x_merchant_id,
            limit=limit,
            before_created_at=before_created_at,
            before_id=before_id,
        )

    # =========================================================================
    # Interactive Demo & Sandbox Simulator Endpoints (Phase 5.3)
    # =========================================================================
    from agent_ready_merchant.schemas.demo_simulator import (
        DemoSeedResponse,
        DemoSimulationStepRequest,
        DemoSimulationStepResponse,
    )
    from agent_ready_merchant.services.demo_simulator_service import DemoSimulatorService

    @app.post(
        "/api/v1/merchant/demo/seed",
        summary="Seed Demo Catalog and Baseline Policies",
        tags=["Demo Simulator"],
        response_model=DemoSeedResponse,
    )
    async def demo_seed_endpoint(
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> DemoSeedResponse:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        return await DemoSimulatorService.seed_demo_catalog_and_policies(db, x_merchant_id)

    @app.post(
        "/api/v1/merchant/demo/simulate",
        summary="Execute Interactive Agent Commerce Simulation",
        tags=["Demo Simulator"],
        response_model=DemoSimulationStepResponse,
    )
    async def demo_simulate_endpoint(
        req: DemoSimulationStepRequest,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        x_idempotency_key: str = Header(
            ..., min_length=1, max_length=255, alias="X-Idempotency-Key"
        ),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> DemoSimulationStepResponse:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        try:
            receipt, replay = await MerchantMutationIdempotencyService.claim_or_replay(
                db,
                merchant_id=x_merchant_id,
                operation="demo.simulate",
                idempotency_key=x_idempotency_key,
                payload=req.model_dump(mode="json"),
            )
            if replay is not None:
                return DemoSimulationStepResponse.model_validate(replay)
            result = await DemoSimulatorService.execute_simulation(
                db, x_merchant_id, req, current_settings
            )
            assert receipt is not None
            await MerchantMutationIdempotencyService.complete(
                db, receipt, result.model_dump(mode="json")
            )
            return result
        except IdempotencyConflictError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    # =========================================================================
    # Phase 7 — Merchant Agent & Experiment Framework Endpoints
    # =========================================================================
    import json

    from agent_ready_merchant.schemas.merchant_agent import (
        ExperimentCreateRequest,
        ExperimentResponse,
        ExperimentResultResponse,
        MerchantAgentAnalyzeResponse,
        MerchantObservationSnapshot,
        MerchantProposalResponse,
        MerchantProposalReviewRequest,
    )
    from agent_ready_merchant.services.merchant_agent_service import MerchantAgentService

    @app.get(
        "/api/v1/merchant/agent/snapshot",
        summary="Retrieve Authoritative Merchant Observation Snapshot",
        tags=["Merchant Agent"],
        response_model=MerchantObservationSnapshot,
    )
    async def get_agent_snapshot_endpoint(
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        window_days: int = 30,
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> MerchantObservationSnapshot:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        try:
            return await MerchantAgentService.build_authoritative_observations(
                session=db, merchant_id=x_merchant_id, window_days=window_days
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.post(
        "/api/v1/merchant/agent/analyze",
        summary="Execute Bounded Merchant Agent Optimization Turn",
        tags=["Merchant Agent"],
        response_model=MerchantAgentAnalyzeResponse,
    )
    async def run_agent_analysis_endpoint(
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        x_idempotency_key: str = Header(
            ..., min_length=1, max_length=255, alias="X-Idempotency-Key"
        ),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> MerchantAgentAnalyzeResponse:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        try:
            receipt, replay = await MerchantMutationIdempotencyService.claim_or_replay(
                db,
                merchant_id=x_merchant_id,
                operation="merchant_agent.analyze",
                idempotency_key=x_idempotency_key,
                payload={},
            )
            if replay is not None:
                return MerchantAgentAnalyzeResponse.model_validate(replay)

            # Provider initialization
            llm_instance: BaseLLMProvider | None
            if current_settings.is_testing:
                from agent_ready_merchant.llm.mock_provider import MockLLMProvider

                mock_response_payload = {
                    "diagnoses": [
                        {
                            "pattern": "REPEATED_DELIVERY_QUESTIONS",
                            "summary": "Buyer agents frequently inquire about delivery timeline.",
                            "severity": "MEDIUM",
                            "evidence_references": [
                                "total_buyer_sessions",
                                "quote_conversion_rate",
                            ],
                            "affected_entities": ["discovery_metadata"],
                        }
                    ],
                    "proposals": [
                        {
                            "proposal_type": "EXPOSE_DELIVERY_ETA",
                            "title": "Expose Delivery ETA in Discovery Response",
                            "observation": "Delivery-timeline questions appear in the snapshot.",
                            "evidence": ["total_buyer_sessions", "quote_conversion_rate"],
                            "hypothesis": "Clear ETA will reduce hesitation and boost conversion.",
                            "proposed_change": "Include delivery window in discovery response.",
                            "target_entity": "discovery_metadata",
                            "expected_effect": "Quote conversion rate may improve.",
                            "expected_metric": "quote_conversion_rate",
                            "confidence": 0.85,
                            "estimated_cost_paise": 0,
                        }
                    ],
                }
                llm_instance = MockLLMProvider(responses=[json.dumps(mock_response_payload)])
            elif not current_settings.GROQ_API_KEY.get_secret_value():
                # Missing provider configuration must never turn into fabricated
                # intelligence. The service returns the authoritative snapshot only.
                llm_instance = None
            else:
                from agent_ready_merchant.llm.groq_provider import GroqProvider

                llm_instance = GroqProvider(
                    api_key=current_settings.GROQ_API_KEY.get_secret_value(),
                    model=current_settings.LLM_MODEL_NAME,
                )

            result = await MerchantAgentService.execute_agent_run(
                session=db,
                merchant_id=x_merchant_id,
                llm_provider=llm_instance,
                settings=current_settings,
            )
            assert receipt is not None
            await MerchantMutationIdempotencyService.complete(
                db, receipt, result.model_dump(mode="json")
            )
            return result
        except IdempotencyConflictError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get(
        "/api/v1/merchant/agent/proposals",
        summary="List Merchant Agent Optimization Proposals",
        tags=["Merchant Agent"],
        response_model=list[MerchantProposalResponse],
    )
    async def list_proposals_endpoint(
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        status_filter: str | None = None,
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> list[MerchantProposalResponse]:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        return await MerchantAgentService.list_proposals(
            session=db, merchant_id=x_merchant_id, status=status_filter
        )

    @app.post(
        "/api/v1/merchant/agent/proposals/{proposal_id}/review",
        summary="Review, Approve, or Reject Merchant Proposal",
        tags=["Merchant Agent"],
        response_model=MerchantProposalResponse,
    )
    async def review_proposal_endpoint(
        proposal_id: uuid.UUID,
        req: MerchantProposalReviewRequest,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        x_idempotency_key: str = Header(
            ..., min_length=1, max_length=255, alias="X-Idempotency-Key"
        ),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> MerchantProposalResponse:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        try:
            receipt, replay = await MerchantMutationIdempotencyService.claim_or_replay(
                db,
                merchant_id=x_merchant_id,
                operation="merchant_agent.proposal.review",
                idempotency_key=x_idempotency_key,
                payload={"proposal_id": str(proposal_id), **req.model_dump(mode="json")},
            )
            if replay is not None:
                return MerchantProposalResponse.model_validate(replay)
            result = await MerchantAgentService.review_proposal(
                session=db,
                merchant_id=x_merchant_id,
                proposal_id=proposal_id,
                review_req=req,
                reviewer_id="merchant_admin",
                commit=False,
            )
            assert receipt is not None
            await MerchantMutationIdempotencyService.complete(
                db, receipt, result.model_dump(mode="json")
            )
            return result
        except IdempotencyConflictError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/merchant/experiments",
        summary="Register Structured Merchant Optimization Experiment",
        tags=["Merchant Experiments"],
        response_model=ExperimentResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_experiment_endpoint(
        req: ExperimentCreateRequest,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        x_idempotency_key: str = Header(
            ..., min_length=1, max_length=255, alias="X-Idempotency-Key"
        ),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> ExperimentResponse:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        try:
            receipt, replay = await MerchantMutationIdempotencyService.claim_or_replay(
                db,
                merchant_id=x_merchant_id,
                operation="merchant_experiment.create",
                idempotency_key=x_idempotency_key,
                payload=req.model_dump(mode="json"),
            )
            if replay is not None:
                return ExperimentResponse.model_validate(replay)
            result = await MerchantAgentService.create_experiment(
                session=db,
                merchant_id=x_merchant_id,
                req=req,
                creator_id="merchant_admin",
                commit=False,
            )
            assert receipt is not None
            await MerchantMutationIdempotencyService.complete(
                db, receipt, result.model_dump(mode="json"), response_status=status.HTTP_201_CREATED
            )
            return result
        except IdempotencyConflictError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get(
        "/api/v1/merchant/experiments",
        summary="List Merchant Optimization Experiments",
        tags=["Merchant Experiments"],
        response_model=list[ExperimentResponse],
    )
    async def list_experiments_endpoint(
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> list[ExperimentResponse]:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        return await MerchantAgentService.list_experiments(session=db, merchant_id=x_merchant_id)

    @app.post(
        "/api/v1/merchant/experiments/{experiment_id}/approve",
        summary="Approve Merchant Experiment",
        tags=["Merchant Experiments"],
        response_model=ExperimentResponse,
    )
    async def approve_experiment_endpoint(
        experiment_id: uuid.UUID,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        x_idempotency_key: str = Header(
            ..., min_length=1, max_length=255, alias="X-Idempotency-Key"
        ),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> ExperimentResponse:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        try:
            receipt, replay = await MerchantMutationIdempotencyService.claim_or_replay(
                db,
                merchant_id=x_merchant_id,
                operation="merchant_experiment.approve",
                idempotency_key=x_idempotency_key,
                payload={"experiment_id": str(experiment_id)},
            )
            if replay is not None:
                return ExperimentResponse.model_validate(replay)
            result = await MerchantAgentService.approve_experiment(
                session=db,
                merchant_id=x_merchant_id,
                experiment_id=experiment_id,
                approver_id="merchant_admin",
                commit=False,
            )
            assert receipt is not None
            await MerchantMutationIdempotencyService.complete(
                db, receipt, result.model_dump(mode="json")
            )
            return result
        except IdempotencyConflictError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/merchant/experiments/{experiment_id}/evaluate",
        summary="Evaluate Experiment Deterministically from Observed Metrics",
        tags=["Merchant Experiments"],
        response_model=ExperimentResultResponse,
    )
    async def evaluate_experiment_endpoint(
        experiment_id: uuid.UUID,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        x_idempotency_key: str = Header(
            ..., min_length=1, max_length=255, alias="X-Idempotency-Key"
        ),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> ExperimentResultResponse:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        try:
            receipt, replay = await MerchantMutationIdempotencyService.claim_or_replay(
                db,
                merchant_id=x_merchant_id,
                operation="merchant_experiment.evaluate",
                idempotency_key=x_idempotency_key,
                payload={"experiment_id": str(experiment_id)},
            )
            if replay is not None:
                return ExperimentResultResponse.model_validate(replay)
            result = await MerchantAgentService.evaluate_experiment_results(
                session=db,
                merchant_id=x_merchant_id,
                experiment_id=experiment_id,
                commit=False,
            )
            assert receipt is not None
            await MerchantMutationIdempotencyService.complete(
                db, receipt, result.model_dump(mode="json")
            )
            return result
        except IdempotencyConflictError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    # =========================================================================
    # Phase 8: Controlled Autonomy & Deterministic Rollback Endpoints
    # =========================================================================
    from datetime import timedelta

    from sqlalchemy import func

    from agent_ready_merchant.db.base import utc_now
    from agent_ready_merchant.models.autonomy import MerchantAutonomyAction
    from agent_ready_merchant.schemas.controlled_autonomy import (
        AutonomousExecutionRequest,
        AutonomousExecutionResponse,
        AutonomyActionResponse,
        AutonomyRuleResponse,
        AutonomyRuleUpdateRequest,
        AutonomyStatusResponse,
        KillSwitchResponse,
        KillSwitchUpdateRequest,
        RollbackRequest,
        RollbackResponse,
    )
    from agent_ready_merchant.services.controlled_autonomy_service import (
        AutonomyExecutionError,
        AutonomySecurityError,
        ControlledAutonomyService,
        OptimisticLockError,
        RollbackConflictError,
    )

    @app.get(
        "/api/v1/merchant/autonomy/status",
        summary="Retrieve Autonomy Engine Status, Kill Switch, and Anomaly State",
        tags=["Controlled Autonomy"],
        response_model=AutonomyStatusResponse,
    )
    async def get_autonomy_status_endpoint(
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> AutonomyStatusResponse:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        merchant = (
            await db.execute(select(Merchant).where(Merchant.id == x_merchant_id))
        ).scalar_one_or_none()
        kill_switch = merchant.kill_switch_enabled if merchant else False

        anomaly_state, anomaly_reasons = await ControlledAutonomyService.evaluate_anomaly_state(
            session=db, merchant_id=x_merchant_id
        )
        rules = await ControlledAutonomyService.get_or_create_default_rules(db, x_merchant_id)

        now = utc_now()
        one_hour_ago = now - timedelta(hours=1)
        one_day_ago = now - timedelta(days=1)

        stmt_hour = select(func.count(MerchantAutonomyAction.id)).where(
            MerchantAutonomyAction.merchant_id == x_merchant_id,
            MerchantAutonomyAction.created_at >= one_hour_ago,
            MerchantAutonomyAction.status != "FAILED",
        )
        hourly_count = (await db.execute(stmt_hour)).scalar() or 0

        stmt_day = select(func.count(MerchantAutonomyAction.id)).where(
            MerchantAutonomyAction.merchant_id == x_merchant_id,
            MerchantAutonomyAction.created_at >= one_day_ago,
            MerchantAutonomyAction.status != "FAILED",
        )
        daily_count = (await db.execute(stmt_day)).scalar() or 0

        stmt_actions = (
            select(MerchantAutonomyAction)
            .where(MerchantAutonomyAction.merchant_id == x_merchant_id)
            .order_by(MerchantAutonomyAction.created_at.desc())
            .limit(10)
        )
        recent_actions = list((await db.execute(stmt_actions)).scalars().all())

        return AutonomyStatusResponse(
            merchant_id=x_merchant_id,
            kill_switch_enabled=kill_switch,
            anomaly_state=anomaly_state,
            anomaly_reasons=anomaly_reasons,
            hourly_executions_count=hourly_count,
            daily_executions_count=daily_count,
            recent_actions=[AutonomyActionResponse.model_validate(a) for a in recent_actions],
            rules=[AutonomyRuleResponse.model_validate(r) for r in rules],
        )

    @app.post(
        "/api/v1/merchant/autonomy/kill-switch",
        summary="Toggle Merchant Master Autonomy Kill Switch",
        tags=["Controlled Autonomy"],
        response_model=KillSwitchResponse,
    )
    async def toggle_kill_switch_endpoint(
        request: KillSwitchUpdateRequest,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> KillSwitchResponse:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        try:
            merchant = await ControlledAutonomyService.set_kill_switch(
                session=db,
                merchant_id=x_merchant_id,
                enabled=request.enabled,
                actor_type="MERCHANT_ADMIN",
                actor_id=x_merchant_id,
                reason=request.reason,
            )
            await db.commit()
            return KillSwitchResponse(
                kill_switch_enabled=merchant.kill_switch_enabled,
                merchant_id=merchant.id,
                updated_at=merchant.updated_at,
            )
        except AutonomySecurityError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get(
        "/api/v1/merchant/autonomy/rules",
        summary="List Merchant Autonomy Rules",
        tags=["Controlled Autonomy"],
        response_model=list[AutonomyRuleResponse],
    )
    async def list_autonomy_rules_endpoint(
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> list[AutonomyRuleResponse]:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        rules = await ControlledAutonomyService.get_or_create_default_rules(db, x_merchant_id)
        return [AutonomyRuleResponse.model_validate(r) for r in rules]

    @app.put(
        "/api/v1/merchant/autonomy/rules/{action_type}",
        summary="Update Autonomy Rule Configuration",
        tags=["Controlled Autonomy"],
        response_model=AutonomyRuleResponse,
    )
    async def update_autonomy_rule_endpoint(
        action_type: str,
        request: AutonomyRuleUpdateRequest,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> AutonomyRuleResponse:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        try:
            rule = await ControlledAutonomyService.update_autonomy_rule(
                session=db,
                merchant_id=x_merchant_id,
                action_type=action_type,
                req=request,
                actor_type="MERCHANT_ADMIN",
                actor_id=x_merchant_id,
            )
            await db.commit()
            return AutonomyRuleResponse.model_validate(rule)
        except AutonomySecurityError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
        except OptimisticLockError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get(
        "/api/v1/merchant/autonomy/actions",
        summary="List Autonomous Action Ledger Records",
        tags=["Controlled Autonomy"],
        response_model=list[AutonomyActionResponse],
    )
    async def list_autonomy_actions_endpoint(
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        limit: int = 50,
        offset: int = 0,
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> list[AutonomyActionResponse]:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        stmt = (
            select(MerchantAutonomyAction)
            .where(MerchantAutonomyAction.merchant_id == x_merchant_id)
            .order_by(MerchantAutonomyAction.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        actions = list((await db.execute(stmt)).scalars().all())
        return [AutonomyActionResponse.model_validate(a) for a in actions]

    @app.get(
        "/api/v1/merchant/autonomy/actions/{action_id}",
        summary="Get Single Autonomous Action Record with Snapshot",
        tags=["Controlled Autonomy"],
        response_model=AutonomyActionResponse,
    )
    async def get_autonomy_action_endpoint(
        action_id: uuid.UUID,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> AutonomyActionResponse:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        stmt = select(MerchantAutonomyAction).where(
            MerchantAutonomyAction.id == action_id,
            MerchantAutonomyAction.merchant_id == x_merchant_id,
        )
        action = (await db.execute(stmt)).scalar_one_or_none()
        if not action:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found.")
        return AutonomyActionResponse.model_validate(action)

    @app.post(
        "/api/v1/merchant/autonomy/execute",
        summary="Execute Approved/Auto-Eligible Proposal Autonomously",
        tags=["Controlled Autonomy"],
        response_model=AutonomousExecutionResponse,
    )
    async def execute_autonomous_action_endpoint(
        request: AutonomousExecutionRequest,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        x_idempotency_key: str = Header(
            ..., min_length=1, max_length=255, alias="X-Idempotency-Key"
        ),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> AutonomousExecutionResponse:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        try:
            result = await ControlledAutonomyService.execute_autonomous_action(
                session=db,
                merchant_id=x_merchant_id,
                proposal_id=request.proposal_id,
                expected_target_version=request.expected_target_version,
                idempotency_key=x_idempotency_key,
                actor_id=x_merchant_id,
            )
            await db.commit()
            return AutonomousExecutionResponse.model_validate(result)
        except IdempotencyConflictError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        except OptimisticLockError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        except AutonomyExecutionError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/merchant/autonomy/actions/{action_id}/rollback",
        summary="Deterministically Roll Back an Autonomous Action",
        tags=["Controlled Autonomy"],
        response_model=RollbackResponse,
    )
    async def rollback_autonomous_action_endpoint(
        action_id: uuid.UUID,
        request: RollbackRequest,
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        x_idempotency_key: str = Header(
            ..., min_length=1, max_length=255, alias="X-Idempotency-Key"
        ),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> RollbackResponse:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        try:
            result = await ControlledAutonomyService.rollback_action(
                session=db,
                merchant_id=x_merchant_id,
                action_id=action_id,
                expected_target_version=request.expected_target_version,
                reason=request.reason,
                idempotency_key=x_idempotency_key,
                actor_id=x_merchant_id,
            )
            await db.commit()
            return RollbackResponse.model_validate(result)
        except IdempotencyConflictError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        except (OptimisticLockError, RollbackConflictError) as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        except AutonomyExecutionError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/merchant/experiments/{experiment_id}/stop",
        summary="Stop Running Experiment",
        tags=["Merchant Experiments"],
    )
    async def stop_experiment_endpoint(
        experiment_id: uuid.UUID,
        payload: dict[str, Any],
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        x_idempotency_key: str = Header(
            ..., min_length=1, max_length=255, alias="X-Idempotency-Key"
        ),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> dict[str, Any]:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        reason = str(payload.get("reason", "Human merchant requested stop"))
        require_rollback = bool(payload.get("require_rollback", False))
        try:
            result = await ControlledAutonomyService.stop_experiment(
                session=db,
                merchant_id=x_merchant_id,
                experiment_id=experiment_id,
                reason=reason,
                require_rollback=require_rollback,
                idempotency_key=x_idempotency_key,
                actor_id=x_merchant_id,
            )
            await db.commit()
            return result
        except IdempotencyConflictError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        "/api/v1/merchant/experiments/{experiment_id}/rollback",
        summary="Roll Back Running/Completed Experiment",
        tags=["Merchant Experiments"],
    )
    async def rollback_experiment_endpoint(
        experiment_id: uuid.UUID,
        payload: dict[str, Any],
        x_merchant_id: uuid.UUID = Header(..., alias="X-Merchant-ID"),
        x_auth_token: str | None = Header(default=None, alias="X-Auth-Token"),
        x_idempotency_key: str = Header(
            ..., min_length=1, max_length=255, alias="X-Idempotency-Key"
        ),
        db: AsyncSession = Depends(get_db_session),
        current_settings: Settings = Depends(get_settings),
    ) -> dict[str, Any]:
        await _require_merchant_auth(x_merchant_id, x_auth_token, current_settings, db)
        reason = str(payload.get("reason", "Human merchant requested rollback"))
        try:
            result = await ControlledAutonomyService.stop_experiment(
                session=db,
                merchant_id=x_merchant_id,
                experiment_id=experiment_id,
                reason=reason,
                require_rollback=True,
                idempotency_key=x_idempotency_key,
                actor_id=x_merchant_id,
            )
            await db.commit()
            return result
        except IdempotencyConflictError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return app


app = create_app()
