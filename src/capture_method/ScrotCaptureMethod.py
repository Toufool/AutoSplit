import sys

if sys.platform != "linux":
    raise OSError

import os
import shutil
import subprocess  # noqa: S404
import tempfile
from typing import override

import cv2
from pywinctl import getWindowsWithTitle
from Xlib.display import Display
from Xlib.error import BadWindow

from capture_method.CaptureMethodBase import CaptureMethodBase
from utils import RUNNING_X11, imread, is_valid_image

IS_SCROT_SUPPORTED = RUNNING_X11 and bool(shutil.which("scrot"))


def _scrot_screenshot(x: int, y: int, width: int, height: int):
    with tempfile.TemporaryDirectory() as tmp:
        screenshot_file = os.path.join(tmp, "something")
        # TODO: Investigate solution for Slow Scrot:
        # https://github.com/asweigart/pyscreeze/issues/68
        subprocess.check_output(("scrot", "-a", f"{x},{y},{width},{height}", "-z", screenshot_file))  # noqa: S603 # Not user input
        # subprocess.check_output(("scrot", "-z", screenshot_file))  # Not user input

        return imread(screenshot_file, cv2.IMREAD_UNCHANGED)


# TODO: Consider maim and fireshot as alternatives to scrot
# https://github.com/naelstrof/maim
# https://github.com/asweigart/pyscreeze/commit/36b822aa54a22b9dafef9ce2d40f8e24f81a5d9e
# https://flameshot.org/docs/installation/installation-linux/
# Maybe even spectacle ?
# https://manpages.debian.org/testing/kde-spectacle/spectacle.1.en.html


class ScrotCaptureMethod(CaptureMethodBase):
    name = "Scrot"
    short_description = "very slow, may leave files"
    description = """
Uses Scrot (SCReenshOT) to take screenshots.
Leaves behind a screenshot file if interrupted."""

    @override
    def get_frame(self):
        if not self.check_selected_region_exists():
            return None

        root = Display().screen().root
        try:
            window_coords = root.translate_coords(self._autosplit_ref.hwnd, 0, 0)._data  # noqa: SLF001
        except BadWindow:
            return None
        selection = self._autosplit_ref.settings_dict["capture_region"]
        image = _scrot_screenshot(
            selection["x"] + window_coords["x"],
            selection["y"] + window_coords["y"],
            selection["width"],
            selection["height"],
        )
        if not is_valid_image(image):
            return None
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGRA)

    @override
    def recover_window(self, captured_window_title: str):
        windows = getWindowsWithTitle(captured_window_title)
        if len(windows) == 0:
            return False
        self._autosplit_ref.hwnd = windows[0].getHandle()
        return self.check_selected_region_exists()
