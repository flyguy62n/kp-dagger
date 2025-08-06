# Contributing to Dagger

Thank you for your interest in contributing to Dagger! This document provides guidelines for contributing to the project.

## 🚧 Current Status

**Dagger is in active development (Pre-Alpha).** Most functionality is not yet implemented. See our [Roadmap](ROADMAP.md) for current development status.

## Getting Started

### Development Environment Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/flyguy62n/Dagger.git
   cd Dagger
   ```

2. **Install dependencies**:
   ```bash
   uv sync --group dev
   ```

3. **Run tests**:
   ```bash
   uv run pytest
   ```

4. **Run linting**:
   ```bash
   uv run ruff check
   uv run ruff format
   ```

### Prerequisites

- Python 3.12 or higher
- UV package manager
- Git
- Basic understanding of network device configurations

## How to Contribute

### 1. Check Existing Issues

Before starting work, check our [GitHub Issues](https://github.com/flyguy62n/Dagger/issues) to see if someone is already working on what you want to do.

### 2. Create an Issue

For new features or bugs:
1. Use our issue templates
2. Provide detailed descriptions
3. Include relevant context (device types, config samples, etc.)

### 3. Fork and Branch

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Write tests for your changes using PyTest
5. Ensure all tests pass locally

### 4. Submit a Pull Request

1. Push your branch to your fork
2. Create a pull request with:
   - Clear description of changes
   - Link to related issues
   - Test results
   - Any breaking changes noted

## Development Guidelines

> 📖 **For detailed development information**, see our comprehensive [Development Guide](docs/development/contributing.md) which covers advanced topics like adding parsers, security rules, and architectural details.

### Code Style

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
# Check code style
uv run ruff check

# Format code
uv run ruff format
```

My Ruff configuration is in [`ruff.toml`](https://github.com/flyguy62n/dotfiles/ruff.toml) and follows the provided ruff.toml from the user's instructions.

### Type Hints

- Use Python 3.12+ type hints
- Avoid `from typing` imports when possible
- Use `list | None` instead of `Optional[list]`
- Type hint all function parameters and return values

### Testing

- Write unit tests for all new functionality
- Use pytest for testing
- Aim for >90% test coverage
- Include integration tests for parsers with real config samples (`testdata/` folder)

### Documentation

- Document all public APIs
- Include docstrings for classes and functions
- Update README.md for significant changes
- Provide examples in documentation

## Areas Where We Need Help

### High Priority
1. **Device Configuration Samples**: We need sanitized real-world configuration files for testing
2. **Parser Implementation**: Help implement parsers for Cisco, FortiGate, and PaloAlto devices
3. **Security Rules**: Implement CIS benchmark checks and security analysis
4. **Testing**: Write comprehensive unit and integration tests

### Medium Priority
1. **Documentation**: User guides and developer documentation
2. **CLI Implementation**: Command-line interface development
3. **Report Templates**: HTML and Excel report generation
4. **Error Handling**: Robust error handling throughout the application

### Low Priority
1. **Additional Device Types**: Support for Juniper, Arista, etc.
2. **Performance Optimization**: Memory usage and speed improvements
3. **Web Interface**: Future web-based interface
4. **Advanced Features**: Change detection, alerting, etc.

## Contribution Types

### Code Contributions
- Bug fixes
- New features
- Performance improvements
- Test coverage improvements

### Documentation Contributions
- User guides and tutorials
- Code documentation improvements
- Example configurations and use cases
- FAQ and troubleshooting guides

### Testing Contributions
- Additional test cases
- Real-world configuration samples
- Performance benchmarking
- Security testing

### Design Contributions
- UI/UX improvements for CLI
- Report template designs
- Architecture feedback
- Security analysis methodology

## Configuration File Guidelines

When contributing configuration samples:

1. **Sanitize Thoroughly**:
   - Remove all IP addresses, hostnames, passwords
   - Replace with realistic but fake data
   - Remove any proprietary or sensitive information

2. **Document Device Context**:
   - Device model and OS version
   - Configuration purpose (router, firewall, etc.)
   - Any special features demonstrated

3. **File Organization**:
   ```
   tests/fixtures/configs/
   ├── cisco_ios/
   │   ├── basic_router.cfg
   │   ├── complex_switch.cfg
   │   └── README.md
   ├── cisco_asa/
   ├── fortigate/
   └── paloalto/
   ```

## Security Considerations

### Reporting Security Issues

For security vulnerabilities:
1. **Do NOT** create a public issue
2. Email the maintainer directly: rjbartels@outlook.com
3. Include detailed description and reproduction steps
4. Allow reasonable time for response and fix

### Configuration Handling

- Never commit real configuration files
- Always sanitize sample configurations
- Be aware of sensitive patterns in configs
- Test with various configuration sizes and complexities

## Development Workflow

### For Major Features

1. Create or comment on relevant GitHub issue
2. Discuss approach with maintainers
3. Create feature branch
4. Implement with tests
5. Update documentation
6. Submit pull request
7. Address review feedback
8. Merge when approved

### For Bug Fixes

1. Create issue describing bug (unless obvious)
2. Create fix branch
3. Implement fix with test
4. Submit pull request
5. Quick review and merge

### For Documentation

1. Identify documentation gaps
2. Create or update documentation
3. Submit pull request
4. Review for accuracy and clarity

## Code Review Process

All contributions go through code review:

1. **Automated Checks**: Linting, testing, coverage
2. **Manual Review**: Code quality, design, documentation
3. **Testing**: Functionality and edge cases
4. **Documentation**: Accuracy and completeness

## Recognition

Contributors will be recognized in:
- Repository contributors list
- Release notes for significant contributions
- Project documentation
- Special recognition for major features

## Questions?

- **General Questions**: Open a GitHub Discussion
- **Specific Issues**: Comment on relevant GitHub Issue
- **Security Issues**: Email rjbartels@outlook.com
- **Feature Requests**: Use the feature request template

## Code of Conduct

This project adheres to a code of professional conduct:
- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers get started
- Maintain professional communication

---

Thank you for contributing to Dagger! Your help makes this project better for everyone in the network security community.
