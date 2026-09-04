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

---

## 5. Controlled Autonomy Invariants

1. **Reversible Low-Risk Scope Exclusivity (INV-AUT-01):**  
   Autonomous execution is strictly confined to 5 typed, reversible optimizations: `IMPROVE_PRODUCT_DESCRIPTION`, `IMPROVE_DISCOVERY_METADATA`, `REORDER_RECOMMENDATIONS`, `EXPOSE_DELIVERY_ETA`, `SUGGEST_BOUNDED_EXPERIMENT`. All other proposals require explicit human review or are rejected fail-closed.
2. **Financial & Policy Immutability by Autonomous Agents (INV-AUT-02):**  
   Autonomous agents cannot alter floor prices, modify profit margins, increase discount ceilings, alter transaction limits, change rule hashes, grant capabilities, or execute direct payments/refunds. Any such action is classified `PROHIBITED` and fails closed.
3. **Deterministic 18-Precondition Gating (INV-AUT-03):**  
   No autonomous mutation can occur without passing all 18 server-authoritative precondition checks sequentially (Actor Authority $\to$ Merchant State $\to$ Kill Switch $\to$ Anomaly State $\to$ Evidence Validation $\to$ Allowlist $\to$ Rule Classification $\to$ Rule Integrity Hash $\to$ Hourly Limit $\to$ Daily Limit $\to$ Cooldown $\to$ Resource Ownership $\to$ Optimistic Lock Version $\to$ Pre-mutation Snapshot $\to$ Idempotency Claim $\to$ Action Gateway Mutation $\to$ Ledger Persistence $\to$ Audit Logging).
4. **Master Kill Switch Precedence (INV-AUT-04):**  
   When the merchant master kill switch is activated (`kill_switch_enabled = True`), all pending autonomous executions are immediately rejected, and all active running experiments are safely stopped with `stopped_by_kill_switch: True`.
5. **Deterministic Rollback & Human Precedence (INV-AUT-05):**  
   Every autonomous action must store a lossless pre-mutation JSON snapshot. Rollback must restore that snapshot state version-checked. If a human merchant modified the entity after autonomous execution, rollback fails closed with `RollbackConflictError` and records `CONFLICT_REJECTED` status to guarantee human edits are never clobbered.
6. **Rate Limit, Quota & Cooldown Bounding (INV-AUT-06):**  
   Hourly budgets [1, 100], daily budgets [1, 1000], and cooldown durations [0, 86400s] are enforced server-side against committed ledger history. Any request exceeding rate limits or cooldown periods is rejected fail-closed.
7. **Idempotency & Tenant Integrity (INV-AUT-07):**  
   All autonomous executions and rollbacks require unique idempotency keys claimed via `MerchantMutationIdempotencyService`. Composite foreign keys enforce tenant isolation across merchants, proposals, actions, and experiments.

---

## 6. Discovery Network Invariants

1. **Descriptive Exclusivity (INV-DISC-01):**  
   Discovery endpoints and public capability graphs are strictly descriptive and read-only. Discovery never grants capability invocation rights, initializes buyer sessions, reserves inventory, creates binding quotes, generates orders, or initiates financial transactions.
2. **Zero Secret & PII Leakage (INV-DISC-02):**  
   Public merchant discovery profiles and search responses must never expose Razorpay keys, webhook secrets, session tokens, merchant/product database IDs, credentials, private policies, floor prices, internal margins, audit logs, or customer PII. Strict allowlisting exposes only an opaque discovery-profile ID and merchant-scoped public SKUs.
3. **Anti-Probing Uniform 404 (INV-DISC-03):**  
   Direct lookups on merchants in non-discoverable states (`PRIVATE`, `PAUSED`, `SUSPENDED`) and non-existent merchant IDs must return an identical, uniform 404 response (`MerchantNotFoundError`) to prevent merchant existence or state probing.
4. **Human-Only Discoverability Authority (INV-DISC-04):**  
   Discoverability state transitions and public discovery metadata modifications require authenticated human `MERCHANT_ADMIN` authorization. Autonomous agents, merchant LLMs, and external buyers fail closed.
5. **Deterministic Matching, Bounded Discovery, & Integer Budget Safety (INV-DISC-05):**
   Buyer intent evaluation, capability filtering, delivery region matching, available-inventory checks, and price range checks are completely deterministic. Search evaluates a bounded cursor page (at most 50 merchant candidates and 20 public product summaries per merchant); budget checks enforce the integer ceiling `min_var_paise * qty <= maximum_budget_paise`. Unsupported capabilities, unavailable inventory, and non-deliverable regions fail closed.
6. **Prompt Injection Search-Keyword Neutralization (INV-DISC-06):**  
   Buyer discovery queries and preference parameters are treated strictly as untrusted literal search text. Prompt injection instructions never influence ranking scores, bypass eligibility filters, modify policies, or trigger model execution.
7. **Replay-Safe Telemetry & Public Rate Limiting (INV-DISC-07):**  
   Discovery search and profile telemetry enforce composite database uniqueness on `(merchant_id, event_type, correlation_id)` to prevent replay distortion. Public discovery search is strictly rate-limited (60 requests/minute per client IP) to protect system compute.
8. **Replay-Safe Discovery Handoff (INV-DISC-08):**
   A discovery handoff claims a durable merchant-scoped idempotency receipt before creating a buyer session. Retried handoffs replay the original session response and never persist or re-expose a server-generated raw buyer token.


