"""
Smoke test: import every one of our own modules, including submodules.

Catches import-time errors early: syntax errors, missing dependencies,
broken platform guards and lazy import issues in module-level code.
"""

import importlib
import operator
import pkgutil
import subprocess  # noqa: S404
import sys
import textwrap
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
                    continue
                module = importlib.import_module(module_name)
                # Force every lazy import proxy to resolve. eval's LOAD_NAME
                # on the module's namespace triggers reification
                # (plain getattr does not).
                for attr_name in [
                    k for k, v in vars(module).items() if type(v).__name__ == "lazy_import"
                ]:
                    eval(attr_name, vars(module))  # noqa: S307

    def test_app_entrypoint_in_fresh_interpreter(self):
        """
        The test runner itself has already imported most of the stdlib, which
        masks lazy import issues that only occur with a clean sys.modules
        (e.g. shiboken6's bootstrap importing stdlib modules through lazy
        proxies). Mimic a real app launch instead.

        Also probes shiboken6's signature support: its bootstrap swallows
        errors and only logs them, and it isn't otherwise guaranteed to be
        exercised by mere imports.
        """
        code = textwrap.dedent("""
            import AutoSplit
            import inspect
            from PySide6 import QtCore
            signature = inspect.signature(QtCore.QObject.objectName)
            assert isinstance(signature, inspect.Signature), signature
        """)
        # Trusted, hardcoded code string ran with our own interpreter
        result = subprocess.run(  # noqa: S603
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            check=False,
            cwd=SRC_DIR,
            timeout=120,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)


if __name__ == "__main__":
    unittest.main()
