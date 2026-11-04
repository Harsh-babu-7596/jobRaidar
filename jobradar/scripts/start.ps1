$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $ProjectRoot "backend"
$Python = Join-Path $BackendDir ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Error "Virtual environment not found. Run .\scripts\setup.ps1 first."
    exit 1
}

Set-Location $BackendDir
Write-Host "Starting JobRadar API at http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Swagger docs: http://127.0.0.1:8000/docs"
Write-Host "Press Ctrl+C to stop the server."
& $Python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
