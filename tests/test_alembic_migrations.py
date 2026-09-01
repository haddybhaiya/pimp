"""Tests for Alembic migrations and schema verification."""

from alembic.config import Config
from alembic.script import ScriptDirectory


def test_alembic_script_directory_and_head() -> None:
    """Verifies that Alembic discovers the complete migration chain and its head."""
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)

    head = script.get_current_head()
    assert head == "009_merchant_agent_runs"

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
