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

---

## ADR-011: Payment Reliability Hardening & Durable Transaction Safeguards

- **Status:** ACCEPTED
- **Context:** Webhooks, reconciliation, and payment order creation face network instability, timeouts, concurrent duplicate deliveries, replay attacks, and potential database transaction rollbacks vs external gateway side effects. A remote mutation succeeded at Razorpay followed by a local network timeout or application crash must never lead to blind duplicate order creation on retry. Concurrently delivered webhooks must not create duplicate ledger entries or race state transitions.
- **Decision:**
  1. **Durable Webhook Ingestion & Deduplication Table:** Persist all received webhooks in a canonical `ProcessedWebhook` database table with a unique constraint on `payload_hash` (`sha256(raw_body)`). Replayed or concurrent duplicates are atomically caught by the database unique constraint and safely ignored (`DUPLICATE_IGNORED`).
  2. **Timestamp Replay Bounds:** Webhook payloads must contain a timestamp within a valid 24-hour freshness window and not exceed 300 seconds in the future (preventing clock-skew / replay attacks). Violations immediately fail closed with `WebhookTimestampError`.
  3. **External Order Recovery & Retry Safety:** In `PaymentService.create_order_from_accepted_quote`, record durable intent breadcrumbs before external invocation. On retry following a timeout or crash, query Razorpay by deterministic receipt (`ord_<quote_id>`) via `RazorpayClient.fetch_order_by_receipt` before creating any remote order, binding to the existing open order without creating a duplicate.
  4. **Database-Enforced Ledger Uniqueness:** Enforce database unique constraint `uq_transaction_records_settlement_entry` on `(settlement_ref, entry_type)` in `TransactionRecord`. Duplicate credits for the same Razorpay payment are physically prohibited at the database level regardless of application concurrency.
  5. **Audit Hash Chain Concurrency Serialization:** Enforce row-level tenant locking (`SELECT ... FOR UPDATE` on `Merchant`) during `AuditEvent.create_event` in PostgreSQL to prevent parallel chain forking. Provide cryptographic verification via `AuditEvent.verify_chain`.
- **Consequences:**
  - *Positive:* Physically guarantees idempotency across network retries, protects against double-charging, ensures audit log integrity under heavy concurrent load, and provides fail-closed replay protection.
  - *Negative:* Requires additional database roundtrips for deduplication and receipt verification.

---

## ADR-012: Deterministic End-to-End Payment Verification & Transport Decoupling

- **Status:** ACCEPTED
- **Context:** Verifying the full canonical commerce lifecycle and edge cases (concurrency races, timeout-after-save, dropped webhooks, fraud detection, cross-tenant isolation) cannot rely on external third-party network services or live test credentials during automated CI runs. At the same time, mocking domain logic obscures real system integration and state-machine race bugs.
- **Decision:**
  1. Implement a protocol-faithful, stateful fake Razorpay transport (`DeterministicFakeRazorpayTransport`) using `httpx.AsyncBaseTransport`. This transport deterministically simulates the external Razorpay REST API (`/v1/orders`, `/v1/payments`, order lookup by receipt, payment capture, and cryptographic HMAC-SHA256 webhook signatures) as well as wire-level faults (connection timeouts, 500 internal errors, and remote-success-followed-by-timeout).
  2. Decouple `CanonicalCommerceGateway` to accept an injected `RazorpayClient`, ensuring the entire gateway end-to-end lifecycle runs against the exact domain models, policies, state machines, and database constraints without mocking away business logic.
  3. Build a comprehensive 17-scenario end-to-end verification suite covering the complete golden path and 16 deliberate edge/failure conditions.
- **Consequences:**
  - *Positive:* Fast, 100% deterministic, hermetic verification in CI without external network dependencies or live API key leaks. Completely preserves and exercises all internal domain models, state machines, database constraints, and cryptographic signatures.
  - *Negative:* The fake transport must be maintained in sync with any Razorpay API contract changes.

---

## ADR-013: Server-Authoritative Identity, Session Authentication & Multi-Tenant Capability Boundary Enforcement

- **Status:** ACCEPTED
- **Context:** External AI buyers, adapters, or adversaries may present forged credentials, forged `X-Capabilities` headers, expired session tokens, or attempt to probe/manipulate quotes and orders across tenant or session boundaries. Allowing client-supplied capability headers to elevate privileges or leaking resource existence through descriptive 403 errors enables credential forging and tenant snooping.
- **Decision:**
  1. **Constant-Time Cryptographic Token Verification:** Verify presented `auth_token` against database `BuyerAgentSession.auth_token_hash` using `hmac.compare_digest(sha256(auth_token), db_hash)` to protect against timing analysis attacks. Missing or invalid tokens fail closed with `AUTH_INVALID_CREDENTIAL`.
  2. **Mandatory Session Gate for Privileged/Stateful Capabilities:** Stateful and privileged financial operations (`get_quote`, `negotiate_quote`, `accept_quote`, `create_order`, `request_checkout`, `get_payment_status`, `get_order_status`, `terminate_session`) strictly require an active, non-expired session (`AUTH_SESSION_NOT_FOUND` / `AUTH_SESSION_EXPIRED`). Anonymous requests are bounded strictly to read capabilities (`discover_products`, `get_product`, `check_inventory`, `calculate_shipping`).
  3. **Server-Authoritative Capability Derivation:** Gateway capabilities are strictly bounded by `BuyerAgentSession.granted_capabilities` persisted in PostgreSQL. Client-supplied headers (e.g. `X-Capabilities: buyer:checkout`) can never self-grant or elevate permissions beyond the persisted grant (`INV-AGY-05`).
  4. **Strict Cross-Tenant & Cross-Session Isolation:** All entity queries (`PriceQuote`, `Order`, `InventoryItem`, `BuyerAgentSession`) strictly filter by `merchant_id` and `session_id`. Mismatches return uniform generic not-found errors (`QUOTE_NOT_FOUND`, `ORDER_NOT_FOUND`, `AUTH_SESSION_NOT_FOUND`) without revealing resource existence across merchant or session boundaries.
- **Consequences:**
  - *Positive:* Eliminates privilege escalation, cross-tenant resource snooping, replay attacks, and timing attacks. Preserves strict separation of intelligence and authority.
  - *Negative:* Session creation is required for all quoting and ordering workflows.

---

## ADR-014: Safety, Policy & Governance Kernel

- **Status:** ACCEPTED
- **Context:** Autonomous and AI-assisted commerce operations require deterministic guardrails, explainable reason codes, tamper-resistant governance records, Human-In-The-Loop (HITL) approval mechanics, and platform safety ceilings that cannot be bypassed by prompt injection, configuration tampering, or LLM non-determinism. Furthermore, audit event logs must maintain cryptographic integrity across time without leaking secrets or buyer PII.
- **Decision:**
  1. **Centralized Policy Decision Record & Deterministic Hashing:** Every consequential action evaluated by `DeterministicPolicyEngine` produces a `PolicyDecisionRecord` containing rule codes, verdicts (`ALLOW`, `DENY`, `ESCALATE_APPROVAL`), and a deterministic SHA-256 `policy_hash` derived from the normalized policy configuration (`compute_policy_hash()`). Future policy modifications do not invalidate historical audit records.
  2. **Platform Safety Boundaries & Governance Ceilings:** The engine enforces hard platform limits: max 20 items per quote (`MAX_ITEMS_PER_QUOTE_EXCEEDED`), absolute 50% discount ceiling (`GOVERNANCE_MAX_DISCOUNT_CEILING_EXCEEDED`), ₹1,00,000 (10,000,000 paise) single transaction limit (`GOVERNANCE_MAX_TRANSACTION_LIMIT_EXCEEDED`), and maximum 3 negotiation rounds per quote (`MAX_NEGOTIATION_ATTEMPTS_EXCEEDED`).
  3. **Human-In-The-Loop (HITL) Merchant Approval Model:** When a proposal exceeds merchant autonomy or discount limits, the system transitions to `ESCALATE_APPROVAL` and persists a `MerchantApproval` row. Resolving approvals via `resolve_approval` enforces strict merchant ownership, expiration deadlines, state machine validations, and optimistic locking to prevent race conditions.
  4. **Immutable Audit Linkage & Cryptographic Hash Verification:** Every domain mutation logs an immutable audit event recording `request_id -> session_id -> quote_id -> policy_decision_hash -> order_id`. `AuditEvent.verify_chain()` detects any back-channel database tampering.
  5. **Zero Secret & Masked PII Redaction:** Audit payloads pass through `sanitize_audit_payload()` to redact sensitive tokens/secrets (`auth_token`, `key_secret`, `password`, `card_number`) to `"[REDACTED_SECRET]"` and mask buyer emails (`a***r@example.com`), ensuring audit logs remain safe for forensic inspection.
  6. **Anti-Context Tampering Gate:** For non-admin callers, gateway capability execution overrides caller-supplied policy parameters by loading authoritative merchant rules directly from PostgreSQL (`PolicyRule`).
---

## ADR-015: Web Foundation, Server-Authoritative Merchant Authentication & SPA Shell

- **Status:** ACCEPTED
- **Context:** Delivering a production-ready merchant control plane requires a responsive, high-performance web surface, secure server-authoritative authentication for store owners, multi-step onboarding wizard, robust route guards, API client error normalization, and visual component tokens inspired by modern accessible UI systems without compromising domain invariants or exposing backend secrets to the browser.
- **Decision:**
  1. **Server-Authoritative Merchant Authentication & Tamper-Evident Tokens:** Built `MerchantAuthService` with HMAC SHA-256 signed bearer tokens encoding merchant ID, slug, and expiration timestamp. Unauthenticated access fails closed (401/403). Cross-tenant queries are strictly rejected.
  2. **Single-Page Application (SPA) Shell & Dual-Mode Root Surface:** Implemented a modern React 18 + TypeScript + Tailwind CSS application in `frontend/` compiled directly to `src/agent_ready_merchant/static/`. FastAPI serves the SPA bundle for browser requests (`Accept: text/html`) across public and protected client routes (`/`, `/login`, `/signup`, `/onboarding`, `/dashboard`, `/approvals`, `/catalog`, `/orders`, `/policies`, `/audit`) while preserving machine-readable JSON root descriptors for programmatic API clients.
  3. **Multi-Step Guided Merchant Onboarding Wizard:** Designed a 4-step interactive setup flow (Store Identity -> Razorpay Settlement Gateway -> Autonomous Policy Bounds -> Review & Activation) with real-time validation and atomic database persistence of default `PolicyRule` records.
  4. **Strict Typed API Client with Fail-Closed Error Interception:** Built `ApiClient` with unified headers (`X-Merchant-ID`, `X-Auth-Token`, `Authorization`), automatic 401/403 session expiration detection, and structured `ApiError` normalization.
  5. **Accessible Reusable UI Component System:** Created foundational primitives (`Button`, `Input`, `Badge`, `Card`, `Dialog`, `StepIndicator`, `Skeleton`, `EmptyState`) strictly respecting design tokens, keyboard navigation, and zero secret leakage (`INV-AGY-03`).
- **Consequences:**
  - *Positive:* Delivers a complete, tested, responsive web foundation for the Agent-Ready Merchant control plane that seamlessly interfaces with existing canonical gateway and settlement endpoints.
  - *Negative:* Frontend assets require compilation with `npm run build` during distribution.


