pyuic6 "%~dp0../res/about.ui" -o "%~dp0../src/about.py"
pyuic6 "%~dp0../res/design.ui" -o "%~dp0../src/design.py"
pyside6-rcc "%~dp0../res/resources.qrc" -o "%~dp0../src/resources_rc.py"
