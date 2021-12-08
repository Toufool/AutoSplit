$originalDirectory = $pwd
cd "$PSScriptRoot\.."
Write-Host $Script:MyInvocation.MyCommand.Path
$exitCodes = 0

Write-Host "`nRunning Pyright..."
pyright --warnings
$exitCodes += $LastExitCode

Write-Host "`nRunning Pylint..."
pylint --score=n --output-format=colorized $(git ls-files '**/*.py*')
$exitCodes += $LastExitCode

Write-Host "`nRunning Flake8..."
flake8
$exitCodes += $LastExitCode

Write-Host "`nRunning Bandit..."
bandit -f custom --silent --recursive src
# $exitCodes += $LastExitCode # Returns 1 on low

if ($exitCodes -gt 0) {
  Write-Host "`nLinting failed ($exitCodes)" -ForegroundColor Red
} else {
  Write-Host "`nLinting passed" -ForegroundColor Green
}

cd $originalDirectory
