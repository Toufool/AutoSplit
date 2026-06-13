"""
Smoke test: import every one of our own modules, including submodules.

Catches import-time errors early: syntax errors, missing dependencies
and broken platform guards in module-level code.
"""

import importlib
import operator
import pkgutil
import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

# Single-platform modules, by the platform they support.
# Importing one on any other platform is expected to raise OSError.
PLATFORM_MODULES = {
    "win32": {
        "capture_method.BitBltCaptureMethod",
        "capture_method.DesktopDuplicationCaptureMethod",
        "capture_method.ForceFullContentRenderingCaptureMethod",
        "capture_method.WindowsGraphicsCaptureMethod",
        "d3d11",
    },
    "linux": {
        "capture_method.Screenshot using QT attempt",
        "capture_method.ScrotCaptureMethod",
        "capture_method.XcbCaptureMethod",
    },
}
EXPECTED_OS_ERRORS = frozenset(
    module
    for platform, modules in PLATFORM_MODULES.items()
    if platform != sys.platform
    for module in modules
)


def iter_all_modules():
    """Yields every top-level module, followed by its direct submodules."""
    for top_level in sorted(pkgutil.iter_modules([SRC_DIR]), key=operator.attrgetter("name")):
        yield top_level.name
        if top_level.ispkg:
            for submodule in pkgutil.iter_modules([SRC_DIR / top_level.name]):
                yield f"{top_level.name}.{submodule.name}"


class TestImportAllModules(unittest.TestCase):
    def test_import_all_modules(self):
        for module_name in iter_all_modules():
            with self.subTest(module=module_name):
                if module_name in EXPECTED_OS_ERRORS:
                    with self.assertRaises(OSError):
                        importlib.import_module(module_name)
                else:
                    importlib.import_module(module_name)


if __name__ == "__main__":
    unittest.main()
