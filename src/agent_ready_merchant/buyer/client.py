"""Authoritative External AI Buyer Client.

Adheres strictly to Phase 2.2 specifications:
- AI buyer/client -> Gateway -> deterministic authority -> domain service -> Razorpay
- Zero direct DB mutation from client
- Zero direct Razorpay mutation from client
- Pure integer paise arithmetic
- Explicit response and failure states
"""

from __future__ import annotations

import hmac
import json
import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.buyer.schemas import (
    BuyerCommerceState,
    BuyerFailureState,
    BuyerFlowContext,
    BuyerFlowResult,
    BuyerFlowStep,
)
from agent_ready_merchant.config import get_settings
from agent_ready_merchant.gateway.canonical import CanonicalCommerceGateway
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
    QuoteItemRequest,
    RequestCheckoutRequest,
    RequestCheckoutResponse,
    ShippingAddressGateway,
    TerminateSessionRequest,
    TerminateSessionResponse,
)
from agent_ready_merchant.services.payment_service import PaymentService
from agent_ready_merchant.tools.base import GatewayContext

logger = logging.getLogger("agent_ready_merchant.buyer.client")


class AIBuyerClient:
    """Independent AI Buyer coordinating end-to-end commerce via CanonicalCommerceGateway."""

    def __init__(
        self,
        merchant_id: uuid.UUID,
        buyer_agent_identifier: str = "ai_buyer_agent_v1",
        gateway: CanonicalCommerceGateway | None = None,
        capabilities: set[str] | None = None,
        autonomy_level: int | None = None,
    ) -> None:
        self.merchant_id = merchant_id
        self.buyer_agent_identifier = buyer_agent_identifier
        self.gateway = gateway or CanonicalCommerceGateway()
        self.autonomy_level = autonomy_level
        self.capabilities = (
            capabilities
            if capabilities is not None
            else {
                "buyer:discover",
                "buyer:read",
                "buyer:quote",
                "buyer:negotiate",
                "buyer:checkout",
                "buyer:payment_status",
            }
        )
        self.context = BuyerFlowContext(
            merchant_id=merchant_id,
            buyer_agent_identifier=buyer_agent_identifier,
        )

    def _get_gateway_context(self) -> GatewayContext:
        settings = get_settings()
        session_id = self.context.session_id or uuid.uuid4()
        return GatewayContext(
            merchant_id=self.merchant_id,
            session_id=session_id,
            capabilities=self.capabilities,
            autonomy_level=self.autonomy_level
            if self.autonomy_level is not None
            else settings.DEFAULT_MERCHANT_AUTONOMY_LEVEL,
            max_discount_percentage=settings.DEFAULT_MAX_DISCOUNT_PERCENTAGE,
            min_margin_percentage=settings.DEFAULT_MIN_MARGIN_PERCENTAGE,
            max_single_transaction_paise=settings.MAX_SINGLE_TRANSACTION_PAISE,
            auth_token=self.context.auth_token_raw,
        )

    def _record_step(
        self,
        step_name: str,
        status: str,
        state: str,
        details: dict[str, Any],
    ) -> None:
        step = BuyerFlowStep(
            step_name=step_name,
            status=status,
            state_after_step=state,
            details=details,
        )
        self.context.history.append(step)

    # -------------------------------------------------------------------------
    # 1. Session Lifecycle
    # -------------------------------------------------------------------------
    async def initialize_session(
        self,
        session: AsyncSession,
        duration_minutes: int = 60,
    ) -> GatewayResponseEnvelope[InitializeSessionResponse]:
        """Initializes a new buyer agent session through the gateway."""
        raw_token = f"tok_{uuid.uuid4().hex}"
        req = InitializeSessionRequest(
            buyer_agent_identifier=self.buyer_agent_identifier,
            auth_token_raw=raw_token,
            duration_minutes=duration_minutes,
            requested_capabilities=list(self.capabilities),
        )
        res = await self.gateway.initialize_session(session, req, self.merchant_id)
        if res.status == "SUCCESS" and res.data:
            self.context.session_id = res.data.session_id
            self.context.auth_token_raw = raw_token
            self._record_step(
                "initialize_session",
                "SUCCESS",
                "SESSION_ACTIVE",
                {"session_id": str(res.data.session_id)},
            )
        else:
            err_code = res.error.code if res.error else "SESSION_INIT_FAILED"
            self.context.current_failure = BuyerFailureState.AUTHORIZATION_REQUIRED
            self._record_step(
                "initialize_session",
                "REJECTED",
                "AUTHORIZATION_REQUIRED",
                {"error": err_code},
            )
        return res

    async def terminate_session(
        self,
        session: AsyncSession,
        reason: str = "Buyer completed session",
    ) -> GatewayResponseEnvelope[TerminateSessionResponse]:
        """Explicitly closes the active buyer session."""
        if not self.context.session_id:
            return self.gateway._rejected_envelope(
                "terminate_session", "NO_ACTIVE_SESSION", "No active session to terminate"
            )
        req = TerminateSessionRequest(session_id=self.context.session_id, reason=reason)
        res = await self.gateway.terminate_session(session, req, self._get_gateway_context())
        if res.status == "SUCCESS":
            self._record_step(
                "terminate_session",
                "SUCCESS",
                "TERMINATED",
                {"session_id": str(self.context.session_id)},
            )
        return res

    # -------------------------------------------------------------------------
    # 2. Discovery & Product Selection
    # -------------------------------------------------------------------------
    async def discover_products(
        self,
        session: AsyncSession,
        query: str | None = None,
        category: str | None = None,
        min_price_paise: int | None = None,
        max_price_paise: int | None = None,
        limit: int = 10,
    ) -> GatewayResponseEnvelope[DiscoverProductsResponse]:
        """Discovers catalog items matching criteria."""
        req = DiscoverProductsRequest(
            query=query,
            category=category,
            min_price_paise=min_price_paise,
            max_price_paise=max_price_paise,
            limit=limit,
        )
        res = await self.gateway.discover_products(session, req, self._get_gateway_context())
        if res.status == "SUCCESS" and res.data:
            self.context.current_state = BuyerCommerceState.DISCOVERED
            self._record_step(
                "discover_products",
                "SUCCESS",
                BuyerCommerceState.DISCOVERED.value,
                {"matched": res.data.total_matched},
            )
        else:
            self._record_step(
                "discover_products",
                "REJECTED",
                "DISCOVERY_FAILED",
                {"error": res.error.code if res.error else "UNKNOWN"},
            )
        return res

    async def get_product(
        self,
        session: AsyncSession,
        sku: str,
    ) -> GatewayResponseEnvelope[GetProductResponse]:
        """Fetches product details and variants."""
        req = GetProductRequest(sku=sku)
        res = await self.gateway.get_product(session, req, self._get_gateway_context())
        if res.status == "SUCCESS" and res.data:
            self.context.selected_sku = res.data.sku
            if res.data.variants:
                self.context.selected_variant_sku = res.data.variants[0].sku
            self.context.current_state = BuyerCommerceState.PRODUCT_SELECTED
            self._record_step(
                "get_product",
                "SUCCESS",
                BuyerCommerceState.PRODUCT_SELECTED.value,
                {"sku": res.data.sku, "title": res.data.title},
            )
        else:
            self._record_step(
                "get_product",
                "REJECTED",
                "PRODUCT_NOT_FOUND",
                {"error": res.error.code if res.error else "UNKNOWN"},
            )
        return res

    # -------------------------------------------------------------------------
    # 3. Real-Time Inventory & Shipping Calculation
    # -------------------------------------------------------------------------
    async def check_inventory(
        self,
        session: AsyncSession,
        sku: str,
        requested_quantity: int = 1,
    ) -> GatewayResponseEnvelope[CheckInventoryResponse]:
        """Validates real-time inventory levels."""
        req = CheckInventoryRequest(sku=sku, requested_quantity=requested_quantity)
        res = await self.gateway.check_inventory(session, req, self._get_gateway_context())
        if res.status == "SUCCESS" and res.data:
            if not res.data.can_fulfill:
                self.context.current_failure = BuyerFailureState.INVENTORY_CHANGED
            self._record_step(
                "check_inventory",
                "SUCCESS",
                "INVENTORY_CHECKED",
                {"can_fulfill": res.data.can_fulfill, "available": res.data.available_quantity},
            )
        return res

    async def calculate_shipping(
        self,
        session: AsyncSession,
        destination_postal_code: str,
        destination_country: str = "IN",
        subtotal_paise: int | None = None,
        quote_id: uuid.UUID | None = None,
    ) -> GatewayResponseEnvelope[CalculateShippingResponse]:
        """Calculates logistics and shipping fees."""
        req = CalculateShippingRequest(
            destination_postal_code=destination_postal_code,
            destination_country=destination_country,
            subtotal_paise=subtotal_paise,
            quote_id=quote_id,
        )
        res = await self.gateway.calculate_shipping(session, req, self._get_gateway_context())
        if res.status == "SUCCESS" and res.data:
            self._record_step(
                "calculate_shipping",
                "SUCCESS",
                "SHIPPING_CALCULATED",
                {
                    "fee_paise": res.data.shipping_fee_paise,
                    "free": res.data.qualifies_for_free_shipping,
                },
            )
        return res

    # -------------------------------------------------------------------------
    # 4. Quote Creation, Negotiation & Acceptance
    # -------------------------------------------------------------------------
    async def get_quote(
        self,
        session: AsyncSession,
        items: list[QuoteItemRequest],
        shipping_country: str = "IN",
    ) -> GatewayResponseEnvelope[GetQuoteResponse]:
        """Generates a binding, time-limited price quote."""
        if not self.context.session_id:
            await self.initialize_session(session)

        req = GetQuoteRequest(
            session_id=self.context.session_id,  # type: ignore[arg-type]
            items=items,
            shipping_country=shipping_country,
        )
        res = await self.gateway.get_quote(session, req, self._get_gateway_context())
        if res.status == "SUCCESS" and res.data:
            self.context.active_quote_id = res.data.quote_id
            self.context.active_quote_total_paise = res.data.total_paise
            self.context.current_state = BuyerCommerceState.QUOTED
            self._record_step(
                "get_quote",
                "SUCCESS",
                BuyerCommerceState.QUOTED.value,
                {"quote_id": str(res.data.quote_id), "total_paise": res.data.total_paise},
            )
        else:
            err_code = res.error.code if res.error else "QUOTE_FAILED"
            if err_code == "INSUFFICIENT_STOCK":
                self.context.current_failure = BuyerFailureState.INVENTORY_CHANGED
            elif err_code == "FLOOR_PRICE_BREACH":
                self.context.current_failure = BuyerFailureState.POLICY_REJECTED
            self._record_step(
                "get_quote",
                "REJECTED",
                "QUOTE_FAILED",
                {"error": err_code},
            )
        return res

    async def negotiate_quote(
        self,
        session: AsyncSession,
        quote_id: uuid.UUID,
        proposed_total_paise: int,
        rationale: str | None = None,
    ) -> GatewayResponseEnvelope[NegotiateQuoteGatewayResponse]:
        """Submits a bounded price counter-offer."""
        req = NegotiateQuoteGatewayRequest(
            quote_id=quote_id,
            proposed_total_paise=proposed_total_paise,
            rationale=rationale,
        )
        res = await self.gateway.negotiate_quote(session, req, self._get_gateway_context())
        if res.status == "SUCCESS" and res.data:
            if res.data.verdict == "ALLOW":
                self.context.active_quote_total_paise = res.data.total_paise
                self.context.current_state = BuyerCommerceState.QUOTED
                self._record_step(
                    "negotiate_quote",
                    "SUCCESS",
                    BuyerCommerceState.QUOTED.value,
                    {"verdict": "ALLOW", "total_paise": res.data.total_paise},
                )
            elif res.data.verdict == "ESCALATE_APPROVAL":
                self.context.current_state = BuyerCommerceState.NEGOTIATION_PENDING
                self._record_step(
                    "negotiate_quote",
                    "SUCCESS",
                    BuyerCommerceState.NEGOTIATION_PENDING.value,
                    {"verdict": "ESCALATE_APPROVAL", "reason": res.data.reason},
                )
        else:
            err_code = res.error.code if res.error else "POLICY_REJECTED"
            self.context.current_failure = BuyerFailureState.POLICY_REJECTED
            self._record_step(
                "negotiate_quote",
                "REJECTED",
                BuyerFailureState.POLICY_REJECTED.value,
                {"error": err_code},
            )
        return res

    async def accept_quote(
        self,
        session: AsyncSession,
        quote_id: uuid.UUID,
    ) -> GatewayResponseEnvelope[AcceptQuoteGatewayResponse]:
        """Accepts a proposed quote to lock terms for checkout."""
        req = AcceptQuoteGatewayRequest(quote_id=quote_id)
        res = await self.gateway.accept_quote(session, req, self._get_gateway_context())
        if res.status == "SUCCESS" and res.data:
            self.context.current_state = BuyerCommerceState.OFFER_ACCEPTED
            self._record_step(
                "accept_quote",
                "SUCCESS",
                BuyerCommerceState.OFFER_ACCEPTED.value,
                {"quote_id": str(res.data.quote_id), "status": res.data.status},
            )
        else:
            err_code = res.error.code if res.error else "ACCEPT_FAILED"
            if err_code == "QUOTE_EXPIRED":
                self.context.current_failure = BuyerFailureState.QUOTE_EXPIRED
            self._record_step(
                "accept_quote",
                "REJECTED",
                "QUOTE_ACCEPTANCE_FAILED",
                {"error": err_code},
            )
        return res

    # -------------------------------------------------------------------------
    # 5. Order Creation & Checkout
    # -------------------------------------------------------------------------
    async def create_order(
        self,
        session: AsyncSession,
        quote_id: uuid.UUID,
        buyer_email: str,
        shipping_address: ShippingAddressGateway,
        idempotency_key: str | None = None,
    ) -> GatewayResponseEnvelope[CreateOrderGatewayResponse]:
        """Converts an accepted quote into a locked Order."""
        idem_key = idempotency_key or f"ord_{quote_id}_{uuid.uuid4().hex[:8]}"
        req = CreateOrderGatewayRequest(
            quote_id=quote_id,
            buyer_email=buyer_email,
            shipping_address=shipping_address,
            idempotency_key=idem_key,
        )
        ctx = self._get_gateway_context()
        ctx.idempotency_key = idem_key
        res = await self.gateway.create_order(session, req, ctx)
        if res.status == "SUCCESS" and res.data:
            self.context.active_order_id = res.data.order_id
            self.context.rzp_order_id = res.data.rzp_order_id
            self.context.current_state = BuyerCommerceState.ORDER_CREATED
            self._record_step(
                "create_order",
                "SUCCESS",
                BuyerCommerceState.ORDER_CREATED.value,
                {"order_id": str(res.data.order_id), "rzp_order_id": res.data.rzp_order_id},
            )
        else:
            err_code = res.error.code if res.error else "ORDER_CREATION_FAILED"
            if err_code == "INSUFFICIENT_STOCK":
                self.context.current_failure = BuyerFailureState.INVENTORY_CHANGED
            elif err_code == "QUOTE_EXPIRED":
                self.context.current_failure = BuyerFailureState.QUOTE_EXPIRED
            self._record_step(
                "create_order",
                "REJECTED",
                "ORDER_CREATION_FAILED",
                {"error": err_code},
            )
        return res

    async def request_checkout(
        self,
        session: AsyncSession,
        order_id: uuid.UUID | None = None,
        quote_id: uuid.UUID | None = None,
        buyer_email: str | None = None,
        shipping_address: ShippingAddressGateway | None = None,
        idempotency_key: str | None = None,
    ) -> GatewayResponseEnvelope[RequestCheckoutResponse]:
        """Requests checkout session parameters and payment metadata."""
        target_order_id = order_id or self.context.active_order_id
        idem_key = idempotency_key or f"chk_{target_order_id or quote_id}_{uuid.uuid4().hex[:8]}"
        req = RequestCheckoutRequest(
            order_id=target_order_id,
            quote_id=quote_id,
            buyer_email=buyer_email,
            shipping_address=shipping_address,
            idempotency_key=idem_key,
        )
        ctx = self._get_gateway_context()
        ctx.idempotency_key = idem_key
        res = await self.gateway.request_checkout(session, req, ctx)
        if res.status == "SUCCESS" and res.data:
            self.context.active_order_id = res.data.order_id
            self.context.rzp_order_id = res.data.rzp_order_id
            self.context.current_state = BuyerCommerceState.PAYMENT_PENDING
            self._record_step(
                "request_checkout",
                "SUCCESS",
                BuyerCommerceState.PAYMENT_PENDING.value,
                {"order_id": str(res.data.order_id), "rzp_order_id": res.data.rzp_order_id},
            )
        return res

    # -------------------------------------------------------------------------
    # 6. Payment Authorization (Simulated Test Mode) & Webhook Verification
    # -------------------------------------------------------------------------
    async def authorize_test_payment(
        self,
        session: AsyncSession,
        order_id: uuid.UUID,
        rzp_payment_id: str | None = None,
        payment_method: str = "upi",
    ) -> dict[str, Any]:
        """Simulates Razorpay payment authorization and verified webhook processing.

        Adheres strictly to invariant: AI buyer cannot mutate DB or payment state directly;
        it must deliver an authentic HMAC signed webhook to PaymentService.
        """
        settings = get_settings()
        if not settings.is_testing and not getattr(
            settings, "ALLOW_TEST_PAYMENT_SIMULATION", False
        ):
            raise PermissionError(
                "Simulated test payment authorization is only permitted in testing mode."
            )
        status_res = await self.get_payment_status(session, order_id)
        if not status_res.data:
            raise ValueError(f"Cannot authorize payment: order {order_id} not found")

        rzp_order_id = status_res.data.rzp_order_id or f"order_{uuid.uuid4().hex[:14]}"
        pay_id = rzp_payment_id or f"pay_{uuid.uuid4().hex[:14]}"
        amount_paise = status_res.data.amount_paise

        webhook_payload_dict = {
            "event": "payment.captured",
            "entity": "event",
            "payload": {
                "payment": {
                    "entity": {
                        "id": pay_id,
                        "order_id": rzp_order_id,
                        "amount": amount_paise,
                        "currency": "INR",
                        "status": "captured",
                        "method": payment_method,
                    }
                },
                "order": {
                    "entity": {
                        "id": rzp_order_id,
                        "amount": amount_paise,
                        "status": "paid",
                    }
                },
            },
        }
        webhook_body = json.dumps(webhook_payload_dict, separators=(",", ":"))
        secret_str = (
            settings.RAZORPAY_WEBHOOK_SECRET.get_secret_value()
            if hasattr(settings.RAZORPAY_WEBHOOK_SECRET, "get_secret_value")
            else str(settings.RAZORPAY_WEBHOOK_SECRET)
        )
        signature = hmac.new(
            secret_str.encode("utf-8"),
            webhook_body.encode("utf-8"),
            "sha256",
        ).hexdigest()

        # Submit to PaymentService webhook receiver
        reco_result = await PaymentService.process_payment_webhook(
            session=session,
            raw_body=webhook_body.encode("utf-8"),
            signature_header=signature,
            webhook_secret=secret_str,
        )
        reco_status = reco_result.get("status") if isinstance(reco_result, dict) else None
        if reco_status in {"PROCESSED", "DUPLICATE_IGNORED"}:
            self.context.current_state = BuyerCommerceState.PAYMENT_SUCCEEDED
            self._record_step(
                "authorize_test_payment",
                "SUCCESS",
                BuyerCommerceState.PAYMENT_SUCCEEDED.value,
                {"payment_id": pay_id, "reco_status": reco_status},
            )
        else:
            self.context.current_failure = BuyerFailureState.PAYMENT_FAILED
            self._record_step(
                "authorize_test_payment",
                "FAILED",
                BuyerFailureState.PAYMENT_FAILED.value,
                {"payment_id": pay_id, "reco_result": reco_result},
            )
        return reco_result

    # -------------------------------------------------------------------------
    # 7. Payment Status & Order Status Lookups
    # -------------------------------------------------------------------------
    async def get_payment_status(
        self,
        session: AsyncSession,
        order_id: uuid.UUID,
    ) -> GatewayResponseEnvelope[GetPaymentStatusResponse]:
        """Queries authoritative settlement and payment status."""
        req = GetPaymentStatusRequest(order_id=order_id)
        res = await self.gateway.get_payment_status(session, req, self._get_gateway_context())
        if res.status == "SUCCESS" and res.data:
            if res.data.is_paid:
                self.context.current_state = BuyerCommerceState.PAYMENT_SUCCEEDED
            self._record_step(
                "get_payment_status",
                "SUCCESS",
                "PAYMENT_STATUS_CHECKED",
                {"is_paid": res.data.is_paid, "status": res.data.order_status},
            )
        return res

    async def get_order_status(
        self,
        session: AsyncSession,
        order_id: uuid.UUID,
    ) -> GatewayResponseEnvelope[GetOrderStatusResponse]:
        """Queries authoritative final order and fulfillment state."""
        req = GetOrderStatusRequest(order_id=order_id)
        res = await self.gateway.get_order_status(session, req, self._get_gateway_context())
        if res.status == "SUCCESS" and res.data:
            if res.data.is_settled:
                self.context.current_state = BuyerCommerceState.COMPLETED
            self._record_step(
                "get_order_status",
                "SUCCESS",
                BuyerCommerceState.COMPLETED.value if res.data.is_settled else res.data.status,
                {"status": res.data.status, "is_settled": res.data.is_settled},
            )
        return res

    # -------------------------------------------------------------------------
    # 8. Full End-to-End Automated Commerce Flow
    # -------------------------------------------------------------------------
    async def execute_full_commerce_flow(
        self,
        session: AsyncSession,
        query: str = "Shoes",
        target_sku: str = "RUN-SHOE-PRO",
        target_variant_sku: str = "RUN-SHOE-PRO-UK9",
        quantity: int = 1,
        buyer_email: str = "buyer.ai@example.com",
        shipping_address: ShippingAddressGateway | None = None,
        negotiate_proposed_paise: int | None = None,
    ) -> BuyerFlowResult:
        """Executes the complete autonomous buyer flow from discovery to settlement."""
        if shipping_address is None:
            shipping_address = ShippingAddressGateway(
                full_name="AI Buyer Representative",
                address_line1="123 Autonomous Lane",
                city="Bengaluru",
                postal_code="560001",
                country="IN",
            )

        # 1. Initialize Session
        init_res = await self.initialize_session(session)
        if init_res.status != "SUCCESS":
            return self._build_result(False, "SESSION_INITIALIZATION_FAILED", init_res.error)

        # 2. Discover Catalog
        disc_res = await self.discover_products(session, query=query)
        if disc_res.status != "SUCCESS":
            return self._build_result(False, "DISCOVERY_FAILED", disc_res.error)

        # 3. Inspect Product
        prod_res = await self.get_product(session, sku=target_sku)
        if prod_res.status != "SUCCESS":
            return self._build_result(False, "PRODUCT_SELECTION_FAILED", prod_res.error)

        # 4. Check Inventory
        inv_res = await self.check_inventory(
            session, sku=target_variant_sku, requested_quantity=quantity
        )
        if inv_res.status != "SUCCESS" or (inv_res.data and not inv_res.data.can_fulfill):
            return self._build_result(False, "INVENTORY_CHANGED", inv_res.error)

        # 5. Calculate Shipping
        ship_res = await self.calculate_shipping(
            session,
            destination_postal_code=shipping_address.postal_code,
            destination_country=shipping_address.country,
        )
        if ship_res.status != "SUCCESS":
            return self._build_result(False, "SHIPPING_UNAVAILABLE", ship_res.error)

        # 6. Request Quote
        quote_items = [QuoteItemRequest(sku=target_variant_sku, quantity=quantity)]
        quote_res = await self.get_quote(session, items=quote_items)
        if quote_res.status != "SUCCESS" or not quote_res.data:
            return self._build_result(False, "QUOTE_FAILED", quote_res.error)

        quote_id = quote_res.data.quote_id

        # 7. Optional Bounded Negotiation
        if negotiate_proposed_paise is not None:
            neg_res = await self.negotiate_quote(
                session,
                quote_id=quote_id,
                proposed_total_paise=negotiate_proposed_paise,
                rationale="Autonomous bulk discount inquiry",
            )
            if neg_res.status != "SUCCESS":
                return self._build_result(False, "POLICY_REJECTED", neg_res.error)
            if neg_res.data and neg_res.data.verdict == "ESCALATE_APPROVAL":
                return self._build_result(False, "NEGOTIATION_PENDING", None, quote_id=quote_id)

        # 8. Accept Quote
        accept_res = await self.accept_quote(session, quote_id=quote_id)
        if accept_res.status != "SUCCESS":
            return self._build_result(False, "OFFER_ACCEPTANCE_FAILED", accept_res.error)

        # 9. Create Order & Checkout
        order_res = await self.create_order(
            session,
            quote_id=quote_id,
            buyer_email=buyer_email,
            shipping_address=shipping_address,
        )
        if order_res.status != "SUCCESS" or not order_res.data:
            return self._build_result(False, "ORDER_CREATION_FAILED", order_res.error)

        order_id = order_res.data.order_id

        # 10. Checkout Request (Payment Metadata)
        await self.request_checkout(session, order_id=order_id)

        # 11. Authorize Razorpay Test Payment via Webhook
        await self.authorize_test_payment(session, order_id=order_id)

        # 12. Poll Payment Status
        pay_stat_res = await self.get_payment_status(session, order_id=order_id)
        if pay_stat_res.status != "SUCCESS" or (
            pay_stat_res.data and not pay_stat_res.data.is_paid
        ):
            return self._build_result(False, "PAYMENT_FAILED", pay_stat_res.error)

        # 13. Final Order Status
        ord_stat_res = await self.get_order_status(session, order_id=order_id)
        if ord_stat_res.status != "SUCCESS":
            return self._build_result(False, "ORDER_LOOKUP_FAILED", ord_stat_res.error)

        # 14. Terminate Session
        await self.terminate_session(session, reason="Flow completed successfully")

        return BuyerFlowResult(
            is_success=True,
            final_state=BuyerCommerceState.COMPLETED.value,
            order_id=order_id,
            quote_id=quote_id,
            amount_paise=ord_stat_res.data.amount_paise if ord_stat_res.data else None,
            currency="INR",
            payment_status=ord_stat_res.data.status if ord_stat_res.data else "PAID",
            step_count=len(self.context.history),
            history=self.context.history,
        )

    def _build_result(
        self,
        is_success: bool,
        final_state: str,
        error: Any = None,
        quote_id: uuid.UUID | None = None,
        order_id: uuid.UUID | None = None,
    ) -> BuyerFlowResult:
        err_code = error.code if error and hasattr(error, "code") else None
        err_msg = error.message if error and hasattr(error, "message") else None
        return BuyerFlowResult(
            is_success=is_success,
            final_state=final_state,
            quote_id=quote_id or self.context.active_quote_id,
            order_id=order_id or self.context.active_order_id,
            amount_paise=self.context.active_quote_total_paise if is_success else None,
            currency="INR",
            error_code=err_code,
            error_message=err_msg,
            step_count=len(self.context.history),
            history=self.context.history,
        )
