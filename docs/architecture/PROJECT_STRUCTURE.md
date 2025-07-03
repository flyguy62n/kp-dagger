# PyBastion - Project Structure

This document outlines the complete project structure for PyBastion, a Python-based tool for analyzing network device configurations for security vulnerabilities, compliance issues, and best practices violations.

## Overview

PyBastion is designed with a modular, extensible architecture that:
- Parses network device configurations from multiple vendors (Cisco IOS/ASA, FortiGate, PAN-OS)
- Normalizes device-specific data into a common database schema using DuckDB
- Performs SQL-based security analysis and compliance checking
- Generates comprehensive reports in multiple formats (JSON, HTML, Excel)

## Project Structure

```
pybastion/
├── .github/                          # GitHub configuration and workflows
├── src/pybastion/     # Main application source code
├── tests/                            # Test suite
├── sql/                              # Database schema and queries
├── docs/                             # Documentation
├── scripts/                          # Development and build scripts
└── [configuration files]            # Project configuration
```

## Detailed Component Description

### `.github/`
GitHub-specific configuration and automation.

```
.github/
├── workflows/
│   ├── ci.yml                        # Continuous integration pipeline
│   └── release.yml                   # Release automation workflow
└── copilot-instructions.md           # Development guidelines and standards
```

**Purpose:**
- **`workflows/`**: Automated testing, linting, and release processes
- **`copilot-instructions.md`**: Coding standards and architectural guidelines

### `src/pybastion/`
Main application source code organized by functional areas.

#### `cli/` - Command Line Interface
```
cli/
├── __init__.py
├── main.py                           # Main CLI entry point with Click
├── commands/                         # CLI command implementations
│   ├── scan.py                       # Scanning operations
│   ├── report.py                     # Report generation commands
│   ├── config.py                     # Configuration management
│   └── validate.py                   # Configuration validation
├── options.py                        # Reusable Click options and parameters
└── utils.py                          # CLI utility functions
```

**Purpose:**
- Provides user-friendly command-line interface using Click
- Supports batch operations, configuration management, and report generation
- Handles user input validation and error reporting

#### `core/` - Core Application Logic
```
core/
├── __init__.py
├── database.py                       # DuckDB connection and management
├── config.py                         # Application configuration handling
├── exceptions.py                     # Custom exception classes
├── scanner.py                        # Main scanning orchestrator
└── normalizer.py                     # Parser output → DB normalization
```

**Purpose:**
- **`database.py`**: DuckDB connection management, schema creation, migrations
- **`scanner.py`**: Coordinates parsing, normalization, and analysis workflows
- **`normalizer.py`**: Converts device-specific models to normalized database models
- **`config.py`**: Handles application settings, API keys, and user preferences

#### `models/` - Data Models Package
Comprehensive data model definitions using SQLModel for both validation and ORM.

##### `models/base/` - Foundation Models
```
models/base/
├── __init__.py
├── mixins.py                         # Common SQLModel mixins (timestamps, device refs)
├── types.py                          # Custom field types (IP addresses, protocols)
├── validators.py                     # Pydantic validators for network concepts
└── enums.py                          # Common enumerations across all models
```

**Purpose:**
- Provides reusable components for all model definitions
- Ensures consistency in data validation and relationships
- Defines network-specific data types and validation rules

##### `models/normalized/` - Database Schema Models
```
models/normalized/
├── device.py                         # Device metadata and information
├── network.py                        # Networks, subnets, IP addresses
├── access_control.py                 # ACLs, firewall rules (device-agnostic)
├── interfaces.py                     # Network interface configurations
├── routing.py                        # Routing tables and protocol configs
├── vpn.py                            # VPN configurations
├── services.py                       # Service definitions and port mappings
├── objects.py                        # Network/service object definitions
├── users.py                          # User accounts and authentication
├── policies.py                       # Security policies
├── nat.py                            # NAT configurations
├── zones.py                          # Security zones
├── certificates.py                   # SSL/TLS certificate information
└── system.py                         # System configuration settings
```

**Purpose:**
- Defines the unified database schema for all device types
- Enables device-agnostic security analysis through SQL queries
- Provides consistent data structure for reporting and analysis

##### `models/{device_type}/` - Device-Specific Models
```
models/cisco_ios/                     # Cisco IOS specific models
models/cisco_asa/                     # Cisco ASA specific models  
models/fortigate/                     # FortiGate specific models
models/paloalto/                      # PAN-OS specific models
├── __init__.py
├── base.py                           # Device-specific base classes
├── access_list.py                    # Device ACL models
├── interface.py                      # Interface configuration models
├── routing.py                        # Routing protocol models
├── security.py                       # Security feature models
├── system.py                         # System configuration models
└── [device-specific modules]         # Additional device features
```

**Purpose:**
- Models device-specific configuration syntax and structure
- Serves as intermediate representation between raw config and normalized DB
- Handles vendor-specific terminology and feature sets

##### `models/analysis/` - Analysis Result Models
```
models/analysis/
├── findings.py                       # Security findings and issues
├── compliance.py                     # CIS compliance check results
├── vulnerabilities.py                # CVE and vulnerability data
├── risks.py                          # Risk assessment results
└── reports.py                        # Report metadata and summaries
```

**Purpose:**
- Structures analysis results for consistent reporting
- Links findings to specific devices and configurations
- Tracks remediation status and priorities

##### `models/api_clients/` - External API Models
```
models/api_clients/
├── cve.py                            # CVE Details API data structures
├── eol.py                            # End-of-life API data structures
└── vendor.py                         # Vendor information models
```

**Purpose:**
- Models external API responses for vulnerability and lifecycle data
- Provides validation for third-party data integration
- Normalizes vendor information across different APIs

#### `parsers/` - Configuration Parsing Package
Device-specific configuration file parsers with normalization capabilities.

##### `parsers/base/` - Parser Foundation
```
parsers/base/
├── __init__.py
├── parser.py                         # Abstract base parser interface
├── lexer.py                          # Base tokenization functionality
├── ast_nodes.py                      # Configuration AST node definitions
├── normalizer.py                     # Base normalization interface
└── exceptions.py                     # Parser-specific exceptions
```

**Purpose:**
- Defines common parser interface for all device types
- Provides shared lexical analysis and AST building functionality
- Ensures consistent error handling across all parsers

##### `parsers/{device_type}/` - Device-Specific Parsers
```
parsers/cisco_ios/                    # Example: Cisco IOS parser
├── __init__.py
├── parser.py                         # Main parser orchestrator
├── lexer.py                          # Device-specific tokenization
├── normalizer.py                     # IOS models → normalized models
├── commands/                         # Command-specific parsing modules
│   ├── access_list.py                # ACL parsing logic
│   ├── interface.py                  # Interface configuration parsing
│   ├── routing.py                    # Routing protocol parsing
│   ├── security.py                   # Security feature parsing
│   └── system.py                     # System configuration parsing
└── utils.py                          # Parser utility functions
```

**Purpose:**
- Handles device-specific configuration syntax and command structures
- Converts raw configuration text into structured data models
- Normalizes device configurations into common database format

#### `analyzers/` - Security Analysis Engine
SQL-based analysis modules for security assessment and compliance checking.

##### `analyzers/sql/` - Analysis Modules
```
analyzers/sql/
├── acl_analyzer.py                   # Access control list analysis
├── compliance_analyzer.py            # CIS benchmark compliance checking
├── vulnerability_analyzer.py         # CVE and vulnerability assessment
├── network_analyzer.py               # Network topology and configuration analysis
├── routing_analyzer.py               # Routing protocol security analysis
└── policy_analyzer.py                # Security policy consistency checking
```

**Purpose:**
- Performs database-driven security analysis using SQL queries
- Implements CIS Level 1 benchmark checking
- Identifies risky configurations and policy violations

##### `analyzers/queries/` - SQL Query Library
```
analyzers/queries/
├── risky_rules.sql                   # Queries for identifying risky ACL rules
├── compliance_checks.sql             # CIS compliance validation queries
├── network_analysis.sql              # Network configuration analysis
├── routing_analysis.sql              # Routing security assessment queries
└── policy_conflicts.sql              # Policy consistency checking
```

**Purpose:**
- Reusable SQL queries for common security analysis patterns
- Optimized queries for performance on large datasets
- Standardized analysis logic across all device types

##### `analyzers/rules/` - Analysis Rules and Benchmarks
```
analyzers/rules/
├── cis_benchmarks/                   # CIS benchmark implementations
│   ├── level1_checks.py              # Generic Level 1 security checks
│   ├── network_rules.py              # Network-related CIS rules
│   ├── routing_rules.py              # Routing protocol security rules
│   ├── access_rules.py               # Access control CIS rules
│   └── system_rules.py               # System configuration CIS rules
├── risk_patterns.py                  # Common security risk patterns
└── vulnerability_rules.py            # Vulnerability assessment rules
```

**Purpose:**
- Implements industry-standard security benchmarks (CIS Level 1)
- Defines risk assessment criteria and scoring
- Provides extensible framework for adding new security rules

#### `api_clients/` - External API Integration
```
api_clients/
├── __init__.py
├── base.py                           # Base API client with rate limiting
├── cve_client.py                     # CVE Details API client
├── eol_client.py                     # End of Life API client
└── exceptions.py                     # API client specific exceptions
```

**Purpose:**
- Integrates with external vulnerability and lifecycle databases
- Provides rate limiting and error handling for API calls
- Normalizes external data for internal use

#### `reports/` - Report Generation System
Multi-format report generation with templates and customization.

```
reports/
├── __init__.py
├── base.py                           # Base reporter interface
├── json_reporter.py                  # Machine-readable JSON reports
├── html_reporter.py                  # Web-based HTML reports with styling
├── excel_reporter.py                 # Rich Excel reports with charts
├── templates/                        # Report templates
│   ├── security_report_template.xlsx # Executive security report template
│   ├── compliance_template.xlsx      # CIS compliance report template
│   └── vulnerability_template.xlsx   # Vulnerability tracking template
└── queries/                          # Report-specific database queries
    ├── summary_stats.sql              # Executive summary statistics
    ├── findings_detail.sql            # Detailed findings queries
    └── compliance_report.sql          # Compliance reporting queries
```

**Purpose:**
- Generates professional reports for different audiences
- Provides templated Excel reports with charts and formatting
- Supports both technical detail and executive summary formats

#### `utils/` - Utility Functions
```
utils/
├── logging.py                        # Centralized logging configuration
├── validation.py                     # Data validation utilities
├── sql_helpers.py                    # SQL utility functions and query builders
└── helpers.py                        # General purpose utility functions
```

**Purpose:**
- Common functionality shared across all modules
- Centralized logging and error handling
- Database and validation utilities

### `tests/` - Test Suite
Comprehensive testing strategy covering unit, integration, and SQL testing.

```
tests/
├── __init__.py
├── conftest.py                       # Pytest configuration and fixtures
├── unit/                             # Unit tests for individual components
│   ├── test_cli.py                   # CLI functionality testing
│   ├── test_database.py              # Database operations testing
│   ├── test_normalizers.py           # Data normalization testing
│   ├── test_analyzers.py             # Analysis engine testing
│   ├── test_reports.py               # Report generation testing
│   ├── test_api_clients.py           # External API testing
│   ├── models/                       # Model validation testing
│   └── parsers/                      # Parser functionality testing
├── integration/                      # Integration and end-to-end testing
│   ├── test_end_to_end.py            # Complete workflow testing
│   ├── test_cli_integration.py       # CLI integration testing
│   ├── test_database_integration.py  # Database integration testing
│   ├── test_model_relationships.py   # Model relationship testing
│   └── test_api_clients_integration.py # External API integration testing
├── sql/                              # SQL query testing
│   ├── test_analyzer_queries.py      # Analysis query validation
│   └── test_report_queries.py        # Report query validation
└── fixtures/                         # Test data and fixtures
    ├── configs/                      # Sample device configurations
    ├── expected_results/             # Expected analysis results
    ├── sample_databases/             # Test database snapshots
    ├── model_samples/                # Sample model instances
    └── excel_templates/              # Test Excel report templates
```

**Purpose:**
- Ensures code quality and reliability through comprehensive testing
- Validates parser accuracy with real device configurations
- Tests database queries and analysis logic

### `sql/` - Database Management
Database schema definitions, migrations, and production queries.

```
sql/
├── schema/                           # Database schema management
│   ├── 001_initial_schema.sql        # Initial database schema
│   ├── 002_add_indexes.sql           # Performance optimization indexes
│   └── 003_add_views.sql             # Commonly used database views
└── queries/                          # Production SQL queries
    ├── analysis/                     # Analysis-specific queries
    ├── reports/                      # Report generation queries
    └── maintenance/                  # Database maintenance queries
```

**Purpose:**
- Version-controlled database schema evolution
- Performance-optimized queries for production use
- Database maintenance and optimization scripts

### `docs/` - Documentation
Comprehensive documentation for users and developers.

```
docs/
├── api/                              # API documentation
│   ├── models/                       # Data model documentation
│   └── api_clients.md                # External API integration guide
├── user_guide/                       # End-user documentation
│   ├── cli_reference.md              # Command-line interface guide
│   └── report_formats.md             # Report format descriptions
├── developer_guide/                  # Developer documentation
│   ├── database_schema.md            # Database design documentation
│   ├── model_design.md               # Data model design principles
│   ├── normalization_guide.md        # Parser normalization guide
│   └── adding_device_types.md        # Guide for adding new device support
└── examples/                         # Usage examples and samples
    └── sample_reports/               # Example generated reports
```

**Purpose:**
- Provides comprehensive user and developer documentation
- Documents architectural decisions and design patterns
- Includes examples and best practices

### `scripts/` - Development and Build Scripts
```
scripts/
├── setup_dev.py                     # Development environment setup
└── build_release.py                 # Release packaging and distribution
```

**Purpose:**
- Automates development environment setup
- Handles release packaging and PyPI distribution

### Configuration Files
```
.gitignore                            # Git ignore patterns
.ruff.toml                            # Ruff linting and formatting configuration
pyproject.toml                        # Project configuration and dependencies
uv.lock                               # UV lock file for reproducible builds
README.md                             # Project overview and quick start
LICENSE                               # Software license
CHANGELOG.md                          # Release notes and version history
main.py                               # Application entry point wrapper
```

## Key Architectural Principles

### 1. **Extensibility**
- Plugin-based architecture for adding new device types
- Clear interfaces for parsers, analyzers, and reporters
- Device-agnostic analysis through normalized data models

### 2. **Separation of Concerns**
- Parsing logic isolated from analysis logic
- Device-specific complexity contained in parser packages
- Database-driven analysis for consistency and performance

### 3. **Data Normalization**
- Device configurations normalized into common database schema
- SQL-based analysis works across all device types
- Consistent reporting regardless of source device type

### 4. **Comprehensive Testing**
- Unit tests for individual components
- Integration tests for complete workflows
- SQL query validation and performance testing

### 5. **Professional Reporting**
- Multiple output formats for different audiences
- Rich Excel reports with charts and conditional formatting
- Executive summaries and detailed technical reports

## Development Workflow

1. **Configuration Parsing**: Device configs → Device-specific models
2. **Data Normalization**: Device models → Normalized database models
3. **Security Analysis**: SQL queries → Analysis results
4. **Report Generation**: Analysis results → Formatted reports
5. **External Integration**: API calls → Vulnerability and lifecycle data

This structure provides a robust, maintainable, and extensible foundation for comprehensive network security analysis.
