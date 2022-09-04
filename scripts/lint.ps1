$originalDirectory = $pwd
Set-Location "$PSScriptRoot/.."
$exitCodes = 0

Write-Host "`nRunning Pyright..."
$Env:PYRIGHT_PYTHON_FORCE_VERSION = 'latest'
pyright --warnings
$exitCodes += $LastExitCode
if ($LastExitCode -gt 0) {
  Write-Host "`Pyright failed ($LastExitCode)" -ForegroundColor Red
}
else {
  Write-Host "`Pyright passed" -ForegroundColor Green
}

Write-Host "`nRunning Pylint..."
pylint --output-format=colorized src/
$exitCodes += $LastExitCode
if ($LastExitCode -gt 0) {
  Write-Host "`Pylint failed ($LastExitCode)" -ForegroundColor Red
}
else {
  Write-Host "`Pylint passed" -ForegroundColor Green
}

Write-Host "`nRunning Flake8..."
flake8
$exitCodes += $LastExitCode
if ($LastExitCode -gt 0) {
  Write-Host "`Flake8 failed ($LastExitCode)" -ForegroundColor Red
}
else {
  Write-Host "`Flake8 passed" -ForegroundColor Green
}

Write-Host "`nRunning Bandit..."
bandit -f custom --silent --recursive src
# $exitCodes += $LastExitCode # Returns 1 on low
if ($LastExitCode -gt 0) {
  Write-Host "`Bandit warning ($LastExitCode)" -ForegroundColor Yellow
}
else {
  Write-Host "`Bandit passed" -ForegroundColor Green
}


if ($exitCodes -gt 0) {
  Write-Host "`nLinting failed ($exitCodes)" -ForegroundColor Red
}
else {
  Write-Host "`nLinting passed" -ForegroundColor Green
}

Set-Location $originalDirectory
