import os
from PyQt4 import QtGui
import about

# About Window
class AboutWidget(QtGui.QWidget, about.Ui_aboutAutoSplitWidget):
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