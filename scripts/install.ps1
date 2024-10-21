$python = $IsWindows ? 'python' : 'python3'

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
    # python3-tk for splash screen, libxcb-cursor-dev for QT_QPA_PLATFORM=xcb, the rest for PySide6
    sudo apt-get install -y python3-pip python3-tk libxcb-cursor-dev libegl1 libxkbcommon0
    # having issues with npm for pyright, maybe let users take care of it themselves? (pyright from pip)
  }
}
# Ensures installation tools are up to date. This also aliases pip to pip3 on MacOS.
&"$python" -m pip install wheel pip setuptools --upgrade
# Upgrading QT to 6.6.2 w/o first uninstalling shiboken6 can lead to issues
# https://bugreports.qt.io/browse/PYSIDE-2616?focusedId=777285&page=com.atlassian.jira.plugin.system.issuetabpanels:comment-tabpanel#comment-777285
&"$python" -m pip uninstall shiboken6 -y
&"$python" -m pip install -r "$PSScriptRoot/requirements$dev.txt" --upgrade
# Temporary hack to test install for Python 3.13
&"$python" -m pip install `
  "PySide6-Essentials>=6.8.0.1 ; python_version >= '3.13'" `
  "shiboken6>=6.8.0.1 ; python_version >= '3.13'" `
  --ignore-requires-python
# These libraries install extra requirements we don't want
# Open suggestion for support in requirements files: https://github.com/pypa/pip/issues/9948 & https://github.com/pypa/pip/pull/10837
# PyAutoGUI: We only use it for hotkeys
&"$python" -m pip install PyAutoGUI --no-deps --upgrade

# Uninstall optional dependencies if PyAutoGUI was installed outside this script
# PyScreeze -> pyscreenshot -> mss deps call SetProcessDpiAwareness, used to be installed on Windows
# pygetwindow, pymsgbox, pytweening, MouseInfo are picked up by PyInstaller
# (also --exclude from build script, but more consistent with unfrozen run)
&"$python" -m pip uninstall pyscreenshot mss pygetwindow pymsgbox pytweening MouseInfo -y
If ($IsWindows) { &"$python" -m pip uninstall PyScreeze -y }

# Don't compile resources on the Build CI job as it'll do so in build script
If ($dev) {
  & "$PSScriptRoot/compile_resources.ps1"
}
