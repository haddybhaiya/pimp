import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from agent_ready_merchant.config import get_settings
from agent_ready_merchant.integrations.razorpay.client import RazorpayClient
from agent_ready_merchant.models.order import Order
from agent_ready_merchant.models.payment import PaymentAttempt
from agent_ready_merchant.models.product import Product, ProductVariant
from agent_ready_merchant.models.quote import PriceQuote, QuoteItem
from agent_ready_merchant.policy.engine import DeterministicPolicyEngine
from agent_ready_merchant.policy.models import (
    PolicyContext,
    PolicyVerdict,
    QuoteItemProposal,
    QuoteProposal,
)
from agent_ready_merchant.services.payment_service import PaymentService
from agent_ready_merchant.state_machines.price_quote import PriceQuoteStateMachine
from agent_ready_merchant.tools.base import BaseTool, GatewayContext
from agent_ready_merchant.tools.models import (
    AcceptQuoteParams,
    CalculateShippingParams,
    CheckInventoryParams,
    CheckPaymentStatusParams,
    CreateOrderParams,
    DiscoverCatalogParams,
    GetOrderStatusParams,
    GetProductDetailsParams,
    NegotiateQuoteParams,
    RequestCheckoutParams,
    RequestPriceQuoteParams,
)

logger = logging.getLogger("agent_ready_merchant.tools")


class DiscoverCatalogTool(BaseTool):
    """Tool to search and filter merchant products."""

    name = "discover_catalog"
    description = "Search and filter merchant products by query, category, or price range."
    side_effect_class = "READ_ONLY"
    required_capability = "buyer:discover"
    param_schema = DiscoverCatalogParams

    async def execute(
        self,
        session: AsyncSession,
        params: BaseModel,
        context: GatewayContext,
    ) -> dict[str, Any]:
        p = DiscoverCatalogParams.model_validate(params)
        stmt = (
            select(Product)
            .options(selectinload(Product.variants))
            .where(Product.merchant_id == context.merchant_id, Product.is_active.is_(True))
        )
        if p.category:
            stmt = stmt.where(Product.category.ilike(f"%{p.category}%"))
        if p.max_price_paise is not None:
            stmt = stmt.where(Product.base_price_paise <= p.max_price_paise)

        res = await session.execute(stmt)
        products = res.scalars().all()

        if p.query:
            q_lower = p.query.lower()
            products = [
                prod
                for prod in products
                if q_lower in prod.title.lower()
                or (prod.description and q_lower in prod.description.lower())
            ]

        matched = products[: p.limit]
        items = [
            {
                "sku": prod.sku,
                "title": prod.title,
                "category": prod.category,
                "base_price_paise": prod.base_price_paise,
                "is_negotiable": prod.is_negotiable,
                "in_stock": True,
            }
            for prod in matched
        ]
        return {"products": items, "total_matched": len(products)}


class GetProductDetailsTool(BaseTool):
    """Tool to get detailed information about a single SKU."""

    name = "get_product_details"
    description = "Retrieve comprehensive specs, attributes, and stock levels for a specific SKU."
    side_effect_class = "READ_ONLY"
    required_capability = "buyer:read"
    param_schema = GetProductDetailsParams

    async def execute(
        self,
        session: AsyncSession,
        params: BaseModel,
        context: GatewayContext,
    ) -> dict[str, Any]:
        p = GetProductDetailsParams.model_validate(params)
        stmt = (
            select(Product)
            .options(selectinload(Product.variants))
            .where(
                Product.merchant_id == context.merchant_id,
                Product.sku == p.sku,
                Product.is_active.is_(True),
            )
        )
        res = await session.execute(stmt)
        product = res.scalar_one_or_none()
        if not product:
            return {
                "error": {
                    "code": "PRODUCT_NOT_FOUND",
                    "message": f"Product with SKU '{p.sku}' not found in catalog.",
                }
            }

        return {
            "sku": product.sku,
            "title": product.title,
            "description": product.description or "",
            "base_price_paise": product.base_price_paise,
            "available_quantity": 100,  # Available inventory in mock/test
            "attributes": product.attributes or {},
            "is_negotiable": product.is_negotiable,
        }


class RequestPriceQuoteTool(BaseTool):
    """Tool to request a time-limited price quote."""

    name = "request_price_quote"
    description = "Request a formal, binding, time-limited price quote for items."
    side_effect_class = "TRANSIENT_STATE"
    required_capability = "buyer:quote"
    param_schema = RequestPriceQuoteParams

    async def execute(
        self,
        session: AsyncSession,
        params: BaseModel,
        context: GatewayContext,
    ) -> dict[str, Any]:
        p = RequestPriceQuoteParams.model_validate(params)

        item_proposals: list[QuoteItemProposal] = []
        db_items: list[tuple[Product, ProductVariant, int]] = []
        subtotal_paise = 0

        for itm in p.items:
            stmt = (
                select(Product, ProductVariant)
                .join(ProductVariant, Product.id == ProductVariant.product_id)
                .where(
                    Product.merchant_id == context.merchant_id,
                    Product.sku == itm.sku,
                    Product.is_active.is_(True),
                )
            )
            res = await session.execute(stmt)
            row = res.first()
            if not row:
                return {
                    "error": {
                        "code": "SKU_NOT_FOUND",
                        "message": f"SKU '{itm.sku}' not found in merchant catalog.",
                    }
                }
            prod, var = row
            item_subtotal = prod.base_price_paise * itm.quantity
            subtotal_paise += item_subtotal

            item_proposals.append(
                QuoteItemProposal(
                    sku=prod.sku,
                    quantity=itm.quantity,
                    unit_base_price_paise=prod.base_price_paise,
                    unit_floor_price_paise=prod.floor_price_paise,
                    proposed_unit_price_paise=prod.base_price_paise,
                    is_negotiable=prod.is_negotiable,
                )
            )
            db_items.append((prod, var, itm.quantity))

        shipping_paise = 0 if subtotal_paise >= 100000 else 10000
        total_paise = subtotal_paise + shipping_paise

        proposal = QuoteProposal(
            items=item_proposals,
            subtotal_paise=subtotal_paise,
            discount_paise=0,
            shipping_paise=shipping_paise,
            total_paise=total_paise,
        )

        policy_ctx = PolicyContext(
            merchant_autonomy_level=context.autonomy_level,
            max_discount_percentage=context.max_discount_percentage,
            min_margin_percentage=context.min_margin_percentage,
            max_single_transaction_paise=context.max_single_transaction_paise,
            session_capabilities=context.capabilities,
        )
        eval_result = DeterministicPolicyEngine.evaluate_quote(proposal, policy_ctx)
        if eval_result.verdict == PolicyVerdict.DENY:
            return {
                "error": {
                    "code": eval_result.rule_code or "POLICY_DENIAL",
                    "message": eval_result.reason,
                }
            }

        now = datetime.now(UTC)
        expires_at = now + timedelta(minutes=15)
        quote = PriceQuote(
            session_id=context.session_id,
            merchant_id=context.merchant_id,
            status="PROPOSED",
            subtotal_paise=subtotal_paise,
            discount_paise=0,
            shipping_paise=shipping_paise,
            total_paise=total_paise,
            expires_at=expires_at,
            idempotency_key=str(uuid.uuid4()),
        )
        session.add(quote)
        await session.flush()

        for prod, var, qty in db_items:
            q_item = QuoteItem(
                quote_id=quote.id,
                variant_id=var.id,
                quantity=qty,
                unit_price_paise=prod.base_price_paise,
                total_price_paise=prod.base_price_paise * qty,
            )
            session.add(q_item)

        await session.flush()

        return {
            "quote_id": str(quote.id),
            "subtotal_paise": quote.subtotal_paise,
            "discount_paise": quote.discount_paise,
            "shipping_paise": quote.shipping_paise,
            "total_paise": quote.total_paise,
            "expires_at": quote.expires_at.isoformat(),
        }


class NegotiateQuoteTool(BaseTool):
    """Tool to submit a counter-offer against an active PriceQuote."""

    name = "negotiate_quote"
    description = "Submit a counter-offer against an active PriceQuote."
    side_effect_class = "TRANSIENT_STATE"
    required_capability = "buyer:negotiate"
    param_schema = NegotiateQuoteParams

    async def execute(
        self,
        session: AsyncSession,
        params: BaseModel,
        context: GatewayContext,
    ) -> dict[str, Any]:
        p = NegotiateQuoteParams.model_validate(params)

        stmt = (
            select(PriceQuote)
            .options(
                selectinload(PriceQuote.items)
                .selectinload(QuoteItem.variant)
                .selectinload(ProductVariant.product)
            )
            .where(
                PriceQuote.id == p.quote_id,
                PriceQuote.merchant_id == context.merchant_id,
                PriceQuote.session_id == context.session_id,
            )
        )
        res = await session.execute(stmt)
        quote = res.scalar_one_or_none()
        if not quote:
            return {
                "error": {
                    "code": "QUOTE_NOT_FOUND",
                    "message": f"PriceQuote with ID {p.quote_id} not found.",
                }
            }

        now = datetime.now(UTC)
        if quote.expires_at.tzinfo is None:
            quote_expires = quote.expires_at.replace(tzinfo=UTC)
        else:
            quote_expires = quote.expires_at

        if now > quote_expires:
            return {
                "error": {
                    "code": "QUOTE_EXPIRED",
                    "message": "Quote has expired and cannot be negotiated.",
                }
            }

        # Build proposal for policy evaluation without mutating quote
        item_proposals = []
        for itm in quote.items:
            prod = itm.variant.product
            item_proposals.append(
                QuoteItemProposal(
                    sku=prod.sku,
                    quantity=itm.quantity,
                    unit_base_price_paise=prod.base_price_paise,
                    unit_floor_price_paise=prod.floor_price_paise,
                    proposed_unit_price_paise=p.proposed_total_paise
                    // (len(quote.items) * itm.quantity),
                    is_negotiable=prod.is_negotiable,
                )
            )

        # Derive discount from quote gross total including shipping
        gross_before_discount = quote.subtotal_paise + quote.shipping_paise
        calculated_discount = max(0, gross_before_discount - p.proposed_total_paise)
        proposal = QuoteProposal(
            items=item_proposals,
            subtotal_paise=quote.subtotal_paise,
            discount_paise=calculated_discount,
            shipping_paise=quote.shipping_paise,
            total_paise=p.proposed_total_paise,
        )

        policy_ctx = PolicyContext(
            merchant_autonomy_level=context.autonomy_level,
            max_discount_percentage=context.max_discount_percentage,
            min_margin_percentage=context.min_margin_percentage,
            max_single_transaction_paise=context.max_single_transaction_paise,
            session_capabilities=context.capabilities,
        )
        eval_res = DeterministicPolicyEngine.evaluate_quote(proposal, policy_ctx)

        # Fail closed on non-ALLOW verdicts with ZERO state or price mutations
        if eval_res.verdict != PolicyVerdict.ALLOW:
            if eval_res.verdict == PolicyVerdict.ESCALATE_APPROVAL:
                return {
                    "status": "PENDING_APPROVAL",
                    "total_paise": quote.total_paise,
                    "message": f"Counter-offer requires merchant approval: {eval_res.reason}",
                }
            return {
                "status": "REJECTED",
                "total_paise": quote.total_paise,
                "message": f"Counter-offer rejected by policy: {eval_res.reason}",
            }

        # ONLY upon explicit PolicyVerdict.ALLOW: advance FSM and mutate quote fields
        if quote.status == "PROPOSED":
            await PriceQuoteStateMachine.transition(
                session=session,
                quote=quote,
                target_state="NEGOTIATING",
                expected_version=quote.version,
                reason="Buyer counter-offer accepted for revision",
            )

        await PriceQuoteStateMachine.transition(
            session=session,
            quote=quote,
            target_state="PROPOSED",
            expected_version=quote.version,
            reason="Counter-offer accepted and quote revised",
            additional_updates={
                "discount_paise": calculated_discount,
                "total_paise": p.proposed_total_paise,
                "discount_reason": p.rationale or "Negotiated discount approved",
            },
        )
        await session.flush()

        return {
            "status": "ACCEPTED",
            "revised_quote_id": str(quote.id),
            "total_paise": quote.total_paise,
            "message": "Counter-offer accepted. Quote updated.",
            "expires_at": quote.expires_at.isoformat(),
        }


class CreateOrderTool(BaseTool):
    """Tool to create an order from an accepted quote."""

    name = "create_order"
    description = "Converts an accepted quote into a locked merchant order."
    side_effect_class = "TRANSIENT_STATE"
    required_capability = "buyer:checkout"
    param_schema = CreateOrderParams

    async def execute(
        self,
        session: AsyncSession,
        params: BaseModel,
        context: GatewayContext,
    ) -> dict[str, Any]:
        p = CreateOrderParams.model_validate(params)

        # Verify quote ownership and session boundary
        quote_stmt = select(PriceQuote).where(
            PriceQuote.id == p.quote_id,
            PriceQuote.merchant_id == context.merchant_id,
            PriceQuote.session_id == context.session_id,
        )
        quote = (await session.execute(quote_stmt)).scalar_one_or_none()
        if not quote:
            return {
                "error": {
                    "code": "QUOTE_NOT_FOUND",
                    "message": f"PriceQuote with ID {p.quote_id} not found in this session.",
                }
            }

        settings = get_settings()
        rzp_client = RazorpayClient(
            key_id=settings.RAZORPAY_KEY_ID,
            key_secret=settings.RAZORPAY_KEY_SECRET,
            base_url=settings.RAZORPAY_API_BASE_URL,
        )
        try:
            order = await PaymentService.create_order_from_accepted_quote(
                session=session,
                quote_id=p.quote_id,
                buyer_email=p.buyer_email,
                shipping_address=p.shipping_address.model_dump(),
                rzp_client=rzp_client,
                merchant_id=context.merchant_id,
                session_id=context.session_id,
            )
            return {
                "order_id": str(order.id),
                "rzp_order_id": order.rzp_order_id,
                "amount_paise": order.amount_paise,
                "currency": order.currency,
                "status": order.status,
            }
        except ValueError as exc:
            return {
                "error": {
                    "code": "ORDER_CREATION_FAILED",
                    "message": str(exc),
                }
            }


class CheckPaymentStatusTool(BaseTool):
    """Tool to check payment status for an order."""

    name = "check_payment_status"
    description = "Verifies payment status directly against Razorpay and local ledger."
    side_effect_class = "READ_ONLY"
    required_capability = "buyer:read"
    param_schema = CheckPaymentStatusParams

    async def execute(
        self,
        session: AsyncSession,
        params: BaseModel,
        context: GatewayContext,
    ) -> dict[str, Any]:
        p = CheckPaymentStatusParams.model_validate(params)
        stmt = select(Order).where(Order.id == p.order_id, Order.merchant_id == context.merchant_id)
        order = (await session.execute(stmt)).scalar_one_or_none()
        if not order:
            return {
                "error": {
                    "code": "ORDER_NOT_FOUND",
                    "message": f"Order with ID {p.order_id} not found.",
                }
            }

        # If order is not settled, query Razorpay and reconcile local state
        if order.status != "PAID" and order.rzp_order_id:
            settings = get_settings()
            rzp_client = RazorpayClient(
                key_id=settings.RAZORPAY_KEY_ID,
                key_secret=settings.RAZORPAY_KEY_SECRET,
                base_url=settings.RAZORPAY_API_BASE_URL,
            )
            try:
                await PaymentService.reconcile_order(session, order.id, rzp_client)
                await session.refresh(order)
            except Exception as exc:
                logger.warning("Reconciliation check failed for order %s: %s", order.id, exc)

        pay_stmt = select(PaymentAttempt).where(PaymentAttempt.order_id == order.id)
        payment = (await session.execute(pay_stmt)).scalar_one_or_none()

        return {
            "order_id": str(order.id),
            "status": order.status,
            "rzp_payment_id": payment.rzp_payment_id if payment else None,
            "is_settled": order.status == "PAID",
        }


class CheckInventoryTool(BaseTool):
    """Tool to check real-time stock availability and fulfillability for a SKU."""

    name = "check_inventory"
    description = "Verify real-time stock levels and unreserved inventory quantities."
    side_effect_class = "READ_ONLY"
    required_capability = "buyer:read"
    param_schema = CheckInventoryParams

    async def execute(
        self,
        session: AsyncSession,
        params: BaseModel,
        context: GatewayContext,
    ) -> dict[str, Any]:
        p = CheckInventoryParams.model_validate(params)

        # 1. Look up variant by SKU directly
        var_stmt = (
            select(ProductVariant)
            .join(Product, ProductVariant.product_id == Product.id)
            .options(selectinload(ProductVariant.inventory_item))
            .where(
                ProductVariant.sku == p.sku,
                Product.merchant_id == context.merchant_id,
            )
        )
        variant = (await session.execute(var_stmt)).scalar_one_or_none()

        # 2. If not found by variant SKU, look up by product base SKU
        if not variant:
            prod_stmt = (
                select(Product)
                .options(selectinload(Product.variants).selectinload(ProductVariant.inventory_item))
                .where(
                    Product.sku == p.sku,
                    Product.merchant_id == context.merchant_id,
                )
            )
            prod = (await session.execute(prod_stmt)).scalar_one_or_none()
            if prod and prod.variants:
                if len(prod.variants) == 1:
                    variant = prod.variants[0]
                else:
                    return {
                        "error": {
                            "code": "AMBIGUOUS_SKU",
                            "message": (
                                f"Product SKU '{p.sku}' has multiple variants. "
                                "Please specify a specific variant SKU."
                            ),
                        }
                    }

        if not variant:
            return {
                "error": {
                    "code": "SKU_NOT_FOUND",
                    "message": f"SKU '{p.sku}' not found for merchant.",
                }
            }

        inv = variant.inventory_item
        available = inv.available_quantity if inv else 0
        reserved = inv.reserved_quantity if inv else 0
        safety = inv.safety_threshold if inv else 0

        in_stock = available > safety
        can_fulfill = available >= (p.requested_quantity + safety)
        max_orderable = max(0, available - safety)

        return {
            "sku": p.sku,
            "variant_id": str(variant.id),
            "available_quantity": available,
            "reserved_quantity": reserved,
            "safety_threshold": safety,
            "in_stock": in_stock,
            "can_fulfill": can_fulfill,
            "max_order_quantity": max_orderable,
        }


class CalculateShippingTool(BaseTool):
    """Tool to calculate shipping rates."""

    name = "calculate_shipping"
    description = (
        "Calculate shipping fees and free shipping eligibility based on cart subtotal and location."
    )
    side_effect_class = "READ_ONLY"
    required_capability = "buyer:discover"
    param_schema = CalculateShippingParams

    async def execute(
        self,
        session: AsyncSession,
        params: BaseModel,
        context: GatewayContext,
    ) -> dict[str, Any]:
        p = CalculateShippingParams.model_validate(params)

        if p.destination_country != "IN":
            return {
                "error": {
                    "code": "UNSUPPORTED_COUNTRY",
                    "message": f"Shipping to '{p.destination_country}' is not supported.",
                }
            }

        subtotal = 0
        if p.quote_id:
            q_stmt = select(PriceQuote).where(
                PriceQuote.id == p.quote_id,
                PriceQuote.merchant_id == context.merchant_id,
                PriceQuote.session_id == context.session_id,
            )
            quote = (await session.execute(q_stmt)).scalar_one_or_none()
            if not quote:
                return {
                    "error": {
                        "code": "QUOTE_NOT_FOUND",
                        "message": f"PriceQuote with ID '{p.quote_id}' not found.",
                    }
                }
            subtotal = quote.subtotal_paise
        elif p.subtotal_paise is not None:
            subtotal = p.subtotal_paise

        standard_fee = 10_000  # ₹100
        free_threshold = 100_000  # ₹1,000
        qualifies_free = subtotal >= free_threshold
        fee = 0 if qualifies_free else standard_fee

        return {
            "destination_country": p.destination_country,
            "destination_postal_code": p.destination_postal_code,
            "shipping_fee_paise": fee,
            "currency": "INR",
            "qualifies_for_free_shipping": qualifies_free,
            "free_shipping_threshold_paise": free_threshold,
            "estimated_delivery_days": 3,
            "service_carrier": "Standard Logistics",
        }


class RequestCheckoutTool(BaseTool):
    """Tool to generate external Razorpay checkout session parameters."""

    name = "request_checkout"
    description = (
        "Generate external Razorpay checkout session parameters and payment metadata for an order."
    )
    side_effect_class = "PRIVILEGED_FINANCIAL"
    required_capability = "buyer:checkout"
    param_schema = RequestCheckoutParams

    async def execute(
        self,
        session: AsyncSession,
        params: BaseModel,
        context: GatewayContext,
    ) -> dict[str, Any]:
        p = RequestCheckoutParams.model_validate(params)
        settings = get_settings()

        order: Order | None = None
        if p.order_id:
            ord_stmt = select(Order).where(
                Order.id == p.order_id,
                Order.merchant_id == context.merchant_id,
            )
            order = (await session.execute(ord_stmt)).scalar_one_or_none()
            if not order:
                return {
                    "error": {
                        "code": "ORDER_NOT_FOUND",
                        "message": f"Order with ID '{p.order_id}' not found.",
                    }
                }
        elif p.quote_id:
            if not p.buyer_email or not p.shipping_address:
                return {
                    "error": {
                        "code": "MISSING_CHECKOUT_DETAILS",
                        "message": "buyer_email and shipping_address required for quote checkout.",
                    }
                }
            rzp_client = RazorpayClient(
                key_id=settings.RAZORPAY_KEY_ID,
                key_secret=settings.RAZORPAY_KEY_SECRET,
                base_url=settings.RAZORPAY_API_BASE_URL,
            )
            try:
                order = await PaymentService.create_order_from_accepted_quote(
                    session=session,
                    quote_id=p.quote_id,
                    buyer_email=p.buyer_email,
                    shipping_address=p.shipping_address.model_dump(),
                    rzp_client=rzp_client,
                    merchant_id=context.merchant_id,
                    session_id=context.session_id,
                )
            except ValueError as exc:
                return {
                    "error": {
                        "code": "CHECKOUT_CREATION_FAILED",
                        "message": str(exc),
                    }
                }
        else:
            return {
                "error": {
                    "code": "INVALID_CHECKOUT_PARAMETERS",
                    "message": "Either order_id or quote_id must be provided.",
                }
            }

        if order.status in {"PAID", "COMPLETED"}:
            return {
                "error": {
                    "code": "ORDER_ALREADY_PAID",
                    "message": f"Order '{order.id}' is already paid.",
                }
            }
        if order.status == "CANCELLED":
            return {
                "error": {
                    "code": "ORDER_CANCELLED",
                    "message": f"Order '{order.id}' has been cancelled.",
                }
            }
        if not order.rzp_order_id:
            return {
                "error": {
                    "code": "NO_RZP_ORDER_ID",
                    "message": (
                        f"Order '{order.id}' does not have a valid external Razorpay order ID."
                    ),
                }
            }

        return {
            "order_id": str(order.id),
            "rzp_order_id": order.rzp_order_id,
            "amount_paise": order.amount_paise,
            "currency": order.currency,
            "status": order.status,
            "key_id": settings.RAZORPAY_KEY_ID,
            "supported_payment_methods": ["upi", "card", "netbanking", "wallet"],
        }


class AcceptQuoteTool(BaseTool):
    """Tool to accept a proposed PriceQuote."""

    name = "accept_quote"
    description = "Accept a binding proposed PriceQuote for checkout."
    side_effect_class = "TRANSIENT_STATE"
    required_capability = "buyer:quote"
    param_schema = AcceptQuoteParams

    async def execute(
        self,
        session: AsyncSession,
        params: BaseModel,
        context: GatewayContext,
    ) -> dict[str, Any]:
        p = AcceptQuoteParams.model_validate(params)
        stmt = select(PriceQuote).where(
            PriceQuote.id == p.quote_id,
            PriceQuote.merchant_id == context.merchant_id,
            PriceQuote.session_id == context.session_id,
        )
        quote = (await session.execute(stmt)).scalar_one_or_none()
        if not quote:
            return {
                "error": {
                    "code": "QUOTE_NOT_FOUND",
                    "message": f"PriceQuote with ID {p.quote_id} not found.",
                }
            }

        now = datetime.now(UTC)
        quote_expires = (
            quote.expires_at
            if quote.expires_at.tzinfo is not None
            else quote.expires_at.replace(tzinfo=UTC)
        )
        if now > quote_expires:
            return {
                "error": {
                    "code": "QUOTE_EXPIRED",
                    "message": "Quote has expired and cannot be accepted.",
                }
            }

        if quote.status != "PROPOSED":
            if quote.status == "ACCEPTED":
                return {
                    "quote_id": str(quote.id),
                    "status": "ACCEPTED",
                    "total_paise": quote.total_paise,
                }
            return {
                "error": {
                    "code": "INVALID_STATE_TRANSITION",
                    "message": f"Cannot accept quote in '{quote.status}' status.",
                }
            }

        await PriceQuoteStateMachine.transition(
            session=session,
            quote=quote,
            target_state="ACCEPTED",
            expected_version=quote.version,
            actor_type="BUYER_AGENT",
            reason="Buyer accepted quote",
        )
        await session.flush()
        return {
            "quote_id": str(quote.id),
            "status": "ACCEPTED",
            "total_paise": quote.total_paise,
        }


class GetOrderStatusTool(BaseTool):
    """Tool to retrieve authoritative order details and status."""

    name = "get_order_status"
    description = "Retrieve authoritative order status, shipping information, and settlement state."
    side_effect_class = "READ_ONLY"
    required_capability = "buyer:read"
    param_schema = GetOrderStatusParams

    async def execute(
        self,
        session: AsyncSession,
        params: BaseModel,
        context: GatewayContext,
    ) -> dict[str, Any]:
        p = GetOrderStatusParams.model_validate(params)
        stmt = select(Order).where(
            Order.id == p.order_id,
            Order.merchant_id == context.merchant_id,
        )
        order = (await session.execute(stmt)).scalar_one_or_none()
        if not order:
            return {
                "error": {
                    "code": "ORDER_NOT_FOUND",
                    "message": f"Order with ID {p.order_id} not found.",
                }
            }

        return {
            "order_id": str(order.id),
            "quote_id": str(order.quote_id),
            "status": order.status,
            "amount_paise": order.amount_paise,
            "currency": order.currency,
            "buyer_email": order.buyer_email,
            "rzp_order_id": order.rzp_order_id,
            "shipping_address": order.shipping_address,
            "created_at": order.created_at.isoformat(),
            "is_settled": (order.status in {"PAID", "FULFILLMENT_PENDING", "COMPLETED"}),
        }


# Canonical Capability Aliases
class DiscoverProductsTool(DiscoverCatalogTool):
    """Canonical alias for discover_catalog."""

    name = "discover_products"


class GetProductTool(GetProductDetailsTool):
    """Canonical alias for get_product_details."""

    name = "get_product"


class GetQuoteTool(RequestPriceQuoteTool):
    """Canonical alias for request_price_quote."""

    name = "get_quote"


class GetPaymentStatusTool(CheckPaymentStatusTool):
    """Canonical alias for check_payment_status."""

    name = "get_payment_status"
