# DECEPTRON BACKEND - BUILD SCRIPT
# This script bundles the FastAPI backend into a single EXE.
# Usage: .\build_backend.ps1

Write-Host "--- Starting Deceptron Backend Build ---" -ForegroundColor Cyan

# 0. Kill existing process if running
Write-Host "[*] Ensuring no existing backend process is running..." -ForegroundColor Cyan
Stop-Process -Name "deceptron_backend" -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# 1. Configuration
Write-Host "[*] Using virtual environment: .\myenv" -ForegroundColor Cyan
$pythonExe = ".\myenv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "[ERROR] Virtual environment not found at .\myenv. Please ensure it exists." -ForegroundColor Red
    exit 1
}

# Ensure PyInstaller is in venv
Write-Host "[*] Checking PyInstaller..." -ForegroundColor Cyan
& $pythonExe -m pip install pyinstaller -q

if (-not (Test-Path ".env")) {
    Write-Host "[!] Error: .env file not found. Please create it first." -ForegroundColor Red
    exit 1
}

# 2. Build Command
# --onefile: Bundle everything into one EXE
# --add-data ".env;.": Embed the .env file in the root of the EXE bundle
# --add-data "modules;modules": Bundle all internal logic modules
# --hidden-import: Ensure dynamic imports are captured
# --name: Resulting file name

$cmd = "& `"$pythonExe`" -m PyInstaller --onefile " + `
       "--collect-all torch " + `
       "--collect-all hsemotion " + `
       "--collect-all mediapipe " + `
       "--collect-all pyannote.audio " + `
       "--collect-all pytorch_lightning " + `
       "--collect-all lightning_fabric " + `
       "--collect-all lightning " + `
       "--copy-metadata torch " + `
       "--add-data '.env;.' " + `
       "--add-data 'modules;modules' " + `
       "--add-data 'api;api' " + `
       "--add-data 'myenv/local_models;myenv/local_models' " + `
       "--hidden-import 'torch' " + `
       "--hidden-import 'hsemotion' " + `
       "--hidden-import 'pyannote.audio' " + `
       "--hidden-import 'whisper' " + `
       "--hidden-import 'fastapi' " + `
       "--hidden-import 'groq' " + `
       "--hidden-import 'dotenv' " + `
       "--hidden-import 'uvicorn.logging' " + `
       "--hidden-import 'mediapipe' " + `
       "--hidden-import 'parselmouth' " + `
       "--hidden-import 'soundfile' " + `
       "--hidden-import 'uvicorn.loops' " + `
       "--hidden-import 'uvicorn.loops.auto' " + `
       "--hidden-import 'uvicorn.protocols' " + `
       "--hidden-import 'uvicorn.protocols.http' " + `
       "--hidden-import 'uvicorn.protocols.http.auto' " + `
       "--hidden-import 'uvicorn.protocols.websockets' " + `
       "--hidden-import 'uvicorn.protocols.websockets.auto' " + `
       "--hidden-import 'uvicorn.lifespan' " + `
       "--hidden-import 'uvicorn.lifespan.on' " + `
       "--name deceptron_backend " + `
       "server.py"

Write-Host "[*] Executing: $cmd" -ForegroundColor Gray
Invoke-Expression $cmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[SUCCESS] Build Successful! Check the 'dist' folder for deceptron_backend.exe" -ForegroundColor Green
} else {
    Write-Host "`n[ERROR] Build Failed." -ForegroundColor Red
}
