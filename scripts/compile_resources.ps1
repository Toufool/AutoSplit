#! /usr/bin/pwsh

$originalDirectory = $pwd
Set-Location "$PSScriptRoot/.."

New-Item ./src/gen -ItemType directory -Force | Out-Null
New-Item ./src/gen/__init__.py -ItemType File -Force | Out-Null
uv run --active pyside6-uic './res/about.ui' -o './src/gen/about.py'
uv run --active pyside6-uic './res/design.ui' -o './src/gen/design.py'
uv run --active pyside6-uic './res/settings.ui' -o './src/gen/settings.py'
uv run --active pyside6-uic './res/update_checker.ui' -o './src/gen/update_checker.py'
uv run --active pyside6-rcc './res/resources.qrc' -o './src/gen/resources_rc.py'
$files = Get-ChildItem ./src/gen/ *.py
foreach ($file in $files) {
    (Get-Content $file.PSPath) |
    ForEach-Object { $_.replace('import resources_rc', 'from . import resources_rc') } |
    ForEach-Object { $_ -replace 'def (\w+?)\(self, (\w+?)\):', 'def $1(self, $2: QWidget):' } |
    Set-Content $file.PSPath
}
Write-Host 'Generated code from .ui files'

$build_vars_path = "$PSScriptRoot/../src/gen/build_vars.py"
If ($Env:GITHUB_EXCLUDE_BUILD_NUMBER -eq $true
  # -or ($Env:GITHUB_EVENT_NAME -eq 'push' -and $Env:GITHUB_REF_NAME -eq 'main')
) {
  $BUILD_NUMBER = ''
}
Else {
  $BUILD_NUMBER = Get-Date -Format yyMMddHHmm
}
$GITHUB_REPOSITORY = $Env:GITHUB_HEAD_REPOSITORY
If (-not $GITHUB_REPOSITORY) {
  $repo_url = git config --get remote.origin.url
  # Validate in case the repo was downloaded rather than cloned
  If ($repo_url) {
    $GITHUB_REPOSITORY = $repo_url.substring(19, $repo_url.length - 19) -replace '\.git', ''
  }
}
If (-not $GITHUB_REPOSITORY) {
  $GITHUB_REPOSITORY = 'Toufool/AutoSplit'
}

New-Item $build_vars_path -ItemType File -Force | Out-Null
Add-Content $build_vars_path "AUTOSPLIT_BUILD_NUMBER = `"$BUILD_NUMBER`""
Add-Content $build_vars_path "AUTOSPLIT_GITHUB_REPOSITORY = `"$GITHUB_REPOSITORY`""
Write-Host "Generated build number: `"$BUILD_NUMBER`""
Write-Host "Set repository to `"$GITHUB_REPOSITORY`""

Set-Location $originalDirectory
