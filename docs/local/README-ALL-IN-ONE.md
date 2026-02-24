# Frappe Docker All-in-One Setup

This directory contains scripts to run all Frappe Docker services in one command.

## Services Included

- **MariaDB** (port 3307) - Database for Frappe
- **Redis Cache** - Caching layer for Frappe
- **Redis Queue** - Queue management for Frappe
- **Frappe Bench** (ports 8000-8005, 9000-9005) - Main Frappe application
- **PostgreSQL** - Database for SonarQube
- **SonarQube** (port 9999) - Code quality and security scanner

## Quick Start

### Windows
```batch
start-all.bat
```

### Linux/Mac
```bash
chmod +x start-all.sh
./start-all.sh
```

### Direct Docker Command
```bash
docker-compose -f docker-compose.all.yml up -d
```

## Commands

### Start all services
```bash
docker-compose -f docker-compose.all.yml up -d
```

### Stop all services
```bash
docker-compose -f docker-compose.all.yml down
```

### Stop and remove all data (volumes)
```bash
docker-compose -f docker-compose.all.yml down -v
```

### View logs
```bash
# All services
docker-compose -f docker-compose.all.yml logs -f

# Specific service
docker-compose -f docker-compose.all.yml logs -f frappe
docker-compose -f docker-compose.all.yml logs -f sonarqube
docker-compose -f docker-compose.all.yml logs -f mariadb
```

### Restart a specific service
```bash
docker-compose -f docker-compose.all.yml restart frappe
docker-compose -f docker-compose.all.yml restart sonarqube
```

## Access URLs

- **Frappe/ERPNext**: http://localhost:8000
- **SonarQube**: http://localhost:9999
  - Default credentials: admin/admin (change on first login)
- **MariaDB**: localhost:3307
  - Root password: 123 (configurable via .env)

## Environment Variables

Create a `.env` file in this directory to customize:

```env
DB_PASSWORD=your_mariadb_password
```

## Network

All services run on a shared Docker network called `frappe-network`, allowing them to communicate with each other.

## Volumes

Data is persisted in Docker volumes:
- `mariadb-data` - MariaDB database files
- `sonarqube_data` - SonarQube data
- `sonarqube_extensions` - SonarQube plugins
- `sonarqube_logs` - SonarQube logs
- `sonarqube_postgresql` - PostgreSQL database files

## Troubleshooting

### Services won't start
1. Check if ports are already in use:
   ```bash
   netstat -ano | findstr :3307
   netstat -ano | findstr :9999
   ```

2. Check Docker logs:
   ```bash
   docker-compose -f docker-compose.all.yml logs
   ```

### Reset everything
```bash
docker-compose -f docker-compose.all.yml down -v
docker-compose -f docker-compose.all.yml up -d
```

### SonarQube connection issues
If SonarQube can't connect to the database, wait a minute for PostgreSQL to fully start, then restart SonarQube:
```bash
docker-compose -f docker-compose.all.yml restart sonarqube
```
