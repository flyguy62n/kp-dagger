"""
Network Security Scanner.

A comprehensive tool for analyzing network device configurations for security
vulnerabilities, compliance issues, and best practices violations.

Supports:
- Cisco IOS/ASA configurations
- FortiGate FortiOS configurations
- Palo Alto PAN-OS configurations
- Extensible architecture for additional device types

Features:
- Device configuration parsing and normalization
- SQL-based security analysis
- CIS Level 1 benchmark compliance checking
- CVE and end-of-life vulnerability assessment
- Multi-format reporting (JSON, HTML, Excel)
"""

__version__ = "0.1.0"
__author__ = "Network Security Scanner Team"
__email__ = "contact@network-security-scanner.com"

__all__ = [
    "Database",
    "ParserFactory",
    "Scanner",
]
