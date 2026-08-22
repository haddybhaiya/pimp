# Phase Status & Roadmap: Agent-Ready Merchant

> **Current Phase:** Phase 1.3 (Server-Authoritative Razorpay Integration)  
> **Status:** 100% COMPLETED & SIGNED OFF  
> **Next Sub-Phase:** Phase 1.4 (Untrusted Intelligence Layer — Groq Adapter & Tool Gateway)

---

## Phase Breakdown & Status

| Phase / Milestone | Description | Status | Scope Cut Line |
|---|---|---|---|
| **Phase 0** | System Architecture, Domain Model, State Machines, Threat Model, Invariants, Evaluation Framework & Contracts | **COMPLETED** | No application/payment/LLM implementation code |
| **Phase 1.0** | Engineering CI Foundation (GitHub Actions, Ruff, Mypy, Pytest, Secret Scan) | **COMPLETED** | CI pipeline, minimal tooling configs, smoke tests only |
| **Phase 1.1** | Core Domain Models, PostgreSQL Migrations & Database Constraints | **COMPLETED** | SQLAlchemy models, Alembic, integer paise columns, optimistic locking |
| **Phase 1.2** | Deterministic Policy Engine & Authoritative State Machines | **COMPLETED** | Pure Python FSMs, pricing floor guards, fail-closed policy engine |
| **Phase 1.3** | Server-Authoritative Razorpay Client & Webhook Receiver | **COMPLETED** | HMAC SHA-256 verification, orders API, payment capture, reconciliation |
| **Phase 1.4** | Untrusted Intelligence Layer (Groq Adapter & Tool Gateway) | PLANNED | Pydantic tool contracts, prompt delimiters, rate limits |
| **Phase 1.5** | End-to-End Golden Path & Deliberate Failure Verification | PLANNED | Integration tests demonstrating E2E transactability & recovery |
| **Phase 2** | Merchant Supervision & Control Plane (UI) | PLANNED | React + TypeScript Dashboard, Live Session Observability |
| **Phase 3** | Autonomous Merchant Optimization Agent | PLANNED | Revenue experiments, catalog auto-tuning, conversion analytics |

---

## Phase 1.3 Deliverables Completed

- [x] Async Razorpay API adapter with timeout and typed error mapping (`src/agent_ready_merchant/integrations/razorpay/client.py`)
- [x] Cryptographic HMAC SHA-256 raw-body webhook signature verification (`src/agent_ready_merchant/integrations/razorpay/webhook.py`)
- [x] Payment & Order coordinator service with state machine integration (`src/agent_ready_merchant/services/payment_service.py`)
- [x] Webhook receiver endpoint with anti-fraud amount validation (`POST /api/v1/payments/webhook`)
- [x] Out-of-band server reconciliation mechanism (`POST /api/v1/orders/{order_id}/reconcile`)
- [x] Append-only ledger integration creating `TransactionRecord` upon verified payment
- [x] Live sandbox test verifying HTTP roundtrip against Razorpay test-mode API (`tests/test_razorpay_live_testmode.py`)
- [x] Configuration cleanup transitioning LLM settings to Groq (`GROQ_API_KEY`)
- [x] 59 Comprehensive unit, integration, and adversarial tests passing

---

## Phase 1.4 Readiness Gates

Before Phase 1.4 implementation begins:
1. Verify all 59 Phase 1.3 tests pass.
2. Confirm Groq API key (`GROQ_API_KEY`) is configured in `.env`.
3. Review Tool Gateway and Pydantic schema validation contracts in `docs/tool-contract.md` and `docs/agent-contract.md`.
