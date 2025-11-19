# One-command dev helper
# - Loads .env
# - Starts backend if not already running on HOST:PORT
# - Waits for health
# - Opens the UI in the default browser

$ErrorActionPreference = 'Stop'

$root = $PSScriptRoot
$envFile = Join-Path $root ".env"

function Load-DotEnv($path) {
    if (-not (Test-Path $path)) { return }
    Write-Host "Loading environment from .env..." -ForegroundColor Cyan
    Get-Content $path | ForEach-Object {
        $line = $_.Trim()
        if (-not $line) { return }
        if ($line.StartsWith('#')) { return }
        if ($line -match '^\s*([^=]+)\s*=\s*(.*)\s*$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            if ($value.StartsWith('"') -and $value.EndsWith('"')) { $value = $value.Trim('"') }
            Set-Item -Path "Env:$name" -Value $value
        }
    }
}

Load-DotEnv $envFile

# Defaults if env not set
$bindHost = if ($env:HOST) { $env:HOST } else { '127.0.0.1' }
$port = if ($env:PORT) { [int]$env:PORT } else { 5000 }

# If backend isn't running, start it in a new window
$healthUrl = "http://${bindHost}:${port}/api/health"

function Test-Health($url) {
    try {
        $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 3
        return $r.StatusCode -eq 200
    } catch { return $false }
}

function Test-Port($hostName, $portNumber) {
    try {
        $res = Test-NetConnection -ComputerName $hostName -Port $portNumber -WarningAction SilentlyContinue
        return $res.TcpTestSucceeded
    } catch { return $false }
}

if (-not (Test-Health $healthUrl)) {
    Write-Host "Starting backend..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $root "start-backend.ps1")
}

Write-Host "Waiting for port ${bindHost}:${port} to be available..." -ForegroundColor Yellow
$portDeadline = (Get-Date).AddSeconds(45)
while ((Get-Date) -lt $portDeadline) {
    if (Test-Port $bindHost $port) { break }
    Start-Sleep -Seconds 1
}

if (-not (Test-Port $bindHost $port)) {
    Write-Host "Backend port ${bindHost}:${port} did not open in time" -ForegroundColor Yellow
    Write-Host "Proceeding to open the UI anyway..." -ForegroundColor Yellow
}

Write-Host "Port is open; checking HTTP health at $healthUrl..." -ForegroundColor Yellow
$healthDeadline = (Get-Date).AddSeconds(20)
while ((Get-Date) -lt $healthDeadline) {
    if (Test-Health $healthUrl) { break }
    Start-Sleep -Seconds 1
}

if (-not (Test-Health $healthUrl)) {
    Write-Host "Backend port open, but health check failed at $healthUrl" -ForegroundColor Yellow
    # Do not fail hard; continue to open UI since other endpoints may be OK
}

Write-Host "Backend is healthy at $healthUrl" -ForegroundColor Green

# Open the UI
$uiPath = Join-Path $root "project2ui.html"
if (Test-Path $uiPath) {
    Start-Process $uiPath
    Write-Host "Opened UI: $uiPath" -ForegroundColor Cyan
} else {
    Write-Host "UI file not found: $uiPath" -ForegroundColor Yellow
}
