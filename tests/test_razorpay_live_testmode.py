"""Live test-mode integration tests executing against Razorpay sandbox endpoints."""

from datetime import UTC, datetime

import pytest

from agent_ready_merchant.config import get_settings
from agent_ready_merchant.integrations.razorpay.client import RazorpayClient


@pytest.mark.asyncio
async def test_live_razorpay_testmode_order_roundtrip() -> None:
    """Verifies real HTTP interaction with Razorpay Test Mode sandbox endpoints."""
    settings = get_settings()
    key_id = settings.RAZORPAY_KEY_ID
    key_secret = settings.RAZORPAY_KEY_SECRET.get_secret_value()

    # Skip if placeholder or empty
    if not key_id.startswith("rzp_test_") or not key_secret:
        pytest.skip(
            "No real Razorpay test-mode credentials configured; skipping live sandbox call."
        )

    client = RazorpayClient(
        key_id=key_id,
        key_secret=settings.RAZORPAY_KEY_SECRET,
        base_url=settings.RAZORPAY_API_BASE_URL,
    )

    # 1. Create a test order for ₹500 (50,000 paise)
    now = datetime.now(UTC)
    receipt_id = f"test_live_{int(now.timestamp())}"[:40]
    order_res = await client.create_order(
        amount_paise=50000,
        currency="INR",
        receipt=receipt_id,
        payment_capture=1,
        notes={"test_suite": "pytest", "env": "sandbox"},
    )

    assert order_res.id.startswith("order_")
    assert order_res.amount == 50000
    assert order_res.currency == "INR"
    assert order_res.status == "created"

    # 2. Fetch order back from Razorpay
    fetched_order = await client.fetch_order(order_res.id)
    assert fetched_order.id == order_res.id
    assert fetched_order.amount == 50000
    assert fetched_order.status == "created"

    # 3. Fetch order payments (should be empty collection for new order)
    payments = await client.fetch_order_payments(order_res.id)
    assert isinstance(payments, list)
    assert len(payments) == 0
