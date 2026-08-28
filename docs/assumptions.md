# Assumptions Registry: Agent-Ready Merchant

> **Assumption Policy:** Assume every external assumption can be wrong. Every critical assumption is tracked with evidence, confidence level, failure impact, mitigations, and verification requirements.

---

## Centralized Assumptions Ledger

### 1. Razorpay Test-Mode Currency & Amount Precision
- **ASSUMPTION:** Razorpay Orders and Payments APIs strictly expect integer paise and return exact integer amounts.
- **EVIDENCE:** Verified against live Razorpay sandbox and mock suite (`tests/test_razorpay_live_testmode.py`, `tests/test_razorpay_boundary_verification.py`).
- **STATUS:** **VERIFIED (PASS)**
- **CONFIDENCE:** 100%
- **FAILURE IF WRONG:** Monetary mismatch between order amount and payment amount, causing transaction failure or financial loss.
- **MITIGATION:** Strict Pydantic parsing with `int` types; reject any floating-point numbers at ingestion.

---

### 2. Webhook Arrival Ordering & Reliability
- **ASSUMPTION:** Razorpay webhooks may arrive delayed, out of chronological order, or drop completely due to network jitter.
- **EVIDENCE:** Tested out-of-band reconciliation and duplicate burst scenarios (`tests/test_concurrency_and_idempotency.py`, `tests/test_deliberate_failures_matrix.py`).
- **STATUS:** **VERIFIED (PASS)**
- **CONFIDENCE:** 100%
- **FAILURE IF WRONG:** Order state machine gets stuck in `PAYMENT_PROCESSING` or transitions incorrectly.
- **MITIGATION:** FSM terminal transitions are idempotent; out-of-band background polling reconciler recovers dropped events (`GET /v1/orders/{id}/payments`).

---

### 3. LLM JSON Schema Adherence & Adversarial Robustness
- **ASSUMPTION:** LLMs (Groq / Provider-agnostic) can be instructed to output valid JSON conforming to tool schemas, but will occasionally emit malformed JSON or hallucinate parameters under adversarial buyer input.
- **EVIDENCE:** Tested malformed retry recovery and prompt injection defense in `tests/test_deliberate_failures_matrix.py` and `tests/test_security_and_prompt_injection.py`.
- **STATUS:** **VERIFIED (PASS)**
- **CONFIDENCE:** 100%
- **FAILURE IF WRONG:** Application crashes with unhandled deserialization errors or executes invalid tool parameters.
- **MITIGATION:** Schema validator wraps all LLM responses; validation errors feed back into bounded retry loop (max 2 attempts); fallback refusal message returned if loop exceeds budget. All tools gated server-side.

---

### 4. Relational Optimistic Locking Under High Concurrency
- **ASSUMPTION:** Row version checks (`WHERE id = :id AND version = :expected_version`) ensure transactional integrity and prevent stale writes or duplicate commitments.
- **EVIDENCE:** Verified via `tests/test_optimistic_concurrency.py` and `tests/test_deliberate_failures_matrix.py` (`OptimisticLockError`).
- **STATUS:** **VERIFIED (PASS)**
- **CONFIDENCE:** 100%
- **FAILURE IF WRONG:** Inventory drops below zero or duplicate transaction records are committed.
- **MITIGATION:** Enforce database check constraints and version-checked atomic mutations.

---

### 5. Multi-Entity Razorpay Payment Binding & Currency Isolation
- **ASSUMPTION:** External payment webhook entities may originate from spoofed or cross-tenant sources, requiring cryptographic verification, currency validation, and strict payment attempt to order ledger binding.
- **EVIDENCE:** Verified via `tests/test_phase3_1_razorpay_boundary.py` (all 12 boundary test scenarios passing deterministically).
- **STATUS:** **VERIFIED (PASS)**
- **CONFIDENCE:** 100%
- **FAILURE IF WRONG:** Cross-order payment appropriation, currency spoofing (e.g. paying in USD for an INR order), or committing transaction records without captured payment attempts.
- **MITIGATION:** `CurrencyMismatchFraudError`, `OrderMismatchError`, and `validate_transaction_binding` raising `TransactionBindingError` fail-closed with audit event logging before committing to ledger.

---

### 6. Durable Webhook Deduplication, Replay Windows & External Order Recovery
- **ASSUMPTION:** Network jitter, provider retries, or local server crashes after remote API mutations can cause concurrent duplicate webhooks, stale replay attacks, or blind duplicate order creation on retry. Process-local locks are insufficient in distributed deployments.
- **EVIDENCE:** Verified via `tests/test_phase3_2_payment_reliability.py` (all 9 reliability, concurrency, and adversarial scenarios passing).
- **STATUS:** **VERIFIED (PASS)**
- **CONFIDENCE:** 100%
- **FAILURE IF WRONG:** Duplicate customer charges, replay of stale payment webhooks, split-brain audit hash chains, or double-entry credits in transaction ledger.
- **MITIGATION:** Canonical `ProcessedWebhook` database table with unique constraint on `payload_hash`, timestamp freshness validation (24h replay window), `uq_transaction_records_settlement_entry` database constraint, receipt-based external order recovery (`RazorpayClient.fetch_order_by_receipt`), and tenant row-level locking for cryptographic audit chain verification.

---

### 7. Hermetic End-to-End Testability via Deterministic Fake Transports
- **ASSUMPTION:** The complete commerce flow (discovery -> quote -> reservation -> payment -> reconciliation -> audit) and edge failure modes can be verified deterministically without external live Razorpay sandbox dependencies by substituting the HTTP transport layer with an in-memory transport adhering strictly to the Razorpay protocol and HMAC signatures.
- **EVIDENCE:** Verified via `tests/test_phase3_3_end_to_end_verification.py` (all 17 end-to-end scenarios passing, including network timeout-after-save, dropped webhooks, inventory races, fraud detection, and cross-session isolation).
- **STATUS:** **VERIFIED (PASS)**
- **CONFIDENCE:** 100%
- **FAILURE IF WRONG:** False confidence due to transport diverging from live Razorpay API behavior.
- **MITIGATION:** Fake transport implements real HMAC SHA-256 signatures, exact payload structures, and receipt querying matching the real Razorpay API contract.

---

### 8. Server-Authoritative Identity, Capability Derivation & Anti-Resource Existence Probing
- **ASSUMPTION:** Client callers and external AI agents cannot be trusted to self-declare capabilities (`X-Capabilities`) or access resources without server-authoritative authentication and multi-tenant session binding. Probing entity existence across tenants must return generic not-found errors rather than descriptive authorization denial messages.
- **EVIDENCE:** Verified via `tests/test_phase4_1_security_and_authorization.py` (all 12 adversarial test cases passing deterministically).
- **STATUS:** **VERIFIED (PASS)**
- **CONFIDENCE:** 100%
- **FAILURE IF WRONG:** Privilege escalation via forged capability headers, cross-tenant quote/order snooping via UUID guessing, or timing attacks on token verification.
- **MITIGATION:** Constant-time `hmac.compare_digest` token verification against SHA-256 hashes, server-authoritative capability intersection against `BuyerAgentSession.granted_capabilities`, mandatory session gates for privileged/stateful operations, and uniform `QUOTE_NOT_FOUND` / `ORDER_NOT_FOUND` error masking.
