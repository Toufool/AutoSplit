$originalDirectory = $pwd
Set-Location "$PSScriptRoot/.."
$exitCodes = 0

Write-Host "`nRunning Ruff check ..."
uv run ruff check --fix
$exitCodes += $LastExitCode
if ($LastExitCode -gt 0) {
  Write-Host "`Ruff failed ($LastExitCode)" -ForegroundColor Red
}
else {
  Write-Host "`Ruff passed" -ForegroundColor Green
}

Write-Host "`nRunning Ruff format ..."
uv run ruff format

$pyrightVersion = $(uv run pyright --version).replace('pyright ', '')
Write-Host "`nRunning Pyright $pyrightVersion ..."
$Env:PYRIGHT_PYTHON_FORCE_VERSION = $pyrightVersion
uv run pyright src/
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
