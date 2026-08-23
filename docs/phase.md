# Phase Status & Roadmap: Agent-Ready Merchant

> **Current Phase:** Phase 1.4 (Untrusted Intelligence Layer + Tool Gateway)  
> **Status:** 100% COMPLETED & SIGNED OFF  
> **Next Sub-Phase:** Phase 1.5 (End-to-End Golden Path & Deliberate Failure Verification)

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
| **Phase 1.5** | End-to-End Golden Path & Deliberate Failure Verification | PLANNED | Integration tests demonstrating E2E transactability & recovery |
| **Phase 2** | Merchant Supervision & Control Plane (UI) | PLANNED | React + TypeScript Dashboard, Live Session Observability |
| **Phase 3** | Autonomous Merchant Optimization Agent | PLANNED | Revenue experiments, catalog auto-tuning, conversion analytics |

---

## Phase 1.4 Deliverables Completed

- [x] Provider-agnostic LLM interface and Groq adapter (`src/agent_ready_merchant/llm/`)
- [x] Structured Intent Protocol parsing & schema validation (`src/agent_ready_merchant/agent/intent.py`)
- [x] Deterministic Tool Gateway with capability, schema, policy, and audit enforcement (`src/agent_ready_merchant/tools/`)
- [x] 6 MVP tools implemented (`discover_catalog`, `get_product_details`, `request_price_quote`, `negotiate_quote`, `create_order`, `check_payment_status`)
- [x] Bounded Agent Runtime enforcing max 5 steps, timeouts, and malformed retry recovery (`src/agent_ready_merchant/agent/runtime.py`)
- [x] Anti-injection parameter delimitation (`<untrusted_buyer_input>`) and zero-secret context guarantees (`src/agent_ready_merchant/agent/prompt.py`)
- [x] 84 Comprehensive tests covering happy paths, bounds, malformed outputs, and adversarial injection attempts (`tests/`)

---

## Phase 1.5 Readiness Gates

Before Phase 1.5 implementation begins:
1. Verify all 84 Phase 1.4 tests pass.
2. Confirm deterministic policy engine and Razorpay test-mode boundary are fully integrated.
3. Review Golden Path and Deliberate Failure scenarios defined in `docs/evaluation.md`.
