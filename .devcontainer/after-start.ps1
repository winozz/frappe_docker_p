<# after-start.ps1
Runs the full post-start routine:
- docker compose up
- bench restart
- bench start (detached)
- ensure HRIS importable
- optional: one-time HRIS install
- optional: rebuild assets
- optional: run status updater
#>

param(
    [switch]$InstallHRIS,    # run once per fresh bench
    [switch]$RebuildAssets,  # run after frontend/HRIS changes
    [switch]$RunUpdater      # run update_accounting_entry_statuses.py at the end
)

$ErrorActionPreference = 'Stop'

$repoRoot   = "C:\Users\user\Documents\Test Env\frappe_docker"
$devcDir    = Join-Path $repoRoot ".devcontainer"
$composeYml = Join-Path $devcDir "docker-compose.cvsu-ais.yml"

function Exec([string]$cmd) {
    Write-Host ">> $cmd" -ForegroundColor Cyan
    cmd /c $cmd | Write-Host
}

# 1) Bring the stack up
Push-Location $devcDir
Exec "docker compose -f `"$composeYml`" up -d"
Pop-Location

# wait for DB + Redis healthy (90s max)
$targets = @("cvsu_ais_mariadb","cvsu_ais_redis_cache","cvsu_ais_redis_queue")
$deadline = (Get-Date).AddSeconds(90)
do {
    $statuses = docker ps --format "{{.Names}} {{.Status}}" | Where-Object { $_ -match "cvsu_ais" }
    $healthy = $targets | Where-Object { $statuses -match "$_ .*healthy" }
    if ($healthy.Count -eq $targets.Count) { break }
    Start-Sleep 3
} while ((Get-Date) -lt $deadline)
Write-Host "Healthy: $($healthy -join ', ')" -ForegroundColor Green

# common bench prefix
$benchPrefix = @"
export PATH=/home/frappe/.local/bin:/home/frappe/.nvm/versions/node/v24.13.0/bin:/usr/bin:/bin:$PATH
export GIT_PYTHON_GIT_EXECUTABLE=/usr/bin/git
cd /workspace/development/frappe-bench
"@

# 2) Bench restart
Exec "docker exec -i cvsu_ais_frappe bash -lc `"$benchPrefix bench restart`""

# 2b) Bench start (detached so script can finish)
Exec "docker exec -d cvsu_ais_frappe bash -lc `"$benchPrefix bench start > /tmp/bench-start.log 2>&1 &`""

# 2c) Quick status peek (tail last 30 lines of bench start log)
Exec "docker exec cvsu_ais_frappe bash -lc `\"tail -n 30 /tmp/bench-start.log`\""

# 2d) Verify bench start process presence
Exec "docker exec cvsu_ais_frappe bash -lc `\"ps -ef | grep 'bench start' | grep -v grep`\""

# 2e) Supervisor status (if available)
Exec "docker exec cvsu_ais_frappe bash -lc `\"supervisorctl status`\""

# 2f) List frappe-related Python processes
Exec "docker exec cvsu_ais_frappe bash -lc `\"pgrep -af 'python.*frappe'`\""

# 3) Ensure HRIS importable
Exec "docker exec -i cvsu_ais_frappe bash -lc `"$benchPrefix env/bin/pip install -e apps/cvsu_hris`""

# One-time HRIS install (if requested)
