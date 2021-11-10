import keyboard
import win32gui
import pickle
import glob
import logging
from PyQt4 import QtGui
from hotkeys import _hotkey_action


def getSaveSettingsValues(self):
    # get values to be able to save settings
    self.x = self.xSpinBox.value()
    self.y = self.ySpinBox.value()
    self.width = self.widthSpinBox.value()
    self.height = self.heightSpinBox.value()
    self.split_image_directory = str(self.splitimagefolderLineEdit.text())
    self.similarity_threshold = self.similaritythresholdDoubleSpinBox.value()
    self.comparison_index = self.comparisonmethodComboBox.currentIndex()
    self.pause = self.pauseDoubleSpinBox.value()
    self.fps_limit = self.fpslimitSpinBox.value()
    self.split_key = str(self.splitLineEdit.text())
    self.reset_key = str(self.resetLineEdit.text())
    self.skip_split_key = str(self.skipsplitLineEdit.text())
    self.undo_split_key = str(self.undosplitLineEdit.text())
    self.pause_key = str(self.pausehotkeyLineEdit.text())

    if self.custompausetimesCheckBox.isChecked():
        self.custom_pause_times_setting = 1
    else:
        self.custom_pause_times_setting = 0

    if self.customthresholdsCheckBox.isChecked():
        self.custom_thresholds_setting = 1
    else:
        self.custom_thresholds_setting = 0

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

def haveSettingsChanged(self):
    self.getSaveSettingsValues()
    self.current_save_settings = [self.split_image_directory, self.similarity_threshold, self.comparison_index, self.pause,
             self.fps_limit, self.split_key,
             self.reset_key, self.skip_split_key, self.undo_split_key, self.pause_key, self.x, self.y, self.width, self.height,
             self.hwnd_title,
             self.custom_pause_times_setting, self.custom_thresholds_setting,
             self.group_dummy_splits_undo_skip_setting, self.loop_setting, self.auto_start_on_reset_setting]

    #one small caveat in this: if you load a settings file from an old version, but dont change settings,
    #the current save settings and last load settings will have different # of elements and it will ask
    #the user to save changes upon closing even though there were none
    if self.current_save_settings == self.last_loaded_settings or self.current_save_settings == self.last_saved_settings:
        return False
    else:
        return True

def saveSettings(self):
    if self.last_successfully_loaded_settings_file_path == None:
        self.saveSettingsAs()
    else:
        self.getSaveSettingsValues()
        self.last_saved_settings = [self.split_image_directory, self.similarity_threshold, self.comparison_index,
                                    self.pause,
                                    self.fps_limit, self.split_key,
                                    self.reset_key, self.skip_split_key, self.undo_split_key, self.pause_key, self.x,
                                    self.y, self.width, self.height,
                                    self.hwnd_title,
                                    self.custom_pause_times_setting, self.custom_thresholds_setting,
                                    self.group_dummy_splits_undo_skip_setting, self.loop_setting, self.auto_start_on_reset_setting]
        # save settings to a .pkl file
        with open(self.last_successfully_loaded_settings_file_path, 'wb') as f:
            pickle.dump(self.last_saved_settings, f)

def saveSettingsAs(self):
    # user picks save destination
    self.save_settings_file_path = str(QtGui.QFileDialog.getSaveFileName(self, "Save Settings As", "", "PKL (*.pkl)"))

    #if user cancels save destination window, don't save settings
    if self.save_settings_file_path == '':
        return

    self.getSaveSettingsValues()
    self.last_saved_settings = [self.split_image_directory, self.similarity_threshold, self.comparison_index, self.pause,
             self.fps_limit, self.split_key,
             self.reset_key, self.skip_split_key, self.undo_split_key, self.pause_key, self.x, self.y, self.width, self.height,
             self.hwnd_title,
             self.custom_pause_times_setting, self.custom_thresholds_setting,
             self.group_dummy_splits_undo_skip_setting, self.loop_setting, self.auto_start_on_reset_setting]

    # save settings to a .pkl file
    with open(self.save_settings_file_path, 'wb') as f:
        pickle.dump(self.last_saved_settings, f)

    #wording is kinda off here but this needs to be here for an edge case: for when a file has never loaded, but you
    #save file as successfully.
    self.last_successfully_loaded_settings_file_path = self.save_settings_file_path


def loadSettings(self):
    # hotkeys need to be initialized to be passed as thread arguments in hotkeys.py
    self.split_hotkey = ""
    self.reset_hotkey = ""
    self.skip_split_hotkey = ""
    self.undo_split_hotkey = ""
    self.pause_hotkey = ""

    if self.load_settings_on_open:
        self.settings_files = glob.glob("*.pkl")
        if len(self.settings_files) < 1:
            self.noSettingsFileOnOpenError()
            self.last_loaded_settings = None
            return
        elif len(self.settings_files) > 1:
            self.tooManySettingsFilesOnOpenError()
            self.last_loaded_settings = None
            return
        else:
            self.load_settings_file_path = self.settings_files[0]

    else:
        self.load_settings_file_path = str(QtGui.QFileDialog.getOpenFileName(self, "Load Settings", "", "PKL (*.pkl)"))

        #
        if self.load_settings_file_path == '':
            return

    try:
        with open(self.load_settings_file_path, 'rb') as f:
            self.settings_count = len(pickle.load(f))
            #v1.5 settings
            if self.settings_count == 20:
                with open(self.load_settings_file_path, 'rb') as f:
                    self.last_loaded_settings = [self.split_image_directory, self.similarity_threshold, self.comparison_index, self.pause,
                     self.fps_limit, self.split_key,
                     self.reset_key, self.skip_split_key, self.undo_split_key, self.pause_key, self.x, self.y, self.width, self.height,
                     self.hwnd_title,
                     self.custom_pause_times_setting, self.custom_thresholds_setting,
                     self.group_dummy_splits_undo_skip_setting, self.loop_setting, self.auto_start_on_reset_setting] = pickle.load(f)
            #v1.3-1.4 settings. add a blank pause key.
            elif self.settings_count == 18:
                with open(self.load_settings_file_path, 'rb') as f:
                    self.last_loaded_settings = [self.split_image_directory, self.similarity_threshold, self.comparison_index, self.pause,
                     self.fps_limit, self.split_key,
                     self.reset_key, self.skip_split_key, self.undo_split_key, self.x, self.y, self.width, self.height,
                     self.hwnd_title,
                     self.custom_pause_times_setting, self.custom_thresholds_setting,
                     self.group_dummy_splits_undo_skip_setting, self.loop_setting] = pickle.load(f)
                self.pause_key = ''
                self.auto_start_on_reset_setting = 0
            elif self.settings_count < 18:
                self.oldVersionSettingsFileError()
                return

        self.split_image_directory = str(self.split_image_directory)
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
        self.custompausetimesCheckBox.setChecked(self.custom_pause_times_setting == 1)
        self.customthresholdsCheckBox.setChecked(self.custom_thresholds_setting == 1)
        self.groupDummySplitsCheckBox.setChecked(self.group_dummy_splits_undo_skip_setting == 1)
        self.loopCheckBox.setChecked(self.loop_setting == 1)
        self.autostartonresetCheckBox.setChecked(self.auto_start_on_reset_setting == 1)

        # TODO: Reuse code from hotkeys rather than duplicating here
        # try to set hotkeys from when user last closed the window
        try:
            keyboard.unhook_key(self.split_hotkey)
        except (AttributeError, KeyError):
            pass
        try:
            self.splitLineEdit.setText(str(self.split_key))
            self.split_hotkey = keyboard.hook_key(str(self.split_key), lambda e: _hotkey_action(e, self.split_key, self.startAutoSplitter))
        # pass if the key is an empty string (hotkey was never set)
        except (ValueError, KeyError):
            pass

        try:
            keyboard.unhook_key(self.reset_hotkey)
        except (AttributeError, KeyError):
            pass
        try:
            self.resetLineEdit.setText(self.reset_key)
            self.reset_hotkey = keyboard.hook_key(self.reset_key, lambda e: _hotkey_action(e, self.reset_key, self.startReset))
        except (ValueError, KeyError):
            pass

        try:
            keyboard.unhook_key(self.skip_split_hotkey)
        except (AttributeError, KeyError):
            pass
        try:
            self.skipsplitLineEdit.setText(self.skip_split_key)
            self.skip_split_hotkey = keyboard.hook_key(self.skip_split_key, lambda e: _hotkey_action(e, self.skip_split_key, self.startSkipSplit))
        except (ValueError, KeyError):
            pass

        try:
            keyboard.unhook_key(self.undo_split_hotkey)
        except (AttributeError, KeyError):
            pass
        try:
            self.undosplitLineEdit.setText(self.undo_split_key)
            self.undo_split_hotkey = keyboard.hook_key(self.undo_split_key, lambda e: _hotkey_action(e, self.undo_split_key, self.startUndoSplit))
        except (ValueError, KeyError):
            pass

        try:
            keyboard.unhook_key(self.pause_hotkey)
        except (AttributeError, KeyError):
            pass
        try:
            self.pausehotkeyLineEdit.setText(self.pause_key)
            self.pause_hotkey = keyboard.hook_key(self.pause_key, lambda e: _hotkey_action(e, self.pause_key, self.startPause))
        except (ValueError, KeyError):
            pass

        self.last_successfully_loaded_settings_file_path = self.load_settings_file_path
        self.checkLiveImage()

    except Exception:
        logging.error(logging.traceback.format_exc())
        self.invalidSettingsError()
