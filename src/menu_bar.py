from __future__ import annotations

import asyncio
import webbrowser
from typing import Any, cast

import requests
from packaging.version import parse as version_parse
from PyQt6 import QtCore, QtWidgets
from requests.exceptions import RequestException

import error_messages
import user_profile
from capture_method import (CAPTURE_METHODS, CameraInfo, CaptureMethodEnum, change_capture_method,
                            get_all_video_capture_devices)
from gen import about, design, resources_rc, settings as settings_ui, update_checker  # noqa F401
from hotkeys import HOTKEYS, Hotkey, set_hotkey
from utils import (AUTOSPLIT_VERSION, FIRST_WIN_11_BUILD, GITHUB_REPOSITORY, WINDOWS_BUILD_NUMBER, decimal,
                   find_autosplit_main_window, fire_and_forget)


class __AboutWidget(QtWidgets.QWidget, about.Ui_AboutAutoSplitWidget):
    """About Window"""

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.created_by_label.setOpenExternalLinks(True)
        self.donate_button_label.setOpenExternalLinks(True)
        self.version_label.setText(f"Version: {AUTOSPLIT_VERSION}")
        self.show()


def open_about():
    autosplit = find_autosplit_main_window()
    if not autosplit.AboutWidget or cast(QtWidgets.QWidget, autosplit.AboutWidget).isHidden():
        autosplit.AboutWidget = __AboutWidget()


class __UpdateCheckerWidget(QtWidgets.QWidget, update_checker.Ui_UpdateChecker):
    def __init__(self, latest_version: str, design_window: design.Ui_MainWindow, check_on_open: bool = False):
        super().__init__()
        self.setupUi(self)
        self.current_version_number_label.setText(AUTOSPLIT_VERSION)
        self.latest_version_number_label.setText(latest_version)
        self.left_button.clicked.connect(self.open_update)
        self.do_not_ask_again_checkbox.stateChanged.connect(self.do_not_ask_me_again_state_changed)
        self.design_window = design_window
        if version_parse(latest_version) > version_parse(AUTOSPLIT_VERSION):
            self.do_not_ask_again_checkbox.setVisible(check_on_open)
            self.left_button.setFocus()
            self.show()
        elif not check_on_open:
            self.update_status_label.setText("You are on the latest AutoSplit version.")
            self.go_to_download_label.setVisible(False)
            self.left_button.setVisible(False)
            self.right_button.setText("OK")
            self.do_not_ask_again_checkbox.setVisible(False)
            self.show()

    def open_update(self):
        webbrowser.open(f"https://github.com/{GITHUB_REPOSITORY}/releases/latest")
        self.close()

    def do_not_ask_me_again_state_changed(self):
        user_profile.set_check_for_updates_on_open(
            self.design_window,
            self.do_not_ask_again_checkbox.isChecked())


def open_update_checker(latest_version: str, check_on_open: bool):
    autosplit = find_autosplit_main_window()
    if not autosplit.UpdateCheckerWidget or cast(QtWidgets.QWidget, autosplit.UpdateCheckerWidget).isHidden():
        autosplit.UpdateCheckerWidget = __UpdateCheckerWidget(latest_version, autosplit, check_on_open)


def view_help():
    webbrowser.open(f"https://github.com/{GITHUB_REPOSITORY}#tutorial")


def about_qt():
    webbrowser.open("https://wiki.qt.io/About_Qt")


def about_qt_for_python():
    webbrowser.open("https://wiki.qt.io/Qt_for_Python")


@fire_and_forget
def check_for_updates(check_on_open: bool = False):
    autosplit = find_autosplit_main_window()
    try:
        response = requests.get(f"https://api.github.com/repos/{GITHUB_REPOSITORY}/releases/latest")
        latest_version = str(response.json()["name"]).split("v")[1]
        autosplit.update_checker_widget_signal.emit(latest_version, check_on_open)
    except (RequestException, KeyError):
        if not check_on_open:
            autosplit.show_error_signal.emit(error_messages.check_for_updates)
    except Exception as exception:   # pylint: disable=broad-except # We really want to catch everything here
        error = exception
        autosplit.show_error_signal.emit(lambda: error_messages.exception_traceback(error))


class __SettingsWidget(QtWidgets.QDialog, settings_ui.Ui_DialogSettings):
    __video_capture_devices: list[CameraInfo] = []
    """
    Used to temporarily store the existing cameras,
    we don't want to call `get_all_video_capture_devices` agains and possibly have a different result
    """

    def __update_default_threshold(self, value: Any):
        self.__set_value("default_similarity_threshold", value)
        self.autosplit.table_current_image_threshold_label.setText(
            decimal(self.autosplit.split_image.get_similarity_threshold())
            if self.autosplit.split_image
            else "-")
        self.autosplit.table_reset_image_threshold_label.setText(
            decimal(self.autosplit.reset_image.get_similarity_threshold())
            if self.autosplit.reset_image
            else "-")

    def __set_value(self, key: str, value: Any):
        self.autosplit.settings_dict[key] = value

    def get_capture_device_index(self, capture_device_id: int):
        """
        Returns 0 if the capture_device_id is invalid
        """
        try:
            return [device.device_id for device in self.__video_capture_devices].index(capture_device_id)
        except ValueError:
            return 0

    def __capture_method_changed(self):
        selected_capture_method = CAPTURE_METHODS.get_method_by_index(self.capture_method_combobox.currentIndex())
        change_capture_method(selected_capture_method)
        return selected_capture_method

    def __capture_device_changed(self):
        device_index = self.capture_device_combobox.currentIndex()
        if device_index == -1:
            return
        capture_device = self.__video_capture_devices[device_index]
        self.autosplit.settings_dict["capture_device_name"] = capture_device.name
        self.autosplit.settings_dict["capture_device_id"] = capture_device.device_id
        if self.autosplit.settings_dict["capture_method"] == CaptureMethodEnum.VIDEO_CAPTURE_DEVICE:
            change_capture_method(CaptureMethodEnum.VIDEO_CAPTURE_DEVICE)

    @fire_and_forget
    def __set_all_capture_devices(self):
        try:
            self.__video_capture_devices = asyncio.run(get_all_video_capture_devices())
            if len(self.__video_capture_devices) > 0:
                for i in range(self.capture_device_combobox.count()):
                    self.capture_device_combobox.removeItem(i)
                self.capture_device_combobox.addItems([
                    f"* {device.name}"
                    + (f" [{device.backend}]" if device.backend else "")
                    + (" (occupied)" if device.occupied else "")
                    for device in self.__video_capture_devices])
                self.capture_device_combobox.setEnabled(True)
                self.capture_device_combobox.setCurrentIndex(
                    self.get_capture_device_index(self.autosplit.settings_dict["capture_device_id"]))
            else:
                self.capture_device_combobox.setPlaceholderText("No device found.")
        except Exception as exception:   # pylint: disable=broad-except # We really want to catch everything here
            error = exception
            self.autosplit.show_error_signal.emit(lambda: error_messages.exception_traceback(error))

    def __init__(self):
        super().__init__()
        self.autosplit = find_autosplit_main_window()
        self.setupUi(self)
        # Spinbox frame disappears and reappears on Windows 11. It's much cleaner to just disable them.
        # Most likely related: https://bugreports.qt.io/browse/QTBUG-95215?jql=labels%20%3D%20Windows11
        # Arrow buttons tend to move a lot as well
        if WINDOWS_BUILD_NUMBER >= FIRST_WIN_11_BUILD:
            self.fps_limit_spinbox.setFrame(False)
            self.default_similarity_threshold_spinbox.setFrame(False)
            self.default_delay_time_spinbox.setFrame(False)
            self.default_pause_time_spinbox.setFrame(False)
        # Don't autofocus any particular field
        self.setFocus()

        self.custom_image_settings_info_label.setText(
            self.custom_image_settings_info_label
                .text()
                .format(GITHUB_REPOSITORY=GITHUB_REPOSITORY))

# region Build the Capture method combobox
        capture_method_values = CAPTURE_METHODS.values()
        self.__set_all_capture_devices()
        capture_list_items = [
            f"- {method.name} ({method.short_description})"
            for method in capture_method_values
        ]
        list_view = QtWidgets.QListView()
        list_view.setWordWrap(True)
        # HACK: The first time the dropdown is rendered, it does not have the right height
        # Assuming all options take 2 lines (except camera and BitBlt which have 1).
        # And all lines take 16 pixels
        # And all separators take 2 pixels
        doubled_len = 2 * len(capture_method_values) or 2
        list_view.setMinimumHeight((doubled_len - 2) * 16 + doubled_len)
        list_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.capture_method_combobox.setView(list_view)
        self.capture_method_combobox.addItems(capture_list_items)
        self.capture_method_combobox.setToolTip("\n\n".join([
            f"{method.name} :\n{method.description}"
            for method in capture_method_values]))
# endregion

        # Hotkeys initial values and bindings
        def hotkey_connect(hotkey: Hotkey):
            return lambda: set_hotkey(hotkey)
        for hotkey in HOTKEYS:
            hotkey_input: QtWidgets.QLineEdit = getattr(self, f"{hotkey}_input")
            set_hotkey_hotkey_button: QtWidgets.QPushButton = getattr(self, f"set_{hotkey}_hotkey_button")
            hotkey_input.setText(cast(str, self.autosplit.settings_dict[f"{hotkey}_hotkey"]))

            set_hotkey_hotkey_button.clicked.connect(hotkey_connect(hotkey))
            # Make it very clear that hotkeys are not used when auto-controlled
            if self.autosplit.is_auto_controlled and hotkey != "toggle_auto_reset_image":
                set_hotkey_hotkey_button.setEnabled(False)
                hotkey_input.setEnabled(False)

# region Set initial values
        # Capture Settings
        self.fps_limit_spinbox.setValue(self.autosplit.settings_dict["fps_limit"])
        self.live_capture_region_checkbox.setChecked(self.autosplit.settings_dict["live_capture_region"])
        self.capture_method_combobox.setCurrentIndex(
            CAPTURE_METHODS.get_index(self.autosplit.settings_dict["capture_method"]))

        # Image Settings
        self.default_comparison_method.setCurrentIndex(self.autosplit.settings_dict["default_comparison_method"])
        self.default_similarity_threshold_spinbox.setValue(self.autosplit.settings_dict["default_similarity_threshold"])
        self.default_delay_time_spinbox.setValue(self.autosplit.settings_dict["default_delay_time"])
        self.default_pause_time_spinbox.setValue(self.autosplit.settings_dict["default_pause_time"])
        self.loop_splits_checkbox.setChecked(self.autosplit.settings_dict["loop_splits"])
        self.enable_auto_reset_checkbox.setChecked(self.autosplit.settings_dict["enable_auto_reset"])
# endregion
# region Binding
        # Capture Settings
        self.fps_limit_spinbox.valueChanged.connect(lambda: self.__set_value(
            "fps_limit",
            self.fps_limit_spinbox.value()))
        self.live_capture_region_checkbox.stateChanged.connect(lambda: self.__set_value(
            "live_capture_region",
            self.live_capture_region_checkbox.isChecked()))
        self.capture_method_combobox.currentIndexChanged.connect(lambda: self.__set_value(
            "capture_method",
            self.__capture_method_changed()))
        self.capture_device_combobox.currentIndexChanged.connect(self.__capture_device_changed)

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
        self.enable_auto_reset_checkbox.stateChanged.connect(lambda: self.__set_value(
            "enable_auto_reset",
            self.enable_auto_reset_checkbox.isChecked()))
# endregion

        self.show()


def open_settings():
    autosplit = find_autosplit_main_window()
    if not autosplit.SettingsWidget or cast(QtWidgets.QDialog, autosplit.SettingsWidget).isHidden():
        autosplit.SettingsWidget = __SettingsWidget()
