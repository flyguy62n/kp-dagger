# Development Guide

This comprehensive guide covers all aspects of developing PyBastion. For quick contribution steps, see the [main CONTRIBUTING.md](../../CONTRIBUTING.md) file.

## Overview

This development guide provides detailed information for contributors who want to understand PyBastion's architecture, add new features, or maintain the codebase.

## Quick Start for Contributors

If you're new to contributing, start with the [main CONTRIBUTING.md](../../CONTRIBUTING.md) which covers:
- Basic setup steps
- Issue creation and PR process  
- Community guidelines
- Quick development workflow

This guide provides deeper technical details for ongoing development work.

## Recommended Workflow for Single-Developer Activity

This is mostly for my own reference unless/until others join the project:

```Powershell
# For any new feature work:
git checkout main
git pull origin main
git checkout -b feature/short-name

# Work on feature (commit frequently)
git add .
git commit -m "feat: implement X"

# When complete (within 1-3 days):
git checkout main
git merge feature/short-name
git branch -d feature/short-name
git push origin main
```

## Advanced Development Setup

### Prerequisites

- Python 3.13 or higher
- UV package manager (recommended) or pip
- Git
- Basic understanding of network device configurations

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/pybastion.git
   cd pybastion
   ```

2. **Install Development Dependencies**
   ```bash
   # Using UV (recommended)
   uv pip install -e .[dev,docs]
   
   # Using pip
   pip install -e .[dev,docs]
   ```

3. **Set Up Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

4. **Verify Installation**
   ```bash
   pytest tests/
   pybastion --version
   mkdocs serve
   ```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

Follow the coding standards and guidelines below.

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/pybastion

# Run specific test file
pytest tests/unit/parsers/test_cisco_ios.py
```

### 4. Update Documentation

- Update docstrings for new functions/classes
- Add examples to documentation
- Update API reference if needed

### 5. Submit a Pull Request

- Write a clear PR description
- Reference any related issues
- Include test results
- Wait for code review

## Coding Standards

### Python Code Style

We use Ruff for linting and formatting:

```bash
# Check code style
ruff check src/ tests/

# Format code
ruff format src/ tests/
```

### Type Hints

Use modern Python type hints:

```python
# ✅ Good - Modern type hints
def process_config(data: str | None) -> dict[str, Any]:
    pass

# ❌ Bad - Old typing module
from typing import Optional, Dict, Any
def process_config(data: Optional[str]) -> Dict[str, Any]:
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def parse_interface_config(config_line: str) -> Interface:
    """Parse a single interface configuration line.
    
    Args:
        config_line: Raw configuration line from device
        
    Returns:
        Parsed interface object with normalized data
        
    Raises:
        ParseError: If configuration line is malformed
        
    Example:
        >>> line = "interface FastEthernet0/1"
        >>> interface = parse_interface_config(line)
        >>> interface.name
        'FastEthernet0/1'
    """
```

### Error Handling

Use specific exception types:

```python
# ✅ Good - Specific exceptions
from pybastion.core.exceptions import ParseError, ValidationError

def parse_config(content: str) -> dict[str, Any]:
    if not content.strip():
        raise ValidationError("Configuration content is empty")
    try:
        return _do_parse(content)
    except Exception as e:
        raise ParseError(f"Failed to parse configuration: {e}") from e
```

## Adding New Features

### Adding a New Device Parser

1. **Create Parser Module**
   ```
   src/pybastion/parsers/new_vendor/
   ├── __init__.py
   ├── parser.py
   └── models.py
   ```

2. **Implement Base Parser**
   ```python
   from pybastion.parsers.base import BaseParser
   
   class NewVendorParser(BaseParser):
       def parse(self, content: str) -> dict[str, Any]:
           # Implementation here
           pass
   ```

3. **Register Parser**
   ```python
   # In src/pybastion/parsers/factory.py
   from .new_vendor.parser import NewVendorParser
   
   PARSER_REGISTRY = {
       # ...existing parsers...
       "new-vendor": NewVendorParser,
   }
   ```

4. **Add Tests**
   ```
   tests/unit/parsers/test_new_vendor.py
   tests/fixtures/configs/new_vendor/
   ```

### Adding New Analysis Rules

1. **Create Rule Module**
   ```python
   # src/pybastion/analyzers/rules/new_rule.py
   from pybastion.analyzers.base import SecurityRule
   
   class NewSecurityRule(SecurityRule):
       rule_id = "NEW-001"
       title = "Check for security issue"
       severity = Severity.HIGH
       
       def analyze(self, device: Device) -> list[SecurityFinding]:
           # Implementation here
           pass
   ```

2. **Register Rule**
   ```python
   # In src/pybastion/analyzers/__init__.py
   from .rules.new_rule import NewSecurityRule
   
   RULE_REGISTRY = [
       # ...existing rules...
       NewSecurityRule,
   ]
   ```

### Adding New Report Formats

1. **Create Report Handler**
   ```python
   # src/pybastion/reports/formatters/new_format.py
   from pybastion.reports.base import BaseReportFormatter
   
   class NewFormatReporter(BaseReportFormatter):
       format_name = "new-format"
       file_extension = ".ext"
       
       def generate(self, findings: list[SecurityFinding]) -> bytes:
           # Implementation here
           pass
   ```

2. **Register Handler**
   ```python
   # In src/pybastion/reports/factory.py
   from .formatters.new_format import NewFormatReporter
   
   FORMATTER_REGISTRY = {
       # ...existing formatters...
       "new-format": NewFormatReporter,
   }
   ```

## Testing Guidelines

### Test Structure

```
tests/
├── unit/                 # Unit tests
│   ├── parsers/
│   ├── analyzers/
│   └── models/
├── integration/          # Integration tests
├── fixtures/            # Test data
│   └── configs/         # Sample configurations
└── conftest.py          # Pytest configuration
```

### Writing Tests

```python
import pytest
from pybastion.parsers.cisco_ios import CiscoIOSParser

class TestCiscoIOSParser:
    @pytest.fixture
    def parser(self):
        return CiscoIOSParser()
    
    @pytest.fixture
    def sample_config(self):
        return """
        hostname test-router
        interface FastEthernet0/1
         ip address 192.168.1.1 255.255.255.0
        """
    
    def test_parse_hostname(self, parser, sample_config):
        result = parser.parse(sample_config)
        assert result["hostname"] == "test-router"
    
    def test_parse_interface(self, parser, sample_config):
        result = parser.parse(sample_config)
        interfaces = result["interfaces"]
        assert len(interfaces) == 1
        assert interfaces[0]["name"] == "FastEthernet0/1"
        assert interfaces[0]["ip_address"] == "192.168.1.1"
```

### Test Coverage

Maintain high test coverage:

```bash
# Generate coverage report
pytest --cov=src/pybastion --cov-report=html

# View coverage
open htmlcov/index.html
```

## Documentation

### API Documentation

Use docstrings that mkdocstrings can parse:

```python
class SecurityAnalyzer:
    """Performs security analysis on network device configurations.
    
    This class implements various security checks including CIS benchmark
    compliance, vulnerability assessment, and best practice validation.
    
    Attributes:
        tenant_id: Unique identifier for the tenant
        rules: List of active security rules
        
    Example:
        ```python
        analyzer = SecurityAnalyzer(tenant_id)
        findings = analyzer.analyze(device_config)
        ```
    """
```

### User Documentation

- Write clear, step-by-step guides
- Include practical examples
- Use proper Markdown formatting
- Add diagrams where helpful

### Building Documentation

```bash
# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build

# Deploy to GitHub Pages (maintainers only)
mkdocs gh-deploy
```

## Pull Request Process

### Before Submitting

1. ✅ All tests pass
2. ✅ Code follows style guidelines
3. ✅ Documentation is updated
4. ✅ No new lint errors
5. ✅ Commit messages are clear

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added for new functionality
```

### Review Process

1. **Automated Checks** - CI/CD pipeline runs
2. **Code Review** - Maintainer reviews code
3. **Testing** - Additional testing if needed
4. **Approval** - Approved by maintainer
5. **Merge** - Merged into main branch

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow professional standards

### Communication

- **GitHub Issues** - Bug reports and feature requests
- **Discussions** - Questions and general discussion
- **Pull Requests** - Code contributions

### Getting Help

- Check existing documentation
- Search GitHub issues
- Ask in GitHub discussions
- Contact maintainers for urgent issues

## Release Process

### Version Numbering

We follow Semantic Versioning (SemVer):

- **MAJOR** - Breaking changes
- **MINOR** - New features (backward compatible)
- **PATCH** - Bug fixes (backward compatible)

### Release Steps (Maintainers)

1. Update version in `src/pybastion/__init__.py`
2. Update CHANGELOG.md
3. Create release PR
4. Tag release after merge
5. Publish to PyPI
6. Update documentation

## Recognition

Contributors are recognized in:

- README.md contributors section
- Release notes
- Documentation credits
- GitHub contributor graphs

Thank you for contributing to PyBastion! 🎉
