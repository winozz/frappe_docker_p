# Start All Services - Usage Guide

## Overview
The `start-all.bat` script has been updated to reliably start all Frappe Docker services on Windows.

## What Gets Started

1. **MariaDB** - Database server (port 3307)
2. **Redis Cache** - In-memory cache (internal)
3. **Redis Queue** - Job queue (internal)
4. **Frappe Bench** - Application server (ports 8000-8005)
5. **PostgreSQL** - SonarQube database (internal)
6. **SonarQube** - Code quality analysis (port 9999)

## How to Run

### Option 1: Double-click the script
```
start-all.bat
```

### Option 2: Run from PowerShell
```powershell
cd "c:\Users\user\Documents\Test Env\frappe_docker"
.\start-all.bat
```

## What the Script Does

1. ✅ Checks if Docker is running
2. ✅ Cleans up any orphaned containers from previous runs
3. ✅ Pulls latest Docker images
4. ✅ Starts all services in the correct order
5. ✅ Waits 30 seconds for services to stabilize
6. ✅ Displays service URLs and useful commands

## Access Services

After the script completes:

- **Frappe Application**: http://localhost:8000
- **SonarQube**: http://localhost:9999
- **MariaDB**: localhost:3307 (root / 123)

## Useful Commands

### View Logs
```bash
docker-compose -f docker-compose.all.yml logs -f
```

### View Frappe Logs Only
```bash
docker-compose -f docker-compose.all.yml logs -f frappe
```

### Stop All Services
```bash
docker-compose -f docker-compose.all.yml down
```

### Stop and Remove Data
```bash
docker-compose -f docker-compose.all.yml down -v
```

### View Running Containers
```bash
docker ps
```

## Troubleshooting

### Docker Not Running
- Start Docker Desktop
- Run the script again

### Container Won't Start
```bash
# Clean everything and restart
docker-compose -f docker-compose.all.yml down -v
.\start-all.bat
```

### Port Already in Use
```bash
# Find container using the port (example: port 8000)
netstat -ano | findstr :8000

# Kill the process
taskkill /PID <PID> /F

# Or use Docker to stop the conflicting container
docker-compose -f docker-compose.all.yml down
```

### Insufficient Disk Space
- Check Docker's disk usage: `docker system df`
- Clean up: `docker system prune -a`
- Run the script again

## Configuration

Edit these files to customize:

- **docker-compose.all.yml** - Service definitions and ports
- **example.env** - Environment variables (copy to .env)

## Notes

- First run may take 5-10 minutes while initializing the Frappe bench
- Subsequent runs are much faster
- All data is persistent in Docker volumes
- To reset everything: `docker-compose -f docker-compose.all.yml down -v`

