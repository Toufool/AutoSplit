from __future__ import annotations

import ctypes
import ctypes.wintypes
from typing import TYPE_CHECKING, cast

import cv2
import d3dshot
import win32con
from win32 import win32gui

from capture_method.BitBltCaptureMethod import BitBltCaptureMethod
from utils import get_window_bounds

if TYPE_CHECKING:
    from AutoSplit import AutoSplit

desktop_duplication = d3dshot.create(capture_output="numpy")


class DesktopDuplicationCaptureMethod(BitBltCaptureMethod):  # pylint: disable=too-few-public-methods
    def get_frame(self, autosplit: AutoSplit):
        selection = autosplit.settings_dict["capture_region"]
        hwnd = autosplit.hwnd
        hmonitor = ctypes.windll.user32.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
        if not hmonitor or not self.check_selected_region_exists(autosplit):
            return None, False

        left_bounds, top_bounds, *_ = get_window_bounds(hwnd)
        desktop_duplication.display = [
            display for display
            in desktop_duplication.displays
            if display.hmonitor == hmonitor
        ][0]
        offset_x, offset_y, *_ = win32gui.GetWindowRect(hwnd)
        offset_x -= desktop_duplication.display.position["left"]
        offset_y -= desktop_duplication.display.position["top"]
        left = selection["x"] + offset_x + left_bounds
        top = selection["y"] + offset_y + top_bounds
        right = selection["width"] + left
        bottom = selection["height"] + top
        screenshot = desktop_duplication.screenshot((left, top, right, bottom))
        if screenshot is None:
            return None, False
        return cv2.cvtColor(cast(cv2.Mat, screenshot), cv2.COLOR_RGBA2BGRA), False
