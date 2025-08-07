# Dagger - Project Structure

This document outlines the complete project structure for Dagger, a Python-based tool for analyzing network device configurations for security vulnerabilities, compliance issues, and best practices violations.

## Overview

KP-Dagger is designed with a **service-oriented architecture using dependency injection** that:
- Uses service layer pattern with dependency injection containers for modularity and testability
- Parses network device configurations from multiple vendors (Cisco IOS/ASA, FortiGate, PAN-OS)
- Normalizes device-specific data into a common database schema using SQLite
- Performs SQL-based security analysis and compliance checking through service orchestration
- Generates comprehensive reports in multiple formats (JSON, HTML, Excel)
- Provides UI-agnostic event system for flexible user interface implementation

## Project Structure

```
Dagger/
├── .github/                          # GitHub configuration and workflows
├── src/kp_dagger/                    # Main application source code
│   ├── services/                     # Service layer with dependency injection
│   ├── containers/                   # Dependency injection containers
│   ├── cli/                          # Command line interface
│   ├── core/                         # Legacy core components (transitioning)
│   ├── models/                       # Data models (SQLModel/Pydantic)
│   ├── parsers/                      # Device-specific parser implementations
│   ├── analyzers/                    # Security analysis implementations  
│   ├── reports/                      # Report generation implementations
│   ├── api_clients/                  # External API client implementations
│   └── utils/                        # Legacy utilities (transitioning to services)
├── tests/                            # Test suite
├── sql/                              # Database schema and queries
├── docs/                             # Documentation
├── scripts/                          # Development and build scripts
└── [configuration files]             # Project configuration
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

### `src/Dagger/`
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

#### `services/` - Service Layer Architecture
Service-oriented architecture using dependency injection for modularity and testability.

##### `services/core/` - Core Infrastructure Services
```
services/core/
├── __init__.py
├── database/
│   ├── __init__.py                   # from .service import DatabaseService
│   ├── interfaces.py                 # IDatabaseService
│   ├── service.py                    # DatabaseService
│   └── manager.py                    # DatabaseManager (SQLite operations)
├── encryption/
│   ├── __init__.py                   # from .service import EncryptionService
│   ├── interfaces.py                 # IEncryptionService
│   ├── service.py                    # EncryptionService
│   └── crypto_engine.py              # Encryption implementation
├── rich_output/
│   ├── __init__.py                   # from .service import RichOutputService
│   ├── interfaces.py                 # IRichOutputService
│   ├── service.py                    # RichOutputService
│   ├── formatters.py                 # Rich formatting components
│   └── themes.py                     # Color themes and styling
├── file_handling/
│   ├── __init__.py                   # from .service import FileHandlingService
│   ├── interfaces.py                 # IFileHandlingService
│   ├── service.py                    # FileHandlingService
│   ├── encoding_detector.py          # File encoding detection
│   └── hash_generator.py             # File integrity hashing
├── parallel_processing/
│   ├── __init__.py                   # from .service import ParallelProcessingService
│   ├── interfaces.py                 # IParallelProcessingService
│   ├── service.py                    # ParallelProcessingService
│   ├── worker_pool.py                # ProcessPoolExecutor management
│   └── task_coordinator.py           # Task distribution and aggregation
├── logging/
│   ├── __init__.py                   # from .service import LoggingService
│   ├── interfaces.py                 # ILoggingService
│   ├── service.py                    # LoggingService
│   ├── handlers.py                   # Custom log handlers
│   └── formatters.py                 # Log formatting (JSON, structured)
├── timestamp/
│   ├── __init__.py                   # from .service import TimestampService
│   ├── interfaces.py                 # ITimestampService
│   ├── service.py                    # TimestampService
│   └── generator.py                  # Timestamp generation utilities
├── events/
│   ├── __init__.py                   # from .service import EventBusService
│   ├── interfaces.py                 # IEventBusService
│   ├── service.py                    # EventBusService
│   └── models.py                     # Event base classes and common events
└── workflow/
    ├── __init__.py                   # from .service import WorkflowService
    ├── interfaces.py                 # IWorkflowService, IProgressReporter
    ├── service.py                    # WorkflowService
    └── progress.py                   # Progress reporting base classes
```

##### `services/parsing/` - Configuration Parsing Services
```
services/parsing/
├── __init__.py
├── interfaces.py                     # IParsingService
├── service.py                        # ParsingService (orchestrates parsers)
├── factory.py                        # ParserFactory (moved from parsers/)
└── utils.py                          # Network validation utilities for parsing
```

##### `services/analysis/` - Security Analysis Services
```
services/analysis/
├── __init__.py
├── interfaces.py                     # IAnalysisService
├── service.py                        # AnalysisService (orchestrates analyzers)
├── compliance/
│   ├── __init__.py
│   └── analyzer.py                   # ComplianceAnalyzer
├── vulnerability/
│   ├── __init__.py
│   └── analyzer.py                   # VulnerabilityAnalyzer
└── risk/
    ├── __init__.py
    └── analyzer.py                   # RiskAnalyzer
```

##### `services/reporting/` - Report Generation Services
```
services/reporting/
├── __init__.py
├── interfaces.py                     # IReportingService
├── service.py                        # ReportingService (orchestrates reporters)
├── json/
│   ├── __init__.py
│   └── reporter.py                   # JsonReporter
├── html/
│   ├── __init__.py
│   └── reporter.py                   # HtmlReporter
└── excel/
    ├── __init__.py
    └── reporter.py                   # ExcelReporter
```

**Purpose:**
- **Core Services**: Infrastructure services (database, encryption, file handling, etc.)
- **Parsing Services**: Orchestrates device configuration parsing operations
- **Analysis Services**: Coordinates security analysis across multiple analyzers  
- **Reporting Services**: Manages report generation in multiple formats
- **Dependency Injection**: Services are injected via containers for modularity and testability

#### `containers/` - Dependency Injection Containers
```
containers/
├── __init__.py
├── application.py                    # ApplicationContainer (main orchestrator)
├── core.py                          # CoreContainer (infrastructure services)
├── parsers.py                       # ParserContainer (parsing services)
├── analyzers.py                     # AnalyzerContainer (analysis services)
├── reports.py                       # ReportContainer (reporting services)
├── api_clients.py                   # ApiClientContainer (external API clients)
└── config.py                        # Configuration models and loading
```

**Purpose:**
- **ApplicationContainer**: Main container orchestrating all service containers
- **Service Containers**: Manage lifecycle and dependencies for specific service domains
- **Configuration**: Pydantic models for type-safe configuration management
- **Wiring**: Automatic dependency injection across application modules

#### `core/` - Legacy Core Components (Transitioning)
```
core/
├── __init__.py
├── exceptions.py                     # Custom exception classes
└── scanner.py                        # Main scanning orchestrator (being replaced by WorkflowService)
```

**Purpose:**
- **`exceptions.py`**: Application-specific exception definitions

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

#### `parsers/` - Configuration Parsing Implementation
Device-specific configuration file parsers (implementation classes only).

```
parsers/
├── __init__.py
├── base/
│   ├── __init__.py
│   ├── parser.py                     # Abstract base parser interface
│   ├── lexer.py                      # Base tokenization functionality
│   ├── ast_nodes.py                  # Configuration AST node definitions
│   ├── normalizer.py                 # Base normalization interface
│   └── exceptions.py                 # Parser-specific exceptions
├── cisco_ios/                        # Cisco IOS parser implementation
│   ├── __init__.py
│   ├── parser.py                     # Main parser orchestrator
│   ├── lexer.py                      # Device-specific tokenization
│   ├── normalizer.py                 # IOS models → normalized models
│   ├── commands/                     # Command-specific parsing modules
│   │   ├── access_list.py            # ACL parsing logic
│   │   ├── interface.py              # Interface configuration parsing
│   │   ├── routing.py                # Routing protocol parsing
│   │   ├── security.py               # Security feature parsing
│   │   └── system.py                 # System configuration parsing
│   └── utils.py                      # Parser utility functions
├── cisco_asa/                        # Cisco ASA parser implementation
├── fortigate/                        # FortiGate parser implementation
└── paloalto/                         # PAN-OS parser implementation
```

**Purpose:**
- Implementation classes for device-specific parsing logic
- Orchestrated by services/parsing/ParsingService
- Factory pattern managed by services/parsing/factory.py
- Converts raw configuration text into structured data models

#### `analyzers/` - Security Analysis Implementation
SQL-based analysis modules (implementation classes only).

```
analyzers/
├── __init__.py
├── queries/                          # SQL query library
│   ├── risky_rules.sql               # Queries for identifying risky ACL rules
│   ├── compliance_checks.sql         # CIS compliance validation queries
│   ├── network_analysis.sql          # Network configuration analysis
│   ├── routing_analysis.sql          # Routing security assessment queries
│   └── policy_conflicts.sql          # Policy consistency checking
├── rules/                            # Analysis rules and benchmarks
│   ├── cis_benchmarks/               # CIS benchmark implementations
│   │   ├── level1_checks.py          # Generic Level 1 security checks
│   │   ├── network_rules.py          # Network-related CIS rules
│   │   ├── routing_rules.py          # Routing protocol security rules
│   │   ├── access_rules.py           # Access control CIS rules
│   │   └── system_rules.py           # System configuration CIS rules
│   ├── risk_patterns.py              # Common security risk patterns
│   └── vulnerability_rules.py        # Vulnerability assessment rules
└── sql/                              # Analysis implementation modules
    ├── acl_analyzer.py               # Access control list analysis
    ├── compliance_analyzer.py        # CIS benchmark compliance checking
    ├── vulnerability_analyzer.py     # CVE and vulnerability assessment
    ├── network_analyzer.py           # Network topology and configuration analysis
    ├── routing_analyzer.py           # Routing protocol security analysis
    └── policy_analyzer.py            # Security policy consistency checking
```

**Purpose:**
- Implementation classes for security analysis logic
- Orchestrated by services/analysis/AnalysisService
- SQL-based analysis for device-agnostic security assessment
- CIS Level 1 benchmark implementations

#### `reports/` - Report Generation Implementation  
Multi-format report generation (implementation classes only).

```
reports/
├── __init__.py
├── generator.py                      # Base report generator
├── templates/                        # Report templates
│   ├── security_report_template.xlsx # Executive security report template
│   ├── compliance_template.xlsx      # CIS compliance report template
│   └── vulnerability_template.xlsx   # Vulnerability tracking template
└── queries/                          # Report-specific database queries
    ├── summary_stats.sql             # Executive summary statistics
    ├── findings_detail.sql           # Detailed findings queries
    └── compliance_report.sql         # Compliance reporting queries
```

**Purpose:**
- Implementation classes for report generation
- Orchestrated by services/reporting/ReportingService
- Template-based report generation with professional formatting
- Support for JSON, HTML, and Excel output formats

#### `utils/` - Utility Functions
```
utils/
├── __init__.py
├── get_file_encoding.py              # File encoding detection (transitioning to services/core/file_handling/)
├── get_timestamp.py                  # Timestamp utilities (transitioning to services/core/timestamp/)
├── hash_generator.py                 # File integrity hashing (transitioning to services/core/file_handling/)
├── logging.py                        # Legacy logging configuration (transitioning to services/core/logging/)
└── network.py                        # Network validation utilities (moving to services/parsing/)
```

**Purpose:**
- Legacy utility functions being transitioned to service-based architecture
- Common functionality shared across modules
- Being gradually migrated to appropriate service packages

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

### 1. **Service-Oriented Architecture with Dependency Injection**
- Service layer pattern with clear interfaces and implementations
- Dependency injection containers for modularity and testability
- UI-agnostic services with event bus pattern for flexible interfaces
- Configuration-driven service behavior through Pydantic models

### 2. **Extensibility**
- Plugin-based architecture for adding new device types
- Clear interfaces for parsers, analyzers, and reporters
- Device-agnostic analysis through normalized data models
- Container-based service registration for new functionality

### 3. **Separation of Concerns**
- Service orchestration separated from implementation logic
- Device-specific complexity contained in implementation packages
- Database-driven analysis coordinated through service layer
- Event system decouples UI from business logic

### 4. **Data Normalization**
- Device configurations normalized into common database schema
- SQL-based analysis works across all device types through service coordination
- Consistent reporting regardless of source device type
- SQLModel provides both ORM and validation capabilities

### 5. **Comprehensive Testing**
- Dependency injection enables easy mocking and testing
- Unit tests for individual service components
- Integration tests for complete service workflows
- Container-based test fixtures for isolated testing

### 6. **Professional Reporting**
- Service-orchestrated report generation across multiple formats
- Rich Excel reports with charts and conditional formatting
- Executive summaries and detailed technical reports
- Template-based report generation through reporting services

## Development Workflow

1. **Service Initialization**: ApplicationContainer → Service containers → Individual services
2. **Configuration Parsing**: ParsingService → Device parsers → Device-specific models
3. **Data Normalization**: ParsingService → Device models → Normalized database models
4. **Security Analysis**: AnalysisService → SQL analyzers → Analysis results
5. **Report Generation**: ReportingService → Format-specific reporters → Formatted reports
6. **External Integration**: API client services → External APIs → Vulnerability and lifecycle data
7. **Event Communication**: EventBusService → UI-agnostic events → Multiple UI implementations

This service-oriented structure provides a robust, maintainable, and extensible foundation for comprehensive network security analysis with dependency injection enabling modularity, testability, and flexible deployment patterns.
