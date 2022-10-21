& "$PSScriptRoot/compile_resources.ps1"
pyinstaller `
  --onefile `
  --windowed `
  --additional-hooks-dir=Pyinstaller/hooks `
  --icon=res/icon.ico `
  --splash=res/splash.png `
  "$PSScriptRoot/../src/AutoSplit.py"
