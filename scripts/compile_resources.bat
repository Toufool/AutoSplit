cd "%~dp0.."
pyuic6 "./res/about.ui" -o "./src/about.py"
pyuic6 "./res/design.ui" -o "./src/design.py"
:: Doesn't work with current setup. Files might have to be moved around.
:: The Donate button file is also missing
pyside6-rcc "./res/resources.qrc" -o "./src/resources_rc.py"
