# Architectural Decision Records (ADRs): Agent-Ready Merchant

> This document records the key architectural and design decisions, their rationale, context, and consequences.

---

## ADR-001: Separation of Intelligence from Authority

- **Status:** ACCEPTED
- **Context:** Large Language Models (LLMs) are probabilistic, susceptible to prompt injection, hallucination, and adversarial jailbreaks. In a financial/commerce system, trusting model output directly with database mutations or payment execution exposes merchants to severe financial loss.
- **Decision:** Establish a strict architectural boundary. The LLM acts purely as an untrusted proposal engine emitting structured Pydantic intent objects. A deterministic policy engine and action gateway enforce mathematical floors, state preconditions, capabilities, and idempotency before executing any side effect.
- **Consequences:**
  - *Positive:* Prevents unauthorized discounts, floor breaches, and financial loss even under complete LLM compromise.
  - *Negative:* Slightly higher architectural complexity and latency due to multi-stage validation pipeline.

---

## ADR-002: Integer Paise Currency Representation

- **Status:** ACCEPTED
- **Context:** Floating-point arithmetic introduces IEEE-754 precision inaccuracies (e.g. `0.1 + 0.2 != 0.3`), which can accumulate or cause discrepancies between internal ledgers and Razorpay payment orders.
- **Decision:** Represent all monetary values across database schemas, APIs, and business logic as 64-bit non-negative integers representing paise (1 INR = 100 paise).
- **Consequences:**
  - *Positive:* Zero rounding errors; 1:1 compatibility with Razorpay API amounts.
  - *Negative:* Display layers must format paise to INR strings explicitly.

---

## ADR-003: Modular Monolith Architecture for MVP

- **Status:** ACCEPTED
- **Context:** Distributing Phase 1 into microservices introduces distributed transaction problems, network overhead, and deployment complexity that obscure core safety guarantees.
- **Decision:** Build Phase 1 as a clean modular monolith using FastAPI, Python 3.11+, and PostgreSQL.
- **Consequences:**
  - *Positive:* Strong ACID guarantees, simple debugging, single deployment artifact, rapid iteration.
  - *Negative:* Must maintain clear internal package boundaries to prevent tight coupling.

---

## ADR-004: Server-Authoritative Webhook & Reconciliation Engine

- **Status:** ACCEPTED
- **Context:** Client-side redirect callbacks from payment gateways can be intercepted, spoofed, or blocked by ad-blockers / network drops.
- **Decision:** All payment state transitions to `PAID` require a cryptographically verified HMAC SHA-256 webhook from Razorpay (`X-Razorpay-Signature`) or an out-of-band server-to-server fetch (`GET /v1/orders/{id}/payments`).
- **Consequences:**
  - *Positive:* Completely eliminates client-side payment forgery attacks.
  - *Negative:* Requires background polling worker for edge cases where webhooks fail to deliver.

---

## ADR-005: Optimistic Concurrency Control for Inventory & Quotes

- **Status:** ACCEPTED
- **Context:** Multiple buyer agents interacting concurrently could attempt to purchase the same limited stock item simultaneously.
- **Decision:** Use PostgreSQL row versioning (`version BIGINT`) and `SELECT ... FOR UPDATE` row-level locks during checkout and stock reservation.
- **Consequences:**
  - *Positive:* Prevents overselling and race conditions without heavy distributed locks.
  - *Negative:* Contested transactions must handle optimistic lock failure gracefully and report stock depletion.

---

## ADR-006: CI Tooling & Engineering Quality Standards

- **Status:** ACCEPTED
- **Context:** Ensuring deterministic, repeatable code quality, type safety, security scanning, and test validation across all contributions in a safety-critical commerce repository.
- **Decision:** Adopt `Ruff` (linting + formatting with bandit security rules), `Mypy` (strict static typing), `Pytest` (with coverage and async support), and automated git secret scanning in GitHub Actions CI across Python 3.11 and 3.12 matrices.
- **Consequences:**
  - *Positive:* Fast, deterministic feedback loop; prevents syntax regressions, type mismatches, and secret leakage before merging.
  - *Negative:* Strict static typing overhead during rapid development.
