# Master GitHub Setup Script for Dagger
# This script creates labels, milestones, and issues in the correct order

Write-Host "========================================" -ForegroundColor Blue
Write-Host "Dagger GitHub Project Setup" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""

# Check if gh CLI is available
try {
    $null = Get-Command gh -ErrorAction Stop
    Write-Host "✓ GitHub CLI is available" -ForegroundColor Green
} catch {
    Write-Error "GitHub CLI (gh) is not installed. Please install it first:"
    Write-Host "winget install GitHub.cli" -ForegroundColor Yellow
    Write-Host "Then run: gh auth login" -ForegroundColor Yellow
    exit 1
}

# Check if we're in a git repository
if (-not (Test-Path ".git")) {
    Write-Error "Please run this script from the root of your kp_dagger repository"
    exit 1
}

# Check authentication
try {
    & gh auth status | Out-Null
    Write-Host "✓ GitHub authentication is valid" -ForegroundColor Green
} catch {
    Write-Error "GitHub authentication failed. Please run: gh auth login"
    exit 1
}

Write-Host ""

# Step 1: Create Labels
Write-Host "Step 1: Creating GitHub Labels..." -ForegroundColor Yellow
try {
    & .\scripts\create-github-labels.ps1
    Write-Host "✓ Labels created successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠ Label creation had issues, but continuing..." -ForegroundColor Yellow
}

Write-Host ""

# Step 2: Create Milestones
Write-Host "Step 2: Creating GitHub Milestones..." -ForegroundColor Yellow
try {
    & .\scripts\create-github-milestones.ps1
    Write-Host "✓ Milestones created successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠ Milestone creation had issues, but continuing..." -ForegroundColor Yellow
}

Write-Host ""

# Step 3: Wait a moment for GitHub to process
Write-Host "Step 3: Waiting for GitHub to process milestones..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
Write-Host "✓ Ready to create issues" -ForegroundColor Green

Write-Host ""

# Step 4: Create Issues
Write-Host "Step 4: Creating GitHub Issues..." -ForegroundColor Yellow
try {
    & .\scripts\create-github-issues.ps1
    Write-Host "✓ Issues created successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠ Issue creation had some problems" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Blue
Write-Host "GitHub Project Setup Complete!" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Green
Write-Host "1. Visit your repository: https://github.com/flyguy62n/Dagger" -ForegroundColor Cyan
Write-Host "2. Review the created labels: https://github.com/flyguy62n/Dagger/labels" -ForegroundColor Cyan
Write-Host "3. Check the milestones: https://github.com/flyguy62n/Dagger/milestones" -ForegroundColor Cyan
Write-Host "4. Review the issues: https://github.com/flyguy62n/Dagger/issues" -ForegroundColor Cyan
Write-Host "5. Create a project board to track progress" -ForegroundColor Cyan
Write-Host ""
Write-Host "Recommended next actions:" -ForegroundColor Green
Write-Host "• Set up a GitHub Project board for kanban-style tracking" -ForegroundColor White
Write-Host "• Review and adjust issue priorities as needed" -ForegroundColor White
Write-Host "• Assign issues to team members" -ForegroundColor White
Write-Host "• Create branch protection rules" -ForegroundColor White
Write-Host "• Set up GitHub Actions for CI/CD" -ForegroundColor White
