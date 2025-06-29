"""
PyBastion.

A comprehensive tool for analyzing network device configurations for security
vulnerabilities, compliance issues, and best practices violations.

⚠️  WARNING: This is a development version and is not ready for production use.
    Features may change significantly between versions.

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

import warnings

__version__ = "0.0.1-dev"
__author__ = "Randy Bartels"
__email__ = "rjbartels@outlook.com"

# Issue development warning when package is imported
warnings.warn(
    "PyBastion is in active development and not ready for production use. "
    "Features may change significantly between versions. "
    "Visit https://github.com/flyguy62n/pybastion for current status.",
    UserWarning,
    stacklevel=2,
)

__all__ = [
    "Database",
    "ParserFactory",
    "Scanner",
]
