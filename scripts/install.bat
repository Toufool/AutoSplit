py -m pip install wheel --upgrade
py -m pip install -r "%~p0requirements.txt" --upgrade
CALL "%~p0compile_resources.bat"
CALL npm install -g pyright@latest
CALL npm list -g pyright
