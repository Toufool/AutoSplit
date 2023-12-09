& "$PSScriptRoot/compile_resources.ps1"

$arguments = @(
  "$PSScriptRoot/../src/AutoSplit.py",
  '--onefile',
  '--windowed',
  '--additional-hooks-dir=Pyinstaller/hooks',
  '--icon=res/icon.ico',
  '--splash=res/splash.png',
  # The install script should ensure that these are not installed
  # But we'll still include unused dependencies that would be picked up by PyInstaller
  # if requirements.txt was used directly to help ensure consistency when building locally.
  #
  # Installed by PyAutoGUI
  '--exclude=pyscreeze',
  '--exclude=pygetwindow',
  '--exclude=pymsgbox',
  '--exclude=pytweening',
  '--exclude=mouseinfo',
  # Used by imagehash.whash
  '--exclude=pywt')

Start-Process -Wait -NoNewWindow pyinstaller -ArgumentList $arguments
