$originalDirectory = $pwd
Set-Location "$PSScriptRoot/.."

New-Item -Force -ItemType directory ./src/gen | Out-Null
pyuic6 './res/about.ui' -o './src/gen/about.py'
pyuic6 './res/design.ui' -o './src/gen/design.py'
pyuic6 './res/settings.ui' -o './src/gen/settings.py'
pyuic6 './res/update_checker.ui' -o './src/gen/update_checker.py'
pyside6-rcc './res/resources.qrc' -o './src/gen/resources_rc.py'
Write-Host 'Generated code from .ui files'

$BUILD_NUMBER = Get-Date -Format yyMMddHHMM
New-Item "$PSScriptRoot/../src/gen/build_number.py" -ItemType File -Force -Value "AUTOSPLIT_BUILD_NUMBER = `"$BUILD_NUMBER`"" | Out-Null
Write-Host "Generated build number: `"$BUILD_NUMBER`""

Set-Location $originalDirectory
