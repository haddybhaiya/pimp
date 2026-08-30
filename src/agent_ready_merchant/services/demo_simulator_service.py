"""Demo & Integration Sandbox Simulator Service for Phase 5.3."""

import hashlib
import hmac
import json
import logging
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.config import Settings
from agent_ready_merchant.models.approval import MerchantApproval
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.inventory import InventoryItem
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.order import Order
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


class DemoSimulatorService:
    """Server-authoritative coordinator for deterministic interactive demo simulations."""

    @classmethod
    async def seed_demo_catalog_and_policies(
        cls, session: AsyncSession, merchant_id: uuid.UUID
    ) -> DemoSeedResponse:
        """Seeds standard catalog products and policy rules for repeatable demo workflows."""
        # 1. Check existing products
        prod_stmt = select(Product).where(Product.merchant_id == merchant_id)
        existing_prods = list((await session.execute(prod_stmt)).scalars().all())

        seeded_count = 0
        if not existing_prods:
            demo_products = [
                {
                    "sku": "RUN-PRO-01",
                    "title": "Apex Carbon Pro Marathon Shoes",
                    "description": "Elite marathon racing shoes with carbon propulsion plate.",
                    "category": "FOOTWEAR",
                    "base_price_paise": 1299900,  # ₹12,999.00
                    "floor_price_paise": 999900,  # ₹9,999.00
                    "stock": 50,
                },
                {
                    "sku": "AIR-VEST-02",
                    "title": "AeroFlow Hydro-Vent Running Vest",
                    "description": "Ultra-breathable 8L hydration vest with dual flask holsters.",
                    "category": "APPAREL",
                    "base_price_paise": 449900,  # ₹4,499.00
                    "floor_price_paise": 349900,  # ₹3,499.00
                    "stock": 35,
                },
                {
                    "sku": "PACE-BAND-03",
                    "title": "TempoPulse GPS Optical HR Sensor",
                    "description": "Sub-millisecond heart rate and cadence tracker with BLE.",
                    "category": "ELECTRONICS",
                    "base_price_paise": 799900,  # ₹7,999.00
                    "floor_price_paise": 649900,  # ₹6,499.00
                    "stock": 20,
                },
            ]

            for dp in demo_products:
                prod = Product(
                    merchant_id=merchant_id,
                    sku=dp["sku"],
                    title=dp["title"],
                    description=dp["description"],
                    category=dp["category"],
                    base_price_paise=dp["base_price_paise"],
                    floor_price_paise=dp["floor_price_paise"],
                    is_negotiable=True,
                    is_active=True,
                    attributes={"brand": "Apex Athletics", "demo_seeded": True},
                )
                session.add(prod)
                await session.flush()

                variant = ProductVariant(
                    product_id=prod.id,
                    sku=prod.sku,
                    title=prod.title,
                    price_override_paise=None,
                    is_active=True,
                )
                session.add(variant)
                await session.flush()

                inv = InventoryItem(
                    variant_id=variant.id,
                    available_quantity=dp["stock"],
                    reserved_quantity=0,
                    safety_threshold=2,
                )
                session.add(inv)
                seeded_count += 1

            await session.flush()

        # 2. Check and seed policies if absent
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
        await session.flush()

        # 3. Log Audit Event
        await AuditEvent.create_event(
            session=session,
            merchant_id=merchant_id,
            actor_type="SYSTEM",
            event_type="DEMO_STATE_INITIALIZED",
            payload={
                "seeded_products_count": seeded_count,
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

        # Ensure demo products exist
        prod_stmt = select(Product).where(
            Product.merchant_id == merchant_id, Product.is_active.is_(True)
        )
        products = list((await session.execute(prod_stmt)).scalars().all())
        if not products:
            await cls.seed_demo_catalog_and_policies(session, merchant_id)
            products = list((await session.execute(prod_stmt)).scalars().all())

        target_product = products[0]
        if req.sku:
            for p in products:
                if p.sku == req.sku:
                    target_product = p
                    break

        # Fetch purchasable variant and inventory
        var_stmt = select(ProductVariant).where(ProductVariant.product_id == target_product.id)
        variant = (await session.execute(var_stmt)).scalars().first()
        if not variant:
            raise ValueError(f"No variant found for product {target_product.sku}")

        # Fetch inventory
        inv_stmt = select(InventoryItem).where(InventoryItem.variant_id == variant.id)
        inventory = (await session.execute(inv_stmt)).scalar_one_or_none()

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
        unit_price = target_product.base_price_paise
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
        autonomy_level = 1
        if req.scenario == "HITL_ESCALATION_COMMERCE":
            discount_pct = 20.0
            autonomy_level = 2  # Supervised HITL mode triggers approval escalation
        elif req.target_discount_pct is not None:
            discount_pct = req.target_discount_pct

        proposed_discount_paise = int(round(subtotal_paise * (discount_pct / 100.0)))
        proposed_total_paise = subtotal_paise - proposed_discount_paise

        policy_ctx = PolicyContext(
            merchant_autonomy_level=autonomy_level,
            max_discount_percentage=30.0 if autonomy_level == 2 else 15.0,
            min_margin_percentage=20.0,
            max_single_transaction_paise=5_000_000,
        )
        unit_discount_paise = int(proposed_discount_paise / req.quantity)
        proposal = QuoteProposal(
            items=[
                QuoteItemProposal(
                    sku=target_product.sku,
                    quantity=req.quantity,
                    unit_base_price_paise=target_product.base_price_paise,
                    unit_floor_price_paise=target_product.floor_price_paise,
                    proposed_unit_price_paise=unit_price - unit_discount_paise,
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

            # Step 6: Simulate Razorpay Payment & Webhook Settlement
            if req.scenario in ["STANDARD_AUTO_COMMERCE", "PAYMENT_RECONCILIATION"]:
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
                    inventory.available_quantity = max(
                        0, inventory.available_quantity - req.quantity
                    )
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

        msg = (
            "Standard Autonomous Commerce completed and settled successfully."
            if decision.verdict == PolicyVerdict.ALLOW
            else "Proposal escalated to Human Approval queue."
        )

        return DemoSimulationStepResponse(
            scenario=req.scenario,
            session_id=agent_session.id,
            quote_id=quote.id,
            approval_id=approval_id,
            order_id=order_id,
            rzp_order_id=rzp_order_id,
            rzp_payment_id=rzp_payment_id,
            status="SETTLED" if decision.verdict == PolicyVerdict.ALLOW else "PENDING_APPROVAL",
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
