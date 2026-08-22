"""Tests for Alembic migrations and schema verification."""

from alembic.config import Config
from alembic.script import ScriptDirectory


def test_alembic_script_directory_and_head() -> None:
    """Verifies that Alembic discovers the initial revision and points to 001_initial_schema."""
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)

    head = script.get_current_head()
    assert head == "001_initial_schema"

    revision = script.get_revision("001_initial_schema")
    assert revision is not None
    assert revision.doc == "001_initial_schema"
    assert revision.revision == "001_initial_schema"
