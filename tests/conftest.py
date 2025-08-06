"""Conftest for pytest configuration."""

from pathlib import Path
from typing import Any

import pytest

from kp_dagger.core.database import DatabaseManager
from kp_dagger.core.scanner import PyBastionScanner


@pytest.fixture
def temp_config_file(tmp_path: Path) -> Path:
    """Create a temporary configuration file for testing."""
    config_content = """
    hostname test-router
    version 15.1
    !
    interface GigabitEthernet0/0
     ip address 192.168.1.1 255.255.255.0
    !
    access-list 101 permit tcp any any eq 80
    """
    config_file = tmp_path / "test_config.cfg"
    config_file.write_text(config_content)
    return config_file


@pytest.fixture
def memory_database() -> DatabaseManager:
    """Create an in-memory database for testing."""
    db = DatabaseManager(":memory:")
    db.initialize()
    return db


@pytest.fixture
def test_scanner() -> PyBastionScanner:
    """Create a test scanner instance."""
    return PyBastionScanner(database_path=":memory:")


@pytest.fixture
def sample_findings() -> list[dict[str, Any]]:
    """Sample security findings for testing."""
    return [
        {
            "id": "finding-001",
            "title": "Weak password policy",
            "description": "Password encryption not enabled",
            "severity": "medium",
            "category": "authentication",
        },
        {
            "id": "finding-002",
            "title": "Permissive ACL rule",
            "description": "Access list allows any source",
            "severity": "high",
            "category": "access_control",
        },
        {
            "id": "finding-003",
            "title": "SSH version not specified",
            "description": "SSH version 2 not enforced",
            "severity": "low",
            "category": "configuration",
        },
    ]
