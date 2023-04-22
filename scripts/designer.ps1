$qt6_applications_import = 'import qt6_applications; print(qt6_applications.__path__[0])'
$qt6_applications_path = python -c $qt6_applications_import
if ($null -eq $qt6_applications_path) {
  Write-Host 'Designer not found, installing qt6_applications'
  python -m pip install qt6_applications
}
$qt6_applications_path = python -c $qt6_applications_import
& "$qt6_applications_path/Qt/bin/designer" `
  "$PSScriptRoot/../res/design.ui" `
  "$PSScriptRoot/../res/about.ui" `
  "$PSScriptRoot/../res/settings.ui" `
  "$PSScriptRoot/../res/update_checker.ui"
