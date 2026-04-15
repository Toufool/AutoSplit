#! /usr/bin/pwsh
param([switch]$WineCompat)

# Validating user groups on Linux
if ($IsLinux) {
  $groups = groups
  if ($groups.Contains('input') -and $groups.Contains('tty')) {
    Write-Host "User $Env:USER is already part of groups input and tty. No actions taken."
  }
  else {
    # https://github.com/boppreh/keyboard/issues/312#issuecomment-1189734564
    Write-Host "User $Env:USER isn't part of groups input and tty. It is required to install the keyboard module."
    # Keep in sync with README.md and src/error_messages.py
    sudo usermod -a -G 'tty,input' $Env:USER
    sudo touch /dev/uinput
    sudo chmod +0666 /dev/uinput
    if (-not $Env:GITHUB_JOB) {
      Write-Output 'KERNEL=="uinput", TAG+="uaccess"' | sudo tee /etc/udev/rules.d/50-uinput.rules
      Write-Output 'SUBSYSTEM=="input", MODE="0666" GROUP="plugdev"' | sudo tee /etc/udev/rules.d/12-input.rules
      Write-Output 'SUBSYSTEM=="misc", MODE="0666" GROUP="plugdev"' | sudo tee -a /etc/udev/rules.d/12-input.rules
      Write-Output 'SUBSYSTEM=="tty", MODE="0666" GROUP="plugdev"' | sudo tee -a /etc/udev/rules.d/12-input.rules
    }
    Write-Host 'You have been added automatically,' `
      "but still need to manually terminate your session with 'loginctl terminate-user $Env:USER'" `
      'for the changes to take effect outside of this script.'
    if (-not $Env:GITHUB_JOB) {
      Write-Host -NoNewline 'Press any key to continue...'
      $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    }
  }
}

if ($IsLinux) {
  if (-not $Env:GITHUB_JOB -or $Env:GITHUB_JOB -eq 'Build') {
    # System dependencies
    sudo apt-get update
    # python3-tk for splash screen, libxcb-cursor-dev for QT_QPA_PLATFORM=xcb, the rest for PySide6
    sudo apt-get install -y python3-tk libxcb-cursor-dev libegl1 libxkbcommon0 libxkbcommon-x11-0 libxcb-icccm4 libxcb-keysyms1

    Write-Output 'Installing appimagetool'
    Invoke-WebRequest `
      -Uri "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-$(uname -m).AppImage" `
      -OutFile "$PSScriptRoot/appimagetool.AppImage"
    chmod +x "$PSScriptRoot/appimagetool.AppImage"
  }
}

# UPX doesn't support macOS,
# doesn't work on ARM64,
# and we avoid using it on the "wine-compatible build"
if (`
    -not $IsMacOS `
    -and [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture -eq 'X64' `
    -and -not $WineCompat
) {
  $UPXVersion = '5.1.1'
  if ($IsLinux) {
    $UPXFolderName = "upx-$UPXVersion-amd64_linux"
    $UPXArchiveName = "$UPXFolderName.tar.xz"
  }
  else {
    $UPXFolderName = "upx-$UPXVersion-win64"
    $UPXArchiveName = "$UPXFolderName.zip"
  }
  $TempDownloadLocation = Join-Path ([System.IO.Path]::GetTempPath()) $UPXArchiveName

  Write-Output "Installing $UPXFolderName"

  if (Test-Path "$PSScriptRoot/.upx") { Remove-Item $PSScriptRoot/.upx -Recurse -Force }
  Invoke-WebRequest `
    -Uri https://github.com/upx/upx/releases/download/v$UPXVersion/$UPXArchiveName `
    -OutFile $TempDownloadLocation
  # Automatically install in a local untracked folder. This makes it easy to version and replicate on CI
  if ($IsLinux) {
    New-Item -ItemType Directory -Force -Path $PSScriptRoot/.upx | Out-Null
    tar -xJf $TempDownloadLocation -C $PSScriptRoot/.upx
  }
  else {
    Expand-Archive $TempDownloadLocation $PSScriptRoot/.upx
  }
  Move-Item $PSScriptRoot/.upx/$UPXFolderName/* $PSScriptRoot/.upx
  Remove-Item $PSScriptRoot/.upx/$UPXFolderName
}

$prod = if ($Env:GITHUB_JOB -eq 'Build') { '--no-dev' } else { }
$lock = if ($Env:GITHUB_JOB) { '--locked' } else { }
Write-Output "Installing Python dependencies with: uv sync $prod $lock"
uv sync --active $prod $lock

# Don't compile resources on the Build CI job as it'll do so in build script
if (-not $prod) {
  & "$PSScriptRoot/compile_resources.ps1"
}
