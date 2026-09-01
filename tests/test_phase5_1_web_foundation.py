"""Phase 5.1 Web Foundation & Merchant Public Surface Test Suite.

Verifies:
1. Merchant signup, store creation & automatic policy seeding.
2. Duplicate slug rejection (fail-closed).
3. Merchant login with token generation & constant-time verification.
4. Merchant profile discovery and multi-tenant isolation.
5. Setup wizard completion and atomic policy updates.
6. Forged, replayed, expired, and cross-tenant admin token rejection.
7. Cryptographic audit chain linkage on all merchant auth events.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.config import get_settings
from agent_ready_merchant.main import app
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.policy import PolicyRule
from agent_ready_merchant.schemas.merchant_auth import MerchantSetupRequest
from agent_ready_merchant.services.merchant_auth_service import MerchantAuthService


@pytest.mark.asyncio
async def test_merchant_signup_creates_store_and_seeds_policies(
    db_session: AsyncSession,
) -> None:
    """Test 1: Merchant signup creates merchant entity and seeds default policy rules."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        unique_slug = f"test-store-{uuid.uuid4().hex[:8]}"
        payload = {
            "name": "Apex Athletic Co",
            "slug": unique_slug,
            "email": "owner@apex-athletic.com",
            "rzp_key_id": "rzp_test_apex123",
            "currency": "INR",
            "initial_autonomy_level": 1,
            "max_discount_percentage": 15.0,
            "min_margin_percentage": 20.0,
            "max_single_transaction_paise": 5000000,
        }

        resp = await client.post("/api/v1/merchant/auth/signup", json=payload)
        assert resp.status_code == 201
        data = resp.json()

        assert data["name"] == "Apex Athletic Co"
        assert data["slug"] == unique_slug
        assert data["status"] == "ACTIVE"
        assert data["currency"] == "INR"
        assert data["token"] is None
        assert "httponly" in resp.headers["set-cookie"].lower()
        assert data["onboarding_completed"] is True
        assert data["policies"]["autonomy_level"] == 1
        assert data["policies"]["max_discount_percentage"] == 15.0
        assert data["policies"]["min_margin_percentage"] == 20.0
        assert len(data["policies"]["policy_hash"]) == 64

        merchant_id = uuid.UUID(data["merchant_id"])

        # Verify DB entities
        m_stmt = select(Merchant).where(Merchant.id == merchant_id)
        merchant = (await db_session.execute(m_stmt)).scalar_one()
        assert merchant.name == "Apex Athletic Co"

        # Verify seeded policy rules
        r_stmt = select(PolicyRule).where(PolicyRule.merchant_id == merchant_id)
        rules = list((await db_session.execute(r_stmt)).scalars().all())
        assert len(rules) == 4
        rule_types = {r.rule_type for r in rules}
        assert rule_types == {
            "AUTONOMY_LEVEL",
            "MAX_DISCOUNT_PCT",
            "MIN_MARGIN_PCT",
            "MAX_CART_VALUE",
        }

        # Verify audit event
        a_stmt = select(AuditEvent).where(
            AuditEvent.merchant_id == merchant_id,
            AuditEvent.event_type == "MERCHANT_REGISTERED",
        )
        audit_event = (await db_session.execute(a_stmt)).scalar_one_or_none()
        assert audit_event is not None
        assert audit_event.payload["slug"] == unique_slug


@pytest.mark.asyncio
async def test_merchant_signup_rejects_duplicate_slug(db_session: AsyncSession) -> None:
    """Test 2: Merchant signup fails closed when attempting to register an existing slug."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        unique_slug = f"dup-store-{uuid.uuid4().hex[:8]}"
        payload = {
            "name": "Original Store",
            "slug": unique_slug,
            "email": "original@store.com",
            "rzp_key_id": "rzp_test_orig",
        }

        # First signup
        resp1 = await client.post("/api/v1/merchant/auth/signup", json=payload)
        assert resp1.status_code == 201

        # Duplicate signup with same slug
        resp2 = await client.post(
            "/api/v1/merchant/auth/signup",
            json={
                "name": "Imposter Store",
                "slug": unique_slug,
                "email": "imposter@store.com",
                "rzp_key_id": "rzp_test_imposter",
            },
        )
        assert resp2.status_code == 400
        assert "already exists" in resp2.json()["detail"]


@pytest.mark.asyncio
async def test_merchant_login_with_valid_session_token_returns_refreshed_bearer_token(
    db_session: AsyncSession,
) -> None:
    """Test 3: Login refresh requires an existing, valid admin session token."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        unique_slug = f"login-store-{uuid.uuid4().hex[:8]}"
        signup_payload = {
            "name": "Login Test Store",
            "slug": unique_slug,
            "email": "login@store.com",
            "rzp_key_id": "rzp_test_login",
        }
        signup_response = await client.post("/api/v1/merchant/auth/signup", json=signup_payload)
        assert signup_response.json()["token"] is None

        # Session refresh uses the HttpOnly cookie automatically.
        login_resp = await client.post(
            "/api/v1/merchant/auth/login",
            json={"slug": unique_slug},
        )
        assert login_resp.status_code == 200
        data = login_resp.json()
        assert data["slug"] == unique_slug
        assert data["status"] == "ACTIVE"
        assert data["token"] is None
        assert "httponly" in login_resp.headers["set-cookie"].lower()


@pytest.mark.asyncio
async def test_merchant_login_rejects_slug_without_existing_session_token(
    db_session: AsyncSession,
) -> None:
    """A public merchant slug must never be sufficient to mint an admin session."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        unique_slug = f"missing-token-{uuid.uuid4().hex[:8]}"
        await client.post(
            "/api/v1/merchant/auth/signup",
            json={
                "name": "No Token Store",
                "slug": unique_slug,
                "email": "missing-token@store.com",
                "rzp_key_id": "rzp_test_missing_token",
            },
        )
        client.cookies.clear()

        response = await client.post("/api/v1/merchant/auth/login", json={"slug": unique_slug})
        assert response.status_code == 401
        assert "session token is required" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_merchant_login_rejects_nonexistent_slug(db_session: AsyncSession) -> None:
    """Test 4: Merchant login with nonexistent slug fails closed with 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/merchant/auth/login",
            json={"slug": f"nonexistent-{uuid.uuid4().hex[:8]}"},
        )
        assert resp.status_code == 401
        assert "not found" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_merchant_me_endpoint_returns_profile_with_valid_token(
    db_session: AsyncSession,
) -> None:
    """Test 5: Authenticated GET /me endpoint returns full merchant profile."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        unique_slug = f"me-store-{uuid.uuid4().hex[:8]}"
        signup_res = await client.post(
            "/api/v1/merchant/auth/signup",
            json={
                "name": "Profile Store",
                "slug": unique_slug,
                "email": "me@store.com",
                "rzp_key_id": "rzp_test_me",
            },
        )
        auth_data = signup_res.json()
        merchant_id = auth_data["merchant_id"]
        assert auth_data["token"] is None
        headers = {"X-Merchant-ID": merchant_id}
        me_resp = await client.get("/api/v1/merchant/auth/me", headers=headers)
        assert me_resp.status_code == 200
        profile = me_resp.json()
        assert profile["merchant_id"] == merchant_id
        assert profile["name"] == "Profile Store"
        assert profile["slug"] == unique_slug
        assert profile["policies"]["max_discount_percentage"] == 15.0


@pytest.mark.asyncio
async def test_merchant_me_endpoint_rejects_forged_token(db_session: AsyncSession) -> None:
    """Test 6: Forged admin token signature fails closed with 401 Unauthorized."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        unique_slug = f"forged-store-{uuid.uuid4().hex[:8]}"
        signup_res = await client.post(
            "/api/v1/merchant/auth/signup",
            json={
                "name": "Forged Test Store",
                "slug": unique_slug,
                "email": "forged@store.com",
                "rzp_key_id": "rzp_test_forged",
            },
        )
        auth_data = signup_res.json()
        merchant_id = auth_data["merchant_id"]

        # Forged token with altered signature
        forged_token = f"admin:{merchant_id}:{unique_slug}:1999999999:bad_signature_here"

        headers = {
            "X-Merchant-ID": merchant_id,
            "X-Auth-Token": forged_token,
        }
        me_resp = await client.get("/api/v1/merchant/auth/me", headers=headers)
        assert me_resp.status_code == 401
        assert (
            "invalid" in me_resp.json()["detail"].lower()
            or "signature" in me_resp.json()["detail"].lower()
        )

        # Missing token must fail closed with 401
        client.cookies.clear()
        missing_token_headers = {"X-Merchant-ID": merchant_id}
        missing_resp = await client.get("/api/v1/merchant/auth/me", headers=missing_token_headers)
        assert missing_resp.status_code == 401
        assert "token is required" in missing_resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_merchant_cannot_access_other_merchant_profile(db_session: AsyncSession) -> None:
    """Test 7: Cross-tenant isolation — Merchant A's token cannot read Merchant B's profile."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create Merchant A
        res_a = await client.post(
            "/api/v1/merchant/auth/signup",
            json={
                "name": "Merchant Alpha",
                "slug": f"alpha-{uuid.uuid4().hex[:8]}",
                "email": "alpha@store.com",
                "rzp_key_id": "rzp_test_alpha",
            },
        )
        merchant_a_id = uuid.UUID(res_a.json()["merchant_id"])
        token_a = MerchantAuthService.generate_admin_token(
            merchant_a_id,
            get_settings().SECRET_KEY.get_secret_value(),
            slug=res_a.json()["slug"],
        )

        # Create Merchant B
        res_b = await client.post(
            "/api/v1/merchant/auth/signup",
            json={
                "name": "Merchant Beta",
                "slug": f"beta-{uuid.uuid4().hex[:8]}",
                "email": "beta@store.com",
                "rzp_key_id": "rzp_test_beta",
            },
        )
        merchant_b_id = res_b.json()["merchant_id"]

        # Merchant A attempts to access Merchant B using A's token
        headers = {
            "X-Merchant-ID": merchant_b_id,
            "X-Auth-Token": token_a,
        }
        cross_resp = await client.get("/api/v1/merchant/auth/me", headers=headers)
        assert cross_resp.status_code == 401


@pytest.mark.asyncio
async def test_merchant_complete_setup_updates_profile_and_policies(
    db_session: AsyncSession,
) -> None:
    """Test 8: Setup wizard completion atomically updates merchant profile and policy bounds."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        unique_slug = f"setup-store-{uuid.uuid4().hex[:8]}"
        res = await client.post(
            "/api/v1/merchant/auth/signup",
            json={
                "name": "Draft Store",
                "slug": unique_slug,
                "email": "setup@store.com",
                "rzp_key_id": "rzp_test_draft",
            },
        )
        data = res.json()
        merchant_id = data["merchant_id"]
        initial_hash = data["policies"]["policy_hash"]

        headers = {"X-Merchant-ID": merchant_id}

        # Complete setup with updated autonomy level and discount cap
        setup_payload = {
            "name": "Activated Enterprise Store",
            "rzp_key_id": "rzp_test_enterprise_live",
            "autonomy_level": 2,
            "max_discount_percentage": 25.0,
            "min_margin_percentage": 30.0,
            "max_single_transaction_paise": 8000000,
        }
        update_resp = await client.post(
            "/api/v1/merchant/setup/complete",
            json=setup_payload,
            headers=headers,
        )
        assert update_resp.status_code == 200
        updated = update_resp.json()

        assert updated["name"] == "Activated Enterprise Store"
        assert updated["rzp_key_id"] == "rzp_test_enterprise_live"
        assert updated["policies"]["autonomy_level"] == 2
        assert updated["policies"]["max_discount_percentage"] == 25.0
        assert updated["policies"]["min_margin_percentage"] == 30.0
        assert updated["policies"]["max_single_transaction_paise"] == 8000000
        assert updated["policies"]["policy_hash"] != initial_hash


@pytest.mark.asyncio
async def test_admin_token_expiration_fails_closed(db_session: AsyncSession) -> None:
    """Test 9: Expired admin token is rejected deterministically with 401."""
    settings = get_settings()
    secret = settings.SECRET_KEY.get_secret_value()

    merchant = Merchant(
        name="Expired Store",
        slug=f"exp-{uuid.uuid4().hex[:8]}",
        status="ACTIVE",
        rzp_key_id="rzp_test_exp",
    )
    db_session.add(merchant)
    await db_session.flush()

    # Create expired token (10 minutes in the past)
    past_time = datetime.now(UTC) - timedelta(minutes=10)
    expired_token = MerchantAuthService._generate_admin_token(merchant, past_time, secret)

    is_valid, m_id, err = MerchantAuthService.verify_admin_token(expired_token, secret)
    assert is_valid is False
    assert m_id is None
    assert "expired" in (err or "").lower()


def test_setup_schema_enforces_platform_transaction_ceiling() -> None:
    """Direct setup payloads cannot bypass the ₹1,00,000 platform boundary."""
    with pytest.raises(ValueError):
        MerchantSetupRequest(max_single_transaction_paise=10_000_001)
    assert (
        MerchantSetupRequest(max_single_transaction_paise=10_000_000).max_single_transaction_paise
        == 10_000_000
    )


@pytest.mark.asyncio
async def test_suspended_merchant_session_is_rejected_immediately(
    db_session: AsyncSession,
) -> None:
    """A valid pre-suspension session cannot access the control plane."""
    settings = get_settings()
    merchant = Merchant(
        name="Suspended Store",
        slug=f"suspended-{uuid.uuid4().hex[:8]}",
        status="ACTIVE",
        rzp_key_id="rzp_test_suspended",
    )
    db_session.add(merchant)
    await db_session.flush()
    token = MerchantAuthService.generate_admin_token(
        merchant.id, settings.SECRET_KEY.get_secret_value(), slug=merchant.slug
    )
    merchant.status = "SUSPENDED"
    await db_session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/api/v1/merchant/dashboard/summary",
            headers={"X-Merchant-ID": str(merchant.id), "X-Auth-Token": token},
        )

    assert response.status_code == 401
    assert "not active" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_insforge_identity_opens_only_its_linked_active_workspace(
    db_session: AsyncSession,
) -> None:
    """A verified InsForge identity may authenticate only its linked merchant."""
    owner_id = uuid.uuid4()
    merchant = Merchant(
        name="InsForge Linked Store",
        slug=f"insforge-{uuid.uuid4().hex[:8]}",
        status="ACTIVE",
        rzp_key_id="rzp_test_insforge_linked",
        auth_user_id=owner_id,
    )
    db_session.add(merchant)
    await db_session.flush()

    response = await MerchantAuthService.authenticate_insforge_merchant(
        db_session, owner_id, get_settings()
    )

    assert response.merchant_id == merchant.id
    assert response.token

    with pytest.raises(ValueError, match="No merchant workspace"):
        await MerchantAuthService.authenticate_insforge_merchant(
            db_session, uuid.uuid4(), get_settings()
        )


@pytest.mark.asyncio
async def test_webhook_secret_cannot_authorize_merchant_session(
    db_session: AsyncSession,
) -> None:
    """Webhook and control-plane signing keys remain separate trust domains."""
    settings = get_settings()
    merchant = Merchant(
        name="Key Separation Store",
        slug=f"key-separation-{uuid.uuid4().hex[:8]}",
        status="ACTIVE",
        rzp_key_id="rzp_test_key_separation",
    )
    db_session.add(merchant)
    await db_session.flush()
    webhook_signed_token = MerchantAuthService.generate_admin_token(
        merchant.id,
        settings.RAZORPAY_WEBHOOK_SECRET.get_secret_value(),
        slug=merchant.slug,
    )
    await db_session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/api/v1/merchant/auth/me",
            headers={"X-Merchant-ID": str(merchant.id), "X-Auth-Token": webhook_signed_token},
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_merchant_auth_events_in_cryptographic_audit_chain(
    db_session: AsyncSession,
) -> None:
    """Test 10: Merchant auth operations maintain unbroken SHA-256 cryptographic audit chain."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        unique_slug = f"audit-chain-store-{uuid.uuid4().hex[:8]}"
        res = await client.post(
            "/api/v1/merchant/auth/signup",
            json={
                "name": "Audit Tracked Store",
                "slug": unique_slug,
                "email": "audit@store.com",
                "rzp_key_id": "rzp_test_audit",
            },
        )
        merchant_id = uuid.UUID(res.json()["merchant_id"])
        # Refresh the active session and perform setup updates.
        login_response = await client.post(
            "/api/v1/merchant/auth/login",
            json={"slug": unique_slug},
        )
        assert login_response.status_code == 200
        await client.post(
            "/api/v1/merchant/setup/complete",
            json={
                "name": "Audit Tracked Store Final",
                "autonomy_level": 2,
                "max_discount_percentage": 20.0,
                "min_margin_percentage": 25.0,
                "max_single_transaction_paise": 6000000,
            },
            headers={"X-Merchant-ID": str(merchant_id)},
        )

        # Verify audit chain integrity
        is_valid, err = await AuditEvent.verify_chain(db_session, merchant_id)
        assert is_valid is True
        assert err is None


@pytest.mark.asyncio
async def test_spa_fallback_routes_and_html_surface() -> None:
    """Test 11: Web surface serves SPA index.html for HTML browser requests and SPA routes."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # JSON API request on root
        json_resp = await client.get("/", headers={"Accept": "application/json"})
        assert json_resp.status_code == 200
        assert json_resp.json()["name"] == "Agent-Ready Merchant Platform"

        # HTML Browser request on root
        html_resp = await client.get("/", headers={"Accept": "text/html,application/xhtml+xml"})
        assert html_resp.status_code == 200
        assert "text/html" in html_resp.headers["content-type"]
        assert '<div id="root"></div>' in html_resp.text

        # SPA protected & public client routes return HTML shell
        for route in ["/login", "/signup", "/onboarding", "/dashboard", "/approvals"]:
            r = await client.get(route)
            assert r.status_code == 200
            assert "text/html" in r.headers["content-type"]
            assert '<div id="root"></div>' in r.text
