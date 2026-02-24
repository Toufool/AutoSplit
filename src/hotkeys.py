from __future__ import annotations

import sys
from typing import TYPE_CHECKING, cast

from PySide6 import QtWidgets, QtGui
from hotkey_constants import CommandStr, Hotkey, SPECIAL_KEYS, HOTKEYS

import error_messages
from utils import try_input_device_access

if sys.platform == "linux":
    import grp
    import os

    groups = {grp.getgrgid(group).gr_name for group in os.getgroups()}
    KEYBOARD_GROUPS_ISSUE = not {"input", "tty"}.issubset(groups)
    KEYBOARD_UINPUT_ISSUE = not try_input_device_access()
else:
    KEYBOARD_GROUPS_ISSUE = False
    KEYBOARD_UINPUT_ISSUE = False

if TYPE_CHECKING:
    from AutoSplit import AutoSplit

SET_HOTKEY_TEXT = "Set Hotkey"
PRESS_A_KEY_TEXT = "Press a key..."


def before_setting_hotkey(autosplit: AutoSplit):
    """Do all of these after you click "Set Hotkey" but before you type the hotkey."""
    autosplit.start_auto_splitter_button.setEnabled(False)
    if autosplit.SettingsWidget:
        for hotkey in HOTKEYS:
            getattr(autosplit.SettingsWidget, f"set_{hotkey}_hotkey_button").setEnabled(False)


def after_setting_hotkey(autosplit: AutoSplit):
    """
    Do all of these things after you set a hotkey.
    A signal connects to this because changing GUI stuff is only possible in the main thread.
    """
    if not autosplit.is_running:
        autosplit.start_auto_splitter_button.setEnabled(True)
    if autosplit.SettingsWidget:
        for hotkey in HOTKEYS:
            getattr(
                autosplit.SettingsWidget,
                f"set_{hotkey}_hotkey_button",
            ).setText(SET_HOTKEY_TEXT)
            getattr(autosplit.SettingsWidget, f"set_{hotkey}_hotkey_button").setEnabled(True)


def send_command(autosplit: AutoSplit, command: CommandStr):
    if command in autosplit.settings_dict["screenshot_on"]:
        autosplit.screenshot_signal.emit()
    match command:
        case _ if autosplit.is_auto_controlled:
            if command == "start" and autosplit.settings_dict["start_also_resets"]:
                print("reset", flush=True)
            print(command, flush=True)
        # Note: Rather than having the start image able to also reset the timer, having
        # the reset image check be active at all time would be a better, more organic solution.
        # But that is dependent on migrating to an observer pattern (#219) and
        # being able to reload all images.
        case "start" if autosplit.settings_dict["start_also_resets"]:
            autosplit.hotkey_thread.run_action_from_cmd("reset")
        case _:
            if command == "start":
                command = "split"
            autosplit.hotkey_thread.run_action_from_cmd(command)


def __is_valid_hotkey_name(hotkey_name: str):
    return any(
        key and key not in SPECIAL_KEYS
        for key in hotkey_name.split("+")
    )


def __pause_thread(autosplit: "AutoSplit"):
    autosplit.hotkey_thread.is_paused = True
    autosplit.hotkey_thread.stop_listener()


def __resume_thread(autosplit: "AutoSplit"):
    autosplit.hotkey_thread.is_paused = False
    # the run function will set again the listener


# TODO: using getattr/setattr is NOT a good way to go about this. It was only temporarily done to
# reduce duplicated code. We should use a dictionary of hotkey class or something.


# TODO: reimplement already existing checks
def set_hotkey(autosplit: "AutoSplit", hotkey: Hotkey, hotkey_name: str | None = None, input_ref: QtWidgets.QKeySequenceEdit | None = None):
    __pause_thread(autosplit)

    if KEYBOARD_GROUPS_ISSUE:
        if hotkey_name is None:
            error_messages.linux_groups()
        __resume_thread(autosplit)
        return
    if KEYBOARD_UINPUT_ISSUE:
        if hotkey_name is None:
            error_messages.linux_uinput()
        __resume_thread(autosplit)
        return

    if autosplit.SettingsWidget is not None:
        # Unfocus all fields
        cast(QtWidgets.QWidget, autosplit.SettingsWidget).setFocus()
        getattr(autosplit.SettingsWidget, f"set_{hotkey}_hotkey_button").setText(PRESS_A_KEY_TEXT)

    # Disable some buttons
    before_setting_hotkey(autosplit)

    try:
        if hotkey_name is not None:
            if autosplit.SettingsWidget is not None and len(hotkey_name) > 0:
                hotkey_input: QtWidgets.QKeySequenceEdit = getattr(autosplit.SettingsWidget, f"{hotkey}_input")

                if not __is_valid_hotkey_name(hotkey_name):
                    autosplit.show_error_signal.emit(lambda: error_messages.invalid_hotkey(hotkey_name))
                    __resume_thread(autosplit)
                    return

                hotkey_input.setKeySequence(QtGui.QKeySequence(hotkey_name))

            autosplit.hotkey_thread.set_sequence(hotkey, hotkey_name)
        elif input_ref is not None:
            autosplit.hotkey_thread.set_sequence(hotkey, input_ref.keySequence().toString().lower())
        else:
            raise ValueError("set_hotkey: unexpected operating mode")
    except Exception as exception:  # noqa: BLE001 # We really want to catch everything here
        autosplit.show_error_signal.emit(lambda: error_messages.exception_traceback(exception))
    finally:
        autosplit.after_setting_hotkey_signal.emit()

    __resume_thread(autosplit)
