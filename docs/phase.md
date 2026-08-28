# Phase Status & Roadmap: Agent-Ready Merchant

> **Current Phase:** Phase 4 (Security Boundary, Authorization Hardening & Governance Kernel)  
> **Status:** 100% COMPLETED & SIGNED OFF  
> **Milestone Status:** Phase 4.1 & Phase 4.2 Complete (Ready for Phase 5 Scope Definition)

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
| **Phase 4.2** | Safety, Policy & Governance Kernel | **COMPLETED** | Centralized policy decision records, immutable audit linkage, deterministic policy hashing, HITL approval gate, platform governance ceilings, zero secret/PII audit sanitization |

---

## Phase 4.1 Deliverables Completed

- [x] **Server-Authoritative Session Authentication:** Constant-time cryptographic token verification (`hmac.compare_digest`) against persisted SHA-256 token hashes (`auth_token_hash`) to mitigate timing attacks.
- [x] **Mandatory Session Boundary Gate:** Stateful and privileged capabilities (`get_quote`, `negotiate_quote`, `accept_quote`, `create_order`, `request_checkout`, `get_payment_status`, `get_order_status`, `terminate_session`) strictly require an active authenticated session (`AUTH_SESSION_NOT_FOUND` fail-closed).
- [x] **Server-Authoritative Capability Derivation:** Gateway strictly derives permissions from database-persisted `BuyerAgentSession.granted_capabilities`, ignoring caller-provided capability elevation (`X-Capabilities`) and failing unauthorized calls closed with `CAPABILITY_DENIED`.
- [x] **Multi-Tenant & Cross-Session Isolation:** Strict row-level verification ensuring buyers cannot access, negotiate, accept, order, or inspect quotes/orders belonging to different merchants or sessions.
- [x] **Anti-Resource Existence Probing:** Uniform not-found errors (`QUOTE_NOT_FOUND`, `ORDER_NOT_FOUND`, `AUTH_SESSION_NOT_FOUND`) on mismatched merchant/session lookups to prevent tenant probing and UUID guessing.
- [x] **Session Expiry & Lifecycle Enforcement:** Real-time expiration enforcement automatically transitioning stale sessions to `EXPIRED` in the database and rejecting replayed credentials.
- [x] **Adversarial Test Suite (`tests/test_phase4_1_security_and_authorization.py`):** 12 comprehensive adversarial tests covering forged tokens, wrong merchants, wrong sessions, forged capabilities, expired sessions, replayed credentials, cross-tenant quote/order access, unauthorized financial mutations, anonymous caller rejections, and malformed contexts.

---

## Phase 4.2 Deliverables Completed

- [x] **Centralized Policy Decision Record & Hashing:** Added `PolicyDecisionRecord` and `compute_policy_hash()` generating deterministic SHA-256 hashes over policy rules. Policy versions and hashes are stamped immutably onto audit logs.
- [x] **Platform Governance Ceilings:** Enforced platform safety boundaries: maximum 20 items per quote (`MAX_ITEMS_PER_QUOTE_EXCEEDED`), absolute 50% discount ceiling (`GOVERNANCE_MAX_DISCOUNT_CEILING_EXCEEDED`), ₹1,00,000 single transaction limit (`GOVERNANCE_MAX_TRANSACTION_LIMIT_EXCEEDED`), and maximum 3 negotiation rounds (`MAX_NEGOTIATION_ATTEMPTS_EXCEEDED`).
- [x] **Human-In-The-Loop (HITL) Merchant Approval Gate:** Created `MerchantApproval` model and `resolve_approval` capability with strict expiration, optimistic locking, and cross-tenant isolation.
- [x] **Immutable Audit Linkage & Anti-Tampering:** End-to-end audit trace linking `request_id -> session_id -> quote_id -> policy_decision_hash -> order_id`. Cryptographic SHA-256 chain verification (`AuditEvent.verify_chain`) detects storage mutations.
- [x] **Audit Secret & PII Sanitization:** Automatic redaction of credentials (`auth_token`, `key_secret`, `password`, `card_number`) and masking of buyer emails (`a***r@example.com`) in immutable audit event payloads.
- [x] **Anti-Context Tampering Gate:** Gateway authoritatively queries merchant configuration from PostgreSQL for non-admin actors, preventing buyer context injection attacks.
- [x] **Adversarial Test Suite (`tests/test_phase4_2_safety_policy_governance.py`):** 12 comprehensive adversarial tests verifying floor breach protection, immutable policy hashes, expired approval tickets, forged/cross-tenant approvals, audit tampering detection, secret/PII redaction, race safety, context tampering override, governance bounds, and non-authoritative LLM mutations.
- [x] **Full Quality Gate Compliance:** 100% clean passes on `ruff format`, `ruff check`, `mypy (strict)`, and `pytest` (227 passing tests across all test suites).

