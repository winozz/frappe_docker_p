# CvSU AMS Quick Setup Script
# For existing frappe_docker installations
# Run this from the frappe_docker root directory

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  CvSU AMS Quick Setup                                    ║" -ForegroundColor Cyan
Write-Host "║  Applying CvSU AMS configuration to frappe_docker        ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if we're in frappe_docker directory
if (-not (Test-Path "devcontainer-example")) {
    Write-Host "❌ Error: This doesn't look like the frappe_docker directory" -ForegroundColor Red
    Write-Host "   Please run this script from the frappe_docker root" -ForegroundColor Yellow
    Write-Host "   Current directory: $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ frappe_docker directory detected" -ForegroundColor Green
Write-Host ""

# Step 1: Setup devcontainer if not exists
if (-not (Test-Path ".devcontainer")) {
    Write-Host "📁 Creating .devcontainer directory..." -ForegroundColor Yellow
    Copy-Item -Recurse -Force "devcontainer-example" ".devcontainer"
    Write-Host "✅ .devcontainer created from devcontainer-example" -ForegroundColor Green
} else {
    Write-Host "ℹ️  .devcontainer directory already exists" -ForegroundColor Cyan
}

# Step 2: Copy CvSU AMS docker-compose configuration
Write-Host ""
Write-Host "📋 Applying CvSU AMS docker-compose configuration..." -ForegroundColor Yellow

$cvsuComposeSource = ".devcontainer\docker-compose.cvsu-ais.yml"
$cvsuComposeTarget = ".devcontainer\docker-compose.yml"

if (Test-Path $cvsuComposeSource) {
    # Backup existing docker-compose.yml if it exists
    if (Test-Path $cvsuComposeTarget) {
        $backupName = ".devcontainer\docker-compose.yml.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Write-Host "⚠️  Backing up existing docker-compose.yml to:" -ForegroundColor Yellow
        Write-Host "   $backupName" -ForegroundColor Yellow
        Copy-Item $cvsuComposeTarget $backupName
    }
    
    Copy-Item -Force $cvsuComposeSource $cvsuComposeTarget
    Write-Host "✅ CvSU AMS docker-compose.yml activated" -ForegroundColor Green
} else {
    Write-Host "❌ Error: docker-compose.cvsu-ais.yml not found" -ForegroundColor Red
    Write-Host "   Expected location: $cvsuComposeSource" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Please ensure all CvSU AMS files are in .devcontainer/" -ForegroundColor Yellow
    exit 1
}

# Step 3: Setup VS Code settings
Write-Host ""
Write-Host "📁 Setting up VS Code configuration..." -ForegroundColor Yellow

if (-not (Test-Path "development\.vscode")) {
    if (Test-Path "development\vscode-example") {
        Copy-Item -Recurse -Force "development\vscode-example" "development\.vscode"
        Write-Host "✅ VS Code settings copied" -ForegroundColor Green
    } else {
        Write-Host "⚠️  development/vscode-example not found, skipping" -ForegroundColor Yellow
    }
} else {
    Write-Host "ℹ️  VS Code settings already exist" -ForegroundColor Cyan
}

# Step 4: Check for documentation files
Write-Host ""
Write-Host "📚 Checking documentation files..." -ForegroundColor Yellow

$docsExist = $true
$docFiles = @(
    ".devcontainer\SETUP_GUIDE.md",
    ".devcontainer\QUICK_REFERENCE.md",
    ".devcontainer\PACKAGE_OVERVIEW.md"
)

foreach ($docFile in $docFiles) {
    if (Test-Path $docFile) {
        Write-Host "  ✅ $(Split-Path $docFile -Leaf)" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  $(Split-Path $docFile -Leaf) - Not found" -ForegroundColor Yellow
        $docsExist = $false
    }
}

if (-not $docsExist) {
    Write-Host ""
    Write-Host "ℹ️  Some documentation files are missing" -ForegroundColor Cyan
    Write-Host "   You can find them in the CvSU AMS package" -ForegroundColor Cyan
}

# Summary
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅ CvSU AMS Configuration Applied!                      ║" -ForegroundColor Green
Write-Host "╠══════════════════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║  Configuration Summary:                                  ║" -ForegroundColor Green
Write-Host "║  • Docker Compose: Activated (CvSU AMS version)          ║" -ForegroundColor Green
Write-Host "║  • Site: accounting.localhost                            ║" -ForegroundColor Green
Write-Host "║  • Python: 3.11.9                                        ║" -ForegroundColor Green
Write-Host "║  • Database: MariaDB 11.8 (port 3307)                    ║" -ForegroundColor Green
Write-Host "║  • SonarQube: Port 9999                                  ║" -ForegroundColor Green
Write-Host "╠══════════════════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║  Next Steps:                                             ║" -ForegroundColor Green
Write-Host "║                                                          ║" -ForegroundColor Green
Write-Host "║  1. Open this folder in VS Code:                         ║" -ForegroundColor Green
Write-Host "║     code .                                               ║" -ForegroundColor Green
Write-Host "║                                                          ║" -ForegroundColor Green
Write-Host "║  2. Reopen in Dev Container:                             ║" -ForegroundColor Green
Write-Host "║     Press: Ctrl+Shift+P                                  ║" -ForegroundColor Green
Write-Host "║     Type: Dev Containers: Reopen in Container            ║" -ForegroundColor Green
Write-Host "║     (First build takes ~5-10 minutes)                    ║" -ForegroundColor Green
Write-Host "║                                                          ║" -ForegroundColor Green
Write-Host "║  3. Inside container, run setup:                         ║" -ForegroundColor Green
Write-Host "║     bash /workspace/development/setup-container.sh       ║" -ForegroundColor Green
Write-Host "║                                                          ║" -ForegroundColor Green
Write-Host "║  4. Start development server:                            ║" -ForegroundColor Green
Write-Host "║     cd frappe-bench                                      ║" -ForegroundColor Green
Write-Host "║     bench start                                          ║" -ForegroundColor Green
Write-Host "║                                                          ║" -ForegroundColor Green
Write-Host "║  5. Access your application:                             ║" -ForegroundColor Green
Write-Host "║     URL: http://localhost:8000                           ║" -ForegroundColor Green
Write-Host "║     Username: Administrator                              ║" -ForegroundColor Green
Write-Host "║     Password: admin                                      ║" -ForegroundColor Green
Write-Host "╠══════════════════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║  📚 Documentation:                                       ║" -ForegroundColor Green
Write-Host "║     .devcontainer/SETUP_GUIDE.md                         ║" -ForegroundColor Green
Write-Host "║     .devcontainer/QUICK_REFERENCE.md                     ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

# Optional: Open VS Code
$openVSCode = Read-Host "Open in VS Code now? (y/N)"
if ($openVSCode -eq 'y' -or $openVSCode -eq 'Y') {
    Write-Host ""
    Write-Host "🚀 Opening VS Code..." -ForegroundColor Yellow
    code .
    Write-Host "✅ VS Code opened" -ForegroundColor Green
    Write-Host "   Remember to 'Reopen in Container' (Ctrl+Shift+P)" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Happy Coding! 🚀" -ForegroundColor Cyan
Write-Host ""
