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

    return

#--------------------HOTKEYS--------------------------
#Going to comment on one func, and others will be similar.
def setSplitHotkey(self):
    self.setsplithotkeyButton.setText('Press a key...')

    # disable some buttons
    self.beforeSettingHotkey()

    # new thread points to callback. this thread is needed or GUI will freeze
    # while the program waits for user input on the hotkey
    def callback():
        # try to remove the previously set hotkey if there is one.
        try:
            keyboard.remove_hotkey(self.split_hotkey)
        except AttributeError:
            pass
        #this error was coming up when loading the program and
        #the lineEdit area was empty (no hotkey set), then you
        #set one, reload the setting once back to blank works,
        #but if you click reload settings again, it errors
        #we can just have it pass, but don't want to throw in
        #generic exception here in case another one of these
        #pops up somewhere.
        except KeyError:
            pass

        # wait until user presses the hotkey, then keyboard module reads the input
        self.split_key = keyboard.read_hotkey(False)

        # If the key the user presses is equal to itself or another hotkey already set,
        # this causes issues. so here, it catches that, and will make no changes to the hotkey.
        try:
            if self.split_key == self.splitLineEdit.text() \
                    or self.split_key == self.resetLineEdit.text() \
                    or self.split_key == self.skipsplitLineEdit.text() \
                    or self.split_key == self.undosplitLineEdit.text() \
                    or self.split_key == self.pausehotkeyLineEdit.text():
                self.split_hotkey = keyboard.add_hotkey(self.old_split_key, self.startAutoSplitter)
                self.afterSettingHotkeySignal.emit()
                return
        except AttributeError:
            self.afterSettingHotkeySignal.emit()
            return

        # keyboard module allows you to hit multiple keys for a hotkey. they are joined
        # together by +. If user hits two keys at the same time, make no changes to the
        # hotkey. A try and except is needed if a hotkey hasn't been set yet. I'm not
        # allowing for these multiple-key hotkeys because it can cause crashes, and
        # not many people are going to really use or need this.
        try:
            if '+' in self.split_key:
                self.split_hotkey = keyboard.add_hotkey(self.old_split_key, self.startAutoSplitter)
                self.afterSettingHotkeySignal.emit()
                return
        except AttributeError:
            self.afterSettingHotkeySignal.emit()
            return

        # add the key as the hotkey, set the text into the LineEdit, set it as old_xxx_key,
        # then emite a signal to re-enable some buttons and change some text in GUI.
        self.split_hotkey = keyboard.add_hotkey(self.split_key, self.startAutoSplitter)
        self.splitLineEdit.setText(self.split_key)
        self.old_split_key = self.split_key
        self.afterSettingHotkeySignal.emit()
        return

    t = threading.Thread(target=callback)
    t.start()
    return

def setResetHotkey(self):
    self.setresethotkeyButton.setText('Press a key...')
    self.beforeSettingHotkey()

    def callback():
        try:
            keyboard.remove_hotkey(self.reset_hotkey)
        except AttributeError:
            pass
        except KeyError:
            pass
        self.reset_key = keyboard.read_hotkey(False)
        try:
            if self.reset_key == self.splitLineEdit.text() \
                    or self.reset_key == self.resetLineEdit.text() \
                    or self.reset_key == self.skipsplitLineEdit.text() \
                    or self.reset_key == self.undosplitLineEdit.text() \
                    or self.reset_key == self.pausehotkeyLineEdit.text():
                self.reset_hotkey = keyboard.add_hotkey(self.old_reset_key, self.startReset)
                self.afterSettingHotkeySignal.emit()
                return
        except AttributeError:
            self.afterSettingHotkeySignal.emit()
            return
        try:
            if '+' in self.reset_key:
                self.reset_hotkey = keyboard.add_hotkey(self.old_reset_key, self.startReset)
                self.afterSettingHotkeySignal.emit()
                return
        except AttributeError:
            self.afterSettingHotkeySignal.emit()
            return
        self.reset_hotkey = keyboard.add_hotkey(self.reset_key, self.startReset)
        self.resetLineEdit.setText(self.reset_key)
        self.old_reset_key = self.reset_key
        self.afterSettingHotkeySignal.emit()
        return

    t = threading.Thread(target=callback)
    t.start()
    return

def setSkipSplitHotkey(self):
    self.setskipsplithotkeyButton.setText('Press a key...')
    self.beforeSettingHotkey()

    def callback():
        try:
            keyboard.remove_hotkey(self.skip_split_hotkey)
        except AttributeError:
            pass
        except KeyError:
            pass

        self.skip_split_key = keyboard.read_hotkey(False)

        try:
            if self.skip_split_key == self.splitLineEdit.text() \
                    or self.skip_split_key == self.resetLineEdit.text() \
                    or self.skip_split_key == self.skipsplitLineEdit.text() \
                    or self.skip_split_key == self.undosplitLineEdit.text() \
                    or self.skip_split_key == self.pausehotkeyLineEdit.text():
                self.skip_split_hotkey = keyboard.add_hotkey(self.old_skip_split_key, self.startSkipSplit)
                self.afterSettingHotkeySignal.emit()
                return
        except AttributeError:
            self.afterSettingHotkeySignal.emit()
            return

        try:
            if '+' in self.skip_split_key:
                self.skip_split_hotkey = keyboard.add_hotkey(self.old_skip_split_key, self.startSkipSplit)
                self.afterSettingHotkeySignal.emit()
                return
        except AttributeError:
            self.afterSettingHotkeySignal.emit()
            return

        self.skip_split_hotkey = keyboard.add_hotkey(self.skip_split_key, self.startSkipSplit)
        self.skipsplitLineEdit.setText(self.skip_split_key)
        self.old_skip_split_key = self.skip_split_key
        self.afterSettingHotkeySignal.emit()
        return

    t = threading.Thread(target=callback)
    t.start()
    return

def setUndoSplitHotkey(self):
    self.setundosplithotkeyButton.setText('Press a key...')
    self.beforeSettingHotkey()

    def callback():
        try:
            keyboard.remove_hotkey(self.undo_split_hotkey)
        except AttributeError:
            pass
        except KeyError:
            pass

        self.undo_split_key = keyboard.read_hotkey(False)

        try:
            if self.undo_split_key == self.splitLineEdit.text() \
                    or self.undo_split_key == self.resetLineEdit.text() \
                    or self.undo_split_key == self.skipsplitLineEdit.text() \
                    or self.undo_split_key == self.undosplitLineEdit.text() \
                    or self.undo_split_key == self.pausehotkeyLineEdit.text():
                self.undo_split_hotkey = keyboard.add_hotkey(self.old_undo_split_key, self.startUndoSplit)
                self.afterSettingHotkeySignal.emit()
                return
        except AttributeError:
            self.afterSettingHotkeySignal.emit()
            return

        try:
            if '+' in self.undo_split_key:
                self.undo_split_hotkey = keyboard.add_hotkey(self.old_undo_split_key, self.startUndoSplit)
                self.afterSettingHotkeySignal.emit()
                return
        except AttributeError:
            self.afterSettingHotkeySignal.emit()
            return

        self.undo_split_hotkey = keyboard.add_hotkey(self.undo_split_key, self.startUndoSplit)
        self.undosplitLineEdit.setText(self.undo_split_key)
        self.old_undo_split_key = self.undo_split_key
        self.afterSettingHotkeySignal.emit()
        return

    t = threading.Thread(target=callback)
    t.start()
    return

def setPauseHotkey(self):
    self.setpausehotkeyButton.setText('Press a key...')
    self.beforeSettingHotkey()

    def callback():
        try:
            keyboard.remove_hotkey(self.pause_hotkey)
        except AttributeError:
            pass
        except KeyError:
            pass

        self.pause_key = keyboard.read_hotkey(False)

        try:
            if self.pause_key == self.splitLineEdit.text() \
                    or self.pause_key == self.resetLineEdit.text() \
                    or self.pause_key == self.skipsplitLineEdit.text() \
                    or self.pause_key == self.undosplitLineEdit.text() \
                    or self.pause_key == self.pausehotkeyLineEdit.text():
                self.pause_hotkey = keyboard.add_hotkey(self.old_pause_key, self.startPause)
                self.afterSettingHotkeySignal.emit()
                return
        except AttributeError:
            self.afterSettingHotkeySignal.emit()
            return

        try:
            if '+' in self.pause_key:
                self.pause_hotkey = keyboard.add_hotkey(self.old_pause_key, self.startPause)
                self.afterSettingHotkeySignal.emit()
                return
        except AttributeError:
            self.afterSettingHotkeySignal.emit()
            return

        self.pause_hotkey = keyboard.add_hotkey(self.pause_key, self.startPause)
        self.pausehotkeyLineEdit.setText(self.pause_key)
        self.old_pause_key = self.pause_key
        self.afterSettingHotkeySignal.emit()
        return

    t = threading.Thread(target=callback)
    t.start()
    return
