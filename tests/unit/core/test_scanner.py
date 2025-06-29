"""Test network scanner core functionality."""

import pytest

from network_security_scanner.core.scanner import NetworkScanner


def test_scanner_initialization():
    """Test NetworkScanner initialization."""
    scanner = NetworkScanner(database_path=":memory:")
    assert scanner.database is not None
    assert scanner.parser_factory is not None


def test_device_type_detection():
    """Test device type auto-detection."""
    scanner = NetworkScanner(database_path=":memory:")

    # Test Cisco IOS detection
    ios_config = "hostname router\nversion 15.1\ninterface GigabitEthernet0/0"
    device_type = scanner._detect_device_type(ios_config)
    assert device_type.value == "cisco-ios"

    # Test unsupported device
    with pytest.raises(Exception):
        scanner._detect_device_type("unknown config format")


def test_severity_counting():
    """Test severity counting functionality."""
    scanner = NetworkScanner(database_path=":memory:")

    findings = [
        {"severity": "high"},
        {"severity": "medium"},
        {"severity": "low"},
        {"severity": "high"},
    ]

    counts = scanner._count_severities(findings)
    assert counts["high"] == 2
    assert counts["medium"] == 1
    assert counts["low"] == 1
    assert counts["critical"] == 0
