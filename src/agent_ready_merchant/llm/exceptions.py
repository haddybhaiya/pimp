"""Exception hierarchy for LLM providers."""


class LLMError(Exception):
    """Base exception for all LLM errors."""

    pass


class LLMAuthenticationError(LLMError):
    """Raised when LLM API credentials are invalid (HTTP 401)."""

    pass


class LLMTimeoutError(LLMError):
    """Raised when LLM provider times out."""

    pass


class LLMProviderError(LLMError):
    """Raised when LLM provider returns a non-2xx error or unexpected payload."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"LLM provider error ({status_code}): {message}")
