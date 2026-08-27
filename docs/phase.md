# Phase Status & Roadmap: Agent-Ready Merchant

> **Current Phase:** Phase 3.2 (Payment Reliability Hardening)  
> **Status:** 100% COMPLETED & SIGNED OFF  
> **Next Milestone:** Phase 3.3 (Autonomous Merchant Optimization & Governance)

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
| **Phase 3.3** | Autonomous Merchant Optimization Agent & Control Plane | PLANNED | Revenue experiments, catalog auto-tuning, conversion analytics, merchant supervision |

---

## Phase 3.2 Deliverables Completed

- [x] Durable Webhook Deduplication backed by `ProcessedWebhook` database table with unique constraints (`uq_processed_webhooks_payload_hash`).
- [x] Webhook Replay Protection enforcing strict timestamp freshness windows against stale/future clock-skewed payloads (`WebhookTimestampError`).
- [x] Order Creation Retry Safety guaranteeing that successful remote Razorpay order mutations followed by local timeouts/crashes reuse the open remote order via receipt query (`fetch_order_by_receipt`) and durable breadcrumbs rather than creating blind duplicates.
- [x] Concurrency Serialization and Race Protection: `with_for_update()` row locking on `Order` and `PaymentAttempt` serializing concurrent webhooks and out-of-band reconciliations.
- [x] Transaction Ledger Uniqueness enforced by database unique constraint `uq_transaction_records_settlement_entry` on `(settlement_ref, entry_type)`.
- [x] Cryptographically Tamper-Evident Audit Event Hash Chaining with concurrency serialization per merchant and verification utility (`AuditEvent.verify_chain`).
- [x] Alembic Migration `004_payment_reliability` for PostgreSQL production deployments.
- [x] Dedicated 9-case adversarial, concurrency, and reliability test suite (`tests/test_phase3_2_payment_reliability.py`).



