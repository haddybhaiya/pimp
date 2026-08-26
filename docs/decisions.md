# Architectural Decision Records (ADRs): Agent-Ready Merchant

> This document records the key architectural and design decisions, their rationale, context, and consequences.

---

## ADR-001: Separation of Intelligence from Authority

- **Status:** ACCEPTED
- **Context:** Large Language Models (LLMs) are probabilistic, susceptible to prompt injection, hallucination, and adversarial jailbreaks. In a financial/commerce system, trusting model output directly with database mutations or payment execution exposes merchants to severe financial loss.
- **Decision:** Establish a strict architectural boundary. The LLM acts purely as an untrusted proposal engine emitting structured Pydantic intent objects. A deterministic policy engine and action gateway enforce mathematical floors, state preconditions, capabilities, and idempotency before executing any side effect.
- **Consequences:**
  - *Positive:* Prevents unauthorized discounts, floor breaches, and financial loss even under complete LLM compromise.
  - *Negative:* Slightly higher architectural complexity and latency due to multi-stage validation pipeline.

---

## ADR-002: Integer Paise Currency Representation

- **Status:** ACCEPTED
- **Context:** Floating-point arithmetic introduces IEEE-754 precision inaccuracies (e.g. `0.1 + 0.2 != 0.3`), which can accumulate or cause discrepancies between internal ledgers and Razorpay payment orders.
- **Decision:** Represent all monetary values across database schemas, APIs, and business logic as 64-bit non-negative integers representing paise (1 INR = 100 paise).
- **Consequences:**
  - *Positive:* Zero rounding errors; 1:1 compatibility with Razorpay API amounts.
  - *Negative:* Display layers must format paise to INR strings explicitly.

---

## ADR-003: Modular Monolith Architecture for MVP

- **Status:** ACCEPTED
- **Context:** Distributing Phase 1 into microservices introduces distributed transaction problems, network overhead, and deployment complexity that obscure core safety guarantees.
- **Decision:** Build Phase 1 as a clean modular monolith using FastAPI, Python 3.11+, and PostgreSQL.
- **Consequences:**
  - *Positive:* Strong ACID guarantees, simple debugging, single deployment artifact, rapid iteration.
  - *Negative:* Must maintain clear internal package boundaries to prevent tight coupling.

---

## ADR-004: Server-Authoritative Webhook & Reconciliation Engine

- **Status:** ACCEPTED
- **Context:** Client-side redirect callbacks from payment gateways can be intercepted, spoofed, or blocked by ad-blockers / network drops.
- **Decision:** All payment state transitions to `PAID` require a cryptographically verified HMAC SHA-256 webhook from Razorpay (`X-Razorpay-Signature`) or an out-of-band server-to-server fetch (`GET /v1/orders/{id}/payments`).
- **Consequences:**
  - *Positive:* Completely eliminates client-side payment forgery attacks.
  - *Negative:* Requires background polling worker for edge cases where webhooks fail to deliver.

---

## ADR-005: Optimistic Concurrency Control for Inventory & Quotes

- **Status:** ACCEPTED
- **Context:** Multiple buyer agents interacting concurrently could attempt to purchase the same limited stock item simultaneously.
- **Decision:** Use PostgreSQL row versioning (`version BIGINT`) and `SELECT ... FOR UPDATE` row-level locks during checkout and stock reservation.
- **Consequences:**
  - *Positive:* Prevents overselling and race conditions without heavy distributed locks.
  - *Negative:* Contested transactions must handle optimistic lock failure gracefully and report stock depletion.

---

## ADR-006: CI Tooling & Engineering Quality Standards

- **Status:** ACCEPTED
- **Context:** Ensuring deterministic, repeatable code quality, type safety, security scanning, and test validation across all contributions in a safety-critical commerce repository.
- **Decision:** Adopt `Ruff` (linting + formatting with bandit security rules), `Mypy` (strict static typing), `Pytest` (with coverage and async support), and automated git secret scanning in GitHub Actions CI across Python 3.11 and 3.12 matrices.
- **Consequences:**
  - *Positive:* Fast, deterministic feedback loop; prevents syntax regressions, type mismatches, and secret leakage before merging.
  - *Negative:* Strict static typing overhead during rapid development.

---

## ADR-007: Canonical Commerce Gateway & Authoritative Merchant AI Representation

- **Status:** ACCEPTED
- **Context:** Arbitrary AI buyers and external protocol adapters require a standardized, deterministic boundary to interact with merchant commerce capabilities without bypassing security policies, financial floor price guards, state machines, inventory locks, or audit ledgers.
- **Decision:** Implement `CanonicalCommerceGateway` exposing 8 canonical capabilities (`discover_products`, `get_product`, `check_inventory`, `get_quote`, `calculate_shipping`, `create_order`, `request_checkout`, `get_payment_status`) with strict Pydantic schemas (`extra="forbid"`), state-oriented response envelopes (`GatewayResponseEnvelope[T]`), and an immutable `CapabilityRegistry`. Construct `MerchantAIRepresentation` derived purely from authoritative server state with SHA-256 policy hashing, ensuring clients and LLMs cannot alter or spoof merchant capabilities.
- **Consequences:**
  - *Positive:* Completely eliminates bypass paths around authorization, policy, inventory, and payment; provides clear state machine guidance (`next_action`, `allowed_actions`) to AI buyers; ensures strict multi-tenant isolation.
  - *Negative:* Requires strict schema adherence and rejects undeclared fields fail-closed.

---

## ADR-008: External AI Buyer Flow & Autonomous Lifecycle Execution

- **Status:** ACCEPTED
- **Context:** External autonomous AI buyers require a structured, end-to-end commerce client to complete the full commerce lifecycle (`DISCOVERED` -> `PRODUCT_SELECTED` -> `QUOTED` -> `NEGOTIATION_PENDING` -> `OFFER_ACCEPTED` -> `ORDER_CREATED` -> `PAYMENT_PENDING` -> `PAYMENT_SUCCEEDED` -> `COMPLETED`) while preserving the critical invariant: `AI buyer -> Gateway -> deterministic authority -> domain service -> Razorpay`.
- **Decision:** Implement `AIBuyerClient` and structured buyer schemas in `src/agent_ready_merchant/buyer/` communicating strictly through `CanonicalCommerceGateway`. Direct database mutations, direct Razorpay API mutations, and unrestricted financial operations are completely prohibited. All quote negotiations execute through `DeterministicPolicyEngine`, quote state advances through version-checked `PriceQuoteStateMachine`, inventory is atomically reserved during order creation, and payment settlement verifies cryptographic HMAC signatures. Explicit response and failure states (`INVENTORY_CHANGED`, `POLICY_REJECTED`, `QUOTE_EXPIRED`, etc.) provide deterministic recovery paths for autonomous buyers.
- **Consequences:**
  - *Positive:* Full autonomous commerce lifecycle support with zero bypass around authorization, inventory reservations, policy evaluation, or audit ledgers. Proven resilient against prompt injection, quote tampering, cross-tenant leaks, and concurrency races.
  - *Negative:* Autonomous buyers must strictly handle state transitions and retryable failure envelopes.

---

## ADR-009: Protocol Boundary, Adapter Interface & Production Hardening

- **Status:** ACCEPTED
- **Context:** External AI agent frameworks require a standardized protocol interface to consume merchant capabilities while insulating the core domain from protocol-specific churn and protecting against operational threats (replays, burst traffic, unbounded payloads, execution timeouts, secret leaks, and blind financial retries).
- **Decision:**
  1. Build replaceable `BaseProtocolAdapter` and concrete `AgentCommerceProtocolAdapter` (ACP) implementing `ProtocolRequestMessage` $\leftrightarrow$ `ProtocolResponseMessage` bidirectional translation without protocol bypass.
  2. Implement `AgentProtocolClient` allowing autonomous agent systems to consume capabilities exclusively via protocol wire messages with safe retry policies (retrying safe reads and idempotent mutations while prohibiting blind retries on financial mutations).
  3. Enforce contract versioning (`COMMERCE_PROTOCOL_VERSION = "2026-03-01"`), `request_id` end-to-end trace propagation, thread-safe `IdempotencyManager` deduplication, sliding-window `GatewayRateLimiter`, 64 KB `BoundedPayloadGuard`, execution timeout boundaries, structured observability, and safe error sanitization (`GatewayErrorCode.INTERNAL_GATEWAY_ERROR`) preventing database schema and secret leakage.
- **Consequences:**
  - *Positive:* Protocol-agnostic core domain; external protocol adapters are swappable without modifying canonical services; deterministic machine-readable errors; hardened against concurrent mutation races, replay attacks, and denial-of-service bursts.
  - *Negative:* Additional translation hop between external wire messages and canonical gateway requests.

---

## ADR-010: Authoritative Razorpay Payment Boundary & Invariant Hardening

- **Status:** ACCEPTED
- **Context:** Financial settlement must be protected against malicious tampering, currency/amount mismatches, cross-order spoofing, out-of-order/delayed webhooks, network timeouts, and state regression attacks. Client-side callbacks can never be trusted to dictate financial state.
- **Decision:**
  1. Enforce strict server-authoritative amount AND currency verification (`CurrencyMismatchFraudError`, `AmountMismatchFraudError`) with immediate tamper-evident audit logging (`PAYMENT_CURRENCY_FRAUD_DETECTED`, `PAYMENT_AMOUNT_FRAUD_DETECTED`).
  2. Enforce strict payment-to-order binding (`OrderMismatchError`) validating that webhook payload order references match authoritative DB orders prior to state transitions.
  3. Enforce multi-entity transaction binding (`validate_transaction_binding` raising `TransactionBindingError`) guaranteeing that append-only `TransactionRecord` ledger entries bind strictly to `CAPTURED` attempts matching the exact order amount, order ID, and merchant ID.
  4. Normalize Razorpay client errors into typed subclasses (`RazorpayBadRequestError`, `RazorpayNotFoundError`, `RazorpayRateLimitError`, `RazorpayServerError`, `RazorpayTimeoutError`, `RazorpayNetworkError`) with explicit `is_retryable` semantics.
  5. Prevent state regression: enforce terminal states and ignore stale/delayed failure webhooks on already settled orders (`STATE_REGRESSION_IGNORED`).
- **Consequences:**
  - *Positive:* Mathematically guarantees zero false payment success, prevents ledger pollution, eliminates race conditions between webhook and reconciliation, and ensures strict adherence to INV-FIN-01 through INV-FIN-05 and INV-STA-01 through INV-STA-05.
  - *Negative:* Requires strict error hierarchy and validation overhead on all payment-related endpoints.




