from __future__ import annotations
from typing import TYPE_CHECKING, Any, TypedDict

if TYPE_CHECKING:
    from AutoSplit import AutoSplit

import os
import sys
import pickle

import keyboard  # https://github.com/boppreh/keyboard/issues/505
from win32 import win32gui
from PyQt6 import QtCore, QtWidgets

import error_messages
from capture_windows import Region
from gen import design
from hotkeys import set_hotkey

# Keyword "frozen" is for setting basedir while in onefile mode in pyinstaller
FROZEN = hasattr(sys, "frozen")
# Get the directory of either AutoSplit.exe or AutoSplit.py
auto_split_directory = os.path.dirname(sys.executable if FROZEN else os.path.abspath(__file__))


class SettingsDict(TypedDict):
    split_hotkey: str
    reset_hotkey: str
    undo_split_hotkey: str
    skip_split_hotkey: str
    pause_hotkey: str
    fps_limit: int
    live_capture_region: bool
    force_print_window: bool
    default_comparison_method: int
    default_similarity_threshold: float
    default_delay_time: int
    default_pause_time: float
    loop_splits: bool

    split_image_directory: str
    captured_window_title: str
    capture_region: Region


class RestrictedUnpickler(pickle.Unpickler):

    def find_class(self, module: str, name: str):
        raise pickle.UnpicklingError(f"'{module}.{name}' is forbidden")


def get_save_settings_values(autosplit: AutoSplit):
    return [
        autosplit.settings_dict["split_image_directory"],
        autosplit.settings_dict["default_similarity_threshold"],
        autosplit.settings_dict["default_comparison_method"],
        autosplit.settings_dict["default_pause_time"],
        autosplit.settings_dict["fps_limit"],
        autosplit.settings_dict["split_hotkey"],
        autosplit.settings_dict["reset_hotkey"],
        autosplit.settings_dict["skip_split_hotkey"],
        autosplit.settings_dict["undo_split_hotkey"],
        autosplit.settings_dict["pause_hotkey"],
        autosplit.settings_dict["capture_region"].x,
        autosplit.settings_dict["capture_region"].y,
        autosplit.settings_dict["capture_region"].width,
        autosplit.settings_dict["capture_region"].height,
        autosplit.settings_dict["captured_window_title"],
        0,
        0,
        1,
        autosplit.settings_dict["loop_splits"],
        0,
        autosplit.settings_dict["force_print_window"]]


def have_settings_changed(autosplit: AutoSplit):
    # One small caveat in this: if you load a settings file from an old version, but dont change settings,
    # the current save settings and last load settings will have different # of elements and it will ask
    # the user to save changes upon closing even though there were none
    return get_save_settings_values(autosplit) not in (autosplit.last_loaded_settings, autosplit.last_saved_settings)


def save_settings(autosplit: AutoSplit):
    """
    @return: The save settings filepath. Or None if "Save Settings As" is cancelled
    """
    if not autosplit.last_successfully_loaded_settings_file_path:
        return save_settings_as(autosplit)

    autosplit.last_saved_settings = get_save_settings_values(autosplit)
    # Save settings to a .pkl file
    with open(autosplit.last_successfully_loaded_settings_file_path, "wb") as file:
        pickle.dump(autosplit.last_saved_settings, file)
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
        or os.path.join(auto_split_directory, "settings.pkl"),
        "PKL (*.pkl)")[0]

    # If user cancels save destination window, don't save settings
    if not save_settings_file_path:
        return ""

    autosplit.last_saved_settings = get_save_settings_values(autosplit)

    # Save settings to a .pkl file
    with open(save_settings_file_path, "wb") as file:
        pickle.dump(autosplit.last_saved_settings, file)

    autosplit.last_successfully_loaded_settings_file_path = save_settings_file_path
    return save_settings_file_path


def __load_settings_from_file(autosplit: AutoSplit, load_settings_file_path: str):
    try:
        with open(load_settings_file_path, "rb") as file:
            settings: list[Any] = RestrictedUnpickler(file).load()
            settings_count = len(settings)
            if settings_count < 18:
                autosplit.show_error_signal.emit(error_messages.old_version_settings_file)
                return False
            # v1.3-1.4 settings. Add default pause_key and auto_start_on_reset_setting
            if settings_count == 18:
                settings.insert(9, "")
                settings.insert(20, 0)
            # v1.5 settings
            if settings_count == 20:
                settings.insert(21, False)
            # v1.6.X settings
            elif settings_count != 21:
                autosplit.show_error_signal.emit(error_messages.invalid_settings)
                return False
            autosplit.last_loaded_settings = settings
    except (FileNotFoundError, MemoryError, pickle.UnpicklingError):
        autosplit.show_error_signal.emit(error_messages.invalid_settings)
        return False

    autosplit.settings_dict["split_image_directory"] = settings[0]
    autosplit.split_image_folder_input.setText(settings[0])
    autosplit.settings_dict["default_similarity_threshold"] = settings[1]
    autosplit.settings_dict["default_comparison_method"] = settings[2]
    autosplit.settings_dict["default_pause_time"] = settings[3]
    autosplit.settings_dict["fps_limit"] = settings[4]
    keyboard.unhook_all()
    if not autosplit.is_auto_controlled:
        set_hotkey(autosplit, "split", settings[5])
        set_hotkey(autosplit, "reset", settings[6])
        set_hotkey(autosplit, "skip_split", settings[7])
        set_hotkey(autosplit, "undo_split", settings[8])
        set_hotkey(autosplit, "pause", settings[9])
    autosplit.x_spinbox.setValue(settings[10])
    autosplit.y_spinbox.setValue(settings[11])
    autosplit.width_spinbox.setValue(settings[12])
    autosplit.height_spinbox.setValue(settings[13])
    autosplit.settings_dict["captured_window_title"] = settings[14]
    autosplit.settings_dict["loop_splits"] = settings[18]
    autosplit.settings_dict["force_print_window"] = settings[20]

    if autosplit.settings_dict["captured_window_title"]:
        # https://github.com/kaluluosi/pywin32-stubs/issues/7
        hwnd = win32gui.FindWindow(None, autosplit.settings_dict["captured_window_title"])  # type: ignore
        if hwnd:
            autosplit.hwnd = hwnd
        else:
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
        "Load Settings",
        os.path.join(auto_split_directory, "settings.pkl"),
        "PKL (*.pkl)")[0]
    if not (load_settings_file_path and __load_settings_from_file(autosplit, load_settings_file_path)):
        return

    autosplit.last_successfully_loaded_settings_file_path = load_settings_file_path
    autosplit.load_start_image_signal.emit()


def load_settings_on_open(autosplit: AutoSplit):
    settings_files = [
        file for file
        in os.listdir(auto_split_directory)
        if file.endswith(".pkl")]

    # find all .pkls in AutoSplit folder, error if there is none or more than 1
    if len(settings_files) < 1:
        error_messages.no_settings_file_on_open()
        autosplit.last_loaded_settings = []
        return
    if len(settings_files) > 1:
        error_messages.too_many_settings_files_on_open()
        autosplit.last_loaded_settings = []
        return
    load_settings(autosplit, os.path.join(auto_split_directory, settings_files[0]))


def load_check_for_updates_on_open(autosplit: AutoSplit):
    """
    Retrieve the "Check For Updates On Open" QSettings and set the checkbox state
    These are only global settings values. They are not *pkl settings values.
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
