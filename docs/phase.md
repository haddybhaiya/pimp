# Phase Status & Roadmap: Agent-Ready Merchant

> **Current Phase:** Phase 7 (Merchant Agent — Intelligence & Optimization Layer)  
> **Status:** 100% COMPLETED & SIGNED OFF  
> **Milestone Status:** Phase 1–5 Complete, Phase 6 Skipped (Satisfied), Phase 7 Complete

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
| **Phase 6** | Autonomous Negotiation Layer | **SKIPPED — FUNCTIONALITY SATISFIED BY EARLIER PHASES** | Counter-offer evaluation, floor price enforcement, margin protections, and HITL escalations fully implemented and verified in Phases 1–5 |
| **Phase 7** | Merchant Agent (Intelligence & Optimization Layer) | **COMPLETED** | Live commerce observation matrix, diagnostic finding engine, evidence-backed proposal generation, server risk governance, approval-first experiment framework, deterministic measurement |

---

## Phase 7 Deliverables Completed

- [x] **Authoritative Merchant Observation Layer (`MerchantAgentService.build_authoritative_observations`):**
  - Collects live commerce telemetry from PostgreSQL directly (sessions, intents, quotes, orders, payments, approvals, inventory).
  - Explicitly categorizes telemetry into `OBSERVED`, `DERIVED`, and `ESTIMATED`.
  - Enforces strict tenant scoping (`merchant_id`).
  - Zero fabricated telemetry; integer paise representation for monetary metrics.
- [x] **Bounded Intelligence Snapshot & Delimited Prompts:**
  - Packages tenant metadata, active policies, catalog stats, telemetry metrics, context signals, and recent experiments.
  - Zero credentials, secrets, or buyer PII exposed to LLM context (`INV-AGY-03`).
- [x] **Diagnostic Finding Engine:**
  - Structured output diagnosing recurring friction patterns (`REPEATED_DELIVERY_QUESTIONS`, `MISSING_PRODUCT_INFO`, `CHECKOUT_FRICTION`, `INVENTORY_LOST_DEMAND`, etc.).
  - Explicit evidence references linked to actual telemetry metrics.
- [x] **Evidence-Backed Proposal Generation:**
  - Generates structured proposals (`IMPROVE_PRODUCT_DESCRIPTION`, `EXPOSE_DELIVERY_ETA`, `REORDER_RECOMMENDATIONS`, `IMPROVE_DISCOVERY_METADATA`, `SUGGEST_BUNDLE`, `SUGGEST_PROMOTIONAL_OFFER`, `SUGGEST_BOUNDED_EXPERIMENT`).
  - Strict Pydantic schema validation (`MerchantProposalCreate`).
- [x] **Server-Authoritative Risk & Governance Classification (`govern_and_classify_proposal`):**
  - Prohibits unauthorized actions (`PROHIBITED`): attempts to alter policy, modify floor prices, grant capabilities, or execute direct payments/refunds.
  - Classifies low-risk reversible proposals as `LOW_RISK_REVERSIBLE` and promotional offers as `APPROVAL_REQUIRED`.
- [x] **Approval-First Experiment Framework (`MerchantExperiment`, `MerchantExperimentResult`):**
  - Durable database models and migrations `008_merchant_agent_and_experiments.py` and `009_merchant_agent_runs.py`.
  - Complete lifecycle: `DRAFT` / `PROPOSED` $\to$ `APPROVAL_REQUIRED` $\to$ `APPROVED` $\to$ `COMPLETED` / `ROLLED_BACK`.
  - Phase 7 does NOT autonomously execute production changes (strictly reserved for Phase 8).
- [x] **Deterministic Experiment Measurement Engine:**
  - Computes post-experiment metrics, absolute change, percentage change, and sample sizes strictly from database observations over equal, fixed 30-day baseline and post-approval windows.
  - Refuses early evaluation rather than persisting a recommendation from an incomplete post-approval window.
  - Deterministically recommends `KEEP`, `ROLLBACK`, or `INCONCLUSIVE` (based on sample size $\ge 5$ and delta thresholds).
  - Rejects ungrounded model evidence, measures only post-approval observations, and database-constrains one deterministic result per experiment.
- [x] **Web Control Plane Integration:**
  - Dedicated Merchant Agent optimization hub (`frontend/src/pages/agent.tsx`) and Experiments workbench (`frontend/src/pages/experiments.tsx`).
  - Full API endpoints (`/api/v1/merchant/agent/*`, `/api/v1/merchant/experiments/*`) protected by `_require_merchant_auth`.
- [x] **Cryptographic Audit Ledger Linkage:**
  - Logs immutable SHA-256 audit events for `MERCHANT_AGENT_RUN_COMPLETED`, `MERCHANT_PROPOSAL_REVIEWED`, `MERCHANT_EXPERIMENT_CREATED`, `MERCHANT_EXPERIMENT_APPROVED`, `MERCHANT_EXPERIMENT_EVALUATED`.
- [x] **Comprehensive Test Suite & Quality Gate Compliance:**
  - 10 comprehensive tests in `tests/test_phase7_merchant_agent.py` covering multi-tenant scoping, evidence validation, adversarial prompt injection safety, proposal governance, and deterministic experiment evaluation.
  - 100% clean passes on Ruff, Mypy strict, Vitest, and Pytest.
