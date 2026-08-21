# System Architecture: Agent-Ready Merchant (Phase 0)

> **Core Thesis:** The LLM is untrusted intelligence. The application is the authority.  
> **Mission:** Enable ordinary merchants to become AI discoverable, understandable, negotiable, and safely transactable on Razorpay test-mode infrastructure.

---

## 1. Executive Architectural Overview

The Agent-Ready Merchant platform provides the bridge between autonomous AI buyer agents and a merchant's commercial operations. It transforms static catalogs, subjective negotiation limits, and payment interfaces into structured, machine-navigable, and deterministically guarded commerce endpoints.

```
       +-------------------------------------------------------------+
       |                     EXTERNAL UNTRUSTED WORLD                |
       |  +---------------------+        +------------------------+  |
       |  |  Autonomous AI      |        |  Human Merchant        |  |
       |  |  Buyer Agent / User |        |  Operator (Dashboard)  |  |
       |  +----------+----------+        +-----------+------------+  |
       +-------------|-------------------------------|---------------+
                     |                               |
=====================|===============================|======================
                     v                               v
       +-------------------------------------------------------------+
       |                 AGENT-READY MERCHANT PLATFORM               |
       |                                                             |
       |  [ 1. Discovery & Intent Gateway ]                          |
       |       - REST / JSON Discovery API                           |
       |       - Machine-Readable Capability Graph                   |
       |       - Context-Bounded System Prompts                      |
       |                                                             |
       |  [ 2. Untrusted Intelligence Layer (LLM Adapter) ]          |
       |       - Provider-Agnostic LLM Client (Gemini Default)       |
       |       - Natural Language Understanding & Negotiation Reas.  |
       |       - Generates Pydantic Structured Intent (NO SIDE EFF.) |
       |                                                             |
       |  [ 3. Deterministic Governance & Policy Engine ]            |
       |       - Strict Schema Validation                            |
       |       - State-Machine Precondition Validation               |
       |       - Floor Price & Max Discount Enforcement              |
       |       - Session Rate & Volume Limiters                      |
       |       - Human-in-the-Loop (HITL) Gatekeeper                 |
       |                                                             |
       |  [ 4. Action Gateway & Idempotency Coordinator ]            |
       |       - Idempotency Key Manager (Redis/Postgres Locked)     |
       |       - Transaction Outbox & Sagas                          |
       |       - Capability & Signature Checker                      |
       |                                                             |
       |  [ 5. Core Domain & Authoritative Ledger ]                  |
       |       - PostgreSQL (ACID State Authority)                   |
       |       - Append-Only Financial Transaction Ledger            |
       |       - Immutable Audit Log                                 |
       |                                                             |
       |  [ 6. External Integration Engine (Razorpay Adapter) ]      |
       |       - Server-Authoritative Razorpay API Client (Test-Mode)|
       |       - Secure Webhook Receiver (HMAC SHA-256 Auth)         |
       |       - Out-of-band Payment Reconciler                      |
       +-------------------------------------------------------------+
```

---

## 2. The Separation of Intelligence and Authority

The cardinal rule of this architecture is:

$$\text{Intelligence} \neq \text{Authority}$$

### Authority Separation Rules

1. **The LLM is a reasoning engine, not an execution engine.**  
   The LLM parses natural language, identifies customer preferences, searches semantic catalog indices, and drafts negotiation proposals. It has **zero direct access** to network sockets, database write handles, or payment credentials.
2. **Intent is not an Action.**  
   The model emits a `StructuredIntent` (e.g., `ProposeQuoteIntent`, `CreateOrderIntent`). This intent is treated as an untrusted proposal.
3. **Deterministic Verification Pipeline:**  
   Every intent must traverse the sequential validation pipeline before any state change or external call occurs:

```
+-----------------------------------------------------------------------------------+
|                        THE DETERMINISTIC PIPELINE                                 |
|                                                                                   |
|  [LLM Proposal]                                                                   |
|         |                                                                         |
|         v                                                                         |
|  1. [Schema Validation]             -> Rejects malformed JSON / type errors       |
|         v                                                                         |
|  2. [Authoritative State Check]     -> Verifies quote/order active in DB          |
|         v                                                                         |
|  3. [Deterministic Policy Engine]   -> Rejects margin/discount/limit violations   |
|         v                                                                         |
|  4. [Permission/Capability Check]   -> Verifies session role & allowed actions    |
|         v                                                                         |
|  5. [Risk & Idempotency Check]      -> Verifies rate limits & payload hash key    |
|         v                                                                         |
|  6. [Action Gateway Execution]      -> Atomically updates DB & invokes Razorpay   |
|         v                                                                         |
|  7. [Immutable Audit Emission]      -> Logs inputs, policies, and result          |
+-----------------------------------------------------------------------------------+
```

---

## 3. Layered Architectural Blueprint

### Layer 1: Ingestion & Discovery Interface
- **Role:** Exposes endpoints for buyer discovery and agent communication.
- **Components:**
  - `GET /.well-known/agent-readiness.json`: Machine-readable capability descriptor, terms of service, negotiation schema, and catalog index pointers.
  - `POST /api/v1/agent/session`: Initiates a buyer agent session, assigns cryptographic session tokens, and enforces rate limits.
  - `POST /api/v1/agent/chat`: Conversational commerce endpoint accepting natural language or structured tool calls.

### Layer 2: Untrusted Intelligence (LLM Orchestration)
- **Role:** Translates unstructured buyer queries into structured merchant domain queries; drafts negotiation counter-offers.
- **Provider Agnosticism:** Uses an abstract `LLMProviderInterface` with an initial concrete adapter for `Google Gemini (Gemini 2.5 / 3.x Flash/Pro)`.
- **System Boundaries:**
  - Operates strictly with read-only view schemas of products and policy boundaries.
  - Maximum context window capped at 8,192 tokens per run to prevent denial-of-wallet.
  - Step limit: Maximum 5 recursive tool calls per buyer request.

### Layer 3: Deterministic Policy Engine
- **Role:** Mathematical and rule-based gatekeeper.
- **Guarantees:**
  - No price can ever be offered below `product.cost_price * (1 + merchant_policy.min_margin)`.
  - No discount can exceed `merchant_policy.max_discount_percentage`.
  - No transaction can exceed `merchant_policy.max_single_transaction_amount`.
  - Evaluates rules via pure, deterministic Python functions with zero external I/O.

### Layer 4: State Machine & Transaction Authority
- **Role:** Authoritative state ledger managing entity lifecycles.
- **Components:**
  - `PostgreSQL 16+`: Master storage with ACID transactions and row-level locking (`SELECT ... FOR UPDATE`).
  - Strict State Machines for: `BuyerIntent`, `PriceQuote`, `Order`, `PaymentAttempt`, `TransactionRecord`, `AgentRun`.

### Layer 5: Action Gateway & External Integrations
- **Role:** Handles side-effecting operations against external providers.
- **Razorpay Adapter (Test Mode):**
  - Isolates API keys (`RZP_KEY_ID`, `RZP_KEY_SECRET`) in server memory.
  - Generates Razorpay Orders via HTTP Basic Auth.
  - Validates and ingests webhook payloads (`payment.authorized`, `payment.captured`, `payment.failed`, `order.paid`).
  - Verifies HMAC SHA-256 signatures before processing.

### Layer 6: Audit & Supervision Ledger
- **Role:** Immutably records every prompt, completion, tool call, policy evaluation, state transition, and payment event.
- **Design:** Append-only ledger table in PostgreSQL with SHA-256 hash chains to ensure tamper resistance.

---

## 4. Architectural Quality Bar: Evaluation of Critical Decisions

| # | Quality Bar Question | Architectural Decision & Guarantee |
|---|----------------------|------------------------------------|
| 1 | **What can go wrong?** | Model hallucinates non-existent discounts; network drops between platform and Razorpay; webhooks arrive delayed or out-of-order; buyer attempts replay attack. |
| 2 | **What happens if the model is wrong?** | Policy engine rejects the invalid output. Error is returned to the model with deterministic guidance; state remains untouched. |
| 3 | **What happens if the external API is unavailable?** | Circuit breaker trips; transactions enter `PENDING_RETRY` or `FAILED`; exponential backoff with jitter is applied; buyer is given a safe recovery status. |
| 4 | **What is authoritative?** | PostgreSQL database tables and verified Razorpay Webhook/Fetch responses. The LLM memory/context is completely non-authoritative. |
| 5 | **Can the action be repeated safely?** | Yes. All financial and state-mutating requests mandate a client-supplied or system-derived `Idempotency-Key` validated via database unique constraints. |
| 6 | **Can the action be audited?** | Yes. Every action generates an `AuditEvent` recording actor, session, prompt hash, policy check outcome, and state transition diff. |
| 7 | **Can the action be stopped?** | Yes. The merchant control plane can toggle the merchant state to `PAUSED`, tripping an emergency kill-switch on all agent actions immediately. |
| 8 | **Can the agent escalate its own authority?** | No. Policies and permissions are hardcoded in application logic and database tables; agent runs in a sandboxed role with no write permissions to configuration tables. |
| 9 | **Can stale state cause an unsafe action?** | No. Quotes have explicit expiration timestamps (`expires_at`, default 15m). Inventory checks use optimistic concurrency control (`version` check on checkout). |
| 10 | **Can a malicious agent exploit the workflow?** | No. System prompts use parameter delimiters; inputs are sanitized; limits are enforced at the gateway; raw Razorpay secrets are never exposed in prompt contexts. |

---

## 5. Architectural Assumptions & Risk Registry

### Assumption 1: Razorpay Test-Mode Orders API Stability
- **ASSUMPTION:** Razorpay Orders API (`POST /v1/orders`) generates unique order objects with deterministic `id` (`order_...`) and adheres to integer paise currency representations.
- **EVIDENCE:** Razorpay public API documentation & standard REST contracts.
- **CONFIDENCE:** 99%
- **FAILURE IF WRONG:** Order creation crashes or amounts are corrupted by float rounding.
- **MITIGATION:** Wrap all monetary inputs in integer `paise` (INR * 100) using Python `int`; enforce strict Pydantic parsing.
- **VERIFICATION REQUIRED:** Execute integration test against Razorpay test sandbox during Phase 1.

### Assumption 2: Webhook Latency & Delivery Out-of-Order
- **ASSUMPTION:** Razorpay webhooks may arrive seconds to minutes after payment completion, or arrive out of sequence (`payment.captured` before `order.paid`).
- **EVIDENCE:** Distributed webhook architecture characteristics.
- **CONFIDENCE:** 95%
- **FAILURE IF WRONG:** State machine locks up or marks valid order as failed.
- **MITIGATION:** State machines handle out-of-order terminal events idempotently; polling fallback (`Payments.fetch`) is scheduled if webhook is not received within 60 seconds.
- **VERIFICATION REQUIRED:** Simulate out-of-order webhook delivery in test suite.
