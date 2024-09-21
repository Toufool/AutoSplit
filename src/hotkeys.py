import sys
from collections.abc import Callable
from typing import TYPE_CHECKING, Literal, cast

import keyboard
import pyautogui
from PySide6 import QtWidgets

import error_messages
from utils import fire_and_forget, is_digit, try_input_device_access

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

# While not usually recommended, we don't manipulate the mouse, and we don't want the extra delay
pyautogui.FAILSAFE = False

SET_HOTKEY_TEXT = "Set Hotkey"
PRESS_A_KEY_TEXT = "Press a key..."

CommandStr = Literal["split", "start", "pause", "reset", "skip", "undo"]
Hotkey = Literal[
    "split",
    "reset",
    "skip_split",
    "undo_split",
    "pause",
    "screenshot",
    "toggle_auto_reset_image",
]
HOTKEYS = (
    "split",
    "reset",
    "skip_split",
    "undo_split",
    "pause",
    "screenshot",
    "toggle_auto_reset_image",
)
HOTKEYS_WHEN_AUTOCONTROLLED = {"screenshot", "toggle_auto_reset_image"}


def remove_all_hotkeys():
    if not KEYBOARD_GROUPS_ISSUE and not KEYBOARD_UINPUT_ISSUE:
        keyboard.unhook_all()


def before_setting_hotkey(autosplit: "AutoSplit"):
    """Do all of these after you click "Set Hotkey" but before you type the hotkey."""
    autosplit.start_auto_splitter_button.setEnabled(False)
    if autosplit.SettingsWidget:
        for hotkey in HOTKEYS:
            getattr(autosplit.SettingsWidget, f"set_{hotkey}_hotkey_button").setEnabled(False)


def after_setting_hotkey(autosplit: "AutoSplit"):
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


def send_command(autosplit: "AutoSplit", command: CommandStr):
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
            _send_hotkey(autosplit.settings_dict["reset_hotkey"])
        case "reset":
            _send_hotkey(autosplit.settings_dict["reset_hotkey"])
        case "start" | "split":
            _send_hotkey(autosplit.settings_dict["split_hotkey"])
        case "pause":
            _send_hotkey(autosplit.settings_dict["pause_hotkey"])
        case "skip":
            _send_hotkey(autosplit.settings_dict["skip_split_hotkey"])
        case "undo":
            _send_hotkey(autosplit.settings_dict["undo_split_hotkey"])
        case _:  # pyright: ignore[reportUnnecessaryComparison]
            raise KeyError(f"{command!r} is not a valid command")


def _unhook(hotkey_callback: Callable[[], None] | None):
    try:
        if hotkey_callback:
            keyboard.unhook_key(hotkey_callback)
    except (AttributeError, KeyError, ValueError):
        pass


def _send_hotkey(hotkey_or_scan_code: int | str | None):
    """Supports sending the appropriate scan code for all the special cases."""
    if not hotkey_or_scan_code:
        return

    # Deal with regular inputs
    # If an int or does not contain the following strings
    if (  # fmt: skip
        isinstance(hotkey_or_scan_code, int)
        or not any(key in hotkey_or_scan_code for key in ("num ", "decimal", "+"))
    ):
        keyboard.send(hotkey_or_scan_code)
        return

    # FIXME: Localized keys won't work here
    # Deal with problematic keys.
    # Even by sending specific scan code "keyboard" still sends the default (wrong) key
    # keyboard also has issues with capitalization modifier (shift+A)
    # keyboard.send(keyboard.key_to_scan_codes(key_or_scan_code)[1])
    pyautogui.hotkey(*[
        "+" if key == "plus" else key  # fmt: skip
        for key in hotkey_or_scan_code.replace(" ", "").split("+")
    ])


def __validate_keypad(expected_key: str, keyboard_event: keyboard.KeyboardEvent) -> bool:
    """
    NOTE: This is a workaround very specific to numpads.
    Windows reports different physical keys with the same scan code.
    For example, "Home", "Num Home" and "Num 7" are all `71`.
    See: https://github.com/boppreh/keyboard/issues/171#issuecomment-390437684 .

    Since we reuse the key string we set to send to LiveSplit,
    we can't use fake names like "num home".
    We're also trying to achieve the same hotkey behaviour as LiveSplit has.
    """
    # Prevent "(keypad)delete", "(keypad)./decimal" and "del" from triggering each other
    # as well as "." and "(keypad)./decimal"
    if keyboard_event.scan_code in {83, 52}:
        # TODO: "del" won't work with "(keypad)delete" if localized in non-english
        # (ie: "suppr" in french)
        return expected_key == keyboard_event.name
    # Prevent "action keys" from triggering "keypad keys"
    if keyboard_event.name and is_digit(keyboard_event.name[-1]):
        # Prevent "regular numbers" and "keypad numbers" from activating each other
        return bool(
            keyboard_event.is_keypad
            if expected_key.startswith("num ")
            else not keyboard_event.is_keypad
        )

    # Prevent "keypad action keys" from triggering "regular numbers" and "keypad numbers"
    # Still allow the same key that might be localized differently on keypad vs non-keypad
    return not is_digit(expected_key[-1])


def _hotkey_action(
    keyboard_event: keyboard.KeyboardEvent,
    key_name: str,
    action: Callable[[], None],
):
    """
    We're doing the check here instead of saving the key code because
    the non-keypad shared keys are localized while the keypad ones aren't.
    They also share scan codes on Windows.
    """
    if keyboard_event.event_type == keyboard.KEY_DOWN and __validate_keypad(
        key_name,
        keyboard_event,
    ):
        action()


def __get_key_name(keyboard_event: keyboard.KeyboardEvent):
    """Ensures proper keypad name."""
    event_name = str(keyboard_event.name)
    # Normally this is done by keyboard.get_hotkey_name. But our code won't always get there.
    if event_name == "+":
        return "plus"
    return (
        f"num {keyboard_event.name}"
        if keyboard_event.is_keypad and is_digit(keyboard_event.name)
        else event_name
    )


def __get_hotkey_name(names: list[str]):
    """
    Uses keyboard.get_hotkey_name but works with non-english modifiers and keypad
    See: https://github.com/boppreh/keyboard/issues/516 .
    """
    if not names:  # 0-length
        return ""

    if len(names) == 1:
        return names[0]

    def sorting_key(key: str):
        return not keyboard.is_modifier(keyboard.key_to_scan_codes(key)[0])

    clean_names = sorted(keyboard.get_hotkey_name(names).split("+"), key=sorting_key)
    # Replace the last key in hotkey_name with what we actually got as a last key_name
    # This ensures we keep proper keypad names
    return "+".join(clean_names[:-1] + names[-1:])


def __read_hotkey():
    """
    Blocks until a hotkey combination is read.
    Returns the hotkey_name and last KeyboardEvent.
    """
    names: list[str] = []
    while True:
        keyboard_event = keyboard.read_event(True)
        # LiveSplit supports modifier keys as the last key, so any keyup means end of hotkey
        if keyboard_event.event_type == keyboard.KEY_UP:
            # Unless keyup is also the very first event,
            # which can happen from a very fast press at the same time we start reading
            if not names:
                continue
            break
        key_name = __get_key_name(keyboard_event)
        # Ignore long presses
        if names and names[-1] == key_name:
            continue
        names.append(__get_key_name(keyboard_event))
        # Stop at the first non-modifier to prevent registering a hotkey with multiple regular keys
        if not keyboard.is_modifier(keyboard_event.scan_code):
            break
    return __get_hotkey_name(names)


def __remove_key_already_set(autosplit: "AutoSplit", key_name: str):
    for hotkey in HOTKEYS:
        settings_key = f"{hotkey}_hotkey"
        if autosplit.settings_dict.get(settings_key) == key_name:
            _unhook(getattr(autosplit, f"{hotkey}_hotkey"))
            autosplit.settings_dict[settings_key] = ""  # pyright: ignore[reportGeneralTypeIssues]
            if autosplit.SettingsWidget:
                getattr(autosplit.SettingsWidget, f"{hotkey}_input").setText("")


def __get_hotkey_action(autosplit: "AutoSplit", hotkey: Hotkey):
    if hotkey == "split":
        return autosplit.start_auto_splitter
    if hotkey == "skip_split":
        return lambda: autosplit.skip_split(navigate_image_only=True)
    if hotkey == "undo_split":
        return lambda: autosplit.undo_split(navigate_image_only=True)
    if hotkey == "toggle_auto_reset_image":

        def toggle_auto_reset_image():
            new_value = not autosplit.settings_dict["enable_auto_reset"]
            autosplit.settings_dict["enable_auto_reset"] = new_value
            if autosplit.SettingsWidget:
                autosplit.SettingsWidget.enable_auto_reset_image_checkbox.setChecked(new_value)

        return toggle_auto_reset_image
    return getattr(autosplit, f"{hotkey}_signal").emit


def is_valid_hotkey_name(hotkey_name: str):
    return any(
        key and not keyboard.is_modifier(keyboard.key_to_scan_codes(key)[0])
        for key in hotkey_name.split("+")
    )


# TODO: using getattr/setattr is NOT a good way to go about this. It was only temporarily done to
# reduce duplicated code. We should use a dictionary of hotkey class or something.


def set_hotkey(autosplit: "AutoSplit", hotkey: Hotkey, preselected_hotkey_name: str = ""):
    if KEYBOARD_GROUPS_ISSUE:
        if not preselected_hotkey_name:
            error_messages.linux_groups()
        return
    if KEYBOARD_UINPUT_ISSUE:
        if not preselected_hotkey_name:
            error_messages.linux_uinput()
        return

    if autosplit.SettingsWidget:
        # Unfocus all fields
        cast(QtWidgets.QWidget, autosplit.SettingsWidget).setFocus()
        getattr(autosplit.SettingsWidget, f"set_{hotkey}_hotkey_button").setText(PRESS_A_KEY_TEXT)

    # Disable some buttons
    before_setting_hotkey(autosplit)

    # New thread points to read_and_set_hotkey. this thread is needed or GUI will freeze
    # while the program waits for user input on the hotkey
    @fire_and_forget
    def read_and_set_hotkey():
        try:
            hotkey_name = preselected_hotkey_name or __read_hotkey()

            # Unset hotkey by pressing "Escape". This is the same behaviour as LiveSplit
            if hotkey_name == "esc":
                _unhook(getattr(autosplit, f"{hotkey}_hotkey"))
                autosplit.settings_dict[f"{hotkey}_hotkey"] = (  # pyright: ignore[reportGeneralTypeIssues]
                    ""
                )
                if autosplit.SettingsWidget:
                    getattr(autosplit.SettingsWidget, f"{hotkey}_input").setText("")
                return

            if not is_valid_hotkey_name(hotkey_name):
                autosplit.show_error_signal.emit(lambda: error_messages.invalid_hotkey(hotkey_name))
                return

            # Try to remove the previously set hotkey if there is one
            _unhook(getattr(autosplit, f"{hotkey}_hotkey"))

            # Remove any hotkey using the same key combination
            __remove_key_already_set(autosplit, hotkey_name)

            action = __get_hotkey_action(autosplit, hotkey)
            setattr(
                autosplit,
                f"{hotkey}_hotkey",
                # keyboard.add_hotkey doesn't give the last keyboard event,
                # so we can't __validate_keypad.
                # This means "ctrl + num 5" and "ctrl + 5" will both be registered.
                # For that reason, we still prefer keyboard.hook_key for single keys.
                # keyboard module allows you to hit multiple keys for a hotkey.
                # They are joined together by + .
                keyboard.add_hotkey(hotkey_name, action)
                if "+" in hotkey_name
                # We need to inspect the event to know if it comes from numpad
                # because of _canonial_names.
                # See: https://github.com/boppreh/keyboard/issues/161#issuecomment-386825737
                # The best way to achieve this is make our own hotkey handling on top of hook
                # See: https://github.com/boppreh/keyboard/issues/216#issuecomment-431999553
                else keyboard.hook_key(
                    hotkey_name,
                    lambda keyboard_event: _hotkey_action(keyboard_event, hotkey_name, action),
                ),
            )

            if autosplit.SettingsWidget:
                getattr(autosplit.SettingsWidget, f"{hotkey}_input").setText(hotkey_name)
            autosplit.settings_dict[f"{hotkey}_hotkey"] = (  # pyright: ignore[reportGeneralTypeIssues]
                hotkey_name
            )
        except Exception as exception:  # noqa: BLE001 # We really want to catch everything here
            error = exception
            autosplit.show_error_signal.emit(lambda: error_messages.exception_traceback(error))
        finally:
            autosplit.after_setting_hotkey_signal.emit()

    read_and_set_hotkey()
