# Failure Model & Safe Recovery Architecture: Agent-Ready Merchant (Phase 0)

> **Core Doctrine:** In a distributed financial architecture, failure is not an anomaly; it is an expected operating condition. Every failure must fail closed, preserve ledger integrity, and provide deterministic recovery paths.

---

## 1. Failure Taxonomy & Recovery Matrix

| Failure Mode | Root Cause | Immediate System Behavior | Recovery / Self-Healing Mechanism | Ledger & Financial Impact |
|---|---|---|---|---|
| **LLM Provider Outage** | Gemini 503 / Rate Limit / Network Blip | Agent runtime catches timeout / exception; aborts run | Fallback to deterministic catalog browse; notifies buyer to retry | Zero financial impact. No order created. |
| **Malformed LLM Output** | Non-JSON response or broken schema | Schema validator rejects; increments error counter | Retry with structured error feedback (max 2); fail with graceful user message | Zero state change. |
| **Policy Violation** | LLM proposes price below floor | Policy engine intercepts and raises `PolicyViolationError` | Returns deterministic reason to LLM; LLM explains floor to buyer | Zero state mutation. |
| **Razorpay API Outage** | Razorpay REST endpoint 5xx or connection timeout | Payment creation fails with `GATEWAY_UNAVAILABLE` | Exponential backoff (2 retries); if still down, mark order `PENDING_PAYMENT_RETRY` | No payment captured. Order remains open until expiry. |
| **Dropped Webhook** | Network partition between Razorpay & server | Order remains in `PAYMENT_PROCESSING` | Out-of-band reconciliation worker polls `GET /v1/orders/{id}/payments` every 60s | Order transitions to `PAID` once verified via polling. |
| **Duplicate Webhook** | Razorpay retries webhook delivery | Webhook receiver checks `event_id` in idempotency table | Returns HTTP 200 immediately; ignores duplicate event | Zero duplicate state transition. |
| **Inventory Oversell Race** | Two buyers checkout last stock simultaneously | PostgreSQL optimistic lock detects `version` mismatch | First transaction commits; second transaction receives `INSUFFICIENT_STOCK` error | Inventory never drops below 0. Second buyer gets clean refusal. |
| **Post-Payment Fulfillment Failure** | Stock physically damaged / unavailable after payment | Fulfillment worker marks order `FULFILLMENT_FAILED` | Compensation saga triggers `Refunds.create` via Razorpay API | Full refund issued to buyer. Transaction record updated to `REVERSED`. |

---

## 2. Circuit Breakers & Degradation Modes

```mermaid
graph TD
    A[Normal Operation: Full Agentic Commerce] -->|LLM Error Rate > 20%| B[Degraded Mode: Deterministic Catalog & Fixed Pricing]
    A -->|Razorpay 5xx Rate > 10%| C[Payment Circuit Open: Pause Checkout]
    B -->|LLM Health Check Passes| A
    C -->|Razorpay Health Restored| A
```

### 2.1 LLM Circuit Breaker
If the LLM provider fails $\ge 5$ consecutive times within a 60-second sliding window:
1. Circuit opens to `DEGRADED`.
2. Conversational agent is replaced by a deterministic keyword search and fixed-price catalog response.
3. Merchant dashboard alerts: `AI Concierge Offline - Operating on Fixed Rules`.

### 2.2 Payment Gateway Circuit Breaker
If Razorpay API calls return 5xx for $\ge 3$ consecutive transactions:
1. Circuit opens to `PAYMENT_PAUSED`.
2. New checkout attempts are temporarily refused with `PAYMENT_SERVICE_MAINTENANCE`.
3. Background health probe tests `GET /v1/orders` every 30 seconds until healthy.

---

## 3. Reconciliation Engine & Compensation Sagas

```mermaid
sequenceDiagram
    autonumber
    participant Worker as Background Reconciler
    participant DB as PostgreSQL Ledger
    participant RZP as Razorpay Test API

    Note over Worker: Runs every 60 seconds
    Worker->>DB: SELECT * FROM orders WHERE status='PAYMENT_PROCESSING' AND updated_at < now() - INTERVAL '60s'
    DB-->>Worker: Found Order (id=123, rzp_order_id='order_abc')
    Worker->>RZP: GET /v1/orders/order_abc/payments
    RZP-->>Worker: Status: 'captured', payment_id: 'pay_xyz', amount: 500000
    Worker->>DB: BEGIN TRANSACTION
    Worker->>DB: UPDATE orders SET status='PAID' WHERE id=123
    Worker->>DB: INSERT INTO payment_attempts (order_id, rzp_payment_id, status) VALUES (123, 'pay_xyz', 'CAPTURED')
    Worker->>DB: INSERT INTO transaction_records (entry_type, amount_paise, status) VALUES ('CREDIT', 500000, 'COMMITTED')
    Worker->>DB: COMMIT TRANSACTION
    Note over Worker,DB: Order state reconciled successfully
```
