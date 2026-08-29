# System & Security Invariants: Agent-Ready Merchant

> **Core Doctrine:** Invariants are non-negotiable architectural truths. Any code, tool, or agent proposal that violates an invariant must be rejected deterministically.

---

## 1. Financial & Monetary Invariants

1. **Integer Paise Representation (INV-FIN-01):**  
   All monetary amounts (prices, discounts, shipping fees, tax, transaction totals) are strictly stored and computed as non-negative 64-bit integers in the smallest currency unit (paise for INR). Floating-point monetary arithmetic is strictly prohibited across all services.
2. **Floor Price Guarantee (INV-FIN-02):**  
   No price quote or order can ever be created with a unit price below $\max(P_{\text{floor\_sku}}, P_{\text{cost}} \times (1 + M_{\text{min}}))$.
3. **Discount Ceiling (INV-FIN-03):**  
   No discount can exceed the merchant's configured `max_discount_percentage`.
4. **Idempotent Side Effects (INV-FIN-04):**  
   Every state-mutating or payment-affecting API request must require an `Idempotency-Key` or derive a deterministic hash key. Replaying an identical request must yield the original result without duplicate side effects.
5. **Server-Authoritative Settlement (INV-FIN-05):**  
   Payment success is established ONLY via cryptographically verified Razorpay Webhooks (HMAC SHA-256) or direct server-to-server REST fetches. Client-side success reports are never authoritative.

---

## 2. Intelligence & Authority Invariants

1. **Intelligence $\neq$ Authority (INV-AGY-01):**  
   The LLM is an untrusted reasoning engine. It produces intent proposals, never direct database mutations, credential access, or financial side effects.
2. **Deterministic Gating Pipeline (INV-AGY-02):**  
   Every agent tool call must sequentially pass Schema Validation $\to$ State Machine Precondition Check $\to$ Deterministic Policy Validation $\to$ Capability Check $\to$ Action Gateway.
3. **Zero Secret Leakage (INV-AGY-03):**  
   Razorpay API keys, HMAC secrets, database credentials, and internal encryption keys must NEVER be placed in LLM system prompts, tool schemas, or context windows.
4. **Bounded Agent Execution (INV-AGY-04):**  
   An agent run cannot exceed 5 recursive tool calls, 8,192 tokens of context, or 15 seconds of execution wall-clock time per turn.
5. **No Self-Privilege Escalation (INV-AGY-05):**  
   The agent has zero tools to alter merchant policies, change floor prices, or grant itself new execution capabilities.

---

## 3. State Machine Invariants

1. **Legal State Transitions Only (INV-STA-01):**  
   An entity can only transition through explicitly declared edges in its finite state machine. Invalid transitions throw an unrecoverable `IllegalStateTransitionError`.
2. **Optimistic Locking Integrity (INV-STA-02):**  
   Every state modification query must assert the expected entity `version` (`WHERE id = :id AND version = :expected_version`) to eliminate race conditions.
3. **Non-Negative Inventory (INV-STA-03):**  
   `available_quantity` and `reserved_quantity` on any SKU can never be $< 0$.
4. **Quote Expiry Enforcement (INV-STA-04):**  
   An expired quote (`now() > expires_at`) cannot be accepted, converted into an order, or paid.
5. **Immutable Financial Ledger (INV-STA-05):**  
   `transaction_records` and `audit_events` tables are strictly append-only. `UPDATE` and `DELETE` queries are prohibited at the database role level.

---

## 4. Safety, Policy & Governance Invariants

1. **Deterministic Policy Hashing (INV-GOV-01):**  
   Every policy decision evaluated for a consequential commerce action must generate and record an immutable, deterministic SHA-256 policy hash (`policy_hash`) and policy version (`policy_version`) in the audit log. Future policy modifications must never alter or invalidate historical audit interpretations.
2. **Platform Safety Ceilings (INV-GOV-02):**  
   Platform safety bounds are non-negotiable hard ceilings: maximum 20 items per quote, absolute 50% discount ceiling, ₹1,00,000 (10,000,000 paise) single transaction limit, and maximum 3 negotiation rounds per quote.
3. **Fail-Closed Human-In-The-Loop Approval Gates (INV-GOV-03):**  
   Any action requiring human approval (e.g. Autonomy Level 2 Supervised HITL or discount escalation) must generate a stateful, expiring `MerchantApproval` record. Expired, forged, or cross-tenant approvals must fail closed deterministically.
4. **Audit Cryptographic Integrity & Sanitization (INV-GOV-04):**  
   Every audit event must be linked in an unbroken cryptographic SHA-256 hash chain verified via `AuditEvent.verify_chain()`. All secrets, tokens, credentials, and buyer PII (email addresses) must be sanitized and masked before being committed to the immutable audit ledger.

