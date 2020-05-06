from os import path
import pickle
import keyboard
import win32gui

import errors

def loadSettings(self):
    try:
        keys = {}

        with open(path.join(self.file_path, 'settings.pkl'), 'rb') as f:
            f2 = pickle.load(f)

        if len(f2) < 19:
            # The settings file might not include the pause hotkey yet
            f2.append('')

        [self.split_image_directory, self.similarity_threshold, self.comparison_index, self.pause,
        self.fps_limit, keys['split'],
        keys['reset'], keys['skip'], keys['undo'], self.x, self.y, self.width, self.height,
        self.hwnd_title,
        self.custom_pause_times_setting, self.custom_thresholds_setting,
        self.group_dummy_splits_undo_skip_setting, self.loop_setting, keys['pause']] = f2

        self.hwnd = win32gui.FindWindow(None, self.hwnd_title)
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

        # Set custom checkboxes accordingly
        self.custompausetimesCheckBox.setChecked(self.custom_pause_times_setting == 1)
        self.customthresholdsCheckBox.setChecked(self.custom_thresholds_setting == 1)

        # Should be activated by default
        self.groupDummySplitsCheckBox.setChecked(self.group_dummy_splits_undo_skip_setting != 0)

        self.loopCheckBox.setChecked(self.loop_setting == 1)

        self.splitLineEdit.setText(str(keys['split']))
        self.resetLineEdit.setText(str(keys['reset']))
        self.skipsplitLineEdit.setText(str(keys['skip']))
        self.undosplitLineEdit.setText(str(keys['undo']))
        self.pauseLineEdit.setText(str(keys['pause']))

        # Try to set hotkeys from when user last closed the window
        if self.is_auto_controlled == False:
            for key in self.hotkeys:
                if self.hotkeys[key].key_press_function is None:
                    self.hotkeys[key].key = str(keys[key])
                else:
                    self.hotkeys[key].setKeyAndHotkey(str(keys[key]))

    except IOError:
        self.showBox(errors.SETTINGS_NOT_FOUND)
        pass
    except Exception:
        self.showBox(errors.INVALID_SETTINGS)
        pass

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
    split_key = str(self.splitLineEdit.text())
    reset_key = str(self.resetLineEdit.text())
    skip_split_key = str(self.skipsplitLineEdit.text())
    undo_split_key = str(self.undosplitLineEdit.text())
    pause_key = str(self.pauseLineEdit.text())

    self.custom_pause_times_setting = int(self.custompausetimesCheckBox.isChecked())
    self.custom_thresholds_setting = int(self.customthresholdsCheckBox.isChecked())
    self.group_dummy_splits_undo_skip_setting = int(self.groupDummySplitsCheckBox.isChecked())
    self.loop_setting = int(self.loopCheckBox.isChecked())

    # Save settings to settings.pkl
    with open(path.join(self.file_path, 'settings.pkl'), 'wb') as f:
        pickle.dump(
            [self.split_image_directory, self.similarity_threshold, self.comparison_index, self.pause,
            self.fps_limit, split_key,
            reset_key, skip_split_key, undo_split_key, self.x, self.y, self.width, self.height,
            self.hwnd_title,
            self.custom_pause_times_setting, self.custom_thresholds_setting,
            self.group_dummy_splits_undo_skip_setting, self.loop_setting, pause_key], f)