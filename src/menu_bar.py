from PyQt6 import QtWidgets
import about
import os

import resources_rc  # noqa: F401

# AutoSplit Version number
VERSION = "1.5.A4"


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


def about(self):
    self.AboutWidget = AboutWidget()
