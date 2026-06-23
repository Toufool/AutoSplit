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
    if ((Get-Command apt-get, dpkg-query -ErrorAction SilentlyContinue).Count -eq 2) {
      $packages = @(
        # For running tests headless on CI
        ($Env:GITHUB_JOB ? 'xvfb' : $null),
        # scikit-build (opencv) defaults to Ninja generator
        'ninja-build'
        # Required by pymonctl at import
        'x11-xserver-utils',
        # For splash screen
        'python3-tk',
        # For QT_QPA_PLATFORM=xcb
        'libxcb-cursor-dev',
        # The rest for PySide6
        'libegl1', 'libxkbcommon0', 'libxkbcommon-x11-0', 'libxcb-icccm4', 'libxcb-keysyms1'
      ).Where({ $_ })
      # Only install missing packages so apt doesn't re-mark them as manually installed.
      # Multi-arch packages report one status line per architecture.
      $missing = $packages.Where({
          @(dpkg-query -W -f='${db:Status-Status}\n' $_ 2>$null) -notcontains 'installed'
        })
      if ($missing) {
        sudo apt-get update
        sudo apt-get install -y $missing
      }
    }

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

# https://github.com/opencv/opencv-python#source-distributions
#
# Allows building OpenCV on Windows ARM64 when only sdist is available
# https://github.com/opencv/opencv-python/issues/1092#issuecomment-2862538656
$Env:CMAKE_ARGS = '-DBUILD_opencv_dnn=OFF -DENABLE_NEON=OFF'
# Match flavors to opencv-contrib-python-headless when building from git source repo
$Env:CMAKE_ARGS += ' -DENABLE_CONTRIB=1 -DENABLE_HEADLESS=1'
# Enable free-threaded builds which don't support the limited API
$Env:CMAKE_ARGS += ' -DPYTHON3_LIMITED_API=OFF'

$prod = if ($Env:GITHUB_JOB -eq 'Build') { '--no-dev' } else { }
$lock = if ($Env:GITHUB_JOB) { '--locked' } else { }
# Verbose to see sdist progression
# Exclude PySide6: uv sync/lock can't distinguish GIL vs free-threading ABI.
# uv pip install does wheel-tag selection at runtime — picks local cp314t wheel
# for free-threading Python, falls back to PyPI abi3 for GIL Python / Windows.
$uvSyncArgs = @('sync', '--active', '--no-install-package', 'pyside6-essentials', '--no-install-package', 'shiboken6') + $prod + $lock # + '--verbose'
Write-Output "Installing Python dependencies with: uv $uvSyncArgs"
uv @uvSyncArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Output 'Installing PySide6 with ABI-aware wheel selection'
uv pip install --active pyside6-essentials shiboken6
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Don't compile resources on the Build CI job as it'll do so in build script
if (-not $prod) {
  & "$PSScriptRoot/compile_resources.ps1"
}
