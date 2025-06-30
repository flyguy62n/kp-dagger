# PyBastion Documentation

Welcome to PyBastion, a comprehensive network device configuration security analysis tool designed for modern enterprise environments.

## What is PyBastion?

PyBastion is a Python-based security analysis tool that helps network administrators and security professionals:

- **Analyze network device configurations** for security vulnerabilities and compliance issues
- **Support multiple vendor platforms** including Cisco IOS/ASA, Fortinet FortiOS, and Palo Alto PAN-OS
- **Provide detailed security reports** with actionable recommendations
- **Maintain configuration compliance** against industry standards like CIS benchmarks
- **Secure sensitive data** with field-level encryption and multi-tenant isolation

## Key Features

### 🔒 **Enterprise Security**
- **Field-level encryption** using AES256-GCM with Argon2id key derivation
- **Multi-tenant architecture** for service provider deployments
- **Secure data storage** with DuckDB integration

### 📊 **Comprehensive Analysis**
- **CIS Benchmark compliance** checking for Level 1 controls
- **CVE vulnerability assessment** against known security issues
- **End-of-life detection** for outdated firmware versions
- **Access control analysis** for risky firewall rules

### 🛠 **Modern Architecture**
- **SQLModel integration** for type-safe database operations
- **Pydantic validation** for robust data handling
- **Click-based CLI** for intuitive command-line usage
- **Extensible parser framework** for adding new device types

### 🔍 **Supported Devices**
- **Cisco IOS** - Router and switch configurations
- **Cisco ASA** - Firewall and VPN configurations  
- **Fortinet FortiOS** - Next-generation firewall configurations
- **Palo Alto PAN-OS** - Security platform configurations

## Quick Start

```bash
# Install PyBastion
pip install pybastion

# Analyze a configuration file
pybastion analyze --config-file router-config.txt --device-type cisco-ios

# Generate security report
pybastion report --tenant my-company --format html
```

## Documentation Structure

### 📚 **Getting Started**
New to PyBastion? Start here for installation, configuration, and your first analysis.

### 👥 **User Guide**
Learn how to use PyBastion effectively for day-to-day security analysis tasks.

### 🏗 **Architecture**
Understand PyBastion's design, data models, and security architecture.

### 📖 **API Reference**
Complete API documentation auto-generated from the source code.

### 🔐 **Security**
In-depth security design, threat model, and compliance information.

### 💻 **Development**
Contributing guidelines, development setup, and extending PyBastion.

### 💡 **Examples**
Practical examples and use cases for common scenarios.

## Community & Support

- **GitHub Repository**: [flyguy62n/pybastion](https://github.com/flyguy62n/pybastion)
- **Issue Tracker**: Report bugs and request features
- **Discussions**: Ask questions and share use cases

## License

PyBastion is licensed under the MIT License. See the [LICENSE](https://github.com/flyguy62n/pybastion/blob/main/LICENSE) file for details.

---

!!! warning "Development Status"
    PyBastion is currently in **pre-alpha development**. While the core functionality is operational, the API may change before the first stable release. Use in production environments is not recommended at this time.
