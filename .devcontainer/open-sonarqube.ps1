# Auto-open SonarQube when ready
Write-Host "Waiting for SonarQube to start..." -ForegroundColor Yellow

$maxAttempts = 60
$attempt = 0
$sonarUrl = "http://localhost:9000"

while ($attempt -lt $maxAttempts) {
    try {
        $response = Invoke-WebRequest -Uri "$sonarUrl/api/system/status" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "SonarQube is ready!" -ForegroundColor Green
            Write-Host "Opening SonarQube at $sonarUrl" -ForegroundColor Cyan
            Start-Process $sonarUrl
            Write-Host ""
            Write-Host "Default credentials:" -ForegroundColor Yellow
            Write-Host "  Username: admin" -ForegroundColor White
            Write-Host "  Password: admin" -ForegroundColor White
            Write-Host ""
            exit 0
        }
    }
    catch {
        # SonarQube not ready yet
    }
    
    $attempt++
    Write-Host "." -NoNewline
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "Timeout waiting for SonarQube. Please check if containers are running." -ForegroundColor Red
Write-Host "Run 'docker ps' to verify containers are up." -ForegroundColor Yellow
