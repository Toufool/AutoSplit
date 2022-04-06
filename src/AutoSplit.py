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
from capture_windows import capture_region, set_ui_image
from gen import about, design, settings as settings_ui, update_checker
from hotkeys import send_command, after_setting_hotkey
from menu_bar import get_default_settings_from_ui, open_about, VERSION, open_settings, view_help, check_for_updates, \
    open_update_checker
from screen_region import select_region, select_window, align_region, validate_before_parsing
from settings_file import FROZEN
from split_parser import BELOW_FLAG, DUMMY_FLAG, PAUSE_FLAG, parse_and_validate_images

CREATE_NEW_ISSUE_MESSAGE = (
    "Please create a New Issue at <a href='https://github.com/Toufool/Auto-Split/issues'>"
    + "github.com/Toufool/Auto-Split/issues</a>, describe what happened, and copy & paste the error message below")
START_AUTO_SPLITTER_TEXT = "Start Auto Splitter"
CHECK_FPS_ITERATIONS = 10

# Needed when compiled, along with the custom hook-requests PyInstaller hook
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()


def make_excepthook(autosplit: AutoSplit):
    def excepthook(exception_type: type[BaseException], exception: BaseException, _traceback: Optional[TracebackType]):
        # Catch Keyboard Interrupts for a clean close
        if exception_type is KeyboardInterrupt or isinstance(exception, KeyboardInterrupt):
            sys.exit(0)
        autosplit.show_error_signal.emit(lambda: error_messages.exception_traceback(
            "AutoSplit encountered an unhandled exception and will try to recover, "
            + f"however, there is no guarantee it will keep working properly. {CREATE_NEW_ISSUE_MESSAGE}",
            exception))
    return excepthook


class AutoSplit(QMainWindow, design.Ui_main_window):
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
    AboutWidget: Optional[about.Ui_AboutAutoSplitWidget] = None
    UpdateCheckerWidget: Optional[update_checker.Ui_UpdateChecker] = None
    CheckForUpdatesThread: Optional[QtCore.QThread] = None
    SettingsWidget: Optional[settings_ui.Ui_DialogSettings] = None

    # hotkeys need to be initialized to be passed as thread arguments in hotkeys.py
    # and for type safety in both hotkeys.py and settings_file.py
    split_hotkey: Optional[Callable[[], None]] = None
    reset_hotkey: Optional[Callable[[], None]] = None
    skip_split_hotkey: Optional[Callable[[], None]] = None
    undo_split_hotkey: Optional[Callable[[], None]] = None
    pause_hotkey: Optional[Callable[[], None]] = None

    # Initialize a few attributes
    hwnd = 0
    """Window Handle used for Capture Region"""
    last_saved_settings: list[Union[str, float, int, bool]] = []
    similarity = 0.0
    split_image_number = 0
    split_images_and_loop_number: list[tuple[AutoSplitImage, int]] = []
    split_groups: list[list[int]] = []

    # Last loaded settings empty and last successful loaded settings file path to None until we try to load them
    last_loaded_settings: list[Union[str, float, int]] = []
    last_successfully_loaded_settings_file_path: Optional[str] = None
    """For when a file has never loaded, but you successfully "Save File As"."""

    # Automatic timer start
    highest_similarity = 0.0
    check_start_image_timestamp = 0.0

    # Define all other attributes
    start_image_split_below_threshold: bool
    waiting_for_split_delay: bool
    split_below_threshold: bool
    run_start_time: float
    start_image: Optional[AutoSplitImage] = None
    reset_image: Optional[AutoSplitImage] = None
    split_images: list[AutoSplitImage] = []
    split_image: AutoSplitImage

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Setup global error handling
        self.show_error_signal.connect(lambda errorMessageBox: errorMessageBox())
        # Whithin LiveSplit excepthook needs to use MainWindow's signals to show errors
        sys.excepthook = make_excepthook(self)

        self.setupUi(self)

        # Get default values defined in SettingsDialog
        self.settings_dict = get_default_settings_from_ui(self)
        settings.load_check_for_updates_on_open(self)

        self.action_view_help.triggered.connect(view_help)
        self.action_about.triggered.connect(lambda: open_about(self))
        self.action_check_for_updates.triggered.connect(lambda: check_for_updates(self))
        self.action_settings.triggered.connect(lambda: open_settings(self))
        self.action_save_profile.triggered.connect(lambda: settings.save_settings(self))
        self.action_save_profile_as.triggered.connect(lambda: settings.save_settings_as(self))
        self.action_load_profile.triggered.connect(lambda: settings.load_settings(self))

        if self.SettingsWidget:
            self.SettingsWidget.split_input.setEnabled(False)
            self.SettingsWidget.reset_input.setEnabled(False)
            self.SettingsWidget.skip_split_input.setEnabled(False)
            self.SettingsWidget.undo_split_input.setEnabled(False)
            self.SettingsWidget.pause_input.setEnabled(False)

        if self.is_auto_controlled:
            self.start_auto_splitter_button.setEnabled(False)

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
        self.next_image_button.clicked.connect(lambda: self.__skip_split(True))
        self.previous_image_button.clicked.connect(lambda: self.__undo_split(True))
        self.align_region_button.clicked.connect(lambda: align_region(self))
        self.select_window_button.clicked.connect(lambda: select_window(self))
        self.reload_start_image_button.clicked.connect(lambda: self.load_start_image(True, True))
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
        self.timer_live_image.start(int(1000 / 60))
        self.timer_live_image.timeout.connect(self.__live_image_function)

        # Automatic timer start
        self.timer_start_image.timeout.connect(self.__start_image_function)

        if not self.is_auto_controlled:
            settings.load_settings_on_open(self)

        self.show()

        # Needs to be after Ui_main_window.show() to be shown overtop
        if self.action_check_for_updates_on_open.isChecked():
            check_for_updates(self, check_on_open=True)

    # FUNCTIONS

    # TODO add checkbox for going back to image 1 when resetting.
    def __browse(self):
        # User selects the file with the split images in it.
        new_split_image_directory = QFileDialog.getExistingDirectory(
            self,
            "Select Split Image Directory",
            os.path.join(self.settings_dict["split_image_directory"] or settings.auto_split_directory, ".."))

        # If the user doesn't select a folder, it defaults to "".
        if new_split_image_directory:
            # set the split image folder line to the directory text
            self.settings_dict["split_image_directory"] = new_split_image_directory
            self.split_image_folder_input.setText(f"{new_split_image_directory}/")
            self.load_start_image()

    def __live_image_function(self):
        self.capture_region_window_label.setText(self.settings_dict["captured_window_title"])
        if not (self.settings_dict["live_capture_region"] and self.settings_dict["captured_window_title"]):
            self.live_image.clear()
            return
        # Set live image in UI
        if self.hwnd:
            capture = capture_region(self.hwnd,
                                     self.settings_dict["capture_region"],
                                     self.settings_dict["force_print_window"])
            set_ui_image(self.live_image, capture, False)

    def load_start_image(self, started_by_button: bool = False, wait_for_delay: bool = True):
        self.timer_start_image.stop()
        self.current_image_file_label.setText("-")
        self.start_image_status_value_label.setText("not found")
        QApplication.processEvents()

        if not self.is_auto_controlled \
            and (not self.settings_dict["split_hotkey"]
                 or not self.settings_dict["reset_hotkey"]
                 or not self.settings_dict["pause_hotkey"]):
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
            self.start_image_status_value_label.setText("paused")
            self.table_current_image_highest_label.setText("-")
            self.table_current_image_threshold_label.setText("-")
        else:
            self.check_start_image_timestamp = 0.0
            self.start_image_status_value_label.setText("ready")
            self.__update_split_image(self.start_image)

        self.highest_similarity = 0.0
        self.start_image_split_below_threshold = False
        self.timer_start_image.start(int(1000 / self.settings_dict["fps_limit"]))

        QApplication.processEvents()

    def __start_image_function(self):
        if self.start_image is None \
                or not self.start_image \
                or time() < self.check_start_image_timestamp \
                or (not self.settings_dict["split_hotkey"] and not self.is_auto_controlled):
            pause_time_left = self.check_start_image_timestamp - time()
            self.current_split_image.setText(
                f"None\n (Paused before loading Start Image).\n {seconds_remaining_text(pause_time_left)}")
            return

        if self.check_start_image_timestamp > 0:
            self.check_start_image_timestamp = 0.0
            self.start_image_status_value_label.setText("ready")
            self.__update_split_image(self.start_image)

        capture = self.__get_capture_for_comparison()
        start_image_threshold = self.start_image.get_similarity_threshold(self)
        start_image_similarity = self.start_image.compare_with_capture(self, capture)
        self.table_current_image_threshold_label.setText(f"{start_image_threshold:.2f}")

        # Show live similarity if the checkbox is checked
        self.table_current_image_live_label.setText(str(start_image_similarity)[:4])

        # If the similarity becomes higher than highest similarity, set it as such.
        if start_image_similarity > self.highest_similarity:
            self.highest_similarity = start_image_similarity

        # Show live highest similarity if the checkbox is checked
        self.table_current_image_highest_label.setText(str(self.highest_similarity)[:4])

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
                self.start_image_status_value_label.setText("delaying start...")
                delay_start_time = time()
                start_delay = self.start_image.delay / 1000
                while time() - delay_start_time < start_delay:
                    delay_time_left = start_delay - (time() - delay_start_time)
                    self.current_split_image.setText(
                        f"Delayed Before Starting:\n {seconds_remaining_text(delay_time_left)}")
                    # Email sent to pyqt@riverbankcomputing.com
                    QtTest.QTest.qWait(1)  # type: ignore

            self.start_image_status_value_label.setText("started")
            send_command(self, "start")
            # Email sent to pyqt@riverbankcomputing.com
            QtTest.QTest.qWait(int(1 / self.settings_dict["fps_limit"]))  # type: ignore
            self.start_auto_splitter()

    # update x, y, width, height when spinbox values are changed
    def __update_x(self):
        self.settings_dict["capture_region"].x = self.x_spinbox.value()

    def __update_y(self):
        self.settings_dict["capture_region"].y = self.y_spinbox.value()

    def __update_width(self):
        self.settings_dict["capture_region"].width = self.width_spinbox.value()

    def __update_height(self):
        self.settings_dict["capture_region"].height = self.height_spinbox.value()

    def __take_screenshot(self):
        if not validate_before_parsing(self, check_empty_directory=False):
            return

        # Check if file exists and rename it if it does.
        # Below starts the file_name_number at #001 up to #999. After that it will go to 1000,
        # which is a problem, but I doubt anyone will get to 1000 split images...
        screenshot_index = 1
        while True:
            screenshot_path = os.path.join(
                self.settings_dict["split_image_directory"],
                f"{screenshot_index:03}_SplitImage.png")
            if not os.path.exists(screenshot_path):
                break
            screenshot_index += 1

        # Grab screenshot of capture region
        capture = capture_region(self.hwnd,
                                 self.settings_dict["capture_region"],
                                 self.settings_dict["force_print_window"])
        if capture is None:
            error_messages.region()
            return

        # save and open image
        cv2.imwrite(screenshot_path, capture)
        os.startfile(screenshot_path)  # nosec

    def __check_fps(self):
        self.fps_value_label.clear()
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
                count += 1

        # calculate FPS
        t1 = time()
        fps = int((CHECK_FPS_ITERATIONS * len(images)) / (t1 - t0))
        self.fps_value_label.setText(str(fps))

    def __is_current_split_out_of_range(self):
        return self.split_image_number < 0 \
            or self.split_image_number > len(self.split_images_and_loop_number) - 1

    def __undo_split(self, navigate_image_only: bool = False):
        """
        "Undo Split" and "Prev. Img." buttons and hotkey connect to here
        """
        # Can't undo until timer is started
        # or Undoing past the first image
        if self.start_auto_splitter_button.text() == START_AUTO_SPLITTER_TEXT \
                or "Delayed Split" in self.current_split_image.text() \
                or (not self.undo_split_button.isEnabled() and not self.is_auto_controlled) \
                or self.__is_current_split_out_of_range():
            return

        if not navigate_image_only:
            for i, group in enumerate(self.split_groups,):
                if i > 0 and self.split_image_number in group:
                    self.split_image_number = self.split_groups[i - 1][-1]
                    break
        else:
            self.split_image_number -= 1

        self.__update_split_image()
        if not navigate_image_only:
            send_command(self, "undo")

    def __skip_split(self, navigate_image_only: bool = False):
        """
        "Skip Split" and "Next Img." buttons and hotkey connect to here
        """
        # Can't skip or split until timer is started
        # or Splitting/skipping when there are no images left
        if self.start_auto_splitter_button.text() == START_AUTO_SPLITTER_TEXT \
                or "Delayed Split" in self.current_split_image.text() \
                or (not self.skip_split_button.isEnabled() and not self.is_auto_controlled) \
                or self.__is_current_split_out_of_range():
            return

        if not navigate_image_only:
            for group in self.split_groups:
                if self.split_image_number in group:
                    self.split_image_number = group[-1] + 1
                    break
        else:
            self.split_image_number += 1

        self.__update_split_image()
        if not navigate_image_only:
            send_command(self, "skip")

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

        start_label: str = self.start_image_status_value_label.text()
        if start_label.endswith("ready") or start_label.endswith("paused"):
            self.start_image_status_value_label.setText("not ready")

        self.start_auto_splitter_signal.emit()

    def __check_for_reset(self):
        if self.start_auto_splitter_button.text() == START_AUTO_SPLITTER_TEXT:
            if self.settings_dict["loop_splits"]:
                self.start_auto_splitter_signal.emit()
            else:
                self.gui_changes_on_reset()
            return True
        return False

    def __auto_splitter(self):
        if not self.settings_dict["split_hotkey"] and not self.is_auto_controlled:
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

        # Construct groups of splits
        self.split_groups = []
        current_group: list[int] = []
        self.split_groups.append(current_group)
        for i, image in enumerate(self.split_images_and_loop_number):
            current_group.append(i)
            if not image[0].check_flag(DUMMY_FLAG) and i < len(self.split_images_and_loop_number) - 1:
                current_group = []
                self.split_groups.append(current_group)

        self.gui_changes_on_start()

        # Initialize a few attributes
        self.split_image_number = 0
        self.waiting_for_split_delay = False
        self.split_below_threshold = False
        split_time = 0
        number_of_split_images = len(self.split_images_and_loop_number)
        dummy_splits_array = [image_loop[0].check_flag(DUMMY_FLAG) for image_loop in self.split_images_and_loop_number]
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
                self.table_current_image_live_label.setText(str(self.similarity)[:4])

                # if the similarity becomes higher than highest similarity, set it as such.
                if self.similarity > self.highest_similarity:
                    self.highest_similarity = self.similarity

                # show live highest similarity if the checkbox is checked
                self.table_current_image_highest_label.setText(str(self.highest_similarity)[:4])

                # If its the last split image and last loop number, disable the next image button
                # If its the first split image, disable the undo split and previous image buttons
                self.next_image_button.setEnabled(self.split_image_number != number_of_split_images - 1)
                self.previous_image_button.setEnabled(self.split_image_number != 0)
                if not self.is_auto_controlled:
                    # If its the last non-dummy split image and last loop number, disable the skip split button
                    self.skip_split_button.setEnabled(dummy_splits_array[self.split_image_number:].count(False) > 1)
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
                frame_interval: float = 1 / self.settings_dict["fps_limit"]
                # Email sent to pyqt@riverbankcomputing.com
                QtTest.QTest.qWait(int(frame_interval - (time() - start) % frame_interval))  # type: ignore
                QApplication.processEvents()

            # comes here when threshold gets met

            # We need to make sure that this isn't a dummy split before sending
            # the key press.
            if not self.split_image.check_flag(DUMMY_FLAG):
                # If it's a delayed split, check if the delay has passed
                # Otherwise calculate the split time for the key press
                split_delay = self.split_image.delay / 1000
                if split_delay > 0 and not self.waiting_for_split_delay:
                    split_time = round(time() + split_delay * 1000)
                    self.waiting_for_split_delay = True
                    self.undo_split_button.setEnabled(False)
                    self.skip_split_button.setEnabled(False)
                    self.current_image_file_label.clear()

                    # check for reset while delayed and display a counter of the remaining split delay time
                    delay_start_time = time()
                    while time() - delay_start_time < split_delay:
                        delay_time_left = split_delay - (time() - delay_start_time)
                        self.current_split_image.setText(f"Delayed Split: {seconds_remaining_text(delay_time_left)}")
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
            if self.settings_dict["loop_splits"] and self.split_image_number == number_of_split_images - 1:
                self.split_image_number = 0
            else:
                self.split_image_number += 1

            # Set a "pause" split image number.
            # This is done so that it can detect if user hit split/undo split while paused.
            pause_split_image_number = self.split_image_number

            # if its not the last split image, pause for the amount set by the user
            if number_of_split_images != self.split_image_number:

                # If its the last split image and last loop number, disable the next image button
                # If its the first split image, disable the undo split and previous image buttons
                self.next_image_button.setEnabled(self.split_image_number != number_of_split_images - 1)
                self.previous_image_button.setEnabled(self.split_image_number != 0)
                if not self.is_auto_controlled:
                    # If its the last non-dummy split image and last loop number, disable the skip split button
                    self.skip_split_button.setEnabled(dummy_splits_array[self.split_image_number:].count(False) > 1)
                    self.undo_split_button.setEnabled(self.split_image_number != 0)

                QApplication.processEvents()

            # A pause loop to check if the user presses skip split, undo split, or reset here.
            # Also updates the current split image text, counting down the time until the next split image
            pause_time = self.split_image.get_pause_time(self)
            if pause_time > 0:
                pause_start_time = time()
                while time() - pause_start_time < pause_time:
                    pause_time_left = pause_time - (time() - pause_start_time)
                    self.current_split_image.setText(f"None (Paused). {seconds_remaining_text(pause_time_left)}")

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
        self.reload_start_image_button.setEnabled(False)
        self.previous_image_button.setEnabled(True)
        self.next_image_button.setEnabled(True)

        if self.SettingsWidget:
            self.SettingsWidget.set_split_hotkey_button.setEnabled(False)
            self.SettingsWidget.set_reset_hotkey_button.setEnabled(False)
            self.SettingsWidget.set_skip_split_hotkey_button.setEnabled(False)
            self.SettingsWidget.set_undo_split_hotkey_button.setEnabled(False)
            self.SettingsWidget.set_pause_hotkey_button.setEnabled(False)

        if not self.is_auto_controlled:
            self.start_auto_splitter_button.setEnabled(False)
            self.reset_button.setEnabled(True)
            self.undo_split_button.setEnabled(True)
            self.skip_split_button.setEnabled(True)

        QApplication.processEvents()

    def gui_changes_on_reset(self):
        self.start_auto_splitter_button.setText(START_AUTO_SPLITTER_TEXT)
        self.image_loop_value_label.setText("N/A")
        self.current_split_image.clear()
        self.current_image_file_label.clear()
        self.table_current_image_live_label.setText("-")
        self.table_current_image_highest_label.setText("-")
        self.table_current_image_threshold_label.setText("-")
        self.browse_button.setEnabled(True)
        self.reload_start_image_button.setEnabled(True)
        self.previous_image_button.setEnabled(False)
        self.next_image_button.setEnabled(False)

        if self.SettingsWidget:
            self.SettingsWidget.set_split_hotkey_button.setEnabled(True)
            self.SettingsWidget.set_reset_hotkey_button.setEnabled(True)
            self.SettingsWidget.set_skip_split_hotkey_button.setEnabled(True)
            self.SettingsWidget.set_undo_split_hotkey_button.setEnabled(True)
            self.SettingsWidget.set_pause_hotkey_button.setEnabled(True)
        if not self.is_auto_controlled:
            self.start_auto_splitter_button.setEnabled(True)
            self.reset_button.setEnabled(False)
            self.undo_split_button.setEnabled(False)
            self.skip_split_button.setEnabled(False)

        QApplication.processEvents()
        self.load_start_image(False, False)

    def __get_capture_for_comparison(self):
        """
        Grab capture region and resize for comparison
        """
        capture = capture_region(self.hwnd,
                                 self.settings_dict["capture_region"],
                                 self.settings_dict["force_print_window"])

        # This most likely means we lost capture (ie the captured window was closed, crashed, etc.)
        if capture is None:
            # Try to recover by using the window name
            self.live_image.setText("Trying to recover window...")
            hwnd = win32gui.FindWindow(None, self.settings_dict["captured_window_title"])
            # Don't fallback to desktop
            if hwnd:
                self.hwnd = hwnd
                capture = capture_region(self.hwnd,
                                         self.settings_dict["capture_region"],
                                         self.settings_dict["force_print_window"])
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

    def __update_split_image(self, specific_image: Optional[AutoSplitImage] = None):
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

        self.current_image_file_label.setText(self.split_image.filename)
        self.table_current_image_threshold_label.setText(f"{self.split_image.get_similarity_threshold(self):.2f}")

        # Set Image Loop #
        if specific_image and specific_image.image_type == ImageType.START:
            self.image_loop_value_label.setText("N/A")
        else:
            loop_tuple = self.split_images_and_loop_number[self.split_image_number]
            self.image_loop_value_label.setText(f"{loop_tuple[1]}/{loop_tuple[0].loops}")

        self.highest_similarity = 0.0
        # need to set split below threshold to false each time an image updates.
        self.split_below_threshold = False

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

            warning = QMessageBox.warning(
                self,
                "AutoSplit",
                f"Do you want to save changes made to settings file {settings_file_name}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)

            if warning is QMessageBox.StandardButton.Yes:
                if settings.save_settings(self):
                    exit_program()
                else:
                    a0.ignore()
            if warning is QMessageBox.StandardButton.No:
                exit_program()
            if warning is QMessageBox.StandardButton.Cancel:
                a0.ignore()
        else:
            exit_program()


def seconds_remaining_text(seconds: float):
    return f"{seconds:.1f} second{'' if 0 < seconds <= 1 else 's'} remaining"


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
            traceback.print_exception(type(exception), exception, exception.__traceback__)
        sys.exit(1)

    # Catch Keyboard Interrupts for a clean close
    signal.signal(signal.SIGINT, lambda code, _: sys.exit(code))

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
