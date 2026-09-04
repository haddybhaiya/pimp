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
  5. **Browser Session Containment:** Merchant portal sessions are delivered only as `HttpOnly`, `SameSite=Strict` cookies. The SPA sends browser credentials automatically and never persists an administrative bearer token in Web Storage; explicit `X-Auth-Token` credentials remain supported for non-browser clients. Merchant-admin session tokens are signed with the dedicated application `SECRET_KEY`, never the Razorpay webhook secret, and every protected request verifies the merchant remains `ACTIVE`.
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

---

## ADR-016: Merchant Control Plane Operations & Human-In-The-Loop (HITL) Management

- **Status:** ACCEPTED
- **Context:** Operating autonomous agent-ready storefronts requires comprehensive merchant administrative surfaces: KPI overview, catalog management, inventory tracking, quotes and negotiations ledger, orders and payments management, policy governance configuration, HITL approval queue, and immutable audit trail verification. In accordance with the foundational separation of intelligence and authority ($\text{Intelligence} \neq \text{Authority}$, `INV-AGY-01`), the browser client is untrusted and must never hold authoritative state over pricing, margins, capabilities, payment settlements, or approvals.
- **Decision:**
  1. **Server-Authoritative Control Plane Endpoints:** Implemented authenticated REST endpoints under `/api/v1/merchant/...` backed by `MerchantPortalService`. Every request enforces HMAC-signed token validation, multi-tenant isolation, optimistic concurrency locking, and integer paise monetary arithmetic.
  2. **Authoritative Human Approval Queue:** Dedicated workbench for reviewing escalated proposals. Approving or rejecting a ticket updates `MerchantApproval` records with optimistic concurrency control, mutates underlying quote terms and statuses, and emits cryptographically signed audit events.
  3. **Policy Governance & Live Fingerprinting:** Merchant policy configurations are governed with platform-enforced hard ceilings (maximum 50% discount rate, 100% margin constraint). Updates dynamically re-calculate the SHA-256 `policy_hash` directly on the server.
  4. **Cryptographic Chain Verification:** The control plane provides real-time verification of the immutable append-only `audit_events` hash chain (`AuditEvent.verify_chain()`), surfacing cryptographic tampering detection badges directly on the UI.
  5. **Out-of-Band Payment Reconciliation:** Store operators can trigger server-side reconciliation for any order directly against Razorpay's authoritative payments API to resolve asynchronous delivery gaps.
  6. **Durable Mutation Idempotency:** Inventory adjustments and demo simulations require an `X-Idempotency-Key`; a transactionally persisted receipt replays an identical completed request and rejects payload/key conflicts before any repeat side effect.
- **Consequences:**
  - *Positive:* Full visibility and operational control over autonomous store actions with tamper-evident audit trails and zero secret exposure.
  - *Negative:* All admin actions require active backend network roundtrips to maintain authoritative state.

---

## ADR-017: Interactive Demo Simulation Sandbox & End-to-End Hardening

- **Status:** ACCEPTED
- **Context:** Demonstrating, evaluating, and stress-testing the Agent-Ready Merchant control plane requires a cohesive, deterministic simulation workbench (`/demo`) that exercises the entire commerce flow (session initiation -> discovery -> quote -> negotiation -> HITL escalation -> order creation -> Razorpay payment capture -> webhook verification -> settlement -> audit hash chaining) without using mocked shortcuts or compromising security invariants.
- **Decision:**
  1. **Server-Authoritative Demo Simulation Service:** Implemented `DemoSimulatorService` (`src/agent_ready_merchant/services/demo_simulator_service.py`) exposed via authenticated endpoints `POST /api/v1/merchant/demo/simulate` and `POST /api/v1/merchant/demo/seed`. All simulation steps operate directly on real PostgreSQL domain models, pure Python state machines, deterministic policy engine rules, and cryptographically verified webhook processors.
  2. **Three Core Demonstration Scenarios:**
     - *Standard Autonomous Commerce:* Policy-compliant discount evaluated to `ALLOW`, order generated, Razorpay HMAC webhook captured, order settled (`PAID`), stock deducted, audit chain appended.
     - *Supervised HITL Escalation:* Aggressive discount in Supervised Autonomy Mode evaluates to `ESCALATE_APPROVAL`, creating a stateful `MerchantApproval` ticket that can be reviewed and resolved in `/approvals`.
     - *Out-of-Band Payment Reconciliation:* Dropped webhook scenario with server-authoritative query against Razorpay client.
  3. **Adversarial Hardening Defense Matrix:** Comprehensive adversarial tests verify resilience against forged merchant tokens, capability injection, below-floor pricing attacks, cross-tenant resource snooping, replay attacks, duplicate submissions, and secret leakage.
- **Consequences:**
  - *Positive:* Allows instant, reproducible verification of the complete platform across all quality gates without external network flakiness.
  - *Negative:* Demo catalog and state requires explicit merchant-scoped reset triggers.

---

## ADR-018: InsForge PostgreSQL Integration & Deployment Architecture

- **Status:** ACCEPTED
- **Context:** Deploying the Agent-Ready Merchant backend to InsForge requires connecting the application and Alembic migrations to InsForge's managed PostgreSQL infrastructure without altering the canonical architecture, state machines, policy engines, or compromising strict security/concurrency invariants (`INV-FIN-01` through `INV-FIN-05`, `INV-AGY-01` through `INV-AGY-05`).
- **Decision:**
  1. **Target Managed PostgreSQL via Connection String:** Connected the FastAPI async backend (`asyncpg`) and Alembic synchronous migration runner (`psycopg2`/`asyncpg`) directly to the linked InsForge PostgreSQL cluster (`9mvctuj3.ap-southeast.database.insforge.app:5432/insforge`).
  2. **Automated Alembic Migration Chain (001 to 006):** Applied the canonical Alembic migration chain against the target database, including the durable merchant mutation receipt uniqueness constraint that prevents replayed control-plane side effects.
  3. **Preservation of Authoritative Domain & Gateway Architecture:** The application logic, deterministic policy engine, HMAC verification, cryptographic audit chain, and capability checks remain 100% server-authoritative inside FastAPI; InsForge serves exclusively as the managed PostgreSQL database and deployment platform.
  4. **Health Check Observability:** Enhanced `/health` endpoint to explicitly report `application_alive`, `database_reachable`, `database_connected`, and `configuration_valid` without exposing database credentials or secrets.
  5. **Direct Concurrency Verification:** Created and verified `tests/test_insforge_postgresql_integration.py` to confirm that PostgreSQL row-level locks (`SELECT ... FOR UPDATE`), transaction rollback boundaries, and cryptographic hash chain linking execute cleanly on InsForge infrastructure.
- **Consequences:**
  - *Positive:* Full feature parity and invariant compliance on production-grade cloud PostgreSQL with zero architectural compromises.
  - *Negative:* Requires SSL connection parameters (`sslmode=require`) and network accessibility to the InsForge database host.

---

## ADR-019: InsForge-Backed Persistent Merchant Identity

- **Status:** ACCEPTED
- **Context:** A store slug and Razorpay key identify a merchant configuration but cannot prove who owns it. The prior browser session refresh mechanism therefore could not support a secure login after logout or session expiry.
- **Decision:** Use InsForge Auth as the browser identity provider. A verified InsForge user ID is bound once to `merchants.auth_user_id` under a unique database constraint. The backend validates the short-lived InsForge bearer token server-side before issuing its existing `HttpOnly`, `SameSite=Strict` merchant session cookie. Slugs remain public identifiers and are never login credentials.
- **Consequences:**
  - *Positive:* Merchants sign up once with email/password and can securely return without Razorpay credentials or browser-stored administrator tokens.
  - *Negative:* Existing merchants created before this binding require an explicit owner-linking migration before they can use InsForge login.

---

## ADR-020: Merchant Agent Intelligence Separation & Approval-First Experimentation Framework

- **Status:** ACCEPTED
- **Context:** Optimizing merchant storefronts (product descriptions, delivery ETA visibility, discovery metadata, recommendation ordering, bundle offerings) requires AI-assisted diagnosis and proposal generation. However, giving an LLM autonomous authority to directly change prices, alter financial policies, grant capabilities, or execute financial transactions violates fundamental financial safety invariants ($\text{Intelligence} \neq \text{Authority}$, `INV-AGY-01`, `INV-AGY-05`).
- **Decision:**
  1. **Intelligence $\neq$ Authority Lifecycle:** The Merchant Agent follows an explicit lifecycle: `OBSERVE → DIAGNOSE → FORM HYPOTHESIS → PROPOSE → ESTIMATE → MEASURE`. It acts strictly as an untrusted proposal engine for human review.
  2. **Authoritative PostgreSQL Observation Layer:** Telemetry metrics are queried directly from database records, strictly tenant-scoped, and explicitly categorized into `OBSERVED` (raw counts), `DERIVED` (deterministic formulas), and `ESTIMATED` (bounded lost demand projections).
  3. **Zero Secret & PII Leakage in Snapshot Context:** Snapshot context excludes credentials, Razorpay secrets, auth tokens, and sanitizes buyer emails before presenting context to the LLM (`INV-AGY-03`).
  4. **Server-Authoritative Risk Classification:** The backend deterministically evaluates all model proposals. Any proposal attempting to change floor prices, alter policies, grant capabilities, or execute payments is immediately marked `PROHIBITED` and rejected.
  5. **Approval-First Experiment Framework:** Durable database entities (`MerchantExperiment`, `MerchantExperimentResult`) require explicit merchant administrative approval (`approval_status = "PENDING"` $\to$ `APPROVED`) before test activation. Autonomous production mutation is strictly forbidden in Phase 7.
  6. **Server-Computed Deterministic Measurement:** Post-experiment metric changes, sample sizes, and recommendations (`KEEP`, `ROLLBACK`, `INCONCLUSIVE`) are computed deterministically from PostgreSQL telemetry; the model cannot hallucinate or fabricate measurement results.
  7. **Immutable Audit Ledger Linkage:** Every agent run, proposal review, experiment creation, approval, and evaluation is recorded in the append-only cryptographic `audit_events` ledger.
- **Consequences:**
  - *Positive:* Unlocks merchant-side AI optimization while maintaining airtight financial invariants, zero secret leakage, and full administrative control.
  - *Negative:* All proposals and experiments require human review and consent prior to production activation.

---

## ADR-021: Controlled Autonomy Architecture, Master Kill Switch, and Deterministic Reversible Rollback Engine

- **Status:** ACCEPTED
- **Context:** While Phase 7 established proposal formulation and approval-first experimentation, merchants require automated execution for explicitly configured, low-risk, reversible optimizations (e.g. improving search descriptions, exposing delivery ETA, reordering recommendations, updating discovery tags). However, autonomy must not bypass security, risk runaway budget consumption, clobber human merchant edits, or allow LLM prompt injection to elevate privileges or modify pricing.
- **Decision:**
  1. **Strict Allowed Action Allowlist:** Autonomous execution is restricted to 5 explicitly enumerated low-risk actions: `IMPROVE_PRODUCT_DESCRIPTION`, `IMPROVE_DISCOVERY_METADATA`, `REORDER_RECOMMENDATIONS`, `EXPOSE_DELIVERY_ETA`, `SUGGEST_BOUNDED_EXPERIMENT`.
  2. **Zero Financial/Policy Mutation:** Financial authority, pricing floors, margins, rules, and capabilities remain strictly human-only. Any autonomous request attempting to modify financial parameters or escalate privileges is classified `PROHIBITED` and rejected fail-closed.
  3. **Authoritative 18-Precondition Gate Pipeline:** Execution must pass sequentially through 18 deterministic server-side gates: actor authority, merchant active state, master kill switch, anomaly check, proposal evidence validation, typed allowlist, rule enablement and `AUTO_LOW_RISK` classification, rule hash integrity, hourly budget, daily budget, cooldown period, target resource existence and tenant ownership, optimistic version check, pre-mutation JSON snapshot generation, idempotency claim, target domain mutation, action ledger commit, and immutable audit event logging.
  4. **Master Kill Switch:** Immediate server-authoritative toggle (`kill_switch_enabled`) that blocks all pending autonomous actions instantly and halts all running experiments safely with `stopped_by_kill_switch: True`.
  5. **Deterministic Reversible Rollback & Human Precedence:** Every autonomous execution records a complete pre-mutation snapshot. Rollback restores the snapshot state version-checked. If a human merchant modified the entity after autonomous execution, rollback fails closed with `RollbackConflictError` and transitions to `CONFLICT_REJECTED` to prevent clobbering human edits.
  6. **Rate Limiting & Quotas:** Enforces per-rule hourly limits [1, 100], daily limits [1, 1000], and cooldown periods [0, 86400s] verified directly via database counts.
  7. **Tenant Isolation & Idempotency:** Composite foreign keys `(experiment_id, merchant_id)` prevent cross-tenant linkage; `MerchantMutationIdempotencyService` guarantees single execution and safe replays.
- **Consequences:**
  - *Positive:* Safe, bounded autonomous store optimization with zero risk to financial boundaries, instant kill-switch control, and guaranteed reversible state snapshots.
  - *Negative:* Autonomous actions cannot alter pricing or financial parameters directly; requires maintenance of pre-mutation snapshots in database.

---

## ADR-022: Discovery Network Architecture, Public Capability Graph, and Deterministic Buyer Matching Engine

- **Status:** ACCEPTED
- **Context:** External AI buyers, autonomous aggregator agents, and commerce protocols require a mechanism to discover agent-ready merchants, explore public catalog summaries, and assess store capabilities matching buyer intent. However, discovery surfaces must not create unauthorized buyer sessions, reserve stock, leak merchant secrets/credentials, expose floor prices or private policy rules, allow prompt injection attacks to alter rankings, or enable resource-existence probing against non-public stores.
- **Decision:**
  1. **Strict Separation of Discovery and Authority ($\text{Intelligence} \neq \text{Authority}$):** Discovery endpoints and capability graphs are strictly descriptive and read-only. Discovery never grants capability execution, initializes buyer sessions, reserves inventory, creates binding quotes, generates orders, or triggers financial transactions.
  2. **Merchant-Controlled Discoverability Lifecycle:** Store discoverability is managed exclusively by human `MERCHANT_ADMIN` users across four explicit states: `PRIVATE` (default upon signup), `DISCOVERABLE`, `PAUSED`, and `SUSPENDED`. Autonomous agents, LLM proposals, and external buyers cannot modify discoverability.
  3. **Anti-Probing Uniform 404:** Direct lookups on merchants in `PRIVATE`, `PAUSED`, `SUSPENDED`, or non-existent states return an identical, uniform 404 error (`MerchantNotFoundError`) with consistent error timing and payloads, preventing merchant enumeration or existence probing.
  4. **Safe Public Capability Graph:** The public capability graph is dynamically derived from the canonical `CapabilityRegistry` with descriptive metadata, monetary classifications, and side-effect classes. Discovery of a capability node does not grant authorization to invoke it.
  5. **Zero Secret & PII Leakage:** Public profiles project strictly allowlisted fields (opaque discovery ID, slug, display name, category, safe product summaries, supported currencies, non-binding price range in integer paise, safe delivery regions, and verified platform trust signals). Razorpay keys, webhook secrets, merchant/product database IDs, internal margin percentages, private policies, and customer PII are strictly excluded.
  6. **Deterministic Matching & Integer Budget Safety:** Buyer intents are evaluated against catalog offerings using deterministic filtering (currency, required capabilities, delivery region, category, public product SKU, attributes, available inventory, and integer budget). Budget checks enforce integer multiplication overflow guards (`min_var_paise * qty <= maximum_budget_paise`). Unsupported capabilities, unavailable inventory, and regions fail closed.
  7. **Prompt Injection Search-Keyword Neutralization:** All text inputs in buyer search queries and parameters are treated strictly as literal search strings. Prompt injection directives (e.g. `IGNORE PREVIOUS INSTRUCTIONS`) cannot modify ranking algorithms, alter floor prices, bypass capability gates, or trigger autonomous mutations.
  8. **Replay-Safe Discovery Telemetry & Bounded Rate Limits:** Telemetry events enforce composite uniqueness on `(merchant_id, event_type, correlation_id)` in PostgreSQL, preventing replay inflation. Public search is protected by in-memory sliding window rate limits (60 req/min per client IP).
- **Consequences:**
  - *Positive:* Enables seamless discovery of agent-ready merchants across the external AI buyer ecosystem while maintaining zero secret leakage, fail-closed security, and complete protection against unauthorized financial or state mutations.
  - *Negative:* Buyers cannot immediately transact from search results; they must perform an explicit, server-authoritative handoff to `initialize_session` on the canonical commerce gateway.







