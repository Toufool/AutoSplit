& "$PSScriptRoot/compile_resources.ps1"

$arguments = @(
  "$PSScriptRoot/../src/AutoSplit.py",
  '--onefile',
  '--windowed',
  '--additional-hooks-dir=Pyinstaller/hooks',
  '--icon=res/icon.ico')
if ($IsWindows) {
  $arguments += @(
    # For now this is broken on Linux because we can't know if the target machine will support it or not
    # https://github.com/pyinstaller/pyinstaller/issues/9022
    '--splash=res/splash.png'
    # Hidden import by winrt.windows.graphics.imaging.SoftwareBitmap.create_copy_from_surface_async
    '--hidden-import=winrt.windows.foundation')
}

Start-Process -Wait -NoNewWindow uv -ArgumentList $(@('run', 'pyinstaller') + $arguments)

If ($IsLinux) {
  Move-Item -Force $PSScriptRoot/../dist/AutoSplit $PSScriptRoot/../dist/AutoSplit.elf
  If ($?) {
    Write-Host 'Added .elf extension'
  }
  chmod +x $PSScriptRoot/../dist/AutoSplit.elf
  Write-Host 'Added execute permission'
}
