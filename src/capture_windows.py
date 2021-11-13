from typing import Dict

from ctypes import windll
from ctypes.wintypes import LONG, RECT, HBITMAP
from packaging import version
from win32 import win32gui
import platform
import numpy as np
import win32ui
import win32con


# This is an undocumented nFlag value for PrintWindow
PW_RENDERFULLCONTENT = 0x00000002
accelerated_windows: Dict[int, bool] = {}
is_windows_11 = version.parse(platform.version()) >= version.parse("10.0.22000")


def capture_region(hwnd: int, rect: RECT):
    """
    Captures an image of the region for a window matching the given
    parameters of the bounding box

    @param hwnd: Handle to the window being captured
    @param rect: The coordinates of the region
    @return: The image of the region in the window in BGRA format
    """

    # Windows 11 has some jank, and we're not ready to fully investigate it
    # for now let's ensure it works at the cost of performance
    is_accelerated_window = is_windows_11 or accelerated_windows.get(hwnd)

    # The window type is not yet known, let's find out!
    if is_accelerated_window is None:
        # We need to get the image at least once to check if it's full black
        image = __get_image(hwnd, rect, False)
        # TODO check for first non-black pixel, no need to iterate through the whole image
        is_accelerated_window = not np.count_nonzero(image)
        accelerated_windows[hwnd] = is_accelerated_window
        return __get_image(hwnd, rect, True) if is_accelerated_window else image

    return __get_image(hwnd, rect, is_accelerated_window)


def __get_image(hwnd: int, rect: RECT, print_window=False):
    width: LONG = rect.right - rect.left
    height: LONG = rect.bottom - rect.top
    windowDC: int = win32gui.GetWindowDC(hwnd)
    dcObject = win32ui.CreateDCFromHandle(windowDC)

    # Causes a 10-15x performance drop. But allows recording hardware accelerated windows
    if (print_window):
        windll.user32.PrintWindow(hwnd, dcObject.GetSafeHdc(), PW_RENDERFULLCONTENT)

    compatibleDC = dcObject.CreateCompatibleDC()
    bitmap: HBITMAP = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(dcObject, width, height)
    compatibleDC.SelectObject(bitmap)
    compatibleDC.BitBlt((0, 0), (width, height), dcObject, (rect.left, rect.top), win32con.SRCCOPY)

    image: np._BufferType = np.frombuffer(bitmap.GetBitmapBits(True), dtype='uint8')
    image.shape = (height, width, 4)

    dcObject.DeleteDC()
    compatibleDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, windowDC)
    win32gui.DeleteObject(bitmap.GetHandle())

    return image
