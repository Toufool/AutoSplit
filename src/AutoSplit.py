#!/usr/bin/python3
import os
import signal
import sys
from collections.abc import Callable
from copy import deepcopy
from time import time
from types import FunctionType
from typing import NoReturn

import cv2
from cv2.typing import MatLike
from psutil import process_iter
from PySide6 import QtCore, QtGui
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QFileDialog, QLabel, QMainWindow, QMessageBox
from typing_extensions import override
from win32comext.shell import shell as shell32

import error_messages
import user_profile
from AutoControlledThread import AutoControlledThread
from AutoSplitImage import START_KEYWORD, AutoSplitImage, ImageType
from capture_method import CaptureMethodBase, CaptureMethodEnum
from gen import about, design, settings, update_checker
from hotkeys import HOTKEYS, after_setting_hotkey, send_command
from menu_bar import (
    about_qt,
    about_qt_for_python,
    check_for_updates,
    get_default_settings_from_ui,
    open_about,
    open_settings,
    open_update_checker,
    view_help,
)
from region_selection import align_region, select_region, select_window, validate_before_parsing
from split_parser import BELOW_FLAG, DUMMY_FLAG, PAUSE_FLAG, parse_and_validate_images
from user_profile import DEFAULT_PROFILE
from utils import (
    AUTOSPLIT_VERSION,
    BGRA_CHANNEL_COUNT,
    FROZEN,
    ONE_SECOND,
    auto_split_directory,
    decimal,
    flatten,
    is_valid_image,
    open_file,
)

CHECK_FPS_ITERATIONS = 10

myappid = f"Toufool.AutoSplit.v{AUTOSPLIT_VERSION}"
shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class AutoSplit(QMainWindow, design.Ui_MainWindow):
    # Parse command line args
    is_auto_controlled = "--auto-controlled" in sys.argv

    # Signals
    start_auto_splitter_signal = QtCore.Signal()
    reset_signal = QtCore.Signal()
    skip_split_signal = QtCore.Signal()
    undo_split_signal = QtCore.Signal()
    pause_signal = QtCore.Signal()
    screenshot_signal = QtCore.Signal()
    after_setting_hotkey_signal = QtCore.Signal()
    update_checker_widget_signal = QtCore.Signal(str, bool)
    load_start_image_signal = QtCore.Signal(bool, bool)
    # Use this signal when trying to show an error from outside the main thread
    show_error_signal = QtCore.Signal(FunctionType)

    # Timers
    timer_live_image = QtCore.QTimer()
    timer_live_image.setTimerType(QtCore.Qt.TimerType.PreciseTimer)
    timer_start_image = QtCore.QTimer()
    timer_start_image.setTimerType(QtCore.Qt.TimerType.PreciseTimer)

    # Widgets
    AboutWidget: about.Ui_AboutAutoSplitWidget | None = None
    UpdateCheckerWidget: update_checker.Ui_UpdateChecker | None = None
    CheckForUpdatesThread: QtCore.QThread | None = None
    SettingsWidget: settings.Ui_SettingsWidget | None = None

    def __init__(self):  # noqa: PLR0915
        super().__init__()

        # Initialize a few attributes
        self.hwnd = 0
        """Window Handle used for Capture Region"""
        self.last_saved_settings = deepcopy(DEFAULT_PROFILE)
        self.similarity = 0.0
        self.split_image_number = 0
        self.split_images_and_loop_number: list[tuple[AutoSplitImage, int]] = []
        self.split_groups: list[list[int]] = []
        self.capture_method = CaptureMethodBase(self)
        self.is_running = False

        self.last_successfully_loaded_settings_file_path = ""
        """Path of the settings file to default to. `None` until we try to load once."""

        # Automatic timer start
        self.highest_similarity = 0.0
        self.reset_highest_similarity = 0.0

        # Ensure all other attributes are defined
        self.waiting_for_split_delay = False
        self.split_below_threshold = False
        self.run_start_time = 0.0
        self.start_image: AutoSplitImage | None = None
        self.reset_image: AutoSplitImage | None = None
        self.split_images: list[AutoSplitImage] = []
        self.split_image: AutoSplitImage | None = None
        self.update_auto_control: AutoControlledThread | None = None

        # Setup global error handling
        def _show_error_signal_slot(error_message_box: Callable[..., object]):
            return error_message_box()

        self.show_error_signal.connect(_show_error_signal_slot)
        sys.excepthook = error_messages.make_excepthook(self)

        self.setupUi(self)
        self.setWindowTitle(
            f"AutoSplit v{AUTOSPLIT_VERSION}" +
            (" (externally controlled)" if self.is_auto_controlled else ""),
        )

        # Hotkeys need to be initialized to be passed as thread arguments in hotkeys.py
        for hotkey in HOTKEYS:
            setattr(self, f"{hotkey}_hotkey", None)

        # Get default values defined in SettingsDialog
        self.settings_dict = get_default_settings_from_ui(self)
        user_profile.load_check_for_updates_on_open(self)

        if self.is_auto_controlled:
            self.start_auto_splitter_button.setEnabled(False)

            # Send version and process ID to stdout
            # THIS HAS TO BE THE FIRST TWO LINES SENT
            print(f"{AUTOSPLIT_VERSION}\n{os.getpid()}", flush=True)

            # Use and Start the thread that checks for updates from LiveSplit
            self.update_auto_control = AutoControlledThread(self)
            self.update_auto_control.start()

        # split image folder line edit text
        self.split_image_folder_input.setText("No Folder Selected")

        # Connecting menu actions
        self.action_view_help.triggered.connect(view_help)
        self.action_about.triggered.connect(lambda: open_about(self))
        self.action_about_qt.triggered.connect(about_qt)
        self.action_about_qt_for_python.triggered.connect(about_qt_for_python)
        self.action_check_for_updates.triggered.connect(lambda: check_for_updates(self))
        self.action_settings.triggered.connect(lambda: open_settings(self))
        self.action_save_profile.triggered.connect(lambda: user_profile.save_settings(self))
        self.action_save_profile_as.triggered.connect(lambda: user_profile.save_settings_as(self))
        self.action_load_profile.triggered.connect(lambda: user_profile.load_settings(self))

        # Connecting button clicks to functions
        self.split_image_folder_button.clicked.connect(self.__browse)
        self.select_region_button.clicked.connect(lambda: select_region(self))
        self.take_screenshot_button.clicked.connect(self.__take_screenshot)
        self.start_auto_splitter_button.clicked.connect(self.__auto_splitter)
        self.check_fps_button.clicked.connect(self.__check_fps)
        self.reset_button.clicked.connect(self.reset)
        self.skip_split_button.clicked.connect(self.skip_split)
        self.undo_split_button.clicked.connect(self.undo_split)
        self.next_image_button.clicked.connect(lambda: self.skip_split(True))
        self.previous_image_button.clicked.connect(lambda: self.undo_split(True))
        self.align_region_button.clicked.connect(lambda: align_region(self))
        self.select_window_button.clicked.connect(lambda: select_window(self))
        self.reload_start_image_button.clicked.connect(lambda: self.__load_start_image(True, True))
        self.action_check_for_updates_on_open.changed.connect(
            lambda: user_profile.set_check_for_updates_on_open(self, self.action_check_for_updates_on_open.isChecked()),
        )

        # update x, y, width, and height when changing the value of these spinbox's are changed
        self.x_spinbox.valueChanged.connect(self.__update_x)
        self.y_spinbox.valueChanged.connect(self.__update_y)
        self.width_spinbox.valueChanged.connect(self.__update_width)
        self.height_spinbox.valueChanged.connect(self.__update_height)

        # connect signals to functions
        self.after_setting_hotkey_signal.connect(lambda: after_setting_hotkey(self))
        self.start_auto_splitter_signal.connect(self.__auto_splitter)

        def _update_checker_widget_signal_slot(latest_version: str, check_on_open: bool):
            return open_update_checker(self, latest_version, check_on_open)

        self.update_checker_widget_signal.connect(_update_checker_widget_signal_slot)

        self.load_start_image_signal.connect(self.__load_start_image)
        self.reset_signal.connect(self.reset)
        self.skip_split_signal.connect(self.skip_split)
        self.undo_split_signal.connect(self.undo_split)
        self.pause_signal.connect(self.pause)
        self.screenshot_signal.connect(self.__take_screenshot)

        # live image checkbox
        self.timer_live_image.timeout.connect(lambda: self.__update_live_image_details(None, True))
        self.timer_live_image.start(int(ONE_SECOND / self.settings_dict["fps_limit"]))

        # Automatic timer start
        self.timer_start_image.timeout.connect(self.__start_image_function)

        self.show()

        try:
            import pyi_splash  # pyright: ignore[reportMissingModuleSource]  # noqa: PLC0415

            pyi_splash.close()
        except ModuleNotFoundError:
            pass

        # Needs to be after Ui_MainWindow.show() to be shown on top
        if not self.is_auto_controlled:
            # Must also be done later to help load the saved capture window
            user_profile.load_settings_on_open(self)
        if self.action_check_for_updates_on_open.isChecked():
            check_for_updates(self, check_on_open=True)

    # FUNCTIONS

    def __browse(self):
        # User selects the file with the split images in it.
        new_split_image_directory = QFileDialog.getExistingDirectory(
            self,
            "Select Split Image Directory",
            os.path.join(self.settings_dict["split_image_directory"] or auto_split_directory, ".."),
        )

        # If the user doesn't select a folder, it defaults to "".
        if new_split_image_directory:
            # set the split image folder line to the directory text
            self.settings_dict["split_image_directory"] = new_split_image_directory
            self.split_image_folder_input.setText(f"{new_split_image_directory}/")
            self.load_start_image_signal.emit(False, True)

    def __update_live_image_details(self, capture: MatLike | None, called_from_timer: bool = False):
        # HACK: Since this is also called in __get_capture_for_comparison,
        # we don't need to update anything if the app is running
        if called_from_timer:
            if self.is_running or self.start_image:
                return
            capture = self.capture_method.get_frame()

        # Update title from target window or Capture Device name
        capture_region_window_label = (
            self.settings_dict["capture_device_name"]
            if self.settings_dict["capture_method"] == CaptureMethodEnum.VIDEO_CAPTURE_DEVICE
            else self.settings_dict["captured_window_title"]
        )
        self.capture_region_window_label.setText(capture_region_window_label)

        # Simply clear if "live capture region" setting is off
        if not (self.settings_dict["live_capture_region"] and capture_region_window_label):
            self.live_image.clear()
        # Set live image in UI
        else:
            set_preview_image(self.live_image, capture)

    def __load_start_image(self, started_by_button: bool = False, wait_for_delay: bool = True):
        """Not thread safe (if triggered by LiveSplit for example). Use `load_start_image_signal.emit` instead."""
        self.timer_start_image.stop()
        self.current_image_file_label.setText("-")
        self.start_image_status_value_label.setText("not found")
        set_preview_image(self.current_split_image, None)

        if not (validate_before_parsing(self, started_by_button) and parse_and_validate_images(self)):
            QApplication.processEvents()
            return

        if not self.start_image:
            if started_by_button:
                error_messages.no_keyword_image(START_KEYWORD)
            QApplication.processEvents()
            return

        self.split_image_number = 0

        if not wait_for_delay and self.start_image.get_pause_time(self) > 0:
            self.start_image_status_value_label.setText("paused")
            self.table_current_image_highest_label.setText("-")
            self.table_current_image_threshold_label.setText("-")
        else:
            self.start_image_status_value_label.setText("ready")
            self.__update_split_image(self.start_image)

        self.highest_similarity = 0.0
        self.reset_highest_similarity = 0.0
        self.split_below_threshold = False
        self.timer_start_image.start(int(ONE_SECOND / self.settings_dict["fps_limit"]))

        QApplication.processEvents()

    def __start_image_function(self):
        if not self.start_image:
            return

        self.start_image_status_value_label.setText("ready")
        self.__update_split_image(self.start_image)

        capture = self.__get_capture_for_comparison()
        start_image_threshold = self.start_image.get_similarity_threshold(self)
        start_image_similarity = self.start_image.compare_with_capture(self, capture)

        # If the similarity becomes higher than highest similarity, set it as such.
        if start_image_similarity > self.highest_similarity:
            self.highest_similarity = start_image_similarity

        self.table_current_image_live_label.setText(decimal(start_image_similarity))
        self.table_current_image_highest_label.setText(decimal(self.highest_similarity))
        self.table_current_image_threshold_label.setText(decimal(start_image_threshold))

        # If the {b} flag is set, let similarity go above threshold first, then split on similarity below threshold
        # Otherwise just split when similarity goes above threshold
        # TODO: Abstract with similar check in split image
        below_flag = self.start_image.check_flag(BELOW_FLAG)

        # Negative means belove threshold, positive means above
        similarity_diff = start_image_similarity - start_image_threshold
        if below_flag and not self.split_below_threshold and similarity_diff >= 0:
            self.split_below_threshold = True
            return
        if (
            (below_flag and self.split_below_threshold and similarity_diff < 0 and is_valid_image(capture))  # noqa: PLR0916 # See above TODO
            or (not below_flag and similarity_diff >= 0)
        ):
            self.timer_start_image.stop()
            self.split_below_threshold = False

            if not self.start_image.check_flag(DUMMY_FLAG):
                # Delay Start Image if needed
                if self.start_image.get_delay_time(self) > 0:
                    self.start_image_status_value_label.setText("delaying start...")
                    delay_start_time = time()
                    start_delay = self.start_image.get_delay_time(self) / ONE_SECOND
                    time_delta = 0.0
                    while time_delta < start_delay:
                        delay_time_left = start_delay - time_delta
                        self.current_split_image.setText(
                            f"Delayed Before Starting:\n {seconds_remaining_text(delay_time_left)}",
                        )
                        # Wait 0.1s. Doesn't need to be shorter as we only show 1 decimal
                        QTest.qWait(100)
                        time_delta = time() - delay_start_time
                send_command(self, "start")

            self.start_image_status_value_label.setText("started")
            self.start_auto_splitter()

    # update x, y, width, height when spinbox values are changed
    def __update_x(self):
        self.settings_dict["capture_region"]["x"] = self.x_spinbox.value()

    def __update_y(self):
        self.settings_dict["capture_region"]["y"] = self.y_spinbox.value()

    def __update_width(self):
        self.settings_dict["capture_region"]["width"] = self.width_spinbox.value()

    def __update_height(self):
        self.settings_dict["capture_region"]["height"] = self.height_spinbox.value()

    def __take_screenshot(self):
        if not validate_before_parsing(self, check_empty_directory=False):
            return

        # Check if file exists and rename it if it does.
        # Below starts the file_name_number at #001 up to #999. After that it will go to 1000,
        # which is a problem, but I doubt anyone will get to 1000 split images...
        screenshot_index = 1
        while True:
            screenshot_path = os.path.join(
                self.settings_dict["screenshot_directory"] or self.settings_dict["split_image_directory"],
                f"{screenshot_index:03}_SplitImage.png",
            )
            if not os.path.exists(screenshot_path):
                break
            screenshot_index += 1

        # Grab screenshot of capture region
        capture = self.capture_method.get_frame()
        if not is_valid_image(capture):
            error_messages.region()
            return

        # Save and open image
        cv2.imwrite(screenshot_path, capture)
        if self.settings_dict["open_screenshot"]:
            open_file(screenshot_path)

    def __check_fps(self):
        self.fps_value_label.setText("...")
        QApplication.processEvents()
        if not (validate_before_parsing(self) and parse_and_validate_images(self)):
            self.fps_value_label.clear()
            return

        images = self.split_images
        if self.start_image:
            images.append(self.start_image)
        if self.reset_image:
            images.append(self.reset_image)

        # run X iterations of screenshotting capture region + comparison + displaying.
        t0 = time()
        last_capture: MatLike | None = None
        for image in images:
            count = 0
            while count < CHECK_FPS_ITERATIONS:
                new_capture = self.__get_capture_for_comparison()
                _ = image.compare_with_capture(self, new_capture)
                # TODO: If an old image is always returned, this becomes an infinite loop
                if new_capture is not last_capture:
                    count += 1
                last_capture = new_capture

        # calculate FPS
        t1 = time()
        fps = int((CHECK_FPS_ITERATIONS * len(images)) / (t1 - t0))
        self.fps_value_label.setText(str(fps))

    def __is_current_split_out_of_range(self):
        return (
            self.split_image_number < 0
            or self.split_image_number > len(self.split_images_and_loop_number) - 1
        )

    def undo_split(self, navigate_image_only: bool = False):
        """Undo Split" and "Prev. Img." buttons connect to here."""
        # Can't undo until timer is started
        # or Undoing past the first image
        if (
            not self.is_running
            or "Delayed Split" in self.current_split_image.text()
            or (not self.undo_split_button.isEnabled() and not self.is_auto_controlled)
            or self.__is_current_split_out_of_range()
        ):
            return

        if not navigate_image_only:
            for i, group in enumerate(self.split_groups):
                if i > 0 and self.split_image_number in group:
                    self.split_image_number = self.split_groups[i - 1][-1]
                    break
        else:
            self.split_image_number -= 1

        self.__update_split_image()
        if not navigate_image_only:
            send_command(self, "undo")

    def skip_split(self, navigate_image_only: bool = False):
        """Skip Split" and "Next Img." buttons connect to here."""
        # Can't skip or split until timer is started
        # or Splitting/skipping when there are no images left
        if (
            not self.is_running
            or "Delayed Split" in self.current_split_image.text()
            or not (self.skip_split_button.isEnabled() or self.is_auto_controlled or navigate_image_only)
            or self.__is_current_split_out_of_range()
        ):
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
        # TODO: add what to do when you hit pause hotkey, if this even needs to be done
        pass

    def reset(self):
        """
        When the reset button or hotkey is pressed, it will set `is_running` to False,
        which will trigger in the __auto_splitter function, if running, to abort and change GUI.
        """
        self.is_running = False

    # Functions for the hotkeys to return to the main thread from signals and start their corresponding functions
    def start_auto_splitter(self):
        # If the auto splitter is already running or the button is disabled, don't emit the signal to start it.
        if (
            self.is_running
            or (not self.start_auto_splitter_button.isEnabled() and not self.is_auto_controlled)
        ):
            return

        start_label = self.start_image_status_value_label.text()
        if start_label.endswith(("ready", "paused")):
            self.start_image_status_value_label.setText("not ready")

        self.start_auto_splitter_signal.emit()

    def __check_for_reset_state_update_ui(self):
        """Check if AutoSplit is started, if not then update the GUI."""
        if not self.is_running:
            self.gui_changes_on_reset(True)
            return True
        return False

    def __auto_splitter(self):  # noqa: PLR0912,PLR0915
        if not self.settings_dict["split_hotkey"] and not self.is_auto_controlled:
            self.gui_changes_on_reset(True)
            error_messages.split_hotkey()
            return

        # Set start time before parsing the images as it's a heavy operation that will cause delays
        self.run_start_time = time()

        if not (validate_before_parsing(self) and parse_and_validate_images(self)):
            # `safe_to_reload_start_image: bool = False` because __load_start_image also does this check,
            # we don't want to double a Start/Reset Image error message
            self.gui_changes_on_reset(False)
            return

        # Construct a list of images + loop count tuples.
        self.split_images_and_loop_number = list(
            flatten(
                ((split_image, i + 1) for i in range(split_image.loops))
                for split_image
                in self.split_images
            ),
        )

        # Construct groups of splits
        self.split_groups = []
        dummy_splits_array: list[bool] = []
        number_of_split_images = len(self.split_images_and_loop_number)
        current_group: list[int] = []
        self.split_groups.append(current_group)
        for i, image in enumerate(self.split_images_and_loop_number):
            current_group.append(i)
            dummy = image[0].check_flag(DUMMY_FLAG)
            dummy_splits_array.append(dummy)
            if not dummy and i < number_of_split_images - 1:
                current_group = []
                self.split_groups.append(current_group)

        self.is_running = True
        self.gui_changes_on_start()

        # Start pause time
        if self.start_image:
            self.__pause_loop(self.start_image.get_pause_time(self), "None (Paused).")

        # Initialize a few attributes
        self.split_image_number = 0
        self.waiting_for_split_delay = False
        self.split_below_threshold = False
        split_time = 0

        # First loop: stays in this loop until all of the split images have been split
        while self.split_image_number < number_of_split_images:
            # Check if we are not waiting for the split delay to send the key press
            if self.waiting_for_split_delay:
                time_millis = int(round(time() * ONE_SECOND))
                if time_millis < split_time:
                    QApplication.processEvents()
                    continue

            self.__update_split_image()

            # Type checking
            if not self.split_image:
                return

            # Second loop: stays in this loop until similarity threshold is met
            if self.__similarity_threshold_loop(number_of_split_images, dummy_splits_array):
                return

            # We need to make sure that this isn't a dummy split before sending the key press.
            if not self.split_image.check_flag(DUMMY_FLAG):
                # If it's a delayed split, check if the delay has passed
                # Otherwise calculate the split time for the key press
                split_delay = self.split_image.get_delay_time(self) / ONE_SECOND
                if split_delay > 0 and not self.waiting_for_split_delay:
                    split_time = round(time() + split_delay * ONE_SECOND)
                    self.waiting_for_split_delay = True
                    buttons_to_disable = [
                        self.next_image_button,
                        self.previous_image_button,
                        self.undo_split_button,
                        self.skip_split_button,
                    ]
                    for button in buttons_to_disable:
                        button.setEnabled(False)
                    self.current_image_file_label.clear()

                    # check for reset while delayed and display a counter of the remaining split delay time
                    if self.__pause_loop(split_delay, "Delayed Split:"):
                        return

                    for button in buttons_to_disable:
                        button.setEnabled(True)

                self.waiting_for_split_delay = False

                # if {p} flag hit pause key, otherwise hit split hotkey
                send_command(self, "pause" if self.split_image.check_flag(PAUSE_FLAG) else "split")

            # if loop check box is checked and its the last split, go to first split.
            # else go to the next split image.
            if self.settings_dict["loop_splits"] and self.split_image_number == number_of_split_images - 1:
                self.split_image_number = 0
            else:
                self.split_image_number += 1

            # If its not the last split image, pause for the amount set by the user
            # A pause loop to check if the user presses skip split, undo split, or reset here.
            # Also updates the current split image text, counting down the time until the next split image
            if self.__pause_loop(self.split_image.get_pause_time(self), "None (Paused)."):
                return

        # loop breaks to here when the last image splits
        self.is_running = False
        self.gui_changes_on_reset(True)

    def __similarity_threshold_loop(self, number_of_split_images: int, dummy_splits_array: list[bool]):
        """
        Wait until the similarity threshold is met.

        Returns True if the loop was interrupted by a reset.
        """
        # Type checking
        if not self.split_image:
            return False

        start = time()
        while True:
            capture = self.__get_capture_for_comparison()

            if self.__reset_if_should(capture):
                return True

            similarity = self.split_image.compare_with_capture(self, capture)

            # Show live similarity
            self.table_current_image_live_label.setText(decimal(similarity))

            # if the similarity becomes higher than highest similarity, set it as such.
            if similarity > self.highest_similarity:
                self.highest_similarity = similarity

            # show live highest similarity if the checkbox is checked
            self.table_current_image_highest_label.setText(decimal(self.highest_similarity))

            # If its the last split image and last loop number, disable the next image button
            # If its the first split image, disable the undo split and previous image buttons
            self.next_image_button.setEnabled(self.split_image_number != number_of_split_images - 1)
            self.previous_image_button.setEnabled(self.split_image_number != 0)
            if not self.is_auto_controlled:
                # If its the last non-dummy split image and last loop number, disable the skip split button
                self.skip_split_button.setEnabled(dummy_splits_array[self.split_image_number :].count(False) > 1)
                self.undo_split_button.setEnabled(self.split_image_number != 0)
            QApplication.processEvents()

            # Limit the number of time the comparison runs to reduce cpu usage
            frame_interval = 1 / self.settings_dict["fps_limit"]
            # Use a time delta to have a consistant check interval
            wait_delta_ms = int((frame_interval - (time() - start) % frame_interval) * ONE_SECOND)

            below_flag = self.split_image.check_flag(BELOW_FLAG)
            # if the b flag is set, let similarity go above threshold first,
            # then split on similarity below threshold.
            # if no b flag, just split when similarity goes above threshold.
            # TODO: Abstract with similar check in Start Image
            if not self.waiting_for_split_delay:
                if similarity >= self.split_image.get_similarity_threshold(self):
                    if not below_flag:
                        break
                    if not self.split_below_threshold:
                        self.split_below_threshold = True
                        QTest.qWait(wait_delta_ms)
                        continue

                elif below_flag and self.split_below_threshold and is_valid_image(capture):
                    self.split_below_threshold = False
                    break

            QTest.qWait(wait_delta_ms)

        return False

    def __pause_loop(self, stop_time: float, message: str):
        """
        Wait for a certain time and show the timer to the user.
        Can be stopped early if the current split goes past the one when the loop started.

        Returns True if the loop was interrupted by a reset.
        """
        if stop_time <= 0:
            return False
        start_time = time()
        # Set a "pause" split image number.
        # This is done so that it can detect if user hit split/undo split while paused/delayed.
        pause_split_image_number = self.split_image_number
        while True:
            # Calculate similarity for Reset Image
            if self.__reset_if_should(self.__get_capture_for_comparison()):
                return True

            time_delta = time() - start_time
            if (
                # Check for end of the pause/delay
                time_delta >= stop_time
                # Check for skip split / next image:
                or self.split_image_number > pause_split_image_number
                # Check for undo split / previous image:
                or self.split_image_number < pause_split_image_number
            ):
                break

            self.current_split_image.setText(f"{message} {seconds_remaining_text(stop_time - time_delta)}")

            QTest.qWait(1)
        return False

    def gui_changes_on_start(self):
        self.timer_start_image.stop()
        self.start_auto_splitter_button.setText("Running...")
        self.split_image_folder_button.setEnabled(False)
        self.reload_start_image_button.setEnabled(False)
        self.previous_image_button.setEnabled(True)
        self.next_image_button.setEnabled(True)

        # TODO: Do we actually need to disable setting new hotkeys once started?
        # What does this achieve? (See below TODO)
        if self.SettingsWidget:
            for hotkey in HOTKEYS:
                getattr(self.SettingsWidget, f"set_{hotkey}_hotkey_button").setEnabled(False)

        if not self.is_auto_controlled:
            self.start_auto_splitter_button.setEnabled(False)
            self.reset_button.setEnabled(True)
            self.undo_split_button.setEnabled(True)
            self.skip_split_button.setEnabled(True)

        QApplication.processEvents()

    def gui_changes_on_reset(self, safe_to_reload_start_image: bool = False):
        self.start_auto_splitter_button.setText("Start Auto Splitter")
        self.image_loop_value_label.setText("N/A")
        self.current_split_image.clear()
        self.current_image_file_label.clear()
        self.table_current_image_live_label.setText("-")
        self.table_current_image_highest_label.setText("-")
        self.table_current_image_threshold_label.setText("-")
        self.table_reset_image_live_label.setText("-")
        self.table_reset_image_highest_label.setText("-")
        self.table_reset_image_threshold_label.setText("-")
        self.split_image_folder_button.setEnabled(True)
        self.reload_start_image_button.setEnabled(True)
        self.previous_image_button.setEnabled(False)
        self.next_image_button.setEnabled(False)

        # TODO: Do we actually need to disable setting new hotkeys once started?
        # What does this achieve? (see above TODO)
        if self.SettingsWidget and not self.is_auto_controlled:
            for hotkey in HOTKEYS:
                getattr(self.SettingsWidget, f"set_{hotkey}_hotkey_button").setEnabled(True)

        if not self.is_auto_controlled:
            self.start_auto_splitter_button.setEnabled(True)
            self.reset_button.setEnabled(False)
            self.undo_split_button.setEnabled(False)
            self.skip_split_button.setEnabled(False)

        QApplication.processEvents()
        if safe_to_reload_start_image:
            self.load_start_image_signal.emit(False, False)

    def __get_capture_for_comparison(self):
        """Grab capture region and resize for comparison."""
        capture = self.capture_method.get_frame()

        # This most likely means we lost capture
        # (ie the captured window was closed, crashed, lost capture device, etc.)
        if not is_valid_image(capture):
            # Try to recover by using the window name
            if self.settings_dict["capture_method"] == CaptureMethodEnum.VIDEO_CAPTURE_DEVICE:
                self.live_image.setText("Waiting for capture device...")
            else:
                message = "Trying to recover window..."
                if self.settings_dict["capture_method"] == CaptureMethodEnum.BITBLT:
                    message += "\n(captured window may be incompatible with BitBlt)"
                self.live_image.setText(message)
                recovered = self.capture_method.recover_window(self.settings_dict["captured_window_title"])
                if recovered:
                    capture = self.capture_method.get_frame()

        self.__update_live_image_details(capture)
        return capture

    def __reset_if_should(self, capture: MatLike | None):
        """Checks if we should reset, resets if it's the case, and returns the result."""
        if self.reset_image:
            if self.settings_dict["enable_auto_reset"]:
                similarity = self.reset_image.compare_with_capture(self, capture)
                threshold = self.reset_image.get_similarity_threshold(self)

                pause_times = [self.reset_image.get_pause_time(self)]
                if self.start_image:
                    pause_times.append(self.start_image.get_pause_time(self))
                paused = time() - self.run_start_time <= max(pause_times)
                if paused:
                    should_reset = False
                    self.table_reset_image_live_label.setText("paused")
                else:
                    should_reset = similarity >= threshold
                    if similarity > self.reset_highest_similarity:
                        self.reset_highest_similarity = similarity
                    self.table_reset_image_highest_label.setText(decimal(self.reset_highest_similarity))
                    self.table_reset_image_live_label.setText(decimal(similarity))

                self.table_reset_image_threshold_label.setText(decimal(threshold))

                if should_reset:
                    send_command(self, "reset")
                    self.reset()
            else:
                self.table_reset_image_live_label.setText("disabled")
        else:
            self.table_reset_image_live_label.setText("N/A")
            self.table_reset_image_threshold_label.setText("N/A")
            self.table_reset_image_highest_label.setText("N/A")

        return self.__check_for_reset_state_update_ui()

    def __update_split_image(self, specific_image: AutoSplitImage | None = None):
        # Start image is expected to be out of range (index 0 of 0-length array)
        if not specific_image or specific_image.image_type != ImageType.START:
            # need to reset highest_similarity and split_below_threshold each time an image updates.
            self.highest_similarity = 0.0
            self.split_below_threshold = False
            # Splitting/skipping when there are no images left or Undoing past the first image
            if self.__is_current_split_out_of_range():
                self.reset()
                return

        # Get split image
        self.split_image = specific_image or self.split_images_and_loop_number[0 + self.split_image_number][0]
        if is_valid_image(self.split_image.byte_array):
            set_preview_image(self.current_split_image, self.split_image.byte_array)

        self.current_image_file_label.setText(self.split_image.filename)
        self.table_current_image_threshold_label.setText(decimal(self.split_image.get_similarity_threshold(self)))

        # Set Image Loop number
        if specific_image and specific_image.image_type == ImageType.START:
            self.image_loop_value_label.setText("N/A")
        else:
            loop_tuple = self.split_images_and_loop_number[self.split_image_number]
            self.image_loop_value_label.setText(f"{loop_tuple[1]}/{loop_tuple[0].loops}")

    @override
    def closeEvent(self, event: QtGui.QCloseEvent | None = None):
        """Exit safely when closing the window."""

        def exit_program() -> NoReturn:
            if self.update_auto_control:
                # self.update_auto_control.terminate() hangs in PySide6
                self.update_auto_control.quit()
            self.capture_method.close()
            if event is not None:
                event.accept()
            if self.is_auto_controlled:
                # stop main thread (which is probably blocked reading input) via an interrupt signal
                os.kill(os.getpid(), signal.SIGINT)
            sys.exit()

        # `event is None` simulates LiveSplit quitting without asking.
        # This also more gracefully exits LiveSplit
        # Users can still manually save their settings
        if event is None or not user_profile.have_settings_changed(self):
            exit_program()

        # Give a different warning if there was never a settings file that was loaded successfully,
        # and "save as" instead of "save".
        settings_file_name = (
            "Untitled"
            if not self.last_successfully_loaded_settings_file_path
            else os.path.basename(self.last_successfully_loaded_settings_file_path)
        )

        warning = QMessageBox.warning(
            self,
            "AutoSplit",
            f"Do you want to save changes made to settings file {settings_file_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
        )

        if warning is QMessageBox.StandardButton.Yes:
            if user_profile.save_settings(self):
                exit_program()
        elif warning is QMessageBox.StandardButton.No:
            exit_program()

        # Fallthrough case: Prevent program from closing.
        event.ignore()


def set_preview_image(qlabel: QLabel, image: MatLike | None):
    if not is_valid_image(image):
        # Clear current pixmap if no image. But don't clear text
        if not qlabel.text():
            qlabel.clear()
    else:
        height, width, channels = image.shape

        if channels == BGRA_CHANNEL_COUNT:
            image_format = QtGui.QImage.Format.Format_RGBA8888
            capture = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
        else:
            image_format = QtGui.QImage.Format.Format_BGR888
            capture = image

        qimage = QtGui.QImage(
            capture.data,  # pyright: ignore[reportGeneralTypeIssues] # https://bugreports.qt.io/browse/PYSIDE-2476
            width,
            height,
            width * channels,
            image_format,
        )
        qlabel.setPixmap(
            QtGui.QPixmap(qimage).scaled(
                qlabel.size(),
                QtCore.Qt.AspectRatioMode.IgnoreAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            ),
        )


def seconds_remaining_text(seconds: float):
    return f"{seconds:.1f} second{'' if 0 < seconds <= 1 else 's'} remaining"


def is_already_open():
    # When running directly in Python, any AutoSplit process means it's already open
    # When bundled, we must ignore itself and the splash screen
    max_processes = 3 if FROZEN else 1
    process_count = 0
    for process in process_iter():
        if process.name() == "AutoSplit.exe":
            process_count += 1
        if process_count >= max_processes:
            return True
    return False


def main():
    # Best to call setStyle before the QApplication constructor
    # https://doc.qt.io/qt-6/qapplication.html#setStyle-1
    QApplication.setStyle("fusion")
    # Call to QApplication outside the try-except so we can show error messages
    app = QApplication(sys.argv)
    try:
        app.setWindowIcon(QtGui.QIcon(":/resources/icon.ico"))

        if is_already_open():
            error_messages.already_open()

        AutoSplit()

        if not FROZEN:
            # Kickoff the event loop every so often so we can handle KeyboardInterrupt (^C)
            timer = QtCore.QTimer()
            timer.timeout.connect(lambda: None)
            timer.start(500)

        exit_code = app.exec()
    except Exception as exception:  # noqa: BLE001 # We really want to catch everything here
        error_messages.handle_top_level_exceptions(exception)

    # Catch Keyboard Interrupts for a clean close
    signal.signal(signal.SIGINT, lambda code, _: sys.exit(code))

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
