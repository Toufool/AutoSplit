from __future__ import annotations
from typing import Optional, TYPE_CHECKING, Union
from collections.abc import Callable
if TYPE_CHECKING:
    from AutoSplit import AutoSplit

import threading
from keyboard._keyboard_event import KeyboardEvent, KEY_DOWN
import keyboard  # https://github.com/boppreh/keyboard/issues/505
import pyautogui  # https://github.com/asweigart/pyautogui/issues/645
# While not usually recommended, we don't manipulate the mouse, and we don't want the extra delay
pyautogui.FAILSAFE = False


# do all of these after you click "set hotkey" but before you type the hotkey.
def beforeSettingHotkey(autosplit: AutoSplit):
    autosplit.startautosplitterButton.setEnabled(False)
    autosplit.setsplithotkeyButton.setEnabled(False)
    autosplit.setresethotkeyButton.setEnabled(False)
    autosplit.setskipsplithotkeyButton.setEnabled(False)
    autosplit.setundosplithotkeyButton.setEnabled(False)
    autosplit.setpausehotkeyButton.setEnabled(False)


# do all of these things after you set a hotkey. a signal connects to this because
# changing GUI stuff in the hotkey thread was causing problems
def afterSettingHotkey(autosplit: AutoSplit):
    autosplit.setsplithotkeyButton.setText("Set Hotkey")
    autosplit.setresethotkeyButton.setText("Set Hotkey")
    autosplit.setskipsplithotkeyButton.setText("Set Hotkey")
    autosplit.setundosplithotkeyButton.setText("Set Hotkey")
    autosplit.setpausehotkeyButton.setText("Set Hotkey")
    autosplit.startautosplitterButton.setEnabled(True)
    autosplit.setsplithotkeyButton.setEnabled(True)
    autosplit.setresethotkeyButton.setEnabled(True)
    autosplit.setskipsplithotkeyButton.setEnabled(True)
    autosplit.setundosplithotkeyButton.setEnabled(True)
    autosplit.setpausehotkeyButton.setEnabled(True)


def is_digit(key: Optional[str]):
    if key is None:
        return False
    try:
        return 0 <= int(key) <= 9
    except ValueError:
        return False


def send_command(autosplit: AutoSplit, command: str):
    if autosplit.is_auto_controlled:
        print(command, flush=True)
    elif command in {"split", "start"}:
        _send_hotkey(autosplit.splitLineEdit.text())
    elif command == "pause":
        _send_hotkey(autosplit.pausehotkeyLineEdit.text())
    elif command == "reset":
        _send_hotkey(autosplit.resetLineEdit.text())
    else:
        raise KeyError(f"'{command}' is not a valid LiveSplit.AutoSplitIntegration command")


# Supports sending the appropriate scan code for all the special cases
def _send_hotkey(key_or_scan_code: Union[int, str]):
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
        # TODO: "del" won't work with "(keypad)delete" if localized in non-english (ie: "suppr" in french)
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
# while the keypad ones aren't.

# Since we reuse the key string we set to send to LiveSplit, we can't use fake names like "num home".
# We're also trying to achieve the same hotkey behaviour as LiveSplit has.
def _hotkey_action(keyboard_event: KeyboardEvent, key_name: str, action: Callable[[], None]):
    if keyboard_event.event_type == KEY_DOWN and __validate_keypad(key_name, keyboard_event):
        action()


def __get_key_name(keyboard_event: KeyboardEvent):
    return f"num {keyboard_event.name}"  \
        if keyboard_event.is_keypad and is_digit(keyboard_event.name) \
        else str(keyboard_event.name)


def __is_key_already_set(autosplit: AutoSplit, key_name: str):
    return key_name in (autosplit.splitLineEdit.text(),
                        autosplit.resetLineEdit.text(),
                        autosplit.skipsplitLineEdit.text(),
                        autosplit.undosplitLineEdit.text(),
                        autosplit.pausehotkeyLineEdit.text())


# --------------------HOTKEYS--------------------------
# TODO: Refactor to de-duplicate all this code, including settings_file.py
# Going to comment on one func, and others will be similar.
def setSplitHotkey(autosplit: AutoSplit):
    autosplit.setsplithotkeyButton.setText("Press a key...")

    # disable some buttons
    beforeSettingHotkey(autosplit)

    # new thread points to callback. this thread is needed or GUI will freeze
    # while the program waits for user input on the hotkey
    def callback(hotkey: Callable[[], None]):
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
            if __is_key_already_set(autosplit, key_name) or (key_name != "+" and "+" in key_name):
                autosplit.afterSettingHotkeySignal.emit()
                return
        except AttributeError:
            autosplit.afterSettingHotkeySignal.emit()
            return

        # add the key as the hotkey, set the text into the LineEdit, set it as old_xxx_key,
        # then emite a signal to re-enable some buttons and change some text in GUI.

        # We need to inspect the event to know if it comes from numpad because of _canonial_names.
        # See: https://github.com/boppreh/keyboard/issues/161#issuecomment-386825737
        # The best way to achieve this is make our own hotkey handling on top of hook
        # See: https://github.com/boppreh/keyboard/issues/216#issuecomment-431999553
        autosplit.split_hotkey = keyboard.hook_key(
            key_name,
            lambda e: _hotkey_action(e, key_name, autosplit.startAutoSplitter))
        autosplit.splitLineEdit.setText(key_name)
        autosplit.split_key = key_name
        autosplit.afterSettingHotkeySignal.emit()

    t = threading.Thread(target=callback, args=(autosplit.split_hotkey,))
    t.start()


def setResetHotkey(autosplit: AutoSplit):
    autosplit.setresethotkeyButton.setText("Press a key...")
    beforeSettingHotkey(autosplit)

    def callback(hotkey: Callable[[], None]):
        try:
            keyboard.unhook_key(hotkey)
        except (AttributeError, KeyError):
            pass

        key_name = __get_key_name(keyboard.read_event(True))

        try:
            if __is_key_already_set(autosplit, key_name) or (key_name != "+" and "+" in key_name):
                autosplit.afterSettingHotkeySignal.emit()
                return
        except AttributeError:
            autosplit.afterSettingHotkeySignal.emit()
            return

        autosplit.reset_hotkey = keyboard.hook_key(
            key_name,
            lambda e: _hotkey_action(e, key_name, autosplit.startReset))
        autosplit.resetLineEdit.setText(key_name)
        autosplit.reset_key = key_name
        autosplit.afterSettingHotkeySignal.emit()

    t = threading.Thread(target=callback, args=(autosplit.reset_hotkey,))
    t.start()


def setSkipSplitHotkey(autosplit: AutoSplit):
    autosplit.setskipsplithotkeyButton.setText("Press a key...")
    beforeSettingHotkey(autosplit)

    def callback(hotkey: Callable[[], None]):
        try:
            keyboard.unhook_key(hotkey)
        except (AttributeError, KeyError):
            pass

        key_name = __get_key_name(keyboard.read_event(True))

        try:
            if __is_key_already_set(autosplit, key_name) or (key_name != "+" and "+" in key_name):
                autosplit.afterSettingHotkeySignal.emit()
                return
        except AttributeError:
            autosplit.afterSettingHotkeySignal.emit()
            return

        autosplit.skip_split_hotkey = keyboard.hook_key(
            key_name,
            lambda e: _hotkey_action(e, key_name, autosplit.startSkipSplit))
        autosplit.skipsplitLineEdit.setText(key_name)
        autosplit.skip_split_key = key_name
        autosplit.afterSettingHotkeySignal.emit()

    t = threading.Thread(target=callback, args=(autosplit.skip_split_hotkey,))
    t.start()


def setUndoSplitHotkey(autosplit: AutoSplit):
    autosplit.setundosplithotkeyButton.setText("Press a key...")
    beforeSettingHotkey(autosplit)

    def callback(hotkey: Callable[[], None]):
        try:
            keyboard.unhook_key(hotkey)
        except (AttributeError, KeyError):
            pass

        key_name = __get_key_name(keyboard.read_event(True))

        try:
            if __is_key_already_set(autosplit, key_name) or (key_name != "+" and "+" in key_name):
                autosplit.afterSettingHotkeySignal.emit()
                return
        except AttributeError:
            autosplit.afterSettingHotkeySignal.emit()
            return

        autosplit.undo_split_hotkey = keyboard.hook_key(
            key_name,
            lambda e: _hotkey_action(e, key_name, autosplit.startUndoSplit))
        autosplit.undosplitLineEdit.setText(key_name)
        autosplit.undo_split_key = key_name
        autosplit.afterSettingHotkeySignal.emit()

    t = threading.Thread(target=callback, args=(autosplit.undo_split_hotkey,))
    t.start()


def setPauseHotkey(autosplit: AutoSplit):
    autosplit.setpausehotkeyButton.setText("Press a key...")
    beforeSettingHotkey(autosplit)

    def callback(hotkey: Callable[[], None]):
        try:
            keyboard.unhook_key(hotkey)
        except (AttributeError, KeyError):
            pass

        key_name = __get_key_name(keyboard.read_event(True))

        try:
            if __is_key_already_set(autosplit, key_name) or (key_name != "+" and "+" in key_name):
                autosplit.afterSettingHotkeySignal.emit()
                return
        except AttributeError:
            autosplit.afterSettingHotkeySignal.emit()
            return

        autosplit.pause_hotkey = keyboard.hook_key(
            key_name,
            lambda e: _hotkey_action(e, key_name, autosplit.startPause))
        autosplit.pausehotkeyLineEdit.setText(key_name)
        autosplit.undo_split_key = key_name
        autosplit.afterSettingHotkeySignal.emit()

    t = threading.Thread(target=callback, args=(autosplit.pause_hotkey,))
    t.start()
