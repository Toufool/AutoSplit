#! /usr/bin/pwsh
param([switch]$WineCompat)

Push-Location "$PSScriptRoot/.." # Avoid issues with space in path

try {
  & 'scripts/compile_resources.ps1'

  $SupportsSplashScreen = [System.Convert]::ToBoolean(
    $(uv run --active python -c '
from PyInstaller.building.splash import Splash
Splash._check_tcl_tk_compatibility()
    '))

  $arguments = @(
    'src/AutoSplit.py',
    '--onefile',
    '--windowed',
    '--optimize=2', # Remove asserts and docstrings for smaller build
    '--additional-hooks-dir=Pyinstaller/hooks',
    "--add-data=pyproject.toml$([System.IO.Path]::PathSeparator).",
    '--icon=res/icon.ico')
  if (-not $WineCompat) {
    $arguments += '--upx-dir=scripts/.upx'
  }
  if ($SupportsSplashScreen) {
    # https://github.com/pyinstaller/pyinstaller/issues/9022
    $arguments += @('--splash=res/splash.png')
  }
  if ($IsWindows) {
    $arguments += @(
      # Hidden import by winrt.windows.graphics.imaging.SoftwareBitmap.create_copy_from_surface_async
      '--hidden-import=winrt.windows.foundation')
  }

  Write-Output $arguments

  Start-Process -Wait -NoNewWindow uv -ArgumentList $(@('run', '--active', 'pyinstaller') + $arguments)

  if ($IsLinux) {
    Move-Item -Force dist/AutoSplit dist/AutoSplit.elf
    if ($?) {
      Write-Host 'Added .elf extension'
    }
    chmod +x dist/AutoSplit.elf
    Write-Host 'Added execute permission'
  }
}
finally {
  Pop-Location
}
