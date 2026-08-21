# Phase Status & Roadmap: Agent-Ready Merchant

> **Current Phase:** Phase 0 (Architecture, Contracts, Invariants, Governance & Threat Modeling)  
> **Status:** 100% COMPLETED & SIGNED OFF  
> **Next Phase:** Phase 1 (Core Domain, State Machines, Policy Engine & Razorpay Client)

---

## Phase Summary

| Phase | Description | Status | Scope Cut Line |
|---|---|---|---|
| **Phase 0** | System Architecture, Domain Model, State Machines, Threat Model, Invariants, Evaluation Framework & Contracts | **COMPLETED** | No application/payment/LLM implementation code |
| **Phase 1** | Deterministic Core & Golden Path MVP | **READY TO START** | Domain models, FSMs, Policy Engine, Razorpay Client, LLM Gateway, Test Suite |
| **Phase 2** | Merchant Supervision & Control Plane (UI) | PLANNED | React + TypeScript Dashboard, Live Session Observability, HITL approvals |
| **Phase 3** | Autonomous Merchant Optimization Agent | PLANNED | Revenue experiments, catalog auto-tuning, conversion analytics |

---

## Phase 0 Deliverables Matrix

- [x] Mandatory Agent Engineering Operating Contract (`skills.md`)
- [x] Canonical System Architecture (`docs/architecture.md`)
- [x] Canonical Domain Entity Model (`docs/domain-model.md`)
- [x] Authoritative State Machines (`docs/state-machines.md`)
- [x] Agent Intelligence Boundary Contract (`docs/agent-contract.md`)
- [x] Typed Tool RPC Catalog & Schemas (`docs/tool-contract.md`)
- [x] Deterministic Policy Engine Model (`docs/policy-model.md`)
- [x] STRIDE Threat Model & Mitigations (`docs/threat-model.md`)
- [x] Failure Taxonomy & Recovery Sagas (`docs/failure-model.md`)
- [x] Razorpay Test-Mode Integration Notes (`docs/razorpay-integration-notes.md`)
- [x] MVP Golden Path & Acceptance Contract (`docs/mvp-contract.md`)
- [x] Hard System Invariants (`docs/invariants.md`)
- [x] Architectural Decision Records (`docs/decisions.md`)
- [x] Centralized Assumptions Registry (`docs/assumptions.md`)
- [x] Objective Evaluation Framework (`docs/evaluation.md`)

---

## Phase 1 Readiness Gates

Before Phase 1 implementation begins:
1. Verify Python 3.11+ / 3.12 environment with `FastAPI`, `SQLAlchemy` (or `SQLModel`), `Pydantic v2`, and `pytest`.
2. Confirm Razorpay test-mode API key pairs (`rzp_test_...` and secret).
3. Confirm Gemini API key availability for LLM adapter testing.
4. Pass Evaluation Gate Readiness Check (`docs/evaluation.md`).
