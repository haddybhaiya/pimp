import os
import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from agent_ready_merchant.config import get_settings
from agent_ready_merchant.db.session import get_db_session
from agent_ready_merchant.main import create_app
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.inventory import InventoryItem
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.product import Product, ProductVariant
from agent_ready_merchant.schemas.demo_simulator import DemoSimulationStepRequest
from agent_ready_merchant.services.demo_simulator_service import DemoSimulatorService
from agent_ready_merchant.services.merchant_auth_service import MerchantAuthService

INSFORGE_DB_URL = os.environ.get("INSFORGE_DATABASE_URL") or os.environ.get("DATABASE_URL")


@pytest.mark.asyncio
async def test_insforge_postgresql_live_concurrency_and_audit():
    """Verifies live PostgreSQL operations: SELECT FOR UPDATE, simulation, and audit chain."""
    if not INSFORGE_DB_URL or "postgresql" not in INSFORGE_DB_URL:
        pytest.skip("INSFORGE_DATABASE_URL or PostgreSQL DATABASE_URL not set in environment.")

    try:
        engine = create_async_engine(INSFORGE_DB_URL, echo=False)
        session_factory = async_sessionmaker(
            bind=engine, class_=AsyncSession, expire_on_commit=False
        )
    except Exception as exc:
        pytest.skip(f"Could not connect to PostgreSQL: {exc}")

    settings = get_settings()
    secret = settings.RAZORPAY_WEBHOOK_SECRET.get_secret_value()

    async with session_factory() as session:
        # 1. Create unique merchant
        slug = f"insforge-ci-{uuid.uuid4().hex[:6]}"
        m = Merchant(
            name="InsForge CI Verified Store",
            slug=slug,
            currency="INR",
            rzp_key_id="rzp_test_ci_key",
            status="ACTIVE",
            created_at=datetime.now(UTC),
        )
        session.add(m)
        await session.flush()
        merchant_id = m.id

        # 2. Append audit event
        ev1 = await AuditEvent.create_event(
            session=session,
            merchant_id=merchant_id,
            actor_type="SYSTEM",
            event_type="INSFORGE_CI_DEPLOYMENT_VERIFIED",
            payload={"verified": True, "provider": "insforge"},
        )
        await session.flush()
        assert ev1.event_hash is not None

        # 3. Seed demo catalog
        seed_res = await DemoSimulatorService.seed_demo_catalog_and_policies(session, merchant_id)
        assert seed_res.products_seeded >= 3

        # 4. Verify PostgreSQL row lock (SELECT ... FOR UPDATE)
        inv_stmt = (
            select(InventoryItem, ProductVariant, Product)
            .join(ProductVariant, InventoryItem.variant_id == ProductVariant.id)
            .join(Product, ProductVariant.product_id == Product.id)
            .where(Product.merchant_id == merchant_id)
            .with_for_update()
        )
        inv_res = (await session.execute(inv_stmt)).first()
        assert inv_res is not None

        # 5. Full Autonomous Commerce simulation
        sim_res = await DemoSimulatorService.execute_simulation(
            session=session,
            merchant_id=merchant_id,
            req=DemoSimulationStepRequest(
                scenario="STANDARD_AUTO_COMMERCE",
                sku="RUN-PRO-01",
                quantity=1,
                target_discount_pct=10.0,
            ),
            settings=settings,
        )
        assert sim_res.status == "SETTLED"
        assert sim_res.policy_verdict == "ALLOW"
        assert sim_res.order_id is not None

        # 6. Verify audit hash chain on PostgreSQL
        is_valid, count = await AuditEvent.verify_chain(session, merchant_id)
        assert is_valid is True

        await session.commit()

    # 7. Test HTTP API Surface with live DB
    app = create_app()

    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as s:
            try:
                yield s
                await s.commit()
            except Exception:
                await s.rollback()
                raise

    app.dependency_overrides[get_db_session] = override_get_db_session
    token = MerchantAuthService.generate_admin_token(merchant_id, secret, slug=slug)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Health check
        health_res = await client.get("/health")
        assert health_res.status_code == 200
        health_data = health_res.json()
        assert health_data["application_alive"] is True
        assert health_data["configuration_valid"] is True

        # Dashboard summary
        dash_res = await client.get(
            "/api/v1/merchant/dashboard/summary",
            headers={"X-Merchant-ID": str(merchant_id), "X-Auth-Token": token},
        )
        assert dash_res.status_code == 200
        dash_data = dash_res.json()
        assert dash_data["total_products"] >= 3
        assert dash_data["total_orders"] >= 1
