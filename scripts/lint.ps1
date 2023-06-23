$originalDirectory = $pwd
Set-Location "$PSScriptRoot/.."
$exitCodes = 0

Write-Host "`nRunning formatting..."
autopep8 src/ --recursive --in-place
add-trailing-comma $(git ls-files '**.py*')

Write-Host "`nRunning Ruff..."
ruff check . --fix
$exitCodes += $LastExitCode
if ($LastExitCode -gt 0) {
  Write-Host "`Ruff failed ($LastExitCode)" -ForegroundColor Red
}
else {
  Write-Host "`Ruff passed" -ForegroundColor Green
}

Write-Host "`nRunning Pyright..."
$Env:PYRIGHT_PYTHON_FORCE_VERSION = 'latest'
npx pyright@latest src/
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
