# First Analysis

This guide walks you through performing your first security analysis with Dagger.

## Prerequisites

Before starting, ensure you have:

- [Installed Dagger](installation.md)
- A network device configuration file
- Basic familiarity with command line interfaces

## Sample Configuration Files

Dagger includes sample configuration files for testing. You can also use your own configuration files.

### Download Test Data

```bash
# Clone the repository for test data
git clone https://github.com/flyguy62n/Dagger.git
cd Dagger/testdata
```

## Step 1: Validate Configuration

First, validate that your configuration file is properly formatted:

```bash
# Validate a Cisco IOS configuration
Dagger validate cisco-ios testdata/router-config.txt

# Validate a Cisco ASA configuration  
Dagger validate cisco-asa firewall-config.txt

# Validate syntax and show parsing results
Dagger validate cisco-ios router-config.txt --verbose
```

### Expected Output

```
✅ Configuration validation successful
📄 File: router-config.txt
📊 Statistics:
   • Lines processed: 245
   • Configuration sections: 12
   • Interfaces found: 8
   • Access lists: 3
   • Routes: 15

⏱️  Parsing completed in 0.12 seconds
```

## Step 2: Perform Security Analysis

Run a comprehensive security analysis:

```bash
# Basic analysis
Dagger analyze cisco-ios testdata/router-config.txt

# Analysis with specific benchmark level
Dagger analyze cisco-ios router-config.txt --cis-level 1

# Analysis with custom output directory
Dagger analyze cisco-ios router-config.txt --output-dir ./analysis-results
```

### Analysis Process

The analysis performs several checks:

1. **Configuration Parsing** - Validates syntax and structure
2. **CIS Benchmark Compliance** - Checks against security standards
3. **Access Control Review** - Analyzes ACLs and firewall rules
4. **Vulnerability Assessment** - Checks for known vulnerabilities
5. **Best Practice Review** - Identifies configuration improvements

### Expected Output

```
🔍 Dagger Security Analysis
📄 Analyzing: router-config.txt (Cisco IOS)

✅ Configuration parsed successfully
📊 Running security analysis...

🔒 CIS Benchmark Compliance (Level 1):
   • 1.1.1 Set the hostname: ✅ PASS
   • 1.2.1 Set IP domain-name: ⚠️  WARNING  
   • 1.3.1 Set authentication passwords: ❌ FAIL
   • 2.1.1 Set console password: ✅ PASS
   • 2.2.1 Set auxiliary password: ❌ FAIL

🛡️  Access Control Analysis:
   • Standard ACL 'STANDARD_ACL': 2 issues found
   • Extended ACL 'EXTENDED_ACL': 1 critical issue
   • Interface ACL assignments: All properly configured

🐛 Vulnerability Assessment:
   • IOS Version 15.1(4)M: 3 known vulnerabilities
   • Critical CVEs: CVE-2023-12345
   • Recommended upgrade: 15.9(3)M or later

📊 Analysis Summary:
   • Total Findings: 12
   • Critical: 2
   • High: 3  
   • Medium: 5
   • Low: 2
   • Info: 0

📄 Detailed report saved: analysis-results/security-report.html
⏱️  Analysis completed in 3.45 seconds
```

## Step 3: Review Findings

### Critical Issues

Focus on critical and high-severity findings first:

```bash
# Show only critical findings
Dagger findings --severity critical

# Show findings for specific category
Dagger findings --category access_control

# Export findings to CSV for tracking
Dagger export findings --format csv --output findings.csv
```

### Example Critical Finding

```
🚨 CRITICAL: Weak Administrative Access Control

Finding ID: CIS-2.3.1
Category: Access Control
Severity: Critical

Description:
Administrative access is configured with default or weak authentication.
Console access lacks proper password protection.

Evidence:
- Line 23: "line con 0" - No password configured
- Line 156: "enable password cisco123" - Weak password detected

Recommendation:
1. Configure strong console passwords: line con 0 → password <strong-password>
2. Use encrypted enable secret: enable secret <strong-password>  
3. Implement login local authentication
4. Consider implementing AAA authentication

References:
- CIS Cisco IOS Benchmark v4.1.0 - Section 2.3.1
- NIST SP 800-53 - IA-5 Authenticator Management
```

## Step 4: Generate Reports

Create formatted reports for different audiences:

### HTML Report (Recommended)

```bash
# Generate comprehensive HTML report
Dagger report --format html --output security-report.html

# Include executive summary  
Dagger report --format html --output report.html --include-executive-summary

# Custom template and branding
Dagger report --format html --template custom.j2 --logo company-logo.png
```

### Other Report Formats

```bash
# JSON for automated processing
Dagger report --format json --output security-data.json

# CSV for spreadsheet analysis
Dagger report --format csv --output findings.csv

# PDF for management (requires additional dependencies)
Dagger report --format pdf --output executive-report.pdf
```

## Step 5: Address Findings

### Prioritization

1. **Critical** - Immediate action required (security vulnerabilities)
2. **High** - Address within 1 week (compliance violations)
3. **Medium** - Address within 1 month (best practice improvements)
4. **Low** - Address during next maintenance window

### Remediation Workflow

1. **Review** each finding and its recommendation
2. **Plan** changes during maintenance windows
3. **Test** configuration changes in lab environment
4. **Implement** changes on production devices
5. **Re-analyze** to verify fixes

### Track Progress

```bash
# Mark findings as resolved
Dagger findings update <finding-id> --status resolved

# Add comments to findings
Dagger findings comment <finding-id> "Fixed in maintenance window MW-2024-001"

# Generate progress report
Dagger report --show-resolved --format html --output progress-report.html
```

## Understanding Report Structure

### Executive Summary

- **Risk overview** and key metrics
- **Top findings** requiring immediate attention  
- **Compliance status** against industry standards
- **Recommendations** for improvement

### Technical Details

- **Device inventory** and configuration summary
- **Detailed findings** with evidence and remediation
- **Vulnerability information** with CVE details
- **Configuration snippets** showing issues

### Appendices

- **CIS benchmark** reference information
- **Vulnerability details** from CVE databases
- **Configuration standards** and best practices

## Next Steps

- [Configuration Management](../user-guide/configuration.md)
- [Understanding Reports](../user-guide/reports.md)
- [Multi-Device Analysis](../user-guide/multi-device.md)
- [Automated Workflows](../examples/automation.md)

## Troubleshooting

### Common Issues

**File not found or permission denied**
```bash
# Check file exists and is readable
ls -la router-config.txt
```

**Unknown device type**
```bash
# Specify device type explicitly
Dagger analyze cisco-ios router-config.txt
```

**Parsing errors**
```bash
# Use verbose mode for detailed error information
Dagger validate cisco-ios router-config.txt --verbose
```

**No findings generated**
```bash
# Check if analysis rules are enabled
Dagger config show analysis
```

For more troubleshooting help, see the [Troubleshooting Guide](../user-guide/troubleshooting.md).
