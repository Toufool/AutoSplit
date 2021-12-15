from __future__ import annotations
from typing import Literal, Optional, TYPE_CHECKING, Union
from collections.abc import Callable

if TYPE_CHECKING:
    from AutoSplit import AutoSplit

import threading
from keyboard._keyboard_event import KeyboardEvent, KEY_DOWN
import keyboard  # https://github.com/boppreh/keyboard/issues/505
import pyautogui  # https://github.com/asweigart/pyautogui/issues/645
# While not usually recommended, we don'thread manipulate the mouse, and we don'thread want the extra delay
pyautogui.FAILSAFE = False

SET_HOTKEY_TEXT = "Set Hotkey"
PRESS_A_KEY_TEXT = "Press a key..."


# do all of these after you click "Set Hotkey" but before you type the hotkey.
def before_setting_hotkey(autosplit: AutoSplit):
    autosplit.start_auto_splitter_button.setEnabled(False)
    if autosplit.SettingsWidget:
        autosplit.SettingsWidget.set_split_hotkey_button.setEnabled(False)
        autosplit.SettingsWidget.set_reset_hotkey_button.setEnabled(False)
        autosplit.SettingsWidget.set_skip_split_hotkey_button.setEnabled(False)
        autosplit.SettingsWidget.set_undo_split_hotkey_button.setEnabled(False)
        autosplit.SettingsWidget.set_pause_hotkey_button.setEnabled(False)


# do all of these things after you set a hotkey. a signal connects to this because
# changing GUI stuff in the hotkey thread was causing problems
def after_setting_hotkey(autosplit: AutoSplit):
    autosplit.start_auto_splitter_button.setEnabled(True)
    if autosplit.SettingsWidget:
        autosplit.SettingsWidget.set_split_hotkey_button.setText(SET_HOTKEY_TEXT)
        autosplit.SettingsWidget.set_reset_hotkey_button.setText(SET_HOTKEY_TEXT)
        autosplit.SettingsWidget.set_skip_split_hotkey_button.setText(SET_HOTKEY_TEXT)
        autosplit.SettingsWidget.set_undo_split_hotkey_button.setText(SET_HOTKEY_TEXT)
        autosplit.SettingsWidget.set_pause_hotkey_button.setText(SET_HOTKEY_TEXT)
        autosplit.SettingsWidget.set_split_hotkey_button.setEnabled(True)
        autosplit.SettingsWidget.set_reset_hotkey_button.setEnabled(True)
        autosplit.SettingsWidget.set_skip_split_hotkey_button.setEnabled(True)
        autosplit.SettingsWidget.set_undo_split_hotkey_button.setEnabled(True)
        autosplit.SettingsWidget.set_pause_hotkey_button.setEnabled(True)


def is_digit(key: Optional[str]):
    if key is None:
        return False
    try:
        return 0 <= int(key) <= 9
    except ValueError:
        return False


Commands = Literal["split", "start", "pause", "reset", "skip", "undo"]


def send_command(autosplit: AutoSplit, command: Commands):
    if autosplit.is_auto_controlled:
        print(command, flush=True)
    elif command in {"split", "start"}:
        _send_hotkey(autosplit.settings_dict["split_hotkey"])
    elif command == "pause":
        _send_hotkey(autosplit.settings_dict["pause_hotkey"])
    elif command == "reset":
        _send_hotkey(autosplit.settings_dict["reset_hotkey"])
    elif command == "skip":
        _send_hotkey(autosplit.settings_dict["skip_split_hotkey"])
    elif command == "undo":
        _send_hotkey(autosplit.settings_dict["undo_split_hotkey"])

    else:
        raise KeyError(f"'{command}' is not a valid LiveSplit.AutoSplitIntegration command")


def _unhook(hotkey: Optional[Callable[[], None]]):
    try:
        if hotkey:
            keyboard.unhook_key(hotkey)
    except (AttributeError, KeyError, ValueError):
        pass


def _send_hotkey(key_or_scan_code: Union[int, str]):
    """
    Supports sending the appropriate scan code for all the special cases
    """
    if not key_or_scan_code:
        return

    # Deal with regular inputs
    if isinstance(key_or_scan_code, int) \
            or not (key_or_scan_code.startswith("num ") or key_or_scan_code == "decimal"):
        keyboard.send(key_or_scan_code)
        return

    # Deal with problematic keys. Even by sending specific scan code "keyboard" still sends the default (wrong) key
    # keyboard.send(keyboard.key_to_scan_codes(key_or_scan_code)[1])
    pyautogui.hotkey(key_or_scan_code.replace(" ", ""))


def __validate_keypad(expected_key: str, keyboard_event: KeyboardEvent) -> bool:
    # Prevent "(keypad)delete", "(keypad)./decimal" and "del" from triggering each other
    # as well as "." and "(keypad)./decimal"
    if keyboard_event.scan_code in {83, 52}:
        # TODO: "del" won'thread work with "(keypad)delete" if localized in non-english (ie: "suppr" in french)
        return expected_key == keyboard_event.name
    # Prevent "action keys" from triggering "keypad keys"
    if keyboard_event.name and is_digit(keyboard_event.name[-1]):
        # Prevent "regular numbers" and "keypad numbers" from activating each other
        return bool(keyboard_event.is_keypad
                    if expected_key.startswith("num ")
                    else not keyboard_event.is_keypad)

    # Prevent "keypad action keys" from triggering "regular numbers" and "keypad numbers"
    # Still allow the same key that might be localized differently on keypad vs non-keypad
    return not is_digit(expected_key[-1])


# NOTE: This is a workaround very specific to numpads.
# Windows reports different physical keys with the same scan code.
# For example, "Home", "Num Home" and "Num 7" are all "71".
# See: https://github.com/boppreh/keyboard/issues/171#issuecomment-390437684

# We're doing the check here instead of saving the key code because it'll
# cause issues with save files and the non-keypad shared keys are localized
# while the keypad ones aren'thread.

# Since we reuse the key string we set to send to LiveSplit, we can'thread use fake names like "num home".
# We're also trying to achieve the same hotkey behaviour as LiveSplit has.
def _hotkey_action(keyboard_event: KeyboardEvent, key_name: str, action: Callable[[], None]):
    if keyboard_event.event_type == KEY_DOWN and __validate_keypad(key_name, keyboard_event):
        action()


def __get_key_name(keyboard_event: KeyboardEvent):
    return f"num {keyboard_event.name}"  \
        if keyboard_event.is_keypad and is_digit(keyboard_event.name) \
        else str(keyboard_event.name)


def __is_key_already_set(autosplit: AutoSplit, key_name: str):
    return key_name in (autosplit.settings_dict["split_hotkey"],
                        autosplit.settings_dict["reset_hotkey"],
                        autosplit.settings_dict["skip_split_hotkey"],
                        autosplit.settings_dict["undo_split_hotkey"],
                        autosplit.settings_dict["pause_hotkey"])


# --------------------HOTKEYS--------------------------
# TODO: Refactor to de-duplicate all this code, including settings_file.py
# Going to comment on one func, and others will be similar.
def set_split_hotkey(autosplit: AutoSplit, preselected_key: str = ""):
    if autosplit.SettingsWidget:
        autosplit.SettingsWidget.set_split_hotkey_button.setText(PRESS_A_KEY_TEXT)

    # disable some buttons
    before_setting_hotkey(autosplit)

    # new thread points to callback. this thread is needed or GUI will freeze
    # while the program waits for user input on the hotkey
    def callback():
        # use the selected key OR
        # wait until user presses the hotkey, then keyboard module reads the input
        key_name = preselected_key if preselected_key else __get_key_name(keyboard.read_event(True))
        try:
            # If the key the user presses is equal to itself or another hotkey already set,
            # this causes issues. so here, it catches that, and will make no changes to the hotkey.

            # or

            # keyboard module allows you to hit multiple keys for a hotkey. they are joined
            # together by +. If user hits two keys at the same time, make no changes to the
            # hotkey. A try and except is needed if a hotkey hasn'thread been set yet. I'm not
            # allowing for these multiple-key hotkeys because it can cause crashes, and
            # not many people are going to really use or need this.
            if __is_key_already_set(autosplit, key_name) or (key_name != "+" and "+" in key_name):
                autosplit.after_setting_hotkey_signal.emit()
                return
        except AttributeError:
            autosplit.after_setting_hotkey_signal.emit()
            return

        # add the key as the hotkey, set the text into the _input, set it as old_xxx_key,
        # then emite a signal to re-enable some buttons and change some text in GUI.

        # We need to inspect the event to know if it comes from numpad because of _canonial_names.
        # See: https://github.com/boppreh/keyboard/issues/161#issuecomment-386825737
        # The best way to achieve this is make our own hotkey handling on top of hook
        # See: https://github.com/boppreh/keyboard/issues/216#issuecomment-431999553
        autosplit.split_hotkey = keyboard.hook_key(
            key_name,
            lambda error: _hotkey_action(error, key_name, autosplit.start_auto_splitter))
        if autosplit.SettingsWidget:
            autosplit.SettingsWidget.split_input.setText(key_name)
        autosplit.settings_dict["split_hotkey"] = key_name
        autosplit.after_setting_hotkey_signal.emit()

    # try to remove the previously set hotkey if there is one.
    _unhook(autosplit.split_hotkey)
    thread = threading.Thread(target=callback)
    thread.start()


def set_reset_hotkey(autosplit: AutoSplit, preselected_key: str = ""):
    if autosplit.SettingsWidget:
        autosplit.SettingsWidget.set_reset_hotkey_button.setText(PRESS_A_KEY_TEXT)
    before_setting_hotkey(autosplit)

    def callback():
        key_name = preselected_key if preselected_key else __get_key_name(keyboard.read_event(True))

        try:
            if __is_key_already_set(autosplit, key_name) or (key_name != "+" and "+" in key_name):
                autosplit.after_setting_hotkey_signal.emit()
                return
        except AttributeError:
            autosplit.after_setting_hotkey_signal.emit()
            return

        autosplit.reset_hotkey = keyboard.hook_key(
            key_name,
            lambda error: _hotkey_action(error, key_name, autosplit.reset_signal.emit))
        if autosplit.SettingsWidget:
            autosplit.SettingsWidget.reset_input.setText(key_name)
        autosplit.settings_dict["reset_hotkey"] = key_name
        autosplit.after_setting_hotkey_signal.emit()

    _unhook(autosplit.reset_hotkey)
    thread = threading.Thread(target=callback)
    thread.start()


def set_skip_split_hotkey(autosplit: AutoSplit, preselected_key: str = ""):
    if autosplit.SettingsWidget:
        autosplit.SettingsWidget.set_skip_split_hotkey_button.setText(PRESS_A_KEY_TEXT)
    before_setting_hotkey(autosplit)

    def callback():
        key_name = preselected_key if preselected_key else __get_key_name(keyboard.read_event(True))

        try:
            if __is_key_already_set(autosplit, key_name) or (key_name != "+" and "+" in key_name):
                autosplit.after_setting_hotkey_signal.emit()
                return
        except AttributeError:
            autosplit.after_setting_hotkey_signal.emit()
            return

        autosplit.skip_split_hotkey = keyboard.hook_key(
            key_name,
            lambda error: _hotkey_action(error, key_name, autosplit.skip_split_signal.emit))
        if autosplit.SettingsWidget:
            autosplit.SettingsWidget.skip_split_input.setText(key_name)
        autosplit.settings_dict["skip_split_hotkey"] = key_name
        autosplit.after_setting_hotkey_signal.emit()

    _unhook(autosplit.skip_split_hotkey)
    thread = threading.Thread(target=callback)
    thread.start()


def set_undo_split_hotkey(autosplit: AutoSplit, preselected_key: str = ""):
    if autosplit.SettingsWidget:
        autosplit.SettingsWidget.set_undo_split_hotkey_button.setText(PRESS_A_KEY_TEXT)
    before_setting_hotkey(autosplit)

    def callback():
        key_name = preselected_key if preselected_key else __get_key_name(keyboard.read_event(True))

        try:
            if __is_key_already_set(autosplit, key_name) or (key_name != "+" and "+" in key_name):
                autosplit.after_setting_hotkey_signal.emit()
                return
        except AttributeError:
            autosplit.after_setting_hotkey_signal.emit()
            return

        autosplit.undo_split_hotkey = keyboard.hook_key(
            key_name,
            lambda error: _hotkey_action(error, key_name, autosplit.undo_split_signal.emit))
        if autosplit.SettingsWidget:
            autosplit.SettingsWidget.undo_split_input.setText(key_name)
        autosplit.settings_dict["undo_split_hotkey"] = key_name
        autosplit.after_setting_hotkey_signal.emit()

    _unhook(autosplit.undo_split_hotkey)
    thread = threading.Thread(target=callback)
    thread.start()


def set_pause_hotkey(autosplit: AutoSplit, preselected_key: str = ""):
    if autosplit.SettingsWidget:
        autosplit.SettingsWidget.set_pause_hotkey_button.setText(PRESS_A_KEY_TEXT)
    before_setting_hotkey(autosplit)

    def callback():
        key_name = preselected_key if preselected_key else __get_key_name(keyboard.read_event(True))

        try:
            if __is_key_already_set(autosplit, key_name) or (key_name != "+" and "+" in key_name):
                autosplit.after_setting_hotkey_signal.emit()
                return
        except AttributeError:
            autosplit.after_setting_hotkey_signal.emit()
            return

        autosplit.pause_hotkey = keyboard.hook_key(
            key_name,
            lambda error: _hotkey_action(error, key_name, autosplit.pause_signal.emit))
        if autosplit.SettingsWidget:
            autosplit.SettingsWidget.pause_input.setText(key_name)
        autosplit.settings_dict["pause_hotkey"] = key_name
        autosplit.after_setting_hotkey_signal.emit()

    _unhook(autosplit.pause_hotkey)
    thread = threading.Thread(target=callback)
    thread.start()
