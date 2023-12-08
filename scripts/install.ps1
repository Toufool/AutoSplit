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
    If (-not $env:GITHUB_JOB) {
      Write-Output 'KERNEL=="uinput", TAG+="uaccess""' | sudo tee /etc/udev/rules.d/50-uinput.rules
      Write-Output 'SUBSYSTEM=="input", MODE="0666" GROUP="plugdev"' | sudo tee /etc/udev/rules.d/12-input.rules
      Write-Output 'SUBSYSTEM=="misc", MODE="0666" GROUP="plugdev"' | sudo tee -a /etc/udev/rules.d/12-input.rules
      Write-Output 'SUBSYSTEM=="tty", MODE="0666" GROUP="plugdev"' | sudo tee -a /etc/udev/rules.d/12-input.rules
    }
    Write-Host 'You have been added automatically,' `
      "but still need to manually terminate your session with 'loginctl terminate-user $Env:USER'" `
      'for the changes to take effect outside of this script.'
    If (-not $env:GITHUB_JOB) {
      Write-Host -NoNewline 'Press any key to continue...';
      $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown');
    }
  }
}

# Installing Python dependencies
$dev = If ($env:GITHUB_JOB -eq 'Build') { '' } Else { '-dev' }
If ($IsLinux) {
  If (-not $env:GITHUB_JOB -or $env:GITHUB_JOB -eq 'Build') {
    sudo apt-get update
    # python3-tk for splash screen, npm for pyright
    sudo apt-get install -y python3-pip python3-tk npm
    # Helps ensure build machine has the required PySide6 libraries for all target machines.
    # Not everything here is required, but using the documentation from
    # https://wiki.qt.io/Building_Qt_5_from_Git#Libxcb
    # TODO: Test if still necessary with PySide6
    sudo apt-get install -y '^libxcb.*-dev' libx11-xcb-dev libglu1-mesa-dev libxrender-dev libxi-dev libxkbcommon-dev libxkbcommon-x11-dev
  }
}
# Ensures installation tools are up to date. This also aliases pip to pip3 on MacOS.
&"$python" -m pip install wheel pip setuptools --upgrade
pip install -r "$PSScriptRoot/requirements$dev.txt" --upgrade

# Don't compile resources on the Build CI job as it'll do so in build script
If ($dev) {
  & "$PSScriptRoot/compile_resources.ps1"
}
