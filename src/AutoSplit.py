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
from typing import Optional, Union

import sys
import os
import ctypes
import signal
import traceback
from time import time

import certifi
import cv2
from PyQt6 import QtCore, QtGui, QtTest
from PyQt6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox, QWidget
from win32 import win32gui
from AutoSplitImage import COMPARISON_RESIZE, AutoSplitImage, ImageType

import error_messages
import settings_file as settings
from AutoControlledWorker import AutoControlledWorker
from capture_windows import capture_region, Rect, set_ui_image
from gen import about, design, update_checker
from hotkeys import send_command, after_setting_hotkey, set_split_hotkey, set_reset_hotkey, set_skip_split_hotkey, \
    set_undo_split_hotkey, set_pause_hotkey
from menu_bar import open_about, VERSION, view_help, check_for_updates, open_update_checker
from screen_region import select_region, select_window, align_region, validate_before_parsing
from settings_file import FROZEN
from split_parser import BELOW_FLAG, DUMMY_FLAG, PAUSE_FLAG, parse_and_validate_images

CREATE_NEW_ISSUE_MESSAGE = "Please create a New Issue at <a href='https://github.com/Toufool/Auto-Split/issues'>" \
    "github.com/Toufool/Auto-Split/issues</a>, describe what happened, and copy & paste the error message below"
START_IMAGE_TEXT = "Start Image"
START_AUTO_SPLITTER_TEXT = "Start Auto Splitter"
CHECK_FPS_ITERATIONS = 10

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

    # Widgets
    AboutWidget: about.Ui_AboutAutoSplitWidget
    UpdateCheckerWidget: update_checker.Ui_UpdateChecker
    CheckForUpdatesThread: QtCore.QThread

    # hotkeys need to be initialized to be passed as thread arguments in hotkeys.py
    # and for type safety in both hotkeys.py and settings_file.py
    split_hotkey: Optional[Callable[[], None]] = None
    reset_hotkey: Optional[Callable[[], None]] = None
    skip_split_hotkey: Optional[Callable[[], None]] = None
    undo_split_hotkey: Optional[Callable[[], None]] = None
    pause_hotkey: Optional[Callable[[], None]] = None

    # Initialize a few attributes
    split_image_directory = ""
    hwnd = 0
    """Window Handle used for Capture Region"""
    selection = Rect()
    last_saved_settings: list[Union[str, float, int, bool]] = []
    save_settings_file_path = ""
    load_settings_file_path = ""
    live_image_function_on_open = True
    split_image_number = 0
    split_images_and_loop_number: list[tuple[AutoSplitImage, int]] = []
    split_groups: list[list[int]] = []

    # Last loaded settings and last successful loaded settings file path to None until we try to load them
    last_loaded_settings: list[Union[str, float, int]] = []
    last_successfully_loaded_settings_file_path: Optional[str] = None

    # Automatic timer start
    highest_similarity = 0.0
    check_start_image_timestamp = 0.0

    # Define all other attributes
    setting_check_for_updates_on_open: QtCore.QSettings
    start_image_split_below_threshold: bool
    waiting_for_split_delay: bool
    split_below_threshold: bool
    run_start_time: float
    similarity: float
    split_delay: float
    start_image: Optional[AutoSplitImage] = None
    reset_image: Optional[AutoSplitImage] = None
    split_images: list[AutoSplitImage] = []
    split_image: AutoSplitImage

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
        self.browse_button.clicked.connect(self.__browse)
        self.select_region_button.clicked.connect(lambda: select_region(self))
        self.take_screenshot_button.clicked.connect(self.__take_screenshot)
        self.start_auto_splitter_button.clicked.connect(self.__auto_splitter)
        self.check_fps_button.clicked.connect(self.__check_fps)
        self.reset_button.clicked.connect(self.reset)
        self.skip_split_button.clicked.connect(self.__skip_split)
        self.undo_split_button.clicked.connect(self.__undo_split)
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
        self.x_spinbox.valueChanged.connect(self.__update_x)
        self.y_spinbox.valueChanged.connect(self.__update_y)
        self.width_spinbox.valueChanged.connect(self.__update_width)
        self.height_spinbox.valueChanged.connect(self.__update_height)

        # connect signals to functions
        self.after_setting_hotkey_signal.connect(lambda: after_setting_hotkey(self))
        self.start_auto_splitter_signal.connect(self.__auto_splitter)
        self.update_checker_widget_signal.connect(lambda latest_version, check_on_open:
                                                  open_update_checker(self, latest_version, check_on_open))
        self.reset_signal.connect(self.reset)
        self.skip_split_signal.connect(self.__skip_split)
        self.undo_split_signal.connect(self.__undo_split)
        self.pause_signal.connect(self.pause)

        # live image checkbox
        self.live_image_checkbox.clicked.connect(self.check_live_image)
        self.timer_live_image.timeout.connect(self.__live_image_function)

        # Automatic timer start
        self.timer_start_image.timeout.connect(self.__start_image_function)

        if not self.is_auto_controlled:
            settings.load_settings(self, load_settings_on_open=True)

        self.show()

        # Needs to be after Ui_MainWindow.show() to be shown overtop
        if self.action_check_for_updates_on_open.isChecked():
            check_for_updates(self, check_on_open=True)

    # FUNCTIONS

    # TODO add checkbox for going back to image 1 when resetting.
    def __browse(self):
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
            self.__live_image_function()

    def __live_image_function(self):
        try:
            window_text = win32gui.GetWindowText(self.hwnd)
            self.capture_region_window_label.setText(window_text)
            if not window_text:
                self.timer_live_image.stop()
                self.live_image.clear()
                if self.live_image_function_on_open:
                    self.live_image_function_on_open = False
                return

            # Set live image in UI
            capture = capture_region(self.hwnd, self.selection, self.force_print_window_checkbox.isChecked())
            set_ui_image(self.live_image, capture, False)

        except AttributeError:
            pass

    def load_start_image(self, started_by_button: bool = False, wait_for_delay: bool = True):
        self.timer_start_image.stop()
        self.current_split_image_file_label.setText(" ")
        self.start_image_label.setText(f"{START_IMAGE_TEXT}: not found")
        QApplication.processEvents()

        if not self.is_auto_controlled \
            and (not self.split_input.text()
                 or not self.reset_input.text()
                 or not self.pause_hotkey_input.text()):
            error_messages.load_start_image()
            return

        if not (validate_before_parsing(self, started_by_button) and parse_and_validate_images(self)):
            return

        if self.start_image is None:
            if started_by_button:
                error_messages.no_keyword_image("start_auto_splitter")
            return

        self.split_image_number = 0

        start_pause_time = self.start_image.get_pause_time(self)
        if not wait_for_delay and start_pause_time > 0:
            self.check_start_image_timestamp = time() + start_pause_time
            self.start_image_label.setText(f"{START_IMAGE_TEXT}: paused")
            self.highest_similarity_label.setText(" ")
            self.current_similarity_threshold_number_label.setText(" ")
        else:
            self.check_start_image_timestamp = 0.0
            self.start_image_label.setText(f"{START_IMAGE_TEXT}: ready")
            self.__update_split_image(self.start_image, from_start_image=True)

        self.highest_similarity = 0.0
        self.start_image_split_below_threshold = False
        self.timer_start_image.start(int(1000 / self.fps_limit_spinbox.value()))

        QApplication.processEvents()

    def __start_image_function(self):
        if self.start_image is None \
                or not self.start_image \
                or time() < self.check_start_image_timestamp \
                or (not self.split_input.text() and not self.is_auto_controlled):
            pause_time_left = f"{self.check_start_image_timestamp - time():.1f}"
            self.current_split_image.setText(
                f"None\n (Paused before loading {START_IMAGE_TEXT}).\n {pause_time_left} sec remaining")
            return

        if self.check_start_image_timestamp > 0:
            self.check_start_image_timestamp = 0.0
            self.start_image_label.setText(f"{START_IMAGE_TEXT}: ready")
            self.__update_split_image(self.start_image, from_start_image=True)

        capture = self.__get_capture_for_comparison()
        start_image_threshold = self.start_image.get_similarity_threshold(self)
        start_image_similarity = self.start_image.compare_with_capture(self, capture)
        self.current_similarity_threshold_number_label.setText(f"{start_image_threshold:.2f}")

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
        below_flag = self.start_image.check_flag(BELOW_FLAG)
        if below_flag \
                and not self.start_image_split_below_threshold \
                and start_image_similarity >= start_image_threshold:
            self.start_image_split_below_threshold = True
            return
        if (below_flag
            and self.start_image_split_below_threshold
            and start_image_similarity < start_image_threshold) \
                or (start_image_similarity >= start_image_threshold and not below_flag):

            self.timer_start_image.stop()
            self.start_image_split_below_threshold = False

            # delay start image if needed
            if self.start_image.delay > 0:
                self.start_image_label.setText(f"{START_IMAGE_TEXT}: delaying start...")
                delay_start_time = time()
                start_delay = self.start_image.delay / 1000
                while time() - delay_start_time < start_delay:
                    delay_time_left = round(start_delay - (time() - delay_start_time), 1)
                    self.current_split_image.setText(
                        f"Delayed Before Starting:\n {delay_time_left} sec remaining")
                    # Email sent to pyqt@riverbankcomputing.com
                    QtTest.QTest.qWait(1)  # type: ignore

            self.start_image_label.setText(f"{START_IMAGE_TEXT}: started")
            send_command(self, "start")
            # Email sent to pyqt@riverbankcomputing.com
            QtTest.QTest.qWait(1 / self.fps_limit_spinbox.value())  # type: ignore
            self.start_auto_splitter()

    # update x, y, width, height when spinbox values are changed
    def __update_x(self):
        try:
            self.selection.left = self.x_spinbox.value()
            self.selection.right = self.selection.left + self.width_spinbox.value()
            self.check_live_image()
        except AttributeError:
            pass

    def __update_y(self):
        try:
            self.selection.top = self.y_spinbox.value()
            self.selection.bottom = self.selection.top + self.height_spinbox.value()
            self.check_live_image()
        except AttributeError:
            pass

    def __update_width(self):
        self.selection.right = self.selection.left + self.width_spinbox.value()
        self.check_live_image()

    def __update_height(self):
        self.selection.bottom = self.selection.top + self.height_spinbox.value()
        self.check_live_image()

    def __take_screenshot(self):
        if not validate_before_parsing(self, check_empty_directory=False):
            return

        # Check if file exists and rename it if it does.
        # Below starts the file_name_number at #001 up to #999. After that it will go to 1000,
        # which is a problem, but I doubt anyone will get to 1000 split images...
        screenshot_index = 1
        while True:
            screenshot_path = os.path.join(self.split_image_directory, f"{screenshot_index:03}_SplitImage.png")
            if not os.path.exists(screenshot_path):
                break
            screenshot_index += 1

        # Grab screenshot of capture region
        capture = capture_region(self.hwnd, self.selection, self.force_print_window_checkbox.isChecked())
        if capture is None:
            error_messages.region()
            return

        # save and open image
        cv2.imwrite(screenshot_path, capture)
        os.startfile(screenshot_path)

    def __check_fps(self):
        self.fps_value_label.setText(" ")
        if not (validate_before_parsing(self) and parse_and_validate_images(self)):
            return

        images = self.split_images
        if self.start_image:
            images.append(self.start_image)
        if self.reset_image:
            images.append(self.reset_image)

        # run X iterations of screenshotting capture region + comparison + displaying.
        t0 = time()
        for image in images:
            count = 0
            while count < CHECK_FPS_ITERATIONS:
                capture = self.__get_capture_for_comparison()
                _ = image.compare_with_capture(self, capture)
                set_ui_image(self.current_split_image, image.bytes, True)
                count += 1
        self.current_split_image.clear()

        # calculate FPS
        t1 = time()
        fps = int((CHECK_FPS_ITERATIONS * len(images)) / (t1 - t0))
        self.fps_value_label.setText(str(fps))

    def __is_current_split_out_of_range(self):
        return self.split_image_number < 0 \
            or self.split_image_number > len(self.split_images_and_loop_number) - 1

    # undo split button and hotkey connect to here
    def __undo_split(self):
        # Can't undo until timer is started
        # or Undoing past the first image
        if self.start_auto_splitter_button.text() == START_AUTO_SPLITTER_TEXT \
                or "Delayed Split" in self.current_split_image.text() \
                or (not self.undo_split_button.isEnabled() and not self.is_auto_controlled) \
                or self.__is_current_split_out_of_range():
            return

        if self.group_dummy_splits_checkbox.isChecked():
            for i, group in enumerate(self.split_groups):
                if i > 0 and self.split_image_number in group:
                    self.split_image_number = self.split_groups[i - 1][0]
                    break
        else:
            self.split_image_number -= 1

        self.__update_split_image()

    # skip split button and hotkey connect to here
    def __skip_split(self):
        # Can't skip or split until timer is started
        # or Splitting/skipping when there are no images left
        if self.start_auto_splitter_button.text() == START_AUTO_SPLITTER_TEXT \
                or "Delayed Split" in self.current_split_image.text() \
                or (not self.skip_split_button.isEnabled() and not self.is_auto_controlled) \
                or self.__is_current_split_out_of_range():
            return

        if self.group_dummy_splits_checkbox.isChecked():
            for group in self.split_groups:
                if self.split_image_number in group:
                    self.split_image_number = group[-1] + 1
                    break
        else:
            self.split_image_number += 1

        self.__update_split_image()

    def pause(self):
        # TODO add what to do when you hit pause hotkey, if this even needs to be done
        pass

    def reset(self):
        # When the reset button or hotkey is pressed, it will change this text,
        # which will trigger in the __auto_splitter function, if running, to abort and change GUI.
        self.start_auto_splitter_button.setText(START_AUTO_SPLITTER_TEXT)

    # Functions for the hotkeys to return to the main thread from signals and start their corresponding functions
    def start_auto_splitter(self):
        # If the auto splitter is already running or the button is disabled, don't emit the signal to start it.
        if self.start_auto_splitter_button.text() == "Running..." \
                or (not self.start_auto_splitter_button.isEnabled() and not self.is_auto_controlled):
            return

        start_label: str = self.start_image_label.text()
        if start_label.endswith("ready") or start_label.endswith("paused"):
            self.start_image_label.setText(f"{START_IMAGE_TEXT}: not ready")

        self.start_auto_splitter_signal.emit()

    def __check_for_reset(self):
        if self.start_auto_splitter_button.text() == START_AUTO_SPLITTER_TEXT:
            if self.auto_start_on_reset_checkbox.isChecked():
                self.start_auto_splitter_signal.emit()
            else:
                self.gui_changes_on_reset()
            return True
        return False

    def __auto_splitter(self):
        if not self.split_input.text() and not self.is_auto_controlled:
            self.gui_changes_on_reset()
            error_messages.split_hotkey()
            return

        if not (validate_before_parsing(self) and parse_and_validate_images(self)):
            self.gui_changes_on_reset()
            return

        # Construct a list of images + loop count tuples.
        self.split_images_and_loop_number = [
            item for flattenlist
            in [[(split_image, i + 1) for i in range(split_image.loops)]
                for split_image
                in self.split_images]
            for item in flattenlist]

        # Construct groups of splits if needed
        self.split_groups = []
        if self.group_dummy_splits_checkbox.isChecked():
            current_group: list[int] = []
            self.split_groups.append(current_group)

            for i, image in enumerate(self.split_images):
                current_group.append(i)

                if not image.check_flag(DUMMY_FLAG) and i < len(self.split_images) - 1:
                    current_group = []
                    self.split_groups.append(current_group)
        self.gui_changes_on_start()

        # Initialize a few attributes
        self.split_image_number = 0
        self.waiting_for_split_delay = False
        self.split_below_threshold = False
        split_time = 0
        number_of_split_images = len(self.split_images_and_loop_number)
        dummy_splits_array = [image.check_flag(DUMMY_FLAG) for image in self.split_images]
        self.run_start_time = time()

        # First while loop: stays in this loop until all of the split images have been split
        while self.split_image_number < number_of_split_images:

            # Check if we are not waiting for the split delay to send the key press
            if self.waiting_for_split_delay:
                time_millis = int(round(time() * 1000))
                if time_millis < split_time:
                    QApplication.processEvents()
                    continue

            self.__update_split_image()

            # second while loop: stays in this loop until similarity threshold is met
            # skip loop if we just finished waiting for the split delay and need to press the split key!
            start = time()
            while True:
                if self.__check_for_reset():
                    return

                # calculate similarity for reset image
                capture = self.__get_capture_for_comparison()

                _ = self.__reset_if_should(capture)

                if self.__check_for_reset():
                    return

                # calculate similarity for split image
                self.similarity = self.split_image.compare_with_capture(self, capture)

                # show live similarity if the checkbox is checked
                self.live_similarity_label.setText(
                    str(self.similarity)[:4]
                    if self.show_live_similarity_checkbox.isChecked()
                    else " ")

                # if the similarity becomes higher than highest similarity, set it as such.
                if self.similarity > self.highest_similarity:
                    self.highest_similarity = self.similarity

                # show live highest similarity if the checkbox is checked
                self.highest_similarity_label.setText(
                    str(self.highest_similarity)[:4]
                    if self.show_highest_similarity_checkbox.isChecked()
                    else " ")

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
                    if self.similarity >= self.split_image.get_similarity_threshold(self):
                        if not self.split_image.check_flag(BELOW_FLAG):
                            break
                        if not self.split_below_threshold:
                            self.split_below_threshold = True
                            continue
                    elif self.split_image.check_flag(BELOW_FLAG) and self.split_below_threshold:
                        self.split_below_threshold = False
                        break

                # limit the number of time the comparison runs to reduce cpu usage
                frame_interval: float = 1 / self.fps_limit_spinbox.value()
                # Email sent to pyqt@riverbankcomputing.com
                QtTest.QTest.qWait(int(frame_interval - (time() - start) % frame_interval))  # type: ignore
                QApplication.processEvents()

            # comes here when threshold gets met

            # We need to make sure that this isn't a dummy split before sending
            # the key press.
            if not self.split_image.check_flag(DUMMY_FLAG):
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
                        if self.__check_for_reset():
                            return

                        # calculate similarity for reset image
                        capture = self.__get_capture_for_comparison()
                        if self.__reset_if_should(capture):
                            continue
                        # Email sent to pyqt@riverbankcomputing.com
                        QtTest.QTest.qWait(1)  # type: ignore

                self.waiting_for_split_delay = False

                # if {p} flag hit pause key, otherwise hit split hotkey
                send_command(self, "pause" if self.split_image.check_flag(PAUSE_FLAG) else "split")

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
            pause_time = self.split_image.get_pause_time(self)
            if pause_time > 0:
                self.current_split_image_file_label.setText(" ")
                self.image_loop_label.setText("Image Loop: -")
                pause_start_time = time()
                while time() - pause_start_time < pause_time:
                    pause_time_left = round(pause_time - (time() - pause_start_time), 1)
                    self.current_split_image.setText(f"None (Paused). {pause_time_left} sec remaining")

                    if self.__check_for_reset():
                        return

                    # check for skip/undo split:
                    if self.split_image_number != pause_split_image_number:
                        break

                    # calculate similarity for reset image
                    capture = self.__get_capture_for_comparison()
                    if self.__reset_if_should(capture):
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

    def __get_capture_for_comparison(self):
        """
        Grab capture region and resize for comparison
        """
        capture = capture_region(self.hwnd, self.selection, self.force_print_window_checkbox.isChecked())
        return None if capture is None else cv2.resize(capture, COMPARISON_RESIZE, interpolation=cv2.INTER_NEAREST)

    def __reset_if_should(self, capture: Optional[cv2.ndarray]):
        """
        Check if we should reset, resets if it's the case, and returns the result
        """
        if not self.reset_image:
            return False

        reset_similarity = self.reset_image.compare_with_capture(self, capture)
        should_reset = reset_similarity >= self.reset_image.get_similarity_threshold(self) \
            and time() - self.run_start_time > self.reset_image.get_pause_time(self)

        if should_reset:
            send_command(self, "reset")
            self.reset()
        return should_reset

    def __update_split_image(self, specific_image: Optional[AutoSplitImage] = None, from_start_image: bool = False):
        # Splitting/skipping when there are no images left or Undoing past the first image
        # Start image is expected to be out of range (index 0 of 0-length array)
        if (not specific_image or specific_image.image_type != ImageType.START) \
                and self.__is_current_split_out_of_range():
            self.reset()
            return

        # Get split image
        self.split_image = specific_image or self.split_images_and_loop_number[0 + self.split_image_number][0]
        if self.split_image.bytes is not None:
            set_ui_image(self.current_split_image, self.split_image.bytes, True)

        self.current_split_image_file_label.setText(self.split_image.filename)
        self.current_similarity_threshold_number_label.setText(f"{self.split_image.get_similarity_threshold(self):.2f}")

        # Set Image Loop #
        if not from_start_image:
            loop_tuple = self.split_images_and_loop_number[self.split_image_number]
            self.image_loop_label.setText(f"Image Loop: {loop_tuple[1]}/{loop_tuple[0].loops}")
        else:
            self.image_loop_label.setText("Image Loop: N/A")

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
