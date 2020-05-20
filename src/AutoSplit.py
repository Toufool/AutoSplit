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
import split_parser
import errors
from screen_region import SelectRegionWidget, SelectWindowWidget
from hotkeys import Hotkey

class AutoSplit(QtGui.QMainWindow, design.Ui_MainWindow):
    # Importing the functions inside of the class will make them
    # methods of the class
    from screen_region import selectRegion, alignRegion, selectWindow, captureRegion
    from settings_file import loadSettings, saveSettings
    from hotkeys import newHotkey, updateHotkeyLineEdits

    myappid = u'mycompany.myproduct.subproduct.version'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # signals
    updateCurrentSplitImage = QtCore.pyqtSignal(QtGui.QImage)
    startAutoSplitterSignal = QtCore.pyqtSignal()
    resetSignal = QtCore.pyqtSignal()
    skipSplitSignal = QtCore.pyqtSignal()
    undoSplitSignal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(AutoSplit, self).__init__(parent)
        self.setupUi(self)

        # Parse command line args
        self.is_auto_controlled = ('--auto-controlled' in sys.argv)

        # close all processes when closing window
        self.actionView_Help.triggered.connect(self.viewHelp)
        self.actionAbout.triggered.connect(self.about)

        # disable buttons upon open
        self.undosplitButton.setEnabled(False)
        self.skipsplitButton.setEnabled(False)
        self.resetButton.setEnabled(False)

        # Version number
        self.VERSION = "1.4.0"

        # Threads die if this is set to True
        self.kill_threads = False

        self.is_comparison_paused = False

        if self.is_auto_controlled:
            self.setsplithotkeyButton.setEnabled(False)
            self.setresethotkeyButton.setEnabled(False)
            self.setskipsplithotkeyButton.setEnabled(False)
            self.setundosplithotkeyButton.setEnabled(False)
            self.setpausehotkeyButton.setEnabled(False)
            self.startautosplitterButton.setEnabled(False)
            self.splitLineEdit.setEnabled(False)
            self.undosplitLineEdit.setEnabled(False)
            self.skipsplitLineEdit.setEnabled(False)
            self.resetLineEdit.setEnabled(False)
            self.pauseLineEdit.setEnabled(False)

            # Send version and process ID to stdout
            print(str(self.VERSION) + '\n' + str(os.getpid()), flush = True)

            # Create thread that checks for updates from LiveSplit
            threading.Thread(target = self.updateAutoControl).start()
        else:
            # Dictionary of Hotkey objects
            self.hotkeys = {'split': Hotkey(self.startAutoSplitter),
                'reset': Hotkey(self.startReset),
                'skip': Hotkey(self.startSkipSplit),
                'undo': Hotkey(self.startUndoSplit),
                'pause': Hotkey()}

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
        self.pauseComparisonButton.clicked.connect(self.pauseComparison)
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
        self.startimagereloadButton.clicked.connect(self.reloadStartImage)

        # Update x, y, width, and height when changing the value of these spinboxes
        self.xSpinBox.valueChanged.connect(self.updateX)
        self.ySpinBox.valueChanged.connect(self.updateY)
        self.widthSpinBox.valueChanged.connect(self.updateWidth)
        self.heightSpinBox.valueChanged.connect(self.updateHeight)

        # Update similarity threshold and pause time when changing the value of these spinboxes
        self.similaritythresholdDoubleSpinBox.valueChanged.connect(self.updateSimilarityThreshold)
        self.pauseDoubleSpinBox.valueChanged.connect(self.updatePause)

        # connect signals to functions
        self.updateCurrentSplitImage.connect(self.updateSplitImageGUI)
        self.startAutoSplitterSignal.connect(self.autoSplitter)
        self.resetSignal.connect(self.reset)
        self.skipSplitSignal.connect(self.skipSplit)
        self.undoSplitSignal.connect(self.undoSplit)

        # live image checkbox
        self.liveimageCheckBox.clicked.connect(self.checkLiveImage)
        self.timerLiveImage = QtCore.QTimer()
        self.timerLiveImage.timeout.connect(self.liveImageFunction)

        # Automatic timer start
        self.timerStartImage = QtCore.QTimer()
        self.timerStartImage.timeout.connect(self.startImageFunction)
        self.timerStartImage_is_running = False
        self.start_image = None

        # Default Settings for the region capture
        self.hwnd = 0
        self.hwnd_title = ''
        self.rect = ctypes.wintypes.RECT()

        # Get the file's path (PyInstaller compatible)
        if getattr(sys, 'frozen', False):
            self.file_path = os.path.dirname(os.path.abspath(sys.executable))
        else:
            self.file_path = os.path.dirname(os.path.abspath(__file__))

        # This variable exists because the start_auto_splitter image might be
        # marked with dummy flag
        self.hasSentStart = True

        # Auto spliter variables
        self.start_image = None
        self.highest_similarity = 0.0
        self.check_start_image_timestamp = 0.0

        # Try to load settings
        self.loadSettings()

        # Try to load start image
        self.loadStartImage(wait_for_delay = False, is_in_startup = True)

    # FUNCTIONS

    def updateAutoControl(self):
        while self.kill_threads == False:
            line = input()
            if line == 'kill':
                self.kill_threads = True
            elif line == 'start':
                self.startAutoSplitter()
            elif line == 'split' or line == 'skip':
                self.startSkipSplit()
            elif line == 'undo':
                self.startUndoSplit()
            elif line == 'reset':
                self.startReset()

    def viewHelp(self):
        os.system('start "" https://github.com/Toufool/Auto-Split#tutorial')
        return

    def about(self):
        self.AboutWidget = AboutWidget(self.VERSION)

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

    def checkLiveImage(self):
        if self.liveimageCheckBox.isChecked():
            self.timerLiveImage.start(1000 / 60)
        else:
            self.timerLiveImage.stop()
            self.liveImageFunction()

    def liveImageFunction(self):
        try:
            if win32gui.GetWindowText(self.hwnd) == '':
                self.showBox(errors.REGION)
                self.timerLiveImage.stop()
                return

            ctypes.windll.user32.SetProcessDPIAware()

            capture = self.captureRegion(self.hwnd, self.rect)
            capture = cv2.resize(capture, (240, 180))
            capture = cv2.cvtColor(capture, cv2.COLOR_BGRA2RGB)

            # Convert to set it on the label
            qImg = QtGui.QImage(capture, capture.shape[1], capture.shape[0], capture.shape[1] * 3,
                                QtGui.QImage.Format_RGB888)
            pix = QtGui.QPixmap(qImg)
            self.liveImage.setPixmap(pix)

        except AttributeError:
            pass

    def reloadStartImage(self):
        self.loadStartImage(True, False)

    def loadStartImage(self, started_by_button = False, wait_for_delay = True, is_in_startup = False):
        self.timerStartImage.stop()
        self.currentSplitImage.setText(' ')
        self.currentsplitimagefileLabel.setText(' ')
        self.startimageLabel.setText("Start image: not found")
        QtGui.QApplication.processEvents()

        if self.splitimagefolderLineEdit.text() == 'No Folder Selected' or not os.path.exists(self.split_image_directory):
            # Only show error messages if the user clicked the button
            if started_by_button:
                self.showBox(errors.SPLIT_IMAGES_DIRECTORY)
            return
        if self.hwnd == 0 or win32gui.GetWindowText(self.hwnd) == '':
            if started_by_button:
                self.showBox(errors.REGION)
            return

        start_image_name = None

        for image in os.listdir(self.split_image_directory):
            if 'START_AUTO_SPLITTER' in image.upper():
                if start_image_name is None:
                    start_image_name = image
                else:
                    if started_by_button:
                        self.showBox(errors.MULTIPLE_IMAGES_WITH_KEYWORD % 'start_auto_splitter')
                    return

        if start_image_name is None:
            if started_by_button:
                self.showBox(errors.NO_START_IMAGE)
            return

        self.start_image = split_parser.SplitImage(self.split_image_directory, start_image_name, get_custom_framerate = True)

        if self.start_image.threshold is None:
            if started_by_button:
                self.showBox(errors.FORCED_THRESHOLD % 'start_auto_splitter')
            return

        if self.start_image.framerate is None:
            self.start_image.framerate = self.fpslimitSpinBox.value()

        image_error = split_parser.getImageError(self.start_image)

        if image_error is not None:
            if started_by_button:
                showBox(image_error % self.start_image)
            return

        self.start_image.getImage(self.RESIZE_WIDTH, self.RESIZE_HEIGHT)

        if wait_for_delay and self.start_image.pause is not None and self.start_image.pause > 0:
            self.check_start_image_timestamp = time.time() + self.start_image.pause
            self.startimageLabel.setText("Start image: paused")
            self.currentSplitImage.setText('none (paused)')
            self.currentSplitImage.setAlignment(QtCore.Qt.AlignCenter)
            self.highestsimilarityLabel.setText(' ')
        else:
            self.check_start_image_timestamp = 0.0
            self.startimageLabel.setText("Start image: ready")
            self.updateSplitImage(self.start_image, False, False)

        self.highest_similarity = 0.0

        if is_in_startup:
            self.pauseComparisonButton.setText("Unpause Compari..")
            self.is_comparison_paused = True

        self.timerStartImage.start(1000 / self.start_image.framerate)

        QtGui.QApplication.processEvents()

    def startImageFunction(self):
        if time.time() < self.check_start_image_timestamp:
            return

        if self.check_start_image_timestamp > 0:
            self.check_start_image_timestamp = 0.0
            self.startimageLabel.setText("Start image: ready")
            self.updateSplitImage(self.start_image, False, False)

        self.start_image.similarity = self.compareImage(self.start_image.similarity, self.start_image)

        if self.start_image.similarity == errors.REGION:
            self.timerStartImage.stop()

        if self.start_image.similarity is None:
            return

        if self.start_image.similarity > self.highest_similarity:
            self.highest_similarity = self.start_image.similarity

        self.updateLiveSimilarity([self.start_image])

        # If the {b} flag is set, let similarity go above threshold first, then split on similarity below threshold
        # Otherwise just split when similarity goes above threshold
        if self.start_image.flags & 0x04 == 0x04 and self.start_image.split_below_threshold == False and self.start_image.similarity >= self.start_image.threshold:
            self.start_image.split_below_threshold = True
            return
        if (self.start_image.flags & 0x04 == 0x04 and self.start_image.split_below_threshold == True and self.start_image.similarity < self.start_image.threshold) or (self.start_image.similarity >= self.start_image.threshold and self.start_image.flags & 0x04 == 0):
            def split():
                self.hasSentStart = False
                self.sendSplitKeyPress(self.start_image.flags)
                time.sleep(1 / self.fpslimitSpinBox.value())
                self.startAutoSplitter(False)

            self.timerStartImage.stop()
            self.startimageLabel.setText("Start image: started")

            if self.start_image.delay > 0:
                threading.Timer(self.start_image.delay / 1000, split).start()
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
        if self.splitimagefolderLineEdit.text() == 'No Folder Selected' or not os.path.exists(self.split_image_directory):
            self.showBox(errors.SPLIT_IMAGES_DIRECTORY)
            return
        if self.hwnd == 0 or win32gui.GetWindowText(self.hwnd) == '':
            self.showBox(errors.REGION)
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
        capture = self.captureRegion(self.hwnd, self.rect)
        capture = cv2.cvtColor(capture, cv2.COLOR_BGRA2BGR)

        # save and open image
        cv2.imwrite(self.split_image_directory + take_screenshot_filename + '.png', capture)
        os.startfile(self.split_image_directory + take_screenshot_filename + '.png')

    def setSplitHotkey(self):
        self.setsplithotkeyButton.setText('Press a key..')
        self.newHotkey('split', self.splitLineEdit)

    def setResetHotkey(self):
        self.resetLineEdit.setText('Press a key..')
        self.newHotkey('reset', self.resetLineEdit)

    def setSkipSplitHotkey(self):
        self.skipsplitLineEdit.setText('Press a key..')
        self.newHotkey('skip', self.skipsplitLineEdit)

    def setUndoSplitHotkey(self):
        self.setundosplithotkeyButton.setText('Press a key..')
        self.newHotkey('undo', self.undosplitLineEdit)

    def setPauseHotkey(self):
        self.setpausehotkeyButton.setText('Press a key..')
        self.newHotkey('pause', self.pauseLineEdit)

    # check max FPS button connects here.
    def checkFPS(self):
        # error checking
        split_image_directory = self.splitimagefolderLineEdit.text()
        if self.splitimagefolderLineEdit.text() == 'No Folder Selected' or not os.path.exists(self.split_image_directory):
            self.showBox(errors.SPLIT_IMAGES_DIRECTORY)
            return

        split_image_filenames = os.listdir(split_image_directory)
        for image in split_image_filenames:
            if cv2.imread(self.split_image_directory + image, cv2.IMREAD_COLOR) is None:
                self.showBox(errors.IMAGE_TYPE % image)
                return
            else:
                pass

        if self.hwnd == 0 or win32gui.GetWindowText(self.hwnd) == '':
            self.showBox(errors.REGION)
            return

        if self.width == 0 or self.height == 0:
            self.showBox(errors.REGION_SIZE)
            return

        # grab first image in the split image folder
        split_image = cv2.imread(split_image_directory + split_image_filenames[0], cv2.IMREAD_COLOR)
        split_image = cv2.cvtColor(split_image, cv2.COLOR_BGR2RGB)
        split_image = cv2.resize(split_image, (self.RESIZE_WIDTH, self.RESIZE_HEIGHT))

        # run 10 iterations of screenshotting capture region + comparison.
        count = 0
        t0 = time.time()
        while count < 10:

            capture = self.captureRegion(self.hwnd, self.rect)
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
        if self.startautosplitterButton.text() == 'Start Auto Splitter' or (self.split_images[self.split_image_index].undo_image_index is None and self.split_images[self.split_image_index].loop == 1):
            return

        if self.loop_number != 1:
            self.loop_number -= 1
        else:
            self.split_image_index = self.split_images[self.split_image_index].undo_image_index

        self.split_image_index_changed = True

    # skip split button and hotkey connect to here
    def skipSplit(self):
        if self.startautosplitterButton.text() == 'Start Auto Splitter' or (self.split_images[self.split_image_index].skip_image_index is None and self.split_images[self.split_image_index].loop == self.loop_number):
            return

        if self.loop_number < self.split_images[self.split_image_index].loop:
            self.loop_number += 1
        else:
            self.split_image_index = self.split_images[self.split_image_index].skip_image_index

        self.split_image_index_changed = True

    # reset button and hotkey connects here.
    def reset(self):
        self.startautosplitterButton.setText('Start Auto Splitter')

    # Functions for the hotkeys to return to the main thread from signals and start their corresponding functions
    def startAutoSplitter(self, skip_if_running = True):
        self.hasSentStart = True

        # If the auto splitter is already running or the button is disabled, don't emit the signal to start it
        if self.startautosplitterButton.text() == 'Running...':
            if skip_if_running:
                self.skipSplit()
            return

        if self.startimageLabel.text() == "Start image: ready" or self.startimageLabel.text() == "Start image: paused":
            self.startimageLabel.setText("Start image: not ready")

        self.startAutoSplitterSignal.emit()

    def startReset(self):
        self.resetSignal.emit()

    def startSkipSplit(self):
        self.skipSplitSignal.emit()

    def startUndoSplit(self):
        self.undoSplitSignal.emit()

    def pauseComparison(self):
        self.is_comparison_paused = (self.is_comparison_paused == False)
        if self.is_comparison_paused:
            self.pauseComparisonButton.setText("Unpause Compari..")
        else:
            self.pauseComparisonButton.setText("Pause Comparison")

    def autoSplitter(self):
        # Error checking:
        if self.splitimagefolderLineEdit.text() == 'No Folder Selected' or not os.path.exists(self.split_image_directory):
            self.showBox(errors.SPLIT_IMAGES_DIRECTORY, True)
            return
        if len(os.listdir(self.split_image_directory)) == 0:
            self.showBox(errors.NO_SPLIT_IMAGES, True)
            return
        if self.hwnd == 0 or win32gui.GetWindowText(self.hwnd) == '':
            self.showBox(errors.REGION, True)
            return

        # Get split image filenames
        self.split_images = []
        previous_n_flag = False

        for image_filename in os.listdir(self.split_image_directory):
            if 'START_AUTO_SPLITTER' in image_filename.upper() and 'RESET' in image_filename.upper() == False:
                continue

            self.split_images.append(split_parser.SplitImage(self.split_image_directory, image_filename, self.default_similarity_threshold, self.default_pause))

            # Make sure that each of the images follows the guidelines for correct format
            # according to all of the settings selected by the user.

            image_error = split_parser.getImageError(self.split_images[-1])

            if image_error is not None:
                self.showBox(image_error % self.split_images[-1], True)
                return

            if self.pauseLineEdit.text() == '' and self.split_images[-1].flags & 0x08 == 0x08 and self.is_auto_controlled == False:
                # Error, no pause hotkey set even though pause flag is set
                self.showBox(errors.PAUSE_HOTKEY, True)
                return

            if self.splitLineEdit.text() == '' and self.split_images[-1].flags & 0x01 == 0 and self.is_auto_controlled == False:
                # Error, no split hotkey set even though dummy flag is not set
                self.showBox(errors.SPLIT_HOTKEY, True)
                return

            if previous_n_flag and self.split_images[-1].loop > 1:
                # Error, an image with the {n} flag is followed by an image with a loop > 1
                self.showBox(errors.INCLUDE_NEXT_FLAG_WITH_LOOP, True)
                return

            previous_n_flag = self.split_images[-1].flags & 0x10 == 0x10

        # If all images had the keyword 'start_auto_splitter', throw an error
        if self.split_images == []:
            self.showBox(errors.NO_SPLIT_IMAGES, True)
            return

        # If the last split has the {n} flag, throw an error
        if self.split_images[-1].flags & 0x10 == 0x10:
            self.showBox(errors.LAST_IMAGE_HAS_INCLUDE_NEXT_FLAG, True)
            return

        # Find reset image then remove it from the list
        self.reset_image = None
        for i, image in enumerate(self.split_images):
            if image.is_reset_image:
                # Check that there's only one reset image
                if self.reset_image is None:
                    if len(self.split_images) == 1:
                        self.showBox(errors.NO_SPLIT_IMAGES, True)
                        return
                    self.reset_image = image
                    self.split_images.pop(i)
                else:
                    self.showBox(errors.MULTIPLE_IMAGES_WITH_KEYWORD % 'reset', True)
                    return

        if self.reset_image is not None:
            self.reset_image.getImage(self.RESIZE_WIDTH, self.RESIZE_HEIGHT)

            # If there is no custom threshold for the reset image, throw an error
            if self.reset_image.threshold is None:
                self.showBox(errors.FORCED_THRESHOLD % 'reset', True)
                return

            # If the reset image has the {n} flag, throw an error
            if self.reset_image.flags & 0x10 == 0x10:
                self.showBox(errors.IMAGE_HAS_INCLUDE_NEXT_FLAG % 'reset', True)
                return

            # If there is no reset hotkey set but a reset image is present, throw an error
            if self.resetLineEdit.text() == '' and self.is_auto_controlled == False:
                self.showBox(errors.RESET_HOTKEY, True)
                return

            if self.reset_image.pause is None:
                self.reset_image.pause = 0

        # Construct groups of splits
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
                    if i + 1 < len(self.split_images):
                        image.skip_image_index = i + 1

                previous_group_undo = current_group_undo
                current_group_start = i + 1
                current_group_undo = current_group_start

        self.timerStartImage.stop()
        # Change auto splitter button text and disable/enable some buttons
        self.startautosplitterButton.setText('Running...')
        self.browseButton.setEnabled(False)
        self.groupDummySplitsCheckBox.setEnabled(False)
        self.startimagereloadButton.setEnabled(False)
        self.comparisonmethodComboBox.setEnabled(False)
        self.similaritythresholdLabel.setText("Similarity threshold\nCurrent value")
        self.pauseLabel.setText("Pause time (seconds)\nCurrent value")

        if self.is_auto_controlled == False:
            self.startautosplitterButton.setEnabled(False)
            self.resetButton.setEnabled(True)
            self.undosplitButton.setEnabled(False)
            self.skipsplitButton.setEnabled(len(self.split_images) > 1 or self.split_images[0].loop > 1)
            self.setsplithotkeyButton.setEnabled(False)
            self.setresethotkeyButton.setEnabled(False)
            self.setskipsplithotkeyButton.setEnabled(False)
            self.setundosplithotkeyButton.setEnabled(False)
            self.setpausehotkeyButton.setEnabled(False)

        # Initialize some settings
        self.split_image_index = 0
        self.split_image_index_changed = True
        self.loop_number = 1
        self.number_of_split_images = len(self.split_images)

        self.run_start_time = time.time()

        # First while loop: stays in this loop until all of the split images have been split
        while self.split_image_index < self.number_of_split_images:

            # second while loop: stays in this loop until similarity threshold is met
            # skip loop if we just finished waiting for the split delay and need to press the split key!
            start = time.time()
            while True:

                if self.split_image_index_changed:
                    # Construct list of images that should be compared
                    self.current_split_images = []
                    for image in self.split_images[self.split_image_index :]:
                        image.getImage(self.RESIZE_WIDTH, self.RESIZE_HEIGHT)
                        image.loop = self.split_images[self.split_image_index].loop
                        self.current_split_images.append(image)
                        if image.flags & 0x10 == 0:
                            break

                    self.updateSplitImage(self.current_split_images[0], len(self.current_split_images) > 1)
                    self.highest_similarity = 0
                    self.split_image_index_changed = False

                # reset if the set screen region window was closed
                if win32gui.GetWindowText(self.hwnd) == '':
                    self.reset()

                # calculate similarity for reset image
                reset_masked = None
                capture = None

                if self.shouldCheckResetImage():
                    self.reset_image.similarity = self.compareImage(self.reset_image.similarity, self.reset_image)
                    if self.reset_image.similarity == errors.REGION or (self.reset_image.similarity is not None and self.reset_image.similarity >= self.reset_image.threshold):
                        if self.is_auto_controlled:
                            print("reset", flush = True)
                        else:
                            keyboard.send(str(self.resetLineEdit.text()))
                        self.reset()

                # loop goes into here if start auto splitter text is "Start Auto Splitter"
                if self.startautosplitterButton.text() == 'Start Auto Splitter':
                    self.resetUI()
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

                            if type(capture) is str:
                                self.reset()
                                self.resetUI()
                                return

                        image.similarity = self.compareImage(image.similarity, image, capture)
                    else:
                        if masked_capture is None:
                            masked_capture = self.getCaptureForComparison(True)

                            if type(capture) is str:
                                self.reset()
                                self.resetUI()
                                return

                        image.similarity = self.compareImage(image.similarity, image, masked_capture)

                    if image.similarity is None:
                        break

                    # If the similarity becomes higher than highest similarity, set it as such
                    if image.similarity > self.highest_similarity:
                        self.highest_similarity = image.similarity

                self.updateLiveSimilarity(self.current_split_images)

                if self.is_auto_controlled == False:
                    # if its the last split image and last loop number, disable the skip split button
                    self.skipsplitButton.setEnabled(self.current_split_images[0].skip_image_index is not None or self.current_split_images[0].loop != self.loop_number)

                    # if its the first split image and first loop, disable the undo split button
                    self.undosplitButton.setEnabled(self.current_split_images[0].undo_image_index is not None or self.current_split_images[0].loop != 1)

                try:
                    for image in self.current_split_images:
                        if image.similarity is None:
                            break

                        # If the {b} flag is set, let similarity go above threshold first, then split on similarity below threshold
                        # Otherwise just split when similarity goes above threshold
                        if image.flags & 0x04 == 0x04 and image.split_below_threshold == False and image.similarity >= image.threshold:
                            image.split_below_threshold = True
                            raise ContinueLoop
                        if (image.flags & 0x04 == 0x04 and image.split_below_threshold == True and image.similarity < image.threshold) or (image.similarity >= image.threshold and image.flags & 0x04 == 0):
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
            if self.successful_split_image.flags & 0x09 == 0x01:
                pass
            else:
                # If it's a delayed split, check if the delay has passed
                # Otherwise calculate the split time for the key press
                if self.successful_split_image.delay > 0:
                    self.split_time = int(round(time.time() * 1000)) + self.successful_split_image.delay

                    self.currentSplitImage.setText('Delayed split...')
                    self.currentsplitimagefileLabel.setText(' ')
                    self.currentSplitImage.setAlignment(QtCore.Qt.AlignCenter)
                    if self.is_auto_controlled == False:
                        self.undosplitButton.setEnabled(False)
                        self.skipsplitButton.setEnabled(False)

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
                            self.reset_image.similarity = self.compareImage(self.reset_image.similarity, self.reset_image)
                            if self.reset_image.similarity == errors.REGION or (self.reset_image.similarity is not None and self.reset_image.similarity >= self.reset_image.threshold):
                                if self.is_auto_controlled:
                                    print("reset", flush = True)
                                else:
                                    keyboard.send(str(self.resetLineEdit.text()))
                                self.reset()
                                continue

                        QtTest.QTest.qWait(1)

                self.sendSplitKeyPress(self.successful_split_image.flags)

            # Increase loop number if needed, set to 1 if it was the last loop
            if self.loop_number < self.successful_split_image.loop:
                self.loop_number += 1
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
            if self.successful_split_image.pause > 0 and (self.loopCheckBox.isChecked() or len(self.split_images) > self.split_image_index):
                # Set current split image to none
                self.currentSplitImage.setText('none (paused)')
                self.currentsplitimagefileLabel.setText(' ')
                self.currentSplitImage.setAlignment(QtCore.Qt.AlignCenter)
                self.imageloopLabel.setText(' ')

                if self.is_auto_controlled == False:
                    # Make sure the index doesn't exceed the list
                    if self.split_image_index < len(self.split_images):
                        # If it's the last split image and last loop number, disable the skip split button
                        self.skipsplitButton.setEnabled(self.successful_split_image.skip_image_index is not None or self.successful_split_image.loop != self.loop_number)

                        # If it's the first split image and first loop, disable the undo split button
                        self.undosplitButton.setEnabled(self.successful_split_image.undo_image_index is not None or self.successful_split_image.loop != 1)
                    else:
                        self.undosplitButton.setEnabled(False)

                QtGui.QApplication.processEvents()

                # I have a pause loop here so that it can check if the user presses skip split, undo split, or reset here.
                # This should probably eventually be a signal... but it works
                pause_end_time = time.time() + self.successful_split_image.pause
                while time.time() < pause_end_time:
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
                        self.reset_image.similarity = self.compareImage(self.reset_image.similarity, self.reset_image)
                        if self.reset_image.similarity == errors.REGION or (self.reset_image.similarity is not None and self.reset_image.similarity >= self.reset_image.threshold):
                            if self.is_auto_controlled:
                                print("reset", flush = True)
                            else:
                                keyboard.send(str(self.resetLineEdit.text()))
                            self.reset()
                            continue

                    QtTest.QTest.qWait(1)

        # loop breaks to here when the last image splits
        self.reset()
        self.resetUI()

    def resetUI(self):
        self.imageloopLabel.setText(' ')
        self.currentSplitImage.setText(' ')
        self.currentsplitimagefileLabel.setText(' ')
        self.livesimilarityLabel.setText(' ')
        self.highestsimilarityLabel.setText(' ')
        self.browseButton.setEnabled(True)
        self.groupDummySplitsCheckBox.setEnabled(True)
        self.startimagereloadButton.setEnabled(True)
        self.comparisonmethodComboBox.setEnabled(True)
        self.similaritythresholdLabel.setText("Similarity threshold\nDefault value")
        self.pauseLabel.setText("Pause time (seconds)\nDefault value")
        self.similaritythresholdDoubleSpinBox.setValue(self.default_similarity_threshold)
        self.pauseDoubleSpinBox.setValue(self.default_pause)
        self.loadStartImage()

        if self.is_auto_controlled == False:
            self.startautosplitterButton.setEnabled(True)
            self.resetButton.setEnabled(False)
            self.undosplitButton.setEnabled(False)
            self.skipsplitButton.setEnabled(False)
            self.setsplithotkeyButton.setEnabled(True)
            self.setresethotkeyButton.setEnabled(True)
            self.setskipsplithotkeyButton.setEnabled(True)
            self.setundosplithotkeyButton.setEnabled(True)
            self.setpausehotkeyButton.setEnabled(True)

        QtGui.QApplication.processEvents()

    def sendSplitKeyPress(self, flags):
        # Split key press unless dummy flag is set
        if flags & 0x01 == 0x00:
            if self.is_auto_controlled:
                if self.hasSentStart:
                    print("split", flush = True)
                else:
                    print("start", flush = True)
                    self.hasSentStart = True
            else:
                keyboard.send(str(self.splitLineEdit.text()))

        # Pause key press if pause flag is set
        if flags & 0x08 == 0x08:
            if self.is_auto_controlled:
                print("pause", flush = True)
            else:
                keyboard.send(str(self.pauseLineEdit.text()))

    def compareImage(self, previous_similarity, image, capture = None):
        if self.is_comparison_paused:
            return None

        if capture is None:
            capture = self.getCaptureForComparison(image.mask is not None)

        if type(capture) is str:
            return errors.REGION

        try:
            if self.comparisonmethodComboBox.currentIndex() == 0:
                return compare.compare_l2_norm(image, capture)
            if self.comparisonmethodComboBox.currentIndex() == 1:
                return compare.compare_histograms(image, capture)
            if self.comparisonmethodComboBox.currentIndex() == 2:
                return compare.compare_phash(image, capture)
        except Exception as e:
            sys.stderr.write("Comparison failed: " + str(e) + "\n")
            return previous_similarity

    def getCaptureForComparison(self, masked):
        if self.is_comparison_paused:
            return None

        # Grab screenshot of capture region
        capture = self.captureRegion(self.hwnd, self.rect)

        if capture is None:
            self.showBox(errors.REGION)
            return errors.REGION

        # If flagged as a mask, capture with nearest neighbor interpolation. else don't so that
        # threshold settings on versions below 1.2.0 aren't messed up
        if masked:
            capture = cv2.resize(capture, (self.RESIZE_WIDTH, self.RESIZE_HEIGHT), interpolation=cv2.INTER_NEAREST)
        else:
            capture = cv2.resize(capture, (self.RESIZE_WIDTH, self.RESIZE_HEIGHT))

        # Convert to BGR
        capture = cv2.cvtColor(capture, cv2.COLOR_BGRA2BGR)

        return capture

    def shouldCheckResetImage(self):
        return (self.reset_image is not None and time.time() - self.run_start_time > self.reset_image.pause)

    def updateLiveSimilarity(self, images):
        # Show live similarity of first comparison image if the checkbox is checked
        if self.showlivesimilarityCheckBox.isChecked() and images[0].similarity is not None:
            currently_highest_similarity = 0
            for image in images:
                if image.similarity > currently_highest_similarity:
                    currently_highest_similarity = image.similarity
            self.livesimilarityLabel.setText(str(currently_highest_similarity)[: 4])
        else:
            self.livesimilarityLabel.setText(' ')

        # Show live highest similarity if the checkbox is checked
        if self.showhighestsimilarityCheckBox.isChecked():
            self.highestsimilarityLabel.setText(str(self.highest_similarity)[: 4])
        else:
            self.highestsimilarityLabel.setText(' ')

    def updateSplitImage(self, image, multiple_images, update_spinboxes = True):

        if image.loop > 1:
            # Set Image Loop #
            self.imageloopLabel.setText("Image Loop #: " + str(self.loop_number))
        else:
            self.imageloopLabel.setText(' ')

        self.similaritythresholdLabel.setEnabled(multiple_images == False)
        self.pauseLabel.setEnabled(multiple_images == False)

        if multiple_images:
            self.currentSplitImage.setText(str(len(self.current_split_images)) + ' images')
            self.currentsplitimagefileLabel.setText(' ')
            self.currentSplitImage.setAlignment(QtCore.Qt.AlignCenter)

            self.similaritythresholdDoubleSpinBox.setValue(self.default_similarity_threshold)
            self.pauseDoubleSpinBox.setValue(self.default_pause)
            return

        if update_spinboxes:
            if image.threshold is not None:
                self.similaritythresholdDoubleSpinBox.setValue(image.threshold)

            if image.pause is not None:
                self.pauseDoubleSpinBox.setValue(image.pause)

        # Set current split image in UI
        # If flagged as mask, transform transparency into UI's gray BG color
        if image.flags & 0x02 == 0x02:
            self.split_image_display = cv2.imread(image.path, cv2.IMREAD_UNCHANGED)
            transparent_mask = self.split_image_display[:, :, 3] == 0
            self.split_image_display[transparent_mask] = [240, 240, 240, 255]
            self.split_image_display = cv2.cvtColor(self.split_image_display, cv2.COLOR_BGRA2RGB)
            self.split_image_display = cv2.resize(self.split_image_display, (240, 180))
        # If not flagged as mask, open normally
        else:
            self.split_image_display = cv2.imread(image.path, cv2.IMREAD_COLOR)
            self.split_image_display = cv2.cvtColor(self.split_image_display, cv2.COLOR_BGR2RGB)
            self.split_image_display = cv2.resize(self.split_image_display, (240, 180))

        qImg = QtGui.QImage(self.split_image_display, self.split_image_display.shape[1],
                            self.split_image_display.shape[0], self.split_image_display.shape[1] * 3,
                            QtGui.QImage.Format_RGB888)
        self.updateCurrentSplitImage.emit(qImg)
        self.currentsplitimagefileLabel.setText(image.filename)

    def updateSimilarityThreshold(self):
        if self.startautosplitterButton.text() == 'Start Auto Splitter':
            self.default_similarity_threshold = self.similaritythresholdDoubleSpinBox.value()
        else:
            self.split_images[self.split_image_index].threshold = self.similaritythresholdDoubleSpinBox.value()

    def updatePause(self):
        if self.startautosplitterButton.text() == 'Start Auto Splitter':
            self.default_pause = self.pauseDoubleSpinBox.value()
        else:
            self.split_images[self.split_image_index].pause = self.pauseDoubleSpinBox.value()

    # Error messages
    def showBox(self, message, reset = False):
        if reset:
            self.loadStartImage()
            if self.is_auto_controlled:
                print('reset', flush = True)
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText(message)
        msgBox.exec_()

    # exit safely when closing the window
    def closeEvent(self, event):
        if self.is_auto_controlled and self.kill_threads == False:
            print('killme', flush = True)
        self.kill_threads = True
        self.saveSettings()
        sys.exit()

class ContinueLoop(Exception):
    pass

class BreakLoop(Exception):
    pass

# About Window
class AboutWidget(QtGui.QWidget, about.Ui_aboutAutoSplitWidget):
    def __init__(self, VERSION):
        super(AboutWidget, self).__init__()
        self.setupUi(self, VERSION)
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
