# Phase Status & Roadmap: Agent-Ready Merchant

> **Current Phase:** Phase 2.2 (External AI Buyer Commerce Flow)  
> **Status:** 100% COMPLETED & SIGNED OFF  
> **Next Milestone:** Phase 2.3 (Merchant Supervision & Control Plane)

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
| **Phase 2.3** | Merchant Supervision & Control Plane (UI) | PLANNED | React + TypeScript Dashboard, Live Session Observability |
| **Phase 3** | Autonomous Merchant Optimization Agent | PLANNED | Revenue experiments, catalog auto-tuning, conversion analytics |

---

## Phase 1.5 Deliverables Completed

- [x] Full end-to-end golden path verification test (`tests/test_e2e_golden_path.py`):
  * Buyer request $\to$ LLM reasoning $\to$ structured intent $\to$ tool gateway $\to$ policy check $\to$ quote $\to$ negotiation $\to$ acceptance $\to$ order creation $\to$ Razorpay test payment $\to$ HMAC webhook $\to$ PAID order $\to$ TransactionRecord $\to$ Audit trail.
- [x] Deliberate Failure Matrix test suite covering 16 critical failure modes (`tests/test_deliberate_failures_matrix.py`):
  * Malformed outputs, prompt injections, unknown tools, unauthorized capabilities, invalid arguments, below-floor prices, excessive discounts, invalid state transitions, stale version locks, duplicate checkouts, tampered webhooks, amount mismatches, payment failures, Razorpay timeouts/500s, dropped webhook reconciliation, secret leakage scanning.
- [x] Concurrency and idempotency test suite (`tests/test_concurrency_and_idempotency.py`):
  * Multi-delivery webhook bursts guaranteeing single transaction record creation.
- [x] 100 passing automated tests across all domain, state machine, policy, payment, and gateway layers.

---

## Phase 2 Readiness Gates

Before Phase 2 implementation begins:
1. Verify all 100 Phase 1 tests pass.
2. Review Merchant Supervision UI and Control Plane requirements in `docs/architecture.md`.
