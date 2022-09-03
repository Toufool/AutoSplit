from __future__ import annotations

import error_messages
import user_profile
from utils import find_autosplit_main_window, fire_and_forget


@fire_and_forget
def start_auto_control_loop():
    autosplit = find_autosplit_main_window()
    try:
        while True:
            try:
                line = input()
            except (RuntimeError, ValueError):
                autosplit.show_error_signal.emit(error_messages.stdin_lost)
                break
            except EOFError:
                continue
            # This is for use in a Development environment
            if line == "kill":
                autosplit.closeEvent()
                break
            if line == "start":
                autosplit.start_auto_splitter()
            elif line in {"split", "skip"}:
                autosplit.skip_split_signal.emit()
            elif line == "undo":
                autosplit.undo_split_signal.emit()
            elif line == "reset":
                autosplit.reset_signal.emit()
            elif line.startswith("settings"):
                # Allow for any split character between "settings" and the path
                user_profile.load_settings(line[9:])
            # TODO: Not yet implemented in AutoSplit Integration
            # elif line == 'pause':
            #     autosplit.pause_signal.emit()
    except Exception as exception:   # pylint: disable=broad-except # We really want to catch everything here
        error = exception
        autosplit.show_error_signal.emit(lambda: error_messages.exception_traceback(error))
