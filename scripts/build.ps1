& "$PSScriptRoot/compile_resources.ps1"

$arguments = @(
  "$PSScriptRoot/../src/AutoSplit.py",
  '--onefile',
  '--windowed',
  '--additional-hooks-dir=Pyinstaller/hooks',
  # Optional packages installed by PyAutoGUI
  '--exclude=pygetwindow',
  '--exclude=pymsgbox',
  '--exclude=pytweening',
  # Used by imagehash.whash
  '--exclude=pywt',
  '--icon=res/icon.ico',
  '--splash=res/splash.png')

Start-Process -Wait -NoNewWindow pyinstaller -ArgumentList $arguments
