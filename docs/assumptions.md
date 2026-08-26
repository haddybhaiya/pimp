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

