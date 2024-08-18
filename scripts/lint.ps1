$originalDirectory = $pwd
Set-Location "$PSScriptRoot/.."
$exitCodes = 0

Write-Host "`nRunning formatting..."
ruff format .
add-trailing-comma $(git ls-files '**.py*')

Write-Host "`nRunning Ruff ..."
ruff check . --fix
$exitCodes += $LastExitCode
if ($LastExitCode -gt 0) {
  Write-Host "`Ruff failed ($LastExitCode)" -ForegroundColor Red
}
else {
  Write-Host "`Ruff passed" -ForegroundColor Green
}

$pyrightVersion = 'latest' # Change this if latest has issues
Write-Host "`nRunning Pyright $pyrightVersion ..."
$Env:PYRIGHT_PYTHON_FORCE_VERSION = $pyrightVersion
npx -y pyright@$pyrightVersion src/
$exitCodes += $LastExitCode
if ($LastExitCode -gt 0) {
  Write-Host "`Pyright failed ($LastExitCode)" -ForegroundColor Red
  if ($pyrightVersion -eq 'latest') {
    npx pyright@latest --version
  }
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
