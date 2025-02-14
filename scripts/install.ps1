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
      Write-Output 'KERNEL=="uinput", TAG+="uaccess"' | sudo tee /etc/udev/rules.d/50-uinput.rules
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
If ($IsLinux) {
  If (-not $Env:GITHUB_JOB -or $Env:GITHUB_JOB -eq 'Build') {
    sudo apt-get update
    # python3-tk for splash screen, libxcb-cursor-dev for QT_QPA_PLATFORM=xcb, the rest for PySide6
    sudo apt-get install -y python3-tk libxcb-cursor-dev libegl1 libxkbcommon0 libxkbcommon-x11-0 libxcb-icccm4 libxcb-keysyms1
  }
}

$prod = If ($Env:GITHUB_JOB -eq 'Build') { '--no-dev' } Else { }
$lock = If ($Env:GITHUB_JOB) { '--locked' } Else { '--upgrade' }
Write-Output "Installing Python dependencies with: uv sync $prod $lock"
uv sync --active $prod $lock

# Don't compile resources on the Build CI job as it'll do so in build script
If (-not $prod) {
  & "$PSScriptRoot/compile_resources.ps1"
}
