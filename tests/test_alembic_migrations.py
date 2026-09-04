"""Tests for Alembic migrations and schema verification."""

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


def test_alembic_script_directory_and_head() -> None:
    """Verifies that Alembic discovers the complete migration chain and its head."""
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)

    head = script.get_current_head()
    assert head == "016_phase9_public_discovery_identifiers"

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

    autonomy_revision = script.get_revision("011_phase8_controlled_autonomy")
    assert autonomy_revision is not None
    assert autonomy_revision.down_revision == "010_phase7_integrity"

    autonomy_proposal_integrity = script.get_revision("012_autonomy_proposal_integrity")
    assert autonomy_proposal_integrity is not None
    assert autonomy_proposal_integrity.down_revision == "011_phase8_controlled_autonomy"

    autonomy_proposal_delete = script.get_revision("013_autonomy_proposal_delete")
    assert autonomy_proposal_delete is not None
    assert autonomy_proposal_delete.down_revision == "012_autonomy_proposal_integrity"

    autonomy_failure_telemetry = script.get_revision("014_autonomy_failure_telemetry")
    assert autonomy_failure_telemetry is not None
    assert autonomy_failure_telemetry.down_revision == "013_autonomy_proposal_delete"

    discovery_network = script.get_revision("015_phase9_discovery_network")
    assert discovery_network is not None
    assert discovery_network.down_revision == "014_autonomy_failure_telemetry"

    public_identifiers = script.get_revision("016_phase9_public_discovery_identifiers")
    assert public_identifiers is not None
    assert public_identifiers.down_revision == "015_phase9_discovery_network"


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


def test_phase8_autonomy_proposal_links_are_tenant_coupled() -> None:
    """Migration 012 must database-enforce action/proposal tenant ownership."""
    migration_source = Path("alembic/versions/012_autonomy_proposal_tenant_integrity.py").read_text(
        encoding="utf-8"
    )

    assert "uq_merchant_proposals_id_merchant" in migration_source
    assert "fk_merchant_autonomy_actions_proposal_merchant" in migration_source
    assert "cross-merchant autonomous action proposal links exist" in migration_source


def test_phase8_proposal_deletion_preserves_autonomy_action_history() -> None:
    """Migration 013 must clear only an optional proposal reference on delete."""
    migration_source = Path("alembic/versions/013_autonomy_proposal_delete.py").read_text(
        encoding="utf-8"
    )

    assert "ON DELETE SET NULL (proposal_id)" in migration_source
    assert '["proposal_id", "merchant_id"]' in migration_source


def test_phase8_failure_telemetry_is_durable_and_tenant_scoped() -> None:
    """Migration 014 must support the rolling autonomy failure circuit breaker."""
    migration_source = Path("alembic/versions/014_autonomy_failure_telemetry.py").read_text(
        encoding="utf-8"
    )

    assert "merchant_autonomy_failures" in migration_source
    assert "ck_merchant_autonomy_failures_code_valid" in migration_source
    assert "ix_merchant_autonomy_failures_merchant_created" in migration_source
