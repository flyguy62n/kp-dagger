# PyBastion

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
pip install pybastion
```

### Development Installation

```bash
git clone https://github.com/flyguy62n/pybastion.git
cd pybastion
uv sync
```

## Quick Start

### Scan Configuration Files

```bash
# Scan a single configuration file
pybastion scan files router.cfg

# Scan multiple files with device type specification
pybastion scan files --device-type cisco-ios *.cfg

# Scan directory recursively
pybastion scan files --recursive /path/to/configs/

# Generate HTML report
pybastion scan files --format html --output report.html *.cfg
```

### Generate Reports

```bash
# Generate report from database
pybastion report generate --database scan.db --format excel --output report.xlsx
```

### Validate Configurations

```bash
# Validate configuration syntax
pybastion validate config router.cfg --device-type cisco-ios
```

## Architecture

The application follows a modular, extensible architecture:

```
src/pybastion/
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
git clone https://github.com/flyguy62n/pybastion.git
cd pybastion

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
