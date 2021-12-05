from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from AutoSplit import AutoSplit

import os

from packaging import version
from PyQt6 import QtWidgets
from PyQt6.QtCore import QThread
from requests.exceptions import RequestException
from simplejson.errors import JSONDecodeError
import requests

import about
import design
import error_messages
import settings_file
import resources_rc  # noqa: F401
import update_checker

# AutoSplit Version number
VERSION = "1.6.1"


# About Window
class __AboutWidget(QtWidgets.QWidget, about.Ui_aboutAutoSplitWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.createdbyLabel.setOpenExternalLinks(True)
        self.donatebuttonLabel.setOpenExternalLinks(True)
        self.versionLabel.setText(f"Version: {VERSION}")
        self.show()


def about(self: AutoSplit):
    self.AboutWidget = __AboutWidget()


class __UpdateCheckerWidget(QtWidgets.QWidget, update_checker.Ui_UpdateChecker):
    def __init__(self, latest_version: str, design_window: design.Ui_MainWindow, check_on_open: bool = False):
        super().__init__()
        self.setupUi(self)
        self.labelCurrentVersionNumber.setText(VERSION)
        self.labelLatestVersionNumber.setText(latest_version)
        self.pushButtonLeft.clicked.connect(self.openUpdate)
        self.checkBoxDoNotAskMeAgain.stateChanged.connect(self.doNotAskMeAgainStateChanged)
        self.design_window = design_window
        if version.parse(latest_version) > version.parse(VERSION):
            self.checkBoxDoNotAskMeAgain.setVisible(check_on_open)
            self.show()
        elif not check_on_open:
            self.labelUpdateStatus.setText("You are on the latest AutoSplit version.")
            self.labelGoToDownload.setVisible(False)
            self.pushButtonLeft.setVisible(False)
            self.pushButtonRight.setText("OK")
            self.checkBoxDoNotAskMeAgain.setVisible(False)
            self.show()

    def openUpdate(self):
        os.system("start \"\" https://github.com/Toufool/Auto-Split/releases/latest")
        self.close()

    def doNotAskMeAgainStateChanged(self):
        settings_file.set_check_for_updates_on_open(
            self.design_window,
            self.checkBoxDoNotAskMeAgain.isChecked())


def open_update_checker(autosplit: AutoSplit, latest_version: str, check_on_open: bool):
    autosplit.UpdateCheckerWidget = __UpdateCheckerWidget(latest_version, autosplit, check_on_open)


def viewHelp():
    os.system("start \"\" https://github.com/Toufool/Auto-Split#tutorial")


class __CheckForUpdatesThread(QThread):
    def __init__(self, autosplit: AutoSplit, check_on_open: bool):
        super().__init__()
        self.autosplit = autosplit
        self.check_on_open = check_on_open

    def run(self):
        try:
            response = requests.get("https://api.github.com/repos/Toufool/Auto-Split/releases/latest")
            latest_version = response.json()["name"].split("v")[1]
            self.autosplit.updateCheckerWidgetSignal.emit(latest_version, self.check_on_open)
        except (RequestException, KeyError, JSONDecodeError):
            if not self.check_on_open:
                self.autosplit.showErrorSignal(error_messages.checkForUpdatesError)


def checkForUpdates(autosplit: AutoSplit, check_on_open: bool = False):
    autosplit.CheckForUpdatesThread = __CheckForUpdatesThread(autosplit, check_on_open)
    autosplit.CheckForUpdatesThread.start()
