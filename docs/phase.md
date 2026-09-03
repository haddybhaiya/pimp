# Phase Status & Roadmap: Agent-Ready Merchant

> **Current Phase:** Phase 8 (Controlled Autonomy)  
> **Status:** 100% COMPLETED & SIGNED OFF  
> **Milestone Status:** Phases 1–5 Complete, Phase 6 Skipped (Satisfied), Phase 7 Complete, Phase 8 Complete  
> **Next Scope Cut Line:** Phase 8 is the final phase of this project. Phase 9 (Discovery Network) is strictly OUT OF SCOPE.

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
| **Phase 8** | Controlled Autonomy | **COMPLETED** | Low-risk reversible optimizations (`IMPROVE_PRODUCT_DESCRIPTION`, `IMPROVE_DISCOVERY_METADATA`, `REORDER_RECOMMENDATIONS`, `EXPOSE_DELIVERY_ETA`, `SUGGEST_BOUNDED_EXPERIMENT`), Master Kill Switch, 18 pre-condition gates, rate limits & cooldowns, deterministic rollback engine |
| **Phase 9** | Discovery Network | **OUT OF SCOPE** | DO NOT IMPLEMENT. Strictly out of scope. |

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
  - Durable database models and migrations `008_merchant_agent_and_experiments.py`, `009_merchant_agent_runs.py`, and `010_phase7_integrity.py`.
  - Composite tenant foreign keys keep proposal-to-run and result-to-experiment links within the same merchant; server-owned demo-product provenance cannot be set through catalog input.
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
- [x] **Review Remediation Boundaries:**
  - Phase 7 mutations use durable idempotency receipts; the audit ledger uses keyset pagination to avoid duplicates or omissions while new events arrive.
  - Malformed structured model payloads degrade to no new intelligence action; scalar and list values are normalized across snake_case, plurals, and camelCase before explicit prohibited-command screening, without rejecting benign commerce terms.
  - Quote conversion is reconstructed from append-only credit-ledger evidence as-of each bounded observation endpoint, preventing later settlements or order updates from biasing historical experiment cohorts.
- [x] **Comprehensive Test Suite & Quality Gate Compliance:**
  - 18 comprehensive tests in `tests/test_phase7_merchant_agent.py` covering multi-tenant scoping, evidence validation, adversarial prompt injection safety, proposal governance, deterministic experiment evaluation, bounded windows, replay-safe mutations, and historical conversion cohorts.
  - 100% clean passes on Ruff, Mypy strict, Vitest, and Pytest.

---

## Phase 8 Deliverables Completed

- [x] **Entry Gate Governance Hardening (`MerchantAgentService.govern_and_classify_proposal`):**
  - Prohibits hidden financial, policy, and authority escalation attacks across scalar, list, and nested object fields.
  - Detects object-first actions (e.g. `autonomy_increase`, `policy_override`, `capability_grant`), direct action values, and inflected verb-object phrases.
  - Evaluates both `metadata` and `metadata_payload` structured action envelopes fail-closed.
  - Preserves reviewability of legitimate commerce terms (`loyalty credits`, `shipping charges`, `refundable`, `credit score`, `delivery policy description`).
- [x] **Database Models & Alembic Migrations 011–014 (`011_phase8_controlled_autonomy.py` through `014_autonomy_failure_telemetry.py`):**
  - Added `merchants.kill_switch_enabled` boolean column.
  - Created `merchant_autonomy_rules` table with deterministic SHA-256 rule hashing, unique composite constraints `(merchant_id, action_type)`, hourly limit bounds [1, 100], and daily limit bounds [1, 1000].
  - Created `merchant_autonomy_actions` ledger with snapshot storage, composite foreign keys to `merchant_experiments(id, merchant_id)` and `merchant_proposals(id, merchant_id)`; proposal deletion clears only the optional `proposal_id` and preserves the tenant-scoped action history.
  - Added a separate, tenant-scoped rejected-execution ledger. Gate failures and optimistic conflicts are auditable inputs to the rolling one-hour anomaly circuit breaker, while successful-action history and execution budgets remain unchanged.
- [x] **Authoritative 18-Precondition Gate Pipeline (`ControlledAutonomyService.execute_autonomous_action`):**
  - Pre-execution validation enforcing: (1) Actor authority, (2) Active merchant state, (3) Master kill-switch check, (4) Anomaly state evaluation, (5) Evidence-backed proposal existence and tenant ownership, (6) Typed action allowlist, (7) Rule enablement and `AUTO_LOW_RISK` classification, (8) Rule version & SHA-256 hash integrity, (9) Hourly rate limit budget, (10) Daily rate limit budget, (11) Cooldown period elapsed, (12) Target resource existence and tenant ownership, (13) Optimistic target version checking, (14) Pre-mutation JSON snapshot generation, (15) Idempotency claim receipt, (16) Target atomic domain mutation, (17) Ledger record persistence, (18) Cryptographic audit event append.
  - Rules are provisioned disabled until an authenticated merchant administrator explicitly enables a typed action. Merchant, rule, proposal, target, and rollback rows are locked at the execution boundary to serialize kill-switch, quota, conflict, and target-version checks.
  - Product mutations require an explicitly identified tenant-owned product; targetless and Phase 7 `general` placeholder proposals fail closed rather than selecting an arbitrary catalog row.
- [x] **Master Kill Switch & Anomaly Controller:**
  - Fast-path kill-switch endpoint (`POST /api/v1/merchant/autonomy/kill-switch`) instantly blocking all autonomous mutations.
  - Safely halts all currently `RUNNING` experiments with `stopped_by_kill_switch: True` and appends immutable audit events.
  - Anomaly state detection (`EVALUATE_ANOMALY_STATE`) shifting to `REQUIRE_HUMAN_REVIEW` upon high execution failure rates ($\ge 3$ durably recorded failures/hour).
- [x] **Deterministic Reversible Rollback Engine (`rollback_action`):**
  - Reverts mutated resources back to exact pre-action snapshot state while asserting current target version equals expected post-action version.
  - Human Precedence Rule: If a human merchant modified the entity after autonomous execution, rollback fails closed with `RollbackConflictError` and records `rollback_status = CONFLICT_REJECTED`.
  - The rejected conflict state and its audit event are committed before HTTP 409 is returned for both direct action and delegated experiment rollbacks, so safety evidence is not lost to request rollback.
  - Idempotent: Repeated rollback calls return the cached rollback receipt safely.
  - Rolling back an autonomous experiment delegates to its linked autonomy-action rollback, restoring the captured target snapshot and reconciling both the experiment and ledger states.
- [x] **Web Control Plane Integration:**
  - Master Kill Switch card on Agent page with live status indicator and emergency trigger.
  - Controlled Autonomy Execution Rules management card on Policies page with toggle and limit views.
  - Autonomous Actions Ledger on Agent page with snapshot inspector dialog and one-click deterministic rollback dialog.
  - Experiments workbench `AUTO_ELIGIBLE` badge, Stop Experiment, and Rollback Variation controls.
- [x] **Comprehensive Test Suite & Quality Gate Compliance:**
  - 24 dedicated integration tests in `tests/test_phase8_controlled_autonomy.py` covering authority boundaries, prohibited attacks, explicit opt-in defaults, rejected-proposal execution blocking, approval-first experiment starts, budget/cooldown enforcement, durable failure anomaly detection, optimistic locking, kill switch pre-execution and running experiment halting, E2E Golden Path, targetless/placeholder mutation rejection, experiment rollback reconciliation and conflict durability, rollback conflict rejection, tenant isolation, idempotency replay, and REST endpoints.
  - 100% clean passes: 316 pytest tests passing, 31 frontend vitest tests passing, 0 Mypy errors across 141 source files, 0 Ruff errors.
- [x] **Phase Stop Boundary Enforced:**
  - Project execution stopped cleanly after Phase 8. Phase 9 (Discovery Network) is strictly OUT OF SCOPE.
