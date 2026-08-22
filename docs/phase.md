# Phase Status & Roadmap: Agent-Ready Merchant

> **Current Phase:** Phase 1.1 (Core Domain Models & Persistence Foundation)  
> **Status:** 100% COMPLETED & SIGNED OFF  
> **Next Sub-Phase:** Phase 1.2 (Deterministic Policy Engine & Authoritative State Machines)

---

## Phase Breakdown & Status

| Phase / Milestone | Description | Status | Scope Cut Line |
|---|---|---|---|
| **Phase 0** | System Architecture, Domain Model, State Machines, Threat Model, Invariants, Evaluation Framework & Contracts | **COMPLETED** | No application/payment/LLM implementation code |
| **Phase 1.0** | Engineering CI Foundation (GitHub Actions, Ruff, Mypy, Pytest, Secret Scan) | **COMPLETED** | CI pipeline, minimal tooling configs, smoke tests only |
| **Phase 1.1** | Core Domain Models, PostgreSQL Migrations & Database Constraints | **COMPLETED** | SQLAlchemy models, Alembic, integer paise columns, optimistic locking |
| **Phase 1.2** | Deterministic Policy Engine & Authoritative State Machines | PLANNED | Pure Python FSMs, pricing floor guards, 100% test coverage |
| **Phase 1.3** | Server-Authoritative Razorpay Client & Webhook Receiver | PLANNED | HMAC SHA-256 verification, orders API, payment capture |
| **Phase 1.4** | Untrusted Intelligence Layer (Gemini Adapter & Tool Gateway) | PLANNED | Pydantic tool contracts, prompt delimiters, rate limits |
| **Phase 1.5** | End-to-End Golden Path & Deliberate Failure Verification | PLANNED | Integration tests demonstrating E2E transactability & recovery |
| **Phase 2** | Merchant Supervision & Control Plane (UI) | PLANNED | React + TypeScript Dashboard, Live Session Observability |
| **Phase 3** | Autonomous Merchant Optimization Agent | PLANNED | Revenue experiments, catalog auto-tuning, conversion analytics |

---

## Phase 1.1 Deliverables Completed

- [x] Application settings with SecretStr masking (`src/agent_ready_merchant/config.py`)
- [x] Database engine, session provider & naming conventions (`src/agent_ready_merchant/db/`)
- [x] Optimistic concurrency primitive & `OptimisticLockError` (`src/agent_ready_merchant/db/concurrency.py`)
- [x] 12 Canonical SQLAlchemy domain models with CHECK constraints (`src/agent_ready_merchant/models/`)
- [x] Domain validation schemas in Pydantic v2 (`src/agent_ready_merchant/schemas/`)
- [x] Alembic configuration & initial migration script (`alembic/versions/001_initial_schema.py`)
- [x] FastAPI application bootstrap & health check (`src/agent_ready_merchant/main.py`)
- [x] 21 Comprehensive automated unit & integration tests (`tests/`)

---

## Phase 1.2 Readiness Gates

Before Phase 1.2 implementation begins:
1. Verify all 21 Phase 1.1 tests pass.
2. Confirm domain entity relationships and integer paise representation match `docs/domain-model.md`.
3. Confirm state transitions to be implemented match `docs/state-machines.md`.
