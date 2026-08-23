"""Tests for HMAC SHA-256 cryptographic webhook signature verification."""

import hashlib
import hmac

import pytest

from agent_ready_merchant.integrations.razorpay.exceptions import InvalidWebhookSignatureError
from agent_ready_merchant.integrations.razorpay.webhook import (
    assert_valid_webhook_signature,
    verify_razorpay_webhook_signature,
)


def _compute_signature(body: bytes, secret: str) -> str:
    return hmac.new(key=secret.encode("utf-8"), msg=body, digestmod=hashlib.sha256).hexdigest()


def test_valid_webhook_signature() -> None:
    """Verifies that a correctly signed raw payload passes verification."""
    secret = "rzp_secret_webhook_12345"
    raw_body = b'{"event":"order.paid","payload":{"order":{"entity":{"id":"order_123"}}}}'
    signature = _compute_signature(raw_body, secret)

    assert verify_razorpay_webhook_signature(raw_body, signature, secret) is True
    # Should not raise
    assert_valid_webhook_signature(raw_body, signature, secret)


def test_tampered_webhook_body_rejected() -> None:
    """Verifies that tampering with raw body bytes fails verification."""
    secret = "rzp_secret_webhook_12345"
    raw_body = b'{"event":"order.paid","amount":50000}'
    signature = _compute_signature(raw_body, secret)

    tampered_body = b'{"event":"order.paid","amount":10000}'  # Modified amount!
    assert verify_razorpay_webhook_signature(tampered_body, signature, secret) is False

    with pytest.raises(InvalidWebhookSignatureError):
        assert_valid_webhook_signature(tampered_body, signature, secret)


def test_wrong_webhook_secret_rejected() -> None:
    """Verifies that signature generated with another secret fails verification."""
    secret_real = "rzp_secret_real"
    secret_attacker = "rzp_secret_attacker"
    raw_body = b'{"event":"payment.captured"}'
    forged_signature = _compute_signature(raw_body, secret_attacker)

    assert verify_razorpay_webhook_signature(raw_body, forged_signature, secret_real) is False

    with pytest.raises(InvalidWebhookSignatureError):
        assert_valid_webhook_signature(raw_body, forged_signature, secret_real)


def test_missing_or_empty_signature_rejected() -> None:
    """Verifies that empty, None, or blank signature headers fail verification."""
    secret = "rzp_secret_123"
    raw_body = b'{"event":"test"}'

    assert verify_razorpay_webhook_signature(raw_body, None, secret) is False
    assert verify_razorpay_webhook_signature(raw_body, "", secret) is False
    assert verify_razorpay_webhook_signature(b"", "sig", secret) is False
    assert verify_razorpay_webhook_signature(raw_body, "sig", "") is False

    with pytest.raises(InvalidWebhookSignatureError):
        assert_valid_webhook_signature(raw_body, None, secret)
