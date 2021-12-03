from __future__ import annotations
from typing import TYPE_CHECKING, List, Union
if TYPE_CHECKING:
    from AutoSplit import AutoSplit

from win32 import win32gui
from PyQt6 import QtCore, QtWidgets
import os
import sys
import keyboard
import pickle

from hotkeys import _hotkey_action
import design
import error_messages

# Keyword 'frozen' is for setting basedir while in onefile mode in pyinstaller
FROZEN = getattr(sys, 'frozen', False)

# Get the directory of either AutoSplit.exe or AutoSplit.py
auto_split_directory = os.path.dirname(sys.executable if FROZEN else os.path.abspath(__file__))


def getSaveSettingsValues(self: AutoSplit):
    # get values to be able to save settings
    self.x = self.xSpinBox.value()
    self.y = self.ySpinBox.value()
    self.width = self.widthSpinBox.value()
    self.height = self.heightSpinBox.value()
    self.similarity_threshold = self.similaritythresholdDoubleSpinBox.value()
    self.comparison_index = self.comparisonmethodComboBox.currentIndex()
    self.pause = self.pauseDoubleSpinBox.value()
    self.fps_limit = self.fpslimitSpinBox.value()
    self.split_key = self.splitLineEdit.text()
    self.reset_key = self.resetLineEdit.text()
    self.skip_split_key = self.skipsplitLineEdit.text()
    self.undo_split_key = self.undosplitLineEdit.text()
    self.pause_key = self.pausehotkeyLineEdit.text()

    if self.groupDummySplitsCheckBox.isChecked():
        self.group_dummy_splits_undo_skip_setting = 1
    else:
        self.group_dummy_splits_undo_skip_setting = 0

    if self.loopCheckBox.isChecked():
        self.loop_setting = 1
    else:
        self.loop_setting = 0

    if self.autostartonresetCheckBox.isChecked():
        self.auto_start_on_reset_setting = 1
    else:
        self.auto_start_on_reset_setting = 0


def haveSettingsChanged(self: AutoSplit):
    self.getSaveSettingsValues()
    current_save_settings = [
        self.split_image_directory,
        self.similarity_threshold,
        self.comparison_index,
        self.pause,
        self.fps_limit,
        self.split_key,
        self.reset_key,
        self.skip_split_key,
        self.undo_split_key,
        self.pause_key,
        self.x,
        self.y,
        self.width,
        self.height,
        self.hwnd_title,
        0,
        0,
        self.group_dummy_splits_undo_skip_setting,
        self.loop_setting,
        self.auto_start_on_reset_setting]

    # One small caveat in this: if you load a settings file from an old version, but dont change settings,
    # the current save settings and last load settings will have different # of elements and it will ask
    # the user to save changes upon closing even though there were none
    return current_save_settings not in (self.last_loaded_settings, self.last_saved_settings)


def saveSettings(self: AutoSplit):
    if self.last_successfully_loaded_settings_file_path == None:
        self.saveSettingsAs()
    else:
        self.getSaveSettingsValues()
        self.last_saved_settings = [
            self.split_image_directory,
            self.similarity_threshold,
            self.comparison_index,
            self.pause,
            self.fps_limit,
            self.split_key,
            self.reset_key,
            self.skip_split_key,
            self.undo_split_key,
            self.pause_key,
            self.x,
            self.y,
            self.width,
            self.height,
            self.hwnd_title,
            0,
            0,
            self.group_dummy_splits_undo_skip_setting,
            self.loop_setting,
            self.auto_start_on_reset_setting]
        # save settings to a .pkl file
        with open(self.last_successfully_loaded_settings_file_path, 'wb') as f:
            pickle.dump(self.last_saved_settings, f)


def saveSettingsAs(self: AutoSplit):
    # User picks save destination
    self.save_settings_file_path = QtWidgets.QFileDialog.getSaveFileName(
        self,
        "Save Settings As",
        os.path.join(auto_split_directory, "settings.pkl"),
        "PKL (*.pkl)")[0]

    # If user cancels save destination window, don't save settings
    if not self.save_settings_file_path:
        return

    self.getSaveSettingsValues()
    self.last_saved_settings = [
        self.split_image_directory,
        self.similarity_threshold,
        self.comparison_index,
        self.pause,
        self.fps_limit,
        self.split_key,
        self.reset_key,
        self.skip_split_key,
        self.undo_split_key,
        self.pause_key,
        self.x,
        self.y,
        self.width,
        self.height,
        self.hwnd_title,
        0,
        0,
        self.group_dummy_splits_undo_skip_setting,
        self.loop_setting,
        self.auto_start_on_reset_setting]

    # save settings to a .pkl file
    with open(self.save_settings_file_path, 'wb') as f:
        pickle.dump(self.last_saved_settings, f)

    #wording is kinda off here but this needs to be here for an edge case: for when a file has never loaded, but you
    #save file as successfully.
    self.last_successfully_loaded_settings_file_path = self.save_settings_file_path


def loadSettings(self: AutoSplit, load_settings_on_open: bool = False, load_settings_from_livesplit: bool = False):
    if load_settings_on_open:

        settings_files = [
            file for file
            in os.listdir(auto_split_directory)
            if file.endswith(".pkl")
        ]

        # find all .pkls in AutoSplit folder, error if there is none or more than 1
        if len(settings_files) < 1:
            error_messages.noSettingsFileOnOpenError()
            self.last_loaded_settings = None
            return
        elif len(settings_files) > 1:
            error_messages.tooManySettingsFilesOnOpenError()
            self.last_loaded_settings = None
            return
        else:
            self.load_settings_file_path = os.path.join(auto_split_directory, settings_files[0])

    elif not load_settings_on_open and not load_settings_from_livesplit:

        self.load_settings_file_path = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Load Settings",
            os.path.join(auto_split_directory, "settings.pkl"),
            "PKL (*.pkl)")[0]

        if self.load_settings_file_path == '':
            return

    try:
        with open(self.load_settings_file_path, 'rb') as f:
            settings: List[Union[str, int]] = pickle.load(f)
            settings_count = len(settings)
            if settings_count < 18:
                self.showErrorSignal.emit(error_messages.oldVersionSettingsFileError)
                return
            # v1.3-1.4 settings. Add default pause_key and auto_start_on_reset_setting
            if settings_count == 18:
                settings.insert(9, '')
                settings.insert(20, 0)
            # v1.5 settings
            elif settings_count != 20:
                self.showErrorSignal.emit(error_messages.invalidSettingsError)
                return
            self.last_loaded_settings = [
                self.split_image_directory,
                self.similarity_threshold,
                self.comparison_index,
                self.pause,
                self.fps_limit,
                self.split_key,
                self.reset_key,
                self.skip_split_key,
                self.undo_split_key,
                self.pause_key,
                self.x,
                self.y,
                self.width,
                self.height,
                self.hwnd_title,
                _,
                _,
                self.group_dummy_splits_undo_skip_setting,
                self.loop_setting,
                self.auto_start_on_reset_setting] = settings
    except (FileNotFoundError, MemoryError, pickle.UnpicklingError):
        self.showErrorSignal.emit(error_messages.invalidSettingsError)
        return

    self.splitimagefolderLineEdit.setText(self.split_image_directory)
    self.similaritythresholdDoubleSpinBox.setValue(self.similarity_threshold)
    self.pauseDoubleSpinBox.setValue(self.pause)
    self.fpslimitSpinBox.setValue(self.fps_limit)
    self.xSpinBox.setValue(self.x)
    self.ySpinBox.setValue(self.y)
    self.widthSpinBox.setValue(self.width)
    self.heightSpinBox.setValue(self.height)
    self.comparisonmethodComboBox.setCurrentIndex(self.comparison_index)
    self.hwnd = win32gui.FindWindow(None, self.hwnd_title)

    # set custom checkbox's accordingly
    self.groupDummySplitsCheckBox.setChecked(self.group_dummy_splits_undo_skip_setting == 1)
    self.loopCheckBox.setChecked(self.loop_setting == 1)
    self.autostartonresetCheckBox.setChecked(self.auto_start_on_reset_setting == 1)
    self.autostartonresetCheckBox.setChecked(self.auto_start_on_reset_setting == 1)

    # TODO: Reuse code from hotkeys rather than duplicating here
    # try to set hotkeys from when user last closed the window
    try:
        keyboard.unhook_key(self.split_hotkey)
    # pass if the key is an empty string (hotkey was never set)
    except (AttributeError, KeyError):
        pass
    try:
        self.splitLineEdit.setText(self.split_key)
        if not self.is_auto_controlled:
            self.split_hotkey = keyboard.hook_key(self.split_key, lambda e: _hotkey_action(e, self.split_key, self.startAutoSplitter))
    except (ValueError, KeyError):
        pass

    try:
        keyboard.unhook_key(self.reset_hotkey)
    except (AttributeError, KeyError):
        pass
    try:
        self.resetLineEdit.setText(self.reset_key)
        if not self.is_auto_controlled:
            self.reset_hotkey = keyboard.hook_key(self.reset_key, lambda e: _hotkey_action(e, self.reset_key, self.startReset))
    except (ValueError, KeyError):
        pass

    try:
        keyboard.unhook_key(self.skip_split_hotkey)
    except (AttributeError, KeyError):
        pass
    try:
        self.skipsplitLineEdit.setText(self.skip_split_key)
        if not self.is_auto_controlled:
            self.skip_split_hotkey = keyboard.hook_key(self.skip_split_key, lambda e: _hotkey_action(e, self.skip_split_key, self.startSkipSplit))
    except (ValueError, KeyError):
        pass

    try:
        keyboard.unhook_key(self.undo_split_hotkey)
    except (AttributeError, KeyError):
        pass
    try:
        self.undosplitLineEdit.setText(self.undo_split_key)
        if not self.is_auto_controlled:
            self.undo_split_hotkey = keyboard.hook_key(self.undo_split_key, lambda e: _hotkey_action(e, self.undo_split_key, self.startUndoSplit))
    except (ValueError, KeyError):
        pass

    try:
        keyboard.unhook_key(self.pause_hotkey)
    except (AttributeError, KeyError):
        pass
    try:
        self.pausehotkeyLineEdit.setText(self.pause_key)
        if not self.is_auto_controlled:
            self.pause_hotkey = keyboard.hook_key(self.pause_key, lambda e: _hotkey_action(e, self.pause_key, self.startPause))
    except (ValueError, KeyError):
        pass

    self.last_successfully_loaded_settings_file_path = self.load_settings_file_path
    self.checkLiveImage()
    self.loadStartImage()


def load_check_for_updates_on_open(designWindow: design.Ui_MainWindow):
    """
    Retrieve the 'Check For Updates On Open' QSettings and set the checkbox state
    These are only global settings values. They are not *pkl settings values.
    """

    value = QtCore \
        .QSettings('AutoSplit', 'Check For Updates On Open') \
        .value('check_for_updates_on_open', True, type=bool)
    designWindow.actionCheck_for_Updates_on_Open.setChecked(value)


def set_check_for_updates_on_open(designWindow: design.Ui_MainWindow, value: bool):
    """
    Sets the 'Check For Updates On Open' QSettings value and the checkbox state
    """

    designWindow.actionCheck_for_Updates_on_Open.setChecked(value)
    QtCore \
        .QSettings('AutoSplit', 'Check For Updates On Open') \
        .setValue('check_for_updates_on_open', value)
