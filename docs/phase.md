# Phase Status & Roadmap: Agent-Ready Merchant

> **Current Phase:** Phase 1.0 (Engineering CI Foundation)  
> **Status:** 100% COMPLETED & SIGNED OFF  
> **Next Sub-Phase:** Phase 1.1 (Core Domain Models & PostgreSQL Migrations)

---

## Phase Breakdown & Status

| Phase / Milestone | Description | Status | Scope Cut Line |
|---|---|---|---|
| **Phase 0** | System Architecture, Domain Model, State Machines, Threat Model, Invariants, Evaluation Framework & Contracts | **COMPLETED** | No application/payment/LLM implementation code |
| **Phase 1.0** | Engineering CI Foundation (GitHub Actions, Ruff, Mypy, Pytest, Secret Scan) | **COMPLETED** | CI pipeline, minimal tooling configs, smoke tests only |
| **Phase 1.1** | Core Domain Models, PostgreSQL Migrations & Database Constraints | PLANNED | SQLAlchemy models, Alembic, integer paise columns |
| **Phase 1.2** | Deterministic Policy Engine & Authoritative State Machines | PLANNED | Pure Python FSMs, pricing floor guards, 100% test coverage |
| **Phase 1.3** | Server-Authoritative Razorpay Client & Webhook Receiver | PLANNED | HMAC SHA-256 verification, orders API, payment capture |
| **Phase 1.4** | Untrusted Intelligence Layer (Gemini Adapter & Tool Gateway) | PLANNED | Pydantic tool contracts, prompt delimiters, rate limits |
| **Phase 1.5** | End-to-End Golden Path & Deliberate Failure Verification | PLANNED | Integration tests demonstrating E2E transactability & recovery |
| **Phase 2** | Merchant Supervision & Control Plane (UI) | PLANNED | React + TypeScript Dashboard, Live Session Observability |
| **Phase 3** | Autonomous Merchant Optimization Agent | PLANNED | Revenue experiments, catalog auto-tuning, conversion analytics |

---

## Phase 1.0 Deliverables Completed

- [x] GitHub Actions CI Pipeline (`.github/workflows/ci.yml`)
- [x] Pinned build configuration and tool metadata (`pyproject.toml`)
- [x] Codebase layout initialization (`src/agent_ready_merchant/`, `tests/`)
- [x] CI Smoke verification test suite (`tests/test_ci_smoke.py`)
- [x] Project documentation overview (`README.md`)
- [x] Architectural Decision Record for CI ([ADR-006](decisions.md#adr-006-ci-tooling--engineering-quality-standards))
- [x] Secret scanning and untracked environment file verification
- [x] Local verification passing (Ruff lint, Ruff format, Mypy strict, Pytest)

---

## Phase 1.1 Readiness Gates

Before Phase 1.1 implementation begins:
1. Verify CI passes on push/pull-request.
2. Confirm PostgreSQL connection string in `.env` / test environment.
3. Validate schema types against `docs/domain-model.md`.
