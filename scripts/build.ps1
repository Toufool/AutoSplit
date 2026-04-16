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
    '--noconfirm',
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
      '--onefile',
      # Hidden import by winrt.windows.graphics.imaging.SoftwareBitmap.create_copy_from_surface_async
      '--hidden-import=winrt.windows.foundation')
  }
  else {
    $arguments += @(
      '--distpath=build/AppDir'
      # Apply a symbol-table strip to the executable and shared libs (not recommended for Windows)
      '--strip')
  }

  Write-Output $arguments
  Start-Process -Wait -NoNewWindow uv -ArgumentList $(@('run', '--active', 'pyinstaller') + $arguments)

  if ($IsLinux) {
    # Hoist the onedir output so files sit directly in the AppDir root.
    # The executable is renamed to AppRun here to avoid a naming conflict with the onedir directory.
    Move-Item build/AppDir/AutoSplit/AutoSplit build/AppDir/AppRun
    Move-Item build/AppDir/AutoSplit/_internal build/AppDir/_internal
    Remove-Item build/AppDir/AutoSplit


    if ([System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture -eq 'X64') {
      # Technically UPX works for Linux executables, but trying to compress .so can still result in Segmentation fault
      # https://github.com/orgs/pyinstaller/discussions/8922#discussioncomment-13185670
      # https://github.com/pyinstaller/pyinstaller/blob/4d28a528f8ab8632f7cfa7662fc6fcc45881e741/PyInstaller/building/utils.py#L281-L288
      $soFilesToCompress = Get-ChildItem -Path build/AppDir/_internal -Recurse -File -Filter '*.so*'
    | Where-Object {
        -not (
          # _internal/*.so* causes Segmentation fault
          $_.Directory -like '*/AppDir/_internal' -or
          # _internal/PySide6/Qt/*/*.so* causes Segmentation fault
          # _internal/PySide6/Qt/plugins/*/*.so* breaks style
          $_.Directory -like '*/AppDir/_internal/PySide6/Qt/*'
        )
      }
      & 'scripts/.upx/upx' --lzma --best build/AppDir/AppRun $soFilesToCompress
    }

    chmod +x build/AppDir/AppRun

    ###
    # Create AppImage
    ###
    Copy-Item res/AutoSplit.desktop build/AppDir/AutoSplit.desktop
    Copy-Item res/splash.png build/AppDir/AutoSplit.png

    if (Test-Path dist) { Remove-Item dist -Recurse -Force }
    New-Item -ItemType Directory -Path dist | Out-Null

    & 'scripts/appimagetool.AppImage' --no-appstream build/AppDir dist/AutoSplit.AppImage
    chmod +x dist/AutoSplit.AppImage

    Write-Host 'Created dist/AutoSplit.AppImage'
  }
}
finally {
  Pop-Location
}
