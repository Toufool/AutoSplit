& "$PSScriptRoot/compile_resources.ps1"

$arguments = @(
  '--onefile',
  '--windowed',
  '--additional-hooks-dir=Pyinstaller/hooks',
  '--icon=res/icon.ico',
  '--splash=res/splash.png')

Start-Process pyinstaller -Wait -ArgumentList "$arguments `"$PSScriptRoot/../src/AutoSplit.py`""
