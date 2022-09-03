from __future__ import annotations

import ctypes
import ctypes.wintypes
from typing import TYPE_CHECKING, cast

import cv2
import numpy as np
import pywintypes
import win32con
import win32ui
from win32 import win32gui

from capture_method.interface import CaptureMethodInterface
from utils import get_window_bounds, is_valid_hwnd

if TYPE_CHECKING:
    from AutoSplit import AutoSplit

# This is an undocumented nFlag value for PrintWindow
PW_RENDERFULLCONTENT = 0x00000002


class BitBltCaptureMethod(CaptureMethodInterface):
    _render_full_content = False

    def get_frame(self, autosplit: AutoSplit) -> tuple[cv2.Mat | None, bool]:
        selection = autosplit.settings_dict["capture_region"]
        hwnd = autosplit.hwnd
        image: cv2.Mat | None = None
        if not self.check_selected_region_exists(autosplit):
            return None, False

        # If the window closes while it's being manipulated, it could cause a crash
        try:
            window_dc = win32gui.GetWindowDC(hwnd)
            dc_object = win32ui.CreateDCFromHandle(window_dc)

            # Causes a 10-15x performance drop. But allows recording hardware accelerated windows
            if self._render_full_content:
                ctypes.windll.user32.PrintWindow(hwnd, dc_object.GetSafeHdc(), PW_RENDERFULLCONTENT)

            # On Windows there is a shadow around the windows that we need to account for.
            left_bounds, top_bounds, *_ = get_window_bounds(hwnd)

            compatible_dc = dc_object.CreateCompatibleDC()
            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(dc_object, selection["width"], selection["height"])
            compatible_dc.SelectObject(bitmap)
            compatible_dc.BitBlt(
                (0, 0),
                (selection["width"], selection["height"]),
                dc_object,
                (selection["x"] + left_bounds, selection["y"] + top_bounds),
                win32con.SRCCOPY)
            image = np.frombuffer(cast(bytes, bitmap.GetBitmapBits(True)), dtype=np.uint8)
            image.shape = (selection["height"], selection["width"], 4)
        except (win32ui.error, pywintypes.error):
            return None, False
        # We already obtained the image, so we can ignore errors during cleanup
        try:
            dc_object.DeleteDC()
            dc_object.DeleteDC()
            compatible_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, window_dc)
            win32gui.DeleteObject(bitmap.GetHandle())
        except win32ui.error:
            pass
        return image, False

    def recover_window(self, captured_window_title: str, autosplit: AutoSplit):
        hwnd = win32gui.FindWindow(None, captured_window_title)
        if not is_valid_hwnd(hwnd):
            return False
        autosplit.hwnd = hwnd
        return self.check_selected_region_exists(autosplit)
