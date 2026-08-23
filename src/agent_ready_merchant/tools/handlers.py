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
    CheckPaymentStatusParams,
    CreateOrderParams,
    DiscoverCatalogParams,
    GetProductDetailsParams,
    NegotiateQuoteParams,
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

        # Transition to NEGOTIATING if PROPOSED
        if quote.status == "PROPOSED":
            await PriceQuoteStateMachine.transition(
                session=session,
                quote=quote,
                target_state="NEGOTIATING",
                expected_version=quote.version,
                reason="Buyer counter-offer submitted",
            )

        # Build proposal for policy evaluation
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

        # Update quote with agreed discount and advance state
        quote.discount_paise = calculated_discount
        quote.total_paise = p.proposed_total_paise
        quote.discount_reason = p.rationale or "Negotiated discount approved"

        await PriceQuoteStateMachine.transition(
            session=session,
            quote=quote,
            target_state="PROPOSED",
            expected_version=quote.version,
            reason="Counter-offer accepted and quote revised",
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
