#! /usr/bin/pwsh

param(
  [switch]$WineCompat,
  [switch]$IncludePythonVersionTag
)

$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true

Push-Location "$PSScriptRoot/.." # Avoid issues with space in path

try {
  & 'scripts/compile_resources.ps1'

  $version = (Select-String 'pyproject.toml' -Pattern '^version = "(.+)"').Matches.Groups[1].Value
  # Include the build number (generated in compile_resources.ps1) in the filename
  # But only on CI, keeping the filename consistent for local dev builds
  $buildNumber = (Select-String 'src/gen/build_vars.py' `
      -Pattern '^AUTOSPLIT_BUILD_NUMBER = "(.*)"').Matches.Groups[1].Value
  $buildNumber = if ($Env:GITHUB_JOB -and $buildNumber) { "-$buildNumber" } else { '' }
  # Semver-compliant Python version tag
  $pythonVersionTag = if ($IncludePythonVersionTag) {
    (uv run --active python --version) -replace '^Python (\d+\.\d+).*', '+Python$1'
  }
  else { '' }

  # CI not allowed to skip splash screen, it MUST build (will fail when calling PyInstaller)
  $supportsSplashScreen = $Env:GITHUB_JOB -or [System.Convert]::ToBoolean(
    $(uv run --active scripts/check_splash_support.py))

  $arguments = @(
    'src/AutoSplit.py',
    '--noconfirm',
    '--windowed',
    '--optimize=2', # Remove asserts and docstrings for smaller build
    '--additional-hooks-dir=Pyinstaller/hooks',
    "--add-data=pyproject.toml$([System.IO.Path]::PathSeparator).",
    '--icon=res/icon.ico')
  # Don't UPX compress if trying to be Wine Compatible, or on Linux (handled manually below)
  if (-not $WineCompat -and -not $IsLinux) {
    $arguments += '--upx-dir=scripts/.upx'
    $arguments += @(
      # pywin32's DLLs do custom load-time magic (__import_pywin32_system_module__) that
      # UPX self-decompression breaks under Wine ("DLL initialisation failed").
      # Native Windows tolerates it, Wine's loader doesn't. Exclude them from compression.
      '--upx-exclude=pythoncom*.dll',
      '--upx-exclude=pywintypes*.dll')
  }
  else {
    # Missing upx executable should be enough, but let's be explicit
    $arguments += '--noupx'
  }
  if ($supportsSplashScreen) {
    # https://github.com/pyinstaller/pyinstaller/issues/9022
    $arguments += @('--splash=res/splash.png')
  }
  if ($IsWindows) {
    $arch = "$([System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture)".ToLower()
    $arguments += @(
      '--onefile',
      "--name=AutoSplit-$version$buildNumber$pythonVersionTag-$arch$(if ($WineCompat) {'-WineCompat'} else {''})"
      # Hidden import by winrt.windows.graphics.imaging.SoftwareBitmap.create_copy_from_surface_async
      '--hidden-import=winrt.windows.foundation')
  }
  else {
    if (Test-Path build/AppDir) { Remove-Item build/AppDir -Recurse -Force }
    $arguments += @(
      '--distpath=build/AppDir'
      # Apply a symbol-table strip to the executable and shared libs (not recommended for Windows)
      '--strip')
  }

  Write-Output "pyinstaller $($arguments -join ' ')"
  & uv run --active pyinstaller @arguments

  if ($IsLinux) {
    # Hoist the onedir output so files sit directly in the AppDir root.
    # The executable is renamed to AppRun here to avoid a naming conflict with the onedir directory.
    Move-Item build/AppDir/AutoSplit/AutoSplit build/AppDir/AppRun
    Move-Item build/AppDir/AutoSplit/_internal build/AppDir/_internal
    Remove-Item build/AppDir/AutoSplit

    $arch = switch ([System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture) {
      'X64' { 'x86_64' }
      'Arm64' { 'aarch64' }
      default { throw "Unsupported arch: $_" }
    }

    if ($arch -eq 'x86_64') {
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
      try {
        & 'scripts/.upx/upx' --lzma --best build/AppDir/AppRun $soFilesToCompress
      }
      catch {
        # UPX exits 1 when a file was skipped (e.g. already compressed) - not fatal
        if ($LASTEXITCODE -ne 1) { throw }
      }
    }

    chmod +x build/AppDir/AppRun

    ###
    # Create AppImage
    ###
    Copy-Item res/AutoSplit.desktop build/AppDir/AutoSplit.desktop
    # Icon as PNG (freedesktop doesn't support .ico), converted from res/icon.ico.
    # Not splash.png, which uses hard transparency for the Tcl/Tk splash.
    New-Item -ItemType Directory -Path build/AppDir/usr/share/icons/hicolor/256x256/apps -Force | Out-Null
    uv run --active python -c "from PIL import Image; Image.open('res/icon.ico').save('build/AppDir/AutoSplit.png')"
    # Top-level -> .DirIcon (file thumbnail); hicolor copy -> desktop integration (menu/taskbar).
    Copy-Item build/AppDir/AutoSplit.png build/AppDir/usr/share/icons/hicolor/256x256/apps/AutoSplit.png
    $date = Get-Date -Format 'yyyy-MM-dd'

    New-Item -ItemType Directory -Path build/AppDir/usr/share/metainfo -Force | Out-Null
    (Get-Content 'res/AutoSplit.metainfo.xml' -Raw) `
      -replace '(<releases>)', "`$1`n    <release version=`"$version`" date=`"$date`" />" |
      Set-Content 'build/AppDir/usr/share/metainfo/io.github.Toufool.AutoSplit.metainfo.xml' -NoNewline

    if (Test-Path dist) { Remove-Item dist -Recurse -Force }
    New-Item -ItemType Directory -Path dist | Out-Null

    # AppImage naming nomenclature:
    # - https://github.com/AppImage/AppImageSpec/blob/master/draft.md#type-2-image-format
    # - https://github.com/AppImage/appimage.github.io#:~:text=Standard%20nomenclature
    $appImageName = "AutoSplit-$version$buildNumber$pythonVersionTag-$arch.AppImage"
    $arguments = @('build/AppDir', "dist/$appImageName")
    # Skip update information (and the zsync file it generates) unless this is a production build:
    # a GitHub build with a clean version number (no build number)
    if ($Env:GITHUB_REPOSITORY -and -not $buildNumber) {
      $owner, $repo = $Env:GITHUB_REPOSITORY -split '/'
      # Update information
      # https://docs.appimage.org/packaging-guide/optional/updates.html#using-appimagetool
      # https://github.com/AppImage/AppImageSpec/blob/master/draft.md#github-releases
      $arguments += @('-u', "gh-releases-zsync|$owner|$repo|latest|AutoSplit-*-$arch.AppImage.zsync")
    }
    & 'scripts/appimagetool.AppImage' @arguments

    # appimagetool writes the .zsync file to the working directory (repo root) as the AppImage
    # basename, not next to the AppImage. Move it into dist/.
    if (Test-Path "$appImageName.zsync") {
      Move-Item "$appImageName.zsync" "dist/$appImageName.zsync" -Force
    }

    Write-Host "Created dist/$appImageName"
  }
}
finally {
  Pop-Location
}
