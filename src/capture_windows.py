from __future__ import annotations
from typing import Optional, TypedDict, cast, TYPE_CHECKING
if TYPE_CHECKING:
    from AutoSplit import AutoSplit

import ctypes
import ctypes.wintypes
import d3dshot
# from winsdk.windows.graphics.capture import GraphicsCapturePicker
# from winsdk._winrt import initialize_with_window

from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QLabel

import cv2
import numpy as np
import win32con
import win32ui
import pywintypes
from win32 import win32gui
from win32typing import PyCBitmap, PyCDC

from capture_method import CaptureMethod


# This is an undocumented nFlag value for PrintWindow
PW_RENDERFULLCONTENT = 0x00000002

desktop_duplication = d3dshot.create(capture_output="numpy")


class Region(TypedDict):
    x: int
    y: int
    width: int
    height: int


def __bit_blt_capture(hwnd: int, selection: Region, render_full_content: bool = False):
    image: Optional[cv2.ndarray] = None
    # If the window closes while it's being manipulated, it could cause a crash
    try:
        window_dc: int = win32gui.GetWindowDC(hwnd)
        # https://github.com/kaluluosi/pywin32-stubs/issues/6
        dc_object: PyCDC = win32ui.CreateDCFromHandle(window_dc)  # type: ignore

        # Causes a 10-15x performance drop. But allows recording hardware accelerated windows
        if render_full_content:
            ctypes.windll.user32.PrintWindow(hwnd, dc_object.GetSafeHdc(), PW_RENDERFULLCONTENT)

        compatible_dc = dc_object.CreateCompatibleDC()
        bitmap: PyCBitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(dc_object, selection["width"], selection["height"])
        compatible_dc.SelectObject(bitmap)
        compatible_dc.BitBlt(
            (0, 0),
            (selection["width"], selection["height"]),
            dc_object,
            (selection["x"], selection["y"]),
            win32con.SRCCOPY)
        image = np.frombuffer(cast(bytes, bitmap.GetBitmapBits(True)), dtype="uint8")
        image.shape = (selection["height"], selection["width"], 4)
    # https://github.com/kaluluosi/pywin32-stubs/issues/5
    # pylint: disable=no-member
    except (win32ui.error, pywintypes.error):  # type: ignore
        return None
    # We already obtained the image, so we can ignore errors during cleanup
    try:
        dc_object.DeleteDC()
        compatible_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, window_dc)
        win32gui.DeleteObject(bitmap.GetHandle())
    # https://github.com/kaluluosi/pywin32-stubs/issues/5
    except win32ui.error:  # type: ignore
        pass
    return image


def __d3d_capture(hwnd: int, selection: Region):
    hmonitor = ctypes.windll.user32.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
    if not hmonitor:
        return None
    desktop_duplication.display = [
        display for display
        in desktop_duplication.displays
        if display.hmonitor == hmonitor][0]
    offset_x, offset_y, *_ = win32gui.GetWindowRect(hwnd)
    offset_x -= desktop_duplication.display.position["left"]
    offset_y -= desktop_duplication.display.position["top"]
    screenshot = desktop_duplication.screenshot((
        selection["x"] + offset_x,
        selection["y"] + offset_y,
        selection["width"] + selection["x"] + offset_x,
        selection["height"] + selection["y"] + offset_y))
    return cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGRA)


# def __windows_graphics_capture(hwnd: int, selection: Region, autosplit_hwnd: int):
#     picker = GraphicsCapturePicker()
#     initialize_with_window(picker, autosplit_hwnd)
#     picker.pick_single_item_async()


def capture_region(autosplit: AutoSplit):
    """
    Captures an image of the region for a window matching the given
    parameters of the bounding box

    @param hwnd: Handle to the window being captured
    @param selection: The coordinates of the region
    @return: The image of the region in the window in BGRA format
    """
    hwnd = autosplit.hwnd
    selection = autosplit.settings_dict["capture_region"]
    capture_method = autosplit.settings_dict["capture_method"]

    # if capture_method == CaptureMethod.WINDOWS_GRAPHICS_CAPTURE:
    #     return __windows_graphics_capture(hwnd, selection, autosplit.effectiveWinId().__int__())

    if capture_method == CaptureMethod.DESKTOP_DUPLICATION:
        return __d3d_capture(hwnd, selection)

    return __bit_blt_capture(hwnd, selection, capture_method == CaptureMethod.PRINTWINDOW_RENDERFULLCONTENT)


def set_ui_image(qlabel: QLabel, image: Optional[cv2.ndarray], transparency: bool):
    if image is None:
        # Clear current pixmap if image is None. But don't clear text
        if not qlabel.text():
            qlabel.clear()
    else:
        if transparency:
            color_code = cv2.COLOR_BGRA2RGBA
            image_format = QtGui.QImage.Format.Format_RGBA8888
        else:
            color_code = cv2.COLOR_BGRA2BGR
            image_format = QtGui.QImage.Format.Format_BGR888

        capture = cv2.cvtColor(image, color_code)
        height, width, channels = capture.shape
        qimage = QtGui.QImage(capture.data, width, height, width * channels, image_format)
        qlabel.setPixmap(QtGui.QPixmap(qimage).scaled(
            qlabel.size(),
            QtCore.Qt.AspectRatioMode.IgnoreAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation))
