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
| **Phase 5.1** | Web Foundation & Public Surface | **COMPLETED** | Public landing page, merchant authentication, setup wizard, authenticated SPA shell, responsive component tokens, typed API client, error normalization |
| **Phase 5.2** | Merchant Admin Portal Views & HITL Operations | **COMPLETED** | Approvals UI, catalog editor, inventory manager, orders & settlements, policy config, audit viewer |

---

## Phase 5.2 Deliverables Completed

- [x] **Authoritative Merchant Dashboard:** Overview page with live aggregated metrics (active products count, order volumes, revenue in ₹, pending HITL approvals, policy fingerprint, autonomy state) without fake client analytics.
- [x] **Product Catalog & Floor Price Enforcement:** Authoritative catalog management with floor price invariant protection (`floor_price <= base_price`), duplicate SKU prevention, category indexing, and live stock tracking.
- [x] **Real-Time Inventory Management:** Stock ledger with optimistic concurrency locking, quantity threshold warnings, and strict non-negative delta adjustments.
- [x] **Quotes & Price Negotiation Trace:** Comprehensive quote ledger showing line items, state machine transitions (`DRAFT` -> `PROPOSED` -> `ACCEPTED`), discount breakdowns, and negotiation histories.
- [x] **Orders & Out-of-Band Payment Reconciliation:** Authoritative order ledger displaying payment attempts, Razorpay order IDs, capture statuses, and manual reconciliation triggers against Razorpay.
- [x] **Payments & Capture Tracking:** Authoritative payment ledger tracking individual Razorpay payment attempts, capture statuses, and payment methods.
- [x] **Human-In-The-Loop (HITL) Approvals Queue:** Dedicated approval workbench supporting status filtering (`PENDING`, `APPROVED`, `REJECTED`), expiration checks, note capture, and atomic quote term adjustments upon approval resolution.
- [x] **Policy & Governance Rules Editor:** Dynamic autonomy and safety boundary configuration interface enforcing platform ceilings ($\le 50\%$ discount, $\le 100\%$ margin) and live deterministic SHA-256 policy hash preview.
- [x] **Cryptographic Audit Trail Inspector:** Immutable audit ledger viewer with real-time SHA-256 hash chain verification badge, previous hash linking, and actor/payload inspector.
- [x] **Store Settings & Public ACP Endpoints:** Merchant store profile details and copyable ACP protocol endpoint URLs.
- [x] **Multi-Tenant Isolation & Security Matrix:** Server-authoritative isolation preventing cross-tenant data leakage or mutation across all endpoints.
- [x] **Comprehensive Test Verification Matrix:**
  - Frontend: 23 unit and integration tests passing in Vitest (`api-client.test.ts`, `auth-store.test.tsx`, `ui-components.test.tsx`, `onboarding.test.tsx`, `router.test.tsx`, `portal-views.test.tsx`).
  - Backend: 6 comprehensive integration tests in pytest (`tests/test_phase5_2_merchant_control_plane.py`).
- [x] **Full Quality Gate Compliance:** 100% clean passes on `ruff format`, `ruff check`, `mypy (strict)`, Vitest (23 tests), and Pytest (250 passing tests across all test suites, 2 skipped, 84% coverage).


