# Phase Status & Roadmap: Agent-Ready Merchant

> **Current Phase:** Phase 3.1 (Razorpay Payment Boundary & Invariant Hardening)  
> **Status:** 100% COMPLETED & SIGNED OFF  
> **Next Milestone:** Phase 3.2 (Autonomous Merchant Optimization & Governance)

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
| **Phase 3.2** | Autonomous Merchant Optimization Agent & Control Plane | PLANNED | Revenue experiments, catalog auto-tuning, conversion analytics, merchant supervision |

---

## Phase 3.1 Deliverables Completed

- [x] Authoritative Razorpay order/payment lifecycle with strict server verification.
- [x] Server-authoritative amount and currency validation with tamper-evident audit events (`PAYMENT_AMOUNT_FRAUD_DETECTED`, `PAYMENT_CURRENCY_FRAUD_DETECTED`).
- [x] Strict payment/order/transaction binding (`OrderMismatchError`, `TransactionBindingError`) preventing cross-order or uncaptured settlement.
- [x] PaymentAttempt and Order state regression prevention (`STATE_REGRESSION_IGNORED`, `STATE_REGRESSION_REJECTED`).
- [x] Razorpay adapter error normalization (`RazorpayBadRequestError`, `RazorpayNotFoundError`, `RazorpayRateLimitError`, `RazorpayServerError`) with typed retryability flags.
- [x] Safe reconciliation handling network/timeout failures without false payment success.
- [x] Concurrent race handling between webhooks and out-of-band reconciliation with optimistic lock deduplication (`DUPLICATE_IGNORED`).
- [x] Dedicated 12-case deterministic test suite (`tests/test_phase3_1_razorpay_boundary.py`).


