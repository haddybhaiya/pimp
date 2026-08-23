"""Application configuration and environment settings management.

Adheres strictly to INV-AGY-03 (Zero Secret Leakage):
Sensitive credentials (API keys, webhook secrets, database passwords) use SecretStr
and are never exposed via logging, serialization, or error responses.
"""

from functools import lru_cache
from typing import ClassVar, Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application configuration loaded from environment and .env file."""

    KNOWN_INSECURE_SECRETS: ClassVar[tuple[str, ...]] = (
        "default-insecure-secret-key-change-in-production",
        "secret",
        "changeme",
        "password",
        "admin",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --------------------------------------------------------------------------
    # 1. Application & Server Settings
    # --------------------------------------------------------------------------
    ENVIRONMENT: Literal["development", "test", "staging", "production"] = "development"
    DEBUG: bool = False
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    SECRET_KEY: SecretStr = Field(
        default=SecretStr("default-insecure-secret-key-change-in-production"),
        description="Application secret key used for session/JWT signing",
    )

    # --------------------------------------------------------------------------
    # 2. Database Configuration (PostgreSQL 16+ / SQLite for isolated tests)
    # --------------------------------------------------------------------------
    DATABASE_URL: SecretStr = Field(
        default=SecretStr(
            "postgresql+asyncpg://postgres:postgres@localhost:5432/agent_ready_merchant"
        ),
        description="Async database connection string",
    )
    DATABASE_URL_SYNC: SecretStr = Field(
        default=SecretStr("postgresql://postgres:postgres@localhost:5432/agent_ready_merchant"),
        description="Synchronous database connection string for migrations",
    )
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # --------------------------------------------------------------------------
    # 3. Razorpay Test-Mode Credentials (Stored safely as SecretStr)
    # --------------------------------------------------------------------------
    RAZORPAY_KEY_ID: str = Field(
        default="rzp_test_placeholder",
        description="Razorpay public test key ID",
    )
    RAZORPAY_KEY_SECRET: SecretStr = Field(
        default=SecretStr(""),
        description="Razorpay private test key secret",
    )
    RAZORPAY_WEBHOOK_SECRET: SecretStr = Field(
        default=SecretStr(""),
        description="Razorpay webhook HMAC SHA-256 secret",
    )
    RAZORPAY_API_BASE_URL: str = "https://api.razorpay.com/v1"

    # --------------------------------------------------------------------------
    # 4. LLM Provider Credentials (Stored safely as SecretStr)
    # --------------------------------------------------------------------------
    GROQ_API_KEY: SecretStr = Field(
        default=SecretStr(""),
        description="Groq API key for model inference",
    )
    LLM_MODEL_NAME: str = "llama-3.3-70b-versatile"
    LLM_MAX_OUTPUT_TOKENS: int = 2048
    LLM_TEMPERATURE: float = 0.2
    LLM_STEP_LIMIT: int = 5
    LLM_TIMEOUT_SECONDS: int = 15

    # --------------------------------------------------------------------------
    # 5. Merchant Default Financial Policies (All monetary values in integer paise)
    # --------------------------------------------------------------------------
    DEFAULT_MERCHANT_AUTONOMY_LEVEL: int = 1  # 0: Read-Only, 1: Bounded Auto, 2: HITL
    DEFAULT_MAX_DISCOUNT_PERCENTAGE: float = 15.0
    DEFAULT_MIN_MARGIN_PERCENTAGE: float = 20.0
    DEFAULT_QUOTE_TTL_MINUTES: int = 15
    MAX_SINGLE_TRANSACTION_PAISE: int = 5_000_000  # ₹50,000 in paise (docs/policy-model.md §2.2)

    # --------------------------------------------------------------------------
    # 6. Rate Limiting & Security Guards
    # --------------------------------------------------------------------------
    SESSION_RATE_LIMIT_PER_MINUTE: int = 20
    MAX_ACTIVE_QUOTES_PER_BUYER: int = 3
    LOG_LEVEL: str = "INFO"

    @property
    def is_testing(self) -> bool:
        """Helper to check if currently executing in test environment."""
        return self.ENVIRONMENT == "test"

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        """Rejects known default, empty, or whitespace SECRET_KEY in production to fail closed."""
        if self.ENVIRONMENT == "production":
            val = self.SECRET_KEY.get_secret_value().strip()
            if not val or val in self.KNOWN_INSECURE_SECRETS:
                raise ValueError("SECRET_KEY must be configured with a secure value in production")
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached singleton provider for application settings."""
    return Settings()
