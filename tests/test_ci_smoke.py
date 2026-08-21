"""CI smoke test for verifying environment setup and package discovery."""

import agent_ready_merchant


def test_package_import_and_version() -> None:
    """Verify that the package imports correctly and exposes expected version string."""
    assert hasattr(agent_ready_merchant, "__version__")
    assert agent_ready_merchant.__version__ == "0.1.0"
