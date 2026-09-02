"""Tests for Alembic migrations and schema verification."""

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


def test_alembic_script_directory_and_head() -> None:
    """Verifies that Alembic discovers the complete migration chain and its head."""
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)

    head = script.get_current_head()
    assert head == "010_phase7_integrity"

    revision = script.get_revision("001_initial_schema")
    assert revision is not None
    assert revision.revision == "001_initial_schema"

    hardening_revision = script.get_revision("002_gateway_hardening")
    assert hardening_revision is not None
    assert hardening_revision.down_revision == "001_initial_schema"

    grants_revision = script.get_revision("003_session_capability_grants")
    assert grants_revision is not None
    assert grants_revision.down_revision == "002_gateway_hardening"

    reliability_revision = script.get_revision("004_payment_reliability")
    assert reliability_revision is not None
    assert reliability_revision.down_revision == "003_session_capability_grants"

    governance_revision = script.get_revision("005_safety_policy_governance")
    assert governance_revision is not None
    assert governance_revision.down_revision == "004_payment_reliability"

    mutation_receipts_revision = script.get_revision("006_merchant_mutation_receipts")
    assert mutation_receipts_revision is not None
    assert mutation_receipts_revision.down_revision == "005_safety_policy_governance"

    auth_binding_revision = script.get_revision("007_merchant_auth_user_binding")
    assert auth_binding_revision is not None
    assert auth_binding_revision.down_revision == "006_merchant_mutation_receipts"

    agent_experiments_revision = script.get_revision("008_merchant_agent_experiments")
    assert agent_experiments_revision is not None
    assert agent_experiments_revision.down_revision == "007_merchant_auth_user_binding"

    merchant_runs_revision = script.get_revision("009_merchant_agent_runs")
    assert merchant_runs_revision is not None
    assert merchant_runs_revision.down_revision == "008_merchant_agent_experiments"

    integrity_revision = script.get_revision("010_phase7_integrity")
    assert integrity_revision is not None
    assert integrity_revision.down_revision == "009_merchant_agent_runs"


def test_merchant_run_downgrade_refuses_to_discard_merchant_scoped_runs() -> None:
    """Downgrade must preserve durable history rather than deleting merchant-only runs."""
    migration_source = Path("alembic/versions/009_merchant_agent_runs.py").read_text(
        encoding="utf-8"
    )
    preflight = "Cannot downgrade 009: merchant-scoped AgentRuns exist"
    assert preflight in migration_source
    assert migration_source.index(preflight) < migration_source.index(
        'op.alter_column("agent_runs", "session_id", existing_type=sa.UUID(), nullable=False)'
    )
    assert "DELETE FROM agent_runs WHERE session_id IS NULL" not in migration_source


def test_phase7_integrity_migration_adds_tenant_and_audit_linkage_constraints() -> None:
    """Forward migration must enforce Phase 7 tenant pairing and durable proposal linkage."""
    migration_source = Path("alembic/versions/010_phase7_integrity.py").read_text(encoding="utf-8")

    assert "fk_merchant_proposals_run_merchant" in migration_source
    assert "fk_merchant_experiment_results_experiment_merchant" in migration_source
    assert "uq_agent_runs_id_merchant" in migration_source
    assert "uq_merchant_experiments_id_merchant" in migration_source
    assert "estimated_cost_paise" in migration_source
    assert "is_demo_sandbox_product" in migration_source
