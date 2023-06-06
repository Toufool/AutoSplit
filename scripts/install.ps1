# Installing Python dependencies
$dev = If ($Env:GITHUB_JOB -eq 'Build') { '' } Else { '-dev' }
# Ensures installation tools are up to date. This also aliases pip to pip3 on MacOS.
python -m pip install wheel pip setuptools --upgrade
pip install -r "$PSScriptRoot/requirements$dev.txt" --upgrade

# Don't compile resources on the Build CI job as it'll do so in build script
If ($dev) {
  & "$PSScriptRoot/compile_resources.ps1"
}
