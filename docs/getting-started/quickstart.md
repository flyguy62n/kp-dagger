# Quick Start

Get up and running with Dagger in minutes.

## Installation

First, install Dagger:

```bash
uv pip install Dagger
```

## Basic Usage

### 1. Analyze a Configuration File

```bash
# Analyze a Cisco IOS configuration
Dagger analyze cisco-ios router-config.txt

# Analyze a Cisco ASA configuration
Dagger analyze cisco-asa firewall-config.txt

# Analyze a Fortigate configuration
Dagger analyze fortigate fortigate-config.txt

# Analyze a PaloAlto configuration
Dagger analyze paloalto panos-config.xml
```

### 2. Generate a Report

```bash
# Generate HTML report
Dagger report --format html --output security-report.html

# Generate JSON report
Dagger report --format json --output security-report.json

# Generate PDF report (requires additional dependencies)
Dagger report --format pdf --output security-report.pdf
```

## Configuration

Create a configuration file for your organization:

```yaml
# ~/.Dagger/config.yaml
database:
  path: "./Dagger.sqlite"
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
Dagger tenant create "acme-corp" --description "ACME Corporation"

# 2. Analyze multiple devices
Dagger analyze cisco-ios devices/router-1.txt --tenant acme-corp
Dagger analyze cisco-asa devices/firewall-1.txt --tenant acme-corp
Dagger analyze fortigate devices/fortigate-1.txt --tenant acme-corp

# 3. Generate comprehensive report
Dagger report --tenant acme-corp --format html \
  --output acme-corp-security-report.html \
  --include-executive-summary \
  --include-recommendations

# 4. Export findings for remediation
Dagger export findings --tenant acme-corp --format csv \
  --output acme-corp-findings.csv
```

## Common Commands

| Command | Description |
|---------|-------------|
| `Dagger analyze <type> <file>` | Analyze configuration file |
| `Dagger report` | Generate security report |
| `Dagger tenant list` | List configured tenants |
| `Dagger status` | Show analysis status |
| `Dagger export` | Export findings data |

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

See the main documentation for configuration, reports, supported devices, and API reference.
