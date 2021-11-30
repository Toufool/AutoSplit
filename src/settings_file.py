from __future__ import annotations
from typing import TYPE_CHECKING, Any, Literal, cast
if TYPE_CHECKING:
    from AutoSplit import AutoSplit

import os
import sys
import pickle
import keyboard  # https://github.com/boppreh/keyboard/issues/505
from win32 import win32gui
from PyQt6 import QtWidgets

import error_messages
# TODO with settings refactoring
from hotkeys import _hotkey_action  # type: ignore

# Get the directory of either AutoSplit.exe or AutoSplit.py
auto_split_directory = os.path.dirname(sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__))


class RestrictedUnpickler(pickle.Unpickler):

    def find_class(self, module: str, name: str):
        raise pickle.UnpicklingError("'%s.%s' is forbidden" % (module, name))


def loadPyQtSettings(autosplit: AutoSplit):
    # These are only global settings values. They are not *pkl settings values.
    autosplit.getGlobalSettingsValues()
    check_for_updates_on_open = autosplit.setting_check_for_updates_on_open.value(
        "check_for_updates_on_open",
        True,
        type=bool)
    autosplit.actionCheck_for_Updates_on_Open.setChecked(check_for_updates_on_open)


def getSaveSettingsValues(autosplit: AutoSplit):
    # get values to be able to save settings
    autosplit.similarity_threshold = autosplit.similaritythresholdDoubleSpinBox.value()
    autosplit.comparison_index = autosplit.comparisonmethodComboBox.currentIndex()
    autosplit.pause = autosplit.pauseDoubleSpinBox.value()
    autosplit.fps_limit = int(autosplit.fpslimitSpinBox.value())
    autosplit.split_key = autosplit.splitLineEdit.text()
    autosplit.reset_key = autosplit.resetLineEdit.text()
    autosplit.skip_split_key = autosplit.skipsplitLineEdit.text()
    autosplit.undo_split_key = autosplit.undosplitLineEdit.text()
    autosplit.pause_key = autosplit.pausehotkeyLineEdit.text()
    autosplit.group_dummy_splits_undo_skip_setting = cast(
        Literal[0, 1],
        int(autosplit.groupDummySplitsCheckBox.isChecked()))
    autosplit.loop_setting = cast(
        Literal[0, 1],
        int(autosplit.loopCheckBox.isChecked()))
    autosplit.auto_start_on_reset_setting = cast(
        Literal[0, 1],
        int(autosplit.autostartonresetCheckBox.isChecked()))


def haveSettingsChanged(autosplit: AutoSplit):
    getSaveSettingsValues(autosplit)
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
        autosplit.xSpinBox.value(),
        autosplit.ySpinBox.value(),
        autosplit.widthSpinBox.value(),
        autosplit.heightSpinBox.value(),
        autosplit.hwnd_title,
        0,
        0,
        autosplit.group_dummy_splits_undo_skip_setting,
        autosplit.loop_setting,
        autosplit.auto_start_on_reset_setting,
        autosplit.forcePrintWindowCheckBox.isChecked()]

    # One small caveat in this: if you load a settings file from an old version, but dont change settings,
    # the current save settings and last load settings will have different # of elements and it will ask
    # the user to save changes upon closing even though there were none
    return current_save_settings not in (autosplit.last_loaded_settings, autosplit.last_saved_settings)


def saveSettings(autosplit: AutoSplit):
    if not autosplit.last_successfully_loaded_settings_file_path:
        saveSettingsAs(autosplit)
    else:
        getSaveSettingsValues(autosplit)
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
            autosplit.xSpinBox.value(),
            autosplit.ySpinBox.value(),
            autosplit.widthSpinBox.value(),
            autosplit.heightSpinBox.value(),
            autosplit.hwnd_title,
            0,
            0,
            autosplit.group_dummy_splits_undo_skip_setting,
            autosplit.loop_setting,
            autosplit.auto_start_on_reset_setting,
            autosplit.forcePrintWindowCheckBox.isChecked()]
        # save settings to a .pkl file
        with open(autosplit.last_successfully_loaded_settings_file_path, "wb") as f:
            pickle.dump(autosplit.last_saved_settings, f)


def saveSettingsAs(autosplit: AutoSplit):
    # User picks save destination
    autosplit.save_settings_file_path = QtWidgets.QFileDialog.getSaveFileName(
        autosplit,
        "Save Settings As",
        os.path.join(auto_split_directory, "settings.pkl"),
        "PKL (*.pkl)")[0]

    # If user cancels save destination window, don't save settings
    if not autosplit.save_settings_file_path:
        return

    getSaveSettingsValues(autosplit)
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
        autosplit.xSpinBox.value(),
        autosplit.ySpinBox.value(),
        autosplit.widthSpinBox.value(),
        autosplit.heightSpinBox.value(),
        autosplit.hwnd_title,
        0,
        0,
        autosplit.group_dummy_splits_undo_skip_setting,
        autosplit.loop_setting,
        autosplit.auto_start_on_reset_setting,
        autosplit.forcePrintWindowCheckBox.isChecked()]

    # save settings to a .pkl file
    with open(autosplit.save_settings_file_path, "wb") as f:
        pickle.dump(autosplit.last_saved_settings, f)

    # Wording is kinda off here but this needs to be here for an edge case:
    # for when a file has never loaded, but you save file as successfully.
    autosplit.last_successfully_loaded_settings_file_path = autosplit.save_settings_file_path


def loadSettings(autosplit: AutoSplit, load_settings_on_open: bool = False, load_settings_from_livesplit: bool = False):
    if load_settings_on_open:
        settings_files = [
            file for file
            in os.listdir(auto_split_directory)
            if file.endswith(".pkl")]

        # find all .pkls in AutoSplit folder, error if there is none or more than 1
        if len(settings_files) < 1:
            error_messages.noSettingsFileOnOpenError()
            autosplit.last_loaded_settings = None
            return
        if len(settings_files) > 1:
            error_messages.tooManySettingsFilesOnOpenError()
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
        with open(autosplit.load_settings_file_path, "rb") as f:
            settings: list[Any] = RestrictedUnpickler(f).load()
            settings_count = len(settings)
            if settings_count < 18:
                autosplit.showErrorSignal.emit(error_messages.oldVersionSettingsFileError)
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
                    autosplit.showErrorSignal.emit(error_messages.invalidSettingsError)
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
                forcePrintWindowCheckBox] = settings

            autosplit.forcePrintWindowCheckBox.setChecked(forcePrintWindowCheckBox)
    except (FileNotFoundError, MemoryError, pickle.UnpicklingError) as e:
        print(e)
        autosplit.showErrorSignal.emit(error_messages.invalidSettingsError)
        return

    autosplit.splitimagefolderLineEdit.setText(autosplit.split_image_directory)
    autosplit.similaritythresholdDoubleSpinBox.setValue(autosplit.similarity_threshold)
    autosplit.pauseDoubleSpinBox.setValue(autosplit.pause)
    autosplit.fpslimitSpinBox.setValue(autosplit.fps_limit)
    autosplit.xSpinBox.setValue(region_x)
    autosplit.ySpinBox.setValue(region_y)
    autosplit.widthSpinBox.setValue(region_width)
    autosplit.heightSpinBox.setValue(region_height)
    autosplit.comparisonmethodComboBox.setCurrentIndex(autosplit.comparison_index)
    # https://github.com/kaluluosi/pywin32-stubs/issues/7
    autosplit.hwnd = win32gui.FindWindow(None, autosplit.hwnd_title)  # type: ignore

    # set custom checkbox's accordingly
    autosplit.groupDummySplitsCheckBox.setChecked(bool(autosplit.group_dummy_splits_undo_skip_setting))
    autosplit.loopCheckBox.setChecked(bool(autosplit.loop_setting))
    autosplit.autostartonresetCheckBox.setChecked(bool(autosplit.auto_start_on_reset_setting))
    autosplit.autostartonresetCheckBox.setChecked(bool(autosplit.auto_start_on_reset_setting))

    # TODO: Reuse code from hotkeys rather than duplicating here
    # try to set hotkeys from when user last closed the window
    if autosplit.split_hotkey:
        keyboard.unhook_key(autosplit.split_hotkey)
    try:
        autosplit.splitLineEdit.setText(autosplit.split_key)
        if not autosplit.is_auto_controlled:
            autosplit.split_hotkey = keyboard.hook_key(
                autosplit.split_key,
                lambda e: _hotkey_action(e, autosplit.split_key, autosplit.startAutoSplitter))
    except (ValueError, KeyError):
        pass

    if autosplit.reset_hotkey:
        keyboard.unhook_key(autosplit.reset_hotkey)
    try:
        autosplit.resetLineEdit.setText(autosplit.reset_key)
        if not autosplit.is_auto_controlled:
            autosplit.reset_hotkey = keyboard.hook_key(
                autosplit.reset_key,
                lambda e: _hotkey_action(e, autosplit.reset_key, autosplit.startReset))
    except (ValueError, KeyError):
        pass

    if autosplit.skip_split_hotkey:
        keyboard.unhook_key(autosplit.skip_split_hotkey)
    try:
        autosplit.skipsplitLineEdit.setText(autosplit.skip_split_key)
        if not autosplit.is_auto_controlled:
            autosplit.skip_split_hotkey = keyboard.hook_key(
                autosplit.skip_split_key,
                lambda e: _hotkey_action(e, autosplit.skip_split_key, autosplit.startSkipSplit))
    except (ValueError, KeyError):
        pass

    if autosplit.skip_split_hotkey:
        keyboard.unhook_key(autosplit.skip_split_hotkey)
    try:
        autosplit.undosplitLineEdit.setText(autosplit.undo_split_key)
        if not autosplit.is_auto_controlled:
            autosplit.undo_split_hotkey = keyboard.hook_key(
                autosplit.undo_split_key,
                lambda e: _hotkey_action(e, autosplit.undo_split_key, autosplit.startUndoSplit))
    except (ValueError, KeyError):
        pass

    if autosplit.pause_hotkey:
        keyboard.unhook_key(autosplit.pause_hotkey)
    try:
        autosplit.pausehotkeyLineEdit.setText(autosplit.pause_key)
        if not autosplit.is_auto_controlled:
            autosplit.pause_hotkey = keyboard.hook_key(
                autosplit.pause_key,
                lambda e: _hotkey_action(e, autosplit.pause_key, autosplit.startPause))
    except (ValueError, KeyError):
        pass

    autosplit.last_successfully_loaded_settings_file_path = autosplit.load_settings_file_path
    autosplit.checkLiveImage()
    autosplit.loadStartImage()
