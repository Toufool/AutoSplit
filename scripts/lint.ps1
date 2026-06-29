#! /usr/bin/pwsh

$originalDirectory = $pwd
Set-Location "$PSScriptRoot/.."
$exitCodes = 0

Write-Host "`nRunning dprint fmt ..."
uv run --active dprint fmt

Write-Host "`nRunning Ruff check ..."
uv run --active ruff check --fix
$exitCodes += $LastExitCode
# Ruff already prints success/failure

Write-Host "`nRunning Ruff format ..."
uv run --active ruff format

# Skip pyright-python's update check, avoiding the npm query (faster, offline-safe) and its warning.
$Env:PYRIGHT_PYTHON_IGNORE_WARNINGS = $true
$pyrightVersion = $(uv run --active pyright --version).replace('pyright ', '')
Write-Host "`nRunning Pyright $pyrightVersion ..."
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
