"""Tests for domain Pydantic schemas and monetary validations."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from agent_ready_merchant.config import get_settings
from agent_ready_merchant.schemas.merchant import MerchantCreate
from agent_ready_merchant.schemas.order import OrderCreate, OrderItemCreate
from agent_ready_merchant.schemas.product import ProductCreate
from agent_ready_merchant.schemas.quote import PriceQuoteCreate, QuoteItemCreate


def test_merchant_create_valid() -> None:
    """Verifies valid merchant creation schema."""
    settings = get_settings()
    merchant = MerchantCreate(
        name="Test Merchant",
        slug="test-merchant",
        status="ACTIVE",
        currency="INR",
        rzp_key_id=settings.RAZORPAY_KEY_ID,
    )
    assert merchant.name == "Test Merchant"
    assert merchant.slug == "test-merchant"


def test_merchant_create_invalid_slug() -> None:
    """Verifies that invalid slug characters raise validation error."""
    settings = get_settings()
    with pytest.raises(ValidationError):
        MerchantCreate(
            name="Test",
            slug="Invalid Slug With Spaces!",
            rzp_key_id=settings.RAZORPAY_KEY_ID,
        )


def test_product_create_floor_lte_base_price() -> None:
    """Verifies that floor_price_paise cannot exceed base_price_paise."""
    # Valid product where floor <= base
    product = ProductCreate(
        merchant_id=uuid.uuid4(),
        sku="SKU-SHOE-01",
        title="Running Shoes",
        category="Footwear",
        base_price_paise=500000,  # ₹5,000
        floor_price_paise=450000,  # ₹4,500
        is_negotiable=True,
    )
    assert product.base_price_paise == 500000
    assert product.floor_price_paise == 450000

    # Invalid product where floor > base
    with pytest.raises(ValidationError) as exc_info:
        ProductCreate(
            merchant_id=uuid.uuid4(),
            sku="SKU-SHOE-02",
            title="Running Shoes",
            category="Footwear",
            base_price_paise=400000,  # ₹4,000
            floor_price_paise=450000,  # ₹4,500 (higher than base!)
            is_negotiable=True,
        )
    assert "floor_price_paise" in str(exc_info.value)


def test_product_create_rejects_negative_or_zero_price() -> None:
    """Verifies that non-positive monetary prices are rejected."""
    with pytest.raises(ValidationError):
        ProductCreate(
            merchant_id=uuid.uuid4(),
            sku="SKU-SHOE-03",
            title="Free Shoes",
            category="Footwear",
            base_price_paise=0,  # Zero base price not allowed
            floor_price_paise=0,
        )

    with pytest.raises(ValidationError):
        ProductCreate(
            merchant_id=uuid.uuid4(),
            sku="SKU-SHOE-04",
            title="Negative Price Shoes",
            category="Footwear",
            base_price_paise=-500000,  # Negative price not allowed
            floor_price_paise=-600000,
        )


def test_quote_total_arithmetic_validation() -> None:
    """Verifies that PriceQuote enforces total = subtotal - discount + shipping."""
    variant_id = uuid.uuid4()
    now = datetime.now(UTC)

    # Valid arithmetic: 500000 - 50000 + 10000 = 460000
    valid_quote = PriceQuoteCreate(
        session_id=uuid.uuid4(),
        merchant_id=uuid.uuid4(),
        status="PROPOSED",
        subtotal_paise=500000,
        discount_paise=50000,
        shipping_paise=10000,
        total_paise=460000,
        expires_at=now + timedelta(minutes=15),
        idempotency_key="quote_key_123",
        items=[
            QuoteItemCreate(
                variant_id=variant_id,
                quantity=1,
                unit_price_paise=500000,
            )
        ],
    )
    assert valid_quote.total_paise == 460000

    # Invalid arithmetic: declared total does not match formula
    with pytest.raises(ValidationError) as exc_info:
        PriceQuoteCreate(
            session_id=uuid.uuid4(),
            merchant_id=uuid.uuid4(),
            status="PROPOSED",
            subtotal_paise=500000,
            discount_paise=50000,
            shipping_paise=10000,
            total_paise=999999,  # Wrong total!
            expires_at=now + timedelta(minutes=15),
            idempotency_key="quote_key_124",
            items=[
                QuoteItemCreate(
                    variant_id=variant_id,
                    quantity=1,
                    unit_price_paise=500000,
                )
            ],
        )
    assert "total_paise" in str(exc_info.value)


def test_order_create_requires_valid_email() -> None:
    """Verifies that Order creation requires a valid email format."""
    variant_id = uuid.uuid4()
    with pytest.raises(ValidationError):
        OrderCreate(
            quote_id=uuid.uuid4(),
            merchant_id=uuid.uuid4(),
            amount_paise=460000,
            currency="INR",
            buyer_email="not-an-email",  # Invalid email format
            items=[
                OrderItemCreate(
                    variant_id=variant_id,
                    quantity=1,
                    unit_price_paise=460000,
                )
            ],
        )
