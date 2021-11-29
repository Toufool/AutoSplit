from __future__ import annotations
from typing import cast, TYPE_CHECKING
if TYPE_CHECKING:
    from AutoSplit import AutoSplit

import os
import ctypes
import ctypes.wintypes
import cv2
import numpy as np
from PyQt6 import QtCore, QtGui, QtTest, QtWidgets
from win32 import win32gui
from win32con import GA_ROOT, MAXBYTE, SM_XVIRTUALSCREEN, SM_YVIRTUALSCREEN, SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN

import capture_windows
import error_messages

DWMWA_EXTENDED_FRAME_BOUNDS = 9
user32 = ctypes.windll.user32


def selectRegion(autosplit: AutoSplit):
    # Create a screen selector widget
    selector = SelectRegionWidget()

    # Need to wait until the user has selected a region using the widget before moving on with
    # selecting the window settings
    while True:
        width = selector.width()
        height = selector.height()
        if width > 0 and height > 0:
            break
        # Email sent to pyqt@riverbankcomputing.com
        QtTest.QTest.qWait(1)  # type: ignore

    # Grab the window handle from the coordinates selected by the widget
    autosplit.hwnd = cast(int, win32gui.WindowFromPoint((selector.left, selector.top)))
    # Want to pull the parent window from the window handle
    # By using GetAncestor we are able to get the parent window instead
    # of the owner window.
    while win32gui.IsChild(win32gui.GetParent(autosplit.hwnd), autosplit.hwnd):
        autosplit.hwnd = user32.GetAncestor(autosplit.hwnd, GA_ROOT)

    windowText = win32gui.GetWindowText(autosplit.hwnd)
    if autosplit.hwnd > 0 or windowText:
        autosplit.hwnd_title = windowText

    # Convert the Desktop Coordinates to Window Coordinates
    # Pull the window's coordinates relative to desktop into selection
    ctypes.windll.dwmapi.DwmGetWindowAttribute(
        autosplit.hwnd,
        ctypes.wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
        ctypes.byref(autosplit.selection),
        ctypes.sizeof(autosplit.selection))

    # On Windows 10 the windows have offsets due to invisible pixels not accounted for in DwmGetWindowAttribute
    # TODO: Since this occurs on Windows 10, is DwmGetWindowAttribute even required over GetWindowRect alone?
    # Research needs to be done to figure out why it was used it over win32gui in the first place...
    # I have a feeling it was due to a misunderstanding and not getting the correct parent window before.
    windowRect = win32gui.GetWindowRect(autosplit.hwnd)
    offset_left = autosplit.selection.left - windowRect[0]
    offset_top = autosplit.selection.top - windowRect[1]

    autosplit.selection.left = selector.left - (autosplit.selection.left - offset_left)
    autosplit.selection.top = selector.top - (autosplit.selection.top - offset_top)
    autosplit.selection.right = autosplit.selection.left + width
    autosplit.selection.bottom = autosplit.selection.top + height

    # Delete that widget since it is no longer used from here on out
    del selector

    autosplit.widthSpinBox.setValue(width)
    autosplit.heightSpinBox.setValue(height)
    autosplit.xSpinBox.setValue(autosplit.selection.left)
    autosplit.ySpinBox.setValue(autosplit.selection.top)

    # check if live image needs to be turned on or just set a single image
    autosplit.checkLiveImage()


def selectWindow(autosplit: AutoSplit):
    # Create a screen selector widget
    selector = SelectWindowWidget()

    # Need to wait until the user has selected a region using the widget before moving on with
    # selecting the window settings
    while selector.x() == -1 and selector.y() == -1:
        # Email sent to pyqt@riverbankcomputing.com
        QtTest.QTest.qWait(1)  # type: ignore

    # Grab the window handle from the coordinates selected by the widget
    autosplit.hwnd = cast(int, win32gui.WindowFromPoint((selector.x(), selector.y())))

    del selector

    if autosplit.hwnd <= 0:
        return

    # Want to pull the parent window from the window handle
    # By using GetAncestor we are able to get the parent window instead
    # of the owner window.
    while win32gui.IsChild(win32gui.GetParent(autosplit.hwnd), autosplit.hwnd):
        autosplit.hwnd = user32.GetAncestor(autosplit.hwnd, GA_ROOT)

    windowText = win32gui.GetWindowText(autosplit.hwnd)
    if autosplit.hwnd > 0 or windowText:
        autosplit.hwnd_title = windowText

    # getting window bounds
    # on windows there are some invisble pixels that are not accounted for
    # also the top bar with the window name is not accounted for
    # I hardcoded the x and y coordinates to fix this
    # This is not an ideal solution because it assumes every window will have a top bar
    selection: tuple[int, int, int, int] = win32gui.GetClientRect(autosplit.hwnd)
    autosplit.selection.left = 8
    autosplit.selection.top = 31
    autosplit.selection.right = 8 + selection[2]
    autosplit.selection.bottom = 31 + selection[3]

    autosplit.widthSpinBox.setValue(selection[2])
    autosplit.heightSpinBox.setValue(selection[3])
    autosplit.xSpinBox.setValue(autosplit.selection.left)
    autosplit.ySpinBox.setValue(autosplit.selection.top)

    autosplit.checkLiveImage()


def alignRegion(autosplit: AutoSplit):
    # check to see if a region has been set
    if autosplit.hwnd <= 0 or not win32gui.GetWindowText(autosplit.hwnd):
        error_messages.regionError()
        return
    # This is the image used for aligning the capture region
    # to the best fit for the user.
    template_filename = QtWidgets.QFileDialog.getOpenFileName(
        autosplit,
        "Select Reference Image",
        "",
        "Image Files (*.png *.jpg *.jpeg *.jpe *.jp2 *.bmp *.tiff *.tif *.dib *.webp *.pbm *.pgm *.ppm *.sr *.ras)")[0]

    # return if the user presses cancel
    if not template_filename:
        return

    template = cv2.imread(template_filename, cv2.IMREAD_COLOR)

    # shouldn't need this, but just for caution, throw a type error if file is not a valid image file
    if template is None:
        error_messages.alignRegionImageTypeError()
        return

    # Obtaining the capture of a region which contains the
    # subregion being searched for to align the image.
    capture = capture_windows.capture_region(autosplit.hwnd, autosplit.selection)
    capture = cv2.cvtColor(capture, cv2.COLOR_BGRA2BGR)

    # Obtain the best matching point for the template within the
    # capture. This assumes that the template is actually smaller
    # than the dimensions of the capture. Since we are using SQDIFF
    # the best match will be the min_val which is located at min_loc.
    # The best match found in the image, set everything to 0 by default
    # so that way the first match will overwrite these values
    best_match = 0.0
    best_height = 0
    best_width = 0
    best_loc = (0, 0)

    # This tests 50 images scaled from 20% to 300% of the original template size
    for scale in np.linspace(0.2, 3, num=56):
        width = int(template.shape[1] * scale)
        height = int(template.shape[0] * scale)

        # The template can not be larger than the capture
        if width > capture.shape[1] or height > capture.shape[0]:
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

    # Go ahead and check if this satisfies our requirement before setting the region
    # We don't want a low similarity image to be aligned.
    if best_match < 0.9:
        error_messages.alignmentNotMatchedError()
        return

    # The new region can be defined by using the min_loc point and the
    # height and width of the template.
    autosplit.selection.left = autosplit.selection.left + best_loc[0]
    autosplit.selection.top = autosplit.selection.top + best_loc[1]
    autosplit.selection.right = autosplit.selection.left + best_width
    autosplit.selection.bottom = autosplit.selection.top + best_height

    autosplit.xSpinBox.setValue(autosplit.selection.left)
    autosplit.ySpinBox.setValue(autosplit.selection.top)
    autosplit.widthSpinBox.setValue(best_width)
    autosplit.heightSpinBox.setValue(best_height)


def validateBeforeComparison(autosplit: AutoSplit, show_error: bool = True, check_empty_directory: bool = True):
    error = None
    if not autosplit.split_image_directory:
        error = error_messages.splitImageDirectoryError
    elif not os.path.isdir(autosplit.split_image_directory):
        error = error_messages.splitImageDirectoryNotFoundError
    elif check_empty_directory and not os.listdir(autosplit.split_image_directory):
        error = error_messages.splitImageDirectoryEmpty
    elif autosplit.hwnd <= 0 or not win32gui.GetWindowText(autosplit.hwnd):
        error = error_messages.regionError
    if error and show_error:
        error()
    return not error


class BaseSelectWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # We need to pull the monitor information to correctly draw the geometry covering all portions
        # of the user's screen. These parameters create the bounding box with left, top, width, and height
        self.setGeometry(
            user32.GetSystemMetrics(SM_XVIRTUALSCREEN),
            user32.GetSystemMetrics(SM_YVIRTUALSCREEN),
            user32.GetSystemMetrics(SM_CXVIRTUALSCREEN),
            user32.GetSystemMetrics(SM_CYVIRTUALSCREEN))
        self.setWindowTitle(" ")
        self.setWindowOpacity(0.5)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.show()

    def keyPressEvent(self, a0: QtGui.QKeyEvent):
        if a0.key() == QtCore.Qt.Key.Key_Escape:
            self.close()


# Widget to select a window and obtain its bounds
class SelectWindowWidget(BaseSelectWidget):
    __x = -1
    __y = -1

    def x(self):
        return self.__x

    def y(self):
        return self.__y

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent):
        self.__x = int(a0.position().x()) + self.geometry().x()
        self.__y = int(a0.position().y()) + self.geometry().y()
        self.close()


# Widget for dragging screen region
# https://github.com/harupy/snipping-tool
class SelectRegionWidget(BaseSelectWidget):
    left: int = -1
    top: int = -1
    right: int = -1
    bottom: int = -1
    __begin = QtCore.QPoint()
    __end = QtCore.QPoint()

    def __init__(self):
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))
        super().__init__()

    def height(self):
        return self.bottom - self.top

    def width(self):
        return self.right - self.left

    def paintEvent(self, a0: QtGui.QPaintEvent):
        if self.__begin != self.__end:
            qPainter = QtGui.QPainter(self)
            qPainter.setPen(QtGui.QPen(QtGui.QColor("red"), 2))
            qPainter.setBrush(QtGui.QColor("opaque"))
            qPainter.drawRect(QtCore.QRect(self.__begin, self.__end))

    def mousePressEvent(self, a0: QtGui.QMouseEvent):
        self.__begin = a0.position().toPoint()
        self.__end = self.__begin
        self.update()

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent):
        self.__end = a0.position().toPoint()
        self.update()

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent):
        if self.__begin != self.__end:
            # The coordinates are pulled relative to the top left of the set geometry,
            # so the added virtual screen offsets convert them back to the virtual screen coordinates
            self.left = min(self.__begin.x(), self.__end.x()) + self.geometry().x()
            self.top = min(self.__begin.y(), self.__end.y()) + self.geometry().y()
            self.right = max(self.__begin.x(), self.__end.x()) + self.geometry().x()
            self.bottom = max(self.__begin.y(), self.__end.y()) + self.geometry().y()

            self.close()

    def close(self):
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        return super().close()
