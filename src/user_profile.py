from __future__ import annotations

import os
from typing import TYPE_CHECKING, TypedDict, cast

import toml
from PyQt6 import QtCore, QtWidgets

import error_messages
from capture_method import CAPTURE_METHODS, CaptureMethodEnum, Region, change_capture_method
from gen import design, settings as settings_ui
from hotkeys import HOTKEYS, remove_all_hotkeys, set_hotkey
from utils import auto_split_directory, find_autosplit_main_window

if TYPE_CHECKING:
    from AutoSplit import AutoSplit


class UserProfileDict(TypedDict):
    split_hotkey: str
    reset_hotkey: str
    undo_split_hotkey: str
    skip_split_hotkey: str
    pause_hotkey: str
    toggle_auto_reset_image_hotkey: str
    fps_limit: int
    live_capture_region: bool
    enable_auto_reset: bool
    capture_method: str | CaptureMethodEnum
    capture_device_id: int
    capture_device_name: str
    default_comparison_method: int
    default_similarity_threshold: float
    default_delay_time: int
    default_pause_time: float
    loop_splits: bool
    split_image_directory: str
    captured_window_title: str
    capture_region: Region


def get_default_settings_from_ui():
    autosplit = find_autosplit_main_window()
    temp_dialog = QtWidgets.QDialog()
    default_settings_dialog = settings_ui.Ui_DialogSettings()
    default_settings_dialog.setupUi(temp_dialog)
    default_settings: UserProfileDict = {
        "split_hotkey": default_settings_dialog.split_input.text(),
        "reset_hotkey": default_settings_dialog.reset_input.text(),
        "undo_split_hotkey": default_settings_dialog.undo_split_input.text(),
        "skip_split_hotkey": default_settings_dialog.skip_split_input.text(),
        "pause_hotkey": default_settings_dialog.pause_input.text(),
        "toggle_auto_reset_image_hotkey": default_settings_dialog.toggle_auto_reset_image_input.text(),
        "fps_limit": default_settings_dialog.fps_limit_spinbox.value(),
        "live_capture_region": default_settings_dialog.live_capture_region_checkbox.isChecked(),
        "enable_auto_reset": default_settings_dialog.enable_auto_reset_checkbox.isChecked(),
        "capture_method": CAPTURE_METHODS.get_method_by_index(
            default_settings_dialog.capture_method_combobox.currentIndex()),
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
        }}
    del temp_dialog
    return default_settings


def have_settings_changed():
    autosplit = find_autosplit_main_window()
    return autosplit.settings_dict not in (autosplit.last_loaded_settings, autosplit.last_saved_settings)


def save_settings():
    """
    @return: The save settings filepath. Or None if "Save Settings As" is cancelled
    """
    autosplit = find_autosplit_main_window()
    return __save_settings_to_file(autosplit, autosplit.last_successfully_loaded_settings_file_path) \
        if autosplit.last_successfully_loaded_settings_file_path \
        else save_settings_as()


def save_settings_as():
    """
    @return: The save settings filepath selected. Empty if cancelled
    """
    autosplit = find_autosplit_main_window()

    # User picks save destination
    save_settings_file_path = QtWidgets.QFileDialog.getSaveFileName(
        autosplit,
        "Save Settings As",
        autosplit.last_successfully_loaded_settings_file_path
        or os.path.join(auto_split_directory, "settings.toml"),
        "TOML (*.toml)")[0]

    # If user cancels save destination window, don't save settings
    if not save_settings_file_path:
        return ""

    return __save_settings_to_file(autosplit, save_settings_file_path)


def __save_settings_to_file(autosplit: AutoSplit, save_settings_file_path: str):
    autosplit.last_saved_settings = autosplit.settings_dict
    # Save settings to a .toml file
    with open(save_settings_file_path, "w", encoding="utf-8") as file:
        toml.dump(autosplit.last_saved_settings, file)
    autosplit.last_successfully_loaded_settings_file_path = save_settings_file_path
    return save_settings_file_path


def __load_settings_from_file(autosplit: AutoSplit, load_settings_file_path: str):
    if load_settings_file_path.endswith(".pkl"):
        autosplit.show_error_signal.emit(error_messages.old_version_settings_file)
        return False
    try:
        with open(load_settings_file_path, "r", encoding="utf-8") as file:
            # Casting here just so we can build an actual UserProfileDict once we're done validating
            # Fallback to default settings if some are missing from the file. This happens when new settings are added.
            loaded_settings = cast(UserProfileDict, {
                **autosplit.DEFAULT_PROFILE,
                **toml.load(file),
            })
            # TODO: Data Validation / fallbacks ?
            autosplit.settings_dict = UserProfileDict(**loaded_settings)
            autosplit.last_loaded_settings = autosplit.settings_dict

            autosplit.x_spinbox.setValue(autosplit.settings_dict["capture_region"]["x"])
            autosplit.y_spinbox.setValue(autosplit.settings_dict["capture_region"]["y"])
            autosplit.width_spinbox.setValue(autosplit.settings_dict["capture_region"]["width"])
            autosplit.height_spinbox.setValue(autosplit.settings_dict["capture_region"]["height"])
            autosplit.split_image_folder_input.setText(autosplit.settings_dict["split_image_directory"])
    except (FileNotFoundError, MemoryError, TypeError, toml.TomlDecodeError):
        autosplit.show_error_signal.emit(error_messages.invalid_settings)
        return False

    remove_all_hotkeys()
    if not autosplit.is_auto_controlled:
        for hotkey, hotkey_name in [(hotkey, f"{hotkey}_hotkey") for hotkey in HOTKEYS]:
            if autosplit.settings_dict[hotkey_name]:
                set_hotkey(hotkey, cast(str, autosplit.settings_dict[hotkey_name]))

    change_capture_method(cast(CaptureMethodEnum, autosplit.settings_dict["capture_method"]))
    autosplit.capture_method.recover_window(autosplit.settings_dict["captured_window_title"])
    if not autosplit.capture_method.check_selected_region_exists():
        autosplit.live_image.setText("Reload settings after opening"
                                     + f'\n"{autosplit.settings_dict["captured_window_title"]}"'
                                     + "\nto automatically load Capture Region")

    return True


def load_settings(from_path: str = ""):
    autosplit = find_autosplit_main_window()
    load_settings_file_path = from_path or QtWidgets.QFileDialog.getOpenFileName(
        autosplit,
        "Load Profile",
        os.path.join(auto_split_directory, "settings.toml"),
        "TOML (*.toml)")[0]
    if not (load_settings_file_path and __load_settings_from_file(autosplit, load_settings_file_path)):
        return

    autosplit.last_successfully_loaded_settings_file_path = load_settings_file_path
    autosplit.load_start_image_signal.emit()


def load_settings_on_open():
    settings_files = [
        file for file
        in os.listdir(auto_split_directory)
        if file.endswith(".toml")]

    # Find all .tomls in AutoSplit folder, error if there is not exactly 1
    error = None
    if len(settings_files) < 1:
        error = error_messages.no_settings_file_on_open
    elif len(settings_files) > 1:
        error = error_messages.too_many_settings_files_on_open
    if error:
        change_capture_method(CAPTURE_METHODS.get_method_by_index(0))
        error()
        return

    load_settings(os.path.join(auto_split_directory, settings_files[0]))


def load_check_for_updates_on_open():
    """
    Retrieve the "Check For Updates On Open" QSettings and set the checkbox state
    These are only global settings values. They are not *toml settings values.
    """
    autosplit = find_autosplit_main_window()
    value = QtCore \
        .QSettings("AutoSplit", "Check For Updates On Open") \
        .value("check_for_updates_on_open", True, type=bool)
    autosplit.action_check_for_updates_on_open.setChecked(value)


def set_check_for_updates_on_open(design_window: design.Ui_MainWindow, value: bool):
    """
    Sets the "Check For Updates On Open" QSettings value and the checkbox state
    """

    design_window.action_check_for_updates_on_open.setChecked(value)
    QtCore \
        .QSettings("AutoSplit", "Check For Updates On Open") \
        .setValue("check_for_updates_on_open", value)
