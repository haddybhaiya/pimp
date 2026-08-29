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
| **Phase 5.2** | Merchant Admin Portal Views & HITL Operations | **NOT STARTED** | Approvals UI, catalog editor, orders & settlements, policy config, audit viewer |

---

## Phase 5.1 Deliverables Completed

- [x] **Public Landing Page Surface:** Modern, responsive public hero surface highlighting autonomous AI commerce capabilities, ACP protocol support, policy governance, and live interactive protocol visualizer.
- [x] **Server-Authoritative Merchant Authentication:** Implemented `MerchantAuthService` with HMAC SHA-256 signed bearer tokens, slug-based registration (`/api/v1/merchant/auth/signup`), login (`/api/v1/merchant/auth/login`), profile retrieval (`/api/v1/merchant/auth/me`), and multi-tenant isolation.
- [x] **Multi-Step Onboarding / Setup Flow:** 4-step guided setup wizard (Store Identity -> Razorpay Settlement Gateway -> Autonomous Policy Bounds -> Review & Activation) with atomic persistence of seeded `PolicyRule` records.
- [x] **Authenticated Application Shell & Navigation:** Desktop sidebar + mobile collapsible navigation drawer, active merchant context display, environment badge, session expiration detection, and route guards.
- [x] **Reusable Accessible UI Component System:** Standardized foundational primitives (`Button`, `Input`, `Badge`, `Card`, `Dialog`, `StepIndicator`, `Skeleton`, `EmptyState`) respecting design tokens and zero secret leakage.
- [x] **Strict Typed API Client Layer:** Frontend `ApiClient` handling standard headers (`X-Merchant-ID`, `X-Auth-Token`, `Authorization`), automatic 401/403 session expiration interception, and `ApiError` normalization.
- [x] **Dual-Mode Root Endpoint & Static SPA Serving:** FastAPI serves compiled SPA assets (`src/agent_ready_merchant/static`) for browser visits across all web routes while preserving JSON metadata descriptors for API clients.
- [x] **Test Verification Matrix:**
  - Frontend: 17 unit and integration tests passing in Vitest (`api-client.test.ts`, `auth-store.test.tsx`, `ui-components.test.tsx`, `onboarding.test.tsx`, `router.test.tsx`).
  - Backend: 11 integration tests passing in pytest (`tests/test_phase5_1_web_foundation.py`).
- [x] **Full Quality Gate Compliance:** 100% clean passes on `ruff format`, `ruff check`, `mypy (strict)`, Vitest (17 tests), and Pytest (244 passing tests across all test suites, 2 skipped, 84% coverage).


