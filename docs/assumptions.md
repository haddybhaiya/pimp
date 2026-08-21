# Assumptions Registry: Agent-Ready Merchant

> **Assumption Policy:** Assume every external assumption can be wrong. Every critical assumption is tracked with evidence, confidence level, failure impact, mitigations, and verification requirements.

---

## Centralized Assumptions Ledger

### 1. Razorpay Test-Mode Currency & Amount Precision
- **ASSUMPTION:** Razorpay Orders and Payments APIs strictly expect integer paise and return exact integer amounts.
- **EVIDENCE:** Official Razorpay API Reference and standard Indian payments specifications.
- **CONFIDENCE:** 99%
- **FAILURE IF WRONG:** Monetary mismatch between order amount and payment amount, causing transaction failure or financial loss.
- **MITIGATION:** Strict Pydantic parsing with `int` types; reject any floating-point numbers at ingestion.
- **VERIFICATION REQUIRED:** Run integration test against Razorpay test API in Phase 1.

---

### 2. Webhook Arrival Ordering & Reliability
- **ASSUMPTION:** Razorpay webhooks may arrive delayed, out of chronological order, or drop completely due to network jitter.
- **EVIDENCE:** Distributed systems architecture across internet boundaries cannot guarantee strict FIFO delivery.
- **CONFIDENCE:** 95%
- **FAILURE IF WRONG:** Order state machine gets stuck in `PAYMENT_PROCESSING` or transitions incorrectly.
- **MITIGATION:** FSM terminal transitions are idempotent; out-of-band background polling reconciler runs every 60 seconds (`GET /v1/orders/{id}/payments`).
- **VERIFICATION REQUIRED:** Unit test FSM with reversed webhook event sequence (`payment.captured` before `order.paid`).

---

### 3. LLM JSON Schema Adherence & Adversarial Robustness
- **ASSUMPTION:** LLMs (Gemini) can be instructed to output valid JSON conforming to tool schemas, but will occasionally emit malformed JSON or hallucinate parameters under adversarial buyer input.
- **EVIDENCE:** Industry empirical observations with function calling and prompt injection attacks.
- **CONFIDENCE:** 90%
- **FAILURE IF WRONG:** Application crashes with unhandled deserialization errors or executes invalid tool parameters.
- **MITIGATION:** Schema validator wraps all LLM responses; validation errors feed back into a bounded retry loop (max 2 attempts); fallback refusal message returned if loop exceeds budget.
- **VERIFICATION REQUIRED:** Execute automated adversarial prompt fuzzing suite in Phase 1.

---

### 4. PostgreSQL Optimistic Locking Under High Concurrency
- **ASSUMPTION:** PostgreSQL row version checks (`WHERE id = :id AND version = :expected_version`) with `SELECT ... FOR UPDATE` are sufficient to prevent overselling on flash sales.
- **EVIDENCE:** Relational database ACID serializability guarantees.
- **CONFIDENCE:** 99%
- **FAILURE IF WRONG:** Inventory drops below zero, leading to unfulfillable orders.
- **MITIGATION:** Enforce database check constraints (`CHECK (available_quantity >= 0)`).
- **VERIFICATION REQUIRED:** Concurrency stress test with 50 parallel requests targeting a single inventory unit.
