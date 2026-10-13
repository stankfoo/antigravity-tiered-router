<#
.SYNOPSIS
    Executa a suíte de testes unitários do MCP e a simulação de benchmark.
#>

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Executando Validações: Antigravity Tiered Router" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

Set-Location $projectRoot

Write-Host "`n[1/2] Rodando Testes Unitários e Integração MCP..." -ForegroundColor Yellow
python tests/test_router.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FALHA] Testes unitários falharam com código $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}
Write-Host "[OK] Todos os testes unitários passaram!" -ForegroundColor Green

Write-Host "`n[2/2] Rodando Bateria de Benchmark..." -ForegroundColor Yellow
python benchmarks/run_benchmark.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FALHA] Benchmark falhou com código $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}
Write-Host "[OK] Benchmark concluído com sucesso!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
