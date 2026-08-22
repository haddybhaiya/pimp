"""Unit tests for RazorpayClient adapter and error mapping."""

import httpx
import pytest
from pydantic import SecretStr

from agent_ready_merchant.integrations.razorpay.client import RazorpayClient
from agent_ready_merchant.integrations.razorpay.exceptions import (
    RazorpayAPIError,
    RazorpayAuthenticationError,
    RazorpayNetworkError,
    RazorpayTimeoutError,
)


@pytest.mark.asyncio
async def test_client_create_order_success() -> None:
    """Verifies create_order sends basic auth and parses response correctly."""

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/orders"
        assert request.headers["authorization"].startswith("Basic ")
        return httpx.Response(
            status_code=200,
            json={
                "id": "order_test_12345",
                "entity": "order",
                "amount": 500000,
                "amount_paid": 0,
                "amount_due": 500000,
                "currency": "INR",
                "receipt": "ord_rec_01",
                "status": "created",
                "attempts": 0,
                "created_at": 1740000000,
            },
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = RazorpayClient(
            key_id="rzp_test_key",
            key_secret=SecretStr("rzp_secret_val"),
            http_client=http_client,
        )
        res = await client.create_order(
            amount_paise=500000,
            currency="INR",
            receipt="ord_rec_01",
        )
        assert res.id == "order_test_12345"
        assert res.amount == 500000
        assert res.status == "created"


@pytest.mark.asyncio
async def test_client_authentication_failure_401() -> None:
    """Verifies that HTTP 401 raises RazorpayAuthenticationError."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=401, json={"error": {"code": "BAD_REQUEST_ERROR"}})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = RazorpayClient(
            key_id="invalid_key",
            key_secret=SecretStr("invalid_secret"),
            http_client=http_client,
        )
        with pytest.raises(RazorpayAuthenticationError):
            await client.fetch_order("order_123")


@pytest.mark.asyncio
async def test_client_api_error_mapping() -> None:
    """Verifies that non-2xx status codes raise RazorpayAPIError with error details."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=400,
            json={
                "error": {
                    "code": "BAD_REQUEST_ERROR",
                    "description": "Order amount is less than minimum allowed",
                }
            },
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = RazorpayClient(
            key_id="key",
            key_secret=SecretStr("secret"),
            http_client=http_client,
        )
        with pytest.raises(RazorpayAPIError) as exc_info:
            await client.create_order(amount_paise=10)
        assert exc_info.value.status_code == 400
        assert exc_info.value.error_code == "BAD_REQUEST_ERROR"
        assert "less than minimum" in str(exc_info.value)


@pytest.mark.asyncio
async def test_client_timeout_error() -> None:
    """Verifies that request timeout raises RazorpayTimeoutError."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("Request timed out")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = RazorpayClient(
            key_id="key",
            key_secret=SecretStr("secret"),
            http_client=http_client,
        )
        with pytest.raises(RazorpayTimeoutError):
            await client.fetch_payment("pay_123")


@pytest.mark.asyncio
async def test_client_network_error() -> None:
    """Verifies that network connection error raises RazorpayNetworkError."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.NetworkError("Failed to resolve host")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = RazorpayClient(
            key_id="key",
            key_secret=SecretStr("secret"),
            http_client=http_client,
        )
        with pytest.raises(RazorpayNetworkError):
            await client.fetch_payment("pay_123")
