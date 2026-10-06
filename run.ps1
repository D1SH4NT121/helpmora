$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:HELPMORA_JWT_SECRET = "helpmora_local_secret_key_1234567890123456"

$VENV_PYTHON = Join-Path $PSScriptRoot ".venv312\Scripts\python.exe"
$HELPMORA_DIR = Join-Path $PSScriptRoot "helpmora"

if (-not (Test-Path $VENV_PYTHON)) {
    Write-Error "Virtual environment not found at .venv312"
    exit 1
}

Push-Location $HELPMORA_DIR
try {
    Write-Host "Starting HELPmora at http://localhost:8000 ..." -ForegroundColor Cyan
    & $VENV_PYTHON -m jaclang start app.jac --no-dev --port 8000 --host 127.0.0.1
} finally {
    Pop-Location
}
