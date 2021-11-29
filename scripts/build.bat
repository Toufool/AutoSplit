CALL "%~p0compile_resources.bat"
pyinstaller -w -F --icon=res\icon.ico "%~p0..\src\AutoSplit.py"
