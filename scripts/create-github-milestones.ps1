# GitHub Milestones Creation Script for PyBastion
# Run this script from PowerShell after installing GitHub CLI

Write-Host "Creating GitHub milestones for PyBastion..." -ForegroundColor Green

# Define milestones with descriptions and due dates
$milestones = @(
    @{
        title="Milestone 1: Core Infrastructure"
        description="Establish solid foundation for all future development. Includes base parser architecture, database layer, and core scanner logic."
        due_date="2025-08-10"  # ~6 weeks from now
    },
    @{
        title="Milestone 2: Device Parsers"
        description="Implement parsers for all four supported device types: Cisco IOS, Cisco ASA, FortiGate, and PaloAlto."
        due_date="2025-10-19"  # ~16 weeks from now
    },
    @{
        title="Milestone 3: Security Analysis"
        description="Implement comprehensive security analysis capabilities including CIS benchmarks and vulnerability assessment."
        due_date="2025-12-14"  # ~24 weeks from now
    },
    @{
        title="Milestone 4: CLI and Reporting"
        description="Complete user interface and reporting capabilities with multi-format output and interactive features."
        due_date="2026-01-25"  # ~30 weeks from now
    },
    @{
        title="Milestone 5: Production Ready"
        description="Prepare for stable release with comprehensive documentation, performance optimization, and production testing."
        due_date="2026-02-22"  # ~34 weeks from now
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
    Write-Error "Please run this script from the root of your PyBastion repository"
    exit 1
}

# Create each milestone
foreach ($milestone in $milestones) {
    Write-Host "Creating milestone: $($milestone.title)" -ForegroundColor Cyan
    
    try {
        & gh api repos/:owner/:repo/milestones -f title="$($milestone.title)" -f description="$($milestone.description)" -f due_on="$($milestone.due_date)T23:59:59Z" --method POST
        Write-Host "Created: $($milestone.title)" -ForegroundColor Green
    } catch {
        if ($_.Exception.Message -like "*already exists*" -or $_.Exception.Message -like "*Validation Failed*") {
            Write-Host "Already exists or validation error: $($milestone.title)" -ForegroundColor Yellow
        } else {
            Write-Host "Failed to create: $($milestone.title) - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "Milestone creation complete!" -ForegroundColor Green
Write-Host "You can view all milestones at: https://github.com/flyguy62n/pybastion/milestones" -ForegroundColor Cyan
