"""
Check whether PyInstaller can build the splash screen on this platform.

Prints "True" or "False" to stdout for consumption by build.ps1.
"""

# Not found in typeshed because private
# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportAttributeAccessIssue=false

import sys

from PyInstaller.building.splash import Splash

try:
    Splash._check_tcl_tk_compatibility()  # noqa: SLF001
    print(True)
except SystemExit as e:
    print(e, file=sys.stderr)
    print(False)
