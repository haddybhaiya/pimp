"""Discovery Network Service coordinating safe public merchant discovery.

Adheres strictly to Phase 9 specifications:
- Governs discoverability states (PRIVATE, DISCOVERABLE, PAUSED, SUSPENDED)
- Human-only administrative control over discoverability
- Public capability graph derived from canonical CapabilityRegistry
- Strict eligibility filtering and explainable deterministic ranking
- Anti-probing: uniform 404 for non-discoverable or nonexistent merchants
- Zero secret, private policy, or buyer PII leakage
- Bounded in-memory search rate-limiting
- Replay-safe discovery telemetry
"""

from __future__ import annotations

import collections
import logging
import time
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from agent_ready_merchant.gateway.registry import CapabilityRegistry
from agent_ready_merchant.models.audit import AuditEvent
from agent_ready_merchant.models.discovery import (
    DiscoverabilityState,
    DiscoveryTelemetryEventType,
    MerchantDiscoveryProfile,
    MerchantDiscoveryTelemetry,
    compute_discovery_metadata_hash,
)
from agent_ready_merchant.models.inventory import InventoryItem
from agent_ready_merchant.models.merchant import Merchant
from agent_ready_merchant.models.policy import PolicyRule
from agent_ready_merchant.models.product import Product, ProductVariant
from agent_ready_merchant.schemas.discovery import (
    BuyerDiscoveryIntent,
    DiscoverabilityStatusResponse,
    DiscoverabilityUpdateRequest,
    DiscoveryMatchResult,
    DiscoverySearchResponse,
    PublicCapabilityNode,
    PublicMerchantProfile,
    PublicProductSummary,
)

logger = logging.getLogger("agent_ready_merchant.discovery")


class DiscoverySecurityError(Exception):
    """Raised when an unauthorized actor attempts to modify discoverability."""


class DiscoveryConflictError(Exception):
    """Raised when an optimistic discovery-profile update is stale."""


class DiscoveryRateLimitError(Exception):
    """Raised when public discovery search rate limit is exceeded."""


class MerchantNotFoundError(Exception):
    """Raised when a merchant is not found or not discoverable (anti-probing)."""


# In-memory sliding window rate limiter: IP -> list of timestamps
_SEARCH_RATE_LIMITS: dict[str, list[float]] = collections.defaultdict(list)
_MAX_SEARCHES_PER_MINUTE = 60
_RATE_LIMIT_WINDOW_SECONDS = 60.0
_MAX_PUBLIC_PRODUCTS_PER_MERCHANT = 20


def check_and_record_search_rate_limit(client_ip: str) -> None:
    """Enforces bounded in-memory sliding window rate limiting on public search."""
    now = time.monotonic()
    window_start = now - _RATE_LIMIT_WINDOW_SECONDS

    # Clean old timestamps
    timestamps = [ts for ts in _SEARCH_RATE_LIMITS[client_ip] if ts > window_start]

    if len(timestamps) >= _MAX_SEARCHES_PER_MINUTE:
        _SEARCH_RATE_LIMITS[client_ip] = timestamps
        raise DiscoveryRateLimitError(
            f"Public discovery search rate limit exceeded ({_MAX_SEARCHES_PER_MINUTE}/min). "
            "Please retry later."
        )

    timestamps.append(now)
    _SEARCH_RATE_LIMITS[client_ip] = timestamps


def reset_search_rate_limits() -> None:
    """Clears rate limiter state (used in testing)."""
    _SEARCH_RATE_LIMITS.clear()


class DiscoveryService:
    """Core server-authoritative service for Phase 9 Discovery Network."""

    @classmethod
    async def get_or_create_profile(
        cls,
        session: AsyncSession,
        merchant_id: uuid.UUID,
        *,
        for_update: bool = False,
    ) -> MerchantDiscoveryProfile:
        """Retrieves or creates the default PRIVATE discovery profile for a merchant."""
        stmt = select(MerchantDiscoveryProfile).where(
            MerchantDiscoveryProfile.merchant_id == merchant_id
        )
        if for_update:
            stmt = stmt.with_for_update()
        profile = (await session.execute(stmt)).scalar_one_or_none()
        if profile is not None:
            return profile

        # Default initial state is strictly PRIVATE
        initial_tags: list[str] = ["general", "commerce"]
        # Delivery coverage is unknown until the merchant explicitly declares it.
        # Do not fabricate a region in a public discovery response.
        initial_regions: list[str] = []
        meta_hash = compute_discovery_metadata_hash(
            {
                "merchant_id": str(merchant_id),
                "discoverability_state": DiscoverabilityState.PRIVATE.value,
                "custom_tags": initial_tags,
                "delivery_regions": initial_regions,
            }
        )

        profile = MerchantDiscoveryProfile(
            public_id=uuid.uuid4(),
            merchant_id=merchant_id,
            discoverability_state=DiscoverabilityState.PRIVATE.value,
            custom_tags=initial_tags,
            custom_description=None,
            delivery_regions=initial_regions,
            profile_version=1,
            metadata_hash=meta_hash,
            last_refreshed_at=datetime.now(UTC),
        )
        session.add(profile)
        await session.flush()
        return profile

    @classmethod
    async def update_discoverability(
        cls,
        session: AsyncSession,
        merchant_id: uuid.UUID,
        req: DiscoverabilityUpdateRequest,
        actor_role: str = "MERCHANT_ADMIN",
        actor_id: str | None = None,
    ) -> MerchantDiscoveryProfile:
        """Updates discoverability settings and metadata.

        Strictly enforces that ONLY human MERCHANT_ADMIN can change discoverability.
        Autonomous agents, buyers, and non-admins fail closed.
        """
        if actor_role != "MERCHANT_ADMIN":
            raise DiscoverySecurityError(
                f"Actor role '{actor_role}' is not authorized to modify discoverability settings. "
                "Only human MERCHANT_ADMIN may publish or modify discovery profiles."
            )

        profile = await cls.get_or_create_profile(session, merchant_id, for_update=True)

        if req.expected_profile_version != profile.profile_version:
            raise DiscoveryConflictError(
                "Discovery profile was updated by another request. Refresh and retry."
            )

        # Apply state changes if requested
        if req.discoverability_state is not None:
            # Cannot self-assign SUSPENDED via merchant control plane
            if req.discoverability_state not in (
                DiscoverabilityState.PRIVATE.value,
                DiscoverabilityState.DISCOVERABLE.value,
                DiscoverabilityState.PAUSED.value,
            ):
                raise ValueError(
                    f"Invalid discoverability state '{req.discoverability_state}'. "
                    "Allowed values: PRIVATE, DISCOVERABLE, PAUSED."
                )
            profile.discoverability_state = req.discoverability_state

        if req.custom_tags is not None:
            # Sanitize and bound tags
            profile.custom_tags = [
                str(t).strip().lower()[:50] for t in req.custom_tags if str(t).strip()
            ][:20]

        if req.custom_description is not None:
            profile.custom_description = req.custom_description[:1000]

        if req.delivery_regions is not None:
            profile.delivery_regions = [
                str(r).strip().upper()[:50] for r in req.delivery_regions if str(r).strip()
            ][:50]

        profile.profile_version += 1
        profile.last_refreshed_at = datetime.now(UTC)

        # Compute updated metadata hash
        profile.metadata_hash = compute_discovery_metadata_hash(
            {
                "merchant_id": str(merchant_id),
                "discoverability_state": profile.discoverability_state,
                "custom_tags": profile.custom_tags,
                "custom_description": profile.custom_description,
                "delivery_regions": profile.delivery_regions,
                "profile_version": profile.profile_version,
            }
        )

        # Commit immutable audit log with cryptographic hash chaining
        await AuditEvent.create_event(
            session=session,
            merchant_id=merchant_id,
            actor_type="MERCHANT_ADMIN",
            event_type="MERCHANT_DISCOVERY_PROFILE_UPDATED",
            payload={
                "actor_id": actor_id or str(merchant_id),
                "discoverability_state": profile.discoverability_state,
                "profile_version": profile.profile_version,
                "metadata_hash": profile.metadata_hash,
                "custom_tags": profile.custom_tags,
            },
        )
        return profile

    @staticmethod
    def _variant_can_fulfill(variant: ProductVariant, quantity: int) -> bool:
        """Uses the canonical inventory rule without reserving stock during discovery."""
        inventory = variant.inventory_item
        return (
            inventory is not None
            and inventory.available_quantity >= quantity + inventory.safety_threshold
        )

    @staticmethod
    def _effective_variant_price(product: Product, variant: ProductVariant) -> int:
        """Returns the canonical non-binding effective price for one variant."""
        return variant.price_override_paise or product.base_price_paise

    @classmethod
    async def _load_public_catalog_summary(
        cls,
        session: AsyncSession,
        merchant_id: uuid.UUID,
    ) -> tuple[list[PublicProductSummary], int, int, bool]:
        """Returns a bounded public sample plus authoritative catalog aggregates.

        The public profile displays a small SKU-ordered sample. Price range and
        availability are separately aggregated in SQL over the active catalog,
        so response bounds never make public metadata inaccurate.
        """
        products_stmt = (
            select(Product)
            .options(
                selectinload(Product.variants).selectinload(ProductVariant.inventory_item),
            )
            .where(
                Product.merchant_id == merchant_id,
                Product.is_active == True,  # noqa: E712
            )
            .order_by(Product.sku.asc())
            .limit(_MAX_PUBLIC_PRODUCTS_PER_MERCHANT)
        )
        products = (await session.execute(products_stmt)).scalars().all()

        summaries: list[PublicProductSummary] = []
        for product in products:
            active_variants = [variant for variant in product.variants if variant.is_active]
            if not active_variants:
                continue
            variant_prices = [
                cls._effective_variant_price(product, variant) for variant in active_variants
            ]
            sample_sku = next(
                (variant.sku for variant in active_variants if variant.sku),
                None,
            )
            summaries.append(
                PublicProductSummary(
                    product_sku=product.sku,
                    title=product.title,
                    category=product.category,
                    description=product.description,
                    price_range_paise={"min": min(variant_prices), "max": max(variant_prices)},
                    in_stock=any(
                        cls._variant_can_fulfill(variant, 1) for variant in active_variants
                    ),
                    attributes={"sample_sku": sample_sku} if sample_sku is not None else {},
                )
            )

        effective_price = func.coalesce(
            ProductVariant.price_override_paise,
            Product.base_price_paise,
        )
        price_range_stmt = (
            select(func.min(effective_price), func.max(effective_price))
            .select_from(Product)
            .join(ProductVariant, ProductVariant.product_id == Product.id)
            .where(
                Product.merchant_id == merchant_id,
                Product.is_active == True,  # noqa: E712
                ProductVariant.is_active == True,  # noqa: E712
            )
        )
        overall_min, overall_max = (await session.execute(price_range_stmt)).one()

        availability_stmt = (
            select(ProductVariant.id)
            .select_from(Product)
            .join(ProductVariant, ProductVariant.product_id == Product.id)
            .join(InventoryItem, InventoryItem.variant_id == ProductVariant.id)
            .where(
                Product.merchant_id == merchant_id,
                Product.is_active == True,  # noqa: E712
                ProductVariant.is_active == True,  # noqa: E712
                InventoryItem.available_quantity >= InventoryItem.safety_threshold + 1,
            )
            .limit(1)
        )
        has_available_inventory = (await session.execute(availability_stmt)).scalar_one_or_none()
        return (
            summaries,
            int(overall_min or 0),
            int(overall_max or 0),
            has_available_inventory is not None,
        )

    @classmethod
    async def _load_matching_products(
        cls,
        session: AsyncSession,
        merchant_id: uuid.UUID,
        intent: BuyerDiscoveryIntent,
        *,
        query_text: str,
        merchant_tags: list[str],
    ) -> list[Product]:
        """Loads at most 20 products matching all known buyer constraints.

        Product, variant, stock, text, attribute, and budget predicates are
        applied before the limit. Public search therefore cannot eager-load a
        merchant's entire catalog, while an explicitly requested later SKU is
        still discoverable.
        """
        stmt = (
            select(Product)
            .join(ProductVariant, ProductVariant.product_id == Product.id)
            .join(InventoryItem, InventoryItem.variant_id == ProductVariant.id)
            .options(
                selectinload(Product.variants).selectinload(ProductVariant.inventory_item),
            )
            .where(
                Product.merchant_id == merchant_id,
                Product.is_active == True,  # noqa: E712
                ProductVariant.is_active == True,  # noqa: E712
                InventoryItem.available_quantity
                >= InventoryItem.safety_threshold + intent.quantity,
            )
        )

        if intent.product_sku:
            stmt = stmt.where(Product.sku == intent.product_sku)

        category_filter = (intent.category or "").strip().lower()
        if category_filter:
            stmt = stmt.where(func.lower(Product.category).contains(category_filter))

        tag_matches_query = bool(
            query_text and any(query_text in tag.lower() for tag in merchant_tags)
        )
        if query_text and not tag_matches_query:
            text_predicates = [
                func.lower(Product.title).contains(query_text),
                func.lower(Product.description).contains(query_text),
                func.lower(Product.category).contains(query_text),
            ]
            for word in query_text.split():
                if len(word) > 2:
                    text_predicates.extend(
                        [
                            func.lower(Product.title).contains(word),
                            func.lower(Product.description).contains(word),
                        ]
                    )
            stmt = stmt.where(or_(*text_predicates))

        required_values = [
            str(value).strip().lower()
            for value in intent.required_attributes.values()
            if str(value).strip()
        ]
        for value in required_values:
            stmt = stmt.where(
                or_(
                    func.lower(ProductVariant.title).contains(value),
                    func.lower(ProductVariant.sku).contains(value),
                )
            )

        if intent.maximum_budget_paise is not None:
            effective_price = func.coalesce(
                ProductVariant.price_override_paise,
                Product.base_price_paise,
            )
            stmt = stmt.where(effective_price * intent.quantity <= intent.maximum_budget_paise)

        stmt = stmt.distinct().order_by(Product.sku.asc()).limit(_MAX_PUBLIC_PRODUCTS_PER_MERCHANT)
        return list((await session.execute(stmt)).scalars().all())

    @classmethod
    def get_public_capability_graph(cls) -> list[PublicCapabilityNode]:
        """Generates the safe, descriptive public capability graph.

        Discovery is descriptive only; discovery of a capability does not grant invocation.
        """
        nodes: list[PublicCapabilityNode] = []
        for name, cap in CapabilityRegistry._CAPABILITIES.items():
            # Classify monetary impact
            monetary_desc = (
                "Direct financial transaction processing"
                if cap.monetary_impact
                else (
                    "Price quote calculation and negotiation"
                    if "quote" in name
                    else "None (informational)"
                )
            )

            side_effect_desc = (
                ", ".join(cap.side_effects)
                if cap.side_effects
                else "Read-only idempotent operation"
            )

            nodes.append(
                PublicCapabilityNode(
                    name=cap.name,
                    protocol_version="1.0.0",
                    classification=cap.classification,
                    side_effect_classification=side_effect_desc,
                    monetary_impact_classification=monetary_desc,
                    authorization_requirement=cap.required_capability,
                    approval_requirement=cap.approval_requirement,
                    idempotency_requirement=cap.idempotency_requirement,
                    supported_adapters=["ACP", "REST"],
                    coarse_availability="AVAILABLE",
                )
            )
        return nodes

    @classmethod
    async def build_public_profile(
        cls,
        session: AsyncSession,
        merchant_id: uuid.UUID,
        *,
        loaded_merchant: Merchant | None = None,
    ) -> PublicMerchantProfile | None:
        """Constructs the safe public discovery representation of a merchant.

        Returns None if merchant is not ACTIVE or discoverability_state != DISCOVERABLE.
        Guarantees zero leakage of secrets, private policies, or buyer PII.
        """
        merchant = loaded_merchant
        if merchant is None:
            stmt_m = (
                select(Merchant)
                .options(
                    selectinload(Merchant.discovery_profile),
                )
                .where(Merchant.id == merchant_id)
            )
            merchant = (await session.execute(stmt_m)).scalar_one_or_none()

        if merchant is None:
            return None

        # Anti-probing: must be ACTIVE and kill switch OFF
        if merchant.status != "ACTIVE" or merchant.kill_switch_enabled:
            return None

        profile = merchant.discovery_profile
        if (
            profile is None
            or profile.discoverability_state != DiscoverabilityState.DISCOVERABLE.value
        ):
            return None

        (
            product_summaries,
            overall_min,
            overall_max,
            has_available_inventory,
        ) = await cls._load_public_catalog_summary(session, merchant_id)

        # Check negotiation support via active merchant policies
        stmt_pol = select(PolicyRule).where(
            PolicyRule.merchant_id == merchant_id,
            PolicyRule.is_active == True,  # noqa: E712
            PolicyRule.rule_type == "MAX_DISCOUNT_PCT",
        )
        policy_rule = (await session.execute(stmt_pol)).scalar_one_or_none()
        negotiation_supported = False
        if policy_rule is not None:
            max_disc = float(
                policy_rule.rule_value.get(
                    "max_discount_pct",
                    policy_rule.rule_value.get(
                        "max_discount_percentage",
                        policy_rule.rule_value.get("max_discount", 0),
                    ),
                )
            )
            negotiation_supported = max_disc > 0

        # Authoritative coarse trust signals
        trust_signals = [
            "MERCHANT_ACTIVE",
            "DISCOVERY_PROFILE_VALID",
            "CANONICAL_GATEWAY_AVAILABLE",
            "POLICY_ENFORCEMENT_ENABLED",
            "AUDIT_LEDGER_ENABLED",
            "CHECKOUT_AVAILABLE",
            "PROTOCOL_SUPPORTED",
        ]

        supported_caps = list(CapabilityRegistry._CAPABILITIES.keys())
        desc = profile.custom_description or f"Official agent-ready storefront for {merchant.name}."

        return PublicMerchantProfile(
            public_id=str(profile.public_id),
            slug=merchant.slug,
            display_name=merchant.name,
            category=product_summaries[0].category if product_summaries else "General",
            description=desc,
            discovery_tags=profile.custom_tags or ["commerce"],
            safe_product_summaries=product_summaries,
            supported_currencies=[merchant.currency],
            price_range_paise={"min": overall_min, "max": overall_max},
            safe_delivery_regions=profile.delivery_regions,
            inventory_summary="AVAILABLE" if has_available_inventory else "OUT_OF_STOCK",
            negotiation_supported=negotiation_supported,
            checkout_available=not merchant.kill_switch_enabled,
            supported_canonical_capabilities=supported_caps,
            supported_protocol_versions=["ACP/1.0", "REST/1.0"],
            discovery_schema_version="1.0.0",
            profile_version=profile.profile_version,
            updated_at=profile.last_refreshed_at.isoformat(),
            verified_trust_signals=trust_signals,
        )

    @classmethod
    async def get_public_merchant_by_id_or_slug(
        cls,
        session: AsyncSession,
        public_id_or_slug: str,
        *,
        correlation_id: str | None = None,
    ) -> PublicMerchantProfile:
        """Retrieves a public merchant profile by ID or slug.

        Enforces anti-probing: throws uniform MerchantNotFoundError for nonexistent,
        PRIVATE, PAUSED, or SUSPENDED merchants.
        """
        merchant_id = await cls.resolve_discoverable_merchant_id(session, public_id_or_slug)
        profile = await cls.build_public_profile(session, merchant_id)
        if profile is None:  # Defensive: resolution already performs this check.
            raise MerchantNotFoundError("Merchant not found or not discoverable.")
        if correlation_id is not None:
            await cls.record_telemetry(
                session=session,
                merchant_id=merchant_id,
                event_type=DiscoveryTelemetryEventType.MERCHANT_SELECTED.value,
                correlation_id=correlation_id,
            )
        return profile

    @classmethod
    async def resolve_discoverable_merchant_id(
        cls,
        session: AsyncSession,
        public_id_or_slug: str,
    ) -> uuid.UUID:
        """Resolves a public reference without exposing a merchant database identifier."""
        merchant_id: uuid.UUID | None = None
        try:
            public_id = uuid.UUID(public_id_or_slug)
            stmt_public_id = select(MerchantDiscoveryProfile.merchant_id).where(
                MerchantDiscoveryProfile.public_id == public_id
            )
            merchant_id = (await session.execute(stmt_public_id)).scalar_one_or_none()
        except ValueError:
            # Slug lookup
            stmt_slug = select(Merchant.id).where(Merchant.slug == public_id_or_slug)
            merchant_id = (await session.execute(stmt_slug)).scalar_one_or_none()

        if merchant_id is None:
            raise MerchantNotFoundError("Merchant not found or not discoverable.")

        profile = await cls.build_public_profile(session, merchant_id)
        if profile is None:
            raise MerchantNotFoundError("Merchant not found or not discoverable.")
        return merchant_id

    @classmethod
    async def search_merchants(
        cls,
        session: AsyncSession,
        intent: BuyerDiscoveryIntent,
        client_ip: str = "127.0.0.1",
        correlation_id: str | None = None,
    ) -> DiscoverySearchResponse:
        """Performs strict, bounded deterministic matching and ranking for external buyers.

        Adheres strictly to Phase 9 rules:
        1. Bounded search rate limiting
        2. Strict eligibility filtering (DISCOVERABLE only, currency, budget overflow protection)
        3. Explainable deterministic ranking with reason codes
        4. Replay-safe discovery telemetry
        5. Prompt injection text treated as search keywords only
        """
        # 1. Rate Limiting Check
        check_and_record_search_rate_limit(client_ip)

        corr_id = correlation_id or f"disc-corr-{uuid.uuid4().hex}"

        # 2. Read one deterministic, bounded candidate window.  Discovery is
        # descriptive: a continuation cursor never changes transaction-time
        # authority, which remains in the canonical gateway.
        stmt = (
            select(Merchant)
            .join(
                MerchantDiscoveryProfile,
                Merchant.id == MerchantDiscoveryProfile.merchant_id,
            )
            .options(
                selectinload(Merchant.discovery_profile),
            )
            .where(
                MerchantDiscoveryProfile.discoverability_state
                == DiscoverabilityState.DISCOVERABLE.value,
                Merchant.status == "ACTIVE",
                Merchant.kill_switch_enabled == False,  # noqa: E712
            )
            .order_by(Merchant.slug.asc())
        )
        if intent.cursor is not None:
            stmt = stmt.where(Merchant.slug > intent.cursor)
        merchants = (await session.execute(stmt.limit(intent.page_size + 1))).scalars().all()
        has_more_candidates = len(merchants) > intent.page_size
        merchants = merchants[: intent.page_size]
        next_cursor = merchants[-1].slug if has_more_candidates and merchants else None

        query_text = (intent.query or "").strip().lower()
        cat_filter = (intent.category or "").strip().lower()
        req_caps = set(intent.required_capabilities)

        matched_results: list[DiscoveryMatchResult] = []

        for m in merchants:
            # Currency eligibility filter
            if m.currency.upper() != intent.currency.upper():
                continue

            # Capability compatibility filter
            supported_caps = set(CapabilityRegistry._CAPABILITIES.keys())
            if req_caps and not req_caps.issubset(supported_caps):
                continue

            profile = m.discovery_profile
            if profile is None:
                continue

            # Delivery compatibility filter (if intent specified delivery_region)
            merchant_regions = [str(r).strip().upper() for r in profile.delivery_regions]
            if intent.delivery_region:
                intent_reg = intent.delivery_region.strip().upper()
                region_matched = (
                    intent_reg in merchant_regions
                    or "ALL" in merchant_regions
                    or (
                        "INDIA" in merchant_regions
                        and (
                            intent_reg == "INDIA"
                            or intent_reg.startswith("IN-")
                            or intent_reg.startswith("IN/")
                        )
                    )
                )
                if not region_matched:
                    continue

            # Inspect a SQL-bounded sample already matching the buyer's known
            # product, stock, attribute, and budget constraints.
            matching_products: list[PublicProductSummary] = []
            has_attribute_match = False
            has_category_match = False
            is_within_budget = False

            candidate_products = await cls._load_matching_products(
                session,
                m.id,
                intent,
                query_text=query_text,
                merchant_tags=[str(tag) for tag in profile.custom_tags],
            )
            for p in candidate_products:
                p_cat = (p.category or "").lower()

                if cat_filter and cat_filter in p_cat:
                    has_category_match = True

                active_variants = [v for v in p.variants if v.is_active]
                purchasable_variants = [
                    v for v in active_variants if cls._variant_can_fulfill(v, intent.quantity)
                ]
                if not purchasable_variants:
                    continue

                # Attributes check (e.g. size, color)
                if intent.required_attributes:
                    attrs_satisfied = False
                    for v in purchasable_variants:
                        v_title = (v.title or "").lower()
                        v_sku = (v.sku or "").lower()
                        req_vals = [
                            str(val).strip().lower()
                            for val in intent.required_attributes.values()
                            if str(val).strip()
                        ]
                        if req_vals and all(val in v_title or val in v_sku for val in req_vals):
                            attrs_satisfied = True
                            break
                    if not attrs_satisfied:
                        continue
                    has_attribute_match = True

                var_prices = [
                    cls._effective_variant_price(p, variant) for variant in purchasable_variants
                ]
                min_var_p: int = min(var_prices)
                max_var_p: int = max(var_prices)

                is_within_budget = True

                matching_products.append(
                    PublicProductSummary(
                        product_sku=p.sku,
                        title=p.title,
                        category=p.category,
                        description=p.description,
                        price_range_paise={"min": min_var_p, "max": max_var_p},
                        in_stock=True,
                        attributes={"variants_count": len(purchasable_variants)},
                    )
                )
                if len(matching_products) >= _MAX_PUBLIC_PRODUCTS_PER_MERCHANT:
                    break

            # A returned merchant must always have at least one product that can
            # fulfill the intent. Otherwise an unfiltered request could surface an
            # unavailable merchant with transaction-oriented next actions.
            if not matching_products:
                continue

            # Build public profile
            pub_prof = await cls.build_public_profile(session, m.id, loaded_merchant=m)
            if pub_prof is None:
                continue

            # Deterministic Reason Codes & Score
            reason_codes: list[str] = []
            score = 0

            if has_attribute_match:
                reason_codes.append("MATCH_EXACT_ATTRIBUTES")
                score += 40
            cat_matched = has_category_match or bool(
                cat_filter and cat_filter in (pub_prof.category or "").lower()
            )
            if cat_matched:
                reason_codes.append("MATCH_CATEGORY")
                score += 20
            if is_within_budget or intent.maximum_budget_paise is None:
                reason_codes.append("WITHIN_BUDGET")
                score += 20
            if pub_prof.inventory_summary == "AVAILABLE":
                reason_codes.append("IN_STOCK")
                score += 15
            if intent.delivery_region and merchant_regions:
                reason_codes.append("DELIVERY_SUPPORTED")
                score += 10
            if req_caps:
                reason_codes.append("CAPABILITY_MATCH")
                score += 10
            if pub_prof.negotiation_supported and intent.negotiation_preference in (
                "WANTED",
                "INDIFFERENT",
                None,
            ):
                reason_codes.append("NEGOTIATION_SUPPORTED")
                score += 5
            if pub_prof.description and pub_prof.discovery_tags:
                reason_codes.append("PROFILE_COMPLETE")
                score += 5

            matched_results.append(
                DiscoveryMatchResult(
                    merchant=pub_prof,
                    matching_products=matching_products,
                    rank=0,  # Will be assigned after sort
                    score=score,
                    reason_codes=reason_codes,
                    next_actions=["START_BUYER_SESSION", "GET_PRODUCT", "GET_QUOTE"],
                )
            )

            # Record telemetry replay-safely
            target_pid = next(
                (
                    p.id
                    for p in candidate_products
                    if matching_products and p.sku == matching_products[0].product_sku
                ),
                None,
            )
            await cls.record_telemetry(
                session=session,
                merchant_id=m.id,
                event_type=DiscoveryTelemetryEventType.SEARCH_RECEIVED.value,
                correlation_id=corr_id,
                sanitized_query=query_text[:255] if query_text else None,
                product_id=target_pid,
            )
            await cls.record_telemetry(
                session=session,
                merchant_id=m.id,
                event_type=DiscoveryTelemetryEventType.MERCHANT_RETURNED.value,
                correlation_id=corr_id,
                sanitized_query=query_text[:255] if query_text else None,
                product_id=target_pid,
            )

        # Deterministic sort: higher score first, lower min_price second, slug third
        matched_results.sort(
            key=lambda res: (
                -res.score,
                res.merchant.price_range_paise.get("min", 0),
                res.merchant.slug,
            )
        )

        # Assign deterministic 1-indexed ranks
        for idx, item in enumerate(matched_results, start=1):
            item.rank = idx

        return DiscoverySearchResponse(
            results=matched_results,
            total_matches=len(matched_results),
            correlation_id=corr_id,
            discovery_schema_version="1.0.0",
            next_cursor=next_cursor,
            next_canonical_action="START_BUYER_SESSION",
        )

    @classmethod
    async def record_telemetry(
        cls,
        session: AsyncSession,
        merchant_id: uuid.UUID,
        event_type: str,
        correlation_id: str,
        sanitized_query: str | None = None,
        product_id: uuid.UUID | None = None,
    ) -> None:
        """Records tenant-scoped discovery telemetry idempotently.

        Uses unique constraint (merchant_id, event_type, correlation_id) to ensure
        replays do not duplicate telemetry entries.
        """
        dialect_name = session.bind.dialect.name if session.bind is not None else ""
        values = {
            "merchant_id": merchant_id,
            "event_type": event_type,
            "correlation_id": correlation_id,
            "sanitized_query": sanitized_query,
            "product_id": product_id,
        }
        conflict_columns = ["merchant_id", "event_type", "correlation_id"]

        statement: Any
        if dialect_name == "postgresql":
            statement = postgresql_insert(MerchantDiscoveryTelemetry).values(values)
        elif dialect_name == "sqlite":
            statement = sqlite_insert(MerchantDiscoveryTelemetry).values(values)
        else:
            raise RuntimeError("Discovery telemetry requires a PostgreSQL-compatible database.")

        # One database statement makes concurrent requests carrying the same
        # client correlation ID replay-safe without poisoning the transaction.
        await session.execute(statement.on_conflict_do_nothing(index_elements=conflict_columns))

    @classmethod
    async def get_discoverability_status(
        cls,
        session: AsyncSession,
        merchant_id: uuid.UUID,
    ) -> DiscoverabilityStatusResponse:
        """Returns the merchant control plane discoverability status and metrics."""
        profile = await cls.get_or_create_profile(session, merchant_id)
        pub_profile = await cls.build_public_profile(session, merchant_id)

        # Query telemetry metrics
        stmt_counts = (
            select(
                MerchantDiscoveryTelemetry.event_type,
                func.count(MerchantDiscoveryTelemetry.id),
            )
            .where(MerchantDiscoveryTelemetry.merchant_id == merchant_id)
            .group_by(MerchantDiscoveryTelemetry.event_type)
        )
        rows = (await session.execute(stmt_counts)).all()
        metrics: dict[str, int] = {
            DiscoveryTelemetryEventType.SEARCH_RECEIVED.value: 0,
            DiscoveryTelemetryEventType.MERCHANT_RETURNED.value: 0,
            DiscoveryTelemetryEventType.MERCHANT_SELECTED.value: 0,
            DiscoveryTelemetryEventType.PRODUCT_SELECTED.value: 0,
            DiscoveryTelemetryEventType.HANDOFF_INITIATED.value: 0,
        }
        for event_type, count in rows:
            metrics[event_type] = int(count)

        caps = cls.get_public_capability_graph()

        return DiscoverabilityStatusResponse(
            discoverability_state=profile.discoverability_state,
            profile=pub_profile,
            metrics=metrics,
            public_capability_graph=caps,
            supported_protocols=["ACP/1.0", "REST/1.0"],
            profile_version=profile.profile_version,
            updated_at=profile.last_refreshed_at.isoformat(),
        )
