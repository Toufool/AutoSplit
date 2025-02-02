import sys

if sys.platform != "win32":
    raise OSError
from typing import TYPE_CHECKING

import cv2
import d3dshot
import win32api
import win32con
import win32gui
from typing_extensions import override

from capture_method.BitBltCaptureMethod import BitBltCaptureMethod
from utils import GITHUB_REPOSITORY, get_window_bounds

if TYPE_CHECKING:
    from AutoSplit import AutoSplit


class DesktopDuplicationCaptureMethod(BitBltCaptureMethod):
    name = "Direct3D Desktop Duplication"
    short_description = "slower, bound to display"
    description = f"""
Duplicates the desktop using Direct3D.
It can record OpenGL and Hardware Accelerated windows.
Up to 15x slower than BitBlt for tiny regions. Not affected by window size.
Limited by the target window and monitor's refresh rate.
Overlapping windows will show up and can't record across displays.
This option may not be available for hybrid GPU laptops,
see D3DDD-Note-Laptops.md for a solution.
https://www.github.com/{GITHUB_REPOSITORY}#capture-method"""

    def __init__(self, autosplit: "AutoSplit"):
        super().__init__(autosplit)
        # Must not set statically as some laptops will throw an error
        self.desktop_duplication = d3dshot.create(capture_output="numpy")

    @override
    def get_frame(self):
        selection = self._autosplit_ref.settings_dict["capture_region"]
        hwnd = self._autosplit_ref.hwnd
        hmonitor = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
        if not hmonitor or not self.check_selected_region_exists():
            return None

        left_bounds, top_bounds, *_ = get_window_bounds(hwnd)
        self.desktop_duplication.display = next(
            display
            for display in self.desktop_duplication.displays
            if display.hmonitor == hmonitor  # fmt: skip
        )
        offset_x, offset_y, *_ = win32gui.GetWindowRect(hwnd)
        offset_x -= self.desktop_duplication.display.position["left"]
        offset_y -= self.desktop_duplication.display.position["top"]
        left = selection["x"] + offset_x + left_bounds
        top = selection["y"] + offset_y + top_bounds
        right = selection["width"] + left
        bottom = selection["height"] + top
        screenshot = self.desktop_duplication.screenshot((left, top, right, bottom))
        if screenshot is None:
            return None
        return cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGRA)
