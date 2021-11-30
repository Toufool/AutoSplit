py -3.9 -m pip install wheel
py -3.9 -m pip install -r "%~p0requirements.txt"
npm install -g pyright
CALL "%~p0compile_resources.bat"
