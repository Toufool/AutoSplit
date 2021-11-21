from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from AutoSplit import AutoSplit

from PyQt6 import QtWidgets
import os

import about
import requests
from packaging import version
import update_checker
import error_messages
import resources_rc  # noqa: F401

# AutoSplit Version number
VERSION = "1.6.0"


# About Window
class AboutWidget(QtWidgets.QWidget, about.Ui_aboutAutoSplitWidget):
    def __init__(self):
        super(AboutWidget, self).__init__()
        self.setupUi(self)
        self.createdbyLabel.setOpenExternalLinks(True)
        self.donatebuttonLabel.setOpenExternalLinks(True)
        self.versionLabel.setText(f"Version: {VERSION}")
        self.show()

class UpdateCheckerWidget(QtWidgets.QWidget, update_checker.Ui_UpdateChecker):
    def __init__(self, current_version, latest_version, update_available, check_for_updates_on_open):
        super(UpdateCheckerWidget, self).__init__()
        self.setupUi(self)
        self.labelCurrentVersionNumber.setText(current_version)
        self.labelLatestVersionNumber.setText(latest_version)
        if update_available:
            self.labelUpdateStatus.setText("There is an update available for AutoSplit.")
            self.labelGoToDownload.setText("Open download page?")
            self.pushButtonLeft.setVisible(True)
            self.pushButtonLeft.setText("Open")
            self.pushButtonRight.setText("Later")
            self.show()
        elif not update_available and not check_for_updates_on_open:
            self.labelUpdateStatus.setText("You are on the latest AutoSplit version.")
            self.pushButtonLeft.setVisible(False)
            self.pushButtonRight.setText("OK")
            self.show()

def viewHelp():
    os.system("start \"\" https://github.com/Toufool/Auto-Split#tutorial")


def about(self: AutoSplit):
    self.AboutWidget = AboutWidget()

def checkForUpdates(self: AutoSplit, check_for_updates_on_open: bool = False):
    try:
        response = requests.get("https://api.github.com/repos/Toufool/Auto-Split/releases/latest")
        latest_version = response.json()["name"].split("v")[1]
        current_version = VERSION
        update_available = version.parse(latest_version) > version.parse(current_version)
        self.UpdateCheckerWidget = UpdateCheckerWidget(current_version, latest_version, update_available, check_for_updates_on_open)
    except:
        if not check_for_updates_on_open:
            error_messages.checkForUpdatesError()
        else:
            pass

