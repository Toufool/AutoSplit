CALL "%~p0compile_resources.bat"
pyinstaller ^
  --windowed ^
  --onefile ^
  --additional-hooks-dir=Pyinstaller\hooks ^
  --icon=res\icon.ico ^
  --splash=res\splash.png ^
  "%~p0..\src\AutoSplit.py"
