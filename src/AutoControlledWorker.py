from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from AutoSplit import AutoSplit
from PyQt6 import QtCore

import error_messages
import settings_file as settings


class AutoControlledWorker(QtCore.QObject):
    def __init__(self, autosplit: AutoSplit):
        self.autosplit = autosplit
        super().__init__()

    def run(self):
        while True:
            try:
                line = input()
            except RuntimeError:
                self.autosplit.show_error_signal.emit(error_messages.stdin_lost)
                break
            except EOFError:
                continue
            # TODO: "AutoSplit Integration" needs to call this and wait instead of outright killing the app.
            # For now this can only used in a Development environment
            if line == "kill":
                self.autosplit.closeEvent()
                break
            if line == "start":
                self.autosplit.start_auto_splitter()
            elif line in {"split", "skip"}:
                self.autosplit.skip_split_signal.emit()
            elif line == "undo":
                self.autosplit.undo_split_signal.emit()
            elif line == "reset":
                self.autosplit.reset_signal.emit()
            elif line.startswith("settings"):
                # Allow for any split character between "settings" and the path
                settings.load_settings(self.autosplit, line[9:])
            # TODO: Not yet implemented in AutoSplit Integration
            # elif line == 'pause':
            #     self.pause_signal.emit()
