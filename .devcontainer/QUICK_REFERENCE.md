# CvSU AMS - Quick Reference Cheat Sheet

## 🚀 Initial Setup (One-time)

```powershell
# Windows - Run from PowerShell
.\setup-windows.ps1

# Or manually:
Copy-Item -Recurse -Force "devcontainer-example" ".devcontainer"
code .
# Then: Ctrl+Shift+P → "Reopen in Container"
```

```bash
# Inside container - Initial bench setup
pyenv install 3.11.9 && pyenv global 3.11.9
bench init --skip-redis-config-generation --frappe-branch version-15 frappe-bench
cd frappe-bench

bench set-config -g db_host mariadb
bench set-config -g redis_cache redis://redis-cache:6379
bench set-config -g redis_queue redis://redis-queue:6379
bench set-config -g redis_socketio redis://redis-queue:6379

# Install apps
bench get-app erpnext --branch version-15
bench get-app hrms --branch version-15
bench get-app payments --branch version-15

# Create site
bench new-site accounting.localhost --admin-password admin --mariadb-root-password 123
bench --site accounting.localhost set-config developer_mode 1
bench use accounting.localhost
bench install-app erpnext hrms payments
```

## 📦 App Management

```bash
# Get app from GitHub
bench get-app <app-name> --branch <branch> <repo-url>
bench get-app cvsu_hris --branch dev https://github.com/Cavite-State-University-Official/hris.git

# Create new app
bench new-app accounting

# Install app on current site
bench install-app <app-name>

# Uninstall app
bench uninstall-app <app-name>

# Remove app from bench
bench remove-app <app-name>

# Update app
bench update --app <app-name>

# List installed apps
bench list-apps

# Link local app
ln -sf /workspace/development/apps/myapp apps/myapp
echo "myapp" >> sites/apps.txt
pip install -e apps/myapp
```

## 🌐 Site Management

```bash
# Create site
bench new-site sitename.localhost --admin-password admin --mariadb-root-password 123

# Drop site
bench drop-site sitename.localhost

# List all sites
bench list-sites

# Set default site (removes need for --site flag)
bench use sitename.localhost

# Set developer mode
bench --site sitename.localhost set-config developer_mode 1

# Migrate site
bench --site sitename.localhost migrate

# Clear cache
bench --site sitename.localhost clear-cache
bench --site sitename.localhost clear-website-cache

# Console (IPython)
bench --site sitename.localhost console
```

## 🏃 Running & Development

```bash
# Start all processes (web, workers, socketio, scheduler)
bench start

# Start specific service
bench serve              # Web server only
bench worker             # Worker only
bench schedule           # Scheduler only

# Watch for frontend changes
bench watch

# Restart
bench restart

# Build assets
bench build
bench build --app <app-name>

# Setup requirements
bench setup requirements
bench setup requirements --dev
```

## 🗄️ Database

```bash
# Access MariaDB console
bench mariadb
# Or: mariadb -h mariadb -u root -p123

# Backup
bench --site sitename.localhost backup
bench --site sitename.localhost backup --with-files

# Restore
bench --site sitename.localhost restore /path/to/backup.sql.gz

# Execute SQL file
bench --site sitename.localhost execute path/to/script.sql

# Database migrate
bench --site sitename.localhost migrate
bench --site sitename.localhost migrate --skip-failing
```

## 🧪 Testing

```bash
# Run all tests for app
bench --site sitename.localhost run-tests --app myapp

# Run specific test file
bench --site sitename.localhost run-tests myapp.tests.test_file

# Run specific test class
bench --site sitename.localhost run-tests myapp.tests.test_file.TestClass

# Run with coverage
bench --site sitename.localhost run-tests --app myapp --coverage

# View coverage report
bench --site sitename.localhost coverage report
```

## 🔍 Debugging & Logs

```bash
# View logs
bench --site sitename.localhost doctor
bench --site sitename.localhost console      # Interactive debugging

# Tail error logs
tail -f logs/web.error.log
tail -f logs/worker.error.log
tail -f sites/sitename.localhost/logs/

# Enable SQL logging
bench --site sitename.localhost set-config allow_tests 1
```

## 🛠️ Frappe Commands

```bash
# Show all bench commands
bench --help

# Check system health
bench doctor

# Version info
bench version
bench --version

# Update bench
bench update --pull        # Pull changes only
bench update --patch       # Update and migrate
bench update --reset       # Hard reset and update

# Setup
bench setup requirements   # Python packages
bench setup add-domain     # Add custom domain
bench setup nginx          # Setup nginx config
bench setup production     # Production setup
```

## 📝 DocType & Code Generation

```bash
# Create DocType
bench --site sitename.localhost new-doctype

# Install fixtures
bench --site sitename.localhost install-fixtures

# Export fixtures
bench --site sitename.localhost export-fixtures

# Make module
bench new-module <module-name> --app <app-name>
```

## 🔧 Configuration

```bash
# Get config value
bench config get <key>

# Set config value
bench set-config <key> <value>
bench set-config -g <key> <value>  # Global

# Common configs
bench set-config developer_mode 1
bench set-config disable_scheduler 1
bench set-config allow_cors '*'
bench set-config http_port 8001
```

## 🐳 Docker Commands

```bash
# View running containers
docker ps

# Enter container
docker exec -it cvsu_ais_frappe bash

# View logs
docker compose logs -f frappe
docker compose logs -f mariadb

# Restart container
docker compose restart frappe

# Stop all
docker compose down

# Stop and remove volumes (DANGER: deletes data)
docker compose down -v
```

## 📊 SonarQube

```bash
# Start SonarQube
docker compose up -d sonarqube

# Run code analysis
cd /workspace/development
bash run_sonarqube_scan.sh

# Access: http://localhost:9999
# Default: admin / admin
```

## 🔐 User Management

```bash
# Create user (in bench console)
bench --site sitename.localhost console

>>> from frappe.utils.password import update_password
>>> frappe.get_doc("User", "user@example.com").update_password("newpassword")
>>> frappe.db.commit()
```

## 📂 Important Paths

```
/workspace/development/frappe-bench/         # Bench root
├── apps/                                    # All apps
│   ├── frappe/
│   ├── erpnext/
│   ├── cvsu_hris/
│   └── accounting/                          # Your custom app
├── sites/                                   # All sites
│   ├── accounting.localhost/
│   │   ├── private/backups/                 # Backups
│   │   └── public/files/                    # Uploaded files
│   ├── apps.txt                             # Installed apps list
│   └── common_site_config.json              # Global config
├── logs/                                    # Log files
└── env/                                     # Python virtual environment
```

## 🆘 Quick Fixes

```bash
# Bench command not found
pip install frappe-bench

# Python version wrong
pyenv install 3.11.9 && pyenv global 3.11.9

# Port 8000 in use
bench set-config http_port 8001

# Database connection failed
bench set-config -g db_host mariadb
bench restart

# Migration failed
bench --site sitename.localhost migrate --skip-failing

# Clear everything
bench --site sitename.localhost clear-cache
bench build
bench restart

# Nuclear option (start fresh)
cd /workspace/development
rm -rf frappe-bench
# Then re-run setup
```

## 🎯 CvSU AMS Specific

```bash
# Site: accounting.localhost
# Username: Administrator
# Password: admin

# Standard apps
bench install-app erpnext hrms payments

# Custom apps
bench get-app cvsu_hris --branch dev https://github.com/Cavite-State-University-Official/hris.git
bench new-app accounting
bench install-app cvsu_hris accounting

# Run AMS tests
bench run-tests --app accounting

# AMS app structure
apps/accounting/accounting/accounting/
├── doctype/project_accounting_entry/
├── utils/constants.py
├── services/tax_calculation_service.py
├── validators/accounting_validator.py
├── api/accounting_api.py
└── tests/
```

## ⌨️ VS Code Shortcuts

```
Ctrl+Shift+P    Command Palette
Ctrl+`          Toggle Terminal
Ctrl+Shift+`    New Terminal
F5              Start Debugging
Ctrl+F5         Run Without Debugging
```

---

**Quick Access URLs:**
- Frappe: http://localhost:8000
- SonarQube: http://localhost:9999
- MariaDB: localhost:3307

**Documentation:**
- Setup Guide: `.devcontainer/SETUP_GUIDE.md`
- AIS Structure: `development/AIS_PROJECT_STRUCTURE.md`
- Implementation: `development/AIS_IMPLEMENTATION_SUMMARY.md`

**Last Updated:** February 9, 2026
