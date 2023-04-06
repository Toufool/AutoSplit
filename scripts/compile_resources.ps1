$originalDirectory = $pwd
Set-Location "$PSScriptRoot/.."

New-Item -Force -ItemType directory ./src/gen | Out-Null
pyside6-uic './res/about.ui' -o './src/gen/about.py'
pyside6-uic './res/design.ui' -o './src/gen/design.py'
pyside6-uic './res/settings.ui' -o './src/gen/settings.py'
pyside6-uic './res/update_checker.ui' -o './src/gen/update_checker.py'
pyside6-rcc './res/resources.qrc' -o './src/gen/resources_rc.py'
$files = Get-ChildItem ./src/gen/ *.py
foreach ($file in $files) {
    (Get-Content $file.PSPath) |
    ForEach-Object { $_ -replace 'import resources_rc', 'from . import resources_rc' } |
    Set-Content $file.PSPath
}
Write-Host 'Generated code from .ui files'

$build_vars_path = "$PSScriptRoot/../src/gen/build_vars.py"
$BUILD_NUMBER = If ($Env:GITHUB_EXCLUDE_BUILD_NUMBER -eq $true) { '' } Else { Get-Date -Format yyMMddHHmm }
$GITHUB_REPOSITORY = $Env:GITHUB_HEAD_REPOSITORY
If (-not $GITHUB_REPOSITORY) {
  $repo_url = git config --get remote.origin.url
  $GITHUB_REPOSITORY = $repo_url.substring(19, $repo_url.length - 19) -replace '\.git', ''
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
