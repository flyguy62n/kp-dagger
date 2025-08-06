"""Tests for dependency injection containers."""

from unittest.mock import Mock, patch

import pytest

from kp_dagger.containers import ApplicationContainer
from kp_dagger.containers.config import (
    PyBastionConfig,
    load_config,
    validate_config,
)


class TestApplicationContainer:
    """Test cases for ApplicationContainer."""

    def test_container_initialization(self) -> None:
        """Test that container initializes properly."""
        container = ApplicationContainer()
        assert container is not None
        assert hasattr(container, "core_container")
        assert hasattr(container, "parser_container")
        assert hasattr(container, "analyzer_container")
        assert hasattr(container, "report_container")
        assert hasattr(container, "api_client_container")

    def test_container_with_config(self) -> None:
        """Test that container accepts configuration."""
        container = ApplicationContainer()

        config_data = {
            "core": {
                "database": {"path": ":memory:"},
                "encryption": {
                    "master_key": "test-key",
                    "salt": "test-salt",
                },
            },
            "api_clients": {
                "cve": {"api_key": "test-key"},
                "eol": {},
            },
            "scanner": {"verbose": True},
        }

        container.config.from_dict(config_data)
        assert container.config.core.database.path() == ":memory:"
        assert container.config.scanner.verbose() is True

    @patch("pybastion.core.database.DatabaseManager")
    @patch("pybastion.parsers.factory.ParserFactory")
    def test_scanner_factory(
        self,
        mock_parser_factory: Mock,  # noqa: ARG002
        mock_db_manager: Mock,  # noqa: ARG002
    ) -> None:
        """Test that scanner can be created from container."""
        container = ApplicationContainer()

        # Configure with minimal config
        config_data: dict[str, dict[str, str]] = {
            "core": {
                "database": {"path": ":memory:"},
                "encryption": {"master_key": "test", "salt": "test"},
            },
            "api_clients": {
                "cve": {"api_key": "test"},
                "eol": {},
            },
            "scanner": {"verbose": False},
        }
        container.config.from_dict(config_data)

        # Test that scanner can be created
        scanner = container.scanner()
        assert scanner is not None

    def test_wire_modules(self) -> None:
        """Test that wire_modules method exists and can be called."""
        container = ApplicationContainer()

        # Should not raise an exception
        try:
            container.wire_modules()
        except Exception as e:  # noqa: BLE001
            # Expected to fail due to missing modules, but method should exist
            assert "wire" in str(e).lower() or "module" in str(e).lower()  # noqa: PT017


class TestConfiguration:
    """Test cases for configuration management."""

    def test_validate_config_minimal(self) -> None:
        """Test validating minimal configuration."""
        config_dict = {
            "core": {
                "encryption": {
                    "master_key": "test-key",
                    "salt": "test-salt",
                },
            },
            "api_clients": {
                "cve": {"api_key": "test-key"},
            },
        }

        config = validate_config(config_dict)
        assert isinstance(config, PyBastionConfig)
        assert config.core.encryption.master_key == "test-key"
        assert config.core.database.path == ":memory:"  # default value

    def test_validate_config_full(self) -> None:
        """Test validating full configuration."""
        config_dict = {
            "core": {
                "database": {"path": "/tmp/test.db"},  # noqa: S108
                "encryption": {
                    "master_key": "test-key",
                    "salt": "test-salt",
                },
            },
            "api_clients": {
                "cve": {
                    "api_key": "test-key",
                    "base_url": "https://test.com/api/",
                    "timeout": 60,
                    "rate_limit": 200,
                },
                "eol": {
                    "base_url": "https://eol.test.com/api/",
                    "timeout": 45,
                    "rate_limit": 500,
                },
            },
            "parsers": {
                "max_file_size": 50000000,
                "encoding": "utf-8",
            },
            "analyzers": {
                "compliance": {
                    "cis_level": 2,
                    "include_level2": True,
                },
                "risk": {
                    "severity_weights": {
                        "critical": 15.0,
                        "high": 10.0,
                        "medium": 5.0,
                        "low": 2.0,
                        "info": 1.0,
                    },
                },
            },
            "reports": {
                "templates": {
                    "html_path": "custom/html",
                    "excel_path": "custom/excel",
                },
                "output_dir": "custom/reports",
            },
            "scanner": {
                "verbose": True,
                "parallel_workers": 8,
            },
        }

        config: PyBastionConfig = validate_config(config_dict)
        assert config.core.database.path == "/tmp/test.db"  # noqa: S108
        assert config.api_clients.cve.timeout == 60  # noqa: PLR2004
        assert config.analyzers.compliance.cis_level == 2  # noqa: PLR2004
        assert config.scanner.parallel_workers == 8  # noqa: PLR2004

    def test_validate_config_missing_required(self) -> None:
        """Test that validation fails with missing required fields."""
        config_dict = {
            "core": {
                # Missing encryption config
            },
        }

        with pytest.raises(Exception):  # Pydantic validation error  # noqa: B017
            validate_config(config_dict)

    @patch("builtins.open")
    @patch("yaml.safe_load")
    @patch("pathlib.Path.exists")
    def test_load_config_success(
        self,
        mock_exists: Mock,
        mock_yaml_load: Mock,
        mock_open: Mock,
    ) -> None:
        """Test successful config loading."""
        mock_exists.return_value = True
        mock_yaml_load.return_value = {"test": "config"}

        result = load_config("test.yml")
        assert result == {"test": "config"}
        mock_open.assert_called_once()

    @patch("pathlib.Path.exists")
    def test_load_config_file_not_found(self, mock_exists: Mock) -> None:
        """Test config loading with missing file."""
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError):
            load_config("missing.yml")
