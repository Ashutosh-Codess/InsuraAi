param (
    [switch]$InstallDeps = $false
)

$ErrorActionPreference = "Stop"

Write-Host "Starting InsuraMind AI Backend natively..." -ForegroundColor Cyan

# 1. Check for Virtual Environment
if (!(Test-Path "backend\.venv")) {
    Write-Host "Virtual environment not found. Creating one at backend\.venv..." -ForegroundColor Yellow
    python -m venv backend\.venv
    $InstallDeps = $true
}

# 2. Activate the Virtual Environment
Write-Host "Activating virtual environment..."
& "backend\.venv\Scripts\Activate.ps1"

# 3. Install dependencies if needed
if ($InstallDeps) {
    Write-Host "Installing backend requirements..." -ForegroundColor Yellow
    pip install -r backend\requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install dependencies."
        exit 1
    }
}

# 4. Set Python Path so backend can see the root directories (agents, guardrails, etc)
$env:PYTHONPATH = (Get-Item .).FullName

# 5. Set Ollama Base URL if it's running natively
if ([string]::IsNullOrEmpty($env:OLLAMA_BASE_URL)) {
    $env:OLLAMA_BASE_URL = "http://127.0.0.1:11434"
}

# 6. Start quickly for portal login. AI components load only when explicitly
# requested, so an unavailable model service cannot prevent authentication.
if ([string]::IsNullOrEmpty($env:INSURAMIND_SKIP_AI_STARTUP)) {
    $env:INSURAMIND_SKIP_AI_STARTUP = "1"
}

# 7. Run the server
Write-Host "Starting FastAPI server..." -ForegroundColor Green
Set-Location backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
