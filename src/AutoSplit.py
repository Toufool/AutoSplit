#!/usr/bin/python3.9
# -*- coding: utf-8 -*-

from PyQt6 import QtCore, QtGui, QtTest, QtWidgets
from win32 import win32gui
import sys
import os
import cv2
import ctypes.wintypes
import ctypes
import keyboard
import numpy as np
import threading
import time

import design
import compare
import capture_windows
import split_parser


class AutoSplit(QtWidgets.QMainWindow, design.Ui_MainWindow):
    from hotkeys import (
        beforeSettingHotkey, afterSettingHotkey, setSplitHotkey, setResetHotkey, setSkipSplitHotkey, setUndoSplitHotkey,
        setPauseHotkey)
    from error_messages import (
        splitImageDirectoryError, splitImageDirectoryNotFoundError, imageTypeError, regionError, regionSizeError,
        splitHotkeyError, customThresholdError, customPauseError, alphaChannelError, alignRegionImageTypeError,
        oldVersionSettingsFileError, noSettingsFileOnOpenError, tooManySettingsFilesOnOpenError, invalidSettingsError,
        multipleKeywordImagesError, noResetImageThresholdError, resetHotkeyError, pauseHotkeyError, noKeywordImageError)
    from settings_file import saveSettings, saveSettingsAs, loadSettings, haveSettingsChanged, getSaveSettingsValues
    from screen_region import selectRegion, selectWindow, alignRegion
    from menu_bar import about, VERSION, viewHelp

    myappid = f'Toufool.AutoSplit.v{VERSION}'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # signals
    updateCurrentSplitImage = QtCore.pyqtSignal(QtGui.QImage)
    startAutoSplitterSignal = QtCore.pyqtSignal()
    resetSignal = QtCore.pyqtSignal()
    skipSplitSignal = QtCore.pyqtSignal()
    undoSplitSignal = QtCore.pyqtSignal()
    pauseSignal = QtCore.pyqtSignal()
    afterSettingHotkeySignal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(AutoSplit, self).__init__(parent)
        self.setupUi(self)

        # close all processes when closing window
        self.actionView_Help.triggered.connect(self.viewHelp)
        self.actionAbout.triggered.connect(self.about)
        self.actionSave_Settings.triggered.connect(self.saveSettings)
        self.actionSave_Settings_As.triggered.connect(self.saveSettingsAs)
        self.actionLoad_Settings.triggered.connect(self.loadSettings)

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
        self.startImageReloadButton.clicked.connect(lambda: self.loadStartImage(True, False))

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
        #self.pauseSignal.connect(self.pause)

        # live image checkbox
        self.liveimageCheckBox.clicked.connect(self.checkLiveImage)
        self.timerLiveImage = QtCore.QTimer()
        self.timerLiveImage.timeout.connect(self.liveImageFunction)

        # Default Settings for the region capture
        self.hwnd = 0
        self.hwnd_title = ''
        self.rect = ctypes.wintypes.RECT()

        # Last loaded settings and last successful loaded settings file path to None until we try to load them
        self.last_loaded_settings = None
        self.last_successfully_loaded_settings_file_path = None

        # find all .pkls in AutoSplit folder, error if there is none or more than 1
        self.load_settings_on_open = True
        self.loadSettings()
        self.load_settings_on_open = False

        # initialize a few settings options
        self.last_saved_settings = None

        self.live_image_function_on_open = True

        # Automatic timer start
        self.timerStartImage = QtCore.QTimer()
        self.timerStartImage.timeout.connect(self.startImageFunction)
        self.timerStartImage_is_running = False
        self.start_image = None
        self.highest_similarity = 0.0
        self.check_start_image_timestamp = 0.0

        # Try to load start image
        self.loadStartImage(wait_for_delay=False)

    # FUNCTIONS
    # TODO add checkbox for going back to image 1 when resetting.
    def browse(self):
        # User selects the file with the split images in it.
        self.split_image_directory = str(
            QtWidgets.QFileDialog.getExistingDirectory(self, "Select Split Image Directory")) + '\\'

        # If the user doesn't select a folder, it defaults to \. Set it back to whats in the LineEdit, and return
        if self.split_image_directory == '\\':
            self.split_image_directory = self.splitimagefolderLineEdit.text()
            return

        # set the split image folder line to the directory text
        self.splitimagefolderLineEdit.setText(self.split_image_directory)

    def checkLiveImage(self):
        if self.liveimageCheckBox.isChecked():
            self.timerLiveImage.start(int(1000 / 60))
        else:
            self.timerLiveImage.stop()
            self.liveImageFunction()

    def liveImageFunction(self):
        try:
            if win32gui.GetWindowText(self.hwnd) == '' and self.live_image_function_on_open == True:
                self.timerLiveImage.stop()
                self.live_image_function_on_open = False
                return

            elif win32gui.GetWindowText(self.hwnd) == '' and self.live_image_function_on_open == False:
                self.regionError()
                self.timerLiveImage.stop()
                return

            ctypes.windll.user32.SetProcessDPIAware()

            capture = capture_windows.capture_region(self.hwnd, self.rect)
            capture = cv2.resize(capture, (240, 180))
            capture = cv2.cvtColor(capture, cv2.COLOR_BGRA2RGB)

            # Convert to set it on the label
            qImg = QtGui.QImage(capture, capture.shape[1], capture.shape[0], capture.shape[1] * 3,
                                QtGui.QImage.Format.Format_RGB888)
            pix = QtGui.QPixmap(qImg)
            self.liveImage.setPixmap(pix)

        except AttributeError:
            pass

    def loadStartImage(self, started_by_button=False, wait_for_delay=True):
        self.timerStartImage.stop()
        self.currentsplitimagefileLabel.setText(' ')
        self.startImageLabel.setText("Start image: not found")
        QtWidgets.QApplication.processEvents()

        if self.splitimagefolderLineEdit.text() == 'No Folder Selected' \
                or not os.path.exists(self.split_image_directory):
            # Only show error messages if the user clicked the button
            if started_by_button:
                self.splitImageDirectoryError()
            return
        if self.hwnd == 0 or win32gui.GetWindowText(self.hwnd) == '':
            if started_by_button:
                self.regionError()
            return

        self.start_image_name = None
        for image in os.listdir(self.split_image_directory):
            if 'start_auto_splitter' in image.lower():
                if self.start_image_name is None:
                    self.start_image_name = image
                else:
                    if started_by_button:
                        self.multipleKeywordImagesError('start_auto_splitter')
                    return

        if self.start_image_name is None:
            if started_by_button:
                self.noKeywordImageError('start_auto_splitter')
            return

        self.split_image_filenames = os.listdir(self.split_image_directory)
        self.split_image_number = 0
        self.loop_number = 1
        self.start_image_mask = None
        flags = split_parser.flags_from_filename(self.start_image_name)
        path = self.split_image_directory + self.start_image_name
        # if theres a mask flag, create a mask
        if (flags & 0x02 == 0x02):
            # create mask based on resized, nearest neighbor interpolated split image
            self.start_image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            self.start_image = cv2.resize(self.start_image, (self.RESIZE_WIDTH, self.RESIZE_HEIGHT),
                                          interpolation=cv2.INTER_NEAREST)
            lower = np.array([0, 0, 0, 1], dtype="uint8")
            upper = np.array([255, 255, 255, 255], dtype="uint8")
            self.start_image_mask = cv2.inRange(self.start_image, lower, upper)

            # set split image as BGR
            self.start_image = cv2.cvtColor(self.start_image, cv2.COLOR_BGRA2BGR)

        # else if there is no mask flag, open image normally. don't interpolate nearest neighbor here so setups before 1.2.0 still work.
        else:
            self.start_image = cv2.imread(path, cv2.IMREAD_COLOR)
            self.start_image = cv2.resize(self.start_image, (self.RESIZE_WIDTH, self.RESIZE_HEIGHT))

        start_image_pause = split_parser.pause_from_filename(self.start_image_name)
        if wait_for_delay and start_image_pause is not None and start_image_pause > 0:
            self.check_start_image_timestamp = time.time() + start_image_pause
            self.startImageLabel.setText("Start image: paused")
            self.currentSplitImage.setText('none (paused)')
            self.currentSplitImage.setAlignment(QtCore.Qt.AlignCenter)
            self.highestsimilarityLabel.setText(' ')
        else:
            self.check_start_image_timestamp = 0.0
            self.startImageLabel.setText("Start image: ready")
            self.updateSplitImage(self.start_image_name)

        self.highest_similarity = 0.0

        self.timerStartImage.start(int(1000 / self.fpslimitSpinBox.value()))

        QtWidgets.QApplication.processEvents()

    def startImageFunction(self):
        if time.time() < self.check_start_image_timestamp:
            return

        if self.check_start_image_timestamp > 0:
            self.check_start_image_timestamp = 0.0
            self.startImageLabel.setText("Start image: ready")
            self.updateSplitImage(self.start_image_name)

        start_image_masked = (self.start_image_mask is not None)
        capture = self.getCaptureForComparison(start_image_masked)
        start_image_similarity = self.compareImage(self.start_image, self.start_image_mask, capture)
        start_image_threshold = split_parser.threshold_from_filename(self.start_image_name) \
            or self.similaritythresholdDoubleSpinBox.value()
        start_image_split_below_threshold = False
        start_image_flags = split_parser.flags_from_filename(self.start_image_name)
        start_image_delay = split_parser.delay_from_filename(self.start_image_name)

        if start_image_similarity > self.highest_similarity:
            self.highest_similarity = start_image_similarity

        # If the {b} flag is set, let similarity go above threshold first, then split on similarity below threshold
        # Otherwise just split when similarity goes above threshold
        if start_image_flags & 0x04 == 0x04 \
                and not start_image_split_below_threshold \
                and start_image_similarity >= start_image_threshold:
            start_image_split_below_threshold = True
            return
        if (start_image_flags & 0x04 == 0x04
            and start_image_split_below_threshold
            and start_image_similarity < start_image_threshold) \
                or (start_image_similarity >= start_image_threshold and start_image_flags & 0x04 == 0):
            def split():
                self.hasSentStart = False
                keyboard.send(str(self.splitLineEdit.text()))
                time.sleep(1 / self.fpslimitSpinBox.value())
                self.startAutoSplitter()

            self.timerStartImage.stop()
            self.startImageLabel.setText("Start image: started")

            if start_image_delay > 0:
                threading.Timer(start_image_delay / 1000, split).start()
            else:
                split()

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
        if os.path.exists(self.splitimagefolderLineEdit.text()) == False:
            self.splitImageDirectoryNotFoundError()
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

    # def pause(self):
        # TODO add what to do when you hit pause hotkey, if this even needs to be done

    def reset(self):
        # When the reset button or hotkey is pressed, it will change this text,
        # which will trigger in the autoSplitter function, if running, to abort and change GUI.
        self.startautosplitterButton.setText('Start Auto Splitter')
        return

    # Functions for the hotkeys to return to the main thread from signals and start their corresponding functions
    def startAutoSplitter(self):
        self.hasSentStart = True

        # If the auto splitter is already running or the button is disabled, don't emit the signal to start it
        if self.startautosplitterButton.text() == 'Running...':
            return

        if self.startImageLabel.text() == "Start image: ready" or self.startImageLabel.text() == "Start image: paused":
            self.startImageLabel.setText("Start image: not ready")

        self.startAutoSplitterSignal.emit()

    def startReset(self):
        self.resetSignal.emit()

    def startSkipSplit(self):
        self.skipSplitSignal.emit()

    def startUndoSplit(self):
        self.undoSplitSignal.emit()

    def startPause(self):
        self.pauseSignal.emit()

    def checkForReset(self):
        if self.startautosplitterButton.text() == 'Start Auto Splitter':
            if self.autostartonresetCheckBox.isChecked():
                self.startAutoSplitterSignal.emit()
            else:
                self.guiChangesOnReset()
            return True
        return False

    def autoSplitter(self):
        # error checking:
        if str(self.splitimagefolderLineEdit.text()) == 'No Folder Selected':
            self.guiChangesOnReset()
            self.splitImageDirectoryError()
            return
        if os.path.exists(self.splitimagefolderLineEdit.text()) == False:
            self.guiChangesOnReset()
            self.splitImageDirectoryNotFoundError()
            return
        if self.hwnd ==  0 or win32gui.GetWindowText(self.hwnd) == '':
            self.guiChangesOnReset()
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
                    self.guiChangesOnReset()
                    self.imageTypeError(image)
                    return

                if source.shape[2] != 4:
                    # Error, this file doesn't have an alpha channel even
                    # though the flag for masking was added
                    self.guiChangesOnReset()
                    self.alphaChannelError(image)
                    return

            else:
                if cv2.imread(self.split_image_directory + image, cv2.IMREAD_COLOR) is None:
                    # Opencv couldn't open this file as an image, this isn't a correct
                    # file format that is supported
                    self.guiChangesOnReset()
                    self.imageTypeError(image)
                    return

            #error out if there is a {p} flag but no pause hotkey set.
            if self.pausehotkeyLineEdit.text() == '' and split_parser.flags_from_filename(image) & 0x08 == 0x08:
                self.guiChangesOnReset()
                self.pauseHotkeyError()
                return

            if self.custompausetimesCheckBox.isChecked() and split_parser.pause_from_filename(image) is None:
                # Error, this file doesn't have a pause, but the checkbox was
                # selected for unique pause times
                self.guiChangesOnReset()
                self.customPauseError(image)
                return

            if self.customthresholdsCheckBox.isChecked() and split_parser.threshold_from_filename(image) is None:
                # Error, this file doesn't have a threshold, but the checkbox
                # was selected for unique thresholds
                self.guiChangesOnReset()
                self.customThresholdError(image)
                return

        if self.splitLineEdit.text() == '':
            self.guiChangesOnReset()
            self.splitHotkeyError()
            return

        # find reset image then remove it from the list
        self.findResetImage()

        # Check that there's only one reset image
        for image in self.split_image_filenames:

            if split_parser.is_reset_image(image):
                self.guiChangesOnReset()
                self.multipleKeywordImagesError('reset')
                return

        # if there is no custom threshold for the reset image, throw an error.
        if self.reset_image is not None and self.reset_image_threshold is None:
            self.guiChangesOnReset()
            self.noResetImageThresholdError()
            return

        # If there is no reset hotkey set but a reset image is present, throw an error.
        if self.resetLineEdit.text() == '' and self.reset_image is not None:
            self.guiChangesOnReset()
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

        # construct dummy splits array
        self.dummy_splits_array = []
        for i, image in enumerate(self.split_image_filenames):
            if split_parser.flags_from_filename(image) & 0x01 == 0x01:
                self.dummy_splits_array.append(True)
            else:
                self.dummy_splits_array.append(False)

        # construct loop amounts for each split image
        self.split_image_loop_amount = []
        for i, image in enumerate(self.split_image_filenames):
            self.split_image_loop_amount.append(split_parser.loop_from_filename(image))

        if any(x > 1 for x in self.split_image_loop_amount) and self.groupDummySplitsCheckBox.isChecked() == True:
            self.dummySplitsError()
            return

        self.guiChangesOnStart()

        # initialize some settings
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
                    QtWidgets.QApplication.processEvents()
                    continue

            self.updateSplitImage()

            # second while loop: stays in this loop until similarity threshold is met
            # skip loop if we just finished waiting for the split delay and need to press the split key!
            start = time.time()
            while True:
                # reset if the set screen region window was closed
                if win32gui.GetWindowText(self.hwnd) == '':
                    self.reset()

                if self.checkForReset():
                    return

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

                if self.checkForReset():
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

                # if the b flag is set, let similarity go above threshold first, then split on similarity below threshold.
                # if no b flag, just split when similarity goes above threshold.
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
                QtWidgets.QApplication.processEvents()

            # comes here when threshold gets met

            # We need to make sure that this isn't a dummy split before sending
            # the key press.
            if (self.flags & 0x01 == 0x01):
                pass
            else:
                # If it's a delayed split, check if the delay has passed
                # Otherwise calculate the split time for the key press
                if self.split_delay > 0 and self.waiting_for_split_delay == False:
                    self.split_time = int(round(time.time() * 1000)) + self.split_delay
                    self.waiting_for_split_delay = True
                    self.undosplitButton.setEnabled(False)
                    self.skipsplitButton.setEnabled(False)
                    self.currentsplitimagefileLabel.setText(' ')
                    self.currentSplitImage.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

                    # check for reset while delayed and display a counter of the remaining split delay time
                    delay_start_time = time.time()
                    while time.time() - delay_start_time < (self.split_delay / 1000):
                        self.delay_time_left = str(round((self.split_delay / 1000) - (time.time() - delay_start_time), 1))
                        self.currentSplitImage.setText('Delayed Split: ' + self.delay_time_left + ' sec remaining')
                        # check for reset
                        if win32gui.GetWindowText(self.hwnd) == '':
                            self.reset()
                        if self.checkForReset():
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

                # if {p} flag hit pause key, otherwise hit split hotkey
                if (self.flags & 0x08 == 0x08):
                    keyboard.send(str(self.pausehotkeyLineEdit.text()))
                else:
                    keyboard.send(str(self.splitLineEdit.text()))

            # increase loop number if needed, set to 1 if it was the last loop.
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
                self.currentsplitimagefileLabel.setText(' ')
                self.currentSplitImage.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
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

                QtWidgets.QApplication.processEvents()

                # I have a pause loop here so that it can check if the user presses skip split, undo split, or reset here.
                # Also updates the current split image text, counting down the time until the next split image
                pause_start_time = time.time()
                while time.time() - pause_start_time < self.pauseDoubleSpinBox.value():
                    self.pause_time_left = str(round((self.pauseDoubleSpinBox.value()) - (time.time() - pause_start_time), 1))
                    self.currentSplitImage.setText('None (Paused). ' + self.pause_time_left + ' sec remaining')

                    # check for reset
                    if win32gui.GetWindowText(self.hwnd) == '':
                        self.reset()
                    if self.checkForReset():
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
        self.guiChangesOnReset()

    def guiChangesOnStart(self):
        self.timerStartImage.stop()
        self.startautosplitterButton.setText('Running...')
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
        self.startImageReloadButton.setEnabled(False)
        QtWidgets.QApplication.processEvents()

    def guiChangesOnReset(self):
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
        self.startImageReloadButton.setEnabled(True)
        QtWidgets.QApplication.processEvents()
        self.loadStartImage(False, False)

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

    def updateSplitImage(self, custom_image_file=None):
        # get split image path
        split_image_file = custom_image_file or self.split_image_filenames[0 + self.split_image_number]
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
                            QtGui.QImage.Format.Format_RGB888)
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
            customPause = split_parser.pause_from_filename(split_image_file)
            if customPause is not None:
                self.pauseDoubleSpinBox.setValue()

        if self.customthresholdsCheckBox.isChecked():
            threshold = split_parser.threshold_from_filename(split_image_file)
            if threshold is not None:
                self.similaritythresholdDoubleSpinBox.setValue(threshold)

        # Get delay for split, if any
        self.split_delay = split_parser.delay_from_filename(split_image_file)

        # Set Image Loop #
        self.imageloopLabel.setText("Image Loop #: " + str(self.loop_number))

        # need to set split below threshold to false each time an image updates.
        self.split_below_threshold = False

        self.similarity = 0
        self.highest_similarity = 0.001

    # exit safely when closing the window
    def closeEvent(self, event):
        if self.haveSettingsChanged():
            # give a different warning if there was never a settings file that was loaded successfully, and save as instead of save.
            msgBox = QtWidgets.QMessageBox
            settings_file_name = "Untitled" \
                if self.last_successfully_loaded_settings_file_path is None \
                else os.path.basename(self.last_successfully_loaded_settings_file_path)
            warning_message = f"Do you want to save changes made to settings file {settings_file_name}?"

            warning = msgBox.warning(
                self,
                "AutoSplit",
                warning_message,
                msgBox.StandardButton.Yes | msgBox.StandardButton.No | msgBox.StandardButton.Cancel)

            if warning == msgBox.StandardButton.Yes:
                # TODO: Don't close if user cancelled the save
                self.saveSettingsAs()
                exit()
            if warning == msgBox.StandardButton.No:
                exit()
            if warning == msgBox.StandardButton.Cancel:
                event.ignore()
        else:
            event.accept()
            sys.exit()


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('icon.ico'))
    w = AutoSplit()
    w.setWindowIcon(QtGui.QIcon('icon.ico'))
    w.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
