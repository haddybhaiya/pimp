# Mandatory Agent Engineering Skills & Operating Contract

> **Scope:** This contract governs every AI agent, pair programmer, and automated contributor operating inside the **Agent-Ready Merchant** codebase. It is non-negotiable.

---

## 1. Mandatory Pre-Flight Protocol (Read Before Acting)

Before writing or modifying any code, configuration, or tests, every agent MUST:

1. **Read `docs/phase.md`:** Confirm the currently active phase and its explicit scope cut line.
2. **Read `docs/decisions.md`:** Review all accepted Architectural Decision Records (ADRs).
3. **Read `docs/invariants.md`:** Review non-negotiable financial, authority, and state invariants.
4. **Inspect Relevant Contracts:** Read domain models (`docs/domain-model.md`), state machines (`docs/state-machines.md`), tool contracts (`docs/tool-contract.md`), policy models (`docs/policy-model.md`), and evaluation criteria (`docs/evaluation.md`).
5. **Inspect Existing Tests & Code:** Inspect existing implementations and unit/integration tests to ensure consistency.
6. **Identify Task Assumptions:** Verify whether any assumptions in `docs/assumptions.md` apply to the task.

---

## 2. Phase Discipline & Scope Confinement

- Implement **ONLY** work explicitly belonging to the active phase defined in `docs/phase.md`.
- **NEVER** expand scope, introduce speculative microservices, implement future phases, or weaken security boundaries.
- **NEVER** silently alter architectural decisions. If a task requires changing an existing ADR, STOP and report the conflict immediately.

---

## 3. Separation of Intelligence and Authority ($\text{Intelligence} \neq \text{Authority}$)

- **Treat the LLM as Untrusted Intelligence:** Model outputs, user prompts, buyer agent messages, catalog descriptions, and external API responses are completely untrusted.
- **The Application is the Authority:** Never allow LLM outputs to directly mutate database records, alter permissions, execute financial transactions, or bypass policies.
- **Deterministic Pipeline:** Every model proposal must pass Schema Validation $\to$ State Machine Precondition Checks $\to$ Deterministic Policy Validation $\to$ Capability Checks $\to$ Idempotency Gate $\to$ Action Gateway.
- **Fail-Closed Principle:** Any validation failure, policy violation, or ambiguous condition must fail closed (reject action, log audit event, preserve state).

---

## 4. Financial & Monetary Safety

- **Integer Paise Representation:** All monetary amounts are strictly 64-bit non-negative integers representing paise (1 INR = 100 paise). Floating-point currency math is prohibited.
- **Floor Price Guarantee:** Never allow any quote or order below the merchant-configured floor price / cost margin.
- **Idempotency:** Every financial side effect and state-mutating operation must require an `Idempotency-Key` or deterministic hash key. Duplicate requests must never produce duplicate charges or orders.
- **Server-Authoritative Settlement:** Verify payment success exclusively via HMAC SHA-256 webhook signatures or direct Razorpay server fetches. Never trust client-side callbacks.

---

## 5. Security & Zero Secret Leakage

- **Zero Credentials in Context:** Razorpay API keys (`rzp_test_...`), HMAC secrets, and database credentials must NEVER be placed in system prompts, tool schemas, or conversational context.
- **Input Sanitization & Parameter Delimitation:** Wrap untrusted inputs with explicit parameter boundaries (e.g. `<untrusted_input>...</untrusted_input>`).
- **Sandboxed Tooling:** Tools must be narrow, typed RPC endpoints. Generic tools like `manage_store()` are strictly prohibited.
- **Bounded Compute:** Cap agent runs at $\le 5$ tool steps, $\le 8,192$ context tokens, and $\le 15$ seconds timeout per turn.

---

## 6. State Machine & Concurrency Integrity

- **Strict Transitions:** Never invent or skip state transitions. Every transition must validate the current state in PostgreSQL.
- **Optimistic Locking:** Enforce version-checked mutations (`WHERE id = :id AND version = :expected_version`) and row locks (`SELECT ... FOR UPDATE`) to prevent inventory overselling and race conditions.
- **Append-Only Ledgers:** `transaction_records` and `audit_events` tables are immutable. Updates and deletions are forbidden.

---

## 7. Mandatory Test & Verification Matrix

Before declaring any implementation task complete, the agent must run and verify tests for:
- Happy paths & standard workflows
- Boundary conditions (zero amounts, max limits, floor prices)
- Malformed & invalid input schemas
- Capability & authorization failures
- Duplicate execution & replay attempts (idempotency)
- Concurrency races & optimistic locking conflicts
- Timeout & external service failure modes
- Adversarial prompt injection & policy override attempts

**Never claim success without running verification.**

---

## 8. Living Documentation Discipline

Whenever an implementation modifies architecture, assumptions, decisions, invariants, phase status, or contracts:
- Update `docs/phase.md` if phase status or readiness changes.
- Update `docs/decisions.md` if an ADR is introduced or revised.
- Update `docs/invariants.md` if invariants are affected.
- Update `docs/assumptions.md` if assumptions are validated, invalidated, or added.
- Update relevant contract and model documentation in `docs/`.

---

## 9. Anomaly & Conflict Protocol (Stop and Report)

If an external dependency, API behavior, LLM provider, or test result contradicts the documented architecture or assumptions:
1. **STOP execution immediately.**
2. Do not introduce silent workarounds or weaken safety guards.
3. Formulate a report detailing:
   - Observed behavior
   - Expected behavior
   - Impact on invariants and contracts
   - Proposed architectural remediation options

---

## 10. Mandatory Agent Completion Report Format

Every agent execution turn must conclude with the following structured report:

### Changed
*Exact files, components, or configurations created or modified.*

### Tested
*Exact test commands, scripts, or verification suites executed, along with results.*

### Documents Updated
*List of all documentation files in `docs/` updated during this task.*

### Decisions
*Any new or modified Architectural Decision Records (ADRs).*

### Assumptions
*Any new, validated, or invalidated assumptions in `docs/assumptions.md`.*

### Risks
*Identified remaining risks or technical debt.*

### Follow-up
*Actionable, prioritized next steps for the subsequent agent run.*
