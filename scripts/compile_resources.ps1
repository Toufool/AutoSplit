$originalDirectory = $pwd
Set-Location "$PSScriptRoot/.."

New-Item -Force -ItemType directory ./src/gen | Out-Null
pyuic6 './res/about.ui' -o './src/gen/about.py'
pyuic6 './res/design.ui' -o './src/gen/design.py'
pyuic6 './res/settings.ui' -o './src/gen/settings.py'
pyuic6 './res/update_checker.ui' -o './src/gen/update_checker.py'
pyside6-rcc './res/resources.qrc' -o './src/gen/resources_rc.py'
Write-Host 'Generated code from .ui files'

$build_vars_path = "$PSScriptRoot/../src/gen/build_vars.py"
$BUILD_NUMBER = If ($Env:GITHUB_EXCLUDE_BUILD_NUMBER -eq $true) { '' } Else { Get-Date -Format yyMMddHHmm }
$GITHUB_REPOSITORY = $Env:GITHUB_HEAD_REPOSITORY
If (-not $GITHUB_REPOSITORY) {
  $repo_url = git config --get remote.origin.url
  $GITHUB_REPOSITORY = $repo_url.substring(19, $repo_url.length - 19) -replace '\.git', ''
}
If (-not $GITHUB_REPOSITORY) {
  $GITHUB_REPOSITORY = 'Toufool/Auto-Split'
}

New-Item $build_vars_path -ItemType File -Force | Out-Null
Add-Content $build_vars_path "AUTOSPLIT_BUILD_NUMBER = `"$BUILD_NUMBER`""
Add-Content $build_vars_path "AUTOSPLIT_GITHUB_REPOSITORY = `"$GITHUB_REPOSITORY`""
Write-Host "Generated build number: `"$BUILD_NUMBER`""
Write-Host "Set repository to `"$GITHUB_REPOSITORY`""

Set-Location $originalDirectory
