from __future__ import annotations

import asyncio
import ctypes
import ctypes.wintypes
from typing import TYPE_CHECKING, Optional, TypedDict, cast

import cv2
import d3dshot
import numpy as np
import pywintypes
import win32con
import win32ui
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QLabel
from win32 import win32gui
from winsdk.windows.graphics.imaging import BitmapBufferAccessMode, SoftwareBitmap

from CaptureMethod import CaptureMethod
from utils import is_valid_image
from WindowsGraphicsCapture import WindowsGraphicsCapture

if TYPE_CHECKING:
    from AutoSplit import AutoSplit

# This is an undocumented nFlag value for PrintWindow
PW_RENDERFULLCONTENT = 0x00000002
DWMWA_EXTENDED_FRAME_BOUNDS = 9


desktop_duplication = d3dshot.create(capture_output="numpy")


class Region(TypedDict):
    x: int
    y: int
    width: int
    height: int


def get_window_bounds(hwnd: int):
    extended_frame_bounds = ctypes.wintypes.RECT()
    ctypes.windll.dwmapi.DwmGetWindowAttribute(
        hwnd,
        DWMWA_EXTENDED_FRAME_BOUNDS,
        ctypes.byref(extended_frame_bounds),
        ctypes.sizeof(extended_frame_bounds))

    window_rect = win32gui.GetWindowRect(hwnd)
    window_left_bounds = cast(int, extended_frame_bounds.left) - window_rect[0]
    window_top_bounds = cast(int, extended_frame_bounds.top) - window_rect[1]
    window_width = cast(int, extended_frame_bounds.right) - cast(int, extended_frame_bounds.left)
    window_height = cast(int, extended_frame_bounds.bottom) - cast(int, extended_frame_bounds.top)
    return window_left_bounds, window_top_bounds, window_width, window_height


def __bit_blt_capture(hwnd: int, selection: Region, render_full_content: bool = False):
    image: Optional[cv2.Mat] = None
    # If the window closes while it's being manipulated, it could cause a crash
    try:
        window_dc = win32gui.GetWindowDC(hwnd)
        dc_object = win32ui.CreateDCFromHandle(window_dc)

        # Causes a 10-15x performance drop. But allows recording hardware accelerated windows
        if render_full_content:
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
    # https://github.com/kaluluosi/pywin32-stubs/issues/5
    except (win32ui.error, pywintypes.error):  # pyright: ignore [reportGeneralTypeIssues] pylint: disable=no-member
        return None
    # We already obtained the image, so we can ignore errors during cleanup
    try:
        dc_object.DeleteDC()
        compatible_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, window_dc)
        win32gui.DeleteObject(bitmap.GetHandle())
    # https://github.com/kaluluosi/pywin32-stubs/issues/5
    except win32ui.error:  # pyright: ignore [reportGeneralTypeIssues]
        pass
    return image


def __d3d_capture(hwnd: int, selection: Region):
    hmonitor = ctypes.windll.user32.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
    if not hmonitor:
        return None

    left_bounds, top_bounds, *_ = get_window_bounds(hwnd)
    desktop_duplication.display = [
        display for display
        in desktop_duplication.displays
        if display.hmonitor == hmonitor][0]
    offset_x, offset_y, *_ = win32gui.GetWindowRect(hwnd)
    offset_x -= desktop_duplication.display.position["left"]
    offset_y -= desktop_duplication.display.position["top"]
    left = selection["x"] + offset_x + left_bounds
    top = selection["y"] + offset_y + top_bounds
    right = selection["width"] + left
    bottom = selection["height"] + top
    screenshot = desktop_duplication.screenshot((left, top, right, bottom))
    return cv2.cvtColor(screenshot, cv2.COLOR_RGBA2BGRA)


def __windows_graphics_capture(windows_graphics_capture: Optional[WindowsGraphicsCapture], selection: Region):
    if not windows_graphics_capture or not windows_graphics_capture.frame_pool:
        return None, False

    try:
        frame = windows_graphics_capture.frame_pool.try_get_next_frame()
    # Frame pool is closed
    except OSError:
        return None, False
    if not frame:
        return windows_graphics_capture.last_captured_frame, True

    async def coroutine():
        return await (SoftwareBitmap.create_copy_from_surface_async(frame.surface) or asyncio.sleep(0, None))
    try:
        software_bitmap = asyncio.run(coroutine())
    except SystemError as exception:
        # HACK: can happen when closing the GraphicsCapturePicker
        if str(exception).endswith("returned a result with an error set"):
            return windows_graphics_capture.last_captured_frame, True
        raise

    if not software_bitmap:
        # HACK: Can happen when starting the region selector
        return windows_graphics_capture.last_captured_frame, True
        # raise ValueError("Unable to convert Direct3D11CaptureFrame to SoftwareBitmap.")
    bitmap_buffer = software_bitmap.lock_buffer(BitmapBufferAccessMode.READ_WRITE)
    if not bitmap_buffer:
        raise ValueError("Unable to obtain the BitmapBuffer from SoftwareBitmap.")
    reference = bitmap_buffer.create_reference()
    image = np.frombuffer(cast(bytes, reference), dtype=np.uint8)
    image.shape = (windows_graphics_capture.size.height, windows_graphics_capture.size.width, 4)
    image = image[
        selection["y"]:selection["y"] + selection["height"],
        selection["x"]:selection["x"] + selection["width"],
    ]
    windows_graphics_capture.last_captured_frame = image
    return image, False


def __camera_capture(capture_device: Optional[cv2.VideoCapture], selection: Region):
    if not capture_device:
        return None
    result, image = capture_device.read()
    if not result:
        return None
    # Ensure we can't go OOB of the image
    y = min(selection["y"], image.shape[0] - 1)
    x = min(selection["x"], image.shape[1] - 1)
    image = image[
        y:selection["height"] + y,
        x:selection["width"] + x,
    ]
    return cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)


def capture_region(autosplit: AutoSplit) -> tuple[Optional[cv2.Mat], bool]:
    """
    Captures an image of the region for a window matching the given
    parameters of the bounding box

    @param hwnd: Handle to the window being captured
    @param selection: The coordinates of the region
    @return: The image of the region in the window in BGRA format
    """
    capture_method = autosplit.settings_dict["capture_method"]
    selection = autosplit.settings_dict["capture_region"]

    if capture_method == CaptureMethod.VIDEO_CAPTURE_DEVICE:
        return __camera_capture(autosplit.capture_device, selection), False

    if not win32gui.IsWindow(autosplit.hwnd):
        return None, False

    if capture_method == CaptureMethod.WINDOWS_GRAPHICS_CAPTURE:
        image, is_old_image = __windows_graphics_capture(autosplit.windows_graphics_capture, selection)
        return (None, False) \
            if is_old_image and not win32gui.IsWindow(autosplit.hwnd) \
            else (image, is_old_image)

    if capture_method == CaptureMethod.DESKTOP_DUPLICATION:
        return __d3d_capture(autosplit.hwnd, selection), False

    return __bit_blt_capture(autosplit.hwnd, selection, capture_method
                             == CaptureMethod.PRINTWINDOW_RENDERFULLCONTENT), False


def set_ui_image(qlabel: QLabel, image: Optional[cv2.Mat], transparency: bool):
    if not is_valid_image(image):
        # Clear current pixmap if no image. But don't clear text
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