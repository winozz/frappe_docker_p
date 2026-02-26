# CvSU AMS Development Environment Setup Script
# Windows PowerShell Automation
# Last Updated: February 9, 2026

param(
    [switch]$SkipClone,
    [switch]$SkipVSCode,
    [string]$TargetDirectory = "frappe_docker"
)

$ErrorActionPreference = "Stop"

Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  CvSU AMS Development Environment Setup                 ║" -ForegroundColor Cyan
Write-Host "║  Cavite State University - Accounting Management System  ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
function Test-Prerequisites {
    Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow
    
    # Check WSL2
    try {
        $wslStatus = wsl --list --verbose
        if ($LASTEXITCODE -ne 0) {
            throw "WSL not installed or not running"
        }
        Write-Host "✅ WSL2 is installed" -ForegroundColor Green
    } catch {
        Write-Host "❌ WSL2 is not installed. Please install WSL2 first:" -ForegroundColor Red
        Write-Host "   Run: wsl --install" -ForegroundColor Yellow
        exit 1
    }
    
    # Check Docker Desktop
    try {
        docker --version | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "Docker not found"
        }
        Write-Host "✅ Docker Desktop is installed" -ForegroundColor Green
    } catch {
        Write-Host "❌ Docker Desktop is not installed" -ForegroundColor Red
        Write-Host "   Download from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
        exit 1
    }
    
    # Check Git
    try {
        git --version | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "Git not found"
        }
        Write-Host "✅ Git is installed" -ForegroundColor Green
    } catch {
        Write-Host "❌ Git is not installed" -ForegroundColor Red
        Write-Host "   Download from: https://git-scm.com/download/win" -ForegroundColor Yellow
        exit 1
    }
    
    # Check VS Code
    if (-not $SkipVSCode) {
        try {
            code --version | Out-Null
            if ($LASTEXITCODE -ne 0) {
                throw "VS Code not found"
            }
            Write-Host "✅ VS Code is installed" -ForegroundColor Green
        } catch {
            Write-Host "⚠️  VS Code is not installed or not in PATH" -ForegroundColor Yellow
            Write-Host "   Download from: https://code.visualstudio.com/" -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
}

# Clone repository
function Clone-Repository {
    if ($SkipClone) {
        Write-Host "⏭️  Skipping repository clone" -ForegroundColor Yellow
        return
    }
    
    Write-Host "📥 Cloning frappe_docker repository..." -ForegroundColor Yellow
    
    if (Test-Path $TargetDirectory) {
        Write-Host "⚠️  Directory '$TargetDirectory' already exists" -ForegroundColor Yellow
        $response = Read-Host "Do you want to delete and re-clone? (y/N)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            Remove-Item -Recurse -Force $TargetDirectory
        } else {
            Write-Host "ℹ️  Using existing directory" -ForegroundColor Cyan
            return
        }
    }
    
    git clone https://github.com/frappe/frappe_docker.git $TargetDirectory
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to clone repository" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Repository cloned successfully" -ForegroundColor Green
    Write-Host ""
}

# Setup dev container
function Setup-DevContainer {
    Write-Host "🔧 Setting up dev container configuration..." -ForegroundColor Yellow
    
    Push-Location $TargetDirectory
    
    # Copy devcontainer configuration
    if (Test-Path ".devcontainer") {
        Write-Host "⚠️  .devcontainer already exists, backing up..." -ForegroundColor Yellow
        if (Test-Path ".devcontainer.backup") {
            Remove-Item -Recurse -Force ".devcontainer.backup"
        }
        Move-Item ".devcontainer" ".devcontainer.backup"
    }
    
    Copy-Item -Recurse -Force "devcontainer-example" ".devcontainer"
    Write-Host "✅ Dev container configuration copied" -ForegroundColor Green
    
    # Copy VS Code settings
    if (-not (Test-Path "development\.vscode")) {
        Copy-Item -Recurse -Force "development\vscode-example" "development\.vscode"
        Write-Host "✅ VS Code settings copied" -ForegroundColor Green
    } else {
        Write-Host "ℹ️  VS Code settings already exist" -ForegroundColor Cyan
    }
    
    # Copy CvSU AMS docker-compose to main docker-compose.yml
    $cvsuComposeSource = ".devcontainer\docker-compose.cvsu-ais.yml"
    $cvsuComposeTarget = ".devcontainer\docker-compose.yml"
    
    if (Test-Path $cvsuComposeSource) {
        Write-Host "📋 Copying CvSU AMS docker-compose configuration..." -ForegroundColor Yellow
        Copy-Item -Force $cvsuComposeSource $cvsuComposeTarget
        Write-Host "✅ CvSU AMS docker-compose activated" -ForegroundColor Green
    } else {
        Write-Host "⚠️  docker-compose.cvsu-ais.yml not found, using default" -ForegroundColor Yellow
    }
    
    Pop-Location
    Write-Host ""
}

# Create environment file
function Create-EnvFile {
    Write-Host "📝 Creating environment file..." -ForegroundColor Yellow
    
    $envContent = @"
# CvSU AMS Environment Configuration
# Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

# Database Configuration
DB_PASSWORD=123
MYSQL_ROOT_PASSWORD=123

# Site Configuration
SITE_NAME=accounting.localhost
ADMIN_PASSWORD=admin

# Developer Mode
DEVELOPER_MODE=1

# Python Version
PYTHON_VERSION=3.11.9

# SonarQube
SONAR_HOST_URL=http://sonarqube:9000
"@
    
    $envPath = Join-Path $TargetDirectory ".devcontainer\.env"
    Set-Content -Path $envPath -Value $envContent
    Write-Host "✅ Environment file created: .devcontainer\.env" -ForegroundColor Green
    Write-Host ""
}

# Create setup script for inside container
function Create-ContainerSetupScript {
    Write-Host "📝 Creating container setup script..." -ForegroundColor Yellow
    
    $setupScript = @'
#!/bin/bash
# CvSU AMS Container Setup Script
# Run this inside the dev container

set -e

echo "🚀 CvSU AMS Container Setup"
echo "=============================="

# Install Python 3.11.9
echo "📦 Installing Python 3.11.9..."
if ! pyenv versions | grep -q "3.11.9"; then
    pyenv install 3.11.9
fi
pyenv global 3.11.9
python --version

# Install frappe-bench
echo "📦 Installing frappe-bench..."
pip install frappe-bench

# Initialize bench
echo "🔨 Initializing Frappe bench..."
cd /workspace/development

if [ ! -d "frappe-bench" ]; then
    bench init --skip-redis-config-generation --frappe-branch version-15 frappe-bench
    cd frappe-bench
    
    # Configure database and Redis
    bench set-config -g db_host mariadb
    bench set-config -g redis_cache redis://redis-cache:6379
    bench set-config -g redis_queue redis://redis-queue:6379
    bench set-config -g redis_socketio redis://redis-queue:6379
    
    # Get standard apps
    echo "📥 Installing ERPNext apps..."
    bench get-app erpnext --branch version-15
    bench get-app hrms --branch version-15
    bench get-app payments --branch version-15
    
    echo "✅ Bench initialized successfully"
else
    echo "ℹ️  Bench already initialized"
    cd frappe-bench
fi

# Create site if not exists
if [ ! -d "sites/accounting.localhost" ]; then
    echo "🌐 Creating site: accounting.localhost..."
    bench new-site accounting.localhost \
        --mariadb-root-password 123 \
        --admin-password admin \
        --no-mariadb-socket \
        --install-app erpnext
    
    # Set developer mode
    bench --site accounting.localhost set-config developer_mode 1
    
    # Set as default site
    bench use accounting.localhost
    
    # Install additional apps
    echo "📦 Installing additional apps..."
    bench install-app hrms
    bench install-app payments
    
    # Run migrations
    bench migrate
    
    echo "✅ Site created successfully"
else
    echo "ℹ️  Site already exists: accounting.localhost"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ✅ Setup Complete!                                      ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  To start development:                                   ║"
echo "║    bench start                                           ║"
echo "║                                                          ║"
echo "║  Access at: http://localhost:8000                        ║"
echo "║  Username: Administrator                                 ║"
echo "║  Password: admin                                         ║"
echo "╚══════════════════════════════════════════════════════════╝"
'@
    
    $scriptPath = Join-Path $TargetDirectory "development\setup-container.sh"
    Set-Content -Path $scriptPath -Value $setupScript
    
    # Convert line endings to LF (Linux)
    $content = Get-Content -Path $scriptPath -Raw
    $content = $content -replace "`r`n", "`n"
    Set-Content -Path $scriptPath -Value $content -NoNewline
    
    Write-Host "✅ Container setup script created: development/setup-container.sh" -ForegroundColor Green
    Write-Host ""
}

# Create README in devcontainer
function Create-DevContainerReadme {
    Write-Host "📝 Creating devcontainer README..." -ForegroundColor Yellow
    
    $readmeContent = @"
# CvSU AMS Dev Container

This dev container is configured for CvSU Accounting Management System development.

## Quick Start

1. **Reopen in Container**
   - Press \`Ctrl+Shift+P\`
   - Type: "Dev Containers: Reopen in Container"
   - Wait for container to build (~5-10 minutes first time)

2. **Run Setup Script**
   \`\`\`bash
   cd /workspace/development
   bash setup-container.sh
   \`\`\`

3. **Start Development Server**
   \`\`\`bash
   cd frappe-bench
   bench start
   \`\`\`

4. **Access Application**
   - URL: http://localhost:8000
   - Username: Administrator
   - Password: admin

## Installed Apps

### Standard Apps
- frappe (Framework)
- erpnext (ERP)
- hrms (HR Management)
- payments (Payment Gateway)

### Custom Apps (To be installed)
- cvsu_hris (CvSU HRIS)
- ams (Accounting Management System)

## Useful Commands

\`\`\`bash
# List all sites
bench list-sites

# Create new app
bench new-app <app-name>

# Install app on site
bench install-app <app-name>

# Run migrations
bench migrate

# Clear cache
bench clear-cache

# Run tests
bench run-tests --app <app-name>

# Backup site
bench backup --with-files

# Console (IPython)
bench console
\`\`\`

## Database Access

\`\`\`bash
# Access MariaDB
mariadb -h mariadb -u root -p
# Password: 123
\`\`\`

## Ports

- 8000-8005: Frappe web servers
- 9000-9005: SocketIO servers
- 3307: MariaDB (mapped to host)
- 9999: SonarQube (mapped to host)

## Troubleshooting

### Bench command not found
\`\`\`bash
pip install frappe-bench
\`\`\`

### Python version issues
\`\`\`bash
pyenv install 3.11.9
pyenv global 3.11.9
\`\`\`

### Clear everything and restart
\`\`\`bash
cd /workspace/development
rm -rf frappe-bench
bash setup-container.sh
\`\`\`

---
For full documentation, see: [SETUP_GUIDE.md](SETUP_GUIDE.md)
"@
    
    $readmePath = Join-Path $TargetDirectory ".devcontainer\README.md"
    Set-Content -Path $readmePath -Value $readmeContent
    Write-Host "✅ Dev container README created" -ForegroundColor Green
    Write-Host ""
}

# Open in VS Code
function Open-InVSCode {
    if ($SkipVSCode) {
        Write-Host "⏭️  Skipping VS Code launch" -ForegroundColor Yellow
        return
    }
    
    Write-Host "🚀 Opening in VS Code..." -ForegroundColor Yellow
    Push-Location $TargetDirectory
    code .
    Pop-Location
    Write-Host "✅ VS Code opened" -ForegroundColor Green
    Write-Host ""
}

# Main execution
function Main {
    Test-Prerequisites
    Clone-Repository
    Setup-DevContainer
    Create-EnvFile
    Create-ContainerSetupScript
    Create-DevContainerReadme
    
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  ✅ Setup Complete!                                      ║" -ForegroundColor Green
    Write-Host "╠══════════════════════════════════════════════════════════╣" -ForegroundColor Green
    Write-Host "║  📋 Configuration Summary:                               ║" -ForegroundColor Green
    Write-Host "║  • Docker Compose: docker-compose.cvsu-ais.yml           ║" -ForegroundColor Green
    Write-Host "║  • Site: accounting.localhost                            ║" -ForegroundColor Green
    Write-Host "║  • Python: 3.11.9                                        ║" -ForegroundColor Green
    Write-Host "║  • Database: MariaDB 11.8 (port 3307)                    ║" -ForegroundColor Green
    Write-Host "║  • SonarQube: Port 9999                                  ║" -ForegroundColor Green
    Write-Host "╠══════════════════════════════════════════════════════════╣" -ForegroundColor Green
    Write-Host "║  Next Steps:                                             ║" -ForegroundColor Green
    Write-Host "║                                                          ║" -ForegroundColor Green
    Write-Host "║  1. Open in VS Code:                                     ║" -ForegroundColor Green
    Write-Host "║     cd $TargetDirectory                                  ║" -ForegroundColor Green
    Write-Host "║     code .                                               ║" -ForegroundColor Green
    Write-Host "║                                                          ║" -ForegroundColor Green
    Write-Host "║  2. Reopen in Container:                                 ║" -ForegroundColor Green
    Write-Host "║     Ctrl+Shift+P → 'Dev Containers: Reopen in Container' ║" -ForegroundColor Green
    Write-Host "║                                                          ║" -ForegroundColor Green
    Write-Host "║  3. Wait for container to build (~5-10 minutes)          ║" -ForegroundColor Green
    Write-Host "║                                                          ║" -ForegroundColor Green
    Write-Host "║  4. Run setup script inside container:                   ║" -ForegroundColor Green
    Write-Host "║     bash /workspace/development/setup-container.sh       ║" -ForegroundColor Green
    Write-Host "║                                                          ║" -ForegroundColor Green
    Write-Host "║  5. Start development:                                   ║" -ForegroundColor Green
    Write-Host "║     cd frappe-bench && bench start                       ║" -ForegroundColor Green
    Write-Host "║                                                          ║" -ForegroundColor Green
    Write-Host "║  6. Access application:                                  ║" -ForegroundColor Green
    Write-Host "║     http://localhost:8000                                ║" -ForegroundColor Green
    Write-Host "║     Username: Administrator                              ║" -ForegroundColor Green
    Write-Host "║     Password: admin                                      ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Green
    
    Open-InVSCode
}

# Run main function
Main
