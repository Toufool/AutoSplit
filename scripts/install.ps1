If ($IsLinux) {
  sudo apt-get install python3-tk
}

python -m pip install wheel --upgrade
python -m pip install -r "$PSScriptRoot/requirements-dev.txt"
& "$PSScriptRoot/compile_resources.ps1"
npm install -g pyright@latest
npm list -g pyright
