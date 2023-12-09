& "$PSScriptRoot/compile_resources.ps1"

$arguments = @(
  "$PSScriptRoot/../src/AutoSplit.py",
  '--onefile',
  '--windowed',
  '--additional-hooks-dir=Pyinstaller/hooks',
  '--icon=res/icon.ico',
  '--splash=res/splash.png',
  # The install script should ensure that these are not installed
  # But we'll still include unused dependencies that would be picked up by PyInstaller
  # if requirements.txt was used directly to help ensure consistency when building locally.
  #
  # Installed by PyAutoGUI
  '--exclude=pygetwindow',
  '--exclude=pymsgbox',
  '--exclude=pytweening',
  '--exclude=mouseinfo',
  # Used by imagehash.whash
  '--exclude=pywt')
if ($IsWindows) {
  # Installed by PyAutoGUI
  $arguments += '--exclude=pyscreeze'
}
if ($IsLinux) {
  $arguments += @(
    # Required on the CI for PyWinCtl
    '--hidden-import pynput.keyboard._xorg',
    '--hidden-import pynput.mouse._xorg')
}

Start-Process -Wait -NoNewWindow pyinstaller -ArgumentList $arguments

If ($IsLinux) {
  Move-Item -Force $PSScriptRoot/../dist/AutoSplit $PSScriptRoot/../dist/AutoSplit.elf
  If ($?) {
    Write-Host 'Added .elf extension'
  }
  chmod +x $PSScriptRoot/../dist/AutoSplit.elf
  Write-Host 'Added execute permission'
}
