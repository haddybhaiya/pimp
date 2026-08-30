"""Merchant Authentication and Setup Domain Service for Phase 5.1."""

from __future__ import annotations

import hashlib
import hmac
import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.config import Settings, get_settings
from agent_ready_merchant.gateway.constants import COMMERCE_PROTOCOL_VERSION
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.policy import PolicyRule
from agent_ready_merchant.policy.models import compute_policy_hash
from agent_ready_merchant.schemas.merchant_auth import (
    MerchantAuthResponse,
    MerchantLoginRequest,
    MerchantProfileResponse,
    MerchantSetupRequest,
    MerchantSignupRequest,
    PolicySummaryItem,
)

logger = logging.getLogger("agent_ready_merchant.auth")


class MerchantAuthService:
    """Authoritative service for merchant authentication, token generation, and setup."""

    @staticmethod
    def _generate_admin_token(merchant: Merchant, expires_at: datetime, secret: str) -> str:
        """Generates a tamper-evident admin token for the authenticated merchant."""
        payload = f"admin:{merchant.id}:{merchant.slug}:{int(expires_at.timestamp())}"
        sig = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
        return f"{payload}:{sig}"

    @classmethod
    def generate_admin_token(
        cls,
        merchant_id: uuid.UUID,
        secret: str,
        slug: str = "default-slug",
        expires_in_hours: int = 24,
    ) -> str:
        """Generates a signed admin session bearer token for a merchant ID."""
        expires_at = datetime.now(UTC) + timedelta(hours=expires_in_hours)
        payload = f"admin:{merchant_id}:{slug}:{int(expires_at.timestamp())}"
        sig = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
        return f"{payload}:{sig}"

    @classmethod
    def verify_admin_token(
        cls, token: str, secret: str
    ) -> tuple[bool, uuid.UUID | None, str | None]:
        """Verifies admin token authenticity and expiration.

        Returns (is_valid, merchant_id, error_message).
        """
        try:
            parts = token.split(":")
            if len(parts) != 5 or parts[0] != "admin":
                return False, None, "Malformed token structure"

            merchant_id_str = parts[1]
            slug = parts[2]
            ts_str = parts[3]
            presented_sig = parts[4]

            expected_payload = f"admin:{merchant_id_str}:{slug}:{ts_str}"
            expected_sig = hmac.new(
                secret.encode("utf-8"), expected_payload.encode("utf-8"), hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(presented_sig, expected_sig):
                return False, None, "Invalid cryptographic token signature"

            expires_ts = int(ts_str)
            now_ts = int(datetime.now(UTC).timestamp())
            if now_ts > expires_ts:
                return False, None, "Admin session token has expired"

            return True, uuid.UUID(merchant_id_str), None
        except Exception as exc:
            return False, None, f"Token verification error: {str(exc)}"

    @classmethod
    async def _build_policy_summary(
        cls, session: AsyncSession, merchant_id: uuid.UUID
    ) -> PolicySummaryItem:
        """Loads active policy rules and computes deterministic policy hash."""
        rules_stmt = select(PolicyRule).where(
            PolicyRule.merchant_id == merchant_id,
            PolicyRule.is_active == True,  # noqa: E712
        )
        rules = list((await session.execute(rules_stmt)).scalars().all())

        autonomy_level = 1
        max_discount_pct = 15.0
        min_margin_pct = 20.0
        max_single_tx_paise = 5_000_000

        for r in rules:
            val = r.rule_value or {}
            if r.rule_type == "AUTONOMY_LEVEL" and "autonomy_level" in val:
                autonomy_level = int(val["autonomy_level"])
            elif r.rule_type == "MAX_DISCOUNT_PCT" and "max_discount_pct" in val:
                max_discount_pct = float(val["max_discount_pct"])
            elif r.rule_type == "MIN_MARGIN_PCT" and "min_margin_pct" in val:
                min_margin_pct = float(val["min_margin_pct"])
            elif r.rule_type == "MAX_CART_VALUE" and "max_single_tx_paise" in val:
                max_single_tx_paise = int(val["max_single_tx_paise"])

        p_hash = compute_policy_hash(
            autonomy_level=autonomy_level,
            max_discount_percentage=max_discount_pct,
            min_margin_percentage=min_margin_pct,
            max_single_transaction_paise=max_single_tx_paise,
            version=COMMERCE_PROTOCOL_VERSION,
        )

        return PolicySummaryItem(
            autonomy_level=autonomy_level,
            max_discount_percentage=max_discount_pct,
            min_margin_percentage=min_margin_pct,
            max_single_transaction_paise=max_single_tx_paise,
            policy_hash=p_hash,
            protocol_version=COMMERCE_PROTOCOL_VERSION,
        )

    @classmethod
    async def register_merchant(
        cls,
        session: AsyncSession,
        request: MerchantSignupRequest,
        settings: Settings | None = None,
    ) -> MerchantAuthResponse:
        """Registers a new merchant, seeds initial policy rules, and issues admin session."""
        effective_settings = settings or get_settings()

        # 1. Unique slug validation
        existing_stmt = select(Merchant).where(Merchant.slug == request.slug)
        existing = (await session.execute(existing_stmt)).scalar_one_or_none()
        if existing:
            raise ValueError(f"Merchant with slug '{request.slug}' already exists.")

        # 2. Persist Merchant entity
        merchant = Merchant(
            name=request.name,
            slug=request.slug,
            status="ACTIVE",
            currency=request.currency,
            rzp_key_id=request.rzp_key_id,
        )
        session.add(merchant)
        await session.flush()

        # 3. Seed default PolicyRules
        default_rules = [
            PolicyRule(
                merchant_id=merchant.id,
                rule_type="AUTONOMY_LEVEL",
                target_scope="GLOBAL",
                rule_value={"autonomy_level": request.initial_autonomy_level},
                is_active=True,
            ),
            PolicyRule(
                merchant_id=merchant.id,
                rule_type="MAX_DISCOUNT_PCT",
                target_scope="GLOBAL",
                rule_value={"max_discount_pct": request.max_discount_percentage},
                is_active=True,
            ),
            PolicyRule(
                merchant_id=merchant.id,
                rule_type="MIN_MARGIN_PCT",
                target_scope="GLOBAL",
                rule_value={"min_margin_pct": request.min_margin_percentage},
                is_active=True,
            ),
            PolicyRule(
                merchant_id=merchant.id,
                rule_type="MAX_CART_VALUE",
                target_scope="GLOBAL",
                rule_value={"max_single_tx_paise": request.max_single_transaction_paise},
                is_active=True,
            ),
        ]
        session.add_all(default_rules)
        await session.flush()

        # 4. Generate Auth token & expiry
        expires_at = datetime.now(UTC) + timedelta(hours=24)
        secret = effective_settings.RAZORPAY_WEBHOOK_SECRET.get_secret_value()
        token = cls._generate_admin_token(merchant, expires_at, secret)

        # 5. Build policy summary
        policies = await cls._build_policy_summary(session, merchant.id)

        # 6. Audit event
        await AuditEvent.create_event(
            session=session,
            merchant_id=merchant.id,
            actor_type="MERCHANT_ADMIN",
            event_type="MERCHANT_REGISTERED",
            payload={
                "merchant_id": str(merchant.id),
                "name": merchant.name,
                "slug": merchant.slug,
                "currency": merchant.currency,
                "email": request.email,
                "initial_autonomy_level": request.initial_autonomy_level,
                "policy_hash": policies.policy_hash,
            },
        )

        return MerchantAuthResponse(
            merchant_id=merchant.id,
            name=merchant.name,
            slug=merchant.slug,
            status=merchant.status,
            currency=merchant.currency,
            token=token,
            expires_at=expires_at,
            onboarding_completed=True,
            policies=policies,
        )

    @classmethod
    async def authenticate_merchant(
        cls,
        session: AsyncSession,
        request: MerchantLoginRequest,
        settings: Settings | None = None,
    ) -> MerchantAuthResponse:
        """Authenticates merchant by slug or token and issues active bearer session."""
        effective_settings = settings or get_settings()
        secret = effective_settings.RAZORPAY_WEBHOOK_SECRET.get_secret_value()

        # 1. Look up merchant by slug
        stmt = select(Merchant).where(Merchant.slug == request.slug)
        merchant = (await session.execute(stmt)).scalar_one_or_none()
        if not merchant:
            raise ValueError(f"Merchant with slug '{request.slug}' not found.")

        if merchant.status != "ACTIVE":
            raise ValueError(f"Merchant account is {merchant.status}. Access denied.")

        # 2. If admin_token is provided, verify it
        if request.admin_token:
            is_valid, tok_merchant_id, err = cls.verify_admin_token(request.admin_token, secret)
            if not is_valid or tok_merchant_id != merchant.id:
                raise ValueError(err or "Invalid or mismatched admin session token.")

        # 3. Generate fresh token
        expires_at = datetime.now(UTC) + timedelta(hours=24)
        token = cls._generate_admin_token(merchant, expires_at, secret)

        # 4. Build policy summary
        policies = await cls._build_policy_summary(session, merchant.id)

        # 5. Audit event
        await AuditEvent.create_event(
            session=session,
            merchant_id=merchant.id,
            actor_type="MERCHANT_ADMIN",
            event_type="MERCHANT_LOGIN",
            payload={
                "merchant_id": str(merchant.id),
                "slug": merchant.slug,
                "status": merchant.status,
                "policy_hash": policies.policy_hash,
            },
        )

        return MerchantAuthResponse(
            merchant_id=merchant.id,
            name=merchant.name,
            slug=merchant.slug,
            status=merchant.status,
            currency=merchant.currency,
            token=token,
            expires_at=expires_at,
            onboarding_completed=True,
            policies=policies,
        )

    @classmethod
    async def get_merchant_profile(
        cls,
        session: AsyncSession,
        merchant_id: uuid.UUID,
    ) -> MerchantProfileResponse:
        """Fetches detailed merchant profile and policy configuration."""
        stmt = select(Merchant).where(Merchant.id == merchant_id)
        merchant = (await session.execute(stmt)).scalar_one_or_none()
        if not merchant:
            raise ValueError(f"Merchant with ID '{merchant_id}' not found.")

        policies = await cls._build_policy_summary(session, merchant.id)

        return MerchantProfileResponse(
            merchant_id=merchant.id,
            name=merchant.name,
            slug=merchant.slug,
            status=merchant.status,
            currency=merchant.currency,
            rzp_key_id=merchant.rzp_key_id,
            onboarding_completed=True,
            policies=policies,
            created_at=merchant.created_at or datetime.now(UTC),
        )

    @classmethod
    async def complete_merchant_setup(
        cls,
        session: AsyncSession,
        merchant_id: uuid.UUID,
        request: MerchantSetupRequest,
    ) -> MerchantProfileResponse:
        """Updates merchant profile and policy configuration upon setup wizard completion."""
        stmt = select(Merchant).where(Merchant.id == merchant_id)
        merchant = (await session.execute(stmt)).scalar_one_or_none()
        if not merchant:
            raise ValueError(f"Merchant with ID '{merchant_id}' not found.")

        if request.name:
            merchant.name = request.name
        if request.rzp_key_id:
            merchant.rzp_key_id = request.rzp_key_id

        # Update or create PolicyRules
        rules_stmt = select(PolicyRule).where(PolicyRule.merchant_id == merchant.id)
        existing_rules = {
            r.rule_type: r for r in (await session.execute(rules_stmt)).scalars().all()
        }

        type_map: dict[str, dict[str, Any]] = {
            "AUTONOMY_LEVEL": {"autonomy_level": request.autonomy_level},
            "MAX_DISCOUNT_PCT": {"max_discount_pct": request.max_discount_percentage},
            "MIN_MARGIN_PCT": {"min_margin_pct": request.min_margin_percentage},
            "MAX_CART_VALUE": {"max_single_tx_paise": request.max_single_transaction_paise},
        }

        for r_type, r_val in type_map.items():
            if r_type in existing_rules:
                existing_rules[r_type].rule_value = r_val
                existing_rules[r_type].is_active = True
            else:
                new_rule = PolicyRule(
                    merchant_id=merchant.id,
                    rule_type=r_type,
                    target_scope="GLOBAL",
                    rule_value=r_val,
                    is_active=True,
                )
                session.add(new_rule)

        await session.flush()

        policies = await cls._build_policy_summary(session, merchant.id)

        await AuditEvent.create_event(
            session=session,
            merchant_id=merchant.id,
            actor_type="MERCHANT_ADMIN",
            event_type="MERCHANT_SETUP_COMPLETED",
            payload={
                "merchant_id": str(merchant.id),
                "name": merchant.name,
                "autonomy_level": request.autonomy_level,
                "policy_hash": policies.policy_hash,
            },
        )

        return MerchantProfileResponse(
            merchant_id=merchant.id,
            name=merchant.name,
            slug=merchant.slug,
            status=merchant.status,
            currency=merchant.currency,
            rzp_key_id=merchant.rzp_key_id,
            onboarding_completed=True,
            policies=policies,
            created_at=merchant.created_at or datetime.now(UTC),
        )
