# GitHub Issues Creation Script for Dagger
# Run this script from PowerShell after installing GitHub CLI

Write-Host "Creating GitHub issues for Dagger..." -ForegroundColor Green

# Define issues with all their metadata
$issues = @(
    # Milestone 1: Core Infrastructure
    @{
        title="Implement Base Parser Architecture"
        body=@"
Implement the base parser architecture that all device-specific parsers will inherit from.

## Acceptance Criteria
- [ ] Complete ``src/Dagger/parsers/base/parser.py`` with abstract base class
- [ ] Define common parsing interfaces and methods
- [ ] Implement error handling and validation
- [ ] Add logging support
- [ ] Create unit tests for base parser
- [ ] Document parser development guidelines

## Related Files
- ``src/Dagger/parsers/base/parser.py``
- ``tests/unit/parsers/test_base_parser.py``

## Technical Requirements
- Use Python 3.12+ type hints
- Follow SQLModel patterns for data models
- Implement comprehensive error handling
- Support extensible architecture for new device types

## Definition of Done
- All acceptance criteria met
- Code reviewed and approved
- Unit tests passing with >90% coverage
- Documentation updated
"@
        labels=@("enhancement", "core", "milestone-1", "priority-high")
        milestone="Milestone 1: Core Infrastructure"
        assignees=@()
    },
    @{
        title="Implement Database Layer with DuckDB"
        body=@"
Complete the database layer implementation using DuckDB for storing parsed configuration data and analysis results.

## Acceptance Criteria
- [ ] Complete ``src/Dagger/core/database.py`` implementation
- [ ] Define database schema for all supported device types
- [ ] Implement connection management and transactions
- [ ] Add database migration support
- [ ] Create database initialization scripts
- [ ] Add comprehensive error handling
- [ ] Write unit tests for database operations
- [ ] Performance optimization for large configurations

## Related Files
- ``src/Dagger/core/database.py``
- ``src/Dagger/models/`` (all model files)
- ``tests/unit/core/test_database.py``

## Technical Requirements
- Use SQLModel for ORM and validation
- Support concurrent access
- Implement proper transaction management
- Handle large configuration files efficiently

## Definition of Done
- Database can store/retrieve configuration data
- All CRUD operations implemented
- Performance benchmarks meet requirements
- Comprehensive test coverage
"@
        labels=@("enhancement", "core", "database", "milestone-1", "priority-high")
        milestone="Milestone 1: Core Infrastructure"
        assignees=@()
    },
    @{
        title="Implement Core Scanner Logic"
        body=@"
Complete the core scanner that orchestrates parsing, analysis, and reporting.

## Acceptance Criteria
- [ ] Complete ``src/Dagger/core/scanner.py`` implementation
- [ ] Implement file discovery and batching
- [ ] Add progress tracking and reporting
- [ ] Implement parallel processing for large sets
- [ ] Add configuration validation
- [ ] Error recovery and partial results handling
- [ ] Memory management for large files
- [ ] Unit tests and integration tests

## Related Files
- ``src/Dagger/core/scanner.py``
- ``tests/unit/core/test_scanner.py``

## Technical Requirements
- Support multiple file formats and device types
- Implement efficient memory usage
- Provide real-time progress feedback
- Handle errors gracefully

## Definition of Done
- Scanner can process configuration files end-to-end
- Progress tracking works correctly
- Error handling is robust
- Performance is acceptable for enterprise use
"@
        labels=@("enhancement", "core", "milestone-1", "priority-high")
        milestone="Milestone 1: Core Infrastructure"
        assignees=@()
    },
    # Milestone 2: Device Parsers
    @{
        title="Implement Cisco IOS Parser"
        body=@"
Implement comprehensive Cisco IOS configuration parser.

## Acceptance Criteria
- [ ] Parse interface configurations
- [ ] Parse access control lists
- [ ] Parse routing protocols (OSPF, EIGRP, BGP)
- [ ] Parse VLAN configurations
- [ ] Parse user authentication settings
- [ ] Parse SNMP configurations
- [ ] Parse logging configurations
- [ ] Handle IOS version differences
- [ ] Comprehensive test suite with real config samples
- [ ] Documentation and examples

## Related Files
- ``src/Dagger/parsers/cisco_ios/parser.py``
- ``src/Dagger/parsers/cisco_ios/commands/``
- ``src/Dagger/models/cisco_ios/``
- ``tests/unit/parsers/test_cisco_ios_parser.py``
- ``tests/fixtures/configs/cisco_ios/``

## Technical Requirements
- Support multiple IOS versions
- Handle configuration variations
- Normalize data to common format
- Comprehensive error handling

## Definition of Done
- Parser handles real-world IOS configurations
- All major configuration sections supported
- Test coverage >90%
- Documentation complete
"@
        labels=@("enhancement", "parser", "cisco", "milestone-2", "priority-high")
        milestone="Milestone 2: Device Parsers"
        assignees=@()
    },
    @{
        title="Implement Cisco ASA Parser"
        body=@"
Implement comprehensive Cisco ASA firewall configuration parser.

## Acceptance Criteria
- [ ] Parse object groups and network objects
- [ ] Parse access control lists and rules
- [ ] Parse NAT configurations
- [ ] Parse VPN configurations
- [ ] Parse interface security levels
- [ ] Parse user authentication settings
- [ ] Parse logging configurations
- [ ] Handle ASA version differences
- [ ] Comprehensive test suite
- [ ] Documentation and examples

## Related Files
- ``src/Dagger/parsers/cisco_asa/parser.py``
- ``src/Dagger/parsers/cisco_asa/commands/``
- ``src/Dagger/models/cisco_asa/``
- ``tests/unit/parsers/test_cisco_asa_parser.py``

## Technical Requirements
- Support ASA-specific configuration format
- Handle firewall-specific features
- Integrate with security analysis
- Comprehensive error handling

## Definition of Done
- Parser handles ASA configurations correctly
- Security features properly extracted
- Integration with analysis engine
- Documentation complete
"@
        labels=@("enhancement", "parser", "cisco", "milestone-2", "priority-high")
        milestone="Milestone 2: Device Parsers"
        assignees=@()
    },
    @{
        title="Implement FortiGate Parser"
        body=@"
Implement comprehensive FortiGate FortiOS configuration parser.

## Acceptance Criteria
- [ ] Parse firewall policies and rules
- [ ] Parse address and service objects
- [ ] Parse interface configurations
- [ ] Parse VPN configurations
- [ ] Parse user authentication settings
- [ ] Parse logging configurations
- [ ] Parse security profiles
- [ ] Handle FortiOS version differences
- [ ] Comprehensive test suite
- [ ] Documentation and examples

## Related Files
- ``src/Dagger/parsers/fortigate/parser.py``
- ``src/Dagger/parsers/fortigate/commands/``
- ``src/Dagger/models/fortigate/``
- ``tests/unit/parsers/test_fortigate_parser.py``

## Technical Requirements
- Support FortiOS configuration format
- Handle Fortinet-specific features
- Integrate with security analysis
- Comprehensive error handling

## Definition of Done
- Parser handles FortiGate configurations
- All major features supported
- Test coverage >90%
- Documentation complete
"@
        labels=@("enhancement", "parser", "fortinet", "milestone-2", "priority-high")
        milestone="Milestone 2: Device Parsers"
        assignees=@()
    },
    @{
        title="Implement PaloAlto Parser"
        body=@"
Implement comprehensive PaloAlto PAN-OS configuration parser.

## Acceptance Criteria
- [ ] Parse security policies and rules
- [ ] Parse address and service objects
- [ ] Parse interface configurations
- [ ] Parse VPN configurations
- [ ] Parse user authentication settings
- [ ] Parse logging configurations
- [ ] Parse security profiles
- [ ] Handle PAN-OS version differences
- [ ] Comprehensive test suite
- [ ] Documentation and examples

## Related Files
- ``src/Dagger/parsers/paloalto/parser.py``
- ``src/Dagger/parsers/paloalto/commands/``
- ``src/Dagger/models/paloalto/``
- ``tests/unit/parsers/test_paloalto_parser.py``

## Technical Requirements
- Support PAN-OS configuration format
- Handle PaloAlto-specific features
- Integrate with security analysis
- Comprehensive error handling

## Definition of Done
- Parser handles PAN-OS configurations
- All major features supported
- Test coverage >90%
- Documentation complete
"@
        labels=@("enhancement", "parser", "paloalto", "milestone-2", "priority-high")
        milestone="Milestone 2: Device Parsers"
        assignees=@()
    },
    # Milestone 3: Security Analysis
    @{
        title="Implement CIS Benchmark Checks for Cisco IOS"
        body=@"
Implement CIS Level 1 benchmark checks for Cisco IOS devices.

## Acceptance Criteria
- [ ] Research and document CIS Cisco IOS Level 1 benchmarks
- [ ] Implement all applicable Level 1 checks
- [ ] Create SQL queries for compliance checking
- [ ] Add severity levels and remediation guidance
- [ ] Unit tests for all checks
- [ ] Integration with analysis engine
- [ ] Documentation of check implementations

## Related Files
- ``src/Dagger/analyzers/rules/cis_benchmarks/cisco.py``
- ``src/Dagger/analyzers/queries/security.py``
- ``tests/unit/analyzers/test_cis_cisco.py``

## Technical Requirements
- Follow CIS Level 1 benchmarks exactly
- Provide actionable remediation guidance
- Support multiple IOS versions
- Integrate with reporting system

## Definition of Done
- All applicable CIS Level 1 checks implemented
- Accurate compliance scoring
- Clear remediation guidance
- Documentation complete
"@
        labels=@("enhancement", "security", "cis", "cisco", "milestone-3", "priority-high")
        milestone="Milestone 3: Security Analysis"
        assignees=@()
    },
    @{
        title="Implement Security Risk Analysis"
        body=@"
Implement comprehensive security risk analysis for network configurations.

## Acceptance Criteria
- [ ] ACL/firewall rule risk assessment
- [ ] Weak authentication detection
- [ ] Insecure protocol identification
- [ ] Default credential detection
- [ ] Unnecessary service identification
- [ ] Risk scoring algorithm
- [ ] SQL-based analysis queries
- [ ] Unit tests and validation

## Related Files
- ``src/Dagger/analyzers/sql/analyzer.py``
- ``src/Dagger/analyzers/queries/security.py``
- ``tests/unit/analyzers/test_security_analysis.py``

## Technical Requirements
- Accurate risk assessment
- Prioritized findings
- Cross-platform analysis
- Performance optimization

## Definition of Done
- Risk analysis provides actionable insights
- Scoring algorithm is accurate
- Performance meets requirements
- Documentation complete
"@
        labels=@("enhancement", "security", "analysis", "milestone-3", "priority-high")
        milestone="Milestone 3: Security Analysis"
        assignees=@()
    },
    @{
        title="Implement Vulnerability Assessment Integration"
        body=@"
Integrate with CVE Details and End of Life APIs for vulnerability assessment.

## Acceptance Criteria
- [ ] Complete CVE Details API client
- [ ] Complete End of Life API client
- [ ] Firmware version extraction from configs
- [ ] Vulnerability matching and scoring
- [ ] Rate limiting and caching
- [ ] Error handling for API failures
- [ ] Unit tests with mocked responses
- [ ] Integration tests

## Related Files
- ``src/Dagger/api_clients/cve_details.py``
- ``src/Dagger/api_clients/endoflife.py``
- ``tests/unit/api_clients/``

## Technical Requirements
- Respect API rate limits
- Implement proper caching
- Handle API failures gracefully
- Accurate vulnerability matching

## Definition of Done
- API integrations working correctly
- Vulnerability data is accurate
- Rate limiting implemented
- Error handling is robust
"@
        labels=@("enhancement", "security", "api", "milestone-3", "priority-medium")
        milestone="Milestone 3: Security Analysis"
        assignees=@()
    },
    # Milestone 4: CLI and Reporting
    @{
        title="Implement Complete CLI Interface"
        body=@"
Implement comprehensive command-line interface using Click.

## Acceptance Criteria
- [ ] Main CLI entry point
- [ ] Scan command with all options
- [ ] Report generation commands
- [ ] Configuration validation commands
- [ ] Database management commands
- [ ] Progress bars and status reporting
- [ ] Configuration file support
- [ ] Rich output formatting
- [ ] Comprehensive help text
- [ ] Shell completion support

## Related Files
- ``src/Dagger/cli/``
- ``tests/unit/cli/``

## Technical Requirements
- Intuitive command structure
- Rich progress feedback
- Comprehensive help system
- Shell integration

## Definition of Done
- All planned commands implemented
- User experience is polished
- Help system is comprehensive
- Shell completion works
"@
        labels=@("enhancement", "cli", "milestone-4", "priority-high")
        milestone="Milestone 4: CLI and Reporting"
        assignees=@()
    },
    @{
        title="Implement Report Generation System"
        body=@"
Implement comprehensive report generation in multiple formats.

## Acceptance Criteria
- [ ] JSON report format
- [ ] HTML report with charts and graphs
- [ ] Excel report with multiple sheets
- [ ] PDF report generation (optional)
- [ ] Report templates and customization
- [ ] Executive summary generation
- [ ] Detailed findings with remediation
- [ ] Report scheduling and automation
- [ ] Unit tests for all formats

## Related Files
- ``src/Dagger/reports/generator.py``
- ``src/Dagger/reports/templates/``
- ``tests/unit/reports/``

## Technical Requirements
- Professional report layouts
- Actionable insights
- Multiple output formats
- Template customization

## Definition of Done
- All report formats working
- Reports provide value to users
- Templates are customizable
- Performance is acceptable
"@
        labels=@("enhancement", "reporting", "milestone-4", "priority-high")
        milestone="Milestone 4: CLI and Reporting"
        assignees=@()
    },
    # Milestone 5: Production Ready
    @{
        title="Create Comprehensive Documentation"
        body=@"
Create comprehensive documentation for users and developers.

## Acceptance Criteria
- [ ] User guide with examples
- [ ] Developer documentation
- [ ] API reference documentation
- [ ] Configuration format guides
- [ ] Troubleshooting guide
- [ ] Contributing guidelines
- [ ] Security analysis methodology
- [ ] Example configurations and reports

## Related Files
- ``docs/``
- ``README.md``
- ``CONTRIBUTING.md``

## Technical Requirements
- Clear, actionable documentation
- Comprehensive examples
- Professional presentation
- Easy navigation

## Definition of Done
- Documentation is complete and accurate
- Examples work as described
- User feedback is positive
- Developer onboarding is smooth
"@
        labels=@("documentation", "milestone-5", "priority-medium")
        milestone="Milestone 5: Production Ready"
        assignees=@()
    },
    @{
        title="Production Release Preparation"
        body=@"
Prepare for production release on PyPI.

## Acceptance Criteria
- [ ] Comprehensive test suite with >90% coverage
- [ ] Performance benchmarking and optimization
- [ ] Security review of code
- [ ] Documentation review and updates
- [ ] Version 1.0.0 release candidate
- [ ] PyPI packaging and metadata
- [ ] Release notes and changelog
- [ ] Migration guide from development version

## Related Files
- ``pyproject.toml``
- ``CHANGELOG.md``
- ``src/Dagger/__init__.py``

## Technical Requirements
- Production-ready code quality
- Comprehensive testing
- Security best practices
- Professional packaging

## Definition of Done
- Version 1.0.0 is ready for release
- All quality gates passed
- Documentation is complete
- Migration path is clear
"@
        labels=@("release", "milestone-5", "priority-high")
        milestone="Milestone 5: Production Ready"
        assignees=@()
    },
    # Quick Start Issues
    @{
        title="Create Basic CLI Stub"
        body=@"
Create basic CLI that shows 'coming soon' messages for all commands.

## Acceptance Criteria
- [ ] CLI entry point works
- [ ] Help text displays properly
- [ ] All planned commands show development status
- [ ] Version information displays correctly

## Technical Requirements
- Use Click framework
- Professional help text
- Clear development status messages
- Easy to extend

## Definition of Done
- CLI is installable and runnable
- All commands show appropriate messages
- Help system works correctly
- Users understand development status
"@
        labels=@("quick-start", "cli", "priority-high")
        milestone="Milestone 1: Core Infrastructure"
        assignees=@()
    },
    @{
        title="Add Development Status Indicators"
        body=@"
Add clear indicators throughout the codebase showing development status.

## Acceptance Criteria
- [ ] Warning messages in appropriate places
- [ ] Status indicators in CLI help
- [ ] Progress tracking in README
- [ ] Development roadmap visibility

## Technical Requirements
- Clear, professional messaging
- Consistent status indicators
- Easy to update as development progresses
- User-friendly communication

## Definition of Done
- Users clearly understand development status
- Status indicators are consistent
- Progress is visible and trackable
- Communication is professional
"@
        labels=@("quick-start", "ux", "priority-medium")
        milestone="Milestone 1: Core Infrastructure"
        assignees=@()
    }
)

# Check if gh CLI is available
try {
    $null = Get-Command gh -ErrorAction Stop
} catch {
    Write-Error "GitHub CLI (gh) is not installed. Please install it first:"
    Write-Host "winget install GitHub.cli" -ForegroundColor Yellow
    exit 1
}

# Check if we're in a git repository
if (-not (Test-Path ".git")) {
    Write-Error "Please run this script from the root of your kp_dagger repository"
    exit 1
}

# Check if milestones exist
Write-Host "Checking existing milestones..." -ForegroundColor Yellow
try {
    $existingMilestones = & gh api repos/:owner/:repo/milestones | ConvertFrom-Json
    if ($existingMilestones.Count -eq 0) {
        Write-Warning "No milestones found. Issues will be created without milestone assignments."
        Write-Host "Run create-github-milestones.ps1 first to create milestones." -ForegroundColor Yellow
    } else {
        Write-Host "Found $($existingMilestones.Count) existing milestones:" -ForegroundColor Green
        $existingMilestones | ForEach-Object { 
            Write-Host "  - $($_.title) (ID: $($_.number))" -ForegroundColor Cyan 
        }
    }
} catch {
    Write-Warning "Could not check milestones: $($_.Exception.Message)"
}
Write-Host ""

# Function to get milestone number by title
function Get-MilestoneNumber {
    param($milestoneTitle)
    
    try {
        $milestones = & gh api repos/:owner/:repo/milestones | ConvertFrom-Json
        $milestone = $milestones | Where-Object { $_.title -eq $milestoneTitle }
        if ($milestone) {
            Write-Host "Found milestone: $milestoneTitle (ID: $($milestone.number))" -ForegroundColor DarkGreen
            return $milestone.number
        } else {
            Write-Warning "Could not find milestone: $milestoneTitle"
            Write-Host "Available milestones:" -ForegroundColor Yellow
            $milestones | ForEach-Object { Write-Host "  - $($_.title) (ID: $($_.number))" -ForegroundColor Yellow }
            return $null
        }
    } catch {
        Write-Warning "Error fetching milestones: $($_.Exception.Message)"
        return $null
    }
}

# Create each issue
$issueCount = 0
foreach ($issue in $issues) {
    $issueCount++
    Write-Host "Creating issue $issueCount/$($issues.Count): $($issue.title)" -ForegroundColor Cyan
    
    try {
        # Create the issue first without milestone
        $createArgs = @("issue", "create", "--title", $issue.title, "--body", $issue.body)
        
        # Add labels individually
        if ($issue.labels.Count -gt 0) {
            foreach ($label in $issue.labels) {
                $createArgs += "--label"
                $createArgs += $label
            }
        }
        
        # Add assignees individually
        if ($issue.assignees.Count -gt 0) {
            foreach ($assignee in $issue.assignees) {
                $createArgs += "--assignee"
                $createArgs += $assignee
            }
        }
        
        $issueUrl = & gh @createArgs
        
        # Then try to add milestone if available
        if ($issue.milestone) {
            try {
                & gh issue edit $issueUrl --milestone "$($issue.milestone)"
                Write-Host "Created with milestone: $($issue.title)" -ForegroundColor Green
            } catch {
                Write-Host "Created (milestone assignment failed): $($issue.title)" -ForegroundColor Yellow
                Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
            }
        } else {
            Write-Host "Created: $($issue.title)" -ForegroundColor Green
        }
        Start-Sleep -Milliseconds 500  # Rate limiting
    } catch {
        Write-Host "Failed to create: $($issue.title) - $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Issue creation complete! Created $issueCount issues." -ForegroundColor Green
Write-Host "You can view all issues at: https://github.com/flyguy62n/Dagger/issues" -ForegroundColor Cyan
