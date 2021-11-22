from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from AutoSplit import AutoSplit

import os
from PyQt6 import QtWidgets

import about
import requests
from packaging import version
import update_checker
import error_messages
import resources_rc  # noqa: F401
from about import Ui_aboutAutoSplitWidget
from PyQt6 import QtCore

# AutoSplit Version number
VERSION = "1.3.0"


# About Window
class AboutWidget(QtWidgets.QWidget, Ui_aboutAutoSplitWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.createdbyLabel.setOpenExternalLinks(True)
        self.donatebuttonLabel.setOpenExternalLinks(True)
        self.versionLabel.setText(f"Version: {VERSION}")
        self.show()

class UpdateCheckerWidget(QtWidgets.QWidget, update_checker.Ui_UpdateChecker):
    def __init__(self, latest_version: str, autosplit: AutoSplit, check_for_updates_on_open: bool = False):
        super().__init__()
        self.setupUi(self)
        self.labelCurrentVersionNumber.setText(VERSION)
        self.labelLatestVersionNumber.setText(latest_version)
        self.pushButtonLeft.clicked.connect(self.openUpdate)
        self.pushButtonRight.clicked.connect(self.closeWindow)
        self.autosplit = autosplit
        if version.parse(latest_version) > version.parse(VERSION):
            self.labelUpdateStatus.setText("There is an update available for AutoSplit.")
            self.labelGoToDownload.setText("Open download page?")
            self.pushButtonLeft.setVisible(True)
            self.pushButtonLeft.setText("Open")
            self.pushButtonRight.setText("Later")
            if not check_for_updates_on_open:
                self.checkBoxDoNotAskMeAgain.setVisible(False)
            self.show()
        elif not check_for_updates_on_open:
            self.labelUpdateStatus.setText("You are on the latest AutoSplit version.")
            self.pushButtonLeft.setVisible(False)
            self.pushButtonRight.setText("OK")
            self.show()

    def openUpdate(self):
        if self.checkBoxDoNotAskMeAgain.isChecked():
            self.autosplit.actionCheck_for_Updates_on_Open.setChecked(False)
        os.system("start \"\" https://github.com/Toufool/Auto-Split/releases/latest")
        self.close()

    def closeWindow(self):
        if self.checkBoxDoNotAskMeAgain.isChecked():
            self.autosplit.actionCheck_for_Updates_on_Open.setChecked(False)
        self.close()

def viewHelp():
    os.system("start \"\" https://github.com/Toufool/Auto-Split#tutorial")


def about(self: AutoSplit):
    self.AboutWidget = AboutWidget()

def checkForUpdates(autosplit: AutoSplit, check_for_updates_on_open: bool = False):
    response = requests.get("https://api.github.com/repos/Toufool/Auto-Split/releases/latest")
    latest_version = response.json()["name"].split("v")[1]
    autosplit.UpdateCheckerWidget = UpdateCheckerWidget(latest_version, autosplit, check_for_updates_on_open)
    if not check_for_updates_on_open:
        error_messages.checkForUpdatesError()
    else:
        pass

