from __future__ import annotations
from typing import cast

import ctypes
import ctypes.wintypes
import platform
from dataclasses import dataclass

import cv2
import numpy as np
import win32con
import win32ui
import pywintypes
from packaging import version
from win32 import win32gui
from win32typing import PyCBitmap, PyCDC

# This is an undocumented nFlag value for PrintWindow
PW_RENDERFULLCONTENT = 0x00000002
accelerated_windows: dict[int, bool] = {}
is_windows_11 = version.parse(platform.version()) >= version.parse("10.0.22000")


# ctypes.wintypes.RECT has c_long which doesn't have math operators implemented
@dataclass
class Rect(ctypes.wintypes.RECT):
    left: int = -1  # type: ignore
    top: int = -1  # type: ignore
    right: int = -1  # type: ignore
    bottom: int = -1  # type: ignore


def capture_region(hwnd: int, selection: Rect, force_print_window: bool):
    """
    Captures an image of the region for a window matching the given
    parameters of the bounding box

    @param hwnd: Handle to the window being captured
    @param selection: The coordinates of the region
    @return: The image of the region in the window in BGRA format
    """

    # Windows 11 has some jank, and we're not ready to fully investigate it
    # for now let's ensure it works at the cost of performance
    is_accelerated_window = force_print_window or is_windows_11 or accelerated_windows.get(hwnd)

    # The window type is not yet known, let's find out!
    if is_accelerated_window is None:
        # We need to get the image at least once to check if it's full black
        image = __get_image(hwnd, selection, False)
        # TODO check for first non-black pixel, no need to iterate through the whole image
        is_accelerated_window = not np.count_nonzero(image)
        accelerated_windows[hwnd] = is_accelerated_window
        return __get_image(hwnd, selection, True) if is_accelerated_window else image

    return __get_image(hwnd, selection, is_accelerated_window)


def __get_image(hwnd: int, selection: Rect, print_window: bool = False):
    width: int = selection.right - selection.left
    height: int = selection.bottom - selection.top
    # If the window closes while it's being manipulated, it could cause a crash
    try:
        window_dc: int = win32gui.GetWindowDC(hwnd)
        # https://github.com/kaluluosi/pywin32-stubs/issues/6
        dc_object: PyCDC = win32ui.CreateDCFromHandle(window_dc)  # type: ignore

        # Causes a 10-15x performance drop. But allows recording hardware accelerated windows
        if print_window:
            ctypes.windll.user32.PrintWindow(hwnd, dc_object.GetSafeHdc(), PW_RENDERFULLCONTENT)

        compatible_dc = cast(PyCDC, dc_object.CreateCompatibleDC())
        bitmap: PyCBitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(dc_object, width, height)
        compatible_dc.SelectObject(bitmap)
        compatible_dc.BitBlt((0, 0), (width, height), dc_object, (selection.left, selection.top), win32con.SRCCOPY)
    # https://github.com/kaluluosi/pywin32-stubs/issues/5
    # pylint: disable=no-member
    except (win32ui.error, pywintypes.error):  # type: ignore
        return np.array([0, 0, 0, 1], dtype="uint8")

    image: cv2.ndarray = np.frombuffer(cast(bytes, bitmap.GetBitmapBits(True)), dtype="uint8")
    image.shape = (height, width, 4)

    try:
        dc_object.DeleteDC()
        compatible_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, window_dc)
        win32gui.DeleteObject(bitmap.GetHandle())
    # https://github.com/kaluluosi/pywin32-stubs/issues/5
    except win32ui.error:  # type: ignore
        pass

    return image
