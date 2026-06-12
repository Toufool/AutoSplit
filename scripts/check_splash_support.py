"""
Check whether PyInstaller can build the splash screen on this platform.

Prints "True" or "False" to stdout for consumption by build.ps1.
"""

# Not found in typeshed because private
# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportAttributeAccessIssue=false

import sys

from PyInstaller.building.splash import Splash

try:
    from PyInstaller.utils.hooks.tcl_tk import tcltk_info

    if not tcltk_info.available:
        raise SystemExit(  # noqa: TRY301 # Copies source
            "ERROR: Your platform does not support the splash screen feature, "
            + "since tkinter is not installed. Please install tkinter and try again."
        )
    Splash._check_tcl_tk_compatibility(tcltk_info)  # noqa: SLF001
    print(True)
except SystemExit as e:
    print(e, file=sys.stderr)
    print(False)
