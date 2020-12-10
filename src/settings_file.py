import keyboard
import win32gui
import pickle

def saveSettings(self):
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

    # save settings to settings.pkl
    with open('settings.pkl', 'wb') as f:
        pickle.dump(
            [self.split_image_directory, self.similarity_threshold, self.comparison_index, self.pause,
             self.fps_limit, self.split_key,
             self.reset_key, self.skip_split_key, self.undo_split_key, self.pause_key, self.x, self.y, self.width, self.height,
             self.hwnd_title,
             self.custom_pause_times_setting, self.custom_thresholds_setting,
             self.group_dummy_splits_undo_skip_setting, self.loop_setting], f)


def loadSettings(self):
    try:
        with open('settings.pkl', 'rb') as f:
            [self.split_image_directory, self.similarity_threshold, self.comparison_index, self.pause,
             self.fps_limit, self.split_key,
             self.reset_key, self.skip_split_key, self.undo_split_key, self.pause_key, self.x, self.y, self.width, self.height,
             self.hwnd_title,
             self.custom_pause_times_setting, self.custom_thresholds_setting,
             self.group_dummy_splits_undo_skip_setting, self.loop_setting] = pickle.load(f)

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

        try:
            try:
                keyboard.remove_hotkey(self.pause_hotkey)
            except AttributeError:
                pass
            self.pauseLineEdit.setText(str(self.pause_key))
            self.pause_hotkey = keyboard.add_hotkey(str(self.pause_key), self.startPause)
            self.old_pause_key = self.pause_key
        except ValueError:
            pass

        self.checkLiveImage()

    except IOError:
        self.settingsNotFoundError()
        pass
    except Exception:
        self.invalidSettingsError()
        pass
