from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from AutoSplit import AutoSplit

import os
import sys
import pickle
import keyboard  # https://github.com/boppreh/keyboard/issues/505
from win32 import win32gui
from PyQt6 import QtCore, QtWidgets

import error_messages
from gen import design
from hotkeys import set_pause_hotkey, set_reset_hotkey, set_skip_split_hotkey, set_split_hotkey, set_undo_split_hotkey

# Keyword "frozen" is for setting basedir while in onefile mode in pyinstaller
FROZEN = hasattr(sys, "frozen")

# Get the directory of either AutoSplit.exe or AutoSplit.py
auto_split_directory = os.path.dirname(sys.executable if FROZEN else os.path.abspath(__file__))


class RestrictedUnpickler(pickle.Unpickler):

    def find_class(self, module: str, name: str):
        raise pickle.UnpicklingError(f"'{module}.{name}' is forbidden")


def load_pyqt_settings(autosplit: AutoSplit):
    # These are only global settings values. They are not *pkl settings values.
    autosplit.setting_check_for_updates_on_open = QtCore.QSettings("AutoSplit", "Check For Updates On Open")
    check_for_updates_on_open = autosplit.setting_check_for_updates_on_open.value(
        "check_for_updates_on_open",
        True,
        type=bool)
    autosplit.action_check_for_updates_on_open.setChecked(check_for_updates_on_open)


def get_save_settings_values(autosplit: AutoSplit):
    return [
        autosplit.split_image_directory,
        autosplit.similarity_threshold_spinbox.value(),
        autosplit.comparison_method_combobox.currentIndex(),
        autosplit.pause_spinbox.value(),
        int(autosplit.fps_limit_spinbox.value()),
        autosplit.split_input.text(),
        autosplit.reset_input.text(),
        autosplit.skip_split_input.text(),
        autosplit.undo_split_input.text(),
        autosplit.pause_hotkey_input.text(),
        autosplit.x_spinbox.value(),
        autosplit.y_spinbox.value(),
        autosplit.width_spinbox.value(),
        autosplit.height_spinbox.value(),
        win32gui.GetWindowText(autosplit.hwnd),
        0,
        0,
        int(autosplit.group_dummy_splits_checkbox.isChecked()),
        int(autosplit.loop_checkbox.isChecked()),
        int(autosplit.auto_start_on_reset_checkbox.isChecked()),
        autosplit.force_print_window_checkbox.isChecked()]


def have_settings_changed(autosplit: AutoSplit):
    # One small caveat in this: if you load a settings file from an old version, but dont change settings,
    # the current save settings and last load settings will have different # of elements and it will ask
    # the user to save changes upon closing even though there were none
    return get_save_settings_values(autosplit) not in (autosplit.last_loaded_settings, autosplit.last_saved_settings)


def save_settings(autosplit: AutoSplit):
    if not autosplit.last_successfully_loaded_settings_file_path:
        save_settings_as(autosplit)
    else:
        autosplit.last_saved_settings = get_save_settings_values(autosplit)
        # save settings to a .pkl file
        with open(autosplit.last_successfully_loaded_settings_file_path, "wb") as file:
            pickle.dump(autosplit.last_saved_settings, file)


def save_settings_as(autosplit: AutoSplit):
    # User picks save destination
    autosplit.save_settings_file_path = QtWidgets.QFileDialog.getSaveFileName(
        autosplit,
        "Save Settings As",
        os.path.join(auto_split_directory, "settings.pkl"),
        "PKL (*.pkl)")[0]

    # If user cancels save destination window, don't save settings
    if not autosplit.save_settings_file_path:
        return

    autosplit.last_saved_settings = get_save_settings_values(autosplit)

    # save settings to a .pkl file
    with open(autosplit.save_settings_file_path, "wb") as file:
        pickle.dump(autosplit.last_saved_settings, file)

    # Wording is kinda off here but this needs to be here for an edge case:
    # for when a file has never loaded, but you save file as successfully.
    autosplit.last_successfully_loaded_settings_file_path = autosplit.save_settings_file_path


def __load_settings_from_file(autosplit: AutoSplit):
    try:
        with open(autosplit.load_settings_file_path, "rb") as file:
            settings: list[Any] = RestrictedUnpickler(file).load()
            settings_count = len(settings)
            if settings_count < 18:
                autosplit.show_error_signal.emit(error_messages.old_version_settings_file)
                return
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
                return
            autosplit.last_loaded_settings = settings
    except (FileNotFoundError, MemoryError, pickle.UnpicklingError):
        autosplit.show_error_signal.emit(error_messages.invalid_settings)
        return

    autosplit.split_image_directory = settings[0]
    autosplit.split_image_folder_input.setText(settings[0])
    autosplit.similarity_threshold_spinbox.setValue(settings[1])
    autosplit.comparison_method_combobox.setCurrentIndex(settings[2])
    autosplit.pause_spinbox.setValue(settings[3])
    autosplit.fps_limit_spinbox.setValue(settings[4])
    autosplit.split_input.setText(settings[5])
    autosplit.reset_input.setText(settings[6])
    autosplit.skip_split_input.setText(settings[7])
    autosplit.undo_split_input.setText(settings[8])
    autosplit.pause_hotkey_input.setText(settings[9])
    autosplit.x_spinbox.setValue(settings[10])
    autosplit.y_spinbox.setValue(settings[11])
    autosplit.width_spinbox.setValue(settings[12])
    autosplit.height_spinbox.setValue(settings[13])
    # https://github.com/kaluluosi/pywin32-stubs/issues/7
    autosplit.hwnd = win32gui.FindWindow(None, settings[14])  # type: ignore
    autosplit.group_dummy_splits_checkbox.setChecked(bool(settings[17]))
    autosplit.loop_checkbox.setChecked(bool(settings[18]))
    autosplit.auto_start_on_reset_checkbox.setChecked(bool(settings[19]))
    autosplit.force_print_window_checkbox.setChecked(settings[20])

    keyboard.unhook_all()
    if not autosplit.is_auto_controlled:
        set_split_hotkey(autosplit, settings[5])
        set_reset_hotkey(autosplit, settings[6])
        set_skip_split_hotkey(autosplit, settings[7])
        set_undo_split_hotkey(autosplit, settings[8])
        set_pause_hotkey(autosplit, settings[9])


def load_settings(
    autosplit: AutoSplit,
    load_settings_on_open: bool = False,
    load_settings_from_livesplit: bool = False
):
    if load_settings_on_open:
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
        autosplit.load_settings_file_path = os.path.join(auto_split_directory, settings_files[0])

    elif not load_settings_on_open and not load_settings_from_livesplit:
        autosplit.load_settings_file_path = QtWidgets.QFileDialog.getOpenFileName(
            autosplit,
            "Load Settings",
            os.path.join(auto_split_directory, "settings.pkl"),
            "PKL (*.pkl)")[0]
        if not autosplit.load_settings_file_path:
            return

    __load_settings_from_file(autosplit)

    autosplit.last_successfully_loaded_settings_file_path = autosplit.load_settings_file_path
    autosplit.check_live_image()
    autosplit.load_start_image()


def load_check_for_updates_on_open(design_window: design.Ui_MainWindow):
    """
    Retrieve the "Check For Updates On Open" QSettings and set the checkbox state
    These are only global settings values. They are not *pkl settings values.
    """

    value = QtCore \
        .QSettings("AutoSplit", "Check For Updates On Open") \
        .value("check_for_updates_on_open", True, type=bool)
    design_window.action_check_for_updates_on_open.setChecked(value)


def set_check_for_updates_on_open(design_window: design.Ui_MainWindow, value: bool):
    """
    Sets the "Check For Updates On Open" QSettings value and the checkbox state
    """

    design_window.action_check_for_updates_on_open.setChecked(value)
    QtCore \
        .QSettings("AutoSplit", "Check For Updates On Open") \
        .setValue("check_for_updates_on_open", value)
