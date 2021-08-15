import keyboard
import win32gui
import pickle
import glob
from PyQt4 import QtGui

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

    self.custom_pause_times_setting = 0
    self.custom_thresholds_setting = 1

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
    self.current_save_settings = [
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
        self.custom_pause_times_setting,
        self.custom_thresholds_setting,
        self.group_dummy_splits_undo_skip_setting,
        self.loop_setting,
        self.auto_start_on_reset_setting]

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
            self.custom_pause_times_setting,
            self.custom_thresholds_setting,
            self.group_dummy_splits_undo_skip_setting,
            self.loop_setting,
            self.auto_start_on_reset_setting]
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
        self.custom_pause_times_setting,
        self.custom_thresholds_setting,
        self.group_dummy_splits_undo_skip_setting,
        self.loop_setting,
        self.auto_start_on_reset_setting]

    # save settings to a .pkl file
    with open(self.save_settings_file_path, 'wb') as f:
        pickle.dump(self.last_saved_settings, f)

    #wording is kinda off here but this needs to be here for an edge case: for when a file has never loaded, but you
    #save file as successfully.
    self.last_successfully_loaded_settings_file_path = self.save_settings_file_path


def loadSettings(self):
    if self.load_settings_on_open == True:
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
                        self.custom_pause_times_setting,
                        self.custom_thresholds_setting,
                        self.group_dummy_splits_undo_skip_setting,
                        self.loop_setting,
                        self.auto_start_on_reset_setting] = pickle.load(f)
            #v1.3-1.4 settings. add a blank pause key.
            elif self.settings_count == 18:
                with open(self.load_settings_file_path, 'rb') as f:
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
                        self.x,
                        self.y,
                        self.width,
                        self.height,
                        self.hwnd_title,
                        self.custom_pause_times_setting,
                        self.custom_thresholds_setting,
                        self.group_dummy_splits_undo_skip_setting,
                        self.loop_setting] = pickle.load(f)
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

        # set custom checkboxes accordingly
        if self.group_dummy_splits_undo_skip_setting == 1:
            self.groupDummySplitsCheckBox.setChecked(True)
        else:
            self.groupDummySplitsCheckBox.setChecked(False)

        if self.loop_setting == 1:
            self.loopCheckBox.setChecked(True)
        else:
            self.loopCheckBox.setChecked(False)

        if self.auto_start_on_reset_setting == 1:
            self.autostartonresetCheckBox.setChecked(True)
        else:
            self.autostartonresetCheckBox.setChecked(False)

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

        self.last_successfully_loaded_settings_file_path = self.load_settings_file_path
        self.checkLiveImage()

    except Exception:
        self.invalidSettingsError()
        pass
