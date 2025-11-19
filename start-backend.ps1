# Start the Nutritional Insights Backend Server .\start-backend.ps1
Write-Host "Starting Nutritional Insights Backend API..." -ForegroundColor Green

# Load environment variables from .env at repo root if present
$envFile = Join-Path $PSScriptRoot ".env"
if (Test-Path $envFile) {
    Write-Host "Loading environment from .env..." -ForegroundColor Cyan
    Get-Content $envFile | ForEach-Object {
        $line = $_.Trim()
        if (-not $line) { return }
        if ($line.StartsWith('#')) { return }
        if ($line -match '^\s*([^=]+)\s*=\s*(.*)\s*$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            # Strip surrounding quotes if provided
            if ($value.StartsWith('"') -and $value.EndsWith('"')) {
                $value = $value.Trim('"')
            }
            Set-Item -Path "Env:$name" -Value $value
        }
    }
}

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Cyan
} catch {
    Write-Host "Error: Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

# Navigate to backend directory
$backendPath = Join-Path $PSScriptRoot "backend"
if (-Not (Test-Path $backendPath)) {
    Write-Host "Error: Backend directory not found at $backendPath" -ForegroundColor Red
    exit 1
}

Set-Location $backendPath

# Check if requirements are installed
Write-Host "`nChecking dependencies..." -ForegroundColor Yellow
$requirementsFile = Join-Path $backendPath "requirements.txt"

if (Test-Path $requirementsFile) {
    Write-Host "Installing/updating dependencies from requirements.txt..." -ForegroundColor Yellow
    python -m pip install -r requirements.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Dependencies installed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Warning: Some dependencies may not have installed correctly." -ForegroundColor Yellow
    }
}

# Start the Flask server
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Starting Flask API Server..." -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
Write-Host "Server will be available at: http://localhost:5000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server`n" -ForegroundColor Yellow

# Prefer PORT/HOST if provided via .env/env, else defaults are handled in app.py
python app.py
