# CvSU AMS Development Setup Guide

Complete setup instructions for the Cavite State University Accounting Management System (AMS) development environment.

## 📋 Prerequisites

- **Windows 10/11** with WSL2 enabled
- **Docker Desktop** for Windows (latest version)
- **VS Code** with Dev Containers extension
- **Git** for Windows
- **At least 16GB RAM** and 50GB free disk space

## 🚀 Quick Start

### Step 1: Clone the Repository

```powershell
# Clone frappe_docker repository
git clone https://github.com/frappe/frappe_docker.git
cd frappe_docker
```

### Step 2: Setup Dev Container Configuration

**Windows PowerShell:**
```powershell
# Copy devcontainer configuration
Copy-Item -Recurse -Force "devcontainer-example" ".devcontainer"
Copy-Item -Recurse -Force "development/vscode-example" "development/.vscode"

# Copy CvSU AMS custom docker-compose (if you have it)
# Copy-Item "docker-compose.cvsu-ais.yml" ".devcontainer/docker-compose.yml"
```

**Linux/Mac:**
```bash
cp -R devcontainer-example .devcontainer
cp -R development/vscode-example development/.vscode
```

### Step 3: Open in VS Code

```powershell
code .
```

### Step 4: Install VS Code Extensions

In VS Code, install:
- **Dev Containers** (ms-vscode-remote.remote-containers)
- **Python** (ms-python.python)
- **Pylance** (ms-python.vscode-pylance)
- **GitHub Copilot** (optional but recommended)

### Step 5: Reopen in Container

1. Press `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac)
2. Type: "Dev Containers: Reopen in Container"
3. Select the command and wait for container to build (~5-10 minutes first time)

### Step 6: Initialize Frappe Bench

Once inside the container terminal:

```bash
# Install Python 3.11.9 (required for Frappe v15)
pyenv install 3.11.9
pyenv global 3.11.9

# Verify Python version
python --version  # Should show 3.11.9

# Install frappe-bench
pip install frappe-bench

# Initialize bench
bench init --skip-redis-config-generation --frappe-branch version-15 frappe-bench
cd frappe-bench

# Configure database and Redis
bench set-config -g db_host mariadb
bench set-config -g redis_cache redis://redis-cache:6379
bench set-config -g redis_queue redis://redis-queue:6379
bench set-config -g redis_socketio redis://redis-queue:6379
```

### Step 7: Install Apps

```bash
# Standard ERPNext apps (install in order)
bench get-app erpnext --branch version-15
bench get-app hrms --branch version-15
bench get-app payments --branch version-15

# CvSU Custom Apps
# Option 1: Clone from GitHub (if you have access)
bench get-app cvsu_hris --branch dev https://github.com/Cavite-State-University-Official/hris.git

# Option 2: Create new accounting app
bench new-app accounting

# Option 3: Link existing local apps
# ln -sf /workspace/development/apps/cvsu_hris /workspace/development/frappe-bench/apps/cvsu_hris
```

### Step 8: Create Site

```bash
# Create new site
bench new-site accounting.localhost \
  --mariadb-root-password 123 \
  --admin-password admin \
  --no-mariadb-socket \
  --install-app erpnext

# Enable developer mode
bench --site accounting.localhost set-config developer_mode 1

# Set as default site (removes need for --site flag)
bench use accounting.localhost

# Install additional apps
bench install-app hrms
bench install-app payments

# Install custom apps (when ready)
# bench install-app cvsu_hris
# bench install-app accounting

# Run migrations
bench migrate
```

### Step 9: Start Development Server

```bash
bench start
```

Access the application at: **http://localhost:8000**

- **Username:** Administrator
- **Password:** admin
- **Site:** accounting.localhost

## 📦 CvSU Apps Architecture

### Standard Apps (from Frappe/ERPNext)
- `frappe` - Core framework
- `erpnext` - ERP functionality
- `hrms` - HR management
- `payments` - Payment integration

### Custom CvSU Apps
- `cvsu_hris` - Human Resource Information System
- `ams` (accounting) - Accounting Management System
  - Project Accounting Entry DocType
  - Tax Calculation Service (BIR-compliant)
  - Budget Validation Service
  - Accounting Entry Service
  - UACS Chart of Accounts

## 🔧 Advanced Setup

### Install Custom App from Local Directory

If you have the app code in `/workspace/development/apps/`:

```bash
cd /workspace/development/frappe-bench

# Link the app
ln -sf /workspace/development/apps/ams apps/ams

# Install in editable mode
source env/bin/activate
pip install -e apps/ams

# Add to apps.txt
echo "ams" >> sites/apps.txt

# Install on site
bench --site accounting.localhost install-app ams
```

### Install HRIS with npm dependencies

```bash
cd /workspace/development/frappe-bench/apps/cvsu_hris
npm install

cd /workspace/development/frappe-bench
bench --site accounting.localhost install-app cvsu_hris
```

### Update Apps

```bash
cd /workspace/development/frappe-bench

# Update specific app
bench update --app erpnext

# Update all apps
bench update

# Update only pull (no migrate)
bench update --pull
```

## 🗄️ Database Management

### Access MariaDB

```bash
# From host machine
docker exec -it frappe_docker_devcontainer-mariadb-1 mariadb -u root -p
# Password: 123

# Inside container
mariadb -h mariadb -u root -p
```

### Backup Site

```bash
# Backup database and files
bench --site accounting.localhost backup --with-files

# Backups are stored in: sites/accounting.localhost/private/backups/
```

### Restore Site

```bash
# Restore from backup
bench --site accounting.localhost restore \
  --mariadb-root-password 123 \
  /path/to/backup.sql.gz
```

### Fix MariaDB Corruption

If MariaDB gets corrupted:

```sql
-- Access MariaDB as root
docker exec -it frappe_docker_devcontainer-mariadb-1 mariadb -u root -p

-- Create database and user
CREATE DATABASE IF NOT EXISTS `accounting_localhost`;
CREATE USER IF NOT EXISTS 'accounting_localhost'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON `accounting_localhost`.* TO 'accounting_localhost'@'%';
FLUSH PRIVILEGES;
EXIT;
```

Then restore from backup or recreate site.

## 👥 Initial Permissions Setup

After site creation, configure role permissions:

1. Go to: **Role Permission Manager**
2. Select DocType: **Employee**
3. Select Role: **HR Manager**
4. Click "Add A New Rule"
5. Set Permission Level 1: ✅ Read, ✅ Write

## 🧪 Development Workflow

### Run Tests

```bash
# Run all tests for custom app
bench --site accounting.localhost run-tests --app ams

# Run specific test file
bench --site accounting.localhost run-tests ams.tests.test_tax_calculations

# Run with coverage
bench --site accounting.localhost run-tests --app ams --coverage
```

### Code Quality

```bash
# Run SonarQube analysis
cd /workspace/development
bash run_sonarqube_scan.sh

# View results at: http://localhost:9999
```

### Watch for Changes

```bash
# Watch and rebuild on file changes
bench watch
```

### Clear Cache

```bash
# Clear all cache
bench --site accounting.localhost clear-cache

# Clear website cache
bench --site accounting.localhost clear-website-cache
```

## 🐛 Troubleshooting

### Check WSL Status

```powershell
# From Windows PowerShell
wsl --list --verbose

# Should show Ubuntu running (STATE: Running)
```

### Container Not Starting

```bash
# View logs
docker compose -f .devcontainer/docker-compose.yml logs -f

# Restart containers
docker compose -f .devcontainer/docker-compose.yml restart
```

### Bench Command Not Found

```bash
# Ensure you're in the right directory
cd /workspace/development/frappe-bench

# Or reinstall bench
pip install frappe-bench
```

### Python Version Issues

```bash
# Check available versions
pyenv versions

# Install correct version
pyenv install 3.11.9
pyenv global 3.11.9

# Verify
python --version
```

### Port Already in Use

If port 8000 is already in use:

```bash
# Find process using port
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or change bench port
bench set-config -g http_port 8001
```

## 📚 Useful Commands Reference

```bash
# Bench commands
bench --version                          # Check bench version
bench --help                             # Show all commands
bench doctor                             # System health check
bench migrate                            # Run database migrations
bench restart                            # Restart bench processes

# Site commands
bench new-site <sitename>                # Create new site
bench drop-site <sitename>               # Delete site
bench list-sites                         # List all sites
bench use <sitename>                     # Set default site

# App commands
bench get-app <app-name>                 # Clone and install app
bench install-app <app-name>             # Install app on current site
bench uninstall-app <app-name>           # Uninstall app from site
bench remove-app <app-name>              # Remove app from bench

# Development
bench start                              # Start development server
bench watch                              # Watch for frontend changes
bench console                            # Open IPython console
bench mariadb                            # Open MariaDB console

# Database
bench backup                             # Backup current site
bench restore <path>                     # Restore from backup
bench migrate-to <sitename>              # Migrate data to another site
```

## 🔗 Additional Resources

- [Frappe Framework Docs](https://frappeframework.com/docs)
- [ERPNext Documentation](https://docs.erpnext.com/)
- [Frappe Docker Repo](https://github.com/frappe/frappe_docker)
- [CvSU AIS Implementation Summary](../development/AIS_IMPLEMENTATION_SUMMARY.md)
- [Project Structure Guide](../development/AIS_PROJECT_STRUCTURE.md)

## ⚙️ Environment Variables

Create `.env` file in `.devcontainer/`:

```env
# Database
DB_PASSWORD=123
MYSQL_ROOT_PASSWORD=123

# Site Configuration
SITE_NAME=accounting.localhost
ADMIN_PASSWORD=admin

# Developer Mode
DEVELOPER_MODE=1

# SonarQube
SONAR_HOST_URL=http://sonarqube:9000
SONAR_TOKEN=your_token_here
```

---

**Last Updated:** February 9, 2026  
**Maintainer:** CvSU Development Team
