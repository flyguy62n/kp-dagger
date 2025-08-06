# Dagger CLI Interface

This directory contains the complete Command Line Interface (CLI) for Dagger, built with Click and Rich for enhanced terminal experience.

## 🏗️ Structure

```
src/Dagger/cli/
├── __init__.py              # CLI package initialization
├── main.py                  # Main CLI entry point with Click groups
├── commands/                # Individual command modules
│   ├── __init__.py
│   ├── analyze.py          # Configuration analysis command
│   ├── report.py           # Report generation command
│   └── validate.py         # Configuration validation command
└── utils/                   # CLI utility modules
    ├── __init__.py
    ├── config.py           # Configuration management
    ├── helpers.py          # Common helper functions
    └── output.py           # Rich output formatting and logging
```

## 🚀 Features

### Core Commands
- **`analyze`** - Analyze configuration files for security vulnerabilities and compliance issues
- **`validate`** - Validate configuration file syntax and structure
- **`report`** - Generate comprehensive reports from analysis results
- **`config`** - Manage CLI configuration settings

### Enhanced Terminal Experience
- **Rich Formatting** - Colored output, tables, progress bars, and panels
- **Interactive Progress** - Real-time progress reporting for long operations
- **Error Handling** - Comprehensive error reporting with stack traces in verbose mode
- **Configurable Output** - Multiple output formats (table, JSON, YAML)

### Configuration Management
- **Persistent Settings** - User configuration stored in `~/.Dagger/config.json`
- **CLI Options** - Override settings via command-line arguments
- **Environment Variables** - Support for environment-based configuration

## 📋 Command Examples

### Analysis Commands

**PowerShell:**
```powershell
# Basic configuration analysis
Dagger analyze router-config.txt

# Multi-file analysis with specific device type
Dagger analyze --device-type cisco-ios *.cfg

# Full security analysis with CIS benchmarks
Dagger analyze --cis-benchmarks --vulnerability-check config.txt

# Parallel analysis with custom output
Dagger analyze --parallel 4 --format json --output results.json configs/
```

**Bash:**
```bash
# Basic configuration analysis
Dagger analyze router-config.txt

# Multi-file analysis with specific device type
Dagger analyze --device-type cisco-ios *.cfg

# Full security analysis with CIS benchmarks
Dagger analyze --cis-benchmarks --vulnerability-check config.txt

# Parallel analysis with custom output
Dagger analyze --parallel 4 --format json --output results.json configs/
```

### Validation Commands

**PowerShell:**
```powershell
# Basic validation
Dagger validate config.txt

# Strict validation (warnings as errors)
Dagger validate --strict --device-type cisco-asa firewall.cfg

# Batch validation with JSON output
Dagger validate --format json --output validation.json *.txt
```

**Bash:**
```bash
# Basic validation
Dagger validate config.txt

# Strict validation (warnings as errors)
Dagger validate --strict --device-type cisco-asa firewall.cfg

# Batch validation with JSON output
Dagger validate --format json --output validation.json *.txt
```

### Report Generation

**PowerShell:**
```powershell
# Generate HTML report
Dagger report analysis-results.json

# Executive summary in PDF format
Dagger report --template executive --format pdf results.json

# Open report automatically
Dagger report --open --format html results.json
```

**Bash:**
```bash
# Generate HTML report
Dagger report analysis-results.json

# Executive summary in PDF format
Dagger report --template executive --format pdf results.json

# Open report automatically
Dagger report --open --format html results.json
```

### Configuration Management

**PowerShell:**
```powershell
# Show current configuration
Dagger config --show

# Set default output format
Dagger config --set output_format json

# Reset to defaults
Dagger config --reset
```

**Bash:**
```bash
# Show current configuration
Dagger config --show

# Set default output format
Dagger config --set output_format json

# Reset to defaults
Dagger config --reset
```

## 🎛️ Global Options

All commands support these global options:

- `--verbose, -v` - Increase verbosity (can be repeated: -vv, -vvv)
- `--quiet, -q` - Suppress all output except errors
- `--output-format` - Set output format (auto, plain, rich)
- `--version` - Show version information
- `--help` - Show help information

## 🔧 Configuration Options

The CLI supports the following configuration options:

| Setting | Default | Description |
|---------|---------|-------------|
| `output_format` | `"table"` | Default output format |
| `verbose` | `0` | Default verbosity level |
| `parallel_jobs` | `1` | Default number of parallel threads |
| `default_device_type` | `"auto"` | Default device type for analysis |
| `include_passed_checks` | `false` | Include passed checks in output |
| `severity_filter` | `"all"` | Default severity filter |
| `report_template` | `"default"` | Default report template |

## 🎨 Rich Output Features

### Progress Reporting
- Animated spinners for long operations
- Progress bars with time elapsed
- Step-by-step status updates

### Formatted Tables
- Colored headers and borders
- Automatic column sizing
- Sortable results

### Error Display
- Structured error messages
- Stack traces in verbose mode
- Contextual help suggestions

### Interactive Elements
- Confirmation prompts
- File picker dialogs
- Configuration wizards

## 🔗 Integration Points

### Entry Points
The CLI is accessible via:
```python
# Direct import
from Dagger.cli.main import main

# Package entry point (pyproject.toml)
Dagger = "Dagger.cli.main:main"
```

### Extensibility
New commands can be added by:
1. Creating a new module in `commands/`
2. Implementing the Click command
3. Adding to `main.py` command group

### Error Handling
Consistent error handling across all commands:
- Graceful handling of missing files
- Network timeouts for API calls
- Memory management for large files
- User interruption (Ctrl+C)

## 🧪 Testing

The CLI structure supports comprehensive testing:
- Unit tests for individual commands
- Integration tests for workflows
- Mock fixtures for external dependencies
- Click's built-in testing utilities

## 📚 Dependencies

Core CLI dependencies (already in pyproject.toml):
- `click>=8.1.0` - Command-line interface framework
- `rich>=13.7.0` - Rich terminal formatting
- `pydantic>=2.5.0` - Data validation (for config)

Optional enhancement dependencies:
- `pyyaml>=6.0.0` - YAML output support
- `openpyxl>=3.1.0` - Excel report generation

## 🚀 Getting Started

1. **Install Dependencies**
   
   **PowerShell:**
   ```powershell
   uv sync  # Install all dependencies
   ```
   
   **Bash:**
   ```bash
   uv sync  # Install all dependencies
   ```

2. **Test CLI**
   
   **PowerShell:**
   ```powershell
   python -m Dagger.cli.main --help
   ```
   
   **Bash:**
   ```bash
   python -m Dagger.cli.main --help
   ```

3. **Run Example**
   
   **PowerShell:**
   ```powershell
   python examples/cli_demo.py
   ```
   
   **Bash:**
   ```bash
   python examples/cli_demo.py
   ```

4. **Development**
   
   **PowerShell:**
   ```powershell
   # Run with development dependencies
   uv run python -m Dagger.cli.main analyze --help
   
   # Command chaining (use semicolon)
   uv sync; uv run python -m Dagger.cli.main --version
   ```
   
   **Bash:**
   ```bash
   # Run with development dependencies
   uv run python -m Dagger.cli.main analyze --help
   
   # Command chaining (use &&)
   uv sync && uv run python -m Dagger.cli.main --version
   ```

This CLI structure provides a solid foundation for Dagger's command-line interface with room for expansion as the core functionality is implemented.
