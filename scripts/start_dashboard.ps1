<#
.SYNOPSIS
    Inicia o Dashboard de Telemetria e Benchmark do Antigravity Tiered Router.
.DESCRIPTION
    Inicia um servidor HTTP local leve em Python na porta 8085 e abre o navegador padrão.
#>

param(
    [int]$Port = 8085
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$dashboardDir = Join-Path $projectRoot "dashboard"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Iniciando Dashboard do Antigravity Tiered Router" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "[*] Pasta do Dashboard: $dashboardDir"
Write-Host "[*] Porta: $Port"

# Check if Python is available
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "[!] Python não encontrado no PATH. Abrindo index.html diretamente..." -ForegroundColor Yellow
    Start-Process (Join-Path $dashboardDir "index.html")
    exit 0
}

Write-Host "[*] Iniciando servidor HTTP local em background..." -ForegroundColor Green
$serverJob = Start-Job -ScriptBlock {
    param($dir, $p)
    Set-Location $dir
    python -m http.server $p
} -ArgumentList $dashboardDir, $Port

Start-Sleep -Seconds 1
$url = "http://localhost:$Port"
Write-Host "[OK] Servidor ativo em $url" -ForegroundColor Green
Write-Host "[*] Abrindo navegador..." -ForegroundColor Cyan
Start-Process $url

Write-Host ""
Write-Host "Pressione Ctrl+C para encerrar o servidor HTTP a qualquer momento." -ForegroundColor Yellow
try {
    while ($true) {
        Start-Sleep -Seconds 2
    }
} finally {
    Stop-Job $serverJob -ErrorAction SilentlyContinue
    Remove-Job $serverJob -ErrorAction SilentlyContinue
    Write-Host "`nServidor encerrado com sucesso." -ForegroundColor Gray
}
