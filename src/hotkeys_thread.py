import error_messages
import time

from hotkey_constants import Hotkey, CommandStr, CommandToHotkey, HOTKEYS, STR_TO_KEYS, SPECIAL_KEYS, FUNC_KEYS
from PySide6.QtCore import QThread
from pynput import keyboard
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from AutoSplit import AutoSplit


def assert_and_show_error(autosplit: "AutoSplit", cond: bool, msg: str):
    try:
        assert cond, msg
    except Exception as exception:
        autosplit.show_error_signal.emit(lambda: error_messages.exception_traceback(exception))


class HotKeyDef:
    """Hotkey Definition, common settings per-hotkey"""

    def __init__(self, autosplit: "AutoSplit", name: Hotkey, action: Any):
        """Sets the name, binds the action and declares empty sequence"""

        self.autosplit = autosplit
        self.name = name
        self.action = action
        self.sequence_str: str | None = None

        # sequence used by the listener
        self.sequence: str | None = None

        # sequence used by the sender
        self.send_keys: list[keyboard.KeyCode] = []

    def clear(self):
        """Resets the hotkey definition, make sure to stop the listener when using this"""

        self.sequence_str = None
        self.sequence = None
        self.send_keys.clear()

    def set_sequence(self, sequence_str: str):
        """Sets a sequence of keys to read/write"""

        # don't process empty sequences
        if len(sequence_str) == 0:
            return

        self.sequence_str = sequence_str

        # `keyboard.GlobalHotkeys` requires < and > to be wrapped around specific keys like modifiers (ctrl, alt, ...)
        special_keys = SPECIAL_KEYS + FUNC_KEYS

        split = sequence_str.split("+")
        sequence: list[str] = []

        for elem in split:
            sequence.append(f"<{elem}>" if elem in special_keys else elem)
            assert_and_show_error(self.autosplit, elem in STR_TO_KEYS, f"unsupported key: {repr(elem)}")
            self.send_keys.append(STR_TO_KEYS[elem])

        self.sequence = "+".join(sequence)


class HotKeyThread(QThread):
    """Hotkey thread, handles listening and sending inputs"""

    def __init__(self, autosplit: "AutoSplit"):
        """Initializes the thread"""

        super().__init__()
        self.autosplit = autosplit
        self.is_paused = False
        self.listener: keyboard.GlobalHotKeys | None = None

        # hotkey_def = HotKeyDef(hotkey_name, self.get_hotkey_action(hotkey_name))
        for name in HOTKEYS:
            setattr(self, f"{name}_def", HotKeyDef(autosplit, name, self.get_hotkey_action(name)))

    def get_hotkey_action(self, hotkey: Hotkey):
        """Fetch the action corresponding to the target hotkey"""

        if hotkey == "split":
            return self.autosplit.start_auto_splitter
        if hotkey == "skip_split":
            return lambda: self.autosplit.skip_split(navigate_image_only=True)
        if hotkey == "undo_split":
            return lambda: self.autosplit.undo_split(navigate_image_only=True)
        if hotkey == "toggle_auto_reset_image":

            def toggle_auto_reset_image():
                new_value = not self.autosplit.settings_dict["enable_auto_reset"]
                self.autosplit.settings_dict["enable_auto_reset"] = new_value
                if self.autosplit.SettingsWidget:
                    self.autosplit.SettingsWidget.enable_auto_reset_image_checkbox.setChecked(new_value)

            return toggle_auto_reset_image
        return getattr(self.autosplit, f"{hotkey}_signal").emit

    def get_def(self, name: str | Hotkey) -> HotKeyDef:
        """Returns the definition ref of the specific hotkey"""

        keydef: HotKeyDef | None = getattr(self, f"{name}_def")
        assert_and_show_error(self.autosplit, keydef is not None, "key def is none")
        return keydef

    def stop_listener(self):
        """If the listener is running stop it and clear the reference"""

        if self.listener is not None:
            self.listener.stop()
            self.listener = None

    def set_sequence(self, name: Hotkey, sequence_str: str):
        """Sets a new key sequence (restarts the listener)"""

        self.stop_listener()

        # clear any hotkey sharing the same sequence
        for hotkey in HOTKEYS:
            if hotkey not in name:
                hdef = self.get_def(hotkey)

                if hdef.sequence_str is not None and hdef.sequence_str == sequence_str:
                    hdef.clear()

        self.get_def(name).set_sequence(sequence_str)
        self.autosplit.settings_dict[f"{name}_hotkey"] = sequence_str # pyright: ignore[reportGeneralTypeIssues]

    def remove_all_hotkeys(self):
        """Clears all hotkeys (restarts the listener)"""

        self.stop_listener()

        for name in HOTKEYS:
            self.get_def(name).clear()

    def get_gh_map(self):
        """Generates the map to use in `keyboard.GlobalHotkeys`"""

        # sequence string: action callback
        gh_map: dict[str, Any] = {}

        for name in HOTKEYS:
            keydef = self.get_def(name)
            if keydef.sequence is not None and len(keydef.sequence) > 0:
                gh_map[keydef.sequence] = keydef.action

        return gh_map

    def run(self):
        """
        Thread's main loop, which is only used for the listener.
        This function will automatically start again the listener if it was previously cleared by `stop_listener`.
        """

        while True:
            if self.is_paused:
                continue

            if self.listener is None:
                with keyboard.GlobalHotKeys(self.get_gh_map()) as listener:
                    self.listener = listener
                    listener.join()

    def run_action_from_cmd(self, cmd: CommandStr):
        """Run the corresponding action by sending the inputs if the command is valid"""

        if cmd not in CommandToHotkey:
            raise KeyError(f"{cmd!r} is not a valid command")

        keydef = self.get_def(CommandToHotkey[cmd])
        assert_and_show_error(self.autosplit, len(keydef.send_keys) > 0, "can't send inputs: sequence is not set")
        controller = keyboard.Controller()

        # it seems the sleeps are required, in some cases the key is still considered as pressed when it shouldn't
        for key in keydef.send_keys:
            controller.press(key)
            time.sleep(0.01)

        time.sleep(0.1)

        for key in reversed(keydef.send_keys):
            controller.release(key)
            time.sleep(0.01)
