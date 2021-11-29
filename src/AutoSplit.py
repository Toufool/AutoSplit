#!/usr/bin/python3.9
# -*- coding: utf-8 -*-

# Imports grouping:
# - Typings
# - Standards
# - Externals
# - Internals
from __future__ import annotations
from types import FunctionType, TracebackType
from typing import Callable, List, Literal, Optional, Type, Union, cast

import sys
import os
import ctypes
import signal
import traceback
from copy import copy
from time import time

import cv2
import numpy as np
from PyQt6 import QtCore, QtGui, QtTest
from PyQt6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox, QWidget
from win32 import win32gui
from win32con import MAXBYTE

import error_messages
import split_parser
from AutoControlledWorker import AutoControlledWorker
from gen import design
from menu_bar import AboutWidget, VERSION, UpdateCheckerWidget, about, viewHelp, checkForUpdates
from capture_windows import capture_region, Rect
from settings_file import auto_split_directory
from split_parser import BELOW_FLAG, DUMMY_FLAG, PAUSE_FLAG
from compare import checkIfImageHasTransparency, compareImage


# Resize to these width and height so that FPS performance increases
COMPARISON_RESIZE_WIDTH = 320
COMPARISON_RESIZE_HEIGHT = 240
COMPARISON_RESIZE = (COMPARISON_RESIZE_WIDTH, COMPARISON_RESIZE_HEIGHT)
DISPLAY_RESIZE_WIDTH = 240
DISPLAY_RESIZE_HEIGHT = 180
DISPLAY_RESIZE = (DISPLAY_RESIZE_WIDTH, DISPLAY_RESIZE_HEIGHT)
CREATE_NEW_ISSUE_MESSAGE = \
    "Please create a New Issue at <a href='https://github.com/Toufool/Auto-Split/issues'>"
"github.com/Toufool/Auto-Split/issues</a>, describe what happened, and copy & paste the error message below"


class AutoSplit(QMainWindow, design.Ui_MainWindow):
    # pylint: disable=import-outside-toplevel
    from hotkeys import send_command
    from settings_file import saveSettings, saveSettingsAs, loadSettings, haveSettingsChanged, getSaveSettingsValues, \
        loadPyQtSettings
    from screen_region import selectRegion, selectWindow, alignRegion, validateBeforeComparison
    from hotkeys import afterSettingHotkey, beforeSettingHotkey, setSplitHotkey, setResetHotkey, setSkipSplitHotkey, \
        setUndoSplitHotkey, setPauseHotkey

    myappid = f'Toufool.AutoSplit.v{VERSION}'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # Parse command line args
    is_auto_controlled = '--auto-controlled' in sys.argv

    # Signals
    updateCurrentSplitImage = QtCore.pyqtSignal(QtGui.QImage)
    startAutoSplitterSignal = QtCore.pyqtSignal()
    resetSignal = QtCore.pyqtSignal()
    skipSplitSignal = QtCore.pyqtSignal()
    undoSplitSignal = QtCore.pyqtSignal()
    pauseSignal = QtCore.pyqtSignal()
    afterSettingHotkeySignal = QtCore.pyqtSignal()
    # Use this signal when trying to show an error from outside the main thread
    showErrorSignal = QtCore.pyqtSignal(FunctionType)

    # Timers
    timerLiveImage = QtCore.QTimer()
    timerStartImage = QtCore.QTimer()

    # Windows
    aboutWidget: AboutWidget
    updateCheckerWidget: UpdateCheckerWidget

    # Settings
    split_image_directory = ""
    similarity_threshold: float
    comparison_index: int
    pause: float
    fps_limit: int
    split_key = ""
    reset_key = ""
    skip_split_key = ""
    undo_split_key = ""
    pause_key = ""
    x: int
    y: int
    width: int
    height: int
    hwnd_title = ''
    group_dummy_splits_undo_skip_setting: Literal[0, 1]
    loop_setting: Literal[0, 1]
    auto_start_on_reset_setting: Literal[0, 1]

    # Default Settings for the region capture
    hwnd = 0
    selection = Rect()

    # hotkeys need to be initialized to be passed as thread arguments in hotkeys.py
    # and for type safety in both hotkeys.py and settings_file.py
    split_hotkey: Optional[Callable[[], None]] = None
    reset_hotkey: Optional[Callable[[], None]] = None
    skip_split_hotkey: Optional[Callable[[], None]] = None
    undo_split_hotkey: Optional[Callable[[], None]] = None
    pause_hotkey: Optional[Callable[[], None]] = None

    # Initialize a few attributes
    last_saved_settings: Optional[List[Union[str, float, int]]] = None
    save_settings_file_path = ""
    load_settings_file_path = ""
    live_image_function_on_open = True
    split_image_loop_amount: List[int] = []
    split_image_number = 0
    loop_number = 1

    # Last loaded settings and last successful loaded settings file path to None until we try to load them
    last_loaded_settings: Optional[List[Union[str, float, int]]] = None
    last_successfully_loaded_settings_file_path: Optional[str] = None

    # Automatic timer start
    timerStartImage_is_running = False
    start_image = None
    highest_similarity = 0.0
    check_start_image_timestamp = 0.0

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setupUi(self)

        self.loadPyQtSettings()

        # close all processes when closing window
        self.actionView_Help.triggered.connect(viewHelp)
        self.actionAbout.triggered.connect(lambda: about(self))
        self.actionCheck_for_Updates.triggered.connect(lambda: checkForUpdates(self))
        self.actionSave_Settings.triggered.connect(self.saveSettings)
        self.actionSave_Settings_As.triggered.connect(self.saveSettingsAs)
        self.actionLoad_Settings.triggered.connect(self.loadSettings)

        # disable buttons upon open
        self.undosplitButton.setEnabled(False)
        self.skipsplitButton.setEnabled(False)
        self.resetButton.setEnabled(False)

        if self.is_auto_controlled:
            self.setsplithotkeyButton.setEnabled(False)
            self.setresethotkeyButton.setEnabled(False)
            self.setskipsplithotkeyButton.setEnabled(False)
            self.setundosplithotkeyButton.setEnabled(False)
            self.setpausehotkeyButton.setEnabled(False)
            self.startautosplitterButton.setEnabled(False)
            self.splitLineEdit.setEnabled(False)
            self.resetLineEdit.setEnabled(False)
            self.skipsplitLineEdit.setEnabled(False)
            self.undosplitLineEdit.setEnabled(False)
            self.pausehotkeyLineEdit.setEnabled(False)
            self.timerglobalhotkeysLabel.setText("Hotkeys Inactive - Use LiveSplit Hotkeys")

            # Send version and process ID to stdout
            print(f"{VERSION}\n{os.getpid()}", flush=True)

            # Use and Start the thread that checks for updates from LiveSplit
            self.update_auto_control = QtCore.QThread()
            worker = AutoControlledWorker(self)
            worker.moveToThread(self.update_auto_control)
            self.update_auto_control.started.connect(worker.run)
            self.update_auto_control.start()

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
        self.startImageReloadButton.clicked.connect(lambda: self.loadStartImage(True, True))

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
        self.showErrorSignal.connect(lambda errorMessageBox: errorMessageBox())

        # live image checkbox
        self.liveimageCheckBox.clicked.connect(self.checkLiveImage)
        self.timerLiveImage.timeout.connect(self.liveImageFunction)

        # Automatic timer start
        self.timerStartImage.timeout.connect(self.startImageFunction)

        # Last loaded settings and last successful loaded settings file path to None until we try to load them
        self.last_loaded_settings = None
        self.last_successfully_loaded_settings_file_path = None

        if not self.is_auto_controlled:
            self.loadSettings(load_settings_on_open=True)

    # FUNCTIONS

    def getGlobalSettingsValues(self):
        self.setting_check_for_updates_on_open = QtCore.QSettings('AutoSplit', 'Check For Updates On Open')

    # TODO add checkbox for going back to image 1 when resetting.
    def browse(self):
        # User selects the file with the split images in it.
        new_split_image_directory = QFileDialog.getExistingDirectory(
            self,
            'Select Split Image Directory',
            os.path.join(self.split_image_directory or auto_split_directory, ".."))

        # If the user doesn't select a folder, it defaults to "".
        if new_split_image_directory:
            # set the split image folder line to the directory text
            self.split_image_directory = new_split_image_directory
            self.splitimagefolderLineEdit.setText(f"{new_split_image_directory}/")
            self.loadStartImage()

    def checkLiveImage(self):
        if self.liveimageCheckBox.isChecked():
            self.timerLiveImage.start(int(1000 / 60))
        else:
            self.timerLiveImage.stop()
            self.liveImageFunction()

    def liveImageFunction(self):
        try:
            if not win32gui.GetWindowText(self.hwnd):
                self.timerLiveImage.stop()
                if self.live_image_function_on_open:
                    self.live_image_function_on_open = False
                else:
                    self.liveImage.clear()
                    error_messages.regionError()
                return

            capture = capture_region(self.hwnd, self.selection)
            capture = cv2.resize(capture, DISPLAY_RESIZE, interpolation=cv2.INTER_NEAREST)

            capture = cv2.cvtColor(capture, cv2.COLOR_BGRA2RGB)

            # Convert to set it on the label
            qImage = QtGui.QImage(cast(bytes, capture),
                                  capture.shape[1],
                                  capture.shape[0],
                                  capture.shape[1] * 3,
                                  QtGui.QImage.Format.Format_RGB888)
            pix = QtGui.QPixmap(qImage)
            self.liveImage.setPixmap(pix)

        except AttributeError:
            pass

    def loadStartImage(self, started_by_button: bool = False, wait_for_delay: bool = True):
        self.timerStartImage.stop()
        self.currentsplitimagefileLabel.setText(' ')
        self.startImageLabel.setText("Start image: not found")
        QApplication.processEvents()

        if not self.validateBeforeComparison(started_by_button):
            return

        self.start_image_name = None
        for image in os.listdir(self.split_image_directory):
            if 'start_auto_splitter' in image.lower():
                if self.start_image_name is None:
                    self.start_image_name = image
                else:
                    if started_by_button:
                        error_messages.multipleKeywordImagesError('start_auto_splitter')
                    return

        if self.start_image_name is None:
            if started_by_button:
                error_messages.noKeywordImageError('start_auto_splitter')
            return

        if self.start_image_name is not None and (not self.splitLineEdit.text() or not self.resetLineEdit.text() or not self.pausehotkeyLineEdit.text()) and not self.is_auto_controlled:
            error_messages.loadStartImageError()
            return

        self.split_image_filenames = os.listdir(self.split_image_directory)
        self.split_image_number = 0
        self.start_image_mask = None
        path = os.path.join(self.split_image_directory, self.start_image_name)

        self.start_image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if self.start_image is None:
            error_messages.imageTypeError(path)
            return
        # if image has transparency, create a mask
        self.imageHasTransparency = checkIfImageHasTransparency(self.start_image)
        if self.imageHasTransparency:
            self.start_image = cv2.resize(self.start_image, COMPARISON_RESIZE, interpolation=cv2.INTER_NEAREST)
            # Create mask based on resized, nearest neighbor interpolated split image
            lower = np.array([0, 0, 0, 1], dtype="uint8")
            upper = np.array([MAXBYTE, MAXBYTE, MAXBYTE, MAXBYTE], dtype="uint8")
            self.start_image_mask = cv2.inRange(self.start_image, lower, upper)

            # set split image as BGR
            self.start_image = cv2.cvtColor(self.start_image, cv2.COLOR_BGRA2BGR)

        # otherwise, open image normally.
        else:
            self.start_image = cv2.imread(path, cv2.IMREAD_COLOR)
            self.start_image = cv2.resize(self.start_image, COMPARISON_RESIZE, interpolation=cv2.INTER_NEAREST)

        start_image_pause = split_parser.pause_from_filename(self.start_image_name)
        if not wait_for_delay and start_image_pause is not None and start_image_pause > 0:
            self.check_start_image_timestamp = time() + start_image_pause
            self.startImageLabel.setText("Start image: paused")
            self.highestsimilarityLabel.setText(' ')
            self.currentsimilaritythresholdnumberLabel.setText(' ')
        else:
            self.check_start_image_timestamp = 0.0
            self.startImageLabel.setText("Start image: ready")
            self.updateSplitImage(self.start_image_name, from_start_image=True)

        self.highest_similarity = 0.0
        self.start_image_split_below_threshold = False
        self.timerStartImage.start(int(1000 / self.fpslimitSpinBox.value()))

        QApplication.processEvents()

    def startImageFunction(self):

        if self.start_image is None \
                or not self.start_image_name \
                or time() < self.check_start_image_timestamp \
                or (not self.splitLineEdit.text() and not self.is_auto_controlled):
            pause_time_left = f"{self.check_start_image_timestamp - time():.1f}"
            self.currentSplitImage.setText(
                f'None\n (Paused before loading Start Image).\n {pause_time_left} sec remaining')
            return

        if self.check_start_image_timestamp > 0:
            self.check_start_image_timestamp = 0.0
            self.startImageLabel.setText("Start image: ready")
            self.updateSplitImage(self.start_image_name, from_start_image=True)

        capture = self.getCaptureForComparison()
        start_image_similarity = compareImage(
            self.comparisonmethodComboBox.currentIndex(),
            self.start_image,
            capture,
            self.start_image_mask)
        start_image_threshold = split_parser.threshold_from_filename(self.start_image_name) \
            or self.similaritythresholdDoubleSpinBox.value()
        self.currentsimilaritythresholdnumberLabel.setText(f"{start_image_threshold:.2f}")
        start_image_flags = split_parser.flags_from_filename(self.start_image_name)
        start_image_delay = split_parser.delay_from_filename(self.start_image_name)

        # Show live similarity if the checkbox is checked
        self.livesimilarityLabel.setText(str(start_image_similarity)[:4]
                                         if self.showlivesimilarityCheckBox.isChecked()
                                         else ' ')

        # If the similarity becomes higher than highest similarity, set it as such.
        if start_image_similarity > self.highest_similarity:
            self.highest_similarity = start_image_similarity

        # Show live highest similarity if the checkbox is checked
        self.highestsimilarityLabel.setText(str(self.highest_similarity)[:4]
                                            if self.showlivesimilarityCheckBox.isChecked()
                                            else ' ')

        # If the {b} flag is set, let similarity go above threshold first, then split on similarity below threshold
        # Otherwise just split when similarity goes above threshold
        if start_image_flags & BELOW_FLAG == BELOW_FLAG \
                and not self.start_image_split_below_threshold \
                and start_image_similarity >= start_image_threshold:
            self.start_image_split_below_threshold = True
            return
        if (start_image_flags & BELOW_FLAG == BELOW_FLAG
            and self.start_image_split_below_threshold
            and start_image_similarity < start_image_threshold) \
                or (start_image_similarity >= start_image_threshold and not start_image_flags & BELOW_FLAG):
            def split():
                self.send_command("start")
                # Email sent to pyqt@riverbankcomputing.com
                QtTest.QTest.qWait(1 / self.fpslimitSpinBox.value())  # type: ignore
                self.startAutoSplitter()

            self.timerStartImage.stop()
            self.start_image_split_below_threshold = False

            # delay start image if needed
            if start_image_delay > 0:
                self.startImageLabel.setText("Start image: delaying start...")
                delay_start_time = time()
                while time() - delay_start_time < (start_image_delay / 1000):
                    delay_time_left = round((start_image_delay / 1000) - (time() - delay_start_time), 1)
                    self.currentSplitImage.setText(f'Delayed Before Starting:\n {delay_time_left} sec remaining')
                    # Email sent to pyqt@riverbankcomputing.com
                    QtTest.QTest.qWait(1)  # type: ignore

            self.startImageLabel.setText("Start image: started")
            split()

    # update x, y, width, height when spinbox values are changed
    def updateX(self):
        try:
            self.selection.left = self.xSpinBox.value()
            self.selection.right = self.selection.left + self.widthSpinBox.value()
            self.checkLiveImage()
        except AttributeError:
            pass

    def updateY(self):
        try:
            self.selection.top = self.ySpinBox.value()
            self.selection.bottom = self.selection.top + self.heightSpinBox.value()
            self.checkLiveImage()
        except AttributeError:
            pass

    def updateWidth(self):
        self.selection.right = self.selection.left + self.widthSpinBox.value()
        self.checkLiveImage()

    def updateHeight(self):
        self.selection.bottom = self.selection.top + self.heightSpinBox.value()
        self.checkLiveImage()

    # update current split image. needed this to avoid updating it through the hotkey thread.
    def updateSplitImageGUI(self, qImage: QtGui.QImage):
        pix = QtGui.QPixmap(qImage)
        self.currentSplitImage.setPixmap(pix)

    def takeScreenshot(self):
        if not self.validateBeforeComparison(check_empty_directory=False):
            return
        take_screenshot_filename = '001_SplitImage'

        # check if file exists and rename it if it does
        # Below starts the FileNameNumber at #001 up to #999. After that it will go to 1000,
        # which is a problem, but I doubt anyone will get to 1000 split images...
        i = 1
        while os.path.exists(os.path.join(self.split_image_directory, f"{take_screenshot_filename}.png")):
            FileNameNumber = (f"{i:03}")
            take_screenshot_filename = f"{FileNameNumber}_SplitImage"
            i += 1

        # grab screenshot of capture region
        capture = capture_region(self.hwnd, self.selection)
        capture = cv2.cvtColor(capture, cv2.COLOR_BGRA2BGR)

        # save and open image
        cv2.imwrite(os.path.join(self.split_image_directory, f"{take_screenshot_filename}.png"), capture)
        os.startfile(os.path.join(self.split_image_directory, f"{take_screenshot_filename}.png"))

    # check max FPS button connects here.
    # TODO: Average on all images and check for transparency (cv2.COLOR_BGRA2RGB and cv2.IMREAD_UNCHANGED)
    def checkFPS(self):
        if not self.validateBeforeComparison():
            return

        split_image_filenames = os.listdir(self.split_image_directory)
        split_images = [
            cv2.imread(os.path.join(self.split_image_directory, image), cv2.IMREAD_COLOR)
            for image
            in split_image_filenames]
        for image in split_images:
            if image is None:
                error_messages.imageTypeError(image)
                return

        # grab first image in the split image folder
        split_image = split_images[0]
        split_image = cv2.cvtColor(split_image, cv2.COLOR_BGR2RGB)
        split_image = cv2.resize(split_image, COMPARISON_RESIZE, interpolation=cv2.INTER_NEAREST)

        # run 10 iterations of screenshotting capture region + comparison.
        count = 0
        t0 = time()
        while count < 10:
            capture = capture_region(self.hwnd, self.selection)
            capture = cv2.resize(capture, COMPARISON_RESIZE, interpolation=cv2.INTER_NEAREST)
            capture = cv2.cvtColor(capture, cv2.COLOR_BGRA2RGB)
            compareImage(self.comparisonmethodComboBox.currentIndex(), split_image, capture)
            count += 1

        # calculate FPS
        t1 = time()
        fps = str(int(10 / (t1 - t0)))
        self.fpsvalueLabel.setText(fps)

    def is_current_split_out_of_range(self):
        return self.split_image_number < 0 \
            or self.split_image_number > len(self.split_image_filenames_including_loops) - 1

    # undo split button and hotkey connect to here
    def undoSplit(self):
        # Can't undo until timer is started
        # or Undoing past the first image
        if self.startautosplitterButton.text() == 'Start Auto Splitter' \
                or "Delayed Split" in self.currentSplitImage.text() \
                or (not self.undosplitButton.isEnabled() and not self.is_auto_controlled) \
                or self.is_current_split_out_of_range():
            return

        if self.groupDummySplitsCheckBox.isChecked():
            for i, group in enumerate(self.split_groups):
                if i > 0 and self.split_image_number in group:
                    self.split_image_number = self.split_groups[i - 1][0]
                    break
        else:
            self.split_image_number -= 1

        self.updateSplitImage()

        return

    # skip split button and hotkey connect to here
    def skipSplit(self):
        # Can't skip or split until timer is started
        # or Splitting/skipping when there are no images left
        if self.startautosplitterButton.text() == 'Start Auto Splitter' \
                or "Delayed Split" in self.currentSplitImage.text() \
                or (not self.skipsplitButton.isEnabled() and not self.is_auto_controlled) \
                or self.is_current_split_out_of_range():
            return

        if self.groupDummySplitsCheckBox.isChecked():
            for group in self.split_groups:
                if self.split_image_number in group:
                    self.split_image_number = group[-1] + 1
                    break
        else:
            self.split_image_number += 1

        self.updateSplitImage()

        return

    # def pause(self):
        # TODO add what to do when you hit pause hotkey, if this even needs to be done

    def reset(self):
        # When the reset button or hotkey is pressed, it will change this text,
        # which will trigger in the autoSplitter function, if running, to abort and change GUI.
        self.startautosplitterButton.setText('Start Auto Splitter')

    # Functions for the hotkeys to return to the main thread from signals and start their corresponding functions
    def startAutoSplitter(self):
        # If the auto splitter is already running or the button is disabled, don't emit the signal to start it.
        if self.startautosplitterButton.text() == 'Running...' \
                or (not self.startautosplitterButton.isEnabled() and not self.is_auto_controlled):
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
        if not self.validateBeforeComparison():
            self.guiChangesOnReset()
            return

        if not self.splitLineEdit.text() and not self.is_auto_controlled:
            self.guiChangesOnReset()
            error_messages.splitHotkeyError()
            return

        # get split image filenames
        self.split_image_filenames = os.listdir(self.split_image_directory)

        split_parser.validate_images_before_parsing(self)

        # find reset image then remove it from the list
        self.findResetImage()

        # Find start_auto_splitter_image and then remove it from the list
        split_parser.removeStartAutoSplitterImage(self.split_image_filenames)

# region TODO I feel this entire region could be simplified

        # construct loop amounts for each split image
        split_image_loop_amount = [
            split_parser.loop_from_filename(image)
            for image
            in self.split_image_filenames]

        # construct a list of filenames, each filename copied with # of loops it has.
        self.split_image_filenames_including_loops: List[str] = []
        for i, filename in enumerate(self.split_image_filenames):
            current_loop = 1
            while split_image_loop_amount[i] >= current_loop:
                self.split_image_filenames_including_loops.append(filename)
                current_loop = current_loop + 1

        # construct a list of corresponding loop number to the filenames
        loop_numbers: List[int] = []
        loop_count = 1
        for i, filename in enumerate(self.split_image_filenames_including_loops):
            if i == 0:
                loop_numbers.append(1)
            else:
                if self.split_image_filenames_including_loops[i] != self.split_image_filenames_including_loops[i - 1]:
                    loop_count = 1
                else:
                    loop_count += 1
                loop_numbers.append(loop_count)

        # Merge them
        self.split_image_filenames_and_loop_number = [
            (filename, loop_numbers[i], self.split_image_filenames_including_loops.count(filename))
            for i, filename in enumerate(self.split_image_filenames_including_loops)
        ]

        # construct groups of splits if needed
        self.split_groups: List[List[int]] = []
        if self.groupDummySplitsCheckBox.isChecked():
            current_group: List[int] = []
            self.split_groups.append(current_group)

            for i, image in enumerate(self.split_image_filenames_including_loops):
                current_group.append(i)

                flags = split_parser.flags_from_filename(image)
                if flags & DUMMY_FLAG != DUMMY_FLAG and i < len(self.split_image_filenames_including_loops) - 1:
                    current_group = []
                    self.split_groups.append(current_group)

# endregion

        self.guiChangesOnStart()

        # Initialize a few attributes
        self.split_image_number = 0
        self.waiting_for_split_delay = False
        self.split_below_threshold = False
        split_time = 0
        number_of_split_images = len(self.split_image_filenames_including_loops)
        dummy_splits_array = [
            split_parser.flags_from_filename(image) & DUMMY_FLAG == DUMMY_FLAG
            for image
            in self.split_image_filenames_including_loops]
        self.run_start_time = time()
        windowText = win32gui.GetWindowText(self.hwnd)

        # First while loop: stays in this loop until all of the split images have been split
        while self.split_image_number < number_of_split_images:

            # Check if we are not waiting for the split delay to send the key press
            if self.waiting_for_split_delay:
                time_millis = int(round(time() * 1000))
                if time_millis < split_time:
                    QApplication.processEvents()
                    continue

            self.updateSplitImage()

            # second while loop: stays in this loop until similarity threshold is met
            # skip loop if we just finished waiting for the split delay and need to press the split key!
            start = time()
            while True:
                # reset if the set screen region window was closed
                if not windowText:
                    self.reset()

                if self.checkForReset():
                    return

                # calculate similarity for reset image
                capture = self.getCaptureForComparison()

                if self.shouldCheckResetImage():
                    reset_similarity = compareImage(
                        self.comparisonmethodComboBox.currentIndex(),
                        self.reset_image,
                        capture,
                        self.reset_mask)
                    if reset_similarity >= self.reset_image_threshold:
                        self.send_command("reset")
                        self.reset()

                if self.checkForReset():
                    return

                # TODO: Check is this actually still needed?
                # get capture again if current and reset image have different mask flags
                if self.imageHasTransparency != (self.reset_mask is not None):
                    capture = self.getCaptureForComparison()

                # calculate similarity for split image
                self.similarity = compareImage(
                    self.comparisonmethodComboBox.currentIndex(),
                    self.split_image,
                    capture,
                    self.image_mask)

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

                if not self.is_auto_controlled:
                    # if its the last split image or can't skip due to grouped dummy splits, disable skip split button
                    is_last = self.split_image_number == number_of_split_images - 1 \
                        or (self.groupDummySplitsCheckBox.isChecked()
                            and dummy_splits_array[self.split_image_number:].count(False) <= 1)
                    self.skipsplitButton.setEnabled(not is_last)

                    # if its the first split image, disable the undo split button
                    self.undosplitButton.setEnabled(self.split_image_number != 0)

                # if the b flag is set, let similarity go above threshold first,
                # then split on similarity below threshold.
                # if no b flag, just split when similarity goes above threshold.
                if not self.waiting_for_split_delay:
                    if self.flags & BELOW_FLAG == BELOW_FLAG and not self.split_below_threshold:
                        if self.similarity >= self.similarity_threshold:
                            self.split_below_threshold = True
                            continue
                    elif self.flags & BELOW_FLAG == BELOW_FLAG and self.split_below_threshold:
                        if self.similarity < self.similarity_threshold:
                            self.split_below_threshold = False
                            break
                    elif self.similarity >= self.similarity_threshold:
                        break

                # limit the number of time the comparison runs to reduce cpu usage
                frame_interval = 1 / self.fpslimitSpinBox.value()
                # Email sent to pyqt@riverbankcomputing.com
                QtTest.QTest.qWait(frame_interval - (time() - start) % frame_interval)  # type: ignore
                QApplication.processEvents()

            # comes here when threshold gets met

            # We need to make sure that this isn't a dummy split before sending
            # the key press.
            if self.flags & DUMMY_FLAG != DUMMY_FLAG:
                # If it's a delayed split, check if the delay has passed
                # Otherwise calculate the split time for the key press
                if self.split_delay > 0 and not self.waiting_for_split_delay:
                    split_time = int(round(time() * 1000) + self.split_delay)
                    self.waiting_for_split_delay = True
                    self.undosplitButton.setEnabled(False)
                    self.skipsplitButton.setEnabled(False)
                    self.currentsplitimagefileLabel.setText(' ')

                    # check for reset while delayed and display a counter of the remaining split delay time
                    delay_start_time = time()
                    split_delay = self.split_delay / 1000
                    while time() - delay_start_time < split_delay:
                        delay_time_left = round(split_delay - (time() - delay_start_time), 1)
                        self.currentSplitImage.setText(f'Delayed Split: {delay_time_left} sec remaining')
                        # check for reset
                        if not windowText:
                            self.reset()
                        if self.checkForReset():
                            return

                        # calculate similarity for reset image
                        if self.shouldCheckResetImage():
                            capture = self.getCaptureForComparison()

                            reset_similarity = compareImage(
                                self.comparisonmethodComboBox.currentIndex(),
                                self.reset_image,
                                capture,
                                self.reset_mask)
                            if reset_similarity >= self.reset_image_threshold:
                                self.send_command("reset")
                                self.reset()
                                continue
                        # Email sent to pyqt@riverbankcomputing.com
                        QtTest.QTest.qWait(1)  # type: ignore

                self.waiting_for_split_delay = False

                # if {p} flag hit pause key, otherwise hit split hotkey
                self.send_command("pause" if self.flags & PAUSE_FLAG == PAUSE_FLAG else "split")

            # if loop check box is checked and its the last split, go to first split.
            # else go to the next split image.
            if self.loopCheckBox.isChecked() and self.split_image_number == number_of_split_images - 1:
                self.split_image_number = 0
            else:
                self.split_image_number += 1

            # Set a "pause" split image number.
            # This is done so that it can detect if user hit split/undo split while paused.
            pause_split_image_number = self.split_image_number

            # if its not the last split image, pause for the amount set by the user
            if number_of_split_images != self.split_image_number:

                if not self.is_auto_controlled:
                    # if its the last split image and last loop number, disable skip split button
                    is_last = self.split_image_number == number_of_split_images - 1 \
                        or (self.groupDummySplitsCheckBox.isChecked()
                            and dummy_splits_array[self.split_image_number:].count(False) <= 1)
                    self.skipsplitButton.setEnabled(not is_last)

                    # if its the first split image, disable the undo split button
                    self.undosplitButton.setEnabled(self.split_image_number != 0)
                QApplication.processEvents()

            # A pause loop to check if the user presses skip split, undo split, or reset here.
            # Also updates the current split image text, counting down the time until the next split image
            if self.pause > 0:
                self.currentsplitimagefileLabel.setText(' ')
                self.imageloopLabel.setText('Image Loop: -')
                pause_start_time = time()
                while time() - pause_start_time < self.pause:
                    pause_time_left = round(self.pause - (time() - pause_start_time), 1)
                    self.currentSplitImage.setText(f'None (Paused). {pause_time_left} sec remaining')

                    # check for reset
                    if not windowText:
                        self.reset()
                    if self.checkForReset():
                        return

                    # check for skip/undo split:
                    if self.split_image_number != pause_split_image_number:
                        break

                    # calculate similarity for reset image
                    if self.shouldCheckResetImage():
                        capture = self.getCaptureForComparison()

                        reset_similarity = compareImage(
                            self.comparisonmethodComboBox.currentIndex(),
                            self.reset_image,
                            capture,
                            self.reset_mask)
                        if reset_similarity >= self.reset_image_threshold:
                            self.send_command("reset")
                            self.reset()
                            continue
                    # Email sent to pyqt@riverbankcomputing.com
                    QtTest.QTest.qWait(1)  # type: ignore

        # loop breaks to here when the last image splits
        self.guiChangesOnReset()

    def guiChangesOnStart(self):
        self.timerStartImage.stop()
        self.startautosplitterButton.setText('Running...')
        self.browseButton.setEnabled(False)
        self.groupDummySplitsCheckBox.setEnabled(False)
        self.startImageReloadButton.setEnabled(False)

        if not self.is_auto_controlled:
            self.startautosplitterButton.setEnabled(False)
            self.resetButton.setEnabled(True)
            self.undosplitButton.setEnabled(True)
            self.skipsplitButton.setEnabled(True)
            self.setsplithotkeyButton.setEnabled(False)
            self.setresethotkeyButton.setEnabled(False)
            self.setskipsplithotkeyButton.setEnabled(False)
            self.setundosplithotkeyButton.setEnabled(False)
            self.setpausehotkeyButton.setEnabled(False)

        QApplication.processEvents()

    def guiChangesOnReset(self):
        self.startautosplitterButton.setText('Start Auto Splitter')
        self.imageloopLabel.setText('Image Loop: -')
        self.currentSplitImage.setText(' ')
        self.currentsplitimagefileLabel.setText(' ')
        self.livesimilarityLabel.setText(' ')
        self.highestsimilarityLabel.setText(' ')
        self.currentsimilaritythresholdnumberLabel.setText(' ')
        self.browseButton.setEnabled(True)
        self.groupDummySplitsCheckBox.setEnabled(True)
        self.startImageReloadButton.setEnabled(True)

        if not self.is_auto_controlled:
            self.startautosplitterButton.setEnabled(True)
            self.resetButton.setEnabled(False)
            self.undosplitButton.setEnabled(False)
            self.skipsplitButton.setEnabled(False)
            self.setsplithotkeyButton.setEnabled(True)
            self.setresethotkeyButton.setEnabled(True)
            self.setskipsplithotkeyButton.setEnabled(True)
            self.setundosplithotkeyButton.setEnabled(True)
            self.setpausehotkeyButton.setEnabled(True)

        QApplication.processEvents()
        self.loadStartImage(False, False)

    def getCaptureForComparison(self):
        # grab screenshot of capture region
        capture = capture_region(self.hwnd, self.selection)
        capture = cv2.resize(capture, COMPARISON_RESIZE, interpolation=cv2.INTER_NEAREST)
        # convert to BGR
        return cv2.cvtColor(capture, cv2.COLOR_BGRA2BGR)

    def shouldCheckResetImage(self):
        return self.reset_image is not None and time() - self.run_start_time > self.reset_image_pause_time

    def findResetImage(self):
        self.reset_image: Optional[cv2.ndarray] = None
        self.reset_mask: Optional[cv2.ndarray] = None

        reset_image_file = None
        for image in self.split_image_filenames:
            if split_parser.is_reset_image(image):
                reset_image_file = image
                break

        if reset_image_file is None:
            return

        self.split_image_filenames.remove(reset_image_file)

        # create reset image and keep in memory
        path = os.path.join(self.split_image_directory, reset_image_file)

        # Override values if they have been specified on the file
        pause_from_filename = split_parser.pause_from_filename(reset_image_file)
        self.reset_image_pause_time = self.pauseDoubleSpinBox.value() \
            if pause_from_filename is None \
            else pause_from_filename
        threshold_from_filename = split_parser.threshold_from_filename(reset_image_file)
        self.reset_image_threshold = self.similaritythresholdDoubleSpinBox.value() \
            if threshold_from_filename is None \
            else threshold_from_filename

        self.reset_image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if self.reset_image is None:
            error_messages.imageTypeError(path)
            return
        # if image has transparency, create a mask
        if checkIfImageHasTransparency(self.reset_image):
            self.reset_image = cv2.resize(self.reset_image, COMPARISON_RESIZE, interpolation=cv2.INTER_NEAREST)
            # Create mask based on resized, nearest neighbor interpolated split image
            lower = np.array([0, 0, 0, 1], dtype="uint8")
            upper = np.array([MAXBYTE, MAXBYTE, MAXBYTE, MAXBYTE], dtype="uint8")
            self.reset_mask = cv2.inRange(self.reset_image, lower, upper)

            # set split image as BGR
            self.reset_image = cv2.cvtColor(self.reset_image, cv2.COLOR_BGRA2BGR)

        # otherwise, open image normally.
        else:
            self.reset_image = cv2.imread(path, cv2.IMREAD_COLOR)
            self.reset_image = cv2.resize(self.reset_image, COMPARISON_RESIZE, interpolation=cv2.INTER_NEAREST)

    def updateSplitImage(self, custom_image_file: str = '', from_start_image: bool = False):
        # Splitting/skipping when there are no images left or Undoing past the first image
        # Start image is expected to be out of range (index 0 of 0-length array)
        if "START_AUTO_SPLITTER" not in custom_image_file.upper() and self.is_current_split_out_of_range():
            self.reset()
            return

        # get split image path
        split_image_file = custom_image_file or self.split_image_filenames_including_loops[0 + self.split_image_number]
        self.split_image_path = os.path.join(self.split_image_directory, split_image_file)

        # get flags
        self.flags = split_parser.flags_from_filename(split_image_file)

        self.split_image = cv2.imread(self.split_image_path, cv2.IMREAD_UNCHANGED)
        if self.split_image is None:
            error_messages.imageTypeError(self.split_image_path)
            return
        self.imageHasTransparency = checkIfImageHasTransparency(self.split_image)
        # if image has transparency, create a mask
        if self.imageHasTransparency:
            split_image_display = copy(self.split_image)
            # Transform transparency into UI's gray BG color
            transparent_mask = split_image_display[:, :, 3] == 0
            split_image_display[:, :, 3] == 0
            split_image_display[transparent_mask] = [240, 240, 240, MAXBYTE]
            split_image_display = cv2.cvtColor(split_image_display, cv2.COLOR_BGRA2RGB)

            self.split_image = cv2.resize(self.split_image, COMPARISON_RESIZE, interpolation=cv2.INTER_NEAREST)
            # Create mask based on resized, nearest neighbor interpolated split image
            lower = np.array([0, 0, 0, 1], dtype="uint8")
            upper = np.array([MAXBYTE, MAXBYTE, MAXBYTE, MAXBYTE], dtype="uint8")
            self.image_mask = cv2.inRange(self.split_image, lower, upper)

            # set split image as BGR
            self.split_image = cv2.cvtColor(self.split_image, cv2.COLOR_BGRA2BGR)

        # otherwise, open image normally.
        else:
            self.split_image = cv2.imread(self.split_image_path, cv2.IMREAD_COLOR)
            split_image_display = cv2.cvtColor(copy(self.split_image), cv2.COLOR_BGR2RGB)
            self.split_image = cv2.resize(self.split_image, COMPARISON_RESIZE, interpolation=cv2.INTER_NEAREST)
            self.image_mask = None

        split_image_display = cv2.resize(split_image_display, DISPLAY_RESIZE)
        # Set current split image in UI
        qImage = QtGui.QImage(cast(bytes, split_image_display),
                              split_image_display.shape[1],
                              split_image_display.shape[0],
                              split_image_display.shape[1] * 3,
                              QtGui.QImage.Format.Format_RGB888)
        self.updateCurrentSplitImage.emit(qImage)
        self.currentsplitimagefileLabel.setText(split_image_file)

        # Override values if they have been specified on the file
        pause_from_filename = split_parser.pause_from_filename(split_image_file)
        self.pause = self.pauseDoubleSpinBox.value() \
            if pause_from_filename is None \
            else pause_from_filename
        threshold_from_filename = split_parser.threshold_from_filename(split_image_file)
        self.similarity_threshold = self.similaritythresholdDoubleSpinBox.value() \
            if threshold_from_filename is None \
            else threshold_from_filename
        self.currentsimilaritythresholdnumberLabel.setText(f"{self.similarity_threshold:.2f}")

        # Get delay for split, if any
        self.split_delay = split_parser.delay_from_filename(split_image_file)

        # Set Image Loop #
        if not from_start_image:
            loop_tuple = self.split_image_filenames_and_loop_number[self.split_image_number]
            self.imageloopLabel.setText(f"Image Loop: {loop_tuple[1]}/{loop_tuple[2]}")
        else:
            self.imageloopLabel.setText("Image Loop: 1/1")

        # need to set split below threshold to false each time an image updates.
        self.split_below_threshold = False

        self.similarity = 0
        self.highest_similarity = 0.001

    # exit safely when closing the window

    def closeEvent(self, a0: Optional[QtGui.QCloseEvent] = None):
        # save global setting values here
        self.setting_check_for_updates_on_open.setValue('check_for_updates_on_open',
                                                        self.actionCheck_for_Updates_on_Open.isChecked())

        def exitProgram():
            if a0 is not None:
                a0.accept()
            if self.is_auto_controlled:
                self.update_auto_control.terminate()
                # stop main thread (which is probably blocked reading input) via an interrupt signal
                # only available for windows in version 3.2 or higher
                os.kill(os.getpid(), signal.SIGINT)
            sys.exit()

        # Simulates LiveSplit quitting without asking. See "TODO" at update_auto_control Worker
        # This also more gracefully exits LiveSplit
        # Users can still manually save their settings
        if a0 is None:
            exitProgram()

        if self.haveSettingsChanged():
            # Give a different warning if there was never a settings file that was loaded successfully,
            # and "save as" instead of "save".
            settings_file_name = "Untitled" \
                if self.last_successfully_loaded_settings_file_path is None \
                else os.path.basename(self.last_successfully_loaded_settings_file_path)
            warning_message = f"Do you want to save changes made to settings file {settings_file_name}?"

            warning = QMessageBox.warning(
                self,
                "AutoSplit",
                warning_message,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)

            if warning is QMessageBox.StandardButton.Yes:
                # TODO: Don't close if user cancelled the save
                self.saveSettingsAs()
                exitProgram()
            if warning is QMessageBox.StandardButton.No:
                exitProgram()
            if warning is QMessageBox.StandardButton.Cancel:
                a0.ignore()
        else:
            exitProgram()


def main():
    app = QApplication(sys.argv)
    try:
        app.setWindowIcon(QtGui.QIcon(':/resources/icon.ico'))
        main_window = AutoSplit()
        main_window.show()
        # Needs to be after main_window.show() to be shown over
        if main_window.actionCheck_for_Updates_on_Open.isChecked():
            checkForUpdates(main_window, check_for_updates_on_open=True)

        # Kickoff the event loop every so often so we can handle KeyboardInterrupt (^C)
        timer = QtCore.QTimer()
        timer.timeout.connect(lambda: None)
        timer.start(500)

        exit_code = app.exec()
    except Exception as exception:
        # Print error to console if not running in executable
        if getattr(sys, 'frozen', False):
            error_messages.exceptionTraceback(
                f"AutoSplit encountered an unrecoverable exception and will now close. {CREATE_NEW_ISSUE_MESSAGE}",
                exception)
        else:
            traceback.print_exception(type(exception), exception, exception.__traceback__)
        sys.exit(1)

    # Catch Keyboard Interrupts for a clean close
    signal.signal(signal.SIGINT, lambda code, _: sys.exit(code))

    sys.exit(exit_code)


def excepthook(exceptionType: Type[BaseException], exception: BaseException, _traceback: Optional[TracebackType]):
    # Catch Keyboard Interrupts for a clean close
    if exceptionType is KeyboardInterrupt:
        sys.exit(0)
    error_messages.exceptionTraceback(
        "AutoSplit encountered an unhandled exception and will try to recover, "
        f"however, there is no guarantee everything will work properly. {CREATE_NEW_ISSUE_MESSAGE}",
        exception)


if __name__ == '__main__':
    sys.excepthook = excepthook
    main()
