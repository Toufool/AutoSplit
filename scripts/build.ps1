& "$PSScriptRoot/compile_resources.ps1"

pyinstaller `
  --windowed `
  --onefile `
  --additional-hooks-dir=Pyinstaller/hooks `
  --icon=res/icon.ico `
  "$PSScriptRoot/../src/AutoSplit.py"
