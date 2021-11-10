from ctypes import windll
from ctypes.wintypes import LONG, RECT
from win32 import win32gui
import numpy as np
import win32ui
import win32con

# This is an undocumented nFlag value for PrintWindow
PW_RENDERFULLCONTENT = 0x00000002


def capture_region(hwnd: int, rect: RECT):
    """
    Captures an image of the region for a window matching the given
    parameters of the bounding box

    @param hwnd: Handle to the window being captured
    @param rect: The coordinates of the region
    @return: The image of the region in the window in BGRA format
    """

    width: LONG = rect.right - rect.left
    height: LONG = rect.bottom - rect.top

    windowDC = win32gui.GetWindowDC(hwnd)
    dcObject = win32ui.CreateDCFromHandle(windowDC)
    compatibleDC = dcObject.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(dcObject, width, height)
    compatibleDC.SelectObject(bmp)
    compatibleDC.BitBlt((0, 0), (width, height), dcObject, (rect.left, rect.top), win32con.SRCCOPY)

    # Force render full content through PrintWindow. Workaround to capture hardware accelerated windows
    windll.user32.PrintWindow(hwnd, dcObject.GetSafeHdc(), PW_RENDERFULLCONTENT)

    img: np._BufferType = np.frombuffer(bmp.GetBitmapBits(True), dtype='uint8')
    img.shape = (height, width, 4)

    dcObject.DeleteDC()
    compatibleDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, windowDC)
    win32gui.DeleteObject(bmp.GetHandle())

    return img
