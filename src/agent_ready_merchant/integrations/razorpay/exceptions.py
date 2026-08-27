"""Exception hierarchy for Razorpay integration."""


class RazorpayError(Exception):
    """Base exception for all Razorpay client errors."""

    @property
    def is_retryable(self) -> bool:
        return False


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

    @property
    def is_client_error(self) -> bool:
        return 400 <= self.status_code < 500

    @property
    def is_server_error(self) -> bool:
        return self.status_code >= 500

    @property
    def is_retryable(self) -> bool:
        return self.status_code in {429, 500, 502, 503, 504}


class RazorpayBadRequestError(RazorpayAPIError):
    """Raised when Razorpay returns HTTP 400 Bad Request."""

    pass


class RazorpayNotFoundError(RazorpayAPIError):
    """Raised when Razorpay returns HTTP 404 Not Found."""

    pass


class RazorpayRateLimitError(RazorpayAPIError):
    """Raised when Razorpay returns HTTP 429 Too Many Requests."""

    @property
    def is_retryable(self) -> bool:
        return True


class RazorpayServerError(RazorpayAPIError):
    """Raised when Razorpay returns HTTP 5xx Server Error."""

    @property
    def is_retryable(self) -> bool:
        return True


class RazorpayNetworkError(RazorpayError):
    """Raised on connection error or network partition."""

    @property
    def is_retryable(self) -> bool:
        return True


class RazorpayTimeoutError(RazorpayError):
    """Raised when Razorpay API request times out."""

    @property
    def is_retryable(self) -> bool:
        return True


class InvalidWebhookSignatureError(RazorpayError):
    """Raised when webhook signature verification fails."""

    pass


class WebhookReplayError(RazorpayError):
    """Raised when a replayed webhook is detected outside acceptable replay windows."""

    pass


class WebhookTimestampError(RazorpayError):
    """Raised when a webhook timestamp is expired or outside valid bounds."""

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


class CurrencyMismatchFraudError(RazorpayError):
    """Raised when verified payment currency differs from order currency."""

    def __init__(self, expected_currency: str, received_currency: str) -> None:
        self.expected_currency = expected_currency
        self.received_currency = received_currency
        super().__init__(
            f"Currency mismatch detected: expected {expected_currency}, "
            f"received {received_currency}"
        )


class OrderMismatchError(RazorpayError):
    """Raised when a payment attempt is bound to a different or invalid order."""

    def __init__(self, expected_order_id: str | None, received_order_id: str | None) -> None:
        self.expected_order_id = expected_order_id
        self.received_order_id = received_order_id
        super().__init__(
            f"Order mismatch detected: expected {expected_order_id}, received {received_order_id}"
        )


class TransactionBindingError(RazorpayError):
    """Raised when a transaction record violates entity binding invariants."""

    pass
