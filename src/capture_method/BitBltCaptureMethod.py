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

from capture_method.CaptureMethodBase import CaptureMethodBase
from utils import RGBA_CHANNEL_COUNT, get_window_bounds, is_valid_hwnd, try_delete_dc

if TYPE_CHECKING:
    from AutoSplit import AutoSplit

# This is an undocumented nFlag value for PrintWindow
PW_RENDERFULLCONTENT = 0x00000002


class BitBltCaptureMethod(CaptureMethodBase):
    name = "BitBlt"
    short_description = "fastest, least compatible"
    description = (
        "\nThe best option when compatible. But it cannot properly record "
        + "\nOpenGL, Hardware Accelerated or Exclusive Fullscreen windows. "
        + "\nThe smaller the selected region, the more efficient it is. "
    )

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
                win32con.SRCCOPY,
            )
            image = np.frombuffer(cast(bytes, bitmap.GetBitmapBits(True)), dtype=np.uint8)
            image.shape = (selection["height"], selection["width"], RGBA_CHANNEL_COUNT)
        except (win32ui.error, pywintypes.error):
            # Invalid handle or the window was closed while it was being manipulated
            return None, False

        # Cleanup DC and handle
        try_delete_dc(dc_object)
        try_delete_dc(compatible_dc)
        win32gui.ReleaseDC(hwnd, window_dc)
        win32gui.DeleteObject(bitmap.GetHandle())
        return image, False

    def recover_window(self, captured_window_title: str, autosplit: AutoSplit):
        hwnd = win32gui.FindWindow(None, captured_window_title)
        if not is_valid_hwnd(hwnd):
            return False
        autosplit.hwnd = hwnd
        return self.check_selected_region_exists(autosplit)
