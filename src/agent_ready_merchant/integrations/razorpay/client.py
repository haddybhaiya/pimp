"""Server-side asynchronous client adapter for Razorpay API.

Adheres strictly to docs/razorpay-integration-notes.md and INV-AGY-03 (Zero Secret Leakage).
"""

import logging
from typing import Any

import httpx
from pydantic import SecretStr

from agent_ready_merchant.integrations.razorpay.exceptions import (
    RazorpayAPIError,
    RazorpayAuthenticationError,
    RazorpayBadRequestError,
    RazorpayNetworkError,
    RazorpayNotFoundError,
    RazorpayRateLimitError,
    RazorpayServerError,
    RazorpayTimeoutError,
)
from agent_ready_merchant.integrations.razorpay.models import (
    RazorpayOrderCreateRequest,
    RazorpayOrderResponse,
    RazorpayPaymentCollection,
    RazorpayPaymentResponse,
    RazorpayRefundResponse,
)

logger = logging.getLogger("agent_ready_merchant.integrations.razorpay")


class RazorpayClient:
    """Server-authoritative client adapter for Razorpay test-mode API."""

    def __init__(
        self,
        key_id: str,
        key_secret: SecretStr | str,
        base_url: str = "https://api.razorpay.com/v1",
        timeout: float = 10.0,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.key_id = key_id
        self._key_secret = (
            key_secret.get_secret_value() if isinstance(key_secret, SecretStr) else key_secret
        )
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._custom_client = http_client

    def _get_auth(self) -> tuple[str, str]:
        return (self.key_id, self._key_secret)

    async def _send_request(
        self,
        method: str,
        endpoint: str,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Dispatches an authenticated HTTP request with timeout and error handling."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        auth = self._get_auth()

        async def _execute(client: httpx.AsyncClient) -> httpx.Response:
            return await client.request(
                method=method,
                url=url,
                auth=auth,
                json=json_data,
                timeout=self.timeout,
            )

        try:
            if self._custom_client:
                response = await _execute(self._custom_client)
            else:
                async with httpx.AsyncClient() as client:
                    response = await _execute(client)

            if response.status_code == 401:
                logger.error("Razorpay authentication failed (HTTP 401)")
                raise RazorpayAuthenticationError("Invalid Razorpay API credentials")

            if response.is_error:
                error_code: str | None = None
                description: str | None = None
                try:
                    err_json = response.json()
                    error_obj = err_json.get("error", {})
                    error_code = error_obj.get("code")
                    description = error_obj.get("description") or error_obj.get("reason")
                except Exception:
                    description = response.text

                logger.warning(
                    "Razorpay returned error status %d: [%s] %s",
                    response.status_code,
                    error_code,
                    description,
                )
                if response.status_code == 400:
                    raise RazorpayBadRequestError(
                        status_code=response.status_code,
                        error_code=error_code,
                        description=description,
                    )
                if response.status_code == 404:
                    raise RazorpayNotFoundError(
                        status_code=response.status_code,
                        error_code=error_code,
                        description=description,
                    )
                if response.status_code == 429:
                    raise RazorpayRateLimitError(
                        status_code=response.status_code,
                        error_code=error_code,
                        description=description,
                    )
                if response.status_code >= 500:
                    raise RazorpayServerError(
                        status_code=response.status_code,
                        error_code=error_code,
                        description=description,
                    )
                raise RazorpayAPIError(
                    status_code=response.status_code,
                    error_code=error_code,
                    description=description,
                )

            return response.json()  # type: ignore[no-any-return]

        except httpx.TimeoutException as exc:
            logger.error("Timeout communicating with Razorpay: %s", exc)
            raise RazorpayTimeoutError(f"Razorpay request timed out after {self.timeout}s") from exc
        except httpx.NetworkError as exc:
            logger.error("Network error communicating with Razorpay: %s", exc)
            raise RazorpayNetworkError(f"Network error connecting to Razorpay: {exc}") from exc

    async def create_order(
        self,
        amount_paise: int,
        currency: str = "INR",
        receipt: str = "",
        payment_capture: int = 1,
        notes: dict[str, Any] | None = None,
    ) -> RazorpayOrderResponse:
        """Creates an order in Razorpay (POST /v1/orders)."""
        req_payload = RazorpayOrderCreateRequest(
            amount=amount_paise,
            currency=currency,
            receipt=receipt[:40],
            payment_capture=payment_capture,
            notes=notes or {},
        )
        data = await self._send_request("POST", "orders", json_data=req_payload.model_dump())
        return RazorpayOrderResponse.model_validate(data)

    async def fetch_order(self, rzp_order_id: str) -> RazorpayOrderResponse:
        """Fetches order details by Razorpay order ID (GET /v1/orders/{id})."""
        data = await self._send_request("GET", f"orders/{rzp_order_id}")
        return RazorpayOrderResponse.model_validate(data)

    async def fetch_order_payments(self, rzp_order_id: str) -> list[RazorpayPaymentResponse]:
        """Fetches all payments associated with an order (GET /v1/orders/{id}/payments)."""
        data = await self._send_request("GET", f"orders/{rzp_order_id}/payments")
        collection = RazorpayPaymentCollection.model_validate(data)
        return collection.items

    async def fetch_payment(self, rzp_payment_id: str) -> RazorpayPaymentResponse:
        """Fetches payment details by Razorpay payment ID (GET /v1/payments/{id})."""
        data = await self._send_request("GET", f"payments/{rzp_payment_id}")
        return RazorpayPaymentResponse.model_validate(data)

    async def create_refund(
        self,
        rzp_payment_id: str,
        amount_paise: int | None = None,
        notes: dict[str, Any] | None = None,
    ) -> RazorpayRefundResponse:
        """Creates a refund for a payment (POST /v1/payments/{id}/refund)."""
        payload: dict[str, Any] = {}
        if amount_paise is not None:
            payload["amount"] = amount_paise
        if notes:
            payload["notes"] = notes

        data = await self._send_request(
            "POST", f"payments/{rzp_payment_id}/refund", json_data=payload
        )
        return RazorpayRefundResponse.model_validate(data)
