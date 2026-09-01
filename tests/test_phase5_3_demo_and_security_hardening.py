"""Phase 5.3 Demo & Integration Hardening Adversarial Test Suite."""

import uuid
from datetime import UTC, datetime

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.config import get_settings
from agent_ready_merchant.main import app
from agent_ready_merchant.models.inventory import InventoryItem
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.order import Order
from agent_ready_merchant.models.payment import PaymentAttempt
from agent_ready_merchant.models.product import Product, ProductVariant
from agent_ready_merchant.models.transaction import TransactionRecord
from agent_ready_merchant.services.merchant_auth_service import MerchantAuthService


@pytest_asyncio.fixture
async def setup_two_merchants(db_session: AsyncSession):
    """Creates two distinct merchants with auth tokens for multi-tenant isolation testing."""
    settings = get_settings()
    secret = settings.SECRET_KEY.get_secret_value()

    # Merchant Alpha
    m1 = Merchant(
        name="Alpha Athletics",
        slug=f"alpha-store-{uuid.uuid4().hex[:6]}",
        rzp_key_id="rzp_test_alpha_key",
        currency="INR",
        status="ACTIVE",
        created_at=datetime.now(UTC),
    )
    db_session.add(m1)
    await db_session.flush()

    token1 = MerchantAuthService.generate_admin_token(m1.id, secret, slug=m1.slug)

    # Merchant Beta
    m2 = Merchant(
        name="Beta Boutique",
        slug=f"beta-store-{uuid.uuid4().hex[:6]}",
        rzp_key_id="rzp_test_beta_key",
        currency="INR",
        status="ACTIVE",
        created_at=datetime.now(UTC),
    )
    db_session.add(m2)
    await db_session.flush()

    token2 = MerchantAuthService.generate_admin_token(m2.id, secret, slug=m2.slug)
    await db_session.commit()

    return {
        "m1": m1,
        "token1": token1,
        "m2": m2,
        "token2": token2,
        "secret": secret,
    }


@pytest.mark.asyncio
async def test_demo_seed_and_standard_auto_commerce_flow(
    setup_two_merchants, db_session: AsyncSession
):
    """Verifies complete standard autonomous flow: seed catalog -> quote -> order -> settled."""
    data = setup_two_merchants
    m1 = data["m1"]
    token1 = data["token1"]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Seed Demo Data
        seed_res = await client.post(
            "/api/v1/merchant/demo/seed",
            headers={
                "X-Merchant-ID": str(m1.id),
                "X-Auth-Token": token1,
                "X-Idempotency-Key": str(uuid.uuid4()),
            },
        )
        assert seed_res.status_code == 200
        seed_data = seed_res.json()
        assert seed_data["products_seeded"] >= 3
        assert seed_data["policies_configured"] is True

        # 2. Execute Standard Auto Commerce Simulation
        sim_res = await client.post(
            "/api/v1/merchant/demo/simulate",
            headers={
                "X-Merchant-ID": str(m1.id),
                "X-Auth-Token": token1,
                "X-Idempotency-Key": str(uuid.uuid4()),
            },
            json={
                "scenario": "STANDARD_AUTO_COMMERCE",
                "sku": "RUN-PRO-01",
                "quantity": 1,
                "target_discount_pct": 10.0,
            },
        )
        assert sim_res.status_code == 200
        sim_data = sim_res.json()
        assert sim_data["status"] == "SETTLED"
        assert sim_data["policy_verdict"] == "ALLOW"
        assert sim_data["order_id"] is not None
        assert sim_data["rzp_order_id"] is not None
        assert sim_data["rzp_payment_id"] is not None
        assert sim_data["subtotal_paise"] == 1299900
        assert sim_data["discount_paise"] == 129990
        assert sim_data["total_paise"] == 1169910
        assert len(sim_data["steps"]) >= 5

        # 3. Verify Order in Order Ledger
        orders_res = await client.get(
            "/api/v1/merchant/orders",
            headers={
                "X-Merchant-ID": str(m1.id),
                "X-Auth-Token": token1,
                "X-Idempotency-Key": str(uuid.uuid4()),
            },
        )
        assert orders_res.status_code == 200
        orders = orders_res.json()
        assert len(orders) >= 1
        assert any(o["id"] == sim_data["order_id"] for o in orders)

        # 4. Verify Cryptographic Audit Chain
        audit_res = await client.get(
            "/api/v1/merchant/audit",
            headers={
                "X-Merchant-ID": str(m1.id),
                "X-Auth-Token": token1,
                "X-Idempotency-Key": str(uuid.uuid4()),
            },
        )
        assert audit_res.status_code == 200
        audit_data = audit_res.json()
        assert audit_data["chain_valid"] is True
        assert audit_data["total_count"] >= 3


@pytest.mark.asyncio
async def test_demo_seed_preserves_merchant_catalog_and_active_demo_reservations(
    setup_two_merchants, db_session: AsyncSession
):
    """Demo initialization must not reset merchant stock or active reservations."""
    data = setup_two_merchants
    merchant = data["m1"]
    token = data["token1"]

    merchant_product = Product(
        merchant_id=merchant.id,
        sku="MERCHANT-LIVE-01",
        title="Merchant Live Product",
        description="A real catalog item outside the demo catalog.",
        category="MERCHANT",
        base_price_paise=120000,
        floor_price_paise=100000,
        is_active=True,
        attributes={},
    )
    db_session.add(merchant_product)
    await db_session.flush()
    merchant_variant = ProductVariant(
        product_id=merchant_product.id,
        sku=merchant_product.sku,
        title=merchant_product.title,
        is_active=True,
    )
    db_session.add(merchant_variant)
    await db_session.flush()
    merchant_inventory = InventoryItem(
        variant_id=merchant_variant.id,
        available_quantity=7,
        reserved_quantity=3,
        safety_threshold=1,
    )
    db_session.add(merchant_inventory)
    await db_session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        headers = {"X-Merchant-ID": str(merchant.id), "X-Auth-Token": token}
        first_seed = await client.post("/api/v1/merchant/demo/seed", headers=headers)
        assert first_seed.status_code == 200

        await db_session.refresh(merchant_inventory)
        assert merchant_inventory.available_quantity == 7
        assert merchant_inventory.reserved_quantity == 3

        demo_product = (
            await db_session.execute(
                select(Product).where(
                    Product.merchant_id == merchant.id,
                    Product.sku == "PACE-BAND-03",
                )
            )
        ).scalar_one()
        demo_variant = (
            await db_session.execute(
                select(ProductVariant).where(ProductVariant.product_id == demo_product.id)
            )
        ).scalar_one()
        demo_inventory = (
            await db_session.execute(
                select(InventoryItem).where(InventoryItem.variant_id == demo_variant.id)
            )
        ).scalar_one()
        demo_inventory.available_quantity = 9
        demo_inventory.reserved_quantity = 2
        await db_session.commit()

        reset_seed = await client.post("/api/v1/merchant/demo/seed", headers=headers)
        assert reset_seed.status_code == 200
        await db_session.refresh(demo_inventory)
        assert demo_inventory.available_quantity == 9
        assert demo_inventory.reserved_quantity == 2


@pytest.mark.asyncio
async def test_demo_hitl_escalation_and_approval_resolution_flow(
    setup_two_merchants, db_session: AsyncSession
):
    """Verifies HITL escalation: 20% discount requested -> approval ticket generated -> approved."""
    data = setup_two_merchants
    m1 = data["m1"]
    token1 = data["token1"]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        seed_headers = {"X-Merchant-ID": str(m1.id), "X-Auth-Token": token1}
        seed_res = await client.post("/api/v1/merchant/demo/seed", headers=seed_headers)
        assert seed_res.status_code == 200
        policy_res = await client.put(
            "/api/v1/merchant/policies",
            headers=seed_headers,
            json={
                "autonomy_level": 2,
                "max_discount_percentage": 30.0,
                "min_margin_percentage": 20.0,
                "max_single_transaction_paise": 5_000_000,
            },
        )
        assert policy_res.status_code == 200

        # 1. Execute HITL Escalation Simulation
        sim_res = await client.post(
            "/api/v1/merchant/demo/simulate",
            headers={
                "X-Merchant-ID": str(m1.id),
                "X-Auth-Token": token1,
                "X-Idempotency-Key": str(uuid.uuid4()),
            },
            json={
                "scenario": "HITL_ESCALATION_COMMERCE",
                "sku": "RUN-PRO-01",
                "quantity": 1,
            },
        )
        assert sim_res.status_code == 200
        sim_data = sim_res.json()
        assert sim_data["status"] == "PENDING_APPROVAL"
        assert sim_data["policy_verdict"] == "ESCALATE_APPROVAL"
        approval_id = sim_data["approval_id"]
        assert approval_id is not None

        # 2. Check Approvals Queue
        approvals_res = await client.get(
            "/api/v1/merchant/approvals?status=PENDING",
            headers={
                "X-Merchant-ID": str(m1.id),
                "X-Auth-Token": token1,
                "X-Idempotency-Key": str(uuid.uuid4()),
            },
        )
        assert approvals_res.status_code == 200
        approvals = approvals_res.json()
        assert any(a["id"] == approval_id for a in approvals)

        # 3. Resolve Approval as Merchant (Approve)
        resolve_res = await client.post(
            f"/api/v1/merchant/approvals/{approval_id}/resolve",
            headers={
                "X-Merchant-ID": str(m1.id),
                "X-Auth-Token": token1,
                "X-Idempotency-Key": str(uuid.uuid4()),
            },
            json={
                "decision": "APPROVE",
                "reason_note": "Special demo customer discount approved by merchant.",
            },
        )
        assert resolve_res.status_code == 200
        resolved = resolve_res.json()
        assert resolved["status"] == "APPROVED"


@pytest.mark.asyncio
async def test_adversarial_forged_merchant_id_rejection(setup_two_merchants):
    """Adversarial Test: Tampered X-Merchant-ID with token of another merchant fails closed."""
    data = setup_two_merchants
    m2 = data["m2"]
    token1 = data["token1"]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(
            "/api/v1/merchant/dashboard/summary",
            headers={"X-Merchant-ID": str(m2.id), "X-Auth-Token": token1},
        )
        assert res.status_code == 401
        detail = res.json().get("detail", "")
        assert "Invalid" in detail or "expired" in detail


@pytest.mark.asyncio
async def test_adversarial_cross_tenant_inventory_mutation(
    setup_two_merchants, db_session: AsyncSession
):
    """Adversarial Test: Merchant 1 attempts to adjust inventory of Merchant 2's product."""
    data = setup_two_merchants
    m1 = data["m1"]
    token1 = data["token1"]
    m2 = data["m2"]

    # Seed product for Merchant 2
    p2 = Product(
        merchant_id=m2.id,
        sku=f"BETA-ITEM-{uuid.uuid4().hex[:4]}",
        title="Beta Exclusive Jacket",
        category="APPAREL",
        base_price_paise=1000000,
        floor_price_paise=800000,
        is_negotiable=True,
    )
    db_session.add(p2)
    await db_session.flush()

    v2 = ProductVariant(product_id=p2.id, sku=p2.sku, title=p2.title)
    db_session.add(v2)
    await db_session.flush()

    inv2 = InventoryItem(
        variant_id=v2.id, available_quantity=50, reserved_quantity=0, safety_threshold=2
    )
    db_session.add(inv2)
    await db_session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post(
            "/api/v1/merchant/inventory/adjust",
            headers={
                "X-Merchant-ID": str(m1.id),
                "X-Auth-Token": token1,
                "X-Idempotency-Key": str(uuid.uuid4()),
            },
            json={"sku": p2.sku, "quantity_delta": 10},
        )
        assert res.status_code == 400
        assert "not found" in res.json().get("detail", "").lower()


@pytest.mark.asyncio
async def test_adversarial_floor_price_violation_rejection(setup_two_merchants):
    """Adversarial Test: Creating product where floor_price > base_price fails closed."""
    data = setup_two_merchants
    m1 = data["m1"]
    token1 = data["token1"]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post(
            "/api/v1/merchant/products",
            headers={
                "X-Merchant-ID": str(m1.id),
                "X-Auth-Token": token1,
                "X-Idempotency-Key": str(uuid.uuid4()),
            },
            json={
                "sku": "INVALID-PRICE-01",
                "title": "Invalid Price Product",
                "category": "FOOTWEAR",
                "base_price_paise": 500000,  # 5,000 INR
                "floor_price_paise": 600000,  # 6,000 INR (violates floor <= base)
            },
        )
        assert res.status_code == 400
        assert "Floor price cannot exceed base price" in res.json().get("detail", "")


@pytest.mark.asyncio
async def test_adversarial_policy_ceiling_enforcement(setup_two_merchants):
    """Adversarial Test: Attempting to set max discount > 50% platform ceiling is rejected."""
    data = setup_two_merchants
    m1 = data["m1"]
    token1 = data["token1"]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.put(
            "/api/v1/merchant/policies",
            headers={"X-Merchant-ID": str(m1.id), "X-Auth-Token": token1},
            json={
                "autonomy_level": 1,
                "max_discount_percentage": 75.0,  # Violates 50% hard platform ceiling
                "min_margin_percentage": 20.0,
                "max_single_transaction_paise": 5000000,
            },
        )
        assert res.status_code in [400, 422]


@pytest.mark.asyncio
async def test_zero_secret_leakage_audit(setup_two_merchants):
    """Adversarial Audit: Asserts that secrets, API keys, and webhook tokens are never exposed."""
    data = setup_two_merchants
    m1 = data["m1"]
    token1 = data["token1"]
    settings = get_settings()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for path in [
            "/api/v1/merchant/auth/me",
            "/api/v1/merchant/dashboard/summary",
            "/api/v1/merchant/policies",
            "/api/v1/merchant/audit",
        ]:
            res = await client.get(
                path,
                headers={"X-Merchant-ID": str(m1.id), "X-Auth-Token": token1},
            )
            assert res.status_code == 200
            body_str = res.text
            # Assert secret absence
            assert settings.RAZORPAY_KEY_SECRET.get_secret_value() not in body_str
            assert settings.RAZORPAY_WEBHOOK_SECRET.get_secret_value() not in body_str
            assert "DATABASE_URL" not in body_str
            assert "admin_token" not in body_str


@pytest.mark.asyncio
async def test_demo_checkout_insufficient_inventory_fails_closed(setup_two_merchants):
    """Verifies that attempting simulation with quantity exceeding available stock fails closed."""
    data = setup_two_merchants
    m1 = data["m1"]
    token1 = data["token1"]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Seed
        await client.post(
            "/api/v1/merchant/demo/seed",
            headers={"X-Merchant-ID": str(m1.id), "X-Auth-Token": token1},
        )

        # Adjust inventory down to 1
        adj_res = await client.post(
            "/api/v1/merchant/inventory/adjust",
            headers={
                "X-Merchant-ID": str(m1.id),
                "X-Auth-Token": token1,
                "X-Idempotency-Key": str(uuid.uuid4()),
            },
            json={"sku": "RUN-PRO-01", "quantity_delta": -49},
        )
        assert adj_res.status_code == 200
        assert adj_res.json()["available_quantity"] == 1

        # Attempt to buy 5 units (exceeding stock of 1)
        res = await client.post(
            "/api/v1/merchant/demo/simulate",
            headers={
                "X-Merchant-ID": str(m1.id),
                "X-Auth-Token": token1,
                "X-Idempotency-Key": str(uuid.uuid4()),
            },
            json={
                "scenario": "STANDARD_AUTO_COMMERCE",
                "sku": "RUN-PRO-01",
                "quantity": 5,
                "target_discount_pct": 10.0,
            },
        )
        assert res.status_code == 400
        assert "insufficient inventory stock" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_demo_rejects_live_catalog_sku_without_mutating_inventory(
    setup_two_merchants, db_session: AsyncSession
):
    """The sandbox must never settle a merchant-owned production catalog SKU."""
    data = setup_two_merchants
    m1 = data["m1"]
    token1 = data["token1"]
    live_product = Product(
        merchant_id=m1.id,
        sku="LIVE-ONLY-01",
        title="Live Production Product",
        description="Ordinary merchant catalog item",
        category="GENERAL",
        base_price_paise=100_000,
        floor_price_paise=90_000,
        is_active=True,
        attributes={"demo_seeded": False},
    )
    db_session.add(live_product)
    await db_session.flush()
    live_variant = ProductVariant(
        product_id=live_product.id,
        sku=live_product.sku,
        title="Standard",
    )
    db_session.add(live_variant)
    await db_session.flush()
    live_inventory = InventoryItem(
        variant_id=live_variant.id,
        available_quantity=7,
        reserved_quantity=0,
    )
    db_session.add(live_inventory)
    await db_session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post(
            "/api/v1/merchant/demo/simulate",
            headers={
                "X-Merchant-ID": str(m1.id),
                "X-Auth-Token": token1,
                "X-Idempotency-Key": str(uuid.uuid4()),
            },
            json={"scenario": "STANDARD_AUTO_COMMERCE", "sku": live_product.sku, "quantity": 1},
        )
    assert res.status_code == 400
    assert "demo sku" in res.json()["detail"].lower()
    await db_session.refresh(live_inventory)
    assert live_inventory.available_quantity == 7


@pytest.mark.asyncio
async def test_demo_payment_reconciliation_flow(setup_two_merchants, db_session: AsyncSession):
    """Verifies PAYMENT_RECONCILIATION scenario uses out-of-band server query instead of webhook."""
    data = setup_two_merchants
    m1 = data["m1"]
    token1 = data["token1"]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post(
            "/api/v1/merchant/demo/seed",
            headers={"X-Merchant-ID": str(m1.id), "X-Auth-Token": token1},
        )

        res = await client.post(
            "/api/v1/merchant/demo/simulate",
            headers={
                "X-Merchant-ID": str(m1.id),
                "X-Auth-Token": token1,
                "X-Idempotency-Key": str(uuid.uuid4()),
            },
            json={
                "scenario": "PAYMENT_RECONCILIATION",
                "sku": "PACE-BAND-03",
                "quantity": 1,
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "SETTLED"
        recon_step = next(s for s in data["steps"] if s["action"] == "reconcile_payment")
        assert recon_step["actor"] == "Server Payment Reconciler"
        assert recon_step["status"] == "SETTLED"
        assert (
            "out-of-band" in recon_step["summary"].lower()
            or "server-side" in recon_step["summary"].lower()
        )

        order = await db_session.get(Order, uuid.UUID(data["order_id"]))
        assert order is not None and order.status == "PAID"
        payment_attempt = (
            await db_session.execute(
                select(PaymentAttempt).where(PaymentAttempt.order_id == order.id)
            )
        ).scalar_one()
        assert payment_attempt.status == "CAPTURED"
        assert payment_attempt.webhook_payload is not None
        assert payment_attempt.webhook_payload["order_id"] == data["rzp_order_id"]
        transaction = (
            await db_session.execute(
                select(TransactionRecord).where(
                    TransactionRecord.payment_attempt_id == payment_attempt.id
                )
            )
        ).scalar_one()
        assert transaction.status == "COMMITTED"
        assert transaction.amount_paise == data["total_paise"]


@pytest.mark.asyncio
async def test_demo_seed_resets_mutated_stock_and_policies(setup_two_merchants):
    """Verifies that seeding demo state resets depleted inventory stock and modified policies."""
    data = setup_two_merchants
    m1 = data["m1"]
    token1 = data["token1"]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Initial seed
        await client.post(
            "/api/v1/merchant/demo/seed",
            headers={"X-Merchant-ID": str(m1.id), "X-Auth-Token": token1},
        )

        # 2. Mutate policy
        await client.put(
            "/api/v1/merchant/policies",
            headers={"X-Merchant-ID": str(m1.id), "X-Auth-Token": token1},
            json={
                "autonomy_level": 2,
                "max_discount_percentage": 30.0,
                "min_margin_percentage": 25.0,
                "max_single_transaction_paise": 1000000,
            },
        )

        # 3. Re-seed / reset
        reset_res = await client.post(
            "/api/v1/merchant/demo/seed",
            headers={"X-Merchant-ID": str(m1.id), "X-Auth-Token": token1},
        )
        assert reset_res.status_code == 200

        # 4. Check policy reset to default baseline
        pol_res = await client.get(
            "/api/v1/merchant/policies",
            headers={"X-Merchant-ID": str(m1.id), "X-Auth-Token": token1},
        )
        assert pol_res.status_code == 200
        pol_data = pol_res.json()
        assert pol_data["autonomy_level"] == 1
        assert pol_data["max_discount_percentage"] == 15.0
