from __future__ import annotations
from typing import Optional, cast

import ctypes
import ctypes.wintypes
from dataclasses import dataclass
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QLabel

import cv2
import numpy as np
import win32con
import win32ui
import pywintypes
from win32 import win32gui
from win32typing import PyCBitmap, PyCDC

# This is an undocumented nFlag value for PrintWindow
PW_RENDERFULLCONTENT = 0x00000002


@dataclass
class Rect(ctypes.wintypes.RECT):
    """
    Overrides `ctypes.wintypes.RECT` to replace c_long with int for math operators
    """
    left: int = -1  # type: ignore
    top: int = -1  # type: ignore
    right: int = -1  # type: ignore
    bottom: int = -1  # type: ignore


def capture_region(hwnd: int, selection: Rect, print_window: bool):
    """
    Captures an image of the region for a window matching the given
    parameters of the bounding box

    @param hwnd: Handle to the window being captured
    @param selection: The coordinates of the region
    @return: The image of the region in the window in BGRA format
    """

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
        return None

    image = np.frombuffer(cast(bytes, bitmap.GetBitmapBits(True)), dtype="uint8")
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
