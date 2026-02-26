# 📦 CvSU AMS Development Environment - Package Overview

**Cavite State University - Accounting Management System**  
**Complete Docker-based Development Setup**  
**Last Updated:** February 9, 2026

---

## ✅ What's Been Created for You

I've created a complete development environment configuration based on your actual setup instructions and the official Frappe Docker documentation. Here's what's included:

### 📁 Files in `.devcontainer/`

1. **docker-compose.cvsu-ais.yml** (384 lines)
   - Complete Docker Compose configuration
   - MariaDB 11.8 with health checks
   - Redis cache & queue
   - Frappe bench with Python 3.11.9
   - SonarQube integration
   - Automated site setup for `accounting.localhost`
   - Developer mode enabled

2. **devcontainer.json** (Updated)
   - VS Code Dev Container settings
   - Python 3.11.9 interpreter path
   - SQLTools connections (root + accounting site)
   - Extended port forwarding (8000-8005, 9000-9005, 9999, 3307)
   - Helpful extensions (Python, Pylance, GitLens, Copilot, etc.)

3. **SETUP_GUIDE.md** (500+ lines)
   - Complete step-by-step setup instructions
   - Prerequisites checklist
   - Manual and automated setup options
   - Database management
   - Permission configuration
   - Comprehensive troubleshooting

4. **QUICK_REFERENCE.md** (300+ lines)
   - Command cheat sheet
   - All bench commands organized by category
   - Docker commands
   - Database operations
   - Testing commands
   - Quick fixes for common issues

5. **setup-windows.ps1** (PowerShell Script)
   - Automated Windows setup
   - Prerequisites validation
   - Repository cloning
   - Configuration copying
   - VS Code launching

6. **setup-container.sh** (Auto-generated)
   - Runs inside the container
   - Installs Python 3.11.9
   - Initializes bench
   - Gets ERPNext apps
   - Creates accounting.localhost site
   - Sets developer mode

---

## 🎯 Configuration Highlights

### Matches Your Actual Setup

✅ **Python 3.11.9** (not 3.11.6 - as per your instructions)  
✅ **Site: accounting.localhost** (not cvsu-ais.localhost)  
✅ **Standard Apps:** frappe, erpnext, hrms, payments  
✅ **Custom Apps:** cvsu_hris, ams (accounting)  
✅ **Developer Mode:** Enabled by default  
✅ **Database:** MariaDB 11.8 on port 3307  
✅ **SonarQube:** Port 9999 (9000 used by SocketIO)  

### Key Features

- **Automatic initialization** - bench setup runs on first start
- **Health checks** - services wait for dependencies
- **Persistent volumes** - data survives container restarts
- **Port mapping** - all Frappe ports (8000-8005, 9000-9005)
- **Database access** - MariaDB accessible from host
- **Code quality** - SonarQube pre-configured

---

## 🚀 Quick Start

### Option 1: Copy to Frappe Docker Repo

If you haven't cloned frappe_docker yet:

```powershell
# 1. Clone frappe_docker
git clone https://github.com/frappe/frappe_docker.git
cd frappe_docker

# 2. Copy the devcontainer configuration
Copy-Item -Recurse -Force "devcontainer-example" ".devcontainer"

# 3. Replace with CvSU AMS config
# (Copy these files from where you saved them)
Copy-Item -Force "path\to\docker-compose.cvsu-ais.yml" ".devcontainer\docker-compose.yml"
Copy-Item -Force "path\to\devcontainer.json" ".devcontainer\devcontainer.json"
Copy-Item -Force "path\to\SETUP_GUIDE.md" ".devcontainer\"
Copy-Item -Force "path\to\QUICK_REFERENCE.md" ".devcontainer\"
Copy-Item -Force "path\to\setup-windows.ps1" ".devcontainer\"

# 4. Open in VS Code
code .

# 5. Reopen in container (Ctrl+Shift+P)
# Select: "Dev Containers: Reopen in Container"
```

### Option 2: Use Existing Setup

If you're already in frappe_docker:

```powershell
# Update your docker-compose.yml
Copy-Item -Force ".devcontainer\docker-compose.cvsu-ais.yml" ".devcontainer\docker-compose.yml"

# Restart container
# Ctrl+Shift+P → "Dev Containers: Rebuild Container"
```

---

## 📋 Standard Workflow

### Initial Setup (First Time)

```bash
# Inside dev container terminal
bash /workspace/development/setup-container.sh
```

This script will:
1. Install Python 3.11.9
2. Initialize Frappe bench
3. Configure database and Redis connections
4. Get ERPNext apps (erpnext, hrms, payments)
5. Create `accounting.localhost` site
6. Enable developer mode
7. Install apps on site

### Daily Development

```bash
# Navigate to bench
cd /workspace/development/frappe-bench

# Start development server
bench start

# Access at: http://localhost:8000
# Username: Administrator
# Password: admin
```

### Install Custom Apps

```bash
cd /workspace/development/frappe-bench

# Get CvSU HRIS (if you have access)
bench get-app cvsu_hris --branch dev https://github.com/Cavite-State-University-Official/hris.git
bench install-app cvsu_hris

# Create AMS app
bench new-app accounting
bench install-app accounting

# Run migrations
bench migrate
```

---

## 🗂️ Apps Structure

As per your AIS Implementation Summary:

```
frappe-bench/apps/
├── frappe/              # Framework
├── erpnext/            # ERP
├── hrms/               # HR Management
├── payments/           # Payment Gateway
├── cvsu_hris/          # CvSU HRIS (custom)
└── accounting/         # AMS (custom)
    └── accounting/accounting/
        ├── doctype/
        │   └── project_accounting_entry/
        ├── utils/
        │   ├── constants.py              # UACS codes, statuses
        │   └── decimal_utils.py          # Decimal arithmetic
        ├── services/
        │   ├── tax_calculation_service.py      # BIR tax (VAT 5%, EWT 1%)
        │   ├── budget_validation_service.py    # Budget checks
        │   └── accounting_entry_service.py     # Balance validation
        ├── validators/
        │   └── accounting_validator.py   # Custom exceptions
        ├── api/
        │   └── accounting_api.py         # REST endpoints
        └── tests/
            └── test_tax_calculations.py
```

---

## 🔧 Common Commands

### Bench Operations
```bash
bench start              # Start development server
bench restart            # Restart all processes
bench migrate            # Run database migrations
bench clear-cache        # Clear all cache
bench update             # Update all apps
```

### Site Management
```bash
bench list-sites                                    # List all sites
bench use accounting.localhost                      # Set default site
bench --site accounting.localhost install-app ams  # Install app
bench --site accounting.localhost migrate          # Migrate site
bench --site accounting.localhost clear-cache      # Clear site cache
```

### Development
```bash
bench new-app accounting                 # Create new app
bench watch                              # Watch for changes
bench console                            # IPython console
bench mariadb                            # Database console
bench run-tests --app accounting         # Run tests
```

For complete command reference, see: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

## 🌐 Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| Frappe Web | http://localhost:8000 | Administrator / admin |
| SonarQube | http://localhost:9999 | admin / admin |
| MariaDB | localhost:3307 | root / 123 |
| SQLTools | VS Code Extension | Pre-configured |

---

## 📚 Documentation Files

1. **This File** - Package overview
2. **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed setup instructions
3. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Command cheat sheet
4. **setup-windows.ps1** - Automation script
5. **docker-compose.cvsu-ais.yml** - Service configuration

Additional docs in `/workspace/development/`:
- AIS_IMPLEMENTATION_SUMMARY.md
- AIS_PROJECT_STRUCTURE.md
- AIS_SYSTEM_ARCHITECTURE.md
- IMPLEMENTATION_PLAN.md

---

## ⚙️ Configuration Summary

### Docker Services

| Service | Image | Purpose | Port |
|---------|-------|---------|------|
| mariadb | mariadb:11.8 | Database | 3307 |
| redis-cache | redis:alpine | Cache | 6379 |
| redis-queue | redis:alpine | Queue | 6379 |
| frappe | frappe/bench:latest | App server | 8000-8005, 9000-9005 |
| sonarqube | sonarqube:9.9 | Code quality | 9999 |
| sonarqube_db | postgres:13 | SonarQube DB | 5432 |

### Python Environment
- **Version:** 3.11.9 (via pyenv)
- **Package Manager:** pip
- **Virtual Env:** frappe-bench/env

### Site Configuration
- **Name:** accounting.localhost
- **Admin:** Administrator / admin
- **Developer Mode:** Enabled
- **Database:** accounting_localhost

---

## 🎓 Next Steps

1. **Review the documentation:**
   - Read [SETUP_GUIDE.md](SETUP_GUIDE.md) for complete setup instructions
   - Bookmark [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for daily use

2. **Set up your environment:**
   - Follow Quick Start section above
   - Or run `setup-windows.ps1` for automation

3. **Start developing:**
   - Create/install custom apps
   - Implement AMS features
   - Run tests
   - Use SonarQube for code quality

4. **Refer to AIS documentation:**
   - Review implementation summary
   - Follow architecture guidelines
   - Use service patterns
   - Maintain test coverage

---

## 🆘 Need Help?

- **Setup Issues:** See [SETUP_GUIDE.md](SETUP_GUIDE.md) → Troubleshooting
- **Command Help:** See [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **Frappe Help:** https://frappeframework.com/docs
- **Docker Help:** https://github.com/frappe/frappe_docker

---

**Configuration Package Version:** 1.0  
**Created:** February 9, 2026  
**Based on:** Official frappe_docker + CvSU requirements  
**Maintained by:** CvSU Development Team

**Ready to start? Open this folder in VS Code and reopen in container! 🚀**
