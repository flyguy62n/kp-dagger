# Quick Start

Get up and running with PyBastion in minutes.

## Installation

First, install PyBastion:

```bash
uv pip install pybastion
```

## Basic Usage

### 1. Analyze a Configuration File

```bash
# Analyze a Cisco IOS configuration
pybastion analyze cisco-ios router-config.txt

# Analyze a Cisco ASA configuration
pybastion analyze cisco-asa firewall-config.txt

# Analyze a Fortigate configuration
pybastion analyze fortigate fortigate-config.txt

# Analyze a PaloAlto configuration
pybastion analyze paloalto panos-config.xml
```

### 2. Generate a Report

```bash
# Generate HTML report
pybastion report --format html --output security-report.html

# Generate JSON report
pybastion report --format json --output security-report.json

# Generate PDF report (requires additional dependencies)
pybastion report --format pdf --output security-report.pdf
```

### 3. Validate Configuration Syntax

```bash
# Validate configuration file syntax
pybastion validate cisco-ios router-config.txt
```

## Configuration

Create a configuration file for your organization:

```yaml
# ~/.pybastion/config.yaml
database:
  path: "./pybastion.db"
  encryption_enabled: true

tenants:
  default:
    name: "My Organization"
    description: "Default tenant for analysis"

analysis:
  cis_benchmarks:
    level: 1
    enabled_checks:
      - access_control
      - authentication
      - logging
      - encryption

reporting:
  default_format: "html"
  include_charts: true
  logo_path: "./assets/logo.png"
```

## Example Workflow

### Complete Security Analysis

```bash
# 1. Set up tenant
pybastion tenant create "acme-corp" --description "ACME Corporation"

# 2. Analyze multiple devices
pybastion analyze cisco-ios devices/router-1.txt --tenant acme-corp
pybastion analyze cisco-asa devices/firewall-1.txt --tenant acme-corp
pybastion analyze fortigate devices/fortigate-1.txt --tenant acme-corp

# 3. Generate comprehensive report
pybastion report --tenant acme-corp --format html \
  --output acme-corp-security-report.html \
  --include-executive-summary \
  --include-recommendations

# 4. Export findings for remediation
pybastion export findings --tenant acme-corp --format csv \
  --output acme-corp-findings.csv
```

## Common Commands

| Command | Description |
|---------|-------------|
| `pybastion analyze <type> <file>` | Analyze configuration file |
| `pybastion report` | Generate security report |
| `pybastion validate <type> <file>` | Validate configuration syntax |
| `pybastion tenant list` | List configured tenants |
| `pybastion status` | Show analysis status |
| `pybastion export` | Export findings data |

## Supported Device Types

- **cisco-ios**: Cisco IOS/IOS-XE routers and switches
- **cisco-asa**: Cisco ASA firewalls
- **fortigate**: Fortigate FortiOS firewalls
- **paloalto**: PaloAlto PAN-OS firewalls

## Example Output

After running an analysis, you'll see output like:

```
✅ Configuration parsed successfully
📊 Running security analysis...
   • Access Control Lists: 12 rules analyzed
   • Authentication Settings: 3 issues found
   • Logging Configuration: 1 warning
   • Encryption Settings: All checks passed

🔍 Analysis Summary:
   • Total Issues: 4
   • Critical: 1
   • High: 1
   • Medium: 2
   • Low: 0

📄 Report generated: security-report.html
```

## Next Steps

- [Configuration Guide](../user-guide/configuration.md)
- [Understanding Reports](../user-guide/reports.md)
- [Supported Devices](../user-guide/device-support.md)
- [API Reference](../api-reference/cli.md)
