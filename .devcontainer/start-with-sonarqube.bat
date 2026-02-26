@echo off
echo ========================================
echo Starting Frappe Development Environment
echo ========================================
echo.

cd /d "%~dp0"

echo Starting Docker containers...
docker-compose up -d

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Failed to start containers
    pause
    exit /b 1
)

echo.
echo Containers started successfully!
echo.
echo Opening SonarQube...
powershell -ExecutionPolicy Bypass -File "%~dp0open-sonarqube.ps1"

echo.
echo ========================================
echo Environment Ready!
echo ========================================
echo.
echo Frappe:     http://localhost:8000
echo SonarQube:  http://localhost:9000
echo MariaDB:    localhost:3307
echo.
echo To stop: docker-compose down
echo.
pause
