#!/usr/bin/env python3
"""Test script to verify basic functionality."""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from kp_dagger.core.exceptions import NetworkScannerError
    from kp_dagger.core.scanner import PyBastionScanner
    from kp_dagger.models.base.enums import DeviceType

    print("✓ All imports successful")

    # Test basic scanner initialization
    scanner = PyBastionScanner(database_path=":memory:")
    print("✓ Scanner initialized successfully")

    # Test device type detection
    test_config = """
    hostname test-router
    version 15.1
    interface GigabitEthernet0/0
     ip address 192.168.1.1 255.255.255.0
    """

    device_type = scanner._detect_device_type(test_config)
    print(f"✓ Device type detection: {device_type.value}")

    # Test report generation
    test_results = [
        {
            "device_id": "test-001",
            "device_type": "cisco-ios",
            "config_file": "test.cfg",
            "findings": [],
            "total_findings": 0,
            "severity_counts": {"low": 0, "medium": 0, "high": 0, "critical": 0},
        },
    ]

    json_report = scanner.generate_report(test_results, "json")
    print("✓ JSON report generation successful")

    html_report = scanner.generate_report(test_results, "html")
    print("✓ HTML report generation successful")

    print("\n🎉 All basic functionality tests passed!")
    print("PyBastion is ready for development.")

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
