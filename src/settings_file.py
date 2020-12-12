import keyboard
import win32gui
import pickle
import glob
from PyQt4 import QtGui

def saveSettings(self):
    # user picks save destination
    self.save_settings_file_path = str(QtGui.QFileDialog.getSaveFileName(self, "Save Settings", "", "PKL (*.pkl)"))
    #if user cancels save destination window, don't save settings
    if self.save_settings_file_path == '':
        return

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

    # save settings to a .pkl file
    with open(self.save_settings_file_path, 'wb') as f:
        pickle.dump(
            [self.split_image_directory, self.similarity_threshold, self.comparison_index, self.pause,
             self.fps_limit, self.split_key,
             self.reset_key, self.skip_split_key, self.undo_split_key, self.pause_key, self.x, self.y, self.width, self.height,
             self.hwnd_title,
             self.custom_pause_times_setting, self.custom_thresholds_setting,
             self.group_dummy_splits_undo_skip_setting, self.loop_setting], f)


def loadSettings(self):
    if self.load_settings_on_open == True:
        self.settings_files = glob.glob("*.pkl")
        if len(self.settings_files) < 1:
            self.noSettingsFileOnOpenError()
            return
        elif len(self.settings_files) > 1:
            self.tooManySettingsFilesOnOpenError()
            return
        else:
            self.load_settings_file_path = self.settings_files[0]

    else:
        self.load_settings_file_path = str(QtGui.QFileDialog.getOpenFileName(self, "Load Settings", "", "PKL (*.pkl)"))

        # if user cancels load settings window, don't attempt to load settings
        if self.load_settings_file_path == '':
            return

    try:
        with open(self.load_settings_file_path, 'rb') as f:
            self.settings_count = len(pickle.load(f))
            #v1.5 settings
            if self.settings_count == 19:
                with open(self.load_settings_file_path, 'rb') as f:
                    [self.split_image_directory, self.similarity_threshold, self.comparison_index, self.pause,
                     self.fps_limit, self.split_key,
                     self.reset_key, self.skip_split_key, self.undo_split_key, self.pause_key, self.x, self.y, self.width, self.height,
                     self.hwnd_title,
                     self.custom_pause_times_setting, self.custom_thresholds_setting,
                     self.group_dummy_splits_undo_skip_setting, self.loop_setting] = pickle.load(f)
            #v1.3-1.4 settings. add a blank pause key.
            elif self.settings_count == 18:
                with open(self.load_settings_file_path, 'rb') as f:
                    [self.split_image_directory, self.similarity_threshold, self.comparison_index, self.pause,
                     self.fps_limit, self.split_key,
                     self.reset_key, self.skip_split_key, self.undo_split_key, self.x, self.y, self.width, self.height,
                     self.hwnd_title,
                     self.custom_pause_times_setting, self.custom_thresholds_setting,
                     self.group_dummy_splits_undo_skip_setting, self.loop_setting] = pickle.load(f)
                self.pause_key = ''
            else:
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
        if self.custom_pause_times_setting == 1:
            self.custompausetimesCheckBox.setChecked(True)
        else:
            self.custompausetimesCheckBox.setChecked(False)

        if self.custom_thresholds_setting == 1:
            self.customthresholdsCheckBox.setChecked(True)
        else:
            self.customthresholdsCheckBox.setChecked(False)

        if self.group_dummy_splits_undo_skip_setting == 1:
            self.groupDummySplitsCheckBox.setChecked(True)
        else:
            self.groupDummySplitsCheckBox.setChecked(False)

        if self.loop_setting == 1:
            self.loopCheckBox.setChecked(True)
        else:
            self.loopCheckBox.setChecked(False)

        # try to set hotkeys from when user last closed the window
        try:
            try:
                keyboard.remove_hotkey(self.split_hotkey)
            except AttributeError:
                pass
            self.splitLineEdit.setText(str(self.split_key))
            self.split_hotkey = keyboard.add_hotkey(str(self.split_key), self.startAutoSplitter)
            self.old_split_key = self.split_key
        # pass if the key is an empty string (hotkey was never set)
        except ValueError:
            pass
        except KeyError:
            pass

        try:
            try:
                keyboard.remove_hotkey(self.reset_hotkey)
            except AttributeError:
                pass
            self.resetLineEdit.setText(str(self.reset_key))
            self.reset_hotkey = keyboard.add_hotkey(str(self.reset_key), self.startReset)
            self.old_reset_key = self.reset_key
        except ValueError:
            pass
        except KeyError:
            pass

        try:
            try:
                keyboard.remove_hotkey(self.skip_split_hotkey)
            except AttributeError:
                pass
            self.skipsplitLineEdit.setText(str(self.skip_split_key))
            self.skip_split_hotkey = keyboard.add_hotkey(str(self.skip_split_key), self.startSkipSplit)
            self.old_skip_split_key = self.skip_split_key
        except ValueError:
            pass
        except KeyError:
            pass

        try:
            try:
                keyboard.remove_hotkey(self.undo_split_hotkey)
            except AttributeError:
                pass
            self.undosplitLineEdit.setText(str(self.undo_split_key))
            self.undo_split_hotkey = keyboard.add_hotkey(str(self.undo_split_key), self.startUndoSplit)
            self.old_undo_split_key = self.undo_split_key
        except ValueError:
            pass
        except KeyError:
            pass

        try:
            try:
                keyboard.remove_hotkey(self.pause_hotkey)
            except AttributeError:
                pass
            self.pausehotkeyLineEdit.setText(str(self.pause_key))
            self.pause_hotkey = keyboard.add_hotkey(str(self.pause_key), self.startPause)
            self.old_pause_key = self.pause_key
        except ValueError:
            pass
        except KeyError:
            pass

        self.checkLiveImage()

    except Exception:
        self.invalidSettingsError()
        pass
