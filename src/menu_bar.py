from __future__ import annotations

import asyncio
import webbrowser
from typing import TYPE_CHECKING, Any, cast

import requests
from packaging.version import parse as version_parse
from PySide6 import QtCore, QtWidgets
from requests.exceptions import RequestException
from typing_extensions import override

import error_messages
import user_profile
from capture_method import (
    CAPTURE_METHODS,
    CameraInfo,
    CaptureMethodEnum,
    change_capture_method,
    get_all_video_capture_devices,
)
from gen import about, design, settings as settings_ui, update_checker
from hotkeys import HOTKEYS, Hotkey, set_hotkey
from utils import AUTOSPLIT_VERSION, GITHUB_REPOSITORY, decimal, fire_and_forget

if TYPE_CHECKING:
    from AutoSplit import AutoSplit


class __AboutWidget(QtWidgets.QWidget, about.Ui_AboutAutoSplitWidget):  # noqa: N801 # Private class
    """About Window."""

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.created_by_label.setOpenExternalLinks(True)
        self.donate_button_label.setOpenExternalLinks(True)
        self.version_label.setText(f"Version: {AUTOSPLIT_VERSION}")
        self.show()


def open_about(autosplit: AutoSplit):
    if not autosplit.AboutWidget or cast(QtWidgets.QWidget, autosplit.AboutWidget).isHidden():
        autosplit.AboutWidget = __AboutWidget()


class __UpdateCheckerWidget(QtWidgets.QWidget, update_checker.Ui_UpdateChecker):  # noqa: N801 # Private class
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
            self.do_not_ask_again_checkbox.isChecked(),
        )


def open_update_checker(autosplit: AutoSplit, latest_version: str, check_on_open: bool):
    if not autosplit.UpdateCheckerWidget or cast(QtWidgets.QWidget, autosplit.UpdateCheckerWidget).isHidden():
        autosplit.UpdateCheckerWidget = __UpdateCheckerWidget(latest_version, autosplit, check_on_open)


def view_help():
    webbrowser.open(f"https://github.com/{GITHUB_REPOSITORY}#tutorial")


class __CheckForUpdatesThread(QtCore.QThread):  # noqa: N801 # Private class
    def __init__(self, autosplit: AutoSplit, check_on_open: bool):
        super().__init__()
        self.autosplit = autosplit
        self.check_on_open = check_on_open

    @override
    def run(self):
        try:
            response = requests.get(f"https://api.github.com/repos/{GITHUB_REPOSITORY}/releases/latest", timeout=30)
            latest_version = str(response.json()["name"]).split("v")[1]
            self.autosplit.update_checker_widget_signal.emit(latest_version, self.check_on_open)
        except (RequestException, KeyError):
            if not self.check_on_open:
                self.autosplit.show_error_signal.emit(error_messages.check_for_updates)


def about_qt():
    webbrowser.open("https://wiki.qt.io/About_Qt")


def about_qt_for_python():
    webbrowser.open("https://wiki.qt.io/Qt_for_Python")


def check_for_updates(autosplit: AutoSplit, check_on_open: bool = False):
    autosplit.CheckForUpdatesThread = __CheckForUpdatesThread(autosplit, check_on_open)
    autosplit.CheckForUpdatesThread.start()


class __SettingsWidget(QtWidgets.QWidget, settings_ui.Ui_SettingsWidget):  # noqa: N801 # Private class
    __video_capture_devices: list[CameraInfo] = []
    """
    Used to temporarily store the existing cameras,
    we don't want to call `get_all_video_capture_devices` agains and possibly have a different result
    """

    def __update_default_threshold(self, value: Any):
        self.__set_value("default_similarity_threshold", value)
        self.autosplit.table_current_image_threshold_label.setText(
            decimal(self.autosplit.split_image.get_similarity_threshold(self.autosplit))
            if self.autosplit.split_image
            else "-",
        )
        self.autosplit.table_reset_image_threshold_label.setText(
            decimal(self.autosplit.reset_image.get_similarity_threshold(self.autosplit))
            if self.autosplit.reset_image
            else "-",
        )

    def __set_value(self, key: str, value: Any):
        self.autosplit.settings_dict[key] = value

    def get_capture_device_index(self, capture_device_id: int):
        """Returns 0 if the capture_device_id is invalid."""
        try:
            return [device.device_id for device in self.__video_capture_devices].index(capture_device_id)
        except ValueError:
            return 0

    def __enable_capture_device_if_its_selected_method(
            self, selected_capture_method: str | CaptureMethodEnum | None = None,
    ):
        if selected_capture_method is None:
            selected_capture_method = self.autosplit.settings_dict["capture_method"]
        is_video_capture_device = selected_capture_method == CaptureMethodEnum.VIDEO_CAPTURE_DEVICE
        self.capture_device_combobox.setEnabled(is_video_capture_device)
        if is_video_capture_device:
            self.capture_device_combobox.setCurrentIndex(
                self.get_capture_device_index(self.autosplit.settings_dict["capture_device_id"]),
            )
        else:
            self.capture_device_combobox.setPlaceholderText('Select "Video Capture Device" above')
            self.capture_device_combobox.setCurrentIndex(-1)

    def __capture_method_changed(self):
        selected_capture_method = CAPTURE_METHODS.get_method_by_index(self.capture_method_combobox.currentIndex())
        self.__enable_capture_device_if_its_selected_method(selected_capture_method)
        change_capture_method(selected_capture_method, self.autosplit)
        return selected_capture_method

    def __capture_device_changed(self):
        device_index = self.capture_device_combobox.currentIndex()
        if device_index == -1:
            return
        capture_device = self.__video_capture_devices[device_index]
        self.autosplit.settings_dict["capture_device_name"] = capture_device.name
        self.autosplit.settings_dict["capture_device_id"] = capture_device.device_id
        if self.autosplit.settings_dict["capture_method"] == CaptureMethodEnum.VIDEO_CAPTURE_DEVICE:
            # Re-initializes the VideoCaptureDeviceCaptureMethod
            change_capture_method(CaptureMethodEnum.VIDEO_CAPTURE_DEVICE, self.autosplit)

    def __fps_limit_changed(self, value: int):
        value = self.fps_limit_spinbox.value()
        self.autosplit.settings_dict["fps_limit"] = value
        self.autosplit.timer_live_image.setInterval(int(1000 / value))
        self.autosplit.timer_live_image.setInterval(int(1000 / value))

    @fire_and_forget
    def __set_all_capture_devices(self):
        self.__video_capture_devices = asyncio.run(get_all_video_capture_devices())
        if len(self.__video_capture_devices) > 0:
            for i in range(self.capture_device_combobox.count()):
                self.capture_device_combobox.removeItem(i)
            self.capture_device_combobox.addItems([
                f"* {device.name}"
                + (f" [{device.backend}]" if device.backend else "")
                + (" (occupied)" if device.occupied else "")
                for device in self.__video_capture_devices
            ])
            self.__enable_capture_device_if_its_selected_method()
        else:
            self.capture_device_combobox.setPlaceholderText("No device found.")

    def __set_readme_link(self):
        self.custom_image_settings_info_label.setText(
            self.custom_image_settings_info_label
                .text()
                .format(GITHUB_REPOSITORY=GITHUB_REPOSITORY),
        )
        # HACK: This is a workaround because custom_image_settings_info_label
        # simply will not open links with a left click no matter what we tried.
        self.readme_link_button.clicked.connect(
            lambda: webbrowser.open(f"https://github.com/{GITHUB_REPOSITORY}#readme"),
        )
        self.readme_link_button.setStyleSheet("border: 0px; background-color:rgba(0,0,0,0%);")

    def __init__(self, autosplit: AutoSplit):
        super().__init__()
        self.setupUi(self)
        self.autosplit = autosplit
        self.__set_readme_link()
        # Don't autofocus any particular field
        self.setFocus()


# region Build the Capture method combobox
        capture_method_values = CAPTURE_METHODS.values()
        self.__set_all_capture_devices()

        # TODO: Word-wrapping works, but there's lots of extra padding to the right. Raise issue upstream
        # list_view = QtWidgets.QListView()
        # list_view.setWordWrap(True)
        # list_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # list_view.setFixedWidth(self.capture_method_combobox.width())
        # self.capture_method_combobox.setView(list_view)

        self.capture_method_combobox.addItems([
            f"- {method.name} ({method.short_description})"
            for method in capture_method_values
        ])
        self.capture_method_combobox.setToolTip(
            "\n\n".join([
                f"{method.name} :\n{method.description}"
                for method in capture_method_values
            ]),
        )
# endregion

        # Hotkey initial values and bindings
        def hotkey_connect(hotkey: Hotkey):
            return lambda: set_hotkey(self.autosplit, hotkey)
        for hotkey in HOTKEYS:
            hotkey_input: QtWidgets.QLineEdit = getattr(self, f"{hotkey}_input")
            set_hotkey_hotkey_button: QtWidgets.QPushButton = getattr(self, f"set_{hotkey}_hotkey_button")
            hotkey_input.setText(
                cast(
                    str,
                    autosplit.settings_dict[f"{hotkey}_hotkey"],  # pyright: ignore[reportGeneralTypeIssues]
                ),
            )

            set_hotkey_hotkey_button.clicked.connect(hotkey_connect(hotkey))
            # Make it very clear that hotkeys are not used when auto-controlled
            if autosplit.is_auto_controlled and hotkey != "toggle_auto_reset_image":
                set_hotkey_hotkey_button.setEnabled(False)
                hotkey_input.setEnabled(False)

# region Set initial values
        # Capture Settings
        self.fps_limit_spinbox.setValue(autosplit.settings_dict["fps_limit"])
        self.live_capture_region_checkbox.setChecked(autosplit.settings_dict["live_capture_region"])
        self.capture_method_combobox.setCurrentIndex(
            CAPTURE_METHODS.get_index(autosplit.settings_dict["capture_method"]),
        )
        # No self.capture_device_combobox.setCurrentIndex
        # It'll set itself asynchronously in self.__set_all_capture_devices()

        # Image Settings
        self.default_comparison_method.setCurrentIndex(autosplit.settings_dict["default_comparison_method"])
        self.default_similarity_threshold_spinbox.setValue(autosplit.settings_dict["default_similarity_threshold"])
        self.default_delay_time_spinbox.setValue(autosplit.settings_dict["default_delay_time"])
        self.default_pause_time_spinbox.setValue(autosplit.settings_dict["default_pause_time"])
        self.loop_splits_checkbox.setChecked(autosplit.settings_dict["loop_splits"])
        self.enable_auto_reset_image_checkbox.setChecked(autosplit.settings_dict["enable_auto_reset"])
# endregion
# region Binding
        # Capture Settings
        self.fps_limit_spinbox.valueChanged.connect(self.__fps_limit_changed)
        self.live_capture_region_checkbox.stateChanged.connect(
            lambda: self.__set_value("live_capture_region", self.live_capture_region_checkbox.isChecked()),
        )
        self.capture_method_combobox.currentIndexChanged.connect(
            lambda: self.__set_value("capture_method", self.__capture_method_changed()),
        )
        self.capture_device_combobox.currentIndexChanged.connect(self.__capture_device_changed)

        # Image Settings
        self.default_comparison_method.currentIndexChanged.connect(
            lambda: self.__set_value("default_comparison_method", self.default_comparison_method.currentIndex()),
        )
        self.default_similarity_threshold_spinbox.valueChanged.connect(
            lambda: self.__update_default_threshold(self.default_similarity_threshold_spinbox.value()),
        )
        self.default_delay_time_spinbox.valueChanged.connect(
            lambda: self.__set_value("default_delay_time", self.default_delay_time_spinbox.value()),
        )
        self.default_pause_time_spinbox.valueChanged.connect(
            lambda: self.__set_value("default_pause_time", self.default_pause_time_spinbox.value()),
        )
        self.loop_splits_checkbox.stateChanged.connect(
            lambda: self.__set_value("loop_splits", self.loop_splits_checkbox.isChecked()),
        )
        self.enable_auto_reset_image_checkbox.stateChanged.connect(
            lambda: self.__set_value("enable_auto_reset", self.enable_auto_reset_image_checkbox.isChecked()),
        )
# endregion

        self.show()


def open_settings(autosplit: AutoSplit):
    if not autosplit.SettingsWidget or cast(QtWidgets.QWidget, autosplit.SettingsWidget).isHidden():
        autosplit.SettingsWidget = __SettingsWidget(autosplit)


def get_default_settings_from_ui(autosplit: AutoSplit):
    temp_dialog = QtWidgets.QWidget()
    default_settings_dialog = settings_ui.Ui_SettingsWidget()
    default_settings_dialog.setupUi(temp_dialog)
    default_settings: user_profile.UserProfileDict = {
        "split_hotkey": default_settings_dialog.split_input.text(),
        "reset_hotkey": default_settings_dialog.reset_input.text(),
        "undo_split_hotkey": default_settings_dialog.undo_split_input.text(),
        "skip_split_hotkey": default_settings_dialog.skip_split_input.text(),
        "pause_hotkey": default_settings_dialog.pause_input.text(),
        "toggle_auto_reset_image_hotkey": default_settings_dialog.toggle_auto_reset_image_input.text(),
        "fps_limit": default_settings_dialog.fps_limit_spinbox.value(),
        "live_capture_region": default_settings_dialog.live_capture_region_checkbox.isChecked(),
        "enable_auto_reset": default_settings_dialog.enable_auto_reset_image_checkbox.isChecked(),
        "capture_method": CAPTURE_METHODS.get_method_by_index(
            default_settings_dialog.capture_method_combobox.currentIndex(),
        ),
        "capture_device_id": default_settings_dialog.capture_device_combobox.currentIndex(),
        "capture_device_name": "",
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
        },
    }
    del temp_dialog
    return default_settings
