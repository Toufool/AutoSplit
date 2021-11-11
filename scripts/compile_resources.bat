cd "%~dp0.."
pyuic6 ".\res\about.ui" -o ".\src\about.py"
pyuic6 ".\res\design.ui" -o ".\src\design.py"
pyside6-rcc ".\res\resources.qrc" -o ".\src\resources_rc.py"
