# Alias python3 to python on Windows
If ($IsWindows) {
  $python = (Get-Command python).Source
  $python3 = "$((Get-Item $python).Directory.FullName)/python3.exe"
  New-Item -ItemType SymbolicLink -Path $python3 -Target $python -ErrorAction SilentlyContinue
}

# Installing Python dependencies
$dev = If ($Env:GITHUB_JOB -eq 'Build') { '' } Else { '-dev' }
# Ensures installation tools are up to date. This also aliases pip to pip3 on MacOS.
python3 -m pip install wheel pip setuptools --upgrade
pip install -r "$PSScriptRoot/requirements$dev.txt" --upgrade
# Don't install pyright on CI. We use an action
if (-not $Env:CI -and (Get-Command 'npm' -ErrorAction SilentlyContinue)) {
  npm i --global pyright@latest
}

# Don't compile resources on the Build CI job as it'll do so in build script
If ($dev) {
  & "$PSScriptRoot/compile_resources.ps1"
}
