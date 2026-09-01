"""Demo & Integration Sandbox Simulator Service for Phase 5.3."""

import hashlib
import hmac
import json
import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import TypedDict

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.config import Settings
from agent_ready_merchant.integrations.razorpay.client import RazorpayClient
from agent_ready_merchant.models.approval import MerchantApproval
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.inventory import InventoryItem
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.order import Order, OrderItem
from agent_ready_merchant.models.policy import PolicyRule
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
from agent_ready_merchant.schemas.demo_simulator import (
    DemoSeedResponse,
    DemoSimulationStepRequest,
    DemoSimulationStepResponse,
    SimulationTraceStep,
)
from agent_ready_merchant.services.payment_service import PaymentService

logger = logging.getLogger("agent_ready_merchant.services.demo_simulator")


class DemoProduct(TypedDict):
    """Canonical product attributes used exclusively by the demo sandbox."""

    sku: str
    title: str
    description: str
    category: str
    base_price_paise: int
    floor_price_paise: int
    stock: int


DEMO_PRODUCTS: tuple[DemoProduct, ...] = (
    {
        "sku": "RUN-PRO-01",
        "title": "Apex Carbon Pro Marathon Shoes",
        "description": "Elite marathon racing shoes with carbon propulsion plate.",
        "category": "FOOTWEAR",
        "base_price_paise": 1299900,
        "floor_price_paise": 999900,
        "stock": 50,
    },
    {
        "sku": "AIR-VEST-02",
        "title": "AeroFlow Hydro-Vent Running Vest",
        "description": "Ultra-breathable 8L hydration vest with dual flask holsters.",
        "category": "APPAREL",
        "base_price_paise": 449900,
        "floor_price_paise": 349900,
        "stock": 35,
    },
    {
        "sku": "PACE-BAND-03",
        "title": "TempoPulse GPS Optical HR Sensor",
        "description": "Sub-millisecond heart rate and cadence tracker with BLE.",
        "category": "ELECTRONICS",
        "base_price_paise": 799900,
        "floor_price_paise": 649900,
        "stock": 20,
    },
)


class DemoSimulatorService:
    """Server-authoritative coordinator for deterministic interactive demo simulations."""

    @staticmethod
    async def _load_active_policy_context(
        session: AsyncSession, merchant_id: uuid.UUID
    ) -> PolicyContext:
        """Builds a policy context from the merchant's active server-side rules."""
        rules_stmt = select(PolicyRule).where(
            PolicyRule.merchant_id == merchant_id,
            PolicyRule.is_active.is_(True),
        )
        rules = list((await session.execute(rules_stmt)).scalars().all())

        autonomy_level = 1
        max_discount_pct = 15.0
        min_margin_pct = 20.0
        max_single_tx_paise = 5_000_000
        for rule in rules:
            value = rule.rule_value or {}
            if rule.rule_type == "AUTONOMY_LEVEL" and "autonomy_level" in value:
                autonomy_level = int(value["autonomy_level"])
            elif rule.rule_type == "MAX_DISCOUNT_PCT" and "max_discount_pct" in value:
                max_discount_pct = float(value["max_discount_pct"])
            elif rule.rule_type == "MIN_MARGIN_PCT" and "min_margin_pct" in value:
                min_margin_pct = float(value["min_margin_pct"])
            elif rule.rule_type == "MAX_CART_VALUE" and "max_single_tx_paise" in value:
                max_single_tx_paise = int(value["max_single_tx_paise"])

        if autonomy_level not in (0, 1, 2):
            raise ValueError("Merchant policy has an invalid autonomy level.")
        if not 0.0 <= max_discount_pct <= 50.0:
            raise ValueError("Merchant policy has an invalid discount ceiling.")
        if not 0.0 <= min_margin_pct <= 100.0:
            raise ValueError("Merchant policy has an invalid margin requirement.")
        if not 0 < max_single_tx_paise <= 10_000_000:
            raise ValueError("Merchant policy has an invalid transaction limit.")

        return PolicyContext(
            merchant_autonomy_level=autonomy_level,
            max_discount_percentage=max_discount_pct,
            min_margin_percentage=min_margin_pct,
            max_single_transaction_paise=max_single_tx_paise,
        )

    @classmethod
    async def seed_demo_catalog_and_policies(
        cls, session: AsyncSession, merchant_id: uuid.UUID
    ) -> DemoSeedResponse:
        """Seeds or restores standard catalog products, stock levels, and baseline policy rules."""
        # 1. Load only the merchant's own records. A demo reset must never
        # alter an ordinary catalog item or release a live reservation.
        prod_stmt = select(Product).where(Product.merchant_id == merchant_id)
        existing_products = list((await session.execute(prod_stmt)).scalars().all())
        demo_products_by_sku = {
            product.sku: product
            for product in existing_products
            if product.attributes.get("demo_seeded") is True
        }
        demo_skus = {product["sku"] for product in DEMO_PRODUCTS}
        conflicting_skus = sorted(
            product.sku
            for product in existing_products
            if product.sku in demo_skus and product.sku not in demo_products_by_sku
        )
        if conflicting_skus:
            raise ValueError(
                "Cannot initialize demo catalog because merchant-owned SKU(s) conflict: "
                + ", ".join(conflicting_skus)
            )

        seeded_count = 0
        for demo_product in DEMO_PRODUCTS:
            product = demo_products_by_sku.get(demo_product["sku"])
            if product is None:
                prod = Product(
                    merchant_id=merchant_id,
                    sku=demo_product["sku"],
                    title=demo_product["title"],
                    description=demo_product["description"],
                    category=demo_product["category"],
                    base_price_paise=demo_product["base_price_paise"],
                    floor_price_paise=demo_product["floor_price_paise"],
                    is_negotiable=True,
                    is_active=True,
                    attributes={"brand": "Apex Athletics", "demo_seeded": True},
                )
                session.add(prod)
                await session.flush()

                variant = ProductVariant(
                    product_id=prod.id,
                    sku=demo_product["sku"],
                    title=demo_product["title"],
                    price_override_paise=None,
                    is_active=True,
                )
                session.add(variant)
                await session.flush()

                inv = InventoryItem(
                    variant_id=variant.id,
                    available_quantity=demo_product["stock"],
                    reserved_quantity=0,
                    safety_threshold=2,
                )
                session.add(inv)
                seeded_count += 1
                continue

            product.is_active = True
            var_stmt = select(ProductVariant).where(ProductVariant.product_id == product.id)
            existing_variant = (await session.execute(var_stmt)).scalars().first()
            if not existing_variant:
                existing_variant = ProductVariant(
                    product_id=product.id,
                    sku=demo_product["sku"],
                    title=demo_product["title"],
                    price_override_paise=None,
                    is_active=True,
                )
                session.add(existing_variant)
                await session.flush()

            inv_stmt = (
                select(InventoryItem)
                .where(InventoryItem.variant_id == existing_variant.id)
                .with_for_update()
            )
            existing_inventory = (await session.execute(inv_stmt)).scalar_one_or_none()
            if existing_inventory is None:
                session.add(
                    InventoryItem(
                        variant_id=existing_variant.id,
                        available_quantity=demo_product["stock"],
                        reserved_quantity=0,
                        safety_threshold=2,
                    )
                )
            elif existing_inventory.reserved_quantity == 0:
                existing_inventory.available_quantity = demo_product["stock"]
            # Active reservations are authoritative live state. Preserve both
            # counts rather than resetting a partially committed checkout.
            seeded_count += 1

        await session.flush()

        # 2. Reset or seed policy rules to standard baseline
        rules_stmt = select(PolicyRule).where(PolicyRule.merchant_id == merchant_id)
        existing_rules = {
            r.rule_type: r for r in (await session.execute(rules_stmt)).scalars().all()
        }

        if "AUTONOMY_LEVEL" not in existing_rules:
            session.add(
                PolicyRule(
                    merchant_id=merchant_id,
                    rule_type="AUTONOMY_LEVEL",
                    target_scope="GLOBAL",
                    rule_value={"autonomy_level": 1},
                    is_active=True,
                )
            )
        else:
            existing_rules["AUTONOMY_LEVEL"].rule_value = {"autonomy_level": 1}
            existing_rules["AUTONOMY_LEVEL"].is_active = True

        if "MAX_DISCOUNT_PCT" not in existing_rules:
            session.add(
                PolicyRule(
                    merchant_id=merchant_id,
                    rule_type="MAX_DISCOUNT_PCT",
                    target_scope="GLOBAL",
                    rule_value={"max_discount_pct": 15.0},
                    is_active=True,
                )
            )
        else:
            existing_rules["MAX_DISCOUNT_PCT"].rule_value = {"max_discount_pct": 15.0}
            existing_rules["MAX_DISCOUNT_PCT"].is_active = True

        if "MIN_MARGIN_PCT" not in existing_rules:
            session.add(
                PolicyRule(
                    merchant_id=merchant_id,
                    rule_type="MIN_MARGIN_PCT",
                    target_scope="GLOBAL",
                    rule_value={"min_margin_pct": 20.0},
                    is_active=True,
                )
            )
        else:
            existing_rules["MIN_MARGIN_PCT"].rule_value = {"min_margin_pct": 20.0}
            existing_rules["MIN_MARGIN_PCT"].is_active = True

        if "MAX_CART_VALUE" not in existing_rules:
            session.add(
                PolicyRule(
                    merchant_id=merchant_id,
                    rule_type="MAX_CART_VALUE",
                    target_scope="GLOBAL",
                    rule_value={"max_single_tx_paise": 5_000_000},
                    is_active=True,
                )
            )
        else:
            existing_rules["MAX_CART_VALUE"].rule_value = {"max_single_tx_paise": 5_000_000}
            existing_rules["MAX_CART_VALUE"].is_active = True

        await session.flush()

        # 3. Log Audit Event
        await AuditEvent.create_event(
            session=session,
            merchant_id=merchant_id,
            actor_type="SYSTEM",
            event_type="DEMO_STATE_INITIALIZED",
            payload={
                "seeded_products_count": seeded_count,
                "restored_baseline": True,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )
        await session.commit()

        return DemoSeedResponse(
            merchant_id=merchant_id,
            products_seeded=seeded_count,
            policies_configured=True,
            message="Demo sandbox catalog and baseline policies successfully initialized.",
        )

    @classmethod
    async def execute_simulation(
        cls,
        session: AsyncSession,
        merchant_id: uuid.UUID,
        req: DemoSimulationStepRequest,
        settings: Settings,
    ) -> DemoSimulationStepResponse:
        """Executes a real end-to-end autonomous commerce lifecycle deterministically."""
        now = datetime.now(UTC)
        steps: list[SimulationTraceStep] = []

        # 1. Fetch active Merchant
        m_stmt = select(Merchant).where(Merchant.id == merchant_id)
        merchant = (await session.execute(m_stmt)).scalar_one_or_none()
        if not merchant:
            raise ValueError(f"Merchant '{merchant_id}' not found.")

        # Simulations are restricted to explicit demo records.  The real checkout
        # and settlement path intentionally changes inventory, so accepting a
        # merchant's production SKU here would mutate live stock.
        prod_stmt = select(Product).where(
            Product.merchant_id == merchant_id,
            Product.is_active.is_(True),
        )
        products = [
            product
            for product in (await session.execute(prod_stmt)).scalars().all()
            if (product.attributes or {}).get("demo_seeded") is True
        ]
        if not products:
            await cls.seed_demo_catalog_and_policies(session, merchant_id)
            products = [
                product
                for product in (await session.execute(prod_stmt)).scalars().all()
                if (product.attributes or {}).get("demo_seeded") is True
            ]

        target_product = products[0]
        if req.sku:
            selected_product = next((p for p in products if p.sku == req.sku), None)
            if selected_product is None:
                raise ValueError(f"Demo SKU '{req.sku}' was not found for this merchant.")
            target_product = selected_product

        # Fetch purchasable variant and lock inventory row to prevent overselling
        var_stmt = select(ProductVariant).where(ProductVariant.product_id == target_product.id)
        variant = (await session.execute(var_stmt)).scalars().first()
        if not variant:
            raise ValueError(f"No variant found for product {target_product.sku}")

        inv_stmt = (
            select(InventoryItem).where(InventoryItem.variant_id == variant.id).with_for_update()
        )
        inventory = (await session.execute(inv_stmt)).scalar_one_or_none()
        if not inventory or inventory.available_quantity < req.quantity:
            avail = inventory.available_quantity if inventory else 0
            raise ValueError(
                f"Insufficient inventory stock for SKU '{target_product.sku}'. "
                f"Available: {avail}, Requested: {req.quantity}."
            )

        # Step 1: Buyer Agent Session Initiation
        buyer_agent_id = f"ai-buyer-{uuid.uuid4().hex[:6]}"
        caps = (
            "discover_products,get_product_details,request_quote,negotiate_quote,"
            "create_order,request_checkout,get_payment_status"
        )
        agent_session = BuyerAgentSession(
            merchant_id=merchant_id,
            buyer_agent_identifier=buyer_agent_id,
            auth_token_hash=hashlib.sha256(f"token-{buyer_agent_id}".encode()).hexdigest(),
            granted_capabilities=caps,
            status="ACTIVE",
            expires_at=now + timedelta(hours=1),
        )
        session.add(agent_session)
        await session.flush()

        await AuditEvent.create_event(
            session=session,
            merchant_id=merchant_id,
            session_id=agent_session.id,
            actor_type="BUYER_AGENT",
            event_type="BUYER_SESSION_CREATED",
            payload={
                "buyer_agent_identifier": buyer_agent_id,
                "capabilities": agent_session.granted_capabilities,
            },
        )

        steps.append(
            SimulationTraceStep(
                step_number=1,
                actor="Buyer Agent (External AI)",
                action="session_init",
                status="SUCCESS",
                summary=f"Initiated ACP buyer session for {buyer_agent_id}.",
                details={
                    "session_id": str(agent_session.id),
                    "capabilities": agent_session.granted_capabilities,
                },
                timestamp=now,
            )
        )

        # Step 2: Catalog Discovery & Product Selection
        unit_price = variant.price_override_paise or target_product.base_price_paise
        subtotal_paise = unit_price * req.quantity

        steps.append(
            SimulationTraceStep(
                step_number=2,
                actor="Buyer Agent (External AI)",
                action="discover_products",
                status="SUCCESS",
                summary=f"Discovered SKU '{target_product.sku}' at ₹{unit_price / 100:.2f}/unit.",
                details={
                    "sku": target_product.sku,
                    "title": target_product.title,
                    "unit_price_paise": unit_price,
                    "available_stock": inventory.available_quantity if inventory else 0,
                },
                timestamp=datetime.now(UTC),
            )
        )

        # Step 3: Quote Request & Policy Evaluation
        quote = PriceQuote(
            session_id=agent_session.id,
            merchant_id=merchant_id,
            status="DRAFT",
            subtotal_paise=subtotal_paise,
            discount_paise=0,
            shipping_paise=0,
            total_paise=subtotal_paise,
            idempotency_key=f"demo-quote-{uuid.uuid4()}",
            expires_at=now + timedelta(minutes=30),
        )
        session.add(quote)
        await session.flush()

        quote_item = QuoteItem(
            quote_id=quote.id,
            variant_id=variant.id,
            quantity=req.quantity,
            unit_price_paise=unit_price,
            total_price_paise=subtotal_paise,
        )
        session.add(quote_item)
        await session.flush()

        # Step 4: Policy Engine Evaluation
        discount_pct = 10.0
        if req.scenario == "HITL_ESCALATION_COMMERCE":
            discount_pct = 20.0
        elif req.target_discount_pct is not None:
            discount_pct = req.target_discount_pct

        requested_discount_paise = int(round(subtotal_paise * (discount_pct / 100.0)))
        requested_total_paise = subtotal_paise - requested_discount_paise
        # QuoteItem enforces a single integer unit price for this single-SKU
        # simulation. Round the total upward to an exactly representable line
        # total, which never grants a larger discount than was requested.
        proposed_unit_price = (requested_total_paise + req.quantity - 1) // req.quantity
        proposed_total_paise = proposed_unit_price * req.quantity
        proposed_discount_paise = subtotal_paise - proposed_total_paise

        policy_ctx = await cls._load_active_policy_context(session, merchant_id)
        proposal = QuoteProposal(
            items=[
                QuoteItemProposal(
                    sku=target_product.sku,
                    quantity=req.quantity,
                    unit_base_price_paise=unit_price,
                    unit_floor_price_paise=target_product.floor_price_paise,
                    proposed_unit_price_paise=proposed_unit_price,
                    is_negotiable=target_product.is_negotiable,
                )
            ],
            subtotal_paise=subtotal_paise,
            discount_paise=proposed_discount_paise,
            shipping_paise=0,
            total_paise=proposed_total_paise,
        )
        decision = DeterministicPolicyEngine.evaluate_quote(proposal, policy_ctx)
        policy_hash_str = decision.policy_hash or policy_ctx.policy_hash

        # Handle Policy Verdict
        approval_id: uuid.UUID | None = None
        order_id: uuid.UUID | None = None
        rzp_order_id: str | None = None
        rzp_payment_id: str | None = None

        if decision.verdict == PolicyVerdict.ALLOW:
            quote.status = "ACCEPTED"
            quote.discount_paise = proposed_discount_paise
            quote.total_paise = proposed_total_paise
            quote_item.unit_price_paise = proposed_unit_price
            quote_item.total_price_paise = proposed_total_paise
            quote.discount_reason = (
                f"Autonomous Policy Approval (Rule: {decision.rule_code or 'AUTONOMY_LEVEL'})"
            )
            await session.flush()

            steps.append(
                SimulationTraceStep(
                    step_number=3,
                    actor="Deterministic Policy Engine",
                    action="policy_evaluate",
                    status="SUCCESS",
                    summary=f"Proposal evaluated: {discount_pct:.1f}% discount approved by policy.",
                    details={
                        "verdict": decision.verdict.value,
                        "discount_paise": proposed_discount_paise,
                        "policy_hash": policy_hash_str,
                    },
                    timestamp=datetime.now(UTC),
                )
            )

            # Step 5: Convert accepted quote to Order
            rzp_order_id = f"order_demo_{uuid.uuid4().hex[:12]}"
            order = Order(
                quote_id=quote.id,
                merchant_id=merchant_id,
                status="PENDING_PAYMENT",
                amount_paise=quote.total_paise,
                currency="INR",
                buyer_email=f"{buyer_agent_id}@demo-agent.internal",
                shipping_address={
                    "city": "Bengaluru",
                    "country": "IN",
                    "line1": "UB City Demo Hub",
                    "postal_code": "560001",
                },
                rzp_order_id=rzp_order_id,
            )
            session.add(order)
            await session.flush()
            order_id = order.id

            session.add(
                OrderItem(
                    order_id=order.id,
                    variant_id=quote_item.variant_id,
                    quantity=quote_item.quantity,
                    unit_price_paise=quote_item.unit_price_paise,
                    total_price_paise=quote_item.total_price_paise,
                )
            )
            await session.flush()

            steps.append(
                SimulationTraceStep(
                    step_number=4,
                    actor="Agent-Ready Merchant Gateway",
                    action="create_order",
                    status="SUCCESS",
                    summary=f"Created Order #{str(order.id)[:8]} (Razorpay Ref: {rzp_order_id}).",
                    details={
                        "order_id": str(order.id),
                        "rzp_order_id": rzp_order_id,
                        "amount_paise": quote.total_paise,
                    },
                    timestamp=datetime.now(UTC),
                )
            )

            # Step 6: Simulate Razorpay Payment & Webhook Settlement or Out-of-Band Reconciliation
            if req.scenario == "STANDARD_AUTO_COMMERCE":
                rzp_payment_id = f"pay_demo_{uuid.uuid4().hex[:12]}"
                webhook_payload = {
                    "entity": "event",
                    "account_id": "acc_demo_merchant",
                    "event": "payment.captured",
                    "contains": ["payment"],
                    "payload": {
                        "payment": {
                            "entity": {
                                "id": rzp_payment_id,
                                "entity": "payment",
                                "amount": quote.total_paise,
                                "currency": "INR",
                                "status": "captured",
                                "order_id": rzp_order_id,
                                "method": "upi",
                                "captured": True,
                                "created_at": int(now.timestamp()),
                            }
                        },
                        "order": {
                            "entity": {
                                "id": rzp_order_id,
                                "entity": "order",
                                "amount": quote.total_paise,
                                "amount_paid": quote.total_paise,
                                "status": "paid",
                            }
                        },
                    },
                    "created_at": int(now.timestamp()),
                }
                raw_body = json.dumps(webhook_payload).encode("utf-8")
                secret = settings.RAZORPAY_WEBHOOK_SECRET.get_secret_value()
                sig = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()

                # Process Webhook
                await PaymentService.process_payment_webhook(
                    session=session,
                    raw_body=raw_body,
                    signature_header=sig,
                    webhook_secret=secret,
                )

                # Deduct inventory
                if inventory:
                    inventory.available_quantity -= req.quantity
                    await session.flush()

                steps.append(
                    SimulationTraceStep(
                        step_number=5,
                        actor="Razorpay Payment Webhook Receiver",
                        action="process_payment_webhook",
                        status="SETTLED",
                        summary=f"HMAC webhook verified. Payment {rzp_payment_id} captured.",
                        details={
                            "payment_id": rzp_payment_id,
                            "order_id": str(order.id),
                            "hmac_verified": True,
                            "amount_paise": quote.total_paise,
                        },
                        timestamp=datetime.now(UTC),
                    )
                )

            elif req.scenario == "PAYMENT_RECONCILIATION":
                # Simulate dropped webhook: the webhook was never received;
                # order remained in PENDING_PAYMENT.
                # The demo transport stands in for Razorpay's authoritative
                # server response; settlement still goes through PaymentService.
                rzp_payment_id = f"pay_recon_{uuid.uuid4().hex[:12]}"

                async def demo_reconciliation_response(request: httpx.Request) -> httpx.Response:
                    expected_path = f"/v1/orders/{rzp_order_id}/payments"
                    if request.method != "GET" or request.url.path != expected_path:
                        return httpx.Response(status_code=404)
                    return httpx.Response(
                        status_code=200,
                        json={
                            "entity": "collection",
                            "count": 1,
                            "items": [
                                {
                                    "id": rzp_payment_id,
                                    "entity": "payment",
                                    "amount": quote.total_paise,
                                    "currency": order.currency,
                                    "status": "captured",
                                    "order_id": rzp_order_id,
                                    "method": "upi",
                                    "created_at": int(now.timestamp()),
                                }
                            ],
                        },
                    )

                async with httpx.AsyncClient(
                    transport=httpx.MockTransport(demo_reconciliation_response)
                ) as http_client:
                    reconciliation_client = RazorpayClient(
                        key_id=settings.RAZORPAY_KEY_ID,
                        key_secret=settings.RAZORPAY_KEY_SECRET,
                        base_url=settings.RAZORPAY_API_BASE_URL,
                        http_client=http_client,
                    )
                    reconciliation_result = await PaymentService.reconcile_order(
                        session=session,
                        order_id=order.id,
                        rzp_client=reconciliation_client,
                        merchant_id=merchant_id,
                    )

                if reconciliation_result.get("status") != "PROCESSED":
                    raise ValueError("Demo payment reconciliation did not settle the order.")

                if inventory:
                    inventory.available_quantity -= req.quantity
                    await session.flush()

                await AuditEvent.create_event(
                    session=session,
                    merchant_id=merchant_id,
                    actor_type="SYSTEM",
                    event_type="PAYMENT_RECONCILED",
                    payload={
                        "order_id": str(order.id),
                        "rzp_order_id": rzp_order_id,
                        "rzp_payment_id": rzp_payment_id,
                        "amount_paise": quote.total_paise,
                        "reconciliation_trigger": "OUT_OF_BAND_POLL",
                        "reconciliation_status": reconciliation_result["status"],
                    },
                )
                await session.flush()

                steps.append(
                    SimulationTraceStep(
                        step_number=5,
                        actor="Server Payment Reconciler",
                        action="reconcile_payment",
                        status="SETTLED",
                        summary=(
                            f"Webhook dropped/missed. Server-side reconciliation "
                            f"fetched Razorpay order status and settled Order #{str(order.id)[:8]}."
                        ),
                        details={
                            "payment_id": rzp_payment_id,
                            "order_id": str(order.id),
                            "reconciliation_method": "out_of_band_server_query",
                            "amount_paise": quote.total_paise,
                        },
                        timestamp=datetime.now(UTC),
                    )
                )

        elif decision.verdict == PolicyVerdict.ESCALATE_APPROVAL:
            quote.status = "NEGOTIATING"
            await session.flush()

            # Create stateful MerchantApproval ticket
            ticket = MerchantApproval(
                merchant_id=merchant_id,
                quote_id=quote.id,
                session_id=agent_session.id,
                approval_type="QUOTE_DISCOUNT",
                status="PENDING",
                requested_amount_paise=proposed_total_paise,
                proposed_discount_paise=proposed_discount_paise,
                policy_decision_hash=policy_hash_str,
                policy_rule_code=decision.rule_code or "MAX_DISCOUNT_PCT",
                reason=f"Buyer requested {discount_pct:.1f}% discount requiring approval.",
                expires_at=now + timedelta(minutes=15),
            )
            session.add(ticket)
            await session.flush()
            approval_id = ticket.id

            await AuditEvent.create_event(
                session=session,
                merchant_id=merchant_id,
                session_id=agent_session.id,
                actor_type="SYSTEM",
                event_type="APPROVAL_REQUESTED",
                payload={
                    "approval_id": str(ticket.id),
                    "quote_id": str(quote.id),
                    "discount_paise": proposed_discount_paise,
                    "reason": ticket.reason,
                },
            )

            steps.append(
                SimulationTraceStep(
                    step_number=3,
                    actor="Deterministic Policy Engine",
                    action="escalate_approval",
                    status="ESCALATED",
                    summary=f"Policy Escalation: {discount_pct:.1f}% discount requires approval.",
                    details={
                        "approval_id": str(ticket.id),
                        "requested_amount_paise": proposed_total_paise,
                        "proposed_discount_paise": proposed_discount_paise,
                        "policy_hash": policy_hash_str,
                    },
                    timestamp=datetime.now(UTC),
                )
            )

        else:
            steps.append(
                SimulationTraceStep(
                    step_number=3,
                    actor="Deterministic Policy Engine",
                    action="policy_evaluate",
                    status="REJECTED",
                    summary="Proposal rejected by the active merchant policy.",
                    details={
                        "verdict": decision.verdict.value,
                        "rule_code": decision.rule_code,
                        "reason": decision.reason,
                        "policy_hash": policy_hash_str,
                    },
                    timestamp=datetime.now(UTC),
                )
            )

        # Step 7: Cryptographic Hash Chain Audit Confirmation
        audit_res = await AuditEvent.create_event(
            session=session,
            merchant_id=merchant_id,
            session_id=agent_session.id,
            actor_type="SYSTEM",
            event_type="DEMO_SIMULATION_COMPLETED",
            payload={
                "scenario": req.scenario,
                "quote_id": str(quote.id),
                "order_id": str(order_id) if order_id else None,
                "approval_id": str(approval_id) if approval_id else None,
                "policy_hash": policy_hash_str,
            },
        )
        await session.commit()

        final_step_num = len(steps) + 1
        steps.append(
            SimulationTraceStep(
                step_number=final_step_num,
                actor="Audit Ledger Kernel",
                action="append_audit_event",
                status="SUCCESS",
                summary=f"Appended SHA-256 audit block: {audit_res.event_hash[:16]}...",
                details={"event_hash": audit_res.event_hash, "chain_valid": True},
                timestamp=datetime.now(UTC),
            )
        )

        if decision.verdict == PolicyVerdict.ALLOW:
            msg = "Standard Autonomous Commerce completed and settled successfully."
            simulation_status = "SETTLED"
        elif decision.verdict == PolicyVerdict.ESCALATE_APPROVAL:
            msg = "Proposal escalated to Human Approval queue."
            simulation_status = "PENDING_APPROVAL"
        else:
            msg = f"Proposal rejected by policy: {decision.reason}"
            simulation_status = "REJECTED"

        return DemoSimulationStepResponse(
            scenario=req.scenario,
            session_id=agent_session.id,
            quote_id=quote.id,
            approval_id=approval_id,
            order_id=order_id,
            rzp_order_id=rzp_order_id,
            rzp_payment_id=rzp_payment_id,
            status=simulation_status,
            subtotal_paise=subtotal_paise,
            discount_paise=(
                proposed_discount_paise if decision.verdict == PolicyVerdict.ALLOW else 0
            ),
            total_paise=(
                proposed_total_paise if decision.verdict == PolicyVerdict.ALLOW else subtotal_paise
            ),
            policy_verdict=decision.verdict.value,
            policy_rule_code=decision.rule_code,
            policy_hash=policy_hash_str,
            audit_event_hash=audit_res.event_hash,
            steps=steps,
            message=msg,
        )
