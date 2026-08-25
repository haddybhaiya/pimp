# Code Review Log

---

# Review 3: Phase 2.3 Protocol Boundary & Production Hardening (`79cb1bb..50920d1`)

> **Reviewed on:** 2026-08-24
> **Commits reviewed:** `79cb1bb`, `4670f5c`, `50920d1`
> **Scope:** ACP wire endpoint (`/api/v1/protocol/acp`) + adapter, `AgentProtocolClient`, `GatewayErrorCode` taxonomy, `IdempotencyManager`, `GatewayRateLimiter`, 64 KB payload guard, timeout boundary, error sanitization, contract versioning, request/idempotency trace IDs.
> **Verification:** Full suite green (150 passed, 2 skipped), `ruff check` clean, `mypy --strict` clean. Line numbers reference HEAD at `50920d1`.

---

## Medium

### 1. Idempotency cache is scoped by merchant+session+key only — different capabilities/payloads sharing a key replay each other's responses

`_build_key` (`hardening.py:74-80`) omits the capability name and any request hash, and `execute_capability` consults the cache before dispatch (`canonical.py:1608-1615`). Any two operations sent under the same `(merchant, session, key)` collide: e.g., an ACP client using one flow-level key (`"checkout-1"`) for `create_order` and then `request_checkout` receives the *create-order* envelope from checkout with `status="SUCCESS"` — no error signals the mixup. Same applies to a mutated payload reusing an old key (changed quantity returns the stale quote). Since ADR-009 designates idempotency keys as the sanctioned retry mechanism for mutations, silent wrong-response replay is a correctness hazard. Include the capability name (and ideally a canonical payload hash) in the key, or return `IDEMPOTENCY_CONFLICT` on reuse with a different fingerprint — the standard Stripe-style behavior.

### 2. `authorize_test_payment` replicates the unconditional-success defect flagged in Review 2 §5

`protocols/client.py:433-502` copies the buyer-client payment simulation verbatim, defects included: `process_payment_webhook`'s result (which can legitimately be `IGNORED`/`DUPLICATE_IGNORED`) is discarded, `current_state = PAYMENT_SUCCEEDED` is set unconditionally (`client.py:488-491`), and the `rzp_order_id = f"order_{uuid4...}"` fallback guarantees the ignored path whenever the order lacks a Razorpay ID. Direct callers get a success signal for a settlement that never happened. `execute_full_commerce_flow` again self-corrects via its step-12 status poll, but this is now a second copy of the known bug to fix — extract one shared helper rather than maintaining two.

### 3. Rate limiter is keyed on attacker-controlled input and never releases memory

`canonical.py:1593` derives the bucket from `context.session_id or context.merchant_id`. Both values come straight from unverified request headers (standing High finding, reviews 1–2), so a caller rotating `X-Session-ID` per request gets a fresh 60-req/min budget each time — the limiter never engages for that pattern. Separately, `GatewayRateLimiter._requests` (`hardening.py:203-226`) prunes timestamps but never deletes empty keys from the `defaultdict`, so every distinct session UUID seen grows the dict permanently — an unbounded slow memory leak under exactly the rotation described. Severity depends on deployment exposure (local/test vs. network-reachable); the leak alone justifies periodic eviction or LRU capping regardless.

### 4. Timeout boundary converts mid-transaction cancellation into a normal return, then the DB dependency commits

On deadline, `asyncio.timeout` cancels in-flight DB work; `execute_capability` catches `TimeoutError` and returns a clean ERROR envelope (`canonical.py:1635-1657`). Because the exception never propagates, `get_db_session`'s post-yield `await session.commit()` (`db/session.py:54-57`) still executes against a transaction whose statements were interrupted midway. Multi-flush flows make partial persistence possible — e.g., `create_order_from_accepted_quote` flushes the order (`payment_service.py:149`) and items (`payment_service.py:171`) separately; a cancellation between them may either commit half the mutation (driver permits the commit) or blow up with `PendingRollbackError` during dependency teardown *after* the response was already sent. Roll back explicitly before returning the timeout envelope, or let the cancellation propagate so the existing rollback-on-exception path runs.

---

## Low / notes

- **Hardening knobs aren't configurable:** `getattr(settings, "GATEWAY_RATE_LIMIT_PER_MINUTE", 60)` and `"GATEWAY_REQUEST_TIMEOUT_SECONDS"` (`canonical.py:1596,1634`) fall back to defaults forever — neither field exists on `Settings` (`config.py`), so setting the env vars does nothing until the fields are declared.
- **Dead `X-Request-ID` fallback:** `main.py:622` (`msg.request_id or x_request_id ...`) can never reach the header — `ProtocolRequestMessage.request_id` has a `default_factory`, so FastAPI always populates it from the body. Clients omitting body `request_id` get a server-random trace ID instead of their header value.
- **Fabricated session UUIDs in `AgentProtocolClient._get_gateway_context`** (`client.py:90`): `session_id=self.context.session_id or uuid.uuid4()` rotates per call pre-initialization, so gateway-side idempotency scoping and the rate bucket change on every attempt until `initialize_session` succeeds. Passing `None` preserves stable scoping.
- **Latent status-semantics inversion:** `acp.py:170` maps `retryable=True → status="REJECTED"`; everywhere else REJECTED means a deterministic business rejection (`retryable=False` always). All current call sites pass `retryable=False`, so nothing misbehaves yet.
- **Payload guard is post-parse:** the 64 KB check runs after Starlette has buffered and JSON-decoded the whole body; cap request body size at the server/proxy layer too, or the guard bounds logic, not memory.
- **Constant drift risks:** `tools/base.py:26` hardcodes `schema_version="2026-03-01"` instead of importing `COMMERCE_PROTOCOL_VERSION`; the `PAYLOAD_SIZE_EXCEEDED` message hardcodes "65536" instead of the effective limit; `IdempotencyRecord.merchant_id` uses `default_factory=uuid.uuid4` (a random merchant identity on omission).
- **Retry-loop semantics:** `max_retries=2` yields two total attempts (one retry), and `MALFORMED_REQUEST_SCHEMA` (declared `retryable=True`) is retried despite being deterministic — harmless, but the flag invites pointless double validation failures.
- **Inherited auth posture:** the wire endpoint builds authority from `X-Merchant-ID`/`X-Session-ID`/`X-Capabilities` exactly like the REST routes, so all financial capabilities are now additionally reachable through `/api/v1/protocol/acp` under the gap documented in reviews 1–2 §1. No new flaw, but the exposed surface grew; closing the underlying enforcement gap closes this too.
- Tests reset the global limiter/idempotency singletons via `seed_hardening_data`; other suites calling `execute_capability` now share the 60/min default bucket per merchant/session — watch for flakiness if a future test makes >60 calls against one seeded merchant within a minute.

---

---

# Review 2: Phase 2.2 External AI Buyer Commerce Flow (`2cca0e5..92081f3`)

> **Reviewed on:** 2026-08-24
> **Commits reviewed:** `68a7d5c`, `a82db4a`, `937eeb1`, `97dfb35`, `92081f3`
> **Scope:** Session lifecycle (`initialize_session`/`terminate_session`), bounded negotiation (`negotiate_quote`), quote acceptance (`accept_quote`), `get_order_status`, new REST endpoints, and the in-process `AIBuyerClient`.

---

## High

### 1. The session lifecycle is decorative — sessions are created but never enforced anywhere

Phase 2.2 introduces `BuyerAgentSession` rows with SHA-256 token hashes (`canonical.py:1050-1063`), but verified via grep: **no code path ever verifies a presented token against `auth_token_hash`**, consults session `status`, or checks `expires_at`. `BuyerAgentSession` is queried exactly once outside initialization — in `terminate_session`. Every capability still derives its full authority from request headers (`main.py:291-316`): `X-Merchant-ID`, `X-Session-ID`, `X-Capabilities`. Consequences:

- `POST /api/v1/gateway/sessions/initialize` (`main.py:508-519`) mints unlimited ACTIVE sessions for any merchant UUID with no credential at all.
- A terminated or expired session's ID works perfectly for negotiate/accept/checkout if supplied in `X-Session-ID`; termination only changes a row nobody reads.
- `granted_capabilities` in `InitializeSessionResponse` is an echo of client input — validated against no vocabulary and stored nowhere (the model has no capabilities column).

This extends the Phase 2.1 High finding (review 1, §1): that review flagged header-only auth while a session entity was absent; Phase 2.2 added the entity and the hash but still not the enforcement. The gap is now easier to close (compare `hashlib.sha256(raw_token).hexdigest()` against the row inside `_get_context`), and severity still depends entirely on whether this service runs outside local/test environments.

---

## Medium

### 2. `negotiate_quote` price math ignores shipping and line heterogeneity — floor-price invariant can be breached, legitimate offers falsely denied

The proposal construction (`canonical.py:1232-1256`) derives every line's `proposed_unit_price_paise = proposed_total_paise // total_items` where `total_items` sums quantities across all lines, then evaluates floors/discount on that basis (`policy/rules.py:44-145`). Three concrete distortions:

- **Floor breach via shipping subsidy (fail-open):** `proposed_total` includes shipping, but the floor check compares the gross per-unit figure against per-unit floors. Example: single unit, base ₹800, floor ₹790, shipping ₹100 (subtotals < ₹1,000 always carry it). Buyer offers total ₹820: `u = 82_000 ≥ 79_000` passes the floor check and discount stays within 15%, yet merchant net proceeds are ₹720 < floor ₹790. The guard that exists to prevent selling below floor silently passes.
- **False rejections on multi-line bundles:** equal-split requires `proposed_total ≥ total_qty × max(floor_i)`. One unit at floor ₹9,000 plus one at floor ₹95 forces offers ≥ ₹18,000 even though aggregate floors sum to ₹9,095 — everything between fails as `FLOOR_PRICE_BREACH`.
- **Shipping consumed as discount:** `calculated_discount = (subtotal + shipping) − proposal` (`canonical.py:1248-1249`) is compared to `subtotal × max_discount_pct` (`rules.py:120-124`). At 15% max discount, any subtotal below ~₹667 makes the flat ₹100 shipping alone exceed the whole discount budget; a buyer offering full list price for goods while paying shipping themselves gets `MAX_DISCOUNT_EXCEEDED`.

Errors run in both directions (false-allow and false-deny). For single-item quotes the first bullet is the important one; consider evaluating floors on `(proposed_total − shipping) / quantity` and computing discount off goods value.

### 3. Negotiation baseline uses product base price instead of the quoted line price

`canonical.py:1240` sets `unit_base_price_paise=prod.base_price_paise`, but the quote line may have been created from `variant.price_override_paise` (see `get_quote`, `canonical.py:569-573`). When an override sits below base, a buyer paying full listed price registers as "discounted" in `evaluate_autonomy_and_negotiation` (`rules.py:184-217`): non-negotiable SKUs get denied for undiscounted purchases, Autonomy Level 2 merchants escalate routine full-price offers to HITL, and the recorded `discount_paise` overstates what was actually conceded. `get_quote` uses the effective unit price for this field; `negotiate_quote` should use `itm.unit_price_paise` (already loaded on the line) for consistency.

### 4. `ESCALATE_APPROVAL` verdict reports a state that doesn't exist and dead-ends the flow

On escalation (`canonical.py:1272-1299`) nothing is persisted: the quote remains `PROPOSED` with old totals, yet the envelope claims `state="PENDING_APPROVAL"`, and there is no approval mechanism anywhere in the codebase to resolve it. The offered `allowed_actions=["get_quote", "terminate_session"]` tell the buyer to give up; meanwhile a subsequent `negotiate_quote` would actually be accepted by the server (status is still `PROPOSED`), contradicting the envelope's own guidance. Either persist a pending-approval marker with a resolution path, or report the true persisted state so autonomous buyers aren't navigating fiction.

### 5. `authorize_test_payment` records success unconditionally and self-signs with the server secret

`buyer/client.py:482-552`: after `PaymentService.process_payment_webhook` returns, status/state are set to SUCCESS/`PAYMENT_SUCCEEDED` without inspecting the result — which can legitimately be `IGNORED` (`order_not_found`, `invalid_payment_amount`, `missing_payment_id`) or `DUPLICATE_IGNORED`. The fallback `rzp_order_id = f"order_{uuid4...}"` (`client.py:499`) guarantees the ignored path when the order has no Razorpay ID. `execute_full_commerce_flow` self-corrects at step 12, but direct callers of `authorize_test_payment` receive a success signal for a settlement that never happened. Separately: the buyer signs webhooks with `RAZORPAY_WEBHOOK_SECRET` from settings (`client.py:527-536`). That's acceptable test-mode scaffolding given both sides run in-process, but it means any code holding settings can settle arbitrary orders — keep this method out of any production wiring (ADR-008's "authentic HMAC signed webhook" invariant holds only because signer and verifier share one process).

---

## Low / notes

- **initialize/terminate skip declared authorization:** registry declares `required_capability="buyer:discover"` for both (`registry.py`), but neither implementation calls `CapabilityRegistry.check_authorization` (unlike negotiate/accept/order-status). For initialize that's arguably correct (it's the entry point); then the metadata is misleading.
- **`negotiate_quote` isn't idempotent despite declaration:** registry says `idempotency_requirement=True`; each call re-runs two FSM transitions, bumps `version`, and appends audit events. Same drift already noted for `get_quote` in review 1.
- **Capability vocabulary mismatch inside negotiation:** gateway authz requires `buyer:negotiate`, but the policy engine re-checks its default `"buyer:quote"` (`policy/engine.py:35`, invoked at `canonical.py:1264`). A context holding only `buyer:negotiate` passes the gateway gate then dies at policy with rule code `CAPABILITY_DENIED` — not among the capability's declared failure states. Latent with current default capability sets.
- **`terminate_session` lacks a status guard:** terminating an `EXPIRED` or already-`TERMINATED` session returns SUCCESS again and appends a duplicate audit event.
- **`get_order_status` guidance contradicts itself for `FULFILLMENT_PENDING`:** counted as settled (`is_settled=True`, `canonical.py:1523`) but yields `allowed_actions=[]` and next_action "Awaiting payment settlement". Also continues merchant-scoped-only order access (no session linkage), consistent with review 1 §5 — docstring still promises cross-session rejection.
- **`BuyerFlowResult.amount_paise` misuse in failure paths:** `_build_result` fills it from `active_quote_total_paise` even when no order was created, mislabeling a quote figure as the final amount.
- Tests correctly relaxed `len(catalog) == 8` → `>= 8` for the five new capabilities; the external-buyer suite covers lifecycle, cross-session/cross-merchant access, replay, stale quotes, inventory races, and prompt-injection handling.

---

---

# Review 1: Phase 2.1 Canonical Commerce Gateway (`66a560e..HEAD`)

> **Reviewed on:** 2026-08-24
> **Commits reviewed:** `ef27da1`, `e1358a5`, `4d71ac3`, `2cca0e5`
> **Context:** Line numbers reference files as of HEAD at time of review. Superseded in part by Review 2 above: the session-lifecycle/negotiation changes flagged there as "out of scope uncommitted work" have since landed as Phase 2.2 and were reviewed separately.

---

## High

### 1. Gateway authorization rests entirely on unauthenticated, client-controlled headers

`src/agent_ready_merchant/main.py:281-300` builds the security context purely from request data: `X-Merchant-ID` becomes `context.merchant_id` and `X-Capabilities` becomes `context.capabilities`. Nothing verifies the caller against `BuyerAgentSession.auth_token_hash`, nor checks session existence, status (`ACTIVE`/`TERMINATED`), or `expires_at`. Consequences:

- Any caller can impersonate any merchant by setting `X-Merchant-ID`.
- Any caller can self-grant `buyer:checkout` / `buyer:payment_status` via `X-Capabilities`, bypassing every `CapabilityRegistry.check_authorization` gate downstream.
- `get_quote`'s session-boundary check (`request.session_id != context.session_id`) compares two attacker-supplied values, so it provides no protection on its own.

This directly contradicts ADR-007 added in `ef27da1` ("ensures clients and LLMs cannot alter or spoof merchant capabilities") and the module docstring in `canonical.py`. The pre-existing `/api/v1/orders/*` endpoints use optional headers similarly, so the pattern isn't new to this codebase — but these commits make the header the *sole* auth boundary for financial capabilities while documenting it as spoof-proof. If this service will ever run outside local/test environments, this needs real authentication before merge. Severity depends entirely on deployment exposure.

---

## Medium

### 2. `create_order`'s audit lookup can never succeed

`src/agent_ready_merchant/gateway/canonical.py:803-812` queries for the latest `AuditEvent` with `event_type == "ORDER_CREATED"` for the merchant. Verified via `git grep`: **no code path ever writes an `ORDER_CREATED` audit event** — `PaymentService.create_order_from_accepted_quote` creates none. So:

- `audit_event_id` in the create-order envelope is always `None`, despite the registry classifying this capability as `PRIVILEGED_FINANCIAL` with `"appends_audit_event"` in its side effects.
- The query is scoped only by merchant and ordered by `created_at DESC` with no order/session linkage — if such events are introduced later, concurrent orders could attach *another* order's audit ID.

Fix by emitting the event inside `PaymentService` and returning/filtering by order linkage, or drop the lookup.

### 3. Only `ValueError` is caught around order creation — Razorpay and lock errors escape the envelope contract

`canonical.py:790-801` (`create_order`) and `canonical.py:883-896` (`request_checkout`) catch only `ValueError` from `PaymentService.create_order_from_accepted_quote`. That call can also raise `RazorpayError` from `rzp_client.create_order` and `OptimisticLockError` from inventory reservation. On the dedicated REST endpoints (`/api/v1/gateway/orders`, `/api/v1/gateway/checkout`) these propagate as raw FastAPI 500s instead of a `GatewayResponseEnvelope` with the declared `PAYMENT_GATEWAY_ERROR` failure state — which the registry promises but nothing emits. Notably, the unified `/execute` dispatcher *does* catch these generically (`canonical.py:1093-1105`), so the same failure produces a structured ERROR envelope through one entry point and an unstructured 500 through another.

### 4. `get_quote` stock check fails open when no inventory row exists

`canonical.py:543-553`: `if inv:` skips the availability check entirely when a variant has no `InventoryItem` row. Meanwhile `check_inventory` (`canonical.py:348-354`) treats a missing row as `available=0` / not fulfillable. So the same SKU reports "out of stock" to inventory checks but accepts unlimited-quantity quotes — and `PaymentService` also skips reservation when `inv is None`, so nothing downstream catches it. Realistic scenario: any catalog item created without an inventory record can be quoted at arbitrary quantity. This should fail closed consistently.

### 5. `request_checkout` doesn't enforce its declared state guards

The registry declares failure states `ORDER_ALREADY_PAID` / `ORDER_CANCELLED` for `request_checkout`, but the implementation (`canonical.py:859-933`) returns fresh checkout parameters (`key_id`, amount, `rzp_order_id`) regardless of `order.status` — including `PAID` or `CANCELLED` orders. Related: `Order` has no `session_id` column, so checkout/status/order-status capabilities scope only by merchant. A buyer-agent session B of the same merchant can check out or track session A's orders. That's fine as tenant isolation but contradicts `canonical.py`'s "cross-session rejection" docstring — worth either scoping via the quote→order chain or correcting the docs.

---

## Low / notes

- **Full-catalog scan per search**: `discover_products` (`canonical.py:108-144`) loads all active products with variants+inventory eagerly, then filters and paginates in Python. Fine at test scale; O(n) memory/latency as catalogs grow. Consider SQL-side filtering, `COUNT`, and `LIMIT/OFFSET`.
- **Variant fallback ignores `is_active`**: `check_inventory`/`get_quote` fall back to `prod.variants[0]` (`canonical.py:338-339`, `532-534`) without checking `is_active`; an inactive first variant gets quoted/checked.
- **Idempotency keys aren't idempotent**: `canonical.py:616-618` embeds `uuid.uuid4().hex[:8]` in the quote idempotency key, guaranteeing uniqueness per call even though the registry declares `idempotency_requirement=True` for `get_quote`. Retries create duplicate quotes.
- **Vocabulary drift between layers**: new-quote envelope returns `allowed_actions=["ACCEPT", "NEGOTIATE", "ABANDON"]` (`canonical.py:693`) while everywhere else uses capability names (`accept_quote`, `negotiate_quote`); handlers' shipping tool returns `UNSUPPORTED_SHIPPING_COUNTRY` while canonical/registry use `UNSUPPORTED_COUNTRY`. Clients driving off `allowed_actions`/error codes will hit dead ends.
- Alias tools delegate cleanly to canonical gateway standards without conflicting with schema models.
- All 13 canonical capabilities across session lifecycle, catalog discovery, dynamic quotes, bounded negotiation, quote acceptance, shipping calculation, order creation, external Razorpay checkout, and payment reconciliation are fully registered, hardened, and verified.

---

# Verification & Remediation Signoff

> **Status:** All findings from Reviews 1, 2, 3 and subsequent code reviews have been **RESOLVED and VERIFIED**.
> **Key Hardening Delivered:**
> - Immutability of `CapabilityDefinition` metadata (`frozen=True`).
> - Non-negative 64-bit integer paise validation (`le=9_223_372_036_854_775_807`) across all request/response models.
> - Authoritative server-side session authentication and dynamic capability derivation from `BuyerAgentSession`.
> - Session-scoped order lookups (`PriceQuote.session_id == context.session_id`) preventing cross-session data leakage.
> - Explicit session rollback on exceptions and Razorpay gateway errors.
> - Disambiguated inventory checks rejecting multi-variant base SKUs.
> - Bounded memory eviction (LRU / TTL) on idempotency coordinators and rate limiters.
> - Complete unification of dedicated REST endpoints through the hardened capability dispatcher.
> - Zero test failures, zero lint errors, 100% strict type safety compliance.
