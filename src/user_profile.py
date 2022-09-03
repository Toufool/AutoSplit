from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING, TypedDict, cast

import keyboard
import toml
from PyQt6 import QtCore, QtWidgets

import error_messages
from capture_method import CAPTURE_METHODS, CaptureMethodEnum, Region, change_capture_method
from gen import design
from hotkeys import set_hotkey

if TYPE_CHECKING:
    from AutoSplit import AutoSplit
# Keyword "frozen" is for setting basedir while in onefile mode in pyinstaller
FROZEN = hasattr(sys, "frozen")
# Get the directory of either AutoSplit.exe or AutoSplit.py
auto_split_directory = os.path.dirname(sys.executable if FROZEN else os.path.abspath(__file__))


class UserProfileDict(TypedDict):
    split_hotkey: str
    reset_hotkey: str
    undo_split_hotkey: str
    skip_split_hotkey: str
    pause_hotkey: str
    fps_limit: int
    live_capture_region: bool
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


DEFAULT_PROFILE = UserProfileDict(
    split_hotkey="",
    reset_hotkey="",
    undo_split_hotkey="",
    skip_split_hotkey="",
    pause_hotkey="",
    fps_limit=60,
    live_capture_region=True,
    capture_method=CAPTURE_METHODS.get_method_by_index(0),
    capture_device_id=0,
    capture_device_name="",
    default_comparison_method=0,
    default_similarity_threshold=0.95,
    default_delay_time=0,
    default_pause_time=10,
    loop_splits=False,
    split_image_directory="",
    captured_window_title="",
    capture_region=Region(x=0, y=0, width=1, height=1),
)


def have_settings_changed(autosplit: AutoSplit):
    return autosplit.settings_dict not in (autosplit.last_loaded_settings, autosplit.last_saved_settings)


def save_settings(autosplit: AutoSplit):
    """
    @return: The save settings filepath. Or None if "Save Settings As" is cancelled
    """
    if not autosplit.last_successfully_loaded_settings_file_path:
        return save_settings_as(autosplit)

    autosplit.last_saved_settings = autosplit.settings_dict
    # Save settings to a .toml file
    with open(autosplit.last_successfully_loaded_settings_file_path, "w", encoding="utf-8") as file:
        toml.dump(autosplit.last_saved_settings, file)
    return autosplit.last_successfully_loaded_settings_file_path


def save_settings_as(autosplit: AutoSplit):
    """
    @return: The save settings filepath selected. Empty if cancelled
    """
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
                **DEFAULT_PROFILE,
                **toml.load(file),
            })
            # TODO: Data Validation / fallbacks ?
            autosplit.settings_dict = UserProfileDict(**loaded_settings)
            autosplit.last_loaded_settings = autosplit.settings_dict

            autosplit.x_spinbox.setValue(autosplit.settings_dict["capture_region"]["x"])
            autosplit.y_spinbox.setValue(autosplit.settings_dict["capture_region"]["y"])
            autosplit.width_spinbox.setValue(autosplit.settings_dict["capture_region"]["width"])
            autosplit.height_spinbox.setValue(autosplit.settings_dict["capture_region"]["height"])
    except (FileNotFoundError, MemoryError, TypeError, toml.TomlDecodeError):
        autosplit.show_error_signal.emit(error_messages.invalid_settings)
        return False

    autosplit.split_image_folder_input.setText(autosplit.settings_dict["split_image_directory"])
    keyboard.unhook_all()
    if not autosplit.is_auto_controlled:
        if autosplit.settings_dict["split_hotkey"]:
            set_hotkey(autosplit, "split", autosplit.settings_dict["split_hotkey"])
        if autosplit.settings_dict["reset_hotkey"]:
            set_hotkey(autosplit, "reset", autosplit.settings_dict["reset_hotkey"])
        if autosplit.settings_dict["skip_split_hotkey"]:
            set_hotkey(autosplit, "skip_split", autosplit.settings_dict["skip_split_hotkey"])
        if autosplit.settings_dict["undo_split_hotkey"]:
            set_hotkey(autosplit, "undo_split", autosplit.settings_dict["undo_split_hotkey"])
        if autosplit.settings_dict["pause_hotkey"]:
            set_hotkey(autosplit, "pause", autosplit.settings_dict["pause_hotkey"])

    change_capture_method(cast(CaptureMethodEnum, autosplit.settings_dict["capture_method"]), autosplit)
    autosplit.capture_method.recover_window(autosplit.settings_dict["captured_window_title"], autosplit)
    if not autosplit.capture_method.check_selected_region_exists(autosplit):
        autosplit.live_image.setText("Reload settings after opening"
                                     + f'\n"{autosplit.settings_dict["captured_window_title"]}"'
                                     + "\nto automatically load Capture Region")

    return True


def load_settings(
    autosplit: AutoSplit,
    from_path: str = ""
):
    load_settings_file_path = from_path or QtWidgets.QFileDialog.getOpenFileName(
        autosplit,
        "Load Profile",
        os.path.join(auto_split_directory, "settings.toml"),
        "TOML (*.toml)")[0]
    if not (load_settings_file_path and __load_settings_from_file(autosplit, load_settings_file_path)):
        return

    autosplit.last_successfully_loaded_settings_file_path = load_settings_file_path
    autosplit.load_start_image_signal.emit()


def load_settings_on_open(autosplit: AutoSplit):
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
        change_capture_method(CAPTURE_METHODS.get_method_by_index(0), autosplit)
        error()
        return

    load_settings(autosplit, os.path.join(auto_split_directory, settings_files[0]))


def load_check_for_updates_on_open(autosplit: AutoSplit):
    """
    Retrieve the "Check For Updates On Open" QSettings and set the checkbox state
    These are only global settings values. They are not *toml settings values.
    """
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
