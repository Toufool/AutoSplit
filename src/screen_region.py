from __future__ import annotations
from typing import Callable, cast, TYPE_CHECKING
if TYPE_CHECKING:
    from AutoSplit import AutoSplit

from PyQt6 import QtCore, QtGui, QtTest, QtWidgets
from win32 import win32gui
import os
import ctypes
import ctypes.wintypes
import cv2
import numpy as np

import capture_windows
import error_messages


def selectRegion(self: AutoSplit):
    # Create a screen selector widget
    selector = SelectRegionWidget()

    # Need to wait until the user has selected a region using the widget before moving on with
    # selecting the window settings
    while selector.height == -1 and selector.width == -1:
        QtTest.QTest.qWait(1)

    # return an error if width or height are zero.
    if selector.width == 0 or selector.height == 0:
        error_messages.regionSizeError()
        return

    # Width and Height of the spinBox
    self.widthSpinBox.setValue(selector.width)
    self.heightSpinBox.setValue(selector.height)

    # Grab the window handle from the coordinates selected by the widget
    self.hwnd = cast(int, win32gui.WindowFromPoint((selector.left, selector.top)))
    # Want to pull the parent window from the window handle
    # By using GetAncestor we are able to get the parent window instead
    # of the owner window.
    GetAncestor = cast(Callable[[int, int], int], ctypes.windll.user32.GetAncestor)
    GA_ROOT = 2

    while win32gui.IsChild(win32gui.GetParent(self.hwnd), self.hwnd):
        self.hwnd = GetAncestor(self.hwnd, GA_ROOT)

    if self.hwnd != 0 or win32gui.GetWindowText(self.hwnd) != '':
        self.hwnd_title = win32gui.GetWindowText(self.hwnd)

    # Convert the Desktop Coordinates to Window Coordinates
    DwmGetWindowAttribute = ctypes.windll.dwmapi.DwmGetWindowAttribute
    DWMWA_EXTENDED_FRAME_BOUNDS = 9

    # Pull the window's coordinates relative to desktop into rect
    DwmGetWindowAttribute(self.hwnd,
                          ctypes.wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
                          ctypes.byref(self.rect),
                          ctypes.sizeof(self.rect)
                          )

    # On Windows 10 the windows have offsets due to invisible pixels not accounted for in DwmGetWindowAttribute
    # TODO: Since this occurs on Windows 10, is DwmGetWindowAttribute even required over GetWindowRect alone?
    # Research needs to be done to figure out why it was used it over win32gui in the first place...
    # I have a feeling it was due to a misunderstanding and not getting the correct parent window before.
    offset_left = self.rect.left - win32gui.GetWindowRect(self.hwnd)[0]
    offset_top = self.rect.top - win32gui.GetWindowRect(self.hwnd)[1]

    self.rect.left = selector.left - (self.rect.left - offset_left)
    self.rect.top = selector.top - (self.rect.top - offset_top)
    self.rect.right = self.rect.left + selector.width
    self.rect.bottom = self.rect.top + selector.height

    self.xSpinBox.setValue(self.rect.left)
    self.ySpinBox.setValue(self.rect.top)

    # Delete that widget since it is no longer used from here on out
    del selector

    # check if live image needs to be turned on or just set a single image
    self.checkLiveImage()


def selectWindow(self: AutoSplit):
    # Create a screen selector widget
    selector = SelectWindowWidget()

    # Need to wait until the user has selected a region using the widget before moving on with
    # selecting the window settings
    while selector.x == -1 and selector.y == -1:
        QtTest.QTest.qWait(1)

    # Grab the window handle from the coordinates selected by the widget
    self.hwnd = cast(int, win32gui.WindowFromPoint((selector.x, selector.y)))

    if self.hwnd == 0:
        return

    del selector

    # Want to pull the parent window from the window handle
    # By using GetAncestor we are able to get the parent window instead
    # of the owner window.
    GetAncestor = cast(Callable[[int, int], int], ctypes.windll.user32.GetAncestor)
    GA_ROOT = 2
    while win32gui.IsChild(win32gui.GetParent(self.hwnd), self.hwnd):
        self.hwnd = GetAncestor(self.hwnd, GA_ROOT)

    if self.hwnd != 0 or win32gui.GetWindowText(self.hwnd) != '':
        self.hwnd_title = win32gui.GetWindowText(self.hwnd)

    # getting window bounds
    # on windows there are some invisble pixels that are not accounted for
    # also the top bar with the window name is not accounted for
    # I hardcoded the x and y coordinates to fix this
    # This is not an ideal solution because it assumes every window will have a top bar
    rect = win32gui.GetClientRect(self.hwnd)
    self.rect.left = 8
    self.rect.top = 31
    self.rect.right = 8 + rect[2]
    self.rect.bottom = 31 + rect[3]

    self.widthSpinBox.setValue(rect[2])
    self.heightSpinBox.setValue(rect[3])
    self.xSpinBox.setValue(self.rect.left)
    self.ySpinBox.setValue(self.rect.top)

    self.checkLiveImage()


def alignRegion(self: AutoSplit):
    # check to see if a region has been set
    if self.hwnd == 0 or win32gui.GetWindowText(self.hwnd) == '':
        error_messages.regionError()
        return
    # This is the image used for aligning the capture region
    # to the best fit for the user.
    template_filename = QtWidgets.QFileDialog.getOpenFileName(
        self,
        "Select Reference Image",
        "",
        "Image Files (*.png *.jpg *.jpeg *.jpe *.jp2 *.bmp *.tiff *.tif *.dib *.webp *.pbm *.pgm *.ppm *.sr *.ras)")[0]

    # return if the user presses cancel
    if template_filename == '':
        return

    template = cv2.imread(template_filename, cv2.IMREAD_COLOR)

    # shouldn't need this, but just for caution, throw a type error if file is not a valid image file
    if template is None:
        error_messages.alignRegionImageTypeError()
        return

    # Obtaining the capture of a region which contains the
    # subregion being searched for to align the image.
    capture = capture_windows.capture_region(self.hwnd, self.rect)
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

        resized = cv2.resize(template, (width, height))

        result = cv2.matchTemplate(capture, resized, cv2.TM_SQDIFF)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # The maximum value for SQ_DIFF is dependent on the size of the template
        # we need this value to normalize it from 0.0 to 1.0
        max_error = resized.size * 255 * 255
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
    self.rect.left = self.rect.left + best_loc[0]
    self.rect.top = self.rect.top + best_loc[1]
    self.rect.right = self.rect.left + best_width
    self.rect.bottom = self.rect.top + best_height

    self.xSpinBox.setValue(self.rect.left)
    self.ySpinBox.setValue(self.rect.top)
    self.widthSpinBox.setValue(best_width)
    self.heightSpinBox.setValue(best_height)


def validateBeforeComparison(self: AutoSplit, show_error: bool = True, check_empty_directory: bool = True):
    error = None
    if not self.split_image_directory:
        error = error_messages.splitImageDirectoryError
    elif not os.path.isdir(self.split_image_directory):
        error = error_messages.splitImageDirectoryNotFoundError
    elif check_empty_directory and not os.listdir(self.split_image_directory):
        error = error_messages.splitImageDirectoryEmpty
    elif self.hwnd == 0 or win32gui.GetWindowText(self.hwnd) == '':
        error = error_messages.regionError
    elif self.width == 0 or self.height == 0:
        error = error_messages.regionSizeError
    if error and show_error:
        error()
    return not error


# widget to select a window and obtain its bounds
class SelectWindowWidget(QtWidgets.QWidget):
    def __init__(self):
        super(SelectWindowWidget, self).__init__()
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()

        self.x = -1
        self.y = -1

        # We need to pull the monitor information to correctly draw the geometry covering all portions
        # of the user's screen. These parameters create the bounding box with left, top, width, and height
        self.SM_XVIRTUALSCREEN = user32.GetSystemMetrics(76)
        self.SM_YVIRTUALSCREEN = user32.GetSystemMetrics(77)
        self.SM_CXVIRTUALSCREEN = user32.GetSystemMetrics(78)
        self.SM_CYVIRTUALSCREEN = user32.GetSystemMetrics(79)

        self.setGeometry(self.SM_XVIRTUALSCREEN, self.SM_YVIRTUALSCREEN, self.SM_CXVIRTUALSCREEN,
                         self.SM_CYVIRTUALSCREEN)
        self.setWindowTitle(' ')

        self.setWindowOpacity(0.5)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.show()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        self.close()
        self.x = int(event.position().x())
        self.y = int(event.position().y())


# Widget for dragging screen region
# https://github.com/harupy/snipping-tool
class SelectRegionWidget(QtWidgets.QWidget):
    def __init__(self):
        super(SelectRegionWidget, self).__init__()
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()

        # We need to pull the monitor information to correctly draw the geometry covering all portions
        # of the user's screen. These parameters create the bounding box with left, top, width, and height
        self.SM_XVIRTUALSCREEN = user32.GetSystemMetrics(76)
        self.SM_YVIRTUALSCREEN = user32.GetSystemMetrics(77)
        self.SM_CXVIRTUALSCREEN = user32.GetSystemMetrics(78)
        self.SM_CYVIRTUALSCREEN = user32.GetSystemMetrics(79)

        self.setGeometry(self.SM_XVIRTUALSCREEN, self.SM_YVIRTUALSCREEN, self.SM_CXVIRTUALSCREEN,
                         self.SM_CYVIRTUALSCREEN)
        self.setWindowTitle(' ')

        self.height = -1
        self.width = -1

        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.setWindowOpacity(0.5)
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.show()

    def paintEvent(self, event: QtGui.QPaintEvent):
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor('red'), 2))
        qp.setBrush(QtGui.QColor('opaque'))
        qp.drawRect(QtCore.QRect(self.begin, self.end))

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        self.begin = event.position().toPoint()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        self.end = event.position().toPoint()
        self.update()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        self.close()

        # The coordinates are pulled relative to the top left of the set geometry,
        # so the added virtual screen offsets convert them back to the virtual
        # screen coordinates
        self.left = int(min(self.begin.x(), self.end.x()) + self.SM_XVIRTUALSCREEN)
        self.top = int(min(self.begin.y(), self.end.y()) + self.SM_YVIRTUALSCREEN)
        self.right = int(max(self.begin.x(), self.end.x()) + self.SM_XVIRTUALSCREEN)
        self.bottom = int(max(self.begin.y(), self.end.y()) + self.SM_YVIRTUALSCREEN)

        self.height = self.bottom - self.top
        self.width = self.right - self.left
