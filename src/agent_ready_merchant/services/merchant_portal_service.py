"""Merchant Control Plane Domain Service for Phase 5.2."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.constants import PLATFORM_MAX_SINGLE_TRANSACTION_PAISE
from agent_ready_merchant.gateway.constants import COMMERCE_PROTOCOL_VERSION
from agent_ready_merchant.models.approval import MerchantApproval
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.inventory import InventoryItem
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.order import Order
from agent_ready_merchant.models.payment import PaymentAttempt
from agent_ready_merchant.models.policy import PolicyRule
from agent_ready_merchant.models.product import Product, ProductVariant
from agent_ready_merchant.models.quote import PriceQuote, QuoteItem
from agent_ready_merchant.policy.engine import DeterministicPolicyEngine
from agent_ready_merchant.policy.models import (
    PolicyContext,
    PolicyVerdict,
    QuoteItemProposal,
    QuoteProposal,
    compute_policy_hash,
)
from agent_ready_merchant.schemas.merchant_auth import PolicySummaryItem
from agent_ready_merchant.schemas.merchant_portal import (
    ApprovalItemResponse,
    AuditEventResponse,
    AuditLedgerCursor,
    AuditLedgerResponse,
    DashboardSummaryResponse,
    InventoryAdjustRequest,
    InventoryItemResponse,
    OrderDetailResponse,
    PaymentAttemptResponse,
    PolicyGovernanceResponse,
    PolicyRuleDetail,
    ProductCreateRequest,
    ProductItemResponse,
    QuoteDetailResponse,
    QuoteItemDetail,
    ResolveApprovalPayload,
)

logger = logging.getLogger("agent_ready_merchant.portal")


class MerchantPortalService:
    """Authoritative domain service executing merchant control plane operations."""

    @classmethod
    async def get_dashboard_summary(
        cls, session: AsyncSession, merchant_id: uuid.UUID
    ) -> DashboardSummaryResponse:
        """Aggregates authoritative operational KPIs for the merchant control plane."""
        # 1. Merchant entity lookup
        m_stmt = select(Merchant).where(Merchant.id == merchant_id)
        merchant = (await session.execute(m_stmt)).scalar_one_or_none()
        if not merchant:
            raise ValueError(f"Merchant with ID '{merchant_id}' not found.")

        # 2. Count products
        prod_count_stmt = select(func.count(Product.id)).where(Product.merchant_id == merchant_id)
        total_products = (await session.execute(prod_count_stmt)).scalar_one() or 0

        # 3. Orders and revenue count
        settled_order_statuses = ("PAID", "FULFILLMENT_PENDING", "COMPLETED")
        order_count_stmt = select(
            func.count(Order.id),
            func.coalesce(func.sum(Order.amount_paise), 0),
        ).where(
            Order.merchant_id == merchant_id,
            Order.status.in_(settled_order_statuses),
        )
        res = (await session.execute(order_count_stmt)).one()
        total_orders = res[0] or 0
        total_revenue_paise = int(res[1] or 0)

        # 4. Pending approvals count
        appr_stmt = select(func.count(MerchantApproval.id)).where(
            MerchantApproval.merchant_id == merchant_id,
            MerchantApproval.status == "PENDING",
            MerchantApproval.expires_at > func.now(),
        )
        pending_approvals_count = (await session.execute(appr_stmt)).scalar_one() or 0

        # 5. Active quotes count
        quote_stmt = select(func.count(PriceQuote.id)).where(
            PriceQuote.merchant_id == merchant_id,
            PriceQuote.status.in_(["PROPOSED", "NEGOTIATING", "ACCEPTED"]),
        )
        active_quotes_count = (await session.execute(quote_stmt)).scalar_one() or 0

        # 6. Policy summary
        policy_summary = await cls._load_policy_summary(session, merchant_id)

        return DashboardSummaryResponse(
            merchant_id=merchant.id,
            merchant_name=merchant.name,
            status=merchant.status,
            currency=merchant.currency,
            total_products=total_products,
            total_orders=total_orders,
            total_revenue_paise=total_revenue_paise,
            pending_approvals_count=pending_approvals_count,
            active_quotes_count=active_quotes_count,
            autonomy_level=policy_summary.autonomy_level,
            max_discount_percentage=policy_summary.max_discount_percentage,
            min_margin_percentage=policy_summary.min_margin_percentage,
            max_single_transaction_paise=policy_summary.max_single_transaction_paise,
            policy_hash=policy_summary.policy_hash,
            system_health="HEALTHY",
        )

    @classmethod
    async def list_products(
        cls, session: AsyncSession, merchant_id: uuid.UUID
    ) -> list[ProductItemResponse]:
        """Lists authoritative catalog products with associated inventory availability."""
        stmt = (
            select(Product)
            .where(Product.merchant_id == merchant_id)
            .order_by(Product.created_at.desc())
        )
        products = list((await session.execute(stmt)).scalars().all())

        items: list[ProductItemResponse] = []
        for p in products:
            # Query variant and inventory
            v_stmt = select(ProductVariant).where(ProductVariant.product_id == p.id)
            variant = (await session.execute(v_stmt)).scalars().first()

            avail_stock = 0
            res_stock = 0
            if variant:
                inv_stmt = select(InventoryItem).where(InventoryItem.variant_id == variant.id)
                inv = (await session.execute(inv_stmt)).scalar_one_or_none()
                if inv:
                    avail_stock = inv.available_quantity
                    res_stock = inv.reserved_quantity

            items.append(
                ProductItemResponse(
                    id=p.id,
                    merchant_id=p.merchant_id,
                    sku=p.sku,
                    title=p.title,
                    description=p.description,
                    category=p.category,
                    base_price_paise=p.base_price_paise,
                    floor_price_paise=p.floor_price_paise,
                    is_negotiable=p.is_negotiable,
                    is_active=p.is_active,
                    attributes=p.attributes or {},
                    version=p.version,
                    created_at=p.created_at or datetime.now(UTC),
                    available_stock=avail_stock,
                    reserved_stock=res_stock,
                )
            )
        return items

    @classmethod
    async def create_product(
        cls, session: AsyncSession, merchant_id: uuid.UUID, req: ProductCreateRequest
    ) -> ProductItemResponse:
        """Creates a new catalog product, default purchasable variant, and inventory entry."""
        # 1. Check duplicate SKU
        dup_stmt = select(Product).where(Product.merchant_id == merchant_id, Product.sku == req.sku)
        if (await session.execute(dup_stmt)).scalar_one_or_none():
            raise ValueError(f"Product with SKU '{req.sku}' already exists.")

        # 2. Floor price invariant check
        if req.floor_price_paise > req.base_price_paise:
            raise ValueError("Floor price cannot exceed base price.")

        # 3. Create Product
        product = Product(
            merchant_id=merchant_id,
            sku=req.sku,
            title=req.title,
            description=req.description,
            category=req.category,
            base_price_paise=req.base_price_paise,
            floor_price_paise=req.floor_price_paise,
            is_negotiable=req.is_negotiable,
            is_active=req.is_active,
            attributes=req.attributes,
        )
        session.add(product)
        await session.flush()

        # 4. Create default purchasable variant
        variant = ProductVariant(
            product_id=product.id,
            sku=req.sku,
            title=req.title,
            price_override_paise=None,
            is_active=True,
        )
        session.add(variant)
        await session.flush()

        # 5. Create InventoryItem
        inventory = InventoryItem(
            variant_id=variant.id,
            available_quantity=req.initial_stock,
            reserved_quantity=0,
            safety_threshold=req.safety_threshold,
        )
        session.add(inventory)
        await session.flush()

        # 6. Audit log
        await AuditEvent.create_event(
            session=session,
            merchant_id=merchant_id,
            actor_type="MERCHANT_ADMIN",
            event_type="PRODUCT_CREATED",
            payload={
                "product_id": str(product.id),
                "sku": product.sku,
                "base_price_paise": product.base_price_paise,
                "floor_price_paise": product.floor_price_paise,
                "initial_stock": req.initial_stock,
            },
        )

        return ProductItemResponse(
            id=product.id,
            merchant_id=product.merchant_id,
            sku=product.sku,
            title=product.title,
            description=product.description,
            category=product.category,
            base_price_paise=product.base_price_paise,
            floor_price_paise=product.floor_price_paise,
            is_negotiable=product.is_negotiable,
            is_active=product.is_active,
            attributes=product.attributes or {},
            version=product.version,
            created_at=product.created_at or datetime.now(UTC),
            available_stock=inventory.available_quantity,
            reserved_stock=inventory.reserved_quantity,
        )

    @classmethod
    async def list_inventory(
        cls, session: AsyncSession, merchant_id: uuid.UUID
    ) -> list[InventoryItemResponse]:
        """Lists authoritative inventory levels for all merchant products."""
        stmt = (
            select(InventoryItem, ProductVariant, Product)
            .join(ProductVariant, InventoryItem.variant_id == ProductVariant.id)
            .join(Product, ProductVariant.product_id == Product.id)
            .where(Product.merchant_id == merchant_id)
        )
        results = (await session.execute(stmt)).all()

        items: list[InventoryItemResponse] = []
        for inv, variant, prod in results:
            items.append(
                InventoryItemResponse(
                    id=inv.id,
                    variant_id=inv.variant_id,
                    sku=variant.sku,
                    product_title=prod.title,
                    available_quantity=inv.available_quantity,
                    reserved_quantity=inv.reserved_quantity,
                    safety_threshold=inv.safety_threshold,
                    updated_at=inv.updated_at or datetime.now(UTC),
                )
            )
        return items

    @classmethod
    async def adjust_inventory(
        cls, session: AsyncSession, merchant_id: uuid.UUID, req: InventoryAdjustRequest
    ) -> InventoryItemResponse:
        """Adjusts available stock units for a specific SKU with optimistic locking."""
        stmt = (
            select(InventoryItem, ProductVariant, Product)
            .join(ProductVariant, InventoryItem.variant_id == ProductVariant.id)
            .join(Product, ProductVariant.product_id == Product.id)
            .where(Product.merchant_id == merchant_id, ProductVariant.sku == req.sku)
            .with_for_update()
        )
        res = (await session.execute(stmt)).first()
        if not res:
            raise ValueError(f"Inventory item for SKU '{req.sku}' not found.")

        inv, variant, prod = res
        new_quantity = inv.available_quantity + req.quantity_delta
        if new_quantity < 0:
            raise ValueError(
                f"Cannot adjust inventory below zero (current: {inv.available_quantity}, "
                f"delta: {req.quantity_delta})."
            )

        inv.available_quantity = new_quantity
        await session.flush()

        await AuditEvent.create_event(
            session=session,
            merchant_id=merchant_id,
            actor_type="MERCHANT_ADMIN",
            event_type="INVENTORY_ADJUSTED",
            payload={
                "sku": req.sku,
                "delta": req.quantity_delta,
                "new_available": new_quantity,
                "reason": req.reason,
            },
        )

        return InventoryItemResponse(
            id=inv.id,
            variant_id=inv.variant_id,
            sku=variant.sku,
            product_title=prod.title,
            available_quantity=inv.available_quantity,
            reserved_quantity=inv.reserved_quantity,
            safety_threshold=inv.safety_threshold,
            updated_at=inv.updated_at or datetime.now(UTC),
        )

    @classmethod
    async def list_quotes(
        cls, session: AsyncSession, merchant_id: uuid.UUID
    ) -> list[QuoteDetailResponse]:
        """Lists authoritative price quotes and line items."""
        stmt = (
            select(PriceQuote)
            .where(PriceQuote.merchant_id == merchant_id)
            .order_by(PriceQuote.created_at.desc())
        )
        quotes = list((await session.execute(stmt)).scalars().all())

        results: list[QuoteDetailResponse] = []
        for q in quotes:
            items_stmt = (
                select(QuoteItem, ProductVariant)
                .join(ProductVariant, QuoteItem.variant_id == ProductVariant.id)
                .where(QuoteItem.quote_id == q.id)
            )
            items_res = (await session.execute(items_stmt)).all()

            line_items = [
                QuoteItemDetail(
                    sku=var.sku,
                    title=var.title,
                    quantity=qi.quantity,
                    unit_price_paise=qi.unit_price_paise,
                    total_price_paise=qi.total_price_paise,
                )
                for qi, var in items_res
            ]

            results.append(
                QuoteDetailResponse(
                    id=q.id,
                    session_id=q.session_id,
                    merchant_id=q.merchant_id,
                    status=q.status,
                    subtotal_paise=q.subtotal_paise,
                    discount_paise=q.discount_paise,
                    shipping_paise=q.shipping_paise,
                    total_paise=q.total_paise,
                    discount_reason=q.discount_reason,
                    expires_at=q.expires_at,
                    created_at=q.created_at,
                    items=line_items,
                )
            )
        return results

    @classmethod
    async def list_orders(
        cls, session: AsyncSession, merchant_id: uuid.UUID
    ) -> list[OrderDetailResponse]:
        """Lists authoritative merchant orders."""
        stmt = (
            select(Order).where(Order.merchant_id == merchant_id).order_by(Order.created_at.desc())
        )
        orders = list((await session.execute(stmt)).scalars().all())

        results: list[OrderDetailResponse] = []
        for o in orders:
            pa_count_stmt = select(func.count(PaymentAttempt.id)).where(
                PaymentAttempt.order_id == o.id
            )
            attempts_count = (await session.execute(pa_count_stmt)).scalar_one() or 0

            results.append(
                OrderDetailResponse(
                    id=o.id,
                    quote_id=o.quote_id,
                    merchant_id=o.merchant_id,
                    status=o.status,
                    amount_paise=o.amount_paise,
                    currency=o.currency,
                    buyer_email=o.buyer_email,
                    shipping_address=o.shipping_address or {},
                    rzp_order_id=o.rzp_order_id,
                    created_at=o.created_at or datetime.now(UTC),
                    payment_attempts_count=attempts_count,
                )
            )
        return results

    @classmethod
    async def list_payments(
        cls, session: AsyncSession, merchant_id: uuid.UUID
    ) -> list[PaymentAttemptResponse]:
        """Lists payment attempts and transaction settlement records."""
        stmt = (
            select(PaymentAttempt)
            .join(Order, PaymentAttempt.order_id == Order.id)
            .where(Order.merchant_id == merchant_id)
            .order_by(PaymentAttempt.created_at.desc())
        )
        payments = list((await session.execute(stmt)).scalars().all())

        return [
            PaymentAttemptResponse(
                id=p.id,
                order_id=p.order_id,
                status=p.status,
                amount_paise=p.amount_paise,
                rzp_payment_id=p.rzp_payment_id,
                rzp_order_id=p.rzp_order_id,
                payment_method=p.payment_method,
                error_code=p.error_code,
                error_description=p.error_description,
                created_at=p.created_at or datetime.now(UTC),
            )
            for p in payments
        ]

    @classmethod
    async def list_approvals(
        cls, session: AsyncSession, merchant_id: uuid.UUID, status_filter: str | None = None
    ) -> list[ApprovalItemResponse]:
        """Lists HITL approval tickets filtered by status."""
        stmt = select(MerchantApproval).where(MerchantApproval.merchant_id == merchant_id)
        if status_filter and status_filter.upper() != "ALL":
            normalized_status = status_filter.upper()
            if normalized_status == "EXPIRED":
                stmt = stmt.where(
                    or_(
                        MerchantApproval.status == "EXPIRED",
                        and_(
                            MerchantApproval.status == "PENDING",
                            MerchantApproval.expires_at <= func.now(),
                        ),
                    )
                )
            else:
                stmt = stmt.where(MerchantApproval.status == normalized_status)
        stmt = stmt.order_by(MerchantApproval.created_at.desc())

        approvals = list((await session.execute(stmt)).scalars().all())

        results: list[ApprovalItemResponse] = []
        now = datetime.now(UTC)
        for a in approvals:
            effective_status = a.status
            exp = (
                a.expires_at
                if a.expires_at.tzinfo is not None
                else a.expires_at.replace(tzinfo=UTC)
            )
            if a.status == "PENDING" and exp < now:
                effective_status = "EXPIRED"

            pct = 0.0
            if a.requested_amount_paise > 0:
                pct = round(
                    (
                        a.proposed_discount_paise
                        / (a.requested_amount_paise + a.proposed_discount_paise)
                    )
                    * 100,
                    2,
                )

            results.append(
                ApprovalItemResponse(
                    id=a.id,
                    merchant_id=a.merchant_id,
                    quote_id=a.quote_id,
                    order_id=a.order_id,
                    session_id=a.session_id,
                    approval_type=a.approval_type,
                    status=effective_status,
                    requested_amount_paise=a.requested_amount_paise,
                    proposed_discount_paise=a.proposed_discount_paise,
                    proposed_discount_percentage=pct,
                    policy_rule_code=a.policy_rule_code,
                    reason=a.reason,
                    approver_identifier=a.approver_identifier,
                    resolved_at=a.resolved_at,
                    expires_at=a.expires_at,
                    created_at=a.created_at or datetime.now(UTC),
                )
            )
        return results

    @classmethod
    async def resolve_approval(
        cls,
        session: AsyncSession,
        merchant_id: uuid.UUID,
        approval_id: uuid.UUID,
        req: ResolveApprovalPayload,
    ) -> ApprovalItemResponse:
        """Resolves a pending HITL approval ticket with server-authoritative state progression."""
        stmt = (
            select(MerchantApproval)
            .where(MerchantApproval.id == approval_id, MerchantApproval.merchant_id == merchant_id)
            .with_for_update()
        )
        approval = (await session.execute(stmt)).scalar_one_or_none()
        if not approval:
            raise ValueError(f"Approval ticket '{approval_id}' not found.")

        if approval.status != "PENDING":
            raise ValueError(
                f"Approval ticket is already resolved with status '{approval.status}'."
            )

        now = datetime.now(UTC)
        exp = (
            approval.expires_at
            if approval.expires_at.tzinfo is not None
            else approval.expires_at.replace(tzinfo=UTC)
        )
        if exp < now:
            approval.status = "EXPIRED"
            await session.flush()
            await AuditEvent.create_event(
                session=session,
                merchant_id=merchant_id,
                actor_type="SYSTEM",
                event_type="APPROVAL_EXPIRED",
                payload={
                    "approval_id": str(approval.id),
                    "quote_id": str(approval.quote_id) if approval.quote_id else None,
                    "status": approval.status,
                    "expires_at": exp.isoformat(),
                },
            )
            raise ValueError("Approval ticket has expired.")

        validated_counter_discount: int | None = None
        if req.decision == "COUNTER_OFFER":
            if req.counter_amount_paise is None:
                raise ValueError("A counter-offer amount is required.")
            if approval.quote_id is None:
                raise ValueError("A counter-offer requires an associated quote.")

            q_stmt = (
                select(PriceQuote)
                .where(
                    PriceQuote.id == approval.quote_id,
                    PriceQuote.merchant_id == merchant_id,
                )
                .with_for_update()
            )
            counter_quote = (await session.execute(q_stmt)).scalar_one_or_none()
            if counter_quote is None:
                raise ValueError("The approval's associated quote was not found.")

            quote_rows_stmt = (
                select(QuoteItem, ProductVariant, Product)
                .join(ProductVariant, QuoteItem.variant_id == ProductVariant.id)
                .join(Product, ProductVariant.product_id == Product.id)
                .where(QuoteItem.quote_id == counter_quote.id)
                .with_for_update()
            )
            quote_rows = list((await session.execute(quote_rows_stmt)).all())
            if not quote_rows:
                raise ValueError("Cannot counter-offer on a quote with no line items.")

            proposed_goods_paise = req.counter_amount_paise - counter_quote.shipping_paise
            if proposed_goods_paise <= 0 or req.counter_amount_paise > (
                counter_quote.subtotal_paise + counter_quote.shipping_paise
            ):
                raise ValueError(
                    "Counter-offer amount must be within the quote's valid total range."
                )

            floor_total_paise = sum(
                product.floor_price_paise * item.quantity for item, _, product in quote_rows
            )
            if proposed_goods_paise < floor_total_paise:
                raise ValueError(
                    "Counter-offer amount would breach one or more product floor prices."
                )

            validated_counter_discount = counter_quote.subtotal_paise - proposed_goods_paise
            item_proposals = [
                QuoteItemProposal(
                    sku=variant.sku,
                    quantity=item.quantity,
                    unit_base_price_paise=item.unit_price_paise,
                    unit_floor_price_paise=product.floor_price_paise,
                    proposed_unit_price_paise=max(
                        product.floor_price_paise,
                        (item.total_price_paise * proposed_goods_paise)
                        // max(1, counter_quote.subtotal_paise * item.quantity),
                    ),
                    is_negotiable=product.is_negotiable,
                )
                for item, variant, product in quote_rows
            ]
            policy_summary = await cls._load_policy_summary(session, merchant_id)
            policy_result = DeterministicPolicyEngine.evaluate_quote(
                QuoteProposal(
                    items=item_proposals,
                    subtotal_paise=counter_quote.subtotal_paise,
                    discount_paise=validated_counter_discount,
                    shipping_paise=counter_quote.shipping_paise,
                    total_paise=req.counter_amount_paise,
                ),
                PolicyContext(
                    merchant_autonomy_level=policy_summary.autonomy_level,
                    max_discount_percentage=policy_summary.max_discount_percentage,
                    min_margin_percentage=policy_summary.min_margin_percentage,
                    max_single_transaction_paise=policy_summary.max_single_transaction_paise,
                ),
                required_capability=None,
            )
            if policy_result.verdict != PolicyVerdict.ALLOW:
                raise ValueError(f"Counter-offer rejected by active policy: {policy_result.reason}")

        # Update approval status
        if req.decision == "APPROVE":
            approval.status = "APPROVED"
        elif req.decision == "REJECT":
            approval.status = "REJECTED"
        elif req.decision == "COUNTER_OFFER":
            approval.status = "APPROVED"
            if req.counter_amount_paise is not None:
                approval.requested_amount_paise = req.counter_amount_paise

        approval.approver_identifier = "MERCHANT_ADMIN"
        approval.resolved_at = datetime.now(UTC)
        await session.flush()

        # Update associated quote if exists
        if approval.quote_id:
            q_stmt = select(PriceQuote).where(PriceQuote.id == approval.quote_id).with_for_update()
            quote = (await session.execute(q_stmt)).scalar_one_or_none()
            if quote:
                if req.decision == "APPROVE":
                    quote.status = "PROPOSED"
                    quote.discount_paise = approval.proposed_discount_paise
                    quote.total_paise = (
                        quote.subtotal_paise - quote.discount_paise + quote.shipping_paise
                    )
                    quote.discount_reason = f"Merchant Approved: {req.reason_note}"
                elif req.decision == "COUNTER_OFFER":
                    quote.status = "PROPOSED"
                    counter_amt = req.counter_amount_paise
                    if counter_amt is None or validated_counter_discount is None:
                        raise ValueError("A validated counter-offer amount is required.")
                    quote.total_paise = counter_amt
                    quote.discount_paise = validated_counter_discount
                    approval.proposed_discount_paise = quote.discount_paise
                    quote.discount_reason = f"Merchant Counter-Offer: {req.reason_note}"
                else:
                    quote.status = "REJECTED"
                    quote.discount_reason = f"Merchant Rejected: {req.reason_note}"
                await session.flush()

        # Audit log
        await AuditEvent.create_event(
            session=session,
            merchant_id=merchant_id,
            actor_type="MERCHANT_ADMIN",
            event_type=f"APPROVAL_{approval.status}",
            payload={
                "approval_id": str(approval.id),
                "quote_id": str(approval.quote_id) if approval.quote_id else None,
                "decision": req.decision,
                "reason_note": req.reason_note,
                "counter_amount_paise": req.counter_amount_paise,
                "status": approval.status,
            },
        )

        pct = 0.0
        if approval.requested_amount_paise > 0:
            pct = round(
                (
                    approval.proposed_discount_paise
                    / (approval.requested_amount_paise + approval.proposed_discount_paise)
                )
                * 100,
                2,
            )

        return ApprovalItemResponse(
            id=approval.id,
            merchant_id=approval.merchant_id,
            quote_id=approval.quote_id,
            order_id=approval.order_id,
            session_id=approval.session_id,
            approval_type=approval.approval_type,
            status=approval.status,
            requested_amount_paise=approval.requested_amount_paise,
            proposed_discount_paise=approval.proposed_discount_paise,
            proposed_discount_percentage=pct,
            policy_rule_code=approval.policy_rule_code,
            reason=approval.reason,
            approver_identifier=approval.approver_identifier,
            resolved_at=approval.resolved_at,
            expires_at=approval.expires_at,
            created_at=approval.created_at or datetime.now(UTC),
        )

    @classmethod
    async def get_policies(
        cls, session: AsyncSession, merchant_id: uuid.UUID
    ) -> PolicyGovernanceResponse:
        """Fetches active policy rules, governance configuration, and deterministic policy hash."""
        rules_stmt = select(PolicyRule).where(
            PolicyRule.merchant_id == merchant_id, PolicyRule.is_active.is_(True)
        )
        rules = list((await session.execute(rules_stmt)).scalars().all())

        summary = await cls._load_policy_summary(session, merchant_id)

        rule_details = [
            PolicyRuleDetail(
                id=r.id,
                rule_type=r.rule_type,
                target_scope=r.target_scope,
                target_id=r.target_id,
                rule_value=r.rule_value or {},
                is_active=r.is_active,
            )
            for r in rules
        ]

        return PolicyGovernanceResponse(
            merchant_id=merchant_id,
            autonomy_level=summary.autonomy_level,
            max_discount_percentage=summary.max_discount_percentage,
            min_margin_percentage=summary.min_margin_percentage,
            max_single_transaction_paise=summary.max_single_transaction_paise,
            policy_hash=summary.policy_hash,
            protocol_version=COMMERCE_PROTOCOL_VERSION,
            rules=rule_details,
        )

    @classmethod
    async def update_policies(
        cls,
        session: AsyncSession,
        merchant_id: uuid.UUID,
        autonomy_level: int,
        max_discount_pct: float,
        min_margin_pct: float,
        max_tx_paise: int,
    ) -> PolicyGovernanceResponse:
        """Updates policy rules atomically with server-authoritative validations."""
        if max_discount_pct > 50.0:
            raise ValueError("Max discount percentage cannot exceed the platform ceiling of 50%.")
        if min_margin_pct < 0.0 or min_margin_pct > 100.0:
            raise ValueError("Min margin percentage must be between 0% and 100%.")
        if autonomy_level not in (0, 1, 2):
            raise ValueError(
                "Autonomy level must be 0 (Read-Only), 1 (Bounded), or 2 (Supervised)."
            )
        if not 100 <= max_tx_paise <= PLATFORM_MAX_SINGLE_TRANSACTION_PAISE:
            raise ValueError("Maximum transaction limit exceeds the platform governance ceiling.")

        rules_stmt = select(PolicyRule).where(PolicyRule.merchant_id == merchant_id)
        existing_rules = {
            r.rule_type: r for r in (await session.execute(rules_stmt)).scalars().all()
        }

        type_map: dict[str, dict[str, Any]] = {
            "AUTONOMY_LEVEL": {"autonomy_level": autonomy_level},
            "MAX_DISCOUNT_PCT": {"max_discount_pct": max_discount_pct},
            "MIN_MARGIN_PCT": {"min_margin_pct": min_margin_pct},
            "MAX_CART_VALUE": {"max_single_tx_paise": max_tx_paise},
        }

        for r_type, r_val in type_map.items():
            if r_type in existing_rules:
                existing_rules[r_type].rule_value = r_val
                existing_rules[r_type].is_active = True
            else:
                new_rule = PolicyRule(
                    merchant_id=merchant_id,
                    rule_type=r_type,
                    target_scope="GLOBAL",
                    rule_value=r_val,
                    is_active=True,
                )
                session.add(new_rule)

        await session.flush()

        # Audit log
        summary = await cls._load_policy_summary(session, merchant_id)
        await AuditEvent.create_event(
            session=session,
            merchant_id=merchant_id,
            actor_type="MERCHANT_ADMIN",
            event_type="POLICIES_UPDATED",
            payload={
                "autonomy_level": autonomy_level,
                "max_discount_percentage": max_discount_pct,
                "min_margin_percentage": min_margin_pct,
                "max_single_transaction_paise": max_tx_paise,
                "policy_hash": summary.policy_hash,
            },
        )

        return await cls.get_policies(session, merchant_id)

    @classmethod
    async def get_audit_ledger(
        cls,
        session: AsyncSession,
        merchant_id: uuid.UUID,
        limit: int = 50,
        before_created_at: datetime | None = None,
        before_id: uuid.UUID | None = None,
    ) -> AuditLedgerResponse:
        """Fetches immutable audit event trail and verifies cryptographic SHA-256 chain."""
        stmt = (
            select(AuditEvent)
            .where(AuditEvent.merchant_id == merchant_id)
            .order_by(AuditEvent.created_at.desc(), AuditEvent.id.desc())
        )
        if before_created_at is not None and before_id is not None:
            stmt = stmt.where(
                or_(
                    AuditEvent.created_at < before_created_at,
                    and_(
                        AuditEvent.created_at == before_created_at,
                        AuditEvent.id < before_id,
                    ),
                )
            )
        page_rows = list((await session.execute(stmt.limit(limit + 1))).scalars().all())
        events = page_rows[:limit]

        count_stmt = select(func.count(AuditEvent.id)).where(AuditEvent.merchant_id == merchant_id)
        total_count = (await session.execute(count_stmt)).scalar_one() or 0

        # Verify cryptographic chain
        is_chain_valid, chain_error = await AuditEvent.verify_chain(session, merchant_id)

        event_responses = [
            AuditEventResponse(
                id=e.id,
                merchant_id=e.merchant_id,
                session_id=e.session_id,
                actor_type=e.actor_type,
                event_type=e.event_type,
                payload=e.payload or {},
                event_hash=e.event_hash,
                prev_event_hash=e.prev_event_hash,
                created_at=e.created_at or datetime.now(UTC),
            )
            for e in events
        ]

        next_cursor: AuditLedgerCursor | None = None
        if len(page_rows) > limit and events:
            last_event = events[-1]
            next_cursor = AuditLedgerCursor(
                created_at=last_event.created_at,
                id=last_event.id,
            )

        return AuditLedgerResponse(
            events=event_responses,
            total_count=total_count,
            chain_valid=is_chain_valid,
            chain_error=chain_error,
            next_cursor=next_cursor,
        )

    @classmethod
    async def _load_policy_summary(
        cls, session: AsyncSession, merchant_id: uuid.UUID
    ) -> PolicySummaryItem:
        """Helper to load authoritative policy bounds and compute SHA-256 hash."""
        rules_stmt = select(PolicyRule).where(
            PolicyRule.merchant_id == merchant_id, PolicyRule.is_active.is_(True)
        )
        rules = list((await session.execute(rules_stmt)).scalars().all())

        autonomy_level = 1
        max_discount_pct = 15.0
        min_margin_pct = 20.0
        max_single_tx_paise = 5_000_000

        for r in rules:
            val = r.rule_value or {}
            if r.rule_type == "AUTONOMY_LEVEL" and "autonomy_level" in val:
                autonomy_level = int(val["autonomy_level"])
            elif r.rule_type == "MAX_DISCOUNT_PCT" and "max_discount_pct" in val:
                max_discount_pct = float(val["max_discount_pct"])
            elif r.rule_type == "MIN_MARGIN_PCT" and "min_margin_pct" in val:
                min_margin_pct = float(val["min_margin_pct"])
            elif r.rule_type == "MAX_CART_VALUE" and "max_single_tx_paise" in val:
                max_single_tx_paise = int(val["max_single_tx_paise"])

        p_hash = compute_policy_hash(
            autonomy_level=autonomy_level,
            max_discount_percentage=max_discount_pct,
            min_margin_percentage=min_margin_pct,
            max_single_transaction_paise=max_single_tx_paise,
            version=COMMERCE_PROTOCOL_VERSION,
        )

        return PolicySummaryItem(
            autonomy_level=autonomy_level,
            max_discount_percentage=max_discount_pct,
            min_margin_percentage=min_margin_pct,
            max_single_transaction_paise=max_single_tx_paise,
            policy_hash=p_hash,
            protocol_version=COMMERCE_PROTOCOL_VERSION,
        )
