# Razorpay Test-Mode Integration Notes & API Contract (Phase 0)

> **Integration Principle:** Zero client-side trust. All payment authorizations and captures must be verified server-side via HMAC SHA-256 webhook signatures or direct REST API fetches with basic authentication.

---

## 1. Verified Razorpay Architecture Facts

| Area | Fact / Verified Characteristic | Architectural Implication |
|---|---|---|
| **Authentication** | HTTP Basic Auth with `Key ID` as username and `Key Secret` as password over TLS/HTTPS. | Secrets remain server-side only; never passed to client browser or LLM context. |
| **Currency & Amounts** | Amounts are strictly integer values in the smallest currency unit (e.g. `INR` in paise: ₹500.00 = `50000`). | No floating point numbers anywhere in the pipeline. Integer paise only. |
| **Order Lifecycle** | States: `created` $\to$ `attempted` $\to$ `paid`. An Order is created before payment and ties payments to a single merchant receipt. | Every checkout must generate a Razorpay Order before payment initiation. |
| **Payment Lifecycle** | States: `created` $\to$ `authorized` $\to$ `captured` (or `failed`, `refunded`). Auto-capture can be enabled via `payment_capture: 1` during order creation. | Enable `payment_capture: 1` in test-mode orders to simplify authorization flow. |
| **Webhook Security** | Payloads are signed using HMAC SHA-256 with a merchant-configured Webhook Secret. The signature is in `X-Razorpay-Signature` header. | Mandatory signature verification before parsing or processing any webhook body. |
| **Receipt Tracking** | `receipt` parameter accepts custom internal identifier (max 40 characters) on `POST /v1/orders`. | Pass `order_{uuid[:32]}` into `receipt` for deterministic correlation. |

---

## 2. API Operations in Scope (Test Mode)

### 2.1 Create Order (`POST /v1/orders`)
- **Endpoint:** `https://api.razorpay.com/v1/orders`
- **Headers:** `Authorization: Basic base64(key_id:key_secret)`, `Content-Type: application/json`
- **Request Payload:**
```json
{
  "amount": 450000,
  "currency": "INR",
  "receipt": "ord_9b1deb4d3b7d4bad",
  "payment_capture": 1,
  "notes": {
    "platform": "agent-ready-merchant",
    "merchant_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "order_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
  }
}
```
- **Response Payload (Success 200):**
```json
{
  "id": "order_EKwxwAgItmmXdp",
  "entity": "order",
  "amount": 450000,
  "amount_paid": 0,
  "amount_due": 450000,
  "currency": "INR",
  "receipt": "ord_9b1deb4d3b7d4bad",
  "status": "created",
  "attempts": 0,
  "notes": { ... },
  "created_at": 1740134400
}
```

---

### 2.2 Fetch Payments for Order (`GET /v1/orders/{order_id}/payments`)
- **Purpose:** Out-of-band reconciliation if webhooks are delayed or dropped.
- **Endpoint:** `https://api.razorpay.com/v1/orders/{order_id}/payments`
- **Response Payload:**
```json
{
  "entity": "collection",
  "count": 1,
  "items": [
    {
      "id": "pay_29QQoUBcxrhErF",
      "entity": "payment",
      "amount": 450000,
      "currency": "INR",
      "status": "captured",
      "order_id": "order_EKwxwAgItmmXdp",
      "method": "card",
      "error_code": null
    }
  ]
}
```

---

### 2.3 Create Refund (`POST /v1/payments/{payment_id}/refund`)
- **Purpose:** Execute compensation transactions if fulfillment fails post-payment.
- **Request Payload:**
```json
{
  "amount": 450000,
  "reverse_all": 1,
  "notes": {
    "reason": "Automatic cancellation: fulfillment inventory unavailable"
  }
}
```

---

## 3. Webhook Handling & Cryptographic Verification

### 3.1 Verification Algorithm
```python
import hmac
import hashlib

def verify_razorpay_webhook(raw_body: bytes, signature_header: str, webhook_secret: str) -> bool:
    """Verifies that the webhook payload was signed by Razorpay."""
    expected_signature = hmac.new(
        key=webhook_secret.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)
```

### 3.2 Supported Webhook Events
1. `order.paid`: Primary trigger to mark order `PAID` and advance state machine.
2. `payment.authorized`: Fired when payment is authorized.
3. `payment.captured`: Confirms funds captured.
4. `payment.failed`: Fired when payment attempt fails; unlocks retry path.

---

## 4. Test-Mode Sandbox Tooling & Artifacts

- **Dummy Card Details:** Razorpay test card `4111 1111 1111 1111`, expiry `12/30`, CVV `123`, OTP `123456` or simulated success button.
- **Mock UPI Handles:** `success@razorpay` (instant success), `failure@razorpay` (instant failure).
- **Webhook Ingestion in Dev:** Ingest local webhooks via `ngrok` tunnel or direct mock event injection endpoint in test harness.

---

## 5. Explicit Unresolved Items & Verification Required

| Item | Status | Verification Plan (Phase 1) |
|---|---|---|
| **Max length of `receipt` field** | Documented as 40 chars; needs confirmation against live test API | Verify with exact 40-char UUID string during initial API smoke test |
| **Auto-capture timing in Test Mode** | Usually synchronous on test authorization, but webhook may arrive before API returns | Test race conditions between frontend callback and webhook in test suite |
| **Refund processing time in Test Mode** | Typically instantaneous in test mode (`status: processed`) | Verify refund webhook payload format against test sandbox |
