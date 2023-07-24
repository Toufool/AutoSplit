from __future__ import annotations

import ctypes
from typing import TYPE_CHECKING, Union, cast

import cv2
import d3dshot
import numpy as np
import win32con
from typing_extensions import override
from win32 import win32gui

from capture_method.BitBltCaptureMethod import BitBltCaptureMethod
from utils import GITHUB_REPOSITORY, get_window_bounds

if TYPE_CHECKING:
    from AutoSplit import AutoSplit


class DesktopDuplicationCaptureMethod(BitBltCaptureMethod):
    name = "Direct3D Desktop Duplication"
    short_description = "slower, bound to display"
    description = (
        "\nDuplicates the desktop using Direct3D. "
        + "\nIt can record OpenGL and Hardware Accelerated windows. "
        + "\nAbout 10-15x slower than BitBlt. Not affected by window size. "
        + "\nOverlapping windows will show up and can't record across displays. "
        + "\nThis option may not be available for hybrid GPU laptops, "
        + "\nsee D3DDD-Note-Laptops.md for a solution. "
        + f"\nhttps://www.github.com/{GITHUB_REPOSITORY}#capture-method "
    )

    def __init__(self, autosplit: AutoSplit | None):
        super().__init__(autosplit)
        # Must not set statically as some laptops will throw an error
        self.desktop_duplication = d3dshot.create(capture_output="numpy")

    @override
    def get_frame(self, autosplit: AutoSplit):
        selection = autosplit.settings_dict["capture_region"]
        hwnd = autosplit.hwnd
        hmonitor = ctypes.windll.user32.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
        if not hmonitor or not self.check_selected_region_exists(autosplit):
            return None, False

        left_bounds, top_bounds, *_ = get_window_bounds(hwnd)
        self.desktop_duplication.display = next(
            display for display
            in self.desktop_duplication.displays
            if display.hmonitor == hmonitor
        )
        offset_x, offset_y, *_ = win32gui.GetWindowRect(hwnd)
        offset_x -= self.desktop_duplication.display.position["left"]
        offset_y -= self.desktop_duplication.display.position["top"]
        left = selection["x"] + offset_x + left_bounds
        top = selection["y"] + offset_y + top_bounds
        right = selection["width"] + left
        bottom = selection["height"] + top
        screenshot = cast(
            Union[np.ndarray[int, np.dtype[np.generic]], None],
            self.desktop_duplication.screenshot((left, top, right, bottom)),
        )
        if screenshot is None:
            return None, False
        return cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGRA), False
