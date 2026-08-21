# Tool Contract Specification: Agent-Ready Merchant (Phase 0)

> **Core Doctrine:** Tools are typed RPC gateways with deterministic side-effect classifications, capability enforcement, strict timeouts, and idempotency guarantees. The LLM cannot execute tools directly; execution is handled by the Action Gateway.

---

## 1. Tool Taxonomy & Side-Effect Classification

Every tool belongs to one of three side-effect classes:
1. `READ_ONLY` (Safe, idempotent, cacheable, zero state mutation)
2. `TRANSIENT_STATE` (Mutates internal session/quote state, reversible, no financial movement)
3. `PRIVILEGED_FINANCIAL` (Interacts with payment gateways or creates binding financial commitments, strictly guarded, requires idempotency keys)

---

## 2. Complete Tool Catalog Specification

### 2.1 `discover_catalog`
- **Purpose:** Search and filter merchant products by natural language query, category, or price range.
- **Classification:** `READ_ONLY`
- **Required Capability:** `buyer:discover`
- **Timeout:** 2,000 ms
- **Retry Policy:** Up to 2 retries on database timeout (exponential backoff 200ms).
- **Idempotency:** Naturally idempotent.

#### Input Schema (JSON Schema)
```json
{
  "type": "object",
  "properties": {
    "query": { "type": "string", "maxLength": 100 },
    "category": { "type": "string", "maxLength": 50 },
    "max_price_paise": { "type": "integer", "minimum": 0 },
    "limit": { "type": "integer", "minimum": 1, "maximum": 10, "default": 5 }
  },
  "required": [],
  "additionalProperties": false
}
```

#### Output Schema
```json
{
  "type": "object",
  "properties": {
    "products": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "sku": { "type": "string" },
          "title": { "type": "string" },
          "category": { "type": "string" },
          "base_price_paise": { "type": "integer" },
          "is_negotiable": { "type": "boolean" },
          "in_stock": { "type": "boolean" }
        },
        "required": ["sku", "title", "base_price_paise", "is_negotiable", "in_stock"]
      }
    },
    "total_matched": { "type": "integer" }
  },
  "required": ["products", "total_matched"]
}
```

---

### 2.2 `get_product_details`
- **Purpose:** Retrieve comprehensive specs, attributes, and stock levels for a specific SKU.
- **Classification:** `READ_ONLY`
- **Required Capability:** `buyer:read`
- **Timeout:** 1,500 ms
- **Retry Policy:** 2 retries.

#### Input Schema
```json
{
  "type": "object",
  "properties": {
    "sku": { "type": "string", "minLength": 1, "maxLength": 100 }
  },
  "required": ["sku"],
  "additionalProperties": false
}
```

#### Output Schema
```json
{
  "type": "object",
  "properties": {
    "sku": { "type": "string" },
    "title": { "type": "string" },
    "description": { "type": "string" },
    "base_price_paise": { "type": "integer" },
    "available_quantity": { "type": "integer" },
    "attributes": { "type": "object" },
    "is_negotiable": { "type": "boolean" }
  },
  "required": ["sku", "title", "base_price_paise", "available_quantity", "is_negotiable"]
}
```

---

### 2.3 `request_price_quote`
- **Purpose:** Request a formal, binding, time-limited price quote for items.
- **Classification:** `TRANSIENT_STATE`
- **Required Capability:** `buyer:quote`
- **Timeout:** 3,000 ms
- **Retry Policy:** Non-retryable on validation error; retryable on database contention (1 retry).
- **Idempotency:** Requires `idempotency_key` generated from `hash(session_id, items, ts_minute)`.

#### Input Schema
```json
{
  "type": "object",
  "properties": {
    "session_id": { "type": "string", "format": "uuid" },
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "sku": { "type": "string" },
          "quantity": { "type": "integer", "minimum": 1, "maximum": 10 }
        },
        "required": ["sku", "quantity"]
      },
      "minItems": 1,
      "maxItems": 5
    }
  },
  "required": ["session_id", "items"],
  "additionalProperties": false
}
```

#### Output Schema
```json
{
  "type": "object",
  "properties": {
    "quote_id": { "type": "string", "format": "uuid" },
    "subtotal_paise": { "type": "integer" },
    "discount_paise": { "type": "integer" },
    "shipping_paise": { "type": "integer" },
    "total_paise": { "type": "integer" },
    "expires_at": { "type": "string", "format": "date-time" }
  },
  "required": ["quote_id", "subtotal_paise", "discount_paise", "shipping_paise", "total_paise", "expires_at"]
}
```

---

### 2.4 `negotiate_quote`
- **Purpose:** Submit a counter-offer against an active `PriceQuote`. Evaluated strictly by the deterministic policy engine.
- **Classification:** `TRANSIENT_STATE`
- **Required Capability:** `buyer:negotiate`
- **Timeout:** 3,000 ms
- **Retry Policy:** None.
- **Idempotency:** Keyed on `hash(quote_id, proposed_total_paise)`.

#### Input Schema
```json
{
  "type": "object",
  "properties": {
    "quote_id": { "type": "string", "format": "uuid" },
    "proposed_total_paise": { "type": "integer", "minimum": 1 },
    "rationale": { "type": "string", "maxLength": 255 }
  },
  "required": ["quote_id", "proposed_total_paise"],
  "additionalProperties": false
}
```

#### Output Schema
```json
{
  "type": "object",
  "properties": {
    "status": { "type": "string", "enum": ["ACCEPTED", "COUNTERED", "REJECTED"] },
    "revised_quote_id": { "type": "string", "format": "uuid" },
    "total_paise": { "type": "integer" },
    "message": { "type": "string" },
    "expires_at": { "type": "string", "format": "date-time" }
  },
  "required": ["status", "total_paise", "message"]
}
```

---

### 2.5 `create_order`
- **Purpose:** Converts an accepted quote into a locked merchant order and reserves inventory.
- **Classification:** `TRANSIENT_STATE`
- **Required Capability:** `buyer:checkout`
- **Timeout:** 4,000 ms
- **Retry Policy:** 1 retry on lock conflict.
- **Idempotency:** Enforced via `quote_id` uniqueness in `orders` table.

#### Input Schema
```json
{
  "type": "object",
  "properties": {
    "quote_id": { "type": "string", "format": "uuid" },
    "buyer_email": { "type": "string", "format": "email" },
    "shipping_address": {
      "type": "object",
      "properties": {
        "full_name": { "type": "string" },
        "address_line1": { "type": "string" },
        "city": { "type": "string" },
        "postal_code": { "type": "string" },
        "country": { "type": "string", "default": "IN" }
      },
      "required": ["full_name", "address_line1", "city", "postal_code"]
    }
  },
  "required": ["quote_id", "buyer_email", "shipping_address"],
  "additionalProperties": false
}
```

#### Output Schema
```json
{
  "type": "object",
  "properties": {
    "order_id": { "type": "string", "format": "uuid" },
    "amount_paise": { "type": "integer" },
    "currency": { "type": "string" },
    "status": { "type": "string", "enum": ["CREATED", "PENDING_PAYMENT"] },
    "expires_at": { "type": "string", "format": "date-time" }
  },
  "required": ["order_id", "amount_paise", "currency", "status", "expires_at"]
}
```

---

### 2.6 `initiate_payment`
- **Purpose:** Generates a server-authoritative Razorpay test-mode Order and prepares payment parameters.
- **Classification:** `PRIVILEGED_FINANCIAL`
- **Required Capability:** `system:payment_initiate`
- **Timeout:** 5,000 ms
- **Retry Policy:** Exponential backoff on Razorpay 5xx (2 retries).
- **Idempotency:** Keyed by `order_id` via Razorpay `receipt` parameter.

#### Input Schema
```json
{
  "type": "object",
  "properties": {
    "order_id": { "type": "string", "format": "uuid" }
  },
  "required": ["order_id"],
  "additionalProperties": false
}
```

#### Output Schema
```json
{
  "type": "object",
  "properties": {
    "order_id": { "type": "string", "format": "uuid" },
    "rzp_order_id": { "type": "string" },
    "amount_paise": { "type": "integer" },
    "currency": { "type": "string" },
    "rzp_key_id": { "type": "string" },
    "checkout_url_or_payload": { "type": "object" }
  },
  "required": ["order_id", "rzp_order_id", "amount_paise", "currency", "rzp_key_id"]
}
```

---

### 2.7 `check_payment_status`
- **Purpose:** Verifies payment status directly against Razorpay REST API and local state.
- **Classification:** `READ_ONLY`
- **Required Capability:** `buyer:read`
- **Timeout:** 3,000 ms
- **Retry Policy:** 2 retries on network blip.

#### Input Schema
```json
{
  "type": "object",
  "properties": {
    "order_id": { "type": "string", "format": "uuid" }
  },
  "required": ["order_id"],
  "additionalProperties": false
}
```

#### Output Schema
```json
{
  "type": "object",
  "properties": {
    "order_id": { "type": "string", "format": "uuid" },
    "status": { "type": "string", "enum": ["PENDING", "PAID", "FAILED", "EXPIRED"] },
    "rzp_payment_id": { "type": "string" },
    "is_settled": { "type": "boolean" }
  },
  "required": ["order_id", "status", "is_settled"]
}
```

---

## 3. Standardized Error Response Structure

When a tool fails or violates a policy, it returns a structured error object back to the agent reasoning loop:

```json
{
  "error": {
    "code": "POLICY_VIOLATION_BELOW_FLOOR_PRICE",
    "message": "Proposed unit price ₹4,000 is below the allowed floor price of ₹4,500.",
    "retryable": false,
    "suggested_action": "Explain the lowest allowed price of ₹4,500 to the buyer."
  }
}
```
