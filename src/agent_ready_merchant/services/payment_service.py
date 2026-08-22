"""Payment and Order Service orchestrating Razorpay integration with authoritative FSMs.

Adheres strictly to docs/razorpay-integration-notes.md, INV-FIN-04, and INV-FIN-05.
"""

import json
import logging
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from agent_ready_merchant.integrations.razorpay.client import RazorpayClient
from agent_ready_merchant.integrations.razorpay.exceptions import (
    AmountMismatchFraudError,
    RazorpayError,
)
from agent_ready_merchant.integrations.razorpay.webhook import (
    assert_valid_webhook_signature,
)
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.order import Order, OrderItem
from agent_ready_merchant.models.payment import PaymentAttempt
from agent_ready_merchant.models.quote import PriceQuote
from agent_ready_merchant.models.transaction import TransactionRecord
from agent_ready_merchant.state_machines.order import OrderStateMachine
from agent_ready_merchant.state_machines.payment_attempt import PaymentAttemptStateMachine

logger = logging.getLogger("agent_ready_merchant.services.payment")


class PaymentService:
    """Server-authoritative coordinator for Orders, Payments, and Razorpay interactions."""

    @classmethod
    async def create_order_from_accepted_quote(
        cls,
        session: AsyncSession,
        quote_id: uuid.UUID,
        buyer_email: str,
        shipping_address: dict[str, Any],
        rzp_client: RazorpayClient,
    ) -> Order:
        """Creates a local Order and Razorpay Order for an ACCEPTED PriceQuote."""
        # 1. Fetch Quote with items
        stmt = (
            select(PriceQuote)
            .options(selectinload(PriceQuote.items))
            .where(PriceQuote.id == quote_id)
        )
        res = await session.execute(stmt)
        quote = res.scalar_one_or_none()
        if not quote:
            raise ValueError(f"PriceQuote with ID {quote_id} not found")

        if quote.status != "ACCEPTED":
            raise ValueError(
                f"Cannot create order: quote is in '{quote.status}', must be 'ACCEPTED'"
            )

        # 2. Check if order already exists for this quote (Idempotency)
        order_stmt = select(Order).where(Order.quote_id == quote_id)
        existing_order = (await session.execute(order_stmt)).scalar_one_or_none()
        if existing_order:
            return existing_order

        # 3. Call Razorpay API to generate external order
        receipt_id = f"ord_{quote.id.hex[:32]}"
        notes = {
            "platform": "agent-ready-merchant",
            "merchant_id": str(quote.merchant_id),
            "quote_id": str(quote.id),
        }
        rzp_order = await rzp_client.create_order(
            amount_paise=quote.total_paise,
            currency="INR",
            receipt=receipt_id,
            payment_capture=1,
            notes=notes,
        )

        # 4. Create Order entity
        order = Order(
            quote_id=quote.id,
            merchant_id=quote.merchant_id,
            status="CREATED",
            amount_paise=quote.total_paise,
            currency="INR",
            buyer_email=buyer_email,
            shipping_address=shipping_address,
            rzp_order_id=rzp_order.id,
        )
        session.add(order)
        await session.flush()

        # 5. Populate OrderItems
        for q_item in quote.items:
            order_item = OrderItem(
                order_id=order.id,
                variant_id=q_item.variant_id,
                quantity=q_item.quantity,
                unit_price_paise=q_item.unit_price_paise,
                total_price_paise=q_item.total_price_paise,
            )
            session.add(order_item)

        # 6. Advance Order FSM: CREATED -> PENDING_PAYMENT
        await OrderStateMachine.transition(
            session=session,
            order=order,
            target_state="PENDING_PAYMENT",
            expected_version=1,
            actor_type="SYSTEM",
            reason=f"Razorpay order created: {rzp_order.id}",
        )
        await session.flush()

        return order

    @classmethod
    async def process_payment_webhook(
        cls,
        session: AsyncSession,
        raw_body: bytes,
        signature_header: str | None,
        webhook_secret: str,
    ) -> dict[str, Any]:
        """Processes an incoming Razorpay webhook with HMAC verification and idempotency."""
        # 1. Cryptographic HMAC verification
        assert_valid_webhook_signature(
            raw_body=raw_body,
            signature_header=signature_header,
            webhook_secret=webhook_secret,
        )

        # 2. Parse payload safely
        try:
            event_dict = json.loads(raw_body.decode("utf-8"))
        except Exception as exc:
            raise RazorpayError(f"Malformed webhook JSON body: {exc}") from exc

        event_name = event_dict.get("event")
        payload = event_dict.get("payload", {})
        payment_data = payload.get("payment", {}).get("entity", {})
        order_data = payload.get("order", {}).get("entity", {})

        rzp_payment_id = payment_data.get("id")
        rzp_order_id = payment_data.get("order_id") or order_data.get("id")
        amount_paise = payment_data.get("amount") or order_data.get("amount")

        if not rzp_order_id:
            logger.warning("Webhook event '%s' ignored: missing rzp_order_id", event_name)
            return {"status": "IGNORED", "reason": "missing_rzp_order_id"}

        # 3. Lookup Order by rzp_order_id
        order_stmt = select(Order).where(Order.rzp_order_id == rzp_order_id)
        order = (await session.execute(order_stmt)).scalar_one_or_none()
        if not order:
            logger.warning(
                "Webhook event '%s' ignored: order '%s' not found", event_name, rzp_order_id
            )
            return {"status": "IGNORED", "reason": "order_not_found"}

        # 4. Handle event types
        if event_name in {"order.paid", "payment.captured"}:
            return await cls._handle_payment_success(
                session=session,
                order=order,
                rzp_payment_id=rzp_payment_id,
                rzp_order_id=rzp_order_id,
                amount_paise=amount_paise,
                payment_data=payment_data,
                event_name=event_name,
            )
        elif event_name == "payment.failed":
            return await cls._handle_payment_failure(
                session=session,
                order=order,
                rzp_payment_id=rzp_payment_id,
                rzp_order_id=rzp_order_id,
                amount_paise=amount_paise,
                payment_data=payment_data,
            )
        else:
            logger.info("Webhook event '%s' received without state action", event_name)
            return {"status": "ACKNOWLEDGED", "event": event_name}

    @classmethod
    async def _handle_payment_success(
        cls,
        session: AsyncSession,
        order: Order,
        rzp_payment_id: str | None,
        rzp_order_id: str,
        amount_paise: int | None,
        payment_data: dict[str, Any],
        event_name: str,
    ) -> dict[str, Any]:
        """Settles payment and executes transitions to PAID and TransactionRecord creation."""
        # Check Amount Invariant (Anti-Fraud)
        if amount_paise is not None and amount_paise != order.amount_paise:
            # Amount mismatch: Log critical security fraud attempt
            audit_event = AuditEvent(
                merchant_id=order.merchant_id,
                session_id=None,
                actor_type="SYSTEM",
                event_type="PAYMENT_AMOUNT_FRAUD_DETECTED",
                payload={
                    "order_id": str(order.id),
                    "expected_amount_paise": order.amount_paise,
                    "received_amount_paise": amount_paise,
                    "rzp_payment_id": rzp_payment_id,
                },
                event_hash=f"fraud_{order.id}_{rzp_payment_id}",
            )
            session.add(audit_event)
            await session.flush()
            raise AmountMismatchFraudError(
                expected_amount_paise=order.amount_paise,
                received_amount_paise=amount_paise,
            )

        # Idempotency Check: check if payment attempt already exists and is CAPTURED
        pay_stmt = select(PaymentAttempt).where(
            PaymentAttempt.order_id == order.id,
            PaymentAttempt.rzp_payment_id == rzp_payment_id,
        )
        existing_attempt = (await session.execute(pay_stmt)).scalar_one_or_none()

        if existing_attempt and existing_attempt.status == "CAPTURED" and order.status == "PAID":
            # Idempotent return without duplicate transaction records
            return {
                "status": "DUPLICATE_IGNORED",
                "order_id": str(order.id),
                "payment_id": rzp_payment_id,
            }

        # Create or update PaymentAttempt
        if not existing_attempt:
            payment_attempt = PaymentAttempt(
                order_id=order.id,
                rzp_payment_id=rzp_payment_id,
                rzp_order_id=rzp_order_id,
                status="CAPTURED",
                amount_paise=order.amount_paise,
                payment_method=payment_data.get("method"),
                webhook_payload=payment_data,
            )
            session.add(payment_attempt)
            await session.flush()
        else:
            if existing_attempt.status != "CAPTURED":
                await PaymentAttemptStateMachine.transition(
                    session=session,
                    payment=existing_attempt,
                    target_state="CAPTURED",
                    reason="Webhook confirmation",
                )
            payment_attempt = existing_attempt

        # Advance Order state to PAID if not already paid
        if order.status in {"PENDING_PAYMENT", "PAYMENT_PROCESSING", "PAYMENT_FAILED"}:
            if order.status == "PENDING_PAYMENT":
                # Advance PENDING_PAYMENT -> PAYMENT_PROCESSING
                await OrderStateMachine.transition(
                    session=session,
                    order=order,
                    target_state="PAYMENT_PROCESSING",
                    expected_version=order.version,
                    reason="Payment captured webhook",
                )
            # Advance PAYMENT_PROCESSING -> PAID
            await OrderStateMachine.transition(
                session=session,
                order=order,
                target_state="PAID",
                expected_version=order.version,
                reason=f"Payment verified via {event_name}",
            )

        # Create Append-Only Ledger Entry (TransactionRecord)
        tx_stmt = select(TransactionRecord).where(
            TransactionRecord.payment_attempt_id == payment_attempt.id,
            TransactionRecord.entry_type == "CREDIT",
        )
        existing_tx = (await session.execute(tx_stmt)).scalar_one_or_none()
        if not existing_tx:
            tx_record = TransactionRecord(
                payment_attempt_id=payment_attempt.id,
                merchant_id=order.merchant_id,
                entry_type="CREDIT",
                amount_paise=order.amount_paise,
                status="COMMITTED",
                settlement_ref=rzp_payment_id,
            )
            session.add(tx_record)
            await session.flush()

        return {
            "status": "PROCESSED",
            "order_id": str(order.id),
            "payment_id": rzp_payment_id,
            "order_status": order.status,
        }

    @classmethod
    async def _handle_payment_failure(
        cls,
        session: AsyncSession,
        order: Order,
        rzp_payment_id: str | None,
        rzp_order_id: str,
        amount_paise: int | None,
        payment_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Records payment attempt failure and updates order status."""
        error_obj = payment_data.get("error_code")
        error_desc = payment_data.get("error_description")

        pay_stmt = select(PaymentAttempt).where(
            PaymentAttempt.order_id == order.id,
            PaymentAttempt.rzp_payment_id == rzp_payment_id,
        )
        existing_attempt = (await session.execute(pay_stmt)).scalar_one_or_none()

        if not existing_attempt:
            payment_attempt = PaymentAttempt(
                order_id=order.id,
                rzp_payment_id=rzp_payment_id,
                rzp_order_id=rzp_order_id,
                status="FAILED",
                amount_paise=amount_paise or order.amount_paise,
                error_code=str(error_obj) if error_obj else None,
                error_description=str(error_desc) if error_desc else None,
                webhook_payload=payment_data,
            )
            session.add(payment_attempt)
            await session.flush()

        if order.status == "PAYMENT_PROCESSING":
            await OrderStateMachine.transition(
                session=session,
                order=order,
                target_state="PAYMENT_FAILED",
                expected_version=order.version,
                reason="Payment failed webhook received",
            )

        return {
            "status": "FAILURE_RECORDED",
            "order_id": str(order.id),
            "payment_id": rzp_payment_id,
        }

    @classmethod
    async def reconcile_order(
        cls,
        session: AsyncSession,
        order_id: uuid.UUID,
        rzp_client: RazorpayClient,
    ) -> dict[str, Any]:
        """Out-of-band reconciliation querying Razorpay for authoritative order payment status."""
        stmt = select(Order).where(Order.id == order_id)
        order = (await session.execute(stmt)).scalar_one_or_none()
        if not order:
            raise ValueError(f"Order with ID {order_id} not found")

        if not order.rzp_order_id:
            return {"status": "NO_RZP_ORDER_ID", "order_id": str(order.id)}

        if order.status in {"PAID", "COMPLETED", "CANCELLED", "REFUNDED"}:
            return {"status": "ALREADY_TERMINAL", "order_status": order.status}

        # Query Razorpay for payments tied to this order
        payments = await rzp_client.fetch_order_payments(order.rzp_order_id)
        captured_payment = next((p for p in payments if p.status == "captured"), None)

        if captured_payment:
            # Reconcile missing webhook: settle payment
            payment_data = captured_payment.model_dump()
            return await cls._handle_payment_success(
                session=session,
                order=order,
                rzp_payment_id=captured_payment.id,
                rzp_order_id=order.rzp_order_id,
                amount_paise=captured_payment.amount,
                payment_data=payment_data,
                event_name="reconciliation.fetch",
            )

        return {"status": "RECONCILED_UNPAID", "order_status": order.status}
