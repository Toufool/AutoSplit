from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from AutoSplit import AutoSplit

import os
from PyQt6 import QtWidgets

import requests
from packaging import version

import about
import design
import error_messages
import settings_file
import resources_rc  # noqa: F401
import update_checker

# AutoSplit Version number
VERSION = "1.5.0"


# About Window
class AboutWidget(QtWidgets.QWidget, about.Ui_aboutAutoSplitWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.createdbyLabel.setOpenExternalLinks(True)
        self.donatebuttonLabel.setOpenExternalLinks(True)
        self.versionLabel.setText(f"Version: {VERSION}")
        self.show()


class UpdateCheckerWidget(QtWidgets.QWidget, update_checker.Ui_UpdateChecker):
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


def viewHelp():
    os.system("start \"\" https://github.com/Toufool/Auto-Split#tutorial")


def about(self: AutoSplit):
    self.AboutWidget = AboutWidget()


def checkForUpdates(autosplit: AutoSplit, check_on_open: bool = False):
    try:
        response = requests.get("https://api.github.com/repos/Toufool/Auto-Split/releases/latest")
        latest_version = response.json()["name"].split("v")[1]
        autosplit.UpdateCheckerWidget = UpdateCheckerWidget(latest_version, autosplit, check_on_open)
    except:
        if not check_on_open:
            error_messages.checkForUpdatesError()
