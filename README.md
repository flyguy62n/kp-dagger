# Network Security Scanner

A comprehensive Python application for analyzing network device configurations to identify security vulnerabilities, compliance violations, and best practice deviations.

## Features

- **Multi-vendor Support**: Parse and analyze configurations from:
  - Cisco IOS
  - Cisco ASA
  - FortiGate FortiOS
  - PaloAlto PAN-OS

- **Security Analysis**: 
  - CIS Benchmark compliance checks (Level 1)
  - Access control list analysis
  - Best practice validation
  - Vulnerability assessment using CVE Details API
  - End-of-life software detection

- **Flexible Reporting**: Generate reports in JSON, HTML, and Excel formats

- **Modern Architecture**: Built with Python 3.12+, SQLModel, DuckDB, and Click

## Installation

### Prerequisites

- Python 3.12 or higher
- UV package manager

### Install from PyPI

```bash
pip install network-security-scanner
```

### Development Installation

```bash
git clone https://github.com/flyguy62n/network-security-scanner.git
cd network-security-scanner
uv sync
```

## Quick Start

### Scan Configuration Files

```bash
# Scan a single configuration file
network-scanner scan files router.cfg

# Scan multiple files with device type specification
network-scanner scan files --device-type cisco-ios *.cfg

# Scan directory recursively
network-scanner scan files --recursive /path/to/configs/

# Generate HTML report
network-scanner scan files --format html --output report.html *.cfg
```

### Generate Reports

```bash
# Generate report from database
network-scanner report generate --database scan.db --format excel --output report.xlsx
```

### Validate Configurations

```bash
# Validate configuration syntax
network-scanner validate config router.cfg --device-type cisco-ios
```

## Architecture

The application follows a modular, extensible architecture:

```
src/network_security_scanner/
├── cli/                    # Command-line interface
├── core/                   # Core scanning logic
├── models/                 # Data models and schemas
├── parsers/                # Device-specific parsers
├── analyzers/              # Security analysis engines
├── api_clients/            # External API integrations
├── reports/                # Report generation
└── utils/                  # Utility functions
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/flyguy62n/network-security-scanner.git
cd network-security-scanner

# Install dependencies
uv sync

# Run tests
uv run pytest

# Run linting
uv run ruff check
uv run ruff format
```

## License

This project is licensed under the MIT License.
