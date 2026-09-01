# Phase Status & Roadmap: Agent-Ready Merchant

> **Current Phase:** Phase 5 (Web Control Plane, Merchant Portal & Demo Hardening)  
> **Status:** 100% COMPLETED & SIGNED OFF  
> **Milestone Status:** Phase 5.1, Phase 5.2 & Phase 5.3 Complete

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
| **Phase 5.3** | Demo Sandbox & Integration Hardening | **COMPLETED** | Interactive simulation sandbox (`/demo`), standard auto commerce, HITL escalation workbench, payment reconciliation, adversarial attack defense matrix |

---

## Phase 5.3 Deliverables Completed

- [x] **Interactive Simulation Sandbox UI (`/demo`):** Production-grade sandbox workbench allowing merchants and evaluators to trigger real end-to-end commerce lifecycles with deterministic data.
- [x] **Standard Autonomous Flow Demonstration:** Buyer session initiation -> product discovery -> quote generation -> deterministic policy approval (`ALLOW`) -> order creation -> Razorpay webhook simulation (`payment.captured`) -> order settlement (`PAID`) -> inventory deduction -> immutable cryptographic audit logging.
- [x] **Human-In-The-Loop (HITL) Escalation Flow Demonstration:** Buyer discount request in Supervised HITL mode -> policy escalation (`ESCALATE_APPROVAL`) -> stateful `MerchantApproval` ticket creation -> real-time resolution in `/approvals` queue -> quote update.
- [x] **Out-of-Band Payment Reconciliation Demonstration:** Dropped webhook simulation and server-authoritative reconciliation against Razorpay.
- [x] **Authoritative Demo Backend Service (`DemoSimulatorService`):** Deterministic execution endpoints (`POST /api/v1/merchant/demo/simulate`, `POST /api/v1/merchant/demo/seed`) operating directly against real domain models, state machines, and cryptographic verification pipelines.
- [x] **Adversarial Security Attack Verification:** Active verification against 10 attack vectors:
  - Forged Merchant IDs & token tampering
  - Forged capabilities & unauthorized privilege escalation
  - Modified prices & floor price guarantees
  - Cross-merchant resource access & entity ID snooping
  - Duplicate submission & idempotency protection
  - Cryptographic HMAC webhook validation & replay prevention
  - Zero secret leakage in API responses
- [x] **Comprehensive Test Verification Matrix:**
  - Frontend: 26 unit and integration tests passing in Vitest across 7 test files (`api-client.test.ts`, `auth-store.test.tsx`, `ui-components.test.tsx`, `onboarding.test.tsx`, `demo-view.test.tsx`, `portal-views.test.tsx`, `router.test.tsx`).
  - Frontend Build: Production bundle compiled cleanly to `src/agent_ready_merchant/static/`.
  - Backend: 257 passing tests across all test suites in pytest (2 skipped, 84% coverage).
- [x] **Full Quality Gate Compliance:** 100% clean passes on `ruff format`, `ruff check`, `mypy (strict)`, Vitest (26 tests), and Pytest (257 tests).



