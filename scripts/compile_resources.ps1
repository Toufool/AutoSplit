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
$versionBumped = $Env:GITHUB_EVENT_NAME -eq 'push' `
  -and (git rev-parse --verify HEAD^ 2>$null) `
  -and (git diff HEAD^ HEAD -- "$PSScriptRoot/../pyproject.toml" | Select-String '^\+version\s*=')

if ($Env:GITHUB_EXCLUDE_BUILD_NUMBER -eq $true -or $versionBumped) {
  $BUILD_NUMBER = ''
}
else {
  $BUILD_NUMBER = Get-Date -Format yyMMddHHmm
}
$GITHUB_REPOSITORY = $Env:GITHUB_HEAD_REPOSITORY
if (-not $GITHUB_REPOSITORY) {
  $repo_url = git config --get remote.origin.url
  # Validate in case the repo was downloaded rather than cloned
  if ($repo_url) {
    $GITHUB_REPOSITORY = $repo_url.substring(19, $repo_url.length - 19) -replace '\.git', ''
  }
}
if (-not $GITHUB_REPOSITORY) {
  $GITHUB_REPOSITORY = 'Toufool/AutoSplit'
}

# Our own top-level modules and packages, used by AutoSplit.py's lazy imports
# filter (Python 3.15+). Generated because PyInstaller-frozen builds can't
# discover pure modules on disk: they live inside the PYZ archive.
$SRC_ROOT_MODULES = (
  @('"__main__"') + (
    Get-ChildItem ./src |
      Where-Object { ($_.Extension -eq '.py' -or $_.PSIsContainer) -and $_.Name -notlike '__*' } |
      ForEach-Object { "`"$($_.BaseName)`"" }
  )
) -join ', '

New-Item $build_vars_path -ItemType File -Force | Out-Null
Add-Content $build_vars_path "AUTOSPLIT_BUILD_NUMBER = `"$BUILD_NUMBER`""
Add-Content $build_vars_path "AUTOSPLIT_GITHUB_REPOSITORY = `"$GITHUB_REPOSITORY`""
Add-Content $build_vars_path "SRC_ROOT_MODULES = frozenset(($SRC_ROOT_MODULES))"
Write-Host "Generated build number: `"$BUILD_NUMBER`""
Write-Host "Set repository to `"$GITHUB_REPOSITORY`""

Set-Location $originalDirectory
