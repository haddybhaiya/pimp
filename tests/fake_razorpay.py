"""Deterministic Fake Razorpay Transport for End-to-End Payment Testing.

Simulates Razorpay API interactions in-memory without network calls or mocking away
domain services, state machines, or cryptographic webhook validations:
- POST /v1/orders
- GET /v1/orders/{order_id}
- GET /v1/orders?receipt={receipt}
- GET /v1/orders/{order_id}/payments
- GET /v1/payments/{payment_id}
- Programmable failure injections (timeouts, server errors, timeouts after remote mutation)
- Cryptographic HMAC SHA-256 signed webhook generation
"""

import hashlib
import hmac
import json
import time
import uuid
from typing import Any

import httpx

from agent_ready_merchant.integrations.razorpay.client import RazorpayClient


class DeterministicFakeRazorpayTransport(httpx.AsyncBaseTransport):
    """In-memory stateful Razorpay HTTP transport."""

    def __init__(self, webhook_secret: str | None = None) -> None:
        self.webhook_secret = webhook_secret or "test_secret_for_fake_transport"
        self.orders: dict[str, dict[str, Any]] = {}
        self.orders_by_receipt: dict[str, dict[str, Any]] = {}
        self.payments: dict[str, dict[str, Any]] = {}
        self.payments_by_order: dict[str, list[dict[str, Any]]] = {}

        # Inspection counters
        self.create_order_calls = 0
        self.fetch_order_by_receipt_calls = 0
        self.fetch_payments_calls = 0

        # Fault injection flags
        self.simulate_order_creation_timeout = False
        self.simulate_order_creation_timeout_after_save = False
        self.simulate_order_creation_500 = False

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        url_path = request.url.path
        method = request.method

        if method == "POST" and url_path == "/v1/orders":
            self.create_order_calls += 1
            content = await request.aread()
            body = json.loads(content.decode("utf-8")) if content else {}
            order_id = f"order_fake_{uuid.uuid4().hex[:12]}"
            receipt = body.get("receipt", "")
            amount = body.get("amount", 0)
            currency = body.get("currency", "INR")
            order_data = {
                "id": order_id,
                "entity": "order",
                "amount": amount,
                "amount_paid": 0,
                "amount_due": amount,
                "currency": currency,
                "receipt": receipt,
                "status": "created",
                "attempts": 0,
                "created_at": int(time.time()),
            }

            if self.simulate_order_creation_timeout_after_save:
                # Order succeeded remotely at Razorpay, but connection dropped before response
                self.orders[order_id] = order_data
                if receipt:
                    self.orders_by_receipt[receipt] = order_data
                raise httpx.ReadTimeout("Simulated external read timeout after remote creation")

            if self.simulate_order_creation_timeout:
                raise httpx.ConnectTimeout("Simulated external connect timeout")

            if self.simulate_order_creation_500:
                return httpx.Response(
                    500,
                    json={
                        "error": {
                            "code": "SERVER_ERROR",
                            "description": "Simulated Razorpay internal server error",
                        }
                    },
                )

            self.orders[order_id] = order_data
            if receipt:
                self.orders_by_receipt[receipt] = order_data
            return httpx.Response(200, json=order_data)

        if method == "GET" and url_path == "/v1/orders":
            self.fetch_order_by_receipt_calls += 1
            receipt = request.url.params.get("receipt")
            matching = []
            if receipt and receipt in self.orders_by_receipt:
                matching.append(self.orders_by_receipt[receipt])
            return httpx.Response(
                200,
                json={"entity": "collection", "count": len(matching), "items": matching},
            )

        if (
            method == "GET"
            and url_path.startswith("/v1/orders/")
            and url_path.endswith("/payments")
        ):
            self.fetch_payments_calls += 1
            order_id = url_path.split("/")[3]
            items = self.payments_by_order.get(order_id, [])
            return httpx.Response(
                200,
                json={"entity": "collection", "count": len(items), "items": items},
            )

        if method == "GET" and url_path.startswith("/v1/orders/"):
            order_id = url_path.split("/")[3]
            if order_id in self.orders:
                return httpx.Response(200, json=self.orders[order_id])
            return httpx.Response(
                404,
                json={"error": {"code": "BAD_REQUEST_ERROR", "description": "Order not found"}},
            )

        if method == "GET" and url_path.startswith("/v1/payments/"):
            pay_id = url_path.split("/")[3]
            if pay_id in self.payments:
                return httpx.Response(200, json=self.payments[pay_id])
            return httpx.Response(
                404,
                json={"error": {"code": "BAD_REQUEST_ERROR", "description": "Payment not found"}},
            )

        return httpx.Response(404, json={"error": {"code": "ROUTE_NOT_FOUND"}})

    def simulate_payment(
        self,
        order_id: str,
        amount: int | None = None,
        currency: str = "INR",
        method: str = "upi",
        status: str = "captured",
        error_code: str | None = None,
        error_description: str | None = None,
        created_at: int | None = None,
    ) -> tuple[dict[str, Any], bytes, str]:
        """Records a simulated payment and generates an HMAC-signed webhook payload."""
        order = self.orders.get(order_id)
        pay_amount = amount if amount is not None else (order["amount"] if order else 10000)
        pay_id = f"pay_fake_{uuid.uuid4().hex[:12]}"
        now_ts = created_at if created_at is not None else int(time.time())

        pay_data = {
            "id": pay_id,
            "entity": "payment",
            "amount": pay_amount,
            "currency": currency,
            "status": status,
            "order_id": order_id,
            "method": method,
            "captured": (status == "captured"),
            "created_at": now_ts,
        }
        if error_code:
            pay_data["error_code"] = error_code
            pay_data["error_description"] = error_description or "Payment failed"

        self.payments[pay_id] = pay_data
        if order_id not in self.payments_by_order:
            self.payments_by_order[order_id] = []
        self.payments_by_order[order_id].append(pay_data)

        if order and status == "captured":
            # Accumulate total captured amount across all payments to correctly reflect
            # multi-payment and partial-payment scenarios (fix: Issue 13).
            total_captured = sum(
                p["amount"]
                for p in self.payments_by_order.get(order_id, [])
                if p.get("status") == "captured"
            )
            order["amount_paid"] = total_captured
            order["amount_due"] = max(0, order["amount"] - total_captured)
            if order["amount_due"] == 0:
                order["status"] = "paid"

        event_name = "payment.captured" if status == "captured" else "payment.failed"
        webhook_body = {
            "entity": "event",
            "account_id": "acc_fake_01",
            "event": event_name,
            "contains": ["payment", "order"],
            "payload": {
                "payment": {"entity": pay_data},
                "order": {
                    "entity": order or {"id": order_id, "amount": pay_amount, "currency": currency}
                },
            },
            "created_at": now_ts,
        }
        raw_body = json.dumps(webhook_body).encode("utf-8")
        signature = hmac.new(
            self.webhook_secret.encode("utf-8"), raw_body, hashlib.sha256
        ).hexdigest()
        return webhook_body, raw_body, signature

    def build_client(self) -> RazorpayClient:
        """Constructs a RazorpayClient bound to this deterministic transport."""
        http_client = httpx.AsyncClient(transport=self)
        return RazorpayClient(
            key_id="rzp_test_fake_key",
            key_secret="fake_rzp_secret",
            http_client=http_client,
        )
