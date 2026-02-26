# Using VSCode Dev Containers

## ✨ What Changed

You don't need to manually run `docker-compose` commands anymore! VSCode Dev Containers will handle everything automatically.

## 🚀 How to Use

### Method 1: Command Palette (Recommended)
1. Press `Ctrl+Shift+P` (or `F1`)
2. Type: **"Dev Containers: Reopen in Container"**
3. Press Enter
4. Wait for VSCode to build and start the containers
5. ✅ Done! You're now inside the container

### Method 2: Notification
- VSCode should show a notification: **"Folder contains a Dev Container configuration"**
- Click **"Reopen in Container"**

### Method 3: Bottom-Left Corner
- Click the green icon in the bottom-left corner of VSCode (`><`)
- Select **"Reopen in Container"**

## 📦 What Happens Automatically

1. **Containers Start**: All services (MariaDB, Redis, SonarQube, Frappe) start automatically
2. **Bench Installed**: frappe-bench is installed for the `frappe` user
3. **Extensions Installed**: Python, Pylance, SonarLint, etc. installed inside container
4. **Ports Forwarded**: 
   - 8000: Frappe Web (notify on ready)
   - 9000: SonarQube (auto-opens in browser!)
   - 3307: MariaDB
5. **Terminal Ready**: Opens inside the container, bench commands work immediately

## 🎯 After Container Opens

Your terminal will be inside the container at `/workspace/development`. Run:

```bash
# Verify bench is working
bench --version

# Initialize your first site (if not done)
cd frappe-bench
bench new-site mysite.localhost --admin-password admin --mariadb-root-password 123

# Start Frappe
bench start
```

## 🔧 Available Services

- **Frappe**: http://localhost:8000
- **SonarQube**: http://localhost:9000 (auto-opens!)
  - Default login: `admin` / `admin`
- **MariaDB**: localhost:3307
  - User: `root`
  - Password: Check your `.env` or use `123`

## 🛑 Stopping the Environment

1. Press `Ctrl+Shift+P`
2. Type: **"Dev Containers: Close Remote Connection"**
3. Or simply close VSCode

To stop containers manually:
```bash
docker-compose down
```

## 💡 Tips

- **Access terminal**: Terminal opens automatically inside the container
- **Python autocomplete**: Works out of the box with Pylance
- **SonarLint**: Real-time code quality feedback
- **Database access**: Use SQLTools extension (already configured)
- **No more manual commands**: Everything is automated!

## 🔄 Rebuilding

If you change `devcontainer.json` or `docker-compose.yml`:

1. `Ctrl+Shift+P`
2. **"Dev Containers: Rebuild Container"**

---

**Old Method (Deprecated)**
~~`docker-compose up`~~ ❌  
~~`.\start-with-sonarqube.bat`~~ ❌

**New Method**
Just click "Reopen in Container" ✅
