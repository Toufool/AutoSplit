import sys
from math import ceil
from typing import TYPE_CHECKING, override

import cv2
import numpy as np
from cv2.typing import MatLike, Point
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtTest import QTest
from pywinctl import getTopWindowAt

import error_messages
from capture_method import Region
from utils import (
    BGR_CHANNEL_COUNT,
    MAXBYTE,
    ImageShape,
    auto_split_directory,
    get_window_bounds,
    imread,
    is_valid_hwnd,
    is_valid_image,
)

if sys.platform == "win32":
    import win32api
    import win32gui
    from win32con import (
        SM_CXVIRTUALSCREEN,
        SM_CYVIRTUALSCREEN,
        SM_XVIRTUALSCREEN,
        SM_YVIRTUALSCREEN,
    )

if sys.platform == "linux":
    from Xlib.display import Display

if TYPE_CHECKING:
    from AutoSplit import AutoSplit

GNOME_DESKTOP_ICONS_EXTENSION = "@!0,0;BDHF"
ALIGN_REGION_THRESHOLD = 0.9
BORDER_WIDTH = 2
SUPPORTED_IMREAD_FORMATS = (
    ("Windows bitmaps", "*.bmp *.dib"),
    ("JPEG files", "*.jpeg *.jpg *.jpe"),
    ("JPEG 2000 files", "*.jp2"),
    ("Portable Network Graphics", "*.png"),
    ("WebP", "*.webp"),
    ("AVIF", "*.avif"),
    ("Portable image format", "*.pbm *.pgm *.ppm *.pxm *.pnm"),
    ("PFM files", "*.pfm"),
    ("Sun rasters", "*.sr *.ras"),
    ("TIFF files", "*.tiff *.tif"),
    ("OpenEXR Image files", "*.exr"),
    ("Radiance HDR", "*.hdr *.pic"),
)
"""https://docs.opencv.org/4.8.0/d4/da8/group__imgcodecs.html#imread"""
IMREAD_EXT_FILTER = (
    "All Files ("
    + " ".join(f"{extensions}" for _, extensions in SUPPORTED_IMREAD_FORMATS)
    + ");;"
    + ";;".join(
        f"{imread_format} ({extensions})" for imread_format, extensions in SUPPORTED_IMREAD_FORMATS
    )
)


def get_top_window_at(x: int, y: int):
    """Give QWidget time to disappear to avoid Xlib.error.BadDrawable on Linux."""
    if sys.platform == "linux":
        # Tested in increments of 10ms on my Pop!_OS 22.04 VM
        QTest.qWait(80)
    return getTopWindowAt(x, y)


# TODO: For later as a different picker option
# def __select_graphics_item(autosplit: "AutoSplit"):
#     """Uses the built-in GraphicsCapturePicker to select the Window."""
#     if sys.platform != "win32":
#         raise OSError
#     from winrt._winrt import initialize_with_window
#     from winrt.windows.foundation import AsyncStatus, IAsyncOperation
#     from winrt.windows.graphics.capture import GraphicsCaptureItem, GraphicsCapturePicker
#
#     def callback(
#         async_operation: IAsyncOperation[GraphicsCaptureItem],
#         async_status: AsyncStatus,
#     ):
#         try:
#             if async_status != AsyncStatus.COMPLETED:
#                 return
#         except SystemError as exception:
#             # HACK: can happen when closing the GraphicsCapturePicker
#             if str(exception).endswith("returned a result with an error set"):
#                 return
#             raise
#         item = async_operation.get_results()
#         if not item:
#             return
#         autosplit.settings_dict["captured_window_title"] = item.display_name
#         autosplit.capture_method.reinitialize()
#
#     picker = GraphicsCapturePicker()
#     initialize_with_window(picker, autosplit.effectiveWinId())
#     async_operation = picker.pick_single_item_async()
#     # None if the selection is canceled
#     if async_operation:
#         async_operation.completed = callback


def select_region(autosplit: "AutoSplit"):
    # Create a screen selector widget
    selector = SelectRegionWidget()

    # Need to wait until the user has selected a region using the widget
    # before moving on with selecting the window settings
    while not selector.isHidden():
        QTest.qWait(1)
    selection = selector.selection
    del selector
    if selection is None:
        return  # No selection done

    window = get_top_window_at(selection["x"], selection["y"])
    if not window:
        error_messages.region()
        return
    hwnd = window.getHandle()
    window_text = window.title
    if not is_valid_hwnd(hwnd) or not window_text:
        error_messages.region()
        return

    autosplit.hwnd = hwnd
    autosplit.settings_dict["captured_window_title"] = window_text
    autosplit.capture_method.reinitialize()

    if sys.platform == "win32":
        left_bounds, top_bounds, *_ = get_window_bounds(hwnd)
        window_x, window_y, *_ = win32gui.GetWindowRect(hwnd)
        offset_x = window_x + left_bounds
        offset_y = window_y + top_bounds
    else:
        data = window._xWin.translate_coords(autosplit.hwnd, 0, 0)._data  # pyright:ignore[reportPrivateUsage] # noqa: SLF001
        offset_x = data["x"]
        offset_y = data["y"]

    __set_region_values(
        autosplit,
        x=selection["x"] - offset_x,
        y=selection["y"] - offset_y,
        width=selection["width"],
        height=selection["height"],
    )


def select_window(autosplit: "AutoSplit"):
    # Create a screen selector widget
    selector = SelectWindowWidget()

    # Need to wait until the user has selected a region using the widget before moving on with
    # selecting the window settings
    while not selector.isHidden():
        QTest.qWait(1)
    selection = selector.selection
    del selector
    if selection is None:
        return  # No selection done

    window = get_top_window_at(selection["x"], selection["y"])
    if not window:
        error_messages.region()
        return
    hwnd = window.getHandle()
    window_text = window.title
    if not is_valid_hwnd(hwnd) or not window_text:
        error_messages.region()
        return

    autosplit.hwnd = hwnd
    autosplit.settings_dict["captured_window_title"] = window_text
    autosplit.capture_method.reinitialize()

    if sys.platform == "win32":
        # Exlude the borders and titlebar from the window selection. To only get the client area.
        _, __, window_width, window_height = get_window_bounds(hwnd)
        _, __, client_width, client_height = win32gui.GetClientRect(hwnd)
        border_width = ceil((window_width - client_width) / 2)
        titlebar_with_border_height = window_height - client_height - border_width
    else:
        data = window._xWin.get_geometry()._data  # pyright:ignore[reportPrivateUsage] # noqa: SLF001
        client_height = data["height"]
        client_width = data["width"]
        border_width = data["border_width"]
        titlebar_with_border_height = border_width

    __set_region_values(
        autosplit,
        x=border_width,
        y=titlebar_with_border_height,
        width=client_width,
        height=client_height - border_width * 2,
    )


def align_region(autosplit: "AutoSplit"):
    # Check to see if a region has been set
    if not autosplit.capture_method.check_selected_region_exists():
        error_messages.region()
        return
    # This is the image used for aligning the capture region to the best fit for the user.
    template_filename = QtWidgets.QFileDialog.getOpenFileName(
        autosplit,
        "Select Reference Image",
        autosplit.settings_dict["split_image_directory"] or auto_split_directory,
        IMREAD_EXT_FILTER,
    )[0]

    # Return if the user presses cancel
    if not template_filename:
        return

    template = imread(template_filename, cv2.IMREAD_UNCHANGED)
    # Add alpha channel to template if it's missing.
    if template.shape[ImageShape.Channels] == BGR_CHANNEL_COUNT:
        template = cv2.cvtColor(template, cv2.COLOR_BGR2BGRA)

    # Validate template is a valid image file
    if not is_valid_image(template):
        error_messages.image_validity()
        return

    # Obtaining the capture of a region which contains the
    # subregion being searched for to align the image.
    capture = autosplit.capture_method.get_frame()

    if not is_valid_image(capture):
        error_messages.region()
        return

    best_match, best_height, best_width, best_loc = __test_alignment(capture, template)

    # Go ahead and check if this satisfies our requirement before setting the region
    # We don't want a low similarity image to be aligned.
    if best_match < ALIGN_REGION_THRESHOLD:
        error_messages.alignment_not_matched()
        return

    # The new region can be defined by using the min_loc point
    # and the best_height and best_width of the template.
    __set_region_values(
        autosplit,
        x=autosplit.settings_dict["capture_region"]["x"] + best_loc[0],
        y=autosplit.settings_dict["capture_region"]["y"] + best_loc[1],
        width=best_width,
        height=best_height,
    )


def __set_region_values(autosplit: "AutoSplit", x: int, y: int, width: int, height: int):
    autosplit.settings_dict["capture_region"]["x"] = x
    autosplit.settings_dict["capture_region"]["y"] = y
    autosplit.settings_dict["capture_region"]["width"] = width
    autosplit.settings_dict["capture_region"]["height"] = height

    autosplit.x_spinbox.setValue(x)
    autosplit.y_spinbox.setValue(y)
    autosplit.width_spinbox.setValue(width)
    autosplit.height_spinbox.setValue(height)


def __test_alignment(capture: MatLike, template: MatLike):
    """
    Obtain the best matching point for the template within the
    capture. This assumes that the template is actually smaller
    than the dimensions of the capture. Since we are using SQDIFF
    the best match will be the min_val which is located at min_loc.
    The best match found in the image, set everything to 0 by default
    so that way the first match will overwrite these values.
    """
    best_match = 0.0
    best_height = 0
    best_width = 0
    best_loc: Point = (0, 0)

    # This tests 50 images scaled from 20% to 300% of the original template size
    for scale in np.linspace(0.2, 3, num=56):
        width = int(template.shape[ImageShape.X] * scale)
        height = int(template.shape[ImageShape.Y] * scale)

        # The template can not be larger than the capture
        if width > capture.shape[ImageShape.X] or height > capture.shape[ImageShape.Y]:
            continue

        resized = cv2.resize(template, (width, height), interpolation=cv2.INTER_NEAREST)

        result = cv2.matchTemplate(capture, resized, cv2.TM_SQDIFF)
        min_val, _, min_loc, *_ = cv2.minMaxLoc(result)

        # The maximum value for SQ_DIFF is dependent on the size of the template
        # we need this value to normalize it from 0.0 to 1.0
        max_error = resized.size * MAXBYTE * MAXBYTE
        similarity = 1 - (min_val / max_error)

        # Check if the similarity was good enough to get alignment
        if similarity > best_match:
            best_match = similarity
            best_width = width
            best_height = height
            best_loc = min_loc
    return best_match, best_height, best_width, best_loc


class BaseSelectWidget(QtWidgets.QWidget):
    selection: Region | None = None

    def __init__(self):
        super().__init__()
        # We need to pull the monitor information to correctly draw
        # the geometry covering all portions of the user's screen.
        # These parameters create the bounding box with left, top, width, and height
        if sys.platform == "win32":
            x = win32api.GetSystemMetrics(SM_XVIRTUALSCREEN)
            y = win32api.GetSystemMetrics(SM_YVIRTUALSCREEN)
            width = win32api.GetSystemMetrics(SM_CXVIRTUALSCREEN)
            height = win32api.GetSystemMetrics(SM_CYVIRTUALSCREEN)
        else:
            data = Display().screen().root.get_geometry()._data  # noqa: SLF001
            x = data["x"]
            y = data["y"]
            width = data["width"]
            height = data["height"]
        self.setGeometry(x, y, width, height)
        self.setFixedSize(width, height)  # Prevent move/resizing on Linux
        self.setWindowTitle(type(self).__name__)
        self.setWindowOpacity(0.5)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.show()

    @override
    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.close()


class SelectWindowWidget(BaseSelectWidget):
    """Widget to select a window and obtain its bounds."""

    @override
    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        x = int(event.position().x()) + self.geometry().x()
        y = int(event.position().y()) + self.geometry().y()
        self.selection = Region(x=x, y=y, width=0, height=0)
        self.close()


class SelectRegionWidget(BaseSelectWidget):
    """
    Widget for dragging screen region
    Originated from https://github.com/harupy/snipping-tool .
    """

    __begin = QtCore.QPoint()
    __end = QtCore.QPoint()

    def __init__(self):
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))
        super().__init__()

    @override
    def paintEvent(self, event: QtGui.QPaintEvent):
        if self.__begin != self.__end:
            qpainter = QtGui.QPainter(self)
            qpainter.setPen(QtGui.QPen(QtGui.QColor("red"), BORDER_WIDTH))
            qpainter.setBrush(QtGui.QColor("opaque"))
            qpainter.drawRect(QtCore.QRect(self.__begin, self.__end))

    @override
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        self.__begin = event.position().toPoint()
        self.__end = self.__begin
        self.update()

    @override
    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        self.__end = event.position().toPoint()
        self.update()

    @override
    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        if self.__begin != self.__end:
            # The coordinates are pulled relative to the top left of the set geometry,
            # so the added virtual screen offsets convert them back to the virtual
            # screen coordinates
            left = min(self.__begin.x(), self.__end.x()) + self.geometry().x()
            top = min(self.__begin.y(), self.__end.y()) + self.geometry().y()
            right = max(self.__begin.x(), self.__end.x()) + self.geometry().x()
            bottom = max(self.__begin.y(), self.__end.y()) + self.geometry().y()

            self.selection = Region(x=left, y=top, width=right - left, height=bottom - top)
            self.close()

    @override
    def close(self):
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        return super().close()
