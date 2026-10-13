<#
.SYNOPSIS
    Configures and validates local Ollama and the official Kev-0.8B decision model for Antigravity Tiered Router.
.DESCRIPTION
    Checks if Ollama is installed and running, starts Ollama if needed,
    creates the official Kev decision model, and verifies connectivity.
#>

param(
    [switch]$TestOnly = $false
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Antigravity Tiered Router - Local Kev Setup and Diagnostic" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Check Ollama executable
$ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollamaCmd) {
    Write-Host "[!] Ollama not found in PATH." -ForegroundColor Yellow
    $altPath = "C:\Users\$env:USERNAME\AppData\Local\Programs\Ollama\ollama.exe"
    if (Test-Path $altPath) {
        Write-Host "[OK] Found Ollama at $altPath" -ForegroundColor Green
        $env:Path += ";C:\Users\$env:USERNAME\AppData\Local\Programs\Ollama"
    } else {
        Write-Host "[ERROR] Ollama is not installed. The router will continue running safely with the built-in local heuristic engine." -ForegroundColor Red
        return
    }
} else {
    Write-Host "[OK] Ollama found: $($ollamaCmd.Source)" -ForegroundColor Green
}

# 2. Check if Ollama service is listening
$ollamaUrl = "http://127.0.0.1:11434"
$isRunning = $false
try {
    $resp = Invoke-RestMethod -Uri "$ollamaUrl/api/tags" -Method Get -TimeoutSec 2 -ErrorAction Stop
    $isRunning = $true
    Write-Host "[OK] Ollama is running and responding at $ollamaUrl" -ForegroundColor Green
} catch {
    Write-Host "[INFO] Ollama service is not currently running." -ForegroundColor Yellow
}

if (-not $isRunning -and -not $TestOnly) {
    Write-Host "[*] Starting Ollama in the background..." -ForegroundColor Cyan
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 3

    try {
        $resp = Invoke-RestMethod -Uri "$ollamaUrl/api/tags" -Method Get -TimeoutSec 3 -ErrorAction Stop
        $isRunning = $true
        Write-Host "[OK] Ollama started successfully!" -ForegroundColor Green
    } catch {
        Write-Host "[WARN] Could not connect to newly started Ollama. Heuristic fallback will be used." -ForegroundColor Yellow
    }
}

# 3. Check for Kev model
if ($isRunning) {
    $models = (ollama list 2>&1)
    $hasKev = $models -match "kev"

    if ($hasKev) {
        Write-Host "[OK] Model 'kev' is already installed and available in Ollama!" -ForegroundColor Green
    } elseif (-not $TestOnly) {
        Write-Host "[*] Setting up official Kev-0.8B decision model..." -ForegroundColor Cyan
        $modelDir = Join-Path $PSScriptRoot "..\models"
        $ggufPath = Join-Path $modelDir "Kev-0.8B-Q8_0.gguf"
        if (-not (Test-Path $ggufPath)) {
            Write-Host "[*] Downloading Kev-0.8B-Q8_0.gguf (~774 MB) from Hugging Face..." -ForegroundColor Cyan
            New-Item -ItemType Directory -Force -Path $modelDir | Out-Null
            $url = "https://huggingface.co/ggml-org/Kev-0.8B-GGUF/resolve/main/Kev-0.8B-Q8_0.gguf"
            Invoke-WebRequest -Uri $url -OutFile $ggufPath
        }
        $modelfile = Join-Path $PSScriptRoot "..\Modelfile"
        ollama create kev -f $modelfile
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Official model 'kev' created and ready!" -ForegroundColor Green
        } else {
            Write-Host "[WARN] Ollama create returned code $LASTEXITCODE. Router will seamlessly use local heuristic engine." -ForegroundColor Yellow
        }
    } else {
        Write-Host "[INFO] Model 'kev' not currently pulled in Ollama." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Diagnostic Summary:" -ForegroundColor Cyan
Write-Host " - Ollama Running: $isRunning"
Write-Host " - Tiered Router MCP Fallback: Always active and ready (0ms latency, zero tokens)"
Write-Host "==========================================================" -ForegroundColor Cyan
