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
                self.autosplit.showErrorSignal.emit(error_messages.stdinLostError)
                break
            # TODO: "AutoSplit Integration" needs to call this and wait instead of outright killing the app.
            # TODO: See if we can also get LiveSplit to wait on Exit in "AutoSplit Integration"
            # For now this can only used in a Development environment
            if line == "kill":
                self.autosplit.closeEvent()
                break
            if line == "start":
                self.autosplit.startAutoSplitter()
            elif line in {"split", "skip"}:
                self.autosplit.startSkipSplit()
            elif line == "undo":
                self.autosplit.startUndoSplit()
            elif line == "reset":
                self.autosplit.startReset()
            elif line.startswith("settings"):
                # Allow for any split character between "settings" and the path
                self.autosplit.load_settings_file_path = line[9:]
                settings.loadSettings(self.autosplit, load_settings_from_livesplit=True)
            # TODO: Not yet implemented in AutoSplit Integration
            # elif line == 'pause':
            #     self.startPause()
