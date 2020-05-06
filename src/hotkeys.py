import keyboard
from threading import Thread

def newHotkey (self, hotkey_name, lineEdit):
    # New thread points to waitForKeyPress. This thread is needed or GUI will freeze
    # while the program waits for user input on the hotkey
    def waitForKeyPress():
        # Disable some buttons
        self.startautosplitterButton.setEnabled(False)
        self.setsplithotkeyButton.setEnabled(False)
        self.setresethotkeyButton.setEnabled(False)
        self.setskipsplithotkeyButton.setEnabled(False)
        self.setundosplithotkeyButton.setEnabled(False)
        self.setpausehotkeyButton.setEnabled(False)
        self.reloadsettingsButton.setEnabled(False)

        self.hotkeys[hotkey_name].detectUserKeyPress([self.splitLineEdit,
            self.resetLineEdit,
            self.skipsplitLineEdit,
            self.undosplitLineEdit,
            self.pauseLineEdit])

        if self.hotkeys[hotkey_name].successful:
            # Set the text into the LineEdit
            self.updateHotkeyLineEdits()
        else:
            self.hotkeys[hotkey_name].key = lineEdit.text()
            if self.hotkeys[hotkey_name].key_press_function is not None:
                self.hotkeys[hotkey_name].hotkey = keyboard.add_hotkey(self.hotkeys[hotkey_name].key, self.hotkeys[hotkey_name].key_press_function)

        # Re-enable some buttons and change some text in GUI.
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
        self.reloadsettingsButton.setEnabled(True)

    Thread(target = waitForKeyPress).start()

def updateHotkeyLineEdits(self):
    self.splitLineEdit.setText(str(self.hotkeys['split'].key))
    self.resetLineEdit.setText(str(self.hotkeys['reset'].key))
    self.skipsplitLineEdit.setText(str(self.hotkeys['skip'].key))
    self.undosplitLineEdit.setText(str(self.hotkeys['undo'].key))
    self.pauseLineEdit.setText(str(self.hotkeys['pause'].key))

class Hotkey:
    def __init__(self, key_press_function = None):
        self.key_press_function = key_press_function

    def detectUserKeyPress(self, lineEdits):
        self.successful = False

        # Try to remove the previously set hotkey if there is one
        try:
            keyboard.remove_hotkey(self.hotkey)
        except (AttributeError, KeyError, NameError):
            pass

        # wait until user presses the hotkey, then keyboard module reads the input
        self.key = keyboard.read_hotkey(False)

        # If the key the user presses is equal to itself or another hotkey already set,
        # this causes issues. So here, it catches that, and will make no changes to the hotkey
        try:
            for lineEdit in lineEdits:
                if lineEdit.text() == self.key:
                    return
        except AttributeError:
            return

        # The keyboard module allows you to hit multiple keys for a hotkey. They are joined
        # together by a '+'. If user hits two keys at the same time, make no changes to the
        # hotkey. A try and except is needed if a hotkey hasn't been set yet. I'm not
        # allowing for these multiple-key hotkeys because it can cause crashes, and
        # not many people are going to really use or need this
        try:
            if '+' in self.key:
                return
        except AttributeError:
            return

        if self.key_press_function is not None:
            # Add the key as a hotkey
            self.hotkey = keyboard.add_hotkey(self.key, self.key_press_function)

        self.successful = True

    def setKeyAndHotkey(self, key):
        try:
            try:
                keyboard.remove_hotkey(self.hotkey)
            except AttributeError:
                pass

            self.key = key
            self.hotkey = keyboard.add_hotkey(key, self.key_press_function)

        # Pass if the key is an empty string (hotkey was never set)
        except ValueError:
            pass