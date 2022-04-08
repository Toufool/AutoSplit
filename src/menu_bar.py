from __future__ import annotations

import webbrowser
from typing import TYPE_CHECKING, Any

import requests
from packaging import version
from PyQt6 import QtWidgets
from PyQt6.QtCore import QThread
from requests.exceptions import RequestException
from simplejson.errors import JSONDecodeError

import error_messages
import user_profile
from gen import about, design, resources_rc, settings as settings_ui, update_checker  # noqa: F401
from hotkeys import set_hotkey

if TYPE_CHECKING:
    from AutoSplit import AutoSplit

# AutoSplit Version number
VERSION = "1.6.1"


# About Window
class __AboutWidget(QtWidgets.QWidget, about.Ui_AboutAutoSplitWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.created_by_label.setOpenExternalLinks(True)
        self.donate_button_label.setOpenExternalLinks(True)
        self.version_label.setText(f"Version: {VERSION}")
        self.show()


def open_about(autosplit: AutoSplit):
    autosplit.AboutWidget = __AboutWidget()


class __UpdateCheckerWidget(QtWidgets.QWidget, update_checker.Ui_UpdateChecker):
    def __init__(self, latest_version: str, design_window: design.Ui_MainWindow, check_on_open: bool = False):
        super().__init__()
        self.setupUi(self)
        self.current_version_number_label.setText(VERSION)
        self.latest_version_number_label.setText(latest_version)
        self.left_button.clicked.connect(self.open_update)
        self.do_not_ask_again_checkbox.stateChanged.connect(self.do_not_ask_me_again_state_changed)
        self.design_window = design_window
        if version.parse(latest_version) > version.parse(VERSION):
            self.do_not_ask_again_checkbox.setVisible(check_on_open)
            self.show()
        elif not check_on_open:
            self.update_status_label.setText("You are on the latest AutoSplit version.")
            self.go_to_download_label.setVisible(False)
            self.left_button.setVisible(False)
            self.right_button.setText("OK")
            self.do_not_ask_again_checkbox.setVisible(False)
            self.show()

    def open_update(self):
        webbrowser.open("https://github.com/Toufool/Auto-Split/releases/latest")
        self.close()

    def do_not_ask_me_again_state_changed(self):
        user_profile.set_check_for_updates_on_open(
            self.design_window,
            self.do_not_ask_again_checkbox.isChecked())


def open_update_checker(autosplit: AutoSplit, latest_version: str, check_on_open: bool):
    autosplit.UpdateCheckerWidget = __UpdateCheckerWidget(latest_version, autosplit, check_on_open)


def view_help():
    webbrowser.open("https://github.com/Toufool/Auto-Split#tutorial")


class __CheckForUpdatesThread(QThread):
    def __init__(self, autosplit: AutoSplit, check_on_open: bool):
        super().__init__()
        self.autosplit = autosplit
        self.check_on_open = check_on_open

    def run(self):
        try:
            response = requests.get("https://api.github.com/repos/Toufool/Auto-Split/releases/latest")
            latest_version = str(response.json()["name"]).split("v")[1]
            self.autosplit.update_checker_widget_signal.emit(latest_version, self.check_on_open)
        except (RequestException, KeyError, JSONDecodeError):
            if not self.check_on_open:
                self.autosplit.show_error_signal.emit(error_messages.check_for_updates)


def check_for_updates(autosplit: AutoSplit, check_on_open: bool = False):
    autosplit.CheckForUpdatesThread = __CheckForUpdatesThread(autosplit, check_on_open)
    autosplit.CheckForUpdatesThread.start()


class __SettingsWidget(QtWidgets.QDialog, settings_ui.Ui_DialogSettings):
    def __update_default_threshold(self, value: Any):
        self.__set_value("default_similarity_threshold", value)
        self.autosplit.table_current_image_threshold_label.setText(
            f"{self.autosplit.split_image.get_similarity_threshold(self.autosplit):.2f}"
            if self.autosplit.split_image
            else "-")
        self.autosplit.table_reset_image_threshold_label.setText(
            f"{self.autosplit.reset_image.get_similarity_threshold(self.autosplit):.2f}"
            if self.autosplit.reset_image
            else "-")

    def __set_value(self, key: str, value: Any):
        self.autosplit.settings_dict[key] = value

    def __init__(self, autosplit: AutoSplit):
        super().__init__()
        self.setupUi(self)
        self.autosplit = autosplit

# region Set initial values
        # Hotkeys
        self.split_input.setText(autosplit.settings_dict["split_hotkey"])
        self.reset_input.setText(autosplit.settings_dict["reset_hotkey"])
        self.undo_split_input.setText(autosplit.settings_dict["undo_split_hotkey"])
        self.skip_split_input.setText(autosplit.settings_dict["skip_split_hotkey"])
        self.pause_input.setText(autosplit.settings_dict["pause_hotkey"])

        # Capture Settings
        self.fps_limit_spinbox.setValue(autosplit.settings_dict["fps_limit"])
        self.live_capture_region_checkbox.setChecked(autosplit.settings_dict["live_capture_region"])
        self.force_print_window_checkbox.setChecked(autosplit.settings_dict["force_print_window"])

        # Image Settings
        self.default_comparison_method.setCurrentIndex(autosplit.settings_dict["default_comparison_method"])
        self.default_similarity_threshold_spinbox.setValue(autosplit.settings_dict["default_similarity_threshold"])
        self.default_delay_time_spinbox.setValue(autosplit.settings_dict["default_delay_time"])
        self.default_pause_time_spinbox.setValue(autosplit.settings_dict["default_pause_time"])
        self.loop_splits_checkbox.setChecked(autosplit.settings_dict["loop_splits"])
# endregion
# region Binding
        # Hotkeys
        self.set_split_hotkey_button.clicked.connect(lambda: set_hotkey(self.autosplit, "split"))
        self.set_reset_hotkey_button.clicked.connect(lambda: set_hotkey(self.autosplit, "reset"))
        self.set_skip_split_hotkey_button.clicked.connect(lambda: set_hotkey(self.autosplit, "skip_split"))
        self.set_undo_split_hotkey_button.clicked.connect(lambda: set_hotkey(self.autosplit, "undo_split"))
        self.set_pause_hotkey_button.clicked.connect(lambda: set_hotkey(self.autosplit, "pause"))

        # Capture Settings
        self.fps_limit_spinbox.valueChanged.connect(lambda: self.__set_value(
            "fps_limit",
            self.fps_limit_spinbox.value()))
        self.live_capture_region_checkbox.stateChanged.connect(lambda: self.__set_value(
            "live_capture_region",
            self.live_capture_region_checkbox.isChecked()))
        self.force_print_window_checkbox.stateChanged.connect(lambda: self.__set_value(
            "force_print_window",
            self.force_print_window_checkbox.isChecked()))

        # Image Settings
        self.default_comparison_method.currentIndexChanged.connect(lambda: self.__set_value(
            "default_comparison_method",
            self.default_comparison_method.currentIndex()))
        self.default_similarity_threshold_spinbox.valueChanged.connect(lambda: self.__update_default_threshold(
            self.default_similarity_threshold_spinbox.value()))
        self.default_delay_time_spinbox.valueChanged.connect(lambda: self.__set_value(
            "default_delay_time",
            self.default_delay_time_spinbox.value()))
        self.default_pause_time_spinbox.valueChanged.connect(lambda: self.__set_value(
            "default_pause_time",
            self.default_pause_time_spinbox.value()))
        self.loop_splits_checkbox.stateChanged.connect(lambda: self.__set_value(
            "loop_splits",
            self.loop_splits_checkbox.isChecked()))
# endregion

        self.show()


def open_settings(autosplit: AutoSplit):
    autosplit.SettingsWidget = __SettingsWidget(autosplit)


def get_default_settings_from_ui(autosplit: AutoSplit):
    temp_dialog = QtWidgets.QDialog()
    default_settings_dialog = settings_ui.Ui_DialogSettings()
    default_settings_dialog.setupUi(temp_dialog)
    default_settings: user_profile.UserProfileDict = {
        "split_hotkey": default_settings_dialog.split_input.text(),
        "reset_hotkey": default_settings_dialog.reset_input.text(),
        "undo_split_hotkey": default_settings_dialog.undo_split_input.text(),
        "skip_split_hotkey": default_settings_dialog.skip_split_input.text(),
        "pause_hotkey": default_settings_dialog.pause_input.text(),
        "fps_limit": default_settings_dialog.fps_limit_spinbox.value(),
        "live_capture_region": default_settings_dialog.live_capture_region_checkbox.isChecked(),
        "force_print_window": default_settings_dialog.force_print_window_checkbox.isChecked(),
        "default_comparison_method": default_settings_dialog.default_comparison_method.currentIndex(),
        "default_similarity_threshold": default_settings_dialog.default_similarity_threshold_spinbox.value(),
        "default_delay_time": default_settings_dialog.default_delay_time_spinbox.value(),
        "default_pause_time": default_settings_dialog.default_pause_time_spinbox.value(),
        "loop_splits": default_settings_dialog.loop_splits_checkbox.isChecked(),

        "split_image_directory": autosplit.split_image_folder_input.text(),
        "captured_window_title": "",
        "capture_region": {
            "x": autosplit.x_spinbox.value(),
            "y": autosplit.y_spinbox.value(),
            "width": autosplit.width_spinbox.value(),
            "height": autosplit.height_spinbox.value(),
        }
    }
    del temp_dialog
    return default_settings
