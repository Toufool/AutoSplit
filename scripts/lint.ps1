#! /usr/bin/pwsh

$originalDirectory = $pwd
Set-Location "$PSScriptRoot/.."
$exitCodes = 0

Write-Host "`nRunning dprint fmt ..."
uv run --active dprint fmt

Write-Host "`nRunning Ruff check ..."
uv run --active ruff check --fix
$exitCodes += $LastExitCode
if ($LastExitCode -gt 0) {
  Write-Host "`Ruff failed ($LastExitCode)" -ForegroundColor Red
}
else {
  Write-Host "`Ruff passed" -ForegroundColor Green
}

Write-Host "`nRunning Ruff format ..."
uv run --active ruff format

$pyrightVersion = $(uv run --active pyright --version).replace('pyright ', '')
Write-Host "`nRunning Pyright $pyrightVersion ..."
$Env:PYRIGHT_PYTHON_FORCE_VERSION = $pyrightVersion
uv run --active pyright src/
$exitCodes += $LastExitCode
if ($LastExitCode -gt 0) {
  Write-Host "`Pyright failed ($LastExitCode)" -ForegroundColor Red
}
else {
  Write-Host "`Pyright passed" -ForegroundColor Green
}

if ($exitCodes -gt 0) {
  Write-Host "`nLinting failed ($exitCodes)" -ForegroundColor Red
}
else {
  Write-Host "`nLinting passed" -ForegroundColor Green
}

Set-Location $originalDirectory
