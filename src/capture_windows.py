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

from capture_method import CaptureMethod
from screen_region import WindowsGraphicsCapture

if TYPE_CHECKING:
    from AutoSplit import AutoSplit

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
        window_dc = win32gui.GetWindowDC(hwnd)
        dc_object = win32ui.CreateDCFromHandle(window_dc)

        # Causes a 10-15x performance drop. But allows recording hardware accelerated windows
        if render_full_content:
            ctypes.windll.user32.PrintWindow(hwnd, dc_object.GetSafeHdc(), PW_RENDERFULLCONTENT)

        compatible_dc = dc_object.CreateCompatibleDC()
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(dc_object, selection["width"], selection["height"])
        compatible_dc.SelectObject(bitmap)
        compatible_dc.BitBlt(
            (0, 0),
            (selection["width"], selection["height"]),
            dc_object,
            (selection["x"], selection["y"]),
            win32con.SRCCOPY)
        image = np.frombuffer(cast(bytes, bitmap.GetBitmapBits(True)), dtype=np.uint8)
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
    return cv2.cvtColor(screenshot, cv2.COLOR_RGBA2BGRA)


def __windows_graphics_capture(windows_graphics_capture: Optional[WindowsGraphicsCapture], selection: Region):
    if not windows_graphics_capture or not windows_graphics_capture.frame_pool:
        return None, False

    frame = windows_graphics_capture.frame_pool.try_get_next_frame()
    if not frame:
        return windows_graphics_capture.last_captured_frame, True

    async def coroutine():
        async_operation = SoftwareBitmap.create_copy_from_surface_async(frame.surface)
        return await async_operation if async_operation else None
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
        raise ValueError("Unable to convert Direct3D11CaptureFrame to SoftwareBitmap.")
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
    image = image[
        selection["y"]:selection["height"] + selection["y"],
        selection["x"]:selection["width"] + selection["x"],
    ]
    return cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)


def capture_region(autosplit: AutoSplit) -> tuple[Optional[cv2.ndarray], bool]:
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

    if capture_method == CaptureMethod.VIDEO_CAPTURE_DEVICE:
        return __camera_capture(autosplit.capture_device, selection), False

    if capture_method == CaptureMethod.WINDOWS_GRAPHICS_CAPTURE:
        return __windows_graphics_capture(autosplit.windows_graphics_capture, selection)

    if capture_method == CaptureMethod.DESKTOP_DUPLICATION:
        return __d3d_capture(hwnd, selection), False

    return __bit_blt_capture(hwnd, selection, capture_method == CaptureMethod.PRINTWINDOW_RENDERFULLCONTENT), False


def set_ui_image(qlabel: QLabel, image: Optional[cv2.ndarray], transparency: bool):
    if image is None or not image.size:
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
