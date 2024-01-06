$python = $IsLinux ? 'python3' : 'python'

# Validating user groups on Linux
If ($IsLinux) {
  $groups = groups
  if ($groups.Contains('input') -and $groups.Contains('tty')) {
    Write-Host "User $Env:USER is already part of groups input and tty. No actions taken."
  }
  Else {
    # https://github.com/boppreh/keyboard/issues/312#issuecomment-1189734564
    Write-Host "User $Env:USER isn't part of groups input and tty. It is required to install the keyboard module."
    # Keep in sync with README.md and src/error_messages.py
    sudo usermod -a -G 'tty,input' $Env:USER
    sudo touch /dev/uinput
    sudo chmod +0666 /dev/uinput
    If (-not $Env:GITHUB_JOB) {
      Write-Output 'KERNEL=="uinput", TAG+="uaccess""' | sudo tee /etc/udev/rules.d/50-uinput.rules
      Write-Output 'SUBSYSTEM=="input", MODE="0666" GROUP="plugdev"' | sudo tee /etc/udev/rules.d/12-input.rules
      Write-Output 'SUBSYSTEM=="misc", MODE="0666" GROUP="plugdev"' | sudo tee -a /etc/udev/rules.d/12-input.rules
      Write-Output 'SUBSYSTEM=="tty", MODE="0666" GROUP="plugdev"' | sudo tee -a /etc/udev/rules.d/12-input.rules
    }
    Write-Host 'You have been added automatically,' `
      "but still need to manually terminate your session with 'loginctl terminate-user $Env:USER'" `
      'for the changes to take effect outside of this script.'
    If (-not $Env:GITHUB_JOB) {
      Write-Host -NoNewline 'Press any key to continue...';
      $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown');
    }
  }
}

# Installing Python dependencies
$dev = If ($Env:GITHUB_JOB -eq 'Build') { '' } Else { '-dev' }
If ($IsLinux) {
  If (-not $Env:GITHUB_JOB -or $Env:GITHUB_JOB -eq 'Build') {
    sudo apt-get update
    # python3-tk for splash screen, npm for pyright, the rest for PySide6
    sudo apt-get install -y python3-pip python3-tk npm libegl1 libxkbcommon0
  }
}
# Ensures installation tools are up to date. This also aliases pip to pip3 on MacOS.
&"$python" -m pip install wheel pip setuptools --upgrade
pip install -r "$PSScriptRoot/requirements$dev.txt" --upgrade
# These libraries install extra requirements we don't want
# Open suggestion for support in requirements files: https://github.com/pypa/pip/issues/9948 & https://github.com/pypa/pip/pull/10837
# PyAutoGUI: We only use it for hotkeys
# D3DShot: Will install Pillow, which we don't use on Windows.
#          Even then, PyPI with Pillow>=7.2.0 will install 0.1.3 instead of 0.1.5
pip install PyAutoGUI "D3DShot>=0.1.5 ; sys_platform == 'win32'" --no-deps --upgrade

# Patch libraries so we don't have to install from git

# Prevent PyAutoGUI and pywinctl from setting Process DPI Awareness, which Qt tries to do then throws warnings about it.
# The unittest workaround significantly increases build time, boot time and build size with PyInstaller.
# https://github.com/asweigart/pyautogui/issues/663#issuecomment-1296719464
$libPath = &"$python" -c 'import pyautogui as _; print(_.__path__[0])'
(Get-Content "$libPath/_pyautogui_win.py").replace('ctypes.windll.user32.SetProcessDPIAware()', 'pass') |
  Set-Content "$libPath/_pyautogui_win.py"
If ($IsWindows) {
  $libPath = &"$python" -c 'import pymonctl as _; print(_.__path__[0])'
  (Get-Content "$libPath/_pymonctl_win.py").replace('ctypes.windll.shcore.SetProcessDpiAwareness(2)', 'pass') |
    Set-Content "$libPath/_pymonctl_win.py"
  $libPath = &"$python" -c 'import pywinbox as _; print(_.__path__[0])'
  (Get-Content "$libPath/_pywinbox_win.py").replace('ctypes.windll.shcore.SetProcessDpiAwareness(2)', 'pass') |
    Set-Content "$libPath/_pywinbox_win.py"
}
# Because Ubuntu 22.04 is forced to use an older version of PySide6, we do a dirty typing patch
# https://bugreports.qt.io/browse/QTBUG-114635
If ($IsLinux) {
  $libPath = &"$python" -c 'import PySide6 as _; print(_.__path__[0])'
  (Get-Content "$libPath/QtWidgets.pyi").replace('-> Tuple:', '-> Tuple[str, ...]:') |
    Set-Content "$libPath/QtWidgets.pyi"
}
# Uninstall optional dependencies if PyAutoGUI or D3DShot was installed outside this script
# pyscreeze -> pyscreenshot -> mss deps call SetProcessDpiAwareness, used to be installed on Windows
# Pillow, pygetwindow, pymsgbox, pytweening, MouseInfo are picked up by PySide6
# (also --exclude from build script, but more consistent with unfrozen run)
pip uninstall pyscreenshot mss pygetwindow pymsgbox pytweening MouseInfo -y
If ($IsWindows) { pip uninstall pyscreeze Pillow -y }

# Don't compile resources on the Build CI job as it'll do so in build script
If ($dev) {
  & "$PSScriptRoot/compile_resources.ps1"
}
