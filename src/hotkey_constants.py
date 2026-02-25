from typing import Literal

from pynput.keyboard import Key, KeyCode

SPECIAL_KEYS = ["ctrl", "alt", "shift", "cmd", "stealth", "pause"]
FUNC_KEYS = [f"f{i}" for i in range(1, 21)]

# TODO: find something better
STR_TO_KEYS = {
    "alt": Key.alt.value,
    "altleft": Key.alt_l.value,
    "altright": Key.alt_r.value,
    "capslock": Key.caps_lock.value,
    "ctrl": Key.ctrl.value,
    "ctrlleft": Key.ctrl_l.value,
    "ctrlright": Key.ctrl_r.value,
    "shift": Key.shift.value,
    "shiftleft": Key.shift_l.value,
    "shiftright": Key.shift_r.value,
    "win": Key.cmd.value,
    "winleft": Key.cmd_l.value,
    "winright": Key.cmd_r.value,
    "command": Key.cmd.value,
    "option": Key.alt.value,
    "optionleft": Key.alt_l.value,
    "optionright": Key.alt_r.value,
    "fn": Key.f1.value,
    "backspace": Key.backspace.value,
    "enter": Key.enter.value,
    "return": Key.enter.value,
    "esc": Key.esc.value,
    "escape": Key.esc.value,
    "space": Key.space.value,
    "tab": Key.tab.value,
    "del": Key.delete.value,
    "delete": Key.delete.value,
    "home": Key.home.value,
    "end": Key.end.value,
    "pageup": Key.page_up.value,
    "pgup": Key.page_up.value,
    "pagedown": Key.page_down.value,
    "pgdn": Key.page_down.value,
    "insert": Key.insert.value,
    "up": Key.up.value,
    "down": Key.down.value,
    "left": Key.left.value,
    "right": Key.right.value,
    "numlock": Key.num_lock.value,
    "decimal": KeyCode.from_char("."),
    "add": KeyCode.from_char("+"),
    "subtract": KeyCode.from_char("-"),
    "multiply": KeyCode.from_char("*"),
    "divide": KeyCode.from_char("/"),
    "printscreen": Key.print_screen.value,
    "prntscrn": Key.print_screen.value,
    "prtsc": Key.print_screen.value,
    "prtscr": Key.print_screen.value,
    "scrolllock": Key.scroll_lock.value,
    "pause": Key.pause.value,
    "volumemute": Key.media_volume_mute.value,
    "volumeup": Key.media_volume_up.value,
    "volumedown": Key.media_volume_down.value,
    "playpause": Key.media_play_pause.value,
    "nexttrack": Key.media_next.value,
    "prevtrack": Key.media_previous.value,
    "a": KeyCode.from_char("a"),
    "b": KeyCode.from_char("b"),
    "c": KeyCode.from_char("c"),
    "d": KeyCode.from_char("d"),
    "e": KeyCode.from_char("e"),
    "f": KeyCode.from_char("f"),
    "g": KeyCode.from_char("g"),
    "h": KeyCode.from_char("h"),
    "i": KeyCode.from_char("i"),
    "j": KeyCode.from_char("j"),
    "k": KeyCode.from_char("k"),
    "l": KeyCode.from_char("l"),
    "m": KeyCode.from_char("m"),
    "n": KeyCode.from_char("n"),
    "o": KeyCode.from_char("o"),
    "p": KeyCode.from_char("p"),
    "q": KeyCode.from_char("q"),
    "r": KeyCode.from_char("r"),
    "s": KeyCode.from_char("s"),
    "t": KeyCode.from_char("t"),
    "u": KeyCode.from_char("u"),
    "v": KeyCode.from_char("v"),
    "w": KeyCode.from_char("w"),
    "x": KeyCode.from_char("x"),
    "y": KeyCode.from_char("y"),
    "z": KeyCode.from_char("z"),
    # F1, F2, ...
    **{f"f{i}": getattr(Key, f"f{i}").value for i in range(1, 21)},
    # 0, 1, ...
    **{f"num{i}": KeyCode.from_char(str(i)) for i in range(10)},
    **{f"{i}": KeyCode.from_char(str(i)) for i in range(10)},
}

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

CommandToHotkey = {
    "split": "split",
    "pause": "pause",
    "reset": "reset",
    "skip": "skip_split",
    "undo": "undo_split",
}

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
