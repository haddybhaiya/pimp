# Phase Status & Roadmap: Agent-Ready Merchant

> **Current Phase:** Phase 2.3 (Protocol Boundary + Production-Grade Demo Hardening)  
> **Status:** 100% COMPLETED & SIGNED OFF  
> **Next Milestone:** Phase 3.0 (Autonomous Merchant Optimization & Governance Dashboard)

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
| **Phase 3** | Autonomous Merchant Optimization Agent & Control Plane | PLANNED | Revenue experiments, catalog auto-tuning, conversion analytics, merchant supervision |

---

## Phase 2.3 Deliverables Completed

- [x] Protocol-neutral external API boundary (`src/agent_ready_merchant/protocols/base.py`):
  * Replaceable `BaseProtocolAdapter` interface with bidirectional schema mapping.
- [x] Agent Commerce Protocol (ACP) Adapter (`src/agent_ready_merchant/protocols/acp.py`):
  * Full translation for all canonical capabilities with strict version negotiation (`2026-03-01`).
- [x] Protocol Agent Client (`src/agent_ready_merchant/protocols/client.py`):
  * Autonomous client operating strictly via protocol wire messages with safe retry policies.
- [x] Production-grade hardening infrastructure (`src/agent_ready_merchant/gateway/hardening.py`):
  * Hierarchical error codes (`GatewayErrorCode`), thread-safe `IdempotencyManager`, sliding-window `GatewayRateLimiter`, 64 KB payload bounds, timeout boundary guards, structured observability, and zero secret/DB leakage error sanitization.
- [x] Protocol wire endpoint on FastAPI (`POST /api/v1/protocol/acp` in `src/agent_ready_merchant/main.py`).
- [x] Comprehensive test suite (`tests/test_phase2_3_protocol_and_hardening.py`):
  * 150 passed automated tests across entire repository (Phase 1, Phase 2.1, Phase 2.2, Phase 2.3).
  * Quality gates passed: `ruff check .`, `ruff format --check .`, `mypy src tests`, `pytest`.

