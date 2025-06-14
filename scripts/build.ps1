#! /usr/bin/pwsh

& "$PSScriptRoot/compile_resources.ps1"

$SupportsSplashScreen = [System.Convert]::ToBoolean($(uv run --active python -c "import _tkinter; print(hasattr(_tkinter, '__file__'))"))

$arguments = @(
  "$PSScriptRoot/../src/AutoSplit.py",
  '--onefile',
  '--windowed',
  '--additional-hooks-dir=Pyinstaller/hooks',
  '--optimize 2', # Remove asserts and docstrings for smaller build
  "--add-data=pyproject.toml$([System.IO.Path]::PathSeparator).",
  '--icon=res/icon.ico')
if ($SupportsSplashScreen) {
  # https://github.com/pyinstaller/pyinstaller/issues/9022
  $arguments += @('--splash=res/splash.png')
}
if ($IsWindows) {
  $arguments += @(
    # Hidden import by winrt.windows.graphics.imaging.SoftwareBitmap.create_copy_from_surface_async
    '--hidden-import=winrt.windows.foundation')
}

Start-Process -Wait -NoNewWindow uv -ArgumentList $(@('run', '--active', 'pyinstaller') + $arguments)

If ($IsLinux) {
  Move-Item -Force $PSScriptRoot/../dist/AutoSplit $PSScriptRoot/../dist/AutoSplit.elf
  If ($?) {
    Write-Host 'Added .elf extension'
  }
  chmod +x $PSScriptRoot/../dist/AutoSplit.elf
  Write-Host 'Added execute permission'
}
