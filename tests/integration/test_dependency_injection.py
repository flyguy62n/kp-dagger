"""Integration tests for dependency injection."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from pybastion.containers import ApplicationContainer
from pybastion.containers.config import PyBastionConfig, load_config, validate_config


class TestDependencyInjectionIntegration:
    """Integration tests for the dependency injection system."""

    def test_full_container_integration(self) -> None:
        """Test that the full container can be initialized and wired."""
        container = ApplicationContainer()

        # Set minimal configuration
        config_data = {
            "core": {
                "database": {"path": ":memory:"},
                "encryption": {
                    "master_key": "test-key-for-integration",
                    "salt": "test-salt-for-integration",
                },
            },
            "api_clients": {
                "cve": {"api_key": "test-api-key"},
                "eol": {},
            },
            "scanner": {"verbose": False},
        }

        container.config.from_dict(config_data)

        # Test that all main services can be retrieved
        assert container.core_container is not None
        assert container.parser_container is not None
        assert container.analyzer_container is not None
        assert container.report_container is not None
        assert container.api_client_container is not None

    @patch("pybastion.core.database.DatabaseManager.initialize")
    def test_scanner_creation_integration(self, mock_db_init: Mock) -> None:  # noqa: ARG002
        """Test that scanner can be created with all dependencies."""
        container = ApplicationContainer()

        config_data: dict[str, dict[str, str]] = {
            "core": {
                "database": {"path": ":memory:"},
                "encryption": {
                    "master_key": "integration-test-key",
                    "salt": "integration-test-salt",
                },
            },
            "api_clients": {
                "cve": {"api_key": "integration-test-key"},
                "eol": {},
            },
            "scanner": {"verbose": True},
        }

        container.config.from_dict(config_data)

        # Should be able to create scanner without errors
        scanner = container.scanner()
        assert scanner is not None
        assert scanner.verbose is True

    def test_config_file_integration(self) -> None:
        """Test loading configuration from file and using it with container."""
        # Create a temporary config file
        config_content = """
core:
  database:
    path: ":memory:"
  encryption:
    master_key: "file-test-key"
    salt: "file-test-salt"

api_clients:
  cve:
    api_key: "file-test-api-key"
    timeout: 45
  eol:
    timeout: 60

scanner:
  verbose: true
  parallel_workers: 2
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write(config_content)
            config_file_path = f.name

        try:
            # Load config from file
            config_dict: dict[str, str | int | bool] = load_config(config_file_path)
            config: PyBastionConfig = validate_config(config_dict)

            # Verify config was loaded correctly
            assert config.core.encryption.master_key == "file-test-key"
            assert config.api_clients.cve.timeout == 45  # noqa: PLR2004
            assert config.scanner.verbose is True
            assert config.scanner.parallel_workers == 2  # noqa: PLR2004

            # Use config with container
            container = ApplicationContainer()
            container.config.from_dict(config_dict)

            # Verify container uses the config
            assert container.config.scanner.verbose() is True

        finally:
            # Clean up temp file
            Path(config_file_path).unlink()

    def test_missing_config_handling(self) -> None:
        """Test that missing configuration is handled gracefully."""
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent-config.yml")

    def test_invalid_config_handling(self) -> None:
        """Test that invalid configuration is rejected."""
        # Config missing required fields
        invalid_config = {
            "core": {
                # Missing encryption config
                "database": {"path": ":memory:"},
            },
        }

        with pytest.raises(Exception):  # Pydantic validation error  # noqa: B017
            validate_config(invalid_config)
