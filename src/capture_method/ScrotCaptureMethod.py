import sys

if sys.platform != "linux":
    raise OSError

import os
import shutil
import subprocess  # noqa: S404
import tempfile
from typing import TYPE_CHECKING, override

import cv2
from Xlib.display import Display
from Xlib.error import BadWindow, DisplayError

from capture_method.CaptureMethodBase import CaptureMethodBase
from utils import HAS_X_DISPLAY, get_windows_with_title, imread, is_valid_image

if TYPE_CHECKING:
    from AutoSplit import AutoSplit


def _is_xwayland():
    """Ask the X server itself, env vars can disagree with the actual `DISPLAY`."""
    try:
        display = Display()
    except DisplayError:
        return False
    try:
        return display.query_extension("XWAYLAND") is not None
    finally:
        display.close()


SCROT_PATH = shutil.which("scrot") or ""
# Scrot always grabs from the root window (even with `--window`),
# which rootless XWayland leaves blank.
IS_SCROT_SUPPORTED = HAS_X_DISPLAY and bool(SCROT_PATH) and not _is_xwayland()


def _scrot_screenshot(x: int, y: int, width: int, height: int):
    with tempfile.TemporaryDirectory() as tmp:
        screenshot_file = os.path.join(tmp, "autosplit")
        try:
            subprocess.check_call((  # noqa: S603 # Not user input
                SCROT_PATH,
                "-a",
                f"{x},{y},{width},{height}",
                "-z",
                screenshot_file,
            ))
            return imread(screenshot_file, cv2.IMREAD_COLOR_BGR)
        except subprocess.CalledProcessError:
            # This can happen when trying to capture a region OOB
            # scrot is rude and prints directly to TTY, no stderr :/
            return None


class ScrotCaptureMethod(CaptureMethodBase):
    name = "Scrot"
    short_description = "slow, may leave files in `/tmp`"
    description = """
Uses Scrot (SCReenshOT) to take screenshots.
Leaves behind a screenshot file in `/tmp` if interrupted.
"scrot" must be installed: `sudo apt install scrot`
Not available on Wayland."""

    def __init__(self, autosplit: AutoSplit):
        super().__init__(autosplit)
        self._display = Display()

    @override
    def close(self):
        self._display.close()

    @override
    def get_frame(self):
        if not self.check_selected_region_exists():
            return None

        root = self._display.screen().root
        try:
            window_coords = root.translate_coords(self._autosplit_ref.hwnd, 0, 0)._data  # noqa: SLF001
        except BadWindow:
            # Window was closed
            return None
        selection = self._autosplit_ref.settings_dict["capture_region"]
        image = _scrot_screenshot(
            selection["x"] + window_coords["x"],
            selection["y"] + window_coords["y"],
            selection["width"],
            selection["height"],
        )
        return image if is_valid_image(image) else None

    @override
    def recover_window(self, captured_window_title: str):
        windows = get_windows_with_title(captured_window_title)
        if len(windows) == 0:
            return False
        self._autosplit_ref.hwnd = windows[0].getHandle()
        return self.check_selected_region_exists()
