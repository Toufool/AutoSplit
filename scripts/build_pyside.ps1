#! /usr/bin/pwsh

# Builds free-threaded (cp314t) PySide6-Essentials + shiboken6 wheels from source
# and drops them into scripts/ for `uv pip install` (via find-links) to pick up.
#
# Why this exists:
# - There are no official free-threading (cp314t) PySide6 wheels yet.
# - The PyPI wheels are built against the limited API (abi3), which is
#   incompatible with the free-threaded ABI and segfaults on import / in
#   pyside6-uic. Building with --limited-api=no produces proper
#   *.cpython-314t-*.so modules that load under a free-threaded interpreter.
#
# This is intentionally NOT part of install.ps1: the build takes ~20min and
# only needs to be re-run when the (system) Qt version changes. The resulting
# wheels are committed to scripts/.
#
# Linux x86_64 only. Run from anywhere; paths are resolved against scripts/.

param(
  # PySide6 version to build. Must match the system Qt version (PySide X.Y.Z
  # links against Qt X.Y.Z). Defaults to whatever qtpaths reports.
  [string]$Version,
  # Qt modules to build. AutoSplit only uses Core, Gui, Widgets and Test.
  # Order matters: a module must come after the modules it depends on
  # (QtTest includes QtWidgets' generated header).
  [string]$ModuleSubset = 'Core,Gui,Widgets,Test'
)

$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true

if (-not $IsLinux) {
  throw 'build_pyside.ps1 only supports Linux. Other platforms use the PyPI wheels.'
}

# --- Discover Qt -------------------------------------------------------------
$qtpaths = (Get-Command qtpaths6 -ErrorAction SilentlyContinue)?.Source
if (-not $qtpaths) { $qtpaths = '/usr/lib/qt6/bin/qtpaths6' }
if (-not (Test-Path $qtpaths)) { throw "qtpaths6 not found (looked for $qtpaths). Install qt6-base-dev-tools." }
if (-not $Version) { $Version = (& $qtpaths --qt-version).Trim() }
Write-Output "Building PySide6-Essentials $Version against Qt at $qtpaths"

# --- Discover LLVM/Clang (shiboken's binding generator needs libclang) -------
# Pick the highest installed /usr/lib/llvm-N. setup_clang() reads LLVM_INSTALL_DIR
# and find_package(Clang) needs ClangConfig.cmake (shipped by clang-N).
$llvmDir = Get-ChildItem /usr/lib -Directory -Filter 'llvm-*' -ErrorAction SilentlyContinue |
  Sort-Object { [int]($_.Name -replace 'llvm-', '') } -Descending |
  Select-Object -First 1 -ExpandProperty FullName
if (-not $llvmDir) { throw 'No /usr/lib/llvm-N found. Install llvm-<N>-dev and clang-<N>.' }
$llvmVersion = ($llvmDir -replace '.*llvm-', '')
Write-Output "Using LLVM/Clang $llvmVersion at $llvmDir"

# --- System build dependencies ----------------------------------------------
if ((Get-Command apt-get, dpkg-query -ErrorAction SilentlyContinue).Count -eq 2) {
  $packages = @(
    'cmake',
    'qt6-base-dev',          # Qt CMake config + headers
    'qt6-base-private-dev',  # private headers shiboken needs
    'libclang-dev',          # clang-c C API headers
    "llvm-$llvmVersion-dev", # LLVMConfig.cmake
    "clang-$llvmVersion"     # ClangConfig.cmake
  )
  $missing = $packages.Where({
      @(dpkg-query -W -f='${db:Status-Status}\n' $_ 2>$null) -notcontains 'installed'
    })
  if ($missing) {
    sudo apt-get update
    sudo apt-get install -y $missing
  }
}

# --- Work in a throwaway directory ------------------------------------------
$workDir = Join-Path ([System.IO.Path]::GetTempPath()) "pyside-build-$Version"
if (Test-Path $workDir) { Remove-Item $workDir -Recurse -Force }
New-Item -ItemType Directory -Force -Path $workDir | Out-Null
Push-Location $workDir
try {
  # Isolated build venv on the free-threaded interpreter. pyside-setup pins
  # setuptools/wheel; newer setuptools vendors a wheel that drops get_abi_tag,
  # which silently breaks pyside's bdist_wheel override (custom options like
  # --module-subset stop being recognized).
  uv venv --python 3.14t buildenv
  $py = Join-Path $workDir 'buildenv/bin/python'
  uv pip install --python buildenv `
    'setuptools==78.1.0' 'wheel==0.43.0' 'packaging==24.2' 'build==1.2.2.post1' `
    distro patchelf 'mypy>=1.15.0'

  # pyside-setup source at the matching tag
  git clone --depth 1 --branch "v$Version" https://code.qt.io/pyside/pyside-setup pyside-setup
  Push-Location pyside-setup
  try {
    $Env:LLVM_INSTALL_DIR = $llvmDir
    $Env:CLANG_INSTALL_DIR = $llvmDir
    # --limited-api=no is the crux: free-threading is incompatible with abi3.
    & $py setup.py bdist_wheel `
      --qtpaths=$qtpaths `
      --module-subset=$ModuleSubset `
      --limited-api=no `
      --parallel=$([Environment]::ProcessorCount)
    if ($LASTEXITCODE -ne 0) { throw 'PySide6 build failed' }
  }
  finally { Pop-Location }

  $dist = Join-Path $workDir 'pyside-setup/dist'

  # setup.py emits a monolithic "PySide6" wheel. With only qtbase modules that
  # is exactly the content of PySide6-Essentials, so rename it (Name in METADATA
  # + dist-info dir + filename) to slot into the existing find-links install.
  $psideWheel = Get-ChildItem $dist -Filter 'PySide6-*.whl' | Select-Object -First 1
  & $py -m wheel unpack $psideWheel.FullName -d $workDir/unpack
  $unpacked = Get-ChildItem "$workDir/unpack" -Directory | Select-Object -First 1
  $di = Get-ChildItem $unpacked.FullName -Directory -Filter 'PySide6-*.dist-info' | Select-Object -First 1
  (Get-Content "$($di.FullName)/METADATA") `
    -replace '^Name: PySide6\s*$', 'Name: PySide6-Essentials' |
    Set-Content "$($di.FullName)/METADATA"
  Rename-Item $di.FullName ($di.Name -replace '^PySide6-', 'PySide6_Essentials-')
  & $py -m wheel pack $unpacked.FullName -d $dist

  # --- Publish to scripts/ ---------------------------------------------------
  # Remove any previously built free-threaded wheels, then copy the new ones.
  Get-ChildItem $PSScriptRoot -Filter 'PySide6_Essentials-*-cp314*.whl' | Remove-Item -Force
  Get-ChildItem $PSScriptRoot -Filter 'pyside6_essentials-*-cp314*.whl' | Remove-Item -Force
  Get-ChildItem $PSScriptRoot -Filter 'shiboken6-*-cp314*.whl' | Remove-Item -Force
  Copy-Item (Join-Path $dist 'PySide6_Essentials-*-cp314*.whl') $PSScriptRoot
  Copy-Item (Join-Path $dist 'shiboken6-*-cp314*.whl') $PSScriptRoot

  Write-Output 'Built and copied to scripts/:'
  Get-ChildItem $PSScriptRoot -Filter '*-cp314*.whl' | ForEach-Object { Write-Output "  $($_.Name)" }
}
finally { Pop-Location }
