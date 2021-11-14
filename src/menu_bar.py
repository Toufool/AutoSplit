from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from AutoSplit import AutoSplit

from PyQt6 import QtWidgets
import os

import about
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


def viewHelp():
    os.system("start \"\" https://github.com/Toufool/Auto-Split#tutorial")


def about(self: AutoSplit):
    self.AboutWidget = AboutWidget()
