# Agent-Ready Merchant

> **Autonomous AI Commerce Platform on Razorpay Infrastructure**

---

## Overview

Agent-Ready Merchant is a financial and commerce control plane that enables ordinary merchants to become AI-discoverable, understandable, negotiable, and safely transactable by autonomous AI buyer agents.

### Core Security Principle
$$\text{Intelligence} \neq \text{Authority}$$
The LLM is untrusted intelligence. The application is the authority.

---

## Development & CI

### Prerequisites
- Python 3.11+
- PostgreSQL 16+

### Quick Start
```bash
# Install dependencies
pip install -e ".[dev]"

# Run code checks
ruff check .
ruff format --check .
mypy src tests

# Run tests
pytest
```

---

## Documentation
- [Phase Status](docs/phase.md)
- [System Architecture](docs/architecture.md)
- [Hard Invariants](docs/invariants.md)
- [Architectural Decisions (ADRs)](docs/decisions.md)
- [Evaluation Framework](docs/evaluation.md)
