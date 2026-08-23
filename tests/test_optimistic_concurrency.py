"""Tests for optimistic locking concurrency control and version checking."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_ready_merchant.db.concurrency import (
    OptimisticLockError,
    update_with_version_check,
)
from agent_ready_merchant.models.inventory import InventoryItem
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.product import Product, ProductVariant


@pytest.mark.asyncio
async def test_optimistic_lock_successful_increment(db_session: AsyncSession) -> None:
    """Verifies that an update with the correct version succeeds and increments the version."""
    merchant = Merchant(name="ConcurStore", slug="concur-store", rzp_key_id="rzp_test_concur")
    db_session.add(merchant)
    await db_session.flush()

    product = Product(
        merchant_id=merchant.id,
        sku="SKU-CONCUR-01",
        title="Concurrent Item",
        category="Tech",
        base_price_paise=100000,
        floor_price_paise=90000,
    )
    db_session.add(product)
    await db_session.flush()

    variant = ProductVariant(product_id=product.id, sku="SKU-CONCUR-01-V", title="Variant 1")
    db_session.add(variant)
    await db_session.flush()

    inventory = InventoryItem(
        variant_id=variant.id,
        available_quantity=5,
        reserved_quantity=0,
    )
    db_session.add(inventory)
    await db_session.flush()

    assert inventory.version == 1
    assert inventory.available_quantity == 5

    # Apply valid version update (version 1 -> 2)
    new_version = await update_with_version_check(
        session=db_session,
        model_class=InventoryItem,
        entity_id=inventory.id,
        expected_version=1,
        values={"available_quantity": 4, "reserved_quantity": 1},
    )
    await db_session.flush()

    assert new_version == 2

    # Verify updated row in DB
    stmt = select(InventoryItem).where(InventoryItem.id == inventory.id)
    result = await db_session.execute(stmt)
    refetched = result.scalar_one()
    assert refetched.version == 2
    assert refetched.available_quantity == 4
    assert refetched.reserved_quantity == 1


@pytest.mark.asyncio
async def test_optimistic_lock_rejects_stale_version(db_session: AsyncSession) -> None:
    """Verifies that update with stale expected_version raises OptimisticLockError."""
    merchant = Merchant(name="RaceStore", slug="race-store", rzp_key_id="rzp_test_race")
    db_session.add(merchant)
    await db_session.flush()

    product = Product(
        merchant_id=merchant.id,
        sku="SKU-RACE-01",
        title="Race Item",
        category="Tech",
        base_price_paise=100000,
        floor_price_paise=90000,
    )
    db_session.add(product)
    await db_session.flush()

    variant = ProductVariant(product_id=product.id, sku="SKU-RACE-01-V", title="Race Variant")
    db_session.add(variant)
    await db_session.flush()

    inventory = InventoryItem(
        variant_id=variant.id,
        available_quantity=1,
        reserved_quantity=0,
    )
    db_session.add(inventory)
    await db_session.flush()

    assert inventory.version == 1

    # First transaction advances version to 2
    await update_with_version_check(
        session=db_session,
        model_class=InventoryItem,
        entity_id=inventory.id,
        expected_version=1,
        values={"available_quantity": 0, "reserved_quantity": 1},
    )
    await db_session.flush()

    # Second transaction attempts to update assuming version is still 1 -> MUST FAIL!
    with pytest.raises(OptimisticLockError) as exc_info:
        await update_with_version_check(
            session=db_session,
            model_class=InventoryItem,
            entity_id=inventory.id,
            expected_version=1,  # Stale version!
            values={"available_quantity": 0, "reserved_quantity": 1},
        )

    assert "Optimistic lock conflict" in str(exc_info.value)
    assert exc_info.value.expected_version == 1
