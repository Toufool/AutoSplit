py -3.9 -m pip install wheel
py -3.9 -m pip install -r "%~p0requirements.txt"
@REM https://github.com/python/mypy/issues/10600 --non-interactive may still have issues
mypy --install-types --non-interactive
npm install -g pyright
CALL "%~p0compile_resources.bat"
