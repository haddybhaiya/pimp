"""External AI buyer client communicating via the protocol adapter interface.

Adheres strictly to Phase 2.3 specifications:
- AI Buyer Client -> Protocol Adapter -> Canonical Commerce Gateway -> Domain Authority
- Zero direct database access
- Zero direct Razorpay API calls
- Explicit retry safety: retries only safe/idempotent requests;
  never blindly retries financial mutations
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
from agent_ready_merchant.gateway.constants import COMMERCE_PROTOCOL_VERSION
from agent_ready_merchant.gateway.schemas import (
    QuoteItemRequest,
    ShippingAddressGateway,
)
from agent_ready_merchant.protocols.acp import AgentCommerceProtocolAdapter
from agent_ready_merchant.protocols.base import (
    BaseProtocolAdapter,
    ProtocolRequestMessage,
    ProtocolResponseMessage,
)
from agent_ready_merchant.services.payment_service import PaymentService
from agent_ready_merchant.tools.base import GatewayContext

logger = logging.getLogger("agent_ready_merchant.protocols.client")


class AgentProtocolClient:
    """Independent AI buyer client communicating with merchants strictly via protocol adapter."""

    SAFE_IDEMPOTENT_ACTIONS: set[str] = {
        "discover_products",
        "get_product",
        "check_inventory",
        "calculate_shipping",
        "get_payment_status",
        "get_order_status",
    }

    def __init__(
        self,
        merchant_id: uuid.UUID,
        buyer_agent_identifier: str = "acp_autonomous_buyer",
        adapter: BaseProtocolAdapter | None = None,
        gateway: CanonicalCommerceGateway | None = None,
        capabilities: set[str] | None = None,
        autonomy_level: int | None = None,
    ) -> None:
        self.merchant_id = merchant_id
        self.buyer_agent_identifier = buyer_agent_identifier
        self.adapter = adapter or AgentCommerceProtocolAdapter()
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
                "buyer:orders",
            }
        )
        self.context = BuyerFlowContext(
            merchant_id=merchant_id,
            buyer_agent_identifier=buyer_agent_identifier,
        )

    def _get_gateway_context(
        self, request_id: uuid.UUID | None = None, idempotency_key: str | None = None
    ) -> GatewayContext:
        settings = get_settings()
        stable_session_id = self.context.session_id or uuid.UUID(
            "00000000-0000-0000-0000-000000000000"
        )
        return GatewayContext(
            merchant_id=self.merchant_id,
            session_id=stable_session_id,
            capabilities=self.capabilities,
            autonomy_level=self.autonomy_level
            if self.autonomy_level is not None
            else settings.DEFAULT_MERCHANT_AUTONOMY_LEVEL,
            max_discount_percentage=settings.DEFAULT_MAX_DISCOUNT_PERCENTAGE,
            min_margin_percentage=settings.DEFAULT_MIN_MARGIN_PERCENTAGE,
            max_single_transaction_paise=settings.MAX_SINGLE_TRANSACTION_PAISE,
            request_id=request_id or uuid.uuid4(),
            idempotency_key=idempotency_key,
            schema_version=COMMERCE_PROTOCOL_VERSION,
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

    async def send_protocol_message(
        self,
        session: AsyncSession,
        action: str,
        params: dict[str, Any],
        idempotency_key: str | None = None,
        max_retries: int = 2,
    ) -> ProtocolResponseMessage:
        """Sends a wire message through the protocol adapter to the commerce gateway.

        Enforces safe retry policy: only safe read actions or idempotent mutations are retried.
        """
        request_id = uuid.uuid4()
        req_msg = ProtocolRequestMessage(
            protocol=self.adapter.protocol_name,
            version=COMMERCE_PROTOCOL_VERSION,
            request_id=request_id,
            action=action,
            params=params,
            idempotency_key=idempotency_key,
        )

        try:
            capability, canonical_payload = self.adapter.to_canonical_request(req_msg)
        except Exception as exc:
            return self.adapter.format_error_response(
                error_code="INVALID_PROTOCOL_MESSAGE",
                message=str(exc),
                request_id=request_id,
                action=action,
                retryable=False,
            )

        is_safe_to_retry = action in self.SAFE_IDEMPOTENT_ACTIONS or idempotency_key is not None
        attempts_allowed = max_retries if is_safe_to_retry else 1

        last_resp: ProtocolResponseMessage | None = None
        for attempt in range(1, attempts_allowed + 1):
            try:
                gw_context = self._get_gateway_context(
                    request_id=request_id, idempotency_key=idempotency_key
                )
                envelope = await self.gateway.execute_capability(
                    session=session,
                    capability_name=capability,
                    payload=canonical_payload,
                    context=gw_context,
                )
                resp_msg = self.adapter.from_canonical_envelope(
                    capability=capability,
                    envelope=envelope,
                    protocol_req=req_msg,
                )
                last_resp = resp_msg

                # If successful or terminal rejection, return immediately
                if resp_msg.status == "SUCCESS" or (
                    resp_msg.error and not resp_msg.error.retryable
                ):
                    return resp_msg

                # If retryable error and attempts left, retry
                if attempt < attempts_allowed:
                    logger.info(
                        "Retrying safe action '%s' (attempt %d/%d)",
                        action,
                        attempt + 1,
                        attempts_allowed,
                    )
                    continue

                return resp_msg

            except Exception as exc:
                logger.error("Exception sending protocol message '%s': %s", action, exc)
                last_resp = self.adapter.format_error_response(
                    error_code="INTERNAL_GATEWAY_ERROR",
                    message=str(exc),
                    request_id=request_id,
                    action=action,
                    retryable=False,
                )
                if not is_safe_to_retry:
                    break

        return last_resp or self.adapter.format_error_response(
            error_code="INTERNAL_GATEWAY_ERROR",
            message="No response received",
            request_id=request_id,
            action=action,
            retryable=False,
        )

    # -------------------------------------------------------------------------
    # High-Level Protocol Operations
    # -------------------------------------------------------------------------
    async def initialize_session(
        self,
        session: AsyncSession,
        duration_minutes: int = 60,
        auth_token_raw: str | None = None,
        idempotency_key: str | None = None,
    ) -> ProtocolResponseMessage:
        """Initializes a protocol session with the merchant."""
        token_to_send = auth_token_raw or "default_buyer_session_auth_token"
        params = {
            "buyer_agent_identifier": self.buyer_agent_identifier,
            "duration_minutes": duration_minutes,
            "auth_token_raw": token_to_send,
            "requested_capabilities": list(self.capabilities),
        }
        res = await self.send_protocol_message(
            session, "initialize_session", params, idempotency_key=idempotency_key
        )
        if res.status == "SUCCESS" and res.result:
            self.context.session_id = uuid.UUID(res.result["session_id"])
            self.context.current_state = BuyerCommerceState.DISCOVERED
        return res

    async def discover_products(
        self,
        session: AsyncSession,
        query: str | None = None,
        category: str | None = None,
        limit: int = 5,
    ) -> ProtocolResponseMessage:
        """Searches products via protocol."""
        params: dict[str, Any] = {"limit": limit}
        if query:
            params["query"] = query
        if category:
            params["category"] = category
        return await self.send_protocol_message(session, "discover_products", params)

    async def get_product(
        self,
        session: AsyncSession,
        sku: str,
    ) -> ProtocolResponseMessage:
        """Retrieves product specifications and variants."""
        res = await self.send_protocol_message(session, "get_product", {"sku": sku})
        if res.status == "SUCCESS":
            self.context.current_state = BuyerCommerceState.PRODUCT_SELECTED
        return res

    async def check_inventory(
        self,
        session: AsyncSession,
        sku: str,
        quantity: int = 1,
    ) -> ProtocolResponseMessage:
        """Checks real-time inventory."""
        return await self.send_protocol_message(
            session, "check_inventory", {"sku": sku, "requested_quantity": quantity}
        )

    async def get_quote(
        self,
        session: AsyncSession,
        items: list[QuoteItemRequest],
        shipping_country: str = "IN",
        idempotency_key: str | None = None,
    ) -> ProtocolResponseMessage:
        """Requests a binding price quote."""
        if not self.context.session_id:
            await self.initialize_session(session)

        params: dict[str, Any] = {
            "session_id": str(self.context.session_id),
            "items": [item.model_dump(mode="json") for item in items],
            "shipping_country": shipping_country,
        }
        res = await self.send_protocol_message(
            session, "get_quote", params, idempotency_key=idempotency_key
        )
        if res.status == "SUCCESS" and res.result:
            self.context.active_quote_id = uuid.UUID(res.result["quote_id"])
            self.context.current_state = BuyerCommerceState.QUOTED
        elif res.status == "REJECTED":
            if res.error and res.error.code == "INSUFFICIENT_STOCK":
                self.context.current_failure = BuyerFailureState.INVENTORY_CHANGED
        return res

    async def negotiate_quote(
        self,
        session: AsyncSession,
        quote_id: uuid.UUID,
        proposed_total_paise: int,
        rationale: str | None = "AI Buyer bulk discount counter-offer",
        idempotency_key: str | None = None,
    ) -> ProtocolResponseMessage:
        """Submits a negotiated counter-offer."""
        params = {
            "quote_id": str(quote_id),
            "proposed_total_paise": proposed_total_paise,
            "rationale": rationale,
        }
        res = await self.send_protocol_message(
            session, "negotiate_quote", params, idempotency_key=idempotency_key
        )
        if res.status == "SUCCESS" and res.result:
            verdict = res.result.get("verdict")
            if verdict == "ALLOW":
                self.context.current_state = BuyerCommerceState.OFFER_ACCEPTED
            elif verdict == "ESCALATE_APPROVAL":
                self.context.current_state = BuyerCommerceState.NEGOTIATION_PENDING
        elif res.status == "REJECTED":
            self.context.current_failure = BuyerFailureState.POLICY_REJECTED
        return res

    async def accept_quote(
        self,
        session: AsyncSession,
        quote_id: uuid.UUID,
        idempotency_key: str | None = None,
    ) -> ProtocolResponseMessage:
        """Locks and accepts a proposed quote."""
        params = {"quote_id": str(quote_id)}
        res = await self.send_protocol_message(
            session, "accept_quote", params, idempotency_key=idempotency_key
        )
        if res.status == "SUCCESS":
            self.context.current_state = BuyerCommerceState.OFFER_ACCEPTED
        return res

    async def calculate_shipping(
        self,
        session: AsyncSession,
        postal_code: str,
        country: str = "IN",
        subtotal_paise: int | None = None,
        quote_id: uuid.UUID | None = None,
    ) -> ProtocolResponseMessage:
        """Calculates shipping fees."""
        params: dict[str, Any] = {
            "destination_postal_code": postal_code,
            "destination_country": country,
        }
        if subtotal_paise is not None:
            params["subtotal_paise"] = subtotal_paise
        if quote_id is not None:
            params["quote_id"] = str(quote_id)
        return await self.send_protocol_message(session, "calculate_shipping", params)

    async def create_order(
        self,
        session: AsyncSession,
        quote_id: uuid.UUID,
        buyer_email: str,
        shipping_address: ShippingAddressGateway,
        idempotency_key: str | None = None,
    ) -> ProtocolResponseMessage:
        """Converts accepted quote to an authoritative order."""
        idem_key = idempotency_key or f"order_{quote_id}_{uuid.uuid4().hex[:8]}"
        params = {
            "quote_id": str(quote_id),
            "buyer_email": buyer_email,
            "shipping_address": shipping_address.model_dump(mode="json"),
            "idempotency_key": idem_key,
        }
        res = await self.send_protocol_message(
            session, "create_order", params, idempotency_key=idem_key
        )
        if res.status == "SUCCESS" and res.result:
            self.context.active_order_id = uuid.UUID(res.result["order_id"])
            self.context.current_state = BuyerCommerceState.ORDER_CREATED
        return res

    async def request_checkout(
        self,
        session: AsyncSession,
        order_id: uuid.UUID | None = None,
        quote_id: uuid.UUID | None = None,
        buyer_email: str | None = None,
        shipping_address: ShippingAddressGateway | None = None,
        idempotency_key: str | None = None,
    ) -> ProtocolResponseMessage:
        """Requests checkout parameters and initiates payment pending state."""
        idem_key = idempotency_key or f"chk_{order_id or quote_id}_{uuid.uuid4().hex[:8]}"
        params: dict[str, Any] = {"idempotency_key": idem_key}
        if order_id:
            params["order_id"] = str(order_id)
        if quote_id:
            params["quote_id"] = str(quote_id)
        if buyer_email:
            params["buyer_email"] = buyer_email
        if shipping_address:
            params["shipping_address"] = shipping_address.model_dump(mode="json")

        res = await self.send_protocol_message(
            session, "request_checkout", params, idempotency_key=idem_key
        )
        if res.status == "SUCCESS":
            self.context.current_state = BuyerCommerceState.PAYMENT_PENDING
        return res

    async def get_payment_status(
        self,
        session: AsyncSession,
        order_id: uuid.UUID,
    ) -> ProtocolResponseMessage:
        """Queries authoritative payment status."""
        return await self.send_protocol_message(
            session, "get_payment_status", {"order_id": str(order_id)}
        )

    async def get_order_status(
        self,
        session: AsyncSession,
        order_id: uuid.UUID,
    ) -> ProtocolResponseMessage:
        """Queries authoritative order and settlement status."""
        return await self.send_protocol_message(
            session, "get_order_status", {"order_id": str(order_id)}
        )

    async def terminate_session(
        self,
        session: AsyncSession,
        reason: str = "Buyer flow completed normally",
    ) -> ProtocolResponseMessage:
        """Terminates the active session."""
        if not self.context.session_id:
            return self.adapter.format_error_response(
                error_code="SESSION_NOT_INITIALIZED",
                message="No active session to terminate",
                request_id=uuid.uuid4(),
                action="terminate_session",
            )
        return await self.send_protocol_message(
            session,
            "terminate_session",
            {"session_id": str(self.context.session_id), "reason": reason},
        )

    async def authorize_test_payment(
        self,
        session: AsyncSession,
        order_id: uuid.UUID,
        rzp_payment_id: str | None = None,
        payment_method: str = "upi",
    ) -> dict[str, Any]:
        """Simulates Razorpay payment authorization via signed webhook."""
        settings = get_settings()
        if not settings.is_testing and not getattr(
            settings, "ALLOW_TEST_PAYMENT_SIMULATION", False
        ):
            raise PermissionError(
                "Simulated test payment authorization is only permitted in testing mode."
            )
        status_res = await self.get_payment_status(session, order_id)
        if not status_res.result:
            raise ValueError(f"Cannot authorize payment: order {order_id} not found")

        rzp_order_id = status_res.result.get("rzp_order_id")
        if not rzp_order_id:
            raise ValueError(
                f"Order {order_id} has not been checked out or has no Razorpay order ID"
            )
        pay_id = rzp_payment_id or f"pay_{uuid.uuid4().hex[:14]}"
        amount_paise = status_res.result.get("amount_paise", 0)

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
                {"order_id": str(order_id), "status": reco_status},
            )
        else:
            self.context.current_failure = BuyerFailureState.PAYMENT_FAILED
            self._record_step(
                "authorize_test_payment",
                "FAILED",
                BuyerFailureState.PAYMENT_FAILED.value,
                {"order_id": str(order_id), "reco_result": reco_result},
            )
        return reco_result

    # -------------------------------------------------------------------------
    # Full Demo End-to-End Orchestrator
    # -------------------------------------------------------------------------
    async def execute_full_commerce_flow(
        self,
        session: AsyncSession,
        query: str,
        target_sku: str,
        target_variant_sku: str,
        quantity: int,
        buyer_email: str,
        shipping_address: ShippingAddressGateway,
        negotiate_proposed_paise: int | None = None,
    ) -> BuyerFlowResult:
        """Executes complete hackathon demo commerce lifecycle via protocol adapter."""
        # 1. Initialize Session
        sess_res = await self.initialize_session(session)
        if sess_res.status != "SUCCESS":
            return BuyerFlowResult(
                is_success=False,
                final_state=BuyerFailureState.AUTHORIZATION_REQUIRED.value,
                error_code=sess_res.error.code if sess_res.error else None,
                error_message=sess_res.error.message if sess_res.error else None,
                step_count=1,
            )

        # 2. Discover Products
        disc_res = await self.discover_products(session, query=query)
        if disc_res.status != "SUCCESS":
            curr_state = (
                self.context.current_state.value if self.context.current_state else "UNKNOWN"
            )
            return BuyerFlowResult(
                is_success=False,
                final_state=curr_state,
                error_code=disc_res.error.code if disc_res.error else None,
                error_message=disc_res.error.message if disc_res.error else None,
                step_count=2,
            )

        # 3. Get Product Details
        prod_res = await self.get_product(session, sku=target_sku)
        if prod_res.status != "SUCCESS":
            curr_state = (
                self.context.current_state.value if self.context.current_state else "UNKNOWN"
            )
            return BuyerFlowResult(
                is_success=False,
                final_state=curr_state,
                error_code=prod_res.error.code if prod_res.error else None,
                error_message=prod_res.error.message if prod_res.error else None,
                step_count=3,
            )

        # 4. Check Inventory
        inv_res = await self.check_inventory(session, sku=target_variant_sku, quantity=quantity)
        if inv_res.status != "SUCCESS":
            curr_state = (
                self.context.current_state.value if self.context.current_state else "UNKNOWN"
            )
            return BuyerFlowResult(
                is_success=False,
                final_state=curr_state,
                error_code=inv_res.error.code if inv_res.error else None,
                error_message=inv_res.error.message if inv_res.error else None,
                step_count=4,
            )

        # 5. Get Quote
        q_res = await self.get_quote(
            session,
            items=[QuoteItemRequest(sku=target_variant_sku, quantity=quantity)],
            shipping_country=shipping_address.country,
        )
        if q_res.status != "SUCCESS" or not q_res.result:
            curr_state = (
                self.context.current_state.value if self.context.current_state else "UNKNOWN"
            )
            return BuyerFlowResult(
                is_success=False,
                final_state=curr_state,
                error_code=q_res.error.code if q_res.error else None,
                error_message=q_res.error.message if q_res.error else None,
                step_count=5,
            )
        quote_id = uuid.UUID(q_res.result["quote_id"])

        # 6. Bounded Negotiation (Optional)
        if negotiate_proposed_paise is not None:
            neg_res = await self.negotiate_quote(
                session,
                quote_id=quote_id,
                proposed_total_paise=negotiate_proposed_paise,
            )
            if neg_res.status != "SUCCESS":
                curr_state = (
                    self.context.current_state.value if self.context.current_state else "UNKNOWN"
                )
                return BuyerFlowResult(
                    is_success=False,
                    final_state=curr_state,
                    error_code=neg_res.error.code if neg_res.error else None,
                    error_message=neg_res.error.message if neg_res.error else None,
                    step_count=6,
                )

        # 7. Accept Quote
        acc_res = await self.accept_quote(session, quote_id=quote_id)
        if acc_res.status != "SUCCESS":
            curr_state = (
                self.context.current_state.value if self.context.current_state else "UNKNOWN"
            )
            return BuyerFlowResult(
                is_success=False,
                final_state=curr_state,
                error_code=acc_res.error.code if acc_res.error else None,
                error_message=acc_res.error.message if acc_res.error else None,
                step_count=7,
            )

        # 8. Calculate Shipping
        ship_res = await self.calculate_shipping(
            session,
            postal_code=shipping_address.postal_code,
            country=shipping_address.country,
            quote_id=quote_id,
        )
        if ship_res.status != "SUCCESS":
            curr_state = (
                self.context.current_state.value if self.context.current_state else "UNKNOWN"
            )
            return BuyerFlowResult(
                is_success=False,
                final_state=curr_state,
                error_code=ship_res.error.code if ship_res.error else "SHIPPING_ERROR",
                error_message=ship_res.error.message if ship_res.error else None,
                step_count=8,
            )

        # 9. Create Order
        ord_res = await self.create_order(
            session,
            quote_id=quote_id,
            buyer_email=buyer_email,
            shipping_address=shipping_address,
        )
        if ord_res.status != "SUCCESS" or not ord_res.result:
            curr_state = (
                self.context.current_state.value if self.context.current_state else "UNKNOWN"
            )
            return BuyerFlowResult(
                is_success=False,
                final_state=curr_state,
                error_code=ord_res.error.code if ord_res.error else None,
                error_message=ord_res.error.message if ord_res.error else None,
                step_count=9,
            )
        order_id = uuid.UUID(ord_res.result["order_id"])

        # 10. Request Checkout
        chk_res = await self.request_checkout(session, order_id=order_id)
        if chk_res.status != "SUCCESS":
            curr_state = (
                self.context.current_state.value if self.context.current_state else "UNKNOWN"
            )
            return BuyerFlowResult(
                is_success=False,
                final_state=curr_state,
                error_code=chk_res.error.code if chk_res.error else None,
                error_message=chk_res.error.message if chk_res.error else None,
                step_count=10,
            )

        # 11. Authorize Payment via Webhook
        await self.authorize_test_payment(session, order_id=order_id)

        # 12. Poll Payment Status
        pay_stat = await self.get_payment_status(session, order_id=order_id)
        if (
            pay_stat.status != "SUCCESS"
            or not pay_stat.result
            or not (
                pay_stat.result.get("is_paid")
                or pay_stat.result.get("status") in {"PAID", "COMPLETED", "FULFILLMENT_PENDING"}
            )
        ):
            return BuyerFlowResult(
                is_success=False,
                final_state=BuyerFailureState.PAYMENT_FAILED.value,
                error_code=pay_stat.error.code if pay_stat.error else "PAYMENT_NOT_SETTLED",
                error_message=(
                    pay_stat.error.message
                    if pay_stat.error
                    else "Payment is not marked settled/paid."
                ),
                step_count=12,
            )

        # 13. Query Final Order Status
        ord_stat = await self.get_order_status(session, order_id=order_id)
        if ord_stat.status != "SUCCESS":
            curr_state = (
                self.context.current_state.value if self.context.current_state else "UNKNOWN"
            )
            return BuyerFlowResult(
                is_success=False,
                final_state=curr_state,
                error_code=ord_stat.error.code if ord_stat.error else None,
                error_message=ord_stat.error.message if ord_stat.error else None,
                step_count=13,
            )

        # 14. Terminate Session
        await self.terminate_session(session)
        self.context.current_state = BuyerCommerceState.COMPLETED

        amount_paise = ord_stat.result.get("amount_paise", 0) if ord_stat.result else 0
        payment_status = ord_stat.result.get("status", "PAID") if ord_stat.result else "PAID"

        return BuyerFlowResult(
            is_success=True,
            final_state=BuyerCommerceState.COMPLETED.value,
            order_id=order_id,
            quote_id=quote_id,
            amount_paise=amount_paise,
            payment_status=payment_status,
            step_count=14,
        )
