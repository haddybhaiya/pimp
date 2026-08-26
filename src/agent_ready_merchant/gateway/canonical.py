"""Canonical Commerce Gateway coordinating AI buyers and the authoritative commerce kernel.

Adheres strictly to Phase 2.1 specifications:
- Gating all 8 canonical capabilities through state machines, policy, and audit
- Strict tenant and session boundary enforcement (cross-merchant / cross-session rejection)
- State-oriented response envelopes with next_action and allowed_actions
- Zero bypass around authorization, inventory reservations, policy, or audit
"""

import asyncio
import hashlib
import logging
import time
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from agent_ready_merchant.config import get_settings
from agent_ready_merchant.db.concurrency import OptimisticLockError
from agent_ready_merchant.gateway.constants import COMMERCE_PROTOCOL_VERSION
from agent_ready_merchant.gateway.hardening import (
    GatewayErrorCode,
    global_idempotency_manager,
    global_rate_limiter,
    sanitize_error_response,
    validate_payload_size,
)
from agent_ready_merchant.gateway.registry import CapabilityDefinition, CapabilityRegistry
from agent_ready_merchant.gateway.representation import (
    MerchantAIRepresentation,
    build_merchant_representation,
)
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
    GatewayError,
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
    PaymentAttemptItem,
    ProductSummaryItem,
    QuoteLineItemDetail,
    RequestCheckoutRequest,
    RequestCheckoutResponse,
    ShippingAddressGateway,
    StateOrientedContext,
    TerminateSessionRequest,
    TerminateSessionResponse,
    VariantDetailItem,
)
from agent_ready_merchant.integrations.razorpay.client import RazorpayClient
from agent_ready_merchant.integrations.razorpay.exceptions import RazorpayError
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.order import Order
from agent_ready_merchant.models.payment import PaymentAttempt
from agent_ready_merchant.models.product import Product, ProductVariant
from agent_ready_merchant.models.quote import PriceQuote, QuoteItem
from agent_ready_merchant.models.session import BuyerAgentSession
from agent_ready_merchant.policy.engine import DeterministicPolicyEngine
from agent_ready_merchant.policy.models import (
    PolicyContext,
    PolicyVerdict,
    QuoteItemProposal,
    QuoteProposal,
)
from agent_ready_merchant.services.payment_service import PaymentService
from agent_ready_merchant.state_machines.price_quote import PriceQuoteStateMachine
from agent_ready_merchant.tools.base import GatewayContext
from agent_ready_merchant.tools.gateway import ToolGateway

logger = logging.getLogger("agent_ready_merchant.gateway.canonical")

_ALLOWED_BUYER_CAPABILITIES: frozenset[str] = frozenset(
    {
        "buyer:discover",
        "buyer:read",
        "buyer:quote",
        "buyer:negotiate",
        "buyer:checkout",
        "buyer:payment_status",
    }
)


class CanonicalCommerceGateway:
    """Server-authoritative boundary between arbitrary AI buyers/adapters and commerce domain."""

    def __init__(self, tool_gateway: ToolGateway | None = None) -> None:
        self.tool_gateway = tool_gateway or ToolGateway()

    async def get_merchant_representation(
        self,
        session: AsyncSession,
        merchant_id: uuid.UUID,
        context: GatewayContext | None = None,
    ) -> MerchantAIRepresentation:
        """Retrieves authoritative merchant identity, policies, and capability boundaries."""
        return await build_merchant_representation(session, merchant_id, context)

    def get_capabilities_catalog(self) -> list[CapabilityDefinition]:
        """Returns the full catalog of declared capabilities and schemas."""
        return CapabilityRegistry.get_all_capabilities()

    # -------------------------------------------------------------------------
    # 1. discover_products
    # -------------------------------------------------------------------------
    async def discover_products(
        self,
        session: AsyncSession,
        request: DiscoverProductsRequest,
        context: GatewayContext,
    ) -> GatewayResponseEnvelope[DiscoverProductsResponse]:
        """Discovers and filters catalog products matching criteria."""
        auth_ok, auth_err = CapabilityRegistry.check_authorization("discover_products", context)
        if not auth_ok:
            return self._rejected_envelope(
                "discover_products", "CAPABILITY_DENIED", auth_err or "Unauthorized"
            )

        stmt = (
            select(Product)
            .options(selectinload(Product.variants).selectinload(ProductVariant.inventory_item))
            .where(Product.merchant_id == context.merchant_id, Product.is_active.is_(True))
        )
        if request.category:
            stmt = stmt.where(Product.category.ilike(f"%{request.category}%"))
        if request.min_price_paise is not None:
            stmt = stmt.where(Product.base_price_paise >= request.min_price_paise)
        if request.max_price_paise is not None:
            stmt = stmt.where(Product.base_price_paise <= request.max_price_paise)

        res = await session.execute(stmt)
        products = list(res.scalars().all())

        if request.query:
            q_lower = request.query.lower()
            products = [
                p
                for p in products
                if q_lower in p.title.lower()
                or (p.description and q_lower in p.description.lower())
            ]

        if request.in_stock_only:
            products = [
                p
                for p in products
                if any(
                    v.inventory_item
                    and v.inventory_item.available_quantity > v.inventory_item.safety_threshold
                    for v in p.variants
                )
            ]

        total_matched = len(products)
        paged = products[request.offset : request.offset + request.limit]

        summary_items: list[ProductSummaryItem] = []
        for p in paged:
            has_stock = (
                any(
                    v.inventory_item
                    and v.inventory_item.available_quantity > v.inventory_item.safety_threshold
                    for v in p.variants
                )
                if p.variants
                else True
            )

            summary_items.append(
                ProductSummaryItem(
                    sku=p.sku,
                    title=p.title,
                    category=p.category,
                    base_price_paise=p.base_price_paise,
                    currency="INR",
                    is_negotiable=p.is_negotiable,
                    in_stock=has_stock,
                    variant_count=max(1, len(p.variants)),
                )
            )

        resp_data = DiscoverProductsResponse(
            products=summary_items,
            total_matched=total_matched,
            limit=request.limit,
            offset=request.offset,
        )
        return GatewayResponseEnvelope[DiscoverProductsResponse](
            status="SUCCESS",
            capability="discover_products",
            data=resp_data,
            state=StateOrientedContext(
                entity_type="Catalog",
                entity_id=str(context.merchant_id),
                state="DISCOVERED",
                allowed_actions=[
                    "get_product",
                    "check_inventory",
                    "get_quote",
                    "calculate_shipping",
                ],
                next_action="Select a product to view details or request a price quote",
            ),
        )

    # -------------------------------------------------------------------------
    # 2. get_product
    # -------------------------------------------------------------------------
    async def get_product(
        self,
        session: AsyncSession,
        request: GetProductRequest,
        context: GatewayContext,
    ) -> GatewayResponseEnvelope[GetProductResponse]:
        """Retrieves comprehensive specifications, pricing, and variants for a SKU."""
        auth_ok, auth_err = CapabilityRegistry.check_authorization("get_product", context)
        if not auth_ok:
            return self._rejected_envelope(
                "get_product", "CAPABILITY_DENIED", auth_err or "Unauthorized"
            )

        stmt = (
            select(Product)
            .options(selectinload(Product.variants).selectinload(ProductVariant.inventory_item))
            .where(
                Product.sku == request.sku,
                Product.merchant_id == context.merchant_id,
            )
        )
        product = (await session.execute(stmt)).scalar_one_or_none()

        # If not found by product SKU, check if SKU is a variant SKU
        if not product:
            var_stmt = (
                select(ProductVariant)
                .join(Product, ProductVariant.product_id == Product.id)
                .options(
                    selectinload(ProductVariant.product)
                    .selectinload(Product.variants)
                    .selectinload(ProductVariant.inventory_item)
                )
                .where(
                    ProductVariant.sku == request.sku,
                    Product.merchant_id == context.merchant_id,
                )
            )
            var_res = (await session.execute(var_stmt)).scalar_one_or_none()
            if var_res:
                product = var_res.product

        if not product or not product.is_active:
            return self._rejected_envelope(
                "get_product",
                "PRODUCT_NOT_FOUND",
                f"Product with SKU '{request.sku}' not found or inactive for this merchant.",
            )

        variant_items: list[VariantDetailItem] = []
        for v in product.variants:
            inv = v.inventory_item
            avail = inv.available_quantity if inv else 0
            safety = inv.safety_threshold if inv else 0
            effective_price = (
                v.price_override_paise
                if v.price_override_paise is not None
                else product.base_price_paise
            )

            variant_items.append(
                VariantDetailItem(
                    variant_id=v.id,
                    sku=v.sku,
                    title=v.title,
                    price_override_paise=v.price_override_paise,
                    effective_price_paise=effective_price,
                    currency="INR",
                    is_active=v.is_active,
                    available_quantity=avail,
                    in_stock=avail > safety,
                    attributes=v.attributes or {},
                )
            )

        resp_data = GetProductResponse(
            product_id=product.id,
            sku=product.sku,
            title=product.title,
            description=product.description or "",
            category=product.category,
            base_price_paise=product.base_price_paise,
            currency="INR",
            is_negotiable=product.is_negotiable,
            is_active=product.is_active,
            attributes=product.attributes or {},
            variants=variant_items,
        )
        return GatewayResponseEnvelope[GetProductResponse](
            status="SUCCESS",
            capability="get_product",
            data=resp_data,
            state=StateOrientedContext(
                entity_type="Product",
                entity_id=str(product.id),
                state="ACTIVE",
                allowed_actions=["check_inventory", "get_quote", "calculate_shipping"],
                next_action="Verify stock or request a formal price quote for this SKU",
            ),
        )

    # -------------------------------------------------------------------------
    # 3. check_inventory
    # -------------------------------------------------------------------------
    async def check_inventory(
        self,
        session: AsyncSession,
        request: CheckInventoryRequest,
        context: GatewayContext,
    ) -> GatewayResponseEnvelope[CheckInventoryResponse]:
        """Checks real-time inventory and fulfillability for a SKU."""
        auth_ok, auth_err = CapabilityRegistry.check_authorization("check_inventory", context)
        if not auth_ok:
            return self._rejected_envelope(
                "check_inventory", "CAPABILITY_DENIED", auth_err or "Unauthorized"
            )

        # 1. Search Variant directly
        var_stmt = (
            select(ProductVariant)
            .join(Product, ProductVariant.product_id == Product.id)
            .options(selectinload(ProductVariant.inventory_item))
            .where(
                ProductVariant.sku == request.sku,
                Product.merchant_id == context.merchant_id,
            )
        )
        variant = (await session.execute(var_stmt)).scalar_one_or_none()

        # 2. If not found by variant, search product base SKU
        if not variant:
            prod_stmt = (
                select(Product)
                .options(selectinload(Product.variants).selectinload(ProductVariant.inventory_item))
                .where(
                    Product.sku == request.sku,
                    Product.merchant_id == context.merchant_id,
                )
            )
            prod = (await session.execute(prod_stmt)).scalar_one_or_none()
            if prod and prod.variants:
                if len(prod.variants) == 1:
                    variant = prod.variants[0]
                else:
                    return self._rejected_envelope(
                        "check_inventory",
                        GatewayErrorCode.AMBIGUOUS_SKU.value,
                        (
                            f"Product SKU '{request.sku}' has multiple variants. "
                            "Please specify a specific variant SKU."
                        ),
                    )

        if not variant:
            return self._rejected_envelope(
                "check_inventory",
                "SKU_NOT_FOUND",
                f"SKU '{request.sku}' not found for authenticated merchant.",
            )

        inv = variant.inventory_item
        available = inv.available_quantity if inv else 0
        reserved = inv.reserved_quantity if inv else 0
        safety = inv.safety_threshold if inv else 0

        in_stock = available > safety
        can_fulfill = available >= (request.requested_quantity + safety)
        max_orderable = max(0, available - safety)

        resp_data = CheckInventoryResponse(
            sku=request.sku,
            variant_id=variant.id,
            available_quantity=available,
            reserved_quantity=reserved,
            safety_threshold=safety,
            in_stock=in_stock,
            can_fulfill=can_fulfill,
            max_order_quantity=max_orderable,
        )
        return GatewayResponseEnvelope[CheckInventoryResponse](
            status="SUCCESS",
            capability="check_inventory",
            data=resp_data,
            state=StateOrientedContext(
                entity_type="InventoryItem",
                entity_id=str(inv.id if inv else variant.id),
                state="AVAILABLE" if can_fulfill else "OUT_OF_STOCK",
                allowed_actions=["get_quote", "calculate_shipping"]
                if can_fulfill
                else ["discover_products"],
                next_action="Proceed to request price quote"
                if can_fulfill
                else "Select alternative in-stock item",
            ),
        )

    # -------------------------------------------------------------------------
    # 4. get_quote
    # -------------------------------------------------------------------------
    async def get_quote(
        self,
        session: AsyncSession,
        request: GetQuoteRequest,
        context: GatewayContext,
    ) -> GatewayResponseEnvelope[GetQuoteResponse]:
        """Creates or retrieves a binding, authoritative price quote."""
        auth_ok, auth_err = CapabilityRegistry.check_authorization("get_quote", context)
        if not auth_ok:
            return self._rejected_envelope(
                "get_quote", "CAPABILITY_DENIED", auth_err or "Unauthorized"
            )

        # Session boundary check
        if request.session_id != context.session_id:
            return self._rejected_envelope(
                "get_quote",
                "UNAUTHORIZED_SESSION",
                (
                    f"Request session '{request.session_id}' does not match "
                    f"active gateway session '{context.session_id}'."
                ),
            )

        # Retrieve existing quote if quote_id passed
        if request.quote_id:
            q_stmt = (
                select(PriceQuote)
                .options(
                    selectinload(PriceQuote.items)
                    .selectinload(QuoteItem.variant)
                    .selectinload(ProductVariant.product)
                )
                .where(
                    PriceQuote.id == request.quote_id,
                    PriceQuote.merchant_id == context.merchant_id,
                    PriceQuote.session_id == context.session_id,
                )
            )
            quote = (await session.execute(q_stmt)).scalar_one_or_none()
            if not quote:
                return self._rejected_envelope(
                    "get_quote",
                    "QUOTE_NOT_FOUND",
                    f"PriceQuote with ID '{request.quote_id}' not found for active session.",
                )

            now = datetime.now(UTC)
            quote_expires = (
                quote.expires_at
                if quote.expires_at.tzinfo
                else quote.expires_at.replace(tzinfo=UTC)
            )
            is_expired = now > quote_expires

            line_items: list[QuoteLineItemDetail] = []
            for item in quote.items:
                title = item.variant.title if item.variant else item.variant_id.hex[:8]
                sku = item.variant.sku if item.variant else str(item.variant_id)
                line_items.append(
                    QuoteLineItemDetail(
                        variant_id=item.variant_id,
                        sku=sku,
                        title=title,
                        quantity=item.quantity,
                        unit_price_paise=item.unit_price_paise,
                        total_price_paise=item.total_price_paise,
                    )
                )

            resp_data = GetQuoteResponse(
                quote_id=quote.id,
                session_id=quote.session_id,
                status=quote.status,
                currency="INR",
                items=line_items,
                subtotal_paise=quote.subtotal_paise,
                discount_paise=quote.discount_paise,
                shipping_paise=quote.shipping_paise,
                total_paise=quote.total_paise,
                expires_at=quote.expires_at,
                is_expired=is_expired,
            )
            allowed = (
                ["create_order", "request_checkout"]
                if quote.status == "ACCEPTED" and not is_expired
                else ["get_quote", "discover_products"]
            )
            return GatewayResponseEnvelope[GetQuoteResponse](
                status="SUCCESS",
                capability="get_quote",
                data=resp_data,
                state=StateOrientedContext(
                    entity_type="PriceQuote",
                    entity_id=str(quote.id),
                    state=quote.status,
                    version=quote.version,
                    allowed_actions=allowed,
                    next_action="Proceed to create order"
                    if quote.status == "ACCEPTED"
                    else "Review quote or generate new quote",
                    expires_at=quote.expires_at,
                ),
            )

        if not request.items:
            return self._rejected_envelope(
                "get_quote",
                "EMPTY_ITEMS",
                "At least 1 item is required to generate a new price quote.",
            )

        # Check active quotes limit per buyer session
        settings = get_settings()
        max_active_quotes = getattr(settings, "MAX_ACTIVE_QUOTES_PER_BUYER", 5)
        active_quotes_stmt = select(func.count(PriceQuote.id)).where(
            PriceQuote.merchant_id == context.merchant_id,
            PriceQuote.session_id == context.session_id,
            PriceQuote.status.in_(["PROPOSED", "NEGOTIATING", "ACCEPTED"]),
            PriceQuote.expires_at > datetime.now(UTC),
        )
        active_quotes_count = (await session.execute(active_quotes_stmt)).scalar() or 0
        if active_quotes_count >= max_active_quotes:
            return self._rejected_envelope(
                "get_quote",
                GatewayErrorCode.MAX_ACTIVE_QUOTES_EXCEEDED.value,
                f"Maximum active quotes limit ({max_active_quotes}) reached for session.",
            )

        # Generate new quote
        now = datetime.now(UTC)
        subtotal = 0
        quote_items_payload: list[dict[str, Any]] = []
        proposal_items: list[QuoteItemProposal] = []

        for req_item in request.items:
            var_stmt = (
                select(ProductVariant)
                .join(Product, ProductVariant.product_id == Product.id)
                .options(
                    selectinload(ProductVariant.product),
                    selectinload(ProductVariant.inventory_item),
                )
                .where(
                    ProductVariant.sku == req_item.sku,
                    Product.merchant_id == context.merchant_id,
                )
            )
            variant = (await session.execute(var_stmt)).scalar_one_or_none()

            if not variant:
                prod_stmt = (
                    select(Product)
                    .options(
                        selectinload(Product.variants).selectinload(ProductVariant.inventory_item)
                    )
                    .where(
                        Product.sku == req_item.sku,
                        Product.merchant_id == context.merchant_id,
                    )
                )
                prod = (await session.execute(prod_stmt)).scalar_one_or_none()
                if prod and prod.variants:
                    active_vars = [v for v in prod.variants if v.is_active]
                    if active_vars:
                        variant = active_vars[0]
                        variant.product = prod

            if not variant or not variant.product.is_active or not variant.is_active:
                return self._rejected_envelope(
                    "get_quote",
                    "SKU_NOT_FOUND",
                    f"Product or variant for SKU '{req_item.sku}' not found or inactive.",
                )

            inv = variant.inventory_item
            safety_thresh = getattr(inv, "safety_threshold", 0) if inv else 0
            if inv is None or inv.available_quantity < (req_item.quantity + safety_thresh):
                avail_qty = inv.available_quantity if inv else 0
                return self._rejected_envelope(
                    "get_quote",
                    "INSUFFICIENT_STOCK",
                    (
                        f"Insufficient stock for SKU '{req_item.sku}': requested "
                        f"{req_item.quantity}, available {avail_qty}."
                    ),
                )

            unit_price = (
                variant.price_override_paise
                if variant.price_override_paise is not None
                else variant.product.base_price_paise
            )
            line_total = unit_price * req_item.quantity
            subtotal += line_total

            quote_items_payload.append(
                {
                    "variant_id": variant.id,
                    "sku": variant.sku,
                    "title": f"{variant.product.title} - {variant.title}",
                    "quantity": req_item.quantity,
                    "unit_price_paise": unit_price,
                    "total_price_paise": line_total,
                }
            )
            proposal_items.append(
                QuoteItemProposal(
                    sku=variant.sku,
                    quantity=req_item.quantity,
                    unit_base_price_paise=unit_price,
                    proposed_unit_price_paise=unit_price,
                    unit_floor_price_paise=variant.product.floor_price_paise,
                    unit_cost_price_paise=int(variant.product.floor_price_paise * 0.8),
                    is_negotiable=variant.product.is_negotiable,
                )
            )

        # Deterministic Shipping & Policy Evaluation
        shipping_fee = 0 if subtotal >= 100_000 else 10_000
        total_paise = subtotal + shipping_fee

        policy_proposal = QuoteProposal(
            items=proposal_items,
            subtotal_paise=subtotal,
            discount_paise=0,
            shipping_paise=shipping_fee,
            total_paise=total_paise,
            shipping_country=request.shipping_country,
        )
        policy_ctx = PolicyContext(
            merchant_autonomy_level=context.autonomy_level,
            max_discount_percentage=context.max_discount_percentage,
            min_margin_percentage=context.min_margin_percentage,
            max_single_transaction_paise=context.max_single_transaction_paise,
            session_capabilities=context.capabilities,
        )
        engine = DeterministicPolicyEngine()
        policy_result = engine.evaluate_quote(policy_proposal, policy_ctx)

        if policy_result.verdict == PolicyVerdict.DENY:
            return self._rejected_envelope(
                "get_quote",
                policy_result.rule_code,
                policy_result.reason,
            )

        # Persist Authoritative Quote
        expires_at = now + timedelta(minutes=15)
        idempotency_key = (
            f"quote_{context.session_id.hex[:16]}_{int(now.timestamp())}_{uuid.uuid4().hex[:8]}"
        )

        new_quote = PriceQuote(
            merchant_id=context.merchant_id,
            session_id=context.session_id,
            status="PROPOSED",
            subtotal_paise=subtotal,
            discount_paise=0,
            shipping_paise=shipping_fee,
            total_paise=total_paise,
            expires_at=expires_at,
            idempotency_key=idempotency_key,
        )
        session.add(new_quote)
        await session.flush()

        for item_data in quote_items_payload:
            qi = QuoteItem(
                quote_id=new_quote.id,
                variant_id=item_data["variant_id"],
                quantity=item_data["quantity"],
                unit_price_paise=item_data["unit_price_paise"],
                total_price_paise=item_data["total_price_paise"],
            )
            session.add(qi)
        await session.flush()

        # Audit Event
        audit_event = await AuditEvent.create_event(
            session=session,
            merchant_id=context.merchant_id,
            actor_type="BUYER_AGENT",
            event_type="PRICE_QUOTE_CREATED",
            payload={
                "quote_id": str(new_quote.id),
                "total_paise": total_paise,
                "item_count": len(quote_items_payload),
            },
            session_id=context.session_id,
        )

        line_items = [
            QuoteLineItemDetail(
                variant_id=it["variant_id"],
                sku=it["sku"],
                title=it["title"],
                quantity=it["quantity"],
                unit_price_paise=it["unit_price_paise"],
                total_price_paise=it["total_price_paise"],
            )
            for it in quote_items_payload
        ]
        resp_data = GetQuoteResponse(
            quote_id=new_quote.id,
            session_id=new_quote.session_id,
            status=new_quote.status,
            currency="INR",
            items=line_items,
            subtotal_paise=subtotal,
            discount_paise=0,
            shipping_paise=shipping_fee,
            total_paise=total_paise,
            expires_at=expires_at,
            is_expired=False,
        )
        return GatewayResponseEnvelope[GetQuoteResponse](
            status="SUCCESS",
            capability="get_quote",
            data=resp_data,
            audit_event_id=audit_event.id,
            state=StateOrientedContext(
                entity_type="PriceQuote",
                entity_id=str(new_quote.id),
                state="PROPOSED",
                version=new_quote.version,
                allowed_actions=["accept_quote", "negotiate_quote", "terminate_session"],
                next_action="Accept quote or negotiate revised pricing before expiry",
                expires_at=expires_at,
            ),
        )

    # -------------------------------------------------------------------------
    # 5. calculate_shipping
    # -------------------------------------------------------------------------
    async def calculate_shipping(
        self,
        session: AsyncSession,
        request: CalculateShippingRequest,
        context: GatewayContext,
    ) -> GatewayResponseEnvelope[CalculateShippingResponse]:
        """Authoritatively calculates logistics shipping fees and free shipping eligibility."""
        auth_ok, auth_err = CapabilityRegistry.check_authorization("calculate_shipping", context)
        if not auth_ok:
            return self._rejected_envelope(
                "calculate_shipping", "CAPABILITY_DENIED", auth_err or "Unauthorized"
            )

        if request.destination_country != "IN":
            return self._rejected_envelope(
                "calculate_shipping",
                "UNSUPPORTED_COUNTRY",
                f"Shipping to '{request.destination_country}' is not supported (IN only).",
            )

        subtotal = 0
        if request.quote_id:
            q_stmt = select(PriceQuote).where(
                PriceQuote.id == request.quote_id,
                PriceQuote.merchant_id == context.merchant_id,
                PriceQuote.session_id == context.session_id,
            )
            quote = (await session.execute(q_stmt)).scalar_one_or_none()
            if not quote:
                return self._rejected_envelope(
                    "calculate_shipping",
                    "QUOTE_NOT_FOUND",
                    f"PriceQuote with ID '{request.quote_id}' not found for active session.",
                )
            subtotal = quote.subtotal_paise
        elif request.subtotal_paise is not None:
            subtotal = request.subtotal_paise

        free_shipping_threshold = 100_000
        standard_shipping_fee = 10_000
        qualifies_free = subtotal >= free_shipping_threshold
        shipping_fee = 0 if qualifies_free else standard_shipping_fee

        resp_data = CalculateShippingResponse(
            destination_country=request.destination_country,
            destination_postal_code=request.destination_postal_code,
            shipping_fee_paise=shipping_fee,
            currency="INR",
            qualifies_for_free_shipping=qualifies_free,
            free_shipping_threshold_paise=free_shipping_threshold,
            estimated_delivery_days=3,
            service_carrier="Standard Logistics",
        )
        return GatewayResponseEnvelope[CalculateShippingResponse](
            status="SUCCESS",
            capability="calculate_shipping",
            data=resp_data,
            state=StateOrientedContext(
                entity_type="ShippingCalculation",
                entity_id=request.destination_postal_code,
                state="CALCULATED",
                allowed_actions=["get_quote", "create_order", "request_checkout"],
                next_action="Review shipping cost and proceed to order creation",
            ),
        )

    # -------------------------------------------------------------------------
    # 6. create_order
    # -------------------------------------------------------------------------
    async def create_order(
        self,
        session: AsyncSession,
        request: CreateOrderGatewayRequest,
        context: GatewayContext,
    ) -> GatewayResponseEnvelope[CreateOrderGatewayResponse]:
        """Converts an ACCEPTED quote into a locked Order, reserving stock and calling Razorpay."""
        auth_ok, auth_err = CapabilityRegistry.check_authorization("create_order", context)
        if not auth_ok:
            return self._rejected_envelope(
                "create_order", "CAPABILITY_DENIED", auth_err or "Unauthorized"
            )

        settings = get_settings()
        rzp_client = RazorpayClient(
            key_id=settings.RAZORPAY_KEY_ID,
            key_secret=settings.RAZORPAY_KEY_SECRET,
            base_url=settings.RAZORPAY_API_BASE_URL,
        )
        try:
            order = await PaymentService.create_order_from_accepted_quote(
                session=session,
                quote_id=request.quote_id,
                buyer_email=str(request.buyer_email),
                shipping_address=request.shipping_address.model_dump(),
                rzp_client=rzp_client,
                merchant_id=context.merchant_id,
                session_id=context.session_id,
            )
        except ValueError as exc:
            await session.rollback()
            return self._rejected_envelope("create_order", "ORDER_CREATION_FAILED", str(exc))
        except RazorpayError as exc:
            await session.rollback()
            return self._error_envelope(
                "create_order",
                GatewayErrorCode.COMMERCE_PAYMENT_GATEWAY_ERROR.value,
                f"Razorpay payment gateway error: {exc}",
                retryable=True,
            )
        except OptimisticLockError as exc:
            await session.rollback()
            return self._rejected_envelope("create_order", "CONCURRENCY_CONFLICT", str(exc))

        # Query audit event created
        audit_stmt = (
            select(AuditEvent)
            .where(
                AuditEvent.merchant_id == context.merchant_id,
                AuditEvent.event_type.in_(["ORDER_CREATED", "ORDER_TRANSITION_PENDING_PAYMENT"]),
            )
            .order_by(AuditEvent.created_at.desc())
        )
        audit_event = (await session.execute(audit_stmt)).scalars().first()

        resp_data = CreateOrderGatewayResponse(
            order_id=order.id,
            quote_id=order.quote_id,
            status=order.status,
            amount_paise=order.amount_paise,
            currency=order.currency,
            buyer_email=order.buyer_email,
            rzp_order_id=order.rzp_order_id,
            shipping_address=request.shipping_address,
            created_at=order.created_at or datetime.now(UTC),
        )
        return GatewayResponseEnvelope[CreateOrderGatewayResponse](
            status="SUCCESS",
            capability="create_order",
            data=resp_data,
            audit_event_id=audit_event.id if audit_event else None,
            state=StateOrientedContext(
                entity_type="Order",
                entity_id=str(order.id),
                state=order.status,
                version=order.version,
                allowed_actions=["request_checkout", "get_payment_status"],
                next_action="Proceed to request checkout and submit customer payment",
            ),
        )

    # -------------------------------------------------------------------------
    # 7. request_checkout
    # -------------------------------------------------------------------------
    async def request_checkout(
        self,
        session: AsyncSession,
        request: RequestCheckoutRequest,
        context: GatewayContext,
    ) -> GatewayResponseEnvelope[RequestCheckoutResponse]:
        """Generates checkout session parameters and external Razorpay metadata for an order."""
        auth_ok, auth_err = CapabilityRegistry.check_authorization("request_checkout", context)
        if not auth_ok:
            return self._rejected_envelope(
                "request_checkout", "CAPABILITY_DENIED", auth_err or "Unauthorized"
            )

        settings = get_settings()
        order: Order | None = None

        if request.order_id:
            ord_stmt = (
                select(Order)
                .join(PriceQuote, Order.quote_id == PriceQuote.id)
                .where(
                    Order.id == request.order_id,
                    Order.merchant_id == context.merchant_id,
                    PriceQuote.session_id == context.session_id,
                )
            )
            order = (await session.execute(ord_stmt)).scalar_one_or_none()
            if not order:
                return self._rejected_envelope(
                    "request_checkout",
                    "ORDER_NOT_FOUND",
                    f"Order with ID '{request.order_id}' not found for authenticated session.",
                )
        elif request.quote_id:
            if not request.buyer_email or not request.shipping_address:
                return self._rejected_envelope(
                    "request_checkout",
                    "MISSING_CHECKOUT_DETAILS",
                    "buyer_email and shipping_address are required when checking out from a quote.",
                )
            rzp_client = RazorpayClient(
                key_id=settings.RAZORPAY_KEY_ID,
                key_secret=settings.RAZORPAY_KEY_SECRET,
                base_url=settings.RAZORPAY_API_BASE_URL,
            )
            try:
                order = await PaymentService.create_order_from_accepted_quote(
                    session=session,
                    quote_id=request.quote_id,
                    buyer_email=str(request.buyer_email),
                    shipping_address=request.shipping_address.model_dump(),
                    rzp_client=rzp_client,
                    merchant_id=context.merchant_id,
                    session_id=context.session_id,
                )
            except ValueError as exc:
                await session.rollback()
                return self._rejected_envelope(
                    "request_checkout", "CHECKOUT_CREATION_FAILED", str(exc)
                )
            except RazorpayError as exc:
                await session.rollback()
                return self._error_envelope(
                    "request_checkout",
                    GatewayErrorCode.COMMERCE_PAYMENT_GATEWAY_ERROR.value,
                    f"Razorpay payment gateway error: {exc}",
                    retryable=True,
                )
            except OptimisticLockError as exc:
                await session.rollback()
                return self._rejected_envelope("request_checkout", "CONCURRENCY_CONFLICT", str(exc))
        else:
            return self._rejected_envelope(
                "request_checkout",
                "INVALID_PARAMETERS",
                "Either order_id or quote_id must be provided to initiate checkout.",
            )

        if order.status in {"PAID", "COMPLETED"}:
            return self._rejected_envelope(
                "request_checkout",
                "ORDER_ALREADY_PAID",
                f"Order '{order.id}' is already paid.",
            )
        if order.status == "CANCELLED":
            return self._rejected_envelope(
                "request_checkout",
                "ORDER_CANCELLED",
                f"Order '{order.id}' has been cancelled.",
            )

        if not order.rzp_order_id:
            return self._rejected_envelope(
                "request_checkout",
                "NO_RZP_ORDER_ID",
                f"Order '{order.id}' does not have a valid external Razorpay order ID.",
            )

        resp_data = RequestCheckoutResponse(
            order_id=order.id,
            rzp_order_id=order.rzp_order_id,
            amount_paise=order.amount_paise,
            currency=order.currency,
            status=order.status,
            key_id=settings.RAZORPAY_KEY_ID,
            supported_payment_methods=["upi", "card", "netbanking", "wallet"],
            callback_url="/api/v1/payments/webhook",
        )
        return GatewayResponseEnvelope[RequestCheckoutResponse](
            status="SUCCESS",
            capability="request_checkout",
            data=resp_data,
            state=StateOrientedContext(
                entity_type="Order",
                entity_id=str(order.id),
                state=order.status,
                version=order.version,
                allowed_actions=["get_payment_status"],
                next_action="Submit payment using Razorpay client SDK or checkout instruments",
            ),
        )

    # -------------------------------------------------------------------------
    # 8. get_payment_status
    # -------------------------------------------------------------------------
    async def get_payment_status(
        self,
        session: AsyncSession,
        request: GetPaymentStatusRequest,
        context: GatewayContext,
    ) -> GatewayResponseEnvelope[GetPaymentStatusResponse]:
        """Retrieves authoritative payment and reconciliation status for an order."""
        auth_ok, auth_err = CapabilityRegistry.check_authorization("get_payment_status", context)
        if not auth_ok:
            return self._rejected_envelope(
                "get_payment_status", "CAPABILITY_DENIED", auth_err or "Unauthorized"
            )

        ord_stmt = (
            select(Order)
            .join(PriceQuote, Order.quote_id == PriceQuote.id)
            .where(
                Order.id == request.order_id,
                Order.merchant_id == context.merchant_id,
                PriceQuote.session_id == context.session_id,
            )
        )
        order = (await session.execute(ord_stmt)).scalar_one_or_none()
        if not order:
            return self._rejected_envelope(
                "get_payment_status",
                "ORDER_NOT_FOUND",
                f"Order with ID '{request.order_id}' not found for authenticated session.",
            )

        # Reconcile if order pending and has external order ID
        if order.status != "PAID" and order.rzp_order_id:
            settings = get_settings()
            rzp_client = RazorpayClient(
                key_id=settings.RAZORPAY_KEY_ID,
                key_secret=settings.RAZORPAY_KEY_SECRET,
                base_url=settings.RAZORPAY_API_BASE_URL,
            )
            try:
                await PaymentService.reconcile_order(
                    session, order.id, rzp_client, merchant_id=context.merchant_id
                )
                await session.refresh(order)
            except Exception as exc:
                logger.warning("Reconciliation check failed during status query: %s", exc)

        pay_stmt = (
            select(PaymentAttempt)
            .where(PaymentAttempt.order_id == order.id)
            .order_by(PaymentAttempt.created_at.desc())
        )
        payments = list((await session.execute(pay_stmt)).scalars().all())
        captured_payment = next((p for p in payments if p.status == "CAPTURED"), None)

        attempt_items = [
            PaymentAttemptItem(
                payment_id=p.id,
                rzp_payment_id=p.rzp_payment_id,
                status=p.status,
                amount_paise=p.amount_paise,
                payment_method=p.payment_method,
                error_code=p.error_code,
                created_at=p.created_at,
            )
            for p in payments
        ]

        resp_data = GetPaymentStatusResponse(
            order_id=order.id,
            order_status=order.status,
            amount_paise=order.amount_paise,
            currency=order.currency,
            is_paid=(order.status == "PAID"),
            rzp_order_id=order.rzp_order_id,
            payment_attempts=attempt_items,
            settled_at=captured_payment.updated_at if captured_payment else None,
        )
        return GatewayResponseEnvelope[GetPaymentStatusResponse](
            status="SUCCESS",
            capability="get_payment_status",
            data=resp_data,
            state=StateOrientedContext(
                entity_type="Order",
                entity_id=str(order.id),
                state=order.status,
                version=order.version,
                allowed_actions=["get_payment_status"] if order.status != "PAID" else [],
                next_action="Order settled and paid"
                if order.status == "PAID"
                else "Awaiting webhook settlement or payment capture",
            ),
        )

    # -------------------------------------------------------------------------
    # 9. Session Lifecycle: initialize_session & terminate_session
    # -------------------------------------------------------------------------
    async def initialize_session(
        self,
        session: AsyncSession,
        request: InitializeSessionRequest,
        merchant_id: uuid.UUID,
    ) -> GatewayResponseEnvelope[InitializeSessionResponse]:
        """Initializes a new authoritative BuyerAgentSession for an external AI buyer."""
        now = datetime.now(UTC)
        expires_at = now + timedelta(minutes=request.duration_minutes)
        raw_token = request.auth_token_raw or f"token_{uuid.uuid4().hex}"
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

        requested_caps = {
            c.strip()
            for c in request.requested_capabilities
            if c.strip() in _ALLOWED_BUYER_CAPABILITIES
        }
        granted_caps = sorted(requested_caps or _ALLOWED_BUYER_CAPABILITIES)

        buyer_session = BuyerAgentSession(
            merchant_id=merchant_id,
            buyer_agent_identifier=request.buyer_agent_identifier,
            auth_token_hash=token_hash,
            granted_capabilities=",".join(granted_caps),
            status="ACTIVE",
            expires_at=expires_at,
        )
        session.add(buyer_session)
        await session.flush()

        audit_event = await AuditEvent.create_event(
            session=session,
            merchant_id=merchant_id,
            actor_type="BUYER_AGENT",
            event_type="BUYER_SESSION_INITIALIZED",
            payload={
                "session_id": str(buyer_session.id),
                "buyer_agent_identifier": request.buyer_agent_identifier,
                "expires_at": expires_at.isoformat(),
            },
            session_id=buyer_session.id,
        )

        resp_data = InitializeSessionResponse(
            session_id=buyer_session.id,
            merchant_id=merchant_id,
            buyer_agent_identifier=request.buyer_agent_identifier,
            status="ACTIVE",
            granted_capabilities=granted_caps,
            auth_token_hash=token_hash,
            expires_at=expires_at,
            created_at=buyer_session.created_at or now,
        )
        return GatewayResponseEnvelope[InitializeSessionResponse](
            status="SUCCESS",
            capability="initialize_session",
            data=resp_data,
            audit_event_id=audit_event.id,
            state=StateOrientedContext(
                entity_type="BuyerAgentSession",
                entity_id=str(buyer_session.id),
                state="ACTIVE",
                allowed_actions=[
                    "discover_products",
                    "get_product",
                    "check_inventory",
                    "get_quote",
                ],
                next_action="Discover catalog products or query specific SKUs",
                expires_at=expires_at,
            ),
        )

    async def terminate_session(
        self,
        session: AsyncSession,
        request: TerminateSessionRequest,
        context: GatewayContext,
    ) -> GatewayResponseEnvelope[TerminateSessionResponse]:
        """Terminates an active BuyerAgentSession."""
        auth_ok, auth_err = CapabilityRegistry.check_authorization("terminate_session", context)
        if not auth_ok:
            return self._rejected_envelope(
                "terminate_session", "CAPABILITY_DENIED", auth_err or "Unauthorized"
            )

        if request.session_id != context.session_id:
            return self._rejected_envelope(
                "terminate_session",
                "UNAUTHORIZED_SESSION",
                (
                    f"Session ID '{request.session_id}' does not match "
                    f"active gateway session '{context.session_id}'."
                ),
            )

        stmt = select(BuyerAgentSession).where(
            BuyerAgentSession.id == request.session_id,
            BuyerAgentSession.merchant_id == context.merchant_id,
        )
        sess = (await session.execute(stmt)).scalar_one_or_none()
        if not sess:
            return self._rejected_envelope(
                "terminate_session",
                "SESSION_NOT_FOUND",
                f"Session with ID '{request.session_id}' not found.",
            )

        if sess.status in {"TERMINATED", "EXPIRED"}:
            return self._rejected_envelope(
                "terminate_session",
                "SESSION_ALREADY_TERMINATED",
                f"Session '{request.session_id}' is already {sess.status.lower()}.",
            )

        sess.status = "TERMINATED"
        now = datetime.now(UTC)
        await session.flush()

        audit_event = await AuditEvent.create_event(
            session=session,
            merchant_id=context.merchant_id,
            actor_type="BUYER_AGENT",
            event_type="BUYER_SESSION_TERMINATED",
            payload={
                "session_id": str(sess.id),
                "reason": request.reason,
            },
            session_id=sess.id,
        )

        resp_data = TerminateSessionResponse(
            session_id=sess.id,
            status="TERMINATED",
            terminated_at=now,
        )
        return GatewayResponseEnvelope[TerminateSessionResponse](
            status="SUCCESS",
            capability="terminate_session",
            data=resp_data,
            audit_event_id=audit_event.id,
            state=StateOrientedContext(
                entity_type="BuyerAgentSession",
                entity_id=str(sess.id),
                state="TERMINATED",
                allowed_actions=[],
                next_action="Session terminated; no further actions permitted",
            ),
        )

    # -------------------------------------------------------------------------
    # 10. Quote Negotiation & Acceptance
    # -------------------------------------------------------------------------
    async def negotiate_quote(
        self,
        session: AsyncSession,
        request: NegotiateQuoteGatewayRequest,
        context: GatewayContext,
    ) -> GatewayResponseEnvelope[NegotiateQuoteGatewayResponse]:
        """Submits a bounded price counter-offer against an active PriceQuote."""
        auth_ok, auth_err = CapabilityRegistry.check_authorization("negotiate_quote", context)
        if not auth_ok:
            return self._rejected_envelope(
                "negotiate_quote", "CAPABILITY_DENIED", auth_err or "Unauthorized"
            )

        stmt = (
            select(PriceQuote)
            .options(
                selectinload(PriceQuote.items)
                .selectinload(QuoteItem.variant)
                .selectinload(ProductVariant.product)
            )
            .where(
                PriceQuote.id == request.quote_id,
                PriceQuote.merchant_id == context.merchant_id,
                PriceQuote.session_id == context.session_id,
            )
        )
        quote = (await session.execute(stmt)).scalar_one_or_none()
        if not quote:
            return self._rejected_envelope(
                "negotiate_quote",
                "QUOTE_NOT_FOUND",
                f"PriceQuote '{request.quote_id}' not found for active merchant and session.",
            )

        now = datetime.now(UTC)
        quote_expires = (
            quote.expires_at
            if quote.expires_at.tzinfo is not None
            else quote.expires_at.replace(tzinfo=UTC)
        )
        if now > quote_expires:
            return self._rejected_envelope(
                "negotiate_quote",
                "QUOTE_EXPIRED",
                f"PriceQuote '{request.quote_id}' expired at {quote_expires.isoformat()}.",
            )

        if quote.status not in {"PROPOSED", "NEGOTIATING"}:
            return self._rejected_envelope(
                "negotiate_quote",
                "INVALID_STATE",
                (
                    f"Cannot negotiate quote in status '{quote.status}', "
                    "must be 'PROPOSED' or 'NEGOTIATING'."
                ),
            )

        proposed_goods_paise = max(0, request.proposed_total_paise - quote.shipping_paise)
        item_proposals: list[QuoteItemProposal] = []
        for itm in quote.items:
            prod = itm.variant.product
            prop_share = itm.total_price_paise / max(1, quote.subtotal_paise)
            item_proposed_total = int(proposed_goods_paise * prop_share)
            item_proposed_unit = item_proposed_total // max(1, itm.quantity)
            item_proposals.append(
                QuoteItemProposal(
                    sku=prod.sku,
                    quantity=itm.quantity,
                    unit_base_price_paise=itm.unit_price_paise,
                    unit_floor_price_paise=prod.floor_price_paise,
                    proposed_unit_price_paise=item_proposed_unit,
                    unit_cost_price_paise=int(prod.floor_price_paise * 0.8),
                    is_negotiable=prod.is_negotiable,
                )
            )

        calculated_discount = max(0, quote.subtotal_paise - proposed_goods_paise)
        proposal = QuoteProposal(
            items=item_proposals,
            subtotal_paise=quote.subtotal_paise,
            discount_paise=calculated_discount,
            shipping_paise=quote.shipping_paise,
            total_paise=request.proposed_total_paise,
        )
        policy_ctx = PolicyContext(
            merchant_autonomy_level=context.autonomy_level,
            max_discount_percentage=context.max_discount_percentage,
            min_margin_percentage=context.min_margin_percentage,
            max_single_transaction_paise=context.max_single_transaction_paise,
            session_capabilities=context.capabilities,
        )
        eval_res = DeterministicPolicyEngine.evaluate_quote(
            proposal, policy_ctx, required_capability="buyer:negotiate"
        )

        if eval_res.verdict == PolicyVerdict.DENY:
            return self._rejected_envelope(
                "negotiate_quote",
                eval_res.rule_code or "POLICY_REJECTED",
                f"Counter-offer rejected by policy: {eval_res.reason}",
            )
        elif eval_res.verdict == PolicyVerdict.ESCALATE_APPROVAL:
            resp_data = NegotiateQuoteGatewayResponse(
                quote_id=quote.id,
                status="PENDING_APPROVAL",
                currency="INR",
                subtotal_paise=quote.subtotal_paise,
                discount_paise=quote.discount_paise,
                shipping_paise=quote.shipping_paise,
                total_paise=quote.total_paise,
                verdict="ESCALATE_APPROVAL",
                rule_code=eval_res.rule_code,
                reason=f"Counter-offer requires merchant human approval: {eval_res.reason}",
                expires_at=quote.expires_at,
            )
            return GatewayResponseEnvelope[NegotiateQuoteGatewayResponse](
                status="SUCCESS",
                capability="negotiate_quote",
                data=resp_data,
                state=StateOrientedContext(
                    entity_type="PriceQuote",
                    entity_id=str(quote.id),
                    state=quote.status,
                    version=quote.version,
                    allowed_actions=["get_quote", "terminate_session"],
                    next_action="Awaiting merchant approval for counter-offer",
                    expires_at=quote.expires_at,
                ),
            )

        # Policy ALLOW: advance quote state
        # Apply negotiated per-line prices keeping every line feasible under
        # ck_*_items_total_arithmetic (total_price_paise = unit_price_paise * quantity).
        for itm, prop in zip(quote.items, item_proposals, strict=False):
            itm.unit_price_paise = prop.proposed_unit_price_paise
            itm.total_price_paise = prop.proposed_unit_price_paise * itm.quantity

        item_sum = sum(itm.total_price_paise for itm in quote.items)
        remainder = proposed_goods_paise - item_sum
        if remainder != 0 and quote.items:
            # Prefer absorbing rounding residue into a quantity-1 line where any
            # total is arithmetically valid.
            unit_line = next((i for i in quote.items if i.quantity == 1), None)
            if unit_line is not None and unit_line.total_price_paise + remainder > 0:
                unit_line.total_price_paise += remainder
                unit_line.unit_price_paise = unit_line.total_price_paise

        # True up quote-level totals against the feasible line sums so
        # ck_price_quotes_total_arithmetic holds without violating per-line
        # arithmetic (subtotal_paise itself is FSM-immutable).
        final_subtotal = sum(itm.total_price_paise for itm in quote.items)
        final_discount = max(0, quote.subtotal_paise - final_subtotal)
        final_total = quote.subtotal_paise - final_discount + quote.shipping_paise

        if quote.status == "PROPOSED":
            await PriceQuoteStateMachine.transition(
                session=session,
                quote=quote,
                target_state="NEGOTIATING",
                expected_version=quote.version,
                actor_type="BUYER_AGENT",
                reason="Buyer counter-offer submitted",
            )
        await PriceQuoteStateMachine.transition(
            session=session,
            quote=quote,
            target_state="PROPOSED",
            expected_version=quote.version,
            actor_type="BUYER_AGENT",
            reason="Counter-offer accepted by policy",
            additional_updates={
                "discount_paise": final_discount,
                "total_paise": final_total,
                "discount_reason": request.rationale or "Negotiated discount approved",
            },
        )
        await session.flush()

        audit_event = await AuditEvent.create_event(
            session=session,
            merchant_id=context.merchant_id,
            actor_type="BUYER_AGENT",
            event_type="PRICE_QUOTE_NEGOTIATED",
            payload={
                "quote_id": str(quote.id),
                "proposed_total_paise": request.proposed_total_paise,
                "applied_discount_paise": final_discount,
                "applied_total_paise": final_total,
                "verdict": "ALLOW",
            },
            session_id=context.session_id,
        )

        resp_data = NegotiateQuoteGatewayResponse(
            quote_id=quote.id,
            status="PROPOSED",
            currency="INR",
            subtotal_paise=quote.subtotal_paise,
            discount_paise=final_discount,
            shipping_paise=quote.shipping_paise,
            total_paise=final_total,
            verdict="ALLOW",
            rule_code=eval_res.rule_code,
            reason="Counter-offer within authorized autonomy bounds",
            expires_at=quote.expires_at,
        )
        return GatewayResponseEnvelope[NegotiateQuoteGatewayResponse](
            status="SUCCESS",
            capability="negotiate_quote",
            data=resp_data,
            audit_event_id=audit_event.id,
            state=StateOrientedContext(
                entity_type="PriceQuote",
                entity_id=str(quote.id),
                state="PROPOSED",
                version=quote.version,
                allowed_actions=["accept_quote", "negotiate_quote", "get_quote"],
                next_action="Accept negotiated quote or propose alternative terms before expiry",
                expires_at=quote.expires_at,
            ),
        )

    async def accept_quote(
        self,
        session: AsyncSession,
        request: AcceptQuoteGatewayRequest,
        context: GatewayContext,
    ) -> GatewayResponseEnvelope[AcceptQuoteGatewayResponse]:
        """Accepts an active PROPOSED PriceQuote and locks terms for checkout."""
        auth_ok, auth_err = CapabilityRegistry.check_authorization("accept_quote", context)
        if not auth_ok:
            return self._rejected_envelope(
                "accept_quote", "CAPABILITY_DENIED", auth_err or "Unauthorized"
            )

        stmt = select(PriceQuote).where(
            PriceQuote.id == request.quote_id,
            PriceQuote.merchant_id == context.merchant_id,
            PriceQuote.session_id == context.session_id,
        )
        quote = (await session.execute(stmt)).scalar_one_or_none()
        if not quote:
            return self._rejected_envelope(
                "accept_quote",
                "QUOTE_NOT_FOUND",
                f"PriceQuote '{request.quote_id}' not found for active merchant and session.",
            )

        now = datetime.now(UTC)
        quote_expires = (
            quote.expires_at
            if quote.expires_at.tzinfo is not None
            else quote.expires_at.replace(tzinfo=UTC)
        )
        if now > quote_expires:
            return self._rejected_envelope(
                "accept_quote",
                "QUOTE_EXPIRED",
                f"PriceQuote '{request.quote_id}' expired at {quote_expires.isoformat()}.",
            )

        if quote.status == "ACCEPTED":
            resp_data = AcceptQuoteGatewayResponse(
                quote_id=quote.id,
                status="ACCEPTED",
                total_paise=quote.total_paise,
                currency="INR",
                accepted_at=now,
                expires_at=quote.expires_at,
            )
            return GatewayResponseEnvelope[AcceptQuoteGatewayResponse](
                status="SUCCESS",
                capability="accept_quote",
                data=resp_data,
                state=StateOrientedContext(
                    entity_type="PriceQuote",
                    entity_id=str(quote.id),
                    state="ACCEPTED",
                    version=quote.version,
                    allowed_actions=["create_order", "request_checkout"],
                    next_action="Proceed to create order or checkout",
                    expires_at=quote.expires_at,
                ),
            )

        if quote.status != "PROPOSED":
            return self._rejected_envelope(
                "accept_quote",
                "INVALID_STATE_TRANSITION",
                f"Cannot accept quote in state '{quote.status}', must be 'PROPOSED'.",
            )

        await PriceQuoteStateMachine.transition(
            session=session,
            quote=quote,
            target_state="ACCEPTED",
            expected_version=quote.version,
            actor_type="BUYER_AGENT",
            reason="Buyer agent accepted quote terms",
        )
        await session.flush()

        audit_event = await AuditEvent.create_event(
            session=session,
            merchant_id=context.merchant_id,
            actor_type="BUYER_AGENT",
            event_type="PRICE_QUOTE_ACCEPTED",
            payload={
                "quote_id": str(quote.id),
                "total_paise": quote.total_paise,
            },
            session_id=context.session_id,
        )

        resp_data = AcceptQuoteGatewayResponse(
            quote_id=quote.id,
            status="ACCEPTED",
            total_paise=quote.total_paise,
            currency="INR",
            accepted_at=now,
            expires_at=quote.expires_at,
        )
        return GatewayResponseEnvelope[AcceptQuoteGatewayResponse](
            status="SUCCESS",
            capability="accept_quote",
            data=resp_data,
            audit_event_id=audit_event.id,
            state=StateOrientedContext(
                entity_type="PriceQuote",
                entity_id=str(quote.id),
                state="ACCEPTED",
                version=quote.version,
                allowed_actions=["create_order", "request_checkout"],
                next_action="Proceed to create order or checkout",
                expires_at=quote.expires_at,
            ),
        )

    # -------------------------------------------------------------------------
    # 11. get_order_status
    # -------------------------------------------------------------------------
    async def get_order_status(
        self,
        session: AsyncSession,
        request: GetOrderStatusRequest,
        context: GatewayContext,
    ) -> GatewayResponseEnvelope[GetOrderStatusResponse]:
        """Retrieves authoritative order details, fulfillment status, and settlement."""
        auth_ok, auth_err = CapabilityRegistry.check_authorization("get_order_status", context)
        if not auth_ok:
            return self._rejected_envelope(
                "get_order_status", "CAPABILITY_DENIED", auth_err or "Unauthorized"
            )

        stmt = (
            select(Order)
            .join(PriceQuote, Order.quote_id == PriceQuote.id)
            .where(
                Order.id == request.order_id,
                Order.merchant_id == context.merchant_id,
                PriceQuote.session_id == context.session_id,
            )
        )
        order = (await session.execute(stmt)).scalar_one_or_none()
        if not order:
            return self._rejected_envelope(
                "get_order_status",
                "ORDER_NOT_FOUND",
                f"Order '{request.order_id}' not found for active session.",
            )

        resp_data = GetOrderStatusResponse(
            order_id=order.id,
            quote_id=order.quote_id,
            status=order.status,
            amount_paise=order.amount_paise,
            currency=order.currency,
            buyer_email=order.buyer_email,
            rzp_order_id=order.rzp_order_id,
            shipping_address=ShippingAddressGateway.model_validate(order.shipping_address),
            created_at=order.created_at,
            is_settled=(order.status in {"PAID", "FULFILLMENT_PENDING", "COMPLETED"}),
        )
        allowed = []
        if order.status == "PENDING_PAYMENT":
            allowed = ["request_checkout", "get_payment_status"]
        elif order.status in {"PAID", "COMPLETED", "FULFILLMENT_PENDING"}:
            allowed = ["get_order_status"]

        return GatewayResponseEnvelope[GetOrderStatusResponse](
            status="SUCCESS",
            capability="get_order_status",
            data=resp_data,
            state=StateOrientedContext(
                entity_type="Order",
                entity_id=str(order.id),
                state=order.status,
                version=order.version,
                allowed_actions=allowed,
                next_action=(
                    "Order completed and settled"
                    if order.status in {"PAID", "COMPLETED"}
                    else (
                        "Order paid and awaiting fulfillment"
                        if order.status == "FULFILLMENT_PENDING"
                        else "Awaiting payment settlement"
                    )
                ),
            ),
        )

    # -------------------------------------------------------------------------
    # Unified Capability Dispatcher
    # -------------------------------------------------------------------------
    async def execute_capability(
        self,
        session: AsyncSession,
        capability_name: str,
        payload: dict[str, Any],
        context: GatewayContext,
    ) -> GatewayResponseEnvelope[Any]:
        """Dispatches untrusted capability payload through strict validation and execution."""
        start_time = time.time()
        settings = get_settings()
        request_id = context.request_id or uuid.uuid4()
        idempotency_key = payload.get("idempotency_key") or context.idempotency_key

        # 1. Check capability registration
        cap_def = CapabilityRegistry.get_capability(capability_name)
        if not cap_def:
            return self._rejected_envelope(
                capability_name,
                GatewayErrorCode.UNKNOWN_CAPABILITY.value,
                f"Capability '{capability_name}' is not registered in the canonical registry.",
                request_id=request_id,
            )

        # 1b. Schema Version Check
        if context.schema_version and context.schema_version != COMMERCE_PROTOCOL_VERSION:
            return self._error_envelope(
                capability_name,
                GatewayErrorCode.UNSUPPORTED_PROTOCOL_VERSION.value,
                (
                    f"Unsupported protocol version '{context.schema_version}'. "
                    f"Expected '{COMMERCE_PROTOCOL_VERSION}'."
                ),
                retryable=False,
                request_id=request_id,
            )

        # 1c. Mandatory Idempotency Requirement Check
        if cap_def.idempotency_requirement and not idempotency_key:
            return self._rejected_envelope(
                capability_name,
                GatewayErrorCode.IDEMPOTENCY_REQUIRED.value,
                f"Capability '{capability_name}' requires a non-empty idempotency key.",
                request_id=request_id,
            )

        # 1d. Authoritative Session Validation & Capability Derivation
        if capability_name != "initialize_session" and context.session_id:
            sess_stmt = select(BuyerAgentSession).where(
                BuyerAgentSession.id == context.session_id,
                BuyerAgentSession.merchant_id == context.merchant_id,
            )
            db_sess = (await session.execute(sess_stmt)).scalar_one_or_none()
            if not db_sess:
                return self._rejected_envelope(
                    capability_name,
                    GatewayErrorCode.AUTH_SESSION_NOT_FOUND.value,
                    f"Session '{context.session_id}' not found for authenticated merchant.",
                    request_id=request_id,
                )
            if db_sess.status != "ACTIVE":
                return self._rejected_envelope(
                    capability_name,
                    GatewayErrorCode.AUTH_SESSION_EXPIRED.value,
                    f"Session '{context.session_id}' is not active (status: {db_sess.status}).",
                    request_id=request_id,
                )
            now = datetime.now(UTC)
            sess_exp = (
                db_sess.expires_at
                if db_sess.expires_at.tzinfo is not None
                else db_sess.expires_at.replace(tzinfo=UTC)
            )
            if now > sess_exp:
                db_sess.status = "EXPIRED"
                await session.flush()
                return self._rejected_envelope(
                    capability_name,
                    GatewayErrorCode.AUTH_SESSION_EXPIRED.value,
                    f"Session '{context.session_id}' has expired.",
                    request_id=request_id,
                )

            # Authoritative Token Authentication: fail-closed verification
            if db_sess.auth_token_hash:
                if not context.auth_token:
                    return self._rejected_envelope(
                        capability_name,
                        GatewayErrorCode.AUTH_INVALID_CREDENTIAL.value,
                        "Authentication token required for active session.",
                        request_id=request_id,
                    )
                presented_hash = hashlib.sha256(context.auth_token.encode("utf-8")).hexdigest()
                if presented_hash != db_sess.auth_token_hash:
                    return self._rejected_envelope(
                        capability_name,
                        GatewayErrorCode.AUTH_INVALID_CREDENTIAL.value,
                        "Invalid session authentication token.",
                        request_id=request_id,
                    )

            # Server-authoritative capability derivation: narrow request-derived
            # grants to the persisted session grant. Sessions without a stored
            # grant (legacy rows) retain the previous default-grant behavior.
            stored_caps_raw = db_sess.granted_capabilities
            if stored_caps_raw:
                stored_caps = {c.strip() for c in stored_caps_raw.split(",") if c.strip()}
                context.capabilities = context.capabilities & stored_caps

        # 2. Bounded Payload Size Validation (Max 64 KB)
        is_payload_valid, payload_size = validate_payload_size(payload)
        if not is_payload_valid:
            return self._error_envelope(
                capability_name,
                GatewayErrorCode.PAYLOAD_SIZE_EXCEEDED.value,
                f"Payload size {payload_size} bytes exceeds maximum allowed limit (65536 bytes).",
                request_id=request_id,
            )

        # 3. Sliding-Window Rate Limiting Check
        client_key = str(context.session_id or context.merchant_id)
        rate_limit = getattr(settings, "GATEWAY_RATE_LIMIT_PER_MINUTE", 60)
        is_allowed, retry_after = await global_rate_limiter.check_rate_limit(
            client_key=client_key,
            limit=rate_limit,
            window_seconds=60,
        )
        if not is_allowed:
            return self._rejected_envelope(
                capability_name,
                GatewayErrorCode.RATE_LIMIT_EXCEEDED.value,
                f"Rate limit exceeded for session. Retry after {retry_after} seconds.",
                details={"retry_after_seconds": retry_after},
                request_id=request_id,
            )

        # 4. Idempotency Check
        if idempotency_key:
            cached_resp = await global_idempotency_manager.check_idempotency(
                merchant_id=context.merchant_id,
                session_id=context.session_id,
                idempotency_key=idempotency_key,
                capability=capability_name,
                payload=payload,
            )
            if cached_resp is not None:
                return cached_resp

            lock_acquired = await global_idempotency_manager.acquire_mutation_lock(
                merchant_id=context.merchant_id,
                session_id=context.session_id,
                idempotency_key=idempotency_key,
                capability=capability_name,
            )
            if not lock_acquired:
                return self._rejected_envelope(
                    capability_name,
                    GatewayErrorCode.IDEMPOTENCY_CONFLICT.value,
                    f"A request with idempotency key '{idempotency_key}' is currently executing.",
                    request_id=request_id,
                )

        try:
            # 5. Execute with Timeout Boundary (10.0 seconds default)
            timeout_sec = getattr(settings, "GATEWAY_REQUEST_TIMEOUT_SECONDS", 10.0)
            async with asyncio.timeout(timeout_sec):
                result_envelope = await self._dispatch_internal(
                    session=session,
                    capability_name=capability_name,
                    payload=payload,
                    context=context,
                )

            # Ensure trace identifiers are populated
            result_envelope.request_id = request_id
            if idempotency_key and not result_envelope.idempotency_key:
                result_envelope.idempotency_key = idempotency_key

            # Record Idempotency Cache for successful/rejected mutations
            if idempotency_key:
                await global_idempotency_manager.record_idempotency(
                    merchant_id=context.merchant_id,
                    session_id=context.session_id,
                    idempotency_key=idempotency_key,
                    envelope=result_envelope,
                    capability=capability_name,
                    payload=payload,
                )

            return result_envelope

        except TimeoutError:
            await session.rollback()
            logger.error(
                "Timeout boundary exceeded during capability execution: %s",
                capability_name,
            )
            is_financial = cap_def.classification == "PRIVILEGED_FINANCIAL"
            return self._error_envelope(
                capability_name,
                GatewayErrorCode.TIMEOUT_BOUNDARY_EXCEEDED.value,
                f"Execution timeout of {timeout_sec}s exceeded for capability '{capability_name}'.",
                retryable=not is_financial,
                request_id=request_id,
            )
        except ValidationError as exc:
            logger.warning("Gateway payload validation failed for '%s': %s", capability_name, exc)
            return self._error_envelope(
                capability_name,
                GatewayErrorCode.MALFORMED_REQUEST_SCHEMA.value,
                f"Schema validation error: {exc}",
                retryable=False,
                request_id=request_id,
            )
        except Exception as exc:
            await session.rollback()
            return sanitize_error_response(
                capability=capability_name,
                exc=exc,
                request_id=request_id,
                is_testing=settings.is_testing,
            )
        finally:
            if idempotency_key:
                await global_idempotency_manager.release_mutation_lock(
                    merchant_id=context.merchant_id,
                    session_id=context.session_id,
                    idempotency_key=idempotency_key,
                    capability=capability_name,
                )
            duration_ms = (time.time() - start_time) * 1000.0
            logger.debug(
                "Gateway capability executed: capability=%s merchant_id=%s "
                "session_id=%s duration_ms=%.2f",
                capability_name,
                context.merchant_id,
                context.session_id,
                duration_ms,
            )

    async def _dispatch_internal(
        self,
        session: AsyncSession,
        capability_name: str,
        payload: dict[str, Any],
        context: GatewayContext,
    ) -> GatewayResponseEnvelope[Any]:
        """Internal router mapping validated capability calls to concrete methods."""
        if capability_name == "initialize_session":
            req_sess = InitializeSessionRequest.model_validate(payload)
            return await self.initialize_session(session, req_sess, context.merchant_id)

        elif capability_name == "terminate_session":
            req_term = TerminateSessionRequest.model_validate(payload)
            return await self.terminate_session(session, req_term, context)

        elif capability_name == "discover_products":
            req_disc = DiscoverProductsRequest.model_validate(payload)
            return await self.discover_products(session, req_disc, context)

        elif capability_name == "get_product":
            req_prod = GetProductRequest.model_validate(payload)
            return await self.get_product(session, req_prod, context)

        elif capability_name == "check_inventory":
            req_inv = CheckInventoryRequest.model_validate(payload)
            return await self.check_inventory(session, req_inv, context)

        elif capability_name == "get_quote":
            req_q = GetQuoteRequest.model_validate(payload)
            return await self.get_quote(session, req_q, context)

        elif capability_name == "negotiate_quote":
            req_neg = NegotiateQuoteGatewayRequest.model_validate(payload)
            return await self.negotiate_quote(session, req_neg, context)

        elif capability_name == "accept_quote":
            req_acc = AcceptQuoteGatewayRequest.model_validate(payload)
            return await self.accept_quote(session, req_acc, context)

        elif capability_name == "calculate_shipping":
            req_ship = CalculateShippingRequest.model_validate(payload)
            return await self.calculate_shipping(session, req_ship, context)

        elif capability_name == "create_order":
            req_ord = CreateOrderGatewayRequest.model_validate(payload)
            return await self.create_order(session, req_ord, context)

        elif capability_name == "request_checkout":
            req_chk = RequestCheckoutRequest.model_validate(payload)
            return await self.request_checkout(session, req_chk, context)

        elif capability_name == "get_payment_status":
            req_pay = GetPaymentStatusRequest.model_validate(payload)
            return await self.get_payment_status(session, req_pay, context)

        elif capability_name == "get_order_status":
            req_ord_stat = GetOrderStatusRequest.model_validate(payload)
            return await self.get_order_status(session, req_ord_stat, context)

        else:
            return self._rejected_envelope(
                capability_name,
                "UNHANDLED_CAPABILITY",
                f"Capability '{capability_name}' lacks a dispatcher mapping.",
            )

    # -------------------------------------------------------------------------
    # Helper Envelope Generators
    # -------------------------------------------------------------------------
    def _rejected_envelope(
        self,
        capability: str,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
        request_id: uuid.UUID | None = None,
        idempotency_key: str | None = None,
    ) -> GatewayResponseEnvelope[Any]:
        return GatewayResponseEnvelope[Any](
            status="REJECTED",
            capability=capability,
            data=None,
            error=GatewayError(code=code, message=message, retryable=False, details=details),
            request_id=request_id or uuid.uuid4(),
            idempotency_key=idempotency_key,
        )

    def _error_envelope(
        self,
        capability: str,
        code: str,
        message: str,
        retryable: bool = False,
        details: dict[str, Any] | None = None,
        request_id: uuid.UUID | None = None,
        idempotency_key: str | None = None,
    ) -> GatewayResponseEnvelope[Any]:
        return GatewayResponseEnvelope[Any](
            status="ERROR",
            capability=capability,
            data=None,
            error=GatewayError(code=code, message=message, retryable=retryable, details=details),
            request_id=request_id or uuid.uuid4(),
            idempotency_key=idempotency_key,
        )
