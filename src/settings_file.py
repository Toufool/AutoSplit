from __future__ import annotations
from typing import TYPE_CHECKING, Any, Literal, cast
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
# TODO with settings refactoring
from hotkeys import _hotkey_action  # type: ignore

# Keyword "frozen" is for setting basedir while in onefile mode in pyinstaller
FROZEN = hasattr(sys, "frozen")

# Get the directory of either AutoSplit.exe or AutoSplit.py
auto_split_directory = os.path.dirname(sys.executable if FROZEN else os.path.abspath(__file__))


class RestrictedUnpickler(pickle.Unpickler):

    def find_class(self, module: str, name: str):
        raise pickle.UnpicklingError(f"'{module}.{name}' is forbidden")


def load_pyqt_settings(autosplit: AutoSplit):
    # These are only global settings values. They are not *pkl settings values.
    autosplit.get_global_settings_values()
    check_for_updates_on_open = autosplit.setting_check_for_updates_on_open.value(
        "check_for_updates_on_open",
        True,
        type=bool)
    autosplit.action_check_for_updates_on_open.setChecked(check_for_updates_on_open)


def get_save_settings_values(autosplit: AutoSplit):
    # get values to be able to save settings
    autosplit.similarity_threshold = autosplit.similarity_threshold_spinbox.value()
    autosplit.comparison_index = autosplit.comparison_method_combobox.currentIndex()
    autosplit.pause = autosplit.pause_spinbox.value()
    autosplit.fps_limit = int(autosplit.fps_limit_spinbox.value())
    autosplit.split_key = autosplit.split_input.text()
    autosplit.reset_key = autosplit.reset_input.text()
    autosplit.skip_split_key = autosplit.skip_split_input.text()
    autosplit.undo_split_key = autosplit.undo_split_input.text()
    autosplit.pause_key = autosplit.pause_hotkey_input.text()
    autosplit.group_dummy_splits_undo_skip_setting = cast(
        Literal[0, 1],
        int(autosplit.group_dummy_splits_checkbox.isChecked()))
    autosplit.loop_setting = cast(
        Literal[0, 1],
        int(autosplit.loop_checkbox.isChecked()))
    autosplit.auto_start_on_reset_setting = cast(
        Literal[0, 1],
        int(autosplit.auto_start_on_reset_checkbox.isChecked()))


def have_settings_changed(autosplit: AutoSplit):
    get_save_settings_values(autosplit)
    current_save_settings = [
        autosplit.split_image_directory,
        autosplit.similarity_threshold,
        autosplit.comparison_index,
        autosplit.pause,
        autosplit.fps_limit,
        autosplit.split_key,
        autosplit.reset_key,
        autosplit.skip_split_key,
        autosplit.undo_split_key,
        autosplit.pause_key,
        autosplit.x_spinbox.value(),
        autosplit.y_spinbox.value(),
        autosplit.width_spinbox.value(),
        autosplit.height_spinbox.value(),
        autosplit.hwnd_title,
        0,
        0,
        autosplit.group_dummy_splits_undo_skip_setting,
        autosplit.loop_setting,
        autosplit.auto_start_on_reset_setting,
        autosplit.force_print_window_checkbox.isChecked()]

    # One small caveat in this: if you load a settings file from an old version, but dont change settings,
    # the current save settings and last load settings will have different # of elements and it will ask
    # the user to save changes upon closing even though there were none
    return current_save_settings not in (autosplit.last_loaded_settings, autosplit.last_saved_settings)


def save_settings(autosplit: AutoSplit):
    if not autosplit.last_successfully_loaded_settings_file_path:
        save_settings_as(autosplit)
    else:
        get_save_settings_values(autosplit)
        autosplit.last_saved_settings = [
            autosplit.split_image_directory,
            autosplit.similarity_threshold,
            autosplit.comparison_index,
            autosplit.pause,
            autosplit.fps_limit,
            autosplit.split_key,
            autosplit.reset_key,
            autosplit.skip_split_key,
            autosplit.undo_split_key,
            autosplit.pause_key,
            autosplit.x_spinbox.value(),
            autosplit.y_spinbox.value(),
            autosplit.width_spinbox.value(),
            autosplit.height_spinbox.value(),
            autosplit.hwnd_title,
            0,
            0,
            autosplit.group_dummy_splits_undo_skip_setting,
            autosplit.loop_setting,
            autosplit.auto_start_on_reset_setting,
            autosplit.force_print_window_checkbox.isChecked()]
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

    get_save_settings_values(autosplit)
    autosplit.last_saved_settings = [
        autosplit.split_image_directory,
        autosplit.similarity_threshold,
        autosplit.comparison_index,
        autosplit.pause,
        autosplit.fps_limit,
        autosplit.split_key,
        autosplit.reset_key,
        autosplit.skip_split_key,
        autosplit.undo_split_key,
        autosplit.pause_key,
        autosplit.x_spinbox.value(),
        autosplit.y_spinbox.value(),
        autosplit.width_spinbox.value(),
        autosplit.height_spinbox.value(),
        autosplit.hwnd_title,
        0,
        0,
        autosplit.group_dummy_splits_undo_skip_setting,
        autosplit.loop_setting,
        autosplit.auto_start_on_reset_setting,
        autosplit.force_print_window_checkbox.isChecked()]

    # save settings to a .pkl file
    with open(autosplit.save_settings_file_path, "wb") as file:
        pickle.dump(autosplit.last_saved_settings, file)

    # Wording is kinda off here but this needs to be here for an edge case:
    # for when a file has never loaded, but you save file as successfully.
    autosplit.last_successfully_loaded_settings_file_path = autosplit.save_settings_file_path


def load_settings(
        autosplit: AutoSplit,
        load_settings_on_open: bool = False,
        load_settings_from_livesplit: bool = False):
    if load_settings_on_open:
        settings_files = [
            file for file
            in os.listdir(auto_split_directory)
            if file.endswith(".pkl")]

        # find all .pkls in AutoSplit folder, error if there is none or more than 1
        if len(settings_files) < 1:
            error_messages.no_settings_file_on_open()
            autosplit.last_loaded_settings = None
            return
        if len(settings_files) > 1:
            error_messages.too_many_settings_files_on_open()
            autosplit.last_loaded_settings = None
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
                if not load_settings_from_livesplit:
                    autosplit.show_error_signal.emit(error_messages.invalid_settings)
                return
            autosplit.last_loaded_settings = [
                autosplit.split_image_directory,
                autosplit.similarity_threshold,
                autosplit.comparison_index,
                autosplit.pause,
                autosplit.fps_limit,
                autosplit.split_key,
                autosplit.reset_key,
                autosplit.skip_split_key,
                autosplit.undo_split_key,
                autosplit.pause_key,
                region_x,
                region_y,
                region_width,
                region_height,
                autosplit.hwnd_title,
                _,
                _,
                autosplit.group_dummy_splits_undo_skip_setting,
                autosplit.loop_setting,
                autosplit.auto_start_on_reset_setting,
                force_print_window_checkbox] = settings

            autosplit.force_print_window_checkbox.setChecked(force_print_window_checkbox)
    except (FileNotFoundError, MemoryError, pickle.UnpicklingError):
        autosplit.show_error_signal.emit(error_messages.invalid_settings)
        return

    autosplit.split_image_folder_input.setText(autosplit.split_image_directory)
    autosplit.similarity_threshold_spinbox.setValue(autosplit.similarity_threshold)
    autosplit.pause_spinbox.setValue(autosplit.pause)
    autosplit.fps_limit_spinbox.setValue(autosplit.fps_limit)
    autosplit.x_spinbox.setValue(region_x)
    autosplit.y_spinbox.setValue(region_y)
    autosplit.width_spinbox.setValue(region_width)
    autosplit.height_spinbox.setValue(region_height)
    autosplit.comparison_method_combobox.setCurrentIndex(autosplit.comparison_index)
    # https://github.com/kaluluosi/pywin32-stubs/issues/7
    autosplit.hwnd = win32gui.FindWindow(None, autosplit.hwnd_title)  # type: ignore

    # set custom checkbox's accordingly
    autosplit.group_dummy_splits_checkbox.setChecked(bool(autosplit.group_dummy_splits_undo_skip_setting))
    autosplit.loop_checkbox.setChecked(bool(autosplit.loop_setting))
    autosplit.auto_start_on_reset_checkbox.setChecked(bool(autosplit.auto_start_on_reset_setting))
    autosplit.auto_start_on_reset_checkbox.setChecked(bool(autosplit.auto_start_on_reset_setting))

    # TODO: Reuse code from hotkeys rather than duplicating here
    # try to set hotkeys from when user last closed the window
    if autosplit.split_hotkey:
        keyboard.unhook_key(autosplit.split_hotkey)
    try:
        autosplit.split_input.setText(autosplit.split_key)
        if not autosplit.is_auto_controlled:
            autosplit.split_hotkey = keyboard.hook_key(
                autosplit.split_key,
                lambda error: _hotkey_action(error, autosplit.split_key, autosplit.start_suto_splitter))
    except (ValueError, KeyError):
        pass

    if autosplit.reset_hotkey:
        keyboard.unhook_key(autosplit.reset_hotkey)
    try:
        autosplit.reset_input.setText(autosplit.reset_key)
        if not autosplit.is_auto_controlled:
            autosplit.reset_hotkey = keyboard.hook_key(
                autosplit.reset_key,
                lambda error: _hotkey_action(error, autosplit.reset_key, autosplit.start_reset))
    except (ValueError, KeyError):
        pass

    if autosplit.skip_split_hotkey:
        keyboard.unhook_key(autosplit.skip_split_hotkey)
    try:
        autosplit.skip_split_input.setText(autosplit.skip_split_key)
        if not autosplit.is_auto_controlled:
            autosplit.skip_split_hotkey = keyboard.hook_key(
                autosplit.skip_split_key,
                lambda error: _hotkey_action(error, autosplit.skip_split_key, autosplit.start_skip_split))
    except (ValueError, KeyError):
        pass

    if autosplit.skip_split_hotkey:
        keyboard.unhook_key(autosplit.skip_split_hotkey)
    try:
        autosplit.undo_split_input.setText(autosplit.undo_split_key)
        if not autosplit.is_auto_controlled:
            autosplit.undo_split_hotkey = keyboard.hook_key(
                autosplit.undo_split_key,
                lambda error: _hotkey_action(error, autosplit.undo_split_key, autosplit.start_undo_split))
    except (ValueError, KeyError):
        pass

    if autosplit.pause_hotkey:
        keyboard.unhook_key(autosplit.pause_hotkey)
    try:
        autosplit.pause_hotkey_input.setText(autosplit.pause_key)
        if not autosplit.is_auto_controlled:
            autosplit.pause_hotkey = keyboard.hook_key(
                autosplit.pause_key,
                lambda error: _hotkey_action(error, autosplit.pause_key, autosplit.start_pause))
    except (ValueError, KeyError):
        pass

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
