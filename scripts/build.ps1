#! /usr/bin/pwsh

& "$PSScriptRoot/compile_resources.ps1"

$ProjectRoot = "$PSScriptRoot/.."
$SupportsSplashScreen = [System.Convert]::ToBoolean($(uv run --active python -c "import _tkinter; print(hasattr(_tkinter, '__file__'))"))

$arguments = @(
  "$ProjectRoot/src/AutoSplit.py",
  '--onefile',
  '--windowed',
  '--optimize=2', # Remove asserts and docstrings for smaller build
  "--additional-hooks-dir=$ProjectRoot/Pyinstaller/hooks",
  "--add-data=$ProjectRoot/pyproject.toml$([System.IO.Path]::PathSeparator).",
  "--upx-dir=$PSScriptRoot/.upx"
  "--icon=$ProjectRoot/res/icon.ico")
if ($SupportsSplashScreen) {
  # https://github.com/pyinstaller/pyinstaller/issues/9022
  $arguments += @("--splash=$ProjectRoot/res/splash.png")
}
if ($IsWindows) {
  $arguments += @(
    # Hidden import by winrt.windows.graphics.imaging.SoftwareBitmap.create_copy_from_surface_async
    '--hidden-import=winrt.windows.foundation')
}

Start-Process -Wait -NoNewWindow uv -ArgumentList $(@('run', '--active', 'pyinstaller') + $arguments)

If ($IsLinux) {
  Move-Item -Force $ProjectRoot/dist/AutoSplit $ProjectRoot/dist/AutoSplit.elf
  If ($?) {
    Write-Host 'Added .elf extension'
  }
  chmod +x $ProjectRoot/dist/AutoSplit.elf
  Write-Host 'Added execute permission'
}
