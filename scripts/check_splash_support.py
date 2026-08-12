"""
Check whether PyInstaller can build the splash screen on this platform.

Prints "True" or "False" to stdout for consumption by build.ps1.
"""

import sys

from PyInstaller.building.splash import Splash

try:
    from PyInstaller.utils.hooks.tcl_tk import tcltk_info

    if not tcltk_info.available:
        raise SystemExit(  # ruff:ignore[raise-within-try] # Copies source
            "ERROR: Your platform does not support the splash screen feature, "
            + "since tkinter is not installed. Please install tkinter and try again."
        )
    Splash._check_tcl_tk_compatibility(tcltk_info)  # ruff:ignore[private-member-access]
    print(True)
except SystemExit as e:
    print(e, file=sys.stderr)
    print(False)
