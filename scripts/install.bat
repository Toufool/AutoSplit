py -m pip install wheel --upgrade
py -m pip install -r "%~p0requirements.txt" --upgrade
npm install -g pyright@latest
CALL "%~p0compile_resources.bat"
