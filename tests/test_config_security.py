import pytest
from pydantic import SecretStr, ValidationError

from agent_ready_merchant.config import Settings


def test_settings_secret_masking() -> None:
    """Verifies that sensitive credentials use SecretStr and are masked."""
    settings = Settings(
        SECRET_KEY=SecretStr("super-sensitive-jwt-key"),
        DATABASE_URL=SecretStr("postgresql+asyncpg://user:pass@localhost:5432/db"),
        DATABASE_URL_SYNC=SecretStr("postgresql://user:pass@localhost:5432/db"),
        RAZORPAY_KEY_SECRET=SecretStr("rzp_secret_xyz123"),
        RAZORPAY_WEBHOOK_SECRET=SecretStr("webhook_secret_abc"),
        GROQ_API_KEY=SecretStr("gsk_key_live_999"),
    )

    # String representations must NEVER expose plaintext secrets (INV-AGY-03)
    str_repr = str(settings)
    repr_repr = repr(settings)

    assert "super-sensitive-jwt-key" not in str_repr
    assert "user:pass" not in str_repr
    assert "rzp_secret_xyz123" not in str_repr
    assert "webhook_secret_abc" not in str_repr
    assert "gsk_key_live_999" not in str_repr

    assert "super-sensitive-jwt-key" not in repr_repr
    assert "user:pass" not in repr_repr
    assert "rzp_secret_xyz123" not in repr_repr
    assert "webhook_secret_abc" not in repr_repr
    assert "gsk_key_live_999" not in repr_repr

    # Values must be retrievable only via get_secret_value()
    assert settings.SECRET_KEY.get_secret_value() == "super-sensitive-jwt-key"
    assert (
        settings.DATABASE_URL.get_secret_value()
        == "postgresql+asyncpg://user:pass@localhost:5432/db"
    )
    assert settings.RAZORPAY_KEY_SECRET.get_secret_value() == "rzp_secret_xyz123"
    assert settings.RAZORPAY_WEBHOOK_SECRET.get_secret_value() == "webhook_secret_abc"
    assert settings.GROQ_API_KEY.get_secret_value() == "gsk_key_live_999"


def test_settings_production_fails_closed_when_default_secret_key() -> None:
    """Verifies that production environment fails closed when SECRET_KEY is default."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY=SecretStr("default-insecure-secret-key-change-in-production"),
        )
    assert "SECRET_KEY must be configured" in str(exc_info.value)


def test_settings_production_fails_closed_when_empty_secret_key() -> None:
    """Verifies that production environment fails closed when SECRET_KEY is empty."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY=SecretStr(""),
        )
    assert "SECRET_KEY must be configured" in str(exc_info.value)


def test_settings_production_fails_closed_when_whitespace_secret_key() -> None:
    """Verifies that production environment fails closed when SECRET_KEY is whitespace only."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY=SecretStr("   "),
        )
    assert "SECRET_KEY must be configured" in str(exc_info.value)


def test_settings_production_fails_closed_when_insecure_known_secret() -> None:
    """Verifies that production fails closed on common insecure placeholders like 'changeme'."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY=SecretStr("changeme"),
        )
    assert "SECRET_KEY must be configured" in str(exc_info.value)


def test_settings_production_succeeds_with_valid_secure_secret() -> None:
    """Verifies that production succeeds when a valid, non-default SECRET_KEY is provided."""
    settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY=SecretStr("production-secure-entropy-key-9876543210"),
    )
    assert settings.ENVIRONMENT == "production"
    assert settings.SECRET_KEY.get_secret_value() == "production-secure-entropy-key-9876543210"


def test_settings_development_and_test_allow_default_secret() -> None:
    """Verifies development and test environments allow default SECRET_KEY without error."""
    dev_settings = Settings(
        ENVIRONMENT="development",
        SECRET_KEY=SecretStr("default-insecure-secret-key-change-in-production"),
    )
    assert dev_settings.ENVIRONMENT == "development"

    test_settings = Settings(
        ENVIRONMENT="test",
        SECRET_KEY=SecretStr("default-insecure-secret-key-change-in-production"),
    )
    assert test_settings.ENVIRONMENT == "test"


def test_settings_monetary_defaults_are_integer_paise() -> None:
    """Verifies that all monetary configuration limits are integers representing paise."""
    settings = Settings()
    assert isinstance(settings.MAX_SINGLE_TRANSACTION_PAISE, int)
    assert settings.MAX_SINGLE_TRANSACTION_PAISE > 0
    assert settings.MAX_SINGLE_TRANSACTION_PAISE == 5_000_000  # ₹50,000 in paise (policy-model.md)
