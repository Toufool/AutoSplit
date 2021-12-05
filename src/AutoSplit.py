#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Imports grouping:
# - Typings
# - Standards
# - Externals
# - Internals
from __future__ import annotations
from collections.abc import Callable
from types import FunctionType, TracebackType
from typing import Literal, Optional, Union, cast

import sys
import os
import ctypes
import signal
import traceback
from copy import copy
from time import time

import certifi
import cv2
import numpy as np
from PyQt6 import QtCore, QtGui, QtTest
from PyQt6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox, QWidget
from win32 import win32gui
from win32con import MAXBYTE

import error_messages
import settings_file as settings
import split_parser
from AutoControlledWorker import AutoControlledWorker
from capture_windows import capture_region, Rect
from compare import check_if_image_has_transparency, compare_image
from gen import about, design, update_checker
from hotkeys import send_command, after_setting_hotkey, set_split_hotkey, set_reset_hotkey, set_skip_split_hotkey, \
    set_undo_split_hotkey, set_pause_hotkey
from menu_bar import open_about, VERSION, view_help, check_for_updates, open_update_checker
from screen_region import select_region, select_window, align_region, validate_before_comparison
from settings_file import FROZEN
from split_parser import BELOW_FLAG, DUMMY_FLAG, PAUSE_FLAG

# Resize to these width and height so that FPS performance increases
COMPARISON_RESIZE_WIDTH = 320
COMPARISON_RESIZE_HEIGHT = 240
COMPARISON_RESIZE = (COMPARISON_RESIZE_WIDTH, COMPARISON_RESIZE_HEIGHT)
DISPLAY_RESIZE_WIDTH = 240
DISPLAY_RESIZE_HEIGHT = 180
DISPLAY_RESIZE = (DISPLAY_RESIZE_WIDTH, DISPLAY_RESIZE_HEIGHT)
CREATE_NEW_ISSUE_MESSAGE = "Please create a New Issue at <a href='https://github.com/Toufool/Auto-Split/issues'>" \
    "github.com/Toufool/Auto-Split/issues</a>, describe what happened, and copy & paste the error message below"
START_IMAGE_TEXT = "Start Image"
START_AUTO_SPLITTER_TEXT = "Start Auto Splitter"

# Needed when compiled, along with the custom hook-requests PyInstaller hook
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()


def make_excepthook(main_window: AutoSplit):
    def excepthook(exception_type: type[BaseException], exception: BaseException, _traceback: Optional[TracebackType]):
        # Catch Keyboard Interrupts for a clean close
        if exception_type is KeyboardInterrupt or isinstance(exception, KeyboardInterrupt):
            sys.exit(0)
        main_window.show_error_signal.emit(lambda: error_messages.exception_traceback(
            "AutoSplit encountered an unhandled exception and will try to recover, "
            f"however, there is no guarantee everything will work properly. {CREATE_NEW_ISSUE_MESSAGE}",
            exception))
    return excepthook


class AutoSplit(QMainWindow, design.Ui_MainWindow):
    myappid = f"Toufool.AutoSplit.v{VERSION}"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # Parse command line args
    is_auto_controlled = "--auto-controlled" in sys.argv

    # Signals
    update_current_split_image = QtCore.pyqtSignal(QtGui.QImage)
    start_auto_splitter_signal = QtCore.pyqtSignal()
    reset_signal = QtCore.pyqtSignal()
    skip_split_signal = QtCore.pyqtSignal()
    undo_split_signal = QtCore.pyqtSignal()
    pause_signal = QtCore.pyqtSignal()
    after_setting_hotkey_signal = QtCore.pyqtSignal()
    update_checker_widget_signal = QtCore.pyqtSignal(str, bool)
    # Use this signal when trying to show an error from outside the main thread
    show_error_signal = QtCore.pyqtSignal(FunctionType)

    # Timers
    timer_live_image = QtCore.QTimer()
    timer_start_image = QtCore.QTimer()

    # Windows
    AboutWidget: about.Ui_AboutAutoSplitWidget
    UpdateCheckerWidget: update_checker.Ui_UpdateChecker
    CheckForUpdatesThread: QtCore.QThread

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
    hwnd_title = ""
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
    last_saved_settings: Optional[list[Union[str, float, int]]] = None
    save_settings_file_path = ""
    load_settings_file_path = ""
    live_image_function_on_open = True
    split_image_loop_amount: list[int] = []
    split_image_number = 0
    loop_number = 1

    # Last loaded settings and last successful loaded settings file path to None until we try to load them
    last_loaded_settings: Optional[list[Union[str, float, int]]] = None
    last_successfully_loaded_settings_file_path: Optional[str] = None

    # Automatic timer start
    timer_start_image_is_running = False
    start_image = None
    highest_similarity = 0.0
    check_start_image_timestamp = 0.0

    # Define all other attributes
    setting_check_for_updates_on_open: QtCore.QSettings
    image_has_transparency: bool
    start_image_split_below_threshold: bool
    waiting_for_split_delay: bool
    split_below_threshold: bool
    split_image_path: str
    split_image_filenames: list[str]
    split_image_filenames_including_loops: list[str]
    split_image_filenames_and_loop_number: list[tuple[str, int, int]]
    split_groups: list[list[int]]
    run_start_time: float
    similarity: float
    reset_image_threshold: float
    reset_image_pause_time: float
    split_delay: float
    flags: int
    reset_image: Optional[cv2.ndarray]
    reset_mask: Optional[cv2.ndarray]
    split_image: cv2.ndarray
    image_mask: Optional[cv2.ndarray]

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Setup global error handling
        self.show_error_signal.connect(lambda errorMessageBox: errorMessageBox())
        # Whithin LiveSplit excepthook needs to use main_window's signals to show errors
        sys.excepthook = make_excepthook(self)

        self.setupUi(self)

        settings.load_pyqt_settings(self)

        # close all processes when closing window
        self.action_view_help.triggered.connect(view_help)
        self.action_about.triggered.connect(lambda: open_about(self))
        self.action_check_for_updates.triggered.connect(lambda: check_for_updates(self))
        self.action_save_settings.triggered.connect(lambda: settings.save_settings(self))
        self.action_save_settings_as.triggered.connect(lambda: settings.save_settings_as(self))
        self.action_load_settings.triggered.connect(lambda: settings.load_settings(self))

        # disable buttons upon open
        self.undo_split_button.setEnabled(False)
        self.skip_split_button.setEnabled(False)
        self.reset_button.setEnabled(False)

        if self.is_auto_controlled:
            self.set_split_hotkey_button.setEnabled(False)
            self.set_reset_hotkey_button.setEnabled(False)
            self.set_skip_split_hotkey_button.setEnabled(False)
            self.set_undo_split_hotkey_button.setEnabled(False)
            self.set_pause_hotkey_button.setEnabled(False)
            self.start_auto_splitter_button.setEnabled(False)
            self.split_input.setEnabled(False)
            self.reset_input.setEnabled(False)
            self.skip_split_input.setEnabled(False)
            self.undo_split_input.setEnabled(False)
            self.pause_hotkey_input.setEnabled(False)
            self.timer_global_hotkeys_label.setText("Hotkeys Inactive - Use LiveSplit Hotkeys")

            # Send version and process ID to stdout
            print(f"{VERSION}\n{os.getpid()}", flush=True)

            # Use and Start the thread that checks for updates from LiveSplit
            self.update_auto_control = QtCore.QThread()
            worker = AutoControlledWorker(self)
            worker.moveToThread(self.update_auto_control)
            self.update_auto_control.started.connect(worker.run)
            self.update_auto_control.start()

        # split image folder line edit text
        self.split_image_folder_input.setText("No Folder Selected")

        # Connecting button clicks to functions
        self.browse_button.clicked.connect(self.browse)
        self.select_region_button.clicked.connect(lambda: select_region(self))
        self.take_screenshot_button.clicked.connect(self.take_screenshot)
        self.start_auto_splitter_button.clicked.connect(self.auto_splitter)
        self.check_fps_button.clicked.connect(self.check_fps)
        self.reset_button.clicked.connect(self.reset)
        self.skip_split_button.clicked.connect(self.skip_split)
        self.undo_split_button.clicked.connect(self.undo_split)
        self.set_split_hotkey_button.clicked.connect(lambda: set_split_hotkey(self))
        self.set_reset_hotkey_button.clicked.connect(lambda: set_reset_hotkey(self))
        self.set_skip_split_hotkey_button.clicked.connect(lambda: set_skip_split_hotkey(self))
        self.set_undo_split_hotkey_button.clicked.connect(lambda: set_undo_split_hotkey(self))
        self.set_pause_hotkey_button.clicked.connect(lambda: set_pause_hotkey(self))
        self.align_region_button.clicked.connect(lambda: align_region(self))
        self.select_window_button.clicked.connect(lambda: select_window(self))
        self.start_image_reload_button.clicked.connect(lambda: self.load_start_image(True, True))
        self.action_check_for_updates_on_open.changed.connect(lambda: settings.set_check_for_updates_on_open(
            self,
            self.action_check_for_updates_on_open.isChecked())
        )

        # update x, y, width, and height when changing the value of these spinbox's are changed
        self.x_spinbox.valueChanged.connect(self.update_x)
        self.y_spinbox.valueChanged.connect(self.update_y)
        self.width_spinbox.valueChanged.connect(self.update_width)
        self.height_spinbox.valueChanged.connect(self.update_height)

        # connect signals to functions
        self.update_current_split_image.connect(self.update_split_image_gui)
        self.after_setting_hotkey_signal.connect(lambda: after_setting_hotkey(self))
        self.start_auto_splitter_signal.connect(self.auto_splitter)
        self.update_checker_widget_signal.connect(lambda latest_version, check_on_open:
                                                  open_update_checker(self, latest_version, check_on_open))
        self.reset_signal.connect(self.reset)
        self.skip_split_signal.connect(self.skip_split)
        self.undo_split_signal.connect(self.undo_split)

        # live image checkbox
        self.live_image_checkbox.clicked.connect(self.check_live_image)
        self.timer_live_image.timeout.connect(self.live_image_function)

        # Automatic timer start
        self.timer_start_image.timeout.connect(self.start_image_function)

        # Last loaded settings and last successful loaded settings file path to None until we try to load them
        self.last_loaded_settings = None
        self.last_successfully_loaded_settings_file_path = None

        if not self.is_auto_controlled:
            settings.load_settings(self, load_settings_on_open=True)

        self.show()

        # Needs to be after Ui_MainWindow.show() to be shown overtop
        if self.action_check_for_updates_on_open.isChecked():
            check_for_updates(self, check_on_open=True)

    # FUNCTIONS

    def get_global_settings_values(self):
        self.setting_check_for_updates_on_open = QtCore.QSettings("AutoSplit", "Check For Updates On Open")

    # TODO add checkbox for going back to image 1 when resetting.
    def browse(self):
        # User selects the file with the split images in it.
        new_split_image_directory = QFileDialog.getExistingDirectory(
            self,
            "Select Split Image Directory",
            os.path.join(self.split_image_directory or settings.auto_split_directory, ".."))

        # If the user doesn't select a folder, it defaults to "".
        if new_split_image_directory:
            # set the split image folder line to the directory text
            self.split_image_directory = new_split_image_directory
            self.split_image_folder_input.setText(f"{new_split_image_directory}/")
            self.load_start_image()

    def check_live_image(self):
        if self.live_image_checkbox.isChecked():
            self.timer_live_image.start(int(1000 / 60))
        else:
            self.timer_live_image.stop()
            self.live_image_function()

    def live_image_function(self):
        try:
            window_text = win32gui.GetWindowText(self.hwnd)
            self.capture_region_window_label.setText(window_text)
            if not window_text:
                self.timer_live_image.stop()
                self.live_image.clear()
                if self.live_image_function_on_open:
                    self.live_image_function_on_open = False
                else:
                    error_messages.region()
                return

            capture = capture_region(self.hwnd, self.selection, self.force_print_window_checkbox.isChecked())
            capture = cv2.resize(capture, DISPLAY_RESIZE, interpolation=cv2.INTER_NEAREST)

            capture = cv2.cvtColor(capture, cv2.COLOR_BGRA2RGB)

            # Convert to set it on the label
            qimage = QtGui.QImage(cast(bytes, capture),
                                  capture.shape[1],
                                  capture.shape[0],
                                  capture.shape[1] * 3,
                                  QtGui.QImage.Format.Format_RGB888)
            pix = QtGui.QPixmap(qimage)
            self.live_image.setPixmap(pix)

        except AttributeError:
            pass

    def load_start_image(self, started_by_button: bool = False, wait_for_delay: bool = True):
        self.timer_start_image.stop()
        self.current_split_image_file_label.setText(" ")
        self.start_image_label.setText(f"{START_IMAGE_TEXT}: not found")
        QApplication.processEvents()

        if not validate_before_comparison(self, started_by_button):
            return

        self.start_image_name = None
        for image in os.listdir(self.split_image_directory):
            if "start_auto_splitter" in image.lower():
                if self.start_image_name is None:
                    self.start_image_name = image
                else:
                    if started_by_button:
                        error_messages.multiple_keyword_images("start_auto_splitter")
                    return

        if self.start_image_name is None:
            if started_by_button:
                error_messages.no_keyword_image("start_auto_splitter")
            return

        if self.start_image_name is not None \
            and not self.is_auto_controlled \
            and (not self.split_input.text()
                 or not self.reset_input.text()
                 or not self.pause_hotkey_input.text()):
            error_messages.load_start_image()
            return

        self.split_image_filenames = os.listdir(self.split_image_directory)
        self.split_image_number = 0
        self.start_image_mask = None
        path = os.path.join(self.split_image_directory, self.start_image_name)

        self.start_image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if self.start_image is None:
            error_messages.image_type(path)
            return
        # if image has transparency, create a mask
        self.image_has_transparency = check_if_image_has_transparency(self.start_image)
        if self.image_has_transparency:
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
            self.start_image_label.setText(f"{START_IMAGE_TEXT}: paused")
            self.highest_similarity_label.setText(" ")
            self.current_similarity_threshold_number_label.setText(" ")
        else:
            self.check_start_image_timestamp = 0.0
            self.start_image_label.setText(f"{START_IMAGE_TEXT}: ready")
            self.update_split_image(self.start_image_name, from_start_image=True)

        self.highest_similarity = 0.0
        self.start_image_split_below_threshold = False
        self.timer_start_image.start(int(1000 / self.fps_limit_spinbox.value()))

        QApplication.processEvents()

    def start_image_function(self):
        if self.start_image is None \
                or not self.start_image_name \
                or time() < self.check_start_image_timestamp \
                or (not self.split_input.text() and not self.is_auto_controlled):
            pause_time_left = f"{self.check_start_image_timestamp - time():.1f}"
            self.current_split_image.setText(
                f"None\n (Paused before loading {START_IMAGE_TEXT}).\n {pause_time_left} sec remaining")
            return

        if self.check_start_image_timestamp > 0:
            self.check_start_image_timestamp = 0.0
            self.start_image_label.setText(f"{START_IMAGE_TEXT}: ready")
            self.update_split_image(self.start_image_name, from_start_image=True)

        capture = self.get_capture_for_comparison()
        start_image_similarity = compare_image(
            self.comparison_method_combobox.currentIndex(),
            self.start_image,
            capture,
            self.start_image_mask)
        start_image_threshold = split_parser.threshold_from_filename(self.start_image_name) \
            or self.similarity_threshold_spinbox.value()
        self.current_similarity_threshold_number_label.setText(f"{start_image_threshold:.2f}")
        start_image_flags = split_parser.flags_from_filename(self.start_image_name)
        start_image_delay = split_parser.delay_from_filename(self.start_image_name)

        # Show live similarity if the checkbox is checked
        self.live_similarity_label.setText(str(start_image_similarity)[:4]
                                           if self.show_live_similarity_checkbox.isChecked()
                                           else " ")

        # If the similarity becomes higher than highest similarity, set it as such.
        if start_image_similarity > self.highest_similarity:
            self.highest_similarity = start_image_similarity

        # Show live highest similarity if the checkbox is checked
        self.highest_similarity_label.setText(str(self.highest_similarity)[:4]
                                              if self.show_live_similarity_checkbox.isChecked()
                                              else " ")

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
                send_command(self, "start")
                # Email sent to pyqt@riverbankcomputing.com
                QtTest.QTest.qWait(1 / self.fps_limit_spinbox.value())  # type: ignore
                self.start_suto_splitter()

            self.timer_start_image.stop()
            self.start_image_split_below_threshold = False

            # delay start image if needed
            if start_image_delay > 0:
                self.start_image_label.setText(f"{START_IMAGE_TEXT}: delaying start...")
                delay_start_time = time()
                while time() - delay_start_time < (start_image_delay / 1000):
                    delay_time_left = round((start_image_delay / 1000) - (time() - delay_start_time), 1)
                    self.current_split_image.setText(
                        f"Delayed Before Starting:\n {delay_time_left} sec remaining")
                    # Email sent to pyqt@riverbankcomputing.com
                    QtTest.QTest.qWait(1)  # type: ignore

            self.start_image_label.setText(f"{START_IMAGE_TEXT}: started")
            split()

    # update x, y, width, height when spinbox values are changed
    def update_x(self):
        try:
            self.selection.left = self.x_spinbox.value()
            self.selection.right = self.selection.left + self.width_spinbox.value()
            self.check_live_image()
        except AttributeError:
            pass

    def update_y(self):
        try:
            self.selection.top = self.y_spinbox.value()
            self.selection.bottom = self.selection.top + self.height_spinbox.value()
            self.check_live_image()
        except AttributeError:
            pass

    def update_width(self):
        self.selection.right = self.selection.left + self.width_spinbox.value()
        self.check_live_image()

    def update_height(self):
        self.selection.bottom = self.selection.top + self.height_spinbox.value()
        self.check_live_image()

    # update current split image. needed this to avoid updating it through the hotkey thread.
    def update_split_image_gui(self, qimage: QtGui.QImage):
        pix = QtGui.QPixmap(qimage)
        self.current_split_image.setPixmap(pix)

    def take_screenshot(self):
        if not validate_before_comparison(self, check_empty_directory=False):
            return
        take_screenshot_filename = "001_SplitImage"

        # check if file exists and rename it if it does
        # Below starts the file_name_number at #001 up to #999. After that it will go to 1000,
        # which is a problem, but I doubt anyone will get to 1000 split images...
        i = 1
        while os.path.exists(os.path.join(self.split_image_directory, f"{take_screenshot_filename}.png")):
            file_name_number = (f"{i:03}")
            take_screenshot_filename = f"{file_name_number}_SplitImage"
            i += 1

        # grab screenshot of capture region
        capture = capture_region(self.hwnd, self.selection, self.force_print_window_checkbox.isChecked())
        capture = cv2.cvtColor(capture, cv2.COLOR_BGRA2BGR)

        # save and open image
        cv2.imwrite(os.path.join(self.split_image_directory, f"{take_screenshot_filename}.png"), capture)
        os.startfile(os.path.join(self.split_image_directory, f"{take_screenshot_filename}.png"))

    # check max FPS button connects here.
    # TODO: Average on all images and check for transparency (cv2.COLOR_BGRA2RGB and cv2.IMREAD_UNCHANGED)
    def check_fps(self):
        if not validate_before_comparison(self):
            return

        split_image_filenames = os.listdir(self.split_image_directory)
        split_images = [
            cv2.imread(os.path.join(self.split_image_directory, image), cv2.IMREAD_COLOR)
            for image
            in split_image_filenames]
        for i, image in enumerate(split_images):
            if image is None:
                error_messages.image_type(split_image_filenames[i])
                return

        # grab first image in the split image folder
        split_image = split_images[0]
        split_image = cv2.cvtColor(split_image, cv2.COLOR_BGR2RGB)
        split_image = cv2.resize(split_image, COMPARISON_RESIZE, interpolation=cv2.INTER_NEAREST)

        # run 10 iterations of screenshotting capture region + comparison.
        count = 0
        t0 = time()
        while count < 10:
            capture = capture_region(self.hwnd, self.selection, self.force_print_window_checkbox.isChecked())
            capture = cv2.resize(capture, COMPARISON_RESIZE, interpolation=cv2.INTER_NEAREST)
            capture = cv2.cvtColor(capture, cv2.COLOR_BGRA2RGB)
            compare_image(self.comparison_method_combobox.currentIndex(), split_image, capture)
            count += 1

        # calculate FPS
        t1 = time()
        fps = str(int(10 / (t1 - t0)))
        self.fps_value_label.setText(fps)

    def is_current_split_out_of_range(self):
        return self.split_image_number < 0 \
            or self.split_image_number > len(self.split_image_filenames_including_loops) - 1

    # undo split button and hotkey connect to here
    def undo_split(self):
        # Can't undo until timer is started
        # or Undoing past the first image
        if self.start_auto_splitter_button.text() == START_AUTO_SPLITTER_TEXT \
                or "Delayed Split" in self.current_split_image.text() \
                or (not self.undo_split_button.isEnabled() and not self.is_auto_controlled) \
                or self.is_current_split_out_of_range():
            return

        if self.group_dummy_splits_checkbox.isChecked():
            for i, group in enumerate(self.split_groups):
                if i > 0 and self.split_image_number in group:
                    self.split_image_number = self.split_groups[i - 1][0]
                    break
        else:
            self.split_image_number -= 1

        self.update_split_image()

    # skip split button and hotkey connect to here
    def skip_split(self):
        # Can't skip or split until timer is started
        # or Splitting/skipping when there are no images left
        if self.start_auto_splitter_button.text() == START_AUTO_SPLITTER_TEXT \
                or "Delayed Split" in self.current_split_image.text() \
                or (not self.skip_split_button.isEnabled() and not self.is_auto_controlled) \
                or self.is_current_split_out_of_range():
            return

        if self.group_dummy_splits_checkbox.isChecked():
            for group in self.split_groups:
                if self.split_image_number in group:
                    self.split_image_number = group[-1] + 1
                    break
        else:
            self.split_image_number += 1

        self.update_split_image()

    # def pause(self):
        # TODO add what to do when you hit pause hotkey, if this even needs to be done

    def reset(self):
        # When the reset button or hotkey is pressed, it will change this text,
        # which will trigger in the auto_splitter function, if running, to abort and change GUI.
        self.start_auto_splitter_button.setText(START_AUTO_SPLITTER_TEXT)

    # Functions for the hotkeys to return to the main thread from signals and start their corresponding functions
    def start_suto_splitter(self):
        # If the auto splitter is already running or the button is disabled, don't emit the signal to start it.
        if self.start_auto_splitter_button.text() == "Running..." \
                or (not self.start_auto_splitter_button.isEnabled() and not self.is_auto_controlled):
            return

        if self.start_image_label.text() == f"{START_IMAGE_TEXT}: ready" or self.start_image_label.text(
        ) == f"{START_IMAGE_TEXT}: paused":
            self.start_image_label.setText(f"{START_IMAGE_TEXT}: not ready")

        self.start_auto_splitter_signal.emit()

    def start_reset(self):
        self.reset_signal.emit()

    def start_skip_split(self):
        self.skip_split_signal.emit()

    def start_undo_split(self):
        self.undo_split_signal.emit()

    def start_pause(self):
        self.pause_signal.emit()

    def check_for_reset(self):
        if self.start_auto_splitter_button.text() == START_AUTO_SPLITTER_TEXT:
            if self.auto_start_on_reset_checkbox.isChecked():
                self.start_auto_splitter_signal.emit()
            else:
                self.gui_changes_on_reset()
            return True
        return False

    def auto_splitter(self):
        if not validate_before_comparison(self):
            self.gui_changes_on_reset()
            return

        if not self.split_input.text() and not self.is_auto_controlled:
            self.gui_changes_on_reset()
            error_messages.split_hotkey()
            return

        # get split image filenames
        self.split_image_filenames = os.listdir(self.split_image_directory)

        split_parser.validate_images_before_parsing(self)

        # find reset image then remove it from the list
        self.find_reset_image()

        # Find start_auto_splitter_image and then remove it from the list
        split_parser.remove_start_auto_splitter_image(self.split_image_filenames)

# region TODO I feel this entire region could be simplified

        # construct loop amounts for each split image
        split_image_loop_amount = [
            split_parser.loop_from_filename(image)
            for image
            in self.split_image_filenames]

        # construct a list of filenames, each filename copied with # of loops it has.
        self.split_image_filenames_including_loops: list[str] = []
        for i, filename in enumerate(self.split_image_filenames):
            current_loop = 1
            while split_image_loop_amount[i] >= current_loop:
                self.split_image_filenames_including_loops.append(filename)
                current_loop = current_loop + 1

        # construct a list of corresponding loop number to the filenames
        loop_numbers: list[int] = []
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
        self.split_groups: list[list[int]] = []
        if self.group_dummy_splits_checkbox.isChecked():
            current_group: list[int] = []
            self.split_groups.append(current_group)

            for i, image in enumerate(self.split_image_filenames_including_loops):
                current_group.append(i)

                flags = split_parser.flags_from_filename(image)
                if flags & DUMMY_FLAG != DUMMY_FLAG and i < len(self.split_image_filenames_including_loops) - 1:
                    current_group = []
                    self.split_groups.append(current_group)

# endregion

        self.gui_changes_on_start()

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
        window_text = win32gui.GetWindowText(self.hwnd)

        # First while loop: stays in this loop until all of the split images have been split
        while self.split_image_number < number_of_split_images:

            # Check if we are not waiting for the split delay to send the key press
            if self.waiting_for_split_delay:
                time_millis = int(round(time() * 1000))
                if time_millis < split_time:
                    QApplication.processEvents()
                    continue

            self.update_split_image()

            # second while loop: stays in this loop until similarity threshold is met
            # skip loop if we just finished waiting for the split delay and need to press the split key!
            start = time()
            while True:
                # reset if the set screen region window was closed
                if not window_text:
                    self.reset()

                if self.check_for_reset():
                    return

                # calculate similarity for reset image
                capture = self.get_capture_for_comparison()

                if self.should_check_reset_image():
                    reset_similarity = compare_image(
                        self.comparison_method_combobox.currentIndex(),
                        self.reset_image,
                        capture,
                        self.reset_mask)
                    if reset_similarity >= self.reset_image_threshold:
                        send_command(self, "reset")
                        self.reset()

                if self.check_for_reset():
                    return

                # TODO: Check is this actually still needed?
                # get capture again if current and reset image have different mask flags
                if self.image_has_transparency != (self.reset_mask is not None):
                    capture = self.get_capture_for_comparison()

                # calculate similarity for split image
                self.similarity = compare_image(
                    self.comparison_method_combobox.currentIndex(),
                    self.split_image,
                    capture,
                    self.image_mask)

                # show live similarity if the checkbox is checked
                if self.show_live_similarity_checkbox.isChecked():
                    self.live_similarity_label.setText(str(self.similarity)[:4])
                else:
                    self.live_similarity_label.setText(" ")

                # if the similarity becomes higher than highest similarity, set it as such.
                if self.similarity > self.highest_similarity:
                    self.highest_similarity = self.similarity

                # show live highest similarity if the checkbox is checked
                if self.show_highest_similarity_checkbox.isChecked():
                    self.highest_similarity_label.setText(str(self.highest_similarity)[:4])
                else:
                    self.highest_similarity_label.setText(" ")

                if not self.is_auto_controlled:
                    # if its the last split image or can't skip due to grouped dummy splits, disable skip split button
                    is_last = self.split_image_number == number_of_split_images - 1 \
                        or (self.group_dummy_splits_checkbox.isChecked()
                            and dummy_splits_array[self.split_image_number:].count(False) <= 1)
                    self.skip_split_button.setEnabled(not is_last)

                    # if its the first split image, disable the undo split button
                    self.undo_split_button.setEnabled(self.split_image_number != 0)

                # if the b flag is set, let similarity go above threshold first,
                # then split on similarity below threshold.
                # if no b flag, just split when similarity goes above threshold.
                if not self.waiting_for_split_delay:
                    if self.flags & BELOW_FLAG == BELOW_FLAG:
                        if self.split_below_threshold:
                            if self.similarity < self.similarity_threshold:
                                self.split_below_threshold = False
                                break
                        elif self.similarity >= self.similarity_threshold:
                            self.split_below_threshold = True
                            continue
                    elif self.similarity >= self.similarity_threshold:
                        break

                # limit the number of time the comparison runs to reduce cpu usage
                frame_interval = 1 / self.fps_limit_spinbox.value()
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
                    self.undo_split_button.setEnabled(False)
                    self.skip_split_button.setEnabled(False)
                    self.current_split_image_file_label.setText(" ")

                    # check for reset while delayed and display a counter of the remaining split delay time
                    delay_start_time = time()
                    split_delay = self.split_delay / 1000
                    while time() - delay_start_time < split_delay:
                        delay_time_left = round(split_delay - (time() - delay_start_time), 1)
                        self.current_split_image.setText(f"Delayed Split: {delay_time_left} sec remaining")
                        # check for reset
                        if not window_text:
                            self.reset()
                        if self.check_for_reset():
                            return

                        # calculate similarity for reset image
                        if self.should_check_reset_image():
                            capture = self.get_capture_for_comparison()

                            reset_similarity = compare_image(
                                self.comparison_method_combobox.currentIndex(),
                                self.reset_image,
                                capture,
                                self.reset_mask)
                            if reset_similarity >= self.reset_image_threshold:
                                send_command(self, "reset")
                                self.reset()
                                continue
                        # Email sent to pyqt@riverbankcomputing.com
                        QtTest.QTest.qWait(1)  # type: ignore

                self.waiting_for_split_delay = False

                # if {p} flag hit pause key, otherwise hit split hotkey
                send_command(self, "pause" if self.flags & PAUSE_FLAG == PAUSE_FLAG else "split")

            # if loop check box is checked and its the last split, go to first split.
            # else go to the next split image.
            if self.loop_checkbox.isChecked() and self.split_image_number == number_of_split_images - 1:
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
                        or (self.group_dummy_splits_checkbox.isChecked()
                            and dummy_splits_array[self.split_image_number:].count(False) <= 1)
                    self.skip_split_button.setEnabled(not is_last)

                    # if its the first split image, disable the undo split button
                    self.undo_split_button.setEnabled(self.split_image_number != 0)
                QApplication.processEvents()

            # A pause loop to check if the user presses skip split, undo split, or reset here.
            # Also updates the current split image text, counting down the time until the next split image
            if self.pause > 0:
                self.current_split_image_file_label.setText(" ")
                self.image_loop_label.setText("Image Loop: -")
                pause_start_time = time()
                while time() - pause_start_time < self.pause:
                    pause_time_left = round(self.pause - (time() - pause_start_time), 1)
                    self.current_split_image.setText(f"None (Paused). {pause_time_left} sec remaining")

                    # check for reset
                    if not window_text:
                        self.reset()
                    if self.check_for_reset():
                        return

                    # check for skip/undo split:
                    if self.split_image_number != pause_split_image_number:
                        break

                    # calculate similarity for reset image
                    if self.should_check_reset_image():
                        capture = self.get_capture_for_comparison()

                        reset_similarity = compare_image(
                            self.comparison_method_combobox.currentIndex(),
                            self.reset_image,
                            capture,
                            self.reset_mask)
                        if reset_similarity >= self.reset_image_threshold:
                            send_command(self, "reset")
                            self.reset()
                            continue
                    # Email sent to pyqt@riverbankcomputing.com
                    QtTest.QTest.qWait(1)  # type: ignore

        # loop breaks to here when the last image splits
        self.gui_changes_on_reset()

    def gui_changes_on_start(self):
        self.timer_start_image.stop()
        self.start_auto_splitter_button.setText("Running...")
        self.browse_button.setEnabled(False)
        self.group_dummy_splits_checkbox.setEnabled(False)
        self.start_image_reload_button.setEnabled(False)

        if not self.is_auto_controlled:
            self.start_auto_splitter_button.setEnabled(False)
            self.reset_button.setEnabled(True)
            self.undo_split_button.setEnabled(True)
            self.skip_split_button.setEnabled(True)
            self.set_split_hotkey_button.setEnabled(False)
            self.set_reset_hotkey_button.setEnabled(False)
            self.set_skip_split_hotkey_button.setEnabled(False)
            self.set_undo_split_hotkey_button.setEnabled(False)
            self.set_pause_hotkey_button.setEnabled(False)

        QApplication.processEvents()

    def gui_changes_on_reset(self):
        self.start_auto_splitter_button.setText(START_AUTO_SPLITTER_TEXT)
        self.image_loop_label.setText("Image Loop: -")
        self.current_split_image.setText(" ")
        self.current_split_image_file_label.setText(" ")
        self.live_similarity_label.setText(" ")
        self.highest_similarity_label.setText(" ")
        self.current_similarity_threshold_number_label.setText(" ")
        self.browse_button.setEnabled(True)
        self.group_dummy_splits_checkbox.setEnabled(True)
        self.start_image_reload_button.setEnabled(True)

        if not self.is_auto_controlled:
            self.start_auto_splitter_button.setEnabled(True)
            self.reset_button.setEnabled(False)
            self.undo_split_button.setEnabled(False)
            self.skip_split_button.setEnabled(False)
            self.set_split_hotkey_button.setEnabled(True)
            self.set_reset_hotkey_button.setEnabled(True)
            self.set_skip_split_hotkey_button.setEnabled(True)
            self.set_undo_split_hotkey_button.setEnabled(True)
            self.set_pause_hotkey_button.setEnabled(True)

        QApplication.processEvents()
        self.load_start_image(False, False)

    def get_capture_for_comparison(self):
        # grab screenshot of capture region
        capture = capture_region(self.hwnd, self.selection, self.force_print_window_checkbox.isChecked())
        capture = cv2.resize(capture, COMPARISON_RESIZE, interpolation=cv2.INTER_NEAREST)
        # convert to BGR
        return cv2.cvtColor(capture, cv2.COLOR_BGRA2BGR)

    def should_check_reset_image(self):
        return self.reset_image is not None and time() - self.run_start_time > self.reset_image_pause_time

    def find_reset_image(self):
        self.reset_image = None
        self.reset_mask = None

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
        self.reset_image_pause_time = self.pause_spinbox.value() \
            if pause_from_filename is None \
            else pause_from_filename
        threshold_from_filename = split_parser.threshold_from_filename(reset_image_file)
        self.reset_image_threshold = self.similarity_threshold_spinbox.value() \
            if threshold_from_filename is None \
            else threshold_from_filename

        self.reset_image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if self.reset_image is None:
            error_messages.image_type(path)
            return
        # if image has transparency, create a mask
        if check_if_image_has_transparency(self.reset_image):
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

    def update_split_image(self, custom_image_file: str = "", from_start_image: bool = False):
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
            error_messages.image_type(self.split_image_path)
            return
        self.image_has_transparency = check_if_image_has_transparency(self.split_image)
        # if image has transparency, create a mask
        if self.image_has_transparency:
            split_image_display = copy(self.split_image)
            # Transform transparency into UI's gray BG color
            transparent_mask = split_image_display[:, :, 3] == 0
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
        qimage = QtGui.QImage(cast(bytes, split_image_display),
                              split_image_display.shape[1],
                              split_image_display.shape[0],
                              split_image_display.shape[1] * 3,
                              QtGui.QImage.Format.Format_RGB888)
        self.update_current_split_image.emit(qimage)
        self.current_split_image_file_label.setText(split_image_file)

        # Override values if they have been specified on the file
        pause_from_filename = split_parser.pause_from_filename(split_image_file)
        self.pause = self.pause_spinbox.value() \
            if pause_from_filename is None \
            else pause_from_filename
        threshold_from_filename = split_parser.threshold_from_filename(split_image_file)
        self.similarity_threshold = self.similarity_threshold_spinbox.value() \
            if threshold_from_filename is None \
            else threshold_from_filename
        self.current_similarity_threshold_number_label.setText(f"{self.similarity_threshold:.2f}")

        # Get delay for split, if any
        self.split_delay = split_parser.delay_from_filename(split_image_file)

        # Set Image Loop #
        if not from_start_image:
            loop_tuple = self.split_image_filenames_and_loop_number[self.split_image_number]
            self.image_loop_label.setText(f"Image Loop: {loop_tuple[1]}/{loop_tuple[2]}")
        else:
            self.image_loop_label.setText("Image Loop: 1/1")

        # need to set split below threshold to false each time an image updates.
        self.split_below_threshold = False

        self.similarity = 0
        self.highest_similarity = 0.001

    def closeEvent(self, a0: Optional[QtGui.QCloseEvent] = None):
        """
        Exit safely when closing the window
        """

        def exit_program():
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
            exit_program()

        if settings.have_settings_changed(self):
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
                self.save_settings_as()
                exit_program()
            if warning is QMessageBox.StandardButton.No:
                exit_program()
            if warning is QMessageBox.StandardButton.Cancel:
                a0.ignore()
        else:
            exit_program()


def main():
    # Call to QApplication outside the try-except so we can show error messages
    app = QApplication(sys.argv)
    try:
        app.setWindowIcon(QtGui.QIcon(":/resources/icon.ico"))
        AutoSplit()

        if not FROZEN:
            # Kickoff the event loop every so often so we can handle KeyboardInterrupt (^C)
            timer = QtCore.QTimer()
            timer.timeout.connect(lambda: None)
            timer.start(500)

        exit_code = app.exec()
    except Exception as exception:  # pylint: disable=broad-except # We really want to catch everything here
        message = f"AutoSplit encountered an unrecoverable exception and will now close. {CREATE_NEW_ISSUE_MESSAGE}"
        # Print error to console if not running in executable
        if FROZEN:
            error_messages.exception_traceback(message, exception)
        else:
            print(message)
            traceback.print_exception(type(exception), exception, exception.__traceback__)
        sys.exit(1)

    # Catch Keyboard Interrupts for a clean close
    signal.signal(signal.SIGINT, lambda code, _: sys.exit(code))

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
