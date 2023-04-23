from __future__ import annotations

import ctypes
from typing import TYPE_CHECKING, cast

import cv2
# import d3dshot
import dxcam
import win32con
from win32 import win32gui, win32api

from capture_method import CaptureMethodBase
from utils import get_window_bounds

if TYPE_CHECKING:
    from AutoSplit import AutoSplit


class DXCamCaptureMethod(CaptureMethodBase):
    name = "DXCam Capture Method"
    short_description = "fast, but slower than Sonic"
    description = (
        "\nWork in progress description "
    )

    def __init__(self, autosplit: AutoSplit):
        super().__init__(autosplit)
        self.camera = None
        self.cached_selection = None
        self.cached_monitor = -1
        self.cached_frame = None
        self.cached_frame_cv2 = None
        self.monitor_rect = None

    def close(self, autosplit: AutoSplit):
        if self.camera is not None:
            del self.camera

    def create_camera(self, monitor):
        if self.camera is not None:
            del self.camera

        self.camera = dxcam.create(output_idx=monitor)
        return self.camera

    def get_cached_selection(self, hwnd, selection):
        do_reset = False

        temp_selection = selection.copy()

        offset_x, offset_y, *_ = win32gui.GetWindowRect(hwnd)

        temp_selection["x"] += offset_x
        temp_selection["y"] += offset_y

        if self.cached_selection != temp_selection:
            self.cached_selection = temp_selection
            do_reset = True

        return self.cached_selection, do_reset

    def monitor_handle_to_index(self, handle):
        index = -1
        for monitor in win32api.EnumDisplayMonitors():
            index += 1
            if monitor[0].handle == handle:
                return index, monitor[2]

        return -1, None

    def get_cached_monitor(self, autosplit: AutoSplit):
        hmonitor = ctypes.windll.user32.MonitorFromWindow(
            autosplit.hwnd, win32con.MONITOR_DEFAULTTONEAREST)
        index, rect = self.monitor_handle_to_index(hmonitor)
        if index == -1 or not self.check_selected_region_exists(autosplit):
            return None, False

        do_reset = False

        if self.cached_monitor != index:
            self.cached_monitor = index
            self.monitor_rect = {
                "left": rect[0],
                "top": rect[1],
                "right": rect[2],
                "bottom": rect[3],
            }
            # self.monitor_width = rect[2] - rect[0]
            # self.monitor_height = rect[3] - rect[1]
            do_reset = True

        return self.cached_monitor, do_reset

    def get_latest_frame_cached(self, frame):
        if frame is not self.cached_frame:
            self.cached_frame = frame
            self.cached_frame_cv2 = cv2.cvtColor(cast(cv2.Mat, frame), cv2.COLOR_RGBA2BGRA)

        return self.cached_frame_cv2

    def get_frame(self, autosplit: AutoSplit):
        monitor, do_reset_monitor = self.get_cached_monitor(autosplit)
        selection, do_reset_selection = self.get_cached_selection(
            autosplit.hwnd,
            autosplit.settings_dict["capture_region"])

        if do_reset_monitor:
            self.create_camera(monitor)
            do_reset_selection = True

        if do_reset_selection:
            self.camera.stop()

            left = max()
            top = max()

            right = min(selection["x"] + selection["width"], self.monitor_rect["right"])
            bottom = min(selection["y"] + selection["height"], self.monitor_rect["bottom"])

            self.camera.start(region=(
                selection["x"],
                selection["y"],
                right,
                bottom
            ))

        screenshot = self.camera.get_latest_frame()
        if screenshot is None:
            return None, False

        return self.get_latest_frame_cached(screenshot), False
