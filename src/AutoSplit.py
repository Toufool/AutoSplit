from PyQt4 import QtGui, QtCore, QtTest
import sys
import os
import win32gui
import cv2
import time
import ctypes.wintypes
import ctypes
import keyboard
import threading
import pickle
import numpy as np

import design
import about
import compare
import capture_windows
import split_parser


class AutoSplit(QtGui.QMainWindow, design.Ui_MainWindow):
    myappid = u'mycompany.myproduct.subproduct.version'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # signals
    updateCurrentSplitImage = QtCore.pyqtSignal(QtGui.QImage)
    startAutoSplitterSignal = QtCore.pyqtSignal()
    resetSignal = QtCore.pyqtSignal()
    skipSplitSignal = QtCore.pyqtSignal()
    undoSplitSignal = QtCore.pyqtSignal()
    afterSettingHotkeySignal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(AutoSplit, self).__init__(parent)
        self.setupUi(self)

        # close all processes when closing window
        self.actionView_Help.triggered.connect(self.viewHelp)
        self.actionAbout.triggered.connect(self.about)

        # disable buttons upon open
        self.undosplitButton.setEnabled(False)
        self.skipsplitButton.setEnabled(False)
        self.resetButton.setEnabled(False)

        # resize to these width and height so that FPS performance increases
        self.RESIZE_WIDTH = 320
        self.RESIZE_HEIGHT = 240

        # split image folder line edit text
        self.splitimagefolderLineEdit.setText('No Folder Selected')

        # Connecting button clicks to functions
        self.browseButton.clicked.connect(self.browse)
        self.selectregionButton.clicked.connect(self.selectRegion)
        self.takescreenshotButton.clicked.connect(self.takeScreenshot)
        self.startautosplitterButton.clicked.connect(self.autoSplitter)
        self.checkfpsButton.clicked.connect(self.checkFPS)
        self.resetButton.clicked.connect(self.reset)
        self.skipsplitButton.clicked.connect(self.skipSplit)
        self.undosplitButton.clicked.connect(self.undoSplit)
        self.setsplithotkeyButton.clicked.connect(self.setSplitHotkey)
        self.setresethotkeyButton.clicked.connect(self.setResetHotkey)
        self.setskipsplithotkeyButton.clicked.connect(self.setSkipSplitHotkey)
        self.setundosplithotkeyButton.clicked.connect(self.setUndoSplitHotkey)
        self.setpausehotkeyButton.clicked.connect(self.setPauseHotkey)
        self.alignregionButton.clicked.connect(self.alignRegion)
        self.selectwindowButton.clicked.connect(self.selectWindow)
        self.reloadsettingsButton.clicked.connect(self.loadSettings)

        # update x, y, width, and height when changing the value of these spinbox's are changed
        self.xSpinBox.valueChanged.connect(self.updateX)
        self.ySpinBox.valueChanged.connect(self.updateY)
        self.widthSpinBox.valueChanged.connect(self.updateWidth)
        self.heightSpinBox.valueChanged.connect(self.updateHeight)

        # connect signals to functions
        self.updateCurrentSplitImage.connect(self.updateSplitImageGUI)
        self.afterSettingHotkeySignal.connect(self.afterSettingHotkey)
        self.startAutoSplitterSignal.connect(self.autoSplitter)
        self.resetSignal.connect(self.reset)
        self.skipSplitSignal.connect(self.skipSplit)
        self.undoSplitSignal.connect(self.undoSplit)

        # live image checkbox
        self.liveimageCheckBox.clicked.connect(self.checkLiveImage)
        self.timerLiveImage = QtCore.QTimer()
        self.timerLiveImage.timeout.connect(self.liveImageFunction)

        # Default Settings for the region capture
        self.hwnd = 0
        self.hwnd_title = ''
        self.rect = ctypes.wintypes.RECT()

        # Get the file's path (PyInstaller compatible)
        if getattr(sys, 'frozen', False):
            self.file_path = os.path.dirname(os.path.abspath(sys.executable))
        else:
            self.file_path = os.path.dirname(os.path.abspath(__file__))

        # try to load settings
        self.loadSettings()

    # FUNCTIONS

    def viewHelp(self):
        os.system("start \"\" https://github.com/Toufool/Auto-Split#tutorial")
        return

    def about(self):
        self.AboutWidget = AboutWidget()

    def browse(self):
        # User selects the file with the split images in it.
        self.split_image_directory = str(
            QtGui.QFileDialog.getExistingDirectory(self, "Select Split Image Directory")) + '\\'

        # If the user doesn't select a folder, it defaults to \. Set it back to whats in the LineEdit, and return
        if self.split_image_directory == '\\':
            self.split_image_directory = self.splitimagefolderLineEdit.text()
            return

        # set the split image folder line to the directory text
        self.splitimagefolderLineEdit.setText(self.split_image_directory)

    def selectRegion(self):
        # Create a screen selector widget
        selector = SelectRegionWidget()

        # Need to wait until the user has selected a region using the widget before moving on with
        # selecting the window settings
        while selector.height == -1 and selector.width == -1:
            QtTest.QTest.qWait(1)

        # return an error if width or height are zero.
        if selector.width == 0 or selector.height == 0:
            self.regionSizeError()
            return

        # Width and Height of the spinBox
        self.widthSpinBox.setValue(selector.width)
        self.heightSpinBox.setValue(selector.height)

        # Grab the window handle from the coordinates selected by the widget
        self.hwnd = win32gui.WindowFromPoint((selector.left, selector.top))
        # Want to pull the parent window from the window handle
        # By using GetAncestor we are able to get the parent window instead
        # of the owner window.
        GetAncestor = ctypes.windll.user32.GetAncestor
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

    def alignRegion(self):
        # check to see if a region has been set
        if self.hwnd == 0 or win32gui.GetWindowText(self.hwnd) == '':
            self.regionError()
            return
        # This is the image used for aligning the capture region
        # to the best fit for the user.
        template_filename = str(QtGui.QFileDialog.getOpenFileName(self, "Select Reference Image", "",
                                                                  "Image Files (*.png *.jpg *.jpeg *.jpe *.jp2 *.bmp *.tiff *.tif *.dib *.webp *.pbm *.pgm *.ppm *.sr *.ras)"))

        # return if the user presses cancel
        if template_filename == '':
            return

        template = cv2.imread(template_filename, cv2.IMREAD_COLOR)

        # shouldn't need this, but just for caution, throw a type error if file is not a valid image file
        if template is None:
            self.alignRegionImageTypeError()
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
            self.alignmentNotMatchedError()
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

    def selectWindow(self):
        # Create a screen selector widget
        selector = SelectWindowWidget()

        # Need to wait until the user has selected a region using the widget before moving on with
        # selecting the window settings
        while selector.x == -1 and selector.y == -1:
            QtTest.QTest.qWait(1)

        # Grab the window handle from the coordinates selected by the widget
        self.hwnd = None
        self.hwnd = win32gui.WindowFromPoint((selector.x, selector.y))

        if self.hwnd is None:
            return

        del selector

        # Want to pull the parent window from the window handle
        # By using GetAncestor we are able to get the parent window instead
        # of the owner window.
        GetAncestor = ctypes.windll.user32.GetAncestor
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
        self.rect.right = 0 + rect[2]
        self.rect.bottom = 0 + rect[3]

        self.widthSpinBox.setValue(self.rect.right)
        self.heightSpinBox.setValue(self.rect.bottom)
        self.xSpinBox.setValue(self.rect.left)
        self.ySpinBox.setValue(self.rect.top)

        self.checkLiveImage()

    def checkLiveImage(self):
        if self.liveimageCheckBox.isChecked():
            self.timerLiveImage.start(1000 / 60)
        else:
            self.timerLiveImage.stop()
            self.liveImageFunction()

    def liveImageFunction(self):
        try:
            if win32gui.GetWindowText(self.hwnd) == '':
                self.regionError()
                self.timerLiveImage.stop()
                return

            ctypes.windll.user32.SetProcessDPIAware()

            capture = capture_windows.capture_region(self.hwnd, self.rect)
            capture = cv2.resize(capture, (240, 180))
            capture = cv2.cvtColor(capture, cv2.COLOR_BGRA2RGB)

            # Convert to set it on the label
            qImg = QtGui.QImage(capture, capture.shape[1], capture.shape[0], capture.shape[1] * 3,
                                QtGui.QImage.Format_RGB888)
            pix = QtGui.QPixmap(qImg)
            self.liveImage.setPixmap(pix)

        except AttributeError:
            pass

    # update x, y, width, height when spinbox values are changed
    def updateX(self):
        try:
            self.rect.left = self.xSpinBox.value()
            self.rect.right = self.rect.left + self.widthSpinBox.value()
            self.checkLiveImage()
        except AttributeError:
            pass

    def updateY(self):
        try:
            self.rect.top = self.ySpinBox.value()
            self.rect.bottom = self.rect.top + self.heightSpinBox.value()
            self.checkLiveImage()
        except AttributeError:
            pass

    def updateWidth(self):
        self.rect.right = self.rect.left + self.widthSpinBox.value()
        self.checkLiveImage()

    def updateHeight(self):
        self.rect.bottom = self.rect.top + self.heightSpinBox.value()
        self.checkLiveImage()

    # update current split image. needed this to avoid updating it through the hotkey thread.
    def updateSplitImageGUI(self, qImg):
        pix = QtGui.QPixmap(qImg)
        self.currentSplitImage.setPixmap(pix)

    def takeScreenshot(self):
        # error checks
        if self.splitimagefolderLineEdit.text() == 'No Folder Selected':
            self.splitImageDirectoryError()
            return
        if self.hwnd == 0 or win32gui.GetWindowText(self.hwnd) == '':
            self.regionError()
            return
        take_screenshot_filename = '001_SplitImage'

        # check if file exists and rename it if it does
        # Below starts the FileNameNumber at #001 up to #999. After that it will go to 1000,
        # which is a problem, but I doubt anyone will get to 1000 split images...
        i = 1
        while os.path.exists(self.split_image_directory + take_screenshot_filename + '.png') == True:
            FileNameNumber = (f"{i:03}")
            take_screenshot_filename = FileNameNumber + '_SplitImage'
            i += 1

        # grab screenshot of capture region
        capture = capture_windows.capture_region(self.hwnd, self.rect)
        capture = cv2.cvtColor(capture, cv2.COLOR_BGRA2BGR)

        # save and open image
        cv2.imwrite(self.split_image_directory + take_screenshot_filename + '.png', capture)
        os.startfile(self.split_image_directory + take_screenshot_filename + '.png')

    # HOTKEYS. I'll comment on one, and the rest are just variations in variables.
    def setSplitHotkey(self):
        self.setsplithotkeyButton.setText('Press a key..')

        # disable some buttons
        self.beforeSettingHotkey()

        # new thread points to callback. this thread is needed or GUI will freeze
        # while the program waits for user input on the hotkey
        def callback():
            # try to remove the previously set hotkey if there is one.
            try:
                keyboard.remove_hotkey(self.split_hotkey)
            except (AttributeError, KeyError):
                pass

            # wait until user presses the hotkey, then keyboard module reads the input
            self.split_key = keyboard.read_hotkey(False)

            # If the key the user presses is equal to itself or another hotkey already set,
            # this causes issues. so here, it catches that, and will make no changes to the hotkey.
            try:
                if self.split_key == self.splitLineEdit.text() or self.split_key == self.resetLineEdit.text() or self.split_key == self.skipsplitLineEdit.text() or self.split_key == self.undosplitLineEdit.text() or self.split_key == self.pauseLineEdit.text():
                    self.split_hotkey = keyboard.add_hotkey(self.old_split_key, self.startAutoSplitter)
                    self.afterSettingHotkeySignal.emit()
                    return
            except AttributeError:
                self.afterSettingHotkeySignal.emit()
                return

            # keyboard module allows you to hit multiple keys for a hotkey. they are joined
            # together by +. If user hits two keys at the same time, make no changes to the
            # hotkey. A try and except is needed if a hotkey hasn't been set yet. I'm not
            # allowing for these multiple-key hotkeys because it can cause crashes, and
            # not many people are going to really use or need this.
            try:
                if '+' in self.split_key:
                    self.split_hotkey = keyboard.add_hotkey(self.old_split_key, self.startAutoSplitter)
                    self.afterSettingHotkeySignal.emit()
                    return
            except AttributeError:
                self.afterSettingHotkeySignal.emit()
                return

            # add the key as the hotkey, set the text into the LineEdit, set it as old_xxx_key,
            # then emite a signal to re-enable some buttons and change some text in GUI.
            self.split_hotkey = keyboard.add_hotkey(self.split_key, self.startAutoSplitter)
            self.splitLineEdit.setText(self.split_key)
            self.old_split_key = self.split_key
            self.afterSettingHotkeySignal.emit()
            return

        t = threading.Thread(target=callback)
        t.start()
        return

    def setResetHotkey(self):
        self.setresethotkeyButton.setText('Press a key..')
        self.beforeSettingHotkey()

        def callback():
            try:
                keyboard.remove_hotkey(self.reset_hotkey)
            except (AttributeError, KeyError):
                pass
            self.reset_key = keyboard.read_hotkey(False)
            try:
                if self.reset_key == self.splitLineEdit.text() or self.reset_key == self.resetLineEdit.text() or self.reset_key == self.skipsplitLineEdit.text() or self.reset_key == self.undosplitLineEdit.text() or self.reset_key == self.pauseLineEdit.text():
                    self.reset_hotkey = keyboard.add_hotkey(self.old_reset_key, self.startReset)
                    self.afterSettingHotkeySignal.emit()
                    return
            except AttributeError:
                self.afterSettingHotkeySignal.emit()
                return
            try:
                if '+' in self.reset_key:
                    self.reset_hotkey = keyboard.add_hotkey(self.old_reset_key, self.startReset)
                    self.afterSettingHotkeySignal.emit()
                    return
            except AttributeError:
                self.afterSettingHotkeySignal.emit()
                return
            self.reset_hotkey = keyboard.add_hotkey(self.reset_key, self.startReset)
            self.resetLineEdit.setText(self.reset_key)
            self.old_reset_key = self.reset_key
            self.afterSettingHotkeySignal.emit()
            return

        t = threading.Thread(target=callback)
        t.start()
        return

    def setSkipSplitHotkey(self):
        self.setskipsplithotkeyButton.setText('Press a key..')
        self.beforeSettingHotkey()

        def callback():
            try:
                keyboard.remove_hotkey(self.skip_split_hotkey)
            except (AttributeError, KeyError):
                pass

            self.skip_split_key = keyboard.read_hotkey(False)

            try:
                if self.skip_split_key == self.splitLineEdit.text() or self.skip_split_key == self.resetLineEdit.text() or self.skip_split_key == self.skipsplitLineEdit.text() or self.skip_split_key == self.undosplitLineEdit.text() or self.skip_split_key == self.pauseLineEdit.text():
                    self.skip_split_hotkey = keyboard.add_hotkey(self.old_skip_split_key, self.startSkipSplit)
                    self.afterSettingHotkeySignal.emit()
                    return
            except AttributeError:
                self.afterSettingHotkeySignal.emit()
                return

            try:
                if '+' in self.skip_split_key:
                    self.skip_split_hotkey = keyboard.add_hotkey(self.old_skip_split_key, self.startSkipSplit)
                    self.afterSettingHotkeySignal.emit()
                    return
            except AttributeError:
                self.afterSettingHotkeySignal.emit()
                return

            self.skip_split_hotkey = keyboard.add_hotkey(self.skip_split_key, self.startSkipSplit)
            self.skipsplitLineEdit.setText(self.skip_split_key)
            self.old_skip_split_key = self.skip_split_key
            self.afterSettingHotkeySignal.emit()
            return

        t = threading.Thread(target=callback)
        t.start()
        return

    def setUndoSplitHotkey(self):
        self.setundosplithotkeyButton.setText('Press a key..')
        self.beforeSettingHotkey()

        def callback():
            try:
                keyboard.remove_hotkey(self.undo_split_hotkey)
            except (AttributeError, KeyError):
                pass

            self.undo_split_key = keyboard.read_hotkey(False)

            try:
                if self.undo_split_key == self.splitLineEdit.text() or self.undo_split_key == self.resetLineEdit.text() or self.undo_split_key == self.skipsplitLineEdit.text() or self.undo_split_key == self.undosplitLineEdit.text() or self.undo_split_key == self.pauseLineEdit.text():
                    self.undo_split_hotkey = keyboard.add_hotkey(self.old_undo_split_key, self.startUndoSplit)
                    self.afterSettingHotkeySignal.emit()
                    return
            except AttributeError:
                self.afterSettingHotkeySignal.emit()
                return

            try:
                if '+' in self.undo_split_key:
                    self.undo_split_hotkey = keyboard.add_hotkey(self.old_undo_split_key, self.startUndoSplit)
                    self.afterSettingHotkeySignal.emit()
                    return
            except AttributeError:
                self.afterSettingHotkeySignal.emit()
                return

            self.undo_split_hotkey = keyboard.add_hotkey(self.undo_split_key, self.startUndoSplit)
            self.undosplitLineEdit.setText(self.undo_split_key)
            self.old_undo_split_key = self.undo_split_key
            self.afterSettingHotkeySignal.emit()
            return

        t = threading.Thread(target=callback)
        t.start()
        return

    # this one is shorter because AutoSplit will ignore pause hotkey presses
    # since it doesn't keep track of whether the timer is paused
    def setPauseHotkey(self):
        self.setpausehotkeyButton.setText('Press a key..')
        self.beforeSettingHotkey()

        def callback():
            self.pause_key = keyboard.read_hotkey(False)
            try:
                if self.pause_key == self.splitLineEdit.text() or self.pause_key == self.resetLineEdit.text() or self.pause_key == self.skipsplitLineEdit.text() or self.pause_key == self.undosplitLineEdit.text() or self.pause_key == self.pauseLineEdit.text():
                    self.afterSettingHotkeySignal.emit()
                    return
            except AttributeError:
                self.afterSettingHotkeySignal.emit()
                return
            try:
                if '+' in self.pause_key:
                    self.afterSettingHotkeySignal.emit()
                    return
            except AttributeError:
                self.afterSettingHotkeySignal.emit()
                return
            self.pauseLineEdit.setText(self.pause_key)
            self.afterSettingHotkeySignal.emit()
            return

        t = threading.Thread(target=callback)
        t.start()
        return

    # do all of these after you click "set hotkey" but before you type the hotkey.
    def beforeSettingHotkey(self):
        self.startautosplitterButton.setEnabled(False)
        self.setsplithotkeyButton.setEnabled(False)
        self.setresethotkeyButton.setEnabled(False)
        self.setskipsplithotkeyButton.setEnabled(False)
        self.setundosplithotkeyButton.setEnabled(False)
        self.setpausehotkeyButton.setEnabled(False)
        self.reloadsettingsButton.setEnabled(False)

    # do all of these things after you set a hotkey. a signal connects to this because
    # changing GUI stuff in the hotkey thread was causing problems
    def afterSettingHotkey(self):
        self.setsplithotkeyButton.setText('Set Hotkey')
        self.setresethotkeyButton.setText('Set Hotkey')
        self.setskipsplithotkeyButton.setText('Set Hotkey')
        self.setundosplithotkeyButton.setText('Set Hotkey')
        self.setpausehotkeyButton.setText('Set Hotkey')
        self.startautosplitterButton.setEnabled(True)
        self.setsplithotkeyButton.setEnabled(True)
        self.setresethotkeyButton.setEnabled(True)
        self.setskipsplithotkeyButton.setEnabled(True)
        self.setundosplithotkeyButton.setEnabled(True)
        self.setpausehotkeyButton.setEnabled(True)
        self.reloadsettingsButton.setEnabled(True)
        return

    # check max FPS button connects here.
    def checkFPS(self):
        # error checking
        split_image_directory = self.splitimagefolderLineEdit.text()
        if split_image_directory == 'No Folder Selected' or split_image_directory is None:
            self.splitImageDirectoryError()
            return

        split_image_filenames = os.listdir(split_image_directory)
        for image in split_image_filenames:
            if cv2.imread(self.split_image_directory + image, cv2.IMREAD_COLOR) is None:
                self.imageTypeError(image)
                return
            else:
                pass

        if self.hwnd == 0 or win32gui.GetWindowText(self.hwnd) == '':
            self.regionError()
            return

        if self.width == 0 or self.height == 0:
            self.regionSizeError()
            return

        # grab first image in the split image folder
        split_image = cv2.imread(split_image_directory + split_image_filenames[0], cv2.IMREAD_COLOR)
        split_image = cv2.cvtColor(split_image, cv2.COLOR_BGR2RGB)
        split_image = cv2.resize(split_image, (self.RESIZE_WIDTH, self.RESIZE_HEIGHT))

        # run 10 iterations of screenshotting capture region + comparison.
        count = 0
        t0 = time.time()
        while count < 10:

            capture = capture_windows.capture_region(self.hwnd, self.rect)
            capture = cv2.resize(capture, (self.RESIZE_WIDTH, self.RESIZE_HEIGHT))
            capture = cv2.cvtColor(capture, cv2.COLOR_BGRA2RGB)

            if self.comparisonmethodComboBox.currentIndex() == 0:
                similarity = compare.compare_l2_norm(split_image, capture)
            elif self.comparisonmethodComboBox.currentIndex() == 1:
                similarity = compare.compare_histograms(split_image, capture)
            elif self.comparisonmethodComboBox.currentIndex() == 2:
                similarity = compare.compare_phash(split_image, capture)

            count += 1

        # calculate FPS
        t1 = time.time()
        FPS = int(10 / (t1 - t0))
        FPS = str(FPS)
        self.fpsvalueLabel.setText(FPS)

    # undo split button and hotkey connect to here
    def undoSplit(self):
        if self.undosplitButton.isEnabled() == False:
            return

        if self.loop_number != 1:
            self.loop_number -= 1
        else:
            self.split_image_index = self.split_images[self.split_image_index].undo_image_index

        self.updateSplitImage()

        return

    # skip split button and hotkey connect to here
    def skipSplit(self):

        if self.skipsplitButton.isEnabled() == False:
            return

        if self.loop_number < self.split_images[self.split_image_index].loop:
            self.loop_number += 1
        else:
            self.split_image_index = self.split_images[self.split_image_index].skip_image_index

        self.updateSplitImage()

        return

    # reset button and hotkey connects here.
    def reset(self):
        self.startautosplitterButton.setText('Start Auto Splitter')
        return

    # functions for the hotkeys to return to the main thread from signals and start their corresponding functions
    def startAutoSplitter(self):
        # if the auto splitter is already running or the button is disabled, don't emit the signal to start it.
        if self.startautosplitterButton.text() == 'Running..' or self.startautosplitterButton.isEnabled() == False:
            return
        else:
            self.startAutoSplitterSignal.emit()

    def startReset(self):
        self.resetSignal.emit()

    def startSkipSplit(self):
        self.skipSplitSignal.emit()

    def startUndoSplit(self):
        self.undoSplitSignal.emit()

    def autoSplitter(self):
        # error checking:
        if self.splitimagefolderLineEdit.text() == 'No Folder Selected':
            self.splitImageDirectoryError()
            return
        if len(os.listdir(self.split_image_directory)) == 0:
            self.noSplitImagesError()
            return
        if self.hwnd == 0 or win32gui.GetWindowText(self.hwnd) == '':
            self.regionError()
            return

        # get split image filenames
        self.split_images = []
        previous_n_flag = False

        for image_filename in os.listdir(self.split_image_directory):
            self.split_images.append(split_parser.SplitImage(self.split_image_directory, image_filename))

            # Make sure that each of the images follows the guidelines for correct format
            # according to all of the settings selected by the user.

            # Check to make sure the file is actually an image format that can be opened
            # according to the mask flag
            if self.split_images[-1].flags & 0x02 == 0x02:
                source = cv2.imread(self.split_images[-1].path, cv2.IMREAD_UNCHANGED)

                if source is None:
                    # Opencv couldn't open this file as an image, this isn't a correct
                    # file format that is supported
                    self.imageTypeError(self.split_images[-1].filename)
                    return

                if source.shape[2] != 4:
                    # Error, this file doesn't have an alpha channel even
                    # though the flag for masking was added
                    self.alphaChannelError(self.split_images[-1].filename)
                    return

            else:
                if cv2.imread(self.split_images[-1].path, cv2.IMREAD_COLOR) is None:
                    # Opencv couldn't open this file as an image, this isn't a correct
                    # file format that is supported
                    self.imageTypeError(self.split_images[-1].filename)
                    return

            if self.custompausetimesCheckBox.isChecked() and self.split_images[-1].pause is None:
                # Error, this file doesn't have a pause, but the checkbox was
                # selected for unique pause times
                self.customPauseError(self.split_images[-1].filename)
                return

            if self.customthresholdsCheckBox.isChecked() and self.split_images[-1].threshold is None:
                # Error, this file doesn't have a threshold, but the checkbox
                # was selected for unique thresholds
                self.customThresholdError(self.split_images[-1].filename)
                return

            if self.pauseLineEdit.text() == '' and self.split_images[-1].flags & 0x08 == 0x08:
                # Error, no pause hotkey set even though pause flag is set
                self.pauseHotkeyError()
                return

            if self.splitLineEdit.text() == '' and self.split_images[-1].flags & 0x01 == 0:
                # Error, no split hotkey set even though dummy flag is not set
                self.splitHotkeyError()
                return

            if previous_n_flag and self.split_images[-1].loop > 1:
                # Error, an image with the {n} flag is followed by an image with a loop > 1
                self.includeNextFlagWithLoopError()
                return

            previous_n_flag = self.split_images[-1].flags & 0x10 == 0x10

        # If the last split has the {n} flag, throw an error
        if self.split_images[-1].flags & 0x10 == 0x10:
            self.lastImageHasIncludeNextFlagError()
            return

        # Find reset image then remove it from the list
        self.reset_image = None
        for i, image in enumerate(self.split_images):
            if image.is_reset_image:
                # Check that there's only one reset image
                if self.reset_image is None:
                    if len(self.split_images) == 1:
                        self.noSplitImagesError()
                        return
                    self.reset_image = image
                    self.split_images.pop(i)
                else:
                    self.multipleResetImagesError()
                    return

        if self.reset_image is not None:
            self.reset_image.get_image(self.RESIZE_WIDTH, self.RESIZE_HEIGHT)

            # If there is no custom threshold for the reset image, throw an error
            if self.reset_image.threshold is None:
                self.noResetImageThresholdError()
                return

            # If the reset image has the {n} flag, throw an error
            if self.reset_image.flags & 0x10 == 0x10:
                self.resetImageHasIncludeNextFlagError()
                return

            # If there is no reset hotkey set but a reset image is present, throw an error
            if self.resetLineEdit.text() == '':
                self.resetHotkeyError()
                return

        # Construct groups of splits
        previous_group_start = None
        previous_group_undo = None
        current_group_start = 0
        current_group_undo = 0
        flags = 0x11
        if self.groupDummySplitsCheckBox.isChecked() == False:
            flags -= 0x01

        for i, image in enumerate(self.split_images):
            if image.flags & 0x20 == 0x20:
                current_group_undo = i
            if image.flags & flags == 0:
                for image in self.split_images[current_group_start : i + 1]:
                    image.undo_image_index = previous_group_undo

                if previous_group_start is not None:
                    for image in self.split_images[previous_group_start : current_group_start]:
                        image.skip_image_index = i + 1

                previous_group_start = current_group_start
                previous_group_undo = current_group_undo
                current_group_start = i + 1
                current_group_undo = current_group_start

        # change auto splitter button text and disable/enable some buttons
        self.startautosplitterButton.setText('Running..')
        self.browseButton.setEnabled(False)
        self.startautosplitterButton.setEnabled(False)
        self.resetButton.setEnabled(True)
        self.undosplitButton.setEnabled(True)
        self.skipsplitButton.setEnabled(True)
        self.setsplithotkeyButton.setEnabled(False)
        self.setresethotkeyButton.setEnabled(False)
        self.setskipsplithotkeyButton.setEnabled(False)
        self.setundosplithotkeyButton.setEnabled(False)
        self.setpausehotkeyButton.setEnabled(False)
        self.custompausetimesCheckBox.setEnabled(False)
        self.customthresholdsCheckBox.setEnabled(False)
        self.groupDummySplitsCheckBox.setEnabled(False)

        # Initialize some settings
        self.split_image_index = 0
        self.split_image_index_changed = True
        self.loop_number = 1
        self.number_of_split_images = len(self.split_images)

        self.run_start_time = time.time()

        # First while loop: stays in this loop until all of the split images have been split
        while self.split_image_index < self.number_of_split_images:

            if self.split_image_index_changed:
                # Construct list of images that should be compared
                self.current_split_images = []
                for image in self.split_images[self.split_image_index :]:
                    image.get_image(self.RESIZE_WIDTH, self.RESIZE_HEIGHT)
                    self.current_split_images.append(image)
                    if image.flags & 0x10 == 0:
                        break

                self.updateSplitImage(self.current_split_images[0])
                self.highest_similarity = 0.001

            # second while loop: stays in this loop until similarity threshold is met
            # skip loop if we just finished waiting for the split delay and need to press the split key!
            start = time.time()
            while True:
                # reset if the set screen region window was closed
                if win32gui.GetWindowText(self.hwnd) == '':
                    self.reset()

                # calculate similarity for reset image
                reset_masked = None
                capture = None

                if self.shouldCheckResetImage():
                    reset_masked = (self.reset_image.mask is not None)
                    capture = self.getCaptureForComparison(reset_masked)

                    self.reset_image.similarity = self.compareImage(self.reset_image, capture)
                    if self.reset_image.similarity >= self.reset_image.threshold:
                        keyboard.send(str(self.resetLineEdit.text()))
                        self.reset()

                # loop goes into here if start auto splitter text is "Start Auto Splitter"
                if self.startautosplitterButton.text() == 'Start Auto Splitter':
                    self.resetUI()
                    QtGui.QApplication.processEvents()
                    return

                # Reuse capture variable as non-masked capture variable
                masked_capture = None
                if reset_masked is not None and capture is not None:
                    masked_capture = capture
                    capture = None

                # Calculate similarities for split images
                for image in self.current_split_images:
                    if image.mask is None:
                        if capture is None:
                            capture = self.getCaptureForComparison(False)
                        image.similarity = self.compareImage(image, capture)
                    else:
                        if masked_capture is None:
                            masked_capture = self.getCaptureForComparison(True)
                        image.similarity = self.compareImage(image, masked_capture)

                    # If the similarity becomes higher than highest similarity, set it as such
                    if image.similarity > self.highest_similarity:
                        self.highest_similarity = image.similarity

                # Show live similarity of first comparison image if the checkbox is checked
                if self.showlivesimilarityCheckBox.isChecked():
                    self.livesimilarityLabel.setText(str(self.current_split_images[0].similarity)[: 4])
                else:
                    self.livesimilarityLabel.setText(' ')

                # show live highest similarity if the checkbox is checked
                if self.showhighestsimilarityCheckBox.isChecked():
                    self.highestsimilarityLabel.setText(str(self.highest_similarity)[: 4])
                else:
                    self.highestsimilarityLabel.setText(' ')

                # if its the last split image and last loop number, disable the skip split button
                self.skipsplitButton.setEnabled(self.current_split_images[0].skip_image_index is not None or self.current_split_images[0].loop != self.loop_number)

                # if its the first split image and first loop, disable the undo split button
                self.undosplitButton.setEnabled(self.current_split_images[0].undo_image_index is not None or self.current_split_images[0].loop != 1)

                try:
                    for image in self.current_split_images:
                        # If the {b} flag is set, let similarity go above threshold first, then split on similarity below threshold
                        # Otherwise just split when similarity goes above threshold
                        if image.flags & 0x04 == 0x04 and image.split_below_threshold == False and image.similarity >= self.similaritythresholdDoubleSpinBox.value():
                            image.split_below_threshold = True
                            raise ContinueLoop
                        if (image.flags & 0x04 == 0x04 and image.split_below_threshold == True and image.similarity < self.similaritythresholdDoubleSpinBox.value()) or (image.similarity >= self.similaritythresholdDoubleSpinBox.value() and image.flags & 0x04 == 0):
                            self.successful_split_image = image
                            raise BreakLoop

                # These exceptions are necessary because else the for loop would be broken/continued instead of the while loop
                except ContinueLoop:
                    continue
                except BreakLoop:
                    break

                # limit the number of time the comparison runs to reduce cpu usage
                fps_limit = self.fpslimitSpinBox.value()
                time.sleep((1 / fps_limit) - (time.time() - start) % (1 / fps_limit))
                QtGui.QApplication.processEvents()


            # comes here when threshold gets met

            # We need to make sure that this isn't a dummy split without pause flag
            # before sending a key press.
            if (self.successful_split_image.flags & 0x09 == 0x01):
                pass
            else:
                # If it's a delayed split, check if the delay has passed
                # Otherwise calculate the split time for the key press
                if self.successful_split_image.delay > 0:
                    self.split_time = int(round(time.time() * 1000)) + self.successful_split_image.delay

                    self.currentSplitImage.setText('Delayed split...')
                    self.undosplitButton.setEnabled(False)
                    self.skipsplitButton.setEnabled(False)
                    self.currentsplitimagefileLabel.setText(' ')
                    self.currentSplitImage.setAlignment(QtCore.Qt.AlignCenter)

                    # check for reset while delayed
                    delay_start_time = time.time()
                    while time.time() - delay_start_time < (self.successful_split_image.delay / 1000):
                        # check for reset
                        if win32gui.GetWindowText(self.hwnd) == '':
                            self.reset()
                        if self.startautosplitterButton.text() == 'Start Auto Splitter':
                            self.resetUI()
                            return

                        # calculate similarity for reset image
                        if self.shouldCheckResetImage():
                            reset_masked = (self.reset_image.mask is not None)
                            capture = self.getCaptureForComparison(reset_masked)

                            reset_image.similarity = self.compareImage(self.reset_image, capture)
                            if reset_image.similarity >= self.reset_image.threshold:
                                keyboard.send(str(self.resetLineEdit.text()))
                                self.reset()
                                continue

                        QtTest.QTest.qWait(1)

                # Split key press unless dummy flag is set
                if (self.successful_split_image.flags & 0x01 == 0x00):
                    keyboard.send(str(self.splitLineEdit.text()))

                # Pause key press if pause flag is set
                if (self.successful_split_image.flags & 0x08 == 0x08):
                    keyboard.send(str(self.pauseLineEdit.text()))

            # Increase loop number if needed, set to 1 if it was the last loop
            if self.loop_number < self.successful_split_image.loop:
                self.loop_number += 1
                self.split_image_index_changed = False
            else:
                self.loop_number = 1
                self.split_image_index_changed = True

            if self.loop_number == 1:
                # If loop check box is checked and its the last split, go to first split
                # Else if current loop amount is back to 1, add 1 to split image number
                if self.loopCheckBox.isChecked() and self.successful_split_image.skip_image_index is None:
                    self.split_image_index = 0
                else:
                    self.split_image_index += len(self.current_split_images)

            # Set a "pause" split image number. This is done so that it can detect if user hit split/undo split while paused
            pause_split_image_index = self.split_image_index
            pause_loop_number = self.loop_number

            # If it's not the last split image, pause for the amount set by the user
            if self.successful_split_image.pause > 0 and (self.loopCheckBox.isChecked() or len(self.split_images) < self.split_image_index):
                # Set current split image to none
                self.currentSplitImage.setText('none (paused)')
                self.currentsplitimagefileLabel.setText(' ')
                self.currentSplitImage.setAlignment(QtCore.Qt.AlignCenter)
                self.imageloopLabel.setText('Image Loop #:     -')

                # Make sure the index doesn't exceed the list
                if self.split_image_index < len(self.split_images):
                    # If it's the last split image and last loop number, disable the skip split button
                    self.skipsplitButton.setEnabled(self.split_images[self.split_image_index].skip_image_index is not None or self.split_images[self.split_image_index].loop != self.loop_number)

                    # If it's the first split image and first loop, disable the undo split button
                    self.undosplitButton.setEnabled(self.split_images[self.split_image_index].undo_image_index is not None or self.split_images[self.split_image_index].loop != 1)
                else:
                    self.undosplitButton.setEnabled(False)

                QtGui.QApplication.processEvents()

                # I have a pause loop here so that it can check if the user presses skip split, undo split, or reset here.
                # This should probably eventually be a signal... but it works
                pause_start_time = time.time()
                while time.time() - pause_start_time < self.pauseDoubleSpinBox.value():
                    # check for reset
                    if win32gui.GetWindowText(self.hwnd) == '':
                        self.reset()
                    if self.startautosplitterButton.text() == 'Start Auto Splitter':
                        self.resetUI()
                        return

                    # check for skip/undo split:
                    if self.split_image_index != pause_split_image_index or self.loop_number != pause_loop_number:
                        break

                    # calculate similarity for reset image
                    if self.shouldCheckResetImage():
                        reset_masked = (self.reset_image.mask is not None)
                        capture = self.getCaptureForComparison(reset_masked)

                        self.reset_image.similarity = self.compareImage(self.reset_image, capture)
                        if self.reset_image.similarity >= self.reset_image.threshold:
                            keyboard.send(str(self.resetLineEdit.text()))
                            self.reset()
                            continue

                    QtTest.QTest.qWait(1)

        # loop breaks to here when the last image splits
        self.startautosplitterButton.setText('Start Auto Splitter')
        self.resetUI()
        QtGui.QApplication.processEvents()

    def resetUI(self):
        self.imageloopLabel.setText("Image Loop #:")
        self.currentSplitImage.setText(' ')
        self.currentsplitimagefileLabel.setText(' ')
        self.livesimilarityLabel.setText(' ')
        self.highestsimilarityLabel.setText(' ')
        self.browseButton.setEnabled(True)
        self.startautosplitterButton.setEnabled(True)
        self.resetButton.setEnabled(False)
        self.undosplitButton.setEnabled(False)
        self.skipsplitButton.setEnabled(False)
        self.setsplithotkeyButton.setEnabled(True)
        self.setresethotkeyButton.setEnabled(True)
        self.setskipsplithotkeyButton.setEnabled(True)
        self.setundosplithotkeyButton.setEnabled(True)
        self.setpausehotkeyButton.setEnabled(True)
        self.custompausetimesCheckBox.setEnabled(True)
        self.customthresholdsCheckBox.setEnabled(True)
        self.groupDummySplitsCheckBox.setEnabled(True)

    def compareImage(self, image, capture):
        if self.comparisonmethodComboBox.currentIndex() == 0:
            return compare.compare_l2_norm(image, capture)
        elif self.comparisonmethodComboBox.currentIndex() == 1:
            return compare.compare_histograms(image, capture)
        elif self.comparisonmethodComboBox.currentIndex() == 2:
            return compare.compare_phash(image, capture)

    def getCaptureForComparison(self, masked):
        # Grab screenshot of capture region
        capture = capture_windows.capture_region(self.hwnd, self.rect)

        # If flagged as a mask, capture with nearest neighbor interpolation. else don't so that
        # threshold settings on versions below 1.2.0 aren't messed up
        if (masked):
            capture = cv2.resize(capture, (self.RESIZE_WIDTH, self.RESIZE_HEIGHT), interpolation=cv2.INTER_NEAREST)
        else:
            capture = cv2.resize(capture, (self.RESIZE_WIDTH, self.RESIZE_HEIGHT))

        # Convert to BGR
        capture = cv2.cvtColor(capture, cv2.COLOR_BGRA2BGR)

        return capture

    def shouldCheckResetImage(self):
        return (self.reset_image is not None and time.time() - self.run_start_time > self.reset_image.pause)

    def updateSplitImage(self, split_image):

        # Set Image Loop #
        self.imageloopLabel.setText("Image Loop #: " + str(self.loop_number))

        if len(self.current_split_images) > 1:
            self.currentSplitImage.setText(str(len(self.current_split_images)) + ' images')
            self.currentsplitimagefileLabel.setText(' ')
            self.currentSplitImage.setAlignment(QtCore.Qt.AlignCenter)
            return

        # Set current split image in UI
        # If flagged as mask, transform transparency into UI's gray BG color
        if (split_image.flags & 0x02 == 0x02):
            self.split_image_display = cv2.imread(split_image.path, cv2.IMREAD_UNCHANGED)
            transparent_mask = self.split_image_display[:, :, 3] == 0
            self.split_image_display[transparent_mask] = [240, 240, 240, 255]
            self.split_image_display = cv2.cvtColor(self.split_image_display, cv2.COLOR_BGRA2RGB)
            self.split_image_display = cv2.resize(self.split_image_display, (240, 180))
        # If not flagged as mask, open normally
        else:
            self.split_image_display = cv2.imread(self.split_image.path, cv2.IMREAD_COLOR)
            self.split_image_display = cv2.cvtColor(self.split_image_display, cv2.COLOR_BGR2RGB)
            self.split_image_display = cv2.resize(self.split_image_display, (240, 180))

        qImg = QtGui.QImage(self.split_image_display, self.split_image_display.shape[1],
                            self.split_image_display.shape[0], self.split_image_display.shape[1] * 3,
                            QtGui.QImage.Format_RGB888)
        self.updateCurrentSplitImage.emit(qImg)
        self.currentsplitimagefileLabel.setText(split_image.filename)

        self.current_split_images[0].get_image(self.RESIZE_WIDTH, self.RESIZE_HEIGHT)

    # Error messages

    def splitImageDirectoryError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("No split image folder is selected.")
        msgBox.exec_()

    def noSplitImagesError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("Your split image folder doesn't contain any splits.")
        msgBox.exec_()

    def imageTypeError(self, image):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText(
            '"' + image + '" is not a valid image file or the full image file path contains a special character.')
        msgBox.exec_()

    def regionError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("No region is selected. Select a region or reload settings while region window is open.")
        msgBox.exec_()

    def regionSizeError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("Width and height cannot be 0. Please select a larger region.")
        msgBox.exec_()

    def splitHotkeyError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("No split hotkey has been set.")
        msgBox.exec_()

    def customThresholdError(self, image):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("\"" + image + "\" doesn't have a valid custom threshold.")
        msgBox.exec_()

    def customPauseError(self, image):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("\"" + image + "\" doesn't have a valid custom pause time.")
        msgBox.exec_()

    def alphaChannelError(self, image):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("\"" + image + "\" is marked with mask flag but it doesn't have transparency.")
        msgBox.exec_()

    def alignRegionImageTypeError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("File not a valid image file.")
        msgBox.exec_()

    def alignmentNotMatchedError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("No area in capture region matched reference image. Alignment failed.")
        msgBox.exec_()

    def multipleResetImagesError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("Only one image with the keyword \"reset\" is allowed.")
        msgBox.exec_()

    def noResetImageThresholdError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("Reset image must have a custom threshold. Please set one and check that it is valid.")
        msgBox.exec_()

    def resetHotkeyError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("Your split image folder contains a reset image, but no reset hotkey is set.")
        msgBox.exec_()

    def pauseHotkeyError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("Your split image folder contains an image marked with pause flag, but no pause hotkey is set.")
        msgBox.exec_()

    def settingsNotFoundError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("No settings file found. The settings file is saved when the program is closed.")
        msgBox.exec_()

    def invalidSettingsError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("The settings file is invalid.")
        msgBox.exec_()

    def lastImageHasIncludeNextFlagError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("The last split image in the image folder is marked with include next flag.")
        msgBox.exec_()

    def resetImageHasIncludeNextFlagError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("The reset image in the image folder is marked with include next flag.")
        msgBox.exec_()

    def includeNextFlagWithLoopError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("Your split image folder contains an image marked with include next flag followed by an image with a loop value greater than 1.")
        msgBox.exec_()

    def saveSettings(self):
        # get values to be able to save settings
        self.x = self.xSpinBox.value()
        self.y = self.ySpinBox.value()
        self.width = self.widthSpinBox.value()
        self.height = self.heightSpinBox.value()
        self.split_image_directory = str(self.splitimagefolderLineEdit.text())
        self.similarity_threshold = self.similaritythresholdDoubleSpinBox.value()
        self.comparison_index = self.comparisonmethodComboBox.currentIndex()
        self.pause = self.pauseDoubleSpinBox.value()
        self.fps_limit = self.fpslimitSpinBox.value()
        self.split_key = str(self.splitLineEdit.text())
        self.reset_key = str(self.resetLineEdit.text())
        self.skip_split_key = str(self.skipsplitLineEdit.text())
        self.undo_split_key = str(self.undosplitLineEdit.text())
        self.pause_key = str(self.pauseLineEdit.text())

        self.custom_pause_times_setting = int(self.custompausetimesCheckBox.isChecked())
        self.custom_thresholds_setting = int(self.customthresholdsCheckBox.isChecked())
        self.group_dummy_splits_undo_skip_setting = int(self.groupDummySplitsCheckBox.isChecked())
        self.loop_setting = int(self.loopCheckBox.isChecked())

        # save settings to settings.pkl
        with open(os.path.join(self.file_path, 'settings.pkl'), 'wb') as f:
            pickle.dump(
                [self.split_image_directory, self.similarity_threshold, self.comparison_index, self.pause,
                 self.fps_limit, self.split_key,
                 self.reset_key, self.skip_split_key, self.undo_split_key, self.x, self.y, self.width, self.height,
                 self.hwnd_title,
                 self.custom_pause_times_setting, self.custom_thresholds_setting,
                 self.group_dummy_splits_undo_skip_setting, self.loop_setting, self.pause_key], f)

    def loadSettings(self):
        try:
            with open(os.path.join(self.file_path, 'settings.pkl'), 'rb') as f:
                f2 = pickle.load(f)
                if len(f2) == 18:
                    # The settings file might not include the pause hotkey yet
                    f2.append('')

                [self.split_image_directory, self.similarity_threshold, self.comparison_index, self.pause,
                self.fps_limit, self.split_key,
                self.reset_key, self.skip_split_key, self.undo_split_key, self.x, self.y, self.width, self.height,
                self.hwnd_title,
                self.custom_pause_times_setting, self.custom_thresholds_setting,
                self.group_dummy_splits_undo_skip_setting, self.loop_setting, self.pause_key] = f2

            self.split_image_directory = str(self.split_image_directory)
            self.splitimagefolderLineEdit.setText(self.split_image_directory)
            self.similaritythresholdDoubleSpinBox.setValue(self.similarity_threshold)
            self.pauseDoubleSpinBox.setValue(self.pause)
            self.fpslimitSpinBox.setValue(self.fps_limit)
            self.xSpinBox.setValue(self.x)
            self.ySpinBox.setValue(self.y)
            self.widthSpinBox.setValue(self.width)
            self.heightSpinBox.setValue(self.height)
            self.comparisonmethodComboBox.setCurrentIndex(self.comparison_index)
            self.hwnd = win32gui.FindWindow(None, self.hwnd_title)

            # Set custom checkboxes accordingly
            self.custompausetimesCheckBox.setChecked(self.custom_pause_times_setting == 1)
            self.customthresholdsCheckBox.setChecked(self.custom_thresholds_setting == 1)

            # Should be activated by default
            self.groupDummySplitsCheckBox.setChecked(self.group_dummy_splits_undo_skip_setting != 0)

            self.loopCheckBox.setChecked(self.loop_setting == 1)

            # try to set hotkeys from when user last closed the window
            try:
                try:
                    keyboard.remove_hotkey(self.split_hotkey)
                except AttributeError:
                    pass
                self.splitLineEdit.setText(str(self.split_key))
                self.split_hotkey = keyboard.add_hotkey(str(self.split_key), self.startAutoSplitter)
                self.old_split_key = self.split_key
            # pass if the key is an empty string (hotkey was never set)
            except ValueError:
                pass

            try:
                try:
                    keyboard.remove_hotkey(self.reset_hotkey)
                except AttributeError:
                    pass
                self.resetLineEdit.setText(str(self.reset_key))
                self.reset_hotkey = keyboard.add_hotkey(str(self.reset_key), self.startReset)
                self.old_reset_key = self.reset_key
            except ValueError:
                pass

            try:
                try:
                    keyboard.remove_hotkey(self.skip_split_hotkey)
                except AttributeError:
                    pass
                self.skipsplitLineEdit.setText(str(self.skip_split_key))
                self.skip_split_hotkey = keyboard.add_hotkey(str(self.skip_split_key), self.startSkipSplit)
                self.old_skip_split_key = self.skip_split_key
            except ValueError:
                pass

            try:
                try:
                    keyboard.remove_hotkey(self.undo_split_hotkey)
                except AttributeError:
                    pass
                self.undosplitLineEdit.setText(str(self.undo_split_key))
                self.undo_split_hotkey = keyboard.add_hotkey(str(self.undo_split_key), self.startUndoSplit)
                self.old_undo_split_key = self.undo_split_key
            except ValueError:
                pass

            try:
                self.pauseLineEdit.setText(str(self.pause_key))
            except ValueError:
                pass

            self.checkLiveImage()

        except IOError:
            self.settingsNotFoundError()
            pass
        except Exception:
            self.invalidSettingsError()
            pass

    # exit safely when closing the window
    def closeEvent(self, event):
        self.saveSettings()
        sys.exit()

class ContinueLoop(Exception):
    pass

class BreakLoop(Exception):
    pass

# Widget for dragging screen region
# https://github.com/harupy/snipping-tool
class SelectRegionWidget(QtGui.QWidget):
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
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.show()

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor('red'), 2))
        qp.setBrush(QtGui.QColor('opaque'))
        qp.drawRect(QtCore.QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.close()

        # The coordinates are pulled relative to the top left of the set geometry,
        # so the added virtual screen offsets convert them back to the virtual
        # screen coordinates
        self.left = min(self.begin.x(), self.end.x()) + self.SM_XVIRTUALSCREEN
        self.top = min(self.begin.y(), self.end.y()) + self.SM_YVIRTUALSCREEN
        self.right = max(self.begin.x(), self.end.x()) + self.SM_XVIRTUALSCREEN
        self.bottom = max(self.begin.y(), self.end.y()) + self.SM_YVIRTUALSCREEN

        self.height = self.bottom - self.top
        self.width = self.right - self.left


# widget to select a window and obtain its bounds
class SelectWindowWidget(QtGui.QWidget):
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
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.show()

    def mouseReleaseEvent(self, event):
        self.close()
        self.x = event.pos().x()
        self.y = event.pos().y()


# About Window
class AboutWidget(QtGui.QWidget, about.Ui_aboutAutoSplitWidget):
    def __init__(self):
        super(AboutWidget, self).__init__()
        self.setupUi(self)
        self.createdbyLabel.setOpenExternalLinks(True)
        self.donatebuttonLabel.setOpenExternalLinks(True)
        self.show()


def main():
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('icon.ico'))
    w = AutoSplit()
    w.setWindowIcon(QtGui.QIcon('icon.ico'))
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
