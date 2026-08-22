"""Tests for configuration security and secret masking."""

from pydantic import SecretStr

from agent_ready_merchant.config import Settings


def test_settings_secret_masking() -> None:
    """Verifies that sensitive credentials use SecretStr and are masked."""
    settings = Settings(
        SECRET_KEY=SecretStr("super-sensitive-jwt-key"),
        RAZORPAY_KEY_SECRET=SecretStr("rzp_secret_xyz123"),
        RAZORPAY_WEBHOOK_SECRET=SecretStr("webhook_secret_abc"),
        GEMINI_API_KEY=SecretStr("gemini_key_live_999"),
    )

    # String representations must NEVER expose plaintext secrets (INV-AGY-03)
    str_repr = str(settings)
    repr_repr = repr(settings)

    assert "super-sensitive-jwt-key" not in str_repr
    assert "rzp_secret_xyz123" not in str_repr
    assert "webhook_secret_abc" not in str_repr
    assert "gemini_key_live_999" not in str_repr

    assert "super-sensitive-jwt-key" not in repr_repr
    assert "rzp_secret_xyz123" not in repr_repr
    assert "webhook_secret_abc" not in repr_repr
    assert "gemini_key_live_999" not in repr_repr

    # Values must be retrievable only via get_secret_value()
    assert settings.SECRET_KEY.get_secret_value() == "super-sensitive-jwt-key"
    assert settings.RAZORPAY_KEY_SECRET.get_secret_value() == "rzp_secret_xyz123"
    assert settings.RAZORPAY_WEBHOOK_SECRET.get_secret_value() == "webhook_secret_abc"
    assert settings.GEMINI_API_KEY.get_secret_value() == "gemini_key_live_999"


def test_settings_monetary_defaults_are_integer_paise() -> None:
    """Verifies that all monetary configuration limits are integers representing paise."""
    settings = Settings()
    assert isinstance(settings.MAX_SINGLE_TRANSACTION_PAISE, int)
    assert settings.MAX_SINGLE_TRANSACTION_PAISE > 0
    assert settings.MAX_SINGLE_TRANSACTION_PAISE == 10_000_000  # ₹100,000 in paise
