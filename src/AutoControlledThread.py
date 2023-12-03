from typing import TYPE_CHECKING

from PySide6 import QtCore

import error_messages
import user_profile

if TYPE_CHECKING:
    from AutoSplit import AutoSplit


class AutoControlledThread(QtCore.QThread):
    def __init__(self, autosplit: "AutoSplit"):
        self._autosplit_ref = autosplit
        super().__init__()

    @QtCore.Slot()
    def run(self):
        while True:
            try:
                line = input()
            except RuntimeError:
                self._autosplit_ref.show_error_signal.emit(error_messages.stdin_lost)
                break
            except EOFError:
                continue
            match line:
                # This is for use in a Development environment
                case "kill":
                    self._autosplit_ref.closeEvent()
                    break
                case "start":
                    self._autosplit_ref.start_auto_splitter()
                case "split" | "skip":
                    self._autosplit_ref.skip_split_signal.emit()
                case "undo":
                    self._autosplit_ref.undo_split_signal.emit()
                case "reset":
                    self._autosplit_ref.reset_signal.emit()
                # TODO: Not yet implemented in AutoSplit Integration
                # case 'pause':
                #     self.pause_signal.emit()
                case line:
                    if line.startswith("settings"):
                        # Allow for any split character between "settings" and the path
                        user_profile.load_settings(self._autosplit_ref, line[9:])
