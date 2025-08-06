# Dagger

⚠️ **DEVELOPMENT VERSION - NOT PRODUCTION READY** ⚠️

A comprehensive Python application for analyzing network security device configurations to identify security vulnerabilities, compliance violations, and best practice deviations.

## 🚧 Current Status

**This package is in active development and is not ready for production use.**

- **Version**: 0.0.1 (Pre-Alpha)
- **Purpose**: PyPI name reservation and early development preview
- **Stability**: Features may change significantly between versions
- **Testing**: Limited functionality currently available

### What's Working
- Basic project structure and framework
- Core architecture design
- Development environment setup

### What's Coming
- Configuration file parsing for multiple vendors
- Security analysis and compliance checking
- Comprehensive reporting capabilities
- Full CLI interface

## Planned Features

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

⚠️ **Warning**: This is a development version. Installing from PyPI will give you a minimal placeholder package.

### Prerequisites

- Python 3.12 or higher
- UV package manager (recommended for development)

### Install from PyPI (Development Version)

```bash
pip install Dagger
```

**Note**: The PyPI version currently provides only basic structure and will display warnings when imported. Most functionality is not yet implemented.

### Development Installation (Recommended)

To work with the actual development code:

```bash
git clone https://github.com/flyguy62n/Dagger.git
cd Dagger
uv sync
```

## Development Status & Roadmap

### Planned Usage (Coming Soon)

Once development is complete, Dagger will support:

```bash
# Scan a single configuration file
Dagger scan files router.cfg

# Scan multiple files with device type specification
Dagger scan files --device-type cisco-ios *.cfg

# Scan directory recursively
Dagger scan files --recursive /path/to/configs/

# Generate HTML report
Dagger scan files --format html --output report.html *.cfg
```

### Generate Reports

```bash
# Generate report from database
Dagger report generate --database scan.db --format excel --output report.xlsx
```

### Validate Configurations

```bash
# Validate configuration syntax
Dagger validate config router.cfg --device-type cisco-ios
```

## Contributing

We welcome contributions! Since this is in early development:

1. Check the [Issues](https://github.com/flyguy62n/Dagger/issues) for current tasks
2. Fork the repository
3. Create a feature branch
4. Submit a pull request

### Development Setup

```bash
git clone https://github.com/flyguy62n/Dagger.git
cd Dagger
uv sync --group dev
uv run pytest
```

## Architecture

The application follows a modular, extensible architecture:

```
src/Dagger/
├── cli/                    # Command-line interface
├── core/                   # Core scanning logic
├── models/                 # Data models and schemas
├── parsers/                # Device-specific parsers
├── analyzers/              # Security analysis engines
├── api_clients/            # External API integrations
├── reports/                # Report generation
└── utils/                  # Utility functions
```

## Development Status

### Completed
- ✅ Project structure and architecture design
- ✅ Core framework setup
- ✅ Development environment configuration
- ✅ Base model classes and interfaces

### In Progress
- 🚧 Configuration file parsers
- 🚧 Security analysis engines
- 🚧 CLI interface implementation

### Planned
- 📅 API client integrations (CVE Details, End of Life)
- 📅 Report generation system
- 📅 Comprehensive test suite
- 📅 Documentation and examples

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/flyguy62n/Dagger.git
cd Dagger

# Install dependencies
uv sync --group dev

# Run tests
uv run pytest

# Run linting
uv run ruff check
uv run ruff format
```

### Publishing to PyPI

This package is currently published as a development placeholder to reserve the name. The process:

```bash
# Build the package
uv build

# Test on TestPyPI first
uv publish --repository testpypi

# Publish to PyPI
uv publish
```

## License

This project is licensed under the MIT License.

## Contact

- **Author**: Randy Bartels
- **Email**: rjbartels@outlook.com
- **Repository**: https://github.com/flyguy62n/Dagger
- **Issues**: https://github.com/flyguy62n/Dagger/issues
