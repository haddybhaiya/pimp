"""Payment and Order Service orchestrating Razorpay integration with authoritative FSMs.

Adheres strictly to docs/razorpay-integration-notes.md, INV-FIN-04, and INV-FIN-05.
"""

import hashlib
import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from agent_ready_merchant.db.concurrency import OptimisticLockError, update_with_version_check
from agent_ready_merchant.db.session import get_session_factory
from agent_ready_merchant.integrations.razorpay.client import RazorpayClient
from agent_ready_merchant.integrations.razorpay.exceptions import (
    AmountMismatchFraudError,
    CurrencyMismatchFraudError,
    OrderMismatchError,
    RazorpayAPIError,
    RazorpayError,
    RazorpayNetworkError,
    RazorpayRateLimitError,
    RazorpayServerError,
    RazorpayTimeoutError,
    TransactionBindingError,
    WebhookProcessingInProgressError,
    WebhookTimestampError,
)
from agent_ready_merchant.integrations.razorpay.webhook import (
    assert_valid_webhook_signature,
)
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.inventory import InventoryItem
from agent_ready_merchant.models.order import Order, OrderItem
from agent_ready_merchant.models.payment import PaymentAttempt
from agent_ready_merchant.models.quote import PriceQuote
from agent_ready_merchant.models.transaction import TransactionRecord
from agent_ready_merchant.models.webhook import ProcessedWebhook
from agent_ready_merchant.state_machines.base import (
    InvalidStateTransitionError,
    TerminalStateError,
)
from agent_ready_merchant.state_machines.order import OrderStateMachine
from agent_ready_merchant.state_machines.payment_attempt import PaymentAttemptStateMachine

logger = logging.getLogger("agent_ready_merchant.services.payment")

_EXTERNAL_ATTEMPT_EVENT = "EXTERNAL_ORDER_ATTEMPT"
_EXTERNAL_OUTCOME_EVENT = "EXTERNAL_ORDER_OUTCOME"


class PaymentService:
    """Server-authoritative coordinator for Orders, Payments, and Razorpay interactions."""

    @classmethod
    def validate_transaction_binding(
        cls,
        payment_attempt: PaymentAttempt,
        order: Order,
        merchant_id: uuid.UUID,
        amount_paise: int,
    ) -> None:
        """Enforces strict multi-entity binding invariants before committing ledger entries."""
        if payment_attempt.order_id != order.id:
            raise TransactionBindingError(
                f"Transaction binding violation: payment attempt order "
                f"'{payment_attempt.order_id}' does not match target order '{order.id}'"
            )
        if merchant_id != order.merchant_id:
            raise TransactionBindingError(
                f"Transaction binding violation: merchant '{merchant_id}' "
                f"does not match order merchant '{order.merchant_id}'"
            )
        if payment_attempt.status != "CAPTURED":
            raise TransactionBindingError(
                f"Transaction binding violation: payment attempt is in status "
                f"'{payment_attempt.status}', must be 'CAPTURED' to commit credit"
            )
        if amount_paise != order.amount_paise or amount_paise != payment_attempt.amount_paise:
            raise TransactionBindingError(
                f"Transaction binding violation: amount {amount_paise} does not match "
                f"order amount {order.amount_paise} or attempt {payment_attempt.amount_paise}"
            )

    @classmethod
    async def create_order_from_accepted_quote(
        cls,
        session: AsyncSession,
        quote_id: uuid.UUID,
        buyer_email: str,
        shipping_address: dict[str, Any],
        rzp_client: RazorpayClient,
        merchant_id: uuid.UUID | None = None,
        session_id: uuid.UUID | None = None,
    ) -> Order:
        """Creates a local Order and Razorpay Order for an ACCEPTED PriceQuote."""
        # 1. Fetch Quote with items and lock quote row against concurrent duplicate checkouts
        stmt = (
            select(PriceQuote)
            .options(selectinload(PriceQuote.items))
            .where(PriceQuote.id == quote_id)
            .with_for_update()
        )
        res = await session.execute(stmt)
        quote = res.scalar_one_or_none()
        if not quote:
            raise ValueError(f"PriceQuote with ID {quote_id} not found")

        if merchant_id is not None and quote.merchant_id != merchant_id:
            raise ValueError(
                f"PriceQuote '{quote_id}' does not belong to authenticated merchant '{merchant_id}'"
            )
        if session_id is not None and quote.session_id != session_id:
            raise ValueError(
                f"PriceQuote '{quote_id}' does not belong to active session '{session_id}'"
            )

        if quote.status != "ACCEPTED":
            raise ValueError(
                f"Cannot create order: quote is in '{quote.status}', must be 'ACCEPTED'"
            )

        # Enforce quote expiry invariant
        now = datetime.now(UTC)
        quote_expires = (
            quote.expires_at
            if quote.expires_at.tzinfo is not None
            else quote.expires_at.replace(tzinfo=UTC)
        )
        if now > quote_expires:
            raise ValueError(
                f"Cannot create order: PriceQuote '{quote_id}' expired at "
                f"{quote_expires.isoformat()}"
            )

        # 2. Check if order already exists for this quote (Idempotency)
        order_stmt = select(Order).where(Order.quote_id == quote_id).with_for_update()
        existing_order = (await session.execute(order_stmt)).scalar_one_or_none()
        if existing_order:
            return existing_order

        # 2.5 Pre-flight stock availability check for each quote line item
        for q_item in quote.items:
            inv_stmt = select(InventoryItem).where(InventoryItem.variant_id == q_item.variant_id)
            inv = (await session.execute(inv_stmt)).scalar_one_or_none()
            if inv is not None and inv.available_quantity < q_item.quantity + inv.safety_threshold:
                raise ValueError(
                    f"Insufficient stock for variant '{q_item.variant_id}': "
                    f"requested {q_item.quantity}, available {inv.available_quantity} "
                    f"(safety threshold: {inv.safety_threshold})"
                )

        # 3. Call Razorpay API to generate external order — with duplicate protection.
        # A timeout after remote creation but before local commit orphans the remote
        # order; retrying blindly creates a second Razorpay order. We therefore
        # persist a durable breadcrumb (append-only audit event in an INDEPENDENT
        # transaction) immediately after remote creation, and on retry reuse the
        # still-open remote order instead of creating a new one.
        receipt_id = f"ord_{quote.id.hex[:32]}"
        notes = {
            "platform": "agent-ready-merchant",
            "merchant_id": str(quote.merchant_id),
            "quote_id": str(quote.id),
        }
        rzp_order = await cls._find_reusable_external_order(session, quote, rzp_client)
        if rzp_order is not None:
            logger.info(
                "Reusing orphaned external Razorpay order '%s' for quote '%s'",
                rzp_order.id,
                quote.id,
            )
        else:
            await cls._record_external_attempt_started(quote=quote, receipt_id=receipt_id)
            rzp_order = await rzp_client.create_order(
                amount_paise=quote.total_paise,
                currency="INR",
                receipt=receipt_id,
                payment_capture=1,
                notes=notes,
            )
            await cls._record_external_attempt(quote=quote, rzp_order=rzp_order)

        # 4. Atomically reserve inventory and create Order entity
        for q_item in quote.items:
            inv_stmt = select(InventoryItem).where(InventoryItem.variant_id == q_item.variant_id)
            inv = (await session.execute(inv_stmt)).scalar_one_or_none()
            if inv is not None:
                if inv.available_quantity < q_item.quantity + inv.safety_threshold:
                    raise ValueError(
                        f"Insufficient stock for variant '{q_item.variant_id}': "
                        f"requested {q_item.quantity}, available {inv.available_quantity} "
                        f"(safety threshold: {inv.safety_threshold})"
                    )
                new_avail = inv.available_quantity - q_item.quantity
                new_res = inv.reserved_quantity + q_item.quantity
                await update_with_version_check(
                    session=session,
                    model_class=InventoryItem,
                    entity_id=inv.id,
                    expected_version=inv.version,
                    values={"available_quantity": new_avail, "reserved_quantity": new_res},
                )
                inv.available_quantity = new_avail
                inv.reserved_quantity = new_res
                inv.version += 1

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

        # Close out the breadcrumb ATOMICALLY with the local order (same
        # transaction): if this transaction commits, the remote order is
        # accounted for; if it rolls back, the CONSUMED event never existed
        # and the breadcrumb stays PENDING so a retry reuses the remote order.
        await AuditEvent.create_event(
            session=session,
            merchant_id=quote.merchant_id,
            actor_type="SYSTEM",
            event_type=_EXTERNAL_OUTCOME_EVENT,
            payload={
                "quote_id": str(quote.id),
                "rzp_order_id": rzp_order.id,
                "status": "CONSUMED",
            },
            session_id=session_id,
        )

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
        pay_order_id = payment_data.get("order_id")
        envelope_order_id = order_data.get("id")

        # 2a. Replay Protection: Validate webhook timestamp if present in payload
        created_at_ts = event_dict.get("created_at")
        if created_at_ts is not None:
            now_ts = int(datetime.now(UTC).timestamp())
            # Allow up to 24 hours in the past (Razorpay retry max window) and 300s clock skew
            if created_at_ts < now_ts - 86400 or created_at_ts > now_ts + 300:
                logger.warning(
                    "Webhook event '%s' rejected: timestamp %s outside valid window (current %s)",
                    event_name,
                    created_at_ts,
                    now_ts,
                )
                raise WebhookTimestampError(
                    f"Webhook event timestamp {created_at_ts} is outside the allowed replay window"
                )

        # 2b. Atomic Webhook Deduplication (Durable DB uniqueness)
        payload_hash = hashlib.sha256(raw_body).hexdigest()
        sig_header_clean = (signature_header or "").strip()
        signature_hash = hashlib.sha256(sig_header_clean.encode("utf-8")).hexdigest()

        pw_stmt = select(ProcessedWebhook).where(ProcessedWebhook.payload_hash == payload_hash)
        existing_pw = (await session.execute(pw_stmt)).scalar_one_or_none()
        if existing_pw:
            if existing_pw.status in {"PROCESSED", "IGNORED"}:
                logger.info(
                    "Atomic webhook deduplication: payload %s already terminal (status=%s)",
                    payload_hash,
                    existing_pw.status,
                )
                return {
                    "status": "DUPLICATE_IGNORED",
                    "order_id": str(existing_pw.rzp_order_id or ""),
                    "payment_id": existing_pw.rzp_payment_id,
                }
            elif existing_pw.status == "PROCESSING":
                logger.info("Webhook %s currently processing in another transaction", payload_hash)
                raise WebhookProcessingInProgressError(
                    "Webhook payload is currently being processed by another transaction"
                )

        pw_record = ProcessedWebhook(
            event_id=event_dict.get("id"),
            event_name=str(event_name or "unknown"),
            payload_hash=payload_hash,
            signature_hash=signature_hash,
            rzp_order_id=envelope_order_id or pay_order_id,
            rzp_payment_id=rzp_payment_id,
            status="PROCESSING",
        )
        session.add(pw_record)
        try:
            await session.flush()
        except IntegrityError as exc:
            await session.rollback()
            logger.info("Concurrent webhook delivery collision caught by unique constraint")
            pw_check_stmt = select(ProcessedWebhook).where(
                ProcessedWebhook.payload_hash == payload_hash
            )
            committed_pw = (await session.execute(pw_check_stmt)).scalar_one_or_none()
            if committed_pw and committed_pw.status == "PROCESSED":
                return {
                    "status": "DUPLICATE_IGNORED",
                    "order_id": str(committed_pw.rzp_order_id or ""),
                    "payment_id": committed_pw.rzp_payment_id,
                }
            raise WebhookProcessingInProgressError(
                "Concurrent webhook delivery detected; winner transaction in flight"
            ) from exc

        # 2c. Cross-payload order mismatch check
        if pay_order_id and envelope_order_id and pay_order_id != envelope_order_id:
            m_stmt = select(Order).where(Order.rzp_order_id.in_([envelope_order_id, pay_order_id]))
            matched_ord = (await session.execute(m_stmt)).scalars().first()
            if matched_ord:
                await AuditEvent.create_event(
                    session=session,
                    merchant_id=matched_ord.merchant_id,
                    session_id=None,
                    actor_type="SYSTEM",
                    event_type="PAYMENT_ORDER_MISMATCH_DETECTED",
                    payload={
                        "order_id": str(matched_ord.id),
                        "expected_rzp_order_id": envelope_order_id,
                        "received_rzp_order_id": pay_order_id,
                        "rzp_payment_id": rzp_payment_id,
                    },
                )
            raise OrderMismatchError(
                expected_order_id=envelope_order_id,
                received_order_id=pay_order_id,
            )

        rzp_order_id = envelope_order_id or pay_order_id
        amount_paise = payment_data.get("amount") or order_data.get("amount")

        if not rzp_order_id:
            logger.warning("Webhook event '%s' ignored: missing rzp_order_id", event_name)
            pw_record.status = "IGNORED"
            pw_record.response_payload = {"status": "IGNORED", "reason": "missing_rzp_order_id"}
            await session.flush()
            return {"status": "IGNORED", "reason": "missing_rzp_order_id"}

        # 3. Lookup Order by rzp_order_id with row-level lock for serialization
        order_stmt = select(Order).where(Order.rzp_order_id == rzp_order_id).with_for_update()
        order = (await session.execute(order_stmt)).scalar_one_or_none()
        if not order:
            logger.warning(
                "Webhook event '%s' ignored: order '%s' not found", event_name, rzp_order_id
            )
            pw_record.status = "IGNORED"
            pw_record.response_payload = {"status": "IGNORED", "reason": "order_not_found"}
            await session.flush()
            return {"status": "IGNORED", "reason": "order_not_found"}

        # Strict payment-to-order binding check
        if pay_order_id and pay_order_id != order.rzp_order_id:
            await AuditEvent.create_event(
                session=session,
                merchant_id=order.merchant_id,
                session_id=None,
                actor_type="SYSTEM",
                event_type="PAYMENT_ORDER_MISMATCH_DETECTED",
                payload={
                    "order_id": str(order.id),
                    "expected_rzp_order_id": order.rzp_order_id,
                    "received_rzp_order_id": pay_order_id,
                    "rzp_payment_id": rzp_payment_id,
                },
            )
            raise OrderMismatchError(
                expected_order_id=order.rzp_order_id,
                received_order_id=pay_order_id,
            )

        # Currency MUST come exclusively from the payment entity — never from order_data.
        # Falling back to order_data would allow a cross-currency attack to silently pass
        # verification (INV-FIN-05 fail-closed).
        currency = payment_data.get("currency")

        # 4. Handle event types
        if event_name in {"order.paid", "payment.captured"}:
            if not rzp_payment_id:
                logger.warning("Webhook %s missing payment ID", event_name)
                pw_record.status = "IGNORED"
                pw_record.response_payload = {"status": "IGNORED", "reason": "missing_payment_id"}
                await session.flush()
                return {"status": "IGNORED", "reason": "missing_payment_id"}
            if not amount_paise or int(amount_paise) <= 0:
                logger.warning("Webhook %s invalid amount: %s", event_name, amount_paise)
                pw_record.status = "IGNORED"
                pw_record.response_payload = {
                    "status": "IGNORED",
                    "reason": "invalid_payment_amount",
                }
                await session.flush()
                return {"status": "IGNORED", "reason": "invalid_payment_amount"}

            result = await cls._handle_payment_success(
                session=session,
                order=order,
                rzp_payment_id=rzp_payment_id,
                rzp_order_id=rzp_order_id,
                amount_paise=int(amount_paise),
                payment_data=payment_data,
                event_name=event_name,
                currency=str(currency) if currency else None,
            )
        elif event_name == "payment.failed":
            result = await cls._handle_payment_failure(
                session=session,
                order=order,
                rzp_payment_id=rzp_payment_id,
                rzp_order_id=rzp_order_id,
                amount_paise=amount_paise,
                payment_data=payment_data,
            )
        else:
            logger.info("Webhook event '%s' received without state action", event_name)
            result = {"status": "ACKNOWLEDGED", "event": event_name}

        # Update processed webhook record
        pw_record.status = (
            "PROCESSED"
            if result.get("status") in {"PROCESSED", "FAILURE_RECORDED", "ACKNOWLEDGED"}
            else "DUPLICATE_IGNORED"
        )
        pw_record.response_payload = result
        pw_record.processed_at = datetime.now(UTC)
        await session.flush()
        return result

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
        currency: str | None = None,
    ) -> dict[str, Any]:
        """Settles payment and executes transitions to PAID and TransactionRecord creation."""
        # 1. Check Currency Invariant (Anti-Fraud: Fail-Closed)
        curr = currency or payment_data.get("currency")
        if not curr or str(curr).strip().upper() != order.currency.upper():
            await AuditEvent.create_event(
                session=session,
                merchant_id=order.merchant_id,
                session_id=None,
                actor_type="SYSTEM",
                event_type="PAYMENT_CURRENCY_FRAUD_DETECTED",
                payload={
                    "order_id": str(order.id),
                    "expected_currency": order.currency,
                    "received_currency": str(curr) if curr else "MISSING",
                    "rzp_payment_id": rzp_payment_id,
                },
            )
            raise CurrencyMismatchFraudError(
                expected_currency=order.currency,
                received_currency=str(curr) if curr else "MISSING",
            )

        # 2. Check Amount Invariant (Anti-Fraud)
        if amount_paise is not None and amount_paise != order.amount_paise:
            # Amount mismatch: Log critical security fraud attempt
            await AuditEvent.create_event(
                session=session,
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
            )
            raise AmountMismatchFraudError(
                expected_amount_paise=order.amount_paise,
                received_amount_paise=amount_paise,
            )

        # 3. Check Order Binding Invariant
        if rzp_order_id != order.rzp_order_id:
            await AuditEvent.create_event(
                session=session,
                merchant_id=order.merchant_id,
                session_id=None,
                actor_type="SYSTEM",
                event_type="PAYMENT_ORDER_MISMATCH_DETECTED",
                payload={
                    "order_id": str(order.id),
                    "expected_rzp_order_id": order.rzp_order_id,
                    "received_rzp_order_id": rzp_order_id,
                    "rzp_payment_id": rzp_payment_id,
                },
            )
            raise OrderMismatchError(
                expected_order_id=order.rzp_order_id,
                received_order_id=rzp_order_id,
            )

        # 4. Idempotency Check: check if payment attempt already exists and is CAPTURED
        pay_stmt = (
            select(PaymentAttempt)
            .where(
                PaymentAttempt.order_id == order.id,
                PaymentAttempt.rzp_payment_id == rzp_payment_id,
            )
            .with_for_update()
        )
        existing_attempt = (await session.execute(pay_stmt)).scalar_one_or_none()

        if existing_attempt and existing_attempt.status == "CAPTURED" and order.status == "PAID":
            # Idempotent return without duplicate transaction records
            return {
                "status": "DUPLICATE_IGNORED",
                "order_id": str(order.id),
                "payment_id": rzp_payment_id,
            }

        # 5. State Regression / Terminal Resurrection Check
        if (
            existing_attempt
            and existing_attempt.status in PaymentAttemptStateMachine.TERMINAL_STATES
        ):
            logger.warning(
                "Rejecting attempt to capture terminal payment %s (status: %s)",
                rzp_payment_id,
                existing_attempt.status,
            )
            return {
                "status": "STATE_REGRESSION_REJECTED",
                "order_id": str(order.id),
                "payment_id": rzp_payment_id,
                "current_status": existing_attempt.status,
            }

        order_id_str = str(order.id)
        merchant_id = order.merchant_id

        try:
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
                        expected_version=existing_attempt.version,
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

            # Strict Transaction Binding Verification
            cls.validate_transaction_binding(
                payment_attempt=payment_attempt,
                order=order,
                merchant_id=merchant_id,
                amount_paise=order.amount_paise,
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
                    merchant_id=merchant_id,
                    entry_type="CREDIT",
                    amount_paise=order.amount_paise,
                    status="COMMITTED",
                    settlement_ref=rzp_payment_id,
                )
                session.add(tx_record)
                await session.flush()
        except (IntegrityError, OptimisticLockError) as exc:
            await session.rollback()
            logger.info(
                "Concurrent webhook delivery collision handled gracefully on order %s: %s",
                order_id_str,
                exc,
            )
            return {
                "status": "DUPLICATE_IGNORED",
                "order_id": order_id_str,
                "payment_id": rzp_payment_id,
            }

        return {
            "status": "PROCESSED",
            "order_id": order_id_str,
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
        order_id_str = str(order.id)

        # Payment State Regression Protection:
        # A failed webhook must never regress an already PAID order or CAPTURED payment
        if order.status in {"PAID", "COMPLETED", "REFUNDED"}:
            logger.warning(
                "Ignoring payment.failed webhook for already settled order %s (status: %s)",
                order_id_str,
                order.status,
            )
            return {
                "status": "STATE_REGRESSION_IGNORED",
                "order_id": order_id_str,
                "payment_id": rzp_payment_id,
            }

        pay_stmt = (
            select(PaymentAttempt)
            .where(
                PaymentAttempt.order_id == order.id,
                PaymentAttempt.rzp_payment_id == rzp_payment_id,
            )
            .with_for_update()
        )
        existing_attempt = (await session.execute(pay_stmt)).scalar_one_or_none()

        if existing_attempt and existing_attempt.status in {"CAPTURED", "REFUNDED"}:
            logger.warning(
                "Ignoring payment.failed webhook for already %s payment %s",
                existing_attempt.status,
                rzp_payment_id,
            )
            return {
                "status": "STATE_REGRESSION_IGNORED",
                "order_id": order_id_str,
                "payment_id": rzp_payment_id,
            }

        try:
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
            else:
                if existing_attempt.status != "FAILED":
                    await PaymentAttemptStateMachine.transition(
                        session=session,
                        payment=existing_attempt,
                        target_state="FAILED",
                        expected_version=existing_attempt.version,
                        reason="Payment failed webhook received",
                    )

            if order.status == "PAYMENT_PROCESSING":
                await OrderStateMachine.transition(
                    session=session,
                    order=order,
                    target_state="PAYMENT_FAILED",
                    expected_version=order.version,
                    reason="Payment failed webhook received",
                )
        except (
            IntegrityError,
            OptimisticLockError,
            InvalidStateTransitionError,
            TerminalStateError,
        ) as exc:
            await session.rollback()
            logger.info("Concurrent or invalid payment failure webhook handled: %s", exc)
            return {
                "status": "DUPLICATE_IGNORED",
                "order_id": order_id_str,
                "payment_id": rzp_payment_id,
            }

        return {
            "status": "FAILURE_RECORDED",
            "order_id": str(order.id),
            "payment_id": rzp_payment_id,
        }

    # -------------------------------------------------------------------------
    # External Order Duplicate Protection (durable breadcrumbs)
    # -------------------------------------------------------------------------
    @classmethod
    async def _latest_external_event(
        cls, session: AsyncSession, quote: PriceQuote
    ) -> AuditEvent | None:
        """Finds the newest breadcrumb event for this quote (any outcome)."""
        stmt = (
            select(AuditEvent)
            .where(
                AuditEvent.merchant_id == quote.merchant_id,
                AuditEvent.event_type.in_([_EXTERNAL_ATTEMPT_EVENT, _EXTERNAL_OUTCOME_EVENT]),
            )
            .order_by(AuditEvent.created_at.desc(), AuditEvent.id.desc())
            .limit(25)
        )
        events = (await session.execute(stmt)).scalars().all()
        for event in events:
            if str(event.payload.get("quote_id")) == str(quote.id):
                return event
        return None

    @classmethod
    async def _find_reusable_external_order(
        cls,
        session: AsyncSession,
        quote: PriceQuote,
        rzp_client: RazorpayClient,
    ) -> Any:
        """Returns the still-open remote order from a prior interrupted attempt.

        A PENDING breadcrumb means Razorpay may already hold an order for this
        quote that never made it into a committed local transaction. The remote
        order is only reused when Razorpay confirms it is still 'created' and
        the amount matches; otherwise the breadcrumb is failed and a fresh
        order must be created. If no breadcrumb exists, it falls back to querying
        Razorpay by deterministic receipt ID.
        """
        latest = await cls._latest_external_event(session, quote)
        if latest is not None and latest.event_type == _EXTERNAL_ATTEMPT_EVENT:
            if latest.payload.get("status") == "PENDING":
                rzp_order_id = latest.payload.get("rzp_order_id")
                if rzp_order_id:
                    try:
                        remote = await rzp_client.fetch_order(rzp_order_id)
                        if remote.status == "created" and remote.amount == quote.total_paise:
                            return remote
                        logger.warning(
                            "External order '%s' is not reusable (status=%s amount=%s)",
                            rzp_order_id,
                            remote.status,
                            remote.amount,
                        )
                        await cls._record_external_outcome(
                            quote=quote, rzp_order_id=rzp_order_id, outcome="FAILED"
                        )
                    except RazorpayError:
                        logger.warning(
                            "Breadcrumb references external order '%s' but fetch failed",
                            rzp_order_id,
                        )
                        await cls._record_external_outcome(
                            quote=quote, rzp_order_id=rzp_order_id, outcome="FAILED"
                        )

        receipt_id = f"ord_{quote.id.hex[:32]}"
        try:
            remote_by_receipt = await rzp_client.fetch_order_by_receipt(receipt_id)
            if (
                remote_by_receipt is not None
                and remote_by_receipt.status == "created"
                and remote_by_receipt.amount == quote.total_paise
            ):
                logger.info(
                    "Reusing external Razorpay order '%s' discovered via receipt '%s'",
                    remote_by_receipt.id,
                    receipt_id,
                )
                await cls._record_external_attempt(quote=quote, rzp_order=remote_by_receipt)
                return remote_by_receipt
        except (
            RazorpayTimeoutError,
            RazorpayNetworkError,
            RazorpayRateLimitError,
            RazorpayServerError,
        ):
            # Transient ambiguity (timeout, network drop, rate-limit, 5xx): re-raise so the
            # caller does NOT proceed to create_order, preventing duplicate remote order
            # creation if Razorpay already created one for this receipt (fix: Issue 2 / INV-FIN-04).
            raise

        except (RazorpayError, Exception) as exc:
            # Definitively no order exists for this receipt (404 Not Found, empty items, or
            # unmocked client) — safe to proceed with fresh order creation.
            logger.debug(
                "Receipt '%s' query not found or ignored (%s); proceeding with new order",
                receipt_id,
                exc,
            )

        return None

    @classmethod
    async def _append_external_event(
        cls,
        merchant_id: uuid.UUID,
        payload: dict[str, Any],
    ) -> None:
        """Appends a breadcrumb audit event in an INDEPENDENT transaction.

        The request transaction may be rolled back at any moment (timeout,
        Razorpay failure); the breadcrumb must survive that rollback to make
        retries idempotent. Failures are logged and swallowed: a missing
        breadcrumb degrades to previous (non-duplicate-protected) behavior.
        """
        try:
            factory = get_session_factory()
            async with factory() as breadcrumb_session:
                await AuditEvent.create_event(
                    session=breadcrumb_session,
                    merchant_id=merchant_id,
                    actor_type="SYSTEM",
                    event_type=_EXTERNAL_ATTEMPT_EVENT
                    if payload["event"] == "attempt"
                    else _EXTERNAL_OUTCOME_EVENT,
                    payload={k: v for k, v in payload.items() if k != "event"},
                    session_id=None,
                )
                await breadcrumb_session.commit()
        except Exception:
            logger.exception("Failed to persist external-order breadcrumb")

    @classmethod
    async def _record_external_attempt_started(cls, quote: PriceQuote, receipt_id: str) -> None:
        await cls._append_external_event(
            merchant_id=quote.merchant_id,
            payload={
                "event": "attempt",
                "quote_id": str(quote.id),
                "receipt": receipt_id,
                "amount_paise": quote.total_paise,
                "status": "PENDING",
            },
        )

    @classmethod
    async def _record_external_attempt(cls, quote: PriceQuote, rzp_order: Any) -> None:
        await cls._append_external_event(
            merchant_id=quote.merchant_id,
            payload={
                "event": "attempt",
                "quote_id": str(quote.id),
                "rzp_order_id": rzp_order.id,
                "amount_paise": quote.total_paise,
                "receipt": f"ord_{quote.id.hex[:32]}",
                "status": "PENDING",
            },
        )

    @classmethod
    async def _record_external_outcome(
        cls, quote: PriceQuote, rzp_order_id: str, outcome: str
    ) -> None:
        await cls._append_external_event(
            merchant_id=quote.merchant_id,
            payload={
                "event": "outcome",
                "quote_id": str(quote.id),
                "rzp_order_id": rzp_order_id,
                "status": outcome,
            },
        )

    @classmethod
    async def reconcile_order(
        cls,
        session: AsyncSession,
        order_id: uuid.UUID,
        rzp_client: RazorpayClient,
        merchant_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        """Out-of-band reconciliation querying Razorpay for authoritative order payment status."""
        stmt = select(Order).where(Order.id == order_id).with_for_update()
        order = (await session.execute(stmt)).scalar_one_or_none()
        if not order:
            raise ValueError(f"Order with ID {order_id} not found")

        if merchant_id is not None and order.merchant_id != merchant_id:
            raise ValueError(
                f"Order '{order_id}' does not belong to authenticated merchant '{merchant_id}'"
            )

        if not order.rzp_order_id:
            return {"status": "NO_RZP_ORDER_ID", "order_id": str(order.id)}

        if order.status in {"PAID", "COMPLETED", "CANCELLED", "REFUNDED"}:
            return {"status": "ALREADY_TERMINAL", "order_status": order.status}

        # Query Razorpay for payments tied to this order
        try:
            payments = await rzp_client.fetch_order_payments(order.rzp_order_id)
        except RazorpayTimeoutError as exc:
            logger.warning("Timeout reconciling order %s with Razorpay: %s", order_id, exc)
            return {
                "status": "RECONCILIATION_FAILED",
                "order_status": order.status,
                "error": "Razorpay request timed out",
                "retryable": True,
            }
        except RazorpayNetworkError as exc:
            logger.warning("Network error reconciling order %s with Razorpay: %s", order_id, exc)
            return {
                "status": "RECONCILIATION_FAILED",
                "order_status": order.status,
                "error": str(exc),
                "retryable": True,
            }
        except RazorpayAPIError as exc:
            logger.warning("Razorpay API error reconciling order %s: %s", order_id, exc)
            return {
                "status": "RECONCILIATION_FAILED",
                "order_status": order.status,
                "error": str(exc),
                "status_code": exc.status_code,
                "retryable": exc.is_retryable,
            }

        captured_payment = next((p for p in payments if p.status == "captured"), None)

        if captured_payment:
            # Server-authoritative currency check (Fail-Closed)
            if (
                not captured_payment.currency
                or captured_payment.currency.strip().upper() != order.currency.upper()
            ):
                await AuditEvent.create_event(
                    session=session,
                    merchant_id=order.merchant_id,
                    session_id=None,
                    actor_type="SYSTEM",
                    event_type="PAYMENT_CURRENCY_FRAUD_DETECTED",
                    payload={
                        "order_id": str(order.id),
                        "expected_currency": order.currency,
                        "received_currency": captured_payment.currency or "MISSING",
                        "rzp_payment_id": captured_payment.id,
                    },
                )
                raise CurrencyMismatchFraudError(
                    expected_currency=order.currency,
                    received_currency=captured_payment.currency or "MISSING",
                )

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
                currency=captured_payment.currency,
            )

        return {"status": "RECONCILED_UNPAID", "order_status": order.status}
