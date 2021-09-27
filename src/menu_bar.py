import os
from PyQt6 import QtWidgets
import about
import resources_rc

# AutoSplit Version number
VERSION = "1.5.A3"


# About Window
class AboutWidget(QtWidgets.QWidget, about.Ui_aboutAutoSplitWidget):
    def __init__(self):
        super(AboutWidget, self).__init__()
        self.setupUi(self)
        self.createdbyLabel.setOpenExternalLinks(True)
        self.donatebuttonLabel.setOpenExternalLinks(True)
        self.show()

def viewHelp(self):
    os.system("start \"\" https://github.com/Toufool/Auto-Split#tutorial")
    return


def about(self):
    self.AboutWidget = AboutWidget()
