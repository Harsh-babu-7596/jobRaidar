$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $ProjectRoot "backend"
$VenvDir = Join-Path $BackendDir ".venv"
$Python = Join-Path $VenvDir "Scripts\python.exe"

Write-Host "== JobRadar Windows setup ==" -ForegroundColor Cyan

# Verify Python launcher
try {
    py --version
} catch {
    Write-Error "Python 3.11+ was not found. Install Python from https://www.python.org/downloads/windows/ and enable 'Add python.exe to PATH'."
    exit 1
}

if (-not (Test-Path $VenvDir)) {
    py -3 -m venv $VenvDir
}

& $Python -m pip install --upgrade pip
& $Python -m pip install -r (Join-Path $BackendDir "requirements.txt")

$EnvFile = Join-Path $BackendDir ".env"
$EnvExample = Join-Path $BackendDir ".env.example"
if (-not (Test-Path $EnvFile)) {
    Copy-Item $EnvExample $EnvFile
    Write-Host "Created backend\.env from .env.example"
}

New-Item -ItemType Directory -Force -Path (Join-Path $BackendDir "data") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $BackendDir "logs") | Out-Null

Write-Host ""
Write-Host "Setup complete. Start JobRadar with:" -ForegroundColor Green
Write-Host ".\scripts\start.ps1"
