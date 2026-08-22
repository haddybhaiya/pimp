"""Exception hierarchy for Razorpay integration."""


class RazorpayError(Exception):
    """Base exception for all Razorpay client errors."""

    pass


class RazorpayAuthenticationError(RazorpayError):
    """Raised when Razorpay rejects credentials (HTTP 401)."""

    pass


class RazorpayAPIError(RazorpayError):
    """Raised when Razorpay returns a non-2xx response."""

    def __init__(self, status_code: int, error_code: str | None, description: str | None) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.description = description
        super().__init__(
            f"Razorpay API error ({status_code}) [{error_code or 'UNKNOWN'}]: "
            f"{description or 'No details provided'}"
        )


class RazorpayNetworkError(RazorpayError):
    """Raised on connection error or network partition."""

    pass


class RazorpayTimeoutError(RazorpayError):
    """Raised when Razorpay API request times out."""

    pass


class InvalidWebhookSignatureError(RazorpayError):
    """Raised when webhook signature verification fails."""

    pass


class AmountMismatchFraudError(RazorpayError):
    """Raised when verified payment amount differs from order amount."""

    def __init__(self, expected_amount_paise: int, received_amount_paise: int) -> None:
        self.expected_amount_paise = expected_amount_paise
        self.received_amount_paise = received_amount_paise
        super().__init__(
            f"Amount mismatch detected: expected {expected_amount_paise} paise, "
            f"received {received_amount_paise} paise"
        )
