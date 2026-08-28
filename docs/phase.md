# Phase Status & Roadmap: Agent-Ready Merchant

> **Current Phase:** Phase 4.1 (Security Boundary & Authorization Hardening)  
> **Status:** 100% COMPLETED & SIGNED OFF  
> **Next Milestone:** Phase 4.2 (External Ecosystem & Autonomous Merchant Optimization)

---

## Phase Breakdown & Status

| Phase / Milestone | Description | Status | Scope Cut Line |
|---|---|---|---|
| **Phase 0** | System Architecture, Domain Model, State Machines, Threat Model, Invariants, Evaluation Framework & Contracts | **COMPLETED** | No application/payment/LLM implementation code |
| **Phase 1.0** | Engineering CI Foundation (GitHub Actions, Ruff, Mypy, Pytest, Secret Scan) | **COMPLETED** | CI pipeline, minimal tooling configs, smoke tests only |
| **Phase 1.1** | Core Domain Models, PostgreSQL Migrations & Database Constraints | **COMPLETED** | SQLAlchemy models, Alembic, integer paise columns, optimistic locking |
| **Phase 1.2** | Deterministic Policy Engine & Authoritative State Machines | **COMPLETED** | Pure Python FSMs, pricing floor guards, fail-closed policy engine |
| **Phase 1.3** | Server-Authoritative Razorpay Client & Webhook Receiver | **COMPLETED** | HMAC SHA-256 verification, orders API, payment capture, reconciliation |
| **Phase 1.4** | Untrusted Intelligence Layer (Groq Adapter & Tool Gateway) | **COMPLETED** | Pydantic tool contracts, prompt delimiters, rate limits, action gateway |
| **Phase 1.5** | End-to-End Golden Path & Deliberate Failure Verification | **COMPLETED** | Integration tests demonstrating E2E transactability & recovery |
| **Phase 2.1** | Canonical Commerce Gateway & Merchant AI Representation | **COMPLETED** | 8 canonical capabilities, CapabilityRegistry, MerchantAIRepresentation, strict envelopes |
| **Phase 2.2** | External AI Buyer Commerce Flow | **COMPLETED** | Autonomous AIBuyerClient, explicit states, bounded negotiation, security matrix, deliberate failure recovery |
| **Phase 2.3** | Protocol Boundary + Production-Grade Demo Hardening | **COMPLETED** | ACP Protocol Adapter, AgentProtocolClient, contract versioning, idempotency manager, rate limiting, bounded payloads, safe error sanitization |
| **Phase 3.1** | Razorpay Payment Boundary & Invariant Hardening | **COMPLETED** | Server-authoritative amount/currency verification, payment-order binding, multi-entity transaction binding, error normalization, race safety |
| **Phase 3.2** | Payment Reliability Hardening | **COMPLETED** | Durable webhook deduplication, replay protection, order creation retry safety, ledger uniqueness, audit chain integrity |
| **Phase 3.3** | End-to-End Payment Verification & Deliberate Failure Suite | **COMPLETED** | Deterministic E2E verification suite, fake Razorpay transport, 1 golden-path lifecycle + 16 deliberate failure scenarios (17 total), zero side-effect verification |
| **Phase 4.1** | Security Boundary & Authorization Hardening | **COMPLETED** | Server-authoritative identity, constant-time token verification, mandatory session boundary on privileged/stateful capabilities, anti-resource existence probing, adversarial verification |

---

## Phase 4.1 Deliverables Completed

- [x] **Server-Authoritative Session Authentication:** Constant-time cryptographic token verification (`hmac.compare_digest`) against persisted SHA-256 token hashes (`auth_token_hash`) to mitigate timing attacks.
- [x] **Mandatory Session Boundary Gate:** Stateful and privileged capabilities (`get_quote`, `negotiate_quote`, `accept_quote`, `create_order`, `request_checkout`, `get_payment_status`, `get_order_status`, `terminate_session`) strictly require an active authenticated session (`AUTH_SESSION_NOT_FOUND` fail-closed).
- [x] **Server-Authoritative Capability Derivation:** Gateway strictly derives permissions from database-persisted `BuyerAgentSession.granted_capabilities`, ignoring caller-provided capability elevation (`X-Capabilities`) and failing unauthorized calls closed with `CAPABILITY_DENIED`.
- [x] **Multi-Tenant & Cross-Session Isolation:** Strict row-level verification ensuring buyers cannot access, negotiate, accept, order, or inspect quotes/orders belonging to different merchants or sessions.
- [x] **Anti-Resource Existence Probing:** Uniform not-found errors (`QUOTE_NOT_FOUND`, `ORDER_NOT_FOUND`, `AUTH_SESSION_NOT_FOUND`) on mismatched merchant/session lookups to prevent tenant probing and UUID guessing.
- [x] **Session Expiry & Lifecycle Enforcement:** Real-time expiration enforcement automatically transitioning stale sessions to `EXPIRED` in the database and rejecting replayed credentials.
- [x] **Adversarial Test Suite (`tests/test_phase4_1_security_and_authorization.py`):** 12 comprehensive adversarial tests covering forged tokens, wrong merchants, wrong sessions, forged capabilities, expired sessions, replayed credentials, cross-tenant quote/order access, unauthorized financial mutations, anonymous caller rejections, and malformed contexts.
- [x] **Full Quality Gate Compliance:** 100% clean passes on `ruff format`, `ruff check`, `mypy (strict)`, and `pytest` (215 passing tests across all suites).
