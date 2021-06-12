import os
from PyQt5 import QtWidgets
import about

# AutoSplit Version number
VERSION = "1.5.0"


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
    os.system("start \"\" https://github.com/Toufool/Auto-Split/blob/master/README.md#tutorial")


def about(self):
    self.AboutWidget = AboutWidget()
