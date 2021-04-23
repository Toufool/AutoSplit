import keyboard
import threading


# do all of these after you click "set hotkey" but before you type the hotkey.
def beforeSettingHotkey(self):
    self.startautosplitterButton.setEnabled(False)
    self.setsplithotkeyButton.setEnabled(False)
    self.setresethotkeyButton.setEnabled(False)
    self.setskipsplithotkeyButton.setEnabled(False)
    self.setundosplithotkeyButton.setEnabled(False)
    self.setpausehotkeyButton.setEnabled(False)


# do all of these things after you set a hotkey. a signal connects to this because
# changing GUI stuff in the hotkey thread was causing problems
def afterSettingHotkey(self):
    self.setsplithotkeyButton.setText('Set Hotkey')
    self.setresethotkeyButton.setText('Set Hotkey')
    self.setskipsplithotkeyButton.setText('Set Hotkey')
    self.setundosplithotkeyButton.setText('Set Hotkey')
    self.setpausehotkeyButton.setText('Set Hotkey')
    self.startautosplitterButton.setEnabled(True)
    self.setsplithotkeyButton.setEnabled(True)
    self.setresethotkeyButton.setEnabled(True)
    self.setskipsplithotkeyButton.setEnabled(True)
    self.setundosplithotkeyButton.setEnabled(True)
    self.setpausehotkeyButton.setEnabled(True)


def is_digit(key):
    try:
        key_as_num = int(key)
        return key_as_num >= 0 and key_as_num <= 9
    except Exception:
        return False


def __validate_keypad(expected_key, keyboard_event):
    # Prevent "num delete", "num dot" and "delete" from triggering each other
    # as well as "dot" and "num dot"
    if keyboard_event.scan_code == 83 or keyboard_event.scan_code == 52:
        if expected_key == keyboard_event.name:
            return True
        else:
            # TODO: "delete" won't work with "num delete" if localized in non-english
            return False
    # Prevent "action" from triggering "numpad" hotkeys
    if is_digit(keyboard_event.name[-1]):
        # Prevent "regular number" from activating "numpad" hotkeys
        if expected_key.startswith("num "):
            return keyboard_event.is_keypad
        # Prevent "numpad" from activating "regular number" hotkeys
        else:
            return not keyboard_event.is_keypad
    else:
        # Prevent "num action" keys from triggering "regular number" and "numpad" hotkeys.
        # Still allow the same key that might be localized differently on keypad vs non-keypad
        return not is_digit(expected_key[-1])


# NOTE: This is a workaround very specific to numpads.
# Windows reports different physical keys with the same scan code.
# For example, "Home", "Num Home" and "Num 7" are all "71".
# See: https://github.com/boppreh/keyboard/issues/171#issuecomment-390437684
#
# We're doing the check here instead of saving the key code because it'll
# cause issues with save files and the non-keypad shared keys are localized
# while the keypad ones aren't.
#
# Since we reuse the key string we set to send to LiveSplit, we can't use fake names like "num home".
# We're also trying to achieve the same hotkey behaviour as LiveSplit has.
def _hotkey_action(keyboard_event, key_name, action):
    if keyboard_event.event_type == keyboard.KEY_DOWN and __validate_keypad(key_name, keyboard_event):
        action()


def __get_key_name(keyboard_event):
    return "num " + keyboard_event.name \
        if keyboard_event.is_keypad and is_digit(keyboard_event.name) \
        else keyboard_event.name


def __is_key_already_set(self, key_name):
    return key_name == self.splitLineEdit.text() \
        or key_name == self.resetLineEdit.text() \
        or key_name == self.skipsplitLineEdit.text() \
        or key_name == self.undosplitLineEdit.text() \
        or key_name == self.pausehotkeyLineEdit.text()


# --------------------HOTKEYS--------------------------
# TODO: Refactor to de-duplicate all this code, including settings_file.py
# Going to comment on one func, and others will be similar.
def setSplitHotkey(self):
    self.setsplithotkeyButton.setText('Press a key..')

    # disable some buttons
    self.beforeSettingHotkey()

    # new thread points to callback. this thread is needed or GUI will freeze
    # while the program waits for user input on the hotkey
    def callback(hotkey):
        # try to remove the previously set hotkey if there is one.
        try:
            keyboard.unhook_key(hotkey)
        # KeyError was coming up when loading the program and
        # the lineEdit area was empty (no hotkey set), then you
        # set one, reload the setting once back to blank works,
        # but if you click reload settings again, it errors
        # we can just have it pass, but don't want to throw in
        # generic exception here in case another one of these
        # pops up somewhere.
        except (AttributeError, KeyError):
            pass

        # wait until user presses the hotkey, then keyboard module reads the input
        key_name = __get_key_name(keyboard.read_event(True))
        try:
            # If the key the user presses is equal to itself or another hotkey already set,
            # this causes issues. so here, it catches that, and will make no changes to the hotkey.

            # or

            # keyboard module allows you to hit multiple keys for a hotkey. they are joined
            # together by +. If user hits two keys at the same time, make no changes to the
            # hotkey. A try and except is needed if a hotkey hasn't been set yet. I'm not
            # allowing for these multiple-key hotkeys because it can cause crashes, and
            # not many people are going to really use or need this.
            if __is_key_already_set(self, key_name) or '+' in key_name:
                self.afterSettingHotkeySignal.emit()
                return
        except AttributeError:
            self.afterSettingHotkeySignal.emit()
            return

        # add the key as the hotkey, set the text into the LineEdit, set it as old_xxx_key,
        # then emite a signal to re-enable some buttons and change some text in GUI.

        # We need to inspect the event to know if it comes from numpad because of _canonial_names.
        # See: https://github.com/boppreh/keyboard/issues/161#issuecomment-386825737
        # The best way to achieve this is make our own hotkey handling on top of hook
        # See: https://github.com/boppreh/keyboard/issues/216#issuecomment-431999553
        self.split_hotkey = keyboard.hook_key(key_name, lambda e: _hotkey_action(e, key_name, self.startAutoSplitter))
        self.splitLineEdit.setText(key_name)
        self.split_key = key_name
        self.afterSettingHotkeySignal.emit()

    t = threading.Thread(target=callback, args=(self.split_hotkey,))
    t.start()


def setResetHotkey(self):
    self.setresethotkeyButton.setText('Press a key..')
    self.beforeSettingHotkey()

    def callback(hotkey):
        try:
            keyboard.unhook_key(hotkey)
        except (AttributeError, KeyError):
            pass

        key_name = __get_key_name(keyboard.read_event(True))

        try:
            if __is_key_already_set(self, key_name) or '+' in key_name:
                self.afterSettingHotkeySignal.emit()
                return
        except AttributeError:
            self.afterSettingHotkeySignal.emit()
            return

        self.reset_hotkey = keyboard.hook_key(key_name, lambda e: _hotkey_action(e, key_name, self.startReset))
        self.resetLineEdit.setText(key_name)
        self.reset_key = key_name
        self.afterSettingHotkeySignal.emit()

    t = threading.Thread(target=callback, args=(self.reset_hotkey,))
    t.start()


def setSkipSplitHotkey(self):
    self.setskipsplithotkeyButton.setText('Press a key..')
    self.beforeSettingHotkey()

    def callback(hotkey):
        try:
            keyboard.unhook_key(hotkey)
        except (AttributeError, KeyError):
            pass

        key_name = __get_key_name(keyboard.read_event(True))

        try:
            if __is_key_already_set(self, key_name) or '+' in key_name:
                self.afterSettingHotkeySignal.emit()
                return
        except AttributeError:
            self.afterSettingHotkeySignal.emit()
            return

        self.skip_split_hotkey = keyboard.hook_key(key_name, lambda e: _hotkey_action(e, key_name, self.startSkipSplit))
        self.skipsplitLineEdit.setText(key_name)
        self.skip_split_key = key_name
        self.afterSettingHotkeySignal.emit()

    t = threading.Thread(target=callback, args=(self.skip_split_hotkey,))
    t.start()


def setUndoSplitHotkey(self):
    self.setundosplithotkeyButton.setText('Press a key..')
    self.beforeSettingHotkey()

    def callback(hotkey):
        try:
            keyboard.unhook_key(hotkey)
        except (AttributeError, KeyError):
            pass

        key_name = __get_key_name(keyboard.read_event(True))

        try:
            if __is_key_already_set(self, key_name) or '+' in key_name:
                self.afterSettingHotkeySignal.emit()
                return
        except AttributeError:
            self.afterSettingHotkeySignal.emit()
            return

        self.undo_split_hotkey = keyboard.hook_key(key_name, lambda e: _hotkey_action(e, key_name, self.startUndoSplit))
        self.undosplitLineEdit.setText(key_name)
        self.undo_split_key = key_name
        self.afterSettingHotkeySignal.emit()

    t = threading.Thread(target=callback, args=(self.undo_split_hotkey,))
    t.start()


def setPauseHotkey(self):
    self.setpausehotkeyButton.setText('Press a key..')
    self.beforeSettingHotkey()

    def callback(hotkey):
        try:
            keyboard.unhook_key(hotkey)
        except (AttributeError, KeyError):
            pass

        key_name = __get_key_name(keyboard.read_event(True))

        try:
            if __is_key_already_set(self, key_name) or '+' in key_name:
                self.afterSettingHotkeySignal.emit()
                return
        except AttributeError:
            self.afterSettingHotkeySignal.emit()
            return

        self.pause_hotkey = keyboard.hook_key(key_name, lambda e: _hotkey_action(e, key_name, self.startPause))
        self.pausehotkeyLineEdit.setText(key_name)
        self.pause_key = key_name
        self.afterSettingHotkeySignal.emit()

    t = threading.Thread(target=callback, args=(self.pause_hotkey,))
    t.start()
