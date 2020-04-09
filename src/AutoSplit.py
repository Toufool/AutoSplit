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
            i = i + 1

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
            except AttributeError:
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
            except AttributeError:
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
            except AttributeError:
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
            except AttributeError:
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
            self.old_pause_key = self.pause_key
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
        split_image_file = split_image_filenames[0]
        split_image_path = split_image_directory + split_image_file
        split_image = cv2.imread(split_image_path, cv2.IMREAD_COLOR)
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

            count = count + 1

        # calculate FPS
        t1 = time.time()
        FPS = int(10 / (t1 - t0))
        FPS = str(FPS)
        self.fpsvalueLabel.setText(FPS)

    # undo split button and hotkey connect to here
    def undoSplit(self):
        if self.undosplitButton.isEnabled() == False:
            return

        if self.loop_number != 1 and self.groupDummySplitsCheckBox.isChecked() == False:
            self.loop_number = self.loop_number - 1

        elif self.groupDummySplitsCheckBox.isChecked() == True:
            for i, group in enumerate(self.split_groups):
                if i > 0 and self.split_image_number in group:
                    self.split_image_number = self.split_groups[i - 1][0]
                    break

        else:
            self.split_image_number = self.split_image_number - 1
            self.loop_number = self.split_image_loop_amount[self.split_image_number]

        self.updateSplitImage()

        return

    # skip split button and hotkey connect to here
    def skipSplit(self):

        if self.skipsplitButton.isEnabled() == False:
            return

        if self.loop_number < self.split_image_loop_amount[self.split_image_number] and self.groupDummySplitsCheckBox.isChecked() == False:
            self.loop_number = self.loop_number + 1
        elif self.groupDummySplitsCheckBox.isChecked() == True:
            for group in self.split_groups:
                if self.split_image_number in group:
                    self.split_image_number = group[-1] + 1
                    break
        else:
            self.split_image_number = self.split_image_number + 1
            self.loop_number = 1

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
        if self.hwnd == 0 or win32gui.GetWindowText(self.hwnd) == '':
            self.regionError()
            return

        # get split image filenames
        self.split_image_filenames = os.listdir(self.split_image_directory)

        # Make sure that each of the images follows the guidelines for correct format
        # according to all of the settings selected by the user.
        for image in self.split_image_filenames:

            # Check to make sure the file is actually an image format that can be opened
            # according to the mask flag
            if split_parser.flags_from_filename(image) & 0x02 == 0x02:
                source = cv2.imread(self.split_image_directory + image, cv2.IMREAD_UNCHANGED)

                if source is None:
                    # Opencv couldn't open this file as an image, this isn't a correct
                    # file format that is supported
                    self.imageTypeError(image)
                    return

                if source.shape[2] != 4:
                    # Error, this file doesn't have an alpha channel even
                    # though the flag for masking was added
                    self.alphaChannelError(image)
                    return

            else:
                if cv2.imread(self.split_image_directory + image, cv2.IMREAD_COLOR) is None:
                    # Opencv couldn't open this file as an image, this isn't a correct
                    # file format that is supported
                    self.imageTypeError(image)
                    return

            if self.custompausetimesCheckBox.isChecked() and split_parser.pause_from_filename(image) is None:
                # Error, this file doesn't have a pause, but the checkbox was
                # selected for unique pause times
                self.customPauseError(image)
                return

            if self.customthresholdsCheckBox.isChecked() and split_parser.threshold_from_filename(image) is None:
                # Error, this file doesn't have a threshold, but the checkbox
                # was selected for unique thresholds
                self.customThresholdError(image)
                return

            if self.pauseLineEdit.text() == '' and split_parser.flags_from_filename(image) & 0x08 == 0x08:
                # Error, no pause hotkey set even though pause flag is set
                self.pauseHotkeyError()
                return

        if self.splitLineEdit.text() == '':
            self.splitHotkeyError()
            return

        # find reset image then remove it from the list
        self.findResetImage()

        # Check that there's only one reset image
        for image in self.split_image_filenames:

            if split_parser.is_reset_image(image):
                self.multipleResetImagesError()
                return

        # if there is no custom threshold for the reset image, throw an error.
        if self.reset_image is not None and self.reset_image_threshold is None:
            self.noResetImageThresholdError()
            return

        # If there is no reset hotkey set but a reset image is present, throw an error.
        if self.resetLineEdit.text() == '' and self.reset_image is not None:
            self.resetHotkeyError()
            return

        # construct groups of splits if needed
        self.split_groups = []
        if self.groupDummySplitsCheckBox.isChecked():
            current_group = []
            self.split_groups.append(current_group)

            for i, image in enumerate(self.split_image_filenames):
                current_group.append(i)

                flags = split_parser.flags_from_filename(image)
                if flags & 0x01 != 0x01 and i < len(self.split_image_filenames) - 1:
                    current_group = []
                    self.split_groups.append(current_group)

        #construct dummy splits array
        self.dummy_splits_array = []
        for i, image in enumerate(self.split_image_filenames):
            if split_parser.flags_from_filename(image) & 0x01 == 0x01:
                self.dummy_splits_array.append(True)
            else:
                self.dummy_splits_array.append(False)


        #construct loop amounts for each split image
        self.split_image_loop_amount = []
        for i, image in enumerate(self.split_image_filenames):
            self.split_image_loop_amount.append(split_parser.loop_from_filename(image))

        if any(x > 1 for x in self.split_image_loop_amount) and self.groupDummySplitsCheckBox.isChecked() == True:
            self.dummySplitsError()
            return

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

        #initialize some settings
        self.split_image_number = 0
        self.loop_number = 1
        self.number_of_split_images = len(self.split_image_filenames)
        self.waiting_for_split_delay = False
        self.split_below_threshold = False

        self.run_start_time = time.time()

        # First while loop: stays in this loop until all of the split images have been split
        while self.split_image_number < self.number_of_split_images:

            # Check if we are not waiting for the split delay to send the key press
            if self.waiting_for_split_delay == True:
                time_millis = int(round(time.time() * 1000))
                if time_millis < self.split_time:
                    QtGui.QApplication.processEvents()
                    continue

            self.updateSplitImage()

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
                    reset_masked = (self.reset_mask is not None)
                    capture = self.getCaptureForComparison(reset_masked)

                    reset_similarity = self.compareImage(self.reset_image, self.reset_mask, capture)
                    if reset_similarity >= self.reset_image_threshold:
                        keyboard.send(str(self.resetLineEdit.text()))
                        self.reset()

                # loop goes into here if start auto splitter text is "Start Auto Splitter"
                if self.startautosplitterButton.text() == 'Start Auto Splitter':
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
                    QtGui.QApplication.processEvents()
                    return

                # get capture again if needed
                masked = (self.flags & 0x02 == 0x02)
                if capture is None or masked != reset_masked:
                    capture = self.getCaptureForComparison(masked)

                # calculate similarity for split image
                self.similarity = self.compareImage(self.split_image, self.mask, capture)

                # show live similarity if the checkbox is checked
                if self.showlivesimilarityCheckBox.isChecked():
                    self.livesimilarityLabel.setText(str(self.similarity)[:4])
                else:
                    self.livesimilarityLabel.setText(' ')

                # if the similarity becomes higher than highest similarity, set it as such.
                if self.similarity > self.highest_similarity:
                    self.highest_similarity = self.similarity

                # show live highest similarity if the checkbox is checked
                if self.showhighestsimilarityCheckBox.isChecked():
                    self.highestsimilarityLabel.setText(str(self.highest_similarity)[:4])
                else:
                    self.highestsimilarityLabel.setText(' ')

                # if its the last split image and last loop number, disable the skip split button
                if (self.split_image_number == self.number_of_split_images - 1 and self.loop_number == self.split_image_loop_amount[self.split_image_number]) or (self.groupDummySplitsCheckBox.isChecked() == True and self.dummy_splits_array[self.split_image_number:].count(False) <= 1):
                    self.skipsplitButton.setEnabled(False)
                else:
                    self.skipsplitButton.setEnabled(True)

                # if its the first split image and first loop, disable the undo split button
                if self.split_image_number == 0 and self.loop_number == 1:
                    self.undosplitButton.setEnabled(False)
                else:
                    self.undosplitButton.setEnabled(True)

                #if the b flag is set, let similarity go above threshold first, then split on similarity below threshold.
                #if no b flag, just split when similarity goes above threshold.
                if self.flags & 0x04 == 0x04 and self.split_below_threshold == False:
                    if self.waiting_for_split_delay == False and self.similarity >= self.similaritythresholdDoubleSpinBox.value():
                        self.split_below_threshold = True
                        continue
                elif self.flags & 0x04 == 0x04 and self.split_below_threshold == True:
                    if self.waiting_for_split_delay == False and self.similarity < self.similaritythresholdDoubleSpinBox.value():
                        self.split_below_threshold = False
                        break
                else:
                    if self.waiting_for_split_delay == False and self.similarity >= self.similaritythresholdDoubleSpinBox.value():
                        break
                        
                # limit the number of time the comparison runs to reduce cpu usage
                fps_limit = self.fpslimitSpinBox.value()
                time.sleep((1 / fps_limit) - (time.time() - start) % (1 / fps_limit))
                QtGui.QApplication.processEvents()


            # comes here when threshold gets met

            # We need to make sure that this isn't a dummy split without pause flag
            # before sending a key press.
            if (self.flags & 0x09 == 0x01):
                pass
            else:
                # If it's a delayed split, check if the delay has passed
                # Otherwise calculate the split time for the key press
                if self.split_delay > 0 and self.waiting_for_split_delay == False:
                    self.split_time = int(round(time.time() * 1000)) + self.split_delay
                    self.waiting_for_split_delay = True

                    self.currentSplitImage.setText('Delayed split...')
                    self.undosplitButton.setEnabled(False)
                    self.skipsplitButton.setEnabled(False)
                    self.currentsplitimagefileLabel.setText(' ')
                    self.currentSplitImage.setAlignment(QtCore.Qt.AlignCenter)

                    # check for reset while delayed
                    delay_start_time = time.time()
                    while time.time() - delay_start_time < (self.split_delay / 1000):
                        # check for reset
                        if win32gui.GetWindowText(self.hwnd) == '':
                            self.reset()
                        if self.startautosplitterButton.text() == 'Start Auto Splitter':
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
                            return

                        # calculate similarity for reset image
                        if self.shouldCheckResetImage() == True:
                            reset_masked = (self.reset_mask is not None)
                            capture = self.getCaptureForComparison(reset_masked)

                            reset_similarity = self.compareImage(self.reset_image, self.reset_mask, capture)
                            if reset_similarity >= self.reset_image_threshold:
                                keyboard.send(str(self.resetLineEdit.text()))
                                self.reset()
                                continue

                        QtTest.QTest.qWait(1)

                self.waiting_for_split_delay = False

                # Split key press unless dummy flag is set
                if (self.flags & 0x01 == 0x00):
                    keyboard.send(str(self.splitLineEdit.text()))

                # Pause key press if pause flag is set
                if (self.flags & 0x08 == 0x08):
                    keyboard.send(str(self.pauseLineEdit.text()))

            #increase loop number if needed, set to 1 if it was the last loop.
            if self.loop_number < self.split_image_loop_amount[self.split_image_number]:
                self.loop_number = self.loop_number + 1
            else:
                self.loop_number = 1

            # if loop check box is checked and its the last split, go to first split.
            # else if current loop amount is back to 1, add 1 to split image number
            # else pass, dont change split image number.
            if self.loopCheckBox.isChecked() and self.split_image_number == self.number_of_split_images - 1 and self.loop_number == 1:
                self.split_image_number = 0
            elif self.loop_number == 1:
                self.split_image_number = self.split_image_number + 1
            else:
                pass

            # set a "pause" split image number. This is done so that it can detect if user hit split/undo split while paused.
            pause_split_image_number = self.split_image_number
            pause_loop_number = self.loop_number

            # if its not the last split image, pause for the amount set by the user
            if self.number_of_split_images != self.split_image_number:
                # set current split image to none
                self.currentSplitImage.setText('none (paused)')
                self.currentsplitimagefileLabel.setText(' ')
                self.currentSplitImage.setAlignment(QtCore.Qt.AlignCenter)
                self.imageloopLabel.setText('Image Loop #:     -')

                # if its the last split image and last loop number, disable the skip split button
                if (self.split_image_number == self.number_of_split_images - 1 and self.loop_number == self.split_image_loop_amount[self.split_image_number]) or (self.groupDummySplitsCheckBox.isChecked() == True and self.dummy_splits_array[self.split_image_number:].count(False) <= 1):
                    self.skipsplitButton.setEnabled(False)
                else:
                    self.skipsplitButton.setEnabled(True)

                # if its the first split image and first loop, disable the undo split button
                if self.split_image_number == 0 and self.loop_number == 1:
                    self.undosplitButton.setEnabled(False)
                else:
                    self.undosplitButton.setEnabled(True)

                QtGui.QApplication.processEvents()

                # I have a pause loop here so that it can check if the user presses skip split, undo split, or reset here.
                # This should probably eventually be a signal... but it works
                pause_start_time = time.time()
                while time.time() - pause_start_time < self.pauseDoubleSpinBox.value():
                    # check for reset
                    if win32gui.GetWindowText(self.hwnd) == '':
                        self.reset()
                    if self.startautosplitterButton.text() == 'Start Auto Splitter':
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
                        return

                    # check for skip/undo split:
                    if self.split_image_number != pause_split_image_number or self.loop_number != pause_loop_number:
                        break

                    # calculate similarity for reset image
                    if self.shouldCheckResetImage() == True:
                        reset_masked = (self.reset_mask is not None)
                        capture = self.getCaptureForComparison(reset_masked)

                        reset_similarity = self.compareImage(self.reset_image, self.reset_mask, capture)
                        if reset_similarity >= self.reset_image_threshold:
                            keyboard.send(str(self.resetLineEdit.text()))
                            self.reset()
                            continue

                    QtTest.QTest.qWait(1)

        # loop breaks to here when the last image splits
        self.startautosplitterButton.setText('Start Auto Splitter')
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
        QtGui.QApplication.processEvents()

    def compareImage(self, image, mask, capture):
        if mask is None:
            if self.comparisonmethodComboBox.currentIndex() == 0:
                return compare.compare_l2_norm(image, capture)
            elif self.comparisonmethodComboBox.currentIndex() == 1:
                return compare.compare_histograms(image, capture)
            elif self.comparisonmethodComboBox.currentIndex() == 2:
                return compare.compare_phash(image, capture)
        else:
            if self.comparisonmethodComboBox.currentIndex() == 0:
                return compare.compare_l2_norm_masked(image, capture, mask)
            elif self.comparisonmethodComboBox.currentIndex() == 1:
                return compare.compare_histograms_masked(image, capture, mask)
            elif self.comparisonmethodComboBox.currentIndex() == 2:
                return compare.compare_phash_masked(image, capture, mask)

    def getCaptureForComparison(self, masked):
        # grab screenshot of capture region
        capture = capture_windows.capture_region(self.hwnd, self.rect)

        # if flagged as a mask, capture with nearest neighbor interpolation. else don't so that
        # threshold settings on versions below 1.2.0 aren't messed up
        if (masked):
            capture = cv2.resize(capture, (self.RESIZE_WIDTH, self.RESIZE_HEIGHT), interpolation=cv2.INTER_NEAREST)
        else:
            capture = cv2.resize(capture, (self.RESIZE_WIDTH, self.RESIZE_HEIGHT))

        # convert to BGR
        capture = cv2.cvtColor(capture, cv2.COLOR_BGRA2BGR)

        return capture

    def shouldCheckResetImage(self):
        if self.reset_image is not None and time.time() - self.run_start_time > self.reset_image_pause_time:
            return True

        return False

    def findResetImage(self):
        self.reset_image = None
        self.reset_mask = None
        self.reset_image_threshold = None

        reset_image_file = None
        for i, image in enumerate(self.split_image_filenames):
            if split_parser.is_reset_image(image):
                reset_image_file = image
                break

        if reset_image_file is None:
            return

        self.split_image_filenames.remove(reset_image_file)

        # create reset image and keep in memory
        path = self.split_image_directory + reset_image_file
        flags = split_parser.flags_from_filename(reset_image_file)

        self.reset_image_threshold = split_parser.threshold_from_filename(reset_image_file)

        self.reset_image_pause_time = split_parser.pause_from_filename(reset_image_file)
        if self.reset_image_pause_time is None:
            self.reset_image_pause_time = 0

        # if theres a mask flag, create a mask
        if (flags & 0x02 == 0x02):
            # create mask based on resized, nearest neighbor interpolated split image
            self.reset_image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            self.reset_image = cv2.resize(self.reset_image, (self.RESIZE_WIDTH, self.RESIZE_HEIGHT),
                                          interpolation=cv2.INTER_NEAREST)
            lower = np.array([0, 0, 0, 1], dtype="uint8")
            upper = np.array([255, 255, 255, 255], dtype="uint8")
            self.reset_mask = cv2.inRange(self.reset_image, lower, upper)

            # set split image as BGR
            self.reset_image = cv2.cvtColor(self.reset_image, cv2.COLOR_BGRA2BGR)

        # else if there is no mask flag, open image normally. don't interpolate nearest neighbor here so setups before 1.2.0 still work.
        else:
            self.reset_image = cv2.imread(path, cv2.IMREAD_COLOR)
            self.reset_image = cv2.resize(self.reset_image, (self.RESIZE_WIDTH, self.RESIZE_HEIGHT))

    def updateSplitImage(self):

        # get split image path
        split_image_file = self.split_image_filenames[0 + self.split_image_number]
        self.split_image_path = self.split_image_directory + split_image_file

        # get flags
        self.flags = split_parser.flags_from_filename(split_image_file)

        # set current split image in UI
        # if flagged as mask, transform transparency into UI's gray BG color
        if (self.flags & 0x02 == 0x02):
            self.split_image_display = cv2.imread(self.split_image_path, cv2.IMREAD_UNCHANGED)
            transparent_mask = self.split_image_display[:, :, 3] == 0
            self.split_image_display[transparent_mask] = [240, 240, 240, 255]
            self.split_image_display = cv2.cvtColor(self.split_image_display, cv2.COLOR_BGRA2RGB)
            self.split_image_display = cv2.resize(self.split_image_display, (240, 180))
        # if not flagged as mask, open normally
        else:
            self.split_image_display = cv2.imread(self.split_image_path, cv2.IMREAD_COLOR)
            self.split_image_display = cv2.cvtColor(self.split_image_display, cv2.COLOR_BGR2RGB)
            self.split_image_display = cv2.resize(self.split_image_display, (240, 180))

        qImg = QtGui.QImage(self.split_image_display, self.split_image_display.shape[1],
                            self.split_image_display.shape[0], self.split_image_display.shape[1] * 3,
                            QtGui.QImage.Format_RGB888)
        self.updateCurrentSplitImage.emit(qImg)
        self.currentsplitimagefileLabel.setText(split_image_file)

        # if theres a mask flag, create a mask
        if (self.flags & 0x02 == 0x02):

            # create mask based on resized, nearest neighbor interpolated split image
            self.split_image = cv2.imread(self.split_image_path, cv2.IMREAD_UNCHANGED)
            self.split_image = cv2.resize(self.split_image, (self.RESIZE_WIDTH, self.RESIZE_HEIGHT),
                                          interpolation=cv2.INTER_NEAREST)
            lower = np.array([0, 0, 0, 1], dtype="uint8")
            upper = np.array([255, 255, 255, 255], dtype="uint8")
            self.mask = cv2.inRange(self.split_image, lower, upper)

            # set split image as BGR
            self.split_image = cv2.cvtColor(self.split_image, cv2.COLOR_BGRA2BGR)

        # else if there is no mask flag, open image normally. don't interpolate nearest neighbor here so setups before 1.2.0 still work.
        else:
            split_image = cv2.imread(self.split_image_path, cv2.IMREAD_COLOR)
            self.split_image = cv2.resize(split_image, (self.RESIZE_WIDTH, self.RESIZE_HEIGHT))
            self.mask = None

        # If the unique parameters are selected, go ahead and set the spinboxes to those values
        if self.custompausetimesCheckBox.isChecked():
            self.pauseDoubleSpinBox.setValue(split_parser.pause_from_filename(split_image_file))

        if self.customthresholdsCheckBox.isChecked():
            self.similaritythresholdDoubleSpinBox.setValue(split_parser.threshold_from_filename(split_image_file))

        # Get delay for split, if any
        self.split_delay = split_parser.delay_from_filename(split_image_file)

        #Set Image Loop #
        self.imageloopLabel.setText("Image Loop #: " + str(self.loop_number))

        #need to set split below threshold to false each time an image updates.
        self.split_below_threshold = False

        self.similarity = 0
        self.highest_similarity = 0.001

    # Error messages

    def splitImageDirectoryError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("No split image folder is selected.")
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
        msgBox.setText("No region is selected. Select a region or reload settings while region window is open")
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
        msgBox.setText("File not a valid image file")
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
        msgBox.setText("Reset Image must have a custom threshold. Please set one and check that it is valid")
        msgBox.exec_()

    def resetHotkeyError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("Your split image folder contains a reset image, but no reset hotkey is set.")
        msgBox.exec_()

    def pauseHotkeyError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("Your split image folder contains an image with the {p} flag, but no pause hotkey is set.")
        msgBox.exec_()

    def dummySplitsError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("Group dummy splits when undoing/skipping cannot be checked if any split image has a loop parameter greater than 1")
        msgBox.exec_()

    def settingsNotFoundError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("No settings file found. The settings file is saved when the program is closed.")
        msgBox.exec_()

    def invalidSettingsError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("The settings file is invalid")
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

        if self.custompausetimesCheckBox.isChecked():
            self.custom_pause_times_setting = 1
        else:
            self.custom_pause_times_setting = 0

        if self.customthresholdsCheckBox.isChecked():
            self.custom_thresholds_setting = 1
        else:
            self.custom_thresholds_setting = 0

        if self.groupDummySplitsCheckBox.isChecked():
            self.group_dummy_splits_undo_skip_setting = 1
        else:
            self.group_dummy_splits_undo_skip_setting = 0

        if self.loopCheckBox.isChecked():
            self.loop_setting = 1
        else:
            self.loop_setting = 0

        # save settings to settings.pkl
        with open(os.path.join(sys.path[0], 'settings.pkl'), 'wb') as f:
            pickle.dump(
                [self.split_image_directory, self.similarity_threshold, self.comparison_index, self.pause,
                 self.fps_limit, self.split_key,
                 self.reset_key, self.skip_split_key, self.undo_split_key, self.x, self.y, self.width, self.height,
                 self.hwnd_title,
                 self.custom_pause_times_setting, self.custom_thresholds_setting,
                 self.group_dummy_splits_undo_skip_setting, self.loop_setting, self.pause_key], f)

    def loadSettings(self):
        try:
            with pickle.load(open(os.path.join(sys.path[0], 'settings.pkl'), 'rb')) as f:
                if len(f) == 18:

                    # the settings file might not include the pause hotkey yet
                    [self.split_image_directory, self.similarity_threshold, self.comparison_index, self.pause,
                    self.fps_limit, self.split_key,
                    self.reset_key, self.skip_split_key, self.undo_split_key, self.x, self.y, self.width, self.height,
                    self.hwnd_title,
                    self.custom_pause_times_setting, self.custom_thresholds_setting,
                    self.group_dummy_splits_undo_skip_setting, self.loop_setting] = f
                else:
                    [self.split_image_directory, self.similarity_threshold, self.comparison_index, self.pause,
                    self.fps_limit, self.split_key,
                    self.reset_key, self.skip_split_key, self.undo_split_key, self.x, self.y, self.width, self.height,
                    self.hwnd_title,
                    self.custom_pause_times_setting, self.custom_thresholds_setting,
                    self.group_dummy_splits_undo_skip_setting, self.loop_setting, self.pause_key] = f

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

            # set custom checkbox's accordingly
            if self.custom_pause_times_setting == 1:
                self.custompausetimesCheckBox.setChecked(True)
            else:
                self.custompausetimesCheckBox.setChecked(False)

            if self.custom_thresholds_setting == 1:
                self.customthresholdsCheckBox.setChecked(True)
            else:
                self.customthresholdsCheckBox.setChecked(False)

            if self.group_dummy_splits_undo_skip_setting == 1:
                self.groupDummySplitsCheckBox.setChecked(True)
            else:
                self.groupDummySplitsCheckBox.setChecked(False)

            if self.loop_setting == 1:
                self.loopCheckBox.setChecked(True)
            else:
                self.loopCheckBox.setChecked(False)

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
                self.old_pause_key = self.pause_key
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
