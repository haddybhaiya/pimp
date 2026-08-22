# Phase Status & Roadmap: Agent-Ready Merchant

> **Current Phase:** Phase 1.2 (Deterministic State Machines + Policy Engine)  
> **Status:** 100% COMPLETED & SIGNED OFF  
> **Next Sub-Phase:** Phase 1.3 (Server-Authoritative Razorpay Client & Webhook Receiver)

---

## Phase Breakdown & Status

| Phase / Milestone | Description | Status | Scope Cut Line |
|---|---|---|---|
| **Phase 0** | System Architecture, Domain Model, State Machines, Threat Model, Invariants, Evaluation Framework & Contracts | **COMPLETED** | No application/payment/LLM implementation code |
| **Phase 1.0** | Engineering CI Foundation (GitHub Actions, Ruff, Mypy, Pytest, Secret Scan) | **COMPLETED** | CI pipeline, minimal tooling configs, smoke tests only |
| **Phase 1.1** | Core Domain Models, PostgreSQL Migrations & Database Constraints | **COMPLETED** | SQLAlchemy models, Alembic, integer paise columns, optimistic locking |
| **Phase 1.2** | Deterministic Policy Engine & Authoritative State Machines | **COMPLETED** | Pure Python FSMs, pricing floor guards, fail-closed policy engine |
| **Phase 1.3** | Server-Authoritative Razorpay Client & Webhook Receiver | PLANNED | HMAC SHA-256 verification, orders API, payment capture |
| **Phase 1.4** | Untrusted Intelligence Layer (Gemini Adapter & Tool Gateway) | PLANNED | Pydantic tool contracts, prompt delimiters, rate limits |
| **Phase 1.5** | End-to-End Golden Path & Deliberate Failure Verification | PLANNED | Integration tests demonstrating E2E transactability & recovery |
| **Phase 2** | Merchant Supervision & Control Plane (UI) | PLANNED | React + TypeScript Dashboard, Live Session Observability |
| **Phase 3** | Autonomous Merchant Optimization Agent | PLANNED | Revenue experiments, catalog auto-tuning, conversion analytics |

---

## Phase 1.2 Deliverables Completed

- [x] Base state machine exceptions & transition result container (`src/agent_ready_merchant/state_machines/base.py`)
- [x] PriceQuote state machine with quote expiry & optimistic concurrency (`src/agent_ready_merchant/state_machines/price_quote.py`)
- [x] Order state machine with terminal state protection (`src/agent_ready_merchant/state_machines/order.py`)
- [x] PaymentAttempt state machine (`src/agent_ready_merchant/state_machines/payment_attempt.py`)
- [x] TransactionRecord state machine (`src/agent_ready_merchant/state_machines/transaction.py`)
- [x] AgentRun state machine with $\le 5$ step execution limit (`src/agent_ready_merchant/state_machines/agent_run.py`)
- [x] BuyerIntent state machine (`src/agent_ready_merchant/state_machines/buyer_intent.py`)
- [x] Pure deterministic policy rules (`src/agent_ready_merchant/policy/rules.py`)
- [x] Deterministic Policy Engine with fail-closed resolution (`src/agent_ready_merchant/policy/engine.py`)
- [x] 42 Comprehensive unit, integration, and adversarial tests (`tests/`)

---

## Phase 1.3 Readiness Gates

Before Phase 1.3 implementation begins:
1. Verify all 42 Phase 1.2 tests pass.
2. Confirm Razorpay test key credentials in `.env` match test mode requirements.
3. Review HMAC SHA-256 webhook signature verification requirements in `docs/razorpay-integration-notes.md`.
