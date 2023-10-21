# Installing Python dependencies
$dev = If ($Env:GITHUB_JOB -eq 'Build') { '' } Else { '-dev' }
# Ensures installation tools are up to date. This also aliases pip to pip3 on MacOS.
python -m pip install wheel pip setuptools --upgrade
pip install -r "$PSScriptRoot/requirements$dev.txt" --upgrade
# These libraries install extra requirements we don't want
# Open suggestion for support in requirements files: https://github.com/pypa/pip/issues/9948 & https://github.com/pypa/pip/pull/10837
# pyautogui: We only use it for hotkeys
# ImageHash: uneeded + broken on Python 3.12 PyWavelets install
# scipy: needed for ImageHash
pip install pyautogui ImageHash scipy --no-deps --upgrade

# Patch libraries so we don't have to install from git

# Prevent pyautogui and pywinctl from setting Process DPI Awareness, which Qt tries to do then throws warnings about it.
# The unittest workaround significantly increases build time, boot time and build size with PyInstaller.
# https://github.com/asweigart/pyautogui/issues/663#issuecomment-1296719464
$libPath = python -c 'import pyautogui as _; print(_.__path__[0])'
(Get-Content "$libPath/_pyautogui_win.py").replace('ctypes.windll.user32.SetProcessDPIAware()', 'pass') |
  Set-Content "$libPath/_pyautogui_win.py"
$libPath = python -c 'import pymonctl as _; print(_.__path__[0])'
(Get-Content "$libPath/_pymonctl_win.py").replace('ctypes.windll.shcore.SetProcessDpiAwareness(2)', 'pass') |
  Set-Content "$libPath/_pymonctl_win.py"
$libPath = python -c 'import pywinbox as _; print(_.__path__[0])'
(Get-Content "$libPath/_pywinbox_win.py").replace('ctypes.windll.shcore.SetProcessDpiAwareness(2)', 'pass') |
  Set-Content "$libPath/_pywinbox_win.py"
# Uninstall optional dependencies if pyautogui was installed outside this script
# pyscreeze -> pyscreenshot -> mss deps call SetProcessDpiAwareness
# pygetwindow, pymsgbox, pytweening are picked up by PySide6 (could --exclude from build, but more consistent with unfrozen run)
# mouseinfo, pyperclip, just to be safe?
python -m pip uninstall pyscreeze pyscreenshot mss pygetwindow pymsgbox pytweening -y


# Don't compile resources on the Build CI job as it'll do so in build script
If ($dev) {
  & "$PSScriptRoot/compile_resources.ps1"
}
