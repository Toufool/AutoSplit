import os
import sys
from math import ceil
from typing import TYPE_CHECKING

import cv2
import numpy as np
from cv2.typing import MatLike
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtTest import QTest
from typing_extensions import override

import error_messages
from utils import (
    BGR_CHANNEL_COUNT,
    MAXBYTE,
    ImageShape,
    auto_split_directory,
    get_window_bounds,
    is_valid_hwnd,
    is_valid_image,
)

if sys.platform == "win32":
    import ctypes

    from win32 import win32gui
    from win32con import SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN, SM_XVIRTUALSCREEN, SM_YVIRTUALSCREEN
    from winsdk._winrt import initialize_with_window
    from winsdk.windows.foundation import AsyncStatus, IAsyncOperation
    from winsdk.windows.graphics.capture import GraphicsCaptureItem, GraphicsCapturePicker
    user32 = ctypes.windll.user32

if sys.platform == "linux":
    from Xlib.display import Display

    # This variable may be missing in desktopless environment. x11 | wayland
    os.environ.setdefault("XDG_SESSION_TYPE", "x11")

# Must come after the linux XDG_SESSION_TYPE environment variable is set
from pywinctl import getTopWindowAt

if TYPE_CHECKING:
    from AutoSplit import AutoSplit

GNOME_DESKTOP_ICONS_EXTENSION = "@!0,0;BDHF"
ALIGN_REGION_THRESHOLD = 0.9
BORDER_WIDTH = 2
SUPPORTED_IMREAD_FORMATS = [
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
]
"""https://docs.opencv.org/4.8.0/d4/da8/group__imgcodecs.html#imread"""
IMREAD_EXT_FILTER = (
    "All Files ("
    + " ".join([f"{extensions}" for _, extensions in SUPPORTED_IMREAD_FORMATS])
    + ");;"
    + ";;".join([f"{imread_format} ({extensions})" for imread_format, extensions in SUPPORTED_IMREAD_FORMATS])
)


def get_top_window_at(x: int, y: int):
    """Give QWidget time to disappear to avoid Xlib.error.BadDrawable on Linux."""
    if sys.platform == "linux":
        # Tested in increments of 10ms on my Pop!_OS 22.04 VM
        QTest.qWait(80)
    return getTopWindowAt(x, y)


# TODO: For later as a different picker option
def __select_graphics_item(autosplit: "AutoSplit"):  # pyright: ignore [reportUnusedFunction]
    """Uses the built-in GraphicsCapturePicker to select the Window."""
    if sys.platform != "win32":
        raise OSError

    def callback(async_operation: IAsyncOperation[GraphicsCaptureItem], async_status: AsyncStatus):
        try:
            if async_status != AsyncStatus.COMPLETED:
                return
        except SystemError as exception:
            # HACK: can happen when closing the GraphicsCapturePicker
            if str(exception).endswith("returned a result with an error set"):
                return
            raise
        item = async_operation.get_results()
        if not item:
            return
        autosplit.settings_dict["captured_window_title"] = item.display_name
        autosplit.capture_method.reinitialize()

    picker = GraphicsCapturePicker()
    initialize_with_window(picker, int(autosplit.effectiveWinId()))
    async_operation = picker.pick_single_item_async()
    # None if the selection is canceled
    if async_operation:
        async_operation.completed = callback


def select_region(autosplit: "AutoSplit"):
    # Create a screen selector widget
    selector = SelectRegionWidget()

    # Need to wait until the user has selected a region using the widget
    # before moving on with selecting the window settings
    while True:
        width = selector.width()
        height = selector.height()
        x = selector.x()
        y = selector.y()
        if width > 0 and height > 0:
            break
        QTest.qWait(1)
    del selector

    window = get_top_window_at(x, y)
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
        left=x - offset_x,
        top=y - offset_y,
        width=width,
        height=height,
    )


def select_window(autosplit: "AutoSplit"):
    # Create a screen selector widget
    selector = SelectWindowWidget()

    # Need to wait until the user has selected a region using the widget before moving on with
    # selecting the window settings
    while True:
        x = selector.x()
        y = selector.y()
        if x and y:
            break
        QTest.qWait(1)
    del selector

    window = get_top_window_at(x, y)
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
        left=border_width,
        top=titlebar_with_border_height,
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

    template = cv2.imread(template_filename, cv2.IMREAD_UNCHANGED)
    # Add alpha channel to template if it's missing.
    if template.shape[ImageShape.Channels] == BGR_CHANNEL_COUNT:
        template = cv2.cvtColor(template, cv2.COLOR_BGR2BGRA)

    # Validate template is a valid image file
    if not is_valid_image(template):
        error_messages.image_validity()
        return

    # Obtaining the capture of a region which contains the
    # subregion being searched for to align the image.
    capture = autosplit.capture_method.last_captured_image

    if not is_valid_image(capture):
        error_messages.region()
        return

    best_match, best_height, best_width, best_loc = __test_alignment(capture, template)

    # Go ahead and check if this satisfies our requirement before setting the region
    # We don't want a low similarity image to be aligned.
    if best_match < ALIGN_REGION_THRESHOLD:
        error_messages.alignment_not_matched()
        return

    # The new region can be defined by using the min_loc point and the best_height and best_width of the template.
    __set_region_values(
        autosplit,
        left=autosplit.settings_dict["capture_region"]["x"] + best_loc[0],
        top=autosplit.settings_dict["capture_region"]["y"] + best_loc[1],
        width=best_width,
        height=best_height,
    )


def __set_region_values(autosplit: "AutoSplit", left: int, top: int, width: int, height: int):
    autosplit.settings_dict["capture_region"]["x"] = left
    autosplit.settings_dict["capture_region"]["y"] = top
    autosplit.settings_dict["capture_region"]["width"] = width
    autosplit.settings_dict["capture_region"]["height"] = height

    autosplit.x_spinbox.setValue(left)
    autosplit.y_spinbox.setValue(top)
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
    best_loc = (0, 0)

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


def validate_before_parsing(autosplit: "AutoSplit", show_error: bool = True, check_empty_directory: bool = True):
    error = None
    if not autosplit.settings_dict["split_image_directory"]:
        error = error_messages.split_image_directory
    elif not os.path.isdir(autosplit.settings_dict["split_image_directory"]):
        error = error_messages.split_image_directory_not_found
    elif check_empty_directory and not os.listdir(autosplit.settings_dict["split_image_directory"]):
        error = error_messages.split_image_directory_empty
    elif not autosplit.capture_method.check_selected_region_exists():
        error = error_messages.region
    if error and show_error:
        error()
    return not error


class BaseSelectWidget(QtWidgets.QWidget):
    _x = 0
    _y = 0

    @override
    def x(self):
        return self._x

    @override
    def y(self):
        return self._y

    def __init__(self):
        super().__init__()
        # We need to pull the monitor information to correctly draw the geometry covering all portions
        # of the user's screen. These parameters create the bounding box with left, top, width, and height
        if sys.platform == "win32":
            self.setGeometry(
                user32.GetSystemMetrics(SM_XVIRTUALSCREEN),
                user32.GetSystemMetrics(SM_YVIRTUALSCREEN),
                user32.GetSystemMetrics(SM_CXVIRTUALSCREEN),
                user32.GetSystemMetrics(SM_CYVIRTUALSCREEN),
            )
        else:
            data = Display().screen().root.get_geometry()._data  # noqa: SLF001
            self.setGeometry(
                data["x"],
                data["y"],
                data["width"],
                data["height"],
            )
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
        self._x = int(event.position().x()) + self.geometry().x()
        self._y = int(event.position().y()) + self.geometry().y()
        self.close()


class SelectRegionWidget(BaseSelectWidget):
    """
    Widget for dragging screen region
    Originated from https://github.com/harupy/snipping-tool .
    """

    _right: int = 0
    _bottom: int = 0
    __begin = QtCore.QPoint()
    __end = QtCore.QPoint()

    def __init__(self):
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))
        super().__init__()

    @override
    def height(self):
        return self._bottom - self._y

    @override
    def width(self):
        return self._right - self._x

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
            # so the added virtual screen offsets convert them back to the virtual screen coordinates
            self._x = min(self.__begin.x(), self.__end.x()) + self.geometry().x()
            self._y = min(self.__begin.y(), self.__end.y()) + self.geometry().y()
            self._right = max(self.__begin.x(), self.__end.x()) + self.geometry().x()
            self._bottom = max(self.__begin.y(), self.__end.y()) + self.geometry().y()

            self.close()

    @override
    def close(self):
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        return super().close()
