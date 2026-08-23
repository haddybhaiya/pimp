"""Cryptographic HMAC SHA-256 webhook signature verification.

Adheres strictly to docs/razorpay-integration-notes.md §3 and zero-client-trust.
"""

import hashlib
import hmac

from agent_ready_merchant.integrations.razorpay.exceptions import InvalidWebhookSignatureError


def verify_razorpay_webhook_signature(
    raw_body: bytes,
    signature_header: str | None,
    webhook_secret: str,
) -> bool:
    """Verifies HMAC SHA-256 signature against the unparsed raw request body bytes.

    Uses constant-time comparison (hmac.compare_digest) to prevent timing attacks.
    """
    if not signature_header or not webhook_secret or not raw_body:
        return False

    expected_signature = hmac.new(
        key=webhook_secret.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature_header.strip())


def assert_valid_webhook_signature(
    raw_body: bytes,
    signature_header: str | None,
    webhook_secret: str,
) -> None:
    """Validates signature and raises InvalidWebhookSignatureError on mismatch."""
    if not verify_razorpay_webhook_signature(raw_body, signature_header, webhook_secret):
        raise InvalidWebhookSignatureError(
            "Invalid or missing Razorpay webhook signature header (X-Razorpay-Signature)"
        )
