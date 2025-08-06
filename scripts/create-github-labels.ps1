# GitHub Labels Creation Script for Dagger
# Run this script from PowerShell after installing GitHub CLI

Write-Host "Creating GitHub labels for Dagger..." -ForegroundColor Green

# Define labels with descriptions and colors
$labels = @(
    @{name="enhancement"; description="New feature or request"; color="a2eeef"},
    @{name="core"; description="Core infrastructure and architecture"; color="1d76db"},
    @{name="parser"; description="Configuration file parsing"; color="fbca04"},
    @{name="security"; description="Security analysis and checks"; color="d93f0b"},
    @{name="cli"; description="Command line interface"; color="0e8a16"},
    @{name="reporting"; description="Report generation"; color="5319e7"},
    @{name="cisco"; description="Cisco device support"; color="006b75"},
    @{name="fortinet"; description="FortiGate device support"; color="d4c5f9"},
    @{name="paloalto"; description="PaloAlto device support"; color="c2e0c6"},
    @{name="device-support"; description="New device type requests"; color="bfd4f2"},
    @{name="milestone-1"; description="Core Infrastructure milestone"; color="0052cc"},
    @{name="milestone-2"; description="Device Parsers milestone"; color="0052cc"},
    @{name="milestone-3"; description="Security Analysis milestone"; color="0052cc"},
    @{name="milestone-4"; description="CLI and Reporting milestone"; color="0052cc"},
    @{name="milestone-5"; description="Production Ready milestone"; color="0052cc"},
    @{name="priority-high"; description="High priority issue"; color="b60205"},
    @{name="priority-medium"; description="Medium priority issue"; color="fbca04"},
    @{name="priority-low"; description="Low priority issue"; color="0e8a16"},
    @{name="cis"; description="CIS benchmark related"; color="e99695"},
    @{name="api"; description="External API integrations"; color="f9d0c4"},
    @{name="web"; description="Web interface (future)"; color="c5def5"},
    @{name="feature"; description="New feature request"; color="c2e0c6"},
    @{name="quick-start"; description="Quick implementation for demo"; color="7057ff"},
    @{name="ux"; description="User experience improvements"; color="d876e3"}
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
    Write-Error "Please run this script from the root of your Dagger repository"
    exit 1
}

# Create each label
foreach ($label in $labels) {
    Write-Host "Creating label: $($label.name)" -ForegroundColor Cyan
    
    try {
        & gh label create $label.name --description $label.description --color $label.color
        Write-Host "Created: $($label.name)" -ForegroundColor Green
    } catch {
        if ($_.Exception.Message -like "*already exists*") {
            Write-Host "Already exists: $($label.name)" -ForegroundColor Yellow
        } else {
            Write-Host "Failed to create: $($label.name) - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "Label creation complete!" -ForegroundColor Green
Write-Host "You can view all labels at: https://github.com/flyguy62n/Dagger/labels" -ForegroundColor Cyan
