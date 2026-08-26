"""Tests for Alembic migrations and schema verification."""

from alembic.config import Config
from alembic.script import ScriptDirectory


def test_alembic_script_directory_and_head() -> None:
    """Verifies that Alembic discovers the migration chain and points to 002_gateway_hardening."""
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)

    head = script.get_current_head()
    assert head == "003_session_capability_grants"

    revision = script.get_revision("001_initial_schema")
    assert revision is not None
    assert revision.revision == "001_initial_schema"

    hardening_revision = script.get_revision("002_gateway_hardening")
    assert hardening_revision is not None
    assert hardening_revision.down_revision == "001_initial_schema"

    grants_revision = script.get_revision("003_session_capability_grants")
    assert grants_revision is not None
    assert grants_revision.down_revision == "002_gateway_hardening"
